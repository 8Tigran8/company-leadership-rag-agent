# Questions And Working Assumptions

These answers affect implementation choices, but none should block starting the prototype.

## Questions For Dmitry

1. Which LLM provider/key should the prototype target first: OpenAI-compatible API, Anthropic, or both through LiteLLM?
2. Do you want the submitted interface to be CLI-only, or should we spend extra time on a small web UI after the CLI works?
3. Should fixtures cover both test inputs, `meetcampfire.com` and `robinhood.com`, or is one excellent fixture plus one live-ingestion demo acceptable?
4. Can we use an external search API such as Tavily, Brave, SerpAPI, or Bing if available, or should live discovery be limited to direct crawling from the input website?
5. What is the expected delivery format: local repo only, GitHub repo, zipped repo, or PR?
6. Do you already have a coding-assistant `session.json` export requirement from their side, or should we create our own structured session log in the repo?

## Default Assumptions

- Build Python CLI first.
- Use SQLite plus JSON fixtures.
- Support both OpenAI-compatible and Anthropic-compatible LLMs if this does not add much complexity; otherwise choose one provider via env vars.
- Collect fixtures for both provided test inputs if time permits.
- Treat Robinhood as the strongest fixture candidate because it has an official investor leadership page.
- Treat Campfire as a harder private-company case where official source coverage may be thinner; use confidence and citations instead of overclaiming.
- Skip web UI until ingestion, fixture quality, and chat answers are reliable.

