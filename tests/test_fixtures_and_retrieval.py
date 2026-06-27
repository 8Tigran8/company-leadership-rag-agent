from pathlib import Path

from company_rag.config import Settings
from company_rag.db import connect, load_fixture
from company_rag.fixtures import read_fixture
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
        assert "10 current VP/SVP/EVP" in vp_count.answer

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

