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

**Generated:** 2026-11-07 03:50:46 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 53
**Rules with graph hits:** 8
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

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/links.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\links.py#L80): OoadClass `StoryMapLinks`: Class 'StoryMapLinks' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/links.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\links.py#L157): OoadClass `DomainModelLinks`: Class 'DomainModelLinks' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L147): OoadClass `_StorySection`: Class '_StorySection' constructs 'Background' inside its constructor.

Evaluate the current context against this rule (use-explicit-dependencies):

### `external-system-interface-is-one-way`

Let a domain wrapper or collaborator depend on the named external-system contract. Keep the external type independent of domain wrappers and domain types, because a reverse dependency makes the external boundary depend on one caller's model.

Evaluate the current context against this rule (external-system-interface-is-one-way):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L63): Operation `from_workspace`: Operation 'from_workspace' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L202): Operation `parse_file`: Operation 'parse_file' mixes I/O-style calls with domain calculation; split responsibilities.

Evaluate the current context against this rule (keep-operations-single-responsibility):

### `limit-operation-parameters`

Have callers pass intent, not setup. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L572): Operation `render_scenarios`: Operation 'render_scenarios' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L937): Operation `render`: Operation 'render' takes 4 parameters (maximum 3, excluding self).

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

**Graph violations:** 10

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/links.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\links.py#L125): Operation `entries`: Operation 'entries' is 30 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/links.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\links.py#L184): Operation `headings`: Operation 'headings' is 22 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L79): Operation `parse`: Operation 'parse' is 43 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L176): Operation `from_workspace`: Operation 'from_workspace' is 24 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L210): Operation `parse_text`: Operation 'parse_text' is 36 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L572): Operation `render_scenarios`: Operation 'render_scenarios' is 22 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L734): Operation `load_scenarios`: Operation 'load_scenarios' is 31 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L878): Operation `from_workspace`: Operation 'from_workspace' is 23 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L937): Operation `render`: Operation 'render' is 26 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L1214): Operation `attach_source_locations`: Operation 'attach_source_locations' is 45 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `missing-module-context`

**Graph violations:** 17

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/links.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\links.py#L67): OoadClass `_Anchors`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/links.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\links.py#L80): OoadClass `StoryMapLinks`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/links.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\links.py#L157): OoadClass `DomainModelLinks`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/markdown_scenario_round_trip_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\markdown_scenario_round_trip_spec.py#L1): OoadClass `_module`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/markdown_story_model_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\markdown_story_model_spec.py#L26): OoadClass `SpecFixture`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L59): OoadClass `MarkdownIncrement`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L147): OoadClass `_StorySection`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L158): OoadClass `MarkdownStep`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L172): OoadClass `MarkdownScenario`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L730): OoadClass `MarkdownStory`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L779): OoadClass `MarkdownEpic`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L803): OoadClass `_ScenarioDocument`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L818): OoadClass `_StepLines`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L858): OoadClass `MarkdownParseError`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L862): OoadClass `MarkdownStoryModel`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/tree.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\tree.py#L1): OoadClass `_module`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/workspace_load_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\workspace_load_spec.py#L1): OoadClass `_module`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.

Evaluate the current context against this rule (missing-module-context):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

**Graph violations:** 7

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/links.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\links.py#L184): Operation `headings`: Operation 'headings' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L79): Operation `parse`: Operation 'parse' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L166): Operation `prose`: Operation 'prose' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L202): Operation `parse_file`: Operation 'parse_file' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L572): Operation `render_scenarios`: Operation 'render_scenarios' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L830): Operation `rows`: Operation 'rows' is a staticmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L850): Operation `line`: Operation 'line' is a staticmethod; prefer an instance operation.

Evaluate the current context against this rule (prefer-instance-operations):

### `simplify-control-flow`

Handle the failing or empty cases first and return. Keep the main path flat. Do not nest more than three levels — deeper than that you cannot tell which conditions hold on a given line without reading back up, and that is where the unhandled branch hides.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L79): Operation `parse`: Operation 'parse' nests control flow 8 levels deep (max 3).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L1214): Operation `attach_source_locations`: Operation 'attach_source_locations' nests control flow 4 levels deep (max 3).

Evaluate the current context against this rule (simplify-control-flow):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 10

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/links.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\links.py#L118): Parameter `story`: Parameter 'story' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/links.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\links.py#L125): Parameter `story_map`: Parameter 'story_map' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L176): Parameter `on_file`: Parameter 'on_file' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L572): Parameter `story_backgrounds`: Parameter 'story_backgrounds' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L734): Parameter `root`: Parameter 'root' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L734): Parameter `scenarios`: Parameter 'scenarios' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L830): Parameter `owner`: Parameter 'owner' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L837): Parameter `part`: Parameter 'part' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L850): Parameter `step`: Parameter 'step' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\stories\model\markdown\nodes.py#L878): Parameter `on_file`: Parameter 'on_file' is missing a type annotation.

Evaluate the current context against this rule (use-typed-signatures):


---

# AI judgment (model fidelity, stories/model/markdown, sub-judge)

## Judgment — `cdd_guidance/practices/stories/model/markdown/nodes.py`

### `keep-classes-single-responsibility` — Fail
- nodes.py:210 `MarkdownScenario.parse_text`: a scenario node doubles as the parser of a whole scenarios document. One `MarkdownScenario()` instance carries about thirty parser fields (`document_parts`, `sections`, `tree_heading`, `_shared_background`, `_scenarios`, `_current`, `_in_examples`, ...) and returns a list of other MarkdownScenarios; the scenario it is never holds a scenario.
- nodes.py:1305 `MarkdownStoryModel._parse_lines`: the story map is also the parser, keeping cursor state (`_story_map`, `_current_epic`, `_sub_epic_stack`, `_raw_line`, `_epic_heading_depth`) on itself while it builds a second `MarkdownStoryModel`; the same for `_parse_outline_lines` (:1443) and the renderer state `_outline_lines` (:1051).

### `do-not-invent-parallel-object-models` — Fail
- nodes.py:533 `step.markdown_line`: the markdown reader keeps "the lines a node was read with" in ad-hoc attributes set with `setattr` and read back with `getattr` (`markdown_line`, `markdown_heading` :332/:1148, `markdown_parts` :333/:1149, `story_backgrounds` :497, `scenario_document`); the code formats keep the same thing in the declared `StoryNode.written` (WrittenBlock). Two mechanisms for one concept, and the markdown one is invisible on Step, Story and Scenario.
- nodes.py:740 `MarkdownStory.load_scenarios`: attaches scenarios to a story by comparing `scenario.story_name` strings, the `*_name` copy judged in story_model.py:516.

### `eliminate-duplication` — Fail
- nodes.py:1214 `attach_source_locations`: after `parse` has read the document, this walks the same text a second time with the same patterns to find each epic's and story's line by name; the parser already sees every line number as it reads (graph hits for length and nesting confirmed).
- nodes.py:796 `_OUTLINE_EPIC_RE`: aliases and copies of the module's own patterns: `_OUTLINE_EPIC_RE = _OUTLINE_EPIC_PATTERN`, `_OUTLINE_STORY_RE`, and `_OUTLINE_ESTIMATE_RE`, `_HEADING_RE`, `_BULLET_RE` recompiled from the same text as :29-:43.
- nodes.py:1375 `_accept_nested_heading`: the sub-epic stack push and pop is written again in `_accept_outline_epic` (:1475).
- nodes.py:746 `load_scenarios`: builds a step identity tuple by hand that `Scenario.code_key` and `_steps_key` (story_model.py:449) already compute.
- nodes.py:1048 `_render_outline`: writes the `(E) {name}` and `(S) {actor} --> {name}` headings that links.py:141/:146 `StoryMapLinks.entries` rebuilds independently to compute anchors; a change to the heading format breaks every story-map link silently.

### `no-legacy-api-after-refactor` — Fail
- nodes.py:731 `MarkdownStory.load_scenario`: no caller; neither have `MarkdownEpic.load_epic` (:780), `load_story` (:783), `MarkdownStoryModel.load_epic` (:871) and `load_increment` (:874). The class attributes `epic_type` and `story_type` replaced these copy hooks; json/nodes.py:51-:87 keeps the same dead set.
- nodes.py:865 `MarkdownStoryModel` docstring: describes a "Uniform Callable Surface" with `parse / render / sync`; there is no `sync`.

### `hold-state-on-the-object-not-in-parameters` — Fail
- nodes.py:951 `render`: sets `self._links` for one call so `_story_label` (:1089) can read it through `getattr`; the next render without links still reads the previous call's links.
- nodes.py:937 `render(self, story_map, previous, links, workspace)`: the model is told which map to render (`save` calls `self.render(self)`), so the map it holds and the map it writes can differ (graph hit for four parameters confirmed).

### `put-logic-on-the-owning-resource` — Fail
- nodes.py:93 `MarkdownIncrement.parse`: constructs `MarkdownScenario()` to call its private `_strip_markup` (also :99, :987 `strip_backticks`); markup stripping is text handling that no scenario owns.

### `domain-exception-carries-context` — Fail
- nodes.py:910 `_read_workspace`: `MarkdownParseError` is caught and the file skipped, so a malformed `story-map.md` reads as an absent one and the caller is never told (the same failure as B17's `json/nodes.py:136`).

### `prefer-class-operations` — Fail
- nodes.py:36 `_outline_depth(match)`: module function used only by MarkdownStoryModel.

### `keep-operations-small-focused` — Fail
- nodes.py:79 `MarkdownIncrement.parse`: 43 lines and eight levels of nesting (graph hits confirmed); also `parse_text` (:210), `load_scenarios` (:734), `render` (:937).

### `use-typed-signatures` — Fail
- nodes.py:734 `load_scenarios(self, root, scenarios=None)`: untyped (graph hit confirmed); also `on_file` at :176 and :878, `story_backgrounds` at :572.

### `use-consistent-naming` — Fail
- nodes.py:23: imports `Epic` twice on one line; nodes.py:1215 docstring says "Epic/Epic/Story", leftovers of the SubEpic rename.

## Judgment — `cdd_guidance/practices/stories/model/markdown/links.py`

### `eliminate-duplication` — Fail
- links.py:41 `_slug`: wraps `Name.title_slug`, and `_words` (:45) splits camel case again (known, integrated report section 4, slug helpers).
- links.py:138 `story_entries`: another hand-written walk of the epic tree, beside `StoryModel.every_story` and `CodeStoryModel.all_epics`.

### `do-not-invent-parallel-object-models` — Fail
- links.py:125 `entries`: returns a dict keyed by `id(node)` holding one link per epic and story; the link belongs to the node it describes, and keying by `id()` breaks as soon as a node is cloned.

### `prefer-class-operations` — Fail
- links.py:49 `_relative` and links.py:56 `_walk`: module functions used only by `StoryMapLinks` and `DomainModelLinks`.

### `use-typed-signatures` — Fail
- links.py:118 `story_file(self, story)`: untyped (graph hit confirmed); also `entries(self, story_map)` at :125.

## Judgment — `cdd_guidance/practices/stories/model/markdown/tree.py`

### `no-legacy-api-after-refactor` — Fail
- tree.py:31 `render_md_tree`: no production caller; its `include_shared` parameter is "accepted for CLI parity" and discarded (:43). A wrapper around `MarkdownStoryModel().render` kept for an old command-line surface.

**Passes:** `cdd_guidance/practices/stories/model/markdown/__init__.py` (re-exports only).

**Graph hits dismissed:**
- `missing-module-context` (17 hits): `markdown/` rolls up into `cdd_guidance/practices/stories/.context/module-context.md`, which exists. The hits on `*_spec.py` are out of scope.
- `use-explicit-dependencies` on `StoryMapLinks` and `DomainModelLinks` constructing `Path`, and on `_StorySection` constructing `Background`: a `Path` is a value, and the section owns its background.
- `keep-operations-single-responsibility` on `MarkdownIncrement.from_workspace` and `MarkdownScenario.parse_file`: each reads one file and hands the text to its parser; that is the whole job of a `from_*` factory.
- `prefer-instance-operations` on `MarkdownIncrement.parse`, `MarkdownScenario.parse_file`: creation factories that return new nodes. The hits on `prose`, `render_scenarios`, `_StepLines.rows` and `_StepLines.line` are confirmed but covered by the single-responsibility finding above.
