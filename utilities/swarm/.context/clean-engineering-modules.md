---
fidelity: [discovery]
artifact: [clean_engineering]
format: md
---

**Sources / context:** `utilities/swarm/.context/story-map.md`; `utilities/swarm/.context/grill-answers.md` (ticks 14–33); `utilities/plan/.context/module-context.md`; `utilities/swarm/.context/module-context.md`; `utilities/cli_agent/.context/module-context.md`; `utilities/workflow/.context/module-context.md`; `utilities/git/.context/module-context.md`; `utilities/workspace/.context/module-context.md`

## Language companion

*Git* is the store. *Plan*, *Swarm*, and *Workflow* are front-ends to *Repo* / *Project* / *Ticket* / *TicketState*. *Workspace* is the working folder; *Repo* is the backend — not the same.

A *Workflow* is **states** on **its own GitHub Project** (one Project per Workflow). Project 1 is the **global inbox**. A *Plan* is that Workflow **plus** the ticket set — not a planned-turn list. FIFO is the default; the agent may batch related tickets. Moving a ticket off the inbox onto a flow board / into a state **creates a real *Turn***. Per-state behavior lives in `workflow/flows/{name}.yaml` (tools, one action, utilities, prose, optional hil/judge, owner + project_number); columns stay on GitHub. `/start-ticket /small-work 14` starts #14 on that board; unnamed start stays inbox In Progress. Harness puts Projects into prompts. Flow-done cards stay on the flow board until `/finish-plan`. Throwaway yaml + temp Project deleted on `/finish-plan`; saved Project/yaml stay. Kit + board only — no GitHub Actions.

*JudgeCheckpoint* and/or *HILCheck* hang on a *Turn* when the entered state marks them. *CliAgent* is the worker; doer-judge fills *judgeResult*. *Plan* does not inject Clean Engineering — BDD owns CE companions.

### plan

- *Workflow* + ticket set (serial or parallel per Plan)
- No planned-turn list; FIFO default; agent may batch
- `/plan` / `/small-work` load Workflow into Plan
- `/finish-plan` returns tickets to inbox, closes issues, closes session
- *start* opens a *WorkSession*

### workflow

- One GitHub *Project* per Workflow; Status columns are states
- Behavior in `workflow/flows/{name}.yaml` (tools, one action, utilities, prose, optional hil/judge, owner + number)
- Saved vs throwaway (temp Project + yaml deleted on `/finish-plan`)
- *small-work* is a prebaked named Workflow

### turn

- Existing *workspace.Turn*; created when a ticket enters a flow state
- One action; tool_keys; optional *JudgeCheckpoint* and/or *HILCheck* from state yaml
- CliAgent describes hanging shape; CLI opens and finishes

### cliagent

- Worker for Plan and Swarm Agents
- Describes hanging *Turn* shape; does not open the *Turn*
- Doer-judge fills *JudgeCheckpoint* on the *Turn*

### judgecheckpoint

- Hangs on a *Turn* when the state yaml includes a judge rubric; filled by *CliAgent* doer-judge

### hilcheck

- Human-in-the-loop check on a *Turn* when the state yaml marks hil

### swarm

- Front-end to git and *Plan*; *Supervisor* plus *Agent*s; shared flow/ticket slice once

### supervisor

- Owns *Outcome* and *rubric*
- *compare* reads *Turn* judge/HIL results — does not judge
- *associate* updates toward *Outcome*

### agent

- A *CliAgent* under one *Hypothesis*
- Registered at Add Agent; *CliAgent.launch_sessions* at *Plan.start*
- Keeps context across calls; may batch related tickets

### hypothesis

- Unique first-order approach toward the Supervisor *Outcome*

### outcome

- Overarching result owned by *Supervisor*

### researchtag

- Label on an existing *Ticket* (git store)

## Modules

Build order: `git` | `workspace` | `cli_agent` → `workflow` → `plan` → `swarm`

---

# utilities/git

- **Purpose:** Git + GitHub store for tickets and Projects (inbox Project 1 + one Project per Workflow).
- **Seam (terms):** Repo, Branch, Commit, Project, Ticket, TicketState, ResearchTag
- **Dependencies (one-way):** consumed by `workspace`, `workflow`, `plan`, `swarm`

# utilities/workspace

- **Purpose:** Working folder aggregate (root is that folder). Not the git Repo. *Turn* is created when a ticket enters a flow state.
- **Seam (terms):** Workspace, WorkSession, Turn, ToolCall, Mistake, Correction, Repair
- **Dependencies (one-way):** `git`

# utilities/cli_agent

- **Purpose:** Interactive CLI worker and doer-judge for Plan/Swarm.
- **Seam (terms):** CliAgent, IdeCli, CursorCli, VscodeCli
- **Dependencies (one-way):** `sub_agent`, `workspace`

# utilities/plan

- **Purpose:** Front-end to git — Plan = Workflow + tickets; `/start-ticket /{flow} N`; `/finish-plan`; no planned-turn list.
- **Seam (terms):** Plan, PlanExecution, TurnAttachments, JudgeCheckpoint, HILCheck
- **Dependencies (one-way):** `workspace`, `git`, `workflow`

# utilities/swarm

- **Purpose:** Front-end to git and Plan — Supervisor + CliAgent Agents on a shared flow/ticket slice.
- **Seam (terms):** Swarm, Supervisor, Agent, Hypothesis, Outcome
- **Dependencies (one-way):** `plan`, `cli_agent`, `workspace`, `git`

# utilities/workflow

- **Purpose:** Front-end to git — one Project per Workflow; per-state behavior in `workflow/flows/*.yaml`; kit reads/writes Status (no Actions).
- **Seam (terms):** Workflow, FlowState, FlowFile
- **Dependencies (one-way):** `git`, `workspace`
