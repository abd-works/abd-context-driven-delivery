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

**Generated:** 2026-11-07 03:44:22 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 43
**Rules with graph hits:** 2
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

### `missing-module-context`

**Graph violations:** 14

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/limit_operation_parameters.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\limit_operation_parameters.py#L31): OoadClass `LimitOperationParameters`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/module_graph_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\module_graph_rules.py#L8): OoadClass `NamedSeamAndConstraint`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/module_graph_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\module_graph_rules.py#L23): OoadClass `PublicSeamOnly`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/module_graph_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\module_graph_rules.py#L43): OoadClass `MissingModuleContext`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/module_graph_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\module_graph_rules.py#L57): OoadClass `LanguageModulesOneSection`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/module_graph_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\module_graph_rules.py#L71): OoadClass `ModulesNotModelBlocks`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/module_naming_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\module_naming_rules.py#L16): OoadClass `DomainNounsOnly`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/module_naming_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\module_naming_rules.py#L32): OoadClass `NoModulePerClass`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/no_prototype_swapping.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\no_prototype_swapping.py#L8): OoadClass `NoPrototypeSwapping`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/practice_wide_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\practice_wide_rules.py#L12): OoadClass `OneWayDeps`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/practice_wide_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\practice_wide_rules.py#L35): OoadClass `LowCoupling`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/practice_wide_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\practice_wide_rules.py#L57): OoadClass `DeepModule`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/practice_wide_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\practice_wide_rules.py#L78): OoadClass `ExtensionsLiveWithTheDomain`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/write_interactions.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\write_interactions.py#L10): OoadClass `WriteInteractions`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.

Evaluate the current context against this rule (missing-module-context):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 29

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/limit_operation_parameters.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\limit_operation_parameters.py#L35): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/limit_operation_parameters.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\limit_operation_parameters.py#L35): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/module_graph_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\module_graph_rules.py#L12): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/module_graph_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\module_graph_rules.py#L12): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/module_graph_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\module_graph_rules.py#L27): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/module_graph_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\module_graph_rules.py#L27): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/module_graph_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\module_graph_rules.py#L47): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/module_graph_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\module_graph_rules.py#L47): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/module_graph_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\module_graph_rules.py#L61): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/module_graph_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\module_graph_rules.py#L61): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/module_graph_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\module_graph_rules.py#L75): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/module_graph_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\module_graph_rules.py#L75): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/module_naming_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\module_naming_rules.py#L20): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/module_naming_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\module_naming_rules.py#L20): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/module_naming_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\module_naming_rules.py#L36): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/module_naming_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\module_naming_rules.py#L36): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/no_prototype_swapping.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\no_prototype_swapping.py#L14): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/no_prototype_swapping.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\no_prototype_swapping.py#L14): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/practice_wide_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\practice_wide_rules.py#L16): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/practice_wide_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\practice_wide_rules.py#L16): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/practice_wide_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\practice_wide_rules.py#L19): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/practice_wide_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\practice_wide_rules.py#L39): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/practice_wide_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\practice_wide_rules.py#L39): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/practice_wide_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\practice_wide_rules.py#L61): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/practice_wide_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\practice_wide_rules.py#L61): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/practice_wide_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\practice_wide_rules.py#L82): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/practice_wide_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\practice_wide_rules.py#L82): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/write_interactions.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\write_interactions.py#L14): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/write_interactions.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\rules\write_interactions.py#L14): Parameter `context`: Parameter 'context' is missing a type annotation.

Evaluate the current context against this rule (use-typed-signatures):

---

# Judgment (model fidelity, `clean_engineering/rules`)

**Graph hits dismissed:** `missing-module-context` (14): `cdd_guidance/practices/clean_engineering/.context/module-context.md` exists and `rules/` rolls up into it.

**Graph hits confirmed (low):** `use-typed-signatures` (29): every `check(self, node, context)` override drops the base's `RuleCheckContext` type, and `node` is untyped on the base too (`harness/graph/practice_rule.py:15`), so each rule reads node facts by string with no contract.

## Judgment — `cdd_guidance/practices/clean_engineering/rules/practice_wide_rules.py`

### `errors-out-of-existence` — Fail
- practice_wide_rules.py:24 `OneWayDeps.check_practice` returns inside the first iteration of `for cycle in _find_cycles(imports)`, so it reports one pair from the first cycle and drops every other cycle; with the 25-module cycle in this repository, validate names a single import pair and hides the rest.

### `vocabulary-traces-to-source` — Fail
- practice_wide_rules.py:57 `DeepModule` checks "more than five classes with one method or fewer"; the rule `deep-module` says at most 40% of a module's classes are public. No graph rule measures the public share, so the scanner reports a different property under the rule's name.

### `prefer-class-operations` — Fail
- practice_wide_rules.py:96 `_folders`, `_is_under`, `_sibling_modules`, `_parent_folder`, `_imports_under`, `_find_cycles`, `_cycles_reachable_from` are free functions taking `node` and `context`; a module's siblings, the folders it contains, and what it imports are questions the graph's Module node and practice should answer.

### `put-logic-on-the-owning-resource` — Fail
- practice_wide_rules.py:106 `_sibling_modules` and `_imports_under` (practice_wide_rules.py:120) work out folder containment and imports from `source.file` strings in the rule, so every rule that needs them repeats the path arithmetic instead of asking the module.

### `use-intention-revealing-names` — Fail
- practice_wide_rules.py:78 `ExtensionsLiveWithTheDomain` only fires for class names that start with `Graph` and contain `Epic`; the rule is written for its example, not for "a domain extension of a framework type".

## Judgment — `cdd_guidance/practices/clean_engineering/rules/module_graph_rules.py`

### `eliminate-duplication` — Fail
- module_graph_rules.py:8 `NamedSeamAndConstraint` and `MissingModuleContext` (module_graph_rules.py:43) both report a folder without `module-context.md`; one fact, two rules, two messages.

### `prefer-class-operations` — Fail
- module_graph_rules.py:36 `_python_class_folder` is a free function taking `node, context` and reaching into `context.practice.registered`; the class node's folder belongs on the class node.

## Judgment — `cdd_guidance/practices/clean_engineering/rules/module_naming_rules.py`

### `keep-classes-single-responsibility` — Fail
- module_naming_rules.py:32 `NoModulePerClass` also reports `*is a type of*` and `Child : Parent` in a module card, which is a modules-fidelity wording rule, not "one module per class"; two rules ride on one slug, so a hit tells the reader the wrong fix.

### `prefer-class-operations` — Fail
- module_naming_rules.py:55 `_public_classes_in` is a free function that scans every class node in the practice for each module.

## Judgment — `cdd_guidance/practices/clean_engineering/rules/limit_operation_parameters.py`

### `eliminate-duplication` — Fail
- limit_operation_parameters.py:12 `_PARAMETER_COUNT_EXEMPT_OPERATION_NAMES` and the `from_` / `fromXxx` / `load` patterns repeat the factory exemptions in `model/rules_shared/operation_checks.py:39` (`_STATIC_FACTORY_NAMES`, `_STATIC_FACTORY_EXTRA_NAMES`); the comment says "align with prefer-instance-operations", which means the two lists are kept in step by hand.

### `hide-inner-details` — Fail
- limit_operation_parameters.py:44 `check` reads `node.practice.edges.get("hasParameter", [])` and filters by `edge.parent is node`; the rule depends on how the graph stores edges instead of asking the operation for its parameters.

## Judgment — `cdd_guidance/practices/clean_engineering/rules/__init__.py`

### `one-canonical-model-document` — Fail
- __init__.py:3 Clean Engineering's graph rules live in two folders: `rules/` and `model/rules_shared/` (plus `CODE_RULES` from `operation_checks.py`), and `rules/__init__.py` stitches them together. Two homes for one rule set mean a reader looking for a rule's check has to search both.

**Passes:** `do-not-invent-terms`, `do-not-invent-parallel-object-models`, `model-modules-follow-the-partition`, `class-not-property-instance-or-subtype`, `shape-classes-around-resources`, `use-property-not-accessor`, `use-explicit-dependencies`, `external-system-interface-is-one-way`, `keep-operations-single-responsibility`, `limit-operation-parameters`, `avoid-vague-parameter-names`, `state-change-returns-record-or-named-failure`, `domain-exception-carries-context`, `limit-comments`, `write-invariants`, `write-interactions`, `no-redundant-relationship-paths`, `use-consistent-naming`.
