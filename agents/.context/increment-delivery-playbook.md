# Increment delivery playbook — #55

issue: 55  
canonical design: `agents/.context/agent-session-redesign-sketch.md`  
canonical stories: `agents/.context/agent-session-redesign-stories-sketch.md`  
test strategy: `agents/.context/bdd-testing-strategy.md`  
code root: `agents/`  
context root: `agents/.context/`

Use this document as the **step-by-step runbook** for each increment. Do not skip the two-agent loop.

**Sketches are done.** Modules + behavior live in `agent-session-redesign-sketch.md` and `agent-session-redesign-stories-sketch.md`. Each increment **implements from those files** — do **not** re-run `/bdd.behavior`, `/clean_engineering.modules`, or regenerate sketches unless the user explicitly asks for a sketch change.

---

## Two agents on every increment

| Role | Job | Must not |
|------|-----|----------|
| **Generation agent (doer)** | Write or extend **production code** + **vanilla BDD** for this increment only | Run live IDE chat; “fix forward” into the next increment |
| **Validation agent (judge)** | **`validate` on the host tool(s) the doer used**, then **pytest**; report violations — **do not edit** | Generate or fix artifacts; expand scope |

**Loop until judge is green:**

1. **Doer** — generate (see increment row)
2. **Judge** — host **`validate`** (judge persona; includes **`scan`** internally) → **pytest** (and agent BDD on inc 10 / 12 only)
3. If red → **doer fixes every reported violation** → back to step 2
4. If green → **done** with this increment; start next increment

Judge triage (from `bdd-testing-strategy.md`):

- **Code defect** → fix + add/adjust vanilla BDD so the class cannot recur  
- **Prompt/guidance defect** (agent BDD only) → fix rubric/instructions only  

---

## Tools and commands (name them exactly)

All generation/validation goes through **`.\tools.ps1 run -`** from repo root unless running pytest directly.

| Purpose | Cursor command / skill | Tools CLI fence |
|---------|------------------------|-----------------|
| **Source of truth (read only)** | — | `agent-session-redesign-sketch.md` · `agent-session-redesign-stories-sketch.md` |
| **Vanilla BDD specs + dev tests** | `/bdd.development` | `toolset: context_tools.bdd.bdd:Bdd` · `context.fidelity: development` · `action: generate` |
| **Production code** | `/clean_engineering.code` | `toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering` · `fidelity: code` |
| **Judge — BDD artifacts** | **`validate`** on **Bdd** · **development** | see fence below |
| **Judge — code artifacts** | **`validate`** on **CleanEngineering** · **code** | see fence below |
| **Scan — BDD artifacts** | `/scan` on **Bdd** host (explicit paths) | see **`scan`** fences below — same host-tool rule as **`validate`** |
| **Scan — code artifacts** | `/scan` on **CleanEngineering** host (explicit paths) | see **`scan`** fences below |
| **Agent BDD spec** (inc 10, 12 only) | `agent_bdd` skill | `toolset: agent_bdd.agent_bdd:AgentBdd` |
| Run vanilla tests | shell | `python -m pytest agents/ -k …` (narrow `-k` to this increment’s spec module) |
| Run agent BDD | shell | `python -m pytest path/to/*_agent_spec.py` (see existing `#44` specs under `utilities/cli_agent/`) |
| Close a hanging turn (optional) | `/finish-turn` | `toolset: workspace.workspace:Turn` · `tool: finish_turn` |

### What `validate` is

**`validate` is the judge action on a host context tool** — critical judge persona, report only, no edits (`context_tools/actions/validate/validate.md`).

- Run it **on the same toolset + fidelity the doer generated** (pair generate → validate).
- It **calls `scan`** on session-rooted paths internally (`validate.md` step 3).
- Do **not** run one umbrella validate “on clean_engineering and bdd together.” Run **Bdd validate** when specs changed; run **CleanEngineering validate** when code changed (one or both, **sequential**, each scoped to its artifact).
- Do **not** add a **separate** scan pass in the judge loop — validate already scanned.

**Bdd judge fence (development specs under `agents/`):**

```yaml
toolset: context_tools.bdd.bdd:Bdd
context:
  fidelity: development
  path: agents
action: validate
```

**CleanEngineering judge fence (code under `agents/`):**

```yaml
toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
context:
  fidelity: code
  path: agents
action: validate
```

### What `scan` is

**`scan` uses the same host-tool rule as `validate`** (`context_tools/actions/scan/scan.md`):

- Pass **one context tool** whose `_scanner_collection` should run — **Bdd** for spec files, **CleanEngineering** for code under `agents/`.
- Pass explicit **`paths`** — a path without a host is a walk with no rules.
- Do **not** run one scan call “on clean_engineering and bdd together.” Same as validate: **Bdd scan** for specs, **CE scan** for code, sequential if both needed.

**When to run scan standalone**

| When | Use |
|------|-----|
| **Judge loop** | **Do not** — `validate` already calls scan |
| **Doer self-check** before handoff | Optional Bdd or CE scan on changed paths |
| **Single rule debug** | Same host scan + optional `rule:` slug |

**Bdd scan fence (development specs):**

```yaml
toolset: scan.scan:Scan
tool: scan
arguments:
  tools:
    - context_tools.bdd.bdd:Bdd
  paths:
    - agents
```

**CleanEngineering scan fence (code):**

```yaml
toolset: scan.scan:Scan
tool: scan
arguments:
  tools:
    - context_tools.clean_engineering.clean_engineering:CleanEngineering
  paths:
    - agents
```

Optional: add `rule: <slug>` to narrow to one scanner.

### Doer after judge FAIL

**Generation agent fixes violations** — not the judge (`validate.md`: “Do not fix. Report failures for fixing, then validate again when ready.”).

1. Read the judge verdict: **validate report** (every named rule / context failure) + **pytest** failures.
2. Edit only under the same paths the increment touched (`agents/`, `agents/.context/` as scoped).
3. Fix **every** reported violation — specs, code, missing module-context, scan failures — without adding the next increment’s scope.
4. Re-run **pytest** locally if helpful; then hand back to the **judge** for **`validate`** again.
5. Repeat until judge PASS.

**Judge standard pass (every increment):**

```text
1. If doer changed specs  → Bdd · development · validate  (path: agents)
2. If doer changed code   → CleanEngineering · code · validate  (path: agents)
3. pytest                 — development specs for this increment
4. Inc 10 / 12 only       — agent BDD pytest after vanilla judge green
5. Verdict                — PASS | FAIL + bullet defects (no fixes in judge turn)
6. If FAIL                — doer fixes violations → judge repeats from step 1
```

**Doer standard handoff to judge:**

```text
- Sketch/stories slice implemented (cite story heading + CE classes)
- List files created/changed under agents/
- List spec files and pytest -k filter to run
```

---

## Where artifacts live

| Artifact | Path |
|----------|------|
| Production modules | `agents/**/*.py` |
| Vanilla BDD (mamba) | `agents/**/*_spec.py` or `agents/**/test_*.py` |
| Agent BDD (inc 10, 12) | `agents/**/*_agent_spec.py` + `agents/.context/.agent_bdd_sessions/<scenario>.json` |
| Module context (when needed) | `agents/.context/module-context.md` |
| InMemory / fakes | colocated with module under test |

---

## Increments — doer / judge checklist

**Precondition for increment N:** increments `1 … N-1` judge-green.

**Doer pattern (every increment):** read the named **stories** + **sketch** classes for this slice → `/clean_engineering.code` + `/bdd.development` → hand to judge.

**Judge pattern (every increment):** Bdd validate · CE validate · pytest (and agent BDD on inc 10 / 12 only).

---

### Increment 1 — One task, stubbed doer

**From sketch/stories:** `Agent`, `AgentTask`, `AgentParticipant` · `Complete Agent Task` (doer only)  
**Vanilla only** — no agent BDD

**Doer:** stub `_send` / `_await_*`; one task → log kinds `send`, `accepted`, `done`

---

### Increment 2 — Doer + judge, stubbed

**From sketch/stories:** `_wait_verdict`, `_complete_task`, kick on FAIL · `Complete Agent Task With Judge and Human` (human optional stub)

**Doer:** PASS → Done; FAIL → kick + retry (base `Agent`; no `maxFails` yet)

---

### Increment 3 — Manifest / turn fence

**From sketch/stories:** `Turn`, tools CLI fence · `Complete Agent Task` (tools / actions / utilities branches)

**Doer:** stub turn open/finish + `append_tool`; fence fields `sessionName`, `contextRoot`, turn id

---

### Increment 4 — Backlog → current

**From sketch/stories:** `add_tasks`, `clear_backlog`, `_launch_next` · `Add Agent Tasks To Backlog` · `Launch Next Task As Current`

**Doer:** refuse `_launch_next` while participant in flight

---

### Increment 5 — Queue drain + template

**From sketch/stories:** `load_template`, `run` drain · `Load Agent Tasks From Template` · `Complete Task And Advance Queue`

**Doer:** multi-task drain; `validation_error` skip vs workflow fault stop

---

### Increment 6 — AgentSession open

**From sketch/stories:** `AgentSession.open`, `folder`, `branch`, `_ensure_session` · Open Default / Existing / New · Reject Multi Repo

**Doer:** `InMemoryRepo` then real `Repo`; caller sets `contextRoot`

---

### Increment 7 — SubAgent spawn

**From sketch/stories:** `SubAgent` — `_send`, `_launch`, `_tear_down_children`

**Doer:** stub child process; optional judge child

---

### Increment 8 — Transcript watcher

**From sketch/stories:** `AgentRuntimeTranscriptWatcher`, `AIChatFault` · Await Accept / Wait For Done / Read Verdict

**Doer:** fake `.jsonl` + injected clock; wire into CliAgent `_await_*` with stubbed `chat.run`

---

### Increment 9 — CliAgent bind + launch

**From sketch/stories:** `CliAgent` bind/launch overrides · Set Chat Context · Launch Doer/Judge · Complete Agent Task Using Cli Agent

**Doer:** `_bind_workspace_root`, `_bind_chat_context`, `_ensure_chat`; `maxFails` / `_auto_kick_stalled_doer`; stubbed `chat.run`

---

### Increment 10 — CliAgent close + **first agent BDD**

**From sketch/stories:** `close_agents`, `cleanup`, `close_cli_session` · Close Cli Agent Session · Kick Stalled Doer  
**Vanilla first, then agent BDD**

**Doer (vanilla):** close + cleanup specs

**Doer (agent BDD):** `#55 one judged job` — extend `cli_agent_44_one_judged_job_agent_spec.py`  
Session: `agents/.context/.agent_bdd_sessions/one-judged-job-55.json`

**Judge (agent BDD):** single task → log `verdict` PASS; optional isolation prompt checks

**Repeat doer/judge loop** until both vanilla and agent BDD green.

---

### Increment 11 — WorkTicket + start

**From sketch/stories:** `WorkTicket`, `Workflow.start ticket` · Create Work Ticket · Start Opens Session And Branch

**Doer:** `openSession`, sibling worktree, issue body → `contextRoot` (stub or InMemory gh)

---

### Increment 12 — Finish + **capstone agent BDD**

**From sketch/stories:** `AgentSession.finish outcome`, `Workflow.finish ticket`, `branch._persist_chats` · Finish Work Session · Finish Ticket

**Doer (vanilla):** finish paths, chat on close commit, issue Done

**Doer (agent BDD)** — one or both:

| Scenario | Spec name | Prior art |
|----------|-----------|-----------|
| Ticket journey | `#55 start ticket to finish` | workflow + `#44 finish worktree` |
| Two-item queue | `#55 ordered queue` | `cli_agent_44_ordered_queue_agent_spec.py` |

**Repeat doer/judge loop** until vanilla + capstone green.

---

## After all 12

- Update `agents/.context/README.md` with spec index
- Optional `/finish-work-session` when landing the ticket branch
- Do **not** add agent BDD for seams already covered by vanilla (see `bdd-testing-strategy.md` workflow rule)

---

## Quick reference — agent BDD scenarios (named)

| When | Scenario | Prior art |
|------|----------|-----------|
| Inc 10 | `#55 one judged job` | `cli_agent_44_one_judged_job_agent_spec.py` |
| Inc 12 A | `#55 start ticket to finish` | workflow + `#44 finish worktree` |
| Inc 12 B | `#55 ordered queue` | `cli_agent_44_ordered_queue_agent_spec.py` |

Only **three** live-chat journeys for the whole redesign; everything else is vanilla BDD.

---

## Overnight / autonomous execution

**Reality:** A single chat **will stop** after one increment (or mid-increment) unless something **wakes** the agent again. Do not expect 12 increments in one turn.

### Recommended: progress file + loop wake

| Piece | Role |
|-------|------|
| **`increment-progress.md`** | Source of truth for what's done — update every time you stop |
| **`/loop` wake** | Re-opens the agent on a timer with the same continuation prompt |
| **One increment per wake** | Finish **one** increment judge-green, update progress, **stop** — let the loop start the next |

**Before you go to bed (local Cursor, machine stays on):**

1. Ensure worktree/git is usable under `c:\dev\abd-cdd-55` (or note `blocked` in progress).
2. Arm a loop (example — adjust interval):

```text
/loop 45m Read agents/.context/increment-delivery-playbook.md and agents/.context/increment-progress.md. Execute the BOOTSTRAP PROMPT below.
```

3. Run the **Bootstrap prompt** once immediately (same text as each loop tick).

**Bootstrap prompt** — paste this in a **new chat** or each loop tick:

```text
You are continuing GitHub #55 agent-session redesign implementation.

1. Read agents/.context/increment-delivery-playbook.md (full runbook).
2. Read agents/.context/increment-progress.md (what is done).
3. Read agents/.context/agent-session-redesign-sketch.md and agent-session-redesign-stories-sketch.md (source of truth — do not regenerate behavior/modules sketches).
4. Pick the lowest increment still pending (or in_progress if resuming).
5. Set that row to in_progress in increment-progress.md.
6. Execute exactly that ONE increment:
   - Doer: implement from sketch/stories → clean_engineering.code + bdd.development under agents/
   - Judge: Bdd development validate + CE code validate + pytest (agent BDD too on inc 10/12)
   - If judge FAIL: doer fixes every reported violation; judge again until PASS
7. Set that row to judge_green with brief notes (spec paths, pytest -k).
8. Do NOT start the next increment in this turn. Stop after one increment is judge_green.

If blocked (git broken, missing tool, ambiguous sketch): set status blocked, write why, stop.
```

### Cloud agent alternative

If using a **Cloud Agent** with subscription timer MCP: run bootstrap once, then subscribe (e.g. `loop-inc-55`, `delaySeconds: 2700`). Same bootstrap prompt each tick. Unsubscribe when inc 12 is `judge_green`.

### Not recommended as the primary overnight driver

| Approach | Why not alone |
|----------|----------------|
| **One long chat, no loop** | Agent stops; you'll find inc 1 half-done |
| **Sub-agent (`/sub-agent`) non-blocking** | Parent does not wait; no progress guarantee; no built-in judge pass |
| **CliAgent `run_backlog` for all 12** | Built for CLI doer/judge **chat jobs**, not CE code + bdd.development generate/validate loops |
| **12 Task subagents in parallel** | Violates increment order; no shared judge gate; merge hell |

Sub-agent **can** help *within* one increment (e.g. judge as separate sub-agent after doer handoff) but still needs a **parent** pass and progress update — use only if you are awake to orchestrate.

### What “done” looks like in the morning

- `increment-progress.md`: rows 1–12 all `judge_green` (or explicit `blocked` with reason)
- Code under `agents/`; vanilla specs green per increment
- Agent BDD specs exist and pass for inc 10 and 12
- Optional: commit per increment or one commit per phase — **only if user asked**

### New chat checklist

```text
□ increment-delivery-playbook.md
□ increment-progress.md
□ agent-session-redesign-sketch.md
□ agent-session-redesign-stories-sketch.md
□ bdd-testing-strategy.md
□ Bootstrap prompt (above)
□ /loop armed OR user will manually re-paste bootstrap
```

