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

**Generated:** 2026-11-07 00:05:09 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 67
**Rules with graph hits:** 12
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

**Graph violations:** 8

- [X] **ERROR** **[graph rule]** - [harness/installation/files.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\files.py#L57): Operation `relative_path`: Operation 'relative_path' is 24 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/installation/files.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\files.py#L261): Operation `write`: Operation 'write' is 39 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/installation/installer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\installer.py#L292): Operation `installations_for`: Operation 'installations_for' is 27 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/installation/installer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\installer.py#L573): Operation `install_board_plugin`: Operation 'install_board_plugin' is 24 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/installation/installer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\installer.py#L686): Operation `diagnose_install`: Operation 'diagnose_install' is 22 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/installation/installer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\installer.py#L827): Operation `write_diagnostics_section`: Operation 'write_diagnostics_section' is 28 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/installation/templates/typescript/cdd-files.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\templates\typescript\cdd-files.tsx#L29): Operation `SourceViewGenerated`: Operation 'SourceViewGenerated' is 27 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/installation/templates/typescript/cdd-files.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\templates\typescript\cdd-files.tsx#L63): Operation `FileListViewGenerated`: Operation 'FileListViewGenerated' is 29 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

**Graph violations:** 9

- [X] **ERROR** **[graph rule]** - [harness/installation/_examples/note.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\_examples\note.py#L35): Operation `new`: Operation 'new' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\destination.py#L39): Operation `marks`: Operation 'marks' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\destination.py#L44): Operation `copied_flags`: Operation 'copied_flags' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\destination.py#L54): Operation `companion_flags`: Operation 'companion_flags' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\destination.py#L121): Operation `languages_of`: Operation 'languages_of' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\destination.py#L126): Operation `identity_fields_of`: Operation 'identity_fields_of' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\destination.py#L151): Operation `fields_of`: Operation 'fields_of' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\destination.py#L238): Operation `name_marked_on`: Operation 'name_marked_on' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\destination.py#L244): Operation `companion_flags`: Operation 'companion_flags' is a classmethod; prefer an instance operation.

Evaluate the current context against this rule (prefer-instance-operations):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [harness/installation/templates/typescript/cdd-connection.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\templates\typescript\cdd-connection.ts#L75): Operation `start`: Operation 'start' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/installation/templates/typescript/cdd-connection.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\templates\typescript\cdd-connection.ts#L75): Operation `start`: Operation 'start' mixes I/O-style calls with domain calculation; split responsibilities.

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

**Graph violations:** 6

- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\destination.py#L230): Parameter `fn`: Parameter 'fn' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/installation/templates/typescript/cdd-connection.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\templates\typescript\cdd-connection.ts#L132): Parameter `id`: Parameter 'id' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/installation/templates/typescript/cdd-connection.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\templates\typescript\cdd-connection.ts#L132): Parameter `id`: Parameter 'id' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/installation/templates/typescript/cdd-shared.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\templates\typescript\cdd-shared.ts#L46): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/installation/templates/typescript/cdd-views.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\templates\typescript\cdd-views.tsx#L11): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/installation/templates/typescript/cdd-views.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\templates\typescript\cdd-views.tsx#L23): Parameter `value`: Parameter 'value' does not reveal intent.

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

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/installation/installer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\installer.py#L292): Operation `installations_for`: Operation 'installations_for' has a descriptive comment.

Evaluate the current context against this rule (limit-comments):

### `avoid-vague-parameter-names`

Do not name parameters `data`, `options`, `info`, or other placeholders that could mean anything. A vague name hides what the caller must supply and what the operation does with it.

**Graph violations:** 12

- [X] **ERROR** **[graph rule]** - [harness/installation/installer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\installer.py#L827): Operation `write_diagnostics_section`: Parameter 'payload' in 'write_diagnostics_section' is vague.
- [X] **ERROR** **[graph rule]** - [harness/installation/installer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\installer.py#L827): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/installation/installer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\installer.py#L1019): Operation `ensure_mcp_server`: Parameter 'payload' in 'ensure_mcp_server' is vague.
- [X] **ERROR** **[graph rule]** - [harness/installation/installer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\installer.py#L1019): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/installation/installer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\installer.py#L1026): Operation `ensure_mcp_server_on_session_start`: Parameter 'payload' in 'ensure_mcp_server_on_session_start' is vague.
- [X] **ERROR** **[graph rule]** - [harness/installation/installer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\installer.py#L1026): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/installation/installer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\installer.py#L1030): Operation `ensure_mcp_server_after_agent_response`: Parameter 'payload' in 'ensure_mcp_server_after_agent_response' is vague.
- [X] **ERROR** **[graph rule]** - [harness/installation/installer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\installer.py#L1030): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/installation/templates/typescript/cdd-connection.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\templates\typescript\cdd-connection.ts#L97): Operation `request`: Parameter 'params' in 'request' is vague.
- [X] **ERROR** **[graph rule]** - [harness/installation/templates/typescript/cdd-connection.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\templates\typescript\cdd-connection.ts#L97): Operation `request`: Parameter 'params' in 'request' is vague.
- [X] **ERROR** **[graph rule]** - [harness/installation/templates/typescript/cdd-connection.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\templates\typescript\cdd-connection.ts#L97): Parameter `params`: Parameter 'params' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/installation/templates/typescript/cdd-connection.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\templates\typescript\cdd-connection.ts#L97): Parameter `params`: Parameter 'params' is vague. Use a domain-specific name.

Evaluate the current context against this rule (avoid-vague-parameter-names):

### `deep-module`

Keep most classes private (at most **40%** public) in each first-class module. A first-class module is a folder that owns `.context/module-context.md`. Nested folders that also own that file are separate modules — respect them. Nested folders that do not own it roll up to the nearest enclosing module-context folder, or to the folder you are querying if none sits in between. Count classes, not operations: a public method on a hidden class is not a second seam. Every public class is a signature you cannot change without editing every caller, so public classes are much harder to refactor than private ones.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/installation](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation#L1): Module `installation`: Module 'installation' splits into many tiny classes (34); prefer a deep module with a small public surface.

Evaluate the current context against this rule (deep-module):

### `keep-classes-single-responsibility`

Give each class one reason to change.

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [harness/installation/installer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\installer.py#L30): OoadClass `Installer`: Class 'Installer' exposes 23 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/installation/templates/typescript/cdd-connection.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\templates\typescript\cdd-connection.ts#L37): OoadClass `names`: Class 'names' exposes 10 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/installation/templates/typescript/cdd-connection.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\templates\typescript\cdd-connection.ts#L38): OoadClass `CddConnection`: Class 'CddConnection' exposes 10 public operations (budget ~9). Split responsibilities.

Evaluate the current context against this rule (keep-classes-single-responsibility):

### `limit-operation-parameters`

Have callers pass intent, not setup. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [harness/installation/files.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\files.py#L57): Operation `relative_path`: Operation 'relative_path' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/installation/templates/typescript/cdd-connection.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\templates\typescript\cdd-connection.ts#L97): Operation `request`: Operation 'request' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/installation/templates/typescript/cdd-connection.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\templates\typescript\cdd-connection.ts#L97): Operation `request`: Operation 'request' takes 4 parameters (maximum 3, excluding self).

Evaluate the current context against this rule (limit-operation-parameters):

### `missing-module-context`

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/installation/_examples/note.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\_examples\note.py#L18): OoadClass `Note`: Module folder '_examples' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.

Evaluate the current context against this rule (missing-module-context):

### `use-explicit-dependencies`

Pass every collaborator through the constructor. Do not reach for a global or construct a collaborator inside construction. A collaborator the class fetches or builds itself cannot be swapped, so the class can only ever run against that one implementation.

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\destination.py#L263): OoadClass `Installation`: Class 'Installation' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/installation/installer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\installer.py#L30): OoadClass `Installer`: Class 'Installer' constructs 'McpInstallation' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/installation/language_adapter.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\language_adapter.py#L170): OoadClass `TypeScriptOperation`: Class 'TypeScriptOperation' constructs 'Name' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/installation/language_adapter.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\language_adapter.py#L246): OoadClass `TypeScriptToolset`: Class 'TypeScriptToolset' constructs 'PurePosixPath' inside its constructor.

Evaluate the current context against this rule (use-explicit-dependencies):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 17

- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\destination.py#L39): Parameter `target`: Parameter 'target' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\destination.py#L58): Parameter `target`: Parameter 'target' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\destination.py#L121): Parameter `toolset`: Parameter 'toolset' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\destination.py#L126): Parameter `toolset`: Parameter 'toolset' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\destination.py#L151): Parameter `operation`: Parameter 'operation' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\destination.py#L238): Parameter `operation`: Parameter 'operation' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\destination.py#L288): Parameter `toolset`: Parameter 'toolset' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\destination.py#L311): Parameter `tool`: Parameter 'tool' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\destination.py#L314): Parameter `tool`: Parameter 'tool' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/installation/files.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\files.py#L57): Parameter `toolset`: Parameter 'toolset' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/installation/files.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\files.py#L57): Parameter `member`: Parameter 'member' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/installation/files.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\files.py#L257): Parameter `member`: Parameter 'member' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/installation/files.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\files.py#L261): Parameter `tool`: Parameter 'tool' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/installation/installer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\installer.py#L292): Parameter `tool`: Parameter 'tool' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/installation/language_adapter.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\language_adapter.py#L701): Parameter `toolset`: Parameter 'toolset' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/installation/templates/typescript/cdd-connection.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\templates\typescript\cdd-connection.ts#L97): Parameter `label`: Parameter 'label' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/installation/templates/typescript/cdd-connection.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\templates\typescript\cdd-connection.ts#L97): Parameter `label`: Parameter 'label' is missing a type annotation.

Evaluate the current context against this rule (use-typed-signatures):

## Judgment — `harness/installation/installer.py`

### `hold-state-on-the-object-not-in-parameters` — Fail
- installer.py:131 `import_path_entries`: takes an optional `repo` though the Installer holds `self.repo`; `pythonpath` (141), `pycache_prefix` (144), `ensure_import_path` (149) and `collect_toolsets` (158) repeat it. Callers hand the Installer its own repo back: harness/installation/bootstrap.py:17 `Installer(repo=root).ensure_import_path(root)`, harness/agent_tools/agent_tools_probe.py:98 `self.installer.ensure_import_path(self.installer.repo)`.

### `do-not-invent-parallel-object-models` — Fail
- installer.py:1019 `ensure_mcp_server`: builds a fresh `McpInstallation(self.ide, self.path, repo=self.repo)` though the Installer already holds one in `self._mcp` (built at 116 and again at 511), so two installation objects for one IDE can disagree.

### `no-legacy-api-after-refactor` — Fail
- installer.py:1019 `ensure_mcp_server`: takes `payload` and never reads it; the two hook wrappers at 1026 and 1030 pass it through only to keep the hook signature.

### `limit-comments` — Fail
- installer.py:1015 `diagnose_install`: the bare statements `self.diagnose_install_instructions` and `self.runtime_instructions` are evaluated for a side effect nobody can see from the line; either name the side effect as an operation or remove them.

### `never-swallow-exceptions` — Fail
- installer.py:361 `clean`: `except OSError: pass` on removing an empty folder, with no log of which folder stayed behind.

### `keep-classes-single-responsibility` — Fail
- installer.py:30 `Installer`: 23 public operations spanning Python import paths, toolset discovery, IDE file writing, clean, runtime install, the board plugin, diagnostics files, and starting the MCP server from hooks. Graph hit confirmed.

## Judgment — `harness/installation/files.py`

### `never-swallow-exceptions` — Fail
- files.py:163 `_instructions_at_install`: any exception expanding an `@agent_instructions` recipe while writing slash markdown becomes `None`, and the docstring is installed instead; a broken recipe ships a wrong command and the install reports success.

### `keep-operations-small-focused` — Fail
- files.py:261 `write`: 39 lines. Graph hit confirmed (57 `relative_path` also confirmed).

Graph hits dismissed: destination.py classmethods `marks`, `copied_flags`, `companion_flags`, `name_marked_on` are decorator-mark plumbing read from a class before any instance exists; `use-explicit-dependencies` for `Path`, `Name`, `PurePosixPath` (values, not collaborators); templates/typescript hits (generated adapter templates; judged where installed, cdd_guidance/patterns/cdd_web_domain_access); `_examples/note.py` (sample).
