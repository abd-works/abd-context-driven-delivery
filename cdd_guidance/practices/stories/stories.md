## Overview

Map stakeholder and system interactions as behaviours that deliver a solution. Every later fidelity builds on these behaviours, so the story map must describe operations that named actors perform and results they can observe.

---

## Guidance

**Think hierarchically.** Use **Epics** for business capabilities or end-to-end outcomes, **Sub-Epics** for outcomes within an Epic, and **Stories** for discrete user or system interactions with observable results. Decompose Stories into **Scenarios**, then express each Scenario as **Given**, **When**, and **Then** steps. The hierarchy lets a reader move from the business outcome to the behaviour that implements it without losing traceability.

**Write action-oriented interactions.** At every level, name the actor, action, and subject when the format includes actor metadata; name nodes with a base-form verb and a noun. `Manage Customer Orders` says what the Epic achieves, while `Orders` does not. Keep 4-9 direct children under an epic or sub-epic, warn at 3 or 10, and restructure at 2 or fewer or 11 or more, because shallow chains and crowded nodes both hide the shape of the work. A story holds 1 to 7 code scenarios; more than 7 and the story is huge.

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
- **`evidence-distinguishes-observed-inferred-and-intended`** - Label behaviour as observed, inferred, or intended and cite its source. When available evidence cannot exercise required behaviour, write the intended GWT and state the limitation, because an unobserved expectation must not be presented as a fact.

---

## Fidelities

### story_map

```yaml
default_format: markdown
stage: discovery
```

#### Overview

Scope the solution using a hierarchy of business goals, user interactions, and system behaviors.  
*a simple graph is easier to change, compare, and reorganize. Humans catch AI Order-of-Magnitude sizing errors.*

#### Sketch

Ask who is trying to reach this outcome, what they need in front of them before they act, what a successful result looks like for them, and what stops them. Ask how that differs for each person who touches the outcome. Write the epic, the people, and the stories from those answers. Do not ask the user to choose one story or a story per system.

#### Guidance

**Name the layers.** Actors are people or systems (`Customer`, `Support Agent`, `Order Service`). Epics name an end-to-end outcome (`Manage Customer Orders`). Sub-Epics name one outcome inside an Epic (`Place Customer Order`). Stories name one observable interaction that can be tested on its own (`Submit Order`).

**Decompose through interactions.** Cover the business capability with Epics, then ground each Epic in Stories that demonstrate real behaviour. Find the **walking skeleton**, the smallest end-to-end path that works and delivers value, and validate it before adding later increments. Split increments by actor, data, workflow, channel, interface, non-functional requirement, or business rule when that creates a demonstrable step.

**Map the complete outcome.** Include the primary path, supporting actors, system interactions, reversals, and recovery behaviour needed to achieve the outcome. Administrators, support staff, partner onboarding, cancellations, refunds, escalations, and failures belong on the map when sources require them, because a forward path alone does not describe the working product.

**Treat a system hop as a boundary interaction.** A hop is an observable request and response across a named system boundary, not every internal function call. Keep internal fan-out within the boundary Story unless another system exposes its own observable interaction. Give an intermediary its own Story when it validates, decides, or translates; keep simple forwarding or display as an outcome on the caller's Story.

#### Scaffold

**When scaffolding only** (`/partition` or a names only first cut), follow this subsection. Write only verb-noun Epic, Sub-Epic, and Story names. Carry the actor on every Story — `{Actor} --> {Verb Noun}` — because the actor is part of the Story's name at every depth. Read the source material in full, split distinct mechanics, and apply `verb-noun-format`, `branch-on-mechanical-uniqueness`, and `do-not-invent-requirements`. Do not write Scenarios, increments, or explanatory prose. Do not read or apply the Rules below. **Stop reading this skill when scaffolding.**

#### Rules

```yaml
alwaysApply: false
globs: "**/*story-map*,**/*-sketch.md"
```

Whenever you create, alter, or delete epics, sub-epics, or stories on the map, or change scenarios or acceptance work that forces a map change. Follow these rules.

If this change will not stay here, follow `practices/stories.mdc`.

- **`verb-noun-format`** - Name every Epic, Sub-Epic, and Story with a base-form verb and noun. Epics and Sub-Epics name goals rather than an actor's activity or a supporting system call, because grammar alone does not preserve the right level of abstraction.
- **`story-name-captures-system-mechanic`** - At Story level, use a verb that names the operation and a noun that names the record or concept it acts on. Replace vague names such as `Handle Request`, `Process Data`, or `Manage Record`, because they hide what the system does.
- **`four-to-nine-children`** - Keep 4-9 direct children on an epic or sub-epic, warn at 3 or 10, and restructure at 2 or fewer or 11 or more, because readers cannot reason easily about shallow chains or crowded nodes. Do not apply this band to the scenarios under a story.
- **`story-scenarios-one-to-four`** - A story's code scenarios number 1 to 7. More than 7 and the story is huge — split it. A story with no scenarios is not a story yet.
- **`branch-on-mechanical-uniqueness`** - Create separate Stories for distinct mechanics and use Scenarios or examples when several source entries share one mechanic, because one Story per source entry duplicates behaviour while one Story for different mechanics hides work.
- **`right-size-story-nodes`** - Put one observable interaction at one system boundary in each Story. Keep the caller's request, response, and translation together; give the callee its own boundary Story; keep display-only and forwarding-only work as outcomes, because splitting every internal call or interface step obscures the interaction being tested.
- **`behaviours-not-one-time-tasks`** - Use Stories for repeatable stakeholder or system interactions that can be expressed as GWT more than once. Keep one-time renames, migrations, and repository changes in plans or tasks, because completed maintenance is not recurring product behaviour.
- **`story-map-links-to-markdown`** - Link every Epic, Sub-Epic, and Story on the map to its entry in `story-map.md`, and link a Story to its own markdown file when one exists. Anchor an entry link at the node's heading (`story-map.md#e-get-sim`); in drawio, put the link on the cell's `link`. Never indent a heading: write each at column 0 and let the `#` count carry the depth. Write plain text when the target file does not exist, because a reader should move from a map node to the behaviour it names without searching, and a link to a missing file misleads.

---

### scenarios

```yaml
default_format: python
stage: specification
```

#### Overview

Define system behavior by taking concrete examples through scenarios; include preconditions, triggers, and outcomes.  
*testable specifications ensure both humans are aligned on exactly what to build and limits AI hallucination*

#### Sketch

Ask what is already true, what the person or system does, what someone else can see afterward, and which situations change that result. Write the scenarios from those answers.

#### Guidance

**Create testable specifications.** Use **Given** for state the system already has, **When** for the operation under test, and **Then** for results a person or another system can observe. Use **And** to continue the current kind of step. Use **But** for a missing record or an action not taken. Start a new **When** only when a new interaction begins, because each outcome must trace to the operation that produced it.

**Start with the main flow, then inspect every variation.** Cover the successful path first, then validation, field-level errors, cross-field rules, operation gating, service failures, reversals, and recovery that the sources or running product contain. Use separate Scenarios when the flow changes and a Scenario Outline when the same flow applies to many data combinations.

**Use concrete examples.** Provide an example for every domain concept the scenario mentions. Put real domain values in Examples so domain experts and developers can agree on the expected result. Relate examples through domain keys when the model relates them. Every example field must change an input, rule, or expected result, because unused data makes the behaviour harder to see.

**Use the correct evidence mode.** For brownfield capture, inspect the running product when it exists and reconcile the Story Map and Scenarios with observed behaviour before finalizing them. For greenfield specification, agreed Scenarios define intended behaviour before production code exists.

#### Rules

```yaml
alwaysApply: false
globs: "**/*_story.test.*,**/*story_test*,**/*story-test*,**/*-sketch.md"
```

Whenever you write or change Given/When/Then scenarios, or change acceptance tests or production code that those scenarios support. Follow these rules.

If this change will not stay here, follow `practices/stories/story_map.mdc`.

- **`gwt-steps-trace-to-domain-operations`** - Map every Given, When, and Then to a named domain operation or property. Express continuation as an operation on the aggregate that receives control, because routes, waits, and framework calls do not describe domain behaviour.
- **`behavioral-and-system-observable-outcomes`** - Write each Then as a result a person or another system can observe, such as changed information, a returned response, or a changed interface state. Keep internal flags and function-local state out of Then, because they do not prove delivered behaviour.
- **`explore-full-interaction-surface`** - Before finalizing Scenarios and again before generating acceptance tests, inspect every distinct visible behaviour required by the source or running product. Add Scenarios for distinct mechanics, because a happy path cannot protect validation and failure behaviour.
- **`examples-trace-domain-model`** - Provide an example for every domain concept the scenario mentions. Use that concept's own terms and the values the source gives, because a step that names a concept without an example leaves the behaviour unagreed.
- **`reconcile-live-immediately`** - In brownfield work, update the map and Scenario in the same increment when the running product contradicts the current description. Mark intended changes separately, because observed and desired behaviour are different evidence.
- **`flagged-writes-intended-gwt`** - When available evidence cannot exercise required behaviour, write the intended Given, When, and Then and state what evidence is missing, because an evidence gap must not erase the requirement or turn an expectation into an observed fact.
- **`scenario-names-continuation`** - Put the main flow first and make each continuing Then name the next Story on the map. Add a missing map node when a live path continues without one, because Scenarios are alternate flows within Stories rather than substitutes for Stories.
- **`given-only-what-the-system-checks`** - Describe the activity and state that the system actually uses for this behaviour, including state left by a prior Story. Omit off-system history, orphan data, screen names used as state, and fields the decision never reads, because irrelevant setup hides the real preconditions.
- **`given-names-complex-state-root-first`** - Begin complex Given state with the aggregate root, then describe its owned parts in their current state, because an owned entity does not have independent context outside its aggregate.
- **`but-marks-missing-state`** - Use But for a record that is absent or an action the actor did not take; use And for consequences of that absence and name gated operations as enabled or disabled, because But should identify the missing condition rather than its effects.
- **`when-holds-the-operation`** - Put the operation under test in When and, in Then, assert only results it has already produced. For downstream system Stories, describe the request arriving at that system instead of replaying the original user action. Specify enablement and activation as separate behaviours when both are observable, because triggers inside assertions and combined operations hide which action caused the result.
- **`when-names-intent-not-interface-gesture`** - Name the actor's domain intent and subject rather than the button or gesture used to express it. Keep click and tap details in UX artifacts unless the physical interaction is required behaviour, because controls can change while intent remains stable.
- **`expressive-system-interactions`** - Describe each system's When and Then in that system's vocabulary. A caller's Then names the result it receives; a translating intermediary names the incoming caller concept and the returned caller-facing result, because "calls the service" does not explain the work performed.
- **`and-chaining`** - Start each state, interaction, and result block with Given, When, and Then, then continue later steps of the same kind with And. Keep Given conditions in root-first order, start a new When for a new interaction, and keep one interaction's observable results in one Then/And block. Use Background only when more than one Scenario shares the state, because repeated keywords hide which conditions, actions, and results belong together.
- **`outline-requires-many-permutations`** - Use a Scenario Outline when many data combinations follow the same steps. Use separate steps or Scenarios for two alternatives or a changed flow, and keep only example fields that affect behaviour, because examples should show variation rather than conceal structure.
- **`plain-english-gwt-steps`** - Write each step as a readable sentence with a named actor and observable behaviour. Use the plain-English example name rather than a code identifier, because test reports must make sense without source code.
- **`seed-prior-story-as-given`** - Seed a later Story from examples produced by prior Stories instead of replaying their When steps. Reuse fixtures from the owning domain concept and keep the boundary under test real, because each Story must run independently while proving its own behaviour.
- **`domain-terms-link-to-model`** - Link each domain term in Given, When, and Then text and in example tables to its definition in the domain model markdown, `domain-model.md` (DDD) or `class-model.md` (Clean Engineering), anchored at the class or term heading (`domain-model.md#sim-aggregate-root-entity`). With no model file, write the term without a link, because a step that leads to its definition keeps the Scenario and the model on one meaning, and a link to a missing file misleads.

#### Scenario realizations (default on)

After the Given/When/Then text is agreed, **produce scenario realizations by default** unless the user says **no realizations** (or an equivalent opt-out). A realization keeps the GWT skeleton and expands each **When** (and any **Then** that itself triggers observable collaborator or system effects) into the domain call graph at sketch fidelity — same `->` / `<-` interaction notation as `@clean_engineering` **model** (`write-interactions`). **Given** and pure state **Then** steps stay plain domain language; do not invent a graph where there is no interaction.

**Procedure:** Follow `@practices/stories/story-realizations` (scope, walk production code, strip helpers, external systems at the boundary). Attach each graph to the step in the scenario artifact:

- **Markdown:** a ` ```realization ` fenced block immediately under the **When** or expandable **Then** step (`templates/md/scenarios.md`).
- **Code channels:** the stories model carries `realization` on each interaction in regenerable spec data and `#` call-graph comments under the matching `when` / `then` in story tests (`practices/stories/model`).

Place one `{scope-kebab-case}-realization.md` per scope when the user wants a consolidated document; otherwise keep realizations inline in the scenario file. Realizations are specification evidence — they do not replace executable acceptance tests.

---

### acceptance_tests

```yaml
default_format: python
stage: implementation
clean_engineering: code
```

#### Overview

Make specifications executable by transforming them into automated tests that validate production code.  
*Context graduates from being merely machine readable to machine executable. AI is allergic to causing tests to fail.*

#### Sketch

Ask which concrete case proves the outcome, which system already holds the starting state, and what a person can check when the action finishes. Write the examples from those answers.

**Produce:** per lowest sub-epic, `{sub_epic_slug}.story.shared.{lang}` registers shared scenarios; `{sub_epic_slug}.story.domain.spec.{lang}` replays them at domain tier (domain is the only tier with one layer in the filename); `{sub_epic_slug}.story.server.spec.{lang}` and other tier specs name the tier explicitly before `spec`. Markdown scenarios stay `{story_snake}_story.test.md`. Shared Given/When/Then helpers stay `story_test.py` / `story-test.ts`.

#### Guidance

Apply `@stories` `#scenarios` § Guidance and § Rules to acceptance tests. Use the **Test shape ladder** in the `testing-approach` rule under `clean_engineering/rules/`: start with the real application when it is available, use deterministic external-system stubs while developing, and replace them with end-to-end boundaries when requested.

When scenario realizations exist (inline or `{scope}-realization.md`), treat them as the agreed call graph for the **When** under test: implement and assert through the outermost domain entry point and named collaborators the realization names — do not re-route through test-only helpers that the realization stripped away.

**Develop the behaviour, not only the test.** Acceptance-test work owns both the executable specification and the production code that satisfies it. Represent each named scenario example as one code fixture, and do not invent fixture values the scenario does not name. Take one Scenario at a time: write the failing acceptance test, invoke the Clean Engineering companion at `code` fidelity, implement the smallest production change that can pass, rerun the test, refactor when it is green, and then continue to the next behaviour. After two failed fix attempts, diagnose the failure before changing more code.

Refer to [`cdd_guidance/rules/language-tools.md`](../../rules/language-tools.md) for language-specific test tools and idioms.

#### Rules

```yaml
alwaysApply: false
globs: "**/*.story.shared.*,**/*.story.domain.spec.*,**/*.story.server.spec.*,**/*_story.test.*,**/*story_test*,**/*story-test*,**/*-sketch.md"
```

Whenever you create, alter, or delete Spec-by-Example / acceptance tests, or production code they support. Follow these rules.

If this change will not stay here, follow `practices/stories/scenarios.mdc`.


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

## Common mistakes still being made

Scratch pad — mistakes people still make against this practice. Each entry: the mistake, an example, what should have happened instead. (Disposition TBD.)

_No entries yet._

---
