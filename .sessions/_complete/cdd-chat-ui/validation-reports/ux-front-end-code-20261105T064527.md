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


Judge only the checked format's files (python: C:/dev/abd-cdd-cdd-chat-ui/harness/chat-ui/{sub_epic_slug}.story.shared.py, C:/dev/abd-cdd-cdd-chat-ui/harness/chat-ui/{sub_epic_slug}.story.domain.spec.py, C:/dev/abd-cdd-cdd-chat-ui/harness/chat-ui/{sub_epic_slug}.story.server.spec.py; python: C:/dev/abd-cdd-cdd-chat-ui/harness/chat-ui/{module}/; html: ). The other formats mirror them, so judging those too reports every finding twice.

# Graph rule validation

**Generated:** 2026-11-05 06:45:27 UTC
**Project:** chat-ui
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-context-driven-delivery\.sessions\cdd-chat-ui\edited-graph.json`

## Summary

**Total graph violations:** 22
**Rules with graph hits:** 6
**AI rules in scope:** 39

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

Keep one object model. Follow the nouns and verbs the rest of the graph already uses for that concept. A class that joins types the rest of the graph keeps apart is a second model — a big ball of mud — and every rule then has to be written and fixed in both. Wrap or extend the live objects and name a wrapper after the type it represents; do not scrape the same data into a second `*Model` or `*Entry` family.

Evaluate the current context against this rule (do-not-invent-parallel-object-models):

### `hide-inner-details`

Expose behavior through named operations. Do not let callers see how the class stores or arranges its data — once they read the storage directly it becomes a public contract you cannot change. Private fields on the same class hide implementation; you do not need a second class for that. Read-only to callers can mean return a copy or immutable view from a property — it does not require a frozen class or a second type to hold build steps.

Evaluate the current context against this rule (hide-inner-details):

### `keep-operations-small-focused`

Keep each operation short enough to read as one thought — under 20 statements. A multi-line call, list, or string initializer is one statement. When it grows, extract a private helper whose name says why that slice exists.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [pane/test/chat-bar-world.ts](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\pane\test\chat-bar-world.ts#L23): Operation `checkoutFlow`: Operation 'checkoutFlow' is 27 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

Evaluate the current context against this rule (prefer-instance-operations):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

Evaluate the current context against this rule (keep-operations-single-responsibility):

### `simplify-control-flow`

Handle the failing or empty cases first and return. Keep the main path flat. Do not nest more than three levels — deeper than that you cannot tell which conditions hold on a given line without reading back up, and that is where the unhandled branch hides.

Evaluate the current context against this rule (simplify-control-flow):

### `errors-out-of-existence`

For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure.

Evaluate the current context against this rule (errors-out-of-existence):

### `no-prototype-swapping`

An object keeps the class it was built as. Do not change it afterwards with `Object.setPrototypeOf`, `__proto__ =`, or `__class__ =`. When a subclass needs to make its own instances, give the base an overridable factory (`blank()`) or build the right class directly. A swapped object skips its constructor, so fields the subclass sets up are missing and nothing tells you.

Evaluate the current context against this rule (no-prototype-swapping):

### `use-intention-revealing-names`

Name each class, property, operation, and parameter so it answers why it exists. Do not abbreviate.

**Graph violations:** 11

- [X] **ERROR** **[graph rule]** - [pane/hooks/chat-bar/chat-bar-client.ts](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\pane\hooks\chat-bar\chat-bar-client.ts#L168): Parameter `bar`: Parameter 'bar' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [pane/hooks/chat-bar/chat-bar-client.ts](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\pane\hooks\chat-bar\chat-bar-client.ts#L179): Parameter `bar`: Parameter 'bar' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [pane/hooks/chat-bar/chat-bar-client.ts](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\pane\hooks\chat-bar\chat-bar-client.ts#L224): Parameter `bar`: Parameter 'bar' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [pane/hooks/chat-bar/chat-bar-client.ts](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\pane\hooks\chat-bar\chat-bar-client.ts#L238): Parameter `bar`: Parameter 'bar' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [pane/hooks/chat-bar/chat-bar-view.tsx](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\pane\hooks\chat-bar\chat-bar-view.tsx#L48): Parameter `bar`: Parameter 'bar' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [pane/hooks/chat-bar/chat-bar-view.tsx](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\pane\hooks\chat-bar\chat-bar-view.tsx#L52): Parameter `bar`: Parameter 'bar' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [pane/test/chat-bar-world.ts](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\pane\test\chat-bar-world.ts#L114): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [pane/test/chat-bar-world.ts](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\pane\test\chat-bar-world.ts#L170): Parameter `ui`: Parameter 'ui' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [pane/test/chat-bar-world.ts](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\pane\test\chat-bar-world.ts#L175): Parameter `ui`: Parameter 'ui' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [pane/test/chat-bar-world.ts](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\pane\test\chat-bar-world.ts#L198): Parameter `ui`: Parameter 'ui' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [pane/test/chat-bar-world.ts](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\pane\test\chat-bar-world.ts#L201): Parameter `ui`: Parameter 'ui' does not reveal intent.

Evaluate the current context against this rule (use-intention-revealing-names):

### `use-consistent-naming`

Use one word per concept. Pick one verb and use it everywhere (`fetch_`, not a mix of `fetch_`, `get_`, and `retrieve_`). Two words for one concept is how the same logic gets written twice — nobody searching for `fetch_` finds the `retrieve_` that already does the job.

Evaluate the current context against this rule (use-consistent-naming):

### `provide-meaningful-context`

Give a number or literal a name that says why it is there (`SECONDS_PER_DAY`, not `86400`). Do not number variables (`item1`).

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [pane/test/chat-bar-world.ts](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\pane\test\chat-bar-world.ts#L186): Operation `settle`: Operation 'settle' uses the unnamed number 50.

Evaluate the current context against this rule (provide-meaningful-context):

### `eliminate-duplication`

Give repeated logic one canonical function. Every copy is another place the fix has to be repeated, and the copy you miss is the bug.

Evaluate the current context against this rule (eliminate-duplication):

### `no-legacy-api-after-refactor`

When you rename or reshape a public seam, update every caller — tests, dependencies, and adjacent modules — to the new API. Do not keep compatibility aliases, re-exports, or thin wrappers that preserve the old name.

Evaluate the current context against this rule (no-legacy-api-after-refactor):

### `use-exceptions-properly`

Raise a domain exception that names the failure (`CartAlreadyCheckedOut`, not `Error` or a bare string). Catch the specific type you can handle. Do not use a bare `except`. A generic exception cannot be caught selectively, so the caller has to handle everything or nothing.

Evaluate the current context against this rule (use-exceptions-properly):

### `never-swallow-exceptions`

Do not catch and ignore. Log and re-raise, or convert to a domain exception that still names the failure. A `pass` in `except` hides a broken invariant.

Evaluate the current context against this rule (never-swallow-exceptions):

### `limit-comments`

write comment in operations and properties only when the signature cannot say a constraint or explain why the code behaves the way it does. Do not narrate a line that already names what it does.

Evaluate the current context against this rule (limit-comments):

### `tab-states-are-separate-screens`

N tabs → N screens; chrome shared via `chrome_of` / inactive tabs.

Evaluate the current context against this rule (tab-states-are-separate-screens):

### `screen-story-budget`

~4 user stories per screen; more signals missed decomposition.

Evaluate the current context against this rule (screen-story-budget):

### `screen-names-use-domain-terms`

Screen labels trace to domain language when it exists.

Evaluate the current context against this rule (screen-names-use-domain-terms):

### `ia-named-regions-only`

At IA, regions are named slots; no control detail yet.

Evaluate the current context against this rule (ia-named-regions-only):

### `story-domain-js-imported`

At mockup+, when practices/stories/domain exist, JS modules are present (transform if needed) and imported by the html surface.

Evaluate the current context against this rule (story-domain-js-imported):

### `real-frontend-not-mockup`

Shipping UI is production frontend code, not the greybox Story Demo frame.

Evaluate the current context against this rule (real-frontend-not-mockup):

### `real-backend-wired`

Client talks to real services/persistence (CE **code**); no silent Fake path as the only path.

Evaluate the current context against this rule (real-backend-wired):

### `upstream-decisions-carried`

Layout and domain terms from earlier fidelities stay authoritative.

Evaluate the current context against this rule (upstream-decisions-carried):

### `keep-classes-single-responsibility`

Give each class one reason to change.

**Graph violations:** 5

- [X] **ERROR** **[graph rule]** - [pane/hooks/chat-bar/chat-bar-client.ts](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\pane\hooks\chat-bar\chat-bar-client.ts#L1): OoadClass `_module`: Class '_module' exposes 17 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [pane/hooks/chat-bar/chat-bar-view.tsx](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\pane\hooks\chat-bar\chat-bar-view.tsx#L1): OoadClass `_module`: Class '_module' exposes 16 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [pane/hooks/chat-bar/fidelity-client.ts](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\pane\hooks\chat-bar\fidelity-client.ts#L1): OoadClass `_module`: Class '_module' exposes 16 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [pane/hooks/register.ts](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\pane\hooks\register.ts#L1): OoadClass `_module`: Class '_module' exposes 19 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [pane/test/chat-bar-world.ts](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\pane\test\chat-bar-world.ts#L1): OoadClass `_module`: Class '_module' exposes 18 public operations (budget ~9). Split responsibilities.

Evaluate the current context against this rule (keep-classes-single-responsibility):

### `limit-operation-parameters`

Have callers pass intent, not setup. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [pane/hooks/chat-bar/chat-bar-view.tsx](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\pane\hooks\chat-bar\chat-bar-view.tsx#L230): Operation `LineView`: Operation 'LineView' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [pane/hooks/chat-bar/chat-bar-view.tsx](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\pane\hooks\chat-bar\chat-bar-view.tsx#L250): Operation `ChatBarView`: Operation 'ChatBarView' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [pane/hooks/register.ts](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\pane\hooks\register.ts#L111): Operation `post`: Operation 'post' takes 4 parameters (maximum 3, excluding self).

Evaluate the current context against this rule (limit-operation-parameters):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [pane/hooks/register.ts](C:\dev\abd-cdd-cdd-chat-ui\harness\chat-ui\pane\hooks\register.ts#L111): Parameter `body`: Parameter 'body' needs a domain-specific type, not a generic container.

Evaluate the current context against this rule (use-typed-signatures):

## Judgment — `harness/chat-ui/pane/hooks/chat-bar/chat-bar-view.tsx`

### `upstream-decisions-carried` — Fail
- chat-bar-view.tsx:171 `SessionCardView`: the canvas and CDR 0001 lay each fidelity's name and state over its own dot and stack the server health panel on top of the card; the card draws a plain list and the health panel stays in the line.
- chat-bar-view.tsx:207 `SessionNameView`: CDR 0001 has hovering the session name open the card; the card opens only on a press.

## Judgment — `harness/chat-ui/pane/hooks/chat-bar/fidelity-client.ts`

### `upstream-decisions-carried` — Fail
- fidelity-client.ts:99 `nextAction`: when the fidelity is not the ticket's next, the mod decides its next action itself (first of generate, validate, review not done); the decided pattern puts what comes next in the Python Ticket.

Passes: real-frontend-not-mockup (the chat bar is the mod's production AbovePrompt render), real-backend-wired (every action calls the cdd MCP tools, and a failed board read is shown above the line), tab-states-are-separate-screens, screen-story-budget, screen-names-use-domain-terms, ia-named-regions-only and story-domain-js-imported (IA and mockup rules; nothing at this fidelity breaks them).
