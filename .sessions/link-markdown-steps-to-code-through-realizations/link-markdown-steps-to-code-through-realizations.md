# Link Markdown Steps To Code Through Realizations

Decided 2026-11-16 in the file-manager chat: only a step backed by code is asked to invoke code (rule `code-steps-invoke-code`; `invokes?:` on `when` in cdd_guidance/practices/stories/model/schema.yaml), so a When in a markdown scenarios file carries no invokes edge and no finding. A markdown step could name its code only through a generated scenario realization, whose call graph names the domain operations the step's linked domain terms (`++Ticket++` -> domain-model.md#ticket) lead to.

To build when worth it:
- Read each scenario's realization (Stories "Scenario realizations", BDD realization) and record, per markdown step, the operations its call graph names.
- Link the step to those operations in Clean Engineering (`invokes` / `invokedBy`), matching through the domain-term links of the step, so the graph view's invokes group and the source view's callouts work for markdown scenarios as they do for story tests.
- Keep the realization in step with the domain model: a renamed operation or a step with no realization yet leaves the step unlinked, never wrongly linked.
- Then ask `code-steps-invoke-code` (or a sibling rule) of markdown Whens that have a realization.

The person judged it possibly "more complex than it's worth", so it waits here.
