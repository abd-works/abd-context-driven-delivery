---
fidelity: [discovery]
artifact: [story-map]
format: md
section: body
---

# Story Map — Plan And Swarm Utilities

**Sources / context:**
`utilities/swarm/.context/plan-and-swarm-utilities-23/issue-body.md`;
`utilities/swarm/.context/plan-and-swarm-utilities-23/session.md`;
`utilities/swarm/.context/plan-and-swarm-utilities-23/grill-answers.md`;
`utilities/swarm/.context/plan-and-swarm-utilities-23/plan-and-swarm-sketch.md`;
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

**In scope:** A Plan associated with a Workspace, holding ordered Turns (existing `workspace.Turn`). Manage Turns / HIL Checks / Judge Checkpoints is add, edit, and delete. Execute Plan runs a Turn, presents results to a human (HILCheck), has a Judge evaluate, reviews progress, advances TicketState to the next Turn, and Fix and Rerun uses existing Turn `record_mistake` / `record_correction` plus WorkSession `Repair`. Swarm comes after: Create Supervisor (Outcome) then Add Agent (Hypothesis). Compare Swarm Results is the same judgment as Execute Plan. Comparative Association is that judgment plus the Supervisor rubric associating Agent results. Git `Repo` / `Ticket` / `Project` / `TicketState` manage research tags, notes, and flow. Related seams: `@sub_agent`, `ai_judge`, workflow ticket + project status.

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

**Outcome:** A Supervisor is created with an Outcome; Agents are added with a Hypothesis; Compare Swarm Results reuses Execute Plan judgment; Comparative Association applies the Supervisor rubric across Agent results.

**Slicing notes:** Create Supervisor before Add Agent. Comparative Association is the extra swarm mechanic on top of singular judgment.

**Decision prompt:** Ready to specify remaining scenarios after this slice?

**Stories:**
- Create Supervisor
- Add Agent
- Compare Swarm Results
- Comparative Association
