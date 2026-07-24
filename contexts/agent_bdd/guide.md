1. Read `contexts/bdd/bdd.md` § Contexts — the underlying test discipline applies here too.
2. Read § Contexts above and the harness surface: `contexts/agent_bdd/__init__.py`, `contexts/agent_bdd/agent_bdd_common.py` (types `AgentResult`, `RunResponse`, `JudgeResult`).
3. Scaffold from `formats/{format}/agent-bdd-template.py`:
   - `with description(...)` → `with context(...)` → `with it(...)` → `with agent(...):`.
   - Assert immediately after each step — `expect(response.ok).to(be_true)` right after `instruct_use_tool`, `ai_judge(...)` right after the final `instruct`. No `self.*`, no `before.all`.
4. Assert `response.action`, `response.tools`, and required substrings in `response.instructions`. Use `ai_judge` for prose outputs.
5. Point every session at `.agent_bdd_sessions/<scenario>.json` beside the spec.
6. Run **validate**.

**Do not:** use a `session.` prefix (`session.instruct`, `session.ai_judge`, etc.) — import and call the free functions; mock the harness or the agent; assert on raw `stdout` when `RunResponse` has a parsed field for the same value; share one session across contexts; or catch `AgentHarnessError` in the spec — let it surface with the log-directory path in the message.
