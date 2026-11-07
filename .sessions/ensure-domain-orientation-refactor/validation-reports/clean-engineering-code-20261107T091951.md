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

**Generated:** 2026-11-07 09:19:51 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 12
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

- [X] **ERROR** **[graph rule]** - [harness/diagnostics/agent_tools_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\diagnostics\agent_tools_probe.py#L175): Operation `invoke`: Operation 'invoke' is 31 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/diagnostics/agent_tools_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\diagnostics\agent_tools_probe.py#L207): Operation `heavy_invoke`: Operation 'heavy_invoke' is 39 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/diagnostics/agent_tools_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\diagnostics\agent_tools_probe.py#L247): Operation `invoke_one`: Operation 'invoke_one' is 35 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/diagnostics/guidance_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\diagnostics\guidance_probe.py#L108): Operation `arguments_for`: Operation 'arguments_for' is 48 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/diagnostics/guidance_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\diagnostics\guidance_probe.py#L33): Operation `filtered_by`: Operation 'filtered_by' is a classmethod; prefer an instance operation.

Evaluate the current context against this rule (prefer-instance-operations):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

Evaluate the current context against this rule (keep-operations-single-responsibility):

### `simplify-control-flow`

Handle the failing or empty cases first and return. Keep the main path flat. Do not nest more than three levels — deeper than that you cannot tell which conditions hold on a given line without reading back up, and that is where the unhandled branch hides.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/diagnostics/guidance_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\diagnostics\guidance_probe.py#L108): Operation `arguments_for`: Operation 'arguments_for' nests control flow 9 levels deep (max 3).

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

### `deep-module`

Keep most classes private (at most **40%** public) in each first-class module. A first-class module is a folder that owns `.context/module-context.md`. Nested folders that also own that file are separate modules — respect them. Nested folders that do not own it roll up to the nearest enclosing module-context folder, or to the folder you are querying if none sits in between. Count classes, not operations: a public method on a hidden class is not a second seam. Every public class is a signature you cannot change without editing every caller, so public classes are much harder to refactor than private ones.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/diagnostics](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\diagnostics#L1): Module `diagnostics`: Module 'diagnostics' splits into many tiny classes (9); prefer a deep module with a small public surface.

Evaluate the current context against this rule (deep-module):

### `limit-operation-parameters`

Have callers pass intent, not setup. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/diagnostics/agent_tools_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\diagnostics\agent_tools_probe.py#L247): Operation `invoke_one`: Operation 'invoke_one' takes 4 parameters (maximum 3, excluding self).

Evaluate the current context against this rule (limit-operation-parameters):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [harness/diagnostics/agent_tools_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\diagnostics\agent_tools_probe.py#L207): Parameter `host`: Parameter 'host' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/diagnostics/agent_tools_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\diagnostics\agent_tools_probe.py#L247): Parameter `host`: Parameter 'host' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/diagnostics/guidance_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\diagnostics\guidance_probe.py#L33): Parameter `installer`: Parameter 'installer' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/diagnostics/guidance_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\diagnostics\guidance_probe.py#L108): Parameter `member`: Parameter 'member' needs a domain-specific type, not a generic container.

Evaluate the current context against this rule (use-typed-signatures):

---

# Judgment (round 3, branch 42ab935c)

Judged the Python in `harness/diagnostics` against the code rules with the leads script and a full read of both probe files. **Graph hits dismissed:** `simplify-control-flow` "9 levels" on `arguments_for` (the graph counts each `elif` as a level; the real depth is three); `deep-module` (no production class is named outside the folder); `prefer-instance-operations` on `filtered_by` (creation factory); `use-typed-signatures` on `host`/`member`/`installer` (judged in the model report); the five `except Exception` leads (agent_tools_probe.py:275, :363; guidance_probe.py:182, :191, :213) — each records the failure's type and message as a red probe result, which is the diagnostic's job, not a substitute answer.

## Judgment — `harness/diagnostics/agent_tools_probe.py`

### `keep-operations-single-responsibility` — Fail
- agent_tools_probe.py:345 **new** — `_dispatch_timed` promises a hard timeout, but it raises from inside `with ThreadPoolExecutor(...)`, whose exit waits for the running call to finish, so a hung tool still hangs the diagnostics; the timing and the pool's lifetime are mixed in one operation.

### `keep-operations-small-focused` — Fail
- agent_tools_probe.py:175 **new** — `invoke` is 21 statements, `heavy_invoke` (:207) 28, `invoke_one` (:247) 25.

### `eliminate-duplication` — Fail
- agent_tools_probe.py:236 **new** — `heavy_invoke` repeats `invoke`'s red/green colour, `!` prefix, and section write (:193-205), which `Installer.write_diagnostics_section` then works out a third time.
- agent_tools_probe.py:384 **new** — `_missing_required_arguments` repeats `GuidanceProbe._required_parameters` (guidance_probe.py:243), and `_signature_parameter_names` (:374) repeats the filter in `arguments_for` (guidance_probe.py:115).
- agent_tools_probe.py:228 **new** — `heavy_invoke` calls `probe_arguments_from_cdd_diagnostic` to check for a fixture, then `invoke_one` → `_workspace_arguments` (:304) calls it again for the same tool.

### `hide-inner-details` — Fail
- agent_tools_probe.py:289 **new** — `_prepare_workspace` imports the bridge's private `_ensure_cdd_diagnostic_path`, and `_slug_for_toolset_ref` (:76) calls `AgentToolSet._load`.

## Judgment — `harness/diagnostics/guidance_probe.py`

### `use-intention-revealing-names` — Fail
- guidance_probe.py:90 **new** — `instructions` returns `"green\n…"` even when its subsection is red; `actions` (:106) and `AgentToolsProbe.ping` (agent_tools_probe.py:173) do the same, so the agent reading the reply is told the probe passed when it failed.

### `keep-operations-small-focused` — Fail
- guidance_probe.py:108 **new** — `arguments_for` is 38 statements: a signature read, then one branch per named action.

### `prefer-instance-operations` — Fail
- guidance_probe.py:242 **new** — `_required_parameters` is a `@staticmethod` helper, not a factory.

## Passes

No `current`/`shared` accessor or class-level registry; the timeout is a named constant; the probe cleans up its own temporary files in `finally` blocks; no legacy aliases or banned words (the MCP host keeps its name).
