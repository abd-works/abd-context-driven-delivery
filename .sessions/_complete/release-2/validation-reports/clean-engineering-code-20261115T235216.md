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


Judge the graph validate built from the checked format's files (python: space/session/files_app/app/files/files-page.ts, space/session/files_app/app/files/file-menu.ts, space/session/files_app/app/files/chat-context.ts, space/session/files_app/app/files/files-notices.ts, space/session/files_app/app/files/files-page-view.tsx, space/session/files_app/app/files/file-comments-actions.ts, space/session/files_app/app/main.tsx), saved at C:\dev\abd-context-driven-delivery\.sessions\release-2\validation-reports\clean-engineering-code-20261115T235216.json: its classes, operations, parameters, properties, relationships, and dependencies, against each rule. Read a file only to see what a node stands for; whether a model document matches the code is a separate, secondary check.

# Graph rule validation

**Generated:** 2026-11-15 23:52:35 UTC
**Project:** abd-cdd-2
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-context-driven-delivery\.sessions\release-2\validation-reports\clean-engineering-code-20261115T235216.json`

**The session's graph also held, and practice-wide rules compared against:**
- `.`
- `.context`
- `cdd_guidance`
- `cdd_guidance/actions`
- `cdd_guidance/builders`
- `cdd_guidance/catalog`
- `cdd_guidance/context_setup`
- `cdd_guidance/patterns`
- `cdd_guidance/practices`
- `harness`
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
- `scripts`
- `scripts/unit_guard`
- `space`
- `space/kanban`
- `space/repo`
- `space/session`
- `tools`
- `tools/drawio_viewer`
- `tools/echo`
- `tools/error_display`
- `tools/granola`
- `tools/prompt_log`
- `tools/prompt_notify`
- `tools/sub_agent`

## Summary

**Total graph violations:** 9
**Rules with graph hits:** 7
**AI rules in scope:** 43

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

- [X] **ERROR** **[graph rule]** - [space/session/files_app/app/files/files-page-view.tsx](C:\dev\abd-cdd-2\space\session\files_app\app\files\files-page-view.tsx#L371): Operation `FilesPageView`: Operation 'FilesPageView' is 27 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `prefer-instance-operations`

Keep operations on the instance. Do not annotate them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, `now` (a new value for this moment), and `every` (each value the class allows). A global accessor such as `current` or `shared` is not a factory: it hands every caller the same object from class-level state, so it stays an instance operation on the object that holds that state, or goes.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [space/session/files_app/app/files/files-page-view.tsx](C:\dev\abd-cdd-2\space\session\files_app\app\files\files-page-view.tsx#L405): Operation `getDerivedStateFromError`: Operation 'getDerivedStateFromError' is a staticmethod; prefer an instance operation.

Evaluate the current context against this rule (prefer-instance-operations):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [space/session/files_app/app/files/files-page-view.tsx](C:\dev\abd-cdd-2\space\session\files_app\app\files\files-page-view.tsx#L355): Operation `ThemeToggleView`: Operation 'ThemeToggleView' mixes I/O-style calls with domain calculation; split responsibilities.

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

- [X] **ERROR** **[graph rule]** - [space/session/files_app/app/files/file-menu.ts](C:\dev\abd-cdd-2\space\session\files_app\app\files\file-menu.ts#L20): Parameter `x`: Parameter 'x' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [space/session/files_app/app/files/file-menu.ts](C:\dev\abd-cdd-2\space\session\files_app\app\files\file-menu.ts#L20): Parameter `y`: Parameter 'y' does not reveal intent.

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

The whole unit tier finishes in under 25 s of wall clock on an idle machine, because it runs after every pass, and a slow unit tier stops being run.

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

### `operation-has-a-proving-test`

Every public operation is invoked by at least one observation or step.

Evaluate the current context against this rule (operation-has-a-proving-test):

### `class-demonstrated-by-a-test`

Every public class is demonstrated through an example or observation.

Evaluate the current context against this rule (class-demonstrated-by-a-test):

### `invariant-has-a-failing-case`

Every invariant has a test that tries to break it and sees the named failure.

Evaluate the current context against this rule (invariant-has-a-failing-case):

### `every-branch-taken-by-a-test`

Every branch in a public operation's body is taken by some test.

Evaluate the current context against this rule (every-branch-taken-by-a-test):

### `keep-classes-single-responsibility`

Give each class one reason to change.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [space/session/files_app/app/files/files-page.ts](C:\dev\abd-cdd-2\space\session\files_app\app\files\files-page.ts#L51): OoadClass `FilesPage`: Class 'FilesPage' exposes 13 public operations (budget ~9). Split responsibilities.

Evaluate the current context against this rule (keep-classes-single-responsibility):

### `limit-operation-parameters`

Have callers pass intent, not setup. A parameter that carries state the object already holds fails `hold-state-on-the-object-not-in-parameters` even when the count is small. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. Count each value a caller supplies: a packed tuple, `*args`, or `**kwargs` that carries four values counts as four parameters, because packing them hides the same setup instead of removing it. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [space/session/files_app/app/files/file-menu.ts](C:\dev\abd-cdd-2\space\session\files_app\app\files\file-menu.ts#L13): Operation `constructor`: Operation 'constructor' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [space/session/files_app/app/files/files-page.ts](C:\dev\abd-cdd-2\space\session\files_app\app\files\files-page.ts#L40): Operation `rootFilesShown`: Operation 'rootFilesShown' takes 4 parameters (maximum 3, excluding self).

Evaluate the current context against this rule (limit-operation-parameters):

### `use-explicit-dependencies`

Pass every collaborator through the constructor. Do not reach for a global or construct a collaborator inside construction. A collaborator the class fetches or builds itself cannot be swapped, so the class can only ever run against that one implementation.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [space/session/files_app/app/files/files-page.ts](C:\dev\abd-cdd-2\space\session\files_app\app\files\files-page.ts#L51): OoadClass `FilesPage`: Class 'FilesPage' constructs 'GuidanceSelector' inside its constructor.

Evaluate the current context against this rule (use-explicit-dependencies):


Judge the work against these overlaid patterns' rules too, as you judge the practices' rules.

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