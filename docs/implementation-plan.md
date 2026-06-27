# Implementation Plan

## Product Goal

Build a compact but production-shaped prototype that can answer leadership questions with citations, confidence, and clear provenance.

The strongest version is not a generic chatbot. It is a structured public-data extraction system with an LLM used where it adds value: entity extraction, claim normalization, and final answer composition.

## Proposed Stack

- Language: Python.
- CLI: Typer + Rich.
- Storage: SQLite for structured people/sources/claims, with JSON fixture export.
- Crawling/extraction: httpx, BeautifulSoup/selectolax, trafilatura-style main-text extraction where useful.
- LLM access: one provider adapter behind environment variables, preferably OpenAI-compatible or Anthropic-compatible via LiteLLM.
- Validation: Pydantic models for extracted people, titles, evidence spans, confidence, and source metadata.
- Tests: pytest, fixture-based tests, optional live tests gated by env vars.

## Why This Shape

Leadership Q&A is mostly structured retrieval:

- "Who's the CTO?" is a role lookup.
- "How many VPs?" is an aggregate query.
- "Who heads marketing?" is a normalized department/title query.
- "Where is the CEO based?" is a claim lookup with source-backed uncertainty.

A vector-only RAG system would be less reliable for counts, role normalization, and citations. The better approach is structured storage first, source snippets second, LLM answer synthesis last.

## Today Plan

### Phase 1: Foundation

- Create repo skeleton and docs.
- Define CLI contract and `.env.example`.
- Define SQLite schema and Pydantic models.
- Add fixture format for committed datasets.

### Phase 2: Source Discovery

- Normalize input URL to company domain.
- Crawl same-domain pages likely to contain leadership:
  - `/about`
  - `/about-us`
  - `/team`
  - `/leadership`
  - `/company`
  - investor/governance leadership pages
  - blog author pages where relevant
- Add optional search-provider hook for public web search if an API key is available.
- Persist all fetched source pages with URL, title, fetched_at, content hash, and text.

### Phase 3: Extraction

- Split source text into candidate chunks.
- Use real LLM structured extraction to identify leadership people.
- Capture:
  - name
  - title
  - normalized seniority
  - department/function
  - company
  - profile URL
  - location if stated
  - evidence quote/snippet
  - source URL
  - confidence
- Dedupe people across sources.
- Preserve conflicting claims instead of overwriting them silently.

### Phase 4: Storage and Fixtures

- Store normalized data in SQLite.
- Export deterministic JSON fixtures under `data/fixtures/`.
- Commit fixtures for both `meetcampfire.com` and `robinhood.com` if time permits.
- At minimum, commit one high-quality fixture and include commands to rebuild both.

### Phase 5: Chat

- Build interactive CLI chat.
- Route questions to structured retrieval:
  - role lookup
  - count/aggregate
  - department lookup
  - location lookup
  - fallback source search
- Send retrieved rows/snippets to the real LLM for final response.
- Always include citations and uncertainty.
- If data is missing, answer clearly instead of hallucinating.

### Phase 6: QA and Packaging

- Add README with setup, env vars, commands, and example transcript.
- Add tests for normalization, fixture loading, and common questions.
- Add a smoke script that runs chat questions against fixtures.
- Add `session.json` or a structured coding-session export artifact.
- Verify a fresh clone path works.

## Success Criteria

- `company-rag ingest https://robinhood.com/` creates or updates a dataset.
- `company-rag chat robinhood.com` can answer the four example question types.
- Answers cite public source URLs.
- Fixture-based tests pass without network.
- Live ingestion fails gracefully when a site blocks crawling or search keys are missing.
- README explains tradeoffs and why the system is not just "LLM over scraped text."

## Cut Lines

If time is tight:

- Keep CLI only; skip web UI.
- Use SQLite + JSON fixtures; skip embeddings.
- Support one search provider optionally; keep same-domain crawling as default.
- Prefer high-quality Robinhood fixture because it has an official investor leadership page.
- For Campfire, collect best public founder/leadership evidence from official site, YC, and press sources, with lower confidence where scope is thin.
