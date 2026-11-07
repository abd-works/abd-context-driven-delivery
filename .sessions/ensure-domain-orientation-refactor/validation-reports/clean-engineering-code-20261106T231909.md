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

**Generated:** 2026-11-06 23:19:09 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 16
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

**Graph violations:** 5

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/graph_json_reader.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\graph_json_reader.py#L83): Operation `refresh_stale_limit_operation_parameter_messages`: Operation 'refresh_stale_limit_operation_parameter_messages' is 58 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validate.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validate.py#L37): Operation `validate`: Operation 'validate' is 49 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validation_report.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validation_report.py#L22): Operation `of_graph_and_ai_rules`: Operation 'of_graph_and_ai_rules' is 34 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validation_report_formatter.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validation_report_formatter.py#L21): Operation `format_violation_line`: Operation 'format_violation_line' is 25 lines (max 20).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/verify_report_links.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\verify_report_links.py#L12): Operation `verify_report`: Operation 'verify_report' is 36 lines (max 20).

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

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validate.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validate.py#L28): OoadClass `Validate`: Operation 'createRule' uses camelCase while other operations on 'Validate' use the other convention.

Evaluate the current context against this rule (use-consistent-naming):

### `provide-meaningful-context`

Give a number or literal a name that says why it is there (`SECONDS_PER_DAY`, not `86400`). Do not number variables (`item1`).

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/verify_report_links.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\verify_report_links.py#L12): Operation `verify_report`: Operation 'verify_report' uses the unnamed number 80.

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

### `limit-operation-parameters`

Have callers pass intent, not setup. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validate.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validate.py#L37): Operation `validate`: Operation 'validate' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validation_report.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validation_report.py#L22): Operation `of_graph_and_ai_rules`: Operation 'of_graph_and_ai_rules' takes 4 parameters (maximum 3, excluding self).

Evaluate the current context against this rule (limit-operation-parameters):

### `missing-module-context`

**Graph violations:** 7

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/graph_json_reader.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\graph_json_reader.py#L1): OoadClass `_module`: Module folder 'validate' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validate.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validate.py#L19): OoadClass `PathsNotFoundError`: Module folder 'validate' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validate.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validate.py#L28): OoadClass `Validate`: Module folder 'validate' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validate_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validate_spec.py#L1): OoadClass `_module`: Module folder 'validate' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validation_report.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validation_report.py#L15): OoadClass `ValidationReport`: Module folder 'validate' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/validation_report_formatter.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\validation_report_formatter.py#L9): OoadClass `ValidationReportFormatter`: Module folder 'validate' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/validate/verify_report_links.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\actions\validate\verify_report_links.py#L1): OoadClass `_module`: Module folder 'validate' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.

Evaluate the current context against this rule (missing-module-context):


---

Judged 2026-11-06 against clean_engineering.md § code Rules, the shared rules, `.claude/rules/coding.md` and `.claude/rules/writing-guidelines.md`. This validate ran on `cdd_guidance/actions/validate`. The later validate calls for the other actions, practices, builders and patterns failed on the MCP host (connection closed, then a 10-second TimeoutError, then ECONNREFUSED), so those files' judgments are appended here too, without graph hits.

Graph hits dismissed: the seven `missing-module-context` hits are false positives. `cdd_guidance/actions/.context/module-context.md` exists and `validate/` rolls up to it (the deep-module roll-up), and one hit is on `validate_spec.py`, a spec. All other graph hits are confirmed below.

## Judgment — `cdd_guidance/actions/validate/validate.py`

### `hold-state-on-the-object-not-in-parameters` — Fail
- validate.py:39 `validate(guidance, ...)`: the action is handed its guidance on every call and parses a `session=` word out of it (inherited `_bind_guidance_string`), instead of being made for its session, practice and fidelity once (P-1, P-2 still open).
- validate.py:146 `_edited_graph_json`: passes `self.session.root` and every catalogue key into `Graph.load_files`; the session's practices own their folders and graph (`PracticeSessionOutput.graph`), so Graph should be reached through them (P-19/P-20 still open).
- validate.py:222 `_graph_and_ai_rule_report`: hands `self.session.root` to the free function `refresh_stale_limit_operation_parameter_messages`.
- validate.py:55 `self._unchecked_files = ...`: per-call state written as a plain field on the shared action. Every other per-call field in GuidanceAction is thread-local because MCP runs calls on several threads; two concurrent validates overwrite each other's set and filter the wrong hits out of a report.

### `keep-operations-small-focused` — Fail
- validate.py:37 `validate`: 49 lines (graph hit confirmed); binding, format choice, graph building, report saving and the inner `on` closure in one operation.

### `keep-operations-single-responsibility` — Fail
- validate.py:208 `_graph_and_ai_rule_report`: reads violations, refreshes them, filters them, logs them, collects rules and re-parses rule bodies, then formats.

### `eliminate-duplication` — Fail
- validate.py:240 `_iter_validate_rules`: the same "shared rules plus current fidelity rules, deduplicated by id" loop as `_rules_for` at validate.py:306 and as diagnose.py:132 `_guidance_rules` (A-F1 still open).
- validate.py:254 `_rule_bodies_from_guidance`: re-parses each RulesCollection's markdown bullets with `Rule.from_bullet` although iterating the collection already yields `Rule` objects with `slug` and `body` (A-F2 still open).
- validate.py:333 `_validate_text`: copy of diagnose.py:153 `_rules_text`.

### `use-consistent-naming` — Fail
- validate.py:348 `createRule`: camelCase operation beside snake_case ones (graph hit confirmed).

### `provide-meaningful-context` — Fail
- validate.py:282 `_log_graph_validation`: the literal `40` (used twice) caps the synopsis with no named constant.

### `limit-operation-parameters` — Fail
- validate.py:37 `validate`: four parameters, one of which (`guidance`) is state the action should hold (graph hit confirmed).

## Judgment — `cdd_guidance/actions/validate/graph_json_reader.py`

### `no-legacy-api-after-refactor` — Fail
- graph_json_reader.py:83 `refresh_stale_limit_operation_parameter_messages`: a compatibility path that re-runs `limit-operation-parameters` when a saved graph still carries "the legacy message" `(maximum 2)`; old graphs should be rebuilt, not patched at report time.

### `do-not-invent-parallel-object-models` — Fail
- graph_json_reader.py:191 `_record`: every violation becomes a 10-key dict (`location`, `rule_slug`, `node_type`, ...) beside the graph's `RuleHit` (harness/graph/explorer.py:39) and kanban's `Violation` (harness/kanban/report.py:44); every reader then does `item.get("...")` (A-F14 still open).
- graph_json_reader.py:94 `refresh_stale_limit_operation_parameter_messages`: re-parses source files and re-checks a rule outside the graph, a second rule-evaluation path.

### `prefer-instance-operations` — Fail
- graph_json_reader.py:225 `filter_violations_by_path_prefix`: a module of free functions (`load_graph_json_paths`, `violations_from_graph_json_files`, `save_checked_graph`, `violations_by_rule`) that take the violation list first; they belong on a violations collection the report owns.

### `keep-operations-small-focused` — Fail
- graph_json_reader.py:83 `refresh_stale_limit_operation_parameter_messages`: 58 lines (graph hit confirmed).

### `eliminate-duplication` — Fail
- graph_json_reader.py:150 `_source_language`: another suffix-to-format table; `harness.markdown.format.Format.from_extension` already owns this.
- graph_json_reader.py:11 `load_graph_json_paths`: returns nothing for `graph=True`, so validate.py:128 handles the `True` case itself.

### `use-exceptions-properly` — Fail
- graph_json_reader.py:31 `violations_from_graph_json_file`: raises bare `ValueError` for an unreadable graph file instead of a named failure.

## Judgment — `cdd_guidance/actions/validate/validation_report.py`

### `keep-operations-small-focused` — Fail
- validation_report.py:22 `of_graph_and_ai_rules`: 34 lines (graph hit confirmed).

### `limit-operation-parameters` — Fail
- validation_report.py:22 `of_graph_and_ai_rules`: takes `rule_bodies` beside `rules` although each `Rule` carries its body (graph hit confirmed; the extra parameter exists only because validate.py:254 re-parses bodies).

### `prefer-instance-operations` — Fail
- validation_report.py:63 `_rule_by_rule_sections`: free functions take the formatter and rule bodies as parameters; they are this report's own operations.

## Judgment — `cdd_guidance/actions/validate/validation_report_formatter.py`

### `keep-operations-small-focused` — Fail
- validation_report_formatter.py:21 `format_violation_line`: 25 lines (graph hit confirmed).

### `use-consistent-naming` — Fail
- validation_report_formatter.py:74 `get_relative_path`: a `get_` accessor beside `_display_path`.
- validation_report_formatter.py:47 `format_violation_message`: returns its argument unchanged, an empty leftover of the agile_bots port.

## Judgment — `cdd_guidance/actions/validate/verify_report_links.py`

### `provide-meaningful-context` — Fail
- verify_report_links.py:19 `verify_report`: unnamed `80` truncation length, repeated four times (graph hit confirmed).

### `keep-operations-small-focused` — Fail
- verify_report_links.py:12 `verify_report`: 36 lines (graph hit confirmed). The module has no production caller; only validation_report_formatter_spec.py imports it.

## Judgment — `cdd_guidance/actions/diagnose/diagnose.py`

### `eliminate-duplication` — Fail
- diagnose.py:132 `_guidance_rules`: copies Validate's shared-plus-current-fidelity rule assembly (`_fidelity_rules`, `_rules_text`), the A-F1 duplication.

### `no-legacy-api-after-refactor` — Fail
- diagnose.py:21 `@mcp` / `@skill`: lowercase aliases (`mcp = Mcp` in harness/mcp/mcp_server.py:63, `skill = Skill` in harness/installation/files.py:33) while the other actions use `@Mcp` / `@Skill`; two names for one decorator, used about 160 and 37 times across the repository.

## Judgment — `cdd_guidance/actions/satisfy/satisfy.py`

### `hold-state-on-the-object-not-in-parameters` — Fail
- satisfy.py:33 `on`: `self._inside(Validate, worked_on).validate(worked_on)` makes the inner Validate for `worked_on` and then hands it the same guidance again; the same pattern is at iterate.py:47, sketch.py:128 and grill_context.py:94.

## Judgment — `cdd_guidance/actions/iterate/iterate.py`

### `use-intention-revealing-names` — Fail
- iterate.py:26 `mark_iterate_tick`: "tick" is a banned word (writing-guidelines); the public MCP name and the class docstring at iterate.py:18 use it.
- iterate.py:34 `iterate(..., tools)`: the `tools` parameter is never read.

### `limit-comments` — Fail
- iterate.py:3 module docstring: names an `@iterate` decorator, `_decorator.py` and `iterate_session`, none of which exist.

### `eliminate-duplication` — Fail
- iterate.py:20 `_grill_context`: identical to sketch.py:42; sketch.py:46 `_generate` is identical to grill_context.py:97, and both build `Generate(self.session)` rather than `self._inside(Generate, ...)` as Satisfy and Iterate do.

## Judgment — `cdd_guidance/actions/improvement/improvement.py`

### `keep-operations-single-responsibility` — Fail
- improvement.py:54 `verify_fix`: a stub that returns `f"verify_fix theme={theme}"` and re-checks nothing (code Guidance: fill every empty body).
- improvement.py:43 `repair`: calls `self.run(on)` with no action name, so the repair is never logged to the session, unlike every other action.

### `use-intention-revealing-names` — Fail
- improvement.py:1 module and class docstrings: "kit" is the banned shorthand for the Improvement action (writing-guidelines).

## Judgment — `cdd_guidance/actions/partition/partition.py`

### `hold-state-on-the-object-not-in-parameters` — Fail
- partition.py:162 `on`: ignores `item` and calls `self.partition_corpus(source, mode)`, passing the source label as `context` and dropping `out_root` and `paths`; `index()` and `segment()` then write under the session root while partition.py:167 tells the agent the docs went under `out_root` (P-18 reshaped, not fixed).

### `limit-operation-parameters` — Fail
- partition.py:145 `partition`: five parameters (`guidance`, `context`, `mode`, `out_root`, `paths`).

### `provide-meaningful-context` — Fail
- partition.py:36 `verify_segment_completeness`: default `120` minimum body length, repeated at partition_index.py:113 and :117 with no named constant.

### `limit-comments` — Fail
- partition.py:21 class docstring: names `GuidanceAction.end` and a "hanging session turn"; GuidanceAction has no `end`.

## Judgment — `cdd_guidance/actions/partition/partition_index.py`

### `prefer-instance-operations` — Fail
- partition_index.py:85 `_parse_config`: four private `@staticmethod` helpers (`_parse_config`, `_non_entry_headers`, `_short_body_pattern`, `_min_body_chars`); segment.py:170, :235 and :239 do the same.

### `do-not-invent-parallel-object-models` — Fail
- partition_index.py:64 `non_entry_headers`: three properties copy fields of its own `SegmentCompletenessConfig` (A-F25 still open).

## Judgment — `cdd_guidance/actions/sketch/sketch.py`

### `hold-state-on-the-object-not-in-parameters` — Fail
- sketch.py:40 `sketch_template`: the action holds `_agent_dir` and then passes it to its own public `find_template(agent_dir)`; one value, two ways in.

## Judgment — `cdd_guidance/actions/grill_context/grill_context.py`

### `use-intention-revealing-names` — Fail
- grill_context.py:110 Step 2 prose: "prove-read" is a banned phrase (writing-guidelines); repeated at grill_context.py:115.

## Judgment — `cdd_guidance/actions/render/render.py`

### `hold-state-on-the-object-not-in-parameters` — Fail
- render.py:37 `on`: `format`, `paths` and `source` pass down into `item.render_files` / `item.render` although the practice holds its format (P-7 still open).

## Judgment — `cdd_guidance/practices/clean_engineering/clean_engineering.py`

### `errors-out-of-existence` — Fail
- clean_engineering.py:71 `generate_output`: calls `self.drawio.render()` unconditionally, while `drawio` defaults to `None` (clean_engineering.py:40) and no caller passes it; `CleanEngineering(fidelity="code").generate_output()` raises `AttributeError: 'NoneType' object has no attribute 'render'`. The docstring says drawio is used only for the drawio format.

## Judgment — `cdd_guidance/practices/ux/ux.py`

### `hold-state-on-the-object-not-in-parameters` — Fail
- ux.py:49 `ensure_javascript(generator: str, ...)`: a practice name string selects which practice to construct; the caller should hold the practice and call its `render`.

### `use-exceptions-properly` — Fail
- ux.py:60 `ensure_javascript`: raises bare `ValueError` for an unknown practice.

## Judgment — `cdd_guidance/practices/bdd/bdd.py`

### `do-not-invent-parallel-object-models` — Fail
- bdd.py:53 `__init__`: takes `path` and `session` and attaches a workspace to the guidance, while `Session.practices[key].guideline` already attaches its session; the guidance keeps a second copy of session state (A-F20). The same constructor is at agent_bdd.py:18 and in all three builders.

## Judgment — `cdd_guidance/practices/agent_bdd/agent_bdd.py`

### `hold-state-on-the-object-not-in-parameters` — Fail
- agent_bdd.py:21 `_bdd`: builds a fresh `Bdd(format=self.format, path=self.path, session=self.session)`, and agent_bdd.py:28 a fresh `Generate(self.workspace)`, handing state across instead of working on the session's own practice (P-15 still open).

## Judgment — `cdd_guidance/practices/agent_bdd/agent_chat_bdd.py`

### `no-legacy-api-after-refactor` — Fail
- agent_chat_bdd.py:81 `instruct_run`: "Back-compat alias for `instruct_use_tool`"; copied again at agent_cli_bdd.py:341, and `RunResponse.stdout` (agent_bdd_common.py:102) is an alias of `text`.

## Judgment — `cdd_guidance/practices/clean_engineering/model/base_class_model.py`

### `do-not-invent-parallel-object-models` — Fail
- base_class_model.py:431 `sync_tree_from_legacy`: OoadClass keeps its members twice, as `properties`/`operations` lists and as `property_nodes`/`operation_nodes`, and copies one into the other on update (base_class_model.py:269).

### `no-legacy-api-after-refactor` — Fail
- base_class_model.py:708 `classes`: "Flat view of all classes across all modules - for backward compat."

## Judgment — `cdd_guidance/practices/stories/stories.py`

### `hold-state-on-the-object-not-in-parameters` — Fail
- stories.py:69 `read_paths`: loads story files relative to `Path.cwd()`, a global, instead of the session root the practice is attached to.

## Judgment — `cdd_guidance/practices/stories/model/json/nodes.py`

### `never-swallow-exceptions` — Fail
- nodes.py:136 `load`: `except Exception: return None` hides every parse failure of a story-graph JSON file.

## Judgment — `cdd_guidance/practices/stories/model/typescript/spec_file.py`

### `eliminate-duplication` — Fail
- spec_file.py:162 `_camel`: hand-rolled case conversion although `harness.agent_tools.name.Name.camel` exists; the same at clean_engineering/model/drawio/drawio_class_model.py:706 `_slug`, stories/model/python/seeds/story_test.py:48 `_slug` and stories/model/markdown/links.py:45 `_words` (root cause 1.10 is marked done but these remain).

## Judgment — `cdd_guidance/practices/clean_engineering/model/operation_metrics.py`

### `prefer-instance-operations` — Fail
- operation_metrics.py:1 module: 28 module-level functions; the same holds in ddd/model/drawio/drawio_bounded_context_map.py (35), patterns/lern_domain_driven/tier_facts.py (20, A-F24), ddd/model/stereotypes.py (17), ddd/model/drawio/drawio_aggregate_model.py (17), ddd/model/clean_engineering_bridge.py (14) and ddd/ddd.py:98 (A-F22).

## Judgment — `cdd_guidance/builders/create_context_tool/create_context_tool.py`

### `no-legacy-api-after-refactor` — Fail
- create_context_tool.py:10 `CreateContextTool`: the old name of `CreatePracticeGuidance`, still deployed as its own skill; create_context_tool.md:3 describes `BaseContextTool`, `practices/base/`, `utilities/workspace/` and `@instruction` slots, none of which exist ("slots" is also a banned word).

### `eliminate-duplication` — Fail
- create_context_tool.py:16 `__init__`: the same four-parameter constructor as create_agent_toolset.py:16 and create_practice_guidance.py:15.
