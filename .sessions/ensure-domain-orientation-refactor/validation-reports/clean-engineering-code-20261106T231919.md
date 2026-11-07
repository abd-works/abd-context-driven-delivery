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

**Generated:** 2026-11-06 23:19:19 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 45
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

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [space/session/chat_pointer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\chat_pointer.py#L101): Operation `in_chat_file`: Operation 'in_chat_file' is 28 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L885): Operation `append_log`: Operation 'append_log' is 36 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L1187): Operation `record_failure`: Operation 'record_failure' is 22 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L1219): Operation `keep_log`: Operation 'keep_log' is 40 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

**Graph violations:** 15

- [X] **ERROR** **[graph rule]** - [space/session/chat_pointer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\chat_pointer.py#L42): Operation `of`: Operation 'of' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/session/chat_pointer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\chat_pointer.py#L53): Operation `taken_from`: Operation 'taken_from' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/session/chat_pointer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\chat_pointer.py#L78): Operation `serving`: Operation 'serving' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/session/chat_pointer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\chat_pointer.py#L88): Operation `in_log_line`: Operation 'in_log_line' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/session/chat_pointer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\chat_pointer.py#L101): Operation `in_chat_file`: Operation 'in_chat_file' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L525): Operation `forget_current`: Operation 'forget_current' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L534): Operation `refresh_current_from_repo`: Operation 'refresh_current_from_repo' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L588): Operation `new`: Operation 'new' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L635): Operation `timestamp`: Operation 'timestamp' is a staticmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L797): Operation `switch`: Operation 'switch' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L843): Operation `mark_loop`: Operation 'mark_loop' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L863): Operation `read_loop`: Operation 'read_loop' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L885): Operation `append_log`: Operation 'append_log' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/session/throwaway_project.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\throwaway_project.py#L30): Operation `close_all`: Operation 'close_all' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/session/throwaway_project.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\throwaway_project.py#L58): Operation `close_all`: Operation 'close_all' is a classmethod; prefer an instance operation.

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

- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L863): Operation `read_loop`: Operation 'read_loop' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L885): Operation `append_log`: Operation 'append_log' raises on an empty or missing value; return a quiet result instead.

Evaluate the current context against this rule (errors-out-of-existence):

### `no-prototype-swapping`

An object keeps the class it was built as. Do not change it afterwards with `Object.setPrototypeOf`, `__proto__ =`, or `__class__ =`. When a subclass needs to make its own instances, give the base an overridable factory (`blank()`) or build the right class directly. A swapped object skips its constructor, so fields the subclass sets up are missing and nothing tells you.

Evaluate the current context against this rule (no-prototype-swapping):

### `use-intention-revealing-names`

Name each class, property, operation, and parameter so it answers why it exists. Do not abbreviate.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L505): Parameter `value`: Parameter 'value' does not reveal intent.

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

- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L204): OoadClass `PracticeSessionOutput`: Class 'PracticeSessionOutput' exposes 13 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L477): OoadClass `Session`: Class 'Session' exposes 44 public operations (budget ~9). Split responsibilities.

Evaluate the current context against this rule (keep-classes-single-responsibility):

### `limit-operation-parameters`

Have callers pass intent, not setup. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L588): Operation `new`: Operation 'new' takes 7 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L797): Operation `switch`: Operation 'switch' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L885): Operation `append_log`: Operation 'append_log' takes 6 parameters (maximum 3, excluding self).

Evaluate the current context against this rule (limit-operation-parameters):

### `missing-module-context`

**Graph violations:** 15

- [X] **ERROR** **[graph rule]** - [space/session/chat_pointer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\chat_pointer.py#L26): OoadClass `ChatPointer`: Module folder 'session' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [space/session/current_session_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\current_session_spec.py#L1): OoadClass `_module`: Module folder 'session' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L73): OoadClass `PracticeRootInContextError`: Module folder 'session' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L88): OoadClass `SessionNameRequiredError`: Module folder 'session' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L98): OoadClass `Loop`: Module folder 'session' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L148): OoadClass `SessionNotFoundError`: Module folder 'session' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L156): OoadClass `UnknownPracticeError`: Module folder 'session' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L165): OoadClass `LogEntry`: Module folder 'session' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L204): OoadClass `PracticeSessionOutput`: Module folder 'session' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L477): OoadClass `Session`: Module folder 'session' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [space/session/session_diagnostics.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session_diagnostics.py#L22): OoadClass `SessionDiagnostics`: Module folder 'session' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [space/session/session_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session_probe.py#L1): OoadClass `_module`: Module folder 'session' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [space/session/session_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session_spec.py#L1): OoadClass `_module`: Module folder 'session' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [space/session/throwaway_project.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\throwaway_project.py#L14): OoadClass `ThrowawayProject`: Module folder 'session' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [space/session/throwaway_project.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\throwaway_project.py#L46): OoadClass `ProjectCall`: Module folder 'session' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.

Evaluate the current context against this rule (missing-module-context):

### `use-explicit-dependencies`

Pass every collaborator through the constructor. Do not reach for a global or construct a collaborator inside construction. A collaborator the class fetches or builds itself cannot be swapped, so the class can only ever run against that one implementation.

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [space/session/chat_pointer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\chat_pointer.py#L26): OoadClass `ChatPointer`: Class 'ChatPointer' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L477): OoadClass `Session`: Class 'Session' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [space/session/throwaway_project.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\throwaway_project.py#L14): OoadClass `ThrowawayProject`: Class 'ThrowawayProject' constructs 'Path' inside its constructor.

Evaluate the current context against this rule (use-explicit-dependencies):


---

# AI judgment (clean-engineering-code, space/session)

Graph hits dismissed as false positives:
- `prefer-instance-operations` chat_pointer.py:42 `of`, :53 `taken_from`, :88 `in_log_line`, :101 `in_chat_file`: named constructors that build a ChatPointer from text (mapping factories). :78 `serving` sets and resets a ContextVar that belongs to the class. throwaway_project.py:30 and :58 `close_all`: spec fixture registries.
- `keep-operations-small-focused` session.py:885 `append_log`: about 10 statements; the docstring makes it long. session.py:1219 `keep_log`: one return of one string (judged under single responsibility below).
- `use-intention-revealing-names` session.py:505 `value`: the parameter of a property setter.
- `use-explicit-dependencies` (all three): building a `Path` from a constructor argument converts a value; it does not fetch a collaborator.

Graph hits confirmed: `keep-operations-small-focused` chat_pointer.py:101, session.py:1187; `prefer-instance-operations` session.py:525, :534, :588, :635, :797, :843, :863, :885; `errors-out-of-existence` session.py:863, :885; `keep-classes-single-responsibility` session.py:204, :477; `limit-operation-parameters` session.py:588, :797, :885; `missing-module-context` (space/session/.context holds session-context.md but no module-context.md).

## Judgment — `space/session/session.py`

### `do-not-invent-parallel-object-models` — Fail
- session.py:424 `output_paths_of`: PracticeSessionOutput answers a fidelity's output paths, files and existing output (`files_of` :436, `has_output_of` :445) from a fidelity handed in, and FidelityGuidance.output_paths/files/has_declared_output (harness/guidance/guidance.py:663-679) only call back here with `self`. The fidelity in this session (its root override and per-format file name in session.json `outputs[practice][fidelity]`) has no object of its own, so one answer has two entry points and the fidelity's state lives in the practice's dict.
- session.py:49 `_KNOWN_ACTIONS`: a hand-written action list that Loop._action_from_entries (:140) scans log words against; the actions catalogue already names the actions, and tools/prompt_notify keeps a third copy (`_FALLBACK_ACTIONS`).
- session.py:489 `_parent_folders`: the repository's `.context/practices.json` (each practice's remembered folders) is held on Session as a dict and written by `_write_practices_json` (:1332), while the practice's default folder lives in `.context/config.json` (ContextConfig) and its chosen root in session.json `outputs`. Three stores say where one practice works; PracticeSessionOutput owns the data but Session keeps the file.

### `hold-state-on-the-object-not-in-parameters` — Fail
- session.py:424 `output_paths_of`: takes the fidelity as a parameter; the fidelity should hold its session output and answer `output_paths()` itself (also :436 `files_of`, :445 `has_output_of`).
- session.py:843 `mark_loop`: a classmethod that acts on `cls.current()`, the global current session, not on the session the call is for; a call made for a board ticket's session marks the loop in whichever session the chat has open (bug 10). Same at :863 `read_loop` and :885 `append_log`.
- session.py:885 `append_log`: three chat strings (`conversation_id`, `transcript_path`, `transcript_lines`) are passed on every call and turned into a ChatPointer by `_note_chat_given` (:1055); the caller should hand over the ChatPointer (P-24). Same at :843 `mark_loop`.
- session.py:244 `guideline` setter: every action assigns its own guidance onto the shared session's practice (`practice.guideline = item` in guidance_actions.py:308), so later readers see the last action's fidelity and format (P-21 still open).
- session.py:621 `from_file`: the session travels as a session.json path string on every board command and is loaded again per call (P-2, P-13); `PracticeSessionOutput.load(session, practice)` at :220 does the same with two strings.

### `hide-inner-details` — Fail
- session.py:247 `guideline` setter: calls `guidance._attach_workspace(...)`, a private member of PracticeGuidance.
- session.py:262 `_folders`: PracticeSessionOutput reaches into Session's private members `_stored_folders`, `_fields` (:304, :358), `_save_fields` (:308, :362), `_write_practices_json` (:280), `_repo` (:449, :463) and `_worked_on_files` (:441); the practice's stored state is laid out inside Session, so neither class can change its storage alone.
- session.py:1019 `loop_at`: Session writes `Loop._session` from outside (also :1066, :1281) instead of passing the session to Loop's constructor.

### `keep-classes-single-responsibility` — Fail
- session.py:477 `Session`: 44 public operations across a per-project current-session registry (class-level `_current_by_project`), folder lifecycle (`new`, `switch`, `close`, `move_to_closed/archive/backlog`, `reopen`), session.json fields, session.log writing and parsing (loops, chat pointers, injected rules, failures), the practice registry, practices.json storage, file listing (`files`, `folder_files`, `read_file`), the file manager, and agent instruction text (`keep_log`). Root cause 1.11 is still open; logging and chat pointer handling are the first candidates to move out.
- session.py:204 `PracticeSessionOutput`: 13 public operations; it holds the practice's on/off flag, root, folders, graph and formats, plus each fidelity's outputs, which belong on a fidelity-in-session object.
- session.py:1219 `keep_log`: a domain method returns 35 lines of agent instructions, and `new` (:588) and `switch` (:797) return that text instead of the Session they opened.

### `prefer-instance-operations` — Fail
- session.py:525 `forget_current`, :534 `refresh_current_from_repo`, :797 `switch`, :843 `mark_loop`, :863 `read_loop`, :885 `append_log`: the class doubles as the registry of current sessions; operations that act on one session are classmethods that look that session up globally.
- session.py:588 `new`: named like a factory but returns the `keep_log` string, so callers (session_probe.py:37-38) look the session up again with `Session.current()`.
- session.py:635 `timestamp`: staticmethod formatting a time; :1153 `_paths_from_tool_input`, :1298 `_read_session_folder_json`, :1315 `_repo_holding` likewise.

### `errors-out-of-existence` — Fail
- session.py:874 `read_loop`: raises ValueError when the log has no loop yet, an ordinary state of a new session; :877 raises again when a numbered loop is absent.
- session.py:1052 `_resolve_append_loop`: raises ValueError when no loop marker exists, so `append_log` fails on an empty log instead of writing into loop 1.

### `use-exceptions-properly` — Fail
- session.py:874 `read_loop`: raises a bare ValueError with a message for missing loops; also :913, :1044, :1046, :1052. Callers cannot tell a missing loop from a bad argument.

### `keep-operations-single-responsibility` — Fail
- session.py:1187 `record_failure`: formats the trace, appends to session.err, counts its lines, and writes the session.log pointer line in one operation.

### `limit-operation-parameters` — Fail
- session.py:588 `new`: seven parameters, of which `title`, `scope` and `parent` describe the ticket the session is for; :797 `switch` takes four location values (P-29), :885 `append_log` six.

### `eliminate-duplication` — Fail
- session.py:429 `output_paths_of`: computes the practice root as fidelity override, else chosen root, else configured folder, else the workpath; `_default_folder` (:376) and `folder` (:384) also fall back to the practice's `default_workspace_folder` (harness, packages). For a pattern practice with no config, `folder` is `work/harness` while its fidelity outputs resolve under `work/`, so the file manager's roots and the declared outputs disagree.
- session.py:1072 `_loop_marker_number`: the same marker parse is written again in `_max_loop_number_from_log` (:1029).
- session.py:84 `PracticeRootInContextError.__init__`: assigns `practice` and `root` twice (:78-79 and :84-85).
- session.py:1111 `log_agent_tool`: a wrapper that only trims the name and calls `log_tool` (:1118), which trims it again; two entry points for one log line.

### `use-intention-revealing-names` — Fail
- session.py:519 `_slot`: banned word (slots) for "the current session of this checkout"; `slot` variables at :537 and :813.
- session.py:1260 `_bind_new`: banned word (binding); the operation creates the session folder.
- session.py:489 `_parent_folders`: holds each practice's remembered folders from practices.json, not parent folders.

### `no-legacy-api-after-refactor` — Fail
- session.py:1318 `_repo_holding`: still recognises `LEGACY_SESSIONS_FOLDER` (`sessions/`); Repo.session_folder (repo.py:1147) also searches it, so one folder has two names.
- session.py:42 `_FORMER_VERBS`: `pull` is still read as `move`, keeping a second verb alive for one log entry type.

### `missing-module-context` — Fail
- session.py:477 `Session`: space/session/.context has session-context.md but no module-context.md, so the module's seam, dependencies and constraints have no agreed home.

## Judgment — `space/session/chat_pointer.py`

### `keep-operations-small-focused` — Fail
- chat_pointer.py:101 `in_chat_file`: parses headers, finds the body and counts lines in one 28-line operation; the header parse wants its own helper.

### `eliminate-duplication` — Fail
- chat_pointer.py:192 `_claude_transcript_of`: globs `*/{id}.jsonl` under the Claude projects folder; tools/chat/chat.py:303 `_transcript` does the same with a different environment variable (`CDD_CLAUDE_PROJECTS` against `CLAUDE_CONFIG_DIR`), so the two can find different transcripts for one chat.

### `use-intention-revealing-names` — Fail
- chat_pointer.py:36 `__init__`: parameter `id` shadows the builtin and says less than `chat_id`, which `of` (:42) already uses; :201 `_event_text(line, line_no)` abbreviates.

## Judgment — `space/session/session_diagnostics.py`

### `prefer-instance-operations` — Fail
- session_diagnostics.py:12 `write_session_diagnostics`: a free function that takes the Installer first and does its work (`installer.write_diagnostics_section`), the P-26 pattern; it belongs on SessionDiagnostics or the Installer.

### `use-explicit-dependencies` — Fail
- session_diagnostics.py:35 `session_diagnostics`: builds `Installer()` itself, so the probe can only run against the real installer.

## Judgment — `space/session/session_probe.py`

### `use-exceptions-properly` — Fail
- session_probe.py:78 `_probe_in`: `except Exception` turns every failure, programming errors included, into a red report; catch the failures the probe expects.

### `hold-state-on-the-object-not-in-parameters` — Fail
- session_probe.py:37 `_probe_in`: `Session.new` returns text, so the probe drops it and finds the session again through the global `Session.current()` (:38, :52).

Passes: `no-prototype-swapping`, `simplify-control-flow`, `provide-meaningful-context` and `limit-comments` on the session module; throwaway_project.py passes every rule (its graph hits are dismissed above).
