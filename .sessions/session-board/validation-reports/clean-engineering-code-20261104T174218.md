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
# Judgment

Judged the production Python of the session board in the session-board worktree (`harness/kanban/ticket.py`, `board.py`, `backlog_item.py`, `data.py`) as it stands at commit c889a955. The board app's TypeScript under `harness/kanban/app/` was not judged in this pass. The renames a fix of the model report is making on main (root to workpath, choose_root to choose_workpath) are not in this checkout yet, so the findings below on those names still hold here.

Passes: `keep-operations-small-focused` (no operation reaches 20 statements; `FidelityProgress.from_log` and `_judgments_in` are the longest at about 13), `simplify-control-flow` (no nesting deeper than three levels; empty cases return first), `no-prototype-swapping` (no class is reassigned), `never-swallow-exceptions` (the only `try` is a `try/finally` in `_files_of`, which re-raises).

## Judgment — `harness/kanban/ticket.py`

### `vocabulary-traces-to-source` — Fail
- ticket.py:338 `root`: the ticket calls the session's folder `root` while the session that stores it calls it `workpath` (`self._session.workpath`, `change_workpath`), so one folder has two names across the seam.
- ticket.py:324 `choose_root`: the tool says choose root and immediately calls `self._session.change_workpath`; a reader has to translate root to workpath to follow the call.
- ticket.py:351 `practice_roots`: the ticket says practice root while the session it reads says output root (`choose_output_root`, `forget_output_root`, `has_chosen_output_root` at lines 334, 347, 355), so the same per-practice folder carries two names.
- ticket.py:127 `lineage`: the session field and `TicketData` say `parent` (lines 128, 449), but the property says `lineage`; the domain word is parent.

### `do-not-invent-terms` — Fail
- ticket.py:559 `_graph_root`: a third name for the session's folder beside `root` and `workpath`, computed the same way as `root` at line 340.
- ticket.py:127 `lineage`: a second noun for the parent ticket, invented beside the `parent` field it reads.

### `do-not-invent-parallel-object-models` — Fail
- ticket.py:817 `Finding`: a second violation shape (file, line, message) beside `ViolationData` (location, line, message, source) in data.py; `_judged_violation` then translates one into the other, so a change to what a violation holds must be made in both.
- ticket.py:599 `_judged_rules`: builds plain `dict[str, Any]` rules instead of `ReportRuleData`, and `_rules_broken_in` at line 591 builds the same dict separately, so the report's rule shape is defined in three places.

### `hide-inner-details` — Fail
- ticket.py:368 `enable_practice`: writes `self._session.practices[practice].enabled` directly, reaching into how the session stores its practices instead of asking the session to enable one.
- ticket.py:640 `_files_of`: sets `practice.fidelities.current` on a shared, process-cached practice and puts it back, depending on how guidance stores its current fidelity; a caller that reads the practice during the call sees the wrong fidelity.
- ticket.py:111 `session`: a public property that hands out the whole session object and has no caller, so it invites callers to change the ticket's state around the ticket's own operations.
- ticket.py:820 `Finding`: `file`, `line`, and `message` are public mutable attributes, and `Judgment.findings` at line 832 is a public mutable list that callers can append to around `add`.

### `prefer-instance-operations` — Fail
- ticket.py:844 `_judgments_in`: a module function that parses a report's judgment; it belongs on an instance that owns the report text, so the parse and its rules sit with the object that uses them.
- ticket.py:863 `practice_key`: a module function about a practice, imported into board.py at lines 157 and 291; it belongs on the practice guidance it describes.
- ticket.py:101 `new`: a `@classmethod` whose name is not one of the allowed factory names (`create`, `from_*`, `load`); `BacklogItem.add` and `Session.new` use other creation verbs.

### `keep-operations-single-responsibility` — Fail
- ticket.py:700 `from_log`: parses log lines into words, finds the fidelity's entries, and decides the validate and review verdicts in one operation, so a change to the log format and a change to when validate counts as done edit the same body.
- ticket.py:659 `_file_entries`: turns a declared path into a pattern, searches the disk, filters to the ticket's work, and falls back to the declared path, mixing calculation with I/O.
- ticket.py:147 `_judged`: reads report files from disk inside the progress calculation, so every read of `progress` searches the report folder once per fidelity.

### `errors-out-of-existence` — Fail
- ticket.py:393 `read_file`: raises `TicketFileError` when the file does not exist, an ordinary case when a listed file was deleted since the board read it; the board then shows a failure toast instead of an empty file.

### `use-intention-revealing-names` — Fail
- ticket.py:513 `marks`: holds the single latest mark, not a list of marks, so the plural misleads.
- ticket.py:555 `held`: names a `Ticket` here while backlog_item.py:100 uses `held` for a folder `Path`; the same word names two different things.
- ticket.py:909 `_words`: also strips trailing commas, which the name does not say.
- ticket.py:834 `add`: parses a line into a finding and ignores paragraphs after the first bullet; the name hides that it parses and filters.

### `use-consistent-naming` — Fail
- ticket.py:528 `_from_project`: three helpers make a path relative to the repository (`_from_project`, `_from_repository` at 359, `_relative_to` at 683), named with project, repository, and relative for one concept.
- ticket.py:324 `choose_root`: the ticket's verbs are choose and use default (`choose_root`, `choose_practice_root`, `use_default_practice_root` at 345) while the session's are change, choose, and forget (`change_workpath`, `choose_output_root`, `forget_output_root`).
- ticket.py:101 `new`: a ticket is created with `new`, a backlog item with `add` (backlog_item.py:46); two verbs for creating a card.

### `provide-meaningful-context` — Fail
- ticket.py:508 `_moved_into`: picks log words by position (`line.split()[2]`, `[1]`) with no name for which word is the verb and which the stage; the same positions repeat at line 516.
- ticket.py:160 `column`: the literal `"Complete"` names a column that board.py builds from another literal (board.py:196), while `BACKLOG_COLUMN` at line 42 names the Backlog; one column has a constant and the other does not.
- ticket.py:149 `_judged`: the literals `"validate"` and `"generate"` (also lines 706, 711, 751) stand for actions `STAGE_ACTIONS` in board.py already names.
- ticket.py:440 `session_file`: the literal `"session.json"` is the session's own file name and belongs to the session that writes it.

### `eliminate-duplication` — Fail
- ticket.py:340 `root`: `Path(self._session.workpath or self._board.repo_root)` is repeated at lines 561 and 674; a change to what the folder of a session with no workpath is must be made three times.
- ticket.py:781 `_practice_fidelities`: the same entries-as-list conversion as `Stage._fidelities_of` in board.py:286.
- ticket.py:592 `_rules_broken_in`: `next(entry for entry in self.progress if entry.slug == ...)` repeats at lines 601 and 649, and `finish_review` builds the same lookup as `by_slug` at line 312.
- ticket.py:633 `_repository_file`: calls `self._board.repo_root.resolve()` again (also lines 360, 661, 673, 680) though `Board.__init__` already resolves `repo_root`.

### `no-legacy-api-after-refactor` — Fail
- ticket.py:39 `MOVE_WORDS`: keeps the old log word `pull` beside `move`, so two words mean one move for every reader of the log.
- ticket.py:811 `JUDGED_RULE_HEADING`: still accepts the old `Warn` verdict that validate.md no longer allows.
- ticket.py:814 `NAMED_LINE`: keeps a second parser for findings written before validate.md gave the judgment its shape, so two finding formats stay supported.

### `use-exceptions-properly` — Fail
- ticket.py:649 `_render_command`: a bare `next(...)` raises `StopIteration` for a slug the ticket has no progress for, so `generate_commands` with an unknown fidelity fails with no named error; `FidelityNotFoundError` already exists for this.
- ticket.py:592 `_rules_broken_in`: the same bare `next(...)` lookup, again at line 601, raises `StopIteration` instead of `FidelityNotFoundError`.
- ticket.py:368 `enable_practice`: an unknown practice raises a bare `KeyError` from the session's practices.
- ticket.py:70 `TicketFileError`: the name says file error, not the failure it raises for (a path outside the repository, or a missing file), so a caller cannot tell the two apart.

### `limit-comments` — Fail
- ticket.py:691 `FidelityProgress`: the comment says validate is done only when its latest line names no graph-rule violations, but `_judged` at line 147 also fails it on a failing judgment, so the comment no longer says what the code does.
- ticket.py:497 `record`: the docstring "Append entry to the session log, timestamped." narrates what the name and body already say.

## Judgment — `harness/kanban/board.py`

### `prefer-instance-operations` — Fail
- board.py:35 `_every_practice`: a module function that builds the practices; it is the board's own factory and belongs on `Board` beside `load`.

### `hide-inner-details` — Fail
- board.py:287 `_fidelities_of`: reads `practice.fidelities.entries` and checks whether it is a dict or a list, depending on how guidance stores its fidelities instead of asking it for them.

### `use-exceptions-properly` — Fail
- board.py:119 `column`: a bare `next(...)` raises `StopIteration` for a column name the board does not have.
- board.py:159 `help`: an unknown practice raises `StopIteration` and an unknown fidelity raises `KeyError` at line 160, neither naming the failure, so the board cannot tell a person which name was wrong.

### `provide-meaningful-context` — Fail
- board.py:196 `_build_columns`: the literal `"Complete"` (and `"Backlog"` at line 222) names a column that ticket.py and backlog_item.py refer to with their own literals.

### `eliminate-duplication` — Fail
- board.py:282 `to_json`: recomputes in progress and done with the same filters the `in_progress` and `done` properties at lines 262 and 266 already hold.
- board.py:222 `Backlog`: the Backlog column's name is written here, in backlog_item.py:81, and in ticket.py:42.

## Judgment — `harness/kanban/backlog_item.py`

### `prefer-instance-operations` — Fail
- backlog_item.py:51 `holding`: a `@classmethod` that is not one of the allowed factory names and also writes a file.
- backlog_item.py:60 `_written`: a private `@classmethod` that writes the item's file; writing belongs on the item once built.

### `keep-operations-single-responsibility` — Fail
- backlog_item.py:51 `holding`: works out the item's path, writes the idea file when it is missing, and builds the item, mixing I/O with creation.

### `use-consistent-naming` — Fail
- backlog_item.py:46 `add`: creates a card with `add` while `Ticket` creates one with `new`.

### `provide-meaningful-context` — Fail
- backlog_item.py:81 `column`: the literal `"Backlog"` while ticket.py names it `BACKLOG_COLUMN`.

## Judgment — `harness/kanban/data.py`

### `vocabulary-traces-to-source` — Fail
- data.py:33 `root`: the TypeScript agreement names the session's folder `root` while the session that stores it says `workpath`, so the name crosses into the board app wrong.
- data.py:14 `PracticeRootData`: practice root here, output root in the session it is read from.
