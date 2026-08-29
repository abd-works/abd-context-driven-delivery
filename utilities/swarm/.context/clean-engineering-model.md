<!-- @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering -->
<!-- invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering -->
<!-- invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering -->

---
fidelity: [spec]
artifact: [clean_engineering]
format: md
---

**Sources / context:** `utilities/swarm/.context/plan-and-swarm-sketch.md`; `utilities/swarm/.context/grill-answers.md`; `utilities/swarm/.context/story-map.md`; `utilities/plan/.context/module-context.md`; `utilities/swarm/.context/module-context.md`; `utilities/workspace/.context/module-context.md`; `utilities/git/.context/module-context.md`; `utilities/sub_agent/.context/module-context.md`; `utilities/cli_agent/.context/module-context.md`

## Language companion

*Git* is the store. *Plan*, *Swarm*, and *Workflow* are front-ends to *Repo* / *Project* / *Ticket*. *Workspace* is the working folder; *Repo* is the backend — not the same. Never treat git root as workspace.

A *Workflow* is **states** on **its own GitHub Project** (one Project per Workflow). Project 1 is the **global inbox**. A *Plan* is that Workflow **plus** the ticket set — **no planned-turn list**. FIFO is the default; the agent may batch related tickets. Moving a ticket off the inbox onto a flow board / into a state **creates a real *Turn***. Per-state behavior lives in `workflow/flows/{name}.yaml` (tools, one action, utilities, prose, optional hil/judge, owner + project_number); columns stay on GitHub. `/start-ticket /small-work 14` starts #14 on that board; unnamed start stays inbox In Progress. Harness puts Projects into prompts. Flow-done cards stay on the flow board until `/finish-plan`. Throwaway yaml + temp Project deleted on `/finish-plan`; saved Project/yaml stay. Kit + board only — no GitHub Actions.

*JudgeCheckpoint* and/or *HILCheck* hang on a *Turn* when the entered state marks them. *CliAgent* is the worker; doer-judge fills *judgeResult*. *Plan* does not depend on *Bdd* or *CleanEngineering* (BDD owns CE companions).

*Swarm* *Agent* is a *CliAgent* under one *Hypothesis*. *Add Agent* registers; *CliAgent.launch_sessions* starts at *Plan.start* on that Agent’s *WorkSession*. *Supervisor.compare* reads *Turn* judge/HIL results and does not judge. *Comparative Association* updates automatically toward *Outcome*.

### plan

- *Workflow* + ticket set (serial or parallel per Plan); no planned-turn list
- `/plan` / `/plan /small-work {context}` load Workflow into Plan
- `/start-ticket /{flow} N` / `/finish-plan`
- *start* opens a *WorkSession*

### workflow

- One GitHub *Project* per Workflow; Status columns are states
- Behavior in `workflow/flows/{name}.yaml`; saved vs throwaway
- *small-work* is a prebaked named Workflow
- Kit reads/writes Status — no GitHub Actions

### turn

- Existing *workspace.Turn*; created when a ticket enters a flow state
- One *action*; *tool_keys*; *toolCalls*; optional *JudgeCheckpoint* and/or *HILCheck* from state yaml

### cliagent

- Worker for Plan and Swarm Agents
- Describes hanging *Turn* shape; does not open the *Turn*
- Doer-judge fills *JudgeCheckpoint* on the *Turn*

### judgecheckpoint

- Hangs on a *Turn*; filled by *CliAgent* doer-judge

### hilcheck

- Human-in-the-loop check on a *Turn*

### swarm

- Front-end to git and *Plan*; *Supervisor* plus *Agent*s; shared flow/ticket slice once

### supervisor

- Owns the overarching *Outcome* and *rubric*
- *compare* reads *Turn* judge/HIL results — does not judge
- *associate* updates automatically after each streamed compare toward Outcome

### agent

- A *CliAgent* running the *Plan* under one *Hypothesis*
- Registered at Add Agent; *CliAgent.launch_sessions* at *Plan.start* on its *WorkSession*

### hypothesis

- The unique first-order approach toward the Supervisor *Outcome*

### outcome

- Overarching result owned by *Supervisor*

### researchtag

- Label on an existing *Ticket* (git store)

## Modules

Build order: `git` | `workspace` | `cli_agent` → `workflow` → `plan` → `swarm`

---

# utilities/git

- **Purpose:** OO git + GitHub domain for CDD workspace sessions and workflow commands. Callers manage research tags, notes, and ticket/session flow on the existing Repo / Project / Ticket / TicketState graph — git-primary notes and trailers, not a second ticket store.
- **Seam (terms):** Repo, Branch, Commit, Project, Ticket, TicketState, Git, ResearchTag
- **Dependencies (one-way):** `tools.tool`; consumed by `workspace`, `workflow`

## Repo

Repo holds Ticket and Project flow for research tags and notes.

Repo()
------
----
ticket(ref: str): Ticket
note(ticket: Ticket, text: str): None
readNotes(ticket: Ticket): list[str]

## Ticket

Ticket is keyed by GitHub issue number and holds research tags, notes, and TicketState.

Ticket()
------
number: int
researchTags: list[ResearchTag]
notes: list[str]
state: TicketState
----
setStatus(state: TicketState): None
parseNumber(ref: str): int

## ResearchTag

ResearchTag is a label on an existing Ticket for research/flow metadata.

ResearchTag()
------
name: str
----

## TicketState

TicketState is Backlog | In Progress | Done — same type on Ticket and on Turn.

TicketState()
------
name: str
----

## Project

Project exposes named TicketState columns on the board. Project 1 is the global inbox; each Workflow has its own Project whose Status columns are that flow’s states.

Project()
------
owner: str
number: int
----
stateNamed(name: str): TicketState
addTicket(ticket: Ticket): None
removeTicket(ticket: Ticket): None

---

# utilities/workspace

- **Purpose:** Working folder aggregate (root is that folder). Owns WorkSessions and Turns (created when a ticket enters a flow state). Not the git Repo.
- **Seam (terms):** Workspace, WorkSession, Turn, ToolCall, Mistake, Correction, Repair, TicketState
- **Dependencies (one-way):** `git`; consumed by `plan`, context tools

## Workspace

Workspace is the parent of `.context/` and owns WorkSessions.

Workspace()
------
workSessions: list[WorkSession]
----
openWorkSession(name: str): WorkSession

## WorkSession

WorkSession owns Turns, the open Turn, and Repairs.

WorkSession()
------
turns: list[Turn]
openTurn: Turn | None
repairs: list[Repair]
----

## Turn

Turn is the existing workspace.Turn: one action; multiple tools via tool_keys and toolCalls; state is TicketState.

Turn()
------
prompt: str
result: str
context: str
action: str
fidelity: str
format: str
tool_keys: list[str]
<< composition >> toolCalls: list[ToolCall]
state: TicketState
<< association >> judgeCheckpoint: JudgeCheckpoint | None
<< association >> hilCheck: HILCheck | None
mistakes: list[Mistake]
correction: Correction | None
----
finish(prompt: str, result: str, context: str): None
recordMistake(): Mistake
recordCorrection(): Correction
performTurn(): None

## CliAgent

CliAgent describes hanging workspace.Turn shape (action, tool_keys, toolCalls) and does not open the Turn; CLI opens and finishes after the action. Holds no Plan.

CliAgent()
------
action: str
tool_keys: list[str]
toolCalls: list[ToolCall]
----

## ToolCall

ToolCall names a toolset member invoked on a Turn.

ToolCall()
------
toolset: str
name: str
----

## Mistake

Mistake records a fault on a Turn before Fix and Rerun.

Mistake()
------
----

## Correction

Correction records the fix paired with a Mistake on a Turn.

Correction()
------
----

## Repair

Repair is held on WorkSession.repairs for Fix and Rerun.

Repair()
------
----

---

# utilities/plan

- **Purpose:** Front-end to git. Plan = Workflow + tickets (no planned-turn list). `/start-ticket /{flow} N`; `/finish-plan`. FIFO default; agent may batch. JudgeCheckpoint/HILCheck hang on Turn when state yaml marks them (CliAgent doer-judge). No Bdd/CleanEngineering dependency.
- **Seam (terms):** Plan, PlanExecution, TurnAttachments, JudgeCheckpoint, HILCheck, ProgressView
- **Dependencies (one-way):** `workspace`, `git`, `workflow`

## Plan

Plan is a Workflow plus a ticket set; associated with a Workspace. Turns are created by flow moves, not pre-listed.

Plan()
------
<< association >> workspace: Workspace
<< association >> workflow: Workflow
workflowName: str
tickets: list[Ticket]
----
create(workspace: Workspace): Plan
from_workflow(workspace: Workspace, workflow: Workflow, workflowName: str, tickets: list[Ticket]): Plan
plan(workflow: str, context: str, workspace: str): dict
small_work(context: str, workspace: str): dict
start_ticket(flow: str, number: int): Turn
finish_plan(): None

## JudgeCheckpoint

JudgeCheckpoint hangs on a Turn when the entered state yaml includes a rubric; CliAgent doer-judge fills judgeResult.

JudgeCheckpoint()
------
rubric: str
judgeResult: str | None
----

## HILCheck

HILCheck hangs on a Turn when the entered state yaml marks hil.

HILCheck()
------
prompt: str | None
validation: str | None
----

---

# utilities/cli_agent

- **Purpose:** Interactive CLI worker and doer-judge for Plan and Swarm Agents. Keeps context across calls; may batch related tickets.
- **Seam (terms):** CliAgent, IdeCli, CursorCli, VscodeCli
- **Dependencies (one-way):** `sub_agent`, `workspace`

## CliAgent

CliAgent is the worker; describes hanging Turn shape; launch_sessions starts doer (and judge when IdeCli.judge is set).

CliAgent()
------
<< association >> ide: IdeCli
----
launch_sessions(tools: list, actions: list): str

---

# utilities/swarm

- **Purpose:** Front-end to git and Plan. Supervisor + CliAgent Agents on a shared flow/ticket slice (not a planned-turn list). Compare reads Turn JudgeCheckpoint results; does not judge.
- **Seam (terms):** Swarm, Supervisor, Agent, Hypothesis, Outcome
- **Dependencies (one-way):** `plan`, `cli_agent`, `workspace`, `git`

## Swarm

Swarm holds the Plan, the shared flow/ticket slice, Supervisor, and Agents.

Swarm()
------
<< association >> plan: Plan
tickets: list[Ticket]
<< composition >> supervisor: Supervisor | None
<< composition >> agents: list[Agent]
----

## Supervisor

Supervisor owns Outcome and rubric; compare reads Turn judge/HIL results — does not judge.

Supervisor()
------
<< composition >> outcome: Outcome
rubric: str
<< composition >> agents: list[Agent]
----
addAgent(hypothesis: Hypothesis): Agent
compare(event: dict): list
associate(event: dict): list

## Agent

Agent is a CliAgent running the Plan under one Hypothesis. Registered at Add Agent; CliAgent.launch_sessions at Plan.start on its WorkSession.

Agent()
------
<< association >> plan: Plan
<< composition >> hypothesis: Hypothesis
<< association >> agentWorkSession: WorkSession | None
<< association >> ide: IdeCli
----
start_plan(workspace: Workspace): WorkSession
launch_sessions(tools: list, actions: list): str

## Hypothesis

Hypothesis is the unique first-order approach toward the Supervisor Outcome.

Hypothesis()
------
name: str
----

## Outcome

Outcome is the overarching result owned by Supervisor.

Outcome()
------
name: str
----

---

# utilities/workflow

- **Purpose:** Front-end to git — one Project per Workflow; per-state behavior in `workflow/flows/*.yaml`; kit reads/writes Status (no Actions).
- **Seam (terms):** Workflow, FlowState, FlowFile
- **Dependencies (one-way):** `git`, `workspace`

## Workflow

Workflow owns one GitHub Project (states = Status columns) and a flow file for per-state behavior. Saved or throwaway.

Workflow()
------
name: str
<< association >> project: Project | None
throwaway: bool
----
load(name: str): Workflow
save(): FlowFile
compose_throwaway(name: str): Workflow
start_ticket(number: int): Turn
advance(ticket: Ticket, state: str): Turn
finish_plan(): None

## FlowState

FlowState is one Status column on the Workflow’s Project plus optional behavior from the flow file.

FlowState()
------
name: str
tools: list[str]
action: str | None
utilities: list[str]
prose: str | None
hil: bool
judge_rubric: str | None
----

## FlowFile

FlowFile is `workflow/flows/{name}.yaml`: name, optional owner + project_number, per-state behavior. Columns stay on GitHub.

FlowFile()
------
name: str
owner: str | None
project_number: int | None
<< composition >> states: list[FlowState]
----
write(): None
delete(): None
