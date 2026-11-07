# Validate

Take the persona of a **critical judge** — do not edit the artifact.

1. Read the appropriate practice and fidelity level guidlines and rules. Scope judgment to artifacts passed into context.
2. Use each **practice** as the rubric — report Pass or Fail per named practice fidelity and named rule with brief evidence. There is no third verdict: a rule that is only partly met is a Fail, because a softer verdict lets a broken rule through review.
3. When **paths** names the files being edited, the graph is built from just those files as they are now, and its rules run on them. Pass the files you wrote, not the whole tree. Without **paths**, when **graph** is `true`, read the workspace's saved graph (`.context/graph.json`, written by `graph_load_working_copy`); when it is a path (or list of paths), read that `graph_return_nodes` JSON or saved graph. Append a **Graph rule validation** report for each guidance's practice. Each rule is one section: heading, rule text, any graph hits (**[graph rule]**), then the AI judgment prompt for that rule.
4. Collection validate on graph-backed practices reads the working copy and reports each rule hit. A single base Rule is instruction text only.
5. Do not fix. Report failures for fixing, then add your judgment for each rule to the report this action saved, so the board links to the whole result. It names the report's path at the end of its reply.
6. Append the judgment to the end of the saved report in exactly this shape. The session board parses it, lists each finding beside the graph's hits, opens the finding's file at its line, and sends a Fix back, so a finding in any other shape is lost:

   ```markdown
   ## Judgment — `harness/kanban/.context/story-map.md`

   ### `rule-slug` — Fail
   - story-map.md:86 `Archive Ticket`: what breaks the rule, and why.

   ### `other-rule-slug` — Fail
   - story-map.md:148 `Send Sketch Iterate Or Document`: what breaks the rule, and why.
   ```

   - **One `## Judgment — ` section per judged file,** with an em dash, and the file in backticks as a path from the project's root, the way the session names paths. Never an absolute path or another checkout's path, because the board opens the file in this project and cannot open one anywhere else.
   - **One `### ` heading per rule that fails:** the rule slug in backticks, an em dash, then `Fail`. Leave passing rules out of these headings; a table or a Passes paragraph after the judgment may list them.
   - **One bullet per finding,** opening with the judged file's name, a colon, and one line number (`story-map.md:86`), then a space and what breaks the rule. A finding that spans lines takes its first line, and a finding at two places is two bullets, because the board opens each finding at one line.


Judge only the checked format's files (python: C:/Users/jeffa/.cdd/runtime-ensure-domain-orientatio/{module}/). The other formats mirror them, so judging those too reports every finding twice.

# Graph rule validation

**Generated:** 2026-11-07 00:09:40 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 286
**Rules with graph hits:** 13
**AI rules in scope:** 18

## Rules

Each rule shows its guidance text, any graph scanner hits (`**[graph rule]**`), then the AI judgment prompt.

### `vocabulary-traces-to-source`

Take every term from the source. The English term and the code name are the same word: *shopping cart* is `ShoppingCart`. When the code says a different word than the domain, every reader keeps a translation in their head, and the two names drift until they mean different things.

Evaluate the current context against this rule (vocabulary-traces-to-source):

### `do-not-invent-terms`

Do not invent a second noun or a parallel vocabulary. A second noun for the same thing becomes a second class, and then the same rule has to be written and fixed in both.

Evaluate the current context against this rule (do-not-invent-terms):

### `do-not-invent-parallel-object-models`

Keep one object model. Follow the nouns and verbs the rest of the graph already uses for that concept. A class that joins types the rest of the graph keeps apart is a second model — a big ball of mud — and every rule then has to be written and fixed in both. When data or behavior already belongs to an object, extend that object and hand callers the object itself: `ticket.session.practices["stories"].fidelities["story_map"].files()`, not `ticket.files(["stories-story_map"])`. A second model is rarely a whole class family; more often it is a small copy beside the owner: a dict holding one field from each member (`fidelity_states`, `violation_counts`), a `*_name` copy of a reference (`column_name`), a helper class that does the owner's job (`TicketFiles`), a bag of a few of the owner's answers (`Workspace`), or a `*Model` / `*Entry` family scraped from live objects. A copy hides that the owner is missing the behavior, so the next caller builds another copy and a fix to the owner never reaches it. **Checking it:** this rule spans modules, and the copy looks fine in the file that holds it. For every property, data field, dict, and helper class the changed code adds, name the class that already owns that data and read it; the rule fails when the owner holds it or should, and the change copies it instead of returning or extending the owner. Count the members of a class that delegates: dozens of members on a class that only reads its collaborators means it is copying them.

Evaluate the current context against this rule (do-not-invent-parallel-object-models):

### `hide-inner-details`

Expose behavior through named operations. Do not let callers see how the class stores or arranges its data — once they read the storage directly it becomes a public contract you cannot change. Private fields on the same class hide implementation; you do not need a second class for that. Read-only to callers can mean return a copy or immutable view from a property — it does not require a frozen class or a second type to hold build steps.

Evaluate the current context against this rule (hide-inner-details):

### `keep-operations-small-focused`

Keep each operation short enough to read as one thought — under 20 statements. A multi-line call, list, or string initializer is one statement. When it grows, extract a private helper whose name says why that slice exists.

**Graph violations:** 43

- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L745): Operation `generate_catalog`: Operation 'generate_catalog' is 34 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L1013): Operation `generate_catalog`: Operation 'generate_catalog' is 24 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L1047): Operation `generate_catalog`: Operation 'generate_catalog' is 26 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L1112): Operation `generate_catalog`: Operation 'generate_catalog' is 41 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L1313): Operation `generate_project_approach`: Operation 'generate_project_approach' is 43 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L1360): Operation `configure_project_approach`: Operation 'configure_project_approach' is 58 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L1646): Operation `approach_page_body`: Operation 'approach_page_body' is 350 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/generate_cdd_catalog.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\generate_cdd_catalog.py#L29): Operation `main`: Operation 'main' is 42 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/monaco_fold_smoke.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\monaco_fold_smoke.py#L29): Operation `main`: Operation 'main' is 84 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/project_approach.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\project_approach.py#L44): Operation `from_paths`: Operation 'from_paths' is 23 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/project_approach.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\project_approach.py#L79): Operation `generate`: Operation 'generate' is 39 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/spec_column_smoke.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\spec_column_smoke.py#L14): Operation `main`: Operation 'main' is 71 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/story_map_smoke.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\story_map_smoke.py#L29): Operation `main`: Operation 'main' is 110 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-approach-stage-columns.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-approach-stage-columns.js#L13): Operation `measureStageColumn`: Operation 'measureStageColumn' is 35 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-drawio.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-drawio.js#L47): Operation `bindStoryMapWrap`: Operation 'bindStoryMapWrap' is 58 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-drawio.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-drawio.js#L108): Operation `bindFramedWrap`: Operation 'bindFramedWrap' is 23 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-drawio.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-drawio.js#L134): Operation `bindWrap`: Operation 'bindWrap' is 34 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-drawio.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-drawio.js#L194): Operation `scrollPageToExample`: Operation 'scrollPageToExample' is 25 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L369): Operation `updateCrosscutSections`: Operation 'updateCrosscutSections' is 25 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L405): Operation `syncBoardGridRows`: Operation 'syncBoardGridRows' is 40 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L534): Operation `applyStageColumnFilter`: Operation 'applyStageColumnFilter' is 28 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L158): Operation `setTourBoardState`: Operation 'setTourBoardState' is 29 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L218): Operation `initFoundryTooltips`: Operation 'initFoundryTooltips' is 117 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L533): Operation `lineUpSpecHeader`: Operation 'lineUpSpecHeader' is 21 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L635): Operation `showAlignedCells`: Operation 'showAlignedCells' is 28 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L697): Operation `flyRingRect`: Operation 'flyRingRect' is 25 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L734): Operation `flyRing`: Operation 'flyRing' is 36 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L884): Operation `transitionTourStep`: Operation 'transitionTourStep' is 21 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L929): Operation `revealGuideText`: Operation 'revealGuideText' is 30 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L969): Operation `resetTour`: Operation 'resetTour' is 23 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L996): Operation `animateScopeTour`: Operation 'animateScopeTour' is 29 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L1030): Operation `animatePerspectiveTour`: Operation 'animatePerspectiveTour' is 26 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L1111): Operation `animateChangeImplications`: Operation 'animateChangeImplications' is 21 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L1136): Operation `advanceMode`: Operation 'advanceMode' is 24 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L1163): Operation `retreatMode`: Operation 'retreatMode' is 23 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-monaco.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-monaco.js#L50): Operation `collapseAllFolds`: Operation 'collapseAllFolds' is 36 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-monaco.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-monaco.js#L96): Operation `scheduleCollapse`: Operation 'scheduleCollapse' is 23 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-monaco.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-monaco.js#L138): Operation `mount`: Operation 'mount' is 41 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-nav.js#L240): Operation `inject`: Operation 'inject' is 115 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L64): Operation `measureExampleHeight`: Operation 'measureExampleHeight' is 38 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L159): Operation `toggleStageColumn`: Operation 'toggleStageColumn' is 22 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L187): Operation `openNext`: Operation 'openNext' is 26 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L258): Operation `bindHost`: Operation 'bindHost' is 21 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L299): Operation `normalize`: Operation 'normalize' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L628): Operation `parse`: Operation 'parse' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L643): Operation `whole_file`: Operation 'whole_file' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L647): Operation `comment_tag`: Operation 'comment_tag' is a classmethod; prefer an instance operation.

Evaluate the current context against this rule (prefer-instance-operations):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

**Graph violations:** 12

- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L1646): Operation `approach_page_body`: Operation 'approach_page_body' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/generate_cdd_catalog.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\generate_cdd_catalog.py#L29): Operation `main`: Operation 'main' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/monaco_fold_smoke.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\monaco_fold_smoke.py#L29): Operation `main`: Operation 'main' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/story_map_smoke.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\story_map_smoke.py#L29): Operation `main`: Operation 'main' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L74): Operation `readSavedFilter`: Operation 'readSavedFilter' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L91): Operation `readSavedStageFilter`: Operation 'readSavedStageFilter' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L131): Operation `readCrosscutPref`: Operation 'readCrosscutPref' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L146): Operation `readCollapsedColsPref`: Operation 'readCollapsedColsPref' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L461): Operation `setSkillsExpanded`: Operation 'setSkillsExpanded' delegates to both I/O and domain helpers; give it one job.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L481): Operation `applyFilter`: Operation 'applyFilter' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L565): Operation `toggleStage`: Operation 'toggleStage' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-nav.js#L240): Operation `inject`: Operation 'inject' delegates to both I/O and domain helpers; give it one job.

Evaluate the current context against this rule (keep-operations-single-responsibility):

### `simplify-control-flow`

Handle the failing or empty cases first and return. Keep the main path flat. Do not nest more than three levels — deeper than that you cannot tell which conditions hold on a given line without reading back up, and that is where the unhandled branch hides.

Evaluate the current context against this rule (simplify-control-flow):

### `errors-out-of-existence`

For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/story_map_smoke.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\story_map_smoke.py#L29): Operation `main`: Operation 'main' raises on an empty or missing value; return a quiet result instead.

Evaluate the current context against this rule (errors-out-of-existence):

### `no-prototype-swapping`

An object keeps the class it was built as. Do not change it afterwards with `Object.setPrototypeOf`, `__proto__ =`, or `__class__ =`. When a subclass needs to make its own instances, give the base an overridable factory (`blank()`) or build the right class directly. A swapped object skips its constructor, so fields the subclass sets up are missing and nothing tells you.

Evaluate the current context against this rule (no-prototype-swapping):

### `use-intention-revealing-names`

Name each class, property, operation, and parameter so it answers why it exists. Do not abbreviate.

**Graph violations:** 12

- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L349): Parameter `el`: Parameter 'el' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L387): Parameter `r`: Parameter 'r' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L441): Parameter `ms`: Parameter 'ms' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L447): Parameter `el`: Parameter 'el' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L456): Parameter `e`: Parameter 'e' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-nav.js#L500): Parameter `m`: Parameter 'm' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L18): Parameter `id`: Parameter 'id' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L129): Parameter `on`: Parameter 'on' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L150): Parameter `id`: Parameter 'id' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L159): Parameter `id`: Parameter 'id' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L232): Parameter `id`: Parameter 'id' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L232): Parameter `on`: Parameter 'on' does not reveal intent.

Evaluate the current context against this rule (use-intention-revealing-names):

### `use-consistent-naming`

Use one word per concept. Pick one verb and use it everywhere (`fetch_`, not a mix of `fetch_`, `get_`, and `retrieve_`). Two words for one concept is how the same logic gets written twice — nobody searching for `fetch_` finds the `retrieve_` that already does the job.

Evaluate the current context against this rule (use-consistent-naming):

### `provide-meaningful-context`

Give a number or literal a name that says why it is there (`SECONDS_PER_DAY`, not `86400`). Do not number variables (`item1`).

**Graph violations:** 31

- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/monaco_fold_smoke.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\monaco_fold_smoke.py#L29): Operation `main`: Operation 'main' uses the unnamed number 2500.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/spec_column_smoke.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\spec_column_smoke.py#L14): Operation `main`: Operation 'main' uses the unnamed number 1400.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/story_map_smoke.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\story_map_smoke.py#L29): Operation `main`: Operation 'main' uses the unnamed number 1200.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-approach-stage-columns.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-approach-stage-columns.js#L8): Operation `monacoWidth`: Operation 'monacoWidth' uses the unnamed number 960.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-approach-stage-columns.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-approach-stage-columns.js#L13): Operation `measureStageColumn`: Operation 'measureStageColumn' uses the unnamed number 320.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-approach-stage-columns.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-approach-stage-columns.js#L86): Operation `init`: Operation 'init' uses the unnamed number 120.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-drawio.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-drawio.js#L134): Operation `bindWrap`: Operation 'bindWrap' uses the unnamed number 120.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-drawio.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-drawio.js#L176): Operation `navOffset`: Operation 'navOffset' uses the unnamed number 16.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-drawio.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-drawio.js#L194): Operation `scrollPageToExample`: Operation 'scrollPageToExample' uses the unnamed number 16.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-drawio.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-drawio.js#L234): Operation `approachStageScroll`: Operation 'approachStageScroll' uses the unnamed number 480.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-drawio.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-drawio.js#L261): Operation `refreshDrawioColumn`: Operation 'refreshDrawioColumn' uses the unnamed number 1200.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L190): Operation `scrollTourToFold`: Operation 'scrollTourToFold' uses the unnamed number 16.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L202): Operation `openStageDetails`: Operation 'openStageDetails' uses the unnamed number 450.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L218): Operation `initFoundryTooltips`: Operation 'initFoundryTooltips' uses the unnamed number 260.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L487): Operation `focusStages`: Operation 'focusStages' uses the unnamed number 220.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L533): Operation `lineUpSpecHeader`: Operation 'lineUpSpecHeader' uses the unnamed number 80.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L635): Operation `showAlignedCells`: Operation 'showAlignedCells' uses the unnamed number 80.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L666): Operation `placeEmptyColumnHead`: Operation 'placeEmptyColumnHead' uses the unnamed number 80.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L697): Operation `flyRingRect`: Operation 'flyRingRect' uses the unnamed number 360.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L734): Operation `flyRing`: Operation 'flyRing' uses the unnamed number 320.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L908): Operation `waitForLayoutAfterCollapse`: Operation 'waitForLayoutAfterCollapse' uses the unnamed number 620.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-monaco.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-monaco.js#L25): Operation `visible`: Operation 'visible' uses the unnamed number 40.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-monaco.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-monaco.js#L96): Operation `scheduleCollapse`: Operation 'scheduleCollapse' uses the unnamed number 40.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-monaco.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-monaco.js#L105): Operation `attempt`: Operation 'attempt' uses the unnamed number 40.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-monaco.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-monaco.js#L138): Operation `mount`: Operation 'mount' uses the unnamed number 13.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-nav.js#L240): Operation `inject`: Operation 'inject' uses the unnamed number 350.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-nav.js#L326): Operation `closeDrawer`: Operation 'closeDrawer' uses the unnamed number 350.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-nav.js#L534): Operation `handleScroll`: Operation 'handleScroll' uses the unnamed number 20.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L51): Operation `showExampleEditors`: Operation 'showExampleEditors' uses the unnamed number 460.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L64): Operation `measureExampleHeight`: Operation 'measureExampleHeight' uses the unnamed number 0.88.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L112): Operation `afterOpen`: Operation 'afterOpen' uses the unnamed number 40.

Evaluate the current context against this rule (provide-meaningful-context):

### `eliminate-duplication`

Give repeated logic one canonical function. Every copy is another place the fix has to be repeated, and the copy you miss is the bug.

Evaluate the current context against this rule (eliminate-duplication):

### `no-legacy-api-after-refactor`

When you rename or reshape a public seam, update every caller — tests, dependencies, and adjacent modules — to the new API. Do not keep compatibility aliases, re-exports, or thin wrappers that preserve the old name.

Evaluate the current context against this rule (no-legacy-api-after-refactor):

### `use-exceptions-properly`

Raise a domain exception that names the failure (`CartAlreadyCheckedOut`, not `Error` or a bare string). Catch the specific type you can handle. Do not use a bare `except`. A generic exception cannot be caught selectively, so the caller has to handle everything or nothing.

Evaluate the current context against this rule (use-exceptions-properly):

### `never-swallow-exceptions`

Do not catch and ignore. Log and re-raise, or convert to a domain exception that still names the failure. A `pass` in `except` hides a broken invariant.

**Graph violations:** 13

- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L15): Operation `stripScrollRestoreFromUrl`: Operation 'stripScrollRestoreFromUrl' swallows a caught failure.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L85): Operation `saveFilter`: Operation 'saveFilter' swallows a caught failure.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L103): Operation `saveStageFilter`: Operation 'saveStageFilter' swallows a caught failure.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L126): Operation `saveSkillsExpandedPref`: Operation 'saveSkillsExpandedPref' swallows a caught failure.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L140): Operation `saveCrosscutPref`: Operation 'saveCrosscutPref' swallows a caught failure.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L155): Operation `saveCollapsedColsPref`: Operation 'saveCollapsedColsPref' swallows a caught failure.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L192): Operation `parseSkillHref`: Operation 'parseSkillHref' swallows a caught failure.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L697): Operation `flyRingRect`: Operation 'flyRingRect' swallows a caught failure.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L734): Operation `flyRing`: Operation 'flyRing' swallows a caught failure.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-nav.js#L50): Operation `modeFromUrl`: Operation 'modeFromUrl' swallows a caught failure.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-nav.js#L59): Operation `resolveInitialMode`: Operation 'resolveInitialMode' swallows a caught failure.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-nav.js#L91): Operation `assetBase`: Operation 'assetBase' swallows a caught failure.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-nav.js#L240): Operation `inject`: Operation 'inject' swallows a caught failure.

Evaluate the current context against this rule (never-swallow-exceptions):

### `limit-comments`

write comment in operations and properties only when the signature cannot say a constraint or explain why the code behaves the way it does. Do not narrate a line that already names what it does.

Evaluate the current context against this rule (limit-comments):

### `avoid-vague-parameter-names`

Do not name parameters `data`, `options`, `info`, or other placeholders that could mean anything. A vague name hides what the caller must supply and what the operation does with it.

**Graph violations:** 6

- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L478): Operation `flyRingToTargets`: Parameter 'opts' in 'flyRingToTargets' is vague.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L697): Operation `flyRingRect`: Parameter 'opts' in 'flyRingRect' is vague.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L734): Operation `flyRing`: Parameter 'opts' in 'flyRing' is vague.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L861): Operation `fadeInTogether`: Parameter 'opts' in 'fadeInTogether' is vague.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L884): Operation `transitionTourStep`: Parameter 'opts' in 'transitionTourStep' is vague.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L929): Operation `revealGuideText`: Parameter 'opts' in 'revealGuideText' is vague.

Evaluate the current context against this rule (avoid-vague-parameter-names):

### `deep-module`

Keep most classes private (at most **40%** public) in each first-class module. A first-class module is a folder that owns `.context/module-context.md`. Nested folders that also own that file are separate modules — respect them. Nested folders that do not own it roll up to the nearest enclosing module-context folder, or to the folder you are querying if none sits in between. Count classes, not operations: a public method on a hidden class is not a second seam. Every public class is a signature you cannot change without editing every caller, so public classes are much harder to refactor than private ones.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/catalog_generator](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator#L1): Module `catalog_generator`: Module 'catalog_generator' splits into many tiny classes (34); prefer a deep module with a small public surface.

Evaluate the current context against this rule (deep-module):

### `keep-classes-single-responsibility`

Give each class one reason to change.

**Graph violations:** 6

- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-drawio.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-drawio.js#L1): OoadClass `_module`: Class '_module' exposes 19 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L1): OoadClass `_module`: Class '_module' exposes 42 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L1): OoadClass `_module`: Class '_module' exposes 66 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-monaco.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-monaco.js#L1): OoadClass `_module`: Class '_module' exposes 11 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-nav.js#L1): OoadClass `_module`: Class '_module' exposes 17 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L1): OoadClass `_module`: Class '_module' exposes 15 public operations (budget ~9). Split responsibilities.

Evaluate the current context against this rule (keep-classes-single-responsibility):

### `limit-operation-parameters`

Have callers pass intent, not setup. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L1313): Operation `generate_project_approach`: Operation 'generate_project_approach' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L478): Operation `flyRingToTargets`: Operation 'flyRingToTargets' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L129): Operation `setStageOpen`: Operation 'setStageOpen' takes 4 parameters (maximum 3, excluding self).

Evaluate the current context against this rule (limit-operation-parameters):

### `use-explicit-dependencies`

Pass every collaborator through the constructor. Do not reach for a global or construct a collaborator inside construction. A collaborator the class fetches or builds itself cannot be swapped, so the class can only ever run against that one implementation.

**Graph violations:** 5

- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L55): OoadClass `CatalogPractice`: Class 'CatalogPractice' constructs 'SkillSlashName' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L341): OoadClass `CatalogPage`: Class 'CatalogPage' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L781): OoadClass `FidelityTemplate`: Class 'FidelityTemplate' constructs 'Format' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L1156): OoadClass `Catalog`: Class 'Catalog' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/foundry_chrome.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\foundry_chrome.py#L290): OoadClass `Brand`: Class 'Brand' constructs 'Path' inside its constructor.

Evaluate the current context against this rule (use-explicit-dependencies):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 149

- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L334): Parameter `func`: Parameter 'func' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L682): Parameter `tool`: Parameter 'tool' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L682): Parameter `owner`: Parameter 'owner' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L1243): Parameter `guidance`: Parameter 'guidance' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L1646): Parameter `example_sources`: Parameter 'example_sources' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-approach-stage-columns.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-approach-stage-columns.js#L8): Parameter `body`: Parameter 'body' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-approach-stage-columns.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-approach-stage-columns.js#L8): Parameter `clip`: Parameter 'clip' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-approach-stage-columns.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-approach-stage-columns.js#L13): Parameter `col`: Parameter 'col' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-approach-stage-columns.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-approach-stage-columns.js#L56): Parameter `host`: Parameter 'host' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-approach-stage-columns.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-approach-stage-columns.js#L56): Parameter `onlyCol`: Parameter 'onlyCol' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-drawio.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-drawio.js#L16): Parameter `wrap`: Parameter 'wrap' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-drawio.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-drawio.js#L20): Parameter `root`: Parameter 'root' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-drawio.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-drawio.js#L20): Parameter `scale`: Parameter 'scale' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-drawio.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-drawio.js#L26): Parameter `wrap`: Parameter 'wrap' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-drawio.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-drawio.js#L36): Parameter `wrap`: Parameter 'wrap' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-drawio.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-drawio.js#L36): Parameter `pageW`: Parameter 'pageW' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-drawio.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-drawio.js#L36): Parameter `pageH`: Parameter 'pageH' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-drawio.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-drawio.js#L47): Parameter `wrap`: Parameter 'wrap' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-drawio.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-drawio.js#L108): Parameter `wrap`: Parameter 'wrap' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-drawio.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-drawio.js#L134): Parameter `wrap`: Parameter 'wrap' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-drawio.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-drawio.js#L181): Parameter `col`: Parameter 'col' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-drawio.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-drawio.js#L194): Parameter `col`: Parameter 'col' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-drawio.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-drawio.js#L224): Parameter `col`: Parameter 'col' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-drawio.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-drawio.js#L234): Parameter `col`: Parameter 'col' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-drawio.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-drawio.js#L246): Parameter `host`: Parameter 'host' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-drawio.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-drawio.js#L253): Parameter `frame`: Parameter 'frame' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-drawio.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-drawio.js#L261): Parameter `col`: Parameter 'col' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L27): Parameter `href`: Parameter 'href' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L85): Parameter `families`: Parameter 'families' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L103): Parameter `stageIds`: Parameter 'stageIds' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L126): Parameter `expanded`: Parameter 'expanded' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L140): Parameter `groups`: Parameter 'groups' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L155): Parameter `cols`: Parameter 'cols' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L165): Parameter `link`: Parameter 'link' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L170): Parameter `surface`: Parameter 'surface' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L192): Parameter `href`: Parameter 'href' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L205): Parameter `stageIds`: Parameter 'stageIds' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L290): Parameter `stage`: Parameter 'stage' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L290): Parameter `collapsed`: Parameter 'collapsed' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L305): Parameter `stage`: Parameter 'stage' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L325): Parameter `row`: Parameter 'row' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L345): Parameter `row`: Parameter 'row' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L345): Parameter `expanded`: Parameter 'expanded' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L360): Parameter `row`: Parameter 'row' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L400): Parameter `expanded`: Parameter 'expanded' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L448): Parameter `btn`: Parameter 'btn' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L461): Parameter `expanded`: Parameter 'expanded' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L461): Parameter `source`: Parameter 'source' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L495): Parameter `btn`: Parameter 'btn' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L495): Parameter `selected`: Parameter 'selected' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L509): Parameter `btn`: Parameter 'btn' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L526): Parameter `stage`: Parameter 'stage' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L530): Parameter `stage`: Parameter 'stage' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-skill-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-skill-nav.js#L565): Parameter `stageId`: Parameter 'stageId' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L123): Parameter `text`: Parameter 'text' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L123): Parameter `withArrow`: Parameter 'withArrow' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L158): Parameter `state`: Parameter 'state' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L226): Parameter `trigger`: Parameter 'trigger' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L226): Parameter `tip`: Parameter 'tip' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L232): Parameter `tip`: Parameter 'tip' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L232): Parameter `holder`: Parameter 'holder' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L239): Parameter `immediate`: Parameter 'immediate' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L260): Parameter `trigger`: Parameter 'trigger' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L260): Parameter `holder`: Parameter 'holder' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L283): Parameter `triggers`: Parameter 'triggers' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L283): Parameter `holderSelector`: Parameter 'holderSelector' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L294): Parameter `triggers`: Parameter 'triggers' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L314): Parameter `triggers`: Parameter 'triggers' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L349): Parameter `el`: Parameter 'el' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L380): Parameter `fromRect`: Parameter 'fromRect' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L387): Parameter `r`: Parameter 'r' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L394): Parameter `elements`: Parameter 'elements' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L394): Parameter `pad`: Parameter 'pad' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L425): Parameter `elements`: Parameter 'elements' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L425): Parameter `pad`: Parameter 'pad' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L441): Parameter `ms`: Parameter 'ms' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L447): Parameter `el`: Parameter 'el' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L447): Parameter `prop`: Parameter 'prop' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L447): Parameter `fallbackMs`: Parameter 'fallbackMs' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L456): Parameter `e`: Parameter 'e' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L478): Parameter `fromRect`: Parameter 'fromRect' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L478): Parameter `elements`: Parameter 'elements' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L478): Parameter `pad`: Parameter 'pad' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L478): Parameter `opts`: Parameter 'opts' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L487): Parameter `elements`: Parameter 'elements' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L611): Parameter `collapsed`: Parameter 'collapsed' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L635): Parameter `texts`: Parameter 'texts' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L697): Parameter `fromRect`: Parameter 'fromRect' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L697): Parameter `toRect`: Parameter 'toRect' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L697): Parameter `opts`: Parameter 'opts' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L734): Parameter `fromEl`: Parameter 'fromEl' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L734): Parameter `toEl`: Parameter 'toEl' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L734): Parameter `opts`: Parameter 'opts' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L777): Parameter `steps`: Parameter 'steps' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L861): Parameter `tag`: Parameter 'tag' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L861): Parameter `html`: Parameter 'html' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L861): Parameter `opts`: Parameter 'opts' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L884): Parameter `runId`: Parameter 'runId' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L884): Parameter `opts`: Parameter 'opts' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L929): Parameter `tag`: Parameter 'tag' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L929): Parameter `html`: Parameter 'html' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L929): Parameter `opts`: Parameter 'opts' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-foundry-tour.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-foundry-tour.js#L964): Parameter `label`: Parameter 'label' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-monaco.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-monaco.js#L25): Parameter `root`: Parameter 'root' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-monaco.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-monaco.js#L50): Parameter `editor`: Parameter 'editor' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-monaco.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-monaco.js#L50): Parameter `folds`: Parameter 'folds' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-monaco.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-monaco.js#L89): Parameter `root`: Parameter 'root' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-monaco.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-monaco.js#L89): Parameter `editor`: Parameter 'editor' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-monaco.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-monaco.js#L96): Parameter `root`: Parameter 'root' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-monaco.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-monaco.js#L96): Parameter `editor`: Parameter 'editor' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-monaco.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-monaco.js#L96): Parameter `folds`: Parameter 'folds' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-monaco.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-monaco.js#L122): Parameter `root`: Parameter 'root' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-monaco.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-monaco.js#L130): Parameter `root`: Parameter 'root' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-monaco.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-monaco.js#L130): Parameter `editor`: Parameter 'editor' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-monaco.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-monaco.js#L138): Parameter `root`: Parameter 'root' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-nav.js#L118): Parameter `name`: Parameter 'name' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-nav.js#L188): Parameter `links`: Parameter 'links' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-nav.js#L188): Parameter `currentPage`: Parameter 'currentPage' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-nav.js#L216): Parameter `currentPage`: Parameter 'currentPage' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-nav.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-nav.js#L500): Parameter `m`: Parameter 'm' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L12): Parameter `host`: Parameter 'host' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L18): Parameter `host`: Parameter 'host' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L18): Parameter `id`: Parameter 'id' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L26): Parameter `host`: Parameter 'host' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L39): Parameter `col`: Parameter 'col' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L45): Parameter `col`: Parameter 'col' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L51): Parameter `col`: Parameter 'col' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L64): Parameter `host`: Parameter 'host' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L64): Parameter `col`: Parameter 'col' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L112): Parameter `host`: Parameter 'host' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L112): Parameter `col`: Parameter 'col' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L129): Parameter `host`: Parameter 'host' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L129): Parameter `col`: Parameter 'col' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L129): Parameter `button`: Parameter 'button' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L129): Parameter `on`: Parameter 'on' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L140): Parameter `host`: Parameter 'host' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L140): Parameter `exceptId`: Parameter 'exceptId' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L150): Parameter `host`: Parameter 'host' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L150): Parameter `id`: Parameter 'id' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L150): Parameter `button`: Parameter 'button' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L159): Parameter `host`: Parameter 'host' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L159): Parameter `id`: Parameter 'id' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L159): Parameter `button`: Parameter 'button' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L187): Parameter `host`: Parameter 'host' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L218): Parameter `host`: Parameter 'host' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L232): Parameter `host`: Parameter 'host' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L232): Parameter `id`: Parameter 'id' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L232): Parameter `on`: Parameter 'on' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/templates/commons/catalog-refine-row.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\templates\commons\catalog-refine-row.js#L258): Parameter `host`: Parameter 'host' is missing a type annotation.

Evaluate the current context against this rule (use-typed-signatures):

## Judgment — `harness/catalog_generator/foundry_chrome.py`

### `do-not-invent-parallel-object-models` — Fail
- foundry_chrome.py:67 `STAGE_COLUMNS`: a hand-built list of the Discovery, Specification and Implementation stages with titles and keys, beside the kanban Stage the board serves and the chat bar's own `STAGE_ICONS` (harness/chat-ui/pane/hooks/chat-bar/stage-client.ts:8). Its docstring calls it "the one place a stage meets its board key", but it is one of three.

### `keep-classes-single-responsibility` — Fail
- foundry_chrome.py:345 `page_shell`: a 2050-line module of free functions emitting HTML strings for grids, tickets, tours and brands; no class owns any of it, so a change to one grid means reading the whole file.

## Judgment — `harness/catalog_generator/catalog_generator.py`

### `do-not-invent-parallel-object-models` — Fail
- catalog_generator.py:178 `UTILITY_REGISTRY`: another hand-kept registry of toolsets by import path (installer, diagnose, echo, handoff, repo) beside the installer's annotation scan, PracticeCatalogue and GuidanceCatalog; a new `@agent_toolset` utility is installed but never shown until someone edits this tuple.

### `use-exceptions-properly` — Fail
- catalog_generator.py:190 `owner`: builds the utility with `self.cls()` and on `TypeError` returns the class instead of an instance, so callers get two different kinds of object from one property, and a `TypeError` inside a constructor is mistaken for "needs arguments".

### `never-swallow-exceptions` — Fail
- catalog_generator.py:1253 `_add_guidance_pages`: any exception rendering a practice's context, guidance or examples page is logged at debug level and the page is skipped, so the generated catalog silently lacks pages and links to them break.

### `keep-operations-small-focused` — Fail
- catalog_generator.py:1646 `approach_page_body`: mixes reading files with building HTML; with 134 functions and classes in 2163 lines, this file holds the catalog model, page rendering, git citations and run-request YAML. Graph hits confirmed.

### `prefer-instance-operations` — Fail
- catalog_generator.py:628 `parse`: classmethods `parse`, `whole_file`, `comment_tag` (643, 647) and `normalize` (299) are string helpers parked on classes. Graph hits confirmed.

## Judgment — `harness/catalog_generator/project_approach.py`

### `use-intention-revealing-names` — Fail
- project_approach.py:30 `ApproachExampleSlot`: banned word "slot"; `with_slot` at 68 likewise.

Dismissed: the graph hits under `templates/commons/*.js` (161 parameter and unnamed-number hits) are browser scripts copied into the generated catalog; they break the same naming and literal rules but are one finding, not 200 — `provide-meaningful-context` and `use-intention-revealing-names` fail there as a class (e.g. catalog-foundry-tour.js:387 `r`, catalog-drawio.js:261 `1200`). `*_smoke.py` hits are manual smoke scripts.
