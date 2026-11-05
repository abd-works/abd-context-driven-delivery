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

**Generated:** 2026-11-04 18:02:53 UTC
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

## Judgment — `harness/kanban/steer-ticket-sessions.story.shared.py`

| Rule | Verdict |
|---|---|
| domain-operations-inline-in-steps | **Fail** |
| infrastructure-in-lifecycle-hooks | **Fail** |
| extract-assertion-helper | **Fail** |
| shared-example-fixtures | **Fail** |

### `domain-operations-inline-in-steps` — Fail
- steer-ticket-sessions.story.shared.py:278 the git checkout, origin, pushed branch, work file, session, and open session of "checkout-flow is the active ticket, on its own branch" are seeded step by step here and again at line 481, where a `seed…` fixture in the examples file should hold that shared prior state.
- steer-ticket-sessions.story.shared.py:314 the checkout-on-main state of "checkout-flow is the active ticket" is seeded step by step here and again at lines 522 and 554 instead of through one `seed…` fixture.

### `infrastructure-in-lifecycle-hooks` — Fail
- steer-ticket-sessions.story.shared.py:255 checkout-flow is loaded in this When and loaded again in the next When at line 267, rather than once at the highest Given that needs it.
- steer-ticket-sessions.story.shared.py:287 checkout-flow is loaded for workspace() and again at line 295 for close(), rather than once at the Given.
- steer-ticket-sessions.story.shared.py:494 billing-report is loaded for workspace() and again at line 506 for activate(), rather than once at the Given.
- steer-ticket-sessions.story.shared.py:678 checkout-flow is loaded again for read_file() after the When at line 672 already loaded it.

### `extract-assertion-helper` — Fail
- steer-ticket-sessions.story.shared.py:193 the shape `Board.current().show().to_json()["active"]` equals a name repeats at lines 307, 510, 539, 572, and 596 with no assertion helper.
- steer-ticket-sessions.story.shared.py:338 the shape "rev-list --count of a branch is 1" repeats at lines 547 and 576 with no assertion helper.
- steer-ticket-sessions.story.shared.py:334 the shape "the session's folder sits under a given .sessions/ folder" repeats at lines 431, 450, and 637 with no assertion helper.
- steer-ticket-sessions.story.shared.py:105 the Backlog's titles are compared at lines 105, 143, and 403 here and twice more in see-work-on-session-board.story.shared.py, each copy reading the column itself.

### `shared-example-fixtures` — Fail
- steer-ticket-sessions.story.shared.py:665 the earlier handoff's text "# Earlier handoff" is a literal in the step rather than a fixture beside LATEST_HANDOFF.

## Judgment — `harness/kanban/see-work-on-session-board.story.shared.py`

| Rule | Verdict |
|---|---|
| shared-example-fixtures | **Fail** |
| infrastructure-in-lifecycle-hooks | **Fail** |
| extract-assertion-helper | **Fail** |

### `shared-example-fixtures` — Fail
- see-work-on-session-board.story.shared.py:59 DISCOVERY_FIDELITIES is copied here and again in guide-work-through-practices.story.shared.py:43, so two copies of one example can drift.
- see-work-on-session-board.story.shared.py:232 pet-visits' log line "generate /work/ux ux mockup html ux" is a literal in the step rather than a named fixture in the examples file.

### `infrastructure-in-lifecycle-hooks` — Fail
- see-work-on-session-board.story.shared.py:87 the practices' modules are imported inside the Given, mixing module wiring into domain state.

### `extract-assertion-helper` — Fail
- see-work-on-session-board.story.shared.py:139 the Backlog's titles are compared here and at line 186 in the same shape as steer-ticket-sessions.story.shared.py:105, with no shared helper.

## Judgment — `harness/kanban/guide-work-through-practices.story.shared.py`

| Rule | Verdict |
|---|---|
| shared-example-fixtures | **Fail** |
| extract-assertion-helper | **Fail** |

### `shared-example-fixtures` — Fail
- guide-work-through-practices.story.shared.py:43 DISCOVERY_FIDELITIES is a second copy of see-work-on-session-board.story.shared.py:59.
- guide-work-through-practices.story.shared.py:51 the log line "generate /work, /work/docs stories story_map markdown stories" is a literal in the step rather than a named fixture.
- guide-work-through-practices.story.shared.py:200 the old-style log lines "pull Specification" and "done Specification" are literals in the step rather than a named fixture.
- guide-work-through-practices.story.shared.py:355 the move line "move Specification" is written out in the step rather than taken from a named fixture.

### `extract-assertion-helper` — Fail
- guide-work-through-practices.story.shared.py:178 the shape "next is None and next_action is empty" repeats at line 378 and at review-fidelity-outputs.story.shared.py:246 with no assertion helper.
- guide-work-through-practices.story.shared.py:82 the shape "one action of the story map reads a state" repeats at line 344, at review-fidelity-outputs.story.shared.py:208, generate-fidelity-outputs.story.shared.py:106, and validate-fidelity-outputs.story.shared.py:72, with no assertion helper.
- guide-work-through-practices.story.shared.py:78 the shape "Validate in progress and the segment in violations" repeats at validate-fidelity-outputs.story.shared.py:86 with no assertion helper.

## Judgment — `harness/kanban/generate-fidelity-outputs.story.shared.py`

| Rule | Verdict |
|---|---|
| shared-example-fixtures | **Fail** |

### `shared-example-fixtures` — Fail
- generate-fidelity-outputs.story.shared.py:70 pet-visits' story map at docs/story-map.md and its text are literals in the step rather than a named Seed fixture.

## Judgment — `harness/kanban/validate-fidelity-outputs.story.shared.py`

| Rule | Verdict |
|---|---|
| domain-operations-inline-in-steps | **Fail** |
| infrastructure-in-lifecycle-hooks | **Fail** |

### `domain-operations-inline-in-steps` — Fail
- validate-fidelity-outputs.story.shared.py:49 seed_checkout_flow_validating is a seed helper in the story file; prior state shared by several steps belongs in a `seed…` fixture in the examples file.

### `infrastructure-in-lifecycle-hooks` — Fail
- validate-fidelity-outputs.story.shared.py:63 pet-visits' session is loaded with Session.at in this When and loaded again at line 76, rather than once at the Given.

## Judgment — `harness/kanban/session_board_examples.py`

| Rule | Verdict |
|---|---|
| examples-declare-seed-vs-interaction | **Fail** |
| seed-state-at-its-real-owner | **Fail** |
| shared-example-fixtures | **Fail** |

### `examples-declare-seed-vs-interaction` — Fail
- session_board_examples.py:165 the block from LATEST_HANDOFF to NO_SUCH_FIDELITY mixes Seed files (handoffs, specs) with Interaction values (OUTSIDE_FILE, NO_SUCH_TICKET, NO_SUCH_FIDELITY) under one heading, so a reader cannot tell which the repository owns.
- session_board_examples.py:179 STORY_MAP and the other Interaction constants follow the Seed fixtures with no declaration of which is which beyond a bare "# Interactions." line.

### `seed-state-at-its-real-owner` — Fail
- session_board_examples.py:236 seed_active writes `.sessions/session.json` by hand although WorkState owns that file and its `session` property is how Session.switch saves the open session.

### `shared-example-fixtures` — Fail
- session_board_examples.py:153 SEARCH_THE_CATALOG_FILE is a second name for SEARCH_THE_CATALOG, so one example has two fixtures.
