# Delivery Checklist

## Repository

- [ ] `README.md` explains the problem and solution.
- [ ] `pyproject.toml` or equivalent dependency file exists.
- [ ] `.env.example` documents required secrets.
- [ ] No secrets committed.
- [ ] License choice is explicit if needed.
- [ ] Repo runs from a fresh clone.

## Ingestion

- [ ] Accepts both full URL and domain.
- [ ] Discovers likely leadership pages.
- [ ] Fetches and caches source pages.
- [ ] Stores source metadata and text.
- [ ] Uses real LLM structured extraction.
- [ ] Validates extracted people and claims.
- [ ] Handles no-data cases gracefully.

## Storage

- [ ] SQLite schema exists.
- [ ] People and claims are separate.
- [ ] Sources and evidence snippets are stored.
- [ ] Fixture export is deterministic.
- [ ] Fixture import works without network.

## Chat

- [ ] `ask` command works for one-off questions.
- [ ] `chat` command works interactively.
- [ ] Answers include citations.
- [ ] CTO lookup works.
- [ ] VP count works.
- [ ] Marketing leader lookup works.
- [ ] CEO location lookup works.
- [ ] Missing facts are reported honestly.

## Data Fixtures

- [ ] Robinhood fixture committed.
- [ ] Campfire fixture committed if data quality is acceptable.
- [ ] Fixture generation date is recorded.
- [ ] Fixture source URLs are preserved.
- [ ] Golden questions are included.

## Tests

- [ ] Domain normalization tests.
- [ ] Role normalization tests.
- [ ] Dedupe/merge tests.
- [ ] Fixture load tests.
- [ ] Structured chat routing tests.
- [ ] Optional live tests are skipped without keys.

## Submission

- [ ] `session.json` or coding-assistant export included.
- [ ] README includes example transcript.
- [ ] README includes known limitations and tradeoffs.
- [ ] Final smoke test run is recorded.

