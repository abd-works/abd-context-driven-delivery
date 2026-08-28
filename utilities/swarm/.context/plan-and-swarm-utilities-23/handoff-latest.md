# Handoff — plan-and-swarm-utilities-23 (2026-08-28)

## Resume

- **Stage:** exploration / sketch. Increments 1–3 BDDs deepened. Increment 4 Swarm Plan is next.
- **Worktree:** `C:\dev\abd-cdd-plan-and-swarm-utilities-23` on `session/plan-and-swarm-utilities-23`. Do not checkout or edit the primary clone `C:\dev\abd-context-driven-delivery` (stale sketch there).
- **Session folder:** `utilities/swarm/.context/plan-and-swarm-utilities-23/`
- **Source of truth:** `plan-and-swarm-sketch.md` (stories + CE). Generated Increment 1 scenario files under `scenarios/` are leftovers — do not treat as SoT. Do not generate more scenario files until the operator says generate.
- **Last work:** Increment 4 deepened through tick 12 — shared Swarm.turns slice, automatic associate, SubAgent.run at Plan.start (`pass #inc4-subagent-launch`).
- **Next action:** Increment 4 sketch stable — scenario generation when the operator says generate.
- **Next focus:** Increment 4 validation / scenario pass (when requested)

## Locked grill answers (`grill-answers.md`)

| Tick | Lock |
|---|---|
| 1 | Plan hangs on a Workspace. Sequence is Turns (was “planned turns”). Judge/HIL optional on a Turn. Start opens WorkSession. After finish, next Turn. |
| 2 | Swarm slice = selected Turns. |
| 3 | Supervisor owns Outcome. Each Agent owns Hypothesis. |
| 4 | Compare: Supervisor rubric → Outcome and/or JudgeCheckpoint rubrics on Turns. |
| 5 | Each Agent opens its own WorkSession on run. |
| 6 | Stream collect after each Judge or HIL evaluation. Supervisor may add an Agent + Hypothesis while running. |
| 7 | Human gate is **HILCheck** (not HipCheckpoint). |
| 8 | No PlannedTurn class. Plan holds existing `workspace.Turn`. `Turn.state` is **TicketState**: Backlog / In Progress / Done. |
| 9 | **Start Plan** opens the WorkSession and moves the first Backlog Turn to In Progress. **Execute Turn** runs an already In Progress Turn (`performTurn`). |
| 10 | One shared turn slice for the whole Swarm, selected once before any Agent runs. Each Agent runs that same slice on its own WorkSession. |
| 11 | Comparative Association runs automatically after each streamed compare event (Judge or HIL). Associate updates under Supervisor rubric toward Outcome. |
| 12 | Add Agent registers the Agent. `SubAgent.run` launches at `Plan.start` on the Agent WorkSession. Mid-run add launches when that Agent starts the Plan. |

## Story map (current)

(E) Run Planned Work
    (E) Compose Plan — Create Plan, Manage Turns, Manage HIL Checks, Manage Judge Checkpoints
    (E) Manage Ticket Flow — Record Research Tags, Record Flow Notes, Update Ticket Status, Resolve Ticket Number
    (E) Execute Plan — Start Plan, Execute Turn, Validate with Human, Evaluate Results, Review Progress, Advance Turn, Fix and Rerun
    (E) Swarm Plan — Create Supervisor, Add Agent, Compare Swarm Results, Comparative Association

HIL and Judge stay **two** Manage stories. “Manage” is add / edit / delete on each.

## Language (existing nouns)

- **Turn** — `action`, `fidelity`, `context`, `toolCalls`, `performTurn`, `finish`, `recordMistake`, `recordCorrection`. State is TicketState.
- **JudgeCheckpoint.rubric** — same argument as `ai_judge`. Holds `JudgeResult`.
- **HILCheck** — human-in-the-loop check on a Turn.
- **Fix and Rerun** — existing Turn mistake/correction + WorkSession.repairs. TicketState stays In Progress.
- **Agent** — SubAgent that runs **Execute Plan** on its own WorkSession. No second run epic.
- **Comparative Association** — Supervisor rubric associating Agent results toward Outcome. Compare Swarm Results is the same judgment as Execute Plan.

Do not use issue-16 experiment nicknames (thin-templates, channel-write). Do not invent Invocation. Do not write “is not X / never X” asides. Do not collapse HIL and Judge into one story.

## Artifacts to read

- `utilities/swarm/.context/plan-and-swarm-utilities-23/plan-and-swarm-sketch.md`
- `utilities/swarm/.context/plan-and-swarm-utilities-23/grill-answers.md`
- `utilities/swarm/.context/plan-and-swarm-utilities-23/story-map.md`
- `utilities/swarm/.context/plan-and-swarm-utilities-23/thin-slicing.md`
- `utilities/plan/.context/module-context.md`
- `utilities/swarm/.context/module-context.md`
- `utilities/workspace/.context/module-context.md`
- `utilities/git/.context/module-context.md`
- `utilities/sub_agent/.context/module-context.md`
- `context_tools/agent_bdd/.context/module-context.md` (ai_judge / JudgeResult)
- Canvas: `C:/Users/jeffa/.cursor/projects/c-dev-abd-works-repo/canvases/run-planned-work-story-map.canvas.tsx`

## Process

- Shell: PowerShell; `;` not `&&`. `$env:PYTHONIOENCODING="utf-8"`. From this repo: `.\tools.ps1` only. Pipe YAML to stdin. Do not remanifest. Do not write `_req.yaml`.
- Primary clone stays on its own branch. Work only in the sibling worktree above.
- Sketch BDDs first. Formal `.md` scenarios are drafts.

## Increment 4 sketch already started

Create Supervisor (Outcome) then Add Agent (Hypothesis). Agent runs Execute Plan on its WorkSession. Compare Swarm Results reuses Evaluate Results / Review Progress. Comparative Association applies Supervisor rubric across Agent results as they arrive.
