# Stories Guidance Assessment

## Purpose

Assess `context_tools/stories/stories.md` against the rules and concrete artifacts in `C:\dev\paradise-mobile\pml-domainmodel\stories`, without changing the guidance.

The assessment distinguishes:

- guidance that is already present but should be strengthened;
- missing rules that are safe to generalize;
- Paradise-specific conventions that should remain local;
- contradictions that must be resolved before changing the shared guidance; and
- structural and editorial weaknesses in the current shared guidance.

## Sources Reviewed

- `C:\dev\abd-context-driven-delivery\context_tools\stories\stories.md`
- `C:\dev\paradise-mobile\pml-domainmodel\stories\AGENTS.md`
- Paradise Mobile `story-map.md`, `story-scenarios.md`, `thin-slice.md`, and `system-terms.md`
- Story scenario Markdown under the Paradise Mobile epic and sub-epic folders
- Paradise Mobile `*_story.spec.ts`, `examples/*.ts`, `story-test.ts`, and test setup
- `context_tools/stories/examples/telco-website/examples.md`

## Executive Assessment

The shared guidance has a sound high-level model: hierarchical story maps, action-oriented names, mechanic-based decomposition, concrete GWT scenarios, domain vocabulary, and observable outcomes. However, the Paradise work exposed four major weaknesses.

1. The shared rules are not precise enough at system boundaries. They do not consistently explain how caller, middleware, and callee stories divide an interaction or how each system should describe its own work.
2. Scenario guidance lacks important semantics for observable outcomes, continuation between map nodes, complex Given state, `But`, and evidence integrity.
3. Example and acceptance-test guidance does not adequately distinguish domain fixtures, external-system seed fixtures, and user-interaction fixtures.
4. Artifact layout, language defaults, and brownfield versus greenfield behavior are contradictory or under-specified.

The Paradise rules should not be copied wholesale. Many encode PML topology, tools, and file layout. Some also disagree with the Paradise artifacts themselves. The right approach is to extract portable principles, resolve shared-guidance contradictions first, and leave concrete topology and naming conventions in project-level guidance.

## Existing Rules To Strengthen

### `read-all-source-context-in-full`

**Current shared guidance:** `stories.md:18`

**Paradise addition:** `AGENTS.md:11` requires concrete evidence from code, recorded walkthroughs, and execution logs, including precise locations.

**Assessment:** The shared rule correctly requires full reads, but it focuses on reading discipline rather than the evidence that must support a hierarchy or system seam.

**Recommended improvement:** Require the author to identify the evidence class and location supporting each important hop or seam. Generalize this as code references, recorded observations, and run logs with relevant ranges. Do not copy PML repository names, Granola, or sandbox terminology into shared guidance.

### `do-not-invent-requirements`

**Current shared guidance:** `stories.md:19`

**Paradise addition:** `AGENTS.md:12` says a system hop exists only when a named application actually calls it.

**Assessment:** The shared rule prevents invented product behavior but does not provide a strong test for invented system topology.

**Recommended improvement:** Add: a system-to-system hop exists only when a named caller invokes it or a source explicitly requires it. This prevents architecture assumptions from becoming stories.

### `verb-noun-format`

**Current shared guidance:** `stories.md:52`

**Paradise addition:** `AGENTS.md:16` says epics and sub-epics name the goal, not the actor's activity or a supporting system hop. A sub-epic is one outcome plus the hops that achieve it.

**Assessment:** The shared rule enforces grammar but not abstraction level. A grammatically correct verb-noun name can still describe the wrong horizon.

**Recommended improvement:** Add the goal-versus-hop distinction and define a sub-epic as one outcome with its supporting interactions. This is portable and should be adopted nearly verbatim.

### `right-size-story-nodes`

**Current shared guidance:** `stories.md:55`

**Paradise addition:** `AGENTS.md:20` separates caller round trips from callee behavior and keeps display-only or forwarding-only work as outcomes rather than new hops.

**Assessment:** This is the most materially under-specified shared rule. "Bigger needs several Whens; smaller is a step" does not tell an author where a system boundary becomes a story.

**Recommended improvement:** Define one story as one observable request/response interaction at one system boundary. Keep internal fan-out within that boundary story unless it creates another independently observable boundary. Give a validating or deciding intermediary its own hop; leave a merely forwarding or displaying intermediary as an outcome on the caller story.

This wording must replace, not merely append, "one story per distinct system hop." Paradise's applied-voucher scenario treats one boundary request with internal fan-out as an intentional compound story, showing that "hop" is otherwise ambiguous.

### `explore-full-interaction-surface`

**Current shared guidance:** `stories.md:76,86`

**Paradise addition:** `AGENTS.md:33,41` requires walking the real UI and reconciling observations immediately.

**Assessment:** The shared guidance already contains the richer inventory of validation and UI behaviors. It lacks the evidence priority rule.

**Recommended improvement:** Add a conditional brownfield clause: when a running system exists, inspect it before locking scenarios, and observed behavior outranks an earlier sketch. Do not make this unconditional because greenfield specifications have no running behavior to inspect.

### `given-only-what-the-system-checks`

**Current shared guidance:** `stories.md:87`

**Paradise addition:** `AGENTS.md:43` says Given names the activity, not the screen; contains state already present in the system; avoids orphan data; uses Background only when more than one scenario shares the state; and excludes fields not read for the decision under test.

**Assessment:** The shared rule only rejects off-system backstory. It does not govern irrelevant in-system state or the level at which state is described.

**Recommended improvement:** Add all portable clauses above. Replace PML field examples with a neutral example showing that a field not read by the decision must not appear as a precondition.

### `when-holds-the-operation`

**Current shared guidance:** `stories.md:88`

**Paradise addition:** `AGENTS.md:46` explains how a caller's result becomes a downstream system's trigger, forbids replaying the original user action in every system story, and distinguishes enabling from activating an operation.

**Assessment:** The shared rule correctly separates trigger from assertion but does not explain continuation across story-map hops.

**Recommended improvement:** State that each downstream system's When describes the request arriving at that system, while the caller's Then describes the result received. Do not repeat the original user's action in every downstream story. Keep enablement and activation as separate behaviors when both are observable.

### `and-chaining`

**Current shared guidance:** `stories.md:90`

**Paradise addition:** `AGENTS.md:48-49` separates Given chaining from Then chaining and requires Given chains to preserve root-first state structure.

**Assessment:** The combined shared rule obscures two different semantics. It also conflicts with `stories.md:74`, which permits a new When when the actor or trigger changes, without defining when a block has ended.

**Recommended improvement:** Split this into `given-and-chaining` and `then-and-chaining`. Define a new When as the start of a new interaction, not merely another assertion. Require Given chaining to reflect aggregate-root-first state.

### `typescript-step-labels-are-plain-english`

**Current shared guidance:** `stories.md:91`

**Paradise addition:** `AGENTS.md:51` requires actor and observable behavior in every step, English example labels instead of camelCase export identifiers, and consistent outline placeholder substitution.

**Assessment:** The current rule only removes Markdown markers from generated TypeScript. It does not ensure that the resulting sentence is readable.

**Recommended improvement:** Rename this to the language-neutral `plain-english-gwt-steps`. Require named actors, observable behavior, plain-English example labels, and no source-code identifiers in rendered step text. Keep language-specific rendering details in language guidance.

### Scenario Outline guidance

**Current shared guidance:** `stories.md:78`

**Paradise addition:** `AGENTS.md:50` says an outline is for many permutations, not two alternations, and every table column must affect behavior.

**Assessment:** The principle exists only as prose and gives no threshold or column-quality test.

**Recommended improvement:** Promote `outline-requires-many-permutations` to a named rule. Use separate scenarios or steps for two meaningful alternatives. Require every example column to change an input, rule, or expected result.

### `seed-prior-story-as-given`

**Current shared guidance:** `stories.md:92`

**Paradise addition:** `AGENTS.md:62` says to reuse the owning aggregate's fixture or stub and never stub the seam being proved.

**Assessment:** The shared rule prevents replay but still permits a test-local fake that bypasses the subject of the story.

**Recommended improvement:** Add: reuse fixtures from the owning concept and do not stub the seam under test.

### `infrastructure-in-lifecycle-hooks`

**Current shared guidance:** `stories.md:115`

**Paradise addition:** `AGENTS.md:60` loads an aggregate once at the highest Given that needs it and reaches owned entities through their aggregate root.

**Assessment:** The shared rule separates infrastructure from domain state but does not protect domain ownership in test setup.

**Recommended improvement:** Add the aggregate ownership principle in neutral terms: resolve entities through their owner when identity is scoped to that owner, and avoid convenience lookups that invent independent identity.

## Missing Rules To Add

### Highest Priority

#### `story-name-captures-system-mechanic`

Source: `AGENTS.md:17,25`

Require a story name's verb to identify the operation and its noun to identify the record or concept acted on. Reject vague verbs such as `Handle`, `Process`, and `Manage` at story level when they hide the mechanic. Keep project-approved verb lists in project vocabulary guidance rather than the shared rule.

#### `behavioral-and-system-observable-outcomes`

Source: `AGENTS.md:31,70`

Require every Then to be observable by a person or another system. Internal flags and function-local state are not scenario outcomes. Give distinct observable results distinct Then statements, but keep results produced by one call together when they form one outcome.

#### `scenario-names-continuation`

Source: `AGENTS.md:35,75`

Require main flow first and prevent dead ends. A scenario's outcome should identify the next map node when the flow continues. A live continuation with no map hop is a map defect. Clarify that scenarios are alternate flows within a story, not substitutes for missing stories.

#### `expressive-system-interactions`

Source: `AGENTS.md:39,68`

Require each system's When and Then to use that system's vocabulary. A caller's Then names the returned result, not the act of making a call. A translating middle layer receives the caller's concept, performs its translation, and returns a result in the caller-facing concept.

#### `given-names-complex-state-root-first`

Source: `AGENTS.md:44,73`

Require complex Given state to begin with the aggregate root and then describe owned parts in their current state. Do not describe an owned part as free-standing state.

#### `but-marks-missing-state`

Source: `AGENTS.md:45,74`

Define `But` as absence: a missing record or an action not taken. Describe consequences with `And`, not another `But`. Describe gated operations explicitly as enabled or disabled.

### Example And Fixture Integrity

#### `notation-in-example-tables`

Source: `AGENTS.md:52`

Require plain-English domain-term and example columns. Keep formatting markers out of cells and code identifiers out of Markdown labels.

#### `examples-trace-domain-model`

Source: `AGENTS.md:53,77`

Require fixture shapes to trace to the domain model and the owning system. External-system records use the external boundary shape; domain aggregates use domain properties. Relate fixtures by shared keys rather than embedding one conceptual model inside another merely for test convenience.

#### `examples-declare-seed-vs-interaction`

Source: `AGENTS.md:54,78`

Classify fixture use before writing it:

- **Seed:** state persisted by an owning system and read through a boundary.
- **Interaction:** values entered, displayed, validated, or otherwise observed through the application.

A story may require both shapes for the same conceptual entity. They should not be treated as interchangeable.

#### `seed-the-owning-system-not-the-domain-repository`

Source: generalized from `AGENTS.md:55`

Seed external state through the concrete acceptance stub for the owning external system. Do not add test-only seed, reset, or inspection operations to production domain repository interfaces.

#### `system-stubs-domain-real`

Source: `AGENTS.md:56`

Permit deterministic fixtures at external-system boundaries. Require domain aggregates, repositories, validations, mappings, and transitions to execute real behavior. Forbid silent no-ops and test-only domain seams.

#### `assert-domain-behavior-not-seeded-state`

Source: generalized from `AGENTS.md:57`

After seeding an external boundary, exercise the domain entry point and assert the resulting domain behavior. Reading back the fixture inserted in Given does not prove the application behavior. Inspect the external stub only for an outbound side effect initiated through the domain.

#### `inline-simple-gwt-bodies`

Source: `AGENTS.md:61,79`

Keep simple GWT bodies inline and use example exports directly. Do not introduce one-line pass-through helpers. Extract helpers only for non-trivial setup or assertions reused enough to justify a name.

### Conditional Brownfield Rules

#### `reconcile-live-immediately`

Source: `AGENTS.md:41`

When capturing an existing system, observed behavior outranks a sketch. Reconcile the sketch and map in the same increment before locking scenarios. Scope this rule explicitly to brownfield capture so it does not conflict with specification-first greenfield work.

#### `explain-deep-link-arrival`

Source: `AGENTS.md:42`

When a scenario starts at a parameterized route or equivalent application state, identify the real arrival mechanism: in-product navigation, external deep link, or a preceding flow state. Do not describe a route as though it were a user control.

#### `flagged-writes-intended-gwt`

Source: `AGENTS.md:58` and repeated `Flagged`/`Intended` sections in the Paradise scenario artifacts

When available evidence cannot exercise a required path, still record the intended GWT and explicitly label the evidence limitation. Do not silently convert an unobserved intended behavior into an observed fact.

#### Story evidence traceability

Source: repeated story type, Source, and Evidence sections in Paradise scenario artifacts

Require system stories to name their source evidence, such as code, recorded observation, or an execution trace. This is not currently a named Paradise rule, but the artifacts show it is essential to distinguishing observed, inferred, and intended behavior.

## Rules And Conventions To Keep Project-Local

The following should not be copied into shared guidance as written:

- Approved Midtier and callee verb lists.
- My Paradise, Midtier, Amplify, Cognito, Mavenir, and other PML topology names.
- `pml-my`, `pml-midtier`, and `pml-website` source locations.
- Granola and sandbox-specific evidence instructions.
- Exact local file names such as `stories/story-test.ts` and `stories/system-terms.md`.
- The session-worktree instruction in `AGENTS.md:5`.
- PML-specific fidelity front matter and artifact names until the shared artifact contract is defined.

The portable principles behind these conventions should be generalized, but their concrete instances belong in project guidance.

## Contradictions To Resolve First

### Artifact Layout

There are three incompatible layouts:

- `stories.md:68,107` prescribes `tests/{epic}/{sub-epic}/{story}.py`, one file per story.
- Paradise `AGENTS.md:10` prescribes one `*_story.ts` per lowest sub-epic, containing every story, with no per-story folders.
- The Paradise artifacts and the shared telco example use per-story folders and `*_story.spec.ts` files.

The Paradise rule also says shared examples live at a parent level, while some artifacts duplicate examples under story folders.

**Required decision:** Define one language-neutral artifact invariant before changing the shared rule. A reasonable invariant is: folders mirror the story hierarchy, runnable specifications map unambiguously to stories, and examples live at the highest scope where they are shared. Language adapters may then choose file extensions and runner-specific naming.

### Language Defaults

`stories.md:64,97` hard-codes Python and `.py` paths, while the Paradise workflow is Markdown scenarios followed by TypeScript acceptance tests.

**Required decision:** Separate artifact fidelity from implementation language. Scenario guidance should be language-neutral; Python and TypeScript rendering conventions should live in language-specific guidance.

### Boundary Meaning Of `right-size-story-nodes`

Paradise says one story per distinct system hop, but an applied-voucher scenario intentionally keeps multiple internal calls in one Midtier story because they belong to one inbound boundary interaction.

**Required decision:** Define hop as an observable request/response across a named system boundary, not every internal call.

### Brownfield Observation Versus Greenfield TDD

Paradise's running-app rule says observed behavior wins. `stories.md:66,101` says scenarios precede code and acceptance tests begin RED against code that may not exist.

**Required decision:** Declare two evidence modes:

- **Brownfield capture:** observed behavior outranks sketches; intended deviations are explicitly flagged.
- **Greenfield specification:** agreed scenarios define intended behavior and tests begin RED.

### Child Count Guidance

`stories.md:11` says no more than 7-9 children. `stories.md:53` says 4-9, warns at 3/10, and errors at 2 or fewer and 11 or more.

**Required decision:** Keep one calibrated rule. The explicit 4-9 thresholds are clearer and match Paradise guidance.

## Structural And Editorial Improvements

1. Change the document H1 from `# Contexts` to `# Stories` when edits are authorized.
2. Resolve the child-count contradiction between `stories.md:11` and `stories.md:53`.
3. Define where story maps, scenario Markdown, indexes, example tables, and runnable acceptance tests live.
4. Separate language-neutral scenario guidance from Python- and TypeScript-specific rendering.
5. Define `But`; it is absent even though the Paradise artifacts use it extensively.
6. Clarify when a new When starts a new interaction and when `.and()` continues the current block.
7. Clarify the relationship between Markdown Examples tables and code fixture folders.
8. Either repeat every shared rule in fidelity sections or repeat none; currently only `do-not-invent-requirements` is repeated as "same rule as Shared."
9. Add a scenario scaffold boundary comparable to the story-map scaffold section, or explain why scenario rules always apply.
10. Consider a recurring-risk and first-time-risk watch list. The Paradise split makes enforcement priorities visible without weakening the canonical rules.
11. Fix the root-relative `context_tools/language-tools.md` link so it works outside a repository-root renderer.
12. Correct grammar and spelling, including `hiererachy`, `dstinct`, `spliting`, `sucessful`, `outomes`, `apporach`, `realcode`, and `does't`.

## Paradise Artifact Drift To Address Separately

These findings affect the reliability of Paradise as a source but are not reasons to reject its portable rules.

- `stories/system-story-strategy.md` is cited by `AGENTS.md` and many scenario files but was not found.
- `stories/.context/create-customer-chat-notes.md` is cited but was not found.
- `AGENTS.md:10` forbids per-story folders, while the artifacts use them.
- The scenario index names a `*_story.ts` file while the artifact is `*_story.spec.ts`.
- Some fixtures are duplicated at story scope despite guidance to place shared examples at parent scope.
- The acceptance harness implements Background scoping and Then/And behavior that neither guidance set fully documents.

These should be treated as project cleanup and convention-reconciliation work, not directly generalized into the shared story guidance.

## Recommended Improvement Order

1. Resolve artifact layout, language-neutrality, boundary-hop meaning, evidence mode, and child-count contradictions.
2. Add the four core semantic rules: `story-name-captures-system-mechanic`, `behavioral-and-system-observable-outcomes`, `scenario-names-continuation`, and `expressive-system-interactions`.
3. Strengthen `right-size-story-nodes`, `given-only-what-the-system-checks`, and `when-holds-the-operation` around system boundaries and flow continuation.
4. Add root-first Given semantics, `But` semantics, and separate Given/Then chaining rules.
5. Add the fixture integrity group: domain-model traceability, seed-versus-interaction shapes, owning-system seeding, real domain behavior, and assertions through the domain seam.
6. Add conditional brownfield evidence rules and an explicit observed/inferred/intended distinction.
7. Define the artifact-placement contract and then align examples and language adapters to it.
8. Finish with editorial cleanup and a focused watch list for recurring failures.

## Bottom Line

The Paradise rules contain substantial improvements to the shared Stories guidance, particularly around system mechanics, boundary-sized stories, observable outcomes, scenario continuation, complex state, and fixture integrity. Their strongest ideas are portable, but their concrete file layout, system names, evidence tools, and some test conventions are not.

The shared guidance should first become internally consistent and language-neutral. After that, the missing semantic and evidence rules can be added without importing PML-specific architecture or preserving conventions that the Paradise artifacts no longer follow.
