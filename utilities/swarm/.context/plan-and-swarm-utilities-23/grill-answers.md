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

## Tick 5 — Swarm WorkSession (Start Agent Swarm)

**Question:** When a Swarm runs PlannedTurns, whose WorkSession holds each Agent’s actual Turns?

**Options offered:** Each Agent opens its own WorkSession | All Agents share the Plan’s WorkSession | Run does not open a WorkSession | Other

**Answer (user):** **Each Agent opens its own WorkSession** — parallel runs stay isolated; compare reads N session trails.

**Slice unlocked:** deepen Run Planned Turns / Create Agent Swarm BDDs — Agent WorkSession is not the Plan’s Start Plan session.

## Tick 6 — Collect timing (Compare Swarm Results)

**Question:** When Collect Swarm Results runs, what is collected?

**Options offered:** Wait until every Agent WorkSession has finished | Collect only finished Agents | Collect a Result object | Other

**Answer (user):** **Other — stream after each in-loop evaluation.**

- Report progress of **every Agent** after every **HIP** or **judge** evaluation.
- As soon as that evaluation finishes, put it on the running report (dashboard / whatever the compare surface is).
- Do **not** wait for an Agent to be done.
- Do **not** wait for all Agents.
- From those learnings, the Supervisor **may add a new sub-agent** with a **new Hypothesis** while the Swarm is still running.

**Slice unlocked:** Incremental collect/compare after each JudgeCheckpoint or HILCheck. Mid-run Create + Assign stays on existing stories.

## Tick 7 — HILCheck name (Compose Plan Sequence)

**Question:** What is the human gate on a PlannedTurn called?

**Answer (user):** **HILCheck** — human-in-the-loop check on a Turn. Same attachment as tick 1.

## Tick 8 — PlannedTurn envelope (Compose Plan Sequence)

**Question:** What does a PlannedTurn hold when it is recorded?

**Options offered:** Same slots as Turn | One kit run | Other

**Answer (user):** **Other — extend existing Turn with TicketState.**

- A **Plan** holds existing **workspace.Turn** objects.
- **Turn** already has action, fidelity, context, and toolCalls.
- **Turn.state** is **TicketState**: Backlog, In Progress, Done — the same work states as **Ticket**.
- Recorded onto a Plan, a Turn starts in **Backlog**. **Start Plan** opens a **WorkSession** and that Turn becomes **In Progress**. **Turn.finish** sets **Done** and the next Backlog Turn becomes In Progress.

## Tick 9 — Execute Turn and WorkSession (Execute Plan)

**Question:** When the first Execute Turn runs on a Plan, what opens the WorkSession?

**Options offered:** Execute Turn opens it | Plan still has its own start | Other

**Answer (user):** **Plan still has its own start.** Start Plan opens the WorkSession. Execute Turn runs a Turn that is already In Progress.
