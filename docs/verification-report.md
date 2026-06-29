# Verification Report

Generated on 2026-06-29.

## Repository State

- GitHub: `https://github.com/8Tigran8/company-leadership-rag-agent`
- Default branch: `main`
- Visibility: public

## Automated Checks

Passed:

```bash
uv run company-rag --help
uv run pytest
uv run ruff check .
```

Observed test result:

```text
13 passed
```

Covered scenarios:

- CLI help.
- Fixture loading through CLI.
- Domain normalization.
- Role normalization.
- Fixture import.
- Structured official leadership roster extraction.
- Deterministic inline role extraction for explicit live-source sentences.
- LLM extraction payload normalization for empty optional fields.
- Fixture claim/source-text support checks.
- Structured question routing for Robinhood.
- Structured question routing for Campfire.
- Visible local-retrieval fallback warning when `OPENAI_API_KEY` is absent.

## Fixture Demo Checks

Robinhood fixture:

- Loaded `data/fixtures/robinhood.com.json`.
- CTO question correctly does not return former CTO Jeffrey Pinner as current.
- VP count returns 12 current VP/SVP/EVP leaders from the official leadership roster.
- Marketing leadership returns Deepak Rao as strongest match and Carley Olivas as related evidence.
- CEO location returns Vlad Tenev as Bay Area of California, using person-specific bio evidence.
- The official leadership roster source text contains all stored name/title pairs and excludes Strategic Advisor Jason Warnick from current operating leadership answers.

Campfire fixture:

- Loaded `data/fixtures/meetcampfire.com.json`.
- CTO question returns Paul Nichols.
- VP count returns 1 current VP/SVP/EVP leader.
- Marketing leadership returns Katrina Queirolo.
- CEO location returns John Glasgow as San Francisco, California, with Medium confidence source caveat.

## Real LLM Smoke

OpenAI API path was checked locally on 2026-06-29. The SDK reached OpenAI but the available key returned `429 insufficient_quota`, so the final completion was not run through that key.

Codex subscription-backed LLM composition was verified without an API key:

```bash
unset OPENAI_API_KEY
LLM_PROVIDER=codex \
CODEX_TIMEOUT_SECONDS=90 \
COMPANY_RAG_DB_PATH=/tmp/company-rag-codex.sqlite \
uv run company-rag ask meetcampfire.com "Who's their CTO?"
```

Observed answer:

```text
Paul Nichols is their Chief Technology Officer (CTO) [1].
```

This mode uses official `codex exec` with local ChatGPT/Codex subscription auth. It is intended as an optional local review path; reviewers can still use `OPENAI_API_KEY`, Ollama, or `--no-llm`.

Codex-backed live ingest was also verified end-to-end:

```bash
unset OPENAI_API_KEY
LLM_PROVIDER=codex \
CODEX_TIMEOUT_SECONDS=180 \
COMPANY_RAG_DB_PATH=/tmp/company-rag-live-codex-fixed2.sqlite \
COMPANY_RAG_CACHE_DIR=/tmp/company-rag-live-codex-fixed2-cache \
uv run company-rag ingest https://meetcampfire.com --limit 8 \
  --output-fixture /tmp/company-rag-live-codex-fixed2-fixture.json

LLM_PROVIDER=codex \
COMPANY_RAG_DB_PATH=/tmp/company-rag-live-codex-fixed2.sqlite \
uv run company-rag ask meetcampfire.com "Who's their CTO?"
```

Result:

- Ingested `meetcampfire.com`.
- Extracted 2 people and 2 claims from 5 sources.
- `inspect` showed John Glasgow and Paul Nichols.
- The CTO question returned Paul Nichols with a citation to the live-fetched Campfire Claude article.

## Live Ingest Smoke On Third Company

Ran live ingest on Asana:

```bash
COMPANY_RAG_DB_PATH=/tmp/company-rag-asana.sqlite \
COMPANY_RAG_CACHE_DIR=/tmp/company-rag-asana-cache \
uv run company-rag ingest https://asana.com --limit 15 --output-fixture /tmp/asana-fixture.json
```

Result:

- Ingested `asana.com`.
- Extracted 8 people and 9 claims from 7 sources.
- CEO question returned Dan Rogers from Asana's official leadership page.
- CTO question returned Amritansh Raghav from Asana's official leadership page.
- VP count returned 0, which is acceptable when collected sources contain C-level leadership but no VP/SVP/EVP roles.

During this smoke test, a quality issue was found and fixed:

- Sitemap discovery initially fetched jobs/template pages.
- LLM extraction from a jobs page produced a conflicting stale-looking CEO claim.
- The extraction filter now skips jobs/careers/templates and deduplicates fetched sources after redirects.

## Archive Check

The generated zip excludes:

- `.git`
- `.venv`
- `.pytest_cache`
- `.ruff_cache`
- `__pycache__`
- local SQLite files

## Remaining Caveats

- Live discovery is lightweight and intentionally not a full web-search system.
- External search APIs are optional and not required for the fixture demo.
- Public company leadership pages can change; fixtures are dated.
- Robinhood's investor site can be slow or block plain HTTP clients; the committed fixture keeps the official roster text so coverage can be verified offline.
- Campfire has sparse official leadership data, so some marketing/location evidence uses public profile or third-party sources with confidence caveats.
