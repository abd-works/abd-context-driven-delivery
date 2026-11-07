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

**Generated:** 2026-11-07 03:42:12 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 56
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

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/bdd_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\bdd_model.py#L20): OoadClass `BddModel`: Class 'BddModel' constructs 'CodeBody' inside its constructor.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\nodes.py#L54): OoadClass `Description`: Class 'Description' constructs 'BoundChildren' inside its constructor.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\nodes.py#L78): OoadClass `Context`: Class 'Context' constructs 'BoundChildren' inside its constructor.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\nodes.py#L104): OoadClass `Observation`: Class 'Observation' constructs 'CodeBody' inside its constructor.

Evaluate the current context against this rule (use-explicit-dependencies):

### `external-system-interface-is-one-way`

Let a domain wrapper or collaborator depend on the named external-system contract. Keep the external type independent of domain wrappers and domain types, because a reverse dependency makes the external boundary depend on one caller's model.

Evaluate the current context against this rule (external-system-interface-is-one-way):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/graph_bdd_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\graph_bdd_model.py#L29): Operation `parse`: Operation 'parse' mixes I/O-style calls with domain calculation; split responsibilities.

Evaluate the current context against this rule (keep-operations-single-responsibility):

### `limit-operation-parameters`

Have callers pass intent, not setup. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/spec_helpers.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\spec_helpers.py#L28): Operation `expect_scan_fails`: Operation 'expect_scan_fails' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/spec_helpers.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\spec_helpers.py#L38): Operation `expect_scan_passes`: Operation 'expect_scan_passes' takes 4 parameters (maximum 3, excluding self).

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

### `deep-module`

Keep most classes private (at most **40%** public) in each first-class module. A first-class module is a folder that owns `.context/module-context.md`. Nested folders that also own that file are separate modules — respect them. Nested folders that do not own it roll up to the nearest enclosing module-context folder, or to the folder you are querying if none sits in between. Count classes, not operations: a public method on a hidden class is not a second seam. Every public class is a signature you cannot change without editing every caller, so public classes are much harder to refactor than private ones.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd#L1): Module `bdd`: Module 'bdd' splits into many tiny classes (33); prefer a deep module with a small public surface.

Evaluate the current context against this rule (deep-module):

### `missing-module-context`

**Graph violations:** 28

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/_examples/examples.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\_examples\examples.py#L95): OoadClass `Character`: Module folder '_examples' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/_examples/faultyAsset.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\_examples\faultyAsset.py#L5): OoadClass `Character`: Module folder '_examples' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/bdd_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\bdd_model.py#L20): OoadClass `BddModel`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/bdd_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\bdd_model.py#L143): OoadClass `MarkdownBddModel`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/code_spec_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\code_spec_model.py#L29): OoadClass `CodeBddModel`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/code_spec_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\code_spec_model.py#L183): OoadClass `PythonBddModel`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/code_spec_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\code_spec_model.py#L261): OoadClass `TypeScriptBddModel`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/code_spec_render_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\code_spec_render_spec.py#L1): OoadClass `_module`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/graph_bdd_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\graph_bdd_model.py#L26): OoadClass `GraphBddModel`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\nodes.py#L37): OoadClass `BehaviorNode`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\nodes.py#L54): OoadClass `Description`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\nodes.py#L78): OoadClass `Context`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\nodes.py#L104): OoadClass `Observation`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/python/_examples/examples.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\python\_examples\examples.py#L95): OoadClass `Character`: Module folder '_examples' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/python/_examples/faultyAsset.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\python\_examples\faultyAsset.py#L5): OoadClass `Character`: Module folder '_examples' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/python/_examples/layer-isolation/widget_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\python\_examples\layer-isolation\widget_spec.py#L1): OoadClass `_module`: Module folder 'layer-isolation' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/python/_examples/observable-behavior/widget_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\python\_examples\observable-behavior\widget_spec.py#L1): OoadClass `_module`: Module folder 'observable-behavior' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/sketch/sketch_bdd_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\sketch\sketch_bdd_model.py#L8): OoadClass `SketchBddModel`: Module folder 'sketch' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/spec_source.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\spec_source.py#L1): OoadClass `_module`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/rules/layer_isolation.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\rules\layer_isolation.py#L8): OoadClass `LayerIsolation`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/rules/observable_behavior.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\rules\observable_behavior.py#L8): OoadClass `ObservableBehavior`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/rules/shared_describe_subject.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\rules\shared_describe_subject.py#L52): OoadClass `SharedDescribeSubject`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/rules/spec_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\rules\spec_rules.py#L18): OoadClass `PlainEnglishOnly`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/rules/spec_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\rules\spec_rules.py#L29): OoadClass `SignatureMarkers`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/rules/tree_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\rules\tree_rules.py#L16): OoadClass `DescribeSubjectNotInternal`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/rules/tree_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\rules\tree_rules.py#L27): OoadClass `StateNotWhen`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/rules/tree_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\rules\tree_rules.py#L38): OoadClass `OneAssertionPerTest`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/rules/tree_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\rules\tree_rules.py#L49): OoadClass `NoImplementation`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.

Evaluate the current context against this rule (missing-module-context):

### `provide-meaningful-context`

Give a number or literal a name that says why it is there (`SECONDS_PER_DAY`, not `86400`). Do not number variables (`item1`).

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/_examples/examples.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\_examples\examples.ts#L111): Operation `defaultStats`: Operation 'defaultStats' uses the unnamed number 6.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/graph_bdd_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\graph_bdd_model.py#L29): Operation `parse`: Operation 'parse' uses the unnamed number 6.

Evaluate the current context against this rule (provide-meaningful-context):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 18

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/rules/layer_isolation.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\rules\layer_isolation.py#L12): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/rules/layer_isolation.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\rules\layer_isolation.py#L12): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/rules/observable_behavior.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\rules\observable_behavior.py#L12): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/rules/observable_behavior.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\rules\observable_behavior.py#L12): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/rules/shared_describe_subject.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\rules\shared_describe_subject.py#L56): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/rules/shared_describe_subject.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\rules\shared_describe_subject.py#L56): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/rules/spec_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\rules\spec_rules.py#L22): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/rules/spec_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\rules\spec_rules.py#L22): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/rules/spec_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\rules\spec_rules.py#L33): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/rules/spec_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\rules\spec_rules.py#L33): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/rules/tree_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\rules\tree_rules.py#L20): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/rules/tree_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\rules\tree_rules.py#L20): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/rules/tree_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\rules\tree_rules.py#L31): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/rules/tree_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\rules\tree_rules.py#L31): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/rules/tree_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\rules\tree_rules.py#L42): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/rules/tree_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\rules\tree_rules.py#L42): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/rules/tree_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\rules\tree_rules.py#L53): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/rules/tree_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\rules\tree_rules.py#L53): Parameter `context`: Parameter 'context' is missing a type annotation.

Evaluate the current context against this rule (use-typed-signatures):

---

# Judgment (model fidelity, BDD production files)

Judged the graph validate built from `bdd.py`, `spec_helpers.py`, `rules/`, and `model/` (production files only; `_examples/`, `templates/`, and `*_spec.py` are out of scope).

**Graph hits dismissed:**
- `missing-module-context` (29): `cdd_guidance/practices/bdd/.context/module-context.md` exists and `model/`, `rules/`, `model/sketch/` roll up into it; the `_examples` hits and the `*_spec.py` pseudo-modules are out of scope.
- `use-explicit-dependencies` (4): `CodeBody` and `BoundChildren` are owned parts (composition) of `BddModel`, `Description`, `Context`, and `Observation`, not swappable collaborators. Building an owned part in the constructor is what composition means.
- `deep-module` (`bdd`, 33 classes): the count includes `_examples` classes and spec pseudo-classes; the production classes are about 20, and the hit's message ("many tiny classes") is not the rule's measure (share of public classes).
- `limit-operation-parameters` on `expect_scan_fails` / `expect_scan_passes`: two of the four are optional keyword filters on a test helper; the real problem with that file is the broken import below.
- `provide-meaningful-context` on `_examples/examples.ts`: out of scope.

**Graph hits confirmed:** `keep-operations-single-responsibility` on `GraphBddModel.parse`; `provide-meaningful-context` on `GraphBddModel.parse` (the 5 and 6 are positional indexes into the graph's node lists); `use-typed-signatures` on every `check(self, node, context)` override (18 hits, low: the overrides drop the base's `RuleCheckContext` type and the base leaves `node` untyped).

## Judgment — `cdd_guidance/practices/bdd/spec_helpers.py`

### `vocabulary-traces-to-source` — Fail
- spec_helpers.py:11 imports `cdd_guidance.practices.clean_engineering.specifications.lern_domain_driven.scanners._scan_base`, which does not exist anywhere in the repository, so `expect_scan_fails` and `expect_scan_passes` raise ImportError on first use. The BDD module card still lists both on the seam, and `templates/bdd.py:62` and `clean_engineering/model/drawio/drawio.py:143` tell agents to call them.

## Judgment — `cdd_guidance/practices/bdd/model/sketch/sketch_bdd_model.py`

### `vocabulary-traces-to-source` — Fail
- sketch_bdd_model.py:22 `render` imports `_render_sketch` from `bdd_model`, which no longer defines it (the sketch writer became `BddModel._sketch_lines`). Rendering any BDD model to the sketch format raises ImportError; only `parse` is covered by a spec.

### `hide-inner-details` — Fail
- sketch_bdd_model.py:13 `parse` imports the private `_parse_sketch` from another file; the sketch reader is a free function that both `BddModel.parse` and this subclass reach into, instead of an operation on `BddModel` the subclass inherits.

## Judgment — `cdd_guidance/practices/bdd/model/nodes.py`

### `class-not-property-instance-or-subtype` — Fail
- nodes.py:37 `BehaviorNode(StoryNode)`: a describe-tree node is made a subtype of the Stories practice's `StoryNode`, inheriting its 13 story graph facts, actor nouns, and generic-verb tables. A describe is not a story node; it needs the graph's `BoundNode`, so BDD depends on the Stories model for nothing it uses.

### `eliminate-duplication` — Fail
- nodes.py:54 `Description` and `Context` (nodes.py:78) hold the same two children (`contexts`, `observations`) and the same `clone` and `load_context`; one base for "a block that holds contexts and observations" would hold them once.
- nodes.py:74 `load_context` and `load_observation` (nodes.py:97) only return `source.clone()`.

### `prefer-class-operations` — Fail
- nodes.py:22 `private_probe_in_text` is a free function used by `BehaviorNode.load_span_facts` and `BddModel.load_source_facts`; the probe belongs on the node that owns the span.

### `use-typed-signatures` — Fail
- nodes.py:22 `private_probe_in_text` returns an untyped `dict` with `line` and `kind` keys, which `rules/observable_behavior.py:14` then indexes by string.

## Judgment — `cdd_guidance/practices/bdd/model/bdd_model.py`

### `prefer-class-operations` — Fail
- bdd_model.py:147 `_parse_sketch` (63 lines) and its four helpers `_owner`, `_current_observation`, `_append_surface_line`, `_apply_fence_block` (bdd_model.py:212 onward) are free functions that take the tree or the owner node as a parameter; they are `BddModel.parse`'s own work.

### `keep-operations-single-responsibility` — Fail
- bdd_model.py:147 `_parse_sketch` reads fences, surface lines, observations, descriptions, and the context stack in one loop with five branches.

### `hide-inner-details` — Fail
- bdd_model.py:113 `setup_at`, `body_at`, `written_at`, and `behavior_nodes` read `setup`, `body`, `contexts`, and `observations` through `getattr` with defaults, because `setup` is never declared on `Description` or `Context` and is attached only while code is parsed (code_spec_model.py:107). The node's fields depend on which reader made it.

### `use-explicit-dependencies` — Fail
- bdd_model.py:59 `load_source_facts` imports `private_probe_in_text`, `code_like_describe_lines`, and `has_signature_marker` inside the method to avoid an import cycle between `bdd_model`, `nodes`, and `spec_source`.

## Judgment — `cdd_guidance/practices/bdd/model/graph_bdd_model.py`

### `do-not-invent-parallel-object-models` — Fail
- graph_bdd_model.py:29 `parse` reads the saved graph JSON itself: node lists by position (`[2]`, `[4]`, `[5]`, `[6]`), edges as tuples, and `model_members` decoded out of Clean Engineering's `root_facts`. That is a second reader of the graph's file format beside `Graph`, and it reaches into Clean Engineering's stored facts instead of asking the graph for the Clean Engineering model.

### `keep-operations-single-responsibility` — Fail
- graph_bdd_model.py:29 `parse` decodes JSON, indexes edges, groups nodes by file, and builds the tree (confirms the graph hit).

### `hide-inner-details` — Fail
- graph_bdd_model.py:35 `self._code` keys the graph's positional lists by id: the layout `Graph.write_json` happens to use is now a contract of the BDD model, and a change to it breaks this reader silently.

### `prefer-class-operations` — Fail
- graph_bdd_model.py:107 `_member_named` is a free function used only by `GraphBddModel._call`.

## Judgment — `cdd_guidance/practices/bdd/model/code_spec_model.py`

### `hold-state-on-the-object-not-in-parameters` — Fail
- code_spec_model.py:40 `render` sets `self._kept` for one call, and every private operation reads it; the previous file's model is per-call state parked on a shared format object.

### `use-typed-signatures` — Fail
- code_spec_model.py:284 `TypeScriptBddModel._block` returns a six-key `dict` (`kind`, `name`, `span`, `inner`, `lines`, `children`) that `_tree`, `_child_blocks`, and `_node` index by string; it is an untyped block object.

### `prefer-class-operations` — Fail
- code_spec_model.py:359 `_behavior_node` is a free function that builds a node and appends it to its parent's children; adding a child is the parent's operation.

### `hide-inner-details` — Fail
- code_spec_model.py:179 `_read_spec` swaps `self.preamble, self.setup = self.setup, CodeBody()`: the spec reuses the `setup` field that `_read_block` writes on every node and then moves it, so `BddModel` briefly carries a `setup` it does not declare.

## Judgment — `cdd_guidance/practices/bdd/model/spec_source.py`

### `prefer-class-operations` — Fail
- spec_source.py:15 `is_spec_file`, `has_signature_marker`, and `code_like_describe_lines` are free functions; the last two are facts `BddModel.load_source_facts` loads about itself, and `is_spec_file` is imported by `harness/graph/working_copy.py:293` and `:804` (the harness importing a practice, part of the cycle in the integrated report §6).

## Judgment — `cdd_guidance/practices/bdd/rules/shared_describe_subject.py`

### `prefer-class-operations` — Fail
- shared_describe_subject.py:13 `_longest_shared_word_prefix` and `branched_top_level_describes` (shared_describe_subject.py:35) are free functions used only by `SharedDescribeSubject.check`.

## Judgment — `cdd_guidance/practices/bdd/bdd.py`

### `limit-comments` — Fail
- bdd.py:13 the docstring says Bdd "Depends on CleanEngineering (lazy import to avoid circular imports at module load time)"; `bdd.py` imports nothing from Clean Engineering.

### `hold-state-on-the-object-not-in-parameters` — Fail
- bdd.py:37 the constructor takes `session` as a name string and hands it to `_attach_workspace`, one of the three ways PracticeGuidance holds its session (integrated report §2).

### `use-consistent-naming` — Fail
- bdd.py:43 the format table names each channel by a `(module path, class name)` string pair, while `clean_engineering.py:46` passes the classes; two mechanisms for one table, and the string form hides the dependency from imports and from the graph.

**Passes:** `model-modules-follow-the-partition`, `shape-classes-around-resources`, `put-logic-on-the-owning-resource`, `use-property-not-accessor`, `external-system-interface-is-one-way`, `avoid-vague-parameter-names`, `errors-out-of-existence`, `state-change-returns-record-or-named-failure`, `domain-exception-carries-context`, `write-invariants`, `write-interactions`, `no-redundant-relationship-paths`, `use-intention-revealing-names`, `one-canonical-model-document`, `do-not-invent-terms`.
