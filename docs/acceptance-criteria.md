# Acceptance Criteria

This document turns the PDF brief into concrete checks for the final repository.

## Functional

- The system accepts either a bare domain or full URL.
- The system can ingest at least one provided test input end to end.
- The system stores collected public leadership data in a reusable local store.
- The system exports committed fixtures for collected example data.
- The system provides an interactive or single-question chat interface.
- The chat uses a real LLM call for answer composition or extraction; completions are not mocked.
- The chat can answer, with citations:
  - Who is the CTO?
  - How many VPs are listed?
  - Who heads marketing?
  - Where is the CEO based?
- If an answer is not supported by collected data, the system says so explicitly.

## Data Quality

- Every leadership claim has at least one source URL.
- Every stored source has a retrieved timestamp.
- Official company or investor pages are ranked higher than third-party pages.
- Current roles are distinguished from former, board, advisor, or investor roles.
- Conflicting claims are preserved instead of silently overwritten.
- Duplicate people are merged conservatively.
- Role normalization preserves the original title.

## Engineering

- Fresh clone setup is documented.
- Secrets are read from environment variables and never committed.
- `.env.example` is present.
- Fixture-based tests run without network access.
- Live tests are optional and skipped when required API keys are missing.
- The repository includes a coding-assistant session artifact or structured session log.
- README explains storage design, data sourcing, limitations, and tradeoffs.

## Demo

The final demo should include commands similar to:

```bash
uv sync
cp .env.example .env
uv run company-rag load-fixture data/fixtures/robinhood.com.json
uv run company-rag ask robinhood.com "Who is their CTO?"
uv run company-rag ask robinhood.com "How many VPs do they have?"
uv run company-rag chat robinhood.com
```

## Non-Goals

- No need for a heavy autonomous multi-agent runtime inside the product.
- No need for a React SPA unless the CLI is already excellent.
- No need for perfect company coverage across the entire web.
- No scraping behind logins.
- No private personal data collection.

