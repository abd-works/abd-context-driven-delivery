---
fidelity: [discovery]
artifact: [thin-slice]
format: md
---

# Thin slicing — Plan And Swarm Utilities

**Sources / context:** `utilities/swarm/.context/plan-and-swarm-sketch.md`; `utilities/swarm/.context/story-map.md`; `utilities/swarm/.context/grill-answers.md`; `utilities/workflow/.context/module-context.md`; `context_tools/bdd/bdd.md`

## Product / context

**Product:** Plan and Swarm utilities — execute planned work on GitHub tickets, then compose Plans and Swarm.

**Slicing intent:** Ship value first by **running an already configured Plan** as a **project Workflow** operators assign tickets to. Theme the backlog around defects and small changes, do root cause, run `/bdd` (Clean Engineering under the hood), fix one issue at a time, and move each ticket Backlog → In Progress → Done with existing Workflow `/backlog` / `/start-ticket` / `/finish-ticket`. Compose/configure the Plan and Swarm wait until that spine works.

## Increments

### Increment 1: Execute themed tickets on a configured Plan Workflow

**Outcome:** Operators assign GitHub tickets under one theme (defects and small changes) to a Plan that is already set and configured in the project repo. For each ticket they do root cause, run `/bdd` (which **must** run Clean Engineering under the hood via the Bdd → CleanEngineering companion), fix that one issue, and move the ticket Backlog → In Progress → Done using existing Workflow `backlog` / `start` / `finish`.

**Slicing notes:** Plan is preconfigured — no Compose in this slice. One theme, one ticket at a time. `/bdd` always includes CleanEngineering (`Bdd.ce()` / companion tool run) — not BDD alone. Ticket columns are only the existing Workflow/git states. Swarm and Plan composition wait.

**Decision prompt:** Ready to compose and configure Plans (Turns, HIL, Judge) after this slice?

**Stories:**
- Start Plan
- Execute Turn
- Validate with Human
- Evaluate Results
- Review Progress
- Advance Turn
- Fix and Rerun
- Record Flow Notes
- Update Ticket Status
- Resolve Ticket Number

### Increment 2: Compose and configure Plan

**Outcome:** A Practitioner creates a Plan and manages Turns, HIL Checks, and Judge Checkpoints (add, edit, delete) so later themes can reuse a configured Plan Workflow.

**Slicing notes:** Compose only. Execution spine already proven in Increment 1.

**Decision prompt:** Ready to deepen ticket research tags after this slice?

**Stories:**
- Create Plan
- Manage Turns
- Manage HIL Checks
- Manage Judge Checkpoints

### Increment 3: Manage ticket research on git

**Outcome:** Research tags and richer flow notes live on the current git Ticket / Project / notes API keyed by GitHub issue `#`, beyond the Workflow status moves already used in Increment 1.

**Slicing notes:** Enhance `Repo`, `Ticket`, `TicketState`, `note` / `read_notes`. Status examples remain Backlog / In Progress / Done.

**Decision prompt:** Ready to swarm after this slice?

**Stories:**
- Record Research Tags
- Record Flow Notes
- Update Ticket Status
- Resolve Ticket Number

### Increment 4: Swarm Plan

**Outcome:** A Supervisor is created with an Outcome and a shared `Swarm.turns` slice selected once; Agents are added with a Hypothesis (register only); each Agent’s `SubAgent.run` launches at `Plan.start` on its own WorkSession and runs that shared slice; Compare Swarm Results streams after each Judge or HIL evaluation; Comparative Association updates automatically under the Supervisor rubric toward Outcome.

**Slicing notes:** Create Supervisor before Add Agent. Shared turn slice before any Agent runs. Mid-run Add Agent registers then launches when that Agent starts the Plan. Comparative Association is automatic after each streamed compare (not a second wait).

**Decision prompt:** Ready to specify remaining scenarios after this slice?

**Stories:**
- Create Supervisor
- Add Agent
- Compare Swarm Results
- Comparative Association
