from __future__ import annotations

from datetime import UTC, datetime

from company_rag.config import Settings
from company_rag.db import insert_claim, insert_company, insert_person, insert_source
from company_rag.models import Company, Fixture
from company_rag.normalize import normalize_domain
from company_rag.pipeline.discover import discover_sources
from company_rag.pipeline.extract import extract_claims_from_sources
from company_rag.pipeline.fetch import fetch_source


def ingest_company(settings: Settings, conn, input_url: str, *, limit: int = 30) -> Fixture:
    domain = normalize_domain(input_url)
    company = Company(domain=domain, name=_company_name(domain), website_url=input_url)
    urls = discover_sources(input_url, limit=limit)
    sources = []
    for url in urls:
        source = fetch_source(url, company_domain=domain, cache_dir=settings.cache_dir / domain)
        if source is not None:
            sources.append(source)

    people, claims = extract_claims_from_sources(
        settings,
        company_name=company.name,
        company_domain=domain,
        sources=sources,
    )

    insert_company(conn, company)
    for source in sources:
        insert_source(conn, source)
    for person in people:
        insert_person(conn, person)
    for claim in claims:
        insert_claim(conn, claim)
    conn.commit()

    return Fixture(
        company=company,
        sources=sources,
        people=people,
        claims=claims,
        generated_at=datetime.now(UTC).isoformat(),
        notes=[f"Live ingestion fetched {len(sources)} sources from {len(urls)} discovered URLs."],
    )


def _company_name(domain: str) -> str:
    stem = domain.split(".")[0]
    if stem == "meetcampfire":
        return "Campfire"
    return stem.replace("-", " ").title()

