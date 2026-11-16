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


Judge the graph validate built from the checked format's files (python: C:/dev/abd-cdd-version-1-refactoring/{module}/), saved at C:\dev\abd-context-driven-delivery\.sessions\version-1-refactoring\.context\graph.json: its classes, operations, parameters, properties, relationships, and dependencies, against each rule. Read a file only to see what a node stands for; whether a model document matches the code is a separate, secondary check.

# Graph rule validation

**Generated:** 2026-11-16 18:21:46 UTC
**Project:** abd-cdd-version-1-refactoring
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-context-driven-delivery\.sessions\version-1-refactoring\.context\graph.json`

## Summary

**Total graph violations:** 31
**Rules with graph hits:** 11
**AI rules in scope:** 24

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

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/lern_domain_driven/graph_overlay.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\lern_domain_driven\graph_overlay.py#L46): OoadClass `_LernReading`: Class '_LernReading' copies the fields ['graph', 'overlay', 'root'] of '_OssReading'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [space/repo/mock_repo.py](C:\dev\abd-cdd-version-1-refactoring\space\repo\mock_repo.py#L69): OoadClass `HeldBranches`: Class 'HeldBranches' copies the fields ['_held', 'logs', 'trees'] of 'HeldOrigin'. Use one canonical model type.

Evaluate the current context against this rule (do-not-invent-parallel-object-models):

### `hide-inner-details`

Expose behavior through named operations. Do not let callers see how the class stores or arranges its data — once they read the storage directly it becomes a public contract you cannot change. Private fields on the same class hide implementation; you do not need a second class for that. Read-only to callers can mean return a copy or immutable view from a property — it does not require a frozen class or a second type to hold build steps.

Evaluate the current context against this rule (hide-inner-details):

### `hold-state-on-the-object-not-in-parameters`

Keep what an object knows on the object, and let its operations read it there. A session holds its practices, a practice holds its fidelities and its current fidelity, a fidelity holds its actions and the format it last used, and an action is made for its session: `session.practices.stories.fidelities.story_map.actions.generate(format="drawio")`, not `Generate.commands_for(session, fidelities, formats)`. A value the caller supplies once, such as a format, is saved on the object that owns it, so the next operation on that object reads it instead of being handed it again. The rule fails when an operation takes, as a parameter, state its own object holds or should hold: the same argument handed down through several layers; a session, guidance, or ticket passed to every call on an object made for it; a name or slug passed so the receiver can look up an object the caller already holds; state written into a string (`session=...`) and parsed back; or a field set on a shared object for one call and restored afterwards. Every layer that passes the value is another place to pass the wrong one, and a call started from inside another, which nobody hands the value to, falls back to a global such as the current session and acts on the wrong object.

Evaluate the current context against this rule (hold-state-on-the-object-not-in-parameters):

### `keep-operations-small-focused`

Keep each operation short enough to read as one thought — under 20 statements. A multi-line call, list, or string initializer is one statement. When it grows, extract a private helper whose name says why that slice exists.

Evaluate the current context against this rule (keep-operations-small-focused):

### `prefer-instance-operations`

Keep operations on the instance. Do not annotate them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, `now` (a new value for this moment), and `every` (each value the class allows). A global accessor such as `current` or `shared` is not a factory: it hands every caller the same object from class-level state, so it stays an instance operation on the object that holds that state, or goes.

Evaluate the current context against this rule (prefer-instance-operations):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

Evaluate the current context against this rule (keep-operations-single-responsibility):

### `simplify-control-flow`

Handle the failing or empty cases first and return. Keep the main path flat. Do not nest more than three levels — deeper than that you cannot tell which conditions hold on a given line without reading back up, and that is where the unhandled branch hides.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\tier_facts.py#L194): Operation `_brace_end`: Operation '_brace_end' nests control flow 4 levels deep (max 3).

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

**Graph violations:** 9

- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/graph_overlay.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\graph_overlay.py#L62): Operation `__init__`: Operation '__init__' duplicates the body of '__init__'.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L79): Operation `check`: Operation 'check' nearly duplicates 'check' (cdd_guidance/patterns/lern_domain_driven/practices/ddd/rules/lern_tier_rules.py): 82% of their code is the same. Give the shared logic one function.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\tier_facts.py#L136): Operation `web_path_literals`: Operation 'web_path_literals' nearly duplicates 'web_path_literals' (cdd_guidance/patterns/lern_domain_driven/tier_facts.py): 76% of their code is the same. Give the shared logic one function.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\tier_facts.py#L205): Operation `_in_import`: Operation '_in_import' nearly duplicates '_in_import' (cdd_guidance/patterns/lern_domain_driven/tier_facts.py): 73% of their code is the same. Give the shared logic one function.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\tier_facts.py#L211): Operation `_in_comment`: Operation '_in_comment' nearly duplicates '_in_comment' (cdd_guidance/patterns/lern_domain_driven/tier_facts.py): 75% of their code is the same. Give the shared logic one function.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\tier_facts.py#L283): Operation `__init__`: Operation '__init__' duplicates the body of '__init__'.
- [X] **ERROR** **[graph rule]** - [space/repo/mock_repo.py](C:\dev\abd-cdd-version-1-refactoring\space\repo\mock_repo.py#L73): Operation `__init__`: Operation '__init__' nearly duplicates '__init__' (space/repo/mock_repo.py): 78% of their code is the same. Give the shared logic one function.
- [X] **ERROR** **[graph rule]** - [space/repo/mock_repo.py](C:\dev\abd-cdd-version-1-refactoring\space\repo\mock_repo.py#L282): Operation `__init__`: Operation '__init__' duplicates the body of '__init__'.
- [X] **ERROR** **[graph rule]** - [space/session/practice_session_output.py](C:\dev\abd-cdd-version-1-refactoring\space\session\practice_session_output.py#L559): Operation `__init__`: Operation '__init__' duplicates the body of '__init__'.

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

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/installation/language_adapter.py](C:\dev\abd-cdd-version-1-refactoring\harness\installation\language_adapter.py#L522): Operation `_base_state_changes`: Operation '_base_state_changes' has a descriptive comment.

Evaluate the current context against this rule (limit-comments):

### `source-parses`

Keep every source file valid in its language. A file that does not parse is read into no classes, so every other rule passes it without looking, and its problems stay hidden until it runs.

Evaluate the current context against this rule (source-parses):

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

### `deep-module`

Keep most classes private (at most **40%** public) in each first-class module. A first-class module is a folder that owns `.context/module-context.md`. Nested folders that also own that file are separate modules — respect them. Nested folders that do not own it roll up to the nearest enclosing module-context folder, or to the folder you are querying if none sits in between. Count classes, not operations: a public method on a hidden class is not a second seam. A class is public when another module's production code names it; a class named only inside its own module, or only by specs, is private. Modules with fewer than 3 classes are not measured, because one public class out of two is the whole seam, not a shallow module. Every public class is a signature you cannot change without editing every caller, so public classes are much harder to refactor than private ones.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/process](C:\dev\abd-cdd-version-1-refactoring\harness\process#L1): Module `process`: Module 'process' exposes 9 of 12 classes to other modules, more than the 4 that 40% allows: BackgroundStart, ClaudeChatProcess, ExclusivePort, Git, GitHubCli, ProcessNotStopped, PythonInterpreter, RepoConnectError, RunningProcess. Keep most classes behind a few public ones.

Evaluate the current context against this rule (deep-module):

### `keep-classes-single-responsibility`

Give each class one reason to change.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\dev\abd-cdd-version-1-refactoring\harness\graph\graph.py#L1380): OoadClass `Graph`: Class 'Graph' exposes 18 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/whiteboard/whiteboard.py](C:\dev\abd-cdd-version-1-refactoring\harness\whiteboard\whiteboard.py#L299): OoadClass `Whiteboard`: Class 'Whiteboard' exposes 10 public operations (budget ~9). Split responsibilities.

Evaluate the current context against this rule (keep-classes-single-responsibility):

### `layer-separation`

keep dependent modules at different levels of abstractions. Collapse pass-through modules — a module that only forwards turns every signature change into an edit in three files instead of one.

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [space/kanban/ticket.py](C:\dev\abd-cdd-version-1-refactoring\space\kanban\ticket.py#L136): OoadClass `TicketChoiceTools`: Class 'TicketChoiceTools' only forwards to 'TicketChoices'; merge the layers or give it real behavior.
- [X] **ERROR** **[graph rule]** - [space/kanban/ticket.py](C:\dev\abd-cdd-version-1-refactoring\space\kanban\ticket.py#L223): OoadClass `TicketTreeTools`: Class 'TicketTreeTools' only forwards to 'TicketTree'; merge the layers or give it real behavior.
- [X] **ERROR** **[graph rule]** - [space/kanban/ticket.py](C:\dev\abd-cdd-version-1-refactoring\space\kanban\ticket.py#L252): OoadClass `TicketEndingTools`: Class 'TicketEndingTools' only forwards to 'TicketEnding'; merge the layers or give it real behavior.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\dev\abd-cdd-version-1-refactoring\space\session\session.py#L133): OoadClass `SessionGraphTools`: Class 'SessionGraphTools' only forwards to 'SessionExplorer'; merge the layers or give it real behavior.

Evaluate the current context against this rule (layer-separation):

### `limit-operation-parameters`

Have callers pass intent, not setup. A parameter that carries state the object already holds fails `hold-state-on-the-object-not-in-parameters` even when the count is small. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. Count each value a caller supplies: a packed tuple, `*args`, or `**kwargs` that carries four values counts as four parameters, because packing them hides the same setup instead of removing it. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object. An operation published as an MCP tool (`@mcp` or `@agent_tool` in Python) is exempt too, because its parameters are the tool's published argument schema, which its callers fill by name.

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/graph_overlay.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\graph_overlay.py#L140): Operation `_tier_facts`: Operation '_tier_facts' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/graph_overlay.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\graph_overlay.py#L195): Operation `_file_node`: Operation '_file_node' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/session-board/http-exception.ts](C:\dev\abd-cdd-version-1-refactoring\space\kanban\app\src\session-board\http-exception.ts#L32): Operation `answerFailure`: Operation 'answerFailure' takes 4 parameters (maximum 3, excluding self).

Evaluate the current context against this rule (limit-operation-parameters):

### `shape-classes-around-resources`

Model a class around the concept that owns the state and the rule, not a doer, handler, or service that acts on a data bag. A Payment has transactions, a source, and a destination, and it moves the money; it is not a `PaymentService` that takes a `PaymentData` object. A service-plus-bag pair splits the rule from its memory, so every change has to be found in two types and the bag cannot enforce anything. Two resources may collaborate — a model that loads a Module is not a service-plus-bag split.

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/open-card-client.ts](C:\dev\abd-cdd-version-1-refactoring\space\kanban\app\src\kanban\ticket\open-card-client.ts#L12): OoadClass `OpenCardClient`: Class 'OpenCardClient' acts on the data bag 'RequiredFidelity', which holds the state but no behavior; put the behavior on the resource that owns the data.
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/report-client.ts](C:\dev\abd-cdd-version-1-refactoring\space\kanban\app\src\kanban\ticket\report-client.ts#L45): OoadClass `ReportClient`: Class 'ReportClient' acts on the data bag 'ViolationData', which holds the state but no behavior; put the behavior on the resource that owns the data.
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-work.ts](C:\dev\abd-cdd-version-1-refactoring\space\kanban\app\src\kanban\ticket\ticket-work.ts#L17): OoadClass `TicketWork`: Class 'TicketWork' acts on the data bag 'RequiredFidelity', which holds the state but no behavior; put the behavior on the resource that owns the data.

Evaluate the current context against this rule (shape-classes-around-resources):

### `state-change-returns-record-or-named-failure`

When an operation coordinates a state change that cannot be one property assignment, return the resulting record or a failure named after the rejected rule. Decide at code fidelity whether that failure is a result type or domain exception, because callers need one explicit outcome contract.

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [cdd_guidance/catalog/commons/catalog-approach.js](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\catalog\commons\catalog-approach.js#L79): Operation `ApproachPage`: Operation 'ApproachPage' mutates state but does not return the record or a named failure.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/catalog/commons/catalog-drawio.js](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\catalog\commons\catalog-drawio.js#L87): Operation `StoryMapZoom`: Operation 'StoryMapZoom' mutates state but does not return the record or a named failure.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/catalog/commons/catalog-foundry-tour.js](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\catalog\commons\catalog-foundry-tour.js#L196): Operation `FloatingTooltips`: Operation 'FloatingTooltips' mutates state but does not return the record or a named failure.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/catalog/commons/catalog-nav.js](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\catalog\commons\catalog-nav.js#L255): Operation `NavDrawer`: Operation 'NavDrawer' mutates state but does not return the record or a named failure.

Evaluate the current context against this rule (state-change-returns-record-or-named-failure):

### `use-explicit-dependencies`

Pass every collaborator through the constructor. Do not reach for a global or construct a collaborator inside construction. A collaborator the class fetches or builds itself cannot be swapped, so the class can only ever run against that one implementation. A part the class builds once from nothing outside itself and keeps, such as an index of its own nodes, is not a collaborator: nothing a caller could hand it differs from it. A repository, service, client, file, or other external system is, and always comes in through the constructor.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/story-demo/mount-generated-mockup.js](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\practices\ux\story-demo\mount-generated-mockup.js#L527): OoadClass `GeneratedMockup`: Class 'GeneratedMockup' constructs 'WeakSet' inside its constructor.

Evaluate the current context against this rule (use-explicit-dependencies):
