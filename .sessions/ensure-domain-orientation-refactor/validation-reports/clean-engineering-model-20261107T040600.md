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

**Generated:** 2026-11-07 04:06:00 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 34
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

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\nodes.py#L310): OoadClass `BoundedContext`: Class 'BoundedContext' exposes 11 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/stereotypes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\stereotypes.py#L1): OoadClass `_module`: Class '_module' exposes 17 public operations (budget ~9). Split responsibilities.

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

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\nodes.py#L128): OoadClass `Entity`: Class 'Entity' constructs 'InvariantObject' inside its constructor.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\nodes.py#L227): OoadClass `DomainEvent`: Class 'DomainEvent' constructs 'Property' inside its constructor.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\nodes.py#L273): OoadClass `Aggregate`: Class 'Aggregate' constructs 'Integration' inside its constructor.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\nodes.py#L310): OoadClass `BoundedContext`: Class 'BoundedContext' constructs 'BoundChildren' inside its constructor.

Evaluate the current context against this rule (use-explicit-dependencies):

### `external-system-interface-is-one-way`

Let a domain wrapper or collaborator depend on the named external-system contract. Keep the external type independent of domain wrappers and domain types, because a reverse dependency makes the external boundary depend on one caller's model.

Evaluate the current context against this rule (external-system-interface-is-one-way):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

Evaluate the current context against this rule (keep-operations-single-responsibility):

### `limit-operation-parameters`

Have callers pass intent, not setup. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/stereotypes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\stereotypes.py#L207): Operation `declares_tactical_stereotype`: Operation 'declares_tactical_stereotype' takes 4 parameters (maximum 3, excluding self).

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

**Graph violations:** 5

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/clean_engineering_bridge.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\clean_engineering_bridge.py#L52): Operation `from_clean_engineering`: Operation 'from_clean_engineering' is 24 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\nodes.py#L102): Operation `load_tactical_facts`: Operation 'load_tactical_facts' is 21 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/stereotypes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\stereotypes.py#L29): Operation `class_declaration_decorated_name`: Operation 'class_declaration_decorated_name' is 24 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/technical_names.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\technical_names.py#L23): Operation `rows_for_technical_names`: Operation 'rows_for_technical_names' is 23 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/vocabulary.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\vocabulary.py#L83): Operation `is_gerund`: Operation 'is_gerund' is 24 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `missing-module-context`

**Graph violations:** 20

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/__init__.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\__init__.py#L1): OoadClass `_module`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/clean_engineering_bridge.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\clean_engineering_bridge.py#L1): OoadClass `_module`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\nodes.py#L33): OoadClass `UnsupportedBoundedContextFile`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\nodes.py#L41): OoadClass `Integration`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\nodes.py#L62): OoadClass `InvariantObject`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\nodes.py#L88): OoadClass `TacticalBuildingBlock`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\nodes.py#L128): OoadClass `Entity`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\nodes.py#L167): OoadClass `ValueObject`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\nodes.py#L189): OoadClass `Repository`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\nodes.py#L209): OoadClass `DomainService`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\nodes.py#L227): OoadClass `DomainEvent`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\nodes.py#L257): OoadClass `Specification`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\nodes.py#L265): OoadClass `Factory`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\nodes.py#L273): OoadClass `Aggregate`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\nodes.py#L310): OoadClass `BoundedContext`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\nodes.py#L402): OoadClass `BoundedContextMap`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\nodes.py#L449): OoadClass `DDDModelFactory`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/stereotypes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\stereotypes.py#L1): OoadClass `_module`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/technical_names.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\technical_names.py#L1): OoadClass `_module`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/vocabulary.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\vocabulary.py#L47): OoadClass `VocabularyHelper`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.

Evaluate the current context against this rule (missing-module-context):

### `simplify-control-flow`

Handle the failing or empty cases first and return. Keep the main path flat. Do not nest more than three levels — deeper than that you cannot tell which conditions hold on a given line without reading back up, and that is where the unhandled branch hides.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/vocabulary.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\vocabulary.py#L66): Operation `is_agent_noun`: Operation 'is_agent_noun' nests control flow 4 levels deep (max 3).

Evaluate the current context against this rule (simplify-control-flow):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/__init__.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\__init__.py#L26): Parameter `root`: Parameter 'root' is missing a type annotation.

Evaluate the current context against this rule (use-typed-signatures):

---

# AI judgment (ddd sub-judge, model fidelity) — top-level files of `cdd_guidance/practices/ddd/model`

## Judgment — `cdd_guidance/practices/ddd/model/clean_engineering_bridge.py`

### `do-not-invent-parallel-object-models` — Fail
- clean_engineering_bridge.py:34 `to_clean_engineering`: DDD's `Entity`, `Repository`, `Aggregate`, and `BoundedContext` already subclass CE's `OoadClass` and `Module` (`nodes.py:16`), yet the bridge rebuilds a second, plain `CleanEngineeringModel` of the same classes and copies every property and operation into it (`:46`, `:99`, `:100`). The DDD subtypes are thrown away on the way to code and rebuilt on the way back, so the two models are kept in step by hand.
- clean_engineering_bridge.py:52 `from_clean_engineering`: always returns the *markdown* subtypes (`MarkdownBoundedContextMap`, `MarkdownAggregate`, `MarkdownEntity`), so the base DDD model cannot be rebuilt without the markdown format adapter; the format adapter has become the real model.
- clean_engineering_bridge.py:55 `contexts` / `aggregates` dicts keyed by name tuples: an index of contexts and aggregates beside the map that already owns them (`BoundedContextMap.contexts`, `BoundedContext.aggregates`).

### `hold-state-on-the-object-not-in-parameters` — Fail
- clean_engineering_bridge.py:93 `_class_from_card`: writes each class's stereotypes and place into its intent text (`<<Aggregate Root>> <<Entity>> Sales · Order`) and `:104 _card_from_class` parses them back with a regex; `:199 _integration_text` and `:208 _take_integrations` do the same for integration arcs. This is state written into a string and parsed back, which the rule names.
- clean_engineering_bridge.py:152 `_aggregate(bounded_context_map, contexts, aggregates, path, aggregate_name)`: five parameters, three of them the conversion's own working state handed down on every call.

### `prefer-class-operations` — Fail
- clean_engineering_bridge.py:34 `to_clean_engineering` and `:52 from_clean_engineering` plus ten private helpers: a file of free functions, each taking the map, aggregate, or card first (`_cards_in_order(aggregate)`, `_infer_relationships(aggregate)`, `_take_integrations(aggregate)`). These are operations on `BoundedContextMap` and `Aggregate` (or a `from_*` factory on the model).

### `hide-inner-details` — Fail
- clean_engineering_bridge.py:72 `aggregate._take_root_card()`: calls a private operation of `MarkdownAggregate` from another module.
- clean_engineering_bridge.py:169 `context._map = bounded_context_map`: sets a private field of `BoundedContext` from outside.
- clean_engineering_bridge.py:230 `_target_parts`: imports the private `_parse_arrow_target` from `markdown/nodes.py`.
- clean_engineering_bridge.py:87 `_cards_in_order`: reads `cards` through `getattr(aggregate, "cards", [])`, a field only `MarkdownAggregate` has; a map read from any other format converts with every non-root class missing.

### `eliminate-duplication` — Fail
- clean_engineering_bridge.py:86 `_cards_in_order`: the root, then repository, then members order is written again in `markdown/nodes.py:286 _model_lines` and `drawio/drawio_aggregate_model.py:231 _split`; `MarkdownAggregate.repository` (`markdown/nodes.py:160`) already answers half of it.
- clean_engineering_bridge.py:30 `_STEREOTYPE`: the fourth stereotype parser (also `stereotypes.py:8`, `markdown/class_cards.py:15`, `markdown/nodes.py:65`).
- clean_engineering_bridge.py:133 the type-hint split regex is written again at `:189` and in `drawio_aggregate_model.py:308 _type_name`.
- clean_engineering_bridge.py:123 `_stereotypes_by_name` and `:137` (`name[: -len("Repository")]`): copy `stereotypes.py:173 repository_root_name` and `stereotypes.py:155`.

### `keep-operations-small-focused` — Fail
- clean_engineering_bridge.py:52 `from_clean_engineering`: 24 lines that place classes, group the unplaced ones, infer relationships, take integrations, and choose roots.

## Judgment — `cdd_guidance/practices/ddd/model/nodes.py`

### `do-not-invent-parallel-object-models` — Fail
- nodes.py:102 `TacticalBuildingBlock.load_tactical_facts`: copies every `OoadClass.graph_facts` value from the parsed class onto itself with `setattr` (`:107`), so each tactical class exists twice — the CE class the parser read and the DDD block that copies it (the docstring at `:91` says so). The parser should build the DDD subtype directly.
- nodes.py:41 `Integration`: holds `context`, `aggregate`, and `target` as name strings, not references to the `BoundedContext` and `Aggregate` it points at, so every reader re-resolves the names (`drawio_bounded_context_map.py:577 _match_context`, `:588 _resolve_target_aggregate`, `drawio_aggregate_model.py:326`).
- nodes.py:402 `BoundedContextMap`: the root of the DDD model is not a graph node (no `BoundNode`/`OoadNode` base), unlike `CleanEngineeringModel` (`base_class_model.py:674`), and keeps a plain `contexts` list while `BoundedContext` uses `BoundChildren`; the map cannot be reached from the graph and duplicates the CE model root's job.
- nodes.py:449 `DDDModelFactory` and `:457 _channel_for`: a second format-to-class registry beside `Ddd(formats=...)` (`ddd.py:43`), knowing only markdown; only `ddd_channel.feature.py` calls it.

### `hold-state-on-the-object-not-in-parameters` — Fail
- nodes.py:102 `load_tactical_facts(parsed, file_text)`: the block is handed the parsed class and the whole file text and re-scans the source with regexes (`method_body`, `:114`, `:118`) for facts the parser already holds as operations and bodies.
- nodes.py:120 `declares_tactical_stereotype(file_text, parsed.name, self.tactical_kind(), set(parsed.peer_names))`: passes four values the block itself holds.
- nodes.py:321 `BoundedContext.__init__`: `name` doubles as the graph (`if isinstance(name, Graph)`) — one parameter carries two kinds of state.

### `keep-classes-single-responsibility` — Fail
- nodes.py:310 `BoundedContext`: 11 public operations, most of them a file-reading cursor (`load_*`, `has_more_*`, `load_next_*`, `get_next_*_from_file`) that only the markdown subclass overrides; the domain node carries the format adapter's reading protocol. The same cursor sits on `Entity` (`:152`) and `BoundedContextMap` (`:431`, with `_lines`/`_index` at `:410`), and `Aggregate` keeps unused `_lines`/`_index` (`:298`).

### `class-not-property-instance-or-subtype` — Fail
- nodes.py:179 `ValueObject.create`, `:182 clone`, `:185 mix`: a model element acting out value-object semantics on itself; `create` and `clone` are identical and `mix` only copies an intent. No production caller.
- nodes.py:257 `Specification` and `:265 Factory`: identical bodies with no behaviour; the kind is data (`_semantic_type_name`), which a property on `TacticalBuildingBlock` would carry.

### `use-consistent-naming` — Fail
- nodes.py:159 `load_next_invariant_object` calls `:163 get_next_invariant_object_from_file`: `load_` and `get_` name the same step; the pair repeats for contexts (`:371`, `:377`) and aggregates (`:390`, `:395`).

### `eliminate-duplication` — Fail
- nodes.py:135 every class carries its own hand-written `source=` copy constructor (`:135`, `:173`, `:195`, `:215`, `:233`, `:289`, `:320`, `:405`), beside the `clone()` that `OoadClass` and `Module` already have (`base_class_model.py:274`, `:552`).
- nodes.py:79 `_LOAD_NAMES`: a second list of load verbs beside `rules/tactical_helpers.py:9`.

## Judgment — `cdd_guidance/practices/ddd/model/stereotypes.py`

### `prefer-class-operations` — Fail
- stereotypes.py:29 `class_declaration_decorated_name` and 16 more free functions (`is_entity`, `is_repository`, `ddd_class_kind`, `inferred_tactical_kind`, `name_reflects_tactical_kind`, ...): a file of hanging functions that each take a class name and re-derive its kind; the kind belongs on the tactical node (known: integrated report section 3, "stereotypes 17").

### `limit-operation-parameters` — Fail
- stereotypes.py:207 `declares_tactical_stereotype(file_text, class_name, graph_kind, peer_names)`: four parameters, all state of the class being asked about.

### `eliminate-duplication` — Fail
- stereotypes.py:59 `plain_class_name`: a second function of the same name sits in `markdown/class_cards.py:80` with different behaviour (this one strips `extends`, that one strips backticks), and a third variant in `markdown/nodes.py:54 plain_name`.
- stereotypes.py:55 `class_stereotypes`: the same stereotype parse as `markdown/class_cards.py:76 stereotypes_in` and `markdown/nodes.py:65 MarkdownDomainNode.stereotypes`.
- stereotypes.py:97 `ddd_class_kind` maps stereotypes to kind names, while `markdown/nodes.py:73 building_block_type` maps the same stereotypes to classes, and `:13 _AT_TO_STEREOTYPE`, `:137 _KIND_TAGS`, `:187 _TAGGED_KINDS` list the kinds again. One table of tactical kinds on the node classes would replace all of them.

### `one-way-deps` — Fail
- stereotypes.py:1: `clean_engineering/model/base_class_model.py:618` imports this module back, and `harness/graph/working_copy.py:597` and `harness/graph/ddd_rule_eval_harness.py:14` import it too (the cycle in integrated report section 6).

## Judgment — `cdd_guidance/practices/ddd/model/technical_names.py`

### `no-legacy-api-after-refactor` — Fail
- technical_names.py:23 `rows_for_technical_names`: no caller anywhere in the repository, specs included; it and its only import, `vocabulary.py`, are dead code. The check in use is `rules/tactical_helpers.py:51 technical_name_violation`.

### `use-intention-revealing-names` — Fail
- technical_names.py:23 `rows_for_technical_names(rows)`: "rows" is a banned word, and the function takes and returns `list[dict]` with `name`/`message`/`contributor` keys instead of a typed violation (one of the rule-hit shapes in integrated report section 2).

### `eliminate-duplication` — Fail
- technical_names.py:19 `ident_tokens`, `:16 _CAMEL`, `:15 _TECHNICAL_SUFFIXES`: verbatim copies of `rules/tactical_helpers.py:17`, `:8`, `:6`.

### `use-explicit-dependencies` — Fail
- technical_names.py:31 `VocabularyHelper()`: constructed again for every token inside the loop instead of being handed in once.

## Judgment — `cdd_guidance/practices/ddd/model/vocabulary.py`

### `use-explicit-dependencies` — Fail
- vocabulary.py:18 `socket.setdefaulttimeout(2)` and the NLTK downloads at import: known bug B15. The module is imported only by `technical_names.py`, which has no caller, so the fix is to delete both files.

### `shape-classes-around-resources` — Fail
- vocabulary.py:47 `VocabularyHelper`: a stateless `*Helper` doer — the agent-noun class name the DDD rule it supports is meant to reject.

### `simplify-control-flow` — Fail
- vocabulary.py:66 `is_agent_noun`: four levels of nesting.

### `errors-out-of-existence` — Fail
- vocabulary.py:51 `_has_synsets` (also `:107 pos_tags`, `:129 is_actor_or_role`): `except Exception` prints a warning and returns `False` or `[]`, so a missing corpus reads as "not a verb".

## Judgment — `cdd_guidance/practices/ddd/model/__init__.py`

### `no-legacy-api-after-refactor` — Fail
- __init__.py:26 `load_bounded_context_map(root)`: no caller; it guesses four file locations instead of asking the session or practice for its folder.

### `use-typed-signatures` — Fail
- __init__.py:26 `load_bounded_context_map(root)`: `root` is untyped and the return type is undeclared.

Passes (all six files): `avoid-vague-parameter-names`, `external-system-interface-is-one-way`, `domain-exception-carries-context` (`UnsupportedBoundedContextFile` carries the path), `state-change-returns-record-or-named-failure`, `no-redundant-relationship-paths`.

Graph hits dismissed:
- `missing-module-context` (20 hits on `model/`): dismissed; `model/` rolls up into `cdd_guidance/practices/ddd/.context/module-context.md`, which exists.
- `use-explicit-dependencies` (4 hits: `Entity`, `DomainEvent`, `Aggregate`, `BoundedContext` construct `InvariantObject`, `Property`, `Integration`, `BoundChildren`): dismissed. These are composed parts and child collections the owner creates for itself; composition owns its parts' lifecycle.
- Confirmed: `keep-classes-single-responsibility` on `BoundedContext` and the stereotypes `_module`; `limit-operation-parameters` on `declares_tactical_stereotype`; `keep-operations-small-focused` (5: `from_clean_engineering`, `load_tactical_facts`, `class_declaration_decorated_name`, `rows_for_technical_names`, `is_gerund`, each over 20 lines; a code-fidelity rule the scanner runs here); `simplify-control-flow` on `is_agent_noun`; `use-typed-signatures` on `load_bounded_context_map`.
