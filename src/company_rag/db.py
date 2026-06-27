from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from company_rag.models import Claim, Company, Fixture, Person, SourceDocument

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS companies (
  domain TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  website_url TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sources (
  id TEXT PRIMARY KEY,
  company_domain TEXT NOT NULL,
  url TEXT NOT NULL,
  title TEXT NOT NULL,
  source_type TEXT NOT NULL,
  fetched_at TEXT NOT NULL,
  text TEXT NOT NULL,
  confidence TEXT NOT NULL,
  metadata_json TEXT NOT NULL,
  FOREIGN KEY(company_domain) REFERENCES companies(domain) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS people (
  id TEXT PRIMARY KEY,
  company_domain TEXT NOT NULL,
  name TEXT NOT NULL,
  profile_url TEXT,
  metadata_json TEXT NOT NULL,
  FOREIGN KEY(company_domain) REFERENCES companies(domain) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS claims (
  id TEXT PRIMARY KEY,
  company_domain TEXT NOT NULL,
  person_id TEXT NOT NULL,
  claim_type TEXT NOT NULL,
  value TEXT NOT NULL,
  normalized_role TEXT,
  seniority TEXT,
  department TEXT,
  status TEXT NOT NULL,
  source_id TEXT NOT NULL,
  evidence TEXT NOT NULL,
  confidence TEXT NOT NULL,
  extracted_at TEXT NOT NULL,
  metadata_json TEXT NOT NULL,
  FOREIGN KEY(company_domain) REFERENCES companies(domain) ON DELETE CASCADE,
  FOREIGN KEY(person_id) REFERENCES people(id) ON DELETE CASCADE,
  FOREIGN KEY(source_id) REFERENCES sources(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chat_sessions (
  id TEXT PRIMARY KEY,
  company_domain TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(company_domain) REFERENCES companies(domain) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chat_messages (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at TEXT NOT NULL,
  citations_json TEXT NOT NULL,
  FOREIGN KEY(session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_claims_company_role ON claims(company_domain, normalized_role);
CREATE INDEX IF NOT EXISTS idx_claims_company_department ON claims(company_domain, department);
CREATE INDEX IF NOT EXISTS idx_claims_person ON claims(person_id);
"""


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    init_db(conn)
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()


def clear_company(conn: sqlite3.Connection, domain: str) -> None:
    conn.execute("DELETE FROM companies WHERE domain = ?", (domain,))
    conn.commit()


def insert_company(conn: sqlite3.Connection, company: Company) -> None:
    conn.execute(
        """
        INSERT INTO companies(domain, name, website_url, updated_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(domain) DO UPDATE SET
          name = excluded.name,
          website_url = excluded.website_url,
          updated_at = CURRENT_TIMESTAMP
        """,
        (company.domain, company.name, company.website_url),
    )


def insert_source(conn: sqlite3.Connection, source: SourceDocument) -> None:
    conn.execute(
        """
        INSERT OR REPLACE INTO sources(
          id, company_domain, url, title, source_type, fetched_at, text, confidence, metadata_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            source.id,
            source.company_domain,
            source.url,
            source.title,
            source.source_type,
            source.fetched_at,
            source.text,
            source.confidence,
            json.dumps(source.metadata, sort_keys=True),
        ),
    )


def insert_person(conn: sqlite3.Connection, person: Person) -> None:
    conn.execute(
        """
        INSERT OR REPLACE INTO people(id, company_domain, name, profile_url, metadata_json)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            person.id,
            person.company_domain,
            person.name,
            person.profile_url,
            json.dumps(person.metadata, sort_keys=True),
        ),
    )


def insert_claim(conn: sqlite3.Connection, claim: Claim) -> None:
    conn.execute(
        """
        INSERT OR REPLACE INTO claims(
          id, company_domain, person_id, claim_type, value, normalized_role, seniority,
          department, status, source_id, evidence, confidence, extracted_at, metadata_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            claim.id,
            claim.company_domain,
            claim.person_id,
            claim.claim_type,
            claim.value,
            claim.normalized_role,
            claim.seniority,
            claim.department,
            claim.status,
            claim.source_id,
            claim.evidence,
            claim.confidence,
            claim.extracted_at,
            json.dumps(claim.metadata, sort_keys=True),
        ),
    )


def load_fixture(conn: sqlite3.Connection, fixture: Fixture) -> None:
    clear_company(conn, fixture.company.domain)
    insert_company(conn, fixture.company)
    for source in fixture.sources:
        insert_source(conn, source)
    for person in fixture.people:
        insert_person(conn, person)
    for claim in fixture.claims:
        insert_claim(conn, claim)
    conn.commit()


def company_exists(conn: sqlite3.Connection, domain: str) -> bool:
    row = conn.execute("SELECT 1 FROM companies WHERE domain = ?", (domain,)).fetchone()
    return row is not None


def get_company(conn: sqlite3.Connection, domain: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM companies WHERE domain = ?", (domain,)).fetchone()


def list_sources(conn: sqlite3.Connection, domain: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM sources WHERE company_domain = ? ORDER BY confidence DESC, title",
        (domain,),
    ).fetchall()


def list_people(conn: sqlite3.Connection, domain: str) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT
          p.id,
          p.name,
          p.profile_url,
          GROUP_CONCAT(
            CASE WHEN c.claim_type = 'role' THEN c.value END,
            '; '
          ) AS roles
        FROM people p
        LEFT JOIN claims c ON c.person_id = p.id AND c.claim_type = 'role'
        WHERE p.company_domain = ?
        GROUP BY p.id, p.name, p.profile_url
        ORDER BY p.name
        """,
        (domain,),
    ).fetchall()


def fixture_from_db(conn: sqlite3.Connection, domain: str, generated_at: str) -> Fixture:
    company_row = get_company(conn, domain)
    if company_row is None:
        raise ValueError(f"No company found for {domain}.")

    sources = [
        SourceDocument(
            id=row["id"],
            company_domain=row["company_domain"],
            url=row["url"],
            title=row["title"],
            source_type=row["source_type"],
            fetched_at=row["fetched_at"],
            text=row["text"],
            confidence=row["confidence"],
            metadata=json.loads(row["metadata_json"]),
        )
        for row in conn.execute(
            "SELECT * FROM sources WHERE company_domain = ? ORDER BY id",
            (domain,),
        )
    ]
    people = [
        Person(
            id=row["id"],
            company_domain=row["company_domain"],
            name=row["name"],
            profile_url=row["profile_url"],
            metadata=json.loads(row["metadata_json"]),
        )
        for row in conn.execute(
            "SELECT * FROM people WHERE company_domain = ? ORDER BY id",
            (domain,),
        )
    ]
    claims = [
        Claim(
            id=row["id"],
            company_domain=row["company_domain"],
            person_id=row["person_id"],
            claim_type=row["claim_type"],
            value=row["value"],
            normalized_role=row["normalized_role"],
            seniority=row["seniority"],
            department=row["department"],
            status=row["status"],
            source_id=row["source_id"],
            evidence=row["evidence"],
            confidence=row["confidence"],
            extracted_at=row["extracted_at"],
            metadata=json.loads(row["metadata_json"]),
        )
        for row in conn.execute(
            "SELECT * FROM claims WHERE company_domain = ? ORDER BY id",
            (domain,),
        )
    ]

    return Fixture(
        company=Company(
            domain=company_row["domain"],
            name=company_row["name"],
            website_url=company_row["website_url"],
        ),
        sources=sources,
        people=people,
        claims=claims,
        generated_at=generated_at,
    )


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]


def get_chat_session(conn: sqlite3.Connection, session_id: str) -> dict[str, Any]:
    session = conn.execute("SELECT * FROM chat_sessions WHERE id = ?", (session_id,)).fetchone()
    if session is None:
        raise ValueError(f"No chat session found for {session_id}.")
    messages = conn.execute(
        "SELECT * FROM chat_messages WHERE session_id = ? ORDER BY created_at, id",
        (session_id,),
    ).fetchall()
    return {
        "session": dict(session),
        "messages": [
            {
                **dict(message),
                "citations": json.loads(message["citations_json"]),
            }
            for message in messages
        ],
    }
