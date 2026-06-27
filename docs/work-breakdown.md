# Work Breakdown

## Agent Decomposition

The project should be split into bounded workstreams:

1. **Main integrator**
   - Owns repo structure, final decisions, and integration.
   - Keeps README and docs aligned with implementation.
   - Reviews all subagent output before merging.

2. **Requirements/risk agent**
   - Extracts hard requirements from the PDF.
   - Identifies hidden evaluation criteria.
   - Checks that the final repo addresses each deliverable.

3. **Architecture agent**
   - Designs storage, ingestion pipeline, and chat retrieval flow.
   - Keeps the system lean enough for a take-home.

4. **Data sourcing agent**
   - Investigates public source availability for test inputs.
   - Builds a source whitelist/ranking.
   - Flags weak or stale sources.

5. **Implementation agent**
   - Implements ingestion, schema, extraction, and fixture export.
   - Uses disjoint files from any UI/chat implementation work.

6. **Chat/UX agent**
   - Implements CLI chat and sample transcript.
   - Focuses on answer quality, citations, and graceful unknowns.

7. **QA agent**
   - Runs tests, fresh-clone smoke check, fixture checks, and README command verification.

## Planned Repo Structure

```text
company-leadership-rag-agent/
  README.md
  docs/
    assignment.md
    implementation-plan.md
    architecture.md
    work-breakdown.md
    questions.md
  data/
    fixtures/
  src/
    leadership_rag/
      __init__.py
      cli.py
      config.py
      db.py
      discovery.py
      fetch.py
      extraction.py
      normalize.py
      retriever.py
      chat.py
      fixtures.py
  tests/
  session.json
  pyproject.toml
  .env.example
```

## Immediate Build Order

1. Package skeleton and CLI.
2. SQLite schema and fixture models.
3. Source fetch/discovery.
4. LLM extraction schema.
5. Normalization and dedupe.
6. Fixture export/import.
7. Chat retrieval and LLM answer composition.
8. Tests and README transcript.

