# Grill answers — plan-and-swarm-utilities-23

Append-only.

## Tick 1 — JudgeCheckpoint vs Step (Compose Plan Sequence)

**Question:** How does JudgeCheckpoint sit on the Plan sequence?

**Options offered:** Step subtype | pause between Steps | flag on Step | Other

**Answer (user):** **Other — planned turns, not a distinct step/turn kind.**

Model what exists so far:

- A **Plan** is associated with a **Workspace**.
- A Plan has **planned turns** it wants to execute.
- Each planned turn invokes a number of context tools, actions, fidelities, context (shape still to model; take inspiration from what every actual turn already captures).
- Starting the plan **initiates a WorkSession** that has (actual) turns.
- Each **planned turn** may optionally have a **judge checkpoint** and/or a **human (HIP) checkpoint**.
- Checkpoints are **not distinct turns**.
- Model **both planned and actual turns**.
- After the turn closes (checkpoints included), go on to the next turn.

**Slice unlocked:** deepen Compose Plan Sequence in the sketch in place. HipCheckpoint follows the same attachment (optional on a planned turn, not its own turn).

## Tick 2 — Swarm slice (Start Agent Swarm)

**Question:** When a swarm runs a slice, what is selected?

**Options offered:** Selected PlannedTurns | Selected invocations inside one PlannedTurn | Full Plan only for v1 | Other

**Answer (user):** **Selected PlannedTurns** — same noun as Plan; issue “selected steps” maps to a planned-turn slice.

**Slice unlocked:** deepen Start Agent Swarm slice in the sketch. Hypothesis ownership is the following grill.

## Tick 3 — Hypothesis ownership (Start Agent Swarm)

**Question:** Who owns Hypothesis?

**Options offered:** Agent owns | Supervisor map | Launch-time copy only | Other

**Answer (user):** **Other — split hypothesis.**

- **Supervisor** owns the **overarching outcome**.
- Each **Agent** owns the **“if we do this we will achieve the outcome”** part of the hypothesis (the unique first-order approach).

Not a single field wholly on Agent, Supervisor map, or launch-time copy only.

**Slice unlocked:** deepen Assign Agent Hypothesis / Hypothesis ownership in the sketch. Next grill was Compare Swarm Results (rubric source) unless the sketcher sees a tighter open branch.

## Tick 4 — Compare rubric source (Compare Swarm Results)

**Question:** What scores the swarm compare?

**Options offered:** Either different targets | Outcome only | Plan judges only | Outcome and each Hypothesis | Other

**Answer (user):** **Either, different targets** — Supervisor rubric against Outcome; and/or Plan JudgeCheckpoint rubrics on PlannedTurns. Matches the issue “or.”

**Slice unlocked:** deepen Compare Swarm Results rubric lines in the sketch.
