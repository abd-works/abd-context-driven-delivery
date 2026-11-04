# Validate

Take the persona of a **critical judge** — do not edit the artifact.

1. Read the appropriate practice and fidelity level guidlines and rules. Scope judgment to artifacts passed into context.
2. Use each **practice** as the rubric — report Pass or Fail per named practice fidelity and named rule with brief evidence. There is no third verdict: a rule that is only partly met is a Fail, because a softer verdict lets a broken rule through review.
3. When **paths** names the files being edited, the graph is built from just those files as they are now, and its rules run on them. Pass the files you wrote, not the whole tree. Without **paths**, when **graph** is `true`, read the workspace's saved graph (`.context/graph.json`, written by `graph_load_working_copy`); when it is a path (or list of paths), read that `graph_return_nodes` JSON or saved graph. Append a **Graph rule validation** report for each guidance's practice. Each rule is one section: heading, rule text, any graph hits (**[graph rule]**), then the AI judgment prompt for that rule.
4. Collection validate on graph-backed practices reads the working copy and reports each rule hit. A single base Rule is instruction text only.
5. Do not fix. Report failures for fixing, then add your judgment for each rule to the report this action saved, so the board links to the whole result. It names the report's path at the end of its reply.
6. Write the judgment in this shape, because the session board reads it and lists each finding beside the graph's hits, with a Fix that sends it back:

   ```markdown
   ## Judgment — `path/of/the/judged/file.md`

   ### `rule-slug` — Fail
   - story-map.md:86 `Archive Ticket`: what breaks the rule, and why.

   ### `other-rule-slug` — Fail
   - story-map.md:148 `Send Sketch Iterate Or Document`: what breaks the rule, and why.
   ```

   One `###` heading per rule that fails, with Fail after the dash. One bullet per finding, opening with the judged file's name and the line, so a person can open the finding at that line. Leave passing rules out of these headings; a table or a Passes paragraph may list them.


# Graph rule validation

**Generated:** 2026-11-04 18:38:48 UTC
**Project:** kanban
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-cdd-session-board\.sessions\session-board\edited-graph.json`

## Summary

**No graph rule violations.** All scanned graph rules passed.
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

## Judgment — `harness/kanban/generate-fidelity-outputs.story.ui.spec.ts`

### `extract-assertion-helper` — Fail
- generate-fidelity-outputs.story.ui.spec.ts:51 waitForNoChat asserts the "No chat connected" text in the same shape as steer-ticket-sessions.story.ui.spec.ts:34 and guide-work-through-practices.story.ui.spec.ts:242, a third copy rather than one helper in app/tests/story-ui.ts.
- generate-fidelity-outputs.story.ui.spec.ts:33 received is the fourth copy of the same reading of what the chat received, also at guide:31, steer:42, and validate:27.

### `shared-example-fixtures` — Fail
- generate-fidelity-outputs.story.ui.spec.ts:35 activate, the seed of the open session, is copied in guide:33, validate:29, and review:24 rather than being one Seed fixture.

### `do-not-invent-requirements` — Fail
- generate-fidelity-outputs.story.ui.spec.ts:115 "Keep Run off with no chat" turns Active session only off, which its Given does not name; Run stays off with no chat either way.
- generate-fidelity-outputs.story.ui.spec.ts:146 "Keep Run off with no format picked" makes billing-report the active ticket, which its Given does not name.
- generate-fidelity-outputs.story.ui.spec.ts:159 "Keep Run off on a render with nothing to render" makes billing-report the active ticket, which its Given does not name; only choosing render needs the ticket unlocked.
- generate-fidelity-outputs.story.ui.spec.ts:239 "Keep render off with nothing to render" makes billing-report the active ticket, which its Given does not name.

## Judgment — `harness/kanban/see-work-on-session-board.story.ui.spec.ts`

### `shared-example-fixtures` — Fail
- see-work-on-session-board.story.ui.spec.ts:126 the generate and validate lines of billing-report's story map are written out as literals rather than taken from one Seed fixture, as guide-work-through-practices.story.ui.spec.ts:25 and validate-fidelity-outputs.story.ui.spec.ts:90 also write them.

## Judgment — `harness/kanban/validate-fidelity-outputs.story.ui.spec.ts`

### `do-not-invent-requirements` — Fail
- validate-fidelity-outputs.story.ui.spec.ts:196 "Keep Validate off with nothing to check" makes billing-report the active ticket, which its Given does not name.

## Judgment — `harness/kanban/review-fidelity-outputs.story.ui.spec.ts`

### `do-not-invent-requirements` — Fail
- review-fidelity-outputs.story.ui.spec.ts:82 "Keep Review off until Validate is clean" makes billing-report the active ticket, which its Given does not name.

Passes: vocabulary-traces-to-domain-source, read-all-source-context-in-full, examples-declare-seed-vs-interaction (each file's docstring says what a Given seeds), seed-state-at-its-real-owner (the fixture project's `.sessions/`, files, and git checkout, written as fixture-repo.ts writes them), separate-test-controls-from-production-contracts, system-stubs-domain-real (the real board server and cdd tools; FakeChat checks in through the board's own route), assert-domain-behavior-not-seeded-state, infrastructure-in-lifecycle-hooks (boards, chats, and resets in beforeAll/beforeEach/afterEach), inline-simple-gwt-bodies, domain-operations-inline-in-steps (helpers are screen gestures).
