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

**Generated:** 2026-11-07 09:28:22 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 50
**Rules with graph hits:** 13
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

- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L181): OoadClass `PracticeGuidance`: Class 'PracticeGuidance' exposes 14 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L634): OoadClass `FidelityGuidance`: Class 'FidelityGuidance' exposes 12 public operations (budget ~9). Split responsibilities.

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

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L127): OoadClass `RulesCollection`: Class 'RulesCollection' constructs 'AppliesTo' inside its constructor.

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

- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L477): Operation `render`: Operation 'render' takes 4 parameters (maximum 3, excluding self).

Evaluate the current context against this rule (limit-operation-parameters):

### `avoid-vague-parameter-names`

Do not name parameters `data`, `options`, `info`, or other placeholders that could mean anything. A vague name hides what the caller must supply and what the operation does with it.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L145): Operation `inject_rules`: Parameter 'payload' in 'inject_rules' is vague.
- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L145): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.

Evaluate the current context against this rule (avoid-vague-parameter-names):

### `errors-out-of-existence`

For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L699): Operation `new_report_path`: Operation 'new_report_path' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\practice_catalogue.py#L57): Operation `practice_class`: Operation 'practice_class' raises on an empty or missing value; return a quiet result instead.

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

**Graph violations:** 6

- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L664): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L675): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L736): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L745): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L771): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L36): Parameter `value`: Parameter 'value' does not reveal intent.

Evaluate the current context against this rule (use-intention-revealing-names):

### `use-consistent-naming`

Use one word per concept. Pick one verb and use it everywhere (`fetch_`, not a mix of `fetch_`, `get_`, and `retrieve_`). Two words for one concept is how the same logic gets written twice — nobody searching for `fetch_` finds the `retrieve_` that already does the job.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L24): OoadClass `AppliesTo`: Operation 'alwaysApply' uses camelCase while other operations on 'AppliesTo' use the other convention.
- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L127): OoadClass `RulesCollection`: Operation 'appliesTo' uses camelCase while other operations on 'RulesCollection' use the other convention.

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

- [X] **ERROR** **[graph rule]** - [harness/guidance](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance#L1): Module `guidance`: Module 'guidance' splits into many tiny classes (36); prefer a deep module with a small public surface.

Evaluate the current context against this rule (deep-module):

### `keep-operations-small-focused`

Keep each operation short enough to read as one thought — under 20 statements. A multi-line call, list, or string initializer is one statement. When it grows, extract a private helper whose name says why that slice exists.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L145): Operation `inject_rules`: Operation 'inject_rules' is 21 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `missing-module-context`

**Graph violations:** 11

- [X] **ERROR** **[graph rule]** - [harness/guidance/fixtures/agentic_ops/agentic_ops.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\fixtures\agentic_ops\agentic_ops.py#L14): OoadClass `SampleAgenticOps`: Module folder 'agentic_ops' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/fixtures/agentic_ops/agentic_ops.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\fixtures\agentic_ops\agentic_ops.py#L42): OoadClass `SampleMcpOps`: Module folder 'agentic_ops' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/fixtures/agentic_ops/hook_ops.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\fixtures\agentic_ops\hook_ops.py#L10): OoadClass `SampleHookOps`: Module folder 'agentic_ops' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/fixtures/other_tool/other_tool_host.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\fixtures\other_tool\other_tool_host.py#L7): OoadClass `OtherTool`: Module folder 'other_tool' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/fixtures/sample_tool/sample_tool_host.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\fixtures\sample_tool\sample_tool_host.py#L11): OoadClass `SampleTool`: Module folder 'sample_tool' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/fixtures/sample_tool/sample_tool_host.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\fixtures\sample_tool\sample_tool_host.py#L24): OoadClass `SampleGuidance`: Module folder 'sample_tool' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/fixtures/sample_tool/sample_tool_host.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\fixtures\sample_tool\sample_tool_host.py#L30): OoadClass `SampleMcpGuidance`: Module folder 'sample_tool' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/fixtures/sample_tool/sample_tool_host.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\fixtures\sample_tool\sample_tool_host.py#L39): OoadClass `SamplePracticeGuidance`: Module folder 'sample_tool' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/fixtures/sample_tool/sample_tool_host.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\fixtures\sample_tool\sample_tool_host.py#L45): OoadClass `SamplePracticeWithFidelities`: Module folder 'sample_tool' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/fixtures/sample_tool/sample_tool_host.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\fixtures\sample_tool\sample_tool_host.py#L49): OoadClass `SampleMcpPractice`: Module folder 'sample_tool' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/fixtures/split_tool/split_tool.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\fixtures\split_tool\split_tool.py#L7): OoadClass `SplitPracticeGuidance`: Module folder 'split_tool' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.

Evaluate the current context against this rule (missing-module-context):

### `one-way-deps`

Make dependencies flow in one direction without cycles. A cycle prevents either module from changing or being tested independently.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/guidance](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance#L1): Module `guidance`: Circular import between 'guidance' and 'sample_tool' breaks one-way dependencies.

Evaluate the current context against this rule (one-way-deps):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

**Graph violations:** 15

- [X] **ERROR** **[graph rule]** - [harness/guidance/action_catalogue.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\action_catalogue.py#L63): Operation `kits`: Operation 'kits' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/action_catalogue.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\action_catalogue.py#L70): Operation `actions`: Operation 'actions' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/action_catalogue.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\action_catalogue.py#L77): Operation `names`: Operation 'names' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/action_catalogue.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\action_catalogue.py#L81): Operation `has`: Operation 'has' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/action_catalogue.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\action_catalogue.py#L85): Operation `action`: Operation 'action' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L159): Operation `child`: Operation 'child' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\practice_catalogue.py#L31): Operation `keys`: Operation 'keys' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\practice_catalogue.py#L36): Operation `has`: Operation 'has' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\practice_catalogue.py#L40): Operation `practices`: Operation 'practices' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\practice_catalogue.py#L45): Operation `practice`: Operation 'practice' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\practice_catalogue.py#L57): Operation `practice_class`: Operation 'practice_class' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\practice_catalogue.py#L65): Operation `module_of`: Operation 'module_of' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\practice_catalogue.py#L70): Operation `practice_named`: Operation 'practice_named' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\practice_catalogue.py#L79): Operation `toolset_ref`: Operation 'toolset_ref' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L59): Operation `strip_fence`: Operation 'strip_fence' is a classmethod; prefer an instance operation.

Evaluate the current context against this rule (prefer-instance-operations):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 5

- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L477): Parameter `content`: Parameter 'content' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L771): Parameter `value`: Parameter 'value' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L36): Parameter `value`: Parameter 'value' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L378): Parameter `parent`: Parameter 'parent' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L451): Parameter `paths`: Parameter 'paths' needs a domain-specific type, not a generic container.

Evaluate the current context against this rule (use-typed-signatures):

---

# Judgment (round 3, branch 42ab935c)

Judged the classes, operations, and relationships of `harness/guidance` (guidance.py, practice_catalogue.py, action_catalogue.py, rule.py, stages.py, schema.py, schema_map.py) against the model rules, including how the action catalogue treats an operation marked `@noDeploy`. **Graph hits dismissed:** all 11 `missing-module-context` hits and the `one-way-deps` cycle with `sample_tool` (they are spec fixtures under `fixtures/`); `prefer-instance-operations` on the catalogue lookups `keys`, `has`, `practices`, `module_of`, `toolset_ref`, `kits`, `actions`, `names`, `action` (the fixed practice list and the action folders are the registries decision 14 chose; the shared instance from `practice` is judged below); `GuidanceCollection.child` (a creation factory); `errors-out-of-existence` on `new_report_path` (raises the named `FidelityWithoutSessionError` for a fidelity with no session, a real failure); `use-explicit-dependencies` on `RulesCollection` building `AppliesTo` (a value it owns); `limit-operation-parameters` on `render` (judged under `hold-state` below).

## Judgment — `harness/guidance/guidance.py`

### `deep-module` — Fail
- guidance.py:181 **left from rounds 1–2 (§6, refined)** — 12 of the folder's 27 production classes are imported by production code elsewhere (44%, over 40%): `PracticeGuidance`, `FidelityGuidance`, `Guidance`, `GuidanceCollection`, `PracticeCatalogue`, `ActionCatalogue`, `Action`, `Rule`, `RulesCollection`, `Schema`, `ApproachStage`, `StageScope`. The lead's 12 of 17 (71%) undercounted the classes; the public count is the same.

### `do-not-invent-parallel-object-models` — Fail
- guidance.py:84 **left from rounds 1–2 (§2, high)** — `PracticeGuidance` still holds its session three ways: `session` (a name string, set in `Guidance.__init__`), `workspace` (the Session object, typed `Any`), and `path`, all set through `_attach_workspace(path, session, workspace)` (:343, called with all three by the builders and from `space/session/practice_session_output.py:127`), while each fidelity holds a fourth view, `session_output` (:638).
- guidance.py:251 **left from rounds 1–2 (§2)** — the practice key is still computed twice on the practice: `key` (:210, the class file's folder) and `context_index_key` (`AssetLocator(...).class_file_directory().name`), and again on the fidelity (:719); the catalog generator reads the second spelling.

### `hold-state-on-the-object-not-in-parameters` — Fail
- guidance.py:477 **left from rounds 1–2 (§3)** — `render(format, content, source, previous)` still takes the target format on every call, and `_render` hands `format`, `source`, `previous`, and `folder` on to the companion practice and `_call_render`; the practice already holds `format` and its current fidelity, which is where the rule says a chosen format is saved.

### `keep-classes-single-responsibility` — Fail
- guidance.py:181 **left from rounds 1–2 (§5)** — `PracticeGuidance` has 47 methods: guidance text assembly, fidelity and format activation, project rules lookup, rendering through format adapters (including reading a code tree, :542), and session attachment (the comment `## workspace integration to move` at :303 says so itself).

## Judgment — `harness/guidance/practice_catalogue.py`

### `use-explicit-dependencies` — Fail
- practice_catalogue.py:45 **left from rounds 1–2 (§3 `PracticeCatalogue._shared`)** — `practice(key)` hands every caller one mutable instance from class-level `_shared` (:28), guarded only by the docstring "do not change its current fidelity or format"; any caller that sets `format` or attaches a workspace changes what every other caller reads.

## Judgment — `harness/guidance/action_catalogue.py`

### `use-intention-revealing-names` — Fail
- action_catalogue.py:73 **new** — `actions()` counts every `@Skill` operation as an action that a kit "publishes as a skill", but `Validate.createRule` also carries `@noDeploy`, so nothing is installed for it; the catalog still writes `actions/createRule.html` and a `createrule` board tile ("Request used as action: createRule"), and `prompt_notify` and the session log match it as an action people can run.

## Passes

One `PracticeCatalogue` and one `ActionCatalogue` hold the practices and actions (decision 14); the catalog generator, session log, and prompt notifications all read them instead of keeping their own lists. `ApproachStage`/`STAGES` are the one stage definition (decision 15), and `FidelityWithoutSessionError` names the failure it reports.
