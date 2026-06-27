# Agent Collaboration Plan

The assignment requires evidence that a coding agent was used. This repository should make that collaboration visible without turning the product into an overbuilt agent system.

## Current Planning Agents

Two planning subagents were used before implementation:

1. Requirements/risk audit.
   - Output: strict requirements, hidden evaluation criteria, risks, edge cases, README obligations.
2. Architecture/MVP audit.
   - Output: stack recommendation, pipeline shape, storage schema, test strategy, UX plan.

Their conclusions are integrated into:

- `docs/acceptance-criteria.md`
- `docs/architecture.md`
- `docs/data-sourcing-policy.md`
- `docs/risk-register.md`
- `docs/delivery-checklist.md`

## Session Artifact

The final repo should include `session.json`.

Recommended structure:

```json
{
  "agent": "Codex",
  "created_at": "2026-06-27T00:00:00Z",
  "task": "Company Leadership RAG Agent",
  "decisions": [],
  "subagents": [],
  "implementation_log": [],
  "test_runs": [],
  "known_limitations": []
}
```

## What To Record

- Major architecture decisions and why they were made.
- Subagent tasks and summaries.
- Important prompts used for extraction/chat design.
- Test runs and failures fixed.
- Known limitations that remain at delivery.

