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

**Generated:** 2026-11-07 00:11:51 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 99
**Rules with graph hits:** 10
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

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L1284): Operation `substitute_template`: Operation 'substitute_template' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_probe.py#L247): Operation `invoke_one`: Operation 'invoke_one' takes 4 parameters (maximum 3, excluding self).

Evaluate the current context against this rule (limit-operation-parameters):

### `avoid-vague-parameter-names`

Do not name parameters `data`, `options`, `info`, or other placeholders that could mean anything. A vague name hides what the caller must supply and what the operation does with it.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L985): Operation `on_stop`: Parameter 'payload' in 'on_stop' is vague.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L985): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.

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

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L222): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L754): Parameter `item`: Parameter 'item' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/sub_agent/mark.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\sub_agent\mark.py#L40): Parameter `fn`: Parameter 'fn' does not reveal intent.

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

- [X] **ERROR** **[graph rule]** - [harness/agent_tools](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools#L1): Module `agent_tools`: Module 'agent_tools' splits into many tiny classes (70); prefer a deep module with a small public surface.

Evaluate the current context against this rule (deep-module):

### `keep-operations-small-focused`

Keep each operation short enough to read as one thought — under 20 statements. A multi-line call, list, or string initializer is one statement. When it grows, extract a private helper whose name says why that slice exists.

**Graph violations:** 6

- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L794): Operation `from_items`: Operation 'from_items' is 28 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L2115): Operation `annotate`: Operation 'annotate' is 25 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L2156): Operation `annotate`: Operation 'annotate' is 27 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_probe.py#L175): Operation `invoke`: Operation 'invoke' is 31 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_probe.py#L207): Operation `heavy_invoke`: Operation 'heavy_invoke' is 39 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_probe.py#L247): Operation `invoke_one`: Operation 'invoke_one' is 35 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `language-modules-one-section`

**Graph violations:** 58

- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L24): OoadClass `AgentToolValidationError`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L45): OoadClass `ExpansionMode`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L64): OoadClass `ExpansionResult`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L76): OoadClass `_LoopItem`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L84): OoadClass `ToolSetCollection`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L134): OoadClass `Collect`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L209): OoadClass `AgentToolSetOrigin`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L246): OoadClass `AgentToolSetTools`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L291): OoadClass `AgentToolSet`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L895): OoadClass `InstallDestination`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L903): OoadClass `AgentToolDestination`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L983): OoadClass `AgentTool`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L1175): OoadClass `AgentOperation`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L1182): OoadClass `GuidanceAgentOperation`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L1203): OoadClass `AgentInstructions`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L2088): OoadClass `AgentToolMark`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L2094): OoadClass `AgentInstructionsMark`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L2100): OoadClass `AgentToolSetMark`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L2142): OoadClass `ToolSetCollectionMark`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L2185): OoadClass `NoSessionLog`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L2193): OoadClass `ToolSubject`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L2202): OoadClass `OnSubject`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_diagnostics.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_diagnostics.py#L11): OoadClass `AgentToolsDiagnostics`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_diagnostics_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_diagnostics_spec.py#L1): OoadClass `_module`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_probe.py#L78): OoadClass `ProbeRequiresServingHost`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_probe.py#L82): OoadClass `AgentToolsProbe`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L49): OoadClass `CarInstance`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L63): OoadClass `_ModeFixture`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L77): OoadClass `_SelfCallAgent`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L101): OoadClass `_BodyModeFlipAgent`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L126): OoadClass `_CalleeAgent`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L143): OoadClass `_CallerAgent`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L162): OoadClass `_PropertyCallerAgent`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L609): OoadClass `_ForEachCallee`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L623): OoadClass `_ForEachCaller`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L667): OoadClass `_ScannerKit`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L674): OoadClass `_HostWithScanner`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L686): OoadClass `_ScanCaller`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L701): OoadClass `_BrokenProvider`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L780): OoadClass `_RulesPropertyHost`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L789): OoadClass `_PracticeWithRules`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L796): OoadClass `_NestedRulesCaller`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L833): OoadClass `_ExecBodyAgent`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L978): OoadClass `_DestinationFixture`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L1018): OoadClass `_BundleTools`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L1027): OoadClass `_PropertyHost`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L1039): OoadClass `_NestedChild`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L1046): OoadClass `_MarkedBag`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L1051): OoadClass `_NestedParent`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L1063): OoadClass `_TwoCollections`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L1081): OoadClass `_CollectChild`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L1088): OoadClass `_WrappedBag`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L1095): OoadClass `_CollectBag`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L1184): OoadClass `Parcel`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/cdd_diagnostic_bridge.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\cdd_diagnostic_bridge.py#L1): OoadClass `_module`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/name.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\name.py#L11): OoadClass `Name`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/parameter_schema.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\parameter_schema.py#L25): OoadClass `ParameterSchema`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/progress.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\progress.py#L1): OoadClass `_module`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.

Evaluate the current context against this rule (language-modules-one-section):

### `missing-module-context`

**Graph violations:** 12

- [X] **ERROR** **[graph rule]** - [harness/agent_tools/_examples/logged_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\_examples\logged_probe.py#L8): OoadClass `LoggedProbe`: Module folder '_examples' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/_examples/reporter/reporter.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\_examples\reporter\reporter.py#L12): OoadClass `Reporter`: Module folder 'reporter' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/_examples/super_delegation/super_delegation_demo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\_examples\super_delegation\super_delegation_demo.py#L13): OoadClass `SuperBase`: Module folder 'super_delegation' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/_examples/super_delegation/super_delegation_demo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\_examples\super_delegation\super_delegation_demo.py#L30): OoadClass `ExplicitSuperChild`: Module folder 'super_delegation' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/_examples/super_delegation/super_delegation_demo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\_examples\super_delegation\super_delegation_demo.py#L42): OoadClass `EmptySuperChild`: Module folder 'super_delegation' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/_examples/super_delegation/super_delegation_demo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\_examples\super_delegation\super_delegation_demo.py#L50): OoadClass `EmptyWithReturn`: Module folder 'super_delegation' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/_examples/templated_md.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\_examples\templated_md.py#L8): OoadClass `TemplatedMdDemo`: Module folder '_examples' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/sub_agent/__init__.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\sub_agent\__init__.py#L1): OoadClass `_module`: Module folder 'sub_agent' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/sub_agent/fixtures.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\sub_agent\fixtures.py#L6): OoadClass `MarkedToolExample`: Module folder 'sub_agent' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/sub_agent/fixtures.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\sub_agent\fixtures.py#L15): OoadClass `MarkedActionExample`: Module folder 'sub_agent' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/sub_agent/mark.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\sub_agent\mark.py#L29): OoadClass `SubAgentMark`: Module folder 'sub_agent' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/sub_agent/sub_agent.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\sub_agent\sub_agent.py#L11): OoadClass `SubAgent`: Module folder 'sub_agent' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.

Evaluate the current context against this rule (missing-module-context):

### `one-way-deps`

Make dependencies flow in one direction without cycles. A cycle prevents either module from changing or being tested independently.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/agent_tools](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools#L1): Module `agent_tools`: Circular import between 'agent_tools' and '_examples' breaks one-way dependencies.

Evaluate the current context against this rule (one-way-deps):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

**Graph violations:** 7

- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L155): Operation `of`: Operation 'of' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L754): Operation `instantiate`: Operation 'instantiate' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L781): Operation `tool_subject_of`: Operation 'tool_subject_of' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L790): Operation `instantiate_all`: Operation 'instantiate_all' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L1224): Operation `for_callable`: Operation 'for_callable' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L1284): Operation `substitute_template`: Operation 'substitute_template' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L1198): Operation `receive`: Operation 'receive' is a classmethod; prefer an instance operation.

Evaluate the current context against this rule (prefer-instance-operations):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 7

- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L113): Parameter `instance`: Parameter 'instance' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L155): Parameter `collection`: Parameter 'collection' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L155): Parameter `return_type`: Parameter 'return_type' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L754): Parameter `item`: Parameter 'item' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L2156): Parameter `target`: Parameter 'target' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_probe.py#L207): Parameter `host`: Parameter 'host' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_probe.py#L247): Parameter `host`: Parameter 'host' needs a domain-specific type, not a generic container.

Evaluate the current context against this rule (use-typed-signatures):

---

# Judgment (model fidelity, judged against the graph this call built)

Scope: the 34 Python classes of `harness/agent_tools` and `harness/agent_tools/sub_agent` in this call's graph (`_examples` left out). Dismissed graph hits: `language-modules-one-section` and `missing-module-context` are modules/language rules about the module context, not the object model; `keep-operations-small-focused` is a code-fidelity rule; `instantiate`, `instantiate_all`, `for_callable`, `Collect.of`, and `tool_subject_of` are factories or class-level lookups of a decorated class, which the factory exemption covers; `value` on `AgentToolSetOrigin.name` is a property setter; `fn` on `SubAgentMark.annotate` is the decorated function, which the decorator protocol names.

## Judgment — `harness/agent_tools/agent_tools.py`

### `keep-classes-single-responsibility` — Fail
- agent_tools.py:1203 `AgentInstructions`: 71 methods and 12 instance fields; it parses a recipe's Python source, walks its AST, expands templates and loops, tracks visited members, and invokes tools — several reasons to change in one class.
- agent_tools.py:291 `AgentToolSet`: 47 methods mixing discovery of marked members, source scanning (`provider_cross_call`), instantiation from refs (`instantiate`, `from_items`), and validation.

### `hold-state-on-the-object-not-in-parameters` — Fail
- agent_tools.py:1296 `expand`: each expansion writes its arguments, execution locals, loop modes, and mode onto the shared AgentInstructions (`_scan_arguments`, `_execution_locals`, `_loop_item_modes`, `_mode` at agent_tools.py:1298-1322) and `scan_with_visited` at agent_tools.py:1361 writes `_scan_visited`; state for one expansion is set on an object every call shares.
- agent_tools.py:1042 `log_session_invocation`: the session is found per call from the call's arguments through `toolset.call_session(payload)`, else `Session.current()` at agent_tools.py:1051, instead of from the toolset the tool belongs to.

### `use-explicit-dependencies` — Fail
- agent_tools.py:1051 `log_session_invocation`: falls back to the global `Session.current()`.

### `write-interactions` — Fail
- agent_tools.py:1190 `GuidanceAgentOperation.log_session_invocation`: calls `toolset._log_running_action(action)`, a private operation of GuidanceAction, and asks for `call_session` only for its side effect of binding guidance.
- agent_tools.py:1050 `log_session_invocation`: finds `call_session` on its toolset with `getattr` instead of through a named operation of a type it is given.

### `use-typed-signatures` — Fail
- agent_tools.py:113 `bind`: `instance: Any`; agent_tools.py:155 `Collect.of` takes `collection: Any` and `return_type: Any`; agent_tools.py:754 `instantiate` takes `item: Any`; agent_tools.py:2156 `annotate` takes `target: Any`.
- agent_tools.py:794 `from_items`: `items: list[Any]` and `context: dict[str, object]`.

### `use-consistent-naming` — Fail
- agent_tools.py:994 `registration_name`: AgentTool carries `slug`, `registration_name`, `deploy_name`, and `mcp_name` (agent_tools.py:990-1004), and AgentToolSetOrigin and ToolSetCollection each repeat `slug` and `registration_name`; four names for one tool's identity, each defined again per class.

## Judgment — `harness/agent_tools/agent_tools_probe.py`

### `use-typed-signatures` — Fail
- agent_tools_probe.py:175 `invoke`: `host: Any`, and agent_tools_probe.py:207 `heavy_invoke` and agent_tools_probe.py:247 `invoke_one` likewise, although it is always the MCP host.

### `prefer-class-operations` — Fail
- agent_tools_probe.py:57 `_probe_progress`: AgentToolsProbe still leans on about seven module-level helpers (`_invoke_skip_reason`, `_signature_parameter_names`, `_builtin_workspace_probe_arguments`, `_missing_required_arguments`, `_slug_for_toolset_ref`, ...) that take its tools as parameters (P-26 partly done).

## Judgment — `harness/agent_tools/progress.py`

### `prefer-class-operations` — Fail
- progress.py:15 `report_progress`: module-level functions over a module-level `ContextVar` reporter (progress.py:12) instead of a progress reporter object handed to the work that reports.

## Judgment — `harness/agent_tools/cdd_diagnostic_bridge.py`

### `prefer-class-operations` — Fail
- cdd_diagnostic_bridge.py:21 `probe_arguments_from_cdd_diagnostic`: a free function taking a tool's MCP name and the repo root; it is AgentToolsProbe's job.

## Judgment — `harness/agent_tools/sub_agent/mark.py`

### `model-modules-follow-the-partition` — Fail
- mark.py:29 `SubAgentMark`: the graph shows a two-way dependency between `harness/agent_tools` and `harness/agent_tools/sub_agent` (agent_tools.py:1091 imports `sub_agent.mark`, and `sub_agent` imports `agent_tools`), so the nested package is not a separate module with a one-way seam; the graph also shows `harness/agent_tools` depending on `_examples`.

Passes: `vocabulary-traces-to-source`, `do-not-invent-terms`, `do-not-invent-parallel-object-models` (AgentTool is the one operation model; the name spellings are judged under consistent naming), `class-not-property-instance-or-subtype`, `shape-classes-around-resources`, `hide-inner-details`, `use-property-not-accessor`, `external-system-interface-is-one-way`, `limit-operation-parameters` (`substitute_template` and `invoke_one` aside, both covered above), `errors-out-of-existence`, `domain-exception-carries-context`, `no-redundant-relationship-paths`, `eliminate-duplication`.
