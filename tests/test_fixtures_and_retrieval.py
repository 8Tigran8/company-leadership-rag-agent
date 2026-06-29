from pathlib import Path

from company_rag.config import Settings
from company_rag.db import connect, load_fixture
from company_rag.fixtures import read_fixture
from company_rag.pipeline.structured import extract_structured_leadership
from company_rag.rag.retriever import retrieve


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        db_path=tmp_path / "test.sqlite",
        cache_dir=tmp_path / "cache",
        llm_provider="openai",
        openai_api_key=None,
        openai_model="gpt-4.1-mini",
    )


def test_fixture_load_and_robinhood_required_questions(tmp_path: Path) -> None:
    fixture = read_fixture(Path("data/fixtures/robinhood.com.json"))
    settings = _settings(tmp_path)
    with connect(settings.db_path) as conn:
        load_fixture(conn, fixture)

        cto = retrieve(conn, "robinhood.com", "Who's their CTO?")
        assert "could not verify a current CTO" in cto.answer
        assert "Jeffrey Pinner" not in cto.answer

        vp_count = retrieve(conn, "robinhood.com", "How many VPs do they have?")
        assert "12 current VP/SVP/EVP" in vp_count.answer
        assert "Chris Koegel" in vp_count.answer
        assert "Seok Lee" in vp_count.answer

        marketing = retrieve(conn, "robinhood.com", "Who heads marketing?")
        assert "Deepak Rao" in marketing.answer

        location = retrieve(conn, "robinhood.com", "Where is their CEO based?")
        assert "Bay Area of California" in location.answer


def test_fixture_load_and_campfire_required_questions(tmp_path: Path) -> None:
    fixture = read_fixture(Path("data/fixtures/meetcampfire.com.json"))
    settings = _settings(tmp_path)
    with connect(settings.db_path) as conn:
        load_fixture(conn, fixture)

        assert "Paul Nichols" in retrieve(conn, "meetcampfire.com", "Who's their CTO?").answer
        assert "1 current VP/SVP/EVP" in retrieve(
            conn, "meetcampfire.com", "How many VPs do they have?"
        ).answer
        assert "Katrina Queirolo" in retrieve(
            conn, "meetcampfire.com", "Who heads marketing?"
        ).answer
        assert "San Francisco, California" in retrieve(
            conn, "meetcampfire.com", "Where is their CEO based?"
        ).answer


def test_robinhood_fixture_covers_full_structured_leadership_source() -> None:
    fixture = read_fixture(Path("data/fixtures/robinhood.com.json"))
    leadership_source = next(
        source for source in fixture.sources if source.id == "src_robinhood_leadership"
    )
    _, extracted_claims = extract_structured_leadership(leadership_source)

    fixture_claims = [
        claim
        for claim in fixture.claims
        if claim.source_id == leadership_source.id
        and claim.claim_type == "role"
        and claim.status == "current"
    ]
    extracted_pairs = {(claim.person_id, claim.value) for claim in extracted_claims}
    fixture_pairs = {(claim.person_id, claim.value) for claim in fixture_claims}

    assert fixture_pairs == extracted_pairs
    assert len(fixture_claims) == 23
    assert sum(claim.normalized_role in {"VP", "SVP", "EVP"} for claim in fixture_claims) == 12
    assert all("Jason Warnick" not in claim.evidence for claim in fixture_claims)


def test_fixture_claims_are_supported_by_stored_source_text() -> None:
    for path in [
        Path("data/fixtures/robinhood.com.json"),
        Path("data/fixtures/meetcampfire.com.json"),
    ]:
        fixture = read_fixture(path)
        sources = {source.id: source for source in fixture.sources}
        people = {person.id: person for person in fixture.people}

        for claim in fixture.claims:
            source_text = sources[claim.source_id].text
            person_name = people[claim.person_id].name
            assert person_name in source_text
            assert claim.value in source_text
