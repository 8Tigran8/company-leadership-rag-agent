from __future__ import annotations

from datetime import UTC, datetime

from company_rag.config import Settings
from company_rag.llm import LLMUnavailableError, extract_people
from company_rag.models import Claim, Person, SourceDocument
from company_rag.normalize import is_excluded_title, normalize_title, slugify


def extract_claims_from_sources(
    settings: Settings,
    *,
    company_name: str,
    company_domain: str,
    sources: list[SourceDocument],
) -> tuple[list[Person], list[Claim]]:
    people_by_id: dict[str, Person] = {}
    claims: list[Claim] = []
    for source in sources:
        if not _looks_relevant(source):
            continue
        try:
            extracted_people = extract_people(
                settings,
                company_name=company_name,
                source_title=source.title,
                source_text=source.text,
            )
        except LLMUnavailableError:
            raise
        for item in extracted_people:
            if not item.current or is_excluded_title(item.title):
                continue
            person_id = f"person_{slugify(company_domain)}_{slugify(item.name)}"
            people_by_id.setdefault(
                person_id,
                Person(
                    id=person_id,
                    company_domain=company_domain,
                    name=item.name,
                    profile_url=str(item.profile_url) if item.profile_url else None,
                ),
            )
            normalized = normalize_title(item.title)
            confidence = _confidence_label(item.confidence)
            claim_id = f"claim_{slugify(company_domain)}_{slugify(item.name)}_{slugify(item.title)}"
            claims.append(
                Claim(
                    id=claim_id,
                    company_domain=company_domain,
                    person_id=person_id,
                    claim_type="role",
                    value=item.title,
                    normalized_role=normalized.normalized_role,
                    seniority=normalized.seniority,
                    department=item.department or normalized.department,
                    source_id=source.id,
                    evidence=item.evidence,
                    confidence=confidence,
                    extracted_at=_now(),
                )
            )
            if item.location:
                claims.append(
                    Claim(
                        id=f"{claim_id}_location",
                        company_domain=company_domain,
                        person_id=person_id,
                        claim_type="location",
                        value=item.location,
                        source_id=source.id,
                        evidence=item.evidence,
                        confidence=confidence,
                        extracted_at=_now(),
                    )
                )
    return list(people_by_id.values()), claims


def _looks_relevant(source: SourceDocument) -> bool:
    title_url = f"{source.title} {source.url}".lower()
    skip_terms = (
        "/jobs",
        "/careers",
        "/templates",
        "template",
        "career",
        "apply for a career",
    )
    if any(term in title_url for term in skip_terms):
        return False

    strong_source_terms = (
        "leadership",
        "management",
        "governance",
        "executive",
        "investor",
        "company",
        "about",
    )
    text = source.text.lower()
    role_terms = (
        "chief",
        "ceo",
        "cto",
        "cfo",
        "cmo",
        "vp",
        "vice president",
        "head of",
        "leadership",
    )
    return any(term in title_url for term in strong_source_terms) and any(
        term in text for term in role_terms
    )


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _confidence_label(value: float) -> str:
    if value >= 0.8:
        return "High"
    if value >= 0.55:
        return "Medium"
    return "Low"
