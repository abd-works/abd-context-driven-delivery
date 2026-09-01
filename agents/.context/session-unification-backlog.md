# Session unification backlog — WorkSession → AgentSession

issue: 55  
canonical: `agents/.context/agent-session-redesign-sketch.md`  
blocked work: inc **3a/3b** CliAgent agent BDD until judge validate/scan share **one** session type  
rule: **no `WorkSession`** in production code; **`AgentSession`** only; **`folder`** = `{repo}/.agent_sessions/{name}/`; **`contextRoot`** = durable `.context/` (or lookupPath override)

---

## How to run (parent chat)

See **`session-unification-backlog-how-to-run.md`** — **Agent** `add_tasks` / `run_task_queue` via `agent.chat_agent:ChatAgent` (`open_session` → `add_tasks` × N → `run_backlog` once). **Not** CliAgent `use_template` / `run_backlog`.

---

## Backlog (independent agent tasks)

| ID | Task | Depends | Touch | Verify |
|----|------|---------|-------|--------|
| **U1** | **AgentSession CDD seam** — on `agent.AgentSession`: `path` (= `context_root`), `decisions`, hanging `turn` / `open_turn`, `eval_log_dir` → `folder/logs`. `Turn.finish_turn()` alias. **Do not change `SessionPaths` / `WorkSession.folder`** — that layer is retired, not migrated. | — | `agents/agent.py`, `agents/agent_spec.py` | `mamba agents/agent_spec.py` |
| **U2** | **Lifecycle → AgentSession** — `lifecycle.py` opens via `agent.agent.Workspace` + `AgentSession`; drop `current_work_session` / `WorkSession`. | U1 | `lifecycle.py` | Bdd validate on actions host |
| **U3** | **BaseContextTool → AgentSession** — `base_context_tool.py` uses `agent.agent.Workspace.open()` → `AgentSession`. Remove `WorkSession` import. | U2 | `context_tools/base/base_context_tool.py` | `mamba context_tools/base/base_context_tool_spec.py` |
| **U4** | **SessionLog + tools run** — bind `SessionLog` and `coalesce_run_context` to `AgentSession` (name, folder, turn). Judge validate/scan same session as agent BDD. | U3 | `utilities/workspace/session_log.py`, `primitives/tools/tool.py` | Validate kit on `agents` |
| **U5** | **CliAgent → AgentSession.folder** — queue, model, cli bindings under `.agent_sessions/{name}/` via AgentSession, not WorkSession paths. | U1 | `utilities/cli_agent/cli_agent.py` | `mamba utilities/cli_agent/cli_agent_spec.py` |
| **U6** | **Retire WorkSession** — delete `WorkSession`, `SessionPaths.session_dir`, `.context/sessions/` usage. Keep git/Turn kit in workspace only until Turn moves to agent. | U2–U5 | `utilities/workspace/workspace.py` | grep-clean + mamba |

---

## Task prompts (copy into `/sub-agent` `prompt`)

### U1 — AgentSession CDD seam

```
Migration U1: Extend agent.AgentSession with CDD seams lifecycle needs: path (= context_root),
decisions (RecordDecisions), turn/open_turn, eval_log_dir under folder/logs.
Add Turn.finish_turn() alias. Do NOT patch SessionPaths or WorkSession — that code is retired.
Canonical: agents/.context/agent-session-redesign-sketch.md.
```

### U2 — Lifecycle

```
Migration U2: lifecycle.py uses agent.agent.Workspace.open → AgentSession.
begin/end use session.turn and session.decisions. Remove WorkSession imports.
```

### U3 — BaseContextTool

```
Migration U3: base_context_tool.py opens agent.agent.Workspace + AgentSession.
Remove workspace.workspace WorkSession. Green base_context_tool_spec.
```

### U4 — SessionLog + tools run

```
Migration U4: SessionLog and tools run coalesce/bind to AgentSession on session/* branches.
Judge validate shares session with agent BDD.
```

### U5 — CliAgent

```
Migration U5: CliAgent queue/model/bindings use AgentSession.folder (.agent_sessions/), not WorkSession.folder.
```

### U6 — Retire WorkSession

```
Migration U6: Delete WorkSession and SessionPaths.session_dir. Grep-clean. Keep git/Turn utilities only.
```

---

## Status (update each stop)

| ID | Status | Notes |
|----|--------|-------|
| U1 | judge_green | doer [3383e523](3383e523-36d8-4a76-94e0-bebda04f073f); mamba 173 pass; validate ok |
| U2 | judge_green | doer [U2 doer](b84cb3c6-63f5-48b2-bb76-fb243c1178a0); validate ok; base_context_tool_spec 97 pass |
| U3 | pending | |
| U4 | pending | |
| U5 | pending | |
| U6 | pending | |

**After U4 judge_green:** resume inc **3a** CliAgent agent BDD.
