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

**Generated:** 2026-11-07 03:58:05 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 32
**Rules with graph hits:** 7
**AI rules in scope:** 27

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

### `model-modules-follow-the-partition`

Use the module names and boundaries established by the partition artifact as the model's top-level modules. Change the partition before moving a model boundary, because otherwise the two artifacts describe different designs.

Evaluate the current context against this rule (model-modules-follow-the-partition):

### `class-not-property-instance-or-subtype`

Before you write a new class, check property, instance, then subtype. Write a class only when none of those three fit. Multi-step work inside one operation usually belongs in private fields on the class that owns the operation, not in another class. Every new class is another type to construct, pass around, and keep in step with the rest; a property or subtype reuses one that already works.

Evaluate the current context against this rule (class-not-property-instance-or-subtype):

### `keep-classes-single-responsibility`

Give each class one reason to change.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/scanners/_drawio_base.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\drawio\scanners\_drawio_base.py#L33): OoadClass `DrawioScanner`: Class 'DrawioScanner' exposes 11 public operations (budget ~9). Split responsibilities.

Evaluate the current context against this rule (keep-classes-single-responsibility):

### `shape-classes-around-resources`

Model a class around the concept that owns the state and the rule, not a doer, handler, or service that acts on a data bag. A Payment has transactions, a source, and a destination, and it moves the money; it is not a `PaymentService` that takes a `PaymentData` object. A service-plus-bag pair splits the rule from its memory, so every change has to be found in two types and the bag cannot enforce anything. Two resources may collaborate — a model that loads a Module is not a service-plus-bag split.

Evaluate the current context against this rule (shape-classes-around-resources):

### `put-logic-on-the-owning-resource`

Put logic on the object that owns the invariant. Do not infer ownership from a route name, Story actor, or Given subject: `client.accounts[id].transactions.last.validate()`, not `client.validateLastTransactionForPrimaryAccount()`. Logic placed away from its state gives two objects authority to change the same rule.

Evaluate the current context against this rule (put-logic-on-the-owning-resource):

### `hide-inner-details`

Expose behavior through named operations. Do not let callers see how the class stores or arranges its data — once they read the storage directly it becomes a public contract you cannot change. Private fields on the same class hide implementation; you do not need a second class for that.

Evaluate the current context against this rule (hide-inner-details):

### `use-property-not-accessor`

Use a named property for stored or derived state. A derived property recalculates from state and collaborators the object already holds, takes no owner or state parameters, and looks like a field to callers through the language's property mechanism. Use an operation only when behavior coordinates several values, collaborators, or lifecycle steps and cannot be represented truthfully as a property. Callers should not need `getX`, `setX`, or storage knowledge. Read-only to callers can mean return a copy or immutable view from a property — it does not require a frozen class or a second type to hold build steps.

Evaluate the current context against this rule (use-property-not-accessor):

### `prefer-class-operations`

Put factory, lifecycle, and helpers used from one class on that class. Do not export them as module-level functions — a free function holds no state, so it takes the object as a parameter and reaches into it to do the work. A file of hanging functions is the same miss: those operations belong on a type, not on the package.

Evaluate the current context against this rule (prefer-class-operations):

### `use-explicit-dependencies`

Pass every collaborator through the constructor. Do not reach for a global or construct a collaborator inside construction. A collaborator the class fetches or builds itself cannot be swapped, so the class can only ever run against that one implementation.

Evaluate the current context against this rule (use-explicit-dependencies):

### `external-system-interface-is-one-way`

Let a domain wrapper or collaborator depend on the named external-system contract. Keep the external type independent of domain wrappers and domain types, because a reverse dependency makes the external boundary depend on one caller's model.

Evaluate the current context against this rule (external-system-interface-is-one-way):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/scanners/_drawio_base.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\drawio\scanners\_drawio_base.py#L153): Operation `run_main`: Operation 'run_main' mixes I/O-style calls with domain calculation; split responsibilities.

Evaluate the current context against this rule (keep-operations-single-responsibility):

### `limit-operation-parameters`

Have callers pass intent, not setup. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/scanners/_drawio_base.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\drawio\scanners\_drawio_base.py#L97): Operation `violation`: Operation 'violation' takes 4 parameters (maximum 3, excluding self).

Evaluate the current context against this rule (limit-operation-parameters):

### `avoid-vague-parameter-names`

Do not name parameters `data`, `options`, `info`, or other placeholders that could mean anything. A vague name hides what the caller must supply and what the operation does with it.

Evaluate the current context against this rule (avoid-vague-parameter-names):

### `errors-out-of-existence`

For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure.

Evaluate the current context against this rule (errors-out-of-existence):

### `state-change-returns-record-or-named-failure`

When an operation coordinates a state change that cannot be one property assignment, return the resulting record or a failure named after the rejected rule. Decide at code fidelity whether that failure is a result type or domain exception, because callers need one explicit outcome contract.

Evaluate the current context against this rule (state-change-returns-record-or-named-failure):

### `domain-exception-carries-context`

Use a typed exception for a broken aggregate or repository operation. One exception type may cover that aggregate's operations when it carries the failed operation, the domain object or input already in hand, the user-facing message, and the underlying cause; do not return bare strings or untyped error objects because callers cannot handle them safely..

Evaluate the current context against this rule (domain-exception-carries-context):

### `limit-comments`

write comment in operations and properties only when the signature cannot say a constraint or explain why the code behaves the way it does. Do not narrate a line that already names what it does.

Evaluate the current context against this rule (limit-comments):

### `write-invariants`

Name a rule the object itself must keep true whenever it acts — a must, never, always, before, or after about its own state. Write one a caller can break by using the object wrong. Do not restate a type, a name, or a single operation’s happy path.

Evaluate the current context against this rule (write-invariants):

### `write-interactions`

Collaborate when this object cannot finish its job from its own state — another object owns the data or the next act. Ask that object to do the work so each keeps its own invariants; do not reach into its internals or steal its job. Ask through a named public operation on a collaborator you hold or are given. Do not point at a type, and do not invent a third object to mediate a conversation two objects can have.

Evaluate the current context against this rule (write-interactions):

### `no-redundant-relationship-paths`

Before you add an association, walk the paths already in the cluster. Each real participant gets one canonical link — not parallel wires through types that collapse to the same thing (`Client` and `ClientIdentity`, or `OfferChannel` on **Offer** and again on an event the offer just emitted). In-process payloads reach a participant through the aggregate that owns the act; outbound events carry the identity or routing fact downstream systems need, not a duplicate of context the publisher already holds.

Evaluate the current context against this rule (no-redundant-relationship-paths):

### `use-intention-revealing-names`

Name each class, property, operation, and parameter so it answers why it exists. Do not abbreviate.

Evaluate the current context against this rule (use-intention-revealing-names):

### `use-consistent-naming`

Use one word per concept. Pick one verb and use it everywhere (`fetch_`, not a mix of `fetch_`, `get_`, and `retrieve_`). Two words for one concept is how the same logic gets written twice — nobody searching for `fetch_` finds the `retrieve_` that already does the job.

Evaluate the current context against this rule (use-consistent-naming):

### `eliminate-duplication`

Give repeated logic one canonical function. Every copy is another place the fix has to be repeated, and the copy you miss is the bug.

Evaluate the current context against this rule (eliminate-duplication):

### `one-canonical-model-document`

Keep all modules for one model artifact in one canonical model document. Link diagrams and code to it rather than restating its classes in another design document, because parallel models become inconsistent.

Evaluate the current context against this rule (one-canonical-model-document):

### `keep-operations-small-focused`

Keep each operation short enough to read as one thought — under 20 statements. A multi-line call, list, or string initializer is one statement. When it grows, extract a private helper whose name says why that slice exists.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/scanners/class_title_no_markdown_bold_scanner.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\drawio\scanners\class_title_no_markdown_bold_scanner.py#L14): Operation `scan_page`: Operation 'scan_page' is 22 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/scanners/stereotype_above_class_name_scanner.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\drawio\scanners\stereotype_above_class_name_scanner.py#L17): Operation `scan_page`: Operation 'scan_page' is 23 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `missing-module-context`

**Graph violations:** 14

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/scanners/_drawio_base.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\drawio\scanners\_drawio_base.py#L21): OoadClass `DrawioViolation`: Module folder 'scanners' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/scanners/_drawio_base.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\drawio\scanners\_drawio_base.py#L33): OoadClass `DrawioScanner`: Module folder 'scanners' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/scanners/base_above_derived_scanner.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\drawio\scanners\base_above_derived_scanner.py#L9): OoadClass `BaseAboveDerivedScanner`: Module folder 'scanners' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/scanners/class_title_no_markdown_bold_scanner.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\drawio\scanners\class_title_no_markdown_bold_scanner.py#L11): OoadClass `ClassTitleNoMarkdownBoldScanner`: Module folder 'scanners' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/scanners/class_title_no_markdown_bold_scanner_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\drawio\scanners\class_title_no_markdown_bold_scanner_spec.py#L53): OoadClass `_ScannerExample`: Module folder 'scanners' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/scanners/distinct_anchor_points_scanner.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\drawio\scanners\distinct_anchor_points_scanner.py#L9): OoadClass `DistinctAnchorPointsScanner`: Module folder 'scanners' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/scanners/edges_approach_perpendicular_scanner.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\drawio\scanners\edges_approach_perpendicular_scanner.py#L6): OoadClass `EdgesApproachPerpendicularScanner`: Module folder 'scanners' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/scanners/edges_do_not_cross_classes_scanner.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\drawio\scanners\edges_do_not_cross_classes_scanner.py#L9): OoadClass `EdgesDoNotCrossClassesScanner`: Module folder 'scanners' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/scanners/edges_do_not_cross_other_edges_scanner.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\drawio\scanners\edges_do_not_cross_other_edges_scanner.py#L6): OoadClass `EdgesDoNotCrossOtherEdgesScanner`: Module folder 'scanners' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/scanners/edges_do_not_overlap_edges_scanner.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\drawio\scanners\edges_do_not_overlap_edges_scanner.py#L9): OoadClass `EdgesDoNotOverlapEdgesScanner`: Module folder 'scanners' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/scanners/leaf_nodes_not_in_horizontal_row_scanner.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\drawio\scanners\leaf_nodes_not_in_horizontal_row_scanner.py#L10): OoadClass `LeafNodesNotInHorizontalRowScanner`: Module folder 'scanners' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/scanners/prefer_short_routes_scanner.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\drawio\scanners\prefer_short_routes_scanner.py#L9): OoadClass `PreferShortRoutesScanner`: Module folder 'scanners' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/scanners/stereotype_above_class_name_scanner.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\drawio\scanners\stereotype_above_class_name_scanner.py#L14): OoadClass `StereotypeAboveClassNameScanner`: Module folder 'scanners' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/scanners/stereotype_above_class_name_scanner_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\drawio\scanners\stereotype_above_class_name_scanner_spec.py#L54): OoadClass `_ScannerExample`: Module folder 'scanners' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.

Evaluate the current context against this rule (missing-module-context):

### `provide-meaningful-context`

Give a number or literal a name that says why it is there (`SECONDS_PER_DAY`, not `86400`). Do not number variables (`item1`).

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/scanners/class_title_no_markdown_bold_scanner.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\drawio\scanners\class_title_no_markdown_bold_scanner.py#L14): Operation `scan_page`: Operation 'scan_page' uses the unnamed number 80.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/scanners/stereotype_above_class_name_scanner.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\drawio\scanners\stereotype_above_class_name_scanner.py#L17): Operation `scan_page`: Operation 'scan_page' uses the unnamed number 80.

Evaluate the current context against this rule (provide-meaningful-context):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 11

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/scanners/_drawio_base.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\drawio\scanners\_drawio_base.py#L94): Parameter `page_root`: Parameter 'page_root' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/scanners/base_above_derived_scanner.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\drawio\scanners\base_above_derived_scanner.py#L12): Parameter `page_root`: Parameter 'page_root' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/scanners/class_title_no_markdown_bold_scanner.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\drawio\scanners\class_title_no_markdown_bold_scanner.py#L14): Parameter `page_root`: Parameter 'page_root' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/scanners/distinct_anchor_points_scanner.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\drawio\scanners\distinct_anchor_points_scanner.py#L12): Parameter `page_root`: Parameter 'page_root' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/scanners/edges_approach_perpendicular_scanner.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\drawio\scanners\edges_approach_perpendicular_scanner.py#L9): Parameter `page_root`: Parameter 'page_root' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/scanners/edges_do_not_cross_classes_scanner.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\drawio\scanners\edges_do_not_cross_classes_scanner.py#L12): Parameter `page_root`: Parameter 'page_root' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/scanners/edges_do_not_cross_other_edges_scanner.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\drawio\scanners\edges_do_not_cross_other_edges_scanner.py#L9): Parameter `page_root`: Parameter 'page_root' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/scanners/edges_do_not_overlap_edges_scanner.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\drawio\scanners\edges_do_not_overlap_edges_scanner.py#L12): Parameter `page_root`: Parameter 'page_root' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/scanners/leaf_nodes_not_in_horizontal_row_scanner.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\drawio\scanners\leaf_nodes_not_in_horizontal_row_scanner.py#L13): Parameter `page_root`: Parameter 'page_root' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/scanners/prefer_short_routes_scanner.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\drawio\scanners\prefer_short_routes_scanner.py#L12): Parameter `page_root`: Parameter 'page_root' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/scanners/stereotype_above_class_name_scanner.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\drawio\scanners\stereotype_above_class_name_scanner.py#L17): Parameter `page_root`: Parameter 'page_root' is missing a type annotation.

Evaluate the current context against this rule (use-typed-signatures):

---

# Judgment (model fidelity, `model/drawio/scanners/`)

**Graph hits dismissed:** `missing-module-context` (14): `scanners/` rolls up into `drawio/.context/` and the Clean Engineering card; two hits are on `*_spec.py` example classes.

**Graph hits confirmed:** `keep-classes-single-responsibility` on `DrawioScanner` (the hit counts 11 public operations; the class has 125 methods, see below); `keep-operations-single-responsibility` on `run_main`; `limit-operation-parameters` on `violation`; `keep-operations-small-focused` and `provide-meaningful-context` (the 80) on the two `scan_page` hits; `use-typed-signatures` on every `scan_page(self, page_root)` (11, low).

## Judgment — `cdd_guidance/practices/clean_engineering/model/drawio/scanners/_drawio_base.py`

### `keep-classes-single-responsibility` — Fail
- _drawio_base.py:33 `DrawioScanner` is 1,607 lines and 125 methods in one class: scanner discovery and loading, file filtering, the CLI (`run_main`), drawio XML reading, geometry and segment intersection maths, every layout check (`_check_prefer_short_routes`, `_check_edges_crossing_classes`, `_check_edges_approach_perpendicular`, `_check_leaf_nodes_horizontal_row`, `_inheritance_flow_violations`, ...), a drawio writer (`_create_class_cell`, `_update_class_cell`, `_delete_class_and_edges`, `_add_page`, `_save_drawio`), and a sync from a drawio page back into a markdown model (`_sync_page_to_model`, `_parse_concepts_from_md`, `_concept_to_md`, `_rewrite_model_section`).

### `put-logic-on-the-owning-resource` — Fail
- _drawio_base.py:599 every rule's check lives on the base; the scanner subclasses are 10-to-40-line shells that call one `_check_*` method and wrap its tuples (`edges_do_not_cross_other_edges_scanner.py:9`, `base_above_derived_scanner.py:12`). Each scanner should own its rule; as written, a change to one rule edits the shared base that every other scanner loads.

### `do-not-invent-parallel-object-models` — Fail
- _drawio_base.py:1350 `_sync_page_to_model`, `_read_classes_from_page`, `_parse_concepts_from_md`, `_concept_to_md`, and `_rewrite_model_section` are a second drawio reader and a second markdown class-model parser and writer working on untyped "concept" dicts, beside `DrawIOCleanEngineeringModel` and `MarkdownCleanEngineeringModel`. Nothing outside this file calls them (no production caller, no spec).
- _drawio_base.py:931 `_build_class_html`, `_parse_class_html` (:957), `_create_class_cell` (:998), and `_classify_edge` (:387) repeat `DrawIOClass.html`, `DrawIOCleanEngineeringModel._parse_class_html` (drawio_class_model.py:1032), and `_classify_edge` (drawio_class_model.py:1070); the writer half (lines 922 to about 1190) has no caller outside this file.
- _drawio_base.py:21 `DrawioViolation` is one of the rule-hit shapes in the integrated report §2.

### `limit-operation-parameters` — Fail
- _drawio_base.py:931 eleven operations take a packed tuple named `_rest` or `parts` in place of their real parameters (`_build_class_html(name, _rest)`, `_update_class_cell(cell, _rest)`, `_calc_cell_height(props_count, _rest)`, `_set_geometry(cell, _rest)`, `_edge_anchor_point(style, _rest)`, `_sync_page_to_model(drawio_path, _rest)`, `_rewrite_model_section(parts)`, ...). The callers build the tuple (`(self._cell_base, properties, operations, invariants, stereotype)` at :1010) and the callee unpacks it: the parameter count rule passes while the operation still takes five values, now untyped and unnamed.

### `hold-state-on-the-object-not-in-parameters` — Fail
- _drawio_base.py:35 `_explicit_paths` is a class-level field that `explicitly_requested` overwrites and restores around a scan, so every scanner instance in the MCP host shares it; two concurrent scans overwrite each other's list.
- _drawio_base.py:1010 `self._cell_base`, and the `self._scan_page_name` / `self._scan_file_path` fields the subclasses read, are set on the scanner for one page and read back by the next step.

### `use-explicit-dependencies` — Fail
- _drawio_base.py:116 `_load_scanner_class` inserts the scanners folder into `sys.path` and replaces `sys.modules['_drawio_base']` while it imports each `*_scanner.py`, because the scanners import `from _drawio_base import DrawioScanner` as a bare module. Loading a scanner changes import resolution for the whole host process, the same double-import problem as bug B5.

### `use-intention-revealing-names` — Fail
- _drawio_base.py:1419 the `_eap_*` family (`_eap_parse_style`, `_eap_anchor_side`, `_eap_seg_orient`, `_eap_seg_dir_signed`, ...) abbreviates "edges approach perpendicular", and `_fmt_seg`, `_ccw_2d` follow the same habit; `_rest` and `parts` say nothing about what they carry.

**Passes:** `vocabulary-traces-to-source`, `do-not-invent-terms`, `model-modules-follow-the-partition`, `class-not-property-instance-or-subtype`, `shape-classes-around-resources`, `hide-inner-details`, `use-property-not-accessor`, `prefer-class-operations`, `external-system-interface-is-one-way`, `avoid-vague-parameter-names`, `errors-out-of-existence`, `state-change-returns-record-or-named-failure`, `domain-exception-carries-context`, `limit-comments`, `write-invariants`, `write-interactions`, `no-redundant-relationship-paths`, `use-consistent-naming`, `one-canonical-model-document`.
