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


Judge only the checked format's files (python: C:/dev/abd-cdd-session-board/harness/kanban/{module}/). The other formats mirror them, so judging those too reports every finding twice.

# Graph rule validation

**Generated:** 2026-11-05 06:50:11 UTC
**Project:** kanban
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-context-driven-delivery\.sessions\session-board\edited-graph.json`

## Summary

**Total graph violations:** 32
**Rules with graph hits:** 8
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

Keep one object model. Follow the nouns and verbs the rest of the graph already uses for that concept. A class that joins types the rest of the graph keeps apart is a second model — a big ball of mud — and every rule then has to be written and fixed in both. Wrap or extend the live objects and name a wrapper after the type it represents; do not scrape the same data into a second `*Model` or `*Entry` family.

Evaluate the current context against this rule (do-not-invent-parallel-object-models):

### `hide-inner-details`

Expose behavior through named operations. Do not let callers see how the class stores or arranges its data — once they read the storage directly it becomes a public contract you cannot change. Private fields on the same class hide implementation; you do not need a second class for that. Read-only to callers can mean return a copy or immutable view from a property — it does not require a frozen class or a second type to hold build steps.

Evaluate the current context against this rule (hide-inner-details):

### `keep-operations-small-focused`

Keep each operation short enough to read as one thought — under 20 statements. A multi-line call, list, or string initializer is one statement. When it grows, extract a private helper whose name says why that slice exists.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [ticket.py](C:\dev\abd-cdd-session-board\harness\kanban\ticket.py#L503): Operation `to_json`: Operation 'to_json' is 24 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [board.py](C:\dev\abd-cdd-session-board\harness\kanban\board.py#L91): Operation `current`: Operation 'current' is a classmethod; prefer an instance operation.

Evaluate the current context against this rule (prefer-instance-operations):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

Evaluate the current context against this rule (keep-operations-single-responsibility):

### `simplify-control-flow`

Handle the failing or empty cases first and return. Keep the main path flat. Do not nest more than three levels — deeper than that you cannot tell which conditions hold on a given line without reading back up, and that is where the unhandled branch hides.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [ticket.py](C:\dev\abd-cdd-session-board\harness\kanban\ticket.py#L875): Operation `from_report`: Operation 'from_report' nests control flow 5 levels deep (max 3).

Evaluate the current context against this rule (simplify-control-flow):

### `errors-out-of-existence`

For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure.

**Graph violations:** 6

- [X] **ERROR** **[graph rule]** - [backlog_item.py](C:\dev\abd-cdd-session-board\harness\kanban\backlog_item.py#L36): Operation `load`: Operation 'load' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [board.py](C:\dev\abd-cdd-session-board\harness\kanban\board.py#L163): Operation `column`: Operation 'column' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [board.py](C:\dev\abd-cdd-session-board\harness\kanban\board.py#L217): Operation `practice`: Operation 'practice' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [ticket.py](C:\dev\abd-cdd-session-board\harness\kanban\ticket.py#L108): Operation `load`: Operation 'load' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [ticket.py](C:\dev\abd-cdd-session-board\harness\kanban\ticket.py#L288): Operation `move_to`: Operation 'move_to' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [ticket.py](C:\dev\abd-cdd-session-board\harness\kanban\ticket.py#L446): Operation `read_file`: Operation 'read_file' raises on an empty or missing value; return a quiet result instead.

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

Raise a domain exception that names the failure (`CartAlreadyCheckedOut`, not `Error` or a bare string). Catch the specific type you can handle. Do not use a bare `except`. A generic exception cannot be caught selectively, so the caller has to handle everything or nothing.

Evaluate the current context against this rule (use-exceptions-properly):

### `never-swallow-exceptions`

Do not catch and ignore. Log and re-raise, or convert to a domain exception that still names the failure. A `pass` in `except` hides a broken invariant.

Evaluate the current context against this rule (never-swallow-exceptions):

### `limit-comments`

write comment in operations and properties only when the signature cannot say a constraint or explain why the code behaves the way it does. Do not narrate a line that already names what it does.

Evaluate the current context against this rule (limit-comments):

### `keep-classes-single-responsibility`

Give each class one reason to change.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [board.py](C:\dev\abd-cdd-session-board\harness\kanban\board.py#L69): OoadClass `Board`: Class 'Board' exposes 13 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [ticket.py](C:\dev\abd-cdd-session-board\harness\kanban\ticket.py#L96): OoadClass `Ticket`: Class 'Ticket' exposes 28 public operations (budget ~9). Split responsibilities.

Evaluate the current context against this rule (keep-classes-single-responsibility):

### `shape-classes-around-resources`

Model a class around the concept that owns the state and the rule, not a doer, handler, or service that acts on a data bag. A Payment has transactions, a source, and a destination, and it moves the money; it is not a `PaymentService` that takes a `PaymentData` object. A service-plus-bag pair splits the rule from its memory, so every change has to be found in two types and the bag cannot enforce anything. Two resources may collaborate — a model that loads a Module is not a service-plus-bag split.

**Graph violations:** 11

- [X] **ERROR** **[graph rule]** - [data.py](C:\dev\abd-cdd-session-board\harness\kanban\data.py#L8): OoadClass `ActionStatesData`: Class 'ActionStatesData' is a passive data bag; shape behavior around a resource.
- [X] **ERROR** **[graph rule]** - [data.py](C:\dev\abd-cdd-session-board\harness\kanban\data.py#L14): OoadClass `PracticeRootData`: Class 'PracticeRootData' is a passive data bag; shape behavior around a resource.
- [X] **ERROR** **[graph rule]** - [data.py](C:\dev\abd-cdd-session-board\harness\kanban\data.py#L42): OoadClass `BacklogItemData`: Class 'BacklogItemData' is a passive data bag; shape behavior around a resource.
- [X] **ERROR** **[graph rule]** - [data.py](C:\dev\abd-cdd-session-board\harness\kanban\data.py#L64): OoadClass `BoardData`: Class 'BoardData' is a passive data bag; shape behavior around a resource.
- [X] **ERROR** **[graph rule]** - [data.py](C:\dev\abd-cdd-session-board\harness\kanban\data.py#L70): OoadClass `HelpRuleData`: Class 'HelpRuleData' is a passive data bag; shape behavior around a resource.
- [X] **ERROR** **[graph rule]** - [data.py](C:\dev\abd-cdd-session-board\harness\kanban\data.py#L85): OoadClass `WorkspaceData`: Class 'WorkspaceData' is a passive data bag; shape behavior around a resource.
- [X] **ERROR** **[graph rule]** - [data.py](C:\dev\abd-cdd-session-board\harness\kanban\data.py#L91): OoadClass `FileEntryData`: Class 'FileEntryData' is a passive data bag; shape behavior around a resource.
- [X] **ERROR** **[graph rule]** - [data.py](C:\dev\abd-cdd-session-board\harness\kanban\data.py#L96): OoadClass `FileTextData`: Class 'FileTextData' is a passive data bag; shape behavior around a resource.
- [X] **ERROR** **[graph rule]** - [data.py](C:\dev\abd-cdd-session-board\harness\kanban\data.py#L101): OoadClass `SourceLineData`: Class 'SourceLineData' is a passive data bag; shape behavior around a resource.
- [X] **ERROR** **[graph rule]** - [data.py](C:\dev\abd-cdd-session-board\harness\kanban\data.py#L106): OoadClass `ViolationData`: Class 'ViolationData' is a passive data bag; shape behavior around a resource.
- [X] **ERROR** **[graph rule]** - [data.py](C:\dev\abd-cdd-session-board\harness\kanban\data.py#L121): OoadClass `ReportData`: Class 'ReportData' is a passive data bag; shape behavior around a resource.

Evaluate the current context against this rule (shape-classes-around-resources):

### `use-explicit-dependencies`

Pass every collaborator through the constructor. Do not reach for a global or construct a collaborator inside construction. A collaborator the class fetches or builds itself cannot be swapped, so the class can only ever run against that one implementation.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [backlog_item.py](C:\dev\abd-cdd-session-board\harness\kanban\backlog_item.py#L27): OoadClass `BacklogItem`: Class 'BacklogItem' constructs 'Path' inside its constructor.

Evaluate the current context against this rule (use-explicit-dependencies):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 9

- [X] **ERROR** **[graph rule]** - [backlog_item.py](C:\dev\abd-cdd-session-board\harness\kanban\backlog_item.py#L36): Parameter `cls`: Parameter 'cls' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [backlog_item.py](C:\dev\abd-cdd-session-board\harness\kanban\backlog_item.py#L46): Parameter `cls`: Parameter 'cls' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [backlog_item.py](C:\dev\abd-cdd-session-board\harness\kanban\backlog_item.py#L54): Parameter `cls`: Parameter 'cls' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [board.py](C:\dev\abd-cdd-session-board\harness\kanban\board.py#L83): Parameter `cls`: Parameter 'cls' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [board.py](C:\dev\abd-cdd-session-board\harness\kanban\board.py#L91): Parameter `cls`: Parameter 'cls' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [ticket.py](C:\dev\abd-cdd-session-board\harness\kanban\ticket.py#L108): Parameter `cls`: Parameter 'cls' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [ticket.py](C:\dev\abd-cdd-session-board\harness\kanban\ticket.py#L118): Parameter `cls`: Parameter 'cls' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [ticket.py](C:\dev\abd-cdd-session-board\harness\kanban\ticket.py#L745): Parameter `cls`: Parameter 'cls' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [ticket.py](C:\dev\abd-cdd-session-board\harness\kanban\ticket.py#L875): Parameter `cls`: Parameter 'cls' is missing a type annotation.

Evaluate the current context against this rule (use-typed-signatures):

## Judgment — `harness/kanban/ticket.py`

### `keep-classes-single-responsibility` — Fail
- ticket.py:102 `Ticket` has more than one reason to change. It places a ticket on the board and moves it, opens and leaves its git branch and worktree (`activate`, `leave`, `open_workspace`, `open_worktree`, `workspace`), lists and searches its declared files (`files`, `session_files`, `read_file`, `_files_under`), and reads its validation reports into rules (`report`, `violations`, `_hits_by_rule`, `_judged_rules`). Each `ticket.*` MCP tool is a public operation of this toolset, so splitting it means a new toolset and new tool names in the board app's TypeScript client. That design change is left for a person to decide.

## Judgment — `harness/kanban/board.py`

### `keep-classes-single-responsibility` — Fail
- board.py:69 `Board` reads the columns and tickets, and also answers `help` (practice guidance) and `folders` (repository folders), which change for reasons unrelated to the board. They are the `board.help` and `board.folders` MCP tools the board app calls, so moving them renames a public seam; left for a person to decide.

Scanner hits judged false positives, not fixed:
- `shape-classes-around-resources` on every `*Data` class in `data.py`: these are the TypedDict shapes `to_json` returns and the TypeScript language adapter reads. No service takes them as input; the behaviour stays on `Board`, `Ticket`, and `BacklogItem`.
- `use-typed-signatures` on `cls`: Python types `cls` implicitly, and the factories it belongs to have typed parameters and returns.
- `errors-out-of-existence` on `Ticket.load`, `BacklogItem.load`, `Board.column`, `Board.practice`, `Ticket.move_to`, `Ticket.read_file`: each raises only when a caller names a ticket, item, column, practice, or stage that does not exist, or a file outside the repository. That is a broken request, not an ordinary empty case. Each raise is a named domain exception, and `read_file` already returns empty text for a missing file.
- `prefer-instance-operations` on `Board.current`: it is the `@tool_subject` factory that loads the board of the project the call names, the same as `load`.

Fixed since the 2026-11-04 report: `Ticket.to_json` split (`_progress_json`), `Judgment.from_report` flattened to three levels, the module-level log and file-search functions moved onto `Ticket` and `FidelityProgress`, `FidelityProgress._actions_naming` staticmethod removed, `Card.to_json` typed with `CardData`, and `BacklogItem` no longer rebuilds the `Path` it is given.
