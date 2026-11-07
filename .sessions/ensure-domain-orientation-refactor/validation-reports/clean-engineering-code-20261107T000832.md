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

**Generated:** 2026-11-07 00:08:32 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 197
**Rules with graph hits:** 17
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

**Graph violations:** 36

- [X] **ERROR** **[graph rule]** - [harness/graph/_examples/input/src/account-credentials/account-credentials.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\_examples\input\src\account-credentials\account-credentials.ts#L183): Operation `authenticateAccount`: Operation 'authenticateAccount' is 25 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/_examples/input/src/customer/customer.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\_examples\input\src\customer\customer.ts#L205): Operation `read`: Operation 'read' is 23 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L30): Operation `App`: Operation 'App' is 342 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L115): Operation `load`: Operation 'load' is 37 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L176): Operation `applyOverlays`: Operation 'applyOverlays' is 22 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L234): Operation `applyFilter`: Operation 'applyFilter' is 29 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L500): Operation `keep`: Operation 'keep' is 24 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/app.test.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\app.test.tsx#L887): Operation `answer`: Operation 'answer' is 71 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/app.test.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\app.test.tsx#L1030): Operation `rowsFor`: Operation 'rowsFor' is 34 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/filter/FilterView.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\filter\FilterView.tsx#L20): Operation `FilterView`: Operation 'FilterView' is 98 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/graph/GraphView.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\graph\GraphView.tsx#L24): Operation `GraphView`: Operation 'GraphView' is 71 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/graph/query-progress.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\graph\query-progress.ts#L26): Operation `queryProgress`: Operation 'queryProgress' is 82 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/kind-mark.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\kind-mark.tsx#L1): Operation `kindLabel`: Operation 'kindLabel' is 61 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/kind-mark.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\kind-mark.tsx#L115): Operation `KindMark`: Operation 'KindMark' is 364 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L85): Operation `collectFoldMembers`: Operation 'collectFoldMembers' is 42 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L160): Operation `braceFolds`: Operation 'braceFolds' is 25 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L232): Operation `inlineCallLayout`: Operation 'inlineCallLayout' is 59 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L333): Operation `variableTypes`: Operation 'variableTypes' is 27 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L374): Operation `callCatalog`: Operation 'callCatalog' is 30 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L611): Operation `callsOnLine`: Operation 'callsOnLine' is 21 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L640): Operation `resolveCall`: Operation 'resolveCall' is 23 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L671): Operation `appendOperation`: Operation 'appendOperation' is 40 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L727): Operation `appendClass`: Operation 'appendClass' is 27 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/vite.config.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\vite.config.ts#L15): Operation `ping`: Operation 'ping' is 25 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/ddd_rule_eval_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\ddd_rule_eval_harness.py#L66): Operation `assert_ddd_example_pair`: Operation 'assert_ddd_example_pair' is 27 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L303): Operation `align_to_example_export`: Operation 'align_to_example_export' is 29 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L736): Operation `fact`: Operation 'fact' is 24 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L837): Operation `serialize`: Operation 'serialize' is 21 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L868): Operation `rule_rows`: Operation 'rule_rows' is 25 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L1190): Operation `load_working_copy`: Operation 'load_working_copy' is 30 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\rules.py#L13): Operation `attach_rules`: Operation 'attach_rules' is 57 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/schema_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\schema_rules.py#L167): Operation `ce_anchor_type`: Operation 'ce_anchor_type' is 23 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/schema_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\schema_rules.py#L222): Operation `rules_for_practice`: Operation 'rules_for_practice' is 23 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/stories_example_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\stories_example_harness.py#L58): Operation `violations_for_story_source`: Operation 'violations_for_story_source' is 28 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/stories_ts_folder_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\stories_ts_folder_harness.py#L49): Operation `assert_stories_folder_pair`: Operation 'assert_stories_folder_pair' is 23 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/working_copy.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\working_copy.py#L60): Operation `fill_working_copy`: Operation 'fill_working_copy' is 33 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

**Graph violations:** 5

- [X] **ERROR** **[graph rule]** - [harness/graph/_examples/input/src/account-credentials/account-credentials-node.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\_examples\input\src\account-credentials\account-credentials-node.ts#L68): Operation `destination`: Operation 'destination' is a staticmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L199): Operation `fact`: Operation 'fact' is a staticmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L736): Operation `fact`: Operation 'fact' is a staticmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L1143): Operation `of_practice`: Operation 'of_practice' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph_rules_collection.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph_rules_collection.py#L42): Operation `prose_only`: Operation 'prose_only' is a classmethod; prefer an instance operation.

Evaluate the current context against this rule (prefer-instance-operations):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L30): Operation `App`: Operation 'App' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L434): Operation `readSavedOverlays`: Operation 'readSavedOverlays' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/SourceView.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\SourceView.tsx#L131): Operation `copyCorrectPrompt`: Operation 'copyCorrectPrompt' delegates to both I/O and domain helpers; give it one job.
- [X] **ERROR** **[graph rule]** - [harness/graph/ce_rule_eval_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\ce_rule_eval_harness.py#L43): Operation `practice_from_class_text`: Operation 'practice_from_class_text' mixes I/O-style calls with domain calculation; split responsibilities.

Evaluate the current context against this rule (keep-operations-single-responsibility):

### `simplify-control-flow`

Handle the failing or empty cases first and return. Keep the main path flat. Do not nest more than three levels — deeper than that you cannot tell which conditions hold on a given line without reading back up, and that is where the unhandled branch hides.

**Graph violations:** 5

- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L30): Operation `App`: Operation 'App' nests control flow 4 levels deep (max 3).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L75): Operation `tick`: Operation 'tick' nests control flow 4 levels deep (max 3).
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L303): Operation `align_to_example_export`: Operation 'align_to_example_export' nests control flow 4 levels deep (max 3).
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L787): Operation `populate`: Operation 'populate' nests control flow 4 levels deep (max 3).
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L1035): Operation `direct_parent`: Operation 'direct_parent' nests control flow 4 levels deep (max 3).

Evaluate the current context against this rule (simplify-control-flow):

### `errors-out-of-existence`

For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure.

**Graph violations:** 8

- [X] **ERROR** **[graph rule]** - [harness/graph/bdd_example_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\bdd_example_harness.py#L39): Operation `assert_bdd_source_pair`: Operation 'assert_bdd_source_pair' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [harness/graph/ce_module_example_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\ce_module_example_harness.py#L21): Operation `assert_module_example_pair`: Operation 'assert_module_example_pair' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [harness/graph/ce_rule_eval_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\ce_rule_eval_harness.py#L19): Operation `ce_rule_by_slug`: Operation 'ce_rule_by_slug' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [harness/graph/ddd_rule_eval_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\ddd_rule_eval_harness.py#L17): Operation `ddd_rule_by_slug`: Operation 'ddd_rule_by_slug' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [harness/graph/ddd_rule_eval_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\ddd_rule_eval_harness.py#L66): Operation `assert_ddd_example_pair`: Operation 'assert_ddd_example_pair' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph_spec.py#L64): Operation `tree_named`: Operation 'tree_named' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [harness/graph/stories_example_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\stories_example_harness.py#L13): Operation `stories_rule_by_slug`: Operation 'stories_rule_by_slug' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [harness/graph/stories_example_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\stories_example_harness.py#L88): Operation `assert_stories_ts_pair`: Operation 'assert_stories_ts_pair' raises on an empty or missing value; return a quiet result instead.

Evaluate the current context against this rule (errors-out-of-existence):

### `no-prototype-swapping`

An object keeps the class it was built as. Do not change it afterwards with `Object.setPrototypeOf`, `__proto__ =`, or `__class__ =`. When a subclass needs to make its own instances, give the base an overridable factory (`blank()`) or build the right class directly. A swapped object skips its constructor, so fields the subclass sets up are missing and nothing tells you.

Evaluate the current context against this rule (no-prototype-swapping):

### `use-intention-revealing-names`

Name each class, property, operation, and parameter so it answers why it exists. Do not abbreviate.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L532): Parameter `id`: Parameter 'id' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L675): Parameter `value`: Parameter 'value' does not reveal intent.

Evaluate the current context against this rule (use-intention-revealing-names):

### `use-consistent-naming`

Use one word per concept. Pick one verb and use it everywhere (`fetch_`, not a mix of `fetch_`, `get_`, and `retrieve_`). Two words for one concept is how the same logic gets written twice — nobody searching for `fetch_` finds the `retrieve_` that already does the job.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L222): OoadClass `Source`: Operation 'startLine' uses camelCase while other operations on 'Source' use the other convention.

Evaluate the current context against this rule (use-consistent-naming):

### `provide-meaningful-context`

Give a number or literal a name that says why it is there (`SECONDS_PER_DAY`, not `86400`). Do not number variables (`item1`).

**Graph violations:** 6

- [X] **ERROR** **[graph rule]** - [harness/graph/app/app.test.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\app.test.tsx#L887): Operation `answer`: Operation 'answer' uses the unnamed number 7.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/graph/GraphView.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\graph\GraphView.tsx#L18): Operation `elapsedLabel`: Operation 'elapsedLabel' uses the unnamed number 60.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/graph/query-progress.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\graph\query-progress.ts#L26): Operation `queryProgress`: Operation 'queryProgress' uses the unnamed number 120.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/SourceView.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\SourceView.tsx#L266): Operation `sourceHeight`: Operation 'sourceHeight' uses the unnamed number 16.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/vite.config.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\vite.config.ts#L15): Operation `ping`: Operation 'ping' uses the unnamed number 5173.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L736): Operation `fact`: Operation 'fact' uses the unnamed number 7.

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

Evaluate the current context against this rule (never-swallow-exceptions):

### `limit-comments`

write comment in operations and properties only when the signature cannot say a constraint or explain why the code behaves the way it does. Do not narrate a line that already names what it does.

Evaluate the current context against this rule (limit-comments):

### `avoid-vague-parameter-names`

Do not name parameters `data`, `options`, `info`, or other placeholders that could mean anything. A vague name hides what the caller must supply and what the operation does with it.

**Graph violations:** 6

- [X] **ERROR** **[graph rule]** - [harness/graph/_examples/input/src/account-credentials/account-credentials-client.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\_examples\input\src\account-credentials\account-credentials-client.tsx#L161): Operation `postOperation`: Parameter 'payload' in 'postOperation' is vague.
- [X] **ERROR** **[graph rule]** - [harness/graph/_examples/input/src/account-credentials/account-credentials-client.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\_examples\input\src\account-credentials\account-credentials-client.tsx#L161): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L232): Operation `inlineCallLayout`: Parameter 'options' in 'inlineCallLayout' is vague.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L232): Parameter `options`: Parameter 'options' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/graph/node_data.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\node_data.py#L22): Operation `encode_node_data`: Parameter 'data' in 'encode_node_data' is vague.
- [X] **ERROR** **[graph rule]** - [harness/graph/node_data.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\node_data.py#L22): Parameter `data`: Parameter 'data' is vague. Use a domain-specific name.

Evaluate the current context against this rule (avoid-vague-parameter-names):

### `deep-module`

Keep most classes private (at most **40%** public) in each first-class module. A first-class module is a folder that owns `.context/module-context.md`. Nested folders that also own that file are separate modules — respect them. Nested folders that do not own it roll up to the nearest enclosing module-context folder, or to the folder you are querying if none sits in between. Count classes, not operations: a public method on a hidden class is not a second seam. Every public class is a signature you cannot change without editing every caller, so public classes are much harder to refactor than private ones.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/graph/_examples/input/src/account-credentials](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\_examples\input\src\account-credentials#L1): Module `account-credentials`: Module 'account-credentials' splits into many tiny classes (10); prefer a deep module with a small public surface.

Evaluate the current context against this rule (deep-module):

### `keep-classes-single-responsibility`

Give each class one reason to change.

**Graph violations:** 12

- [X] **ERROR** **[graph rule]** - [harness/graph/_examples/input/src/account-credentials/account-credentials-client.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\_examples\input\src\account-credentials\account-credentials-client.tsx#L24): OoadClass `AccountCredentialsClient`: Class 'AccountCredentialsClient' exposes 19 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/graph/_examples/input/src/account-credentials/account-credentials.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\_examples\input\src\account-credentials\account-credentials.ts#L33): OoadClass `AccountCredentials`: Class 'AccountCredentials' exposes 14 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/graph/_examples/input/src/customer/customer.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\_examples\input\src\customer\customer.ts#L108): OoadClass `CustomerRepository`: Class 'CustomerRepository' exposes 14 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/graph/_examples/input/tests/onboard-a-customer/authenticate-user/examples/account-credentials.examples.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\_examples\input\tests\onboard-a-customer\authenticate-user\examples\account-credentials.examples.ts#L1): OoadClass `_module`: Class '_module' exposes 20 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L1): OoadClass `_module`: Class '_module' exposes 28 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/app.test.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\app.test.tsx#L1): OoadClass `_module`: Class '_module' exposes 13 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/SourceView.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\SourceView.tsx#L1): OoadClass `_module`: Class '_module' exposes 11 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L1): OoadClass `_module`: Class '_module' exposes 27 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L432): OoadClass `Filter`: Class 'Filter' exposes 11 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L898): OoadClass `PracticeGraph`: Class 'PracticeGraph' exposes 12 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L1129): OoadClass `Graph`: Class 'Graph' exposes 17 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph_spec.py#L1): OoadClass `_module`: Class '_module' exposes 15 public operations (budget ~9). Split responsibilities.

Evaluate the current context against this rule (keep-classes-single-responsibility):

### `limit-operation-parameters`

Have callers pass intent, not setup. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

**Graph violations:** 20

- [X] **ERROR** **[graph rule]** - [harness/graph/_examples/input/src/account-credentials/account-credentials-client.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\_examples\input\src\account-credentials\account-credentials-client.tsx#L161): Operation `postOperation`: Operation 'postOperation' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/_examples/input/src/customer/customer.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\_examples\input\src\customer\customer.ts#L240): Operation `exception`: Operation 'exception' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L410): Operation `overlayFilterRefresh`: Operation 'overlayFilterRefresh' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L500): Operation `keep`: Operation 'keep' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/SourceView.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\SourceView.tsx#L281): Operation `violationLineDecorations`: Operation 'violationLineDecorations' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L232): Operation `inlineCallLayout`: Operation 'inlineCallLayout' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L611): Operation `callsOnLine`: Operation 'callsOnLine' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L640): Operation `resolveCall`: Operation 'resolveCall' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L671): Operation `appendOperation`: Operation 'appendOperation' takes 12 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L727): Operation `appendClass`: Operation 'appendClass' takes 10 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/bdd_example_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\bdd_example_harness.py#L39): Operation `assert_bdd_source_pair`: Operation 'assert_bdd_source_pair' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/ce_rule_eval_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\ce_rule_eval_harness.py#L78): Operation `assert_rule_pair`: Operation 'assert_rule_pair' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/ddd_rule_eval_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\ddd_rule_eval_harness.py#L52): Operation `violations_for_ddd_rule`: Operation 'violations_for_ddd_rule' takes 6 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/ddd_rule_eval_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\ddd_rule_eval_harness.py#L66): Operation `assert_ddd_example_pair`: Operation 'assert_ddd_example_pair' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L1190): Operation `load_working_copy`: Operation 'load_working_copy' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L1224): Operation `load_files`: Operation 'load_files' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/schema_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\schema_rules.py#L288): Operation `qualified_rule_label`: Operation 'qualified_rule_label' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/stories_example_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\stories_example_harness.py#L58): Operation `violations_for_story_source`: Operation 'violations_for_story_source' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/stories_example_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\stories_example_harness.py#L88): Operation `assert_stories_ts_pair`: Operation 'assert_stories_ts_pair' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/stories_ts_folder_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\stories_ts_folder_harness.py#L49): Operation `assert_stories_folder_pair`: Operation 'assert_stories_folder_pair' takes 4 parameters (maximum 3, excluding self).

Evaluate the current context against this rule (limit-operation-parameters):

### `missing-module-context`

**Graph violations:** 55

- [X] **ERROR** **[graph rule]** - [harness/graph/app_smoke_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app_smoke_spec.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/bdd_example_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\bdd_example_harness.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/bdd_examples_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\bdd_examples_spec.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/bdd_invokes_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\bdd_invokes_spec.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/bound_node.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\bound_node.py#L19): OoadClass `BoundChildren`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/bound_node.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\bound_node.py#L53): OoadClass `BoundNode`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/c_family_parse_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\c_family_parse_spec.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/ce_module_example_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\ce_module_example_harness.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/ce_rule_eval_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\ce_rule_eval_harness.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/ce_rules_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\ce_rules_spec.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/ddd_rule_eval_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\ddd_rule_eval_harness.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/drawio_rules_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\drawio_rules_spec.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/explorer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\explorer.py#L15): OoadClass `GraphLoaded`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/explorer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\explorer.py#L27): OoadClass `GraphSaved`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/explorer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\explorer.py#L39): OoadClass `RuleHit`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/explorer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\explorer.py#L73): OoadClass `ExplorerEntry`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/explorer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\explorer.py#L102): OoadClass `RuleCategory`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/explorer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\explorer.py#L118): OoadClass `RuleEntry`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/explorer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\explorer.py#L150): OoadClass `Overlay`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/explorer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\explorer.py#L162): OoadClass `FilteredNode`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/explorer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\explorer.py#L206): OoadClass `Member`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/explorer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\explorer.py#L255): OoadClass `NodeSource`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L116): OoadClass `GraphFailure`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L178): OoadClass `EdgeType`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L185): OoadClass `Edge`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L213): OoadClass `Call`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L222): OoadClass `Source`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L432): OoadClass `Filter`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L650): OoadClass `Node`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L898): OoadClass `PracticeGraph`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L1090): OoadClass `Inventory`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L1114): OoadClass `AppliedOverlays`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L1129): OoadClass `Graph`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph_json_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph_json_spec.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph_rules_collection.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph_rules_collection.py#L11): OoadClass `GraphRule`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph_rules_collection.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph_rules_collection.py#L71): OoadClass `GraphRulesCollection`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph_spec.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/guidance_prose_index.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\guidance_prose_index.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/language_for_node.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\language_for_node.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/node_data.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\node_data.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/node_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\node_rules.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/practice_rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\practice_rule.py#L11): OoadClass `PracticeGraphRule`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/practice_rules_registry.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\practice_rules_registry.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/rule_category_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\rule_category_spec.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/rule_context.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\rule_context.py#L11): OoadClass `RuleCheckContext`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\rules.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/schema_edges.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\schema_edges.py#L87): OoadClass `SchemaField`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/schema_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\schema_rules.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/skipped_folders.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\skipped_folders.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/stories_example_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\stories_example_harness.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/stories_rules_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\stories_rules_spec.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/stories_ts_folder_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\stories_ts_folder_harness.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/story_scenario_count_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\story_scenario_count_spec.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/working_copy.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\working_copy.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/working_copy_scan_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\working_copy_scan_spec.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.

Evaluate the current context against this rule (missing-module-context):

### `one-way-deps`

Make dependencies flow in one direction without cycles. A cycle prevents either module from changing or being tested independently.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/graph/_examples/input/src/account-credentials](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\_examples\input\src\account-credentials#L1): Module `account-credentials`: Circular import between 'account-credentials' and 'customer' breaks one-way dependencies.

Evaluate the current context against this rule (one-way-deps):

### `state-change-returns-record-or-named-failure`

When an operation coordinates a state change that cannot be one property assignment, return the resulting record or a failure named after the rejected rule. Decide at code fidelity whether that failure is a result type or domain exception, because callers need one explicit outcome contract.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/graph/_examples/input/src/account-credentials/account-credentials.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\_examples\input\src\account-credentials\account-credentials.ts#L229): Operation `storeCustomerId`: Operation 'storeCustomerId' mutates state but does not return the record or a named failure.

Evaluate the current context against this rule (state-change-returns-record-or-named-failure):

### `use-explicit-dependencies`

Pass every collaborator through the constructor. Do not reach for a global or construct a collaborator inside construction. A collaborator the class fetches or builds itself cannot be swapped, so the class can only ever run against that one implementation.

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [harness/graph/bound_node.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\bound_node.py#L53): OoadClass `BoundNode`: Class 'BoundNode' constructs 'Graph' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L898): OoadClass `PracticeGraph`: Class 'PracticeGraph' constructs 'Node' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L1129): OoadClass `Graph`: Class 'Graph' constructs 'Filter' inside its constructor.

Evaluate the current context against this rule (use-explicit-dependencies):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 31

- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L115): Parameter `next`: Parameter 'next' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L115): Parameter `force`: Parameter 'force' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L234): Parameter `practices`: Parameter 'practices' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L500): Parameter `violationsOnly`: Parameter 'violationsOnly' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/graph/GraphClient.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\graph\GraphClient.ts#L11): Parameter `title`: Parameter 'title' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L206): Parameter `quote`: Parameter 'quote' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L727): Parameter `again`: Parameter 'again' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/bdd_example_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\bdd_example_harness.py#L22): Parameter `rule`: Parameter 'rule' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/bound_node.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\bound_node.py#L28): Parameter `child`: Parameter 'child' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/bound_node.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\bound_node.py#L36): Parameter `child`: Parameter 'child' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/ce_rule_eval_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\ce_rule_eval_harness.py#L60): Parameter `rule`: Parameter 'rule' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/ddd_rule_eval_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\ddd_rule_eval_harness.py#L52): Parameter `rule`: Parameter 'rule' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/explorer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\explorer.py#L49): Parameter `hit`: Parameter 'hit' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L568): Parameter `request`: Parameter 'request' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L675): Parameter `value`: Parameter 'value' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L679): Parameter `default`: Parameter 'default' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L762): Parameter `row`: Parameter 'row' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L1010): Parameter `fact`: Parameter 'fact' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph_rules_collection.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph_rules_collection.py#L49): Parameter `source`: Parameter 'source' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/graph/language_for_node.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\language_for_node.py#L8): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/node_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\node_rules.py#L11): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/practice_rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\practice_rule.py#L15): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/practice_rules_registry.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\practice_rules_registry.py#L79): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/rule_context.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\rule_context.py#L18): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/rule_context.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\rule_context.py#L26): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/rule_context.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\rule_context.py#L33): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/rule_context.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\rule_context.py#L37): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/rule_context.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\rule_context.py#L40): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\rules.py#L13): Parameter `practice`: Parameter 'practice' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/schema_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\schema_rules.py#L271): Parameter `practice_graph`: Parameter 'practice_graph' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/stories_example_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\stories_example_harness.py#L58): Parameter `rule`: Parameter 'rule' is missing a type annotation.

Evaluate the current context against this rule (use-typed-signatures):

## Judgment — `harness/graph/rules.py`

### `hold-state-on-the-object-not-in-parameters` — Fail
- rules.py:13 `attach_rules`: a free function handed a PracticeGraph that reads its graph, overlays, nodes and source root, and writes violations onto its nodes; it is PracticeGraph's own operation living outside it. Graph hit (57 lines, untyped `practice`) confirmed.

### `hide-inner-details` — Fail
- rules.py:26 `schema_slugs_for`: reads and tests `node._rules` (lines 26, 37, 39, 55), the Node's private field, from outside the class, and creates it with `attach_node_rules` when missing.

### `eliminate-duplication` — Fail
- rules.py:39 `record`: records each violation on the node with `node._rules.record_violation`, then line 67 hands the same triples to `practice.apply_rules`, which looks every node up again and records the violation a second time unless it finds the message already there (harness/graph/graph.py:1066). Two writers for one fact; the de-duplication in `apply_rules` is the only thing hiding the double count.

### `do-not-invent-parallel-object-models` — Fail
- rules.py:23 `rows_by_slug`: violations travel as `[slug, node_id, message]` string lists and are unpacked positionally with padding in graph.py:1069 `(row + [""] * 3)[:3]` — a fourth violation shape beside the graph-reader dict, RuleHit and the kanban Violation.

## Judgment — `harness/graph/graph.py`

### `use-intention-revealing-names` — Fail
- graph.py:868 `rule_rows`: uses the banned word "rows" (.claude/rules/writing-guidelines.md) and returns `RuleEntry` objects; `fact(row: Tuple)` at 199 and 736 and `apply_rules(..., tuples)` at 1066 name positional tuples instead of the facts they carry.
- graph.py:919 `bind_rule`: banned word "binding"; it registers which node types a rule applies to.

### `prefer-instance-operations` — Fail
- graph.py:736 `fact`: staticmethod that parses a positional 7-tuple padded with `[""] * 7`; graph hits at 199 and 1143 `of_practice` confirmed. Annotated `Tuple` but concatenated with a list, which raises `TypeError` if a real tuple is ever passed.

### `keep-classes-single-responsibility` — Fail
- graph.py:1129 `Graph`: 17 public operations (loading files, working copy, overlays, filtering, saving, progress). Graph hits on Filter (432) and PracticeGraph (898) confirmed.

## Judgment — `harness/graph/app/App.tsx`

### `keep-operations-small-focused` — Fail
- App.tsx:30 `App`: a 342-line component holding loading, overlays, filtering and source view state; graph/app/kind-mark.tsx:115 `KindMark` is 364 lines and source/call-expansion.ts has nine operations over 20 lines. Graph hits confirmed.

## Judgment — `harness/graph/graph_rules_collection.py`

### `missing-module-context` — Fail
- graph_rules_collection.py:1 `graph`: harness/graph/.context holds defects.md and three design notes but no module-context.md. Graph hit confirmed.

Dismissed: `errors-out-of-existence` hits on the `*_harness.py` example harnesses (test support that should raise); every hit under `_examples/` and `app.test.tsx`; `provide-meaningful-context` for 5173 in vite.config.ts (the Vite port).
