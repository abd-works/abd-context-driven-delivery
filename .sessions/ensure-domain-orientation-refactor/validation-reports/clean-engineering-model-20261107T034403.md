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

**Generated:** 2026-11-07 03:44:03 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 79
**Rules with graph hits:** 3
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

**Graph violations:** 26

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/acceptance_tests.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\acceptance_tests.py#L7): OoadClass `DomainFixtureExampleFiles`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/acceptance_tests.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\acceptance_tests.py#L23): OoadClass `ExampleRoleNames`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/acceptance_tests.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\acceptance_tests.py#L37): OoadClass `OriginatingSubEpicExamples`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/acceptance_tests.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\acceptance_tests.py#L49): OoadClass `ExamplesExportDataNotRepository`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L43): OoadClass `AndChaining`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L58): OoadClass `ButMarksMissingState`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L70): OoadClass `WhenHoldsTheOperation`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L85): OoadClass `OutlineRequiresManyPermutations`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L117): OoadClass `ExamplesTraceDomainModel`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L137): OoadClass `WhenNamesIntentNotInterfaceGesture`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L150): OoadClass `BehavioralAndSystemObservableOutcomes`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L163): OoadClass `FlaggedWritesIntendedGwt`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L180): OoadClass `GivenNamesComplexStateRootFirst`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L196): OoadClass `ScenarioNamesContinuation`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L232): OoadClass `ScenariosShape`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L301): OoadClass `PlainEnglishGwtSteps`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L317): OoadClass `GwtStepsTraceToDomainOperations`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L334): OoadClass `DomainOperationInTheStep`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/story_map.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\story_map.py#L11): OoadClass `VerbNounFormat`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/story_map.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\story_map.py#L24): OoadClass `FourToNineChildren`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/story_map.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\story_map.py#L40): OoadClass `StoryScenariosOneToFour`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/story_map.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\story_map.py#L59): OoadClass `KebabCasePaths`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/story_map.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\story_map.py#L70): OoadClass `StoryNameCapturesSystemMechanic`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/story_map.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\story_map.py#L82): OoadClass `RightSizeStoryNodes`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/story_map.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\story_map.py#L94): OoadClass `BranchOnMechanicalUniqueness`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/story_map.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\story_map.py#L107): OoadClass `BehavioursNotOneTimeTasks`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.

Evaluate the current context against this rule (missing-module-context):

### `provide-meaningful-context`

Give a number or literal a name that says why it is there (`SECONDS_PER_DAY`, not `86400`). Do not number variables (`item1`).

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L200): Operation `check`: Operation 'check' uses the unnamed number 12.

Evaluate the current context against this rule (provide-meaningful-context):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 52

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/acceptance_tests.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\acceptance_tests.py#L11): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/acceptance_tests.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\acceptance_tests.py#L11): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/acceptance_tests.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\acceptance_tests.py#L27): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/acceptance_tests.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\acceptance_tests.py#L27): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/acceptance_tests.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\acceptance_tests.py#L41): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/acceptance_tests.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\acceptance_tests.py#L41): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/acceptance_tests.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\acceptance_tests.py#L53): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/acceptance_tests.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\acceptance_tests.py#L53): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L47): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L47): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L62): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L62): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L74): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L74): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L89): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L89): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L121): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L121): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L141): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L141): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L154): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L154): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L167): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L167): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L184): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L184): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L200): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L200): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L236): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L236): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L305): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L305): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L321): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L321): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L338): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/scenarios.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\scenarios.py#L338): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/story_map.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\story_map.py#L15): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/story_map.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\story_map.py#L15): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/story_map.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\story_map.py#L28): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/story_map.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\story_map.py#L28): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/story_map.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\story_map.py#L47): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/story_map.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\story_map.py#L47): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/story_map.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\story_map.py#L63): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/story_map.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\story_map.py#L63): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/story_map.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\story_map.py#L74): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/story_map.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\story_map.py#L74): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/story_map.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\story_map.py#L88): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/story_map.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\story_map.py#L88): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/story_map.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\story_map.py#L98): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/story_map.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\story_map.py#L98): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/story_map.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\story_map.py#L111): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/rules/story_map.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\rules\story_map.py#L111): Parameter `context`: Parameter 'context' is missing a type annotation.

Evaluate the current context against this rule (use-typed-signatures):

## Judgment — `cdd_guidance/practices/stories/rules/scenarios.py`

### `prefer-class-operations` — Fail
- scenarios.py:22 `scenario_of(node)`: a free function that takes the graph node and reaches into `node.model`; the node should answer its own parsed scenario.
- scenarios.py:27 `story_of(node, context)`: free function that asks the practice for the node's parent; the Scenario node owns its parent link.
- scenarios.py:283 `_keyword(step)`, `_text` (:288), `_phase` (:293), `_step_keyword` (:298): four free functions that each read one fact off a Step node. Step's keyword, text, and phase are the Step's own properties; every rule re-derives them through these helpers instead.
- scenarios.py:105 `scenario_domain_concepts(steps)`: walks a scenario's steps and their `ands` to collect concepts less actors; this is the Scenario's derived property, written here as a free function.

### `eliminate-duplication` — Fail
- scenarios.py:47 `AndChaining.check`: the rule is written twice, once over the parsed scenario (`when_then_runs`, line 51) and once over graph children (`_and_chaining_from_graph`, line 212), and the two disagree: only the graph path flags a scenario that ends after a When with no Then. Which answer a user gets depends on whether the graph came from a live load or from `graph.json`. This is the node-plus-parsed-object split (1.4 Mode B, integrated report §2) producing two rule bodies.
- scenarios.py:90 `OutlineRequiresManyPermutations`, :168 `FlaggedWritesIntendedGwt`, :125 `ExamplesTraceDomainModel`: each rule merges a graph answer with a `node.model` answer by hand (`outline or scenario.is_outline`, `max(examples, example_count(...))`), and `ExamplesTraceDomainModel` returns no finding at all for a graph reloaded from JSON (line 123). Same root cause as above.
- scenarios.py:271 `_parent_story`: a second way to find a scenario's story (walk `parent`, then scan `edges["scenarios"]`) beside `story_of` (line 27, `direct_parent`). Two lookups of one relationship in one file.
- scenarios.py:75 the gate "keyword is X or blank, unless the node type is X" is written five times (:75, :142, :155, :185, :201) with slightly different shapes; :75-77 nests it differently from the other four.
- scenarios.py:324 `GwtStepsTraceToDomainOperations` repeats the identifier check of `PlainEnglishGwtSteps` (:311), so one code-like step is reported by two rules for the same reason.

### `do-not-invent-terms` — Fail
- scenarios.py:190 `GivenNamesComplexStateRootFirst`: decides whether a Given "opens with the aggregate root" by matching the literal words `root|aggregate|cart|order|account`. Those are words from one sample domain, not the project's model; any real project's root names (Ticket, Session, Screen) always fail. The aggregate root belongs to the DDD model, which this rule never reads.

### `provide-meaningful-context` — Fail
- scenarios.py:206 `ScenarioNamesContinuation.check`: the unnamed limit `12` words (graph hit, confirmed).
- scenarios.py:188 `GivenNamesComplexStateRootFirst.check`: the unnamed limit `8` words (missed by the scanner).
- scenarios.py:99 `OutlineRequiresManyPermutations.check`: the unnamed limit `2` example sets.

### `limit-comments` — Fail
- scenarios.py:313 `PlainEnglishGwtSteps.check`: the final `if ...: return []` followed by `return []` is a dead branch; both paths return the same thing.

### `use-typed-signatures` — Fail
- scenarios.py:47 every `check(self, node, context)` override (14 in this file) drops the base's `RuleCheckContext` annotation, and the base `PracticeGraphRule.check` (`harness/graph/practice_rule.py:15`) leaves `node` untyped too. One finding for the 52 graph hits across the three files; fix it once on the base and in each override.

## Judgment — `cdd_guidance/practices/stories/rules/story_map.py`

### `use-intention-revealing-names` — Fail
- story_map.py:40 `StoryScenariosOneToFour`: the class name and slug `story-scenarios-one-to-four` promise 1-4 scenarios, but the rule allows up to `_MOST_SCENARIOS = 7` (line 8) and its docstring says "at most 7". A reader searching for the 1-4 limit finds a rule that enforces 7.

### `limit-comments` — Fail
- story_map.py:29 `FourToNineChildren.check`: `if node.type in {"Story", "Scenario"}: return []` can never be true because `node_types` is `("Epic", "SubEpic")`; dead code.

### `put-logic-on-the-owning-resource` — Fail
- story_map.py:36 `FourToNineChildren.check`: `node.type.lower().replace("subepic", "sub-epic")` re-derives the display name of a node type that the Stories model already names; the same spelling is repeated across the format adapters (see the stories/model reports).

## Judgment — `cdd_guidance/practices/stories/rules/acceptance_tests.py`

### `put-logic-on-the-owning-resource` — Fail
- acceptance_tests.py:15 `DomainFixtureExampleFiles.check`: hard-codes `.ts` (`module.lower() + ".ts"`, `endswith(".examples.ts")`), although Stories writes acceptance tests in Python, Java, and JavaScript too. The file suffix for a language belongs to `Format`; every Python or Java example file fails this rule. (Suffix tables copied beside `Format.from_extension` are known, §4; this instance is new.)
- acceptance_tests.py:45 `OriginatingSubEpicExamples.check`: decides epic versus sub-epic versus story by substrings of the file path (`"epic" in path`, `"story" not in path`). The Example node's owning story or sub-epic is a graph relationship; reading it from folder spelling misfires whenever a folder name contains "story" or "epic".

## Judgment — `cdd_guidance/practices/stories/rules/__init__.py`

### `do-not-invent-parallel-object-models` — Fail
- __init__.py:36 `RULES` and `BY_SLUG` (line 65): a hand-kept list of rule instances and a slug-keyed registry beside the rule classes themselves; every new rule must be added in three places (class, import, tuple). Known: integrated report §2 (rules keyed by practice name, registries).

**Passes:** the rule classes are small, single-purpose `PracticeGraphRule` subtypes with no state; `keep-classes-single-responsibility`, `shape-classes-around-resources`, `limit-operation-parameters`, `errors-out-of-existence`, `use-explicit-dependencies` pass.

**Graph hits dismissed:** all 26 `missing-module-context` hits on `rules/` — the folder rolls up into `cdd_guidance/practices/stories/.context/module-context.md`, which exists. The 52 `use-typed-signatures` hits are confirmed and grouped into one finding above.
