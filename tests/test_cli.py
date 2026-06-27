from typer.testing import CliRunner

from company_rag.cli import app

runner = CliRunner()


def test_cli_help() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Company Leadership RAG Agent" in result.output


def test_cli_load_fixture_and_ask(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("COMPANY_RAG_DB_PATH", str(tmp_path / "cli.sqlite"))
    load_result = runner.invoke(app, ["load-fixture", "data/fixtures/meetcampfire.com.json"])
    assert load_result.exit_code == 0
    assert "Loaded fixture" in load_result.output

    ask_result = runner.invoke(
        app,
        ["ask", "meetcampfire.com", "Who's their CTO?", "--no-llm"],
    )
    assert ask_result.exit_code == 0
    assert "Paul Nichols" in ask_result.output
    assert "Sources:" in ask_result.output
