1. Read `context_tools/bdd/bdd.md` § Contexts — the underlying test discipline applies here too.
2. Read § Contexts above and the harness surface: `context_tools/agent_bdd/__init__.py`, `context_tools/agent_bdd/agent_bdd_common.py` (types `AgentResult`, `RunResponse`, `JudgeResult`).
3. Scaffold from `templates/agent_bdd-templates.py`:
   - `with description(...)` → `with context(...)` → `with it(...)` → `with agent(...):`.
   - Assert immediately after each step — `expect(response.ok).to(be_true)` right after `instruct_use_tool`, `ai_judge(...)` right after the final `instruct`. No `self.*`, no `before.all`.
4. Assert `response.action`, `response.tools`, and required substrings in `response.instructions` for the tools run. For work-producing scenarios, also assert the **artifact on disk** (exists, non-empty, domain markers), then `ai_judge` that file’s contents — not chat claims.
5. Point every session at `.agent_bdd_sessions/<scenario>.json` beside the spec.
6. Run **validate**.
7. On a **red** agent BDD: triage prompt vs code (§ Failures). Code gaps → fix code + add the vanilla BDD that covers the miss; prompt gaps → fix guidance/agent BDD only.

**Do not:** use a `session.` prefix (`session.instruct`, `session.ai_judge`, etc.) — import and call the free functions; mock the harness or the agent; assert on raw `stdout` when `RunResponse` has a parsed field for the same value; share one session across contexts; catch `AgentHarnessError` in the spec — let it surface with the log-directory path in the message; fix a **code** failure with prompt-only changes and no vanilla BDD for the gap; or treat “prompt/skill exists” / “agent said it worked” as a PASS for a behavioral run.
