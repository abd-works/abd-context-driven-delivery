# Validate: clean-engineering-model on harness/kanban/kanban-model.md

Rubric: `validate-kanban-model.md` (Validate action, guidance `clean-engineering-model`, paths `harness/kanban/kanban-model.md`).

## Graph rules

No violations. The graph built from the edited paths holds the `harness/kanban` module and its `module-context.md`; it does not read classes from a markdown model, so the class rules below are judged by reading the model.

## AI-judged rules

| Rule | Verdict | Evidence |
|---|---|---|
| vocabulary-traces-to-source | pass | kanban board, ticket, stage, board position, skill progress, lineage from the abd-skills kanban domain model; guidance and PracticeGuidance from harness/guidance |
| do-not-invent-terms | pass | no second noun for an existing concept |
| do-not-invent-parallel-object-models | pass, watch | `SessionLog` reads the file `Session` writes. It adds only what the board needs (progress per guidance, pull lines) and records pulls through `Session.append_log`. If `Session` later grows its own log reader, merge them. |
| model-modules-follow-the-partition | pass | one module, `harness/kanban`, matching `.context/module-context.md` |
| class-not-property-instance-or-subtype | pass | `SkillProgress`, `BoardPosition`, `Stage` each carry derived behaviour (`is_reviewed`, `is_ready_to_pull`, `work_required`) |
| keep-classes-single-responsibility | pass | board reads and lists; ticket moves itself; log reads progress |
| shape-classes-around-resources | pass | no manager or service; `Ticket` owns pull, close, archive |
| put-logic-on-the-owning-resource | pass | `Ticket.pull` checks its own stage; `Stage.work_required` filters by its own fidelities |
| hide-inner-details | pass | storage (`session.json`, folder moves) stays behind `Ticket` operations |
| use-property-not-accessor | pass | `position`, `next_guidance`, `skill_progress`, `is_closed` are derived properties |
| prefer-class-operations | pass | no module-level functions |
| use-explicit-dependencies | pass, note | collaborators arrive through constructors. `KanbanBoard` builds a `Ticket` per folder while reading; at code fidelity give it a way to build tickets that a test can replace |
| external-system-interface-is-one-way | not applicable | no external system |
| keep-operations-single-responsibility | pass | |
| limit-operation-parameters | pass | at most 3 |
| avoid-vague-parameter-names | pass | |
| errors-out-of-existence | pass | no folder, no options, no pulls each return empty or defaults |
| state-change-returns-record-or-named-failure | pass | `select_guidance`, `close`, `archive`, `new_ticket` return the `Ticket`; `pull` returns the `BoardPosition` or fails with `StageNotDone` |
| domain-exception-carries-context | pass, note | `StageNotDone` named; its fields (ticket, stage, guidance not yet reviewed) are decided at code fidelity |
| limit-comments | pass | comments are invariants only |
| write-invariants | pass | one column per ticket; never moves by itself; progress never stored; selection within options |
| write-interactions | pass | calls name public operations on `Session`, `Repo`, `SessionLog`, `Stage`, `BoardOptions` |
| no-redundant-relationship-paths | pass | `KanbanBoard.active` is one of `tickets`, not a second link |
| use-intention-revealing-names | pass | |
| use-consistent-naming | pass | guidance throughout: `selected_guidance`, `select_guidance`, `next_guidance` |
| eliminate-duplication | pass | |
| one-canonical-model-document | pass | `module-context.md` holds the seam only and points at the model |

## Outside the rubric

- `KanbanBoard.board()` returns `dict`. It is the JSON the board pane and other IDEs read; its shape is in `.context/backlog/session-board.md`. At code fidelity, give that shape a type so callers do not depend on dictionary keys.

No failures to fix.
