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

**Generated:** 2026-11-07 00:06:48 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 9
**Rules with graph hits:** 5
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

Evaluate the current context against this rule (keep-operations-small-focused):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance_actions\guidance_actions.py#L497): Operation `ref_for`: Operation 'ref_for' is a classmethod; prefer an instance operation.

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

### `avoid-vague-parameter-names`

Do not name parameters `data`, `options`, `info`, or other placeholders that could mean anything. A vague name hides what the caller must supply and what the operation does with it.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance_actions\guidance_actions.py#L426): Operation `inject_rules`: Parameter 'payload' in 'inject_rules' is vague.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance_actions\guidance_actions.py#L426): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.

Evaluate the current context against this rule (avoid-vague-parameter-names):

### `keep-classes-single-responsibility`

Give each class one reason to change.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance_actions\guidance_actions.py#L77): OoadClass `GuidanceAction`: Class 'GuidanceAction' exposes 10 public operations (budget ~9). Split responsibilities.

Evaluate the current context against this rule (keep-classes-single-responsibility):

### `missing-module-context`

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance_actions\guidance_actions.py#L17): OoadClass `GuidanceRef`: Module folder 'guidance_actions' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance_actions\guidance_actions.py#L77): OoadClass `GuidanceAction`: Module folder 'guidance_actions' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance_actions\guidance_actions.py#L491): OoadClass `GuidanceCatalog`: Module folder 'guidance_actions' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.

Evaluate the current context against this rule (missing-module-context):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance_actions\guidance_actions.py#L328): Parameter `operation`: Parameter 'operation' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance_actions\guidance_actions.py#L335): Parameter `operation`: Parameter 'operation' is missing a type annotation.

Evaluate the current context against this rule (use-typed-signatures):

## Judgment — `harness/guidance_actions/guidance_actions.py`

### `do-not-invent-parallel-object-models` — Fail
- guidance_actions.py:491 `GuidanceCatalog`: a third practice registry, built by scanning `cdd_guidance/practices` and instantiating every practice, beside `PracticeCatalogue._REFS` (harness/guidance/practice_catalogue.py:22) and the installer's own toolset collection. The three can disagree on which practices and fidelities exist.
- guidance_actions.py:533 `_index_ref`: registers each fidelity under up to four names (`stories-story-map`, `story_map`, `story-map`, and the practice slug), so one fidelity has several public names and lookups succeed on whichever happened to register first.

### `hide-inner-details` — Fail
- guidance_actions.py:511 `_load`: calls the Installer's private `_iter_collect_files` and `_toolset_refs_in_file`, so the installer's file walk is now a contract this module depends on.

### `never-swallow-exceptions` — Fail
- guidance_actions.py:520 `_index_ref`: a practice that fails to import (ImportError, TypeError, AttributeError, OSError, ...) is skipped with no log, so its slugs silently stop resolving and every action on it reports "unknown guidance" instead of the import error.

### `no-legacy-api-after-refactor` — Fail
- guidance_actions.py:377 `begin`: twelve lines of commented-out code after `return ""` still reference the retired `self.workspace.current_work_session` and `session.turn`; and `begin` takes `action` and never reads it.

### `hold-state-on-the-object-not-in-parameters` — Fail
- guidance_actions.py:130 `_named_session_file`: the action keeps the session's file path as a string and rebuilds `Session.from_file(...)` on each read (160) instead of holding the Session it was made for; with none named it falls back to the global `Session.current()` (162).
- guidance_actions.py:164 `start_call`: one action object serves every MCP call and resets six per-call fields kept in a thread-local; the state belongs on a per-call object (the action made for its session), not on a shared action wiped at each call.

### `missing-module-context` — Fail
- guidance_actions.py:17 `GuidanceRef`: harness/guidance_actions has no .context folder at all. Graph hits confirmed.

### `keep-classes-single-responsibility` — Fail
- guidance_actions.py:77 `GuidanceAction`: binds guidance from strings, JSON and dicts, chooses the session, keeps formats, logs to the session, and injects rules on hooks. Graph hit confirmed.

Dismissed: `prefer-instance-operations` on `ref_for` is folded into the GuidanceCatalog finding above.
