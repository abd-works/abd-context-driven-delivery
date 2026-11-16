Write artifacts for each listed guidance at its current fidelity. The shared rules and that fidelity's rules are part of these instructions. After the artifact is written, call validate with the same guidance and paths set to the files you wrote.

### `vocabulary-traces-to-domain-source`

Use terms from the domain language and model when they exist, because one shared definition keeps Stories, examples, and code consistent.

Evaluate the current context against this rule (vocabulary-traces-to-domain-source):

### `read-all-source-context-in-full`

Before fixing the hierarchy or asking a question about an interaction between systems, read every referenced source that informs the decision, including the owning segment, module context, session records, related Story context, build order, code, recorded observations, and relevant run logs. Name the source and location that supports each important interaction, because titles and search results do not explain behaviour.

Evaluate the current context against this rule (read-all-source-context-in-full):

### `do-not-invent-requirements`

Write only behaviour described by a source or explicitly requested by the user. Add a system-to-system interaction only when a named caller invokes it or a source requires it, because an assumed interaction becomes unrequested architecture, Scenarios, and tests.

Evaluate the current context against this rule (do-not-invent-requirements):

### `examples-declare-seed-vs-interaction`

Identify each fixture as **Seed** state owned by a system or **Interaction** data entered, displayed, or validated through the product. Use both when the Story needs both, because persisted records and user-facing data often represent the same concept differently.

Evaluate the current context against this rule (examples-declare-seed-vs-interaction):

### `shared-example-fixtures`

Represent each named example as one reusable code fixture for its domain concept. Shape that fixture from the owning system: the external system's record shape at that boundary and the product's aggregate shape inside the domain, because a convenient mixed object conceals a mapping error and a copied value drifts from the Scenario.

Evaluate the current context against this rule (shared-example-fixtures):

### `seed-state-at-its-real-owner`

Seed and inspect state through the component that owns it in the production architecture. When a rich domain layer integrates with an external system, seed the external test adapter and exercise production behaviour through the aggregates and repositories above it. When the repository is itself the storage boundary and no separate system exists, direct repository setup and loading are appropriate, because tests should reflect the architecture rather than create an extra layer.

Evaluate the current context against this rule (seed-state-at-its-real-owner):

### `separate-test-controls-from-production-contracts`

Keep seed, reset, and inspection operations off the production repository or adapter contract. Add them to a testable extension, test adapter, or stub when acceptance setup needs them, because test control is useful without becoming a production domain capability.

Evaluate the current context against this rule (separate-test-controls-from-production-contracts):

### `system-stubs-domain-real`

Before creating an external-system stub, inspect the real integration contract again and identify the boundary that production code calls. Make the stub reproduce that boundary's operations, request and response structures, identifiers, state changes, and failure behaviour; do not invent a simpler test API. Keep domain aggregates, repositories, validation, mapping, and state transitions real, because an inaccurate stub, silent no-op, or test-only domain operation can make a test pass without implementing production behaviour.

Evaluate the current context against this rule (system-stubs-domain-real):

### `assert-domain-behavior-not-seeded-state`

Exercise the product's domain entry point after seeding its underlying state owner and assert the product result. Inspect that owner for stored data or outbound effects only after the product initiated them, because reading back data inserted during Given proves only that the fixture was stored.

Evaluate the current context against this rule (assert-domain-behavior-not-seeded-state):

### `infrastructure-in-lifecycle-hooks`

Put browser startup, application wiring, and shutdown in lifecycle hooks; keep Given for domain state. Load an aggregate once at the highest Given that needs it and reach owned entities through their aggregate root, because infrastructure and shortcut lookups obscure the behaviour's real state.

Evaluate the current context against this rule (infrastructure-in-lifecycle-hooks):

### `inline-simple-gwt-bodies`

Keep simple Given, When, and Then bodies inline and use example exports directly. Extract a helper only for repeated interaction that is not a domain operation, such as a screen gesture or application wiring, because pass-through helpers add names without adding meaning.

Evaluate the current context against this rule (inline-simple-gwt-bodies):

### `domain-operations-inline-in-steps`

Call each domain operation — a repository load with the identity in hand, an aggregate command, the refusal it raises — directly in the Given, When, or Then that relies on it. Do not wrap domain calls in story-file helpers such as `signIn` or `reloadAccount`. When several steps need the same prior state, seed it with a `seed…` fixture in the examples file, because the acceptance test exists to show which domain operation each step runs and what it proves.

Evaluate the current context against this rule (domain-operations-inline-in-steps):

### `extract-assertion-helper`

Extract the same assertion shape after it appears more than twice and pass its concrete values as data, because copied assertions become inconsistent when behaviour changes.

Evaluate the current context against this rule (extract-assertion-helper):

### `suffix-names-the-tier`

`*_spec` is unit, `*_heavy_spec` is heavy, and `*_e2e_spec` / `*_agent_spec` is e2e; a story test's tier file follows the same suffixes. A suffix that names the wrong tier puts a slow test in the run that must stay fast.

Evaluate the current context against this rule (suffix-names-the-tier):

### `unit-tier-fakes-every-boundary`

A unit spec reaches no real resource: a fake sits at every architecture boundary.

Evaluate the current context against this rule (unit-tier-fakes-every-boundary):

### `heavy-tier-holds-a-real-resource`

A heavy spec uses a real resource (git, a server, a daemon, an installer, a worker, a big load); without one it belongs in the unit tier.

Evaluate the current context against this rule (heavy-tier-holds-a-real-resource):

### `e2e-tier-drives-browser-or-agent`

An e2e spec drives a real browser or a real agent, and no other tier does.

Evaluate the current context against this rule (e2e-tier-drives-browser-or-agent):

### `slow-example-moves-not-the-file`

An example over budget moves out alone, never the whole file: its stub stays in the unit spec and its real run goes to the heavy spec beside it, under the same described subject.

Evaluate the current context against this rule (slow-example-moves-not-the-file):

### `no-skipped-or-empty-test`

No test is skipped, commented out, or left without an assertion.

Evaluate the current context against this rule (no-skipped-or-empty-test):

### `unit-example-within-100-ms`

Every unit example runs within 100 ms, its before-each and after-each included.

Evaluate the current context against this rule (unit-example-within-100-ms):

### `unit-file-within-2-seconds`

A unit spec file runs within 2 s.

Evaluate the current context against this rule (unit-file-within-2-seconds):

### `unit-tier-within-25-seconds`

The whole unit tier finishes in under 25 s of wall clock on an idle machine, because it runs in a sub-task while the person tries each change, and a slow unit tier stops being run.

Evaluate the current context against this rule (unit-tier-within-25-seconds):

### `specs-run-in-parallel`

A spec can run beside any other: no fixed port, no shared temp folder, no shared `CDD_HOME`, no order between files.

Evaluate the current context against this rule (specs-run-in-parallel):

### `heavy-spec-owns-its-resources`

A heavy spec makes its own throwaway resources (repository, server port, `CDD_HOME`), so heavy specs can run in parallel too.

Evaluate the current context against this rule (heavy-spec-owns-its-resources):

### `expensive-fixture-built-once`

A read-only fixture that is slow to build is built once per file and shared, not once per example.

Evaluate the current context against this rule (expensive-fixture-built-once):

### `no-wait-in-unit-test`

A unit test never sleeps or polls; time, retries, and timeouts come from a fake clock.

Evaluate the current context against this rule (no-wait-in-unit-test):

### `budget-never-raised`

The 100 ms, 2 s, and 25 s budgets are never raised to make a slow test pass; the test gets fast or moves tier.

Evaluate the current context against this rule (budget-never-raised):

### `stubbed-boundary-has-heavy-coverage`

Every boundary a unit spec stubs is run for real by a heavy or e2e example with the same `should` sentence under the same subject. A stub with none is unchecked and drifts from the real thing.

Evaluate the current context against this rule (stubbed-boundary-has-heavy-coverage):

### `heavy-example-has-a-stubbed-twin`

Every heavy example has a stubbed twin in the unit spec beside it, so a break is caught after every pass and not only on the heavy cadence.

Evaluate the current context against this rule (heavy-example-has-a-stubbed-twin):

### `heavy-run-within-the-hour`

The newest heavy run on main is under an hour old and passed, or its failure is open on the board.

Evaluate the current context against this rule (heavy-run-within-the-hour):

### `e2e-run-within-the-day`

The newest e2e run on main is under a day old and passed, or its failure is open on the board.

Evaluate the current context against this rule (e2e-run-within-the-day):

### `release-follows-a-green-e2e`

A release tag points at a commit whose e2e and heavy runs passed.

Evaluate the current context against this rule (release-follows-a-green-e2e):

Guide this action so the output conforms to this schema.

[epic]

storyNode:
  fidelity: story_map
  text: string
  order: number
  belongsTo?: storyNode
  id: dotPath
  decomposedInto?: [storyNode]
  where:
    - id is the text slugs from the root to this node, joined by dots
    - id is unique on the map
  rules:
    - vocabulary-traces-to-domain-source
    - read-all-source-context-in-full
    - do-not-invent-requirements

epic:
  fidelity: story_map
  id: dotPath
  uses?: [module]
  decomposedInto: [subEpic | story]
  where:
    - id is the text slugs from the root to this node, joined by dots
    - decomposedInto count 4..9 warn 3,10
    - uses is the home module of a demonstrated class or an invoked member
  rules:
    - verb-noun-format
    - branch-on-mechanical-uniqueness
    - four-to-nine-children

subEpic:
  fidelity: story_map
  id: dotPath
  belongsTo: epic
  decomposedInto: [subEpic | story]
  where:
    - id is the text slugs from the root to this node, joined by dots
    - decomposedInto count 4..9 warn 3,10
    - examples belong on this sub-epic, not on the epic
  rules:
    - verb-noun-format
    - branch-on-mechanical-uniqueness
    - four-to-nine-children

story:
  fidelity: story_map
  id: dotPath
  belongsTo: [subEpic | epic]
  background?: background
  scenarios: [scenario]
  invokes?: [operation | property]
  shownOn?: [screen]
  where:
    - id is the text slugs from the root to this node, joined by dots
    - scenarios count 1..4; more than 4 and the story is huge
    - background only when scenarios share its given
    - one observable interaction at one system boundary
    - invokes is the union of invokes on the steps this story owns
  rules:
    - verb-noun-format
    - story-name-captures-system-mechanic
    - right-size-story-nodes
    - behaviours-not-one-time-tasks
    - story-scenarios-at-most-seven
    - kebab-case-paths

scenario:
  fidelity: scenarios
  id: dotPath
  steps: [step]
  examples?: [example]
  invokes?: [operation | property]
  specifiedBy?: [observation]
  shownOn?: [screen]
  where:
    - id is the text slugs from the root to this node, joined by dots
    - steps match given+ (when then+)+
    - shownOn is the screen whose showsScenarios holds this scenario; with none, the scenario shows its story's screen
    - outline when examples count > 2
    - a later then names the next story
    - examples cover every domain concept the steps name
    - invokes is the union of invokes on these steps
  rules:
    - scenarios-shape
    - outline-requires-many-permutations
    - explore-full-interaction-surface
    - and-chaining
    - examples-trace-domain-model
    - reconcile-live-immediately
    - flagged-writes-intended-gwt

step:
  fidelity: scenarios
  id: dotPath
  order: number
  belongsTo: scenario
  ands?: [step]
  shownOn?: [screen]
  where:
    - id is the text slugs from the root to this node, joined by dots
    - ands continue the step they follow
    - shownOn is the screen whose showsSteps holds this step
    - but marks a missing state
  rules:
    - plain-english-gwt-steps
    - gwt-steps-trace-to-domain-operations
    - but-marks-missing-state

given:
  fidelity: scenarios
  is: step
  id: dotPath
  order: number
  examples?: [example]
  where:
    - id is the text slugs from the root to this node, joined by dots
  rules:
    - given-only-what-the-system-checks
    - given-names-complex-state-root-first
    - seed-prior-story-as-given

when:
  fidelity: scenarios
  is: step
  id: dotPath
  order: number
  invokes: [operation | property]
  where:
    - id is the text slugs from the root to this node, joined by dots
  rules:
    - when-holds-the-operation
    - when-names-intent-not-interface-gesture
    - expressive-system-interactions

then:
  fidelity: scenarios
  is: step
  id: dotPath
  order: number
  observes: example
  where:
    - id is the text slugs from the root to this node, joined by dots
  rules:
    - behavioral-and-system-observable-outcomes
    - scenario-names-continuation
    - browser-then-asserts-screen-widgets
    - assert-domain-behavior-not-seeded-state

background:
  fidelity: scenarios
  is: given
  id: dotPath
  given: given
  belongsTo: story
  scopes?: [example]
  where:
    - id is the text slugs from the root to this node, joined by dots
    - scopes the examples its given steps own
    - present only when more than one scenario shares the state

example:
  fidelity: scenarios
  id: dotPath
  text: string
  demonstrates: class
  retrievedUsing: [operation | property]
  where:
    - id is the text slugs from the root to this node, joined by dots
  rules:
    - examples-declare-seed-vs-interaction
    - examples-trace-domain-model
    - example-role-names
    - domain-fixture-example-files
    - examples-export-data-not-repository
    - shared-example-fixtures
    - seed-state-at-its-real-owner
    - separate-test-controls-from-production-contracts
    - system-stubs-domain-real
    - infrastructure-in-lifecycle-hooks
    - inline-simple-gwt-bodies
    - domain-operations-inline-in-steps
    - extract-assertion-helper

## Overview

Map stakeholder and system interactions as behaviours that deliver a solution. Every later fidelity builds on these behaviours, so the story map must describe operations that named actors perform and results they can observe.

---

## Guidance

**Think hierarchically.** Use **Epics** for business capabilities or end-to-end outcomes, **Sub-Epics** for outcomes within an Epic, and **Stories** for discrete user or system interactions with observable results. Decompose Stories into **Scenarios**, then express each Scenario as **Given**, **When**, and **Then** steps. The hierarchy lets a reader move from the business outcome to the behaviour that implements it without losing traceability.

**Write action-oriented interactions.** At every level, name the actor, action, and subject when the format includes actor metadata; name nodes with a base-form verb and a noun. `Manage Customer Orders` says what the Epic achieves, while `Orders` does not. Keep 4-9 direct children under an epic or sub-epic, and restructure at 3 or fewer or 10 or more, because shallow chains and crowded nodes both hide the shape of the work. A story holds at most 7 code scenarios; more than 7 and the story is huge. A story with none is waiting for its scenarios, which is fine.

---

## Shared rules

```yaml
alwaysApply: false
globs: "**/*story-map*,**/*_story.test.*,**/*story_test*,**/*story-test*,**/*-sketch.md"
```

Whenever you define or change user interactions and resulting system behavior, at any level of detail. Follow these rules.

- **`vocabulary-traces-to-domain-source`** - Use terms from the domain language and model when they exist, because one shared definition keeps Stories, examples, and code consistent.
- **`read-all-source-context-in-full`** - Before fixing the hierarchy or asking a question about an interaction between systems, read every referenced source that informs the decision, including the owning segment, module context, session records, related Story context, build order, code, recorded observations, and relevant run logs. Name the source and location that supports each important interaction, because titles and search results do not explain behaviour.
- **`do-not-invent-requirements`** - Write only behaviour described by a source or explicitly requested by the user. Add a system-to-system interaction only when a named caller invokes it or a source requires it, because an assumed interaction becomes unrequested architecture, Scenarios, and tests.

---

#### Overview

Make specifications executable by transforming them into automated tests that validate production code.  
*Context graduates from being merely machine readable to machine executable. AI is allergic to causing tests to fail.*

#### Guidance

Apply `@stories` `#scenarios` § Guidance and § Rules to acceptance tests. Use the **Test shape ladder** in the `testing-approach` rule under `clean_engineering/rules/`: start with the real application when it is available, use deterministic external-system stubs while developing, and replace them with end-to-end boundaries when requested.

When scenario realizations exist (inline or `{scope}-scenario-realization.md`), treat them as the agreed call graph for the **When** under test: implement and assert through the outermost domain entry point and named collaborators the realization names — do not re-route through test-only helpers that the realization stripped away.

**Develop the behaviour, not only the test.** Acceptance-test work owns both the executable specification and the production code that satisfies it. Represent each named scenario example as one code fixture, and do not invent fixture values the scenario does not name. Take one Scenario at a time: write the failing acceptance test, invoke the Clean Engineering companion at `code` fidelity, implement the smallest production change that can pass, rerun the test, refactor when it is green, and then continue to the next behaviour. After two failed fix attempts, diagnose the failure before changing more code.

Refer to [`cdd_guidance/references/language-tools.md`](../../references/language-tools.md) for language-specific test tools and idioms.

#### Rules

```yaml
alwaysApply: false
globs: "**/*.story.shared.*,**/*.story.domain.spec.*,**/*.story.server.spec.*,**/*_story.test.*,**/*story_test*,**/*story-test*,**/*-sketch.md"
```

Whenever you create, alter, or delete Spec-by-Example / acceptance tests, or production code they support. Follow these rules.

If this change will not stay here, follow `practices/stories/stories-scenarios.mdc`.


- **`examples-declare-seed-vs-interaction`** - Identify each fixture as **Seed** state owned by a system or **Interaction** data entered, displayed, or validated through the product. Use both when the Story needs both, because persisted records and user-facing data often represent the same concept differently.
- **`shared-example-fixtures`** - Represent each named example as one reusable code fixture for its domain concept. Shape that fixture from the owning system: the external system's record shape at that boundary and the product's aggregate shape inside the domain, because a convenient mixed object conceals a mapping error and a copied value drifts from the Scenario.
- **`seed-state-at-its-real-owner`** - Seed and inspect state through the component that owns it in the production architecture. When a rich domain layer integrates with an external system, seed the external test adapter and exercise production behaviour through the aggregates and repositories above it. When the repository is itself the storage boundary and no separate system exists, direct repository setup and loading are appropriate, because tests should reflect the architecture rather than create an extra layer.
- **`separate-test-controls-from-production-contracts`** - Keep seed, reset, and inspection operations off the production repository or adapter contract. Add them to a testable extension, test adapter, or stub when acceptance setup needs them, because test control is useful without becoming a production domain capability.
- **`system-stubs-domain-real`** - Before creating an external-system stub, inspect the real integration contract again and identify the boundary that production code calls. Make the stub reproduce that boundary's operations, request and response structures, identifiers, state changes, and failure behaviour; do not invent a simpler test API. Keep domain aggregates, repositories, validation, mapping, and state transitions real, because an inaccurate stub, silent no-op, or test-only domain operation can make a test pass without implementing production behaviour.
- **`assert-domain-behavior-not-seeded-state`** - Exercise the product's domain entry point after seeding its underlying state owner and assert the product result. Inspect that owner for stored data or outbound effects only after the product initiated them, because reading back data inserted during Given proves only that the fixture was stored.
- **`infrastructure-in-lifecycle-hooks`** - Put browser startup, application wiring, and shutdown in lifecycle hooks; keep Given for domain state. Load an aggregate once at the highest Given that needs it and reach owned entities through their aggregate root, because infrastructure and shortcut lookups obscure the behaviour's real state.
- **`inline-simple-gwt-bodies`** - Keep simple Given, When, and Then bodies inline and use example exports directly. Extract a helper only for repeated interaction that is not a domain operation, such as a screen gesture or application wiring, because pass-through helpers add names without adding meaning.
- **`domain-operations-inline-in-steps`** - Call each domain operation — a repository load with the identity in hand, an aggregate command, the refusal it raises — directly in the Given, When, or Then that relies on it. Do not wrap domain calls in story-file helpers such as `signIn` or `reloadAccount`. When several steps need the same prior state, seed it with a `seed…` fixture in the examples file, because the acceptance test exists to show which domain operation each step runs and what it proves.
- **`extract-assertion-helper`** - Extract the same assertion shape after it appears more than twice and pass its concrete values as data, because copied assertions become inconsistent when behaviour changes.

---

Guide this action so the output conforms to this schema.

[module | package]

module:
  fidelity: modules
  id: dotPath
  name: string
  stereotypes?: [string]
  participants: [module | package | class | operation]
  dependsOn?: [module]
  usedBy?: [epic]
  where:
    - id is the name slugs from the root module to this module, joined by dots
    - name is a domain noun or a path
    - a nested module shares a base seam or is a sub-system
    - at most 40% of classes are public
    - dependencies flow one way, with no cycle
    - seam terms are what a caller types
    - purpose opens with the job a caller hires it for
  rules:
    - vocabulary-traces-to-source
    - do-not-invent-terms
    - do-not-invent-parallel-object-models
    - domain-nouns-only
    - named-seam-and-constraint
    - high-cohesion
    - no-module-per-class
    - single-boundary
    - deep-module
    - abstraction-focus
    - purpose-before-mechanism
    - public-seam-only
    - use-typed-signatures
    - general-purpose-surface
    - temporal-independence
    - one-way-deps
    - extensions-live-with-the-domain
    - low-coupling
    - layer-separation
    - missing-module-context
    - language-modules-one-section
    - modules-not-model-blocks
    - source-parses

package:
  fidelity: modules
  id: dotPath
  name: string
  belongsTo: module
  participants: [class | package | module]
  where:
    - id is the module id, then this package name, joined by dots
    - a package groups classes inside a module
  rules:
    - one-way-deps
    - layer-separation

class:
  fidelity: model
  id: dotPath
  name: string
  belongsTo: module
  stereotypes?: [string]
  baseClass?: class
  dependsOn?: [class]
  relationships?: [relationship]
  demonstratedThrough?: [example | observation]
  participants: [operation | property]
  where:
    - id is the module id, then this class name, joined by dots
    - a class exists when a property, an instance, and a subtype do not fit
    - a subtype works wherever the base is used
    - collaborators arrive through the constructor
    - behavior sits on the object that owns the invariant
    - one reason to change
  rules:
    - model-modules-follow-the-partition
    - class-not-property-instance-or-subtype
    - no-prototype-swapping
    - keep-classes-single-responsibility
    - shape-classes-around-resources
    - put-logic-on-the-owning-resource
    - hide-inner-details
    - use-explicit-dependencies
    - external-system-interface-is-one-way
    - use-intention-revealing-names
    - use-consistent-naming
    - one-canonical-model-document
    - no-redundant-relationship-paths
    - missing-module-context
    - language-modules-one-section
    - modules-not-model-blocks
    - prefer-class-operations
    - limit-comments
    - do-not-invent-parallel-object-models
    - layer-separation
    - extensions-live-with-the-domain
    - write-interactions

relationship:
  fidelity: model
  id: dotPath
  kind: "composition" | "aggregation" | "association"
  target: class
  cardinality?: string
  where:
    - id is the class id, then kind, then the target class name, joined by dots
    - composition when the part has no identity outside the owner
    - aggregation when members keep their own identity
    - association when both sides stay independent
    - one canonical link per participant

operation:
  fidelity: model
  id: dotPath
  name: string
  belongsTo: class
  parameters?: [parameter]
  returnType: class | string
  body?: string
  invokes: [operation | property]
  invokedBy?: [step | observation]
  invariants?: [invariant]
  where:
    - id is the class id, then this operation name, joined by dots
    - 0..3 parameters on a domain operation (self not counted)
    - one job
    - body under 20 statements
    - a state change returns the record or a failure named after the rejected rule
    - interactions call a named public operation on a collaborator
  rules:
    - keep-operations-single-responsibility
    - limit-operation-parameters
    - avoid-vague-parameter-names
    - errors-out-of-existence
    - state-change-returns-record-or-named-failure
    - domain-exception-carries-context
    - write-invariants
    - write-interactions
    - prefer-instance-operations
    - keep-operations-small-focused
    - simplify-control-flow
    - use-exceptions-properly
    - never-swallow-exceptions
    - limit-comments
    - provide-meaningful-context
    - no-legacy-api-after-refactor
    - hide-inner-details
    - put-logic-on-the-owning-resource
    - use-property-not-accessor
    - eliminate-duplication

property:
  fidelity: model
  id: dotPath
  name: string
  belongsTo: class
  type: string
  value?: string
  hasType?: class
  invokes?: [operation | property]
  invariants?: [invariant]
  where:
    - id is the class id, then this property name, joined by dots
    - a derived property takes no owner or state parameter
    - a relationship stereotype on the property copies onto relationship.kind
  rules:
    - use-property-not-accessor
    - hide-inner-details
    - keep-operations-small-focused
    - simplify-control-flow
    - use-exceptions-properly
    - never-swallow-exceptions
    - limit-operation-parameters
    - write-interactions

parameter:
  fidelity: model
  id: dotPath
  name: string
  belongsTo: operation
  type: string
  where:
    - id is the operation id, then this parameter name, joined by dots
    - the name says what the caller supplies
  rules:
    - avoid-vague-parameter-names
    - use-typed-signatures
    - use-intention-revealing-names

invariant:
  fidelity: model
  id: dotPath
  text: string
  belongsTo: [operation | property]
  where:
    - id is the owner id, then this text slug, joined by dots
    - a must, never, always, before, or after about this object's own state
  rules:
    - write-invariants
    - limit-comments
    - write-interactions

## Overview

Structure the problem into independent modules with small public interfaces, substantial hidden functionality, and one-way dependencies. Implement those modules with rigorous object-oriented and clean-code practices. When boundaries hold, a change stays inside one module; when they blur, callers depend on internal decisions and must change with them.

## Guidance

Partition first, then type the objects, then implement. Keep the same names in language, modules, model, and code — in prose, diagrams, and source.

## Shared rules

```yaml
alwaysApply: false
globs: "**/*-sketch.md"
```

Use these rules whenever you name a concept, draw a dependency, or write a public seam — in prose, a diagram, or source.

- **`vocabulary-traces-to-source`** — Take every term from the source. The English term and the code name are the same word: *shopping cart* is `ShoppingCart`. When the code says a different word than the domain, every reader keeps a translation in their head, and the two names drift until they mean different things.
- **`do-not-invent-terms`** — Do not invent a second noun or a parallel vocabulary. A second noun for the same thing becomes a second class, and then the same rule has to be written and fixed in both.
- **`do-not-invent-parallel-object-models`** — Keep one object model. Follow the nouns and verbs the rest of the graph already uses for that concept. A class that joins types the rest of the graph keeps apart is a second model — a big ball of mud — and every rule then has to be written and fixed in both. When data or behavior already belongs to an object, extend that object and hand callers the object itself: `ticket.session.practices["stories"].fidelities["story_map"].files()`, not `ticket.files(["stories-story-map"])`. A second model is rarely a whole class family; more often it is a small copy beside the owner: a dict holding one field from each member (`fidelity_states`, `violation_counts`), a `*_name` copy of a reference (`column_name`), a helper class that does the owner's job (`TicketFiles`), a bag of a few of the owner's answers (`Workspace`), or a `*Model` / `*Entry` family scraped from live objects. A copy hides that the owner is missing the behavior, so the next caller builds another copy and a fix to the owner never reaches it. **Checking it:** this rule spans modules, and the copy looks fine in the file that holds it. For every property, data field, dict, and helper class the changed code adds, name the class that already owns that data and read it; the rule fails when the owner holds it or should, and the change copies it instead of returning or extending the owner. Count the members of a class that delegates: dozens of members on a class that only reads its collaborators means it is copying them.

---

#### Overview

Write working production code — real persistence, services, and UI behind the public seams.

#### Guidance

Follow the idioms in [`cdd_guidance/references/language-tools.md`](../../references/language-tools.md).

Start by **Implementing the public surface.** Where the model asked for an interface, the class implements it in the same file and the interface stays public-only. Where it did not, continue to implement the class. Implement public properties and operations first; write out private members next — the seam the model named is the contract, and privates follow from what those operations need, not the other way around. Relationships keep the kind and cardinality already named. 

Make sure to **Implement real behavior.** Fill every empty body — a stub ships as a silent no-op and hides that the seam was never finished. Wire real persistence, services, and other-module seams — not stand-ins as the shipping path. Add helpers, named constants, and domain exceptions only when the implementation needs them; speculative helpers become APIs nobody asked for. Keep an existing interface as the seam; otherwise treat the class as the seam. 

When writing out code take care to **Fill out all interactions with real code.** Turn `-> collaborator.operation` notes into actual calls — have the object ask its collaborators to do the work; do not reach into their internals. A placeholder left in place means the module boundary was never exercised; reaching past the seam couples you to another module's internals. Drop the placeholder once the call is real.

**Honor invariants in the implementation.** Turn `// remaining budget never goes negative` comments into methods where you can; replace comments with explicit code. A comment-only invariant runs only if someone read it — explicit code runs on every path.

**Keep the code clean.** Give each operation one thing to do; keep it short and at one level of abstraction — do not mix orchestration with raw I/O, or a storage change drags through business logic. Name things so they say why they exist. Handle the failing or empty cases first and return — then write the main path flat. Do not bury the real work inside nested ifs. Name exceptions after the failure; never swallow them. Give magic numbers names. Keep the public surface the seam already designed: short, caller-facing, with substantial implementation behind it, still in the module folder.

**Skip the model only for a very small change** — fill a body, rename, extract a helper, honor an invariant already named. The language is already there; keep it current. When you start needing to model — a new class, a new responsibility, a new relationship, a new public seam, or a new concept — stop and go to **model**. See `@clean-engineering-model`. Then return to code and implement what the model now names. Do not grow a shadow model only in the implementation — code-only design drifts from the language and module-context, and the next reader cannot find what you decided.

**Refresh the language and the seam.** Keep class identity in the docstring; put member bullets on the members. Edit the same public-seam module-context — how to use it, what callers must honor, what it depends on. Never internals. Never a parallel file — two documents drift, and documented internals read as promises callers build against.

#### Rules

```yaml
alwaysApply: false
globs: "**/*.py,**/*.ts,**/*.tsx,**/*.js,**/*.java,**/*-sketch.md"
```

Whenever you create, alter, or delete production behavior — bodies, constructors, call sites — including code supported by a model or module map. Follow these rules.

If this change will not stay here, follow `practices/clean-engineering/clean-engineering-model.mdc`.

**Implement the model**
- `hide-inner-details` — Expose behavior through named operations. Do not let callers see how the class stores or arranges its data — once they read the storage directly it becomes a public contract you cannot change. Private fields on the same class hide implementation; you do not need a second class for that. Read-only to callers can mean return a copy or immutable view from a property — it does not require a frozen class or a second type to hold build steps.
- `hold-state-on-the-object-not-in-parameters` — Keep what an object knows on the object, and let its operations read it there. A session holds its practices, a practice holds its fidelities and its current fidelity, a fidelity holds its actions and the format it last used, and an action is made for its session: `session.practices.stories.fidelities.story_map.actions.generate(format="drawio")`, not `Generate.commands_for(session, fidelities, formats)`. A value the caller supplies once, such as a format, is saved on the object that owns it, so the next operation on that object reads it instead of being handed it again. The rule fails when an operation takes, as a parameter, state its own object holds or should hold: the same argument handed down through several layers; a session, guidance, or ticket passed to every call on an object made for it; a name or slug passed so the receiver can look up an object the caller already holds; state written into a string (`session=...`) and parsed back; or a field set on a shared object for one call and restored afterwards. Every layer that passes the value is another place to pass the wrong one, and a call started from inside another, which nobody hands the value to, falls back to a global such as the current session and acts on the wrong object.
- `keep-operations-small-focused` — Keep each operation short enough to read as one thought — under 20 statements. A multi-line call, list, or string initializer is one statement. When it grows, extract a private helper whose name says why that slice exists.
- `prefer-instance-operations` — Keep operations on the instance. Do not annotate them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, `now` (a new value for this moment), and `every` (each value the class allows). A global accessor such as `current` or `shared` is not a factory: it hands every caller the same object from class-level state, so it stays an instance operation on the object that holds that state, or goes.
- `keep-operations-single-responsibility` — Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.
- `simplify-control-flow` — Handle the failing or empty cases first and return. Keep the main path flat. Do not nest more than three levels — deeper than that you cannot tell which conditions hold on a given line without reading back up, and that is where the unhandled branch hides.
- `errors-out-of-existence` — For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure. A missing required argument is a broken call, not an ordinary edge: refuse it with a failure the program declares and names (`CommitPathsRequiredError`), which `domain-exception-carries-context` then asks to carry the rejected value.
- `no-prototype-swapping` — An object keeps the class it was built as. Do not change it afterwards with `Object.setPrototypeOf`, `__proto__ =`, or `__class__ =`. When a subclass needs to make its own instances, give the base an overridable factory (`blank()`) or build the right class directly. A swapped object skips its constructor, so fields the subclass sets up are missing and nothing tells you.

**Names and reuse**
- `use-intention-revealing-names` — Name each class, property, operation, and parameter so it answers why it exists. Do not abbreviate.
- `use-consistent-naming` — Use one word per concept. Pick one verb and use it everywhere (`fetch_`, not a mix of `fetch_`, `get_`, and `retrieve_`). Two words for one concept is how the same logic gets written twice — nobody searching for `fetch_` finds the `retrieve_` that already does the job.
- `provide-meaningful-context` — Give a number or literal a name that says why it is there (`SECONDS_PER_DAY`, not `86400`). Do not number variables (`item1`).
- `eliminate-duplication` — Give repeated logic one canonical function. Every copy is another place the fix has to be repeated, and the copy you miss is the bug.
- `no-legacy-api-after-refactor` — When you rename or reshape a public seam, update every caller — tests, dependencies, and adjacent modules — to the new API. Do not keep compatibility aliases, re-exports, or thin wrappers that preserve the old name.

**Errors / comments**
- `use-exceptions-properly` — Raise a domain exception that names the failure (`CartAlreadyCheckedOut`, not `Error` or a bare string). Catch the specific type you can handle. Do not use a bare `except`, and do not catch `Exception` (or `BaseException`) to return a default or substitute a fallback value: that turns every failure, including a bug, into the ordinary answer. A generic exception cannot be caught selectively, so the caller has to handle everything or nothing.
- `never-swallow-exceptions` — Do not catch and ignore. Log and re-raise, or convert to a domain exception that still names the failure. An `except Exception` that returns, `pass`es, or substitutes a fallback (an empty dict, `None`, the input unchanged) is swallowing too: the caller reads the fallback as a real answer, so a broken invariant reaches the next step unseen.
- `limit-comments` — write comment in operations and properties only when the signature cannot say a constraint or explain why the code behaves the way it does. Do not narrate a line that already names what it does.
- `source-parses` — Keep every source file valid in its language. A file that does not parse is read into no classes, so every other rule passes it without looking, and its problems stay hidden until it runs.

---

#### Template

"""
# Conceptual Clean Engineering Reference (Python style)
# Refer to cdd_guidance/references/language-tools.md for tool recommendations.
# =============================================================================
# Put a class family in one file: the primary type, its subtypes, and
# tightly connected peers that only make sense together (element +
# collection, small aggregate + its part). Name the file after the family
# concept (`abilities.py` for Ability + Abilities). Split into another
# file only when a type is independently reused across families or the
# file becomes a grab-bag. Do not default to one class per file.
# Default: Class is the seam. I{ClassName} is not the default — add it in
# this same file when multiple implementations sit behind one seam, or when
# the user asks. Public members only on I{ClassName}; private members stay
# on {ClassName}. Put `{Type}ExampleFactory` in a sibling file — never in
# the production family file. Write each file under the module folder
# (`{module}/{family_slug}.py`), not beside the module.
# Invariants, interactions, comments (model):
#   Write each invariant as `#` on the class (or above the property /
#   operation it constrains): a must / never / always / before / after
#   that stays true when the object acts.
#   Write each interaction as `-> {collaborator}.{operation}` nested
#   under the calling operation. `-> ClassName` alone is not an interaction.
#   State an invariant or a sequence with `#`. Leave every other line
#   uncommented.
# =============================================================================
"""
from __future__ import annotations
from abc import ABC, abstractmethod

# FILE: {family_slug}.py
# Optional — omit unless generating an interface:
class I{ClassName}(ABC):
    @property
    @abstractmethod
    def {property}(self) -> {Type}:
        ...

    @abstractmethod
    def {operation}(self, {param}: {Type}) -> {ReturnType}:
        ...

class {ClassName}:  # or class {ClassName}(I{ClassName}):
    """*{ClassName}* unique role."""
    # {must / never / always / before / after that stays true of the object}

    @property
    def {property}(self) -> {Type}:
        # {must / never / always / before / after about this property}
        ...

    def {operation}(self, {param}: {Type}) -> {ReturnType}:
        # {must / never / always / before / after when this operation runs}
        # -> {collaborator}.{operation}
        ...

    def _{private_helper}(self, {param}: {Type}) -> {Type}:
        ...

# FILE: {type_slug}_example_factory.py
class {ClassName}ExampleFactory:
    def load_{example_key}(self, *, mode: str = "fake") -> {ClassName}:
        ...

## Supplement: tdd

## Overview

Test-driven development at implementation: every behavior is proven working for real before it is trusted, then kept proven by a test at the fastest tier that can prove it. TDD supplements the implementation fidelities of Clean Engineering (code), Stories (acceptance tests), BDD (development), and DDD (tactics); UX front-end code is not supplemented. Its guidance is the process; its rules check what the finished tests and code show. It has no rules for every fidelity it supplements: each section of rules names the fidelities it is for. The graph checks `unit-tier-fakes-every-boundary` on BDD specs and on Stories acceptance tests (its overlay records each test file's tier and the real resources a unit test imports); validate judges the rest.

## Guidance

### Choose the flow first

The order of work depends on whether the story crosses an architectural boundary for the first time. An area is **known** when an e2e or heavy test already runs real code across every architectural boundary the story touches. If any boundary is new (a new module seam, a new external system, a new tier), use Flow A for that boundary.

**Flow A — a new feature or story that crosses an architectural boundary for the first time.** Run it for real first: the danger here is an AI that believes its own stubs.

1. **Run it end to end, directly.** Drive it through the real stack yourself (browser, server, store, agent), or ask the person to. Record every failure as it happens.
2. **Iterate until it works for real.** A person verifies the result. A human seeing the real thing work is the only way to rule out hallucination.
3. **Capture it in an e2e or heavy test.** Write the test that runs the same path end to end, and see it pass against the real stack, so the success cannot be hallucinated later.
4. **Then write the stubbed and mocked unit tests,** only where a stub or mock was actually used, each checked against the real seam you just ran. An AI tends to stub critical functionality, or to put the stub at the wrong seam and fake what should be real.

**Flow B — another story or feature on a known area.** The seams are proven, so the order reverses:

1. **Write the unit tests** on the seams that already exist, and see them fail for the right reason.
2. **Write the code and run only the tests for the change** — the specs of the files it touched — until they pass. Not the whole tier.
3. **Hand it to the person to try,** and while they test it, run the whole unit tier in a sub-task off the person's thread; report its result when it comes back.
4. **Write the heavy and/or e2e tests in a sub-task:** hand them to a background agent so the person is not kept waiting, and tell the person when they are done.

### Red, green, refactor

Inside Flow B, and for Flow A's unit tests once the real run works: see the test fail for the right reason, write the least production code that makes it pass, and refactor only while green. Take one signature or scenario to green before opening the next. It is not the opening move on a first boundary crossing.

### Arrange, act, assert

Lay out each test body as arrange, act, assert, and assert one outcome, so a failure names the behavior that broke.

### Test doubles and heavy coverage

Fake only what crosses the architecture boundary, never the subject under test, and build each fake from the real seam: the same operations and the same failure cases. **Every stub comes with heavy coverage:** stubbing a boundary makes the unit test fast but leaves the real boundary unproven, so whenever you stub, write a heavy (or e2e) example that runs the same `should` against the real boundary, or confirm one already exists. It runs the other way too: a heavy example keeps a stubbed twin in the unit spec beside it. Unit runs the stub after every pass; heavy checks, on its own cadence, that the stub still behaves like the real thing.

### Fixtures and example data

Keep example data in one home per concept and reuse it. Build a fixture that is slow to make and only read, such as a parsed graph or a loaded practice, once per file and share it. Extract shared setup once three sibling tests repeat it.

### Tiers by speed

A spec file's suffix names its tier, and the tier is about speed:

| Tier | Files | Holds |
|---|---|---|
| unit | `*_spec`, story tiers | Examples that run in microseconds to milliseconds, with a fake at every architecture boundary |
| heavy | `*_heavy_spec` | Examples that need a real resource: git, a server, a daemon, an installer, a worker process, a big load |
| e2e | `*_e2e_spec`, `*_agent_spec` | Examples that drive a real browser or a real agent |

### Make slow tests fast first

The first move for an example over budget is to find out why it is slow and make it fast. Measure where the time goes, then look, in order, for:

1. **A real boundary the unit test does not need** — a socket, a subprocess, git, the file system, a server. Put a fake at that boundary, and make sure a heavy test covers the real one. (On Windows a closed loopback port is not refused at once: a ping to it waits out its whole connect timeout.)
2. **A wait** — a sleep, a poll, a retry loop. Use a fake clock or an event.
3. **An expensive fixture rebuilt for every example.** Build it once per file.
4. **Work the example does not assert on.**

Only an example that is still slow, or that exists to prove the real resource, moves to the heavy spec under the same described subject, keeping its stubbed twin in unit.

### Cadence

Stay off the person's thread. In the foreground run only what proves the change just made; every larger run (the whole unit tier, heavy, e2e) goes to a sub-task or background process, and its result is reported when it comes back.

| Tier | When it runs | Who runs it |
|---|---|---|
| unit, for the change | After every change | The agent, in the foreground: only the specs of the files the change touched, so the answer comes in seconds |
| unit, whole tier | While the person tries the change, and before a push | A sub-task off the person's thread (about 20 s); nobody waits on it |
| heavy | Every hour, and once at the end of multi-pass work | A background process; push without waiting, report its result when it comes back |
| e2e | Every day, before every release, and at the end of work that touches a browser or an agent | The daily scheduled run and the release command |

Read the runner's slow list after every whole-tier unit run and fix each example in the same pass, optimizing first. Keep the runner's timings (`.pycache/spec-seconds.json`): they order the next run's batches, longest first.

### When stuck

After two failed fixes for the same failure, stop and diagnose before a third: read the failure, reproduce it on its own, and find the cause.

## stories-acceptance-tests, bdd-development

The tests Stories acceptance tests and BDD development write share their tiers, their speed, their stubs and heavy coverage, and the cadence they run on.

### Rules

```yaml
alwaysApply: false
globs: "**/*spec.py,**/*_spec.py,**/*spec.ts,**/*.spec.shared.ts,**/*Spec.java,**/*.story.*,**/*_story.test.*"
```

Whenever you create, alter, or delete acceptance tests or BDD specs. Follow these rules.

**Tiers**
- **`suffix-names-the-tier`** — `*_spec` is unit, `*_heavy_spec` is heavy, and `*_e2e_spec` / `*_agent_spec` is e2e; a story test's tier file follows the same suffixes. A suffix that names the wrong tier puts a slow test in the run that must stay fast.
- **`unit-tier-fakes-every-boundary`** — A unit spec reaches no real resource: a fake sits at every architecture boundary.
- **`heavy-tier-holds-a-real-resource`** — A heavy spec uses a real resource (git, a server, a daemon, an installer, a worker, a big load); without one it belongs in the unit tier.
- **`e2e-tier-drives-browser-or-agent`** — An e2e spec drives a real browser or a real agent, and no other tier does.
- **`slow-example-moves-not-the-file`** — An example over budget moves out alone, never the whole file: its stub stays in the unit spec and its real run goes to the heavy spec beside it, under the same described subject.
- **`no-skipped-or-empty-test`** — No test is skipped, commented out, or left without an assertion.

**Speed**
- **`unit-example-within-100-ms`** — Every unit example runs within 100 ms, its before-each and after-each included.
- **`unit-file-within-2-seconds`** — A unit spec file runs within 2 s.
- **`unit-tier-within-25-seconds`** — The whole unit tier finishes in under 25 s of wall clock on an idle machine, because it runs in a sub-task while the person tries each change, and a slow unit tier stops being run.
- **`specs-run-in-parallel`** — A spec can run beside any other: no fixed port, no shared temp folder, no shared `CDD_HOME`, no order between files.
- **`heavy-spec-owns-its-resources`** — A heavy spec makes its own throwaway resources (repository, server port, `CDD_HOME`), so heavy specs can run in parallel too.
- **`expensive-fixture-built-once`** — A read-only fixture that is slow to build is built once per file and shared, not once per example.
- **`no-wait-in-unit-test`** — A unit test never sleeps or polls; time, retries, and timeouts come from a fake clock.
- **`budget-never-raised`** — The 100 ms, 2 s, and 25 s budgets are never raised to make a slow test pass; the test gets fast or moves tier.

**Stubs and heavy coverage**
- **`stubbed-boundary-has-heavy-coverage`** — Every boundary a unit spec stubs is run for real by a heavy or e2e example with the same `should` sentence under the same subject. A stub with none is unchecked and drifts from the real thing.
- **`heavy-example-has-a-stubbed-twin`** — Every heavy example has a stubbed twin in the unit spec beside it, so a break is caught after every pass and not only on the heavy cadence.

**Cadence**
- **`heavy-run-within-the-hour`** — The newest heavy run on main is under an hour old and passed, or its failure is open on the board.
- **`e2e-run-within-the-day`** — The newest e2e run on main is under a day old and passed, or its failure is open on the board.
- **`release-follows-a-green-e2e`** — A release tag points at a commit whose e2e and heavy runs passed.

## stories-acceptance-tests

One scenario at a time, in the flow's order. Flow A: run the scenario for real end to end, have the person verify it, turn it into the heavy or e2e story test, then write the stubbed domain tier. Flow B: domain tier red on its Then, code to green, the person tries it, then the heavy and e2e tiers in a sub-task. Stories' own acceptance-test rules (seeding at the real owner, stubs at the system boundary, one interaction's outcomes in one Then) stay Stories'.

Save each format you write at its path, filling any {name} from the work: python: C:/Users/jeffa/AppData/Local/Temp/cdd-generate-g42l_dbb/{sub_epic_slug}.story.shared.py, C:/Users/jeffa/AppData/Local/Temp/cdd-generate-g42l_dbb/{sub_epic_slug}.story.domain.spec.py, C:/Users/jeffa/AppData/Local/Temp/cdd-generate-g42l_dbb/{sub_epic_slug}.story.server.spec.py; typescript: C:/Users/jeffa/AppData/Local/Temp/cdd-generate-g42l_dbb/{sub_epic_slug}.story.shared.ts, C:/Users/jeffa/AppData/Local/Temp/cdd-generate-g42l_dbb/{sub_epic_slug}.story.domain.spec.ts, C:/Users/jeffa/AppData/Local/Temp/cdd-generate-g42l_dbb/{sub_epic_slug}.story.server.spec.ts

After the artifact is written, call validate with this same guidance and paths set to the files you wrote: validate refreshes the session's graph with exactly those files, so the graph rules run on them as they are now.