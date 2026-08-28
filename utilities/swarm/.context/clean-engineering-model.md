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

*Plan* is associated with a *Workspace*. It holds ordered *Turn*s. Each *Turn* has one *action* and may hold multiple tools via *tool_keys* and *toolCalls*. *Turn.state* is *TicketState* (Backlog / In Progress / Done). A *JudgeCheckpoint* and/or *HILCheck* may hang on a *Turn*. *CliAgent* describes the hanging *Turn* shape (`action`, `tool_keys`, `toolCalls`) and does not open the *Turn*; the CLI opens the hanging *Turn* and finishes it after the action. No *PlannedTurn*. No *Plan* on *CliAgent*.

*Start Plan* opens a *WorkSession*; the first Backlog Turn becomes In Progress. *Execute Turn* runs that Turn. *Advance Turn* finishes it (Done) and the next Backlog Turn becomes In Progress.

*Swarm* comes after Execute Plan. *Create Supervisor* owns *Outcome*. A shared *Swarm.turns* slice is selected once before any Agent runs. *Add Agent* owns *Hypothesis* and registers the Agent. *SubAgent.run* launches at *Plan.start* on that Agent’s own *WorkSession*; each Agent runs the shared slice. *Compare Swarm Results* streams after each Judge or HIL evaluation. *Comparative Association* updates automatically under the Supervisor rubric toward *Outcome*.

*ResearchTag* is ticket metadata on the existing *Ticket* / *Project* graph in **git**, keyed by GitHub issue `#`. *TicketState* remains Backlog / In Progress / Done.

### plan

- Associated with a *Workspace*; holds ordered *Turn*s
- *start* opens a *WorkSession*

### turn

- Existing *workspace.Turn*: one *action*; *tool_keys*; *toolCalls*; *fidelity*; *format*; *context*
- *state* is *TicketState*: Backlog / In Progress / Done
- Optional *JudgeCheckpoint* and/or *HILCheck*

### cliagent

- Describes hanging *Turn* shape (`action`, `tool_keys`, `toolCalls`)
- Does not open the *Turn*; CLI opens and finishes after the action
- Holds no *Plan*

### judgecheckpoint

- AI judge against a rubric on a *Turn* — same *rubric* argument as *ai_judge*

### hilcheck

- Human-in-the-loop check on a *Turn*

### swarm

- *Supervisor* plus *Agent*s on a *Plan*
- Holds shared *turns* chosen once before Agents run
- Each Agent runs Execute Plan on that shared slice in its *WorkSession*

### supervisor

- Owns the overarching *Outcome* and *rubric*
- *compare* streams after each Judge or HIL evaluation
- *associate* updates automatically after each streamed compare toward Outcome

### agent

- A *SubAgent* running the *Plan* under one *Hypothesis*
- Registered at Add Agent; *SubAgent.run* launches at *Plan.start* on its *WorkSession*

### hypothesis

- The unique first-order approach toward the Supervisor *Outcome*

### outcome

- Overarching result owned by *Supervisor*

### researchtag

- Label on an existing *Ticket* for research/flow metadata

## Modules

Build order: `git` | `workspace` | `sub_agent` → `plan` → `swarm`

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

- **Purpose:** Workspace aggregate parent of `.context/`; owns WorkSessions and path overrides. Turn kit holds hanging turn state including action, tool_keys, and toolCalls. CliAgent describes hanging Turn shape; CLI opens and finishes the Turn.
- **Seam (terms):** Workspace, WorkSession, Turn, ToolCall, Mistake, Correction, Repair, CliAgent, TicketState
- **Dependencies (one-way):** `tools.tool`, `git`; consumed by `plan`, context tools

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

- **Purpose:** Owns a Plan associated with a Workspace: ordered Turns. Turn.state is TicketState. Optional JudgeCheckpoint and/or HILCheck hang on a Turn. Start Plan opens a WorkSession; Execute Turn runs the In Progress Turn; Advance Turn finishes and moves the next Backlog Turn to In Progress.
- **Seam (terms):** Plan, JudgeCheckpoint, HILCheck
- **Dependencies (one-way):** `workspace`

## Plan

Plan is associated with a Workspace and holds ordered Turns.

Plan()
------
<< association >> workspace: Workspace
<< composition >> turns: list[Turn]
----
create(workspace: Workspace): Plan
start(): WorkSession
executeTurn(): None
advanceTurn(): None

## JudgeCheckpoint

JudgeCheckpoint is an AI judge against a rubric on a Turn — same rubric argument as ai_judge.

JudgeCheckpoint()
------
rubric: str
judgeResult: str | None
----

## HILCheck

HILCheck is a human-in-the-loop check on a Turn.

HILCheck()
------
----

---

# utilities/sub_agent

- **Purpose:** Non-blocking SubAgent launch seam. SubAgent.run launches the worker; when actions are listed those kits open the session/turn; otherwise performTurn wraps listed context-tool work.
- **Seam (terms):** SubAgent
- **Dependencies (one-way):** `tools.tool`, `harness`, `primitives.actions`

## SubAgent

SubAgent is the non-blocking launch seam used by Swarm Agents.

SubAgent()
------
----
run(tools: list, actions: list): None

---

# utilities/swarm

- **Purpose:** Create Supervisor (Outcome) then select shared Swarm.turns once; Add Agent registers Hypothesis; SubAgent.run launches at Plan.start on each Agent WorkSession running that slice. Compare streams after Judge/HIL; associate updates automatically under Supervisor rubric toward Outcome.
- **Seam (terms):** Swarm, Supervisor, Agent, Hypothesis, Outcome
- **Dependencies (one-way):** `plan`, `sub_agent`

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

Supervisor owns Outcome and rubric; compare streams after Judge/HIL; associate updates automatically toward Outcome.

Supervisor()
------
<< composition >> outcome: Outcome
rubric: str
<< composition >> agents: list[Agent]
----
addAgent(hypothesis: Hypothesis): Agent
compare(): None
associate(): None

## Agent

Agent is a SubAgent running the Plan under one Hypothesis. Registered at Add Agent; SubAgent.run launches at Plan.start on its WorkSession.

Agent()
------
<< association >> plan: Plan
<< composition >> hypothesis: Hypothesis
<< association >> workSession: WorkSession | None
----

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
