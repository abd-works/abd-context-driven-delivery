# clean-engineering-model: harness/kanban/kanban-model

**Validated:** `harness/kanban/kanban-model.md`, `harness/kanban/kanban-model.drawio`, 2026-10-31
**Graph rules:** no violations reported. The validate call listed the Stories rules as its AI rules, not the Clean Engineering model rules, so the judgments below are against the model rules from the generate reply.

## Judgment

- `vocabulary-traces-to-source`, `do-not-invent-terms`: pass. Names come from the code and the Board canvas.
- `do-not-invent-parallel-object-models`: pass. The pane is not modelled as a second Board.
- `model-modules-follow-the-partition`: pass. One module, `harness/kanban`.
- `class-not-property-instance-or-subtype`: pass. No class added; next_action and practices are properties.
- `keep-classes-single-responsibility`, `shape-classes-around-resources`, `put-logic-on-the-owning-resource`: pass. next_action sits on FidelityProgress, which owns the actions done.
- `hide-inner-details`: warning. `_log_lines` is a private member kept in the model for its log-format note.
- `use-property-not-accessor`, `avoid-vague-parameter-names`, `limit-operation-parameters`: pass.
- `prefer-class-operations`: finding in the code, not the model. `practice_key` is a module-level function in `ticket.py`.
- `use-explicit-dependencies`: pass. `Board.load` is a factory.
- `state-change-returns-record-or-named-failure`: warning. `Ticket.move_previous` is typed as returning Ticket, and its intended move into the Backlog returns a BacklogItem. The note says so; the signature changes when that is built.
- `domain-exception-carries-context`: pass. StageNotDone carries the ticket and stage, and goes with pull.
- `write-invariants`, `write-interactions`: pass.
- `no-redundant-relationship-paths`: pass.
- `use-consistent-naming`: failed, fixed. `switch_practice` reused the word session.switch uses for the active session; it is now `enable_practice`.
- `use-intention-revealing-names`, `eliminate-duplication`: pass.
- `one-canonical-model-document`: pass.

## Not passing yet

- `to_json(): dict` and `reports: dict` are untyped, mirroring the code.
- The rendered diagram has no inheritance arrows for Backlog and Stage, and no edges from Board to Column or BacklogItem or from Kanban.
