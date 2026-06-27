# Verification Report

Generated on 2026-06-27.

## Repository State

- GitHub: `https://github.com/dmitryprotasov-gif/company-leadership-rag-agent`
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
7 passed
```

Covered scenarios:

- CLI help.
- Fixture loading through CLI.
- Domain normalization.
- Role normalization.
- Fixture import.
- Structured question routing for Robinhood.
- Structured question routing for Campfire.

## Fixture Demo Checks

Robinhood fixture:

- Loaded `data/fixtures/robinhood.com.json`.
- CTO question correctly does not return former CTO Jeffrey Pinner as current.
- VP count returns 10 current VP/SVP/EVP leaders.
- Marketing leadership returns Deepak Rao as strongest match and Carley Olivas as related evidence.
- CEO location returns Vlad Tenev as Bay Area of California, using person-specific bio evidence.

Campfire fixture:

- Loaded `data/fixtures/meetcampfire.com.json`.
- CTO question returns Paul Nichols.
- VP count returns 1 current VP/SVP/EVP leader.
- Marketing leadership returns Katrina Queirolo.
- CEO location returns John Glasgow as San Francisco, California, with Medium confidence source caveat.

## Real LLM Smoke

Environment had `OPENAI_API_KEY` present.

Verified:

```bash
uv run company-rag ask meetcampfire.com "Who's their CTO?"
```

The command used LLM answer composition and returned a cited answer for Paul Nichols.

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
- Campfire has sparse official leadership data, so some marketing/location evidence uses public profile or third-party sources with confidence caveats.
