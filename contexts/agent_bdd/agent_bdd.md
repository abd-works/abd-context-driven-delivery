# Instructions

Write **agent BDD specs** — mamba tests that drive a real agent through the `agent(...)` harness and assert on the parsed `RunResponse` plus AI-judged prose.

The **`bdd`** generator supplies the underlying test discipline (RED-GREEN, AAA, mocks, minimalism, shared setup). Agent specs layer harness-specific rules on top.

---
# Contexts

## Harness

- **`same-harness-interface`** — `agent(workspace, session_file)` in `contexts/agent_bdd/__init__.py` routes to `cli_agent` (cursor-agent CLI, `agent_cli_bdd.py`) or `chat_agent` (in-chat inbox, `agent_chat_bdd.py`) based on `AGENT_BDD_IN_CHAT`. Both blocks expose the same three operations; specs never import either implementation directly.
- **`free-function-api`** — `instruct`, `instruct_use_tool`, and `ai_judge` are free functions imported from `agent_bdd`. They delegate to the active `with agent(...)` block via a thread-local. Call them directly — never via a session prefix. If called outside an `agent` block, they raise `RuntimeError`.

## instruct vs instruct_use_tool

- **`instruct-for-setup`** — Use `instruct(prompt)` when the agent should read files, prime state, or perform a natural-language step. Returns `AgentResult(exit_code, stdout, stderr, elapsed_seconds)`; treat assertions on `stdout` as opportunistic.
- **`instruct-run-for-toolset`** — Use `instruct_use_tool(prompt)` when the agent must invoke `python -m tools run -` and return a fenced YAML CLI response. Returns `RunResponse` with parsed `.ok`, `.toolset`, `.action`, `.tool`, `.tools`, `.instructions`, `.arguments`, `.resources`, `.result`.
- **`fenced-yaml-contract`** — `instruct_use_tool` auto-appends *"Return the complete fenced YAML stdout from the CLI"* and validates the response `action`/`tool` matches the prompt YAML. If the agent skips the shell call, the harness replays the YAML through a local subprocess as a fallback so the assertion still runs.

## Session lifecycle

- **`act-assert-inline`** — Place the `with agent(...):` block directly inside `with it(...)`. Assert immediately after each `instruct` or `instruct_use_tool` call — no `self.*` accumulation, no split `before.all` + separate `it` blocks. Act → assert → act → assert in one linear flow.
- **`session-file-per-scenario`** — Session JSON lands in `.agent_bdd_sessions/<name>.json` beside the spec. One file per `it` so each run is isolatable and re-runnable.

## Assertions

- **`assert-on-response-fields`** — Structural checks target `response.ok`, `response.action`, `response.tools`, `response.arguments`, and substrings in `response.instructions`. These are cheap and deterministic.
- **`judge-qualitative-outcomes`** — Free-form outputs (generated markdown, natural-language artifacts) go through `ai_judge(output, rubric)` inside the `with agent(...)` block. `ai_judge` raises `AssertionError(reason)` on FAIL — it is self-contained like `expect`. No return value to store or check.
- **`no-mocking-the-harness`** — Agent specs test the real agent end-to-end. Never mock `agent()`, the block, the harness helpers, or the agent's output.

## Timeouts

- **`timeout-per-instruct`** — Default 300s. Long generate/repair actions may need 300–600s. On timeout, `instruct_use_tool` falls back to a local YAML replay so a slow agent does not kill the assertion.

---
# Generate

1. Read `contexts/bdd/bdd.md` § Contexts — the underlying test discipline applies here too.
2. Read § Contexts above and the harness surface: `contexts/agent_bdd/__init__.py`, `contexts/agent_bdd/agent_bdd_common.py` (types `AgentResult`, `RunResponse`, `JudgeResult`).
3. Scaffold from `formats/{format}/agent-bdd-template.py`:
   - `with description(...)` → `with context(...)` → `with it(...)` → `with agent(...):`.
   - Assert immediately after each step — `expect(response.ok).to(be_true)` right after `instruct_use_tool`, `ai_judge(...)` right after the final `instruct`. No `self.*`, no `before.all`.
4. Assert `response.action`, `response.tools`, and required substrings in `response.instructions`. Use `ai_judge` for prose outputs.
5. Point every session at `.agent_bdd_sessions/<scenario>.json` beside the spec.
6. Run **validate**.

**Do not:** use a `session.` prefix (`session.instruct`, `session.ai_judge`, etc.) — import and call the free functions; mock the harness or the agent; assert on raw `stdout` when `RunResponse` has a parsed field for the same value; share one session across contexts; or catch `AgentHarnessError` in the spec — let it surface with the log-directory path in the message.
