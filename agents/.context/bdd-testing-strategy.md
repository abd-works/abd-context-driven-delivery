# Agent session redesign — BDD testing strategy

issue: 55
source: dialogue while finishing `agent-session-redesign-stories-sketch.md`
related:
  - `agents/.context/agent-session-redesign-sketch.md` (CE modules)
  - `agents/.context/agent-session-redesign-stories-sketch.md` (story map + behavior trees)

---

## Lesson learned (#44 / pre-redesign)

We moved through vanilla BDD and object modeling **too fast**, then tried to prove orchestration with **agent BDD** on flows that looked simple (one judged job, ordered queue) but pulled in worktree bind, spawn, transcript watch, queue advance, judge spawn, and close **all at once**.

Agent BDD became the integration test suite. Each run surfaced another **code** bug. After hours of fixes, agent BDD kept finding more — an endless cycle. That is the wrong tool for discovering orchestration seams.

**Today’s fix:** name **proper seams** in the stories sketch (session, queue, Cli mechanics, ticket) with defer stories — then build **vanilla BDD per seam** before any live-chat journey. Agent BDD becomes a **thin gate**, not the primary debugger.

---

## Two test layers

| Layer | Tool | What it proves | How |
|-------|------|----------------|-----|
| **Vanilla BDD** | `bdd` behavior specs | Orchestration **contract**: state, paths, log kinds, timeouts, faults | Fake transcript `.jsonl`, injected `clock` / `sleep`, stubbed `chat.run`, `run_backlog` hooks |
| **Agent BDD** | `agent_bdd` | **Behavior**: did a real chat reasonably do the work? | Live cursor-agent (or in-chat harness), artifacts on disk, `ai_judge` on file contents |

Stories sketch header rule:

> vanilla BDD signatures for code seams; agent BDD GWT later for agent-facing journeys

From `agent_bdd.md`: if agent BDD fails on **code**, fix code **and** add vanilla BDD that would have caught it. Prompt-only failures stay in agent BDD.

---

## Vanilla BDD — what it is / is not

**Is not:** spinning up real AI chat runtimes or judging LLM output quality.

**Is:** testing the **watcher and orchestrator** against simulated signals:

- **Await Accept** — fake jsonl gains a user line before deadline → accepted + log; timeout + dead pid → `not_accepted`
- **Wait For Done** — append lines on fake clock → growth then quiet → done; no growth → `stall`
- **Read Verdict** — PASS/FAIL parsed from jsonl **shape** (flat and Cursor-nested), not whether the judge reasoned well
- **Launch / bind** — stub spawn; assert `workspacePath`, `sessionName`, log kinds
- **Queue** — `run_backlog` with hooks first, then stubbed spawn; refuse while in flight; advance on complete
- **Close Cli** — bindings cleared, no zombie PIDs, temps removed, durable artifacts kept

Existing patterns to extend: `_TranscriptWatch.wait_for_growth(..., sleep=, clock=)`, `_Pickup.accepted`, `#44` `run_backlog` hook tests in `cli_agent_spec.py`.

---

## Agent BDD — when it runs

**After** vanilla BDD is green on the increment being exercised.

Suggested journeys (map to increments above — not per-story duplication):

1. **Inc 10** — one judged backlog item (doer + judge; extend `#44 one judged job` to redesign model)
2. **Inc 12** — ordered queue (two items) **or** start-ticket → PASS → finish ticket
3. Session / worktree isolation (prompt + doc regression — fold into Inc 10–12 agent BDD)

Agent BDD must **not** be the first test that proves transcript grew, worktree bound, or queue advanced.

---

## Recommended pyramid (Option A)

```
        ┌─────────────────────┐
        │  2–4 Agent BDD      │  nightly / manual gate
        ├─────────────────────┤
        │  ~30–50 Vanilla BDD │  every PR — one spec per story seam
        └─────────────────────┘
```

**Increments (12 — evolutionary, plumbing last):**

Build each row **vanilla first**; agent BDD only where the column says so — and only after that increment’s vanilla specs are green.

| # | Increment | Vanilla first (what goes green) | Agent BDD after green |
|---|-----------|--------------------------------|------------------------|
| 1 | **One task, stubbed doer** | Single `AgentTask`; stub `_send` / `_await_accept` / `_await_done`; log kinds `send`, `accepted`, `done`; no git, no chat | — |
| 2 | **Doer + judge, stubbed** | Same stubs; `_wait_verdict`; PASS → `_complete_task` Done; FAIL → kick + retry same task | — |
| 3 | **Manifest / turn fence** | Stub `chat.run` + tools CLI path: slash → action begin/end, `Turn.open` / `Turn.finish`, `append_tool`; context guidance carries `sessionName`, `contextRoot`, turn id; tools / actions / utilities from doer prompt | — |
| 4 | **Backlog → current** | `add_tasks`, `clear_backlog`; `_launch_next`; refuse `_launch_next` while doer/judge/human in flight; stubbed participants only | — |
| 5 | **Queue drain + template** | Two+ tasks; `load_template` → `_instantiate_tasks` → `add_tasks`; `run` drains backlog; `validation_error` skips task; workflow fault stops run | — |
| 6 | **AgentSession open** | `InMemoryRepo` then real `Repo`; `session.open` → folder, `branch.checkout_or_create`, log `open`; caller sets `contextRoot`; `_ensure_session` before `run` | — |
| 7 | **SubAgent spawn** | SubAgent `_send` via stubbed child process; `_launch` non-blocking; `_tear_down_children` on `agent.close`; judge optional | — |
| 8 | **Transcript watcher** | Fake `.jsonl` + injected clock; `AgentRuntimeTranscriptWatcher` accept / growth-then-quiet / verdict; `AIChatFault` `not_accepted`, `stall`; wired into CliAgent `_await_*` with **stubbed** `chat.run` | — |
| 9 | **CliAgent bind + launch** | `_bind_workspace_root`, `_bind_chat_context`, `_ensure_chat`; `_launch_doer` / `_launch_judge` with stubbed `AIChatInstance`; `maxFails` / `failCount`; `_auto_kick_stalled_doer` | — |
| 10 | **CliAgent close** | `close_agents`, `cleanup`, `close_cli_session`; bindings cleared; no zombie PIDs; temps removed | **One judged job** (doer + judge, real or harness chat) |
| 11 | **WorkTicket + start** | `WorkTicket.create`, `openSession`, `start`; `Workflow.start ticket` → `add_tasks` + `run`; sibling worktree path; issue body → `contextRoot` | — |
| 12 | **Finish + capstone** | `AgentSession.finish outcome` (chats on close commit via `branch._persist_chats`); `Workflow.finish ticket`; multi-repo reject | **Ticket journey** or **two-item queue** |

**Why session opens at 6 (not 1):** increments 1–5 prove Agent queue + participant orchestration + manifest/turn contract with **stubbed** runtimes — no worktree, no transcript files, no IDE. That is most of the business logic. Increment 6 adds the real session seam (folder, branch, log) because isolation and `_ensure_session` need it; increment 7 adds SubAgent before CLI because child spawn is a separate participant strategy. CLI plumbing (8–10) layers on only after orchestration is already green under stubs.

**Pyramid per phase:**

```
Inc 1–5   ~15–20 vanilla   (Agent core, no plumbing)
Inc 6–7   ~8–10 vanilla    (session + SubAgent)
Inc 8–10  ~10–15 vanilla   (CliAgent)  + 1 agent BDD @10
Inc 11–12 ~8–10 vanilla    (Workflow)  + 1–2 agent BDD capstones
```

**Step-by-step delivery (doer/judge, tools, pytest):** `increment-delivery-playbook.md`

---

## Story → test type (summary)

### Vanilla only

- Reject multi-repo, Open Default/Existing/New, Close Agent Session, Finish Work Session (chats on close commit)
- Add tasks, Load template, Launch Next, Complete & Advance, Kick Stalled Participant
- Set Chat Context, Launch Doer/Judge, Await Accept, Wait For Done, Read Verdict
- Close Cli Agent Session, Kick Stalled Doer
- Ticket create/start/finish (structural)
- SubAgent spawn/teardown (not instruction grep alone)

### Defer-only story anchors (no separate specs)

- Complete Agent Task Using Sub/Cli Agent
- Run Agent Task Queue Using Cli Agent

### Agent BDD only (after vanilla)

- Doer runs context tools/actions with reasonable outcome
- Judge qualitative validation
- Full journeys above
- Prompt/instruction regression (isolation, thin doer, no self-driving queue)

---

## Error-prone seams — vanilla first

Build these **before** agent BDD on increment 10 (map to vanilla increments):

| Seam | Vanilla increment |
|------|---------------------|
| Stub doer/judge orchestration + log kinds | 1–2 |
| Manifest / turn fence (tools, actions, utilities) | 3 |
| `_launch_next` refuse while in flight; queue drain | 4–5 |
| `AgentSession.open`, `contextRoot`, `_ensure_session` | 6 |
| SubAgent spawn / teardown | 7 |
| Await Accept / Wait For Done / Read Verdict (fake jsonl + clock) | 8 |
| Set Chat Context — bind worktree; no durable CliAgent on main before worktree | 9 |
| Complete & Advance — validation-error skip vs workflow-fault stop; maxFails | 5, 9 |
| Close Cli — processes stopped, bindings cleared | 10 |
| Finish Work Session — chats on **close commit** via `branch._persist_chats`; never on `Turn.finish` | 12 |
| Kick Stalled Doer — automatic, no user intervention | 9–10 |

---

## Old BDD inventory (pre-redesign)

**Had real vanilla coverage:** `cli_agent_spec.py` (run_backlog hooks, log kinds, pickup, read_verdict units, bind-before-start-ticket, cleanup), `workflow_spec.py` (open_ticket_session), `sub_agent_spec.py` (markers/instructions).

**Gaps that let agent BDD find endless code bugs:**

- No `AgentSession` / redesign model specs
- Transcript units not wired `_send → accept → done → verdict` as one seam
- No `close_agents` / `close_cli_sessions` specs
- No named `AIChatFault` contract tests
- SubAgent / Cli capstone integration missing
- Agent BDD often doc-grep or full E2E without structural floor

**New stories sketch fixes structure; tests still to generate.**

---

## Workflow rule (break the cycle)

1. Vanilla BDD on **one seam** → green  
2. Next seam up → green (still no IDE)  
3. Full increment vanilla → green  
4. **One** agent BDD journey  
5. If agent BDD red → triage:  
   - **Code** → fix + **must** add vanilla repro for that failure class  
   - **Prompt** → fix guidance / rubric only  

Never run the full agent journey again for a bug class that lacks a vanilla repro.

---

## Terminology (stories sketch)

- **AI chat runtime** — live chat side; context guidance destination
- **agent runtime** — doer/judge runtimes where prompts run
- **AIChatInstance** — CE type for CLI realization (Cursor, VS Code, …)
- **session.folder** — `.agent_sessions/{name}/` orchestration (log, state) — not contextRoot
- **contextRoot** — any repo path for context-tool artifacts; resolved via path / Workspace lookup
- **workspacePath** — branch worktree path for git cwd and agent runtime — not contextRoot
- Not “IDE chat” in story prose
