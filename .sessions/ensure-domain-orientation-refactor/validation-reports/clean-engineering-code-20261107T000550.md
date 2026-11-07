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

**Generated:** 2026-11-07 00:05:50 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 68
**Rules with graph hits:** 12
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

- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance_probe.py#L106): Operation `arguments_for`: Operation 'arguments_for' is 48 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L129): Operation `inject_rules`: Operation 'inject_rules' is 25 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

**Graph violations:** 10

- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L157): Operation `child`: Operation 'child' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance_probe.py#L31): Operation `filtered_by`: Operation 'filtered_by' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\practice_catalogue.py#L31): Operation `keys`: Operation 'keys' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\practice_catalogue.py#L36): Operation `has`: Operation 'has' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\practice_catalogue.py#L40): Operation `practices`: Operation 'practices' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\practice_catalogue.py#L45): Operation `practice`: Operation 'practice' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\practice_catalogue.py#L57): Operation `practice_class`: Operation 'practice_class' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\practice_catalogue.py#L65): Operation `module_of`: Operation 'module_of' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\practice_catalogue.py#L70): Operation `practice_named`: Operation 'practice_named' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L55): Operation `strip_fence`: Operation 'strip_fence' is a classmethod; prefer an instance operation.

Evaluate the current context against this rule (prefer-instance-operations):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

Evaluate the current context against this rule (keep-operations-single-responsibility):

### `simplify-control-flow`

Handle the failing or empty cases first and return. Keep the main path flat. Do not nest more than three levels — deeper than that you cannot tell which conditions hold on a given line without reading back up, and that is where the unhandled branch hides.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance_probe.py#L106): Operation `arguments_for`: Operation 'arguments_for' nests control flow 9 levels deep (max 3).

Evaluate the current context against this rule (simplify-control-flow):

### `errors-out-of-existence`

For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L691): Operation `new_report_path`: Operation 'new_report_path' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\practice_catalogue.py#L57): Operation `practice_class`: Operation 'practice_class' raises on an empty or missing value; return a quiet result instead.

Evaluate the current context against this rule (errors-out-of-existence):

### `no-prototype-swapping`

An object keeps the class it was built as. Do not change it afterwards with `Object.setPrototypeOf`, `__proto__ =`, or `__class__ =`. When a subclass needs to make its own instances, give the base an overridable factory (`blank()`) or build the right class directly. A swapped object skips its constructor, so fields the subclass sets up are missing and nothing tells you.

Evaluate the current context against this rule (no-prototype-swapping):

### `use-intention-revealing-names`

Name each class, property, operation, and parameter so it answers why it exists. Do not abbreviate.

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L728): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L736): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L763): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L32): Parameter `value`: Parameter 'value' does not reveal intent.

Evaluate the current context against this rule (use-intention-revealing-names):

### `use-consistent-naming`

Use one word per concept. Pick one verb and use it everywhere (`fetch_`, not a mix of `fetch_`, `get_`, and `retrieve_`). Two words for one concept is how the same logic gets written twice — nobody searching for `fetch_` finds the `retrieve_` that already does the job.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L20): OoadClass `AppliesTo`: Operation 'alwaysApply' uses camelCase while other operations on 'AppliesTo' use the other convention.
- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L111): OoadClass `RulesCollection`: Operation 'appliesTo' uses camelCase while other operations on 'RulesCollection' use the other convention.

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

- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L129): Operation `inject_rules`: Parameter 'payload' in 'inject_rules' is vague.
- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L129): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.

Evaluate the current context against this rule (avoid-vague-parameter-names):

### `keep-classes-single-responsibility`

Give each class one reason to change.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L179): OoadClass `PracticeGuidance`: Class 'PracticeGuidance' exposes 14 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L642): OoadClass `FidelityGuidance`: Class 'FidelityGuidance' exposes 10 public operations (budget ~9). Split responsibilities.

Evaluate the current context against this rule (keep-classes-single-responsibility):

### `limit-operation-parameters`

Have callers pass intent, not setup. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L486): Operation `render`: Operation 'render' takes 4 parameters (maximum 3, excluding self).

Evaluate the current context against this rule (limit-operation-parameters):

### `missing-module-context`

**Graph violations:** 34

- [X] **ERROR** **[graph rule]** - [harness/guidance/__init__.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\__init__.py#L1): OoadClass `_module`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/fixtures/agentic_ops/agentic_ops.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\fixtures\agentic_ops\agentic_ops.py#L14): OoadClass `SampleAgenticOps`: Module folder 'agentic_ops' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/fixtures/agentic_ops/agentic_ops.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\fixtures\agentic_ops\agentic_ops.py#L42): OoadClass `SampleMcpOps`: Module folder 'agentic_ops' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/fixtures/agentic_ops/hook_ops.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\fixtures\agentic_ops\hook_ops.py#L10): OoadClass `SampleHookOps`: Module folder 'agentic_ops' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/fixtures/other_tool/other_tool_host.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\fixtures\other_tool\other_tool_host.py#L7): OoadClass `OtherTool`: Module folder 'other_tool' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/fixtures/sample_tool/sample_tool_host.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\fixtures\sample_tool\sample_tool_host.py#L11): OoadClass `SampleTool`: Module folder 'sample_tool' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/fixtures/sample_tool/sample_tool_host.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\fixtures\sample_tool\sample_tool_host.py#L24): OoadClass `SampleGuidance`: Module folder 'sample_tool' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/fixtures/sample_tool/sample_tool_host.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\fixtures\sample_tool\sample_tool_host.py#L30): OoadClass `SampleMcpGuidance`: Module folder 'sample_tool' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/fixtures/sample_tool/sample_tool_host.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\fixtures\sample_tool\sample_tool_host.py#L39): OoadClass `SamplePracticeGuidance`: Module folder 'sample_tool' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/fixtures/sample_tool/sample_tool_host.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\fixtures\sample_tool\sample_tool_host.py#L45): OoadClass `SamplePracticeWithFidelities`: Module folder 'sample_tool' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/fixtures/sample_tool/sample_tool_host.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\fixtures\sample_tool\sample_tool_host.py#L49): OoadClass `SampleMcpPractice`: Module folder 'sample_tool' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/fixtures/split_tool/split_tool.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\fixtures\split_tool\split_tool.py#L7): OoadClass `SplitPracticeGuidance`: Module folder 'split_tool' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L39): OoadClass `FidelityWithoutSessionError`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L47): OoadClass `Guidance`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L143): OoadClass `GuidanceCollection`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L179): OoadClass `PracticeGuidance`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L642): OoadClass `FidelityGuidance`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance_diagnose_heavy_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance_diagnose_heavy_spec.py#L1): OoadClass `_module`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance_diagnose_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance_diagnose_spec.py#L1): OoadClass `_module`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance_diagnostics.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance_diagnostics.py#L11): OoadClass `GuidanceDiagnostics`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance_probe.py#L21): OoadClass `GuidanceProbe`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance_spec.py#L1): OoadClass `_module`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\practice_catalogue.py#L12): OoadClass `PracticeCatalogue`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/project_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\project_rules.py#L18): OoadClass `ProjectRulesets`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/project_rules_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\project_rules_spec.py#L21): OoadClass `_Fidelities`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/project_rules_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\project_rules_spec.py#L29): OoadClass `_StoriesRules`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/project_rules_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\project_rules_spec.py#L64): OoadClass `_Node`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L20): OoadClass `AppliesTo`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L61): OoadClass `Rule`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L111): OoadClass `RulesCollection`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/schema.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\schema.py#L26): OoadClass `SchemaType`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/schema.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\schema.py#L49): OoadClass `Schema`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/schema_map.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\schema_map.py#L1): OoadClass `_module`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/guidance/schema_map_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\schema_map_spec.py#L1): OoadClass `_module`: Module folder 'guidance' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.

Evaluate the current context against this rule (missing-module-context):

### `use-explicit-dependencies`

Pass every collaborator through the constructor. Do not reach for a global or construct a collaborator inside construction. A collaborator the class fetches or builds itself cannot be swapped, so the class can only ever run against that one implementation.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L111): OoadClass `RulesCollection`: Class 'RulesCollection' constructs 'AppliesTo' inside its constructor.

Evaluate the current context against this rule (use-explicit-dependencies):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 7

- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L486): Parameter `content`: Parameter 'content' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance.py#L763): Parameter `value`: Parameter 'value' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance_probe.py#L31): Parameter `installer`: Parameter 'installer' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\guidance_probe.py#L106): Parameter `member`: Parameter 'member' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L32): Parameter `value`: Parameter 'value' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L383): Parameter `parent`: Parameter 'parent' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance/rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\guidance\rule.py#L456): Parameter `paths`: Parameter 'paths' needs a domain-specific type, not a generic container.

Evaluate the current context against this rule (use-typed-signatures):

## Judgment — `harness/guidance/guidance.py`

### `use-exceptions-properly` — Fail
- guidance.py:577 `_live_adapter`: guesses a format adapter's constructor by calling `create()`, then `adapter(tests_root=...)`, then `adapter()`, catching `TypeError` each time, and finally returns the class itself instead of an instance. A `TypeError` raised inside a constructor body is caught as "wrong signature", and a caller can receive a class where it expects an adapter, so `render` fails later far from the cause. Each format adapter should declare one way to be built.

### `no-legacy-api-after-refactor` — Fail
- guidance.py:157 `child`: classmethod takes `body` and never uses it.

### `keep-classes-single-responsibility` — Fail
- guidance.py:179 `PracticeGuidance`: 14 public operations covering markdown sections, fidelity selection, format adapters and rendering. Graph hit confirmed; FidelityGuidance (642) hit confirmed (rules, reports folder and report naming, files).

## Judgment — `harness/guidance/practice_catalogue.py`

### `do-not-invent-parallel-object-models` — Fail
- practice_catalogue.py:22 `_REFS`: a hand-kept table of the five practices and their import paths, a second registry beside the one the installer builds from `@agent_toolset` annotations; a new practice works in one and is missing from the other.

### `hold-state-on-the-object-not-in-parameters` — Fail
- practice_catalogue.py:45 `practice`: hands every caller the same cached `PracticeGuidance` from the class-level `_shared` dict and relies on the docstring ("do not change its current fidelity or format") to keep callers from mutating shared state. A practice's current fidelity is state the practice should hold per session; one shared instance per process means a caller that sets it changes every other caller's view.

### `prefer-instance-operations` — Fail
- practice_catalogue.py:31 `keys`: the whole catalogue is classmethods over class-level dicts (`keys`, `has`, `practices`, `practice`, `practice_class`, `module_of`, `practice_named`), a module-global registry with no instance to pass or replace. Graph hits confirmed.

## Judgment — `harness/guidance/guidance_probe.py`

### `simplify-control-flow` — Fail
- guidance_probe.py:106 `arguments_for`: a 48-line `if/elif` chain keyed on MCP tool names (`render.render`, `partition.index`, `sketch.save_sketch`, ...). Graph hits (length, nesting) confirmed.

### `do-not-invent-parallel-object-models` — Fail
- guidance_probe.py:121 `arguments_for`: the probe holds its own copy of what each action's parameters mean; the action is the owner and should say how it is probed, otherwise a renamed parameter breaks the probe silently.

## Judgment — `harness/guidance/rule.py`

### `use-consistent-naming` — Fail
- rule.py:20 `AppliesTo`: camelCase `alwaysApply`, and `appliesTo` on RulesCollection (111), beside snake_case operations. The camelCase follows the rule front-matter keys, but the Python members should not; graph hits confirmed.

## Judgment — `harness/guidance/__init__.py`

### `missing-module-context` — Fail
- __init__.py:1 `guidance`: harness/guidance/.context holds only fidelities-collection-sketch.md and no module-context.md. Graph hit confirmed; the hits under fixtures/ and *_spec.py are dismissed.

Dismissed: `errors-out-of-existence` on `new_report_path` (691) and `practice_class` (57) — a fidelity with no session and an unknown practice key are real failures with named exceptions; `use-explicit-dependencies` on RulesCollection building `AppliesTo` (a value).
