---
fidelity: [discovery]
artifact: [thin-slice]
format: md
---

# Thin slicing — Plan And Swarm Utilities

**Sources / context:** `utilities/swarm/.context/plan-and-swarm-sketch.md`; `utilities/swarm/.context/story-map.md`; `utilities/swarm/.context/grill-answers.md` (ticks 14–33); `utilities/workflow/.context/module-context.md`; `context_tools/bdd/bdd.md`

## Product / context

**Product:** Plan and Swarm utilities — run tickets through a Workflow’s GitHub Project, then compose Plans/Workflows and Swarm.

**Slicing intent:** Ship value first by **running an already configured Plan** (Workflow Project + ticket set). Theme the inbox around defects and small changes, take tickets onto the flow board (`/start-ticket /{flow} N`), do root cause, run `/bdd` (Clean Engineering under the hood), fix, FIFO-move through states (each move creates a Turn; agent may batch), leave cards on the flow board, then `/finish-plan`. Compose/configure Workflow yaml and Swarm wait until that spine works.

## Increments

### Increment 1: Execute themed tickets on a configured flow Plan

**Outcome:** Operators take themed GitHub tickets off the inbox onto a configured flow Project, run per-state work (root cause, `/bdd` with CE under the hood, fix), FIFO-move through that board (kit + board only; each move creates a Turn; agent may batch related cards), leave cards on the flow board when the flow is done, then `/finish-plan` (inbox Done, close issues, close session).

**Slicing notes:** Plan is preconfigured — no Compose in this slice. One theme. `/bdd` always includes CleanEngineering (`Bdd.ce()` / companion tool run). Unnamed `/start-ticket` stays inbox In Progress. Harness puts Projects into prompts. No GitHub Actions. Swarm and Plan composition wait.

**Decision prompt:** Ready to compose and save Workflows (states, yaml behavior, HIL, Judge) after this slice?

**Stories:**
- Start Ticket On Flow
- Execute Turn
- Validate with Human
- Evaluate Results
- Review Progress
- Advance Ticket State
- Fix and Rerun
- Finish Plan
- Record Flow Notes
- Update Ticket Status
- Resolve Ticket Number

### Increment 2: Compose and configure Plan / Workflow

**Outcome:** A Practitioner creates a Plan as Workflow + tickets (saved or throwaway), loads `/plan /small-work {context}`, configures per-state behavior in `workflow/flows/{name}.yaml`, and manages HIL/judge markers per state.

**Slicing notes:** No planned-turn list. Columns stay on GitHub. small-work is prebaked; does not run against issues in generate. Throwaway yaml + temp Project deleted on `/finish-plan`; saved Project/yaml survive.

**Decision prompt:** Ready to deepen ticket research tags after this slice?

**Stories:**
- Create Plan
- Load Small-Work Plan
- Configure State Behavior
- Manage HIL Checks
- Manage Judge Checkpoints
- Save Workflow
- Compose Throwaway Workflow

### Increment 3: Manage ticket research on git

**Outcome:** Research tags and richer flow notes live on the current git Ticket / Project / notes API keyed by GitHub issue `#`, beyond the kit Status moves already used in Increment 1.

**Slicing notes:** Enhance `Repo`, `Ticket`, `TicketState`, `note` / `read_notes`. Inbox remains Backlog / In Progress / Done; flow columns come from each Workflow’s Project.

**Decision prompt:** Ready to swarm after this slice?

**Stories:**
- Record Research Tags
- Record Flow Notes
- Update Ticket Status
- Resolve Ticket Number

### Increment 4: Swarm Plan

**Outcome:** A Supervisor is created with an Outcome and a shared flow/ticket slice selected once; Agents are added with a Hypothesis (register only); each Agent’s `CliAgent.launch_sessions` starts at `Plan.start` on its own WorkSession and runs that shared slice; Compare Swarm Results streams after each Turn JudgeCheckpoint or HIL result; Comparative Association updates automatically under the Supervisor rubric toward Outcome.

**Slicing notes:** Create Supervisor before Add Agent. Shared slice before any Agent runs. Mid-run Add Agent registers then launches when that Agent starts the Plan. Comparative Association is automatic after each streamed compare (not a second wait).

**Decision prompt:** Ready to specify remaining scenarios after this slice?

**Stories:**
- Create Supervisor
- Add Agent
- Compare Swarm Results
- Comparative Association
