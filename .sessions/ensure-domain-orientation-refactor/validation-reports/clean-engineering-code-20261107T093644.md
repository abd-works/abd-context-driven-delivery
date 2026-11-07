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

**Generated:** 2026-11-07 09:36:43 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 40
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

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_daemon.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_daemon.py#L75): Operation `spawn`: Operation 'spawn' is 34 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_server.py#L659): Operation `handle_stdin`: Operation 'handle_stdin' is 23 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

**Graph violations:** 6

- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_server.py#L470): Operation `show_toasts_with`: Operation 'show_toasts_with' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_server.py#L492): Operation `state_path`: Operation 'state_path' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_server.py#L496): Operation `ensure`: Operation 'ensure' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hooks.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hooks.py#L84): Operation `companion_flags`: Operation 'companion_flags' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hooks.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hooks.py#L88): Operation `disabled_on`: Operation 'disabled_on' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hooks.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hooks.py#L93): Operation `normalize_event`: Operation 'normalize_event' is a classmethod; prefer an instance operation.

Evaluate the current context against this rule (prefer-instance-operations):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

Evaluate the current context against this rule (keep-operations-single-responsibility):

### `simplify-control-flow`

Handle the failing or empty cases first and return. Keep the main path flat. Do not nest more than three levels — deeper than that you cannot tell which conditions hold on a given line without reading back up, and that is where the unhandled branch hides.

Evaluate the current context against this rule (simplify-control-flow):

### `errors-out-of-existence`

For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_server.py#L496): Operation `ensure`: Operation 'ensure' raises on an empty or missing value; return a quiet result instead.

Evaluate the current context against this rule (errors-out-of-existence):

### `no-prototype-swapping`

An object keeps the class it was built as. Do not change it afterwards with `Object.setPrototypeOf`, `__proto__ =`, or `__class__ =`. When a subclass needs to make its own instances, give the base an overridable factory (`blank()`) or build the right class directly. A swapped object skips its constructor, so fields the subclass sets up are missing and nothing tells you.

Evaluate the current context against this rule (no-prototype-swapping):

### `use-intention-revealing-names`

Name each class, property, operation, and parameter so it answers why it exists. Do not abbreviate.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_server.py#L387): Parameter `item`: Parameter 'item' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hooks.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hooks.py#L77): Parameter `fn`: Parameter 'fn' does not reveal intent.

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

**Graph violations:** 22

- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_server.py#L269): Operation `is_enabled`: Parameter 'payload' in 'is_enabled' is vague.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_server.py#L269): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_server.py#L324): Operation `invoke`: Parameter 'payload' in 'invoke' is vague.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_server.py#L324): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_server.py#L610): Operation `dispatch`: Parameter 'payload' in 'dispatch' is vague.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_server.py#L610): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_spec.py#L74): Operation `on_after`: Parameter 'payload' in 'on_after' is vague.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_spec.py#L74): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_spec.py#L84): Operation `on_after`: Parameter 'payload' in 'on_after' is vague.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_spec.py#L84): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_spec.py#L94): Operation `on_stop`: Parameter 'payload' in 'on_stop' is vague.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_spec.py#L94): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_spec.py#L105): Operation `inject_rules`: Parameter 'payload' in 'inject_rules' is vague.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_spec.py#L105): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_spec.py#L115): Operation `on_used`: Parameter 'payload' in 'on_used' is vague.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_spec.py#L115): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_spec.py#L125): Operation `inject_rules`: Parameter 'payload' in 'inject_rules' is vague.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_spec.py#L125): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_spec.py#L155): Operation `on_stop`: Parameter 'payload' in 'on_stop' is vague.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_spec.py#L155): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_spec.py#L810): Operation `on_used`: Parameter 'payload' in 'on_used' is vague.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_spec.py#L810): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.

Evaluate the current context against this rule (avoid-vague-parameter-names):

### `deep-module`

Keep most classes private (at most **40%** public) in each first-class module. A first-class module is a folder that owns `.context/module-context.md`. Nested folders that also own that file are separate modules — respect them. Nested folders that do not own it roll up to the nearest enclosing module-context folder, or to the folder you are querying if none sits in between. Count classes, not operations: a public method on a hidden class is not a second seam. Every public class is a signature you cannot change without editing every caller, so public classes are much harder to refactor than private ones.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/hooks](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks#L1): Module `hooks`: Module 'hooks' splits into many tiny classes (21); prefer a deep module with a small public surface.

Evaluate the current context against this rule (deep-module):

### `keep-classes-single-responsibility`

Give each class one reason to change.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_server.py#L462): OoadClass `HookServer`: Class 'HookServer' exposes 14 public operations (budget ~9). Split responsibilities.

Evaluate the current context against this rule (keep-classes-single-responsibility):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 5

- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_daemon.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_daemon.py#L116): Parameter `inner`: Parameter 'inner' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_server.py#L387): Parameter `item`: Parameter 'item' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hooks.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hooks.py#L77): Parameter `fn`: Parameter 'fn' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hooks.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hooks.py#L88): Parameter `operation`: Parameter 'operation' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hooks.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hooks.py#L129): Parameter `tool`: Parameter 'tool' needs a domain-specific type, not a generic container.

Evaluate the current context against this rule (use-typed-signatures):


---

# Judgment (round 3, branch 42ab935c)

Judged the bodies of `hooks.py`, `hook_server.py`, and `hook_daemon.py` (specs excluded) against the code rules. **Graph hits dismissed:** the 22 `payload` hits (spec files, or typed `HookPayload`); `item` / `fn` / `operation` names and types (framework code that takes any ref or callable); `errors-out-of-existence` on `ensure` (a daemon that never starts is a failure, named by `HookStandupFailed`); `prefer-instance-operations` on `show_toasts_with` (decision 16) and `Hook.companion_flags` / `disabled_on` (mark framework class flags); `deep-module` (count includes spec classes). Leads dismissed: the four `except Exception ... continue` blocks at hook_server.py:361, 411, 650, 810 wrap the failure in `HookIllegitimateHandler`, log it with its traceback, and `diagnose` reports it, so one broken handler does not stop the others.

## Judgment — `harness/hooks/hook_server.py`

### `simplify-control-flow` — Fail
- hook_server.py:785 **new** — `_chat_injection_path` reads `self.session.session_path` without the `session is None` check the other readers make (`_write_last_chat_injected`, `_append_debug`); `ToolCall.session` is none when no sessions are registered (the daemon's import of `space/session` failed, which `RepositoryToolsets.import_modules` only logs), and then every `beforeSubmitPrompt` with a conversation id, and every result with context, raises AttributeError inside the daemon thread and the hook returns nothing.

### `hold-state-on-the-object-not-in-parameters` — Fail
- hook_server.py:611 **new** — `dispatch` saves the event on the long-lived server (`self._payload = payload`) so `_conversation_id` can read it later in `handle_stdin`; it is a field set on a shared object for one call, safe today only because the daemon serialises dispatch with a lock.

### `keep-operations-small-focused` — Fail
- hook_server.py:659 **new** — `handle_stdin` is 23 lines doing two jobs: forwarding to the daemon when `_port` is set, and parsing, dispatching, and saving chat injections when it is not.

### `prefer-instance-operations` — Fail
- hook_server.py:492 **left from §3** — `state_path` is a classmethod taking repo, not a factory; an instance already holds `_repo_root`.
- hook_server.py:496 **left from §3** — `ensure` and its helpers `_connect`, `_spawn`, `_claim_spawn`, `_release_dead_spawn`, `_wait_for_daemon`, `_release_spawn` are eight classmethods that pass repo and path among themselves.

### `eliminate-duplication` — Fail
- hook_server.py:28 **left from §4** — the import-path setup is written here, again at hook_daemon.py:17, and again in `RepositoryToolsets.ensure_import_path` (which line 42 also calls), each with a different folder list (`patterns` and `builders` differ).
- hook_server.py:664 **new** — `"127.0.0.1"` repeats `HookDaemon.HOST`.

### `no-legacy-api-after-refactor` — Fail
- hook_server.py:54 **new** — `CursorEvent.normalize` and the `Hook.normalize_event` it calls (hooks.py:93) have no caller; dead code kept alive by each other.

## Judgment — `harness/hooks/hook_daemon.py`

### `keep-operations-small-focused` — Fail
- hook_daemon.py:75 **new** — `spawn` is 34 lines: it rebuilds the import path and bytecode folder that `RepositoryToolsets.pythonpath()` and `pycache_prefix()` already answer, opens a log file it never closes, then starts the process.

### `provide-meaningful-context` — Fail
- hook_daemon.py:222 **new** — `_rpc` waits `timeout=600` seconds; the number has no name, and `live_address` uses the same ten-minute wait for a ping.

## Judgment — `harness/hooks/hooks.py`

### `provide-meaningful-context` — Fail
- hooks.py:192 **new** — the hook command's `"timeout": 30` is an unnamed number written into every IDE's hooks.json.

## Passes

`_end_process` is gone (B14 fixed): the daemon stops a stale process through `StoppableProcess` with the named `_STOP_SECONDS`. Hook handlers receive `HookPayload` rather than a raw dict (the §2 item is gone). Exceptions raised while standing up the server are named (`HookStandupFailed`, `HookIllegitimateHandler`). The `hook = Hook` / `hooks = Hooks` aliases remain (hooks.py:97, 2 `@hook` against 42 `@Hook` uses); decision 10 keeps lowercase decorator aliases, so they are not judged a failure.
