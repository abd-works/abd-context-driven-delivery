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

**Generated:** 2026-11-07 09:37:59 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 49
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

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [harness/installation/files.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\files.py#L78): Operation `relative_path`: Operation 'relative_path' is 24 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/installation/files.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\files.py#L280): Operation `write`: Operation 'write' is 37 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/installation/templates/typescript/cdd-files.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\templates\typescript\cdd-files.tsx#L29): Operation `SourceViewGenerated`: Operation 'SourceViewGenerated' is 27 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/installation/templates/typescript/cdd-files.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\templates\typescript\cdd-files.tsx#L63): Operation `FileListViewGenerated`: Operation 'FileListViewGenerated' is 29 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

**Graph violations:** 6

- [X] **ERROR** **[graph rule]** - [harness/installation/_examples/note.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\_examples\note.py#L36): Operation `new`: Operation 'new' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\destination.py#L55): Operation `languages_of`: Operation 'languages_of' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\destination.py#L83): Operation `fields_of`: Operation 'fields_of' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\destination.py#L115): Operation `fields_of`: Operation 'fields_of' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\destination.py#L149): Operation `is_reference`: Operation 'is_reference' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\destination.py#L154): Operation `fields_of`: Operation 'fields_of' is a classmethod; prefer an instance operation.

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

**Graph violations:** 5

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

Evaluate the current context against this rule (limit-comments):

### `avoid-vague-parameter-names`

Do not name parameters `data`, `options`, `info`, or other placeholders that could mean anything. A vague name hides what the caller must supply and what the operation does with it.

**Graph violations:** 6

- [X] **ERROR** **[graph rule]** - [harness/installation/context_config.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\context_config.py#L64): Operation `save`: Parameter 'data' in 'save' is vague.
- [X] **ERROR** **[graph rule]** - [harness/installation/context_config.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\context_config.py#L64): Parameter `data`: Parameter 'data' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/installation/templates/typescript/cdd-connection.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\templates\typescript\cdd-connection.ts#L97): Operation `request`: Parameter 'params' in 'request' is vague.
- [X] **ERROR** **[graph rule]** - [harness/installation/templates/typescript/cdd-connection.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\templates\typescript\cdd-connection.ts#L97): Operation `request`: Parameter 'params' in 'request' is vague.
- [X] **ERROR** **[graph rule]** - [harness/installation/templates/typescript/cdd-connection.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\templates\typescript\cdd-connection.ts#L97): Parameter `params`: Parameter 'params' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/installation/templates/typescript/cdd-connection.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\templates\typescript\cdd-connection.ts#L97): Parameter `params`: Parameter 'params' is vague. Use a domain-specific name.

Evaluate the current context against this rule (avoid-vague-parameter-names):

### `deep-module`

Keep most classes private (at most **40%** public) in each first-class module. A first-class module is a folder that owns `.context/module-context.md`. Nested folders that also own that file are separate modules — respect them. Nested folders that do not own it roll up to the nearest enclosing module-context folder, or to the folder you are querying if none sits in between. Count classes, not operations: a public method on a hidden class is not a second seam. Every public class is a signature you cannot change without editing every caller, so public classes are much harder to refactor than private ones.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/installation](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation#L1): Module `installation`: Module 'installation' splits into many tiny classes (41); prefer a deep module with a small public surface.

Evaluate the current context against this rule (deep-module):

### `keep-classes-single-responsibility`

Give each class one reason to change.

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [harness/installation/context_config.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\context_config.py#L23): OoadClass `ContextConfig`: Class 'ContextConfig' exposes 10 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/installation/templates/typescript/cdd-connection.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\templates\typescript\cdd-connection.ts#L37): OoadClass `names`: Class 'names' exposes 10 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/installation/templates/typescript/cdd-connection.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\templates\typescript\cdd-connection.ts#L38): OoadClass `CddConnection`: Class 'CddConnection' exposes 10 public operations (budget ~9). Split responsibilities.

Evaluate the current context against this rule (keep-classes-single-responsibility):

### `limit-operation-parameters`

Have callers pass intent, not setup. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [harness/installation/files.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\files.py#L78): Operation `relative_path`: Operation 'relative_path' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/installation/templates/typescript/cdd-connection.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\templates\typescript\cdd-connection.ts#L97): Operation `request`: Operation 'request' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/installation/templates/typescript/cdd-connection.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\templates\typescript\cdd-connection.ts#L97): Operation `request`: Operation 'request' takes 4 parameters (maximum 3, excluding self).

Evaluate the current context against this rule (limit-operation-parameters):

### `missing-module-context`

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/installation/_examples/note.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\_examples\note.py#L19): OoadClass `Note`: Module folder '_examples' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.

Evaluate the current context against this rule (missing-module-context):

### `use-explicit-dependencies`

Pass every collaborator through the constructor. Do not reach for a global or construct a collaborator inside construction. A collaborator the class fetches or builds itself cannot be swapped, so the class can only ever run against that one implementation.

**Graph violations:** 5

- [X] **ERROR** **[graph rule]** - [harness/installation/context_config.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\context_config.py#L23): OoadClass `ContextConfig`: Class 'ContextConfig' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\destination.py#L207): OoadClass `Installation`: Class 'Installation' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/installation/language_adapter.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\language_adapter.py#L180): OoadClass `TypeScriptOperation`: Class 'TypeScriptOperation' constructs 'Name' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/installation/language_adapter.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\language_adapter.py#L257): OoadClass `TypeScriptToolset`: Class 'TypeScriptToolset' constructs 'PurePosixPath' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/installation/repository_toolsets.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\repository_toolsets.py#L17): OoadClass `RepositoryToolsets`: Class 'RepositoryToolsets' constructs 'Path' inside its constructor.

Evaluate the current context against this rule (use-explicit-dependencies):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 13

- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\destination.py#L55): Parameter `toolset`: Parameter 'toolset' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\destination.py#L115): Parameter `operation`: Parameter 'operation' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\destination.py#L143): Parameter `getter`: Parameter 'getter' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\destination.py#L232): Parameter `toolset`: Parameter 'toolset' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\destination.py#L255): Parameter `tool`: Parameter 'tool' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\destination.py#L258): Parameter `tool`: Parameter 'tool' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/installation/files.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\files.py#L78): Parameter `toolset`: Parameter 'toolset' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/installation/files.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\files.py#L78): Parameter `member`: Parameter 'member' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/installation/files.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\files.py#L276): Parameter `member`: Parameter 'member' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/installation/files.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\files.py#L280): Parameter `tool`: Parameter 'tool' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/installation/language_adapter.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\language_adapter.py#L739): Parameter `toolset`: Parameter 'toolset' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/installation/templates/typescript/cdd-connection.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\templates\typescript\cdd-connection.ts#L97): Parameter `label`: Parameter 'label' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/installation/templates/typescript/cdd-connection.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installation\templates\typescript\cdd-connection.ts#L97): Parameter `label`: Parameter 'label' is missing a type annotation.

Evaluate the current context against this rule (use-typed-signatures):


---

# Judgment (round 3, branch 42ab935c)

Judged the Python bodies of `harness/installation` (specs, `_examples`, and the TypeScript templates excluded) against the code rules. **Graph hits dismissed:** every hit in `templates/typescript/*` (another format's template files); `_examples/note.py`; `Path` / `PurePosixPath` / `Name` built in constructors (value normalising); ContextConfig's ten operations (one file, one job); `toolset` / `operation` / `getter` typed `Any` on the mark classes and `record`; `deep-module` (count includes templates and `_examples`). Leads dismissed: the `except Exception` at repository_toolsets.py:107 logs the traceback and returns the failed modules to the caller; `ContextConfig.update(**sections)` takes named configuration sections, not packed setup.

## Judgment — `harness/installation/files.py`

### `keep-operations-small-focused` — Fail
- files.py:280 **new** — `write` is 31 statements: it filters by kind, assembles the body, appends schema and invoke text, works out the path, adds front matter, rewrites references, and writes the file.
- files.py:78 **new** — `relative_path` is 21 statements, one branch per destination, each with its own per-IDE choice.
- files.py:375 **new** — `_rules_front_matter` is 24 statements, mixing description extraction, `appliesTo` reading, and two front-matter formats.

### `eliminate-duplication` — Fail
- files.py:127 **new** — `_command_stem` tests `practice_guidance` and reads `slug` in two consecutive blocks, the second repeating the first with a suffix.

### `no-legacy-api-after-refactor` — Fail
- files.py:276 **new** — `render(section, member, tool)` ignores `member` and `tool`; dead parameters every caller still passes.

## Judgment — `harness/installation/destination.py`

### `prefer-instance-operations` — Fail
- destination.py:55 **left from I-F16** — `LanguageAdapter.languages_of(toolset)` is a classmethod that takes the object it reads; the I-F16 free functions became classmethods on the marks (`Identity.fields_of`, `Edits.fields_of`, `DataField.is_reference`, `DataField.fields_of`), still not factories.
- destination.py:154 **left from I-F16** — `DataField.fields_of(data_class)` walks a class's MRO from a classmethod; the same shape as above.

## Judgment — `harness/installation/context_config.py`

### `eliminate-duplication` — Fail
- context_config.py:91 **new** — `guideline` and `practice_folder` (line 98) repeat the same `replace("-", "_").casefold()` key lookup; `set_guidelines` and `set_practice_folders` (lines 105, 113) repeat the same text-or-mapping conversion.

### `no-legacy-api-after-refactor` — Fail
- context_config.py:10 **new** — `guidelines.config` and `practice-folders.config` are still read as a second source beside `config.json`; the old format stays a live entry point instead of being converted once.

## Passes

B17 at files.py:163 is fixed: a failure reading an operation's instructions raises `InstructionsUnreadableAtInstall` with the operation and cause, so no wrong slash command is installed. B6 holds: an unreadable `config.json` raises `MalformedContextConfigError`. The I-F16 free functions `data_fields_of`, `omitted_from_catalog`, `omitted_from_deploy` no longer exist anywhere. No banned words in names.
