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

**Generated:** 2026-11-07 03:47:36 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 22
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

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/base_class_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\base_class_model.py#L175): OoadClass `OoadClass`: Class 'OoadClass' exposes 28 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/base_class_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\base_class_model.py#L467): OoadClass `Module`: Class 'Module' exposes 23 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/base_class_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\base_class_model.py#L674): OoadClass `CleanEngineeringModel`: Class 'CleanEngineeringModel' exposes 13 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/code_class_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\code_class_model.py#L20): OoadClass `CodeCleanEngineeringModel`: Class 'CodeCleanEngineeringModel' exposes 14 public operations (budget ~9). Split responsibilities.

Evaluate the current context against this rule (keep-classes-single-responsibility):

### `shape-classes-around-resources`

Model a class around the concept that owns the state and the rule, not a doer, handler, or service that acts on a data bag. A Payment has transactions, a source, and a destination, and it moves the money; it is not a `PaymentService` that takes a `PaymentData` object. A service-plus-bag pair splits the rule from its memory, so every change has to be found in two types and the bag cannot enforce anything. Two resources may collaborate — a model that loads a Module is not a service-plus-bag split.

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/base_class_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\base_class_model.py#L175): OoadClass `OoadClass`: Class 'OoadClass' mirrors framework model types; use domain names.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/base_class_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\base_class_model.py#L467): OoadClass `Module`: Class 'Module' mirrors framework model types; use domain names.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/base_class_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\base_class_model.py#L674): OoadClass `CleanEngineeringModel`: Class 'CleanEngineeringModel' mirrors framework model types; use domain names.

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

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/base_class_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\base_class_model.py#L175): OoadClass `OoadClass`: Class 'OoadClass' constructs 'BoundChildren' inside its constructor.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/base_class_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\base_class_model.py#L467): OoadClass `Module`: Class 'Module' constructs 'CodeBody' inside its constructor.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/base_class_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\base_class_model.py#L674): OoadClass `CleanEngineeringModel`: Class 'CleanEngineeringModel' constructs 'BoundChildren' inside its constructor.

Evaluate the current context against this rule (use-explicit-dependencies):

### `external-system-interface-is-one-way`

Let a domain wrapper or collaborator depend on the named external-system contract. Keep the external type independent of domain wrappers and domain types, because a reverse dependency makes the external boundary depend on one caller's model.

Evaluate the current context against this rule (external-system-interface-is-one-way):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/c_family_parse.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\c_family_parse.py#L82): Operation `parse`: Operation 'parse' mixes I/O-style calls with domain calculation; split responsibilities.

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

### `keep-operations-small-focused`

Keep each operation short enough to read as one thought — under 20 statements. A multi-line call, list, or string initializer is one statement. When it grows, extract a private helper whose name says why that slice exists.

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/base_class_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\base_class_model.py#L310): Operation `load_property`: Operation 'load_property' is 21 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/base_class_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\base_class_model.py#L781): Operation `load`: Operation 'load' is 40 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/module_context_files.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\module_context_files.py#L92): Operation `public_seam_hits`: Operation 'public_seam_hits' is 28 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/c_family_parse.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\c_family_parse.py#L63): Operation `method_span_in_text`: Operation 'method_span_in_text' is a staticmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/code_body.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\code_body.py#L58): Operation `named`: Operation 'named' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/code_body.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\code_body.py#L170): Operation `split_inside`: Operation 'split_inside' is a staticmethod; prefer an instance operation.

Evaluate the current context against this rule (prefer-instance-operations):

### `simplify-control-flow`

Handle the failing or empty cases first and return. Keep the main path flat. Do not nest more than three levels — deeper than that you cannot tell which conditions hold on a given line without reading back up, and that is where the unhandled branch hides.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/c_family_parse.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\c_family_parse.py#L63): Operation `method_span_in_text`: Operation 'method_span_in_text' nests control flow 4 levels deep (max 3).

Evaluate the current context against this rule (simplify-control-flow):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/module_context_files.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\module_context_files.py#L72): Parameter `row`: Parameter 'row' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/module_context_files.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\module_context_files.py#L82): Parameter `row`: Parameter 'row' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/module_context_files.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\module_context_files.py#L92): Parameter `row`: Parameter 'row' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/module_context_files.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\clean_engineering\model\module_context_files.py#L121): Parameter `row`: Parameter 'row' needs a domain-specific type, not a generic container.

Evaluate the current context against this rule (use-typed-signatures):

---

# Judgment (model fidelity, `clean_engineering/model` top-level files, group 1)

Files: `base_class_model.py`, `c_family_parse.py`, `call_graph.py`, `code_body.py`, `code_class_model.py`, `field_types.py`, `model_descriptions.py`, `module_context_files.py`.

**Graph hits dismissed:**
- `shape-classes-around-resources` (3, "mirrors framework model types"): `OoadClass`, `Module`, and `CleanEngineeringModel` are this practice's own domain (a model of classes and modules); they are the resources, not service-plus-bag pairs.
- `use-explicit-dependencies` (3): `BoundChildren` and `CodeBody` are owned parts (composition), not swappable collaborators.
- `prefer-instance-operations` on `CodeLanguage.named`: a named factory, the exemption the rule allows.

**Graph hits confirmed:** `keep-classes-single-responsibility` on `OoadClass` (28 public operations), `Module` (23), `CleanEngineeringModel` (13), `CodeCleanEngineeringModel` (14); `keep-operations-single-responsibility` on `CFamilyParse.parse`; `keep-operations-small-focused` on `OoadClass.load_property`, `CleanEngineeringModelFactory.load` (40 lines), `ModuleContext.public_seam_hits`; `prefer-instance-operations` on `CFamilyParse.method_span_in_text` (called as a static by `harness/graph/working_copy.py:639`) and `WrittenBlock.split_inside`; `simplify-control-flow` on `method_span_in_text`; `use-typed-signatures` on the four `row: dict` parameters in `module_context_files.py`.

## Judgment — `cdd_guidance/practices/clean_engineering/model/base_class_model.py`

### `do-not-invent-parallel-object-models` — Fail
- base_class_model.py:221 `OoadClass` keeps its members twice (`properties`/`operations` and `property_nodes`/`operation_nodes`) synced by `sync_tree_from_legacy` / `sync_legacy_from_tree` (already in the integrated report §2).
- base_class_model.py:780 `CleanEngineeringModelFactory.load` picks the format model from a file suffix, a second format table beside the `formats` map in `clean_engineering.py:46` and `Format.from_extension`; a new format has to be added in both.

### `class-not-property-instance-or-subtype` — Fail
- base_class_model.py:735 `CleanEngineeringModel.load(path)` reads a path, but `DrawIOCleanEngineeringModel.load` (drawio_class_model.py:122) and `MiroCleanEngineeringModel.load` (miro_class_model.py:90) take the file's text under the same name, so the factory calls `load(text)` for two formats (base_class_model.py:801) and `load(path)` for the others. A subtype that changes what its parameter means cannot stand in for the base.

### `keep-classes-single-responsibility` — Fail
- base_class_model.py:467 `Module` holds the module tree and also reads folders and card files from disk (`load_folder_facts`, base_class_model.py:640), resolves script imports (`import_targets`), and loads DDD stereotypes (`load_source_facts`); 23 public operations across model, file I/O, and graph facts.
- base_class_model.py:175 `OoadClass` has 28 public operations: the class model, five copies of the `has_more_*` / `load_next_*` / `get_next_*_from_file` loading protocol, legacy sync, and graph fact loading.

### `eliminate-duplication` — Fail
- base_class_model.py:362 the `load_X` / `has_more_X` / `load_next_X` / `get_next_X_from_file` loop is written five times (properties, operations, relationships, modules, classes) across `OoadClass`, `Module`, and `CleanEngineeringModel`: fifteen near-identical methods for one loading pattern.

### `use-consistent-naming` — Fail
- base_class_model.py:372 `get_next_property_from_file` beside `load_next_property` and `load_property`: three verbs (`get`, `load_next`, `load`) for reading one member, and `load_property` (base_class_model.py:310) means "copy from another model", not "read from the file".

### `one-canonical-model-document` — Fail
- base_class_model.py:618 `Module.load_source_facts` imports `cdd_guidance.practices.ddd.model.stereotypes` to classify entities and aggregate roots, so Clean Engineering's base model depends on DDD while DDD's models subclass Clean Engineering's; the stereotype facts belong to DDD's own module subtype.

### `prefer-class-operations` — Fail
- base_class_model.py:51 `is_interface_name`, `interface_name_for`, `production_name_for`, `example_extension_kind`, `base_type_name_for`, `companion_interface_name` are free functions about a class name; they are questions an `OoadClass` answers about itself.
- base_class_model.py:34 `_internal_design_in` and `_readable_text` are free functions used only by `Module.load_folder_facts`.

### `avoid-vague-parameter-names` — Fail
- base_class_model.py:677 `CleanEngineeringModel.__init__(name: str | Graph)` lets the first parameter be either a name or a graph, and the constructor swaps them; a caller cannot tell from the signature what to pass.
- base_class_model.py:649 `modules_heading_hit({})` and `model_block_hits({})` are called with an empty dict for a `row` they do not need, and `ModuleContext(folder / "_.py")` (base_class_model.py:644) builds a fake file path because the constructor asks for a Python file instead of a folder.

### `no-legacy-api-after-refactor` — Fail
- base_class_model.py:709 `CleanEngineeringModel.classes` is documented "for backward compat".
- base_class_model.py:823 the module-level `__getattr__` re-exports `Property`, `Operation`, and `Parameter` from this module after they moved to `property.py` and `operation.py`; a second import path for each class.

### `use-intention-revealing-names` — Fail
- base_class_model.py:402 `place_relationship` calls `bind_property_relationship` (property.py:81, also c_family_parse.py:385 `_bind_member_relationships`): "bind" is on the repository's banned-word list, and the name does not say what the call does to the property.

## Judgment — `cdd_guidance/practices/clean_engineering/model/module_context_files.py`

### `do-not-invent-parallel-object-models` — Fail
- module_context_files.py:137 `ModuleContextFiles` and `ModuleContext.missing_hit` / `modules_heading_hit` / `public_seam_hits` / `model_block_hits` re-implement the graph rules `MissingModuleContext`, `LanguageModulesOneSection`, `PublicSeamOnly`, and `ModulesNotModelBlocks` (`rules/module_graph_rules.py`) with the same messages, over a `{name, message, contributor}` dict. That is a sixth shape of a rule hit beside the five in the integrated report §2, and `ModuleContextFiles` has no caller outside its own spec.

### `use-typed-signatures` — Fail
- module_context_files.py:193 `_py_file(row)` reads the Python file's path out of the hit dict's `message` key; the dict carries a path in a field named for something else.

### `eliminate-duplication` — Fail
- module_context_files.py:138 the four `rows_for_*` operations repeat one loop (build `ModuleContext`, de-duplicate by key, collect hits) with a different hit method.

## Judgment — `cdd_guidance/practices/clean_engineering/model/model_descriptions.py`

### `do-not-invent-parallel-object-models` — Fail
- model_descriptions.py:45 `model_members` flattens every class member into a `{"Class.member": {kind, interactions, model_parameters, model_returns, model_file}}` dict that `harness/graph/working_copy.py:168` saves as a fact on the Clean Engineering root and `bdd/model/graph_bdd_model.py:34` reads back. The Clean Engineering model already owns those classes and members; the graph keeps a dict copy keyed by name strings, so a fix to how an operation reports its interactions has to be made in the model and in this copy.

## Judgment — `cdd_guidance/practices/clean_engineering/model/call_graph.py`

### `eliminate-duplication` — Fail
- call_graph.py:35 `parse_call_graph_block` reads indented arrow lines into `CallGraphEntry` values; `bdd/model/bdd_model.py:233` `_apply_fence_block` repeats the same loop (depth from indent, `parse_arrow_line`, else `call`) instead of calling it.

### `prefer-class-operations` — Fail
- call_graph.py:26 `parse_arrow_line`, `parse_call_graph_block`, `render_call_graph_block`, `call_graph_to_callees`, `callees_to_call_graph` are five free functions over a list of `CallGraphEntry`; a call graph is a concept with its own parse and render, and no class holds it.

## Judgment — `cdd_guidance/practices/clean_engineering/model/c_family_parse.py`

### `shape-classes-around-resources` — Fail
- c_family_parse.py:51 `CFamilyParse` is a doer handed the model's and the class's factories; it builds a `CleanEngineeringModel` it does not own. The TypeScript, JavaScript, and Java models share the brace-language reading, so it belongs on a common brace-language model base they extend, not in a parser that the channels and `harness/graph/working_copy.py:637` both call.

**Passes:** `vocabulary-traces-to-source`, `do-not-invent-terms`, `model-modules-follow-the-partition`, `put-logic-on-the-owning-resource`, `hide-inner-details`, `use-property-not-accessor`, `external-system-interface-is-one-way`, `limit-operation-parameters`, `errors-out-of-existence`, `state-change-returns-record-or-named-failure`, `domain-exception-carries-context`, `limit-comments`, `write-invariants`, `write-interactions`, `no-redundant-relationship-paths`.
