## How to run (parent chat)

**Base Agent model** — `SubAgent` / `Agent`: `add_tasks` → `run_task_queue` (doer → judge → next). Same loop as inc 7 / 2b BDD in `agent_spec.py`. **Not** CliAgent `JobQueue` / `run_backlog` for session-unification parent orchestration unless you are on the CliAgent track (inc 3a+).

Tools CLI surface (proven in vanilla BDD): `agent.chat_agent:ChatAgent` — thin wrapper over `_ChatEngine(Agent)`.

Slash **`/agent-backlog`** — full parent orchestration prose on `ChatAgent.run_backlog_queue`.

---

## Rules (read before any backlog work)

| Rule | Meaning |
|------|---------|
| **Sequential** | Task 1 doer → judge PASS → task 2 doer → judge PASS → … |
| **One drain** | `run_backlog` once after all `add_tasks` calls |
| **One worker** | Each doer dispatch gets **one** `/sub-agent` (or inline fulfillment) — not N parallel Task agents |
| **Separate tasks** | Separate **queue rows**, not concurrent workers |
| **Do not stop at enqueue** | Enqueue + `run_backlog` + fulfill each doer + judge |

**NEVER** launch multiple `/sub-agent` workers or Task agents in parallel for the same backlog unless the user explicitly says "in parallel".

---

## ChatAgent parent (session unification U rows)

**One drain:**

```yaml
toolset: agent.chat_agent:ChatAgent
context:
  workspace: c:\dev\abd-cdd-55
  session: agent-based-redesign-of-cli-agent-sub-agent-and-workspace-session-isolation-55
tool: open_session
arguments:
  name: agent-based-redesign-of-cli-agent-sub-agent-and-workspace-session-isolation-55
  goal: "Session unification U2–U6"
```

For each pending U row — `add_tasks` (doer prompt from Task prompts below + judge rubric from Verify column):

```yaml
toolset: agent.chat_agent:ChatAgent
context:
  workspace: c:\dev\abd-cdd-55
  session: agent-based-redesign-of-cli-agent-sub-agent-and-workspace-session-isolation-55
tool: add_tasks
arguments:
  tasks:
    - doer_prompt: |
        <U task prompt — vanilla BDD first, then generate; finish Turn>
      judge_prompt: |
        PASS only when Verify column satisfied and validate green on touched paths.
```

Then **once**:

```yaml
toolset: agent.chat_agent:ChatAgent
context:
  workspace: c:\dev\abd-cdd-55
  session: agent-based-redesign-of-cli-agent-sub-agent-and-workspace-session-isolation-55
tool: run_backlog
```

After each `run_doer` dispatch: fulfill the doer prompt (typically **one** `/sub-agent` with Bdd + CE + Generate), then `run_judge` PASS/FAIL. Monitor `.agent_sessions/{session}/agent-session.jsonl` (`send`, `verdict`, `complete_task`).

---

## `/sub-agent` (worker, not orchestrator)

`/sub-agent` (`agents.sub_agent_kit:SubAgentKit` `run`) launches **one** worker for **one** prompt.

- Parent pipes one tools CLI call per worker.
- For backlog: parent uses ChatAgent queue + `run_backlog`; workers are launched **one at a time** as each doer prompt is dispatched.
- Worker does migration/tools work; parent does not inline worker steps.

---

## CliAgent parent (inc 3a+ only — after U4)

When on CliAgent track: `add_tasks` → `run_backlog` **once** (sequential in-process loop). Same sequential rule. Do not run two `run_backlog` calls in parallel on the same session.
