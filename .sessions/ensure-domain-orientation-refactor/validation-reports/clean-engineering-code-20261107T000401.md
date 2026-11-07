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

**Generated:** 2026-11-07 00:04:01 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 35
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

- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_daemon.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_daemon.py#L71): Operation `spawn`: Operation 'spawn' is 34 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_server.py#L608): Operation `handle_stdin`: Operation 'handle_stdin' is 26 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

**Graph violations:** 5

- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_server.py#L446): Operation `state_path`: Operation 'state_path' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_server.py#L450): Operation `ensure`: Operation 'ensure' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hooks.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hooks.py#L80): Operation `companion_flags`: Operation 'companion_flags' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hooks.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hooks.py#L84): Operation `disabled_on`: Operation 'disabled_on' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hooks.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hooks.py#L89): Operation `normalize_event`: Operation 'normalize_event' is a classmethod; prefer an instance operation.

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

- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_server.py#L450): Operation `ensure`: Operation 'ensure' raises on an empty or missing value; return a quiet result instead.

Evaluate the current context against this rule (errors-out-of-existence):

### `no-prototype-swapping`

An object keeps the class it was built as. Do not change it afterwards with `Object.setPrototypeOf`, `__proto__ =`, or `__class__ =`. When a subclass needs to make its own instances, give the base an overridable factory (`blank()`) or build the right class directly. A swapped object skips its constructor, so fields the subclass sets up are missing and nothing tells you.

Evaluate the current context against this rule (no-prototype-swapping):

### `use-intention-revealing-names`

Name each class, property, operation, and parameter so it answers why it exists. Do not abbreviate.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_server.py#L345): Parameter `item`: Parameter 'item' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hooks.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hooks.py#L73): Parameter `fn`: Parameter 'fn' does not reveal intent.

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

**Graph violations:** 18

- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_server.py#L215): Operation `is_enabled`: Parameter 'payload' in 'is_enabled' is vague.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_server.py#L215): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_server.py#L282): Operation `invoke`: Parameter 'payload' in 'invoke' is vague.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_server.py#L282): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_server.py#L564): Operation `dispatch`: Parameter 'payload' in 'dispatch' is vague.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_server.py#L564): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_spec.py#L73): Operation `on_after`: Parameter 'payload' in 'on_after' is vague.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_spec.py#L73): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_spec.py#L83): Operation `on_after`: Parameter 'payload' in 'on_after' is vague.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_spec.py#L83): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_spec.py#L93): Operation `on_stop`: Parameter 'payload' in 'on_stop' is vague.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_spec.py#L93): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_spec.py#L104): Operation `inject_rules`: Parameter 'payload' in 'inject_rules' is vague.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_spec.py#L104): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_spec.py#L114): Operation `inject_rules`: Parameter 'payload' in 'inject_rules' is vague.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_spec.py#L114): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_spec.py#L144): Operation `on_stop`: Parameter 'payload' in 'on_stop' is vague.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_spec.py#L144): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.

Evaluate the current context against this rule (avoid-vague-parameter-names):

### `deep-module`

Keep most classes private (at most **40%** public) in each first-class module. A first-class module is a folder that owns `.context/module-context.md`. Nested folders that also own that file are separate modules — respect them. Nested folders that do not own it roll up to the nearest enclosing module-context folder, or to the folder you are querying if none sits in between. Count classes, not operations: a public method on a hidden class is not a second seam. Every public class is a signature you cannot change without editing every caller, so public classes are much harder to refactor than private ones.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/hooks](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks#L1): Module `hooks`: Module 'hooks' splits into many tiny classes (22); prefer a deep module with a small public surface.

Evaluate the current context against this rule (deep-module):

### `keep-classes-single-responsibility`

Give each class one reason to change.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_server.py#L422): OoadClass `HookServer`: Class 'HookServer' exposes 13 public operations (budget ~9). Split responsibilities.

Evaluate the current context against this rule (keep-classes-single-responsibility):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 5

- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_daemon.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_daemon.py#L112): Parameter `inner`: Parameter 'inner' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hook_server.py#L345): Parameter `item`: Parameter 'item' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hooks.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hooks.py#L73): Parameter `fn`: Parameter 'fn' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hooks.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hooks.py#L84): Parameter `operation`: Parameter 'operation' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hooks.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\hooks\hooks.py#L125): Parameter `tool`: Parameter 'tool' needs a domain-specific type, not a generic container.

Evaluate the current context against this rule (use-typed-signatures):

## Judgment — `harness/hooks/hook_server.py`

### `keep-classes-single-responsibility` — Fail
- hook_server.py:449 `ensure`: HookServer carries the daemon's process lifecycle — spawn lock (`_claim_spawn`, `_release_dead_spawn`, `_release_spawn`), connection polling (`_connect`, `_wait_for_daemon`, `_wait_until_connected`) and spawning — as classmethods taking `repo` and `path`, beside dispatching hooks, publishing context and diagnosing. HookDaemon already owns spawn, live address and stale replacement; the lock and polling belong there. Graph hit (13 public operations) confirmed.

### `prefer-instance-operations` — Fail
- hook_server.py:466 `_connect`: one of six classmethods (`_connect`, `_spawn`, `_claim_spawn`, `_release_dead_spawn`, `_wait_for_daemon`, `_release_spawn`) that pass `repo` and `path` between them because there is no object holding them. Graph hits at 446 `state_path` and 450 `ensure` confirmed (ensure is a lookup-or-start, not a factory).

### `keep-operations-single-responsibility` — Fail
- hook_server.py:608 `handle_stdin`: is both the remote client (forwards raw bytes to the daemon when `_port` is set) and the local dispatcher (parses, dispatches, filters a rules dump, publishes context, writes last-chat state, injects saved chat context), plus creates the main session through SessionLogs. Graph hit confirmed.

### `use-explicit-dependencies` — Fail
- hook_server.py:453 `ensure`: builds a new `HookDaemon()` inside `ensure`, `_connect` and `_spawn`, and line 440 reaches `Session.current(repo_root)` in the constructor.

### `avoid-vague-parameter-names` — Fail
- hook_server.py:564 `dispatch`: `payload` is typed `HookPayload`, so the type is fine but the name hides that it is the hook event; graph hits at 215 and 282 are the same name. (hook_spec.py hits dismissed: test fixtures.)

## Judgment — `harness/hooks/hook_daemon.py`

### `eliminate-duplication` — Fail
- hook_daemon.py:172 `_end_process`: a copy of harness/mcp/mcp_daemon.py:150 `_end_process` (SIGTERM, then poll until gone) that has already drifted: this copy lacks the `pid <= 0 or pid == os.getpid()` guard, so a stale state file naming pid 0 or the current process signals it, and its wait is a bare `3` seconds where the MCP copy names `_STOP_SECONDS`.

### `provide-meaningful-context` — Fail
- hook_daemon.py:177 `_end_process`: `time.time() + 3` and `time.sleep(0.05)` are unnamed waits.

### `use-typed-signatures` — Fail
- hook_daemon.py:112 `serve`: `inner=None` and `server` (lines 190, 203, 209) are untyped; the reply dicts (`_rpc`, `_read_json`) are bare `dict`. Graph hit confirmed.

## Judgment — `harness/hooks/hooks.py`

### `no-legacy-api-after-refactor` — Fail
- hooks.py:93 `hook`: `hook = Hook` and `hooks = Hooks` keep lowercase second names for the decorators; one caller (harness/guidance/fixtures/agentic_ops/hook_ops.py:6) uses `hook` while every other module uses `Hook`/`Hooks`.

### `prefer-instance-operations` — Fail
- hooks.py:84 `disabled_on`: a classmethod reading a flag off another operation; graph hits at 80 and 89 confirmed (`normalize_event` is a free name conversion parked on the class).

Graph hits dismissed: `errors-out-of-existence` on `ensure` (a daemon that never starts is broken, so raising `HookStandupFailed` is right); `deep-module` count of 22 (includes spec fixtures).
