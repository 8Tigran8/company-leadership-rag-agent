from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from company_rag.answerer import answer_question, create_chat_session, save_chat_message
from company_rag.config import get_settings
from company_rag.db import (
    company_exists,
    connect,
    fixture_from_db,
    get_chat_session,
    list_people,
    list_sources,
)
from company_rag.db import (
    load_fixture as load_fixture_into_db,
)
from company_rag.fixtures import read_fixture, write_fixture
from company_rag.llm import LLMUnavailableError
from company_rag.normalize import normalize_domain
from company_rag.pipeline.run import ingest_company

app = typer.Typer(help="Company Leadership RAG Agent")
console = Console()


@app.callback()
def main() -> None:
    """Inspect, ingest, and chat with company leadership data."""


@app.command()
def load_fixture(path: Path) -> None:
    """Load a committed JSON fixture into the local SQLite store."""
    settings = get_settings()
    fixture = read_fixture(path)
    with connect(settings.db_path) as conn:
        load_fixture_into_db(conn, fixture)
    console.print(
        f"Loaded fixture for [bold]{fixture.company.domain}[/bold]: "
        f"{len(fixture.people)} people, {len(fixture.claims)} claims, "
        f"{len(fixture.sources)} sources."
    )


@app.command()
def export_fixture(domain: str, path: Path) -> None:
    """Export a company dataset from SQLite into a deterministic JSON fixture."""
    settings = get_settings()
    normalized = normalize_domain(domain)
    with connect(settings.db_path) as conn:
        fixture = fixture_from_db(conn, normalized, generated_at="manual-export")
    write_fixture(path, fixture)
    console.print(f"Exported fixture for [bold]{normalized}[/bold] to {path}.")


@app.command()
def inspect(
    domain: str,
    people: Annotated[bool, typer.Option("--people", help="Show people and roles.")] = False,
    sources: Annotated[
        bool,
        typer.Option("--sources", help="Show collected sources."),
    ] = False,
) -> None:
    """Inspect stored people and sources for a company."""
    settings = get_settings()
    normalized = normalize_domain(domain)
    with connect(settings.db_path) as conn:
        if not company_exists(conn, normalized):
            raise typer.BadParameter(
                f"No local dataset for {normalized}. Load a fixture or run ingest."
            )
        if not people and not sources:
            people = sources = True
        if people:
            _print_people(conn, normalized)
        if sources:
            _print_sources(conn, normalized)


@app.command()
def ask(
    domain: str,
    question: str,
    no_llm: Annotated[
        bool,
        typer.Option("--no-llm", help="Use deterministic retrieval answer only."),
    ] = False,
) -> None:
    """Ask one question over a stored company dataset."""
    settings = get_settings()
    normalized = normalize_domain(domain)
    with connect(settings.db_path) as conn:
        if not company_exists(conn, normalized):
            raise typer.BadParameter(
                f"No local dataset for {normalized}. Load a fixture or run ingest."
            )
        answer, result = answer_question(
            conn,
            settings,
            domain=normalized,
            question=question,
            use_llm=not no_llm,
        )
    console.print(answer)
    _print_citations(result)


@app.command()
def chat(
    domain: str,
    no_llm: Annotated[
        bool,
        typer.Option("--no-llm", help="Use deterministic retrieval answer only."),
    ] = False,
) -> None:
    """Start an interactive chat over a stored company dataset."""
    settings = get_settings()
    normalized = normalize_domain(domain)
    with connect(settings.db_path) as conn:
        if not company_exists(conn, normalized):
            raise typer.BadParameter(
                f"No local dataset for {normalized}. Load a fixture or run ingest."
            )
        session_id = create_chat_session(conn, normalized)
        console.print(f"Chat session: [bold]{session_id}[/bold]. Type 'exit' to quit.")
        while True:
            question = typer.prompt("You")
            if question.strip().lower() in {"exit", "quit", ":q"}:
                break
            save_chat_message(conn, session_id=session_id, role="user", content=question)
            answer, result = answer_question(
                conn,
                settings,
                domain=normalized,
                question=question,
                use_llm=not no_llm,
            )
            citations = [citation.__dict__ for citation in result.citations]
            save_chat_message(
                conn,
                session_id=session_id,
                role="assistant",
                content=answer,
                citations_json=json.dumps(citations),
            )
            console.print(answer)
            _print_citations(result)


@app.command()
def export_session(session_id: str, path: Path) -> None:
    """Export a chat session from SQLite as JSON."""
    settings = get_settings()
    with connect(settings.db_path) as conn:
        payload = get_chat_session(conn, session_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    console.print(f"Exported session [bold]{session_id}[/bold] to {path}.")


@app.command()
def ingest(
    url: str,
    output_fixture: Annotated[
        Path | None,
        typer.Option(
            "--output-fixture",
            help="Optional path to write the collected dataset fixture.",
        ),
    ] = None,
    limit: Annotated[int, typer.Option("--limit", min=1, max=80)] = 30,
) -> None:
    """Run live source discovery, fetching, LLM extraction, and storage."""
    settings = get_settings()
    if not settings.openai_api_key:
        raise typer.BadParameter(
            "OPENAI_API_KEY is required for live LLM extraction. "
            "Use load-fixture for offline demo mode."
        )
    with connect(settings.db_path) as conn:
        try:
            fixture = ingest_company(settings, conn, url, limit=limit)
        except LLMUnavailableError as exc:
            raise typer.BadParameter(str(exc)) from exc
    console.print(
        f"Ingested [bold]{fixture.company.domain}[/bold]: "
        f"{len(fixture.people)} people, {len(fixture.claims)} claims, "
        f"{len(fixture.sources)} sources."
    )
    if output_fixture is not None:
        write_fixture(output_fixture, fixture)
        console.print(f"Wrote fixture to {output_fixture}.")


def _print_people(conn, domain: str) -> None:
    table = Table(title=f"People for {domain}")
    table.add_column("Name")
    table.add_column("Roles")
    table.add_column("Profile")
    for row in list_people(conn, domain):
        table.add_row(row["name"], row["roles"] or "", row["profile_url"] or "")
    console.print(table)


def _print_sources(conn, domain: str) -> None:
    table = Table(title=f"Sources for {domain}")
    table.add_column("Title")
    table.add_column("Confidence")
    table.add_column("URL")
    for row in list_sources(conn, domain):
        table.add_row(row["title"], row["confidence"], row["url"])
    console.print(table)


def _print_citations(result) -> None:
    if not result.citations:
        console.print("\nSources: none in collected data.")
        return
    console.print("\nSources:")
    for citation in result.citations:
        console.print(f"[{citation.index}] {citation.title} - {citation.url}")
        console.print(f"    {citation.evidence}")
