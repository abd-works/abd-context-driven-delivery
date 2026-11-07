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

**Generated:** 2026-11-07 03:45:23 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 75
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

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/brace_story.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\brace_story.py#L116): OoadClass `BraceStoryModel`: Class 'BraceStoryModel' exposes 15 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/code_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\code_story_model.py#L104): OoadClass `CodeScenario`: Class 'CodeScenario' exposes 10 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/code_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\code_story_model.py#L330): OoadClass `CodeStoryModel`: Class 'CodeStoryModel' exposes 40 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\story_model.py#L608): OoadClass `Epic`: Class 'Epic' exposes 12 public operations (budget ~9). Split responsibilities.

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

**Graph violations:** 7

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\story_model.py#L32): OoadClass `StoryNode`: Class 'StoryNode' constructs 'CodeBody' inside its constructor.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\story_model.py#L335): OoadClass `Step`: Class 'Step' constructs 'CodeBody' inside its constructor.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\story_model.py#L453): OoadClass `Background`: Class 'Background' constructs 'Examples' inside its constructor.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\story_model.py#L497): OoadClass `Scenario`: Class 'Scenario' constructs 'Examples' inside its constructor.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\story_model.py#L608): OoadClass `Epic`: Class 'Epic' constructs 'Examples' inside its constructor.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\story_model.py#L786): OoadClass `Story`: Class 'Story' constructs 'Background' inside its constructor.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\story_model.py#L883): OoadClass `StoryModel`: Class 'StoryModel' constructs 'Examples' inside its constructor.

Evaluate the current context against this rule (use-explicit-dependencies):

### `external-system-interface-is-one-way`

Let a domain wrapper or collaborator depend on the named external-system contract. Keep the external type independent of domain wrappers and domain types, because a reverse dependency makes the external boundary depend on one caller's model.

Evaluate the current context against this rule (external-system-interface-is-one-way):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/code_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\code_story_model.py#L372): Operation `render`: Operation 'render' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/code_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\code_story_model.py#L657): Operation `parse`: Operation 'parse' mixes I/O-style calls with domain calculation; split responsibilities.

Evaluate the current context against this rule (keep-operations-single-responsibility):

### `limit-operation-parameters`

Have callers pass intent, not setup. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

Evaluate the current context against this rule (limit-operation-parameters):

### `avoid-vague-parameter-names`

Do not name parameters `data`, `options`, `info`, or other placeholders that could mean anything. A vague name hides what the caller must supply and what the operation does with it.

Evaluate the current context against this rule (avoid-vague-parameter-names):

### `errors-out-of-existence`

For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/code_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\code_story_model.py#L742): Operation `sub_epic_for`: Operation 'sub_epic_for' raises on an empty or missing value; return a quiet result instead.

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

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/code_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\code_story_model.py#L173): Operation `steps_from`: Operation 'steps_from' is 24 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/code_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\code_story_model.py#L626): Operation `load`: Operation 'load' is 30 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/code_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\code_story_model.py#L676): Operation `take_sub_epic_file`: Operation 'take_sub_epic_file' is 30 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\story_model.py#L549): Operation `when_then_runs`: Operation 'when_then_runs' is 21 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\story_model.py#L935): Operation `load`: Operation 'load' is 23 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `missing-module-context`

**Graph violations:** 28

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/brace_story.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\brace_story.py#L13): OoadClass `BraceScenario`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/brace_story.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\brace_story.py#L116): OoadClass `BraceStoryModel`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/code_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\code_story_model.py#L48): OoadClass `CodeStoryModelError`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/code_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\code_story_model.py#L84): OoadClass `CodeStoryNode`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/code_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\code_story_model.py#L104): OoadClass `CodeScenario`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/code_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\code_story_model.py#L229): OoadClass `CodeStory`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/code_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\code_story_model.py#L304): OoadClass `CodeIncrement`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/code_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\code_story_model.py#L308): OoadClass `CodeEpic`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/code_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\code_story_model.py#L330): OoadClass `CodeStoryModel`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/diagram_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\diagram_story_model.py#L10): OoadClass `DiagramStoryNode`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/diagram_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\diagram_story_model.py#L107): OoadClass `DiagramEpic`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/diagram_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\diagram_story_model.py#L122): OoadClass `DiagramStory`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/diagram_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\diagram_story_model.py#L135): OoadClass `DiagramIncrement`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/diagram_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\diagram_story_model.py#L143): OoadClass `DiagramStoryModel`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/graph_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\graph_story_model.py#L49): OoadClass `GraphStoryModel`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\story_model.py#L32): OoadClass `StoryNode`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\story_model.py#L186): OoadClass `Example`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\story_model.py#L240): OoadClass `Examples`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\story_model.py#L281): OoadClass `Increment`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\story_model.py#L335): OoadClass `Step`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\story_model.py#L453): OoadClass `Background`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\story_model.py#L489): OoadClass `StepType`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\story_model.py#L497): OoadClass `Scenario`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\story_model.py#L602): OoadClass `StoryType`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\story_model.py#L608): OoadClass `Epic`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\story_model.py#L786): OoadClass `Story`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\story_model.py#L883): OoadClass `StoryModel`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\story_model.py#L1119): OoadClass `StoryModelFactory`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.

Evaluate the current context against this rule (missing-module-context):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

**Graph violations:** 16

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/brace_story.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\brace_story.py#L31): Operation `without_background`: Operation 'without_background' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/brace_story.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\brace_story.py#L47): Operation `scenario_blocks`: Operation 'scenario_blocks' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/brace_story.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\brace_story.py#L57): Operation `backgrounds_in`: Operation 'backgrounds_in' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/brace_story.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\brace_story.py#L90): Operation `example_names`: Operation 'example_names' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/code_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\code_story_model.py#L100): Operation `name_from_slug`: Operation 'name_from_slug' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/code_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\code_story_model.py#L121): Operation `background_lines`: Operation 'background_lines' is a staticmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/code_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\code_story_model.py#L157): Operation `scenario_blocks`: Operation 'scenario_blocks' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/code_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\code_story_model.py#L161): Operation `backgrounds_in`: Operation 'backgrounds_in' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/code_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\code_story_model.py#L165): Operation `example_names`: Operation 'example_names' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/code_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\code_story_model.py#L173): Operation `steps_from`: Operation 'steps_from' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/code_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\code_story_model.py#L199): Operation `balanced`: Operation 'balanced' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/code_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\code_story_model.py#L211): Operation `outside_scenarios`: Operation 'outside_scenarios' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/code_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\code_story_model.py#L233): Operation `load_all`: Operation 'load_all' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/code_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\code_story_model.py#L247): Operation `background_example_line`: Operation 'background_example_line' is a staticmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/code_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\code_story_model.py#L310): Operation `epic_name_in`: Operation 'epic_name_in' is a staticmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\story_model.py#L960): Operation `load_files`: Operation 'load_files' is a classmethod; prefer an instance operation.

Evaluate the current context against this rule (prefer-instance-operations):

### `provide-meaningful-context`

Give a number or literal a name that says why it is there (`SECONDS_PER_DAY`, not `86400`). Do not number variables (`item1`).

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\story_model.py#L754): Operation `diagram_span_columns`: Operation 'diagram_span_columns' uses the unnamed number 22.

Evaluate the current context against this rule (provide-meaningful-context):

### `simplify-control-flow`

Handle the failing or empty cases first and return. Keep the main path flat. Do not nest more than three levels — deeper than that you cannot tell which conditions hold on a given line without reading back up, and that is where the unhandled branch hides.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/code_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\code_story_model.py#L199): Operation `balanced`: Operation 'balanced' nests control flow 4 levels deep (max 3).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/code_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\code_story_model.py#L270): Operation `fill`: Operation 'fill' nests control flow 4 levels deep (max 3).

Evaluate the current context against this rule (simplify-control-flow):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 9

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/code_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\code_story_model.py#L121): Parameter `scenario`: Parameter 'scenario' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/code_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\code_story_model.py#L169): Parameter `scenario`: Parameter 'scenario' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/graph_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\graph_story_model.py#L61): Parameter `practice`: Parameter 'practice' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/graph_story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\graph_story_model.py#L61): Parameter `on_node`: Parameter 'on_node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\story_model.py#L935): Parameter `root`: Parameter 'root' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\story_model.py#L935): Parameter `on_file`: Parameter 'on_file' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\story_model.py#L960): Parameter `files`: Parameter 'files' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\story_model.py#L960): Parameter `project`: Parameter 'project' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\story_model.py#L960): Parameter `on_file`: Parameter 'on_file' is missing a type annotation.

Evaluate the current context against this rule (use-typed-signatures):


---

# AI judgment (model fidelity, stories/model top-level files, sub-judge)

## Judgment — `cdd_guidance/practices/stories/model/story_model.py`

### `do-not-invent-parallel-object-models` — Fail
- story_model.py:516 `Scenario.story_name`: a `*_name` copy of the Story that already holds the scenario in `Story._scenarios`; graph_story_model.py:144 copies it again into node facts and markdown/nodes.py:740 matches on it, so a renamed Story leaves its scenarios naming the old story.
- story_model.py:1119 `StoryModelFactory`: a second loader beside `StoryModel.load` and `StoryModel.load_files`, with one caller (`story_channel.feature.py:239`); three entry points for "read a story map" means a fix to one never reaches the others.

### `eliminate-duplication` — Fail
- story_model.py:621 `Epic.__init__(source)`: every node has two copy paths, the copy-constructor and `clone()`, and they already diverge: the constructor leaves `examples` empty while `Epic.clone` (story_model.py:668) copies them. Any channel model built from a canonical map (`CodeStoryModel._copy_of`, drawio `type(self)(markdown.parse(body))`) loses the epic-level examples markdown reads at markdown/nodes.py:1127.
- story_model.py:918 `StoryModel._copy_map`: drops the map's own `examples`, while `StoryModel.clone` (story_model.py:1077) keeps them; the same divergence one level up.
- story_model.py:1016 `every_story`: one of four hand-written walks of the epic tree (`CodeStoryModel.all_epics` code_story_model.py:582, `GraphStoryModel._story_count` and `_file_under` graph_story_model.py:79 and :210).
- story_model.py:699 `_stamp_source`: with `_stamp_epic` (:716), `_stamp_story` (:725) and `place_in` (:706) this is four operations that stamp a SourceLocation onto a subtree, each called from a different format reader (json/nodes.py:120, markdown/nodes.py:1262 and :1267).
- story_model.py:66 `StoryNode._VERBS`: a hand list of verbs that decides whether a name opens with a verb; verb_noun.py:10 decides the same thing with NLTK part-of-speech tags, and rules/story_map `VerbNounFormat` a third time.
- story_model.py:1090 `story_test_type`: the story-test suffix table (`_story.test.py/.ts/.js`) is written again in code_story_model.py:728 `_file_stem_slug` and in each language's `LEAF_EXTENSION` (known, integrated report section 4, suffix tables).

### `keep-classes-single-responsibility` — Fail
- story_model.py:32 `StoryNode`: one class is the graph node, the carrier of code read from a language (`written`, `setup`, `take_code_from`), and the story-map linter (verb, actor, gerund and nominalisation word lists, `_classify_opening`, `_camel_case_file`); a change to a lint word list edits the base of every story node.
- story_model.py:608 `Epic` (graph hit confirmed, 12 public operations): tree membership, diagram layout (`span_columns`, `layout_column_count`, `diagram_span_columns`, `tree_depth`, `estimate_label`) and source stamping. The layout belongs on `DiagramEpic`; `layout_column_count` (:746) has no caller.
- story_model.py:883 `StoryModel`: the map plus folder discovery (`load`, `load_files`, `_maps_beside`, `_nearest_map`, `_story_map_at`, `_story_map_file`).

### `use-explicit-dependencies` — Fail
- story_model.py:939 `StoryModel.load`: the base class imports and constructs its own format subclasses (`JsonStoryModel`, `MarkdownStoryModel`, and at :1028 `DrawIOStoryModel`; :1096-:1104 `PythonStory`, `TypeScriptStory`, `JavaScriptStory`), so the base model depends on every adapter built on it and cannot be loaded or tested without all of them.

### `prefer-class-operations` — Fail
- story_model.py:1090 `story_test_type(path)` and `is_story_map_file(path)` (:1110): module functions that decide a file's story type; they belong on the story-file type (or `Format`) the rest of the code already uses for suffixes.
- story_model.py:449 `_steps_key(steps)`: a helper Background and Scenario share; it belongs on the step list they own.

### `use-consistent-naming` — Fail
- story_model.py:411 `Step.continuation`: a second name for `is_continuation` (:405), kept "for the fact name rules read"; two names for one fact.

### `hide-inner-details` — Fail
- story_model.py:240 `Examples(dict)`: the example map is a public `dict` subclass, so callers replace it with a plain dict (markdown/nodes.py:1127 `holder.examples = ... or {}`), which skips the scope linking in `__setitem__`.

### `use-property-not-accessor` — Fail
- story_model.py:104 `StoryNode.__init__`: thirteen derived lint facts (`opening_token`, `opening_class`, `child_count`, `child_band`, `near_duplicate`, `shared_verb`, ...) are stored fields that hold true only after someone calls `load_map_facts`; they derive from the name and children and should be properties, not state that goes stale when a child is added.

### `provide-meaningful-context` — Fail
- story_model.py:767 `diagram_span_columns`: unnamed layout numbers 2, 8, 12, 18, 22, 15, 5 (graph hit confirmed).

### `keep-operations-small-focused` — Fail
- story_model.py:935 `StoryModel.load` (graph hit confirmed): three fallback search strategies in one operation.

### `use-typed-signatures` — Fail
- story_model.py:935 `load(cls, root, *, on_file=None)`: untyped public parameters (graph hit confirmed).
- story_model.py:960 `load_files(cls, files, project, *, on_file=None)`: untyped public parameters (graph hit confirmed).

## Judgment — `cdd_guidance/practices/stories/model/graph_story_model.py`

### `do-not-invent-parallel-object-models` — Fail
- graph_story_model.py:190 `_row`: every StoryNode is already a graph `Node` (through `BoundNode`), yet the recorder builds a second shape, a positional list `[node_id, name, semantic, "stories", file, line, end]` plus a `_models` dict from id to object, and invents its own node ids (:86, :103, :170). Known: integrated report section 2, "The graph's own node", 1.4 Mode B.
- graph_story_model.py:144 `story_name` fact: copies `Scenario.story_name`, itself a copy of the parent Story.

### `hold-state-on-the-object-not-in-parameters` — Fail
- graph_story_model.py:65 `record`: `_on_node` is set on the object for one call and cleared in `finally`, the pattern the rule names.
- graph_story_model.py:82 `_epic`: `root`, `nodes` and `edges` are handed down every recursive call (`_epic`, `_story`, `_background`, `_scenario`, `_step`) though they are this call's own state.

### `limit-operation-parameters` — Fail
- graph_story_model.py:125 `_scenario`: seven parameters; `_step` (:156) and `_row` (:177) take eight each.

### `put-logic-on-the-owning-resource` — Fail
- graph_story_model.py:295 `_step_semantic`: re-derives Given/When/Then from `step_type` and `keyword`, which `Step.phase` and `Step.keyword` already own.
- graph_story_model.py:221 `_file`: re-derives a node's file from `source.file`, which `BoundNode.has_source_file` and `source` own and `StoryNode._load_path_case` derives again.

### `keep-classes-single-responsibility` — Fail
- graph_story_model.py:254 `_file_facts`: the language-neutral recorder scans TypeScript text (`export const`, `export function activate|handle|process`, named imports) and caches file lines and a search cursor; reading story files is the format readers' job.

### `prefer-class-operations` — Fail
- graph_story_model.py:25 `_imported_modules`: module function over the story file's text.
- graph_story_model.py:39 `_opening_docblock`: module function over the story file's lines.
- graph_story_model.py:295 `_step_semantic`: module function that takes a Step.

### `use-typed-signatures` — Fail
- graph_story_model.py:61 `record(self, practice, *, on_node=None)`: untyped public parameters (graph hit confirmed).

## Judgment — `cdd_guidance/practices/stories/model/code_story_model.py`

### `eliminate-duplication` — Fail
- code_story_model.py:361 `save`: every language model overrides `save` with `write_epics`, so the base `save` and its render path (`_render_epic` :778, `_render_sub_epic` :800, `_render_leaf_file` :847, `_render_epic_helper` :824, `_epic_helper_path`, `_epic_marker_path`, `_render_epic_marker`, `_folder_slug`, `_is_leaf_path`) are a second, dead walk of the epic tree beside `_write_epic` (:533).
- code_story_model.py:626 `load`: every language overrides `load`, and the four overrides (java_story_model.py:56, javascript_story_model.py:57, python_story_model.py:36, typescript_story_model.py:102) each repeat one skeleton: dict check, `epics.clear()`, `_ordered_paths`, suffix filter, strip the tests root, `take_sub_epic_file`. The base `load` that should hold it is dead.
- code_story_model.py:178 `steps_from`: the `and` and `but` branches are identical (graph hit for length confirmed).
- code_story_model.py:199 `CodeScenario.balanced`: brace matching written again as `BraceCall._matching` (brace_story_reader.py:45).
- code_story_model.py:100 `name_from_slug`: the slug-to-name rule is written again as `story_slug.replace("-", " ").title()` in java/nodes.py:101, javascript/nodes.py:28 and typescript/nodes.py:47.
- code_story_model.py:66 `flat_steps`: the same step-and-ands flattening as story_model.py:449 `_steps_key`.
- code_story_model.py:728 `_file_stem_slug`: the suffix table again (known, section 4).

### `no-legacy-api-after-refactor` — Fail
- code_story_model.py:23 module docstring: "render and parse call those so existing callers keep working"; code_story_model.py:300 `from_source` is an alias of `load` with no caller.
- code_story_model.py:766 `folders_of`: no caller.

### `hold-state-on-the-object-not-in-parameters` — Fail
- code_story_model.py:648 `load`: `_leaf_file_name` and `_leaf_content` are set on the model for one call so `_hydrate_leaf_sub_epic_from_content` can read them; nothing reads them (no override exists).

### `use-intention-revealing-names` — Fail
- code_story_model.py:756 `_hydrate_leaf_sub_epic_from_content`: uses the banned word "hydrate", and the method is an empty hook nobody overrides.

### `keep-classes-single-responsibility` — Fail
- code_story_model.py:330 `CodeStoryModel` (graph hit confirmed, 40 public operations): reading a file tree (`load`, `take_sub_epic_file`, `epic_for`, `sub_epic_for`), about twenty spelling hooks, merging code from a previous tree (`adopt_code`, `_take_*`), and path utilities (`strip_tests_root_prefix`, `leaf_files_of`, `folders_of`).
- code_story_model.py:104 `CodeScenario` (graph hit confirmed): a language-neutral scenario that carries brace-language text parsing (`balanced`, `outside_scenarios` hard-code `scenario(`, `=>`, `{`), which Python and Java scenarios inherit.

### `use-consistent-naming` — Fail
- code_story_model.py:626 `CodeStoryModel.load(external: dict)`: an instance method that overrides the classmethod `StoryModel.load(root)` with a different meaning and signature, so the subtype cannot stand in for the base; `load` also means `CodeStory.load(content, slug)` and `DrawIOStoryModel.load(text)`.

### `prefer-class-operations` — Fail
- code_story_model.py:56 `example_names_of(stories)`: called by three language models as `example_names_of(list(epic.stories))`; it belongs on Epic.
- code_story_model.py:71 `as_read(written, language, key)`: wraps `WrittenBlock.is_in`; it belongs on WrittenBlock.
- code_story_model.py:121 `CodeScenario.background_lines(scenario, prefix)`: a static method that takes its own owner as the first parameter.
- code_story_model.py:247 `CodeStory.background_example_line(story, prefix)`: a static method that takes its own owner as the first parameter.

### `keep-operations-small-focused` — Fail
- code_story_model.py:676 `take_sub_epic_file` (graph hit confirmed): 30 lines.

### `simplify-control-flow` — Fail
- code_story_model.py:270 `fill`: four levels of nesting (graph hit confirmed).

### `limit-comments` — Fail
- code_story_model.py:757 `# WHY:`: narrates what the empty hook returns; also :822 and :825.

### `use-typed-signatures` — Fail
- code_story_model.py:121 `background_lines(scenario, ...)`: untyped (graph hit confirmed); also `create(cls, scenario)` at :169.
- code_story_model.py:836 `_folder_slug`: `Union[Epic, Epic]`.

## Judgment — `cdd_guidance/practices/stories/model/diagram_story_model.py`

### `class-not-property-instance-or-subtype` — Fail
- diagram_story_model.py:20 `DiagramStoryNode.width`: the shared mixin switches on `isinstance(self, Story)` and `isinstance(self, Epic)` in `width`, `height`, `y`, `x` and `role` (:20-:98); each variant's behaviour belongs on `DiagramEpic`, `DiagramStory` and `DiagramIncrement`, the subtypes that already exist.

### `eliminate-duplication` — Fail
- diagram_story_model.py:26 `width`: the epic-width rule (`diagram_span_columns` for a nested epic, `span_columns` otherwise) is written again in drawio/nodes.py:167 and miro/nodes.py:220, with a different unit (`base_width` here, `pitch` there).

### `put-logic-on-the-owning-resource` — Fail
- diagram_story_model.py:155 `max_sub_epic_depth`: reads `Epic.tree_depth`, and `width` reads `Epic.span_columns` and `diagram_span_columns`; the layout lives on the base `Epic` in story_model.py while the diagram subtype that owns layout sits here.

### `hide-inner-details` — Fail
- diagram_story_model.py:68 `place`: writes `_place_side` and `_place_destination`, which nothing reads.

## Judgment — `cdd_guidance/practices/stories/model/brace_story.py`

### `eliminate-duplication` — Fail
- brace_story.py:16 `BraceScenario._CALL`: the brace story file is parsed twice with two sets of patterns: here for structure (`without_background`, `scenario_blocks`, `backgrounds_in`, `_inside_scenario`) and again by brace_story_reader.py:18-22 for code. A syntax change has to be made in both, and the two can disagree about which block is a scenario.

### `prefer-class-operations` — Fail
- brace_story.py:107 `unescape`: module function, passed as a callable into `BraceStoryReader` (brace_story.py:122).
- brace_story.py:111 `quoted`: module function.

### `prefer-instance-operations` — Fail
- brace_story.py:31 `without_background`: classmethod that parses text (graph hit confirmed); also `scenario_blocks` :47, `backgrounds_in` :57, `example_names` :90, and the same pattern in code_story_model.py:157-:211.

### `use-consistent-naming` — Fail
- brace_story.py:9: imports `example_names_of`, which this file never uses.

**Passes:** no file in this call passes every rule.

**Graph hits dismissed:**
- `missing-module-context` (28 hits): `stories/model` rolls up into `cdd_guidance/practices/stories/.context/module-context.md`, which exists.
- `use-explicit-dependencies` on StoryNode, Step, Background, Scenario, Epic, Story and StoryModel constructing `CodeBody`, `Examples` or `Background`: these are owned parts (composition) built empty or copied from the source, not swappable collaborators.
- `keep-classes-single-responsibility` on `BraceStoryModel` (15): the spelling hooks of one template, one job.
- `keep-operations-single-responsibility` on `render` and `parse`: pure orchestration of the object's own calls; no I/O mixed in.
- `errors-out-of-existence` on `sub_epic_for`: the raise guards an empty slug list no caller can pass; a broken invariant, not an ordinary edge.
- `keep-operations-small-focused` on `when_then_runs`: the scanner counts the nested `close()`; about 13 statements.
- `simplify-control-flow` on `balanced`: three levels, not four.
- `prefer-instance-operations` on `load_all` and `load_files`: `load*` factories, exempt.
