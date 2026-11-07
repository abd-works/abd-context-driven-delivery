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

**Generated:** 2026-11-07 00:00:24 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 99
**Rules with graph hits:** 10
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

**Graph violations:** 6

- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L794): Operation `from_items`: Operation 'from_items' is 28 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L2115): Operation `annotate`: Operation 'annotate' is 25 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L2156): Operation `annotate`: Operation 'annotate' is 27 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_probe.py#L175): Operation `invoke`: Operation 'invoke' is 31 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_probe.py#L207): Operation `heavy_invoke`: Operation 'heavy_invoke' is 39 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_probe.py#L247): Operation `invoke_one`: Operation 'invoke_one' is 35 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

**Graph violations:** 7

- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L155): Operation `of`: Operation 'of' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L754): Operation `instantiate`: Operation 'instantiate' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L781): Operation `tool_subject_of`: Operation 'tool_subject_of' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L790): Operation `instantiate_all`: Operation 'instantiate_all' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L1224): Operation `for_callable`: Operation 'for_callable' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L1284): Operation `substitute_template`: Operation 'substitute_template' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L1198): Operation `receive`: Operation 'receive' is a classmethod; prefer an instance operation.

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

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L222): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L754): Parameter `item`: Parameter 'item' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/sub_agent/mark.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\sub_agent\mark.py#L40): Parameter `fn`: Parameter 'fn' does not reveal intent.

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

- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L985): Operation `on_stop`: Parameter 'payload' in 'on_stop' is vague.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L985): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.

Evaluate the current context against this rule (avoid-vague-parameter-names):

### `deep-module`

Keep most classes private (at most **40%** public) in each first-class module. A first-class module is a folder that owns `.context/module-context.md`. Nested folders that also own that file are separate modules — respect them. Nested folders that do not own it roll up to the nearest enclosing module-context folder, or to the folder you are querying if none sits in between. Count classes, not operations: a public method on a hidden class is not a second seam. Every public class is a signature you cannot change without editing every caller, so public classes are much harder to refactor than private ones.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/agent_tools](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools#L1): Module `agent_tools`: Module 'agent_tools' splits into many tiny classes (70); prefer a deep module with a small public surface.

Evaluate the current context against this rule (deep-module):

### `language-modules-one-section`

**Graph violations:** 58

- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L24): OoadClass `AgentToolValidationError`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L45): OoadClass `ExpansionMode`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L64): OoadClass `ExpansionResult`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L76): OoadClass `_LoopItem`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L84): OoadClass `ToolSetCollection`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L134): OoadClass `Collect`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L209): OoadClass `AgentToolSetOrigin`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L246): OoadClass `AgentToolSetTools`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L291): OoadClass `AgentToolSet`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L895): OoadClass `InstallDestination`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L903): OoadClass `AgentToolDestination`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L983): OoadClass `AgentTool`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L1175): OoadClass `AgentOperation`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L1182): OoadClass `GuidanceAgentOperation`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L1203): OoadClass `AgentInstructions`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L2088): OoadClass `AgentToolMark`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L2094): OoadClass `AgentInstructionsMark`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L2100): OoadClass `AgentToolSetMark`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L2142): OoadClass `ToolSetCollectionMark`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L2185): OoadClass `NoSessionLog`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L2193): OoadClass `ToolSubject`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L2202): OoadClass `OnSubject`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_diagnostics.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_diagnostics.py#L11): OoadClass `AgentToolsDiagnostics`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_diagnostics_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_diagnostics_spec.py#L1): OoadClass `_module`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_probe.py#L78): OoadClass `ProbeRequiresServingHost`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_probe.py#L82): OoadClass `AgentToolsProbe`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L49): OoadClass `CarInstance`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L63): OoadClass `_ModeFixture`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L77): OoadClass `_SelfCallAgent`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L101): OoadClass `_BodyModeFlipAgent`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L126): OoadClass `_CalleeAgent`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L143): OoadClass `_CallerAgent`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L162): OoadClass `_PropertyCallerAgent`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L609): OoadClass `_ForEachCallee`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L623): OoadClass `_ForEachCaller`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L667): OoadClass `_ScannerKit`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L674): OoadClass `_HostWithScanner`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L686): OoadClass `_ScanCaller`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L701): OoadClass `_BrokenProvider`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L780): OoadClass `_RulesPropertyHost`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L789): OoadClass `_PracticeWithRules`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L796): OoadClass `_NestedRulesCaller`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L833): OoadClass `_ExecBodyAgent`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L978): OoadClass `_DestinationFixture`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L1018): OoadClass `_BundleTools`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L1027): OoadClass `_PropertyHost`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L1039): OoadClass `_NestedChild`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L1046): OoadClass `_MarkedBag`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L1051): OoadClass `_NestedParent`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L1063): OoadClass `_TwoCollections`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L1081): OoadClass `_CollectChild`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L1088): OoadClass `_WrappedBag`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L1095): OoadClass `_CollectBag`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_spec.py#L1184): OoadClass `Parcel`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/cdd_diagnostic_bridge.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\cdd_diagnostic_bridge.py#L1): OoadClass `_module`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/name.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\name.py#L11): OoadClass `Name`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/parameter_schema.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\parameter_schema.py#L25): OoadClass `ParameterSchema`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/progress.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\progress.py#L1): OoadClass `_module`: Module 'agent_tools' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.

Evaluate the current context against this rule (language-modules-one-section):

### `limit-operation-parameters`

Have callers pass intent, not setup. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L1284): Operation `substitute_template`: Operation 'substitute_template' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_probe.py#L247): Operation `invoke_one`: Operation 'invoke_one' takes 4 parameters (maximum 3, excluding self).

Evaluate the current context against this rule (limit-operation-parameters):

### `missing-module-context`

**Graph violations:** 12

- [X] **ERROR** **[graph rule]** - [harness/agent_tools/_examples/logged_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\_examples\logged_probe.py#L8): OoadClass `LoggedProbe`: Module folder '_examples' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/_examples/reporter/reporter.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\_examples\reporter\reporter.py#L12): OoadClass `Reporter`: Module folder 'reporter' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/_examples/super_delegation/super_delegation_demo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\_examples\super_delegation\super_delegation_demo.py#L13): OoadClass `SuperBase`: Module folder 'super_delegation' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/_examples/super_delegation/super_delegation_demo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\_examples\super_delegation\super_delegation_demo.py#L30): OoadClass `ExplicitSuperChild`: Module folder 'super_delegation' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/_examples/super_delegation/super_delegation_demo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\_examples\super_delegation\super_delegation_demo.py#L42): OoadClass `EmptySuperChild`: Module folder 'super_delegation' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/_examples/super_delegation/super_delegation_demo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\_examples\super_delegation\super_delegation_demo.py#L50): OoadClass `EmptyWithReturn`: Module folder 'super_delegation' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/_examples/templated_md.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\_examples\templated_md.py#L8): OoadClass `TemplatedMdDemo`: Module folder '_examples' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/sub_agent/__init__.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\sub_agent\__init__.py#L1): OoadClass `_module`: Module folder 'sub_agent' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/sub_agent/fixtures.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\sub_agent\fixtures.py#L6): OoadClass `MarkedToolExample`: Module folder 'sub_agent' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/sub_agent/fixtures.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\sub_agent\fixtures.py#L15): OoadClass `MarkedActionExample`: Module folder 'sub_agent' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/sub_agent/mark.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\sub_agent\mark.py#L29): OoadClass `SubAgentMark`: Module folder 'sub_agent' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/sub_agent/sub_agent.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\sub_agent\sub_agent.py#L11): OoadClass `SubAgent`: Module folder 'sub_agent' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.

Evaluate the current context against this rule (missing-module-context):

### `one-way-deps`

Make dependencies flow in one direction without cycles. A cycle prevents either module from changing or being tested independently.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/agent_tools](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools#L1): Module `agent_tools`: Circular import between 'agent_tools' and '_examples' breaks one-way dependencies.

Evaluate the current context against this rule (one-way-deps):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 7

- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L113): Parameter `instance`: Parameter 'instance' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L155): Parameter `collection`: Parameter 'collection' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L155): Parameter `return_type`: Parameter 'return_type' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L754): Parameter `item`: Parameter 'item' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools.py#L2156): Parameter `target`: Parameter 'target' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_probe.py#L207): Parameter `host`: Parameter 'host' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\agent_tools\agent_tools_probe.py#L247): Parameter `host`: Parameter 'host' needs a domain-specific type, not a generic container.

Evaluate the current context against this rule (use-typed-signatures):

## Judgment — `harness/agent_tools/agent_tools.py`

### `never-swallow-exceptions` — Fail
- agent_tools.py:1796 `_run_expr`: the recipe interpreter catches every exception from evaluating a recipe line and returns silently, so a broken `@agent_instructions` recipe produces instructions with that line missing and nothing reports it.
- agent_tools.py:1830 `_dispatch_for`: an exception evaluating a loop's iterable becomes an empty list, so the loop's instructions vanish.
- agent_tools.py:1911 `_dispatch_if_statement`: an exception in an `if` test silently takes the `else` branch, so the agent receives the wrong branch's instructions.
- agent_tools.py:1968 `_dispatch_each`: an exception from the iterator member becomes `[]` and then `[None]`.
- agent_tools.py:1984 `_scan_return`: an exception evaluating a return value is replaced by the expression's source text, which is then sent to the agent as instructions.
- agent_tools.py:812 `from_items`: `except Exception` with `skip_errors` drops a toolset that failed to build without logging which one or why.

### `no-legacy-api-after-refactor` — Fail
- agent_tools.py:1296 `expand`: takes `context` and immediately `del context`; the parameter is dead and every caller (agent_tools.py:1263, cdd_guidance/actions/satisfy/satisfy.py:36) still passes `{}`.
- agent_tools.py:1284 `substitute_template`: a public classmethod used only by agent_tools_spec.py; it builds a throwaway `AgentInstructions` around `lambda self: None` to reach `_substitute`.
- agent_tools.py:790 `instantiate_all`: a one-line wrapper over `instantiate` with a single caller (harness/guidance_actions/guidance_actions.py:281), a second entry point for the same job beside `from_items`.

### `prefer-instance-operations` — Fail
- agent_tools.py:781 `tool_subject_of`: a classmethod that inspects another type; not a factory. Graph hit confirmed. (Hits at 155 `of`, 754 `instantiate`, 1224 `for_callable` dismissed: creation factories.)
- agent_tools.py:1284 `substitute_template`: classmethod reaching an instance helper through a throwaway instance. Graph hit confirmed.

### `no-prototype-swapping` — Fail
- agent_tools.py:777 `_built`: `toolset.__new__(toolset)` makes a toolset without running its constructor, so every field the constructor sets is missing and any tool that touches one fails at call time — the harm this rule names.

### `use-typed-signatures` — Fail
- agent_tools.py:754 `instantiate`: `item: Any` dispatches on dict, str, type, or instance; callers cannot tell which shape is wanted. Graph hit confirmed.

### `hold-state-on-the-object-not-in-parameters` — Fail
- agent_tools.py:1254 `invoke`: probes the toolset with `hasattr(toolset, "start_call")` and `getattr(toolset, "session_context", "")` instead of the toolset declaring those operations.

### `keep-operations-small-focused` — Fail
- agent_tools.py:794 `from_items`: prepares items, instantiates, skips errors and de-duplicates by type in one 28-line body. Graph hit confirmed (2115/2156 `annotate` also confirmed).

### `language-modules-one-section` — Fail
- agent_tools.py:24 `AgentToolValidationError`: harness/agent_tools/.context/module-context.md still has `## Language` and `## Modules` headings (lines 1 and 53). One document problem; the 57 other hits repeat it per class.

## Judgment — `harness/agent_tools/agent_tools_probe.py`

### `hide-inner-details` — Fail
- agent_tools_probe.py:259 `invoke_one`: reads `host._runtime`, the MCP host's private field.

### `hold-state-on-the-object-not-in-parameters` — Fail
- agent_tools_probe.py:175 `invoke`: takes `host` though the probe already holds `self.host`; `heavy_invoke` (line 207) requires it as a parameter.

### `do-not-invent-parallel-object-models` — Fail
- agent_tools_probe.py:175 `invoke`: each probe result is a `dict[str, Any]` with `mcp`, `color`, `skipped` keys, an untyped probe-result model rebuilt in every phase.

### `keep-operations-small-focused` — Fail
- agent_tools_probe.py:207 `heavy_invoke`: 39 lines covering import check, filtering, invoking and writing diagnostics. Graph hits at 175 and 247 confirmed.

## Judgment — `harness/agent_tools/sub_agent/sub_agent.py`

### `missing-module-context` — Fail
- sub_agent.py:11 `SubAgent`: harness/agent_tools/sub_agent defines classes and has no .context/module-context.md. Graph hit confirmed.

Dismissed graph hits: `missing-module-context` on `_examples/` (sample code); `one-way-deps` agent_tools to `_examples` (only agent_tools_spec.py imports `_examples`); `avoid-vague-parameter-names` and `prefer-instance-operations` in agent_tools_spec.py (test fixtures); `deep-module` count of 70 classes (includes spec fixtures and examples; the production public classes are the decorator surface).
