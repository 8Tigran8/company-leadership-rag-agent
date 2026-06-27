# Company Leadership RAG Agent

CLI-first take-home implementation for collecting public company leadership data, storing cited claims, and answering leadership questions over the collected dataset.

The core design is intentionally lean: SQLite for structured facts, JSON fixtures for reproducible demos, and a real OpenAI-compatible LLM path for live extraction and answer composition. Fixture loading and inspection work without an API key so reviewers can inspect the dataset immediately.

## Quickstart

```bash
uv sync

# Offline fixture demo, no API key required.
uv run company-rag load-fixture data/fixtures/robinhood.com.json
uv run company-rag ask robinhood.com "Who's their CTO?" --no-llm
uv run company-rag ask robinhood.com "How many VPs do they have?" --no-llm
uv run company-rag ask robinhood.com "Who heads marketing?" --no-llm
uv run company-rag ask robinhood.com "Where is their CEO based?" --no-llm

# Inspect the stored dataset.
uv run company-rag inspect robinhood.com --people --sources
```

For the second assignment input:

```bash
uv run company-rag load-fixture data/fixtures/meetcampfire.com.json
uv run company-rag ask meetcampfire.com "Who's their CTO?" --no-llm
```

`meetcampfire.com` redirects to `campfire.ai`; the fixture keeps the assignment domain as the company key and cites current `campfire.ai` public sources.

## Real LLM Mode

The assignment requires real LLM calls and no mocked completions. Set an OpenAI-compatible key for live extraction and LLM answer composition:

```bash
cp .env.example .env
# edit .env and set OPENAI_API_KEY
uv run company-rag ingest https://robinhood.com/ --output-fixture data/fixtures/live-robinhood.json
uv run company-rag ask robinhood.com "Who heads marketing?"
uv run company-rag chat robinhood.com
```

Without `OPENAI_API_KEY`, `ask --no-llm` uses deterministic structured retrieval over the fixture. That mode is not a mocked LLM completion; it is provided so the stored data and retrieval logic are reviewable without secrets.

## CLI

```bash
uv run company-rag load-fixture data/fixtures/robinhood.com.json
uv run company-rag export-fixture robinhood.com data/fixtures/exported-robinhood.json
uv run company-rag inspect robinhood.com --people --sources
uv run company-rag ask robinhood.com "Where is their CEO based?"
uv run company-rag chat robinhood.com
uv run company-rag export-session <session_id> outputs/session.json
uv run company-rag ingest https://robinhood.com/ --output-fixture data/fixtures/live-robinhood.json
```

## Architecture

The system treats leadership data as source-backed claims:

- `people` are canonical entities.
- `claims` are facts about people, such as role, department, or location.
- `sources` store URL, title, fetched time, source type, and evidence text.

Question routing is structured first:

- CTO lookup queries current role claims with `normalized_role = CTO`.
- VP count counts current `VP`, `SVP`, and `EVP` people.
- Marketing lookup searches current marketing/go-to-market leadership claims.
- CEO location only uses person-specific location claims; it does not infer from HQ.

The LLM is used for live extraction and optional final answer composition. Counts and role filtering stay deterministic.

## Fixtures

Committed fixtures:

- `data/fixtures/robinhood.com.json`
- `data/fixtures/meetcampfire.com.json`

Fixture notes:

- Robinhood uses the official IR leadership page, official Vlad Tenev bio, and SEC 8-K evidence for the former CTO case.
- Campfire uses current `campfire.ai` official blogs plus public profile/third-party sources where official leadership pages are sparse.
- Former CTO claims are stored with `status = former` and excluded from current leadership answers.

## Data Policy

Included:

- Current C-level executives.
- Current VP/SVP/EVP roles.
- Current Heads of departments or senior functional leaders.

Excluded by default:

- Board-only members.
- Advisors and investors.
- Former employees.
- Article authors without current leadership roles.

Every answer cites collected source evidence. If a fact is missing, the answer says so directly.

## Environment

See `.env.example`:

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
COMPANY_RAG_DB_PATH=data/company_rag.sqlite
COMPANY_RAG_CACHE_DIR=data/cache
```

The SQLite database, cache, and local runtime artifacts are ignored by git.

## Tests

```bash
uv run pytest
uv run ruff check .
```

Live tests are intended to be marked with `pytest -m live` and skipped when `OPENAI_API_KEY` is absent.

## Limitations

- Public leadership data can be incomplete, especially for private companies.
- Live discovery is intentionally lightweight: sitemap, known paths, domain-specific high-signal seeds, and fetched page text.
- LinkedIn is not scraped behind login. Public profile URLs may be stored as references.
- The fixture reflects public data researched on 2026-06-27 and may become stale.
- No web UI is included; the submitted interface is the CLI.

## Coding-Agent Evidence

`session.json` records the planning and implementation decisions, subagent research, and verification runs.

