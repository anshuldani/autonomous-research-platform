# Changelog

All notable changes to the Autonomous Research Platform are tracked here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
no tagged releases yet.

## Unreleased

### Added
- `Makefile` covering backend, Next.js frontend, and MCP server: `setup`,
  `run`, `test`, `lint`, `clean` targets per component
- `mcp_server/` integration smoke tests (8 passing) and a Claude Desktop
  config example
- README sections: "why this is hard", engineering-decisions, observed
  results, MCP setup guide

### Changed
- `day3_advanced_rag_agent.py` renamed to `planning_agent.py`; all imports
  and tests updated to match
- Pinecone metadata stores 1500 chars per chunk (was 200) to make recalled
  context useful for downstream answers
- `.gitignore` extended to cover the MCP server's venv and env files
- Quality scorer / research tools / planning agent: dead-code and noisy
  init-print cleanup

### Fixed
- `main.py` and `mcp_server/server.py` use `asyncio.get_running_loop()`
  inside async handlers (was deprecated `get_event_loop()`)
- `test_iterative.py`: `== True/False` comparisons replaced with truthiness
  checks; `inspect` hoisted out of the test body
- Search-behaviour tests inject `TAVILY_API_KEY` so they don't depend on
  the developer's shell environment
- Improvement log only appends an ellipsis when the question exceeds 70
  chars (was always appending, even on short questions)
