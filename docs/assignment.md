# Assignment Brief

Source PDF: `/Users/dmitry/Downloads/Telegram Desktop/Take-home_ Company Leadership RAG Agent-2.pdf`

The PDF has no usable text layer, so this brief was transcribed from OCR plus visual inspection.

## Original Requirements

**Take-home: Company Leadership RAG Agent**

**Input.** A company's domain or website URL.

**Goal.** Build an end-to-end system that:

1. Finds the company's leadership from public sources.
2. Exposes a chat interface to ask questions over the collected data.

**Scope of "leadership."** C-level executives such as CEO, CTO, CFO, CMO, Vice Presidents, and Heads of departments.

## Two Parts

1. **Data collection and storage**
   - Find the people.
   - Collect their public profile data.
   - Decide on a storage model: flat files, SQLite, vector store, graph, or whatever fits.

2. **Chat interface**
   - LLM-powered chat over the dataset.
   - Example questions:
     - "Who's their CTO?"
     - "How many VPs do they have?"
     - "Who heads marketing?"
     - "Where is their CEO based?"

## Rules

- Real LLMs only; no stubs or mocked completions.
- No technical constraints on stack, libraries, or architecture.
- Lean/no-overengineering is welcomed.
- Must use a coding agent for development.

## Deliverables

- Runnable Git repository; reviewers should be able to clone-and-go.
- Data fixtures: collected dataset for the example company.
- Chat interface in any reasonable form: CLI, web, notebook, Claude/ChatGPT app, etc.
- `session.json` or chat export from the coding-assistant session.

## Test Inputs

- `https://meetcampfire.com/`
- `https://robinhood.com/`

## Evaluation Criteria

They will evaluate:

1. Data sourcing approach.
2. Storage design.
3. Agent architecture.
4. Collaboration loop with Claude Code or another coding agent.

