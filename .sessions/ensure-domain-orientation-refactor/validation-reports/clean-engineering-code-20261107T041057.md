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

**Generated:** 2026-11-07 04:10:57 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 17
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

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/class_cards.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\class_cards.py#L39): Operation `lines`: Operation 'lines' is 25 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\nodes.py#L73): Operation `building_block_type`: Operation 'building_block_type' is 21 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\nodes.py#L251): Operation `lines`: Operation 'lines' is 33 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\nodes.py#L316): Operation `lines`: Operation 'lines' is 26 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

Evaluate the current context against this rule (prefer-instance-operations):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\nodes.py#L379): Operation `parse`: Operation 'parse' mixes I/O-style calls with domain calculation; split responsibilities.

Evaluate the current context against this rule (keep-operations-single-responsibility):

### `simplify-control-flow`

Handle the failing or empty cases first and return. Keep the main path flat. Do not nest more than three levels — deeper than that you cannot tell which conditions hold on a given line without reading back up, and that is where the unhandled branch hides.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\nodes.py#L251): Operation `lines`: Operation 'lines' nests control flow 4 levels deep (max 3).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\nodes.py#L316): Operation `lines`: Operation 'lines' nests control flow 4 levels deep (max 3).

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

### `missing-module-context`

**Graph violations:** 9

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/class_cards.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\class_cards.py#L23): OoadClass `ClassCard`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/class_cards_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\class_cards_spec.py#L1): OoadClass `_module`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\nodes.py#L53): OoadClass `MarkdownDomainNode`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\nodes.py#L96): OoadClass `MarkdownIntegration`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\nodes.py#L100): OoadClass `MarkdownInvariantObject`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\nodes.py#L104): OoadClass `MarkdownEntity`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\nodes.py#L120): OoadClass `MarkdownAggregate`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\nodes.py#L315): OoadClass `MarkdownBoundedContext`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\nodes.py#L354): OoadClass `MarkdownBoundedContextMap`: Module folder 'markdown' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.

Evaluate the current context against this rule (missing-module-context):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ddd\model\markdown\nodes.py#L386): Parameter `canonical`: Parameter 'canonical' is missing a type annotation.

Evaluate the current context against this rule (use-typed-signatures):

---

# AI judgment (ddd sub-judge, code fidelity) — `cdd_guidance/practices/ddd/model/markdown`

The model-fidelity judgment of the same files is in `clean-engineering-model-20261107T040747.md` (fields shared with the sketch adapter, cards beside root members, `_services_in` always empty, plain maps rendering as an empty document, the duplicated parsers). The findings below are the code rules.

## Judgment — `cdd_guidance/practices/ddd/model/markdown/nodes.py`

### `hold-state-on-the-object-not-in-parameters` — Fail
- nodes.py:164 `_read_map_lines`: swaps `self._body` for one call and restores it in `finally`; `_read_map_body` and `_read_integrations` read the swapped field instead of taking the lines they work on.

### `keep-operations-small-focused` — Fail
- nodes.py:251 `MarkdownAggregate.lines` (33 lines), `:316 MarkdownBoundedContext.lines` (26), `:73 building_block_type` (21), as the scanner found.
- nodes.py:171 `_read_map_body` (about 40 lines), `:212 _read_integrations` (37), `:546 _wire_event` (33): longer still, and not measured by the scanner.

### `simplify-control-flow` — Fail
- nodes.py:251 `lines` and `:316 lines`: four levels, as the scanner found.
- nodes.py:494 `_apply_event_map`: `while` / `if` / `while` / `if` — four levels — and the outer loop scans every line of the file again after the contexts were read.

### `use-exceptions-properly` — Fail
- nodes.py:369 `get_next_bounded_context_from_file`: `assert start is not None` guards a public operation; with assertions off (`python -O`) it fails later with a `TypeError` on `self._lines[None]`. A named exception, or no call without `has_more_bounded_context`, states the contract.

### `provide-meaningful-context` — Fail
- nodes.py:435 `_sketch_metadata`: `"Product / Feature Name"` and `"see engagement sketch"` are placeholder text written into a published document when the sketch has no title or source line, with nothing naming them as defaults.
- nodes.py:370 `self._lines[start].strip()[3:]` and `:475 line[4:]`: heading prefixes cut by length instead of by the named markers.

### `eliminate-duplication` — Fail
- nodes.py:263 the integration and event lines are written in `lines` and again in `_integration_lines` (`:297`).
- nodes.py:25 `_parse_arrow_target` and `:45 _looks_like_operation`: copied verbatim into `drawio/drawio_bounded_context_map.py:561` and `:816`.
- nodes.py:520 `_services_in` and `:531 _events_in`: the same loop over each aggregate's root properties, filtered by type.

### `no-legacy-api-after-refactor` — Fail
- nodes.py:131 `has_more_integration` and `:134 get_next_integration_from_file`: no caller.
- nodes.py:542 `_consumer_name(consumer)`: returns `consumer.name`; a wrapper that adds nothing.

## Judgment — `cdd_guidance/practices/ddd/model/markdown/class_cards.py`

### `keep-operations-small-focused` — Fail
- class_cards.py:39 `ClassCard.lines` (25 lines), as the scanner found.
- class_cards.py:109 `read_card` (37 lines) and `:177 card_from_sketch` (50 lines): module-level functions the scanner does not measure.

### `simplify-control-flow` — Fail
- class_cards.py:205 `card_from_sketch`: `while` / `if lower.startswith("repo:")` / `if index < ...` / `for name` / `if _IDENT.match` — five levels.

### `use-consistent-naming` — Fail
- class_cards.py:166 `_read_member`: a public property gets `access = "both"` while a public operation gets `access = "public"` (`:158`), so the same mark (`+`) reads as two different access words.

### `use-intention-revealing-names` — Fail
- class_cards.py:151 `_kind`: read from the operation pattern and thrown away, so `+ <<query>> find()` silently loses its stereotype.

Passes (both files): `prefer-instance-operations`, `no-prototype-swapping`, `never-swallow-exceptions` (no exception handling), `errors-out-of-existence` (missing sections give empty lists), `limit-comments`.

Graph hits dismissed:
- `missing-module-context` (9): dismissed; `model/markdown/` rolls up into `cdd_guidance/practices/ddd/.context/module-context.md`, which exists; the hit on `class_cards_spec.py` is a spec.
- `keep-operations-single-responsibility` on `nodes.py:379 parse` ("mixes I/O-style calls"): dismissed; `parse` reads no file, it builds a fresh map from text in hand.
- Confirmed: `keep-operations-small-focused` (4), `simplify-control-flow` (2), `use-typed-signatures` on `render(canonical=None)`.
