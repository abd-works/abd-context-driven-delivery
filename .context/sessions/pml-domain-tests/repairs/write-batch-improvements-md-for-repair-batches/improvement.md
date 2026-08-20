# write-batch-improvements-md-for-repair-batches

- **tool:** Eval (Repair)
- **error:** A batch of open mistakes was walked one-by-one in chat (and toward new scanners) instead of one table against the existing tool surface, recorded in the session.
- **rule:** (process) several open mistakes
- **what changed:**
  - **Prose — yes.** `utilities/eval/repair.md`: for several open mistakes, inspect the whole existing tool, write `{session.folder}/batch-improvements.md` (theme / already in the tool / why it failed / improvement), one batch decision, then apply. `createRule` only when mechanical and the existing surface cannot carry it.
  - **Prose — yes.** `utilities/eval/.context/module-context.md` records the batch file.
  - **Prose — yes.** `context_tools/base/createRule.md`: do not mint a ban-list rule until contexts/examples/template/generator have been checked.
  - **Detector — no.**
  - **This session’s record:** `{session.folder}/batch-improvements.md`
