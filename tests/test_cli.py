from typer.testing import CliRunner

from company_rag.cli import app


def test_cli_help() -> None:
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Company Leadership RAG Agent" in result.output

