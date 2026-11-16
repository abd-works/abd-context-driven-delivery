# Validate

Take the persona of a **critical judge** — do not edit the artifact.

1. Read the appropriate practice and fidelity level guidlines and rules. Scope judgment to artifacts passed into context.
1b. **Stories in the session's scope.** A session's ticket names its stories (its `Story:` headings); they are the increment. Every one of them is generated and validated with the patterns its content is generated with: generate uses the session's overlays and records them in `.context/patterns.md` at the root of each folder it writes, with the roles the folder holds of a pattern whose layers sit in several folders; validate reads that file. Stories the ticket does not name belong to other increments: leave them alone, and do not judge or report them. **Measure the scope, not the repository:** the graph report keeps only the findings inside the work's scope, on those stories and everything under them (their scenarios, steps, and examples) and in the files the call names; name, as paths, exactly the modules and tests the work changed. Judge only those too.
1c. **Patterns used in part.** The graph checks content against every applied pattern's schema and rules mechanically (`conforms-to-schema` and each pattern's rules), so a pattern used only in part reports members its content never meant to have. Judge each such finding against the patterns' own instructions and the patterns the content was generated with (`.context/patterns.md`, with the roles a folder holds): when another applied pattern supplies that member in its own way, the finding is noise; say so in the judgment and name the pattern that covers it (LERN overlaid with cdd_web_domain_access has its domain in Python behind MCP, so LERN's TypeScript domain, node tier, routes and lowdb store are not expected). Every other finding stands.
2. Use each **practice** as the rubric — report Pass or Fail per named practice fidelity and named rule with brief evidence. There is no third verdict: a rule that is only partly met is a Fail, because a softer verdict lets a broken rule through review.
3. When **paths** names the files being edited, the graph is built from just those files as they are now, and its rules run on them. Pass the files you wrote, not the whole tree. Without **paths**, when **graph** is `true`, read the session's graph (`graph.json` in the session's own folder, created for the session); when it is a path (or list of paths), read that `graph_return_nodes` JSON or saved graph. Append a **Graph rule validation** report for each guidance's practice. Each rule is one section: heading, rule text, any graph hits (**[graph rule]**), then the AI judgment prompt for that rule.
4. Collection validate on graph-backed practices reads the working copy and reports each rule hit. A single base Rule is instruction text only.
5. Do not fix. Report failures for fixing, then add your judgment for each rule to the report this action saved, so the board links to the whole result. It names the report's path at the end of its reply.
6. Append the judgment to the end of the saved report in exactly this shape. The session board parses it, lists each finding beside the graph's hits, opens the finding's file at its line, and sends a Fix back, so a finding in any other shape is lost:

   ```markdown
   ## Judgment — `.context/story-map.md`

   ### `rule-slug` — Fail
   - story-map.md:86 `Archive Ticket`: what breaks the rule, and why.

   ### `other-rule-slug` — Fail
   - story-map.md:148 `Send Sketch Iterate Or Document`: what breaks the rule, and why.
   ```

   - **One `## Judgment — ` section per judged file,** with an em dash, and the file in backticks as a path from the project's root, the way the session names paths. Never an absolute path or another checkout's path, because the board opens the file in this project and cannot open one anywhere else.
   - **One `### ` heading per rule that fails:** the rule slug in backticks, an em dash, then `Fail`. Leave passing rules out of these headings; a table or a Passes paragraph after the judgment may list them.
   - **One bullet per finding,** opening with the judged file's name, a colon, and one line number (`story-map.md:86`), then a space and what breaks the rule. A finding that spans lines takes its first line, and a finding at two places is two bullets, because the board opens each finding at one line.


Judge only the checked format's files (python: ../story_tests/review-generated-work-in-file-viewer/switch-files-app-between-files-and-graph/switch-files-app-between-files-and-graph.story.shared.py, ../story_tests/review-generated-work-in-file-viewer/switch-files-app-between-files-and-graph/switch-files-app-between-files-and-graph.story.domain.spec.py, ../story_tests/review-generated-work-in-file-viewer/switch-files-app-between-files-and-graph/switch-files-app-between-files-and-graph.story.server.spec.py, ../story_tests/review-generated-work-in-file-viewer/switch-files-app-between-files-and-graph/switch_files_app_between_files_and_graph_story.test.md). The other formats mirror them, so judging those too reports every finding twice.

# Graph rule validation

**Generated:** 2026-11-16 06:00:56 UTC
**Project:** harness
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-context-driven-delivery\.sessions\file-manager\validation-reports\stories-acceptance-tests-20261116T060056.json`

**The session's graph also held, and practice-wide rules compared against:**
- `.`
- `../story_tests`

## Summary

**Total graph violations:** 14
**Rules with graph hits:** 3
**AI rules in scope:** 32

## Rules

Each rule shows its guidance text, any graph scanner hits (`**[graph rule]**`), then the AI judgment prompt.

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

### `but-marks-missing-state`

Use But for a record that is absent or an action the actor did not take; use And for consequences of that absence and name gated operations as enabled or disabled, because But should identify the missing condition rather than its effects.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [switch_files_app_between_files_and_graph_story.test.md](C:\dev\abd-cdd-file-manager\story_tests\review-generated-work-in-file-viewer\switch-files-app-between-files-and-graph\switch_files_app_between_files_and_graph_story.test.md#L72): Then `but none of the old story map's epics`: But step should mark missing or absent state, not a consequence: "none of the old story map's epics".

Evaluate the current context against this rule (but-marks-missing-state):

### `conforms-to-schema`

Content conforms to its schema: every node has each relationship its schema type requires, up to the fidelity being worked. It checks only what the schema requires (a field written `name?:` is optional) and only for the fidelities worked so far: a relationship whose target a later fidelity creates is not required yet. Validate keeps only the findings inside the work's scope: the session's stories and everything under them, and the files the call names. It runs only on a graph that holds the session's whole working copy across its practices, so links across practices are judged; on a load of named files alone the AI judge weighs them.

**Graph violations:** 12

- [X] **ERROR** **[graph rule]** - [switch_files_app_between_files_and_graph_story.test.md](C:\dev\abd-cdd-file-manager\story_tests\review-generated-work-in-file-viewer\switch-files-app-between-files-and-graph\switch_files_app_between_files_and_graph_story.test.md#L56): When `when the Person switches the file bar to the graph view`: When 'when the Person switches the file bar to the graph view' has no invokes relationship to Operation | Property, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [switch_files_app_between_files_and_graph_story.test.md](C:\dev\abd-cdd-file-manager\story_tests\review-generated-work-in-file-viewer\switch-files-app-between-files-and-graph\switch_files_app_between_files_and_graph_story.test.md#L63): When `when the Person switches the file bar back to the files`: When 'when the Person switches the file bar back to the files' has no invokes relationship to Operation | Property, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [switch_files_app_between_files_and_graph_story.test.md](C:\dev\abd-cdd-file-manager\story_tests\review-generated-work-in-file-viewer\switch-files-app-between-files-and-graph\switch_files_app_between_files_and_graph_story.test.md#L70): When `when the Person switches the file bar to the graph view`: When 'when the Person switches the file bar to the graph view' has no invokes relationship to Operation | Property, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [switch_files_app_between_files_and_graph_story.test.md](C:\dev\abd-cdd-file-manager\story_tests\review-generated-work-in-file-viewer\switch-files-app-between-files-and-graph\switch_files_app_between_files_and_graph_story.test.md#L86): When `when the Person turns Clean Engineering off`: When 'when the Person turns Clean Engineering off' has no invokes relationship to Operation | Property, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [switch_files_app_between_files_and_graph_story.test.md](C:\dev\abd-cdd-file-manager\story_tests\review-generated-work-in-file-viewer\switch-files-app-between-files-and-graph\switch_files_app_between_files_and_graph_story.test.md#L93): When `when the Person turns the Changed button on`: When 'when the Person turns the Changed button on' has no invokes relationship to Operation | Property, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [switch_files_app_between_files_and_graph_story.test.md](C:\dev\abd-cdd-file-manager\story_tests\review-generated-work-in-file-viewer\switch-files-app-between-files-and-graph\switch_files_app_between_files_and_graph_story.test.md#L100): When `when the Person selects only the Stories dot on the chat bar`: When 'when the Person selects only the Stories dot on the chat bar' has no invokes relationship to Operation | Property, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [switch_files_app_between_files_and_graph_story.test.md](C:\dev\abd-cdd-file-manager\story_tests\review-generated-work-in-file-viewer\switch-files-app-between-files-and-graph\switch_files_app_between_files_and_graph_story.test.md#L115): When `when the Person selects Ticket.activate`: When 'when the Person selects Ticket.activate' has no invokes relationship to Operation | Property, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [switch_files_app_between_files_and_graph_story.test.md](C:\dev\abd-cdd-file-manager\story_tests\review-generated-work-in-file-viewer\switch-files-app-between-files-and-graph\switch_files_app_between_files_and_graph_story.test.md#L121): When `when the Person also selects Board.reread`: When 'when the Person also selects Board.reread' has no invokes relationship to Operation | Property, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [switch_files_app_between_files_and_graph_story.test.md](C:\dev\abd-cdd-file-manager\story_tests\review-generated-work-in-file-viewer\switch-files-app-between-files-and-graph\switch_files_app_between_files_and_graph_story.test.md#L127): When `when the Person selects the Clean Engineering root, which no file's lines hold`: When 'when the Person selects the Clean Engineering root, which no file's lines hold' has no invokes relationship to Operation | Property, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [switch_files_app_between_files_and_graph_story.test.md](C:\dev\abd-cdd-file-manager\story_tests\review-generated-work-in-file-viewer\switch-files-app-between-files-and-graph\switch_files_app_between_files_and_graph_story.test.md#L143): When `when the Files app shows ticket.py`: When 'when the Files app shows ticket.py' has no invokes relationship to Operation | Property, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [switch_files_app_between_files_and_graph_story.test.md](C:\dev\abd-cdd-file-manager\story_tests\review-generated-work-in-file-viewer\switch-files-app-between-files-and-graph\switch_files_app_between_files_and_graph_story.test.md#L150): When `when the Person also selects Ticket.close`: When 'when the Person also selects Ticket.close' has no invokes relationship to Operation | Property, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [switch_files_app_between_files_and_graph_story.test.md](C:\dev\abd-cdd-file-manager\story_tests\review-generated-work-in-file-viewer\switch-files-app-between-files-and-graph\switch_files_app_between_files_and_graph_story.test.md#L157): When `when the Person selects Ticket.close, at line 538`: When 'when the Person selects Ticket.close, at line 538' has no invokes relationship to Operation | Property, which the stories practice schema requires.

Evaluate the current context against this rule (conforms-to-schema):

### `when-names-intent-not-interface-gesture`

Name the actor's domain intent and subject rather than the button or gesture used to express it. Keep click and tap details in UX artifacts unless the physical interaction is required behaviour, because controls can change while intent remains stable.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [switch_files_app_between_files_and_graph_story.test.md](C:\dev\abd-cdd-file-manager\story_tests\review-generated-work-in-file-viewer\switch-files-app-between-files-and-graph\switch_files_app_between_files_and_graph_story.test.md#L93): When `when the Person turns the Changed button on`: When step 'the Person turns the Changed button on' names a UI gesture; state the domain intent instead.

Evaluate the current context against this rule (when-names-intent-not-interface-gesture):

## Judgment — `story_tests/review-generated-work-in-file-viewer/switch-files-app-between-files-and-graph/switch_files_app_between_files_and_graph_story.test.md`

### `conforms-to-schema` — Fail
- switch_files_app_between_files_and_graph_story.test.md:56 `when the Person switches the file bar to the graph view`: this When, and the eleven others the graph names (lines 63, 70, 86, 93, 100, 115, 121, 127, 143, 150, 157), records no invokes link to the operation it runs. The Python story test calls each one (session.graph_trees, graph_branch, graph_node_ranges), but nothing ties the markdown step to it; the page's own steps (the file bar's toggle, the Changed filter, the chat bar's dots) run in the Files app's TypeScript, which the graph does not link either.

Graph findings judged as noise: `but-marks-missing-state` (line 72) and `when-names-intent-not-interface-gesture` (line 93) were read from the graph before the scenario file was read again (a listed scenarios markdown file did not bring in its map, so a refresh kept the old nodes; fixed on file-manager in Stories.read_files). The file now reads `*And* holds none of the old story map's epics` and `*When* the Person narrows the files to those the branch changed`.

## Judgment — `story_tests/review-generated-work-in-file-viewer/switch-files-app-between-files-and-graph/switch-files-app-between-files-and-graph.story.shared.py`

### `domain-operations-inline-in-steps` — Fail
- switch-files-app-between-files-and-graph.story.shared.py:34 `names_in`: steps reach session.graph_trees and session.graph_branch through this story-file helper (and `opened_names`, `lines_of`, and `node_id_of` in space/session/graph_view_examples.py) instead of calling them in the When; only the newest scenario, Selecting a step opens its scenarios file, calls session.graph_node_ranges inline.

### `unit-example-within-100-ms` — Fail
- switch-files-app-between-files-and-graph.story.shared.py:174 `Selecting a folder's node opens every listed file below it`: replayed at the cdd tools tier it runs about 1 s, starting a cdd server on a throwaway project in its Given; the server tier's examples share that cost across this repository's story tests.

Passes: `examples-declare-seed-vs-interaction` (every fixture in graph_view_examples.py is marked Seed), `shared-example-fixtures` (one examples module for both graph sub-epics), `seed-state-at-its-real-owner` (files and the session seeded through the throwaway project, the session read through its own operations), `no-skipped-or-empty-test`, `suffix-names-the-tier`, `unit-file-within-2-seconds` (domain 1.1 s, server 1.1 s), `assert-domain-behavior-not-seeded-state` (each Then asserts what graph_trees or graph_node_ranges answers, not the seeded files).
