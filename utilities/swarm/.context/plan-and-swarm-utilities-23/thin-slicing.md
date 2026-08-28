# Thin slicing — Plan And Swarm Utilities

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
