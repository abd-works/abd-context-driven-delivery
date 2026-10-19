# Graph rules

A practice graph carries its rules on the nodes. Loading the graph runs the executable checks. The serialized tree, the host CLI, and the web app all show the same rules and the same violations.

Work **one fidelity at a time**. A fidelity is done when its rule types own their checks, the graph spec asserts the violations on the serialized tree, and both the CLI and the web app show them on a loaded practice. Do not finish every class before touching tests, and do not batch a whole practice into one pass.

Working copy for the graph spec and the app proof: `harness/graph/_examples/input`.

---

## How a rule is built

Two layouts apply to every practice, including stories.

**One module per fidelity.** The stories package is the layout: `story_map.py`, `scenarios.py`, `acceptance_tests.py`. Each file holds the epic/sub-epic/story rules, or the scenario/step rules, or the example/fixture rules. Clean engineering, DDD, BDD, UX, and the draw.io channel get the same split when that practice's first slice starts. A rule that checks several node types stays in the fidelity that owns it. `node_types` stays as it is.

**Facts on the node that already loads them.** The model object loads itself. A new fact is another field that load fills. Pick the type by how widely the fact applies:

| The fact applies to | It lives on | Filled by |
|---|---|---|
| Every node of every type | `Node` in `harness/graph/graph.py` | `Node`'s own load. Source file and line span already live here. |
| Every node in one model | That model's base: `OoadNode`, `StoryNode`, and the BDD, UX, and DDD base of the same kind | That base type's load |
| One kind of node | That type: `OoadClass`, `Operation`, `Module`, `Story`, `Scenario`, `Step`, `Repository`, … | That type's load (`OoadClass.load_operation`, `Operation.load_parameters`, `Module.load`, and the matching load on the other types) |

`operation_metrics.py` is a side collector. Operation-specific facts (`peer_private_access`, `swallows_exceptions`, `max_control_flow_depth`) move onto `Operation` and are filled while that operation loads. Later slices do the same on the type that owns the fact. No metrics module, no scanner module, no second object whose job is "collect data for the rule."

`tactical_helpers.py` and `class_names_in_file` are facts about a DDD type (stereotype, technical name, lifecycle operations, who references it). They are filled by that type's load. `_first_token`, `_classify`, and `_phase` are filled by `Story` and `Step` load. Import cycles and sibling names are filled by `Module` load. `spec_helpers.py` findings are filled by the spec type's load. Delete the helper module when nothing imports it.

A generic helper is rare. It earns a place when the work is a grammar library or loading a vocabulary, and that helper serves more than one rule. Parsing and token walks stay inside the type's load.

For **each rule**, and for **each violation** that rule records, run the full generate-then-validate loop. Generate writes the artifact; validate checks that same guidance before the next one.

| Order | Guidance | What it produces |
|---|---|---|
| 1 | `bdd-behavior` | Signatures only. One `describe` for the rule. Nested state for a node that violates it and a node that passes it. One `it` per violation message and per clean pass. No test bodies. |
| 2 | `clean-engineering-model` | The field on the type that owns it, filled by that type's existing load. `check` stays a short read of that field. |
| 3 | `bdd-development` | One signature at a time: failing spec, then the model field and the thin `check` that makes that violation or that pass true. |

Call `generate` with that guidance, then `validate` with the same guidance, at each row. The violation is part of the behavior tree (message, file, start line, end line on the serialized rule), not a string added after the class exists.

---

## Where things stand

Schema `rules:` slugs versus an executable class (audit):

| Practice | Schema rules | With a class | Prompt only |
|---|---:|---:|---:|
| stories | 41 | 23 | 18 |
| clean engineering | 53 | 38 | 15 |
| ddd | 9 | 9 | 0 on schema |
| bdd | 22 | 8 | 14 |
| ux | 16 | 2 | 14 |

Clean engineering draw.io checks live beside the schema rules and are not on that schema. They stay in the draw.io slice.

DDD markdown rules that are not on `practices/ddd/model/schema.yaml` belong on the type the section already names. Add them on that type's column-0 `rules:` block in the fidelity slice (`domainEvent` has no block yet; add one). Slugs already on a type stay there. `load-with-identity-in-hand` and `user-facing-system-first` are repeated under Document and Generate; they are the same slugs, not extra entries.

Shared rules attach to every name-bearing DDD type (`boundedContext`, `aggregate`, `entityRoot`, `entity`, `valueObject`, `repository`, `domainService`, `factory`, `specification`, `domainEvent`):

- `ubiquitous-language-everywhere`
- `model-the-domain-not-the-implementation`
- `vocabulary-traces-to-domain-source`
- `do-not-invent-concepts`
- `read-all-source-context-in-full` — `boundedContext` and `aggregate` only (the rule is about locking a boundary)

| Schema type | Add these slugs |
|---|---|
| `boundedContext` | `experts-words-preferred`, `domain-concepts-not-technical-names`, `bc-by-lifecycle-not-ui-themes`, `one-meaning-per-context`, `bc-above-aggregate`, `one-module-per-context-when-small`, `integrations-cross-context-only`, `dependency-fields-tracked`, `no-orphan-contexts`, `vendor-not-implementation`, `context-tree-bc-aggregate-concept`, `bounded-context-file-marks-the-folder`, `user-facing-system-first`, `link-arrow-target`, `hang-deps-on-owning-bc`, `architectural-granularity-decided` |
| `aggregate` | `experts-words-preferred`, `domain-concepts-not-technical-names`, `aggregate-clusters-entities`, `integrations-cross-context-only`, `link-arrow-target`, `hang-deps-on-owning-bc`, `aggregate-root-identity-and-entry`, `every-concept-classified`, `cross-boundary-synchronization-decided`, `architectural-granularity-decided`, `preserve-upstream-names` |
| `entityRoot` | `identity-test-entity-vs-vo`, `aggregate-root-identity-and-entry`, `repository-owns-aggregate-lifecycle`, `factory-is-complex-creation`, `shared-identity-is-generalisation`, `no-premature-infrastructure`, `hang-deps-on-owning-bc`, `link-arrow-target`, `preserve-upstream-names` |
| `entity` | `identity-test-entity-vs-vo`, `shared-identity-is-generalisation`, `no-premature-infrastructure`, `hang-deps-on-owning-bc`, `link-arrow-target`, `preserve-upstream-names` |
| `valueObject` | `identity-test-entity-vs-vo`, `no-premature-infrastructure`, `preserve-upstream-names` |
| `repository` | `repository-owns-aggregate-lifecycle`, `external-system-access-is-service-interface`, `no-orphaned-objects`, `screen-interface-not-a-domain-object`, `flaccid-data-object-no-behavior`, `no-premature-infrastructure`, `ports-behind-adapters`, `one-pattern-per-building-block`, `architectural-granularity-decided`, `preserve-upstream-names` |
| `domainService` | `external-system-access-is-service-interface`, `no-orphaned-objects`, `screen-interface-not-a-domain-object`, `no-premature-infrastructure`, `ports-behind-adapters`, `one-pattern-per-building-block`, `preserve-upstream-names` |
| `factory` | `factory-is-complex-creation`, `no-orphaned-objects`, `no-premature-infrastructure`, `one-pattern-per-building-block`, `preserve-upstream-names` |
| `specification` | `specification-is-reusable-rule`, `no-orphaned-objects`, `no-premature-infrastructure`, `one-pattern-per-building-block`, `preserve-upstream-names` |
| `domainEvent` | `domain-events-past-tense`, `domain-concepts-not-technical-names`, `no-orphaned-objects`, `no-premature-infrastructure`, `ports-behind-adapters`, `one-pattern-per-building-block`, `preserve-upstream-names` |

`contextMapping` stays a nested def under `boundedContext.mappedTo`. Its rules (`integrations-cross-context-only`, `dependency-fields-tracked`, `link-arrow-target`) sit on `boundedContext`, and again on `aggregate` because the map hangs each outbound link on the aggregate that has the dependency. `building-blocks-fidelity-requires-tactical-stereotype` and `private-method-naming` stay on the class types that already list them. `domainEvent` is a property, so it does not take those two.

Story rule modules are already one file per fidelity. Their checks still call module-level functions, so the stories slices move those onto the rule types:

- `practices/stories/rules/story_map.py` — epic, sub-epic, story (`_first_token`, `_classify`, `_band`, `_child_tally`, `_story_parent_id`, `_is_near_duplicate`)
- `practices/stories/rules/scenarios.py` — scenario, step, given, when, then (`_and_chaining_from_graph`, `_phase`)
- `practices/stories/rules/acceptance_tests.py` — example, fixture

Other practices still mix fidelities, and several keep a helper module:

| Practice | Rule modules | Facts, and the load that fills them |
|---|---|---|
| ddd | `tactical.py` | Stereotype, technical name, lifecycle operations, and references, filled by that DDD type's load. Retire `tactical_helpers.py` and `class_names_in_file`. |
| clean engineering | `module_naming_rules.py`, `module_graph_rules.py`, `practice_wide_rules.py`, `write_interactions.py`, `limit_operation_parameters.py` | Import graph, cycles, and sibling names on `Module.load`. Class findings on `OoadClass` load. Operation findings on `Operation` load, including what `operation_metrics.py` currently fills from outside. |
| stories | `story_map.py`, `scenarios.py`, `acceptance_tests.py` | Token class and child band on `Story` load. Step phase on `Step` load. |
| bdd | `tree_rules.py`, `spec_rules.py`, `observable_behavior.py`, `layer_isolation.py` | Spec findings on the spec type's load. Retire `spec_helpers.py`. |
| ux | `screen_rules.py` | Screen facts on the screen type's load. Split the rule file by ia, mockup, and front-end code when those slices start. |
| draw.io | `practices/clean_engineering/model/drawio/rules/` | Diagram facts on the draw.io type's load. One rule module per diagram group. |

`Node.rule_rows` in `harness/graph/graph.py` currently writes one `violation` string per slug. `failed.setdefault` drops every message after the first, and the row does not copy the node source file or line span. `graph_spec.py` only asserts that single string for `limit-operation-parameters` on the clean-engineering `failure` operation. The stored shape is the full list: every message the check records, each with its own file and line span. See **Serialized violations** below.

---

## 1. Finish the executable checks

Write a class when the check can be decided from a field the node already loaded. When the field is missing, add it on `Node`, on that model's base type, or on the specific type, and fill it inside the load that type already has. `check` reads the field. Leave judgment calls as prompt-only rules (`GraphRule.prose_only`): ubiquitous language, invented requirements, red-then-green, full-surface coverage, and the other rules that need a reader.

Each rule type:

- lives in the fidelity module, after `bdd-behavior`, `clean-engineering-model`, and `bdd-development` have each been generated and validated
- reads model fields in `check` (a grammar library or a shared vocabulary load is the rare helper)
- is registered from that practice's `rules/__init__.py` `RULES` / `BY_SLUG`
- is listed on the schema type it checks
- returns every failure message, naming the offending text and the source span

Plant the fault in the working copy (or the practice `.examples` pair the graph already loads), not only in a hand-built `Node`. The behavior spec's violating example and the graph spec's planted violation are the same fault.

### Slice order

Stories first (modules already match the fidelities, and `graph_spec.py` already loads the story tree). Clean engineering second (the spec already has one violation there, so the row shape gets proven on a real check). Then DDD, BDD, UX.

| Slice | Practice | Fidelity | Rule home |
|---|---|---|---|
| 1 | stories | story_map | `practices/stories/rules/story_map.py` |
| 2 | stories | scenarios | `practices/stories/rules/scenarios.py` |
| 3 | stories | acceptance_tests | `practices/stories/rules/acceptance_tests.py` |
| 4 | clean engineering | modules | `practices/clean_engineering/rules/` → `modules.py` |
| 5 | clean engineering | model | → `model.py` |
| 6 | clean engineering | code | → `code.py` |
| 7 | clean engineering | draw.io | `practices/clean_engineering/model/drawio/rules/` |
| 8 | ddd | bounded_context | `practices/ddd/rules/` → `bounded_context.py` |
| 9 | ddd | building_blocks | → `building_blocks.py` |
| 10 | ddd | tactics | `practices/ddd/rules/tactical.py` |
| 11 | bdd | behavior | `practices/bdd/rules/` → `behavior.py` |
| 12 | bdd | development | → `development.py` |
| 13 | ux | ia | `practices/ux/rules/` → `ia.py` |
| 14 | ux | mockup | → `mockup.py` |
| 15 | ux | front_end_code | → `front_end_code.py` |

Inside a fidelity, add the mechanical prompt-only rules before polishing heuristic ones (verb-noun lexicon, name denylists, near-duplicate size). Heuristic classes stay paired with their markdown.

Prompt-only rules that are mechanical enough to take next, by fidelity:

- **story_map** — evidence enum, seed versus interaction tag
- **scenarios** — browser-then
- **acceptance_tests** — extract-assertion-helper, infrastructure-in-lifecycle-hooks, separate-test-controls
- **clean engineering model** — external-system-interface-is-one-way, no-redundant-relationship-paths, one-canonical-model-document
- **ddd bounded_context** — the `boundedContext` and `aggregate` rows in the schema table above. Mechanical first: `bounded-context-file-marks-the-folder`, `no-orphan-contexts`, `integrations-cross-context-only`, `dependency-fields-tracked`, `link-arrow-target`, `context-tree-bc-aggregate-concept`, `vendor-not-implementation`, `hang-deps-on-owning-bc`, `bc-above-aggregate`, `aggregate-clusters-entities`
- **ddd building_blocks** — the participant rows. Mechanical first: `domain-events-past-tense` on `domainEvent`, `aggregate-root-identity-and-entry` on `aggregate` and `entityRoot`, `no-orphaned-objects` on the types that do not list it yet
- **ddd tactics** — `ports-behind-adapters` on `repository`, `domainService`, and `domainEvent`; `load-with-identity-in-hand` is already on `repository`
- **bdd behavior** — context-sharing, hierarchy-preservation
- **bdd development** — scan-fixture-pair
- **ux ia** — tab screens, ia regions, in-scope epics
- **ux front_end_code** — story/domain JS import, data-goto, StoryDemoControl, mockup shell

---

## 2. One graph spec, nested by what the graph is

`harness/graph/graph_spec.py` is the spec. It already describes a graph loaded from the account credentials working copy, then nests clean engineering, stories, DDD, BDD, and UX. Rule checks, filters, and serialization currently also live in sibling files that build their own nodes:

| File | What it covers | Where it belongs |
|---|---|---|
| `graph_spec.py` | counts, edges, filters, one parameter-rule violation, source span; plus sibling describes `a scenario` and `a step` | stays the root |
| `rule_category_spec.py` | rules child on serialize / `return_nodes` | clean engineering, with operations selected |
| `graph_view_spec.py` | violation filter, passing rules, source folds | same graph, under the filter and source contexts |
| `schema_rules_spec.py` | schema slugs become the node's rules collection | each practice context, "should list the schema rules on {type}" |
| `app_smoke_spec.py` | host inventory matches graph counts | "that the host has loaded" under the same graph |
| `pattern_overlay_spec.py` | overlay path and rebuilt tree | "with a pattern overlay" |
| `ce_rules_spec.py` | fault/clean pairs via a harness | clean engineering fidelities, on the serialized node |
| `drawio_rules_spec.py` | draw.io XML fixtures | clean engineering draw.io context |
| `stories_rules_spec.py` | `VerbNounFormat.check` on a handmade story | stories / story_map |
| `stories_examples_spec.py` | TypeScript `.examples` pairs | stories fidelities |
| `ddd_rules_spec.py` | tactical example pairs | ddd / tactics |
| `bdd_examples_spec.py` | layer-isolation pair | bdd / development |
| `node_fact_spec.py` | edge tuples must not become nodes | "loaded from the working copy", with a row that is an edge |
| `host_spec.py` | unknown operation returns a traceback | leave this file; the subject is the host process, not the graph |

Fold a file into `graph_spec.py` in the slice that owns it. Delete the old file in that same slice once its examples live under the practice context. `host_spec.py` stays.

Target tree (usage order). Counts, edges, and source stay where `graph_spec.py` already has them. Every fidelity context below names the rules on that node and the violations the spec plants. A rule that fails twice shows both entries. The clean twin of that node keeps the same rule `passing`. Prompt-only rules show `prompt`.

```
a graph
  loaded from the account credentials working copy
    with a row that is an edge
      it should reject an edge tuple as a node
      it should accept a DDD aggregate node tuple
    with clean engineering
      with modules
        a module lists domain-nouns-only, named-seam-and-constraint, high-cohesion,
          no-module-per-class, single-boundary, deep-module, abstraction-focus,
          purpose-before-mechanism, public-seam-only, use-typed-signatures,
          general-purpose-surface, temporal-independence, one-way-deps,
          extensions-live-with-the-domain, low-coupling, layer-separation,
          missing-module-context, language-modules-one-section, modules-not-model-blocks,
          vocabulary-traces-to-source, do-not-invent-terms, do-not-invent-parallel-object-models
        it should violate domain-nouns-only on a module named for a verb
        it should violate one-way-deps on a module cycle, and store every cycle message
        it should leave domain-nouns-only passing on account-credentials
      with the class model
        a class lists model-modules-follow-the-partition, class-not-property-instance-or-subtype,
          keep-classes-single-responsibility, shape-classes-around-resources,
          put-logic-on-the-owning-resource, hide-inner-details, use-explicit-dependencies,
          external-system-interface-is-one-way, use-intention-revealing-names,
          use-consistent-naming, eliminate-duplication, one-canonical-model-document,
          no-redundant-relationship-paths, missing-module-context,
          language-modules-one-section, modules-not-model-blocks
        an operation lists keep-operations-single-responsibility, limit-operation-parameters,
          avoid-vague-parameter-names, errors-out-of-existence,
          state-change-returns-record-or-named-failure, domain-exception-carries-context,
          write-invariants, write-interactions, prefer-class-operations, prefer-instance-operations,
          keep-operations-small-focused, simplify-control-flow, use-exceptions-properly,
          never-swallow-exceptions, limit-comments, provide-meaningful-context,
          no-legacy-api-after-refactor
        a property lists use-property-not-accessor, hide-inner-details
        a parameter lists avoid-vague-parameter-names, use-typed-signatures, use-intention-revealing-names
        an invariant lists write-invariants, limit-comments
        with operations selected
          it should offer limit-operation-parameters and avoid-vague-parameter-names in the rule filter
          it should store both violations on operation failure:
            limit-operation-parameters (more than two parameters, with file and line span)
            avoid-vague-parameter-names (a parameter named data, with its own span)
          it should leave both rules passing on operation register
          it should omit the passing rules when the violations filter is on
        it should violate use-explicit-dependencies on a class that constructs its own collaborator
        it should leave use-explicit-dependencies passing on AccountCredentials
      with a draw.io diagram
        the diagram node lists the draw.io rule slugs, including class-title-no-markdown-bold
          and stereotype-above-class-name
        it should violate class-title-no-markdown-bold on a class title wrapped in markdown bold
        it should leave that rule passing on a plain class title
    with stories
      with a story map
        a story node lists vocabulary-traces-to-domain-source, read-all-source-context-in-full,
          do-not-invent-requirements, evidence-distinguishes-observed-inferred-and-intended
        an epic and a sub-epic list verb-noun-format, branch-on-mechanical-uniqueness, four-to-nine-children
        a story lists verb-noun-format, story-name-captures-system-mechanic, right-size-story-nodes,
          behaviours-not-one-time-tasks, four-to-nine-children
        it should violate verb-noun-format and story-name-captures-system-mechanic on "Handle Request",
          and store both violations
        it should leave verb-noun-format passing on "Submit Order"
        it should violate four-to-nine-children on an epic whose child count is outside 4..9
        it should leave do-not-invent-requirements prompt
      with scenarios
        a scenario lists scenarios-shape, scenario-names-continuation, outline-requires-many-permutations,
          explore-full-interaction-surface, and-chaining, examples-trace-domain-model,
          reconcile-live-immediately, flagged-writes-intended-gwt
        a step lists plain-english-gwt-steps, gwt-steps-trace-to-domain-operations, but-marks-missing-state
        a given lists given-only-what-the-system-checks, given-names-complex-state-root-first,
          seed-prior-story-as-given
        a when lists when-holds-the-operation, when-names-intent-not-interface-gesture,
          expressive-system-interactions
        a then lists behavioral-and-system-observable-outcomes, browser-then-asserts-screen-widgets,
          assert-domain-behavior-not-seeded-state
        with steps recorded in query order
          it should list the steps in source order
        it should violate plain-english-gwt-steps on a camelCase given
        it should violate gwt-steps-trace-to-domain-operations on a step that names no domain operation
        it should violate when-names-intent-not-interface-gesture on "clicks the button"
        it should leave plain-english-gwt-steps passing on a sentence step
        it should leave explore-full-interaction-surface prompt
      with acceptance tests
        an example lists examples-declare-seed-vs-interaction, examples-trace-domain-model,
          example-role-names, domain-fixture-example-files, examples-export-data-not-repository,
          shared-example-fixtures, seed-state-at-its-real-owner,
          separate-test-controls-from-production-contracts, system-stubs-domain-real,
          infrastructure-in-lifecycle-hooks, inline-simple-gwt-bodies, extract-assertion-helper
        it should violate domain-fixture-example-files on an example file outside the domain fixture
        it should violate examples-export-data-not-repository on an example that exports a repository
        it should leave domain-fixture-example-files passing on a domain fixture example
    with domain-driven design
      with a bounded context
        a bounded context lists experts-words-preferred, domain-concepts-not-technical-names,
          bc-by-lifecycle-not-ui-themes, one-meaning-per-context, bc-above-aggregate,
          one-module-per-context-when-small, integrations-cross-context-only,
          dependency-fields-tracked, no-orphan-contexts, vendor-not-implementation,
          context-tree-bc-aggregate-concept, bounded-context-file-marks-the-folder,
          user-facing-system-first, link-arrow-target, hang-deps-on-owning-bc,
          architectural-granularity-decided, plus the shared name rules
        an aggregate lists experts-words-preferred, domain-concepts-not-technical-names,
          aggregate-clusters-entities, integrations-cross-context-only, link-arrow-target,
          hang-deps-on-owning-bc, aggregate-root-identity-and-entry, every-concept-classified,
          cross-boundary-synchronization-decided, architectural-granularity-decided,
          preserve-upstream-names, plus the shared name rules
        it should violate bounded-context-file-marks-the-folder on a class folder with no bounded-context.md
        it should violate no-orphan-contexts on a context with no dependency arc and no standalone reason
        it should violate integrations-cross-context-only on an arc whose target is inside the same context
        it should leave bounded-context-file-marks-the-folder passing on the account context folder
        it should leave ubiquitous-language-everywhere prompt
      with building blocks
        an entity root lists the stereotype, technical-name, private-method, flaccid, orphan, and screen rules
          already on the schema, plus identity-test-entity-vs-vo, aggregate-root-identity-and-entry,
          repository-owns-aggregate-lifecycle, factory-is-complex-creation,
          shared-identity-is-generalisation, no-premature-infrastructure, hang-deps-on-owning-bc,
          link-arrow-target, preserve-upstream-names
        an entity lists the same schema rules, plus identity-test-entity-vs-vo,
          shared-identity-is-generalisation, no-premature-infrastructure, hang-deps-on-owning-bc,
          link-arrow-target, preserve-upstream-names
        a value object lists the same schema rules, plus identity-test-entity-vs-vo,
          no-premature-infrastructure, preserve-upstream-names
        a domain event lists domain-events-past-tense, domain-concepts-not-technical-names,
          no-orphaned-objects, no-premature-infrastructure, ports-behind-adapters,
          one-pattern-per-building-block, preserve-upstream-names
        it should violate domain-events-past-tense on an event named CreateAccount
        it should violate aggregate-root-identity-and-entry on an aggregate with no root identity
        it should violate flaccid-data-object-no-behavior on an entity root with properties and no operations
        it should leave domain-events-past-tense passing on AccountCreated
      with tactics
        a repository lists the schema rules it already has, plus repository-owns-aggregate-lifecycle,
          external-system-access-is-service-interface, no-orphaned-objects,
          screen-interface-not-a-domain-object, flaccid-data-object-no-behavior,
          no-premature-infrastructure, ports-behind-adapters, one-pattern-per-building-block,
          architectural-granularity-decided, preserve-upstream-names
        a domain service lists its schema rules, plus external-system-access-is-service-interface,
          no-orphaned-objects, screen-interface-not-a-domain-object, no-premature-infrastructure,
          ports-behind-adapters, one-pattern-per-building-block, preserve-upstream-names
        a factory lists its schema rules, plus factory-is-complex-creation, no-orphaned-objects,
          no-premature-infrastructure, one-pattern-per-building-block, preserve-upstream-names
        a specification lists its schema rules, plus specification-is-reusable-rule, no-orphaned-objects,
          no-premature-infrastructure, one-pattern-per-building-block, preserve-upstream-names
        it should violate ports-behind-adapters on a repository that imports a concrete store
        it should violate load-with-identity-in-hand on a load with no identity argument
        it should leave ports-behind-adapters passing on a repository that depends on a port
    with behavior specs
      with behavior
        a spec lists observable-behavior, domain-practice-alignment, usage-order-behaviors,
          full-surface-coverage, framework-syntax
        a description lists describe-is-subject-not-internal, describe-is-plain-english,
          domain-practice-alignment
        a context lists state-not-when, nest-by-enabling-events, context-setup-expresses-state,
          context-sharing
        it should violate describe-is-subject-not-internal on a description named SessionLog
        it should violate describe-is-plain-english on a description named for a symbol
        it should violate state-not-when on a context labeled when
        it should leave describe-is-plain-english passing on "an action that is annotated with log"
        it should leave full-surface-coverage prompt
      with development
        an observation lists observable-behavior, full-surface-coverage, no-implementation,
          hierarchy-preservation, one-assertion-per-test, one-signature-at-a-time, red-then-green,
          minimum-green, code-minimalism, layer-isolation, oo-api-design,
          honors-documented-surface-contracts, scan-fixture-pair
        it should violate no-implementation on an observation whose body asserts
        it should violate layer-isolation on an import-time patch of the subject
        it should leave no-implementation passing on a signature with an empty body
        it should leave red-then-green prompt
    with experience
      with information architecture
        a map lists in-scope-epics-only, story-domain-js-imported
        a screen lists tab-states-are-separate-screens, screen-story-budget,
          screen-names-use-domain-terms, ia-named-regions-only,
          system-stories-group-with-visible-trigger, in-scope-epics-only,
          upstream-decisions-carried, real-frontend-not-mockup, real-backend-wired
        a ux context lists in-scope-epics-only
        it should violate screen-names-use-domain-terms on a screen named Page1
        it should violate tab-states-are-separate-screens on a tab drawn as a state of one screen
        it should violate in-scope-epics-only on a screen from an epic outside the map
        it should leave screen-names-use-domain-terms passing on Account credentials
      with a mockup
        a control lists controls-match-interaction-decisions, brand-is-opt-in, stub-catalogue-honest
        a story demo control lists story-demo-control-for-gwt, key-interactions-wired,
          shell-from-template, story-domain-js-imported
        an interaction lists key-interactions-wired, controls-match-interaction-decisions
        it should violate shell-from-template on a story demo control with no template shell
        it should violate story-demo-control-for-gwt on a control whose steps do not match the story
        it should leave shell-from-template passing on a control built from the template
      with front-end code
        the screen lists real-frontend-not-mockup, real-backend-wired
        it should violate real-frontend-not-mockup on a screen that still renders the mockup shell
        it should violate real-backend-wired on a screen whose data is a local stub
        it should leave real-backend-wired passing on a screen that calls the domain module
    with a pattern overlay
      it should resolve a pattern name and a practices folder to the same root
      it should keep the overlaid rules on the DDD node after the tree rebuilds
  that the host has loaded
    it should count the same nodes and edges as the graph for each practice
    it should return the same violations the graph serialized for the planted failure
```

### Serialized violations

Store **every** violation a rule records. A check that returns three messages leaves three entries on that rule. `failed.setdefault` and the single `violation` string both go away, so a second failure is still on the node after serialize and after `return_nodes`.

Change the row once, in the clean-engineering code slice, before later slices assert it. The spec plants one rule that fails twice and asserts both entries, in the order the check recorded them.

A rule child keeps `type: Rule`, `name` = slug, and `children: []`. `status` is `violating`, `passing`, or `prompt`. A prompt-only rule is `prompt`, so an unloaded check does not look clean. A rule with any stored violation is `violating`.

```json
"violations": [
  { "message": "Operation 'failure' takes more than two parameters.", "file": "src/account-credentials/...", "start": 12, "end": 18 },
  { "message": "Operation 'failure' names a parameter 'data'.", "file": "src/account-credentials/...", "start": 14, "end": 14 }
]
```

`file` / `start` / `end` come from the span for that hit. The web source view opens the entry the user selects.

Each fidelity context in the spec asserts three things on `return_nodes` / `serialize`:

1. A node of that fidelity lists its schema rule slugs.
2. A planted rule that fails more than once is `violating`, and `violations` contains every message and span from that check.
3. The matching clean node keeps that rule `passing` (or omits it when the violations filter is on).

The `it` reads the serialized graph. Arrange code may build the working copy. It does not replace the rule's operations, and it does not grow another `*_helpers.py`.

---

## 3. CLI and web app

This is the proof for the slice. Spec green is not enough.

**CLI.** `harness/graph/app/host.py` speaks JSON lines on stdin. The web server spawns that process. For the slice, send:

1. `load_working_copy` for `harness/graph/_examples/input` and the practice under test.
2. `filter_choices` for that practice and one node type in the fidelity. The reply's `rules` list includes the slice's slugs.
3. `return_nodes` with `{ "practices": [...], "node_types": [...], "violations": true }`. A node in the reply has a `rules` child. A rule that failed twice has both entries in `violations`, each with message and line span.

**Web.** From `harness/graph/app`, start `npm run server` (API on port 3000) and `npm run dev` (UI on port 5173). Load the same working copy.

1. Select the practice and a node type from the fidelity.
2. Expand a node's `rules` child. Passing, prompt, and violating rows are visible.
3. Turn violations on. The tree keeps the planted failure and drops the passing rule.
4. Open each stored violation. The source view lands on that entry's line. Both hits of a two-failure rule are listed.

If either surface is missing the rules child or the violation, the slice is still open. Fix the graph, then re-check the spec, the CLI, and the page.

---

## Slice checklist

Copy this onto the slice when it starts. Leave the boxes until that fidelity is done.

- [x] Fidelity module holds the practice's rules for that fidelity; each fact is a field on `Node`, the model base, or the specific type, filled by the load that type already has
- [ ] Each rule and each violation went through `generate` then `validate` for `bdd-behavior`, then `clean-engineering-model`, then `bdd-development`
- [x] Mechanical prompt-only rules in that fidelity have a rule type and a schema `rules:` entry
- [x] Prompt-only rules that need a reader stay `prompt` on the node
- [x] Working copy contains one planted fault and one clean node for a rule in the slice
- [x] `graph_spec.py` asserts schema slugs, every stored violation on a rule that fails more than once (message and span, in record order), and the clean pass
- [x] The sibling spec file for that slice is folded in and removed
- [x] Host CLI `return_nodes` shows every violation on that rule
- [ ] Web app shows the rules child, the violations filter, and every violation's source line
