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


Judge the graph validate built from the checked format's files (python: space/kanban/.context/kanban-model.md), saved at C:\dev\abd-context-driven-delivery\.sessions\maintain-tickets-on-board\validation-reports\clean-engineering-model-20261112T050132.json: its classes, operations, parameters, properties, relationships, and dependencies, against each rule. Read a file only to see what a node stands for; whether a model document matches the code is a separate, secondary check.

# Graph rule validation

**Generated:** 2026-11-12 05:01:36 UTC
**Project:** abd-cdd-maintain-tickets-on-boar
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-context-driven-delivery\.sessions\maintain-tickets-on-board\validation-reports\clean-engineering-model-20261112T050132.json`

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

**No graph rule violations.** All scanned graph rules passed.
**AI rules in scope:** 28

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

### `model-modules-follow-the-partition`

Use the module names and boundaries established by the partition artifact as the model's top-level modules. Change the partition before moving a model boundary, because otherwise the two artifacts describe different designs.

Evaluate the current context against this rule (model-modules-follow-the-partition):

### `class-not-property-instance-or-subtype`

Before you write a new class, check property, instance, then subtype. Write a class only when none of those three fit. Multi-step work inside one operation usually belongs in private fields on the class that owns the operation, not in another class. Every new class is another type to construct, pass around, and keep in step with the rest; a property or subtype reuses one that already works.

Evaluate the current context against this rule (class-not-property-instance-or-subtype):

### `keep-classes-single-responsibility`

Give each class one reason to change.

Evaluate the current context against this rule (keep-classes-single-responsibility):

### `shape-classes-around-resources`

Model a class around the concept that owns the state and the rule, not a doer, handler, or service that acts on a data bag. A Payment has transactions, a source, and a destination, and it moves the money; it is not a `PaymentService` that takes a `PaymentData` object. A service-plus-bag pair splits the rule from its memory, so every change has to be found in two types and the bag cannot enforce anything. Two resources may collaborate — a model that loads a Module is not a service-plus-bag split.

Evaluate the current context against this rule (shape-classes-around-resources):

### `put-logic-on-the-owning-resource`

Put logic on the object that owns the invariant. Do not infer ownership from a route name, Story actor, or Given subject: `client.accounts[id].transactions.last.validate()`, not `client.validateLastTransactionForPrimaryAccount()`. Logic placed away from its state gives two objects authority to change the same rule.

Evaluate the current context against this rule (put-logic-on-the-owning-resource):

### `hide-inner-details`

Expose behavior through named operations. Do not let callers see how the class stores or arranges its data — once they read the storage directly it becomes a public contract you cannot change. Private fields on the same class hide implementation; you do not need a second class for that.

Evaluate the current context against this rule (hide-inner-details):

### `use-property-not-accessor`

Use a named property for stored or derived state. A derived property recalculates from state and collaborators the object already holds, takes no owner or state parameters, and looks like a field to callers through the language's property mechanism. Use an operation only when behavior coordinates several values, collaborators, or lifecycle steps and cannot be represented truthfully as a property. Callers should not need `getX`, `setX`, or storage knowledge. Read-only to callers can mean return a copy or immutable view from a property — it does not require a frozen class or a second type to hold build steps.

Evaluate the current context against this rule (use-property-not-accessor):

### `prefer-class-operations`

Put factory, lifecycle, and helpers used from one class on that class. Do not export them as module-level functions — a free function holds no state, so it takes the object as a parameter and reaches into it to do the work. A file of hanging functions is the same miss: those operations belong on a type, not on the package.

Evaluate the current context against this rule (prefer-class-operations):

### `use-explicit-dependencies`

Pass every collaborator through the constructor. Do not reach for a global or construct a collaborator inside construction. A collaborator the class fetches or builds itself cannot be swapped, so the class can only ever run against that one implementation.

Evaluate the current context against this rule (use-explicit-dependencies):

### `external-system-interface-is-one-way`

Let a domain wrapper or collaborator depend on the named external-system contract. Keep the external type independent of domain wrappers and domain types, because a reverse dependency makes the external boundary depend on one caller's model.

Evaluate the current context against this rule (external-system-interface-is-one-way):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

Evaluate the current context against this rule (keep-operations-single-responsibility):

### `limit-operation-parameters`

Have callers pass intent, not setup. A parameter that carries state the object already holds fails `hold-state-on-the-object-not-in-parameters` even when the count is small. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. Count each value a caller supplies: a packed tuple, `*args`, or `**kwargs` that carries four values counts as four parameters, because packing them hides the same setup instead of removing it. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

Evaluate the current context against this rule (limit-operation-parameters):

### `hold-state-on-the-object-not-in-parameters`

Keep what an object knows on the object, and let its operations read it there. A session holds its practices, a practice holds its fidelities and its current fidelity, a fidelity holds its actions and the format it last used, and an action is made for its session: `session.practices.stories.fidelities.story_map.actions.generate(format="drawio")`, not `Generate.commands_for(session, fidelities, formats)`. A value the caller supplies once, such as a format, is saved on the object that owns it, so the next operation on that object reads it instead of being handed it again. The rule fails when an operation takes, as a parameter, state its own object holds or should hold: the same argument handed down through several layers; a session, guidance, or ticket passed to every call on an object made for it; a name or slug passed so the receiver can look up an object the caller already holds; state written into a string (`session=...`) and parsed back; or a field set on a shared object for one call and restored afterwards. Every layer that passes the value is another place to pass the wrong one, and a call started from inside another, which nobody hands the value to, falls back to a global such as the current session and acts on the wrong object.

Evaluate the current context against this rule (hold-state-on-the-object-not-in-parameters):

### `avoid-vague-parameter-names`

Do not name parameters `data`, `options`, `info`, or other placeholders that could mean anything. A vague name hides what the caller must supply and what the operation does with it.

Evaluate the current context against this rule (avoid-vague-parameter-names):

### `errors-out-of-existence`

For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure. A missing required argument is a broken call, not an ordinary edge: refuse it with a failure the program declares and names (`CommitPathsRequiredError`), which `domain-exception-carries-context` then asks to carry the rejected value.

Evaluate the current context against this rule (errors-out-of-existence):

### `state-change-returns-record-or-named-failure`

When an operation coordinates a state change that cannot be one property assignment, return the resulting record or a failure named after the rejected rule. Decide at code fidelity whether that failure is a result type or domain exception, because callers need one explicit outcome contract.

Evaluate the current context against this rule (state-change-returns-record-or-named-failure):

### `domain-exception-carries-context`

Use a typed exception for a broken aggregate or repository operation. One exception type may cover that aggregate's operations when it carries the failed operation, the domain object or input already in hand, the user-facing message, and the underlying cause; do not return bare strings or untyped error objects because callers cannot handle them safely..

Evaluate the current context against this rule (domain-exception-carries-context):

### `limit-comments`

write comment in operations and properties only when the signature cannot say a constraint or explain why the code behaves the way it does. Do not narrate a line that already names what it does.

Evaluate the current context against this rule (limit-comments):

### `write-invariants`

Name a rule the object itself must keep true whenever it acts — a must, never, always, before, or after about its own state. Write one a caller can break by using the object wrong. Do not restate a type, a name, or a single operation’s happy path.

Evaluate the current context against this rule (write-invariants):

### `write-interactions`

Collaborate when this object cannot finish its job from its own state — another object owns the data or the next act. Ask that object to do the work so each keeps its own invariants; do not reach into its internals or steal its job. Ask through a named public operation on a collaborator you hold or are given. Do not point at a type, and do not invent a third object to mediate a conversation two objects can have.

Evaluate the current context against this rule (write-interactions):

### `no-redundant-relationship-paths`

Before you add an association, walk the paths already in the cluster. Each real participant gets one canonical link — not parallel wires through types that collapse to the same thing (`Client` and `ClientIdentity`, or `OfferChannel` on **Offer** and again on an event the offer just emitted). In-process payloads reach a participant through the aggregate that owns the act; outbound events carry the identity or routing fact downstream systems need, not a duplicate of context the publisher already holds.

Evaluate the current context against this rule (no-redundant-relationship-paths):

### `use-intention-revealing-names`

Name each class, property, operation, and parameter so it answers why it exists. Do not abbreviate.

Evaluate the current context against this rule (use-intention-revealing-names):

### `use-consistent-naming`

Use one word per concept. Pick one verb and use it everywhere (`fetch_`, not a mix of `fetch_`, `get_`, and `retrieve_`). Two words for one concept is how the same logic gets written twice — nobody searching for `fetch_` finds the `retrieve_` that already does the job.

Evaluate the current context against this rule (use-consistent-naming):

### `eliminate-duplication`

Give repeated logic one canonical function. Every copy is another place the fix has to be repeated, and the copy you miss is the bug.

Evaluate the current context against this rule (eliminate-duplication):

### `one-canonical-model-document`

Keep all modules for one model artifact in one canonical model document. Link diagrams and code to it rather than restating its classes in another design document, because parallel models become inconsistent.

Evaluate the current context against this rule (one-canonical-model-document):


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
- **`playwright-tests-browser-interaction`** — Playwright tests interaction the domain spec and the server spec cannot see: a rendered screen, navigation, and controls the user operates in the browser. The file is optional. It states its own screen story. It leaves the shared story to the domain spec and the server spec.
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
## Judgment — `space/kanban/.context/kanban-model.md`

Passes every rule. The graph found nothing. The three gaps from the last run are closed: `Ticket.parent_choices`, `BacklogItem.start_under(parent)`, and `Board.sends_fixes_directly` with `set_sends_fixes_directly(sends)` are in the model and in `kanban-model.drawio`, matching `ticket.py`, `backlog_item.py` and `board.py`. Ticket's size stays as decided (cdr 0004).
