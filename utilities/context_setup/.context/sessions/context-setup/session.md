# Session: context-setup

## Start

- **date:** 2026-08-04
- **path:** utilities/context_setup
- **goal:** Design an agentic toolset (actions + tools) that abstracts a source (live app or documents) into queryable context memory, replacing the 7 separate script-based skills (app-extractor, app-sandbox, to-markdown, semantic-index, chunk, db-embed, db-ask).
- **fidelities:** story_map, scenarios, acceptance_tests
- **contexts:** (unset)

## Progress

- **2026-08-05:** Acceptance tests and production code written for Increment 1.
  - `utilities/context_setup/context_setup.py` — `ContextSetup` (@toolset): `convert` (@tool) + `capture_from_documents` (@action)
  - `utilities/context_setup/context_index.py` — `ContextIndex` (@toolset): `embed` (@tool) + `search` (@tool) + `ask` (@action)
  - `utilities/context_setup/context_setup_spec.py` — 24 mamba specs for ContextSetup (all green)
  - `utilities/context_setup/context_index_spec.py` — 21 mamba specs for ContextIndex (all green)
  - 45/45 examples pass. No OpenAI API key required for any spec (FakeEmbeddingProvider).
- **2026-08-13:** Increment 2 (`Capture From Live App`) implemented and green.
  - Story map grilled and sketched for `Capture From Live App` sub-epic.
  - Expanded from 4 stub stories to 7 across two nested sub-epics (`Stub External Dependencies`, `Capture App Pages`).
  - `context_setup.py` — added `capture_from_live_app` (@action) + `smoke_test`, `scout_app`, `complete_capture` (@tools)
  - Result types added: `ScreenResult`, `SmokeTestResult`, `PageCapture`, `ScoutResult`, `CaptureResult`
  - `context_setup_spec.py` — 36 new specs (60 total, all green). Uses real HTTP test server + Playwright for tool specs.
  - Tools use: `requests` for HTTP smoke tests, `playwright` (v1.60 `aria_snapshot()`) for page capture.
  - Open: `mode="tool"` deferral decisions for `smoke_test`/`scout_app`; `complete_capture` recursive-vs-separate; multi-surface hybrid.
