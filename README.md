# Company Leadership RAG Agent

Planning scaffold for the take-home assignment.

The goal is an end-to-end system that accepts a company domain or website URL, finds leadership from public sources, stores a cited dataset, and exposes a real-LLM chat interface over that data.

## Current Status

This repository is in the planning phase. Implementation should follow the docs in this order:

1. [Assignment brief](docs/assignment.md)
2. [Implementation plan](docs/implementation-plan.md)
3. [Architecture](docs/architecture.md)
4. [Work breakdown](docs/work-breakdown.md)
5. [Acceptance criteria](docs/acceptance-criteria.md)
6. [Data sourcing policy](docs/data-sourcing-policy.md)
7. [Risk register](docs/risk-register.md)
8. [Project thoughts](docs/project-thoughts.md)
9. [Delivery checklist](docs/delivery-checklist.md)
10. [Agent collaboration plan](docs/agent-collaboration.md)
11. [Questions and assumptions](docs/questions.md)

## Quality Bar

- Runnable clone-and-go repository.
- Real LLM calls only; no mocked completions.
- Public-source provenance for every leadership claim.
- Data fixtures committed for the example company inputs.
- Chat answers grounded in structured data plus source snippets.
- Clear session/coding-agent collaboration artifact.

## Planned MVP Interface

The first deliverable should be a polished CLI chat:

```bash
company-rag ingest https://robinhood.com/
company-rag chat robinhood.com
```

The CLI is the fastest path to a reliable take-home. A small web UI can be added only after the ingestion, storage, citations, and chat behavior are solid.
