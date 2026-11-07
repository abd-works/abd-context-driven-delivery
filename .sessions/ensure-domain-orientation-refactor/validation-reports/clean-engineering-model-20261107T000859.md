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

**Generated:** 2026-11-07 00:08:59 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 68
**Rules with graph hits:** 12
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

- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L179): OoadClass `PracticeGuidance`: Class 'PracticeGuidance' exposes 14 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L642): OoadClass `FidelityGuidance`: Class 'FidelityGuidance' exposes 10 public operations (budget ~9). Split responsibilities.

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

- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L111): OoadClass `RulesCollection`: Class 'RulesCollection' constructs 'AppliesTo' inside its constructor.

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

- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L486): Operation `render`: Operation 'render' takes 4 parameters (maximum 3, excluding self).

Evaluate the current context against this rule (limit-operation-parameters):

### `avoid-vague-parameter-names`

Do not name parameters `data`, `options`, `info`, or other placeholders that could mean anything. A vague name hides what the caller must supply and what the operation does with it.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L129): Operation `inject_rules`: Parameter 'payload' in 'inject_rules' is vague.
- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L129): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.

Evaluate the current context against this rule (avoid-vague-parameter-names):

### `errors-out-of-existence`

For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L691): Operation `new_report_path`: Operation 'new_report_path' raises on an empty or missing value; return a quiet result instead.
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

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L728): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L736): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L763): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L32): Parameter `value`: Parameter 'value' does not reveal intent.

Evaluate the current context against this rule (use-intention-revealing-names):

### `use-consistent-naming`

Use one word per concept. Pick one verb and use it everywhere (`fetch_`, not a mix of `fetch_`, `get_`, and `retrieve_`). Two words for one concept is how the same logic gets written twice — nobody searching for `fetch_` finds the `retrieve_` that already does the job.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L20): OoadClass `AppliesTo`: Operation 'alwaysApply' uses camelCase while other operations on 'AppliesTo' use the other convention.
- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L111): OoadClass `RulesCollection`: Operation 'appliesTo' uses camelCase while other operations on 'RulesCollection' use the other convention.

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

- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance_probe.py#L106): Operation `arguments_for`: Operation 'arguments_for' is 48 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L129): Operation `inject_rules`: Operation 'inject_rules' is 25 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `missing-module-context`

**Graph violations:** 34

- [X] **ERROR** **[graph rule]** - [harness/guidance/__init__.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\__init__.py#L1): OoadClass `_module`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
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
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L39): OoadClass `FidelityWithoutSessionError`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L47): OoadClass `Guidance`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L143): OoadClass `GuidanceCollection`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L179): OoadClass `PracticeGuidance`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L642): OoadClass `FidelityGuidance`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance_diagnose_heavy_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance_diagnose_heavy_spec.py#L1): OoadClass `_module`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance_diagnose_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance_diagnose_spec.py#L1): OoadClass `_module`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance_diagnostics.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance_diagnostics.py#L11): OoadClass `GuidanceDiagnostics`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance_probe.py#L21): OoadClass `GuidanceProbe`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance_spec.py#L1): OoadClass `_module`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\practice_catalogue.py#L12): OoadClass `PracticeCatalogue`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/project_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\project_rules.py#L18): OoadClass `ProjectRulesets`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/project_rules_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\project_rules_spec.py#L21): OoadClass `_Fidelities`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/project_rules_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\project_rules_spec.py#L29): OoadClass `_StoriesRules`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/project_rules_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\project_rules_spec.py#L64): OoadClass `_Node`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L20): OoadClass `AppliesTo`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L61): OoadClass `Rule`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L111): OoadClass `RulesCollection`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/schema.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\schema.py#L26): OoadClass `SchemaType`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/schema.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\schema.py#L49): OoadClass `Schema`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/schema_map.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\schema_map.py#L1): OoadClass `_module`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/schema_map_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\schema_map_spec.py#L1): OoadClass `_module`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.

Evaluate the current context against this rule (missing-module-context):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

**Graph violations:** 10

- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L157): Operation `child`: Operation 'child' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance_probe.py#L31): Operation `filtered_by`: Operation 'filtered_by' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\practice_catalogue.py#L31): Operation `keys`: Operation 'keys' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\practice_catalogue.py#L36): Operation `has`: Operation 'has' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\practice_catalogue.py#L40): Operation `practices`: Operation 'practices' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\practice_catalogue.py#L45): Operation `practice`: Operation 'practice' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\practice_catalogue.py#L57): Operation `practice_class`: Operation 'practice_class' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\practice_catalogue.py#L65): Operation `module_of`: Operation 'module_of' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\practice_catalogue.py#L70): Operation `practice_named`: Operation 'practice_named' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L55): Operation `strip_fence`: Operation 'strip_fence' is a classmethod; prefer an instance operation.

Evaluate the current context against this rule (prefer-instance-operations):

### `simplify-control-flow`

Handle the failing or empty cases first and return. Keep the main path flat. Do not nest more than three levels — deeper than that you cannot tell which conditions hold on a given line without reading back up, and that is where the unhandled branch hides.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance_probe.py#L106): Operation `arguments_for`: Operation 'arguments_for' nests control flow 9 levels deep (max 3).

Evaluate the current context against this rule (simplify-control-flow):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 7

- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L486): Parameter `content`: Parameter 'content' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L763): Parameter `value`: Parameter 'value' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance_probe.py#L31): Parameter `installer`: Parameter 'installer' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance_probe.py#L106): Parameter `member`: Parameter 'member' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L32): Parameter `value`: Parameter 'value' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L383): Parameter `parent`: Parameter 'parent' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L456): Parameter `paths`: Parameter 'paths' needs a domain-specific type, not a generic container.

Evaluate the current context against this rule (use-typed-signatures):

---

# Judgment (model fidelity, judged against the graph this call built)

Scope: the 16 Python classes of `harness/guidance` in this call's graph (fixtures and specs left out). Dismissed graph hits: `missing-module-context` is a modules-fidelity rule (and `harness/guidance/.context/` does exist, holding a model document but no `module-context.md`); `value` on `FidelityGuidance.format`, `default_format`, and `clean_engineering` are property setters, where `value` is the language's convention; `RulesCollection.appliesTo` / `AppliesTo.alwaysApply` keep the camelCase key of the rule front matter they read; `errors-out-of-existence` on `PracticeCatalogue.practice_class` (an unknown practice key is a broken request) and `FidelityGuidance.new_report_path` (`FidelityWithoutSessionError` names a real misuse); `keep-operations-small-focused` / `simplify-control-flow` on `GuidanceProbe.arguments_for` are code-fidelity rules.

## Judgment — `harness/guidance/guidance.py`

### `do-not-invent-parallel-object-models` — Fail
- guidance.py:219 `practice_slug`: a second name for `slug`, published as `slug`, so the practice has two properties for one value.
- guidance.py:235 `fidelity_slugs`: the practice's fidelities copied as slug strings and published as `fidelities`, so readers get strings instead of the FidelityGuidance objects.
- guidance.py:87 `session`: the guidance keeps the session's name as a string (`active_session` at guidance.py:359 returns it) beside `session_output` (guidance.py:213), which already holds the PracticeSessionOutput; two references to one session, one of them a `*_name`-style copy.

### `hold-state-on-the-object-not-in-parameters` — Fail
- guidance.py:486 `render`: takes `format` on every call although the practice holds its fidelities' formats (`formats`, `FidelityGuidance.format`); `source` and `previous` are passed beside it, the P-7 shape.
- guidance.py:491 `render_files`: takes `format` again and passes a folder worked out from the paths down to `_render`.

### `keep-classes-single-responsibility` — Fail
- guidance.py:179 `PracticeGuidance`: 48 methods, 14 public operations and 13 properties covering rules, session files and output paths, rendering, schema reading, examples, and instruction text; reading files (`read_paths`) and rendering are a separate reason to change from describing the practice.
- guidance.py:642 `FidelityGuidance`: 10 public operations and 14 properties mixing description (overview, scaffold, rules) with session outputs and reports (`output_paths`, `files`, `reports`, `new_report_path`).

### `use-typed-signatures` — Fail
- guidance.py:213 `session_output`: typed `Any` although it is always a PracticeSessionOutput.
- guidance.py:486 `render`: `content: Any` and a bare `dict` return.
- guidance.py:763 `clean_engineering`: setter takes `Any` for a FidelityGuidance.

## Judgment — `harness/guidance/practice_catalogue.py`

### `prefer-instance-operations` — Fail
- practice_catalogue.py:45 `practice`: every operation (`keys`, `has`, `practices`, `practice`, `practice_class`, `module_of`, `practice_named`) is a classmethod over the process-wide `_shared` dict at practice_catalogue.py:28, so callers share one global set of practice instances instead of being handed a catalogue.

### `use-explicit-dependencies` — Fail
- practice_catalogue.py:28 `_shared`: a class-level cache of practice instances read by every caller; a caller cannot be given its own catalogue, and a change to a shared practice's current fidelity is seen by all (the docstring has to warn callers not to change it).

## Judgment — `harness/guidance/rule.py`

### `do-not-invent-parallel-object-models` — Fail
- rule.py:77 `attribute_to`: stores the owning practice on the Rule as a string (`self.practice = practice`) instead of a reference to the PracticeGuidance.
- rule.py:167 `practice_key`: RulesCollection publishes its owner's key as a string, and rule.py:174 `fidelity_name` the fidelity's name, read through `getattr` chains, instead of handing the practice and fidelity it belongs to.

### `use-explicit-dependencies` — Fail
- rule.py:162 `inject_rules`: reaches for `Session.current()` to note injected rules instead of the session the rules' practice already works in.

### `use-typed-signatures` — Fail
- rule.py:129 `inject_rules`: `payload: dict[str, Any]`, an untyped hook payload with a vague name.
- rule.py:456 `scan`: `paths: Any`.
- rule.py:383 `from_markdown`: `parent: Any` for the guidance that owns the rules.

## Judgment — `harness/guidance/schema_map.py`

### `prefer-class-operations` — Fail
- schema_map.py:17 `node_fidelities`: one of seven module-level functions (`fidelity_sections`, `fidelity_order`, `schema_fidelity_path`, `load_node_fidelities`, `fidelity_for_node`, `validate_schema_fidelities`) that take a practice's markdown text or folder and do Schema's and PracticeGuidance's work; they belong on `Schema` (schema.py:49) and `PracticeGuidance`.

## Judgment — `harness/guidance/guidance_probe.py`

### `use-typed-signatures` — Fail
- guidance_probe.py:31 `filtered_by`: `installer: Any` for the Installer it probes; guidance_probe.py:106 `arguments_for` takes `member: Any`.

Passes: `vocabulary-traces-to-source`, `do-not-invent-terms`, `model-modules-follow-the-partition`, `shape-classes-around-resources`, `put-logic-on-the-owning-resource` (fidelities answer their own outputs and reports), `hide-inner-details`, `use-property-not-accessor`, `external-system-interface-is-one-way`, `limit-operation-parameters` (only `render`, already failed above), `domain-exception-carries-context`, `no-redundant-relationship-paths` aside from the copies above, `use-consistent-naming`, `eliminate-duplication`.
