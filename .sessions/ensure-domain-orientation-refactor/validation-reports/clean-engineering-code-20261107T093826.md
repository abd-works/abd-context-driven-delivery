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

**Generated:** 2026-11-07 09:38:26 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 14
**Rules with graph hits:** 6
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

- [X] **ERROR** **[graph rule]** - [harness/installer/installer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installer\installer.py#L138): Operation `installations_for`: Operation 'installations_for' is 27 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/installer/installer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installer\installer.py#L419): Operation `install_board_plugin`: Operation 'install_board_plugin' is 24 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/installer/installer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installer\installer.py#L532): Operation `diagnose_install`: Operation 'diagnose_install' is 22 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/installer/installer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installer\installer.py#L673): Operation `write_diagnostics_section`: Operation 'write_diagnostics_section' is 28 lines (max 20).

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

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/installer/installer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installer\installer.py#L138): Operation `installations_for`: Operation 'installations_for' has a descriptive comment.

Evaluate the current context against this rule (limit-comments):

### `avoid-vague-parameter-names`

Do not name parameters `data`, `options`, `info`, or other placeholders that could mean anything. A vague name hides what the caller must supply and what the operation does with it.

**Graph violations:** 6

- [X] **ERROR** **[graph rule]** - [harness/installer/installer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installer\installer.py#L673): Operation `write_diagnostics_section`: Parameter 'payload' in 'write_diagnostics_section' is vague.
- [X] **ERROR** **[graph rule]** - [harness/installer/installer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installer\installer.py#L673): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/installer/installer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installer\installer.py#L872): Operation `ensure_mcp_server_on_session_start`: Parameter 'payload' in 'ensure_mcp_server_on_session_start' is vague.
- [X] **ERROR** **[graph rule]** - [harness/installer/installer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installer\installer.py#L872): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/installer/installer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installer\installer.py#L876): Operation `ensure_mcp_server_after_agent_response`: Parameter 'payload' in 'ensure_mcp_server_after_agent_response' is vague.
- [X] **ERROR** **[graph rule]** - [harness/installer/installer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installer\installer.py#L876): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.

Evaluate the current context against this rule (avoid-vague-parameter-names):

### `keep-classes-single-responsibility`

Give each class one reason to change.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/installer/installer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installer\installer.py#L34): OoadClass `Installer`: Class 'Installer' exposes 18 public operations (budget ~9). Split responsibilities.

Evaluate the current context against this rule (keep-classes-single-responsibility):

### `use-explicit-dependencies`

Pass every collaborator through the constructor. Do not reach for a global or construct a collaborator inside construction. A collaborator the class fetches or builds itself cannot be swapped, so the class can only ever run against that one implementation.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/installer/installer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installer\installer.py#L34): OoadClass `Installer`: Class 'Installer' constructs 'McpInstallation' inside its constructor.

Evaluate the current context against this rule (use-explicit-dependencies):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/installer/installer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\installer\installer.py#L138): Parameter `tool`: Parameter 'tool' needs a domain-specific type, not a generic container.

Evaluate the current context against this rule (use-typed-signatures):


---

# Judgment (round 3, branch 42ab935c)

Judged the bodies of `harness/installer/installer.py` against the code rules. **Graph hits dismissed:** `payload` on the two `@Hook` handlers (typed `HookPayload`); `limit-comments` at line 138 (explains why, not what). Leads dismissed: `_remove_legacy_underscore_skills` cleans files an older install left on disk, it is not a legacy API; `_run_claude(claude, *args)` passes command-line words, not packed setup; `_surface_change` / `_compare_report` take the current and previous channel lists with their differences, all private helpers of one comparison.

## Judgment — `harness/installer/installer.py`

### `keep-operations-small-focused` — Fail
- installer.py:54 **new** — `__init__` is 22 statements of state-file reading, path choosing, and collaborator building.
- installer.py:232 **new** — `_remove_skills_naming_missing_mcp` is 24 statements.
- installer.py:284 **new** — `_install_run` is 22 statements orchestrating twelve steps inline.
- installer.py:648 **new** — `_append_install_log` is 23 statements and reads `diagnostics.json` twice (lines 652 and 669).
- installer.py:673 **new** — `write_diagnostics_section` is 28 lines, colour scoring mixed with file writing.

### `use-exceptions-properly` — Fail
- installer.py:377 **new** — `_install_all` catches `Exception` and raises a bare `RuntimeError("install failed for ...")`; a named install failure carrying the toolset ref would let callers handle it.
- installer.py:411 **new** — `_ensure_hook_runtime` raises a bare `RuntimeError` for a hook server that is not running.

### `provide-meaningful-context` — Fail
- installer.py:503 **new** — `timeout=120` for a `claude` command has no name.

### `no-legacy-api-after-refactor` — Fail
- installer.py:859 **new** — `diagnose_instructions` reads four markdown properties as bare statements and discards them, then returns one of them; the three dead reads remain from an older shape.

## Passes

The `repo` parameters are gone from Installer's operations; `clean` returns what it removed; state-file reads tolerate a missing file and name their colour thresholds (`_GREEN_SURFACE_CHANGE`, `_YELLOW_SURFACE_CHANGE`). No banned words in names.
