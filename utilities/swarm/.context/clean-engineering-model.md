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

*Plan* is based on a reusable *Workflow* or a new *Workflow* named on `/plan`. `/plan /small-work {context}` loads the prebaked *small-work* *Workflow* into a *Plan*. When `context` names a `theme:…`, *SmallWorkRunner* executes that theme's issues one at a time (thin context → Grill + HIL Grill; judge replies via `hil_reply`; then next issue; report when Done). *Plan* holds ordered *Turn*s. *Turn.state* is *TicketState* mapped to Project/Workflow columns — not a parallel store. *JudgeCheckpoint* and/or *HILCheck* hang on a *Turn*. *CliAgent* is the worker; when a *Turn* needs a judge, *CliAgent* doer-judge fills *JudgeCheckpoint.judgeResult*. *Plan* does not depend on *Bdd* or *CleanEngineering* (BDD owns CE companions).

*Start Plan* opens a *WorkSession*; the first Backlog Turn becomes In Progress. *Execute Turn* runs that Turn. *Advance Turn* finishes it (Done) and the next Backlog Turn becomes In Progress.

*Swarm* *Agent* is a *CliAgent* under one *Hypothesis*. *Add Agent* registers; *CliAgent.launch_sessions* starts at *Plan.start* on that Agent’s *WorkSession*. *Supervisor.compare* reads *Turn* judge/HIL results and does not judge. *Comparative Association* updates automatically toward *Outcome*.

### plan

- Front-end to git; based on a reusable or named *Workflow*
- `/plan` / `/plan /small-work {context}` load Workflow into Plan
- *start* opens a *WorkSession*

### workflow

- Front-end to git Project columns; reusable by name (*small-work* is prebaked)
- *Plan* is based on *Workflow*

### turn

- Existing *workspace.Turn*: one *action*; *tool_keys*; *toolCalls*; *fidelity*; *format*; *context*
- *state* is *TicketState*: Project/Workflow Backlog / In Progress / Done
- Optional *JudgeCheckpoint* and/or *HILCheck*

### cliagent

- Worker for Plan and Swarm Agents
- Describes hanging *Turn* shape; does not open the *Turn*
- Doer-judge fills *JudgeCheckpoint* on the *Turn*

### judgecheckpoint

- Hangs on a *Turn*; filled by *CliAgent* doer-judge

### hilcheck

- Human-in-the-loop check on a *Turn*

### swarm

- Front-end to git and *Plan*; *Supervisor* plus *Agent*s; shared *turns* once

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

Build order: `git` | `workspace` | `cli_agent` → `plan` → `swarm` | `workflow`

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

Project exposes named TicketState columns on the board.

Project()
------
----
stateNamed(name: str): TicketState

---

# utilities/workspace

- **Purpose:** Working folder aggregate (root is that folder). Owns WorkSessions and Turns. Not the git Repo.
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

- **Purpose:** Front-end to git. Plan is based on a reusable or named Workflow. `/plan /small-work` loads prebaked small-work Workflow. Turn.state maps to Project/Workflow columns. JudgeCheckpoint hangs on Turn (CliAgent doer-judge). No Bdd/CleanEngineering dependency.
- **Seam (terms):** Plan, PlanExecution, TurnAttachments, TurnTemplate, JudgeCheckpoint, HILCheck, ProgressView
- **Dependencies (one-way):** `workspace`, `git`, `workflow`

## Plan

Plan is based on a Workflow; associated with a Workspace; holds ordered Turns.

Plan()
------
<< association >> workspace: Workspace
<< association >> workflow: Workflow
workflowName: str
<< composition >> turns: list[Turn]
----
create(workspace: Workspace): Plan
from_workflow(workspace: Workspace, workflow: Workflow, workflowName: str): Plan
plan(workflow: str, context: str, workspace: str): dict
small_work(context: str, workspace: str): dict

## TurnTemplate

TurnTemplate is one prebaked Turn shape on a named Workflow.

TurnTemplate()
------
action: str
fidelity: str
format: str
context: str
tool_keys: list[str]
----

## JudgeCheckpoint

JudgeCheckpoint hangs on a Turn; CliAgent doer-judge fills judgeResult.

JudgeCheckpoint()
------
rubric: str
judgeResult: str | None
----

## HILCheck

HILCheck is a human-in-the-loop check on a Turn.

HILCheck()
------
validation: str | None
----

---

# utilities/cli_agent

- **Purpose:** Interactive CLI worker and doer-judge for Plan and Swarm Agents.
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

- **Purpose:** Front-end to git and Plan. Supervisor + CliAgent Agents on shared Swarm.turns. Compare reads Turn JudgeCheckpoint results; does not judge.
- **Seam (terms):** Swarm, Supervisor, Agent, Hypothesis, Outcome
- **Dependencies (one-way):** `plan`, `cli_agent`, `workspace`, `git`

## Swarm

Swarm holds the Plan, the shared turns slice, Supervisor, and Agents.

Swarm()
------
<< association >> plan: Plan
<< association >> turns: list[Turn]
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
start_plan(workspace: Workspace, swarm_turns: list[Turn]): WorkSession
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

- **Purpose:** Front-end to git Project columns (backlog / start / finish).
- **Seam (terms):** Workflow
- **Dependencies (one-way):** `git`, `workspace`

## Workflow

Workflow()
------
----
backlog(focus: str, context: str): dict
start(ticket: str, instructions: str, workspace: str): dict
finish(outcome: str, workspace: str): dict
