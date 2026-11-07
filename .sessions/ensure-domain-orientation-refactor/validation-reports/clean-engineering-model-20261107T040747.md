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

**Generated:** 2026-11-07 04:07:47 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 17
**Rules with graph hits:** 5
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

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\nodes.py#L379): Operation `parse`: Operation 'parse' mixes I/O-style calls with domain calculation; split responsibilities.

Evaluate the current context against this rule (keep-operations-single-responsibility):

### `limit-operation-parameters`

Have callers pass intent, not setup. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

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

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/class_cards.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\class_cards.py#L39): Operation `lines`: Operation 'lines' is 25 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\nodes.py#L73): Operation `building_block_type`: Operation 'building_block_type' is 21 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\nodes.py#L251): Operation `lines`: Operation 'lines' is 33 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\nodes.py#L316): Operation `lines`: Operation 'lines' is 26 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `missing-module-context`

**Graph violations:** 9

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/class_cards.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\class_cards.py#L23): OoadClass `ClassCard`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/class_cards_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\class_cards_spec.py#L1): OoadClass `_module`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\nodes.py#L53): OoadClass `MarkdownDomainNode`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\nodes.py#L96): OoadClass `MarkdownIntegration`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\nodes.py#L100): OoadClass `MarkdownInvariantObject`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\nodes.py#L104): OoadClass `MarkdownEntity`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\nodes.py#L120): OoadClass `MarkdownAggregate`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\nodes.py#L315): OoadClass `MarkdownBoundedContext`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\nodes.py#L354): OoadClass `MarkdownBoundedContextMap`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.

Evaluate the current context against this rule (missing-module-context):

### `simplify-control-flow`

Handle the failing or empty cases first and return. Keep the main path flat. Do not nest more than three levels — deeper than that you cannot tell which conditions hold on a given line without reading back up, and that is where the unhandled branch hides.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\nodes.py#L251): Operation `lines`: Operation 'lines' nests control flow 4 levels deep (max 3).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\nodes.py#L316): Operation `lines`: Operation 'lines' nests control flow 4 levels deep (max 3).

Evaluate the current context against this rule (simplify-control-flow):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\nodes.py#L386): Parameter `canonical`: Parameter 'canonical' is missing a type annotation.

Evaluate the current context against this rule (use-typed-signatures):

---

# AI judgment (ddd sub-judge, model fidelity) — `cdd_guidance/practices/ddd/model/markdown`

## Judgment — `cdd_guidance/practices/ddd/model/markdown/nodes.py`

### `hold-state-on-the-object-not-in-parameters` — Fail
- nodes.py:164 `MarkdownAggregate._read_map_lines`: swaps `self._body` for the map lines, calls `_read_map_body`, and restores the old body in `finally` — a field set on the object for one call and restored afterwards, which the rule names.

### `hide-inner-details` — Fail
- nodes.py:319 `MarkdownBoundedContext.lines`: reads `_preamble`, `_module_name`, `_module_body`, `_group_preambles` (`:319`–`:325`) and each aggregate's `_group` (`:332`) through `getattr`; no constructor declares them. The sketch adapter sets them from outside (`sketch/sketch_ddd_model.py:104`–`:107`, `:155`), so two modules share private fields of a third.
- nodes.py:256 `lines`: reads `self._operations` through `getattr`; it is only set inside `_read_map_body` (`:203`), never declared.

### `do-not-invent-parallel-object-models` — Fail
- nodes.py:120 `MarkdownAggregate`: holds `cards` (a list of `ClassCard`, each wrapping an `OoadClass`) beside `root` and `root.invariant_objects`, and `_take_root_card` (`:143`) re-derives `root` and `invariant_objects` from the cards. The aggregate's members are kept twice — as cards and as root members — and the bridge, the drawio aggregate view, and the sketch adapter read `cards` while the context-map path reads `invariant_objects`.
- nodes.py:53 `MarkdownDomainNode`: a mixin of name and stereotype parsing that every markdown subtype inherits beside its domain base (`MarkdownIntegration(Integration, MarkdownDomainNode)`, `:96`), so an `Integration` "is a" markdown parser; `clean_engineering_bridge.py:113` builds a throwaway `MarkdownAggregate()` just to call `building_block_type`.

### `prefer-class-operations` — Fail
- nodes.py:507 `_aggregates_in(bounded_context_map)`, `:520 _services_in`, `:531 _events_in`, `:546 _wire_event`: free functions taking the map first; they are the map's own queries and are imported privately by `sketch/sketch_ddd_model.py:11`.
- nodes.py:25 `_parse_arrow_target(target)`: parsing an integration target belongs on `Integration`, which holds `target`, `context`, and `aggregate`.

### `keep-operations-single-responsibility` — Fail
- nodes.py:520 `_services_in`: looks for `DomainService` instances in `aggregate.root.properties`, but nothing ever puts a `DomainService` (an `OoadClass`) on a property list, so it always returns an empty list (checked: a map whose event map names two consumer services gives `0`). `_wire_event` therefore creates every consumer service fresh.

### `eliminate-duplication` — Fail
- nodes.py:251 `MarkdownAggregate.lines` writes the integration lines (`:263`–`:275`) and emitted events (`:276`–`:281`) that `_integration_lines` (`:297`–`:312`) writes again, in two layouts.
- nodes.py:25 `_parse_arrow_target`: copied verbatim as `drawio/drawio_bounded_context_map.py:561 _parse_integration_target` (with `_ARROW_SPLIT` copied at `:45`), and again in `drawio_aggregate_model.py:326 _integration_root`.
- nodes.py:45 `_looks_like_operation`: copied verbatim as `drawio/drawio_bounded_context_map.py:816`.
- nodes.py:65 `MarkdownDomainNode.stereotypes` and `:54 plain_name`: the same jobs as `class_cards.py:76 stereotypes_in` and `:80 plain_class_name` in the sibling file, and `model/stereotypes.py:55`/`:59`.
- nodes.py:507 `_aggregates_in`: the same context-tree walk as `ddd.py:98`, `clean_engineering_bridge.py:78`, and `drawio_aggregate_model.py:224`.

### `errors-out-of-existence` — Fail
- nodes.py:386 `MarkdownBoundedContextMap.render`: a map that is not already a `MarkdownBoundedContextMap` is copied with `type(self)(source)`, whose base copy constructor (`model/nodes.py:412`) builds plain `BoundedContext` objects with no aggregates or child contexts, and `save` (`:399`) skips anything that is not a `MarkdownBoundedContext`. Checked: rendering a plain `BoundedContextMap` copy of a one-context map returns `'# Bounded Context Map\n'` — the content is dropped without an error.

### `use-consistent-naming` — Fail
- nodes.py:131 `has_more_integration` / `:134 get_next_integration_from_file`: a reading protocol nothing calls (the base `Aggregate` has no integration loop); dead names that look like the context and aggregate protocol.

### `keep-operations-small-focused` — Fail
- nodes.py:251 `MarkdownAggregate.lines` (33 lines, 4 levels deep) and `:316 MarkdownBoundedContext.lines` (26 lines, 4 levels deep).
- nodes.py:73 `building_block_type` (21 lines): a chain of stereotype tests with lazy imports in each branch, a third stereotype-to-kind table (see `model/stereotypes.py:97`).

## Judgment — `cdd_guidance/practices/ddd/model/markdown/class_cards.py`

### `do-not-invent-parallel-object-models` — Fail
- class_cards.py:23 `ClassCard`: wraps an `OoadClass` and adds `stereotypes` and `invariants`, which are facts of the class itself; DDD already has typed subclasses for each stereotype (`model/nodes.py` `Entity`, `Repository`, ...). `is_root` and `is_repository` (`:31`, `:35`) re-derive from strings what the node's type already says, so a card can claim `<<Repository>>` while wrapping an `Entity`.

### `prefer-class-operations` — Fail
- class_cards.py:66 `plain_properties(node)`: a free function taking the class first; it filters out `DomainEvent`/`InvariantObject` that DDD put on the same property list, so the class should expose its plain properties itself (used from four files).
- class_cards.py:109 `read_card(section, node_type_for)` and `:177 card_from_sketch(heading, lines, node_type_for)`: factories for `ClassCard` written as free functions that take a type-choosing callback; a `ClassCard.from_*` factory would hold this.

### `keep-operations-single-responsibility` — Fail
- class_cards.py:177 `card_from_sketch`: the sketch format's parser lives in the markdown adapter, and `sketch/sketch_ddd_model.py:193` turns its result back into markdown text (`card.lines()`) only for the markdown reader to parse again (`MarkdownAggregate._read_body`); one format's reader depends on another format's writer and reader.

### `eliminate-duplication` — Fail
- class_cards.py:80 `plain_class_name`: same name as `model/stereotypes.py:59 plain_class_name`, different behaviour.
- class_cards.py:20 `_ORDER` and `:84 ordered_stereotypes`: the root, entity, value object, repository ordering, written again as card ordering in `nodes.py:286`, `clean_engineering_bridge.py:86`, `drawio_aggregate_model.py:231`.
- class_cards.py:39 `ClassCard.lines`: member text formatting (`+ name: Type`, `+ op(params): Return`) is written again in `drawio/drawio_aggregate_model.py:297 _property_text` / `:302 _operation_text`, which drop private access, so the two formats disagree on the same class.

### `keep-operations-small-focused` — Fail
- class_cards.py:39 `ClassCard.lines`: 25 lines.

Passes: `avoid-vague-parameter-names`, `external-system-interface-is-one-way`, `domain-exception-carries-context`, `write-invariants` (not applicable to a format adapter), `use-explicit-dependencies`.

Graph hits dismissed:
- `missing-module-context` (9 hits on `model/markdown/`): dismissed; the folder rolls up into `cdd_guidance/practices/ddd/.context/module-context.md`, which exists. The hit on `class_cards_spec.py` is a spec and out of scope.
- `keep-operations-single-responsibility` on `nodes.py:379 parse` ("mixes I/O-style calls"): dismissed. `parse` does no I/O; it builds a fresh map from text already in hand. File reading is in `load_bounded_context_map_content` (`:360`).
- Confirmed: `keep-operations-small-focused` (4), `simplify-control-flow` (2), `use-typed-signatures` on `render(canonical=None)` (`canonical` is untyped and accepts any map).
