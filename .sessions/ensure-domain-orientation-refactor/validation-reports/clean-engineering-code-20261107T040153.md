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

**Generated:** 2026-11-07 04:01:53 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 18
**Rules with graph hits:** 4
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

Evaluate the current context against this rule (prefer-instance-operations):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/graph_bdd_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\graph_bdd_model.py#L29): Operation `parse`: Operation 'parse' mixes I/O-style calls with domain calculation; split responsibilities.

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

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/graph_bdd_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\graph_bdd_model.py#L29): Operation `parse`: Operation 'parse' uses the unnamed number 6.

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

### `missing-module-context`

**Graph violations:** 12

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/bdd_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\bdd_model.py#L20): OoadClass `BddModel`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/bdd_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\bdd_model.py#L143): OoadClass `MarkdownBddModel`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/code_spec_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\code_spec_model.py#L29): OoadClass `CodeBddModel`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/code_spec_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\code_spec_model.py#L183): OoadClass `PythonBddModel`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/code_spec_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\code_spec_model.py#L261): OoadClass `TypeScriptBddModel`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/graph_bdd_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\graph_bdd_model.py#L26): OoadClass `GraphBddModel`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\nodes.py#L37): OoadClass `BehaviorNode`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\nodes.py#L54): OoadClass `Description`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\nodes.py#L78): OoadClass `Context`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\nodes.py#L104): OoadClass `Observation`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/sketch/sketch_bdd_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\sketch\sketch_bdd_model.py#L8): OoadClass `SketchBddModel`: Module folder 'sketch' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/spec_source.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\spec_source.py#L1): OoadClass `_module`: Module folder 'model' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.

Evaluate the current context against this rule (missing-module-context):

### `use-explicit-dependencies`

Pass every collaborator through the constructor. Do not reach for a global or construct a collaborator inside construction. A collaborator the class fetches or builds itself cannot be swapped, so the class can only ever run against that one implementation.

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/bdd_model.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\bdd_model.py#L20): OoadClass `BddModel`: Class 'BddModel' constructs 'CodeBody' inside its constructor.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\nodes.py#L54): OoadClass `Description`: Class 'Description' constructs 'BoundChildren' inside its constructor.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\nodes.py#L78): OoadClass `Context`: Class 'Context' constructs 'BoundChildren' inside its constructor.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\bdd\model\nodes.py#L104): OoadClass `Observation`: Class 'Observation' constructs 'CodeBody' inside its constructor.

Evaluate the current context against this rule (use-explicit-dependencies):

---

# Judgment (code fidelity, `cdd_guidance/practices/bdd/model`)

Files: `bdd_model.py`, `code_spec_model.py`, `graph_bdd_model.py`, `nodes.py`, `spec_source.py`, `sketch/sketch_bdd_model.py`, `__init__.py` (specs and `python/_examples` excluded).

**Graph hits dismissed:**
- `missing-module-context` (12): `model/` and `model/sketch/` roll up into `cdd_guidance/practices/bdd/.context/module-context.md`, which exists.
- `use-explicit-dependencies` (4): `CodeBody` and `BoundChildren` are owned parts (composition), not swappable collaborators.

**Graph hits confirmed:** `keep-operations-single-responsibility` and `provide-meaningful-context` on `GraphBddModel.parse` (it decodes JSON, indexes edges, groups nodes by file, and builds the tree; the 5 and 6 are positional indexes into the graph's node lists).

**Scanner gap:** the code-fidelity scan did not report `_parse_sketch` (63 lines, four levels of nesting) or `_apply_fence_block` (27 lines), because module-level functions are not checked by `keep-operations-small-focused` or `simplify-control-flow`; moving logic out of a class into a free function hides it from both rules.

## Judgment — `cdd_guidance/practices/bdd/model/sketch/sketch_bdd_model.py`

### `no-legacy-api-after-refactor` — Fail
- sketch_bdd_model.py:22 `render` still imports `_render_sketch` from `bdd_model`; the refactor replaced it with `BddModel._sketch_lines` and left this caller on the removed name, so rendering a BDD model to the sketch format raises ImportError. No spec renders through `SketchBddModel`, which is why the suite passes.

## Judgment — `cdd_guidance/practices/bdd/model/bdd_model.py`

### `keep-operations-small-focused` — Fail
- bdd_model.py:147 `_parse_sketch` is 63 lines (about 45 statements) handling fences, surface lines, observations, descriptions, and the context stack in one loop.
- bdd_model.py:233 `_apply_fence_block` is 27 lines.

### `simplify-control-flow` — Fail
- bdd_model.py:165 `_parse_sketch` nests `for` → `if` (fence) → `else` → `while` four levels deep, and the `it` branch (bdd_model.py:184) repeats the stack-popping `while` at the same depth.

### `eliminate-duplication` — Fail
- bdd_model.py:233 `_apply_fence_block` re-implements `parse_call_graph_block` (`clean_engineering/model/call_graph.py:35`): depth from indent, `parse_arrow_line`, else a `call` entry.
- bdd_model.py:164 the indent-to-depth calculation `(len(raw) - len(raw.lstrip(" "))) // 2` is written four times in this file (:164, :180, :255, :258) with the indent width 2 unnamed.

### `hide-inner-details` — Fail
- bdd_model.py:113 `setup_at`, `body_at`, and `behavior_nodes` (:68) read `setup`, `body`, `contexts`, and `observations` through `getattr` with defaults, because `setup` is attached to nodes only by the code readers and is never declared on `Description` or `Context`.

## Judgment — `cdd_guidance/practices/bdd/model/code_spec_model.py`

### `never-swallow-exceptions` — Fail
- code_spec_model.py:191 `PythonBddModel.parse_code` catches `SyntaxError` and returns an empty model. `CodeBddModel.render` (code_spec_model.py:40) parses the previous file this way to keep its hand-written bodies, so a spec file with one syntax error is re-rendered from the canonical tree with scaffold comments in place of every test body the person wrote, and nothing reports that the previous file could not be read.

### `hold-state-on-the-object-not-in-parameters` — Fail
- code_spec_model.py:40 `render` stores the previous file's model on `self._kept`, and `parse_code` stores `self._lines` (:193), `self._text` (:267), and `self._roots` (:176) for the private readers and the lambdas from `_reader`; per-call state parked on the format object, so one object cannot parse or render two files at once.

### `use-intention-revealing-names` — Fail
- code_spec_model.py:40 `_kept` holds the previous file's spec as read, beside `previous` (the parameter) and `written` (each block as read); three words for "what the file said before", and `_kept` does not say it is the previous file.

## Judgment — `cdd_guidance/practices/bdd/model/graph_bdd_model.py`

### `hide-inner-details` — Fail
- graph_bdd_model.py:45 sorts and unpacks graph nodes by position (`row[5]`, `-row[6]`, `row[4]`, `row[2]`), and `_read_spec` (:48) unpacks eight positional fields; the layout of `Graph.write_json` is a contract this reader depends on without a type.

### `hold-state-on-the-object-not-in-parameters` — Fail
- graph_bdd_model.py:34 `parse` creates `self._members`, `self._code`, and `self._invoked` outside the constructor; `_realization` and `_call` read them, so calling either before `parse` raises AttributeError.

## Judgment — `cdd_guidance/practices/bdd/model/nodes.py`

### `eliminate-duplication` — Fail
- nodes.py:65 `Description.clone` and `Context.clone` (nodes.py:88) are the same loop over two child lists in a different order.

**Passes:** `do-not-invent-terms`, `prefer-instance-operations`, `errors-out-of-existence`, `no-prototype-swapping`, `use-consistent-naming`, `use-exceptions-properly`, `limit-comments`.
