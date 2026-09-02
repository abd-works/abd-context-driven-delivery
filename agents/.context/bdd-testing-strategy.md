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

## Four test layers (do not invert)

Stories sketch header is the source of truth. Specs must use the same `##` story names, in sketch order.

| Layer | Where | What it proves | Marker |
|-------|--------|----------------|--------|
| **1. Run Agent Runtime** | vanilla + live | Same Agent ops (`_send` / `_await_*`). **AIChatInstance is a handle.** No clocks. | **CliAgent** in `agent_spec.py` (not agentic). SubAgent/ChatAgent live: `(agentic)` |
| **2. Time Agent Runtime** | vanilla + live timeouts | FileSync wait_accept / wait_done | **CliAgent** + SubAgent same stories. SubAgent live: `(agentic)`. ChatAgent has no FileSync. |
| **3. Vanilla story map** | `agent_spec.py` | Orchestration with stubbed runtimes | unmarked |
| **4. Isolate session by subtype** | C test helpers | Same session/queue examples on each Agent | **CliAgent** in `agent_spec.py`. SubAgent/ChatAgent: `(agentic)` |
| **5. End-to-end** | last | Pieces together | **CliAgent** in `agent_spec.py`. SubAgent/ChatAgent: `(agentic)` |

`(agentic)` = `agent_agent_spec.py` / agent_bdd — the subject talks to AI chat (SubAgent child, ChatAgent parent). **CliAgent is never `(agentic)`:** live `CursorChatInstance` stays in vanilla `agents/agent_spec.py`.

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

Live I/O for **Run Agent Runtime** runs first (mailbox, jsonl, parent window) — that is not e2e. E2e journeys run **last**, after vanilla orchestration is green.

If agent BDD fails on **code**, add a vanilla repro under the matching runtime or timing story.

---

## Recommended pyramid

```
        ┌──────────────────────────────┐
        │  End To End (agentic)        │  last
        ├──────────────────────────────┤
        │  Vanilla story map           │  session / queue / ticket
        ├──────────────────────────────┤
        │  Time Agent Runtime          │  subtype clocks
        ├──────────────────────────────┤
        │  Run Agent Runtime           │  FIRST — same ops, three types
        │  (agentic I/O + vanilla stub)│
        └──────────────────────────────┘
```

**Increments (stories sketch footer):**

| # | Increment | What |
|---|-----------|------|
| 0 | **Run Agent Runtime** | send / accept / done / verdict / continue / stop on Agent for CliAgent, SubAgent, ChatAgent. Handle is AIChatInstance. Wait is FileSync (Cli/Sub) or parent window (Chat). No clocks. |
| 0b | **Time Agent Runtime** | FileSync acceptSeconds / stall / quiet — C test CliAgent and SubAgent. ChatAgent has no FileSync. |
| 1 | **Run Agent Session + queue** | Canonical session/queue examples — one set |
| 1b | **Isolate Agent Session By Subtype** | `C test` that set on SubAgent, CliAgent, ChatAgent |
| 2 | **Subtype extras** | children, close_agents, parent ToolsCli — not copies of Complete Task |
| 3 | **Ticket** | Create / Start / Finish |
| 4 | **End To End** | one judged job, two-item queue, start-ticket-to-finish |

**Why runtime ops at 0:** a judged job is the wrong first test of "has the Agent sent a request" and "is FileSync still waiting." Those are `Agent._send` / `_await_*` plus FileSync, not flags on `AIChatInstance`. Time stories add clocks on FileSync. Orchestration stories assume that channel already works.

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

- Run Agent Task Queue Using Cli Agent

### Agent BDD only (after vanilla)

- **Inc 7:** one judged job via SubAgent (doer + judge runtime roles) — first real two-role gate
- Doer runs context tools/actions with reasonable outcome
- Judge qualitative validation
- Full journeys above
- Prompt/instruction regression (isolation, thin doer, no self-driving queue)

---

## Error-prone seams — vanilla first

Build these **before** agent BDD on increment **7** (SubAgent one judged job):

| Seam | Vanilla increment |
|------|---------------------|
| Stub doer/judge orchestration + log kinds | 1–2 |
| Manifest / turn fence (tools, actions, utilities) | 3 |
| `_launch_next` refuse while in flight; queue drain | 4–5 |
| `AgentSession.open`, `contextRoot`, `_ensure_session` | 6 |
| SubAgent spawn / teardown **and** doer+judge runtime roles on one task | 7 |
| Await Accept / Wait For Done / Read Verdict (fake jsonl + clock) — **CliAgent** | 8 |
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
