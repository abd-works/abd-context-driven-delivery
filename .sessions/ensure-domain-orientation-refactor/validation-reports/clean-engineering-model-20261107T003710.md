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

**Generated:** 2026-11-07 00:37:10 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 41
**Rules with graph hits:** 9
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

**Graph violations:** 5

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/partition/partition.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\partition\partition.py#L32): Operation `verify_segment_completeness`: Operation 'verify_segment_completeness' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/partition/partition.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\partition\partition.py#L145): Operation `partition`: Operation 'partition' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/render/render.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\render\render.py#L17): Operation `render`: Operation 'render' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validate.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validate.py#L37): Operation `validate`: Operation 'validate' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validation_report.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validation_report.py#L22): Operation `of_graph_and_ai_rules`: Operation 'of_graph_and_ai_rules' takes 4 parameters (maximum 3, excluding self).

Evaluate the current context against this rule (limit-operation-parameters):

### `avoid-vague-parameter-names`

Do not name parameters `data`, `options`, `info`, or other placeholders that could mean anything. A vague name hides what the caller must supply and what the operation does with it.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/partition/segment.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\partition\segment.py#L92): Operation `from_text`: Parameter 'config' in 'from_text' is vague.

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

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/_examples/car_story/car_story.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\_examples\car_story\car_story.py#L12): OoadClass `CarStory`: Operation 'travelTo' uses camelCase while other operations on 'CarStory' use the other convention.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validate.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validate.py#L28): OoadClass `Validate`: Operation 'createRule' uses camelCase while other operations on 'Validate' use the other convention.

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

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions#L1): Module `actions`: Module 'actions' splits into many tiny classes (33); prefer a deep module with a small public surface.

Evaluate the current context against this rule (deep-module):

### `keep-operations-small-focused`

Keep each operation short enough to read as one thought — under 20 statements. A multi-line call, list, or string initializer is one statement. When it grows, extract a private helper whose name says why that slice exists.

**Graph violations:** 10

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/diagnose/diagnose.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\diagnose\diagnose.py#L24): Operation `diagnose`: Operation 'diagnose' is 107 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/grill_context/grill_context.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\grill_context\grill_context.py#L41): Operation `explore_context_files`: Operation 'explore_context_files' is 21 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/partition/partition.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\partition\partition.py#L145): Operation `partition`: Operation 'partition' is 26 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/render/render.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\render\render.py#L17): Operation `render`: Operation 'render' is 27 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/satisfy/satisfy.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\satisfy\satisfy.py#L22): Operation `satisfy`: Operation 'satisfy' is 24 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/graph_json_reader.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\graph_json_reader.py#L83): Operation `refresh_stale_limit_operation_parameter_messages`: Operation 'refresh_stale_limit_operation_parameter_messages' is 58 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validate.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validate.py#L37): Operation `validate`: Operation 'validate' is 49 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validation_report.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validation_report.py#L22): Operation `of_graph_and_ai_rules`: Operation 'of_graph_and_ai_rules' is 34 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validation_report_formatter.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validation_report_formatter.py#L21): Operation `format_violation_line`: Operation 'format_violation_line' is 25 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/verify_report_links.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\verify_report_links.py#L12): Operation `verify_report`: Operation 'verify_report' is 36 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `missing-module-context`

**Graph violations:** 16

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/_examples/car_story/car_story.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\_examples\car_story\car_story.py#L12): OoadClass `CarStory`: Module folder 'car_story' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/diagnose/_examples/memory_leak_hunt/memory_leak_hunt.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\diagnose\_examples\memory_leak_hunt\memory_leak_hunt.py#L7): OoadClass `MemoryLeakHunt`: Module folder 'memory_leak_hunt' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/document/document.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\document\document.py#L11): OoadClass `Document`: Module folder 'document' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/generate/generate.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\generate\generate.py#L13): OoadClass `Generate`: Module folder 'generate' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/generate/generate_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\generate\generate_spec.py#L1): OoadClass `_module`: Module folder 'generate' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/iterate/_examples/story_generator/story_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\iterate\_examples\story_generator\story_generator.py#L7): OoadClass `StoryGenerator`: Module folder 'story_generator' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/render/render.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\render\render.py#L11): OoadClass `Render`: Module folder 'render' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/satisfy/satisfy.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\satisfy\satisfy.py#L16): OoadClass `Satisfy`: Module folder 'satisfy' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/sketch/_examples/module_sketch/module_sketch.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\sketch\_examples\module_sketch\module_sketch.py#L8): OoadClass `ModuleSketch`: Module folder 'module_sketch' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/graph_json_reader.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\graph_json_reader.py#L1): OoadClass `_module`: Module folder 'validate' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validate.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validate.py#L19): OoadClass `PathsNotFoundError`: Module folder 'validate' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validate.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validate.py#L28): OoadClass `Validate`: Module folder 'validate' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validate_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validate_spec.py#L1): OoadClass `_module`: Module folder 'validate' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validation_report.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validation_report.py#L15): OoadClass `ValidationReport`: Module folder 'validate' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validation_report_formatter.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validation_report_formatter.py#L9): OoadClass `ValidationReportFormatter`: Module folder 'validate' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/verify_report_links.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\verify_report_links.py#L1): OoadClass `_module`: Module folder 'validate' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.

Evaluate the current context against this rule (missing-module-context):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/partition/partition_index.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\partition\partition_index.py#L37): Operation `resolve_near`: Operation 'resolve_near' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/sketch/sketch_outline.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\sketch\sketch_outline.py#L13): Operation `of`: Operation 'of' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/sketch/sketch_outline.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\sketch\sketch_outline.py#L20): Operation `every`: Operation 'every' is a classmethod; prefer an instance operation.

Evaluate the current context against this rule (prefer-instance-operations):

### `provide-meaningful-context`

Give a number or literal a name that says why it is there (`SECONDS_PER_DAY`, not `86400`). Do not number variables (`item1`).

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/partition/partition.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\partition\partition.py#L32): Operation `verify_segment_completeness`: Operation 'verify_segment_completeness' uses the unnamed number 120.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/verify_report_links.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\verify_report_links.py#L12): Operation `verify_report`: Operation 'verify_report' uses the unnamed number 80.

Evaluate the current context against this rule (provide-meaningful-context):

### `simplify-control-flow`

Handle the failing or empty cases first and return. Keep the main path flat. Do not nest more than three levels — deeper than that you cannot tell which conditions hold on a given line without reading back up, and that is where the unhandled branch hides.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/sketch/sketch.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\sketch\sketch.py#L53): Operation `find_template`: Operation 'find_template' nests control flow 4 levels deep (max 3).

Evaluate the current context against this rule (simplify-control-flow):

---

# Judgment (model fidelity, judged against the graph this call built)

Scope: the 23 Python classes and module-function sets of `cdd_guidance/actions` in this call's graph; `_examples` folders and specs are left out. Dismissed graph hits: `missing-module-context` and `deep-module` (modules rules); `keep-operations-small-focused`, `simplify-control-flow`, and `provide-meaningful-context` (code rules); `Segment.from_text` and `PartitionIndex.from_text` are factories; `SketchLens.of`/`every` build lenses and are judged below as a copy instead.

## Judgment — `cdd_guidance/actions/validate/validate.py`

### `hold-state-on-the-object-not-in-parameters` — Fail
- validate.py:37 `validate`: every action's public operation takes `guidance` as a slug string, dict, or list (`GuidanceArg`) and looks the fidelity up again, instead of being reached through the fidelity its session holds (`session.practices[...].fidelities[...].actions.validate(...)`); the same shape is on `Generate.generate` (generate.py:19), `Render.render` (render.py:17), `Satisfy.satisfy` (satisfy.py:22), `Sketch.sketch` (sketch.py:116), `GrillContext.grill` (grill_context.py:90), `Document.document` (document.py:17), `Iterate.iterate` (iterate.py:34), `Improvement.repair` (improvement.py:30), `Partition.partition` (partition.py:145), and `Diagnose.diagnose` (diagnose.py:24).

### `keep-classes-single-responsibility` — Fail
- validate.py:28 `Validate`: 26 methods covering rule listing, building and saving the graph for the edited paths, reading saved graph JSON, writing the report, and session logging; `_unchecked_files` holds per-call state on the shared action.

### `use-consistent-naming` — Fail
- validate.py:348 `createRule`: camelCase among snake_case operations.

## Judgment — `cdd_guidance/actions/validate/graph_json_reader.py`

### `do-not-invent-parallel-object-models` — Fail
- graph_json_reader.py:22 `violations_from_graph_json_file`: validate passes graph violations around as `list[dict[str, Any]]` (also `filter_violations_by_path_prefix` at graph_json_reader.py:225, `violations_by_rule` at graph_json_reader.py:242, `ValidationReport.of_graph_and_ai_rules` at validation_report.py:22, `ValidationReportFormatter.format_violation_line` at validation_report_formatter.py:21), while `harness/kanban/report.py` models the same report as `Violation` and `ReportRule` classes; the report has two models, one of them untyped dicts.

### `prefer-class-operations` — Fail
- graph_json_reader.py:83 `refresh_stale_limit_operation_parameter_messages`: one of seven module-level functions over the saved graph and its violations; they belong on the Graph or on a report class (known open item from P-19).

## Judgment — `cdd_guidance/actions/render/render.py`

### `hold-state-on-the-object-not-in-parameters` — Fail
- render.py:17 `render`: takes `format` and `source` on every call (five parameters with `guidance`, `paths`, and `content`), although the fidelity holds the format chosen for it (P-3 still open in this seam).

## Judgment — `cdd_guidance/actions/partition/partition.py`

### `limit-operation-parameters` — Fail
- partition.py:145 `partition`: five parameters (`guidance`, `context`, `mode`, `out_root`, `paths`); partition.py:32 `verify_segment_completeness` takes four (`segment_path`, `expected_names`, `min_body_chars`, `index_path`) that a Segment and its PartitionIndex already hold.

## Judgment — `cdd_guidance/actions/partition/segment.py`

### `do-not-invent-parallel-object-models` — Fail
- segment.py:22 `SegmentCompletenessConfig`: a bag of `min_body_chars`, `non_entry_headers`, and `short_body_pattern` that PartitionIndex re-exposes field by field (partition_index.py:19 `completeness`, `non_entry_headers`, `short_body_pattern`, `min_body_chars`) and Segment carries as `config`; one set of rules is held in three places.

## Judgment — `cdd_guidance/actions/sketch/sketch_outline.py`

### `do-not-invent-parallel-object-models` — Fail
- sketch_outline.py:13 `of`: SketchLens is built from a practice key and copies that practice's `sketch_titles`, so the sketch reads a copy of what PracticeGuidance declares instead of asking the practice whether a heading opens its section.

## Judgment — `cdd_guidance/actions/validate/validation_report_formatter.py`

### `use-property-not-accessor` — Fail
- validation_report_formatter.py:74 `get_relative_path`: a `get_` accessor taking a path; a file's path from the project is Session's `from_project` (space/session/session.py:673), so this is also a second copy of that rule.

Passes: `vocabulary-traces-to-source`, `do-not-invent-terms`, `model-modules-follow-the-partition`, `class-not-property-instance-or-subtype`, `shape-classes-around-resources`, `hide-inner-details`, `use-explicit-dependencies`, `external-system-interface-is-one-way`, `errors-out-of-existence`, `domain-exception-carries-context` (`PathsNotFoundError`), `no-redundant-relationship-paths`. Actions inherit `GuidanceAction` and read their session's folders (P-16, P-17, P-18 confirmed for the folders; the `guidance` argument itself remains).
