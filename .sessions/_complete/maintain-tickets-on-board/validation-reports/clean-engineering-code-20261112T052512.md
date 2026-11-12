# Validate

Take the persona of a **critical judge** — do not edit the artifact.

1. Read the appropriate practice and fidelity level guidlines and rules. Scope judgment to artifacts passed into context.
1b. **Stories in the session's scope.** A session's ticket names its stories (its `Story:` headings); they are the increment. Every one of them is generated and validated with the patterns its content is generated with: generate uses the session's overlays and records them in `.context/patterns.md` at the root of each folder it writes, with the roles the folder holds of a pattern whose layers sit in several folders; validate reads that file. Stories the ticket does not name belong to other increments: leave them alone, and do not judge or report them. The graph report already keeps only the story map's findings on those stories.
2. Use each **practice** as the rubric — report Pass or Fail per named practice fidelity and named rule with brief evidence. There is no third verdict: a rule that is only partly met is a Fail, because a softer verdict lets a broken rule through review.
3. When **paths** names the files being edited, the graph is built from just those files as they are now, and its rules run on them. Pass the files you wrote, not the whole tree. Without **paths**, when **graph** is `true`, read the saved graph of the session's folder (`.context/graph.json`, which exists only after `graph.load_working_copy` has run on that folder); when it is a path (or list of paths), read that `graph_return_nodes` JSON or saved graph. Append a **Graph rule validation** report for each guidance's practice. Each rule is one section: heading, rule text, any graph hits (**[graph rule]**), then the AI judgment prompt for that rule.
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


Judge the graph validate built from the checked format's files (python: space/kanban/ticket.py, space/kanban/board.py, space/kanban/backlog_item.py, space/kanban/app/src/kanban/ticket/ticket-client.tsx, space/kanban/app/src/kanban/ticket/ticket-card-view.tsx, space/kanban/app/src/kanban/ticket/card-upkeep-view.tsx, space/kanban/app/src/kanban/ticket/child-rows-view.tsx, space/kanban/app/src/kanban/ticket/card-drag.ts, space/kanban/app/src/kanban/ticket/report-client.ts, space/kanban/app/src/kanban/ticket/open-card-client.ts, space/kanban/app/src/kanban/shared/card-field-view.tsx, space/kanban/app/src/kanban/board/board-client.tsx, space/kanban/app/src/kanban/board/board-header-view.tsx, space/kanban/app/src/kanban/backlog-item/backlog-item-client.tsx, space/kanban/app/src/kanban/backlog-item/backlog-item-view.tsx, cdd_guidance/actions/validate/validate.py, cdd_guidance/actions/validate/checked_graph.py, cdd_guidance/actions/generate/generate.py, harness/graph/patterns_file.py, harness/graph/pattern_overlays.py, space/session/idea_file.py, cdd_guidance/patterns/lern_domain_driven/practices/stories/rules/shared_story_rules.py), saved at C:\dev\abd-context-driven-delivery\.sessions\maintain-tickets-on-board\validation-reports\clean-engineering-code-20261112T052512.json: its classes, operations, parameters, properties, relationships, and dependencies, against each rule. Read a file only to see what a node stands for; whether a model document matches the code is a separate, secondary check.

# Graph rule validation

**Generated:** 2026-11-12 05:25:18 UTC
**Project:** abd-cdd-maintain-tickets-on-boar
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-context-driven-delivery\.sessions\maintain-tickets-on-board\validation-reports\clean-engineering-code-20261112T052512.json`

**The session's graph also held, and practice-wide rules compared against:**
- `.`
- `author-story-maps/author-story-changes-with-ai`
- `author-story-maps/save-and-share-changes`
- `author-story-maps/view-story-map`
- `build-design-canvas-screens/publish-and-release-a-canvas-version`
- `cdd_guidance`
- `cdd_guidance/actions`
- `cdd_guidance/patterns`
- `connect-sessions-across-channels-and-apps/check-work-in-generate`
- `connect-sessions-across-channels-and-apps/connect-chat-bar-board-and-story-ui`
- `connect-sessions-across-channels-and-apps/read-graph-violations-in-chat-bar`
- `connect-sessions-across-channels-and-apps/read-graph-violations-on-board`
- `explore-stories-in-story-ui/frame-design-canvas-screens-in-explorer`
- `explore-stories-in-story-ui/navigate-the-story-tree`
- `explore-stories-in-story-ui/play-stories-in-the-explorer`
- `explore-stories-in-story-ui/show-screen-frames-in-story-ui`
- `harness`
- `harness/.context`
- `harness/chat`
- `harness/diagnostics`
- `harness/graph`
- `harness/installation`
- `map-work-into-knowledge-graph/review-violations-in-graph-app`
- `move-work-forward-from-chat-bar/capture-session-knowledge`
- `move-work-forward-from-chat-bar/enter-cdd-commands-faster`
- `move-work-forward-from-chat-bar/generate-fidelity-outputs-in-chat-bar`
- `move-work-forward-from-chat-bar/guide-work-through-practices`
- `move-work-forward-from-chat-bar/integrate-practice-content-editor-apps-in-chat-bar`
- `move-work-forward-from-chat-bar/see-work-in-chat-bar`
- `move-work-forward-from-chat-bar/steer-sessions`
- `move-work-forward-on-session-board/guide-work-through-practices-on-board`
- `move-work-forward-on-session-board/integrate-practice-content-editor-apps-on-board`
- `move-work-forward-on-session-board/maintain-tickets`
- `move-work-forward-on-session-board/organize-ticket-hierarchy`
- `move-work-forward-on-session-board/see-work-on-session-board`
- `move-work-forward-on-session-board/steer-ticket-sessions`
- `move-work-forward-on-session-board/work-fidelity-outputs-on-board`
- `space`
- `space/kanban`
- `space/repo`
- `space/session`

## Summary

**Total graph violations:** 17
**Rules with graph hits:** 6
**AI rules in scope:** 20

## Rules

Each rule shows its guidance text, any graph scanner hits (`**[graph rule]**`), then the AI judgment prompt.

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

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validate.py](C:\dev\abd-cdd-maintain-tickets-on-boar\cdd_guidance\actions\validate\validate.py#L42): Operation `validate`: Operation 'validate' is 21 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `prefer-instance-operations`

Keep operations on the instance. Do not annotate them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, `now` (a new value for this moment), and `every` (each value the class allows). A global accessor such as `current` or `shared` is not a factory: it hands every caller the same object from class-level state, so it stays an instance operation on the object that holds that state, or goes.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [harness/graph/pattern_overlays.py](C:\dev\abd-cdd-maintain-tickets-on-boar\harness\graph\pattern_overlays.py#L92): Operation `register`: Operation 'register' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/kanban/board.py](C:\dev\abd-cdd-maintain-tickets-on-boar\space\kanban\board.py#L117): Operation `places_cards`: Operation 'places_cards' is a classmethod; prefer an instance operation.

Evaluate the current context against this rule (prefer-instance-operations):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validate.py](C:\dev\abd-cdd-maintain-tickets-on-boar\cdd_guidance\actions\validate\validate.py#L42): Operation `validate`: Operation 'validate' mixes I/O-style calls with domain calculation; split responsibilities.

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

### `keep-classes-single-responsibility`

Give each class one reason to change.

**Graph violations:** 6

- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/board/board-client.tsx](C:\dev\abd-cdd-maintain-tickets-on-boar\space\kanban\app\src\kanban\board\board-client.tsx#L21): OoadClass `BoardClient`: Class 'BoardClient' exposes 10 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/open-card-client.ts](C:\dev\abd-cdd-maintain-tickets-on-boar\space\kanban\app\src\kanban\ticket\open-card-client.ts#L12): OoadClass `OpenCardClient`: Class 'OpenCardClient' exposes 10 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-client.tsx](C:\dev\abd-cdd-maintain-tickets-on-boar\space\kanban\app\src\kanban\ticket\ticket-client.tsx#L30): OoadClass `TicketClient`: Class 'TicketClient' exposes 30 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/kanban/backlog_item.py](C:\dev\abd-cdd-maintain-tickets-on-boar\space\kanban\backlog_item.py#L24): OoadClass `BacklogItem`: Class 'BacklogItem' exposes 10 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/kanban/board.py](C:\dev\abd-cdd-maintain-tickets-on-boar\space\kanban\board.py#L93): OoadClass `Board`: Class 'Board' exposes 25 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/kanban/ticket.py](C:\dev\abd-cdd-maintain-tickets-on-boar\space\kanban\ticket.py#L83): OoadClass `Ticket`: Class 'Ticket' exposes 23 public operations (budget ~9). Split responsibilities.

Evaluate the current context against this rule (keep-classes-single-responsibility):

### `limit-operation-parameters`

Have callers pass intent, not setup. A parameter that carries state the object already holds fails `hold-state-on-the-object-not-in-parameters` even when the count is small. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. Count each value a caller supplies: a packed tuple, `*args`, or `**kwargs` that carries four values counts as four parameters, because packing them hides the same setup instead of removing it. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validate.py](C:\dev\abd-cdd-maintain-tickets-on-boar\cdd_guidance\actions\validate\validate.py#L42): Operation `validate`: Operation 'validate' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [space/kanban/board.py](C:\dev\abd-cdd-maintain-tickets-on-boar\space\kanban\board.py#L326): Operation `open_ticket`: Operation 'open_ticket' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [space/kanban/board.py](C:\dev\abd-cdd-maintain-tickets-on-boar\space\kanban\board.py#L645): Operation `__init__`: Operation '__init__' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [space/kanban/ticket.py](C:\dev\abd-cdd-maintain-tickets-on-boar\space\kanban\ticket.py#L705): Operation `__init__`: Operation '__init__' takes 5 parameters (maximum 3, excluding self).

Evaluate the current context against this rule (limit-operation-parameters):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [harness/graph/pattern_overlays.py](C:\dev\abd-cdd-maintain-tickets-on-boar\harness\graph\pattern_overlays.py#L33): Parameter `pattern`: Parameter 'pattern' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/graph/pattern_overlays.py](C:\dev\abd-cdd-maintain-tickets-on-boar\harness\graph\pattern_overlays.py#L75): Parameter `practice`: Parameter 'practice' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/graph/pattern_overlays.py](C:\dev\abd-cdd-maintain-tickets-on-boar\harness\graph\pattern_overlays.py#L139): Parameter `practice`: Parameter 'practice' needs a domain-specific type, not a generic container.

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

- Edit Ticket Text
- Reorder Tickets In Column
- Tag Ticket Session
- Delete Ticket
- Expand Ticket From Empty Area
- Add Child Ticket
- Display Child Tickets In Parent
- Expand Parent Ticket
- Detach Child Ticket
- Reassign Ticket Parent
- Place Parent At Leftmost Child Stage
## Judgment — `space/kanban/app/src/kanban/ticket/open-card-client.ts`

Down from 30 graph findings to 17. Fixed since the last run: `CardFaceView` and `OpenCardView` lengths, `isSelected`, the `item` parameters, `_content_root` and the walk to `.context` (one owner, `PatternsFile.for_content`), `record_content`, `_story_sections` nesting, `_story_heading` and `_story_key` as instance operations, and the LERN story rules' types. The rest stand as Fails:

### `keep-classes-single-responsibility` — Fail
- open-card-client.ts:12 `OpenCardClient`: 10 public operations, one over budget, since `open` was added for Expand Ticket From Empty Area.
- board-client.tsx:21 `BoardClient`: 10 public operations since `ticketAt` replaced three copies of the same lookup.
- backlog_item.py:24 `BacklogItem`: 10 public operations since `start_under`.
- ticket-client.tsx:30 `TicketClient`: 30 public operations; long-standing.
- board.py:93 `Board` (25) and ticket.py:83 `Ticket` (23): long-standing; Ticket's size is the decision in cdr 0004.

### `keep-operations-small-focused` — Fail
- validate.py:42 `validate`: 21 lines, of which the docstring is most: it is the MCP tool's published description. The body is four lines.

### `limit-operation-parameters` — Fail
- validate.py:42 `validate`: four parameters, which are the MCP tool's public contract (guidance, rule, graph, paths).
- board.py:326 `open_ticket`, board.py:645 `Board.__init__`, ticket.py:705 `Ticket.__init__`: long-standing.

### `keep-operations-single-responsibility` — Fail
- validate.py:42 `validate`: the scanner still reads saving the report beside composing it; the composing is in `_report`, the I/O in `_check` and `ReportFiles.save`.

### `prefer-instance-operations` — Fail
- pattern_overlays.py:92 `register` and board.py:117 `places_cards`: long-standing classmethods.

### `use-typed-signatures` — Fail
- pattern_overlays.py:33, :75, :139: `pattern` and `practice` typed `Any`, because harness/graph may not import the guidance classes that patterns and practices are; long-standing.

Passes: every other practice rule. LERN and cdd_web_domain_access rules for the board files pass: the page reaches Python only through the generated adapters (`TicketClient` and `BacklogItemClient` subclass the generated clients and refresh through `onChanged`), views render clients, every decision about a drop (`parentChoices`, `dropTargets`) is Python's, and no state is copied beside a client (`foldedParents` is page-only display state). LERN's node, route, store and lowdb rules do not apply: this board's domain is Python behind MCP.
