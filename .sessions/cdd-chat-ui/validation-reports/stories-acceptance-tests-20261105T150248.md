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


Judge only the checked format's files (python: C:/dev/abd-cdd-chat-ui/harness/chat-ui/{sub_epic_slug}.story.shared.py, C:/dev/abd-cdd-chat-ui/harness/chat-ui/{sub_epic_slug}.story.domain.spec.py, C:/dev/abd-cdd-chat-ui/harness/chat-ui/{sub_epic_slug}.story.server.spec.py). The other formats mirror them, so judging those too reports every finding twice.

# Graph rule validation

**Generated:** 2026-11-05 15:02:48 UTC
**Project:** chat-ui
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-context-driven-delivery\.sessions\cdd-chat-ui\edited-graph.json`

## Summary

**Total graph violations:** 28
**Rules with graph hits:** 1
**AI rules in scope:** 13

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

### `domain-fixture-example-files`

**Graph violations:** 28

- [X] **ERROR** **[graph rule]** - [pane/test/chat-bar-examples.ts](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\test\chat-bar-examples.ts#L29): Example `checkoutFlow`: Example file 'chat-bar-examples.ts' should end with .examples.ts under an examples/ folder.
- [X] **ERROR** **[graph rule]** - [pane/test/chat-bar-examples.ts](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\test\chat-bar-examples.ts#L29): Example `checkoutFlow`: Example file 'chat-bar-examples.ts' should end with .examples.ts under an examples/ folder.
- [X] **ERROR** **[graph rule]** - [pane/test/chat-bar-examples.ts](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\test\chat-bar-examples.ts#L65): Example `checkoutFlowWith`: Example file 'chat-bar-examples.ts' should end with .examples.ts under an examples/ folder.
- [X] **ERROR** **[graph rule]** - [pane/test/chat-bar-examples.ts](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\test\chat-bar-examples.ts#L65): Example `checkoutFlowWith`: Example file 'chat-bar-examples.ts' should end with .examples.ts under an examples/ folder.
- [X] **ERROR** **[graph rule]** - [pane/test/chat-bar-examples.ts](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\test\chat-bar-examples.ts#L65): Example `checkoutFlowWith`: Example file 'chat-bar-examples.ts' should end with .examples.ts under an examples/ folder.
- [X] **ERROR** **[graph rule]** - [pane/test/chat-bar-examples.ts](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\test\chat-bar-examples.ts#L65): Example `checkoutFlowWith`: Example file 'chat-bar-examples.ts' should end with .examples.ts under an examples/ folder.
- [X] **ERROR** **[graph rule]** - [pane/test/chat-bar-examples.ts](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\test\chat-bar-examples.ts#L65): Example `checkoutFlowWith`: Example file 'chat-bar-examples.ts' should end with .examples.ts under an examples/ folder.
- [X] **ERROR** **[graph rule]** - [pane/test/chat-bar-examples.ts](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\test\chat-bar-examples.ts#L65): Example `checkoutFlowWith`: Example file 'chat-bar-examples.ts' should end with .examples.ts under an examples/ folder.
- [X] **ERROR** **[graph rule]** - [pane/test/chat-bar-examples.ts](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\test\chat-bar-examples.ts#L77): Example `paymentRetry`: Example file 'chat-bar-examples.ts' should end with .examples.ts under an examples/ folder.
- [X] **ERROR** **[graph rule]** - [pane/test/chat-bar-examples.ts](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\test\chat-bar-examples.ts#L91): Example `boardOf`: Example file 'chat-bar-examples.ts' should end with .examples.ts under an examples/ folder.
- [X] **ERROR** **[graph rule]** - [pane/test/chat-bar-examples.ts](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\test\chat-bar-examples.ts#L91): Example `boardOf`: Example file 'chat-bar-examples.ts' should end with .examples.ts under an examples/ folder.
- [X] **ERROR** **[graph rule]** - [pane/test/chat-bar-examples.ts](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\test\chat-bar-examples.ts#L91): Example `boardOf`: Example file 'chat-bar-examples.ts' should end with .examples.ts under an examples/ folder.
- [X] **ERROR** **[graph rule]** - [pane/test/chat-bar-examples.ts](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\test\chat-bar-examples.ts#L91): Example `boardOf`: Example file 'chat-bar-examples.ts' should end with .examples.ts under an examples/ folder.
- [X] **ERROR** **[graph rule]** - [pane/test/chat-bar-examples.ts](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\test\chat-bar-examples.ts#L91): Example `boardOf`: Example file 'chat-bar-examples.ts' should end with .examples.ts under an examples/ folder.
- [X] **ERROR** **[graph rule]** - [pane/test/chat-bar-examples.ts](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\test\chat-bar-examples.ts#L91): Example `boardOf`: Example file 'chat-bar-examples.ts' should end with .examples.ts under an examples/ folder.
- [X] **ERROR** **[graph rule]** - [pane/test/chat-bar-examples.ts](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\test\chat-bar-examples.ts#L91): Example `boardOf`: Example file 'chat-bar-examples.ts' should end with .examples.ts under an examples/ folder.
- [X] **ERROR** **[graph rule]** - [pane/test/chat-bar-examples.ts](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\test\chat-bar-examples.ts#L91): Example `boardOf`: Example file 'chat-bar-examples.ts' should end with .examples.ts under an examples/ folder.
- [X] **ERROR** **[graph rule]** - [pane/test/move-work-forward-from-chat-bar/check-cdd-server-health/open-server-health-panel/open_server_health_panel_story.test.ts](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\test\move-work-forward-from-chat-bar\check-cdd-server-health\open-server-health-panel\open_server_health_panel_story.test.ts#L16): Example `HEALTHY`: Example file 'open_server_health_panel_story.test.ts' should end with .examples.ts under an examples/ folder.
- [X] **ERROR** **[graph rule]** - [pane/test/move-work-forward-from-chat-bar/guide-work-through-practices/display-stage-fidelities/display_stage_fidelities_story.test.ts](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\test\move-work-forward-from-chat-bar\guide-work-through-practices\display-stage-fidelities\display_stage_fidelities_story.test.ts#L15): Example `DONE`: Example file 'display_stage_fidelities_story.test.ts' should end with .examples.ts under an examples/ folder.
- [X] **ERROR** **[graph rule]** - [pane/test/move-work-forward-from-chat-bar/guide-work-through-practices/invoke-next-fidelity-action/invoke_next_fidelity_action_story.test.ts](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\test\move-work-forward-from-chat-bar\guide-work-through-practices\invoke-next-fidelity-action\invoke_next_fidelity_action_story.test.ts#L15): Example `GENERATED`: Example file 'invoke_next_fidelity_action_story.test.ts' should end with .examples.ts under an examples/ folder.
- [X] **ERROR** **[graph rule]** - [pane/test/move-work-forward-from-chat-bar/guide-work-through-practices/move-session-to-next-stage/move_session_to_next_stage_story.test.ts](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\test\move-work-forward-from-chat-bar\guide-work-through-practices\move-session-to-next-stage\move_session_to_next_stage_story.test.ts#L16): Example `DONE`: Example file 'move_session_to_next_stage_story.test.ts' should end with .examples.ts under an examples/ folder.
- [X] **ERROR** **[graph rule]** - [pane/test/move-work-forward-from-chat-bar/guide-work-through-practices/move-session-to-next-stage/move_session_to_next_stage_story.test.ts](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\test\move-work-forward-from-chat-bar\guide-work-through-practices\move-session-to-next-stage\move_session_to_next_stage_story.test.ts#L37): Example `GENERATED`: Example file 'move_session_to_next_stage_story.test.ts' should end with .examples.ts under an examples/ folder.
- [X] **ERROR** **[graph rule]** - [pane/test/move-work-forward-from-chat-bar/guide-work-through-practices/review-fidelity/review_fidelity_story.test.ts](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\test\move-work-forward-from-chat-bar\guide-work-through-practices\review-fidelity\review_fidelity_story.test.ts#L16): Example `VALIDATED`: Example file 'review_fidelity_story.test.ts' should end with .examples.ts under an examples/ folder.
- [X] **ERROR** **[graph rule]** - [pane/test/move-work-forward-from-chat-bar/see-work-in-chat-bar/display-fidelity-progress/display_fidelity_progress_story.test.ts](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\test\move-work-forward-from-chat-bar\see-work-in-chat-bar\display-fidelity-progress\display_fidelity_progress_story.test.ts#L15): Example `DONE`: Example file 'display_fidelity_progress_story.test.ts' should end with .examples.ts under an examples/ folder.
- [X] **ERROR** **[graph rule]** - [pane/test/move-work-forward-from-chat-bar/see-work-in-chat-bar/display-fidelity-progress/display_fidelity_progress_story.test.ts](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\test\move-work-forward-from-chat-bar\see-work-in-chat-bar\display-fidelity-progress\display_fidelity_progress_story.test.ts#L15): Example `GENERATED`: Example file 'display_fidelity_progress_story.test.ts' should end with .examples.ts under an examples/ folder.
- [X] **ERROR** **[graph rule]** - [pane/test/move-work-forward-from-chat-bar/see-work-in-chat-bar/display-fidelity-progress/display_fidelity_progress_story.test.ts](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\test\move-work-forward-from-chat-bar\see-work-in-chat-bar\display-fidelity-progress\display_fidelity_progress_story.test.ts#L28): Example `VALIDATED`: Example file 'display_fidelity_progress_story.test.ts' should end with .examples.ts under an examples/ folder.
- [X] **ERROR** **[graph rule]** - [pane/test/move-work-forward-from-chat-bar/see-work-in-chat-bar/display-session-card/display_session_card_story.test.ts](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\test\move-work-forward-from-chat-bar\see-work-in-chat-bar\display-session-card\display_session_card_story.test.ts#L15): Example `DONE`: Example file 'display_session_card_story.test.ts' should end with .examples.ts under an examples/ folder.
- [X] **ERROR** **[graph rule]** - [pane/test/move-work-forward-from-chat-bar/see-work-in-chat-bar/display-stage-strip/display_stage_strip_story.test.ts](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\test\move-work-forward-from-chat-bar\see-work-in-chat-bar\display-stage-strip\display_stage_strip_story.test.ts#L50): Example `SPECIFICATION`: Example file 'display_stage_strip_story.test.ts' should end with .examples.ts under an examples/ folder.

Evaluate the current context against this rule (domain-fixture-example-files):

## Judgment — `harness/chat-ui/pane/test/chat-bar-examples.ts`

### `domain-fixture-example-files` — Fail
- chat-bar-examples.ts:29 `checkoutFlow`: the shared examples sit in test/chat-bar-examples.ts; the rule wants them in an examples/ folder as chat-bar.examples.ts (graph, 28 hits from this one file name, counted again at each story test that imports DONE, GENERATED, VALIDATED, HEALTHY or SPECIFICATION).

### `shared-example-fixtures` — Fail
- chat-bar-examples.ts:96 `NEW_SESSION_NAME`: the Interaction example is declared but create_new_session_story.test.ts:22 still types the literal 'payment-retry', so the fixture and the Scenario can drift.

## Judgment — `harness/chat-ui/pane/test/move-work-forward-from-chat-bar/guide-work-through-practices/review-fidelity/review_fidelity_story.test.ts`

### `infrastructure-in-lifecycle-hooks` — Fail
- review_fidelity_story.test.ts:20 `checkout-flow's ux-mockup is the selected fidelity`: the Given still opens the pane itself (`await scene.open()`) before pressing the dot; story-test.ts now opens the pane before the first When or Then, but 18 story tests keep a `scene.open()` in a Given, most of them with nothing after it that needs the pane before the When.

## Judgment — `harness/chat-ui/pane/test/move-work-forward-from-chat-bar/check-cdd-server-health/reinstall-cdd-tools/reinstall_cdd_tools_story.test.ts`

### `assert-domain-behavior-not-seeded-state` — Fail
- reinstall_cdd_tools_story.test.ts:28 `the panel says installing while the installer runs`: still asserts the installer's argv, not the Installing. line; holding the installer in the stub timed the test out, because the test kit draws nothing while a press runs. Only a surface heavy spec can prove this Then.

Passes: vocabulary-traces-to-domain-source, read-all-source-context-in-full, do-not-invent-requirements, examples-declare-seed-vs-interaction (chat-bar-examples.ts labels each fixture Seed or Interaction), seed-state-at-its-real-owner (Givens set the board on the cdd stub), separate-test-controls-from-production-contracts, system-stubs-domain-real (cdd-stub.ts changes the board on ticket.move_next, finish_review, close, activate and create as the Python Ticket does; create opens the ticket in Discovery, as Ticket.create does), inline-simple-gwt-bodies, domain-operations-inline-in-steps, extract-assertion-helper (expectMarks, expectMarkLooks, expectMarkColours). The earlier fails on keep-classes-single-responsibility (chat-bar-world.ts split into cdd-stub.ts, chat-bar-examples.ts, chat-bar-screen.ts), provide-meaningful-context (ENGINE_SETTLE_MILLISECONDS) and use-intention-revealing-names (toolJson) are resolved, and the health panel's stacking on the card is now asserted (card-health). 52 of 52 engine tests pass.
