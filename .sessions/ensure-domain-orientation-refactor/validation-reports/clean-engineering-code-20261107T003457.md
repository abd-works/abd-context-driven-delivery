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

**Generated:** 2026-11-07 00:34:57 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 32
**Rules with graph hits:** 3
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

- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/lern_domain_driven/tier_facts.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\patterns\lern_domain_driven\tier_facts.py#L80): Operation `web_path_literals`: Operation 'web_path_literals' uses the unnamed number 40.

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

**Graph violations:** 13

- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/cdd_web_domain_access/access_facts.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\patterns\cdd_web_domain_access\access_facts.py#L1): OoadClass `_module`: Module folder 'cdd_web_domain_access' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/cdd_web_domain_access/practices/ddd/rules/access_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\patterns\cdd_web_domain_access\practices\ddd\rules\access_rules.py#L8): OoadClass `OneClassPerObject`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/cdd_web_domain_access/practices/ddd/rules/access_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\patterns\cdd_web_domain_access\practices\ddd\rules\access_rules.py#L21): OoadClass `StateLivesBehindTheTool`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/cdd_web_domain_access/practices/ddd/rules/access_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\patterns\cdd_web_domain_access\practices\ddd\rules\access_rules.py#L34): OoadClass `AdapterIsGenerated`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/cdd_web_domain_access/practices/ddd/rules/access_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\patterns\cdd_web_domain_access\practices\ddd\rules\access_rules.py#L48): OoadClass `AnnotateWhatTypeScriptReads`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/lern_domain_driven/lern_domain_driven.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\patterns\lern_domain_driven\lern_domain_driven.py#L18): OoadClass `LernDomainDriven`: Module folder 'lern_domain_driven' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/lern_domain_driven/practices/ddd/rules/lern_tier_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\patterns\lern_domain_driven\practices\ddd\rules\lern_tier_rules.py#L8): OoadClass `NodeRepositoryParsesOnRead`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/lern_domain_driven/practices/ddd/rules/lern_tier_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\patterns\lern_domain_driven\practices\ddd\rules\lern_tier_rules.py#L30): OoadClass `PostedBodyParsedInNode`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/lern_domain_driven/practices/ddd/rules/lern_tier_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\patterns\lern_domain_driven\practices\ddd\rules\lern_tier_rules.py#L57): OoadClass `ThrowHttpExceptions`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/lern_domain_driven/practices/ddd/rules/lern_tier_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\patterns\lern_domain_driven\practices\ddd\rules\lern_tier_rules.py#L73): OoadClass `OneHomeForWebPaths`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/lern_domain_driven/practices/ddd/rules/lern_tier_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\patterns\lern_domain_driven\practices\ddd\rules\lern_tier_rules.py#L86): OoadClass `ResetEveryRepository`: Module folder 'rules' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/lern_domain_driven/tier_facts.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\patterns\lern_domain_driven\tier_facts.py#L1): OoadClass `_module`: Module folder 'lern_domain_driven' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/mern_domain_driven/mern_domain_driven.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\patterns\mern_domain_driven\mern_domain_driven.py#L16): OoadClass `MernDomainDriven`: Module folder 'mern_domain_driven' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.

Evaluate the current context against this rule (missing-module-context):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 18

- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/cdd_web_domain_access/practices/ddd/rules/access_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\patterns\cdd_web_domain_access\practices\ddd\rules\access_rules.py#L14): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/cdd_web_domain_access/practices/ddd/rules/access_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\patterns\cdd_web_domain_access\practices\ddd\rules\access_rules.py#L14): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/cdd_web_domain_access/practices/ddd/rules/access_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\patterns\cdd_web_domain_access\practices\ddd\rules\access_rules.py#L27): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/cdd_web_domain_access/practices/ddd/rules/access_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\patterns\cdd_web_domain_access\practices\ddd\rules\access_rules.py#L27): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/cdd_web_domain_access/practices/ddd/rules/access_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\patterns\cdd_web_domain_access\practices\ddd\rules\access_rules.py#L40): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/cdd_web_domain_access/practices/ddd/rules/access_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\patterns\cdd_web_domain_access\practices\ddd\rules\access_rules.py#L40): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/cdd_web_domain_access/practices/ddd/rules/access_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\patterns\cdd_web_domain_access\practices\ddd\rules\access_rules.py#L54): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/cdd_web_domain_access/practices/ddd/rules/access_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\patterns\cdd_web_domain_access\practices\ddd\rules\access_rules.py#L54): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/lern_domain_driven/practices/ddd/rules/lern_tier_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\patterns\lern_domain_driven\practices\ddd\rules\lern_tier_rules.py#L17): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/lern_domain_driven/practices/ddd/rules/lern_tier_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\patterns\lern_domain_driven\practices\ddd\rules\lern_tier_rules.py#L17): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/lern_domain_driven/practices/ddd/rules/lern_tier_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\patterns\lern_domain_driven\practices\ddd\rules\lern_tier_rules.py#L40): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/lern_domain_driven/practices/ddd/rules/lern_tier_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\patterns\lern_domain_driven\practices\ddd\rules\lern_tier_rules.py#L40): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/lern_domain_driven/practices/ddd/rules/lern_tier_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\patterns\lern_domain_driven\practices\ddd\rules\lern_tier_rules.py#L63): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/lern_domain_driven/practices/ddd/rules/lern_tier_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\patterns\lern_domain_driven\practices\ddd\rules\lern_tier_rules.py#L63): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/lern_domain_driven/practices/ddd/rules/lern_tier_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\patterns\lern_domain_driven\practices\ddd\rules\lern_tier_rules.py#L79): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/lern_domain_driven/practices/ddd/rules/lern_tier_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\patterns\lern_domain_driven\practices\ddd\rules\lern_tier_rules.py#L79): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/lern_domain_driven/practices/ddd/rules/lern_tier_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\patterns\lern_domain_driven\practices\ddd\rules\lern_tier_rules.py#L95): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/lern_domain_driven/practices/ddd/rules/lern_tier_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\patterns\lern_domain_driven\practices\ddd\rules\lern_tier_rules.py#L95): Parameter `context`: Parameter 'context' is missing a type annotation.

Evaluate the current context against this rule (use-typed-signatures):

## Judgment — `cdd_guidance/patterns/mern_domain_driven/mern_domain_driven.py`

### `eliminate-duplication` — Fail
- mern_domain_driven.py:16 `MernDomainDriven`: its constructor and `_stories` companion are a line-for-line copy of cdd_guidance/patterns/lern_domain_driven/lern_domain_driven.py:18 `LernDomainDriven`; the two stack patterns differ only in `pattern`, `story_test_folder` and their markdown, so the shared part belongs on one pattern base.

### `hold-state-on-the-object-not-in-parameters` — Fail
- mern_domain_driven.py:26 `_stories`: builds a fresh `Stories(fidelity="acceptance_tests", format="typescript")` on each call instead of the session's Stories practice, so a fidelity or format the session holds for Stories is ignored and `mode = "tool"` is set on a throwaway (same in lern_domain_driven.py).

## Judgment — `cdd_guidance/patterns/lern_domain_driven/practices/ddd/rules/lern_tier_rules.py`

### `use-typed-signatures` — Fail
- lern_tier_rules.py:17 `check`: every rule's `check(node, context)` is untyped (graph hits at 17, 40, 63, 79, 95 and access_rules.py:14, 27, 40, 54 confirmed); harness/graph/rule_context.py has the context type these should name.

### `missing-module-context` — Fail
- lern_tier_rules.py:8 `NodeRepositoryParsesOnRead`: the patterns' rules folders and the pattern folders themselves (lern_domain_driven, mern_domain_driven, cdd_web_domain_access) have no .context/module-context.md. Graph hits confirmed.

Dismissed: `provide-meaningful-context` 40 in tier_facts.py:80 (low). builders/ holds only templates (`templates/*.py` are scaffolds the builders copy), not judged.
