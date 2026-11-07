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

**Generated:** 2026-11-07 09:03:12 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 21
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

Keep one object model. Follow the nouns and verbs the rest of the graph already uses for that concept. A class that joins types the rest of the graph keeps apart is a second model — a big ball of mud — and every rule then has to be written and fixed in both. When data or behavior already belongs to an object, extend that object and hand callers the object itself: `ticket.session.practices["stories"].fidelities["story_map"].files()`, not `ticket.files(["stories-story_map"])`. A second model is rarely a whole class family; more often it is a small copy beside the owner: a dict holding one field from each member (`fidelity_states`, `violation_counts`), a `*_name` copy of a reference (`column_name`), a helper class that does the owner's job (`TicketFiles`), a bag of a few of the owner's answers (`Workspace`), or a `*Model` / `*Entry` family scraped from live objects. A copy hides that the owner is missing the behavior, so the next caller builds another copy and a fix to the owner never reaches it. **Checking it:** this rule spans modules, and the copy looks fine in the file that holds it. For every property, data field, dict, and helper class the changed code adds, name the class that already owns that data and read it; the rule fails when the owner holds it or should, and the change copies it instead of returning or extending the owner. Count the members of a class that delegates: dozens of members on a class that only reads its collaborators means it is copying them.

Evaluate the current context against this rule (do-not-invent-parallel-object-models):

### `hide-inner-details`

Expose behavior through named operations. Do not let callers see how the class stores or arranges its data — once they read the storage directly it becomes a public contract you cannot change. Private fields on the same class hide implementation; you do not need a second class for that. Read-only to callers can mean return a copy or immutable view from a property — it does not require a frozen class or a second type to hold build steps.

Evaluate the current context against this rule (hide-inner-details):

### `keep-operations-small-focused`

Keep each operation short enough to read as one thought — under 20 statements. A multi-line call, list, or string initializer is one statement. When it grows, extract a private helper whose name says why that slice exists.

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L364): Operation `append_log`: Operation 'append_log' is 25 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L406): Operation `handoff_session`: Operation 'handoff_session' is 52 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/session/session_log.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session_log.py#L394): Operation `instructions`: Operation 'instructions' is 38 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [space/session/session_log.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session_log.py#L146): Operation `timestamp`: Operation 'timestamp' is a staticmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/session/sessions.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\sessions.py#L44): Operation `of_project`: Operation 'of_project' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/session/throwaway_project.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\throwaway_project.py#L26): Operation `close_all`: Operation 'close_all' is a classmethod; prefer an instance operation.

Evaluate the current context against this rule (prefer-instance-operations):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

Evaluate the current context against this rule (keep-operations-single-responsibility):

### `simplify-control-flow`

Handle the failing or empty cases first and return. Keep the main path flat. Do not nest more than three levels — deeper than that you cannot tell which conditions hold on a given line without reading back up, and that is where the unhandled branch hides.

Evaluate the current context against this rule (simplify-control-flow):

### `errors-out-of-existence`

For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [space/session/session_log.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session_log.py#L333): Operation `read_loop`: Operation 'read_loop' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/session/session_log.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session_log.py#L343): Operation `append_note`: Operation 'append_note' raises on an empty or missing value; return a quiet result instead.

Evaluate the current context against this rule (errors-out-of-existence):

### `no-prototype-swapping`

An object keeps the class it was built as. Do not change it afterwards with `Object.setPrototypeOf`, `__proto__ =`, or `__class__ =`. When a subclass needs to make its own instances, give the base an overridable factory (`blank()`) or build the right class directly. A swapped object skips its constructor, so fields the subclass sets up are missing and nothing tells you.

Evaluate the current context against this rule (no-prototype-swapping):

### `use-intention-revealing-names`

Name each class, property, operation, and parameter so it answers why it exists. Do not abbreviate.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L113): Parameter `value`: Parameter 'value' does not reveal intent.

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

### `deep-module`

Keep most classes private (at most **40%** public) in each first-class module. A first-class module is a folder that owns `.context/module-context.md`. Nested folders that also own that file are separate modules — respect them. Nested folders that do not own it roll up to the nearest enclosing module-context folder, or to the folder you are querying if none sits in between. Count classes, not operations: a public method on a hidden class is not a second seam. Every public class is a signature you cannot change without editing every caller, so public classes are much harder to refactor than private ones.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [space/session](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session#L1): Module `session`: Module 'session' splits into many tiny classes (24); prefer a deep module with a small public surface.

Evaluate the current context against this rule (deep-module):

### `keep-classes-single-responsibility`

Give each class one reason to change.

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [space/session/practice_session_output.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\practice_session_output.py#L76): OoadClass `PracticeSessionOutput`: Class 'PracticeSessionOutput' exposes 11 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L66): OoadClass `Session`: Class 'Session' exposes 29 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/session/session_log.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session_log.py#L135): OoadClass `SessionLog`: Class 'SessionLog' exposes 19 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/session/sessions.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\sessions.py#L32): OoadClass `Sessions`: Class 'Sessions' exposes 10 public operations (budget ~9). Split responsibilities.

Evaluate the current context against this rule (keep-classes-single-responsibility):

### `limit-operation-parameters`

Have callers pass intent, not setup. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L364): Operation `append_log`: Operation 'append_log' takes 6 parameters (maximum 3, excluding self).

Evaluate the current context against this rule (limit-operation-parameters):

### `use-explicit-dependencies`

Pass every collaborator through the constructor. Do not reach for a global or construct a collaborator inside construction. A collaborator the class fetches or builds itself cannot be swapped, so the class can only ever run against that one implementation.

**Graph violations:** 6

- [X] **ERROR** **[graph rule]** - [space/session/decision_records.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\decision_records.py#L11): OoadClass `DecisionRecords`: Class 'DecisionRecords' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [space/session/handoffs.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\handoffs.py#L12): OoadClass `Handoffs`: Class 'Handoffs' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [space/session/practice_session_output.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\practice_session_output.py#L42): OoadClass `RememberedFolders`: Class 'RememberedFolders' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L66): OoadClass `Session`: Class 'Session' constructs 'SessionLog' inside its constructor.
- [X] **ERROR** **[graph rule]** - [space/session/sessions.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\sessions.py#L32): OoadClass `Sessions`: Class 'Sessions' constructs 'Repo' inside its constructor.
- [X] **ERROR** **[graph rule]** - [space/session/throwaway_project.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\throwaway_project.py#L11): OoadClass `ThrowawayProject`: Class 'ThrowawayProject' constructs 'Path' inside its constructor.

Evaluate the current context against this rule (use-explicit-dependencies):

---

# AI judgment (round 3, code fidelity, `space/session`)

Each finding says **new** or **left** (from rounds 1–2). The model-fidelity judgment of the same folder is in `clean-engineering-model-20261107T090151.md`; class-shape findings are not repeated here.

Graph hits: the same as at model fidelity — `Path` constructions dismissed (value conversions), `SessionLog`/`SessionFiles` parts dismissed (composition), `handoff_session` and `SessionLog.instructions` length dismissed (prompt prose), `read_loop` raise dismissed (a loop never marked is a caller error), setter `value` dismissed; `append_log` parameters, `append_note` raise, `SessionLog.timestamp` and `ThrowawayProject.close_all` confirmed.

## Judgment — `space/session/session.py`

### `hold-state-on-the-object-not-in-parameters` — Fail
- session.py:406 `handoff_session`: takes `session` (a session.json string) on an object that is that session (new).
- session.py:364 `append_log`: three chat strings instead of the ChatPointer the session holds (left, P-24).

### `hide-inner-details` — Fail
- session.py:181 `save_fields(**values)`: any caller writes any key into session.json; `PracticeSessionOutput._save` and `_save_overrides` (practice_session_output.py:188, :242) and `Sessions.create` (sessions.py:116) all reach the file layout through it, so session.json's shape is a public contract (new).

### `prefer-instance-operations` — Fail
- session.py:41 `name_of`: module-level function re-exported from `space/session/__init__.py` (left, §4).

## Judgment — `space/session/session_log.py`

### `no-legacy-api-after-refactor` — Fail
- session_log.py:27 `_FORMER_VERBS = {"pull": "move"}`: older logs' verb kept as an alias (left, §7).

### `errors-out-of-existence` — Fail
- session_log.py:347 `append_note`: `ValueError("note is required")` for an empty note, a generic exception for an ordinary empty input (new).

### `prefer-instance-operations` — Fail
- session_log.py:145 `timestamp`: `@staticmethod`, and `_paths_from_tool_input` (:387) too (new, low).

## Judgment — `space/session/practice_session_output.py`

### `simplify-control-flow` — Fail
- practice_session_output.py:357 `has_output`: two nested loops with two conditions inside repeat the pattern logic of `_declared_files` (:366): `path_from_top`, `_named_parts_as_wildcards`, `"*" in pattern`, `repo.file_manager.find` (new, low).

### `eliminate-duplication` — Fail
- practice_session_output.py:359 `has_output`: the "declared path or pattern" decision is written twice, here and in `_declared_files` (:371) (new, low).

### `use-intention-revealing-names` — Fail
- practice_session_output.py:207 `working_fidelity`: `getattr(self.guideline.fidelities, "current", None)` and `getattr(self.guideline, "format", "")` (:213) read a guidance's own attributes defensively, hiding which contract the code relies on (new, low).

## Judgment — `space/session/session_files.py`

### `no-redundant-relationship-paths` — Fail
- session_files.py:45 `read`: reads through `self._session.repo.file_manager` while `file_manager` (:23) builds a second FileManager rooted at the practices' folders; `FidelitySessionOutput` also uses the repo's. Two file managers per session, and `Session.repo` makes a new `Repo` on every access (new, low).

## Judgment — `space/session/session_probe.py`

### `keep-operations-small-focused` — Fail
- session_probe.py:28 `_probe_in`: about 30 statements that build a project, run two actions, read the log, check five facts and build a report (left, P-26 probes).

### `never-swallow-exceptions` — Fail
- session_probe.py:71 `_probe_in`: `except Exception` turns any failure, including a bug in the probe, into a red report with one line of text and no trace (new; the rule's new text names "substitutes a fallback").

### `eliminate-duplication` — Fail
- session_probe.py:18 `probe_session_log`: calls `ensure_import_path`, which exists twice (left, §4).

Passes: no bare `except`, no prototype swapping, named exceptions (`SessionNotFoundError`, `UnknownPracticeError`, `LoopNotFoundError`, `PracticeRootInContextError`, `SessionNameRequiredError`).
