---
fidelity: [discovery]
artifact: [clean_engineering]
format: md
---

**Sources / context:** `utilities/swarm/.context/story-map.md`; `utilities/plan/.context/module-context.md`; `utilities/swarm/.context/module-context.md`; `utilities/cli_agent/.context/module-context.md`; `utilities/workflow/.context/module-context.md`; `utilities/git/.context/module-context.md`; `utilities/workspace/.context/module-context.md`

## Language companion

*Git* is the store. *Plan*, *Swarm*, and *Workflow* are front-ends to *Repo* / *Project* / *Ticket* / *TicketState*. *Workspace* is the working folder; *Repo* is the backend — not the same.

*Plan* holds ordered *Turn*s. *Turn.state* maps to Project/Workflow columns (Backlog / In Progress / Done). *JudgeCheckpoint* and/or *HILCheck* hang on a *Turn*. *CliAgent* is the worker; it describes hanging *Turn* shape and does not open the *Turn*. When a *Turn* needs a judge, *CliAgent* doer-judge fills *JudgeCheckpoint.judgeResult*.

*Swarm* *Agent* is a *CliAgent* under one *Hypothesis*. *CliAgent.launch_sessions* starts at *Plan.start*. *Supervisor.compare* reads *Turn* judge/HIL results and does not judge. *Plan* does not depend on *Bdd* or *CleanEngineering*.

### plan

- Front-end to git; associated with a *Workspace*; holds ordered *Turn*s
- *start* opens a *WorkSession*

### turn

- Existing *workspace.Turn*; *state* is *TicketState* (Project/Workflow columns)
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

- Owns *Outcome* and *rubric*
- *compare* reads *Turn* judge/HIL results — does not judge
- *associate* updates toward *Outcome*

### agent

- A *CliAgent* under one *Hypothesis*
- Registered at Add Agent; *CliAgent.launch_sessions* at *Plan.start*

### hypothesis

- Unique first-order approach toward the Supervisor *Outcome*

### outcome

- Overarching result owned by *Supervisor*

### researchtag

- Label on an existing *Ticket* (git store)

## Modules

Build order: `git` | `workspace` | `cli_agent` → `plan` → `swarm` | `workflow`

---

# utilities/git

- **Purpose:** Git + GitHub store for tickets and Project columns.
- **Seam (terms):** Repo, Branch, Commit, Project, Ticket, TicketState, ResearchTag
- **Dependencies (one-way):** consumed by `workspace`, `workflow`, `plan`, `swarm`

# utilities/workspace

- **Purpose:** Working folder aggregate (root is that folder). Not the git Repo.
- **Seam (terms):** Workspace, WorkSession, Turn, ToolCall, Mistake, Correction, Repair
- **Dependencies (one-way):** `git`

# utilities/cli_agent

- **Purpose:** Interactive CLI worker and doer-judge for Plan/Swarm.
- **Seam (terms):** CliAgent, IdeCli, CursorCli, VscodeCli
- **Dependencies (one-way):** `sub_agent`, `workspace`

# utilities/plan

- **Purpose:** Front-end to git — ordered Turns; TicketState maps to Project columns.
- **Seam (terms):** Plan, JudgeCheckpoint, HILCheck
- **Dependencies (one-way):** `workspace`, `git`

# utilities/swarm

- **Purpose:** Front-end to git and Plan — Supervisor + CliAgent Agents on a shared turn slice.
- **Seam (terms):** Swarm, Supervisor, Agent, Hypothesis, Outcome
- **Dependencies (one-way):** `plan`, `cli_agent`, `workspace`, `git`

# utilities/workflow

- **Purpose:** Front-end to git — backlog / start / finish Project columns.
- **Seam (terms):** Workflow
- **Dependencies (one-way):** `git`, `workspace`
