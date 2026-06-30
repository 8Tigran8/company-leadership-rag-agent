# Evaluation Metrics

Generated on 2026-06-30 from the repository state after commit `49a5912`.

## Reproducible Metrics Command

```bash
uv run python scripts/evaluate.py
```

The script loads committed fixtures into temporary SQLite databases, runs the required golden questions, checks citation/evidence coverage, and exits non-zero if a threshold fails.

## Scorecard

| Area | Metric | Result | Status |
| --- | --- | ---: | --- |
| Repository | Required files present | 7/7 | Pass |
| Tests | Unit/fixture tests | 14/14 | Pass |
| Lint | Ruff | clean | Pass |
| Security | Secret/token scan | clean | Pass |
| Fresh clone | `uv sync --frozen`, fixture smoke, tests | pass | Pass |
| Fixtures | Required fixture files | 2/2 | Pass |
| Fixture data | People | 29 | Pass |
| Fixture data | Claims | 31 | Pass |
| Fixture data | Sources | 9 | Pass |
| Data quality | Claim source URL coverage | 31/31 | Pass |
| Data quality | Claim evidence coverage | 31/31 | Pass |
| Data quality | Claim supported by stored source text | 31/31 | Pass |
| Data quality | Role normalization coverage | 29/29 role claims | Pass |
| Data quality | Trusted source coverage | 9/9 | Pass |
| Data quality | Duplicate person names | 0 | Pass |
| Required questions | Golden question pass rate | 8/8 | Pass |
| Chat | Interactive `company-rag chat` smoke with Codex | pass | Pass |
| Live ingest | Campfire live Codex ingest and ask | pass | Pass |
| Live ingest | Robinhood live Codex ingest | degraded | External-source caveat |

## Fixture Dataset Metrics

| Fixture | People | Claims | Sources | Current Claims | Former Claims | Source Types |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `robinhood.com` | 24 | 25 | 3 | 24 | 1 | official, sec |
| `meetcampfire.com` | 5 | 6 | 6 | 5 | 1 | official, public-profile |

Both fixtures reached 100% claim source URL coverage, 100% evidence coverage, and 100% source-text support for stored claims.

## Golden Questions

| Domain | Question | Expected Behavior | Status |
| --- | --- | --- | --- |
| `robinhood.com` | Who's their CTO? | Honestly reports no verified current CTO; does not return former CTO Jeffrey Pinner | Pass |
| `robinhood.com` | How many VPs do they have? | Returns 12 current VP/SVP/EVP leaders | Pass |
| `robinhood.com` | Who heads marketing? | Returns Deepak Rao as strongest marketing leader | Pass |
| `robinhood.com` | Where is their CEO based? | Returns Vlad Tenev as Bay Area of California | Pass |
| `meetcampfire.com` | Who's their CTO? | Returns Paul Nichols | Pass |
| `meetcampfire.com` | How many VPs do they have? | Returns 1 current VP/SVP/EVP leader | Pass |
| `meetcampfire.com` | Who heads marketing? | Returns Katrina Queirolo | Pass |
| `meetcampfire.com` | Where is their CEO based? | Returns John Glasgow as San Francisco, California | Pass |

All golden answers included citations to stored source evidence.

## Live Smoke Results

### Campfire

Command:

```bash
unset OPENAI_API_KEY
export LLM_PROVIDER=codex
export CODEX_TIMEOUT_SECONDS=180
uv run company-rag ingest https://meetcampfire.com --limit 8 --output-fixture /tmp/company-rag-live-campfire.json
uv run company-rag inspect meetcampfire.com
uv run company-rag ask meetcampfire.com "Who's their CTO?"
```

Observed result:

- Fetched 5 live sources.
- Extracted 2 people and 2 claims.
- `inspect` showed John Glasgow and Paul Nichols.
- `ask` returned Paul Nichols as CTO with citation to the live-fetched Campfire Claude article.
- Runtime: 21 seconds.

### Robinhood

Command:

```bash
unset OPENAI_API_KEY
export LLM_PROVIDER=codex
export CODEX_TIMEOUT_SECONDS=180
uv run company-rag ingest https://robinhood.com --limit 8 --output-fixture /tmp/company-rag-live-robinhood.json
```

Observed result:

- Fetched 3 general Robinhood marketing/about sources.
- Extracted 0 people and 0 claims.
- The high-signal investor leadership pages timed out during live fetch.
- The SEC source blocked the default automated request as an undeclared tool.

This is recorded as an external-source caveat rather than a submission blocker. The committed Robinhood fixture uses the official investor leadership roster and SEC evidence, and the fixture path passes 8/8 required golden checks with 100% evidence/source coverage.

## Go/No-Go

Submission gate: **Pass**.

The reproducible fixture path, required questions, citations, tests, lint, fresh clone, interactive chat, and Campfire live LLM pipeline all pass. Robinhood live ingestion remains dependent on external investor/SEC access behavior, so the official committed fixture is the reliable review path for that required input.
