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
   ## Judgment — `harness/.context/stories/story-map.md`

   ### `rule-slug` — Fail
   - story-map.md:86 `Archive Ticket`: what breaks the rule, and why.

   ### `other-rule-slug` — Fail
   - story-map.md:148 `Send Sketch Iterate Or Document`: what breaks the rule, and why.
   ```

   - **One `## Judgment — ` section per judged file,** with an em dash, and the file in backticks as a path from the project's root, the way the session names paths. Never an absolute path or another checkout's path, because the board opens the file in this project and cannot open one anywhere else.
   - **One `### ` heading per rule that fails:** the rule slug in backticks, an em dash, then `Fail`. Leave passing rules out of these headings; a table or a Passes paragraph after the judgment may list them.
   - **One bullet per finding,** opening with the judged file's name, a colon, and one line number (`story-map.md:86`), then a space and what breaks the rule. A finding that spans lines takes its first line, and a finding at two places is two bullets, because the board opens each finding at one line.


Judge the graph validate built from the checked format's files (python: space/kanban/integrate-practice-content-editor-apps-in-chat-bar.story.shared.py, space/kanban/integrate-practice-content-editor-apps-on-board.story.shared.py, space/kanban/editor_apps_examples.py, space/kanban/editor_apps_tiers.py, space/kanban/board.py, space/kanban/board_app.py, space/kanban/ticket.py, space/session/session.py, harness/guidance/guidance.py, space/kanban/app/packages/session-board/app.ts, space/kanban/app/src/session-board/story-map-mount.spec.ts, space/kanban/app/src/kanban/board/editor-app-client.ts, space/kanban/app/src/kanban/board/editor-app-client.spec.ts, space/kanban/app/src/kanban/ticket/tile-view.tsx, harness/chat-ui/pane/hooks/chat-bar/fidelity-files-client.ts, harness/chat-ui/pane/hooks/chat-bar/fidelity-files-view.tsx, harness/chat-ui/pane/hooks/chat-bar/fidelity-progress-client.ts, harness/chat-ui/pane/hooks/chat-bar/chat-bar-client.ts, cdd_guidance/practices/stories/app/story-map/story-map-api.ts), saved at C:\dev\abd-context-driven-delivery\.sessions\integrate-practice-content-editor-apps\validation-reports\stories-acceptance-tests-20261113T002430.json: its classes, operations, parameters, properties, relationships, and dependencies, against each rule. Read a file only to see what a node stands for; whether a model document matches the code is a separate, secondary check.

Judge only the checked format's files (python: space/kanban/integrate-practice-content-editor-apps-in-chat-bar.story.shared.py, space/kanban/integrate-practice-content-editor-apps-on-board.story.shared.py, space/kanban/editor_apps_examples.py, space/kanban/editor_apps_tiers.py, space/kanban/board.py, space/kanban/board_app.py, space/kanban/ticket.py, space/session/session.py, harness/guidance/guidance.py, space/kanban/app/packages/session-board/app.ts, space/kanban/app/src/session-board/story-map-mount.spec.ts, space/kanban/app/src/kanban/board/editor-app-client.ts, space/kanban/app/src/kanban/board/editor-app-client.spec.ts, space/kanban/app/src/kanban/ticket/tile-view.tsx, harness/chat-ui/pane/hooks/chat-bar/fidelity-files-client.ts, harness/chat-ui/pane/hooks/chat-bar/fidelity-files-view.tsx, harness/chat-ui/pane/hooks/chat-bar/fidelity-progress-client.ts, harness/chat-ui/pane/hooks/chat-bar/chat-bar-client.ts, cdd_guidance/practices/stories/app/story-map/story-map-api.ts). The other formats mirror them, so judging those too reports every finding twice.

# Graph rule validation

**Generated:** 2026-11-13 00:25:03 UTC
**Project:** abd-cdd-integrate-practice-conte
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-context-driven-delivery\.sessions\integrate-practice-content-editor-apps\validation-reports\stories-acceptance-tests-20261113T002430.json`

**The session's graph also held, and practice-wide rules compared against:**
- `.`
- `cdd_guidance`
- `cdd_guidance/actions`
- `cdd_guidance/builders`
- `cdd_guidance/catalog`
- `cdd_guidance/context_setup`
- `cdd_guidance/patterns`
- `cdd_guidance/practices`
- `harness`
- `harness/.context`
- `harness/agent_tools`
- `harness/annotations`
- `harness/catalog_generator`
- `harness/chat`
- `harness/chat-ui`
- `harness/design_canvas`
- `harness/diagnostics`
- `harness/graph`
- `harness/guidance`
- `harness/guidance_actions`
- `harness/hooks`
- `harness/installation`
- `harness/markdown`
- `harness/mcp`
- `harness/process`
- `sandbox/mm3e`
- `sandbox/space-battle`
- `scripts`
- `space`
- `space/kanban`
- `space/repo`
- `space/session`
- `tools`
- `tools/drawio_viewer`
- `tools/echo`
- `tools/granola`
- `tools/prompt_log`
- `tools/prompt_notify`
- `tools/sub_agent`

## Summary

**Total graph violations:** 67
**Rules with graph hits:** 10
**AI rules in scope:** 33

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

### `vocabulary-traces-to-source`

Take every term from the source. The English term and the code name are the same word: *shopping cart* is `ShoppingCart`. When the code says a different word than the domain, every reader keeps a translation in their head, and the two names drift until they mean different things.

Evaluate the current context against this rule (vocabulary-traces-to-source):

### `do-not-invent-terms`

Do not invent a second noun or a parallel vocabulary. A second noun for the same thing becomes a second class, and then the same rule has to be written and fixed in both.

Evaluate the current context against this rule (do-not-invent-terms):

### `do-not-invent-parallel-object-models`

Keep one object model. Follow the nouns and verbs the rest of the graph already uses for that concept. A class that joins types the rest of the graph keeps apart is a second model — a big ball of mud — and every rule then has to be written and fixed in both. When data or behavior already belongs to an object, extend that object and hand callers the object itself: `ticket.session.practices["stories"].fidelities["story_map"].files()`, not `ticket.files(["stories-story-map"])`. A second model is rarely a whole class family; more often it is a small copy beside the owner: a dict holding one field from each member (`fidelity_states`, `violation_counts`), a `*_name` copy of a reference (`column_name`), a helper class that does the owner's job (`TicketFiles`), a bag of a few of the owner's answers (`Workspace`), or a `*Model` / `*Entry` family scraped from live objects. A copy hides that the owner is missing the behavior, so the next caller builds another copy and a fix to the owner never reaches it. **Checking it:** this rule spans modules, and the copy looks fine in the file that holds it. For every property, data field, dict, and helper class the changed code adds, name the class that already owns that data and read it; the rule fails when the owner holds it or should, and the change copies it instead of returning or extending the owner. Count the members of a class that delegates: dozens of members on a class that only reads its collaborators means it is copying them.

Evaluate the current context against this rule (do-not-invent-parallel-object-models):

### `hide-inner-details`

Expose behavior through named operations. Do not let callers see how the class stores or arranges its data — once they read the storage directly it becomes a public contract you cannot change. Private fields on the same class hide implementation; you do not need a second class for that. Read-only to callers can mean return a copy or immutable view from a property — it does not require a frozen class or a second type to hold build steps.

Evaluate the current context against this rule (hide-inner-details):

### `hold-state-on-the-object-not-in-parameters`

Keep what an object knows on the object, and let its operations read it there. A session holds its practices, a practice holds its fidelities and its current fidelity, a fidelity holds its actions and the format it last used, and an action is made for its session: `session.practices.stories.fidelities.story_map.actions.generate(format="drawio")`, not `Generate.commands_for(session, fidelities, formats)`. A value the caller supplies once, such as a format, is saved on the object that owns it, so the next operation on that object reads it instead of being handed it again. The rule fails when an operation takes, as a parameter, state its own object holds or should hold: the same argument handed down through several layers; a session, guidance, or ticket passed to every call on an object made for it; a name or slug passed so the receiver can look up an object the caller already holds; state written into a string (`session=...`) and parsed back; or a field set on a shared object for one call and restored afterwards. Every layer that passes the value is another place to pass the wrong one, and a call started from inside another, which nobody hands the value to, falls back to a global such as the current session and acts on the wrong object.

Evaluate the current context against this rule (hold-state-on-the-object-not-in-parameters):

### `keep-operations-small-focused`

Keep each operation short enough to read as one thought — under 20 statements. A multi-line call, list, or string initializer is one statement. When it grows, extract a private helper whose name says why that slice exists.

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\dev\abd-cdd-integrate-practice-conte\harness\guidance\guidance.py#L321): Operation `__init__`: Operation '__init__' is 25 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\dev\abd-cdd-integrate-practice-conte\harness\guidance\guidance.py#L935): Operation `instructions_in`: Operation 'instructions_in' is 28 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\dev\abd-cdd-integrate-practice-conte\space\session\session.py#L94): Operation `__init__`: Operation '__init__' is 30 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\dev\abd-cdd-integrate-practice-conte\space\session\session.py#L224): Property `graph`: Property 'graph' is 21 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `prefer-instance-operations`

Keep operations on the instance. Do not annotate them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, `now` (a new value for this moment), and `every` (each value the class allows). A global accessor such as `current` or `shared` is not a factory: it hands every caller the same object from class-level state, so it stays an instance operation on the object that holds that state, or goes.

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\dev\abd-cdd-integrate-practice-conte\harness\guidance\guidance.py#L250): Operation `child`: Operation 'child' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\dev\abd-cdd-integrate-practice-conte\harness\guidance\guidance.py#L316): Operation `edit_with`: Operation 'edit_with' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\dev\abd-cdd-integrate-practice-conte\harness\guidance\guidance.py#L412): Operation `class_key`: Operation 'class_key' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/kanban/board.py](C:\dev\abd-cdd-integrate-practice-conte\space\kanban\board.py#L117): Operation `places_cards`: Operation 'places_cards' is a classmethod; prefer an instance operation.

Evaluate the current context against this rule (prefer-instance-operations):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

Evaluate the current context against this rule (keep-operations-single-responsibility):

### `simplify-control-flow`

Handle the failing or empty cases first and return. Keep the main path flat. Do not nest more than three levels — deeper than that you cannot tell which conditions hold on a given line without reading back up, and that is where the unhandled branch hides.

Evaluate the current context against this rule (simplify-control-flow):

### `errors-out-of-existence`

For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure. A missing required argument is a broken call, not an ordinary edge: refuse it with a failure the program declares and names (`CommitPathsRequiredError`), which `domain-exception-carries-context` then asks to carry the rejected value.

Evaluate the current context against this rule (errors-out-of-existence):

### `no-prototype-swapping`

An object keeps the class it was built as. Do not change it afterwards with `Object.setPrototypeOf`, `__proto__ =`, or `__class__ =`. When a subclass needs to make its own instances, give the base an overridable factory (`blank()`) or build the right class directly. A swapped object skips its constructor, so fields the subclass sets up are missing and nothing tells you.

Evaluate the current context against this rule (no-prototype-swapping):

### `use-intention-revealing-names`

Name each class, property, operation, and parameter so it answers why it exists. Do not abbreviate.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\dev\abd-cdd-integrate-practice-conte\harness\guidance\guidance.py#L740): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\dev\abd-cdd-integrate-practice-conte\space\session\session.py#L52): Parameter `value`: Parameter 'value' does not reveal intent.

Evaluate the current context against this rule (use-intention-revealing-names):

### `use-consistent-naming`

Use one word per concept. Pick one verb and use it everywhere (`fetch_`, not a mix of `fetch_`, `get_`, and `retrieve_`). Two words for one concept is how the same logic gets written twice — nobody searching for `fetch_` finds the `retrieve_` that already does the job.

Evaluate the current context against this rule (use-consistent-naming):

### `provide-meaningful-context`

Give a number or literal a name that says why it is there (`SECONDS_PER_DAY`, not `86400`). Do not number variables (`item1`).

Evaluate the current context against this rule (provide-meaningful-context):

### `eliminate-duplication`

Give repeated logic one canonical function. Every copy is another place the fix has to be repeated, and the copy you miss is the bug.

Evaluate the current context against this rule (eliminate-duplication):

### `no-legacy-api-after-refactor`

When you rename or reshape a public seam, update every caller — tests, dependencies, and adjacent modules — to the new API. Do not keep compatibility aliases, re-exports, or thin wrappers that preserve the old name.

Evaluate the current context against this rule (no-legacy-api-after-refactor):

### `use-exceptions-properly`

Raise a domain exception that names the failure (`CartAlreadyCheckedOut`, not `Error` or a bare string). Catch the specific type you can handle. Do not use a bare `except`, and do not catch `Exception` (or `BaseException`) to return a default or substitute a fallback value: that turns every failure, including a bug, into the ordinary answer. A generic exception cannot be caught selectively, so the caller has to handle everything or nothing.

Evaluate the current context against this rule (use-exceptions-properly):

### `never-swallow-exceptions`

Do not catch and ignore. Log and re-raise, or convert to a domain exception that still names the failure. An `except Exception` that returns, `pass`es, or substitutes a fallback (an empty dict, `None`, the input unchanged) is swallowing too: the caller reads the fallback as a real answer, so a broken invariant reaches the next step unseen.

Evaluate the current context against this rule (never-swallow-exceptions):

### `limit-comments`

write comment in operations and properties only when the signature cannot say a constraint or explain why the code behaves the way it does. Do not narrate a line that already names what it does.

Evaluate the current context against this rule (limit-comments):

### `source-parses`

Keep every source file valid in its language. A file that does not parse is read into no classes, so every other rule passes it without looking, and its problems stay hidden until it runs.

Evaluate the current context against this rule (source-parses):

### `avoid-vague-parameter-names`

Do not name parameters `data`, `options`, `info`, or other placeholders that could mean anything. A vague name hides what the caller must supply and what the operation does with it.

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\dev\abd-cdd-integrate-practice-conte\harness\guidance\guidance.py#L203): Operation `rules_after_edit`: Parameter 'payload' in 'rules_after_edit' is vague.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\dev\abd-cdd-integrate-practice-conte\harness\guidance\guidance.py#L203): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\dev\abd-cdd-integrate-practice-conte\harness\guidance\guidance.py#L600): Operation `apply_settings`: Parameter 'settings' in 'apply_settings' is vague.

Evaluate the current context against this rule (avoid-vague-parameter-names):

### `conforms-to-schema`

Content conforms to its schema: every node has each relationship its schema type requires, up to the fidelity being worked. It checks only what the schema requires (a field written `name?:` is optional) and only for the fidelities worked so far: a relationship whose target a later fidelity creates is not required yet. Validate keeps only the findings inside the work's scope: the session's stories and everything under them, and the files the call names. It runs only on a graph that holds the session's whole working copy across its practices, so links across practices are judged; on a load of named files alone the AI judge weighs them.

**Graph violations:** 25

- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\dev\abd-cdd-integrate-practice-conte\harness\guidance\guidance.py#L52): Operation `__init__`: Operation '__init__' has no invokes relationship to Operation | Property, which the clean_engineering practice schema requires.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\dev\abd-cdd-integrate-practice-conte\harness\guidance\guidance.py#L55): Operation `opens`: Operation 'opens' has no invokes relationship to Operation | Property, which the clean_engineering practice schema requires.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\dev\abd-cdd-integrate-practice-conte\harness\guidance\guidance.py#L69): Operation `__init__`: Operation '__init__' has no invokes relationship to Operation | Property, which the clean_engineering practice schema requires.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\dev\abd-cdd-integrate-practice-conte\harness\guidance\guidance.py#L723): Operation `offers`: Operation 'offers' has no invokes relationship to Operation | Property, which the clean_engineering practice schema requires.
- [X] **ERROR** **[graph rule]** - [space/kanban/board.py](C:\dev\abd-cdd-integrate-practice-conte\space\kanban\board.py#L117): Operation `places_cards`: Operation 'places_cards' has no invokes relationship to Operation | Property, which the clean_engineering practice schema requires.
- [X] **ERROR** **[graph rule]** - [space/kanban/board.py](C:\dev\abd-cdd-integrate-practice-conte\space\kanban\board.py#L251): Operation `make_ticket`: Operation 'make_ticket' has no invokes relationship to Operation | Property, which the clean_engineering practice schema requires.
- [X] **ERROR** **[graph rule]** - [space/kanban/board.py](C:\dev\abd-cdd-integrate-practice-conte\space\kanban\board.py#L255): Operation `make_backlog_item`: Operation 'make_backlog_item' has no invokes relationship to Operation | Property, which the clean_engineering practice schema requires.
- [X] **ERROR** **[graph rule]** - [space/kanban/board.py](C:\dev\abd-cdd-integrate-practice-conte\space\kanban\board.py#L379): Operation `__init__`: Operation '__init__' has no invokes relationship to Operation | Property, which the clean_engineering practice schema requires.
- [X] **ERROR** **[graph rule]** - [space/kanban/board.py](C:\dev\abd-cdd-integrate-practice-conte\space\kanban\board.py#L429): Operation `__init__`: Operation '__init__' has no invokes relationship to Operation | Property, which the clean_engineering practice schema requires.
- [X] **ERROR** **[graph rule]** - [space/kanban/board.py](C:\dev\abd-cdd-integrate-practice-conte\space\kanban\board.py#L595): Operation `__init__`: Operation '__init__' has no invokes relationship to Operation | Property, which the clean_engineering practice schema requires.
- [X] **ERROR** **[graph rule]** - [space/kanban/board.py](C:\dev\abd-cdd-integrate-practice-conte\space\kanban\board.py#L639): Operation `_timestamp`: Operation '_timestamp' has no invokes relationship to Operation | Property, which the clean_engineering practice schema requires.
- [X] **ERROR** **[graph rule]** - [space/kanban/board.py](C:\dev\abd-cdd-integrate-practice-conte\space\kanban\board.py#L647): Operation `__init__`: Operation '__init__' has no invokes relationship to Operation | Property, which the clean_engineering practice schema requires.
- [X] **ERROR** **[graph rule]** - [space/kanban/board.py](C:\dev\abd-cdd-integrate-practice-conte\space\kanban\board.py#L694): Operation `__init__`: Operation '__init__' has no invokes relationship to Operation | Property, which the clean_engineering practice schema requires.
- [X] **ERROR** **[graph rule]** - [space/kanban/board.py](C:\dev\abd-cdd-integrate-practice-conte\space\kanban\board.py#L728): Operation `__init__`: Operation '__init__' has no invokes relationship to Operation | Property, which the clean_engineering practice schema requires.
- [X] **ERROR** **[graph rule]** - [space/kanban/board.py](C:\dev\abd-cdd-integrate-practice-conte\space\kanban\board.py#L763): Operation `__init__`: Operation '__init__' has no invokes relationship to Operation | Property, which the clean_engineering practice schema requires.
- [X] **ERROR** **[graph rule]** - [space/kanban/board.py](C:\dev\abd-cdd-integrate-practice-conte\space\kanban\board.py#L793): Operation `__init__`: Operation '__init__' has no invokes relationship to Operation | Property, which the clean_engineering practice schema requires.
- [X] **ERROR** **[graph rule]** - [space/kanban/ticket.py](C:\dev\abd-cdd-integrate-practice-conte\space\kanban\ticket.py#L88): Operation `__init__`: Operation '__init__' has no invokes relationship to Operation | Property, which the clean_engineering practice schema requires.
- [X] **ERROR** **[graph rule]** - [space/kanban/ticket.py](C:\dev\abd-cdd-integrate-practice-conte\space\kanban\ticket.py#L619): Operation `__init__`: Operation '__init__' has no invokes relationship to Operation | Property, which the clean_engineering practice schema requires.
- [X] **ERROR** **[graph rule]** - [space/kanban/ticket.py](C:\dev\abd-cdd-integrate-practice-conte\space\kanban\ticket.py#L696): Operation `__init__`: Operation '__init__' has no invokes relationship to Operation | Property, which the clean_engineering practice schema requires.
- [X] **ERROR** **[graph rule]** - [space/kanban/ticket.py](C:\dev\abd-cdd-integrate-practice-conte\space\kanban\ticket.py#L980): Operation `__init__`: Operation '__init__' has no invokes relationship to Operation | Property, which the clean_engineering practice schema requires.
- [X] **ERROR** **[graph rule]** - [space/kanban/ticket.py](C:\dev\abd-cdd-integrate-practice-conte\space\kanban\ticket.py#L999): Operation `_state_with`: Operation '_state_with' has no invokes relationship to Operation | Property, which the clean_engineering practice schema requires.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\dev\abd-cdd-integrate-practice-conte\space\session\session.py#L52): Operation `_shown`: Operation '_shown' has no invokes relationship to Operation | Property, which the clean_engineering practice schema requires.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\dev\abd-cdd-integrate-practice-conte\space\session\session.py#L141): Operation `name`: Operation 'name' has no invokes relationship to Operation | Property, which the clean_engineering practice schema requires.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\dev\abd-cdd-integrate-practice-conte\space\session\session.py#L170): Operation `session_path`: Operation 'session_path' has no invokes relationship to Operation | Property, which the clean_engineering practice schema requires.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\dev\abd-cdd-integrate-practice-conte\space\session\session.py#L397): Operation `hook_log`: Operation 'hook_log' has no invokes relationship to Operation | Property, which the clean_engineering practice schema requires.

Evaluate the current context against this rule (conforms-to-schema):

### `keep-classes-single-responsibility`

Give each class one reason to change.

**Graph violations:** 5

- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\dev\abd-cdd-integrate-practice-conte\harness\guidance\guidance.py#L278): OoadClass `PracticeGuidance`: Class 'PracticeGuidance' exposes 18 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\dev\abd-cdd-integrate-practice-conte\harness\guidance\guidance.py#L576): OoadClass `FidelityGuidance`: Class 'FidelityGuidance' exposes 24 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/kanban/board.py](C:\dev\abd-cdd-integrate-practice-conte\space\kanban\board.py#L93): OoadClass `Board`: Class 'Board' exposes 25 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/kanban/ticket.py](C:\dev\abd-cdd-integrate-practice-conte\space\kanban\ticket.py#L107): OoadClass `Ticket`: Class 'Ticket' exposes 24 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\dev\abd-cdd-integrate-practice-conte\space\session\session.py#L86): OoadClass `Session`: Class 'Session' exposes 39 public operations (budget ~9). Split responsibilities.

Evaluate the current context against this rule (keep-classes-single-responsibility):

### `limit-operation-parameters`

Have callers pass intent, not setup. A parameter that carries state the object already holds fails `hold-state-on-the-object-not-in-parameters` even when the count is small. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. Count each value a caller supplies: a packed tuple, `*args`, or `**kwargs` that carries four values counts as four parameters, because packing them hides the same setup instead of removing it. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

**Graph violations:** 10

- [X] **ERROR** **[graph rule]** - [harness/chat-ui/pane/hooks/chat-bar/fidelity-progress-client.ts](C:\dev\abd-cdd-integrate-practice-conte\harness\chat-ui\pane\hooks\chat-bar\fidelity-progress-client.ts#L27): Operation `constructor`: Operation 'constructor' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/chat-ui/pane/hooks/chat-bar/fidelity-progress-client.ts](C:\dev\abd-cdd-integrate-practice-conte\harness\chat-ui\pane\hooks\chat-bar\fidelity-progress-client.ts#L125): Operation `runActionOn`: Operation 'runActionOn' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\dev\abd-cdd-integrate-practice-conte\harness\guidance\guidance.py#L321): Operation `__init__`: Operation '__init__' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\dev\abd-cdd-integrate-practice-conte\harness\guidance\guidance.py#L542): Operation `render`: Operation 'render' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\dev\abd-cdd-integrate-practice-conte\harness\guidance\guidance.py#L585): Operation `__init__`: Operation '__init__' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\dev\abd-cdd-integrate-practice-conte\harness\guidance\guidance.py#L860): Operation `render`: Operation 'render' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [space/kanban/board.py](C:\dev\abd-cdd-integrate-practice-conte\space\kanban\board.py#L320): Operation `open_ticket`: Operation 'open_ticket' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [space/kanban/board.py](C:\dev\abd-cdd-integrate-practice-conte\space\kanban\board.py#L647): Operation `__init__`: Operation '__init__' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [space/kanban/ticket.py](C:\dev\abd-cdd-integrate-practice-conte\space\kanban\ticket.py#L754): Operation `__init__`: Operation '__init__' takes 6 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\dev\abd-cdd-integrate-practice-conte\space\session\session.py#L546): Operation `append_log`: Operation 'append_log' takes 4 parameters (maximum 3, excluding self).

Evaluate the current context against this rule (limit-operation-parameters):

### `prefer-class-operations`

Put factory, lifecycle, and helpers used from one class on that class. Do not export them as module-level functions — a free function holds no state, so it takes the object as a parameter and reaches into it to do the work. A file of hanging functions is the same miss: those operations belong on a type, not on the package.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\dev\abd-cdd-integrate-practice-conte\harness\guidance\guidance.py#L576): OoadClass `FidelityGuidance`: Module function '_folder_of' (line 562) is only used from 'FidelityGuidance'. Move it onto 'FidelityGuidance' as a method.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\dev\abd-cdd-integrate-practice-conte\space\session\session.py#L86): OoadClass `Session`: Module function '_shown' (line 52) is only used from 'Session'. Move it onto 'Session' as a method.

Evaluate the current context against this rule (prefer-class-operations):

### `use-explicit-dependencies`

Pass every collaborator through the constructor. Do not reach for a global or construct a collaborator inside construction. A collaborator the class fetches or builds itself cannot be swapped, so the class can only ever run against that one implementation.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\dev\abd-cdd-integrate-practice-conte\harness\guidance\guidance.py#L278): OoadClass `PracticeGuidance`: Class 'PracticeGuidance' constructs 'Format' inside its constructor.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\dev\abd-cdd-integrate-practice-conte\space\session\session.py#L86): OoadClass `Session`: Class 'Session' constructs 'DecisionRecords' inside its constructor.

Evaluate the current context against this rule (use-explicit-dependencies):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 10

- [X] **ERROR** **[graph rule]** - [harness/chat-ui/pane/hooks/chat-bar/chat-bar-client.ts](C:\dev\abd-cdd-integrate-practice-conte\harness\chat-ui\pane\hooks\chat-bar\chat-bar-client.ts#L221): Parameter `args`: Parameter 'args' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/chat-ui/pane/hooks/chat-bar/fidelity-progress-client.ts](C:\dev\abd-cdd-integrate-practice-conte\harness\chat-ui\pane\hooks\chat-bar\fidelity-progress-client.ts#L125): Parameter `suffix`: Parameter 'suffix' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\dev\abd-cdd-integrate-practice-conte\harness\guidance\guidance.py#L203): Parameter `payload`: Parameter 'payload' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\dev\abd-cdd-integrate-practice-conte\harness\guidance\guidance.py#L244): Parameter `parent`: Parameter 'parent' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\dev\abd-cdd-integrate-practice-conte\harness\guidance\guidance.py#L316): Parameter `app`: Parameter 'app' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\dev\abd-cdd-integrate-practice-conte\harness\guidance\guidance.py#L471): Parameter `session_output`: Parameter 'session_output' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\dev\abd-cdd-integrate-practice-conte\harness\guidance\guidance.py#L542): Parameter `content`: Parameter 'content' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\dev\abd-cdd-integrate-practice-conte\harness\guidance\guidance.py#L660): Parameter `session_output`: Parameter 'session_output' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\dev\abd-cdd-integrate-practice-conte\harness\guidance\guidance.py#L860): Parameter `content`: Parameter 'content' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\dev\abd-cdd-integrate-practice-conte\space\session\session.py#L52): Parameter `value`: Parameter 'value' needs a domain-specific type, not a generic container.

Evaluate the current context against this rule (use-typed-signatures):


Judge the work against these overlaid patterns' rules too, as you judge the practices' rules.

## Pattern overlay: lern_domain_driven

This session overlays the lern_domain_driven pattern, so its shared rules below apply on top of the practices' rules. Its whole guidance is its instructions, `lern-domain-driven_instructions`.

## Shared rules



Whenever you create, alter, or delete a LERN domain module under `src/`, an epic
package under `packages/`, or tests they support. Follow these rules.

If this change will not stay here, follow `practices/clean-engineering/clean-engineering-code.mdc`. If the tests are Spec-by-Example, also follow `practices/stories/stories-acceptance-tests.mdc`. The `practices/ddd/ddd-tactics.mdc` rules apply to domain classes.

### Layout and tiers

- **`screens-live-in-their-domain`** — A screen lives in the aggregate folder of the domain it serves, beside that aggregate's client and node. Keep the aggregate under `src/<boundedContext>/<aggregate>/` (`<aggregate>.ts`, `<aggregate>-node.ts`, `<aggregate>-client.tsx`, the views, one `<aggregate>-routes.ts`, and the json store). `packages/<epicSlug>/` holds epic boot (`app.ts`, `serve.ts`, `main.tsx`) and what is common across the epic — the top-level router, the frame that composes the step screens, the shell layout, shared assets, and epic-wide logic such as a plan carried in from a marketing link. Never put a step screen, `<aggregate>.ts`, `<aggregate>-node.ts`, `<aggregate>-client.tsx`, or an aggregate route file under the epic package.
- **`domain-core-file-matches-folder-slug`** — Name the domain core file after the aggregate folder slug in kebab-case (`src/<boundedContext>/<aggregate>/<aggregate>.ts`). Keep exported classes PascalCase (`{Domain}`). Place `<aggregate>-node.ts`, `<aggregate>-client.tsx`, the views, and one route file in that same aggregate folder. Exception: the epic-wide module `src/<epicSlug>/` (e.g. `src/my-paradise/`) holds global session and navigation objects that belong to no single aggregate; it needs no `<epicSlug>.ts` core, and its node and client need not extend one.
- **`node-tier-uses-node-suffix`** — Name the Node.js LERN tier with the `Node` suffix and `<domain>-node.ts` filenames (`{Domain}Node`, `{Domain}RepositoryNode`). Type request-context fields as `*Node`, not `Server`. `{Domain}RepositoryNode` extends the in-memory `{Domain}Repository` and is the class that runs Zod `.parse()` and writes `<aggregate>.json`.
- **`client-subtypes-domain-hosts-browser-logic`** — For each aggregate folder, derive `<aggregate>.ts`, `<aggregate>-client.tsx`, and `<aggregate>-node.ts` from the folder slug. The `*Client` and `*Node` classes extend the core domain class. The view renders the client. The node selects the view. Domain operations on the core are the operations the client hosts for the browser; field changes return a new client instance for React state.

### Navigation and views

- **`node-decides-next-page`** — The node class decides the next page. `*Node.destination` maps the domain step to the browser path; path maps stay in `*-node.ts`.
- **`router-asks-the-node`** — Route modules only ask node classes and return the path they produce. Redirect components fetch that result and mount the view — neither derives the page from a step locally.
- **`views-render-only`** — A view lives in the aggregate folder and only renders. It keeps the client in React state and paints fields, requirement lines, and actions the client exposes. Field entry, touched flags, and host operations stay on the client. The node selects the next view.
- **`compose-steps-from-the-owner`** — Dependencies follow the domain model in every tier, not only the core: an aggregate's routes, client, and views import only the aggregates it depends on. A step screen knows its own aggregate; it takes what it shows from the epic's frame as props and reports `onDone`-style callbacks. The frame (`packages/<epicSlug>/`) composes the step screens and turns each callback into an operation on the owning aggregate's client. A step's own routes touch only its aggregate; the route that records a finished step on the owner lives in the owner's route file, runs the step's aggregate first, then the owner, in one request.
- **`one-home-for-web-paths`** — Browser paths are string literals in one `<aggregate>-paths.ts` module. The node's path map, the epic router, and views import them; nothing else spells a path out.

### Persistence and repositories

- **`one-json-store-per-aggregate`** — Each aggregate root owns its own JSON file in its aggregate folder. Do not put several aggregates in one file. Repositories never open another aggregate's JSON file.
- **`repository-owns-aggregate-lifecycle`** — `{Domain}Repository` is the in-memory collection seam for the root: `load`, `create`, `search`, `update` — named in ubiquitous language. `{Domain}RepositoryNode` extends it, runs Zod `.parse()`, and writes `<aggregate>.json`.
- **`one-repository-per-aggregate`** — One in-memory `{Domain}Repository` on `<aggregate>.ts` and one `{Domain}RepositoryNode` on `<aggregate>-node.ts`. The client does not declare a repository.
- **`node-repository-parses-on-read`** — `{Domain}RepositoryNode` reads `<aggregate>.json` through the lowdb helpers and runs the aggregate's Zod schema `.parse()` on what it reads. No `readFileSync` or `writeFileSync` in a repository.

### Naming, purity, and packaging

- **`share-domain-logic`** — Entities, value objects, Zod schemas, and business rules defined once in `<domain>.ts`; `-node.ts` and `-client.tsx` import from there, never re-derive.
- **`maintain-layer-purity`** — `<domain>.ts` is framework-free (no Express, no React, no lowdb); `-node.ts` and `-client.tsx` never cross-import each other.
- **`use-ubiquitous-language`** — Names come from the domain model; no `Manager`, `Handler`, `Helper`, or `Domain*` prefixes/suffixes.
- **`cross-layer-method-naming`** — The same `{verbNoun}` method stem flows through core → client → node → route → HTTP; subclasses keep every inherited base operation unchanged.
- **`preserve-arg-names-across-layers`** — Argument names stay identical across layer boundaries; only types narrow.
- **`property-casing-transform`** — `camelCase` in TypeScript; `snake_case` in JSON (lowdb documents and HTTP bodies).
- **`consistent-view-naming`** — React components end in `View`; screen filenames stay kebab-case.
- **`ensure-type-safe-routes`** — Route handlers compile without implicit `any`; request extensions are typed.
- **`standard-mutation-response`** — Every mutation on the same aggregate returns the same response shape.
- **`implement-domain-entities-correctly`** — Business rules live on domain classes. `{Domain}Repository` is in-memory only. `{Domain}RepositoryNode` runs Zod `.parse()` and writes `<aggregate>.json`. Routes and views do not validate or write the store.
- **`implement-full-interfaces`** — Every `implements` clause covers all interface members; no stub no-ops.
- **`use-valid-package-names`** — One epic package per feature with `@src` imports into `src/`; no phantom imports or legacy flat `*-shared` / `*-server` / `*-client` package split.
- **`include-all-external-dependencies`** — Every import has a declared dependency (`lowdb` on the server); the project compiles after a clean install.
- **`posted-body-parsed-in-node`** — A route passes `req` to `{Domain}Node.fromRequest`, which parses the posted body with a Zod schema. Routes never read `req.body.<field>`.
- **`throw-http-exceptions`** — Routes and nodes fail by throwing `HttpException` (or a subclass). One error middleware turns it into the reply. No `throw {…}`, no thrown strings, no hand-written `res.status(4xx).json(…)`.

### Testing and story generation

- **`reduce-story-overlap`** — Each sub-epic states each story once in `<snake>.story.shared.ts`. The domain spec runs that story on the entity repository. The server spec runs that same story on the node repository. A scenario's Given, When, and Then stay in the shared story; domain and server specs run it with `.run()`, `runAll()`, or `withScenario().run()`. When two files would assert the same outcome, keep that assertion in the shared story and run it from both tiers. A server spec adds a scenario only for an HTTP or route result the shared story does not cover. A Playwright file adds a screen story only for interaction the shared story does not cover.
- **`scaffold-test-scripts`** — `scripts/test.sh`, `test.ps1`, `test-e2e.sh`, `test-e2e.ps1` at the workspace root; Vitest and Playwright stay separate.
- **`playwright-tests-browser-interaction`** — Playwright tests interaction the domain spec and the server spec cannot see: a rendered screen, navigation, and controls the user operates in the browser. Every story a person does on a screen has one: a describe named as the story, a test per scenario; only a system or technical story has none. It states its own screen story. It leaves the shared story to the domain spec and the server spec.
- **`tier-bound-repository-accessor`** — Shared stories reach repositories through the accessor each tier binds (`repositories.subscriptions`, …), never by casting the story context (`ctx.x as X`).
- **`no-expect-in-given`** — A Given sets up state; it does not assert. Checks belong in a Then.
- **`outline-entries-loop-over-examples`** — A Scenario Outline runs as `examples.forEach(row => scenario(`Name: ${row.example}`, …))` over its examples export, in the shared story and in the Playwright screen story alike. Never hand-write one `scenario('Name: entry', …)` per example entry: a hand-written entry drops the other entries silently.
- **`reset-every-repository`** — Every exported repository instance, in-memory and node, is reset before each story, so no story sees another's state.

### Testing with BDD

- **`shared-behavior-stays-tier-free`** — A shared behavior reaches its tier only through its driver. It imports no node or client and never touches `page` or `fetch`, because a line tied to one tier stops the behavior running on the others.
- **`tier-runs-shared-behavior`** — Each tier file runs the shared behavior with `itBehavesLike`, so a signature exists once. A tier that copies a behavior keeps passing after the shared one changes.
- **`server-tier-calls-the-real-thing`** — The server tier calls `{Domain}Node` objects, which call their real store or MCP tool, with no `vi.mock`, `vi.fn`, or spy. Give it a throwaway store or project. A stub here would agree with the code that wrote it and prove nothing about the real answer.
- **`e2e-runs-the-whole-stack`** — The e2e tier runs the page, the real server, and the real store or tool, with no stub and no intercepted request. Anything stubbed there is already covered by a faster tier, and the gap between the layers is what this tier exists to catch.
- **`domain-tier-only-for-domain-logic`** — Add a domain tier only when `<aggregate>.ts` holds logic worth proving alone. A core that only states structure has nothing to run, and the server tier already exercises it.
- **`same-signature-across-languages`** — When the domain is in another language, as a CDD-backed domain is, a behavior the Mamba spec states keeps the same `should` sentence in the shared behavior. A sentence on one side only shows a behavior untested on the other.
- **`ask-cross-aggregate-sync`** — **Hard gate** when generating stories. Use AskQuestion; persist the answer under **Cross-aggregate sync** in `.context/grill-answers.md` before writing story files.

## Pattern overlay: cdd_web_domain_access

This session overlays the cdd_web_domain_access pattern, so its shared rules below apply on top of the practices' rules. Its whole guidance is its instructions, `cdd-web-domain-access_instructions`.

## Shared rules



Whenever you create, alter, or delete code outside Python that reaches the CDD domain, or the MCP tools it calls. Follow these rules.

If this change will not stay here, follow `practices/clean-engineering/clean-engineering-code.mdc`. The `practices/ddd/ddd-tactics.mdc` rules apply to the Python domain classes.

### Domain and state

- **`domain-lives-in-python`** — Put every rule and decision in the Python domain class: what a state means, whether an action is allowed, what comes next. A rule written in another language is lost to the agent's tools and to every other door.
- **`state-lives-behind-the-tool`** — Get every fact about a CDD object from its adapter, and keep no repository, store, or cache of it beside the state the adapter's last call returned. The agent changes that state without telling the application, so a copy goes stale.

### One object, one set of generated classes

- **`one-class-per-object`** — Each domain object has its own generated `{Object}Adapter` and `{Object}ClientGenerated` that call only that object's tools. Code that calls a tool by name, or posts to a tool's route by hand, has skipped the object's typed operation and hides which object owns it.
- **`adapter-is-generated`** — The installer writes `CddConnection`, `{Object}`, `{Object}Adapter`, `{Object}ClientGenerated`, and `{object}Routes`, and nobody edits them or writes one by hand. Subclass `{Object}ClientGenerated` only for what the page alone knows, never to add a call, a route, or parsing. A hand-kept class drifts from Python, and the compiler then checks the wrong thing. The generated views are the exception: they only present what the client already does, so an application may copy one and change it.
- **`views-are-a-starting-point`** — Compose a generated view into the application's own page, or copy it into the application's source and change it; never ship one as the page itself. It knows the object's fields and operations but nothing about the page it sits on.
- **`edits-go-through-operations`** — A view changes a field only by calling the domain operation that changes it, and shows a field no operation changes as read-only. A view that writes a field directly decides in the browser what only Python may decide.
- **`views-share-the-client-state`** — A view reads its object through `use{Object}(client)` and keeps no copy of the object's state. A second copy shows the old state after an operation returns.
- **`annotate-toolsets-that-return-data`** — Annotate a toolset with `@language_adapter` when an application needs its results as data, and annotate its `@identity` when a tool loads one object. Annotating one that returns prompt text adds an adapter nobody can type.

### One line from adapter to domain

- **`one-line-to-the-domain`** — One adapter operation reaches one MCP tool, which calls one domain operation. Work spanning several calls belongs in a domain operation, so an agent and a person get the same result.
- **`tool-matches-the-object`** — Name the toolset after the Python object it acts on, so the tool reads `ticket.move_next`. A tool named after the component gathers every object's operations into one class.
- **`same-verb-across-layers`** — Use the same verb and noun from page to domain: `moveNext`, `/ticket/:ticket/move-next`, `ticket.move_next`, `Ticket.move_next`. A reader can then follow an action by searching one word.
- **`tool-stays-thin`** — A tool finds the domain object, calls one operation, and returns the object it answers with; MCP sends that object's data fields. Logic in a tool cannot be reached by anything that calls the domain directly.

### Contract and failure

- **`annotate-what-typescript-reads`** — Annotate each property another language reads with `@data_field`, and annotate each MCP operation on an annotated toolset with the domain class it returns. A plain `dict[str, Any]` generates an open record, which the compiler cannot check.
- **`calls-finish-in-ten-minutes`** — Keep every operation within the ten-minute limit, and fix one that needs longer instead of raising the limit. A page that waits longer than that looks broken, and a raised limit hides the slow operation.
- **`report-progress-on-long-calls`** — An operation that takes more than a few seconds calls `report_progress` at each step, and the page shows them with `ProgressViewGenerated`. A page with no news looks the same as one that has stopped.
- **`read-files-through-the-file-manager`** — Show a file through the session's `FileManager` and its source view, and annotate a file field `Annotated[str, SourceFile]`. A read operation or a file viewer written for one object is a second copy of what every application shares.
- **`fail-loud-on-mcp`** — When a call fails or the server is missing, show the person what failed and how to fix it. Drawing old state as if it were current misleads them into acting on it.

### Testing

- **`test-the-adapter-against-real-cdd`** — Tests that call `{Object}Adapter` run against a real cdd server on a throwaway project. A stubbed tool would pass after the Python changed.
- **`act-on-a-throwaway-project`** — Any test that moves, closes, or commits runs on a throwaway project with no real remote, because these tools really commit and push.

## Stories in this session

This session's increment is these stories, named in its ticket. Generate and validate every one of them with the patterns its content is generated with (lern_domain_driven, cdd_web_domain_access). Stories outside this list belong to other increments: do not generate, judge, or report them.

- Open Story UI Side Panel From Chat Bar
- Trace Story Through Artifacts
- Open Knowledge Graph Side Panel From Chat Bar
- Open Kanban Side Panel From Chat Bar
- Invoke Claude Design Story Explorer From Chat Bar
- Deploy Story UI App With Board State
- Refactor Story UI App To Web Domain Access
- Open Story UI On Ticket Scope
- Filter Knowledge Graph To Ticket Scope
- Filter Knowledge Graph To Ticket Practices
- Deploy Knowledge Graph App With Board State
- Refactor Kanban Board To Web Domain Access
## Judgment — `space/kanban/app/src/kanban/board/editor-app-client.ts`

### `eliminate-duplication` — Fail
- editor-app-client.ts:10 `EditorAppClient`: openOn repeats GraphAppClient.openOn (board/graph-app-client.ts: app.open through AppClientGenerated, refuse when not running, open the page with ?project=). One client should open any app on a project, and the graph widget should call it; GraphAppClient belongs to the graph agent's widget, so it was left for that owner.

## Judgment — `harness/guidance/guidance.py`

### `prefer-instance-operations` — Fail
- guidance.py:314 `edit_with`: a classmethod that only set class state. Fixed after this report: removed; space/kanban sets the class field `Stories.editor = STORY_UI_APP`.

### `use-typed-signatures` — Fail
- guidance.py:314 `edit_with(app: Any)`: untyped app. Fixed after this report: the field is `ClassVar[App | None]`, App imported for typing only.

Passes for the changed code: hide-inner-details, hold-state-on-the-object-not-in-parameters (BoardPractice.editor and FidelityProgress.editor read their practice; Session.design_view reads its own outputs), keep-operations-small-focused, keep-operations-single-responsibility, simplify-control-flow, errors-out-of-existence (no design view is an empty string; no editor is None), use-intention-revealing-names, use-consistent-naming (editor, design_view, openOn as the graph client names it), no-legacy-api-after-refactor (edit_with removed with every caller), use-exceptions-properly, never-swallow-exceptions, limit-comments, source-parses, do-not-invent-parallel-object-models (BoardPractice.editor and FidelityProgress.editor return the practice's App itself, no copy). The other graph hits in these files (Board, Ticket, Session, PracticeGuidance size; __init__ invokes) are on code this work did not change.
