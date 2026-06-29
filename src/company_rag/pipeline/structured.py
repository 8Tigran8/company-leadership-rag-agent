from __future__ import annotations

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
    """Extract complete name/title roster pairs from official structured leadership pages."""
    if not _is_structured_leadership_source(source):
        return [], []

    people: list[Person] = []
    claims: list[Claim] = []
    seen_people: set[str] = set()
    for name, title in _name_title_pairs(source.text):
        if is_excluded_title(title):
            continue

        normalized = normalize_title(title)
        if normalized.normalized_role is None:
            continue

        person_id = f"person_{slugify(source.company_domain)}_{slugify(name)}"
        if person_id not in seen_people:
            seen_people.add(person_id)
            people.append(
                Person(
                    id=person_id,
                    company_domain=source.company_domain,
                    name=name,
                    metadata={"extraction_method": "structured_roster"},
                )
            )

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
                evidence=(
                    f"The official leadership page lists {name} as {title}."
                ),
                confidence="High",
                extracted_at=_now(),
                metadata={"extraction_method": "structured_roster"},
            )
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


def _now() -> str:
    return datetime.now(UTC).isoformat()
