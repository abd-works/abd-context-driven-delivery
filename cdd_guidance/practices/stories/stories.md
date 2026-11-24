## Overview

Map stakeholder and system interactions as behaviours that deliver a solution. Every later fidelity builds on these behaviours, so the story map must describe operations that named actors perform and results they can observe.

---

## Guidance

**Think hierarchically.** Use **Epics** for business capabilities or end-to-end outcomes, **Sub-Epics** for outcomes within an Epic, and **Stories** for discrete user or system interactions with observable results. Decompose Stories into **Scenarios**, then express each Scenario as **Given**, **When**, and **Then** steps. The hierarchy lets a reader move from the business outcome to the behaviour that implements it without losing traceability.

**Write action-oriented interactions.** At every level, name the actor, action, and subject when the format includes actor metadata; name nodes with a base-form verb and a noun. `Manage Customer Orders` says what the Epic achieves, while `Orders` does not. Size each node by its layer: an epic or sub-epic that holds sub-epics groups {{child_band.holding_sub_epics}} of them, a sub-epic holds {{child_band.sub_epic}} stories, and an epic that holds only stories holds {{child_band.flat_epic}}, because shallow chains and crowded nodes both hide the shape of the work. A story holds at most {{story.most_scenarios}} code scenarios; more than {{story.most_scenarios}} and the story is huge. A story with none is waiting for its scenarios, which is fine.

---

## Shared rules

```yaml
alwaysApply: false
globs: "**/*story-map*,**/*_story.test.*,**/*story_test*,**/*story-test*,**/*-sketch.md"
```

Whenever you define or change user interactions and resulting system behavior, at any level of detail. Follow these rules.

- **`vocabulary-traces-to-domain-source`** - Use terms from the domain language and model when they exist, because one shared definition keeps Stories, examples, and code consistent.
- **`read-all-source-context-in-full`** - Before fixing the hierarchy or asking a question about an interaction between systems, read every referenced source that informs the decision, including the owning segment, module context, session records, related Story context, build order, code, recorded observations, and relevant run logs. Name the source and location that supports each important interaction, because titles and search results do not explain behaviour.
- **`do-not-invent-requirements`** - Write only features and behaviour described by a source or explicitly requested by the user. Add a system-to-system interaction only when a named caller invokes it or a source requires it, because an assumed interaction becomes unrequested architecture, Scenarios, and tests. Asking how a described behaviour acts at its edges is required, and is not invention: ask each edge question of the behaviour and take the answer from the source, the running product, or the person, because a behaviour whose edges nobody asked about is specified only for the case its author had in mind.

---

## Fidelities

### story_map

```yaml
default_format: markdown
stage: discovery
outputs:
  markdown: ".context/story-map.md"
  drawio: ".context/story-map.drawio"
  whiteboard: ".context/story-map.whiteboard"
  thin_slice: [".context/thin-slice.md", ".context/thin-slice.drawio", ".context/thin-slice.whiteboard"]
example: "_examples/manage-customer-orders/md/story-map.md"
leaves_out:
  drawio: "the document's front matter, its title, and prose that is not an epic, a sub-epic, a story or an actor. They stay in story-map.md"
  whiteboard: "the document's front matter, its title, and prose that is not an epic, a sub-epic, a story or an actor. They stay in story-map.md"
```

#### Overview

Scope the solution using a hierarchy of business goals, user interactions, and system behaviors.  
*a simple graph is easier to change, compare, and reorganize. Humans catch AI Order-of-Magnitude sizing errors.*

#### Sketch

Ask who is trying to reach this outcome, what they need in front of them before they act, what a successful result looks like for them, and what stops them. Ask how that differs for each person who touches the outcome. Write the epic, the people, and the stories from those answers. Do not ask the user to choose one story or a story per system. Decide each epic's shape from those answers: give it sub-epics when its stories fall into separate outcomes, such as placing, tracking, and cancelling an order, and keep it flat when they are one outcome. The sketch fixes the shape generate fills, so a shape decided here by habit is the shape the map keeps.

#### Guidance

**Name the layers.** Actors are people or systems (`Customer`, `Support Agent`, `Order Service`). Epics name an end-to-end outcome (`Manage Customer Orders`). Sub-Epics name one outcome inside an Epic (`Place Customer Order`). Stories name one observable interaction that can be tested on its own (`Submit Order`).

**Decompose through interactions.** Cover the business capability with Epics, then ground each Epic in Stories that demonstrate real behaviour. Find the **walking skeleton**, the smallest end-to-end path that works and delivers value, and validate it before adding later increments. Split increments by actor, data, workflow, channel, interface, non-functional requirement, or business rule when that creates a demonstrable step.

**Map the complete outcome.** Include the primary path, supporting actors, system interactions, reversals, and recovery behaviour needed to achieve the outcome. Administrators, support staff, partner onboarding, cancellations, refunds, escalations, and failures belong on the map when sources require them, because a forward path alone does not describe the working product. A sub-epic's stories include the edge and error cases that are stories in their own right, such as a refund, a retry after a failure, or a refusal that starts its own flow; the nine conditions in the scenarios Guidance are the prompt for finding them, and a smaller case is a Scenario of the story it belongs to (`edge-and-error-cases-have-scenarios`).

**Take the map's shape from the sources.** Decide for each epic on its own whether its stories fall into separate outcomes, and give it sub-epics when they do; a map where most epics hold two to five sub-epics of a few stories each is normal when the sources describe that many outcomes. Every map has its own shape, so do not copy the structure of an example, a template, another session's map, or a test fixture: examples show notation, naming, and depth, and their epic count and nesting belong to their own domain. When you generate a map again, read the story-map.md already there as a draft to check against the sources, not as the frame to fill: regroup its stories where the sources describe other outcomes, because keeping the old epics by default repeats every shaping mistake the first pass made.

**Treat a system hop as a boundary interaction.** A hop is an observable request and response across a named system boundary, not every internal function call. Keep internal fan-out within the boundary Story unless another system exposes its own observable interaction. Give an intermediary its own Story when it validates, decides, or translates; keep simple forwarding or display as an outcome on the caller's Story.

**Play the map in Claude Design.** For a stakeholder session, render the map as the UX practice's Claude Design story canvas: one story-map artboard laid out like the drawio, one screen thumbnail per story, and a story explorer that runs each story's screen on its scenarios' fixtures. The canvas shows the stories on their screens, so the UX practice draws it; follow `practices/ux/model/claude_design/story_canvas.md`.

#### Scaffold

**When scaffolding only** (`/partition` or a names only first cut), follow this subsection. Write only verb-noun Epic, Sub-Epic, and Story names. Carry the actor on every Story — `{Actor} --> {Verb Noun}` — because the actor is part of the Story's name at every depth. Read the source material in full, split distinct mechanics, and apply `verb-noun-format`, `branch-on-mechanical-uniqueness`, and `do-not-invent-requirements`. Do not write Scenarios, increments, or explanatory prose. Do not read or apply the Rules below. **Stop reading this skill when scaffolding.**

#### Rules

```yaml
alwaysApply: false
globs: "**/*story-map*,**/*-sketch.md"
```

Whenever you create, alter, or delete epics, sub-epics, or stories on the map, or change scenarios or acceptance work that forces a map change. Follow these rules.

If this change will not stay here, follow `practices/stories.mdc`.

- **`verb-noun-format`** - Name every Epic, Sub-Epic, and Story with a base-form verb and noun. Epics and Sub-Epics name goals rather than an actor's activity or a supporting system call, because grammar alone does not preserve the right level of abstraction. A generic verb (handle, process, manage, perform, do, execute, run) is not wrong in itself: the graph passes it here, lists a Story that opens with one as a candidate under `story-name-captures-system-mechanic`, and the judgment decides it from its context. It passes when its noun and its place on the map make the action plain, such as an Epic *Manage Tickets* gathering the ticket stories below it; it fails when it hides which mechanic the node performs, such as a Story *Handle Ticket* standing for deleting one. {{decided.verb_noun_format}}
- **`story-name-captures-system-mechanic`** - At Story level, use a verb that names the operation and a noun that names the record or concept it acts on. Replace vague names such as `Handle Request`, `Process Data`, or `Manage Record`, because they hide what the system does. {{decided.story_name_captures_system_mechanic}}
- **`child-count-fits-layer`** - Size an epic or sub-epic by the layer it is: one that holds sub-epics groups {{child_band.holding_sub_epics}} children, a sub-epic that holds only stories holds {{child_band.sub_epic}}, and a top epic that holds only stories holds {{child_band.flat_epic}}. Restructure outside the band: split a crowded node, and move an epic of two or three stories under the neighbouring epic whose outcome it serves rather than padding it, because readers cannot reason easily about shallow chains or crowded nodes, and a band that only counts stories pushes every map toward flat epics. Do not apply this band to the scenarios under a story. {{decided.child_count_fits_layer}}
- **`story-scenarios-at-most-seven`** - A story holds at most {{story.most_scenarios}} code scenarios. More than {{story.most_scenarios}} and the story is huge — split it, because one story should be one interaction a reader can test in a few examples. A story with no scenarios passes: its scenarios are simply not written yet. {{decided.story_scenarios_at_most_seven}}
- **`branch-on-mechanical-uniqueness`** - Create separate Stories for distinct mechanics and use Scenarios or examples when several source entries share one mechanic, because one Story per source entry duplicates behaviour while one Story for different mechanics hides work. {{decided.branch_on_mechanical_uniqueness}}
- **`right-size-story-nodes`** - Put one observable interaction at one system boundary in each Story. Keep the caller's request, response, and translation together; give the callee its own boundary Story; keep display-only and forwarding-only work as outcomes, because splitting every internal call or interface step obscures the interaction being tested. {{decided.right_size_story_nodes}}
- **`behaviours-not-build-tasks`** - Write each Story as a behaviour of the product: what an actor does with it and what it does in return. Keep the work of getting that behaviour to exist, such as building, defining, designing, setting up, migrating or validating it, in plans and tasks, because a story about making the thing has no Given, When and Then of its own and tells nobody what the product does. How often the behaviour happens does not matter: one that happens once is as much a behaviour as one that happens every day. A judge reads the story's name and description for this; no name pattern decides it.
- **`kebab-case-paths`** - Name every epic, sub-epic, and story folder in lowercase kebab-case (`onboard-a-customer/`) and every story file in lowercase (`create_customer_story.test.ts`, `create-customer.story.shared.ts`), never CamelCase (`HandleRequest_story.test.ts`), because the folders mirror the story map and a reader finds a story's file from its name only when one case holds everywhere. {{decided.kebab_case_paths}}
- **`story-map-links-to-markdown`** - Link every Epic, Sub-Epic, and Story on the map to its entry in `story-map.md`, and link a Story to its own markdown file when one exists. Anchor an entry link at the node's heading (`story-map.md#e-get-sim`); in drawio, put the link on the cell's `link`. Never indent a heading: write each at column 0 and let the `#` count carry the depth. Write plain text when the target file does not exist, because a reader should move from a map node to the behaviour it names without searching, and a link to a missing file misleads.

---

### scenarios

```yaml
default_format: python
stage: specification
outputs:
  python:
    - "story_tests/{epic}/{sub-epic}/{story}/{story_snake}_story.test.py"
    - "story_tests/{epic}/{story}/{story_snake}_story.test.py"
  typescript:
    - "story_tests/{epic}/{sub-epic}/{story}/{story_snake}_story.test.ts"
    - "story_tests/{epic}/{story}/{story_snake}_story.test.ts"
    - "story_tests/**/story-test.ts"
  javascript:
    - "story_tests/{epic}/{sub-epic}/{story}/{story_snake}_story.test.js"
    - "story_tests/{epic}/{story}/{story_snake}_story.test.js"
    - "story_tests/**/story-test.js"
  markdown:
    - "story_tests/{epic}/{sub-epic}/{story_snake}_story.test.md"
    - "story_tests/{epic}/{epic_snake}_story.test.md"
  realization: ".context/{scope}-scenario-realization.md"
example: "_examples/telco-website/onboard-a-customer"
```

#### Overview

Define system behavior by taking concrete examples through scenarios; include preconditions, triggers, and outcomes.  
*testable specifications ensure both humans are aligned on exactly what to build and limits AI hallucination*

#### Sketch

Ask what is already true, what the person or system does, what someone else can see afterward, and which situations change that result. Write the scenarios from those answers.

#### Guidance

**Create testable specifications.** Use **Given** for state the system already has, **When** for the operation under test, and **Then** for results a person or another system can observe. Use **And** to continue the current kind of step. Use **But** for a missing record or an action not taken. Start a new **When** only when a new interaction begins, because each outcome must trace to the operation that produced it.

**Start with the main flow, then inspect every variation.** Cover the successful path first, then validation, field-level errors, cross-field rules, operation gating, service failures, reversals, and recovery that the sources or running product contain. Use separate Scenarios when the flow changes and a Scenario Outline when the same flow applies to many data combinations.

**Write the edge and error cases as scenarios.** A source describes the case its author had in mind and is usually silent about what happens around it, so a story's scenarios cover its edge and error cases beside its main flow, each as an ordinary Scenario. Use the nine conditions below as a prompt for which Scenarios to write: ask each of the story, and write a Scenario for every one that applies. They are a prompt, not a checklist to record: a condition that does not apply is simply not written, and no table, list, or note of the conditions is kept in the scenarios file or anywhere beside it. Where a condition plainly applies and neither the source nor the running product says what should happen, ask the person in the chat and write the Scenario from the answer. Where a case is big enough to be a story of its own, such as a refund or a recovery after a failure, it is a Story under the sub-epic on the map. The conditions fit any product; each shows examples from two domains.

- **Missing or empty input.** A value the action needs is not given, or is given blank: a bank transfer sent with no amount; a booking made with no date.
- **Malformed input, or input at or past a limit.** A value has the wrong form, or sits at or beyond the smallest or largest the action accepts: a shop order for zero items, or for more than the stock holds; a thermostat set above its highest temperature.
- **Duplicate.** The thing being created or added already exists: opening a bank account with an email address another account holds; adding a discount code the basket already carries.
- **Repeated action.** The same actor does the same action a second time: pressing Pay twice in a shop; cancelling a booking that is already cancelled.
- **Two actors at once.** Two people or systems act on the same thing at the same moment: two guests booking the last room; two withdrawals drawn on one bank balance.
- **Interrupted action.** The action stops partway, and the next attempt finds what it left: power lost while a device installs an update; a shop's connection dropping between payment and confirmation.
- **Dependency absent, unavailable, slow, or wrong.** Something the action relies on is not there, does not answer, answers late, or answers with something unusable: a bank's fraud check timing out; a device's sensor returning no reading.
- **Changed or gone since last seen.** The thing acted on was changed or removed after the actor last saw it: a price changing while the item sits in the basket; a flight cancelled while the traveller chooses a seat.
- **Actor not allowed.** The actor has no right to do this, or to do it to this thing: a bank teller approving a loan above their limit; a guest user changing a device's owner settings.

**Use concrete examples.** Provide an example for every domain concept the scenario mentions. Put real domain values in Examples so domain experts and developers can agree on the expected result. Relate examples through domain keys when the model relates them. Every example field must change an input, rule, or expected result, because unused data makes the behaviour harder to see.

**Use the correct evidence mode.** For brownfield capture, inspect the running product when it exists and reconcile the Story Map and Scenarios with observed behaviour before finalizing them. For greenfield specification, agreed Scenarios define intended behaviour before production code exists.

#### Scaffold

**When scaffolding only** (`/partition` or a names-only first cut, not full generation at this fidelity), follow this subsection. Do not use the Guidance or Rules below.

Rough scenario index for a **partition** pass or first cut — the story map's epics and stories, each story with the names of its scenarios (`{Actor} {does something} {and sees a result}`) and the actor it serves. No Given/When/Then steps, no examples, no backgrounds yet: a scenario name says which case the source describes, and the steps are written when the scenarios are generated.

#### Rules

```yaml
alwaysApply: false
globs: "**/*_story.test.*,**/*story_test*,**/*story-test*,**/*-sketch.md"
```

Whenever you write or change Given/When/Then scenarios, or change acceptance tests or production code that those scenarios support. Follow these rules.

If this change will not stay here, follow `practices/stories/stories-story-map.mdc`.

- **`gwt-steps-trace-to-domain-operations`** - Map every Given, When, and Then to a named domain operation or property. Express continuation as an operation on the aggregate that receives control, because routes, waits, and framework calls do not describe domain behaviour. {{decided.gwt_steps_trace_to_domain_operations}}
- **`behavioral-and-system-observable-outcomes`** - Write each Then as a result a person or another system can observe, such as changed information, a returned response, or a changed interface state. Keep internal flags and function-local state out of Then, because they do not prove delivered behaviour. {{decided.behavioral_and_system_observable_outcomes}}
- **`explore-full-interaction-surface`** - Before finalizing Scenarios and again before generating acceptance tests, inspect every distinct visible behaviour required by the source or running product. Add Scenarios for distinct mechanics, because a happy path cannot protect validation and failure behaviour.
- **`edge-and-error-cases-have-scenarios`** - Give every Story the Scenarios that cover its edge and error cases, written as ordinary Scenarios beside its main flow, and give a sub-epic a Story for each edge or error case big enough to be a story of its own. Use the nine conditions in this fidelity's Guidance as a prompt for which to write, and write nothing for a condition that does not apply. Where a case plainly applies and the source and the running product are silent on what should happen, ask the person in the chat and write the Scenario from the answer. Keep no table, list, or note of the conditions beside the Scenarios, because a case is covered only when a Scenario says what the system does, and a record kept beside the Scenarios is a second thing to maintain that tests nothing.
- **`examples-trace-domain-model`** - Provide an example for every domain concept the scenario mentions. Use that concept's own terms and the values the source gives, because a step that names a concept without an example leaves the behaviour unagreed. {{decided.examples_trace_domain_model}}
- **`reconcile-live-immediately`** - In brownfield work, update the map and Scenario in the same increment when the running product contradicts the current description. Mark intended changes separately, because observed and desired behaviour are different evidence.
- **`flagged-writes-intended-gwt`** - When available evidence cannot exercise required behaviour, write the intended Given, When, and Then and state what evidence is missing, because an evidence gap must not erase the requirement or turn an expectation into an observed fact. {{decided.flagged_writes_intended_gwt}}
- **`scenario-names-continuation`** - Put the main flow first and make each continuing Then name the next Story on the map. Add a missing map node when a live path continues without one, because Scenarios are alternate flows within Stories rather than substitutes for Stories. {{decided.scenario_names_continuation}}
- **`scenarios-name-a-story-on-the-map`** - Head each story's scenarios with the name the story has on the story map, and add a story to the map before writing its scenarios. A scenarios file that names a story the map does not hold is read with its scenarios under no epic and reported, because scenarios the map cannot place are otherwise left out of every check without a word. {{decided.scenarios_name_a_story_on_the_map}}
- **`given-only-what-the-system-checks`** - Describe the activity and state that the system actually uses for this behaviour, including state left by a prior Story. Omit off-system history, orphan data, screen names used as state, and fields the decision never reads, because irrelevant setup hides the real preconditions.
- **`given-names-complex-state-root-first`** - Begin complex Given state with the aggregate root, then describe its owned parts in their current state, because an owned entity does not have independent context outside its aggregate. {{decided.given_names_complex_state_root_first}}
- **`but-marks-missing-state`** - Use But for a record that is absent or an action the actor did not take; use And for consequences of that absence and name gated operations as enabled or disabled, because But should identify the missing condition rather than its effects. {{decided.but_marks_missing_state}}
- **`when-holds-the-operation`** - Put the operation under test in When and, in Then, assert only results it has already produced. For downstream system Stories, describe the request arriving at that system instead of replaying the original user action. Specify enablement and activation as separate behaviours when both are observable, because triggers inside assertions and combined operations hide which action caused the result. {{decided.when_holds_the_operation}}
- **`when-names-intent-not-interface-gesture`** - Name the actor's domain intent and subject rather than the button or gesture used to express it. Keep click and tap details in UX artifacts unless the physical interaction is required behaviour, because controls can change while intent remains stable. {{decided.when_names_intent_not_interface_gesture}}
- **`expressive-system-interactions`** - Describe each system's When and Then in that system's vocabulary. A caller's Then names the result it receives; a translating intermediary names the incoming caller concept and the returned caller-facing result, because "calls the service" does not explain the work performed.
- **`and-chaining`** - Start each state, interaction, and result block with Given, When, and Then, then continue later steps of the same kind with And. Keep Given conditions in root-first order, start a new When for a new interaction, and keep one interaction's observable results in one Then/And block. Use Background only when more than one Scenario shares the state, because repeated keywords hide which conditions, actions, and results belong together. {{decided.and_chaining}}
- **`outline-requires-many-permutations`** - Use a Scenario Outline when many data combinations follow the same steps. Use separate steps or Scenarios for two alternatives or a changed flow, and keep only example fields that affect behaviour, because examples should show variation rather than conceal structure. {{decided.outline_requires_many_permutations}}
- **`plain-english-gwt-steps`** - Write each step as a readable sentence with a named actor and observable behaviour. Use the plain-English example name rather than a code identifier, because test reports must make sense without source code. {{decided.plain_english_gwt_steps}}
- **`seed-prior-story-as-given`** - Seed a later Story from examples produced by prior Stories instead of replaying their When steps. Reuse fixtures from the owning domain concept and keep the boundary under test real, because each Story must run independently while proving its own behaviour.
- **`domain-terms-link-to-model`** - Link each domain term in Given, When, and Then text and in example tables to its definition in the domain model markdown, `domain-model.md` (DDD) or `class-model.md` (Clean Engineering), anchored at the class or term heading (`domain-model.md#sim-aggregate-root-entity`). A step that leads to its definition keeps the Scenario and the model on one meaning. Where no model is written yet, write the term without a link, or link it to the heading the model will give it: the knowledge graph records an edge from the step to the class only when the link reaches a class it read, and reports nothing for a link that reaches none, because Scenarios are often written before the model they will join. {{decided.domain_terms_link_to_model}}
- **`then-observes-an-example`** - Where a domain model or a class model is written for the Story's area of the map, name in each Then, or in a Given of its Scenario or of its Story's Background, the example whose outcome the Then observes. A Story's area is the Stories directly under its sub-epic or epic, with their Scenarios, steps, and examples. A model is written for the area when the knowledge graph joins one of those steps or examples to a class of the domain model (DDD) or the class model (Clean Engineering): a linked domain term leads to a class heading the graph read, a step calls an operation of a class, or an example is built as a class. Where no model is written for the area, a Then needs no example and an example needs no class, because an outcome with no example cannot be checked against the model, while asking for a model nobody has written stops Scenarios from being written first. {{decided.then_observes_an_example}}

#### Scenario realizations (default on)

After the Given/When/Then text is agreed, **produce scenario realizations by default** unless the user says **no realizations** (or an equivalent opt-out). A realization keeps the GWT skeleton and expands each **When** (and any **Then** that itself triggers observable collaborator or system effects) into the domain call graph at sketch fidelity — same `->` / `<-` interaction notation as `@clean_engineering` **model** (`write-interactions`). **Given** and pure state **Then** steps stay plain domain language; do not invent a graph where there is no interaction.

**Procedure:** Follow `@practices/stories/story-realizations` (scope, walk production code, strip helpers, external systems at the boundary). Attach each graph to the step in the scenario artifact:

- **Markdown:** a ` ```realization ` fenced block immediately under the **When** or expandable **Then** step (`templates/md/scenarios.md`).
- **Code channels:** the stories model carries `realization` on each interaction in regenerable spec data and `#` call-graph comments under the matching `when` / `then` in story tests (`practices/stories/model`).

Place one `{scope-kebab-case}-scenario-realization.md` per scope when the user wants a consolidated document; otherwise keep realizations inline in the scenario file. Realizations are specification evidence — they do not replace executable acceptance tests.

A scenario realization is not the BDD realization. The scenario realization follows the story map: each Scenario's Given/When/Then, with the call graph under the step that acts. The BDD realization (`@bdd` `#realization`, `{scope}-bdd-realization.md`) follows the spec files: each `it should`, with the call graph its test runs. The two use the same `->` / `<-` notation and name the same operations, so they live in separate files, because a reader has to know whether a graph realizes a Scenario or an observation.

---

### acceptance_tests

```yaml
default_format: python
stage: implementation
clean_engineering: code
outputs:
  python:
    - "story_tests/{epic}/{sub-epic}/{sub_epic_slug}.story.shared.py"
    - "story_tests/{epic}/{sub-epic}/{sub_epic_slug}.story.domain.spec.py"
    - "story_tests/{epic}/{sub-epic}/{sub_epic_slug}.story.server.spec.py"
    - "story_tests/{epic}/{sub-epic}/{story}/{story_snake}_story.test.py"
    - "story_tests/{epic}/{epic_slug}.story.shared.py"
    - "story_tests/{epic}/{epic_slug}.story.domain.spec.py"
    - "story_tests/{epic}/{epic_slug}.story.server.spec.py"
    - "story_tests/{epic}/{story}/{story_snake}_story.test.py"
    - "{module}/{concept}_examples.py"
    - "story_tests/**/story_test.py"
  typescript:
    - "story_tests/{epic}/{sub-epic}/{sub_epic_slug}.story.shared.ts"
    - "story_tests/{epic}/{sub-epic}/{sub_epic_slug}.story.domain.spec.ts"
    - "story_tests/{epic}/{sub-epic}/{sub_epic_slug}.story.server.spec.ts"
    - "story_tests/{epic}/{sub-epic}/{story}/{story_snake}_story.test.ts"
    - "story_tests/{epic}/{sub-epic}/{sub_epic_slug}.story.ui.spec.ts"
    - "story_tests/{epic}/{epic_slug}.story.shared.ts"
    - "story_tests/{epic}/{epic_slug}.story.domain.spec.ts"
    - "story_tests/{epic}/{epic_slug}.story.server.spec.ts"
    - "story_tests/{epic}/{story}/{story_snake}_story.test.ts"
    - "story_tests/{epic}/{epic_slug}.story.ui.spec.ts"
    - "story_tests/{epic}/examples/{concept}.examples.ts"
    - "story_tests/**/story-test.ts"
  javascript:
    - "story_tests/{epic}/{sub-epic}/{sub_epic_slug}.story.shared.js"
    - "story_tests/{epic}/{sub-epic}/{sub_epic_slug}.story.domain.spec.js"
    - "story_tests/{epic}/{sub-epic}/{sub_epic_slug}.story.server.spec.js"
    - "story_tests/{epic}/{sub-epic}/{story}/{story_snake}_story.test.js"
    - "story_tests/{epic}/{sub-epic}/{sub_epic_slug}.story.ui.spec.js"
    - "story_tests/{epic}/{epic_slug}.story.shared.js"
    - "story_tests/{epic}/{epic_slug}.story.domain.spec.js"
    - "story_tests/{epic}/{epic_slug}.story.server.spec.js"
    - "story_tests/{epic}/{story}/{story_snake}_story.test.js"
    - "story_tests/{epic}/{epic_slug}.story.ui.spec.js"
    - "story_tests/{epic}/examples/{concept}.examples.js"
    - "story_tests/**/story-test.js"
example: "_examples/telco-website/onboard-a-customer"
```

#### Overview

Make specifications executable by transforming them into automated tests that validate production code.  
*Context graduates from being merely machine readable to machine executable. AI is allergic to causing tests to fail.*

#### Sketch

Ask which concrete case proves the outcome, which system already holds the starting state, and what a person can check when the action finishes. Write the examples from those answers.

**Produce:** a story whose scenarios are written as one runnable file, `{story_snake}_story.test.{lang}` with its steps' bodies filled in, is its own acceptance test. Otherwise, per lowest sub-epic, `{sub_epic_slug}.story.shared.{lang}` registers shared scenarios; `{sub_epic_slug}.story.domain.spec.{lang}` replays them at domain tier (domain is the only tier with one layer in the filename); `{sub_epic_slug}.story.server.spec.{lang}` and other tier specs name the tier explicitly before `spec`. Markdown scenarios stay `{story_snake}_story.test.md`. Shared Given/When/Then helpers stay `story_test.py` / `story-test.ts` / `story-test.js`. Example fixtures in TypeScript and JavaScript sit in the epic's `examples/` folder (`{concept}.examples.ts`); Python ones sit beside the code they build (`{module}/{concept}_examples.py`, as `space/kanban/session_board_examples.py` does), because a story folder's name holds hyphens, which no Python import can name.

#### Guidance

Apply `@stories` `#scenarios` § Guidance and § Rules to acceptance tests. Use the **Test shape ladder** in the `testing-approach` rule under `clean_engineering/rules/`: start with the real application when it is available, use deterministic external-system stubs while developing, and replace them with end-to-end boundaries when requested.

When scenario realizations exist (inline or `{scope}-scenario-realization.md`), treat them as the agreed call graph for the **When** under test: implement and assert through the outermost domain entry point and named collaborators the realization names — do not re-route through test-only helpers that the realization stripped away.

**Develop the behaviour, not only the test.** Acceptance-test work owns both the executable specification and the production code that satisfies it. Represent each named scenario example as one code fixture, and do not invent fixture values the scenario does not name. Take one Scenario at a time: write the failing acceptance test, invoke the Clean Engineering companion at `code` fidelity, implement the smallest production change that can pass, rerun the test, refactor when it is green, and then continue to the next behaviour. After two failed fix attempts, diagnose the failure before changing more code.

**Judge each screen against its step.** A browser story test (`*.story.ui.spec.ts`) runs each Given, When and Then through `step(page, '<step text>', body)` (`space/kanban/app/tests/step-capture.ts`), which screenshots the settled page and writes the step's row to the run's `results.json`. Whether the AI walks a scenario by hand or reviews a run, it reads each screenshot against its step text and asks whether a person looking at the screen would agree the step happened: the Given's state is visible, the When's action took effect, the Then's outcome is shown with the right values, labels and messages. A Given about state the screen cannot show, such as a file's contents, is judged by what the next step shows of it. TDD's Reviewing e2e screens says when this happens and what follows a miss.

Refer to [`cdd_guidance/references/language-tools.md`](../../references/language-tools.md) for language-specific test tools and idioms.

#### Scaffold

**When scaffolding only** (`/partition` or a names-only first cut, not full generation at this fidelity), follow this subsection. Do not use the Guidance or Rules below.

Rough story-test index for a **partition** pass or first cut — for each story, the story-test file it becomes (`tests/<epic>/<story>_story.test.ts` or the language's spelling) and the scenarios that file will hold, with the domain objects and examples each scenario names. No test bodies, step library, or production code yet.

#### Rules

```yaml
alwaysApply: false
globs: "**/*.story.shared.*,**/*.story.domain.spec.*,**/*.story.server.spec.*,**/*.story.ui.spec.*,**/*_story.test.*,**/*story_test*,**/*story-test*,**/*-sketch.md"
```

Whenever you create, alter, or delete Spec-by-Example / acceptance tests, or production code they support. Follow these rules.

If this change will not stay here, follow `practices/stories/stories-scenarios.mdc`.


- **`examples-declare-seed-vs-interaction`** - Identify each fixture as **Seed** state owned by a system or **Interaction** data entered, displayed, or validated through the product. Use both when the Story needs both, because persisted records and user-facing data often represent the same concept differently.
- **`shared-example-fixtures`** - Represent each named example as one reusable code fixture for its domain concept. Shape that fixture from the owning system: the external system's record shape at that boundary and the product's aggregate shape inside the domain, because a convenient mixed object conceals a mapping error and a copied value drifts from the Scenario.
- **`seed-state-at-its-real-owner`** - Seed and inspect state through the component that owns it in the production architecture. When a rich domain layer integrates with an external system, seed the external test adapter and exercise production behaviour through the aggregates and repositories above it. When the repository is itself the storage boundary and no separate system exists, direct repository setup and loading are appropriate, because tests should reflect the architecture rather than create an extra layer.
- **`missed-screen-change-tested-at-its-owner`** - When a screen changed and no test caught it, write the missing test at the layer that owns the behaviour: a rule or a value in the story markdown and its domain story test, a control or label in the browser story test, and pure look in CSS alone. A test written at the wrong layer catches the change where it shows rather than where it is decided, so the next screen that shows the same value breaks unseen.
- **`every-step-captured`** - Run every Given, When and Then of a browser story test through `step`, so each records its screenshot and result under its story › scenario › step key, with the step text as the scenario writes it. A step that is not captured cannot be compared with the walk or the last accepted run, and a break on its screen goes unseen.
- **`separate-test-controls-from-production-contracts`** - Keep seed, reset, and inspection operations off the production repository or adapter contract. Add them to a testable extension, test adapter, or stub when acceptance setup needs them, because test control is useful without becoming a production domain capability.
- **`system-stubs-domain-real`** - Before creating an external-system stub, inspect the real integration contract again and identify the boundary that production code calls. Make the stub reproduce that boundary's operations, request and response structures, identifiers, state changes, and failure behaviour; do not invent a simpler test API. Keep domain aggregates, repositories, validation, mapping, and state transitions real, because an inaccurate stub, silent no-op, or test-only domain operation can make a test pass without implementing production behaviour.
- **`assert-domain-behavior-not-seeded-state`** - Exercise the product's domain entry point after seeding its underlying state owner and assert the product result. Inspect that owner for stored data or outbound effects only after the product initiated them, because reading back data inserted during Given proves only that the fixture was stored.
- **`infrastructure-in-lifecycle-hooks`** - Put browser startup, application wiring, and shutdown in lifecycle hooks; keep Given for domain state. Load an aggregate once at the highest Given that needs it and reach owned entities through their aggregate root, because infrastructure and shortcut lookups obscure the behaviour's real state.
- **`inline-simple-gwt-bodies`** - Keep simple Given, When, and Then bodies inline and use example exports directly. Extract a helper only for repeated interaction that is not a domain operation, such as a screen gesture or application wiring, because pass-through helpers add names without adding meaning.
- **`domain-operations-inline-in-steps`** - Call each domain operation — a repository load with the identity in hand, an aggregate command, the refusal it raises — directly in the Given, When, or Then that relies on it. Do not wrap domain calls in story-file helpers such as `signIn` or `reloadAccount`. When several steps need the same prior state, seed it with a `seed…` fixture in the examples file, because the acceptance test exists to show which domain operation each step runs and what it proves.
- **`code-steps-invoke-code`** - Make each When of a story test in code call the domain operation it tests, so the graph links the step to that operation in Clean Engineering. A When that calls only the test's own helpers or its examples' seeds tests nothing. A When in markdown is asked once it has a realization: each operation the realization names is matched, through the step's domain-term links, to that operation in the domain model or class model they lead to, and the step is linked to it as a story test's step is linked to code; a When whose realization names no operation that model declares fails, because a realization that names nothing real specifies nothing the code can be held to. {{decided.code_steps_invoke_code}}
- **`extract-assertion-helper`** - Extract the same assertion shape after it appears more than twice and pass its concrete values as data, because copied assertions become inconsistent when behaviour changes.

---

## Common mistakes still being made

Scratch pad — mistakes people still make against this practice. Each entry: the mistake, an example, what should have happened instead. (Disposition TBD.)

_No entries yet._

---
