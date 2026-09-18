**Default format:** markdown

**Produce:** Story map.

**Goal:** Define a visual hierarchy of how users and systems achieve business outcomes: `Epic` -> nestable `Sub-Epic` -> `Story`. It is easier to change the map while Stories are titles than after Scenarios, screens, and tests exist.

**Actors** are people or systems that interact with the system being described. Examples include `Customer`, `Support Agent`, `Order Service`, and `Payment Provider`.

**Epics** name major business capabilities or end-to-end outcomes. Examples include `Manage Customer Orders` and `Process Payments`.

**Sub-Epics** name one outcome within an Epic and contain the interactions that achieve it. Examples include `Place Customer Order` and `Collect Payment`.

**Stories** name discrete, observable interactions that can be tested independently. Examples include `Submit Order`, `Validate Payment`, and `Authorize Card Transaction`.

### Guidance

**Decompose through interactions.** Cover the business capability with Epics, then ground each Epic in Stories that demonstrate real behaviour. Find the **walking skeleton**, the smallest end-to-end path that works and delivers value, and validate it before adding later increments. Split increments by actor, data, workflow, channel, interface, non-functional requirement, or business rule when that creates a demonstrable step.

**Map the complete outcome.** Include the primary path, supporting actors, system interactions, reversals, and recovery behaviour needed to achieve the outcome. Administrators, support staff, partner onboarding, cancellations, refunds, escalations, and failures belong on the map when sources require them, because a forward path alone does not describe the working product.

**Treat a system hop as a boundary interaction.** A hop is an observable request and response across a named system boundary, not every internal function call. Keep internal fan-out within the boundary Story unless another system exposes its own observable interaction. Give an intermediary its own Story when it validates, decides, or translates; keep simple forwarding or display as an outcome on the caller's Story.

### Scaffold

**When scaffolding only** (`/partition` or a names-only first cut), follow this subsection. Write only verb-noun Epic, Sub-Epic, and Story names. Read the source material in full, split distinct mechanics, and apply `verb-noun-format`, `branch-on-mechanical-uniqueness`, and `do-not-invent-requirements`. Do not write Scenarios, increments, or explanatory prose. Do not read or apply the Rules below. **Stop reading this skill when scaffolding.**

### Rules

- **`verb-noun-format`** - Name every Epic, Sub-Epic, and Story with a base-form verb and noun. Epics and Sub-Epics name goals rather than an actor's activity or a supporting system call, because grammar alone does not preserve the right level of abstraction.
- **`story-name-captures-system-mechanic`** - At Story level, use a verb that names the operation and a noun that names the record or concept it acts on. Replace vague names such as `Handle Request`, `Process Data`, or `Manage Record`, because they hide what the system does.
- **`four-to-nine-children`** - Keep 4-9 direct children, warn at 3 or 10, and restructure at 2 or fewer or 11 or more, because readers cannot reason easily about shallow chains or crowded nodes.
- **`branch-on-mechanical-uniqueness`** - Create separate Stories for distinct mechanics and use Scenarios or examples when several source entries share one mechanic, because one Story per source entry duplicates behaviour while one Story for different mechanics hides work.
- **`right-size-story-nodes`** - Put one observable interaction at one system boundary in each Story. Keep the caller's request, response, and translation together; give the callee its own boundary Story; keep display-only and forwarding-only work as outcomes, because splitting every internal call or interface step obscures the interaction being tested.
- **`behaviours-not-one-time-tasks`** - Use Stories for repeatable stakeholder or system interactions that can be expressed as GWT more than once. Keep one-time renames, migrations, and repository changes in plans or tasks, because completed maintenance is not recurring product behaviour.

---

### Guidance

**Create testable specifications.** Use **Given** for state the system already has, **When** for the operation under test, and **Then** for results a person or another system can observe. Use **And** to continue the current kind of step. Use **But** for a missing record or an action not taken. Start a new **When** only when a new interaction begins, because each outcome must trace to the operation that produced it.

**Start with the main flow, then inspect every variation.** Cover the successful path first, then validation, field-level errors, cross-field rules, operation gating, service failures, reversals, and recovery that the sources or running product contain. Use separate Scenarios when the flow changes and a Scenario Outline when the same flow applies to many data combinations.

**Use concrete examples.** Put real domain values in Examples so domain experts and developers can agree on the expected result. Relate examples through domain keys when the model relates them. Acceptance tests represent the same named examples as code fixtures rather than inventing new values. Every example field must change an input, rule, or expected result, because unused data makes the behaviour harder to see.

**Use the correct evidence mode.** For brownfield capture, inspect the running product when it exists and reconcile the Story Map and Scenarios with observed behaviour before finalizing them. For greenfield specification, agreed Scenarios define intended behaviour before production code exists.

### Rules

- **gwt-steps-trace-to-domain-operations** — Map every Given, When, and Then to a named domain operation or property. Express continuation as an operation on the aggregate that receives control, because routes, waits, and framework calls do not describe domain behaviour.
- **behavioral-and-system-observable-outcomes** — Write each Then as a result a person or another system can observe, such as changed information, a returned response, or a changed interface state. Keep internal flags and function-local state out of Then, because they do not prove delivered behaviour.
- **explore-full-interaction-surface** — Before finalizing Scenarios and again before generating acceptance tests, inspect every distinct visible behaviour required by the source or running product. Add Scenarios for distinct mechanics, because a happy path cannot protect validation and failure behaviour.
- **reconcile-live-immediately** — In brownfield work, update the map and Scenario in the same increment when the running product contradicts the current description. Mark intended changes separately, because observed and desired behaviour are different evidence.
- **flagged-writes-intended-gwt** — When available evidence cannot exercise required behaviour, write the intended Given, When, and Then and state what evidence is missing, because an evidence gap must not erase the requirement or turn an expectation into an observed fact.
- **scenario-names-continuation** — Put the main flow first and make each continuing Then name the next Story on the map. Add a missing map node when a live path continues without one, because Scenarios are alternate flows within Stories rather than substitutes for Stories.
- **given-only-what-the-system-checks** — Describe the activity and state that the system actually uses for this behaviour, including state left by a prior Story. Omit off-system history, orphan data, screen names used as state, and fields the decision never reads, because irrelevant setup hides the real preconditions.
- **given-names-complex-state-root-first** — Begin complex Given state with the aggregate root, then describe its owned parts in their current state, because an owned entity does not have independent context outside its aggregate.
- **but-marks-missing-state** — Use But for a record that is absent or an action the actor did not take; use And for consequences of that absence and name gated operations as enabled or disabled, because But should identify the missing condition rather than its effects.
- **when-holds-the-operation** — Put the operation under test in When and, in Then, assert only results it has already produced. For downstream system Stories, describe the request arriving at that system instead of replaying the original user action. Specify enablement and activation as separate behaviours when both are observable, because triggers inside assertions and combined operations hide which action caused the result.
- **when-names-intent-not-interface-gesture** — Name the actor's domain intent and subject rather than the button or gesture used to express it. Keep click and tap details in UX artifacts unless the physical interaction is required behaviour, because controls can change while intent remains stable.
- **expressive-system-interactions** — Describe each system's When and Then in that system's vocabulary. A caller's Then names the result it receives; a translating intermediary names the incoming caller concept and the returned caller-facing result, because "calls the service" does not explain the work performed.
- **and-chaining** — Start each state, interaction, and result block with Given, When, and Then, then continue later steps of the same kind with And. Keep Given conditions in root-first order, start a new When for a new interaction, and keep one interaction's observable results in one Then/And block. Use Background only when more than one Scenario shares the state, because repeated keywords hide which conditions, actions, and results belong together.
- **outline-requires-many-permutations** — Use a Scenario Outline when many data combinations follow the same steps. Use separate steps or Scenarios for two alternatives or a changed flow, and keep only example fields that affect behaviour, because examples should show variation rather than conceal structure.
- **plain-english-gwt-steps** — Write each step as a readable sentence with a named actor and observable behaviour. Use the plain-English example name rather than a code identifier, because test reports must make sense without source code.
- **explain-deep-link-arrival** — When a Scenario starts at a parameterized route or equivalent application state, name the real arrival path: product navigation, an external deep link, or a preceding flow state. A route is not a user action.
- **seed-prior-story-as-given** — Seed a later Story from examples produced by prior Stories instead of replaying their When steps. Reuse fixtures from the owning domain concept and keep the boundary under test real, because each Story must run independently while proving its own behaviour.
