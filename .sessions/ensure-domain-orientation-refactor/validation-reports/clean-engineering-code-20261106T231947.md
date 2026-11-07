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


Judge only the checked format's files (python: C:/Users/jeffa/.cdd/runtime-ensure-domain-orientatio/{module}/). The other formats mirror them, so judging those too reports every finding twice.

# Graph rule validation

**Generated:** 2026-11-06 23:19:47 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 81
**Rules with graph hits:** 11
**AI rules in scope:** 18

## Rules

Each rule shows its guidance text, any graph scanner hits (`**[graph rule]**`), then the AI judgment prompt.

### `vocabulary-traces-to-source`

Take every term from the source. The English term and the code name are the same word: *shopping cart* is `ShoppingCart`. When the code says a different word than the domain, every reader keeps a translation in their head, and the two names drift until they mean different things.

Evaluate the current context against this rule (vocabulary-traces-to-source):

### `do-not-invent-terms`

Do not invent a second noun or a parallel vocabulary. A second noun for the same thing becomes a second class, and then the same rule has to be written and fixed in both.

Evaluate the current context against this rule (do-not-invent-terms):

### `do-not-invent-parallel-object-models`

Keep one object model. Follow the nouns and verbs the rest of the graph already uses for that concept. A class that joins types the rest of the graph keeps apart is a second model — a big ball of mud — and every rule then has to be written and fixed in both. When data or behavior already belongs to an object, extend that object and hand callers the object itself: `ticket.session.practices["stories"].fidelities["story_map"].files()`, not `ticket.files(["stories-story_map"])`. A second model is rarely a whole class family; more often it is a small copy beside the owner: a dict holding one field from each member (`fidelity_states`, `violation_counts`), a `*_name` copy of a reference (`column_name`), a helper class that does the owner's job (`TicketFiles`), a bag of a few of the owner's answers (`Workspace`), or a `*Model` / `*Entry` family scraped from live objects. A copy hides that the owner is missing the behavior, so the next caller builds another copy and a fix to the owner never reaches it. **Checking it:** this rule spans modules, and the copy looks fine in the file that holds it. For every property, data field, dict, and helper class the changed code adds, name the class that already owns that data and read it; the rule fails when the owner holds it or should, and the change copies it instead of returning or extending the owner. Count the members of a class that delegates: dozens of members on a class that only reads its collaborators means it is copying them.

Evaluate the current context against this rule (do-not-invent-parallel-object-models):

### `hide-inner-details`

Expose behavior through named operations. Do not let callers see how the class stores or arranges its data — once they read the storage directly it becomes a public contract you cannot change. Private fields on the same class hide implementation; you do not need a second class for that. Read-only to callers can mean return a copy or immutable view from a property — it does not require a frozen class or a second type to hold build steps.

Evaluate the current context against this rule (hide-inner-details):

### `keep-operations-small-focused`

Keep each operation short enough to read as one thought — under 20 statements. A multi-line call, list, or string initializer is one statement. When it grows, extract a private helper whose name says why that slice exists.

**Graph violations:** 7

- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/board/board-columns-view.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\board\board-columns-view.tsx#L87): Operation `DropZoneView`: Operation 'DropZoneView' is 29 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/ticket/details-view.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\ticket\details-view.tsx#L27): Operation `TicketBarView`: Operation 'TicketBarView' is 36 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/ticket/root-choice-view.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\ticket\root-choice-view.tsx#L35): Operation `RootsListView`: Operation 'RootsListView' is 26 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/ticket/root-choice-view.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\ticket\root-choice-view.tsx#L64): Operation `FolderBrowserView`: Operation 'FolderBrowserView' is 31 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/ticket/ticket-card-view.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\ticket\ticket-card-view.tsx#L63): Operation `CardFaceView`: Operation 'CardFaceView' is 24 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/ticket/ticket-card-view.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\ticket\ticket-card-view.tsx#L148): Operation `OpenCardView`: Operation 'OpenCardView' is 21 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/ticket/ticket-card-view.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\ticket\ticket-card-view.tsx#L174): Operation `TicketCardView`: Operation 'TicketCardView' is 29 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

**Graph violations:** 5

- [X] **ERROR** **[graph rule]** - [harness/kanban/app/test-utils/behavior-test/throwaway-cdd-home.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\test-utils\behavior-test\throwaway-cdd-home.ts#L31): Operation `install`: Operation 'install' is a staticmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/test-utils/behavior-test/throwaway-cdd-home.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\test-utils\behavior-test\throwaway-cdd-home.ts#L40): Operation `forRun`: Operation 'forRun' is a staticmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/test-utils/behavior-test/throwaway-cdd-home.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\test-utils\behavior-test\throwaway-cdd-home.ts#L44): Operation `ofRun`: Operation 'ofRun' is a staticmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/test-utils/board-page-support.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\test-utils\board-page-support.ts#L82): Operation `on`: Operation 'on' is a staticmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/test-utils/board-page-support.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\test-utils\board-page-support.ts#L173): Operation `start`: Operation 'start' is a staticmethod; prefer an instance operation.

Evaluate the current context against this rule (prefer-instance-operations):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/board/board-store.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\board\board-store.ts#L126): Operation `savedLayout`: Operation 'savedLayout' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/ticket/action-bar-view.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\ticket\action-bar-view.tsx#L64): Operation `ValidateLineView`: Operation 'ValidateLineView' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/ticket/tile-actions-client.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\ticket\tile-actions-client.ts#L117): Operation `validate`: Operation 'validate' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/test-utils/fixture-repo.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\test-utils\fixture-repo.ts#L49): Operation `writeSessions`: Operation 'writeSessions' mixes I/O-style calls with domain calculation; split responsibilities.

Evaluate the current context against this rule (keep-operations-single-responsibility):

### `simplify-control-flow`

Handle the failing or empty cases first and return. Keep the main path flat. Do not nest more than three levels — deeper than that you cannot tell which conditions hold on a given line without reading back up, and that is where the unhandled branch hides.

Evaluate the current context against this rule (simplify-control-flow):

### `errors-out-of-existence`

For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure.

**Graph violations:** 8

- [X] **ERROR** **[graph rule]** - [harness/kanban/backlog_item.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\backlog_item.py#L35): Operation `load`: Operation 'load' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [harness/kanban/board.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\board.py#L170): Operation `column`: Operation 'column' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [harness/kanban/board.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\board.py#L214): Operation `practice`: Operation 'practice' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [harness/kanban/session_board_tiers.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\session_board_tiers.py#L167): Operation `data`: Operation 'data' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [harness/kanban/session_board_tiers.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\session_board_tiers.py#L290): Operation `data`: Operation 'data' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [harness/kanban/ticket.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\ticket.py#L75): Operation `load`: Operation 'load' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [harness/kanban/ticket.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\ticket.py#L135): Operation `progress_of`: Operation 'progress_of' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [harness/kanban/ticket.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\ticket.py#L298): Operation `move_to`: Operation 'move_to' raises on an empty or missing value; return a quiet result instead.

Evaluate the current context against this rule (errors-out-of-existence):

### `no-prototype-swapping`

An object keeps the class it was built as. Do not change it afterwards with `Object.setPrototypeOf`, `__proto__ =`, or `__class__ =`. When a subclass needs to make its own instances, give the base an overridable factory (`blank()`) or build the right class directly. A swapped object skips its constructor, so fields the subclass sets up are missing and nothing tells you.

Evaluate the current context against this rule (no-prototype-swapping):

### `use-intention-revealing-names`

Name each class, property, operation, and parameter so it answers why it exists. Do not abbreviate.

**Graph violations:** 8

- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/ticket/root-choice-client.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\ticket\root-choice-client.ts#L33): Parameter `item`: Parameter 'item' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/ticket/ticket-client.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\ticket\ticket-client.tsx#L241): Parameter `item`: Parameter 'item' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/test-utils/board-page-support.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\test-utils\board-page-support.ts#L192): Parameter `id`: Parameter 'id' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/test-utils/board-page-support.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\test-utils\board-page-support.ts#L197): Parameter `id`: Parameter 'id' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/test-utils/board-page-support.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\test-utils\board-page-support.ts#L206): Parameter `id`: Parameter 'id' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/kanban/generate-fidelity-outputs.story.ui.spec.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\generate-fidelity-outputs.story.ui.spec.ts#L30): Parameter `bar`: Parameter 'bar' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/kanban/generate-fidelity-outputs.story.ui.spec.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\generate-fidelity-outputs.story.ui.spec.ts#L31): Parameter `bar`: Parameter 'bar' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/kanban/session_board_examples.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\session_board_examples.py#L248): Parameter `item`: Parameter 'item' does not reveal intent.

Evaluate the current context against this rule (use-intention-revealing-names):

### `use-consistent-naming`

Use one word per concept. Pick one verb and use it everywhere (`fetch_`, not a mix of `fetch_`, `get_`, and `retrieve_`). Two words for one concept is how the same logic gets written twice — nobody searching for `fetch_` finds the `retrieve_` that already does the job.

Evaluate the current context against this rule (use-consistent-naming):

### `provide-meaningful-context`

Give a number or literal a name that says why it is there (`SECONDS_PER_DAY`, not `86400`). Do not number variables (`item1`).

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [harness/kanban/app/tests/support.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\tests\support.ts#L42): Operation `dragCard`: Operation 'dragCard' uses the unnamed number 20.
- [X] **ERROR** **[graph rule]** - [harness/kanban/guide-work-through-practices.story.ui.spec.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\guide-work-through-practices.story.ui.spec.ts#L35): Operation `dragIntoView`: Operation 'dragIntoView' uses the unnamed number 24.

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

### `deep-module`

Keep most classes private (at most **40%** public) in each first-class module. A first-class module is a folder that owns `.context/module-context.md`. Nested folders that also own that file are separate modules — respect them. Nested folders that do not own it roll up to the nearest enclosing module-context folder, or to the folder you are querying if none sits in between. Count classes, not operations: a public method on a hidden class is not a second seam. Every public class is a signature you cannot change without editing every caller, so public classes are much harder to refactor than private ones.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/kanban](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban#L1): Module `kanban`: Module 'kanban' splits into many tiny classes (175); prefer a deep module with a small public surface.

Evaluate the current context against this rule (deep-module):

### `keep-classes-single-responsibility`

Give each class one reason to change.

**Graph violations:** 16

- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/board/board-columns-view.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\board\board-columns-view.tsx#L1): OoadClass `_module`: Class '_module' exposes 11 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/board/side-panel-client.spec.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\board\side-panel-client.spec.ts#L1): OoadClass `_module`: Class '_module' exposes 11 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/chat/chat-client.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\chat\chat-client.tsx#L36): OoadClass `ChatClient`: Class 'ChatClient' exposes 13 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/ticket/files-panel-client.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\ticket\files-panel-client.ts#L51): OoadClass `FilesPanelClient`: Class 'FilesPanelClient' exposes 14 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/ticket/root-choice-client.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\ticket\root-choice-client.ts#L13): OoadClass `RootChoiceClient`: Class 'RootChoiceClient' exposes 10 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/ticket/ticket-card-view.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\ticket\ticket-card-view.tsx#L1): OoadClass `_module`: Class '_module' exposes 11 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/ticket/ticket-client.spec.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\ticket\ticket-client.spec.ts#L1): OoadClass `_module`: Class '_module' exposes 11 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/ticket/ticket-client.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\ticket\ticket-client.tsx#L27): OoadClass `TicketClient`: Class 'TicketClient' exposes 34 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/ticket/tile-actions-client.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\ticket\tile-actions-client.ts#L57): OoadClass `TileActionsClient`: Class 'TileActionsClient' exposes 11 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/ticket/tile-client.spec.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\ticket\tile-client.spec.ts#L1): OoadClass `_module`: Class '_module' exposes 10 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/ticket/tile-client.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\ticket\tile-client.ts#L23): OoadClass `TileClient`: Class 'TileClient' exposes 11 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/test-utils/board-page-support.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\test-utils\board-page-support.ts#L161): OoadClass `BoardOnProject`: Class 'BoardOnProject' exposes 18 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/test-utils/fixture-repo.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\test-utils\fixture-repo.ts#L1): OoadClass `_module`: Class '_module' exposes 11 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/kanban/board.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\board.py#L81): OoadClass `Board`: Class 'Board' exposes 10 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/kanban/session_board_examples.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\session_board_examples.py#L207): OoadClass `SessionsProject`: Class 'SessionsProject' exposes 19 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/kanban/ticket.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\ticket.py#L60): OoadClass `Ticket`: Class 'Ticket' exposes 14 public operations (budget ~9). Split responsibilities.

Evaluate the current context against this rule (keep-classes-single-responsibility):

### `limit-operation-parameters`

Have callers pass intent, not setup. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

**Graph violations:** 5

- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/ticket/files-panel-client.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\ticket\files-panel-client.ts#L41): Operation `showingTab`: Operation 'showingTab' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/ticket/files-panel-client.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\ticket\files-panel-client.ts#L87): Operation `openPanel`: Operation 'openPanel' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/ticket/files-panel-client.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\ticket\files-panel-client.ts#L116): Operation `openFileAtLine`: Operation 'openFileAtLine' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/ticket/tile-client.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\ticket\tile-client.ts#L56): Operation `withFiles`: Operation 'withFiles' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/session-board/http-exception.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\session-board\http-exception.ts#L31): Operation `answerFailure`: Operation 'answerFailure' takes 4 parameters (maximum 3, excluding self).

Evaluate the current context against this rule (limit-operation-parameters):

### `use-explicit-dependencies`

Pass every collaborator through the constructor. Do not reach for a global or construct a collaborator inside construction. A collaborator the class fetches or builds itself cannot be swapped, so the class can only ever run against that one implementation.

**Graph violations:** 6

- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/board/board-page.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\board\board-page.ts#L33): OoadClass `BoardPage`: Class 'BoardPage' constructs 'BoardApi' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/test-utils/behavior-test/cdd-project.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\test-utils\behavior-test\cdd-project.ts#L15): OoadClass `CddProject`: Class 'CddProject' constructs 'CddConnection' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/kanban/kanban_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\kanban_spec.py#L24): OoadClass `SessionsFolder`: Class 'SessionsFolder' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/kanban/kanban_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\kanban_tools_spec.py#L140): OoadClass `ProjectTools`: Class 'ProjectTools' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/kanban/session_board_examples.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\session_board_examples.py#L207): OoadClass `SessionsProject`: Class 'SessionsProject' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/kanban/session_board_tiers.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\session_board_tiers.py#L82): OoadClass `CddTools`: Class 'CddTools' constructs 'McpServer' inside its constructor.

Evaluate the current context against this rule (use-explicit-dependencies):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 19

- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/board/board-api.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\board\board-api.ts#L9): Parameter `path`: Parameter 'path' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/board/board-api.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\board\board-api.ts#L9): Parameter `init`: Parameter 'init' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/board/side-panel-client.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\board\side-panel-client.ts#L29): Parameter `panel`: Parameter 'panel' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/ticket/files-panel-client.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\ticket\files-panel-client.ts#L63): Parameter `panel`: Parameter 'panel' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/ticket/ticket-card-view.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\ticket\ticket-card-view.tsx#L172): Parameter `isSelected`: Parameter 'isSelected' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/kanban/ticket/tile-client.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\kanban\ticket\tile-client.ts#L62): Parameter `tile`: Parameter 'tile' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/session-board/board-update.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\session-board\board-update.ts#L22): Parameter `command`: Parameter 'command' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/session-board/board-update.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\session-board\board-update.ts#L22): Parameter `args`: Parameter 'args' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/session-board/board-update.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\session-board\board-update.ts#L22): Parameter `folder`: Parameter 'folder' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/session-board/claude-link.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\session-board\claude-link.ts#L19): Parameter `command`: Parameter 'command' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/src/session-board/claude-link.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\src\session-board\claude-link.ts#L19): Parameter `args`: Parameter 'args' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/test-utils/board-page-support.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\test-utils\board-page-support.ts#L136): Parameter `isBusy`: Parameter 'isBusy' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/test-utils/board-page-support.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\test-utils\board-page-support.ts#L192): Parameter `name`: Parameter 'name' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/test-utils/board-page-support.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\test-utils\board-page-support.ts#L192): Parameter `folder`: Parameter 'folder' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/test-utils/board-page-support.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\test-utils\board-page-support.ts#L197): Parameter `id`: Parameter 'id' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/kanban/app/test-utils/board-page-support.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\app\test-utils\board-page-support.ts#L197): Parameter `isBusy`: Parameter 'isBusy' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/kanban/review-fidelity-outputs.story.shared.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\review-fidelity-outputs.story.shared.py#L52): Parameter `world`: Parameter 'world' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/kanban/review-fidelity-outputs.story.shared.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\review-fidelity-outputs.story.shared.py#L52): Parameter `seed`: Parameter 'seed' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/kanban/steer-ticket-sessions.story.shared.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\kanban\steer-ticket-sessions.story.shared.py#L74): Parameter `board`: Parameter 'board' needs a domain-specific type, not a generic container.

Evaluate the current context against this rule (use-typed-signatures):

## Judgment — `harness/kanban/ticket.py`

### `hold-state-on-the-object-not-in-parameters` — Fail
- ticket.py:338 `generate_commands(fidelities, formats)`: the fidelities travel as slug strings so `progress_of` can find progress the caller already held, and the formats are handed in rather than saved on the fidelity they were chosen for (P-2, P-3, P-4 still open).
- ticket.py:659 `_in_session`: the ticket's session is written into the command text as `session=...` for the action to parse back and load again (P-2 still open).
- ticket.py:634 `FidelityCommands.__init__`: takes `session` beside `progress`, though the progress already reaches its ticket's session, so there are two ways to pass the wrong session.
- ticket.py:638 `FidelityCommands.generate(formats, *alongside)`: the format list is handed down to every `render_earlier(formats)` call instead of being read from each fidelity.
- ticket.py:428 `FidelityProgress.load(ticket, fidelity)`: every tool call carries two name strings and rebuilds the whole board to find the one progress the client had (P-13 still open).
- ticket.py:127 `_own`: the board's fidelity is looked up again in the session by practice key and name, because the board and the session hold separate instances of one fidelity (P-14 still open).

### `do-not-invent-parallel-object-models` — Fail
- ticket.py:131 `progress_by_fidelity`: a dict keyed by slug sent as `progress`, so every client indexes progress by string instead of holding the progress objects; the board app's `progressOf(slug)`, `isOn(slug)` and `stateOf(slug)` follow from it.
- ticket.py:157 `column_name`: a `*_name` copy of `column`, sent as the ticket's column (K-F21 still open).
- ticket.py:206 `next_slug`: a slug copy of `next_fidelity`, sent as `next` (K-F21).
- ticket.py:434 `FidelityProgress.ticket`: the ticket's name as a string data field rather than the ticket it is on.
- ticket.py:593 `rules_answered_by`: FidelityProgress works out which rules a report answers for (the shared rules and the earlier fidelities' rules), which is the fidelity's and its reports' own job (P-22). With `rule_descriptions`, `earlier_fidelities` and `_latest_report_in`, FidelityProgress has 36 members, many of them only reading its fidelity, ticket and session.

### `no-legacy-api-after-refactor` — Fail
- ticket.py:363 `_folder`: a dead private property left from the TicketFiles split; nothing reads it.
- ticket.py:5 `cached_property`: an import left after the refactor; unused.

## Judgment — `harness/kanban/board.py`

### `do-not-invent-parallel-object-models` — Fail
- board.py:300 `Stage.formats`: a dict keyed by fidelity slug holding one field of each fidelity (`outputs`), the shape the rule names (`fidelity_states`); the board app then picks formats from it in TypeScript.
- board.py:305 `Stage.default_formats`: the same pattern, a dict of each fidelity's `default_format` keyed by slug.
- board.py:295 `work_required_slugs`: the stage sends slug strings, not its fidelities, so every client looks them up again by slug.
- board.py:166 `active_name`: a `*_name` copy of `active`, sent as `active`; the chat bar reads it as `board.active` (K-F21 still open).
- board.py:396 `Help`: copies the practice's and fidelity's key, name, slug, stage, overview, guidance and rules into a second class beside PracticeGuidance and FidelityGuidance (K-F20).
- board.py:473 `Workspace`: still a bag of three of the branches' answers, the exact example the rule names; callers could be handed the ticket's `Branch` and the active ticket's `Branch` instead.

### `hold-state-on-the-object-not-in-parameters` — Fail
- board.py:204 `help(slug)`: TypeScript passes a slug so that Board can find a practice or fidelity the tile already showed (P-28 still open).

### `use-exceptions-properly` — Fail
- board.py:212 `help`: an unknown fidelity slug raises `PracticeNotFoundError`, which names the wrong failure; `FidelityNotFoundError` exists for it.

### `no-legacy-api-after-refactor` — Fail
- board.py:214 `practice`: no caller in the repository; dead after the practice catalogue refactor.

## Judgment — `harness/kanban/report.py`

### `do-not-invent-parallel-object-models` — Fail
- report.py:44 `Violation`: a third violation shape beside graph_json_reader's violation dict and `RuleHit` in harness/graph/explorer.py; `_violation_of` converts one into the other (A-F14 still open).
- report.py:81 `ReportRule.fidelity`: the fidelity held as a slug string instead of the fidelity.

### `vocabulary-traces-to-source` — Fail
- report.py:115 `identity`: rebuilds the practice with `split("-")[0]` on the slug, which gives `clean` for clean-engineering; the practice is already an object that the report's progress holds (1.10, K-F20).

### `use-typed-signatures` — Fail
- report.py:217 `_hits_by_rule`: returns `dict[str, list[dict]]`, which are untyped violation dicts from a free function in validate.

## Judgment — `harness/kanban/app/src/kanban/ticket/ticket-client.tsx`

### `hold-state-on-the-object-not-in-parameters` — Fail
- ticket-client.tsx:264 `actionCommand`: still appends `session=` to every command, the TypeScript half of P-2.
- ticket-client.tsx:81 `progressOf(slug)`: every per-fidelity operation (`isOn`, `stateOf`, `lightOf`, `actionsOf`, `allows`, `progressClient`) takes a slug to find progress again; a tile should hold its FidelityProgress clients (P-4, P-8).

### `do-not-invent-parallel-object-models` — Fail
- ticket-client.tsx:14 `RUN_NEXT_COMMANDS`: slash command names are written out in TypeScript, and line 304 assembles the validate and satisfy commands, which belong to the fidelity's actions in Python (KB-3, 1.3).
- ticket-client.tsx:305 `runNext`: chooses the generate format from the stage's `defaultFormats` dict in TypeScript (P-3).

### `keep-classes-single-responsibility` — Fail
- ticket-client.tsx:27 `TicketClient`: 34 public members that mix display text, fidelity lookups, chat commands and moves. The graph hit is confirmed.

### `use-exceptions-properly` — Fail
- ticket-client.tsx:83 `progressOf`: throws a plain `Error` with a message string.

## Judgment — `harness/kanban/app/src/kanban/ticket/tile-actions-client.ts`

### `do-not-invent-parallel-object-models` — Fail
- tile-actions-client.ts:110 `run`: builds `/actions-${tile.action} ...` in TypeScript, a second command builder beside `FidelityCommands` in Python.
- tile-actions-client.ts:114 `run`: builds `/actions-render ... format=` without the `source=` that the Python render command adds, so the two builders have already drifted.
- tile-actions-client.ts:118 `validate`: builds `/actions-validate` in TypeScript. This is the graph's single-responsibility hit, confirmed: it builds a command and also sends it.

### `hold-state-on-the-object-not-in-parameters` — Fail
- tile-actions-client.ts:103 `runCommandsOf(ticket, fidelities, formats)`: the format list starts its six-layer trip here (P-3).
- tile-actions-client.ts:28 `reportSlugOf(ticket, tile)`: these free functions take the ticket and the tile, although the tile already holds its ticket; they belong on the tile (the P-10 pattern, in the board app).

## Judgment — `harness/kanban/app/src/kanban/ticket/tile-formats.ts`

### `do-not-invent-parallel-object-models` — Fail
- tile-formats.ts:17 `chipFormat`: decides in TypeScript which format each fidelity uses (its default when the group holds it), a domain rule that Python's fidelity should own (P-3, 1.3).

### `hold-state-on-the-object-not-in-parameters` — Fail
- tile-formats.ts:23 `chosenFormats(stage, slugs, picked)`: free functions handed the stage, slugs and picks that a tile holds.

## Judgment — `harness/kanban/app/src/kanban/ticket/files-panel-client.ts`

### `hold-state-on-the-object-not-in-parameters` — Fail
- files-panel-client.ts:73 `openFiles(ticket, slugs, mode)`: the ticket is passed on every call, although the open panel holds it.
- files-panel-client.ts:116 `openFileAtLine(ticket, fidelity, path, line)`: four values, with the fidelity passed as a slug. This also confirms the graph's limit-operation-parameters hit.

### `keep-classes-single-responsibility` — Fail
- files-panel-client.ts:51 `FilesPanelClient`: 14 public operations. The graph hit is confirmed.

## Judgment — `harness/kanban/app/src/kanban/ticket/tile-client.ts`

### `hold-state-on-the-object-not-in-parameters` — Fail
- tile-client.ts:61 `change(ticket: string, place)`: the ticket's name is passed to find a tile that already holds its TicketClient. P-9 is still partly open: tiles now hold the client, but the lookups still go by name.

## Judgment — `harness/kanban/app/src/kanban/chat/chat-client.tsx`

### `hold-state-on-the-object-not-in-parameters` — Fail
- chat-client.tsx:65 `chatFor(ticket, worktree)`: ChatClient still takes the ticket's name and worktree as strings. `TicketChat` wraps it, but the seam underneath is unchanged (P-11 partly open).
- chat-client.tsx:86 `startFor(ticket, worktree)`: the same pair of strings.

### Graph hits dismissed
- keep-operations-small-focused on the seven React views (board-columns-view.tsx:87, details-view.tsx:27, root-choice-view.tsx:35 and :64, ticket-card-view.tsx:63, :148 and :174): each view is a few statements and one JSX return, which the rule counts as one statement.
- keep-operations-single-responsibility on action-bar-view.tsx:64 and board-store.ts:126: a click handler in JSX and a guarded localStorage read are each one job. The hit on tile-actions-client.ts:117 is confirmed above under a different rule.
- errors-out-of-existence on ticket.py:75, :135 and :298, board.py:170 and :214, and backlog_item.py:35: each one looks up a ticket, fidelity, column or stage that the caller named, so a miss means the request was wrong, and a named domain exception is correct there.
- use-explicit-dependencies on board-page.ts:33: BoardPage is the page's composition root, the one place meant to build its collaborators.
- prefer-instance-operations, use-intention-revealing-names, provide-meaningful-context, use-typed-signatures, use-explicit-dependencies and keep-classes-single-responsibility hits in test-utils/, tests/, *.story.*, *_spec.py, *.spec.ts, session_board_tiers.py, session_board_examples.py and story_test.py: these files are test support, not production code.
- use-typed-signatures on board-api.ts:9, side-panel-client.ts:29, files-panel-client.ts:63, tile-client.ts:62, board-update.ts:22, claude-link.ts:19 and ticket-card-view.tsx:172: TypeScript infers these parameter types from a typed context (arrow functions in typed positions, or defaulted props), so they are not judged as failures.
- deep-module on harness/kanban (175 classes): the count includes the app's views, test utilities and specs, while the production Python is five files.
- keep-classes-single-responsibility on board.py:81 `Board` (10 public operations): one over the budget. Its real problem is the copies listed above.
