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

**Generated:** 2026-11-07 00:29:21 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 24
**Rules with graph hits:** 6
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

- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L55): OoadClass `CatalogPractice`: Class 'CatalogPractice' constructs 'SkillSlashName' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L341): OoadClass `CatalogPage`: Class 'CatalogPage' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L781): OoadClass `FidelityTemplate`: Class 'FidelityTemplate' constructs 'Format' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L1156): OoadClass `Catalog`: Class 'Catalog' constructs 'Path' inside its constructor.

Evaluate the current context against this rule (use-explicit-dependencies):

### `external-system-interface-is-one-way`

Let a domain wrapper or collaborator depend on the named external-system contract. Keep the external type independent of domain wrappers and domain types, because a reverse dependency makes the external boundary depend on one caller's model.

Evaluate the current context against this rule (external-system-interface-is-one-way):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L1646): Operation `approach_page_body`: Operation 'approach_page_body' mixes I/O-style calls with domain calculation; split responsibilities.

Evaluate the current context against this rule (keep-operations-single-responsibility):

### `limit-operation-parameters`

Have callers pass intent, not setup. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L1313): Operation `generate_project_approach`: Operation 'generate_project_approach' takes 5 parameters (maximum 3, excluding self).

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

**Graph violations:** 9

- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L745): Operation `generate_catalog`: Operation 'generate_catalog' is 34 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L1013): Operation `generate_catalog`: Operation 'generate_catalog' is 24 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L1047): Operation `generate_catalog`: Operation 'generate_catalog' is 26 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L1112): Operation `generate_catalog`: Operation 'generate_catalog' is 41 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L1313): Operation `generate_project_approach`: Operation 'generate_project_approach' is 43 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L1360): Operation `configure_project_approach`: Operation 'configure_project_approach' is 58 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L1646): Operation `approach_page_body`: Operation 'approach_page_body' is 350 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/project_approach.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\project_approach.py#L44): Operation `from_paths`: Operation 'from_paths' is 23 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/project_approach.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\project_approach.py#L79): Operation `generate`: Operation 'generate' is 39 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L299): Operation `normalize`: Operation 'normalize' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L628): Operation `parse`: Operation 'parse' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L643): Operation `whole_file`: Operation 'whole_file' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L647): Operation `comment_tag`: Operation 'comment_tag' is a classmethod; prefer an instance operation.

Evaluate the current context against this rule (prefer-instance-operations):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 5

- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L334): Parameter `func`: Parameter 'func' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L682): Parameter `tool`: Parameter 'tool' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L682): Parameter `owner`: Parameter 'owner' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L1243): Parameter `guidance`: Parameter 'guidance' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\catalog_generator\catalog_generator.py#L1646): Parameter `example_sources`: Parameter 'example_sources' is missing a type annotation.

Evaluate the current context against this rule (use-typed-signatures):

---

# Judgment (model fidelity, judged against the graph this call built)

Scope: validate on the whole `harness/catalog_generator` folder timed out twice, so this call covers `catalog_generator.py`, `project_approach.py`, and `approach_copy.py` (19 classes); `foundry_chrome.py` (page chrome) and the smoke scripts are not in this graph. The graph records module-level functions only for files with no class, so the free functions in `catalog_generator.py` were confirmed in the source. Dismissed graph hits: `CatalogPage`, `Catalog`, and `FidelityTemplate` constructing `Path`/`Format` (values); `CatalogPractice` building a default `SkillSlashName` is judged below with the other dependency findings; `keep-operations-small-focused` and `keep-operations-single-responsibility` on `approach_page_body` (a 350-line operation) are code-fidelity rules, reported to the code judge.

## Judgment — `harness/catalog_generator/catalog_generator.py`

### `do-not-invent-parallel-object-models` — Fail
- catalog_generator.py:165 `UTILITY_REGISTRY`: a hand-written list of utility toolsets by module path and class name, read into `RegistryEntry` objects (catalog_generator.py:175, with a `class_name` string copy), beside the Installer's discovery of every `@agent_toolset`; a utility added to the repository is missing from the catalog until someone edits this list.
- catalog_generator.py:59 `_CARD_DEFAULTS`: CatalogPractice reads each practice's catalog card (family, perspective, order, blurbs) from an untyped `catalog_card` dict on the practice class and copies it into `self._card`; that presentation data belongs on PracticeGuidance as named properties.

### `keep-classes-single-responsibility` — Fail
- catalog_generator.py:1156 `Catalog`: 40 methods and 9 public operations covering building the catalog from guidance, brands, writing pages, the CDD approach page, and the project approach page (`generate_project_approach`, `configure_project_approach`).

### `prefer-class-operations` — Fail
- catalog_generator.py:152 `catalog_practices`: module-level functions do Catalog's and CatalogPractice's work — `catalog_utilities` (catalog_generator.py:197), `keep_in_catalog` (catalog_generator.py:207), `resolve_lifecycle_actions` (catalog_generator.py:489), `build_run_request` (catalog_generator.py:543), and `dump_run_request_yaml` (catalog_generator.py:600).

### `use-explicit-dependencies` — Fail
- catalog_generator.py:69 `__init__`: CatalogPractice builds its own `SkillSlashName()` when none is given, and `RegistryEntry.owner` (catalog_generator.py:188) constructs the utility class on every read.

### `limit-operation-parameters` — Fail
- catalog_generator.py:1313 `generate_project_approach`: five parameters describing one project's approach (`project_root`, `out_root`, `project_title`, `repo_url`, and an `examples_json` string mapping practice to stage to path); they form one ProjectApproach, which project_approach.py:36 already models.

### `use-typed-signatures` — Fail
- catalog_generator.py:1243 `add_guidance`: `guidance: Any`; catalog_generator.py:1237 `from_registry` takes `Iterable[Any]`; catalog_generator.py:1646 `approach_page_body` takes `example_hrefs: dict[str, str]` and an untyped `example_sources`.

Passes: `vocabulary-traces-to-source`, `do-not-invent-terms`, `model-modules-follow-the-partition`, `class-not-property-instance-or-subtype`, `shape-classes-around-resources`, `put-logic-on-the-owning-resource` (CatalogFidelity and CatalogPractice render from the live FidelityGuidance, 1.7 confirmed), `hide-inner-details`, `use-property-not-accessor`, `external-system-interface-is-one-way`, `errors-out-of-existence`, `domain-exception-carries-context`, `no-redundant-relationship-paths`, `use-consistent-naming`. No `_current_*` fields remain on Catalog (P-37 confirmed). `GitCitation.normalize` and `IllustratedExampleRow.parse`/`whole_file`/`comment_tag` are parsing factories, which the factory exemption covers.
