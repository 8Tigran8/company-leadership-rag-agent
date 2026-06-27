# Risk Register

## High Risk

### Public data is incomplete

Private companies may not publish full leadership teams.

Mitigation:

- Preserve source scope in answers.
- Use confidence labels.
- Avoid guessing.
- Commit fixtures so demo remains stable.

### LLM extraction can hallucinate

The extractor may infer people or roles not supported by text.

Mitigation:

- Use structured output schema.
- Require evidence snippets.
- Validate titles against role taxonomy.
- Reject candidates without source-backed evidence.

### Counts require structured retrieval

VP counts and department queries are unreliable with pure vector search.

Mitigation:

- Store normalized roles and seniority.
- Route counting questions to SQL.
- Use LLM only to phrase the answer.

### Sites may block crawling or change layout

Live ingestion may fail even if fixtures work.

Mitigation:

- Cache fetched pages.
- Use timeouts and graceful errors.
- Keep fixture mode as first-class demo path.
- Document live ingestion limitations.

## Medium Risk

### Current vs former roles

Sources often mention former executives.

Mitigation:

- Detect former/current language.
- Store status when known.
- Exclude former roles from default answers.

### Duplicate people across sources

Same person can appear on official bio, press release, and third-party profile.

Mitigation:

- Merge by normalized name plus company.
- Keep separate claims.
- Prefer official/current claims in retrieval.

### Location is ambiguous

CEO location may not be public, and company headquarters is not person location.

Mitigation:

- Store person location only if explicitly stated.
- Answer unknown when only HQ is available.

### Ambiguous department mappings

"Growth" can map to marketing, product, or revenue.

Mitigation:

- Preserve original title.
- Map department with confidence.
- Surface uncertainty in answers.

## Low Risk

### Overengineering

The project can become larger than the take-home expects.

Mitigation:

- Keep SQLite and CLI as the core.
- Add web UI only after core is complete.
- Avoid framework-heavy agent orchestration inside the app.

### API key handling

Reviewers may not have the same API keys.

Mitigation:

- Provide `.env.example`.
- Make fixture loading and inspection work without LLM keys.
- Clearly mark live extraction/chat requirements.

