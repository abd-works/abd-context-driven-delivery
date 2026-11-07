1. Read `practices/bdd/bdd.md` § Overview — the underlying test discipline applies here too.
2. Read § Overview above and the harness surface: `practices/agent_bdd/agent_block.py` (`agent` and the *AgentBlock* it yields), `practices/agent_bdd/agent_bdd_common.py` (types `AgentResult`, `RunResponse`, `JudgeResult`).
3. Scaffold from `templates/agent_bdd-templates.py`:
   - `with description(...)` → `with context(...)` → `with it(...)` → `with agent(...) as run:`.
   - Assert immediately after each step — `expect(response.ok).to(be_true)` right after `run.instruct_use_tool`, `run.ai_judge(...)` right after the final `run.instruct`. No `self.*`, no `before.all`.
4. Assert `response.action`, `response.tools`, and required substrings in `response.instructions` for the tools run. For work-producing scenarios, also assert the **artifact on disk** (exists, non-empty, domain markers), then `ai_judge` that file’s contents — not chat claims.
5. Point every session at `.agent_bdd_sessions/<scenario>.json` beside the spec.
6. Run **validate**.
7. On a **red** agent BDD: triage prompt vs code (§ Failures). Code gaps → fix code + add the vanilla BDD that covers the miss; prompt gaps → fix guidance/agent BDD only.

**Do not:** call a step on anything but the block `with agent(...) as run:` yields; mock the harness or the agent; assert on raw `stdout` when `RunResponse` has a parsed field for the same value; share one session across contexts; catch `AgentHarnessError` in the spec — let it surface with the log-directory path in the message; fix a **code** failure with prompt-only changes and no vanilla BDD for the gap; or treat “prompt/skill exists” / “agent said it worked” as a PASS for a behavioral run.
