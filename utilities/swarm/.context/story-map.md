---
fidelity: [discovery]
artifact: [story-map]
format: md
section: body
---

# Story Map — Plan And Swarm Utilities

**Sources / context:**
`utilities/swarm/.context/issue-body.md`;
`utilities/swarm/.context/grill-answers.md` (ticks 14–33 lock; later ticks correct 14);
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
        (S) Practitioner --> Start Ticket On Flow
        (S) Practitioner --> Execute Turn
        (S) Practitioner --> Validate with Human
        (S) Judge --> Evaluate Results
        (S) Practitioner --> Review Progress
        (S) Practitioner --> Advance Ticket State
        (S) Practitioner --> Fix and Rerun
        (S) Practitioner --> Finish Plan
    (E) Manage Ticket Flow
        (S) Practitioner --> Record Research Tags
        (S) Practitioner --> Record Flow Notes
        (S) Practitioner --> Update Ticket Status
        (S) Agent --> Resolve Ticket Number
    (E) Compose Plan
        (S) Practitioner --> Create Plan
        (S) Practitioner --> Load Small-Work Plan
        (S) Practitioner --> Configure State Behavior
        (S) Practitioner --> Manage HIL Checks
        (S) Practitioner --> Manage Judge Checkpoints
        (S) Practitioner --> Save Workflow
        (S) Practitioner --> Compose Throwaway Workflow
    (E) Swarm Plan
        (S) Supervisor --> Create Supervisor
        (S) Supervisor --> Add Agent
        (S) Supervisor --> Compare Swarm Results
        (S) Supervisor --> Comparative Association

---

## Scope boundary

**In scope:** Git is the store (`Repo`, GitHub Projects, issues). Plan, Swarm, and Workflow are front-ends to git — not a parallel ticket machine. A **Workflow** is **states** on **its own GitHub Project** (one Project per Workflow). Project 1 is the **global inbox** (Backlog / Done). A **Plan** is that Workflow **plus** the ticket set (serial vs parallel is per Plan). **No planned turns** — FIFO is the default; the agent may batch related tickets. **Moving** a ticket off the inbox onto a flow board / into a state **creates a real Turn** (work + commit). Per-state behavior lives in `workflow/flows/{name}.yaml` (tools, one action, utilities, prose, optional hil/judge, owner + project_number); **columns stay on GitHub**. `/start-ticket /small-work 14` starts #14 on that board; unnamed start stays inbox In Progress. Harness must put Projects into prompts. Flow-done cards **stay on the flow board** until operator `/finish-plan` (move to inbox, close issues, close session). Throwaway yaml + temp Project **deleted** on `/finish-plan`; saved Project/yaml **stay**. **Kit + board only** — no GitHub Actions. Workspace is the working folder; Repo is the git backend. CliAgent describes hanging Turn shape and does not open the Turn; the CLI opens and finishes it. JudgeCheckpoint / HILCheck hang on the Turn when the entered state marks them. No Plan on CliAgent. Plan does not depend on Bdd or CleanEngineering (BDD owns CE companions).

**Out of scope:** Ahead-of-time ticket×state planned-turn lists. Invented kanban columns duplicated in the repo. A second ticket identity besides GitHub issue `#`. A parallel yaml ticket store beside `utilities/git`. GitHub Actions moving cards. Auto-return to inbox Done without `/finish-plan`. Plan owning BDD/CE companion rules.

---

## Thin slices

### Increment 1: Execute themed tickets on a configured flow Plan

**Outcome:** Operators take GitHub tickets under one theme off the inbox onto a configured flow Project, run each state’s work (root cause, `/bdd` with Clean Engineering under the hood, fix), FIFO-move through that board (each move creates a Turn; agent may batch related cards), leave cards on the flow board when the flow is done, then `/finish-plan` to inbox Done / close issues / close session.

**Slicing notes:** Plan is preconfigured — no Compose in this slice. Kit + board only. Unnamed `/start-ticket` still means inbox In Progress. `/bdd` runs with CE companions owned by BDD.

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

**Outcome:** A Practitioner creates a Plan as Workflow + tickets (saved reusable or throwaway), loads `/plan /small-work {context}`, configures per-state behavior in `workflow/flows/{name}.yaml` (tools, one action, utilities, prose, optional HIL/judge, owner + number), and saves or leaves throwaway for `/finish-plan` cleanup.

**Slicing notes:** No planned-turn list. Columns stay on the GitHub Project. small-work is prebaked; does not run against issues in generate. HIL/judge are per state in yaml.

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

**Slicing notes:** Enhance `Repo`, `Ticket`, `TicketState`, `note` / `read_notes`. Inbox columns remain Backlog / In Progress / Done; flow columns come from each Workflow’s Project.

**Decision prompt:** Ready to swarm after this slice?

**Stories:**
- Record Research Tags
- Record Flow Notes
- Update Ticket Status
- Resolve Ticket Number

### Increment 4: Swarm Plan

**Outcome:** A Supervisor is created with an Outcome and a shared flow/ticket slice selected once; Agents are added with a Hypothesis (register only); each Agent’s `CliAgent.launch_sessions` starts at `Plan.start` on its own WorkSession and runs that shared slice; Compare Swarm Results streams after each Turn JudgeCheckpoint or HIL result (Supervisor reads, does not judge); Comparative Association updates automatically under the Supervisor rubric toward Outcome.

**Slicing notes:** Create Supervisor before Add Agent. Shared slice before any Agent runs. Mid-run Add Agent registers then launches when that Agent starts the Plan. Comparative Association is automatic after each streamed compare (not a second wait).

**Decision prompt:** Ready to specify remaining scenarios after this slice?

**Stories:**
- Create Supervisor
- Add Agent
- Compare Swarm Results
- Comparative Association
