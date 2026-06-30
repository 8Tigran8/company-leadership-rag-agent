# Delivery Checklist

## Repository

- [x] `README.md` explains the problem and solution.
- [x] `pyproject.toml` and `uv.lock` exist.
- [x] `.env.example` documents required secrets and provider settings.
- [x] No secrets committed.
- [x] License file intentionally omitted; the assignment did not request redistribution terms.
- [x] Repo runs from a fresh clone (`uv sync --frozen`, fixture smoke, and tests verified on 2026-06-30).

## Ingestion

- [x] Accepts both full URL and domain.
- [x] Discovers likely leadership pages from known paths, sitemap entries, and domain-specific seeds.
- [x] Fetches and caches source pages.
- [x] Stores source metadata and text.
- [x] Uses real LLM structured extraction through OpenAI-compatible providers, Codex CLI, or Ollama.
- [x] Validates extracted people and claims, including empty optional LLM fields.
- [x] Handles no-data cases gracefully.

## Storage

- [x] SQLite schema exists.
- [x] People and claims are separate.
- [x] Sources and evidence snippets are stored.
- [x] Fixture export is deterministic.
- [x] Fixture import works without network.

## Chat

- [x] `ask` command works for one-off questions.
- [x] `chat` command works interactively.
- [x] Answers include citations.
- [x] CTO lookup works.
- [x] VP count works.
- [x] Marketing leader lookup works.
- [x] CEO location lookup works.
- [x] Missing facts are reported honestly.

## Data Fixtures

- [x] Robinhood fixture committed.
- [x] Campfire fixture committed.
- [x] Fixture generation date is recorded.
- [x] Fixture source URLs are preserved.
- [x] Golden questions are covered by README examples, tests, and verification report.

## Tests

- [x] Domain normalization tests.
- [x] Role normalization tests.
- [x] Dedupe/merge coverage through structured roster extraction and fixture coverage tests.
- [x] Fixture load tests.
- [x] Structured chat routing tests.
- [x] Live checks are documented as manual smoke tests so the automated suite runs without keys.

## Submission

- [x] `session.json` included.
- [x] README includes example transcript.
- [x] README includes known limitations and tradeoffs.
- [x] Final smoke test run is recorded in `docs/verification-report.md` and `session.json`.
