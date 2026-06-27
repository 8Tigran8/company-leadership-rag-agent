from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Citation:
    index: int
    title: str
    url: str
    evidence: str


@dataclass
class RetrievalResult:
    intent: str
    answer: str
    citations: list[Citation] = field(default_factory=list)
    rows: list[dict[str, Any]] = field(default_factory=list)
    needs_llm: bool = True


def retrieve(conn: sqlite3.Connection, domain: str, question: str) -> RetrievalResult:
    text = question.lower()
    if "how many" in text and ("vp" in text or "vice president" in text):
        return _vp_count(conn, domain)
    if "cto" in text or "chief technology" in text:
        return _role_lookup(conn, domain, "CTO", "CTO")
    if "marketing" in text and ("head" in text or "lead" in text or "who" in text):
        return _marketing_leader(conn, domain)
    if "ceo" in text and ("where" in text or "based" in text or "located" in text):
        return _ceo_location(conn, domain)
    if "ceo" in text or "chief executive" in text:
        return _role_lookup(conn, domain, "CEO", "CEO")
    return _leadership_summary(conn, domain)


def _role_lookup(conn: sqlite3.Connection, domain: str, role: str, label: str) -> RetrievalResult:
    rows = conn.execute(
        """
        SELECT p.name, p.profile_url, c.value AS title, c.normalized_role, c.department,
               c.confidence, c.evidence, s.title AS source_title, s.url AS source_url
        FROM claims c
        JOIN people p ON p.id = c.person_id
        JOIN sources s ON s.id = c.source_id
        WHERE c.company_domain = ?
          AND c.claim_type = 'role'
          AND c.status = 'current'
          AND c.normalized_role = ?
        ORDER BY
          CASE c.confidence WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END,
          p.name
        """,
        (domain, role),
    ).fetchall()
    if rows:
        citations = _citations(rows)
        names = ", ".join(f"{row['name']} ({row['title']})" for row in rows)
        return RetrievalResult(
            intent=f"{role.lower()}_lookup",
            answer=f"{names}.",
            citations=citations,
            rows=[dict(row) for row in rows],
        )

    closest = conn.execute(
        """
        SELECT p.name, c.value AS title, c.normalized_role, c.department, c.confidence,
               c.evidence, s.title AS source_title, s.url AS source_url
        FROM claims c
        JOIN people p ON p.id = c.person_id
        JOIN sources s ON s.id = c.source_id
        WHERE c.company_domain = ?
          AND c.claim_type = 'role'
          AND c.status = 'current'
          AND (
            c.department IN ('Engineering', 'Security', 'Product')
            OR c.value LIKE '%Technology%'
          )
        ORDER BY
          CASE c.confidence WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END,
          p.name
        LIMIT 3
        """,
        (domain,),
    ).fetchall()
    citations = _citations(closest)
    answer = f"I could not verify a current {label} in the collected public sources."
    if closest:
        answer += " Closest related leadership evidence: " + "; ".join(
            f"{row['name']} ({row['title']})" for row in closest
        )
    return RetrievalResult(
        intent=f"{role.lower()}_lookup_missing",
        answer=answer,
        citations=citations,
        rows=[dict(row) for row in closest],
    )


def _vp_count(conn: sqlite3.Connection, domain: str) -> RetrievalResult:
    rows = conn.execute(
        """
        SELECT p.name, c.value AS title, c.normalized_role, c.department, c.confidence,
               c.evidence, s.title AS source_title, s.url AS source_url
        FROM claims c
        JOIN people p ON p.id = c.person_id
        JOIN sources s ON s.id = c.source_id
        WHERE c.company_domain = ?
          AND c.claim_type = 'role'
          AND c.status = 'current'
          AND c.normalized_role IN ('VP', 'SVP', 'EVP')
        ORDER BY p.name
        """,
        (domain,),
    ).fetchall()
    people = {row["name"] for row in rows}
    answer = (
        f"I found {len(people)} current VP/SVP/EVP leaders in the collected dataset. "
        "Included roles are VP, SVP, and EVP; board-only, advisor, and former roles are excluded."
    )
    if people:
        answer += " People counted: " + ", ".join(sorted(people)) + "."
    return RetrievalResult(
        intent="vp_count",
        answer=answer,
        citations=_citations(rows),
        rows=[dict(row) for row in rows],
    )


def _marketing_leader(conn: sqlite3.Connection, domain: str) -> RetrievalResult:
    rows = conn.execute(
        """
        SELECT p.name, c.value AS title, c.normalized_role, c.department, c.confidence,
               c.evidence, s.title AS source_title, s.url AS source_url
        FROM claims c
        JOIN people p ON p.id = c.person_id
        JOIN sources s ON s.id = c.source_id
        WHERE c.company_domain = ?
          AND c.claim_type = 'role'
          AND c.status = 'current'
          AND c.department IN ('Marketing', 'Go-to-market')
        ORDER BY
          CASE c.normalized_role
            WHEN 'CMO' THEN 1
            WHEN 'SVP' THEN 2
            WHEN 'EVP' THEN 3
            WHEN 'VP' THEN 4
            WHEN 'HEAD' THEN 5
            WHEN 'DIRECTOR' THEN 6
            ELSE 7
          END,
          CASE c.confidence WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END
        """,
        (domain,),
    ).fetchall()
    if not rows:
        return RetrievalResult(
            intent="marketing_leader_missing",
            answer="I could not verify a current marketing leader in the collected public sources.",
        )

    top = rows[0]
    answer = f"{top['name']} is the strongest match for marketing leadership: {top['title']}."
    if len(rows) > 1:
        answer += " Other related marketing/go-to-market leaders found: " + ", ".join(
            f"{row['name']} ({row['title']})" for row in rows[1:4]
        )
    return RetrievalResult(
        intent="marketing_leader",
        answer=answer,
        citations=_citations(rows),
        rows=[dict(row) for row in rows],
    )


def _ceo_location(conn: sqlite3.Connection, domain: str) -> RetrievalResult:
    ceo_rows = conn.execute(
        """
        SELECT p.id, p.name, c.value AS title, c.evidence,
               s.title AS source_title, s.url AS source_url
        FROM claims c
        JOIN people p ON p.id = c.person_id
        JOIN sources s ON s.id = c.source_id
        WHERE c.company_domain = ?
          AND c.claim_type = 'role'
          AND c.status = 'current'
          AND c.normalized_role = 'CEO'
        ORDER BY CASE c.confidence WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END
        LIMIT 1
        """,
        (domain,),
    ).fetchall()
    if not ceo_rows:
        return RetrievalResult(
            intent="ceo_location_missing",
            answer="I could not verify a current CEO in the collected public sources.",
        )

    ceo = ceo_rows[0]
    location_rows = conn.execute(
        """
        SELECT p.name, c.value AS title, c.confidence, c.evidence,
               s.title AS source_title, s.url AS source_url
        FROM claims c
        JOIN people p ON p.id = c.person_id
        JOIN sources s ON s.id = c.source_id
        WHERE c.company_domain = ?
          AND c.person_id = ?
          AND c.claim_type = 'location'
          AND c.status = 'current'
        ORDER BY CASE c.confidence WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END
        """,
        (domain, ceo["id"]),
    ).fetchall()
    if not location_rows:
        return RetrievalResult(
            intent="ceo_location_unknown",
            answer=(
                f"I verified {ceo['name']} as CEO, but the collected public sources do not state "
                "where the CEO is based. I will not infer a person location "
                "from company headquarters."
            ),
            citations=_citations(ceo_rows),
            rows=[dict(row) for row in ceo_rows],
        )

    location = location_rows[0]
    return RetrievalResult(
        intent="ceo_location",
        answer=f"{location['name']} is listed as based in {location['title']}.",
        citations=_citations(location_rows + ceo_rows),
        rows=[dict(row) for row in location_rows + ceo_rows],
    )


def _leadership_summary(conn: sqlite3.Connection, domain: str) -> RetrievalResult:
    rows = conn.execute(
        """
        SELECT p.name, c.value AS title, c.normalized_role, c.department, c.confidence,
               c.evidence, s.title AS source_title, s.url AS source_url
        FROM claims c
        JOIN people p ON p.id = c.person_id
        JOIN sources s ON s.id = c.source_id
        WHERE c.company_domain = ?
          AND c.claim_type = 'role'
          AND c.status = 'current'
        ORDER BY
          CASE c.normalized_role
            WHEN 'CEO' THEN 1
            WHEN 'CTO' THEN 2
            WHEN 'CFO' THEN 3
            WHEN 'CMO' THEN 4
            WHEN 'SVP' THEN 5
            WHEN 'VP' THEN 6
            ELSE 7
          END,
          p.name
        LIMIT 12
        """,
        (domain,),
    ).fetchall()
    if not rows:
        return RetrievalResult(
            intent="summary_missing",
            answer="No current leadership claims were found for this company in the local dataset.",
        )
    answer = "Collected leadership includes: " + "; ".join(
        f"{row['name']} ({row['title']})" for row in rows
    )
    return RetrievalResult(
        intent="leadership_summary",
        answer=answer,
        citations=_citations(rows),
        rows=[dict(row) for row in rows],
    )


def _citations(rows: list[sqlite3.Row]) -> list[Citation]:
    citations: list[Citation] = []
    seen: set[tuple[str, str]] = set()
    for row in rows:
        key = (row["source_url"], row["evidence"])
        if key in seen:
            continue
        seen.add(key)
        citations.append(
            Citation(
                index=len(citations) + 1,
                title=row["source_title"],
                url=row["source_url"],
                evidence=row["evidence"],
            )
        )
    return citations
