---
fidelity: [discovery]
artifact: [story-map]
format: md
section: body
---

# Story Map — Plan And Swarm Utilities

**Sources / context:**
`utilities/swarm/.context/issue-body.md`;
`utilities/swarm/.context/grill-answers.md`;
`utilities/swarm/.context/plan-and-swarm-sketch.md`;
`utilities/swarm/.context/thin-slicing.md`;
`utilities/plan/.context/module-context.md`;
`utilities/git/.context/module-context.md`;
`utilities/git/.context/git-modules.md`;
`utilities/workflow/.context/module-context.md`;
`utilities/sub_agent/.context/module-context.md`;
`utilities/workspace/.context/module-context.md`;
`utilities/cli_agent/.context/module-context.md`;
`context_tools/agent_bdd/.context/module-context.md`;
`context_tools/bdd/bdd.md`;
`context_tools/stories/stories.md`;
`context_tools/stories/templates/md/story-map.md`

---

(E) Run Planned Work
    (E) Execute Plan
        (S) Practitioner --> Start Plan
        (S) Practitioner --> Execute Turn
        (S) Practitioner --> Validate with Human
        (S) Judge --> Evaluate Results
        (S) Practitioner --> Review Progress
        (S) Practitioner --> Advance Turn
        (S) Practitioner --> Fix and Rerun
    (E) Manage Ticket Flow
        (S) Practitioner --> Record Research Tags
        (S) Practitioner --> Record Flow Notes
        (S) Practitioner --> Update Ticket Status
        (S) Agent --> Resolve Ticket Number
    (E) Compose Plan
        (S) Practitioner --> Create Plan
        (S) Practitioner --> Manage Turns
        (S) Practitioner --> Manage HIL Checks
        (S) Practitioner --> Manage Judge Checkpoints
    (E) Swarm Plan
        (S) Supervisor --> Create Supervisor
        (S) Supervisor --> Add Agent
        (S) Supervisor --> Compare Swarm Results
        (S) Supervisor --> Comparative Association

---

## Scope boundary

**In scope:** Git is the store (`Repo`, GitHub Projects, issues, Backlog / In Progress / Done). Plan, Swarm, and Workflow are front-ends to git — not a parallel ticket machine. Workspace is the working folder (its root is that folder); Repo is the git backend — never treat git root as workspace. Plan holds ordered `workspace.Turn`s; `Turn.state` is TicketState mapped to Project/Workflow columns. CliAgent is the worker for Plan and Swarm Agents (`CliAgent.launch_sessions` at Plan.start). JudgeCheckpoint hangs on the Turn; when a Turn needs a judge, use CliAgent doer-judge (own console, never print mode, 3-fail). Supervisor.compare reads that result and does not judge — no judge-as-agent policy on Swarm Agent. CliAgent describes hanging Turn shape and does not open the Turn; the CLI opens and finishes it. No Plan on CliAgent. No PlannedTurn. Plan does not depend on Bdd or CleanEngineering (BDD owns its companion tools). Compose/configure Plan and Swarm follow the thin-slice order.

**Out of scope:** New slash-command product UX beyond existing kits. Invented kanban columns or status badges. A second ticket identity besides GitHub issue `#`. A parallel yaml/store beside `utilities/git`. Plan owning BDD/CE companion rules.

---

## Thin slices

### Increment 1: Execute themed tickets on a configured Plan Workflow

**Outcome:** Operators assign GitHub tickets under one theme (defects and small changes) to a Plan that is already set and configured in the project repo. For each ticket they do root cause, run `/bdd` (Clean Engineering under the hood), fix that one issue, and move the ticket Backlog → In Progress → Done using existing Workflow `backlog` / `start` / `finish`.

**Slicing notes:** Plan is preconfigured — no Compose in this slice. One theme, one ticket at a time. `/bdd` always includes CleanEngineering companion — not BDD alone. Ticket columns are only the existing Workflow/git states.

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

**Outcome:** A Supervisor is created with an Outcome and a shared `Swarm.turns` slice selected once; Agents are added with a Hypothesis (register only); each Agent’s `CliAgent.launch_sessions` starts at `Plan.start` on its own WorkSession and runs that shared slice; Compare Swarm Results streams after each Turn JudgeCheckpoint or HIL result (Supervisor reads, does not judge); Comparative Association updates automatically under the Supervisor rubric toward Outcome.

**Slicing notes:** Create Supervisor before Add Agent. Shared turn slice before any Agent runs. Mid-run Add Agent registers then launches when that Agent starts the Plan. Comparative Association is automatic after each streamed compare (not a second wait).

**Decision prompt:** Ready to specify remaining scenarios after this slice?

**Stories:**
- Create Supervisor
- Add Agent
- Compare Swarm Results
- Comparative Association
