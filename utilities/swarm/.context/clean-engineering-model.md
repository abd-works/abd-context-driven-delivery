**Sources / context:** `utilities/swarm/.context/plan-and-swarm-sketch.md`; `utilities/swarm/.context/grill-answers.md`; `utilities/swarm/.context/story-map.md`; `utilities/plan/.context/module-context.md`; `utilities/swarm/.context/module-context.md`; `utilities/workspace/.context/module-context.md`; `utilities/git/.context/module-context.md`; `utilities/sub_agent/.context/module-context.md`; `context_tools/agent_bdd/.context/module-context.md`

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

## Ticket

## ResearchTag

## TicketState

## Project

---

# utilities/workspace

- **Purpose:** Workspace aggregate parent of `.context/`; owns WorkSessions and path overrides. Turn kit holds hanging turn state including action, tool_keys, and toolCalls.
- **Seam (terms):** Workspace, WorkSession, Turn, ToolCall, Mistake, Correction, Repair, CliAgent, TicketState
- **Dependencies (one-way):** `tools.tool`; consumed by `plan`, context tools

## Workspace

## WorkSession

## Turn

## CliAgent

## ToolCall

## Mistake

## Correction

## Repair

---

# utilities/plan

- **Purpose:** Owns a Plan associated with a Workspace: ordered Turns. Turn.state is TicketState. Optional JudgeCheckpoint and/or HILCheck hang on a Turn. Start Plan opens a WorkSession; Execute Turn runs the In Progress Turn.
- **Seam (terms):** Plan, JudgeCheckpoint, HILCheck
- **Dependencies (one-way):** `workspace`

## Plan

## JudgeCheckpoint

## HILCheck

---

# utilities/sub_agent

- **Purpose:** Non-blocking SubAgent launch seam. SubAgent.run launches the worker; when actions are listed those kits open the session/turn; otherwise performTurn wraps listed context-tool work.
- **Seam (terms):** SubAgent
- **Dependencies (one-way):** `tools.tool`, `harness`, `primitives.actions`

## SubAgent

---

# utilities/swarm

- **Purpose:** Create Supervisor (Outcome) then select shared Swarm.turns once; Add Agent registers Hypothesis; SubAgent.run launches at Plan.start on each Agent WorkSession running that slice. Compare streams after Judge/HIL; associate updates automatically under Supervisor rubric toward Outcome.
- **Seam (terms):** Swarm, Supervisor, Agent, Hypothesis, Outcome
- **Dependencies (one-way):** `plan`, `sub_agent`

## Swarm

## Supervisor

## Agent

## Hypothesis

## Outcome
