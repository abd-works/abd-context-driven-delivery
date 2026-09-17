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

## Tick 10 — Turn slice binding (Add Agent / swarm run)

**Question:** When are the Plan Turns bound for an Agent's Execute Plan run?

**Options offered:** One shared turn slice for the whole Swarm, selected once before any Agent runs (Recommended) | Each Agent gets its own turn slice at Add Agent time | Slice is implied by Hypothesis — Agent runs the Plan Turn(s) matching its Hypothesis action/fidelity/context | Other / I'll specify

**Answer (user):** **One shared turn slice for the whole Swarm, selected once before any Agent runs.** Same noun as tick 2 (selected Turns). Each Agent runs that same slice on its own WorkSession.

**Slice unlocked:** deepen Add Agent / Swarm turn-slice BDDs — shared selected Turns on Swarm; every Agent runs that slice in its own WorkSession.

## Tick 11 — Comparative Association timing (Compare Swarm Results / Comparative Association)

**Question:** When does Comparative Association run relative to Compare Swarm Results streaming?

**Options offered:** Automatic after each streamed compare event (Judge or HIL) — associate updates under the Supervisor rubric toward Outcome (Recommended) | Explicit operator step — compare streams per tick 6; associate is a separate Supervisor invoke when ready | Automatic only when the Supervisor rubric is set — compare alone until then, then associate on each stream | Other / I'll specify

**Answer (user):** **Automatic after each streamed compare event (Judge or HIL).** Associate updates under the Supervisor rubric toward Outcome. Matches tick 6 stream; not a second wait.

**Slice unlocked:** deepen Compare / Comparative Association BDDs — associate follows each streamed Judge or HIL compare; no separate operator wait.

## Tick 12 — SubAgent launch timing (Add Agent)

**Question:** When does SubAgent.run launch the Agent?

**Options offered:** At Add Agent — SubAgent.run launches immediately when the Supervisor adds the Agent | When the Agent starts the Plan — Add Agent registers the Agent; SubAgent.run launches at Plan.start on the Agent WorkSession (Recommended) | When the Swarm run begins — one launch wave after the shared turn slice is selected | Other / I'll specify

**Answer (user):** **When the Agent starts the Plan.** Add Agent registers the Agent. `SubAgent.run` launches at `Plan.start` on the Agent WorkSession. Fits tick 5 (WorkSession opens at start) and tick 10 (shared slice; each Agent runs it on start). Mid-run add registers at add and launches when that Agent starts the Plan.

**Slice unlocked:** deepen Add Agent BDDs — register at add; `SubAgent.run` at `Plan.start` on the Agent WorkSession.

## Tick 13 — Turn tools vs action (Compose Plan / CliAgent)

**Question:** How do tools and action sit on a Turn that CliAgent describes?

**Answer (user):** **A Turn has multiple tools and one action.** `CliAgent` describes that shape (`action`, `tool_keys`, `toolCalls`). The CLI opens the hanging `workspace.Turn` and finishes it after the action. `CliAgent` does not open the Turn. No PlannedTurn. No Plan on CliAgent. Keep TicketState, HILCheck, JudgeCheckpoint.

**Slice unlocked:** deepen Manage Turns / CE — `Turn.tool_keys` + one `action`; `CliAgent` describes shape; CLI open/finish.

## Tick 14 — Workflow vs Plan (operator restatement 2026-08-29)

**Question:** What is a Plan vs a Workflow, and what finishes a Plan?

**Answer (user):** Two requirements.

**1. Plan = workflow + work items.** A Plan has planned turns. Each turn has a **name** (that name **is** the state). Each turn is a sequential set of activities and may invoke one or more tools, one action, one or more utilities, or a plain prompt. A Workflow alone is not a Plan: you must say **what goes through** it — one ticket or many. The Plan is **done** when **every** ticket has gone through **every** named state successfully.

**2. Saved reusable Workflow.** A created Workflow can be saved and reused. A Plan can be as small as: pick that Workflow + tell the agent which tickets + run the same states. Tickets may run **one at a time** or **batched in parallel**; that choice is ours per Plan, not fixed in the Workflow.

**3. Throwaway Workflow (operator correction).** You can also **compose a Workflow on the fly**, run it as a Plan (same: turns + tickets), and **not save it**. Save/reuse is optional, not required.

**Not answered here:** where a saved Workflow file lives; whether each turn name is also a GitHub Project Status column.

**Slice unlocked:** treat Workflow as the reusable named-turn sequence; Plan as that sequence plus the ticket set plus serial-vs-parallel. Do not equate Plan with “open the 3-column board” alone.

## Tick 15 — Turn vs workflow state (operator correction)

**Question:** When a ticket “goes through a state,” is the turn name the state?

**Answer (user):** No. Those are different things.

- A **workflow state** is only a state. Moving a ticket into a state is when you **start** (that ticket + that state).
- A **turn** is one increment of **actual work**: one **issue/ticket** going through **one** workflow state. You do the work and **commit**. That is the turn.
- **7 tickets × 5 states = 35 turns** if you materialize them.
- **Planned turns** are only an optional ahead-of-time list of which tickets run in what order. Dump that list if it is unnecessary and use **FIFO** instead.

**Corrects Tick 14 wording:** a planned turn is not “the state.” The Workflow is the states. The Plan still says which tickets go through that Workflow. Turns happen when a ticket is in a state and work is committed.

## Tick 16 — kill planned turns; FIFO move creates a real Turn

**Answer (user):** Drop **planned turns**. Overkill.

- A **Workflow** is states. Issues go through those states **FIFO**.
- **Moving a ticket into a state** creates a **real Turn** and runs the regular turn machinery (do the work, commit).
- No ahead-of-time ticket×state list.

## Tick 17 — where the ticket moves

**Answer (user):** **Pretty sure A** — GitHub Project **Status** columns are the workflow states. The kit can read and write them. Open question: benefit of that vs **Actions** moving tickets.

**Reopens** Ticket 23 / story-map: invented Kanban columns were out of scope. Operator is choosing columns as the states anyway.

## Tick 18 — Actions

**Answer (user):** **Kit + board only.** No GitHub Actions. The kit reads/writes Project Status; that move creates the Turn. Actions later only if they want a GitHub button/event that moves a card without the kit.

## Tick 19 — distinct boards per flow

**Answer (user):** A single shared Kanban is useless. They need **distinct Kanban boards for distinct flows** they can actually see. The “one Status field / union of columns” option does not do that.

**Follow-up (user):** More than one Project on a repo is fine. “One Project per repo” was only because they did not see a need yet. That lock is lifted.

**Locked:** one GitHub **Project per Workflow**. That Project’s Status columns are that flow’s states. Project 1 can remain the inbox. The kit reads/writes that flow Project; moving a card creates the Turn.

## Tick 20 — inbox vs flow Project

**Answer (user, confirmed):** Project 1 is the **global inbox** (Backlog, and Done). A Workflow **takes tickets off** that Project onto the **flow Project**, FIFO-moves them through that board’s states (each move creates a Turn), then **moves them back** to the global Project as Done. GitHub allows an issue on two Projects; “move” here means remove from one and add to the other, not leave it on both.

## Operator lock — proceed means grill

**Answer (user):** “Proceed” continues **grilling only**. Do **not** generate or build until they say so.

## Tick 21 — throwaway Workflow board

**Answer (user):** **Temporary GitHub Project** for that run. Same move: off inbox → through that board → back to Done. **Delete the Project** when the Plan is done. No leftover board to reuse.

## Tick 22 — what is saved in the repo

**Answer (user):** Do not repeat the Kanban in the repo. Save **per-state behavior** in `workflow/flows/*.yaml`:

- which **tools** to run, if any
- which **action** to run (only one), if any
- which **utilities** to run
- **prose** to bring in, if any

The GitHub Project remains the board (columns, cards). The yaml is the behavior for each state, not a copy of the board.

## Tick 23 — pointer lives in the same flow file

**Answer (user):** Same `workflow/flows/{name}.yaml`: name, optional owner + project_number (written when the Project is created on save), then per-state behavior. Columns still come from GitHub.

## Tick 24 — /start-ticket and the board

**Answer (user):** `/start-ticket /small-work 14` starts ticket **#14** on the **small-work** board (off inbox, onto that flow, first state, create the Turn). If you **do not name a board**, it stays today’s behavior: **In Progress** on the inbox. The **harness must put Projects into prompts** with those instructions (which boards exist, how to start on one).

## Tick 25 — FIFO plus agent batching

**Answer (user):** FIFO / one-active is **fine as the default**. The agent that runs the flow must **keep context across calls** and the **overall set of tickets**. If four tickets touch the same change, do the fix **once** and move those tickets together — do not walk each card blindly. **AI decides when a bunch is done.**

## Tick 26 — who marks inbox Done

**Answer (user):** Depends on HIL in the flow.

- **No HIL** in the flow: the **agent** moves the ticket to Done when the work is done. The operator does not. Nobody else does.
- **HIL** in the flow: the **human** must say they are finished with that loop before it proceeds / is Done.

## Tick 27 — HIL is per state in the flow yaml

**Answer (user):** `workflow/flows/*.yaml` marks the state (`hil: true` or a HIL prompt). Entering that state creates the Turn with a HILCheck. The agent cannot pass that state (or return to inbox Done) until the human says the loop is finished.

## Tick 28 — judge is per state in the flow yaml

**Answer (user):** Yes. A state may include a **judge rubric**. Entering the state creates the Turn with that JudgeCheckpoint. CliAgent doer-judge runs it (existing 3-fail). No rubric = no judge on that state.

## Tick 29 — throwaway writes then deletes

**Answer (user):** Write `workflow/flows/{name}.yaml` for the run. When the Plan is done, **delete that file and the temp Project**. Nothing reused.

## Tick 30 — /finish-plan, not auto-return

**Answer (user):** When the **workflow/flow is done**, tickets **stay on the flow Project** for now. There is always a **final check** (a quick scan of what was done), even if no state had HIL. The operator then runs **`/finish-plan`**: move those tickets onto the inbox board, **close all those issues**, and do the usual close-session work. The agent does **not** put them back on project 1 by itself.

## Tick 31 — final check is you + /finish-plan

**Answer (user):** You look at the flow board and the work. When satisfied, you run **`/finish-plan`**. The agent is not blocked on a HILCheck for that scan unless you added one on a state. **`/finish-plan` is the gate.**

## Tick 32 — throwaway deleted on /finish-plan

**Answer (user):** **`/finish-plan`** deletes the temp Project and the throwaway `workflow/flows/{name}.yaml`, after tickets are on the inbox and issues are closed. The board exists for the scan.

## Tick 33 — saved flow survives /finish-plan

**Answer (user):** Keep the saved Project and yaml (already implied by reuse). Only the tickets move. Do not re-ask requirement recaps.
