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

**Generated:** 2026-11-07 00:01:30 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 37
**Rules with graph hits:** 13
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

**Graph violations:** 5

- [X] **ERROR** **[graph rule]** - [harness/mcp/__main__.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\__main__.py#L9): Operation `main`: Operation 'main' is 24 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/mcp/_examples/parameter_types/parameter_types.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\_examples\parameter_types\parameter_types.py#L22): Operation `echo`: Operation 'echo' is 50 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\mcp_server.py#L451): Operation `start`: Operation 'start' is 27 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\mcp_server.py#L844): Operation `http_app`: Operation 'http_app' is 25 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\mcp_server.py#L888): Operation `diagnose`: Operation 'diagnose' is 21 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\mcp_server.py#L924): Operation `standup`: Operation 'standup' is a classmethod; prefer an instance operation.

Evaluate the current context against this rule (prefer-instance-operations):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

Evaluate the current context against this rule (keep-operations-single-responsibility):

### `simplify-control-flow`

Handle the failing or empty cases first and return. Keep the main path flat. Do not nest more than three levels — deeper than that you cannot tell which conditions hold on a given line without reading back up, and that is where the unhandled branch hides.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\mcp_server.py#L451): Operation `start`: Operation 'start' nests control flow 4 levels deep (max 3).

Evaluate the current context against this rule (simplify-control-flow):

### `errors-out-of-existence`

For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure.

Evaluate the current context against this rule (errors-out-of-existence):

### `no-prototype-swapping`

An object keeps the class it was built as. Do not change it afterwards with `Object.setPrototypeOf`, `__proto__ =`, or `__class__ =`. When a subclass needs to make its own instances, give the base an overridable factory (`blank()`) or build the right class directly. A swapped object skips its constructor, so fields the subclass sets up are missing and nothing tells you.

Evaluate the current context against this rule (no-prototype-swapping):

### `use-intention-revealing-names`

Name each class, property, operation, and parameter so it answers why it exists. Do not abbreviate.

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [harness/mcp/_examples/parameter_types/parameter_types.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\_examples\parameter_types\parameter_types.py#L81): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/mcp/_examples/parameter_types/parameter_types.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\_examples\parameter_types\parameter_types.py#L87): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/mcp/_examples/parameter_types/parameter_types.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\_examples\parameter_types\parameter_types.py#L93): Parameter `value`: Parameter 'value' does not reveal intent.

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

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\mcp_server.py#L215): Operation `allow_cdd_tools`: Parameter 'settings' in 'allow_cdd_tools' is vague.

Evaluate the current context against this rule (avoid-vague-parameter-names):

### `deep-module`

Keep most classes private (at most **40%** public) in each first-class module. A first-class module is a folder that owns `.context/module-context.md`. Nested folders that also own that file are separate modules — respect them. Nested folders that do not own it roll up to the nearest enclosing module-context folder, or to the folder you are querying if none sits in between. Count classes, not operations: a public method on a hidden class is not a second seam. Every public class is a signature you cannot change without editing every caller, so public classes are much harder to refactor than private ones.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/mcp](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp#L1): Module `mcp`: Module 'mcp' splits into many tiny classes (33); prefer a deep module with a small public surface.

Evaluate the current context against this rule (deep-module):

### `keep-classes-single-responsibility`

Give each class one reason to change.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\mcp_server.py#L144): OoadClass `McpInstallation`: Class 'McpInstallation' exposes 13 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\mcp_server.py#L597): OoadClass `McpHost`: Class 'McpHost' exposes 11 public operations (budget ~9). Split responsibilities.

Evaluate the current context against this rule (keep-classes-single-responsibility):

### `limit-operation-parameters`

Have callers pass intent, not setup. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/mcp/_examples/parameter_types/parameter_types.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\_examples\parameter_types\parameter_types.py#L22): Operation `echo`: Operation 'echo' takes 22 parameters (maximum 3, excluding self).

Evaluate the current context against this rule (limit-operation-parameters):

### `missing-module-context`

**Graph violations:** 7

- [X] **ERROR** **[graph rule]** - [harness/mcp/_examples/hosting_demo/hosting_demo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\_examples\hosting_demo\hosting_demo.py#L11): OoadClass `PlanWorkResult`: Module folder 'hosting_demo' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/mcp/_examples/hosting_demo/hosting_demo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\_examples\hosting_demo\hosting_demo.py#L16): OoadClass `OrchestrateResult`: Module folder 'hosting_demo' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/mcp/_examples/hosting_demo/hosting_demo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\_examples\hosting_demo\hosting_demo.py#L22): OoadClass `HostingDemo`: Module folder 'hosting_demo' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/mcp/_examples/illegitimate_name/illegitimate_name.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\_examples\illegitimate_name\illegitimate_name.py#L9): OoadClass `IllegitimateName`: Module folder 'illegitimate_name' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/mcp/_examples/parameter_types/parameter_types.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\_examples\parameter_types\parameter_types.py#L11): OoadClass `NamedRecord`: Module folder 'parameter_types' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/mcp/_examples/parameter_types/parameter_types.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\_examples\parameter_types\parameter_types.py#L17): OoadClass `ParameterTypes`: Module folder 'parameter_types' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/mcp/scripts/connect.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\scripts\connect.py#L1): OoadClass `_module`: Module folder 'scripts' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.

Evaluate the current context against this rule (missing-module-context):

### `one-way-deps`

Make dependencies flow in one direction without cycles. A cycle prevents either module from changing or being tested independently.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/mcp](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp#L1): Module `mcp`: Circular import between 'mcp' and 'illegitimate_name' breaks one-way dependencies.

Evaluate the current context against this rule (one-way-deps):

### `state-change-returns-record-or-named-failure`

When an operation coordinates a state change that cannot be one property assignment, return the resulting record or a failure named after the rejected rule. Decide at code fidelity whether that failure is a result type or domain exception, because callers need one explicit outcome contract.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/mcp/restart_gate.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\restart_gate.py#L35): Operation `restarting`: Operation 'restarting' mutates state but does not return the record or a named failure.

Evaluate the current context against this rule (state-change-returns-record-or-named-failure):

### `use-explicit-dependencies`

Pass every collaborator through the constructor. Do not reach for a global or construct a collaborator inside construction. A collaborator the class fetches or builds itself cannot be swapped, so the class can only ever run against that one implementation.

**Graph violations:** 8

- [X] **ERROR** **[graph rule]** - [harness/mcp/cdd_home.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\cdd_home.py#L48): OoadClass `CddHome`: Class 'CddHome' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_daemon.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\mcp_daemon.py#L37): OoadClass `McpDaemon`: Class 'McpDaemon' constructs 'CddHome' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\mcp_server.py#L376): OoadClass `McpServer`: Class 'McpServer' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\mcp_server.py#L597): OoadClass `McpHost`: Class 'McpHost' constructs 'RestartGate' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server_host_heavy_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\mcp_server_host_heavy_spec.py#L114): OoadClass `TwoWorktrees`: Class 'TwoWorktrees' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/mcp/spec_support.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\spec_support.py#L20): OoadClass `UserHome`: Class 'UserHome' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/mcp/spec_support.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\spec_support.py#L44): OoadClass `SpecServer`: Class 'SpecServer' constructs 'CddHome' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/mcp/spec_support.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\spec_support.py#L101): OoadClass `ThrowawayMachine`: Class 'ThrowawayMachine' constructs 'UserHome' inside its constructor.

Evaluate the current context against this rule (use-explicit-dependencies):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 5

- [X] **ERROR** **[graph rule]** - [harness/mcp/_examples/parameter_types/parameter_types.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\_examples\parameter_types\parameter_types.py#L22): Parameter `untyped_fields`: Parameter 'untyped_fields' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/mcp/_examples/parameter_types/parameter_types.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\_examples\parameter_types\parameter_types.py#L93): Parameter `value`: Parameter 'value' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\mcp_server.py#L156): Parameter `tool`: Parameter 'tool' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\mcp_server.py#L315): Parameter `server`: Parameter 'server' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\mcp_server.py#L831): Parameter `daemon`: Parameter 'daemon' needs a domain-specific type, not a generic container.

Evaluate the current context against this rule (use-typed-signatures):

## Judgment — `harness/mcp/mcp_server.py`

### `never-swallow-exceptions` — Fail
- mcp_server.py:703 `_register_handlers`: `anyio.fail_after` around `to_thread.run_sync` (default `abandon_on_cancel=False`) cannot stop the thread; the tool runs to the end, its side effects happen (reports saved, files written), and then its result is thrown away and the caller is told `TimeoutError ... exceeded 10 seconds`. The caller retries work that already finished, which is how parallel validate calls piled up and dropped the host.
- mcp_server.py:220 `allow_cdd_tools`: a settings file that is unreadable or not JSON returns silently, so the install reports success while Claude Code still prompts for every cdd tool; the same pattern at 238 `drop_project_cdd_server` and 255 `drop_user_cdd_server` leaves a stale `cdd` entry that outranks the plugin.

### `hide-inner-details` — Fail
- mcp_server.py:820 `_enrolled`: McpHost reads `self._runtime._tools` and `self._runtime._prompts`, McpServer's private dicts, though McpServer exposes `tools` and `prompts`.

### `use-explicit-dependencies` — Fail
- mcp_server.py:51 `_SERVING_MCP_HOST`: a module global set by `_bind_as_serving` and read through `serving_mcp_host()`, so any module can reach the running host without it being passed.
- mcp_server.py:330 `server_home`: a property that builds a new `CddHome()` on every read; `ensure_server`, `pin_server` and `serve_from_checkout` each build one or more, plus a fresh `McpDaemon` per call.

### `keep-classes-single-responsibility` — Fail
- mcp_server.py:144 `McpInstallation`: writes the MCP manifest, edits the user's Claude permissions, removes `cdd` from project and user configs, stands the host up and diagnoses it, and installs, pins and starts the daemon — five reasons to change. Graph hit confirmed; McpHost (597) hit confirmed for the same reason (protocol handlers, dispatch, restart, diagnose, notice).

### `hold-state-on-the-object-not-in-parameters` — Fail
- mcp_server.py:798 `_dispatch_between_restarts`: calls `Session.refresh_current_from_repo(project)` and `Session.current(project)` with the project on each call instead of asking the runtime for that project's session object it already chose (`runtime_for(project)`).

### `simplify-control-flow` — Fail
- mcp_server.py:451 `start`: for, try, for, try nests four levels; the per-toolset enrolment belongs in a helper. Graph hit confirmed.

### `use-typed-signatures` — Fail
- mcp_server.py:156 `write`: `tool: Any` though `record_operation` (162) takes `AgentTool`; 315 `bind(server: Any)` and 831 `serve(daemon: Any)` likewise. Graph hits confirmed.

## Judgment — `harness/mcp/restart_gate.py`

Graph hit `state-change-returns-record-or-named-failure` on `restarting` (line 35) dismissed: it is a context manager guarding a lock, not a domain state change.

Other dismissals: `standup` classmethod (924) is a creation factory; `missing-module-context`, `limit-operation-parameters`, `use-intention-revealing-names` and `one-way-deps` hits under `_examples/` are sample toolsets; `use-explicit-dependencies` hits in spec_support.py and the heavy spec are test support; CddHome (cdd_home.py:48) building a `Path` in its constructor is a value, not a collaborator.
