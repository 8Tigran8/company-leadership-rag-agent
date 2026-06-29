from __future__ import annotations

import re
from datetime import UTC, datetime

from company_rag.models import Claim, Person, SourceDocument
from company_rag.normalize import is_excluded_title, normalize_title, slugify

ROLE_CUES = (
    "chief",
    "vp",
    "vice president",
    "president",
    "head of",
    "general manager",
    "managing director",
    "senior director",
    "director",
    "strategic advisor",
)


def extract_structured_leadership(source: SourceDocument) -> tuple[list[Person], list[Claim]]:
    """Extract deterministic leadership mentions before falling back to LLM extraction."""
    people: list[Person] = []
    claims: list[Claim] = []
    seen_people: set[str] = set()
    seen_claims: set[tuple[str, str, str]] = set()

    def add_role_claim(
        *,
        name: str,
        title: str,
        evidence: str,
        confidence: str,
        extraction_method: str,
    ) -> None:
        if is_excluded_title(title):
            return

        normalized = normalize_title(title)
        if normalized.normalized_role is None:
            return

        person_id = f"person_{slugify(source.company_domain)}_{slugify(name)}"
        if person_id not in seen_people:
            seen_people.add(person_id)
            people.append(
                Person(
                    id=person_id,
                    company_domain=source.company_domain,
                    name=name,
                    metadata={"extraction_method": extraction_method},
                )
            )

        claim_key = (person_id, title, source.id)
        if claim_key in seen_claims:
            return
        seen_claims.add(claim_key)
        claims.append(
            Claim(
                id=(
                    f"claim_{slugify(source.company_domain)}_{slugify(name)}_"
                    f"{slugify(title)}"
                ),
                company_domain=source.company_domain,
                person_id=person_id,
                claim_type="role",
                value=title,
                normalized_role=normalized.normalized_role,
                seniority=normalized.seniority,
                department=normalized.department,
                status="current",
                source_id=source.id,
                evidence=evidence,
                confidence=confidence,
                extracted_at=_now(),
                metadata={"extraction_method": extraction_method},
            )
        )

    if _is_structured_leadership_source(source):
        for name, title in _name_title_pairs(source.text):
            add_role_claim(
                name=name,
                title=title,
                evidence=f"The official leadership page lists {name} as {title}.",
                confidence="High",
                extraction_method="structured_roster",
            )

    for name, title, evidence in _inline_role_mentions(source):
        add_role_claim(
            name=name,
            title=title,
            evidence=evidence,
            confidence="Medium",
            extraction_method="inline_role_mention",
        )
    return people, claims


def _is_structured_leadership_source(source: SourceDocument) -> bool:
    url = source.url.lower()
    title = source.title.lower()
    source_type = source.source_type.lower()
    return (
        "leadership" in title
        and ("official" in source_type or "investor" in url or "governance" in url)
    )


def _name_title_pairs(text: str) -> list[tuple[str, str]]:
    lines = [_clean_line(line) for line in text.splitlines()]
    lines = [line for line in lines if line]

    pairs: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    pairs_started = False
    for index, line in enumerate(lines[:-1]):
        if pairs_started and _is_stop_line(line):
            break
        title = lines[index + 1]
        if not _looks_like_name(line) or not _looks_like_title(title):
            continue
        key = (line, title)
        if key in seen:
            continue
        pairs_started = True
        seen.add(key)
        pairs.append(key)
    return pairs


def _clean_line(line: str) -> str:
    return " ".join(line.strip().split())


def _looks_like_name(line: str) -> bool:
    if len(line) > 60:
        return False
    lowered = line.lower()
    if any(cue in lowered for cue in ROLE_CUES):
        return False
    parts = line.replace(",", "").split()
    if not 2 <= len(parts) <= 5:
        return False
    return all(part[:1].isupper() or part.isupper() for part in parts)


def _looks_like_title(line: str) -> bool:
    lowered = line.lower()
    return any(cue in lowered for cue in ROLE_CUES)


def _is_stop_line(line: str) -> bool:
    lowered = line.lower()
    return lowered in {"board of directors", "committee composition", "governance documents"}


def _inline_role_mentions(source: SourceDocument) -> list[tuple[str, str, str]]:
    text = _clean_line(source.text)
    company_hints = _company_hints(source.company_domain)
    mentions: list[tuple[str, str, str]] = []

    title_pattern = (
        r"Chief [A-Z][A-Za-z&,\- ]+? Officer|"
        r"CEO|CTO|CFO|CMO|COO|CISO|CIO|"
        r"SVP|EVP|VP|"
        r"Head of [A-Z][A-Za-z&,\- ]+|"
        r"Founder(?: and CEO)?|"
        r"CEO and Founder|Founder and CEO"
    )
    name_pattern = r"[A-Z][A-Za-z'.-]+(?:\s+[A-Z][A-Za-z'.-]+){1,3}"

    patterns = [
        re.compile(
            rf"\bled by (?P<title>{title_pattern}) (?P<name>{name_pattern})\b",
            re.IGNORECASE,
        ),
        re.compile(
            rf"\b(?P<name>{name_pattern}),\s+(?P<title>{title_pattern})\s+"
            r"(?:of|at|for)\s+(?P<company>[A-Z][A-Za-z0-9& .'-]{2,80})",
            re.IGNORECASE,
        ),
    ]

    seen: set[tuple[str, str]] = set()
    for pattern in patterns:
        for match in pattern.finditer(text):
            company = match.groupdict().get("company")
            if company and not _company_matches(company, company_hints):
                continue
            name = _clean_inline_value(match.group("name"))
            title = _clean_inline_value(match.group("title"))
            key = (name, title)
            if key in seen or not _looks_like_name(name):
                continue
            seen.add(key)
            mentions.append((name, title, _sentence_evidence(text, match.start(), match.end())))
    return mentions


def _clean_inline_value(value: str) -> str:
    return " ".join(value.strip(" ,.;:").split())


def _company_hints(domain: str) -> set[str]:
    stem = domain.split(".")[0].lower().replace("-", "")
    hints = {stem}
    if stem.startswith("meet") and len(stem) > 4:
        hints.add(stem[4:])
    return hints


def _company_matches(company: str, hints: set[str]) -> bool:
    normalized = re.sub(r"[^a-z0-9]+", "", company.lower())
    return any(hint and hint in normalized for hint in hints)


def _sentence_evidence(text: str, start: int, end: int) -> str:
    left = text.rfind(".", 0, start)
    right = text.find(".", end)
    left = 0 if left == -1 else left + 1
    right = len(text) if right == -1 else right + 1
    evidence = _clean_line(text[left:right])
    return evidence[:500]


def _now() -> str:
    return datetime.now(UTC).isoformat()
