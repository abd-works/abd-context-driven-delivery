# Link Markdown Steps To Code Through Realizations

Decided 2026-11-16 in the file-manager chat: only a step backed by code is asked to invoke code (rule `code-steps-invoke-code`; `invokes?:` on `when` in cdd_guidance/practices/stories/model/schema.yaml), so a When in a markdown scenarios file carries no invokes edge and no finding. A markdown step could name its code only through a generated scenario realization, whose call graph names the domain operations the step's linked domain terms (`++Ticket++` -> domain-model.md#ticket) lead to.

To build when worth it:
- Read each scenario's realization (Stories "Scenario realizations", BDD realization) and record, per markdown step, the operations its call graph names.
- Link the step to those operations in Clean Engineering (`invokes` / `invokedBy`), matching through the domain-term links of the step, so the graph view's invokes group and the source view's callouts work for markdown scenarios as they do for story tests.
- Keep the realization in step with the domain model: a renamed operation or a step with no realization yet leaves the step unlinked, never wrongly linked.
- Then ask `code-steps-invoke-code` (or a sibling rule) of markdown Whens that have a realization.

The person judged it possibly "more complex than it's worth", so it waits here.

## Done 2026-11-23

Built on release-1-2-fixes at the person's direction of 2026-11-23: a realization links markdown to markdown, as a code step links to code.

- A step keeps the calls its realization's call graph names as its `realization_calls` fact (`cdd_guidance/practices/stories/model/story_map.py`).
- DDD records each operation a domain model card declares as an Operation node under its building block, so a domain model's operations can be linked to (`cdd_guidance/practices/ddd/reading/graph_reading.py`); the Clean Engineering class model's operations were nodes already.
- `RealizationLinks` (`cdd_guidance/practices/stories/model/realization_links.py`) links each step to the operations its calls name, matched only in the model documents the step's domain-term links lead to: `Cart.addBook(...)` is Cart's addBook; a call on an example or a field is the operation of the one linked class that declares it. A renamed operation, a call two linked classes could answer, and a step with no realization stay unlinked; a step whose links reach no model document the graph read is left unjudged, as scenarios are often written before their model.
- `code-steps-invoke-code` now also reports a markdown When whose realization names no operation of the model its links lead to.
- Story: *Link Markdown Steps To Model Operations* under Map Work Into Knowledge Graph › Build Practice Trees From Source, in thin slice Increment 0: Built.
