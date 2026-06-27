# Project Thoughts

This document captures product and engineering thinking around the Company Leadership RAG Agent. It is intentionally written as internal notes: what matters, what to optimize for, what to avoid, and how to make the take-home feel mature without overbuilding it.

## Core Insight

The assignment is not really asking for a generic chatbot. It is asking whether we can build a trustworthy public-data pipeline and then expose a chat interface over the resulting dataset.

The hard part is not answering "Who is the CTO?" with an LLM. The hard part is knowing whether the system has enough evidence to answer at all.

That means the prototype should be judged by:

- how it finds sources;
- how it stores facts and evidence;
- how it handles uncertainty;
- how it avoids hallucinating;
- how easy it is for a reviewer to reproduce the result.

## Best Positioning

Position the project as a cited leadership intelligence tool, not as a web scraper and not as a loose RAG demo.

A strong one-sentence description:

> A small, reproducible agent pipeline that discovers public leadership sources, extracts structured people and role claims with citations, and answers leadership questions through a grounded LLM chat interface.

The most important word is "claims." We should not pretend that the system has perfect truth. It has collected public claims from ranked sources and can explain where each answer came from.

## What Will Impress Reviewers

Reviewers will likely see many take-homes that do one of these:

- scrape a few pages;
- send all text to an LLM;
- return plausible but uncited answers;
- have no stable fixtures;
- fail when the website changes.

We should make the opposite choices:

- store every source;
- attach every answer to evidence;
- keep fixture mode first-class;
- answer "not found" when evidence is missing;
- make VP counts and role lookup deterministic;
- keep the code small enough to audit.

The best impression will come from a reviewer running one command, asking the example questions, and seeing concise answers with citations and confidence notes.

## Architecture Philosophy

Use LLMs where they are useful, not everywhere.

Good LLM use:

- extracting structured people/role/location claims from messy pages;
- normalizing titles into role categories;
- composing final answers from retrieved evidence;
- explaining uncertainty in a human-friendly way.

Bad LLM use:

- counting VPs from raw text;
- deciding whether a source exists without checking;
- inventing missing roles;
- using one huge prompt as the whole system.

The architecture should be boring in the right places:

- SQLite for facts;
- JSON fixtures for reproducibility;
- Typer CLI for the interface;
- Pydantic schemas for validation;
- simple source ranking;
- explicit retrieval routes.

## Structured Facts First

Most required questions are structured:

- "Who is their CTO?" means role lookup.
- "How many VPs do they have?" means aggregate count.
- "Who heads marketing?" means department/function query.
- "Where is their CEO based?" means person claim lookup.

These should not depend on semantic similarity alone. A vector index can help with fallback context, but the primary source of truth should be structured people and claims.

The chat layer should feel intelligent, but underneath it should use predictable retrieval.

## Data Model Thought

The central model should be:

- company;
- source document;
- person;
- claim;
- evidence snippet;
- chat session.

People are entities. Claims are source-backed statements about entities.

Example:

- Person: "Vlad Tenev"
- Claim: "Chairman and CEO"
- Claim type: role
- Normalized role: CEO
- Source: official Robinhood investor page
- Evidence: snippet from page
- Confidence: High

This makes conflicts manageable. If one source says "CEO" and another source says "Co-Founder and CEO", both can be stored. If a source says "former CTO", it can be stored but excluded from current-role answers.

## Source Strategy

Official sources should win whenever available.

For Robinhood, likely strong sources are:

- official investor relations;
- management/leadership pages;
- SEC-related filings;
- official newsroom/press releases.

For Campfire, the data may be thinner. That is a feature, not a failure, if handled honestly. A high-quality answer for a private company can say:

> I found founder/executive evidence from these public sources, but I could not verify a current CTO from the collected data.

That kind of answer shows discipline.

## Handling Campfire

Campfire is probably the harder test input because small/private companies often have sparse public leadership data.

Do not overclaim. If the public website only exposes founders or a small team, store that and mark the source coverage.

Potential strategy:

- crawl official pages first;
- inspect YC/company profile sources if relevant;
- use press/funding announcements for founders and executive roles;
- avoid treating every employee or investor as leadership;
- clearly state missing roles.

The goal is not to find a full org chart at any cost. The goal is to demonstrate a reliable method.

## Handling Robinhood

Robinhood is likely easier because it is public and has official executive data.

Potential risks:

- mixing board members with executives;
- including former leaders from old articles;
- counting board titles or legal entity officers as VPs;
- assuming headquarters equals CEO location.

The system should prefer current official pages and distinguish management from board.

## Chat Behavior

Every answer should follow a compact pattern:

1. Direct answer.
2. Evidence/citations.
3. Uncertainty note if relevant.

Example:

```text
I could not verify a current CTO in the collected Robinhood sources.

Closest technical leadership evidence: ...

Sources:
[1] ...
```

For counts:

```text
I found 3 current VP/SVP/EVP leaders in the collected dataset.

Included roles: VP, SVP, EVP.
Excluded: board members, advisors, former employees.

Sources:
[1] ...
```

This makes the answer auditable and reduces the risk of hallucination.

## Confidence And Honesty

Confidence should be explainable, not performative.

Prefer:

- High: official source, explicit current title.
- Medium: trusted third-party source or partial official support.
- Low: indirect, dated, ambiguous, or weak source.

Avoid:

- fake precision like `0.873421`;
- hiding uncertainty;
- promoting weak third-party evidence above official source data.

## What Not To Build First

Do not start with:

- React SPA;
- LangChain-heavy abstractions;
- autonomous multi-agent graph inside the product;
- Postgres or external vector DB;
- login-based scraping;
- complex browser automation.

These can consume time without improving the evaluation criteria.

The right MVP is smaller:

- ingest;
- store;
- inspect;
- ask;
- chat;
- export session.

## Documentation Angle

The README should explicitly say why the design is lean.

Good phrasing:

> I intentionally used SQLite and a CLI-first interface because the core challenge is reliable public-source extraction and grounded question answering. This keeps the demo easy to run while still exercising the full pipeline.

Also include:

- source ranking;
- role inclusion/exclusion rules;
- how fixtures were generated;
- example transcript;
- limitations;
- what would be improved with more time.

## Demo Strategy

Best demo sequence:

1. Load fixture.
2. Inspect people and sources.
3. Ask the four required questions.
4. Show citations.
5. Run tests.
6. Show `session.json`.

The demo should work even without live crawling. Live crawling is a bonus path, not the only path.

## Suggested Implementation Order

1. Domain normalization and config.
2. SQLite schema.
3. Fixture import/export.
4. Manual high-quality fixture for one company.
5. Query router and deterministic answers.
6. LLM answer composer.
7. Live fetch/discovery.
8. LLM extractor.
9. Tests and README transcript.

This order gives an end-to-end demo early. It also reduces risk: even if live ingestion is imperfect, fixture-backed chat can still be excellent.

## Final Bar

The submission should make three things obvious:

1. The system is real: it can run and answer questions.
2. The data is grounded: claims have sources and evidence.
3. The engineering is controlled: the design handles uncertainty instead of pretending it does not exist.

That is the difference between a quick RAG demo and a take-home that feels production-minded.

