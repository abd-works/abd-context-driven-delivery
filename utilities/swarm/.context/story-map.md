---
fidelity: [discovery]
artifact: [story-map]
format: md
section: body
---

# Story Map — Plan And Swarm Utilities

**Sources / context:**
`utilities/swarm/.context/issue-body.md`;
`utilities/swarm/.context/session.md`;
`utilities/swarm/.context/grill-answers.md`;
`utilities/swarm/.context/plan-and-swarm-sketch.md`;
`utilities/plan/.context/module-context.md`;
`utilities/git/.context/module-context.md`;
`utilities/git/.context/git-modules.md`;
`utilities/workflow/.context/module-context.md`;
`utilities/sub_agent/.context/module-context.md`;
`utilities/workspace/.context/module-context.md`;
`context_tools/agent_bdd/.context/module-context.md`;
`context_tools/stories/stories.md`;
`context_tools/stories/templates/md/story-map.md`

---

(E) Run Planned Work
    (E) Compose Plan
        (S) Practitioner --> Create Plan
        (S) Practitioner --> Manage Turns
        (S) Practitioner --> Manage HIL Checks
        (S) Practitioner --> Manage Judge Checkpoints
    (E) Manage Ticket Flow
        (S) Practitioner --> Record Research Tags
        (S) Practitioner --> Record Flow Notes
        (S) Practitioner --> Update Ticket Status
        (S) Agent --> Resolve Ticket Number
    (E) Execute Plan
        (S) Practitioner --> Start Plan
        (S) Practitioner --> Execute Turn
        (S) Practitioner --> Validate with Human
        (S) Judge --> Evaluate Results
        (S) Practitioner --> Review Progress
        (S) Practitioner --> Advance Turn
        (S) Practitioner --> Fix and Rerun
    (E) Swarm Plan
        (S) Supervisor --> Create Supervisor
        (S) Supervisor --> Add Agent
        (S) Supervisor --> Compare Swarm Results
        (S) Supervisor --> Comparative Association

---

## Scope boundary

**In scope:** A Plan associated with a Workspace, holding ordered Turns (existing `workspace.Turn`). A Turn has one action and may hold multiple tools (`tool_keys`, `toolCalls`). CliAgent describes that hanging Turn shape (`action`, `tool_keys`, `toolCalls`) and does not open the Turn; the CLI opens the hanging Turn and finishes it after the action. No Plan on CliAgent. No PlannedTurn class. Manage Turns / HIL Checks / Judge Checkpoints is add, edit, and delete. Execute Plan runs a Turn, presents results to a human (HILCheck), has a Judge evaluate, reviews progress, advances TicketState to the next Turn, and Fix and Rerun uses existing Turn `record_mistake` / `record_correction` plus WorkSession `Repair`. Swarm comes after: Create Supervisor (Outcome) then Add Agent (Hypothesis). One shared turn slice (`Swarm.turns`) is selected once before any Agent runs; each Agent runs that same slice on its own WorkSession. Add Agent registers the Agent; `SubAgent.run` launches at `Plan.start` on that WorkSession. Compare Swarm Results is the same judgment as Execute Plan and streams after each Judge or HIL evaluation. Comparative Association runs automatically after each streamed compare under the Supervisor rubric toward Outcome. Git `Repo` / `Ticket` / `Project` / `TicketState` manage research tags, notes, and flow. Related seams: `@sub_agent`, `ai_judge`, workflow ticket + project status.

**Out of scope:** New slash-command product UX beyond existing kits (`/backlog`, `/start-ticket`, `/finish-ticket`, `/sub-agent`). Invented kanban columns or status badges. A second ticket identity besides GitHub issue `#`. A parallel yaml/store beside `utilities/git`. Production Python in this pass.

---

## Thin slices

### Increment 1: Compose Plan

**Outcome:** A Practitioner creates a Plan and manages Turns, HIL Checks, and Judge Checkpoints (add, edit, delete).

**Slicing notes:** Compose only. Execute is the next slice.

**Decision prompt:** Ready to manage ticket flow on the existing git API after this slice?

**Stories:**
- Create Plan
- Manage Turns
- Manage HIL Checks
- Manage Judge Checkpoints

### Increment 2: Manage ticket flow on git

**Outcome:** Research tags, flow notes, and project TicketState (Backlog / In Progress / Done) live on the current git Ticket / Project / notes API keyed by GitHub issue `#`.

**Slicing notes:** Enhance `Repo`, `Ticket`, `TicketState`, `note` / `read_notes`. Status examples are the existing columns only.

**Decision prompt:** Ready to execute a plan after this slice?

**Stories:**
- Record Research Tags
- Record Flow Notes
- Update Ticket Status
- Resolve Ticket Number

### Increment 3: Execute Plan

**Outcome:** Start Plan opens a WorkSession and moves the first Backlog Turn to In Progress. Execute Turn runs that Turn. Results go to a human (HILCheck) and a Judge; progress is reviewed; TicketState advances; Fix and Rerun records Mistake and Correction on the Turn and associates the existing Repair.

**Slicing notes:** Existing Turn and WorkSession.repairs. Swarm waits until this slice is sketched.

**Decision prompt:** Ready to swarm after this slice?

**Stories:**
- Start Plan
- Execute Turn
- Validate with Human
- Evaluate Results
- Review Progress
- Advance Turn
- Fix and Rerun

### Increment 4: Swarm Plan

**Outcome:** A Supervisor is created with an Outcome and a shared `Swarm.turns` slice selected once; Agents are added with a Hypothesis (register only); each Agent’s `SubAgent.run` launches at `Plan.start` on its own WorkSession and runs that shared slice; Compare Swarm Results streams after each Judge or HIL evaluation; Comparative Association updates automatically under the Supervisor rubric toward Outcome.

**Slicing notes:** Create Supervisor before Add Agent. Shared turn slice before any Agent runs. Mid-run Add Agent registers then launches when that Agent starts the Plan. Comparative Association is automatic after each streamed compare (not a second wait).

**Decision prompt:** Ready to specify remaining scenarios after this slice?

**Stories:**
- Create Supervisor
- Add Agent
- Compare Swarm Results
- Comparative Association
