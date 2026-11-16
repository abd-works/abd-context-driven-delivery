# Validate

Take the persona of a **critical judge** — do not edit the artifact.

1. Read the appropriate practice and fidelity level guidlines and rules. Scope judgment to artifacts passed into context.
1b. **Stories in the session's scope.** A session's ticket names its stories (its `Story:` headings); they are the increment. Every one of them is generated and validated with the patterns its content is generated with: generate uses the session's overlays and records them in `.context/patterns.md` at the root of each folder it writes, with the roles the folder holds of a pattern whose layers sit in several folders; validate reads that file. Stories the ticket does not name belong to other increments: leave them alone, and do not judge or report them. **Measure the scope, not the repository:** the graph report keeps only the findings inside the work's scope, on those stories and everything under them (their scenarios, steps, and examples) and in the files the call names; name, as paths, exactly the modules and tests the work changed. Judge only those too.
1c. **Patterns used in part.** The graph checks content against every applied pattern's schema and rules mechanically (`conforms-to-schema` and each pattern's rules), so a pattern used only in part reports members its content never meant to have. Judge each such finding against the patterns' own instructions and the patterns the content was generated with (`.context/patterns.md`, with the roles a folder holds): when another applied pattern supplies that member in its own way, the finding is noise; say so in the judgment and name the pattern that covers it (LERN overlaid with cdd_web_domain_access has its domain in Python behind MCP, so LERN's TypeScript domain, node tier, routes and lowdb store are not expected). Every other finding stands.
2. Use each **practice** as the rubric — report Pass or Fail per named practice fidelity and named rule with brief evidence. There is no third verdict: a rule that is only partly met is a Fail, because a softer verdict lets a broken rule through review.
3. When **paths** names the files being edited, the graph is built from just those files as they are now, and its rules run on them. Pass the files you wrote, not the whole tree. Without **paths**, when **graph** is `true`, read the session's graph (`graph.json` in the session's own folder, created for the session); when it is a path (or list of paths), read that `graph_return_nodes` JSON or saved graph. Append a **Graph rule validation** report for each guidance's practice. Each rule is one section: heading, rule text, any graph hits (**[graph rule]**), then the AI judgment prompt for that rule.
4. Collection validate on graph-backed practices reads the working copy and reports each rule hit. A single base Rule is instruction text only.
5. Do not fix. Report failures for fixing, then add your judgment for each rule to the report this action saved, so the board links to the whole result. It names the report's path at the end of its reply.
6. Append the judgment to the end of the saved report in exactly this shape. The session board parses it, lists each finding beside the graph's hits, opens the finding's file at its line, and sends a Fix back, so a finding in any other shape is lost:

   ```markdown
   ## Judgment — `.context/story-map.md`

   ### `rule-slug` — Fail
   - story-map.md:86 `Archive Ticket`: what breaks the rule, and why.

   ### `other-rule-slug` — Fail
   - story-map.md:148 `Send Sketch Iterate Or Document`: what breaks the rule, and why.
   ```

   - **One `## Judgment — ` section per judged file,** with an em dash, and the file in backticks as a path from the project's root, the way the session names paths. Never an absolute path or another checkout's path, because the board opens the file in this project and cannot open one anywhere else.
   - **One `### ` heading per rule that fails:** the rule slug in backticks, an em dash, then `Fail`. Leave passing rules out of these headings; a table or a Passes paragraph after the judgment may list them.
   - **One bullet per finding,** opening with the judged file's name, a colon, and one line number (`story-map.md:86`), then a space and what breaks the rule. A finding that spans lines takes its first line, and a finding at two places is two bullets, because the board opens each finding at one line.


Judge the graph validate built from the checked format's files (python: C:/dev/abd-cdd-version-1-refactoring/{module}/), saved at C:\dev\abd-context-driven-delivery\.sessions\version-1-refactoring\.context\graph.json: its classes, operations, parameters, properties, relationships, and dependencies, against each rule. Read a file only to see what a node stands for; whether a model document matches the code is a separate, secondary check.

# Graph rule validation

**Generated:** 2026-11-16 16:32:01 UTC
**Project:** abd-cdd-version-1-refactoring
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-context-driven-delivery\.sessions\version-1-refactoring\.context\graph.json`

## Summary

**Total graph violations:** 192
**Rules with graph hits:** 20
**AI rules in scope:** 24

## Rules

Each rule shows its guidance text, any graph scanner hits (`**[graph rule]**`), then the AI judgment prompt.

### `vocabulary-traces-to-source`

Take every term from the source. The English term and the code name are the same word: *shopping cart* is `ShoppingCart`. When the code says a different word than the domain, every reader keeps a translation in their head, and the two names drift until they mean different things.

Evaluate the current context against this rule (vocabulary-traces-to-source):

### `do-not-invent-terms`

Do not invent a second noun or a parallel vocabulary. A second noun for the same thing becomes a second class, and then the same rule has to be written and fixed in both.

Evaluate the current context against this rule (do-not-invent-terms):

### `do-not-invent-parallel-object-models`

Keep one object model. Follow the nouns and verbs the rest of the graph already uses for that concept. A class that joins types the rest of the graph keeps apart is a second model — a big ball of mud — and every rule then has to be written and fixed in both. When data or behavior already belongs to an object, extend that object and hand callers the object itself: `ticket.session.practices["stories"].fidelities["story_map"].files()`, not `ticket.files(["stories-story-map"])`. A second model is rarely a whole class family; more often it is a small copy beside the owner: a dict holding one field from each member (`fidelity_states`, `violation_counts`), a `*_name` copy of a reference (`column_name`), a helper class that does the owner's job (`TicketFiles`), a bag of a few of the owner's answers (`Workspace`), or a `*Model` / `*Entry` family scraped from live objects. A copy hides that the owner is missing the behavior, so the next caller builds another copy and a fix to the owner never reaches it. **Checking it:** this rule spans modules, and the copy looks fine in the file that holds it. For every property, data field, dict, and helper class the changed code adds, name the class that already owns that data and read it; the rule fails when the owner holds it or should, and the change copies it instead of returning or extending the owner. Count the members of a class that delegates: dozens of members on a class that only reads its collaborators means it is copying them.

**Graph violations:** 5

- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/cdd_web_domain_access/access_facts.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\cdd_web_domain_access\access_facts.py#L23): OoadClass `AccessFile`: Class 'AccessFile' copies the fields ['_source', 'name', 'text'] of 'MigrationFile'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/lern_domain_driven/graph_overlay.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\lern_domain_driven\graph_overlay.py#L48): OoadClass `_LernReading`: Class '_LernReading' copies the fields ['graph', 'overlay', 'root'] of '_OssReading'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/lern_domain_driven/tier_facts.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\lern_domain_driven\tier_facts.py#L48): OoadClass `TierFile`: Class 'TierFile' copies the fields ['_source', 'relative', 'text'] of 'OssFile'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/hub_board.py](C:\dev\abd-cdd-version-1-refactoring\harness\catalog_generator\hub_board.py#L74): OoadClass `HubBoard`: Class 'HubBoard' copies the fields ['practices', 'stages', 'stories'] of 'ApproachGrids'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [harness/whiteboard/whiteboard.py](C:\dev\abd-cdd-version-1-refactoring\harness\whiteboard\whiteboard.py#L32): OoadClass `Box`: Class 'Box' copies the fields ['h', 'w', 'x', 'y'] of 'MiroShape'. Use one canonical model type.

Evaluate the current context against this rule (do-not-invent-parallel-object-models):

### `hide-inner-details`

Expose behavior through named operations. Do not let callers see how the class stores or arranges its data — once they read the storage directly it becomes a public contract you cannot change. Private fields on the same class hide implementation; you do not need a second class for that. Read-only to callers can mean return a copy or immutable view from a property — it does not require a frozen class or a second type to hold build steps.

Evaluate the current context against this rule (hide-inner-details):

### `hold-state-on-the-object-not-in-parameters`

Keep what an object knows on the object, and let its operations read it there. A session holds its practices, a practice holds its fidelities and its current fidelity, a fidelity holds its actions and the format it last used, and an action is made for its session: `session.practices.stories.fidelities.story_map.actions.generate(format="drawio")`, not `Generate.commands_for(session, fidelities, formats)`. A value the caller supplies once, such as a format, is saved on the object that owns it, so the next operation on that object reads it instead of being handed it again. The rule fails when an operation takes, as a parameter, state its own object holds or should hold: the same argument handed down through several layers; a session, guidance, or ticket passed to every call on an object made for it; a name or slug passed so the receiver can look up an object the caller already holds; state written into a string (`session=...`) and parsed back; or a field set on a shared object for one call and restored afterwards. Every layer that passes the value is another place to pass the wrong one, and a call started from inside another, which nobody hands the value to, falls back to a global such as the current session and acts on the wrong object.

Evaluate the current context against this rule (hold-state-on-the-object-not-in-parameters):

### `keep-operations-small-focused`

Keep each operation short enough to read as one thought — under 20 statements. A multi-line call, list, or string initializer is one statement. When it grows, extract a private helper whose name says why that slice exists.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\practices\clean_engineering\model\diagram\class_layout.py#L468): Operation `run`: Operation 'run' is 50 statements (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `prefer-instance-operations`

Keep operations on the instance. Do not annotate them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, `now` (a new value for this moment), and `every` (each value the class allows). A global accessor such as `current` or `shared` is not a factory: it hands every caller the same object from class-level state, so it stays an instance operation on the object that holds that state, or goes.

**Graph violations:** 43

- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\dev\abd-cdd-version-1-refactoring\harness\agent_tools\agent_tools.py#L585): Operation `instantiate`: Operation 'instantiate' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\dev\abd-cdd-version-1-refactoring\harness\agent_tools\agent_tools.py#L1316): Operation `installs_member`: Operation 'installs_member' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/agent_tools.py](C:\dev\abd-cdd-version-1-refactoring\harness\agent_tools\agent_tools.py#L1327): Operation `installs_member`: Operation 'installs_member' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/tool_call.py](C:\dev\abd-cdd-version-1-refactoring\harness\agent_tools\tool_call.py#L159): Operation `open_sessions_with`: Operation 'open_sessions_with' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/tool_call.py](C:\dev\abd-cdd-version-1-refactoring\harness\agent_tools\tool_call.py#L176): Operation `session_in`: Operation 'session_in' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/annotations/annotation.py](C:\dev\abd-cdd-version-1-refactoring\harness\annotations\annotation.py#L111): Operation `annotates`: Operation 'annotates' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/annotations/annotation.py](C:\dev\abd-cdd-version-1-refactoring\harness\annotations\annotation.py#L116): Operation `written_as`: Operation 'written_as' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/annotations/annotation.py](C:\dev\abd-cdd-version-1-refactoring\harness\annotations\annotation.py#L122): Operation `installs_member`: Operation 'installs_member' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/annotations/annotation.py](C:\dev\abd-cdd-version-1-refactoring\harness\annotations\annotation.py#L127): Operation `companion_flags`: Operation 'companion_flags' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/annotations/annotation.py](C:\dev\abd-cdd-version-1-refactoring\harness\annotations\annotation.py#L157): Operation `names_on`: Operation 'names_on' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/annotations/annotation.py](C:\dev\abd-cdd-version-1-refactoring\harness\annotations\annotation.py#L171): Operation `annotates`: Operation 'annotates' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/annotations/annotation.py](C:\dev\abd-cdd-version-1-refactoring\harness\annotations\annotation.py#L184): Operation `annotates`: Operation 'annotates' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/annotations/annotation.py](C:\dev\abd-cdd-version-1-refactoring\harness\annotations\annotation.py#L212): Operation `installs_member`: Operation 'installs_member' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/annotations/annotation.py](C:\dev\abd-cdd-version-1-refactoring\harness\annotations\annotation.py#L217): Operation `name_annotated_on`: Operation 'name_annotated_on' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/annotations/annotation.py](C:\dev\abd-cdd-version-1-refactoring\harness\annotations\annotation.py#L223): Operation `companion_flags`: Operation 'companion_flags' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/annotations/annotation.py](C:\dev\abd-cdd-version-1-refactoring\harness\annotations\annotation.py#L227): Operation `disabled_on`: Operation 'disabled_on' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/chat/chat.py](C:\dev\abd-cdd-version-1-refactoring\harness\chat\chat.py#L233): Operation `list`: Operation 'list' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/chat/chat.py](C:\dev\abd-cdd-version-1-refactoring\harness\chat\chat.py#L242): Operation `open`: Operation 'open' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/graph/model_node.py](C:\dev\abd-cdd-version-1-refactoring\harness\graph\model_node.py#L173): Operation `register_practice`: Operation 'register_practice' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/graph/model_node.py](C:\dev\abd-cdd-version-1-refactoring\harness\graph\model_node.py#L180): Operation `practice_kind`: Operation 'practice_kind' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/graph/pattern_overlays.py](C:\dev\abd-cdd-version-1-refactoring\harness\graph\pattern_overlays.py#L106): Operation `register`: Operation 'register' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/action_catalogue.py](C:\dev\abd-cdd-version-1-refactoring\harness\guidance\action_catalogue.py#L121): Operation `register`: Operation 'register' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/action_catalogue.py](C:\dev\abd-cdd-version-1-refactoring\harness\guidance\action_catalogue.py#L127): Operation `run_actions_with`: Operation 'run_actions_with' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/action_catalogue.py](C:\dev\abd-cdd-version-1-refactoring\harness\guidance\action_catalogue.py#L132): Operation `runner`: Operation 'runner' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/action_catalogue.py](C:\dev\abd-cdd-version-1-refactoring\harness\guidance\action_catalogue.py#L139): Operation `fidelity_actions`: Operation 'fidelity_actions' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/action_catalogue.py](C:\dev\abd-cdd-version-1-refactoring\harness\guidance\action_catalogue.py#L145): Operation `toolsets`: Operation 'toolsets' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/action_catalogue.py](C:\dev\abd-cdd-version-1-refactoring\harness\guidance\action_catalogue.py#L150): Operation `actions`: Operation 'actions' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/action_catalogue.py](C:\dev\abd-cdd-version-1-refactoring\harness\guidance\action_catalogue.py#L163): Operation `names`: Operation 'names' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/action_catalogue.py](C:\dev\abd-cdd-version-1-refactoring\harness\guidance\action_catalogue.py#L167): Operation `has`: Operation 'has' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/action_catalogue.py](C:\dev\abd-cdd-version-1-refactoring\harness\guidance\action_catalogue.py#L171): Operation `action`: Operation 'action' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\dev\abd-cdd-version-1-refactoring\harness\guidance\practice_catalogue.py#L46): Operation `register`: Operation 'register' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\dev\abd-cdd-version-1-refactoring\harness\guidance\practice_catalogue.py#L51): Operation `register_supplements`: Operation 'register_supplements' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\dev\abd-cdd-version-1-refactoring\harness\guidance\practice_catalogue.py#L57): Operation `supplement_classes`: Operation 'supplement_classes' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\dev\abd-cdd-version-1-refactoring\harness\guidance\practice_catalogue.py#L62): Operation `keys`: Operation 'keys' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\dev\abd-cdd-version-1-refactoring\harness\guidance\practice_catalogue.py#L67): Operation `has`: Operation 'has' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\dev\abd-cdd-version-1-refactoring\harness\guidance\practice_catalogue.py#L89): Operation `create_all`: Operation 'create_all' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\dev\abd-cdd-version-1-refactoring\harness\guidance\practice_catalogue.py#L100): Operation `_always_on_supplements`: Operation '_always_on_supplements' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\dev\abd-cdd-version-1-refactoring\harness\guidance\practice_catalogue.py#L109): Operation `practice_class`: Operation 'practice_class' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_catalogue.py](C:\dev\abd-cdd-version-1-refactoring\harness\guidance\practice_catalogue.py#L116): Operation `_registered`: Operation '_registered' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_server.py](C:\dev\abd-cdd-version-1-refactoring\harness\hooks\hook_server.py#L436): Operation `show_toasts_with`: Operation 'show_toasts_with' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hooks.py](C:\dev\abd-cdd-version-1-refactoring\harness\hooks\hooks.py#L92): Operation `companion_flags`: Operation 'companion_flags' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hooks.py](C:\dev\abd-cdd-version-1-refactoring\harness\hooks\hooks.py#L96): Operation `disabled_on`: Operation 'disabled_on' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/installation/repository_toolsets.py](C:\dev\abd-cdd-version-1-refactoring\harness\installation\repository_toolsets.py#L93): Operation `of_running_checkout`: Operation 'of_running_checkout' is a classmethod; prefer an instance operation.

Evaluate the current context against this rule (prefer-instance-operations):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

**Graph violations:** 7

- [X] **ERROR** **[graph rule]** - [cdd_guidance/context_setup/context_setup.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\context_setup\context_setup.py#L138): Operation `_markdown_of`: Operation '_markdown_of' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/graph_reading.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\practices\clean_engineering\model\graph_reading.py#L216): Operation `_model_in`: Operation '_model_in' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/json/nodes.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\practices\stories\model\json\nodes.py#L304): Operation `from_workspace`: Operation 'from_workspace' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/nodes.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\practices\stories\model\markdown\nodes.py#L424): Operation `_read_file`: Operation '_read_file' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/brand.py](C:\dev\abd-cdd-version-1-refactoring\harness\catalog_generator\brand.py#L53): Operation `apply`: Operation 'apply' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/brand.py](C:\dev\abd-cdd-version-1-refactoring\harness\catalog_generator\brand.py#L70): Operation `copy_commons`: Operation 'copy_commons' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/generate_cdd_catalog.py](C:\dev\abd-cdd-version-1-refactoring\harness\catalog_generator\generate_cdd_catalog.py#L31): Operation `main`: Operation 'main' mixes I/O-style calls with domain calculation; split responsibilities.

Evaluate the current context against this rule (keep-operations-single-responsibility):

### `simplify-control-flow`

Handle the failing or empty cases first and return. Keep the main path flat. Do not nest more than three levels — deeper than that you cannot tell which conditions hold on a given line without reading back up, and that is where the unhandled branch hides.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\tier_facts.py#L194): Operation `_brace_end`: Operation '_brace_end' nests control flow 4 levels deep (max 3).

Evaluate the current context against this rule (simplify-control-flow):

### `errors-out-of-existence`

For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure. A missing required argument is a broken call, not an ordinary edge: refuse it with a failure the program declares and names (`CommitPathsRequiredError`), which `domain-exception-carries-context` then asks to carry the rejected value.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/agent_bdd/agent_cli_bdd.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\practices\agent_bdd\agent_cli_bdd.py#L290): Operation `_assert_authenticated`: Operation '_assert_authenticated' raises on an empty or missing value; return a quiet result instead.

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

**Graph violations:** 11

- [X] **ERROR** **[graph rule]** - [cdd_guidance/catalog/examples/ddd/tactics.ts](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\catalog\examples\ddd\tactics.ts#L479): Operation `authenticateAccount`: Operation 'authenticateAccount' nearly duplicates 'register' (cdd_guidance/catalog/examples/ddd/tactics.ts): 70% of their code is the same. Give the shared logic one function.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/graph_overlay.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\graph_overlay.py#L58): Operation `__init__`: Operation '__init__' duplicates the body of '__init__'.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L73): Operation `check`: Operation 'check' nearly duplicates 'check' (cdd_guidance/patterns/lern_domain_driven/practices/ddd/rules/lern_tier_rules.py): 82% of their code is the same. Give the shared logic one function.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\tier_facts.py#L75): Operation `__init__`: Operation '__init__' duplicates the body of '__init__'.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\tier_facts.py#L136): Operation `web_path_literals`: Operation 'web_path_literals' nearly duplicates 'web_path_literals' (cdd_guidance/patterns/lern_domain_driven/tier_facts.py): 78% of their code is the same. Give the shared logic one function.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\tier_facts.py#L205): Operation `_in_import`: Operation '_in_import' nearly duplicates '_in_import' (cdd_guidance/patterns/lern_domain_driven/tier_facts.py): 77% of their code is the same. Give the shared logic one function.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\tier_facts.py#L211): Operation `_in_comment`: Operation '_in_comment' nearly duplicates '_in_comment' (cdd_guidance/patterns/lern_domain_driven/tier_facts.py): 79% of their code is the same. Give the shared logic one function.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\tier_facts.py#L267): Operation `__init__`: Operation '__init__' duplicates the body of '__init__'.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\tier_facts.py#L283): Operation `__init__`: Operation '__init__' duplicates the body of '__init__'.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/ddd.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\practices\ddd\ddd.py#L79): Operation `__init__`: Operation '__init__' duplicates the body of '__init__'.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/ux.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\practices\ux\ux.py#L60): Operation `__init__`: Operation '__init__' duplicates the body of '__init__'.

Evaluate the current context against this rule (eliminate-duplication):

### `no-legacy-api-after-refactor`

When you rename or reshape a public seam, update every caller — tests, dependencies, and adjacent modules — to the new API. Do not keep compatibility aliases, re-exports, or thin wrappers that preserve the old name.

Evaluate the current context against this rule (no-legacy-api-after-refactor):

### `use-exceptions-properly`

Raise a domain exception that names the failure (`CartAlreadyCheckedOut`, not `Error` or a bare string). Catch the specific type you can handle. Do not use a bare `except`, and do not catch `Exception` (or `BaseException`) to return a default or substitute a fallback value: that turns every failure, including a bug, into the ordinary answer. A generic exception cannot be caught selectively, so the caller has to handle everything or nothing.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-version-1-refactoring\harness\mcp\mcp_server.py#L607): Operation `_answer_chat`: Operation '_answer_chat' catches every exception (a bare except, or except Exception that never re-raises).
- [X] **ERROR** **[graph rule]** - [harness/mcp/tool_calls.py](C:\dev\abd-cdd-version-1-refactoring\harness\mcp\tool_calls.py#L152): Operation `_start`: Operation '_start' catches every exception (a bare except, or except Exception that never re-raises).

Evaluate the current context against this rule (use-exceptions-properly):

### `never-swallow-exceptions`

Do not catch and ignore. Log and re-raise, or convert to a domain exception that still names the failure. An `except Exception` that returns, `pass`es, or substitutes a fallback (an empty dict, `None`, the input unchanged) is swallowing too: the caller reads the fallback as a real answer, so a broken invariant reaches the next step unseen.

**Graph violations:** 8

- [X] **ERROR** **[graph rule]** - [harness/chat-ui/pane/hooks/chat-bar/chat-bar-client.ts](C:\dev\abd-cdd-version-1-refactoring\harness\chat-ui\pane\hooks\chat-bar\chat-bar-client.ts#L344): Operation `restartServer`: Operation 'restartServer' swallows a caught failure or hands back a fallback in its place.
- [X] **ERROR** **[graph rule]** - [harness/chat-ui/pane/hooks/chat-bar/session-client.ts](C:\dev\abd-cdd-version-1-refactoring\harness\chat-ui\pane\hooks\chat-bar\session-client.ts#L36): Operation `activatedTicket`: Operation 'activatedTicket' swallows a caught failure or hands back a fallback in its place.
- [X] **ERROR** **[graph rule]** - [harness/chat-ui/pane/hooks/health/cdd-version-client.ts](C:\dev\abd-cdd-version-1-refactoring\harness\chat-ui\pane\hooks\health\cdd-version-client.ts#L102): Operation `askVersion`: Operation 'askVersion' swallows a caught failure or hands back a fallback in its place.
- [X] **ERROR** **[graph rule]** - [harness/chat-ui/pane/hooks/health/cdd-version-client.ts](C:\dev\abd-cdd-version-1-refactoring\harness\chat-ui\pane\hooks\health\cdd-version-client.ts#L135): Operation `versionFrom`: Operation 'versionFrom' swallows a caught failure or hands back a fallback in its place.
- [X] **ERROR** **[graph rule]** - [harness/chat-ui/pane/hooks/health/server-health-client.ts](C:\dev\abd-cdd-version-1-refactoring\harness\chat-ui\pane\hooks\health\server-health-client.ts#L138): Operation `reportFrom`: Operation 'reportFrom' swallows a caught failure or hands back a fallback in its place.
- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-version-1-refactoring\harness\mcp\mcp_server.py#L607): Operation `_answer_chat`: Operation '_answer_chat' swallows a caught failure or hands back a fallback in its place.
- [X] **ERROR** **[graph rule]** - [harness/mcp/tool_calls.py](C:\dev\abd-cdd-version-1-refactoring\harness\mcp\tool_calls.py#L152): Operation `_start`: Operation '_start' swallows a caught failure or hands back a fallback in its place.
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/ide_toast/watch_notice.js](C:\dev\abd-cdd-version-1-refactoring\tools\prompt_notify\ide_toast\watch_notice.js#L12): Operation `messageFromNotice`: Operation 'messageFromNotice' swallows a caught failure or hands back a fallback in its place.

Evaluate the current context against this rule (never-swallow-exceptions):

### `limit-comments`

write comment in operations and properties only when the signature cannot say a constraint or explain why the code behaves the way it does. Do not narrate a line that already names what it does.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/installation/language_adapter.py](C:\dev\abd-cdd-version-1-refactoring\harness\installation\language_adapter.py#L522): Operation `_base_state_changes`: Operation '_base_state_changes' has a descriptive comment.

Evaluate the current context against this rule (limit-comments):

### `source-parses`

Keep every source file valid in its language. A file that does not parse is read into no classes, so every other rule passes it without looking, and its problems stay hidden until it runs.

Evaluate the current context against this rule (source-parses):

### `operation-has-a-proving-test`

Every public operation is invoked by at least one observation or step.

Evaluate the current context against this rule (operation-has-a-proving-test):

### `class-demonstrated-by-a-test`

Every public class is demonstrated through an example or observation.

Evaluate the current context against this rule (class-demonstrated-by-a-test):

### `invariant-has-a-failing-case`

Every invariant has a test that tries to break it and sees the named failure.

Evaluate the current context against this rule (invariant-has-a-failing-case):

### `every-branch-taken-by-a-test`

Every branch in a public operation's body is taken by some test.

Evaluate the current context against this rule (every-branch-taken-by-a-test):

### `conforms-to-schema`

Content conforms to its schema: every node has each relationship its schema type requires, up to the fidelity being worked. It checks only what the schema requires (a field written `name?:` is optional) and only for the fidelities worked so far: a relationship whose target a later fidelity creates is not required yet. Validate keeps only the findings inside the work's scope: the session's stories and everything under them, and the files the call names. It runs only on a graph that holds the session's whole working copy across its practices, so links across practices are judged; on a load of named files alone the AI judge weighs them.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/claude_design](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\practices\stories\model\claude_design#L1): Package `claude_design`: Package 'claude_design' has no participants relationship to OoadClass | Class | Package | Module, which the clean_engineering practice schema requires.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/javascript/seeds](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\practices\stories\model\javascript\seeds#L1): Package `seeds`: Package 'seeds' has no participants relationship to OoadClass | Class | Package | Module, which the clean_engineering practice schema requires.

Evaluate the current context against this rule (conforms-to-schema):

### `deep-module`

Keep most classes private (at most **40%** public) in each first-class module. A first-class module is a folder that owns `.context/module-context.md`. Nested folders that also own that file are separate modules — respect them. Nested folders that do not own it roll up to the nearest enclosing module-context folder, or to the folder you are querying if none sits in between. Count classes, not operations: a public method on a hidden class is not a second seam. A class is public when another module's production code names it; a class named only inside its own module, or only by specs, is private. Modules with fewer than 3 classes are not measured, because one public class out of two is the whole seam, not a shallow module. Every public class is a signature you cannot change without editing every caller, so public classes are much harder to refactor than private ones.

**Graph violations:** 6

- [X] **ERROR** **[graph rule]** - [harness/annotations](C:\dev\abd-cdd-version-1-refactoring\harness\annotations#L1): Module `annotations`: Module 'annotations' exposes 8 of 9 classes to other modules, more than the 3 that 40% allows: Annotation, Destination, HostedOnly, Name, NamedDestination, NamesAnnotation, OmissionAnnotation, Toast. Keep most classes behind a few public ones.
- [X] **ERROR** **[graph rule]** - [harness/design_canvas](C:\dev\abd-cdd-version-1-refactoring\harness\design_canvas#L1): Module `design_canvas`: Module 'design_canvas' exposes 5 of 10 classes to other modules, more than the 4 that 40% allows: Artboard, CanvasBoard, CanvasVersions, DesignCanvas, Place. Keep most classes behind a few public ones.
- [X] **ERROR** **[graph rule]** - [harness/guidance](C:\dev\abd-cdd-version-1-refactoring\harness\guidance#L1): Module `guidance`: Module 'guidance' exposes 20 of 39 classes to other modules, more than the 15 that 40% allows: Action, ActionCatalogue, ApproachStage, DeclaredFile, FidelityGuidance, Guidance, GuidanceCollection, PracticeCatalogue, PracticeFormats, PracticeGuidance, PracticeReading, PracticeSupplement, RenderRequest, Rule, RulesCollection, Schema, SessionFiles, SketchLens, StageScope, UnknownPractice. Keep most classes behind a few public ones.
- [X] **ERROR** **[graph rule]** - [harness/markdown](C:\dev\abd-cdd-version-1-refactoring\harness\markdown#L1): Module `markdown`: Module 'markdown' exposes 7 of 17 classes to other modules, more than the 6 that 40% allows: Format, FrontMatter, Markdown, MarkdownCollection, MarkdownScope, MarkdownText, OperationProperty. Keep most classes behind a few public ones.
- [X] **ERROR** **[graph rule]** - [harness/process](C:\dev\abd-cdd-version-1-refactoring\harness\process#L1): Module `process`: Module 'process' exposes 11 of 13 classes to other modules, more than the 5 that 40% allows: BackgroundStart, ClaudeChatProcess, ExclusivePort, Git, GitHubCli, ListeningPorts, ProcessNotStopped, PythonInterpreter, RepoConnectError, RunningProcess, StoppableProcess. Keep most classes behind a few public ones.
- [X] **ERROR** **[graph rule]** - [harness/whiteboard](C:\dev\abd-cdd-version-1-refactoring\harness\whiteboard#L1): Module `whiteboard`: Module 'whiteboard' exposes 9 of 12 classes to other modules, more than the 4 that 40% allows: Arrow, BoardElement, Box, Label, Section, Shape, UnreadableBoard, Whiteboard, WhiteboardNode. Keep most classes behind a few public ones.

Evaluate the current context against this rule (deep-module):

### `extensions-live-with-the-domain`

Domain extensions of a framework belong in the domain module — a nested package under that domain is fine. Do not host them in the base framework package. `GraphEpic` lives with Stories, not in Knowledge Graph; otherwise the framework depends on every practice and cannot stay generic.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/graph/graph_rules_collection.py](C:\dev\abd-cdd-version-1-refactoring\harness\graph\graph_rules_collection.py#L18): OoadClass `GraphRule`: Class 'GraphRule' extends Rule from 'harness/guidance' with this package's PracticeGraphRule: it is an extension of 'harness/guidance' and belongs there, so this package does not depend on it.

Evaluate the current context against this rule (extensions-live-with-the-domain):

### `keep-classes-single-responsibility`

Give each class one reason to change.

**Graph violations:** 22

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/base_class_model.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\practices\clean_engineering\model\base_class_model.py#L119): OoadClass `OoadClass`: Class 'OoadClass' exposes 13 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/base_class_model.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\practices\clean_engineering\model\base_class_model.py#L344): OoadClass `Module`: Class 'Module' exposes 12 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/code_class_model.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\practices\clean_engineering\model\code_class_model.py#L104): OoadClass `CodeClass`: Class 'CodeClass' exposes 13 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/operation.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\practices\clean_engineering\model\operation.py#L88): OoadClass `Operation`: Class 'Operation' exposes 14 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/operation_metrics.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\practices\clean_engineering\model\operation_metrics.py#L169): OoadClass `SourceText`: Class 'SourceText' exposes 18 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/operation_metrics.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\practices\clean_engineering\model\operation_metrics.py#L442): OoadClass `PythonFunctionBody`: Class 'PythonFunctionBody' exposes 10 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/property.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\practices\clean_engineering\model\property.py#L60): OoadClass `Property`: Class 'Property' exposes 11 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/chat/chat.py](C:\dev\abd-cdd-version-1-refactoring\harness\chat\chat.py#L203): OoadClass `Chat`: Class 'Chat' exposes 11 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\dev\abd-cdd-version-1-refactoring\harness\graph\graph.py#L859): OoadClass `PracticeNodes`: Class 'PracticeNodes' exposes 18 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\dev\abd-cdd-version-1-refactoring\harness\graph\graph.py#L1290): OoadClass `Graph`: Class 'Graph' exposes 22 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\dev\abd-cdd-version-1-refactoring\harness\guidance\guidance.py#L240): OoadClass `PracticeGuidance`: Class 'PracticeGuidance' exposes 11 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-version-1-refactoring\harness\guidance_actions\guidance_actions.py#L480): OoadClass `GuidanceAction`: Class 'GuidanceAction' exposes 10 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/files-panel-client.ts](C:\dev\abd-cdd-version-1-refactoring\space\kanban\app\src\kanban\ticket\files-panel-client.ts#L44): OoadClass `FilesPanelClient`: Class 'FilesPanelClient' exposes 11 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-client.tsx](C:\dev\abd-cdd-version-1-refactoring\space\kanban\app\src\kanban\ticket\ticket-client.tsx#L19): OoadClass `TicketClient`: Class 'TicketClient' exposes 15 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/kanban/backlog_item.py](C:\dev\abd-cdd-version-1-refactoring\space\kanban\backlog_item.py#L46): OoadClass `BacklogItem`: Class 'BacklogItem' exposes 14 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/kanban/board.py](C:\dev\abd-cdd-version-1-refactoring\space\kanban\board.py#L104): OoadClass `Board`: Class 'Board' exposes 15 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/kanban/ticket.py](C:\dev\abd-cdd-version-1-refactoring\space\kanban\ticket.py#L109): OoadClass `Ticket`: Class 'Ticket' exposes 28 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/repo/mock_repo.py](C:\dev\abd-cdd-version-1-refactoring\space\repo\mock_repo.py#L69): OoadClass `MockGit`: Class 'MockGit' exposes 14 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\dev\abd-cdd-version-1-refactoring\space\repo\repo.py#L77): OoadClass `Repo`: Class 'Repo' exposes 14 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/session/practice_session_output.py](C:\dev\abd-cdd-version-1-refactoring\space\session\practice_session_output.py#L255): OoadClass `FidelitySessionOutput`: Class 'FidelitySessionOutput' exposes 10 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\dev\abd-cdd-version-1-refactoring\space\session\session.py#L82): OoadClass `Session`: Class 'Session' exposes 32 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/session/sessions.py](C:\dev\abd-cdd-version-1-refactoring\space\session\sessions.py#L111): OoadClass `Sessions`: Class 'Sessions' exposes 16 public operations (budget ~9). Split responsibilities.

Evaluate the current context against this rule (keep-classes-single-responsibility):

### `limit-operation-parameters`

Have callers pass intent, not setup. A parameter that carries state the object already holds fails `hold-state-on-the-object-not-in-parameters` even when the count is small. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. Count each value a caller supplies: a packed tuple, `*args`, or `**kwargs` that carries four values counts as four parameters, because packing them hides the same setup instead of removing it. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object. An operation published as an MCP tool (`@mcp` or `@agent_tool` in Python) is exempt too, because its parameters are the tool's published argument schema, which its callers fill by name.

**Graph violations:** 9

- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/graph_overlay.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\graph_overlay.py#L136): Operation `_tier_facts`: Operation '_tier_facts' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/graph_overlay.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\graph_overlay.py#L191): Operation `_file_node`: Operation '_file_node' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/app/story-map/story-map-views.tsx](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\practices\stories\app\story-map\story-map-views.tsx#L32): Operation `useStoryMapReading`: Operation 'useStoryMapReading' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\dev\abd-cdd-version-1-refactoring\harness\graph\graph.py#L527): Operation `__init__`: Operation '__init__' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\dev\abd-cdd-version-1-refactoring\harness\graph\graph.py#L990): Operation `add_named`: Operation 'add_named' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/guidance/stages.py](C:\dev\abd-cdd-version-1-refactoring\harness\guidance\stages.py#L26): Operation `__init__`: Operation '__init__' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/installation/files.py](C:\dev\abd-cdd-version-1-refactoring\harness\installation\files.py#L100): Operation `__init__`: Operation '__init__' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/session-board/http-exception.ts](C:\dev\abd-cdd-version-1-refactoring\space\kanban\app\src\session-board\http-exception.ts#L31): Operation `answerFailure`: Operation 'answerFailure' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [space/repo/mock_repo.py](C:\dev\abd-cdd-version-1-refactoring\space\repo\mock_repo.py#L154): Operation `commit`: Operation 'commit' takes 4 parameters (maximum 3, excluding self).

Evaluate the current context against this rule (limit-operation-parameters):

### `no-module-per-class`

A module groups multiple cohesive classes. One folder or package per class is an anti-pattern unless each class is a genuinely independent subsystem. When sketching with DDD, a small bounded context is usually **one module** with several entities inside — not one module per aggregate root.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [scripts/unit_guard](C:\dev\abd-cdd-version-1-refactoring\scripts\unit_guard#L1): Module `unit_guard`: Module 'unit_guard' exposes a single class in one file; group cohesive classes or merge into an existing module.

Evaluate the current context against this rule (no-module-per-class):

### `shape-classes-around-resources`

Model a class around the concept that owns the state and the rule, not a doer, handler, or service that acts on a data bag. A Payment has transactions, a source, and a destination, and it moves the money; it is not a `PaymentService` that takes a `PaymentData` object. A service-plus-bag pair splits the rule from its memory, so every change has to be found in two types and the bag cannot enforce anything. Two resources may collaborate — a model that loads a Module is not a service-plus-bag split.

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/open-card-client.ts](C:\dev\abd-cdd-version-1-refactoring\space\kanban\app\src\kanban\ticket\open-card-client.ts#L12): OoadClass `OpenCardClient`: Class 'OpenCardClient' acts on the data bag 'RequiredFidelity', which holds the state but no behavior; put the behavior on the resource that owns the data.
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/report-client.ts](C:\dev\abd-cdd-version-1-refactoring\space\kanban\app\src\kanban\ticket\report-client.ts#L45): OoadClass `ReportClient`: Class 'ReportClient' acts on the data bag 'ViolationData', which holds the state but no behavior; put the behavior on the resource that owns the data.
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-work.ts](C:\dev\abd-cdd-version-1-refactoring\space\kanban\app\src\kanban\ticket\ticket-work.ts#L21): OoadClass `TicketWork`: Class 'TicketWork' acts on the data bag 'RequiredFidelity', which holds the state but no behavior; put the behavior on the resource that owns the data.

Evaluate the current context against this rule (shape-classes-around-resources):

### `state-change-returns-record-or-named-failure`

When an operation coordinates a state change that cannot be one property assignment, return the resulting record or a failure named after the rejected rule. Decide at code fidelity whether that failure is a result type or domain exception, because callers need one explicit outcome contract.

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [cdd_guidance/catalog/commons/catalog-approach.js](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\catalog\commons\catalog-approach.js#L79): Operation `ApproachPage`: Operation 'ApproachPage' mutates state but does not return the record or a named failure.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/catalog/commons/catalog-drawio.js](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\catalog\commons\catalog-drawio.js#L87): Operation `StoryMapZoom`: Operation 'StoryMapZoom' mutates state but does not return the record or a named failure.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/catalog/commons/catalog-foundry-tour.js](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\catalog\commons\catalog-foundry-tour.js#L196): Operation `FloatingTooltips`: Operation 'FloatingTooltips' mutates state but does not return the record or a named failure.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/catalog/commons/catalog-nav.js](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\catalog\commons\catalog-nav.js#L255): Operation `NavDrawer`: Operation 'NavDrawer' mutates state but does not return the record or a named failure.

Evaluate the current context against this rule (state-change-returns-record-or-named-failure):

### `use-explicit-dependencies`

Pass every collaborator through the constructor. Do not reach for a global or construct a collaborator inside construction. A collaborator the class fetches or builds itself cannot be swapped, so the class can only ever run against that one implementation. A part the class builds once from nothing outside itself and keeps, such as an index of its own nodes, is not a collaborator: nothing a caller could hand it differs from it. A repository, service, client, file, or other external system is, and always comes in through the constructor.

**Graph violations:** 11

- [X] **ERROR** **[graph rule]** - [cdd_guidance/context_setup/context_index.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\context_setup\context_index.py#L131): OoadClass `OpenAIEmbeddingProvider`: Class 'OpenAIEmbeddingProvider' constructs 'OpenAI' inside its constructor.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/agent_bdd/agent_cli_bdd.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\practices\agent_bdd\agent_cli_bdd.py#L273): OoadClass `CliAgentBlock`: Class 'CliAgentBlock' constructs 'CursorCli' inside its constructor.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/app/story-map/story-map-failures.ts](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\practices\stories\app\story-map\story-map-failures.ts#L7): OoadClass `StoryMapFailures`: Class 'StoryMapFailures' constructs 'StoryMapApi' inside its constructor.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/story-demo/mount-generated-mockup.js](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\practices\ux\story-demo\mount-generated-mockup.js#L527): OoadClass `GeneratedMockup`: Class 'GeneratedMockup' constructs 'WeakSet' inside its constructor.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/story-demo/story-demo-page.js](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\practices\ux\story-demo\story-demo-page.js#L14): OoadClass `StoryDemoPage`: Class 'StoryDemoPage' constructs 'PlayDualRunner' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_practice.py](C:\dev\abd-cdd-version-1-refactoring\harness\catalog_generator\catalog_practice.py#L33): OoadClass `CatalogSkills`: Class 'CatalogSkills' constructs 'IdeLayout' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/project_approach.py](C:\dev\abd-cdd-version-1-refactoring\harness\catalog_generator\project_approach.py#L56): OoadClass `ProjectFiles`: Class 'ProjectFiles' constructs 'JsonFile' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/installation/installer.py](C:\dev\abd-cdd-version-1-refactoring\harness\installation\installer.py#L326): OoadClass `Installer`: Class 'Installer' constructs 'InstallRecord' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-version-1-refactoring\harness\mcp\mcp_server.py#L225): OoadClass `McpInstallation`: Class 'McpInstallation' constructs 'ServedCheckout' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/mcp/server_hooks.py](C:\dev\abd-cdd-version-1-refactoring\harness\mcp\server_hooks.py#L18): OoadClass `CddServerHooks`: Class 'CddServerHooks' constructs 'ServedCheckout' inside its constructor.
- [X] **ERROR** **[graph rule]** - [space/repo/repos.py](C:\dev\abd-cdd-version-1-refactoring\space\repo\repos.py#L116): OoadClass `CddConfig`: Class 'CddConfig' constructs 'JsonFile' inside its constructor.

Evaluate the current context against this rule (use-explicit-dependencies):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 53

- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/graph_overlay.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\graph_overlay.py#L187): Parameter `facts`: Parameter 'facts' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/graph_overlay.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\graph_overlay.py#L191): Parameter `practice`: Parameter 'practice' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L16): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L27): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L27): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L37): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L37): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L47): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L47): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L58): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L58): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L73): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L73): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L86): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L86): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L96): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L96): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L106): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L106): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L116): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L116): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L126): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L126): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L136): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L136): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L146): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L146): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L158): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L158): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L174): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L174): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L191): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L191): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/stories/rules/oss_story_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\stories\rules\oss_story_rules.py#L16): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/stories/rules/oss_story_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\stories\rules\oss_story_rules.py#L16): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/stories/rules/oss_story_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\stories\rules\oss_story_rules.py#L30): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/stories/rules/oss_story_rules.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\patterns\oss_portal_domain_driven\practices\stories\rules\oss_story_rules.py#L30): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/graph_reading.py](C:\dev\abd-cdd-version-1-refactoring\cdd_guidance\practices\ddd\model\graph_reading.py#L122): Parameter `default`: Parameter 'default' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/diagnostics/probe_outcome.py](C:\dev\abd-cdd-version-1-refactoring\harness\diagnostics\probe_outcome.py#L35): Parameter `answer`: Parameter 'answer' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_reading.py](C:\dev\abd-cdd-version-1-refactoring\harness\guidance\practice_reading.py#L72): Parameter `graph`: Parameter 'graph' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_reading.py](C:\dev\abd-cdd-version-1-refactoring\harness\guidance\practice_reading.py#L72): Parameter `nodes`: Parameter 'nodes' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/installation/data_class.py](C:\dev\abd-cdd-version-1-refactoring\harness\installation\data_class.py#L177): Parameter `instance`: Parameter 'instance' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/installation/data_class.py](C:\dev\abd-cdd-version-1-refactoring\harness\installation\data_class.py#L185): Parameter `instance`: Parameter 'instance' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/installation/data_class.py](C:\dev\abd-cdd-version-1-refactoring\harness\installation\data_class.py#L194): Parameter `held`: Parameter 'held' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/installation/data_class.py](C:\dev\abd-cdd-version-1-refactoring\harness\installation\data_class.py#L200): Parameter `held`: Parameter 'held' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/installation/data_class.py](C:\dev\abd-cdd-version-1-refactoring\harness\installation\data_class.py#L212): Parameter `subject`: Parameter 'subject' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-version-1-refactoring\harness\mcp\mcp_server.py#L792): Parameter `answer`: Parameter 'answer' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/mcp/tool_calls.py](C:\dev\abd-cdd-version-1-refactoring\harness\mcp\tool_calls.py#L93): Parameter `answer`: Parameter 'answer' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/board/side-panel-client.ts](C:\dev\abd-cdd-version-1-refactoring\space\kanban\app\src\kanban\board\side-panel-client.ts#L31): Parameter `panel`: Parameter 'panel' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/files-panel-client.ts](C:\dev\abd-cdd-version-1-refactoring\space\kanban\app\src\kanban\ticket\files-panel-client.ts#L58): Parameter `panel`: Parameter 'panel' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/files-panel-client.ts](C:\dev\abd-cdd-version-1-refactoring\space\kanban\app\src\kanban\ticket\files-panel-client.ts#L63): Parameter `source`: Parameter 'source' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/tile-client.ts](C:\dev\abd-cdd-version-1-refactoring\space\kanban\app\src\kanban\ticket\tile-client.ts#L61): Parameter `tile`: Parameter 'tile' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [tools/prompt_log/prompt_log.py](C:\dev\abd-cdd-version-1-refactoring\tools\prompt_log\prompt_log.py#L133): Parameter `text`: Parameter 'text' needs a domain-specific type, not a generic container.

Evaluate the current context against this rule (use-typed-signatures):

---

Judgment by five parallel judges (2026-11-16), each graph hit confirmed or judged noise, with a cross-file pass (parallel models, duplication, vocabulary, state handed down, hidden storage, legacy API, dependency direction) that searched beyond the flagged files. The four test-coverage rules (operation-has-a-proving-test, class-demonstrated-by-a-test, invariant-has-a-failing-case, every-branch-taken-by-a-test) need a coverage run and were not judged.

## Judgment — `cdd_guidance/patterns/lern_domain_driven/graph_overlay.py`

### `do-not-invent-parallel-object-models` — Fail
- graph_overlay.py:48 `_LernReading`: OSS's `_OssReading` is a second copy of this reading (overlay, graph, root, link, file-node creation, aggregate-folder discovery) instead of one shared pattern reading that both overlays extend.

## Judgment — `cdd_guidance/patterns/lern_domain_driven/tier_facts.py`

### `do-not-invent-parallel-object-models` — Fail
- tier_facts.py:48 `TierFile`: OSS's `OssFile` repeats this class (text, relative, `_source`, `at`, `web_path_literals`, `_in_import`, `_in_comment`) for the same concept, a TypeScript tier file of a pattern the OSS pattern says it carries from LERN; there should be one tier-file model.

## Judgment — `cdd_guidance/patterns/oss_portal_domain_driven/graph_overlay.py`

### `limit-operation-parameters` — Fail
- graph_overlay.py:136 `_tier_facts`: takes 5 values; `slug` and `service_name` are derived from `folder`, so callers pass setup, not intent (LERN holds these on `_AggregateTiers`).
- graph_overlay.py:191 `_file_node`: takes 4 values (practice, relative, semantic, name); LERN's `_PracticeFiles(practice).node(relative, semantic, name)` shows the practice belongs on an object.

### `eliminate-duplication` — Fail
- graph_overlay.py:58 `__init__`: `_OssReading.__init__` is the same body as `_LernReading.__init__`; the whole reading class (and `_file_node` vs `_PracticeFiles.node`, `_link` vs `link`, `_aggregate_folders` vs `_tier_folders`) is copied from LERN.
- graph_overlay.py:187 `_set_facts`: the same "for key, value in facts: node.set_fact" loop also appears in cdd_guidance/patterns/lern_domain_driven/graph_overlay.py:89, :114, :221 and cdd_guidance/patterns/cdd_web_domain_access/graph_overlay.py:30; `Node` (harness/graph/graph.py:540) owns facts and only offers `set_fact`, so each overlay copies the loop.
- graph_overlay.py:191 `_file_node`: makes the practice's whole-file node exactly as LERN's `_PracticeFiles.node` (cdd_guidance/patterns/lern_domain_driven/graph_overlay.py:152) and cdd_guidance/patterns/cdd_web_domain_access/graph_overlay.py:29 do; three copies of one lookup-or-add.

### `hold-state-on-the-object-not-in-parameters` — Fail
- graph_overlay.py:191 `_file_node`: every caller (lines 92, 96, 102, 123, 166, 182) passes `self.ddd` or `self.stories` as `practice`, state the reading already holds on itself.

### `hide-inner-details` — Fail
- graph_overlay.py:198 `_file_node`: reads `practice.reading.graph` and `practice.reading.in_graph.source_root` and calls `in_graph.add_named` directly, so the practice reading's storage (harness/graph/graph.py:990 `add_named`, :114 `Source.whole_file`) is a contract for each pattern; LERN (cdd_guidance/patterns/lern_domain_driven/graph_overlay.py:154-159) reaches in the same way.

### `use-consistent-naming` — Fail
- graph_overlay.py:63 `_link`: the same operation is `link` in LERN's `_LernReading` (cdd_guidance/patterns/lern_domain_driven/graph_overlay.py:56); one verb, two names and visibilities.

## Judgment — `cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py`

### `use-typed-signatures` — Fail
- oss_tier_rules.py:16 `_hits`: `node` is untyped; it is a graph `Node`.
- oss_tier_rules.py:27 `BrowserCallsOnlyTheBff.check`: `node` and `context` untyped; the base `PracticeGraphRule.check` and every LERN rule type them `Node` / `RuleCheckContext`.
- oss_tier_rules.py:37 `TokensStayOnTheServer.check`: `node` and `context` untyped.
- oss_tier_rules.py:47 `ViewsRenderOnly.check`: `node` and `context` untyped.
- oss_tier_rules.py:58 `MaintainLayerPurity.check`: `node` and `context` untyped.
- oss_tier_rules.py:73 `BffDecidesNextPage.check`: `node` and `context` untyped.
- oss_tier_rules.py:86 `RepositoryOwnsAggregateLifecycle.check`: `node` and `context` untyped.
- oss_tier_rules.py:96 `NoCrossServiceTables.check`: `node` and `context` untyped.
- oss_tier_rules.py:106 `SanitisedErrorsOnly.check`: `node` and `context` untyped.
- oss_tier_rules.py:116 `PublishEventsFromTheOwningService.check`: `node` and `context` untyped.
- oss_tier_rules.py:126 `SecretsFromSecretManager.check`: `node` and `context` untyped.
- oss_tier_rules.py:136 `NoPersonalDataInLogs.check`: `node` and `context` untyped.
- oss_tier_rules.py:146 `OneProxyPerService.check`: `node` and `context` untyped.
- oss_tier_rules.py:158 `VersionBreakingChanges.check`: `node` and `context` untyped.
- oss_tier_rules.py:174 `StandardPolicyChain.check`: `node` and `context` untyped.
- oss_tier_rules.py:191 `ExpandAndContractMigrations.check`: `node` and `context` untyped.

### `eliminate-duplication` — Fail
- oss_tier_rules.py:73 `BffDecidesNextPage.check`: same comprehension over `web_path_literals` as LERN `OneHomeForWebPaths.check`; the pattern says the rule is carried from LERN, so it should reuse LERN's rule as the OSS story rules do.

## Judgment — `cdd_guidance/patterns/oss_portal_domain_driven/practices/stories/rules/oss_story_rules.py`

### `use-typed-signatures` — Fail
- oss_story_rules.py:16 `ServiceTierRunsARealDatabase.check`: `node` and `context` untyped, unlike the base `PracticeGraphRule.check`.
- oss_story_rules.py:30 `JourneyTestPerRelease.check`: `node` and `context` untyped.

## Judgment — `cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py`

### `eliminate-duplication` — Fail
- tier_facts.py:75 `OssFile.__init__`: same body as `TierFile.__init__`; `OssFile` is a copy of LERN's `TierFile`, which this module already uses for story files.
- tier_facts.py:136 `OssFile.web_path_literals`: 78% the same as `TierFile.web_path_literals`; only the regex differs.
- tier_facts.py:205 `OssFile._in_import`: the same logic as `TierFile._in_import`.
- tier_facts.py:211 `OssFile._in_comment`: the same logic as `TierFile._in_comment`.
- tier_facts.py:283 `AggregateFolder.__init__`: same body as LERN's `AggregateFolder.__init__`; the class is a copy of LERN's `AggregateFolder` under the same name.
- tier_facts.py:194 `OssFile._brace_end`: brace matching that LERN's `TierFile._braced_body` (cdd_guidance/patterns/lern_domain_driven/tier_facts.py:200) and `_BraceScanner.matching_brace` (harness/catalog_generator/source_folds.py:163) already do; three brace scanners, only the last steps over strings and comments.

### `do-not-invent-parallel-object-models` — Fail
- tier_facts.py:280 `AggregateFolder`: a second class of the same name and role as LERN's `AggregateFolder` (cdd_guidance/patterns/lern_domain_driven/tier_facts.py:236), so the OSS overlay must import two `AggregateFolder`-shaped models from two modules.

## Judgment — `cdd_guidance/patterns/cdd_web_domain_access/graph_overlay.py`

### `eliminate-duplication` — Fail
- graph_overlay.py:29 `WebDomainAccessOverlay.read`: inline whole-file node creation and the fact loop at line 30 repeat LERN's `_PracticeFiles.node` (cdd_guidance/patterns/lern_domain_driven/graph_overlay.py:152) and OSS's `_file_node` / `_set_facts` (cdd_guidance/patterns/oss_portal_domain_driven/graph_overlay.py:191, :187).

### `hide-inner-details` — Fail
- graph_overlay.py:29 `WebDomainAccessOverlay.read`: calls `ddd.reading.in_graph.add_named` on the DDD practice's reading storage directly instead of a named operation on the practice or graph (harness/graph/graph.py:990).

## Judgment — `harness/annotations/annotation.py`

### `prefer-instance-operations` — Fail
- annotation.py:111 `Annotation.annotates`: a classmethod query on a kind of annotation, no factory; the registry could hold kind instances and ask them.
- annotation.py:116 `Annotation.written_as`: classmethod returning the kind's typed name; not a creation or mapping factory.
- annotation.py:122 `Annotation.installs_member`: classmethod policy query; belongs on an instance of the kind.
- annotation.py:127 `Annotation.companion_flags`: classmethod policy query; not a factory.
- annotation.py:157 `NamesAnnotation.names_on`: classmethod reader of the recorded names; not a factory.
- annotation.py:171 `OmissionAnnotation.annotates`: classmethod override of the class-level query; not a factory.
- annotation.py:184 `HostedOnly.annotates`: classmethod override of the class-level query; not a factory.
- annotation.py:212 `Destination.installs_member`: classmethod policy query; not a factory.
- annotation.py:217 `Destination.name_annotated_on`: classmethod reader of the name an annotation gave; not a factory.
- annotation.py:223 `Destination.companion_flags`: classmethod policy query; not a factory.
- annotation.py:227 `Destination.disabled_on`: classmethod policy query; not a factory.

### `eliminate-duplication` — Fail
- annotation.py:205 `Destination.annotate`: repeats `setattr(target, self.flag, True)` from `Annotation.annotate` (annotation.py:132) instead of calling `super().annotate(target)`, so a change to how a flag is recorded misses destinations.

## Judgment — `harness/guidance/action_catalogue.py`

### `prefer-instance-operations` — Fail
- action_catalogue.py:121 `ActionCatalogue.register`: classmethod writing class-level ClassVar state, the global-state pattern the rule names; should be an instance the framework holds.
- action_catalogue.py:127 `ActionCatalogue.run_actions_with`: classmethod setting a class-level runner; global state, not a factory.
- action_catalogue.py:132 `ActionCatalogue.runner`: classmethod global accessor handing every caller the same class-level runner, which the rule says is not a factory.
- action_catalogue.py:139 `ActionCatalogue.fidelity_actions`: classmethod query over class-level state.
- action_catalogue.py:145 `ActionCatalogue.toolsets`: classmethod global accessor over class-level state.
- action_catalogue.py:150 `ActionCatalogue.actions`: classmethod that caches into class-level state; not a factory.
- action_catalogue.py:163 `ActionCatalogue.names`: classmethod query over class-level state.
- action_catalogue.py:167 `ActionCatalogue.has`: classmethod query over class-level state.
- action_catalogue.py:171 `ActionCatalogue.action`: classmethod lookup over class-level state; a lookup, not a creation factory.

### `use-explicit-dependencies` — Fail
- action_catalogue.py:61 `Action.run_on`: reaches the process-wide `ActionCatalogue.runner()` global instead of being handed its runner, so an action cannot run against another runner.
- action_catalogue.py:93 `FidelityActions.__init__`: fetches its actions from the `ActionCatalogue.fidelity_actions()` global during construction rather than receiving the catalogue.

## Judgment — `harness/guidance/practice_catalogue.py`

### `prefer-instance-operations` — Fail
- practice_catalogue.py:46 `PracticeCatalogue.register`: classmethod writing class-level ClassVar state; global registry, not a factory.
- practice_catalogue.py:51 `PracticeCatalogue.register_supplements`: classmethod writing class-level state.
- practice_catalogue.py:57 `PracticeCatalogue.supplement_classes`: classmethod global accessor over class-level state.
- practice_catalogue.py:62 `PracticeCatalogue.keys`: classmethod query over class-level state.
- practice_catalogue.py:67 `PracticeCatalogue.has`: classmethod query over class-level state.
- practice_catalogue.py:100 `PracticeCatalogue._always_on_supplements`: classmethod helper reading class-level supplement classes; not itself a named factory.
- practice_catalogue.py:109 `PracticeCatalogue.practice_class`: classmethod lookup over class-level state; not a factory.
- practice_catalogue.py:116 `PracticeCatalogue._registered`: classmethod global accessor over class-level state.

### `eliminate-duplication` — Fail
- practice_catalogue.py:46 `PracticeCatalogue.register`: the same class-level "register classes, keep them in a ClassVar, look them up by name" registry as `ActionCatalogue.register` (harness/guidance/action_catalogue.py:121) and `PatternOverlays.register` (harness/graph/pattern_overlays.py:106); three registries with no shared owner.

### `use-consistent-naming` — Fail
- practice_catalogue.py:62 `PracticeCatalogue.keys`: the identifiers of what a registry holds are `keys` here but `names` on `ActionCatalogue.names` (harness/guidance/action_catalogue.py:163), `ApproachStages.names` (harness/guidance/stages.py:132) and `PatternOverlays.names` (harness/graph/pattern_overlays.py:223); two words for one concept.

## Judgment — `harness/graph/pattern_overlays.py`

### `eliminate-duplication` — Fail
- pattern_overlays.py:106 `PatternOverlays.register`: copies the class-level registry of `ActionCatalogue.register` (harness/guidance/action_catalogue.py:121) and `PracticeCatalogue.register` (harness/guidance/practice_catalogue.py:46).

### `prefer-instance-operations` — Fail
- pattern_overlays.py:106 `PatternOverlays.register`: classmethod writing class-level `_registered`; global setter, not a factory.

## Judgment — `harness/guidance/guidance.py`

### `keep-classes-single-responsibility` — Fail
- guidance.py:240 `PracticeGuidance`: one class reads its document and schema, picks fidelity and format, holds its practice set, binds to a session, renders, and serves instructions; several reasons to change.

## Judgment — `harness/guidance/practice_reading.py`

### `use-typed-signatures` — Fail
- practice_reading.py:72 `graph`: `held_in(graph: Any, ...)` puts `Any` on a public signature; the graph could be named by a Protocol, as action_catalogue does with WorkedFidelity.
- practice_reading.py:72 `nodes`: `held_in(..., nodes: Any)` puts `Any` on a public signature for the practice's PracticeNodes.

## Judgment — `harness/guidance/stages.py`

### `do-not-invent-parallel-object-models` — Fail
- stages.py:67 `ApproachStage._OTHER_ACTIONS`: with `_BEFORE_STEPS` (line 66) and `_STEPS` (line 64), keeps a hand-written string list of action names ("partition", "iterate", "sketch", "document") beside the one list of actions, `ActionCatalogue.actions` (harness/guidance/action_catalogue.py:150); a renamed or added action is missed here.

## Judgment — `harness/catalog_generator/stage_columns.py`

### `do-not-invent-terms` — Fail
- stage_columns.py:50 `_COLUMN_KEYS`: renames the stages `specification` and `implementation` (owner harness/guidance/stages.py:12-13) to "spec" and "engineer", a second vocabulary for the same stages.

## Judgment — `harness/guidance_actions/guidance_actions.py`

### `keep-classes-single-responsibility` — Fail
- guidance_actions.py:480 `GuidanceAction`: one class resolves the call's session, holds the work list, logs to the session, builds overlay/story-scope prose, and builds session-context prose; several reasons to change.

### `hold-state-on-the-object-not-in-parameters` — Fail
- guidance_actions.py:88 `session_file_named`: the session is written into the guidance string as a `session=` word (space/kanban/app/src/kanban/ticket/ticket-chat-prompts.ts:18) and parsed back here, the exact pattern the rule names; `overlays=` and `format=` (guidance_actions.py:96, :184) ride the same string.

## Judgment — `harness/diagnostics/probe_arguments.py`

### `eliminate-duplication` — Fail
- probe_arguments.py:47 `practice_named`: repeats the "find the practice whose `answers_to(slug)` is not none across a practice set" search that `_named` does (harness/guidance_actions/guidance_actions.py:236); the practice set has no owner for the lookup, so each caller writes its own.

## Judgment — `harness/diagnostics/guidance_probe.py`

### `hold-state-on-the-object-not-in-parameters` — Fail
- guidance_probe.py:92 `_instructions_of`: passes the slug again to `practice.answers_to(slug)` to re-find the guidance that `practice_named` (harness/diagnostics/probe_arguments.py:47) already found by that slug and discarded.

## Judgment — `harness/installation/repository_toolsets.py`

### `eliminate-duplication` — Fail
- repository_toolsets.py:226 `_is_hosted_only`: hard-codes "hosted_only", the name `HostedOnly.written_as()` (harness/annotations/annotation.py:116) already gives, and so misses the `@HostedOnly` spelling that line 233 catches through `Name(...).snake`.

## Judgment — `harness/guidance/fixtures/sample_supplement/rules/__init__.py`

### `one-way-deps` — Fail
- __init__.py:2 `Bdd`: a harness fixture imports `cdd_guidance.practices` (also line 3), which AGENTS.md says harness never imports, so harness/guidance's specs cannot run without the practices built on it.
- __init__.py:4 `SharedPracticeGraphRule`: a harness/guidance fixture imports `harness.graph`, a layer above guidance.

## Judgment — `harness/guidance/fixtures/sample_supplement/sample_supplement.py`

### `one-way-deps` — Fail
- sample_supplement.py:16 `GraphOverlay`: a harness/guidance fixture imports `harness.graph.pattern_overlays`, a layer above guidance.

## Judgment — `harness/agent_tools/agent_tools.py`

### `prefer-instance-operations` — Fail
- agent_tools.py:1316 `AgentToolAnnotation.installs_member`: classmethod answering a constant; not a creation factory, belongs as an instance operation or class attribute.
- agent_tools.py:1327 `AgentInstructionsAnnotation.installs_member`: same classmethod constant answer; not a factory.

## Judgment — `harness/agent_tools/tool_call.py`

### `prefer-instance-operations` — Fail
- tool_call.py:159 `ToolCall.open_sessions_with`: classmethod writing class-level global `ToolCall._sessions`; a global setter, not a factory.
- tool_call.py:176 `ToolCall.session_in`: classmethod global accessor reading class-level `ToolCall._sessions`, which the rule names as not a factory.

## Judgment — `harness/annotations`

### `deep-module` — Fail
- annotations:1 `annotations`: 8 of 9 classes named by other modules' production code (Name in 58 files), far over 40%; module-context's "all seam by design" is not an exemption the rule allows.

## Judgment — `harness/catalog_generator/catalog_practice.py`

### `use-explicit-dependencies` — Fail
- catalog_practice.py:33 `CatalogSkills`: constructor builds `IdeLayout` and a `FileInstallation` (an install/file collaborator) instead of receiving them.

## Judgment — `harness/catalog_generator/hub_board.py`

### `do-not-invent-parallel-object-models` — Fail
- hub_board.py:74 `HubBoard`: holds the catalog's practices, stage copy, and recomputes `stories = giving_stage_examples(practices)` exactly as `ApproachGrids` does (harness/catalog_generator/approach_page.py:172-183); both are fed the same Catalog data (catalog_generator.py:680, approach_page.py:360), so the "catalog approach" concept is modelled twice.

## Judgment — `harness/catalog_generator/project_approach.py`

### `use-explicit-dependencies` — Fail
- project_approach.py:56 `ProjectFiles`: constructor builds `JsonFile` (an external file) instead of taking it as a collaborator.

## Judgment — `harness/chat-ui/pane/hooks/health/cdd-version-client.ts`

### `eliminate-duplication` — Fail
- cdd-version-client.ts:104 `askVersion`: re-implements call → isError → JSON.parse-or-fail by hand (with `versionFrom` at :135) instead of using the one canonical `callTool` in harness/chat-ui/pane/hooks/chat-bar/chat-bar-client.ts:273.

## Judgment — `harness/chat-ui/pane/hooks/health/server-health-client.ts`

### `eliminate-duplication` — Fail
- server-health-client.ts:126 `askServer`: same hand-rolled call/isError/JSON.parse-or-null (with `reportFrom` at :138) duplicating `callTool` in harness/chat-ui/pane/hooks/chat-bar/chat-bar-client.ts:273.

## Judgment — `harness/chat-ui/pane/hooks/chat-bar/guidance-client.ts`

### `eliminate-duplication` — Fail
- guidance-client.ts:105 `call`: a third copy of call/isError/JSON.parse-or-throw, duplicating `callTool` in harness/chat-ui/pane/hooks/chat-bar/chat-bar-client.ts:273.

## Judgment — `harness/chat/chat.py`

### `keep-classes-single-responsibility` — Fail
- chat.py:203 `Chat`: one chat's mailbox operations plus the roster of all chats (`list`) and opening new chats (`open`); 11 public operations, two reasons to change.

### `prefer-instance-operations` — Fail
- chat.py:233 `Chat.list`: classmethod enumerating every chat from the folder; a collection query, not a factory.
- chat.py:242 `Chat.open`: classmethod acting through class-level `cls.opener`; not a factory.

## Judgment — `harness/design_canvas`

### `deep-module` — Fail
- design_canvas:1 `design_canvas`: 5 of 10 classes (Artboard, CanvasBoard, CanvasVersions, DesignCanvas, Place) named by other modules (ux story_canvas.py, space/session/practice_session_output.py, drawio_class_model.py), over 40%.

## Judgment — `harness/diagnostics/probe_outcome.py`

### `use-typed-signatures` — Fail
- probe_outcome.py:35 `ProbeOutcome.from_answer`: public parameter `answer: object` is an untyped bag; the rule gives factories no exemption from typed signatures.

## Judgment — `harness/graph/graph.py`

### `keep-classes-single-responsibility` — Fail
- graph.py:1290 `Graph`: 22+ public operations spanning loading, refreshing, saving, overlays, inventory, and explorer views.
- graph.py:859 `PracticeNodes`: holds nodes, links edges, builds schemas, and runs rule checks; several reasons to change.

### `limit-operation-parameters` — Fail
- graph.py:527 `Node.__init__`: 5 parameters; type/node_id/name/source form one identity concept that should be an object.
- graph.py:990 `PracticeNodes.add_named`: 4 parameters repeating the Node constructor's setup.

## Judgment — `harness/graph/model_node.py`

### `prefer-instance-operations` — Fail
- model_node.py:173 `register_practice`: classmethod writing class-level registry state; not a factory.
- model_node.py:180 `practice_kind`: classmethod reading class-level registry state; not a factory.

## Judgment — `harness/guidance`

### `deep-module` — Fail
- guidance:1 `guidance`: 20 of 39 classes named by other modules, over the 15 that 40% allows.

## Judgment — `harness/hooks/hook_server.py`

### `prefer-instance-operations` — Fail
- hook_server.py:436 `HookServer.show_toasts_with`: classmethod setting class-level `_toast_shown_by`; global setter, not a factory.

## Judgment — `harness/hooks/hooks.py`

### `prefer-instance-operations` — Fail
- hooks.py:92 `Hook.companion_flags`: classmethod, not a factory.
- hooks.py:96 `Hook.disabled_on`: classmethod reading a flag off an operation; not a factory.

## Judgment — `harness/installation/files.py`

### `limit-operation-parameters` — Fail
- files.py:100 `FileInstallation.__init__`: 4 parameters (layout, path, channel, repo), over the 3 allowed; constructors are not exempt.

## Judgment — `harness/installation/installer.py`

### `use-explicit-dependencies` — Fail
- installer.py:326 `Installer`: constructor builds `InstallRecord(_SHARED_RECORD)` (a file record) and `IdeLayout` instead of receiving them.

## Judgment — `harness/markdown`

### `deep-module` — Fail
- markdown:1 `markdown`: 7 of 17 classes named by other modules, over the 6 that 40% allows.

## Judgment — `harness/mcp/mcp_server.py`

### `use-explicit-dependencies` — Fail
- mcp_server.py:225 `McpInstallation`: constructor builds `McpDaemon(CddHome())`, an external server collaborator, instead of receiving it.

## Judgment — `harness/mcp/server_hooks.py`

### `use-explicit-dependencies` — Fail
- server_hooks.py:18 `CddServerHooks`: constructor builds `ServedCheckout`, `McpDaemon`, and reaches the global `RepositoryToolsets.of_running_checkout()`.

## Judgment — `harness/process`

### `deep-module` — Fail
- process:1 `process`: 11 of 13 classes named by diagnostics, hooks, mcp, catalog_generator, and scripts, over the 5 that 40% allows.

## Judgment — `harness/whiteboard/whiteboard.py`

### `do-not-invent-parallel-object-models` — Fail
- whiteboard.py:32 `Box`: the canonical geometry, but `MiroShape` (cdd_guidance/practices/stories/model/miro/nodes.py:42) copies its x/y/w/h fields instead of holding a `Box`; the copy is in MiroShape.

## Judgment — `harness/whiteboard`

### `deep-module` — Fail
- whiteboard:1 `whiteboard`: 9 of 12 classes named by clean_engineering, stories, and ddd whiteboard models, over the 4 that 40% allows.

## Judgment — `cdd_guidance/practices/clean_engineering/model/graph_reading.py`

### `hide-inner-details` — Fail
- graph_reading.py:77 `_exempt_test_code`: reads `node.data.get(...)` directly, the fact storage of `Node` (harness/graph/graph.py:534), instead of `node.get_fact` (graph.py:549); the dict becomes a cross-module contract.

## Judgment — `scripts/unit_guard/sitecustomize.py`

### `no-prototype-swapping` — Fail
- sitecustomize.py:68 `_time_examples`: replaces mamba's `Example._finish` on the class at import time (`mamba_example.Example._finish = timed_finish`), monkeypatching a third-party type instead of hooking through a reporter or seam.

## Judgment — `space/kanban/app/src/kanban/board/side-panel-client.ts`

### `hold-state-on-the-object-not-in-parameters` — Fail
- side-panel-client.ts:73 `closeTicketPanels`: takes the ticket's name, which `TicketClient.letGo` (ticket-client.tsx:223) passes as `this.name` though it holds the ticket; the name is also called `ticket`, while `ticket` is a `TicketClient` everywhere else in the file (line 44).

## Judgment — `space/kanban/app/src/kanban/ticket/open-card-client.ts`

### `hold-state-on-the-object-not-in-parameters` — Fail
- open-card-client.ts:72 `releaseTicket`: takes a ticket's name, which `TicketClient.letGo` (ticket-client.tsx:222) passes as `this.name` while holding the ticket; the parameter is still called `ticket`, beside `ticket: TicketClient` in `toggle`/`open`/`openSegment`.
- open-card-client.ts:80 `dropPractice`: `TicketPractices` (ticket-practices.ts:27) passes `this.ticket.name` down so the receiver matches tiles by name instead of being handed the ticket it holds.

## Judgment — `space/kanban/app/src/kanban/ticket/files-panel-client.ts`

### `eliminate-duplication` — Fail
- files-panel-client.ts:54 `show`: re-implements the panel-replacing body `[...panels.filter(entry => entry.kind !== panel.kind), panel]` that `replacing` in side-panel-client.ts:13 already holds (and `change`, line 57, repeats `changeReport` from side-panel-client.ts:30 by kind); one store-of-panels operation written twice.

## Judgment — `space/kanban/app/src/kanban/ticket/ticket-work.ts`

### `do-not-invent-parallel-object-models` — Fail
- ticket-work.ts:17 `WorkStanding`: a hand-made camelCase copy of Python's `StageWork` (space/kanban/ticket.py:1136: `action_states`, `has_violations`, `violation_count`, `allowed_actions`, `commands`), rebuilt field by field in `workIn` (line 71) and used by tile-actions-client.ts; under cdd_web_domain_access the browser uses the generated data/client, not a parallel type, and "standing" is a term the Python model does not use.

## Judgment — `space/kanban/app/src/kanban/ticket/ticket-client.tsx`

### `keep-classes-single-responsibility` — Fail
- ticket-client.tsx:19 `TicketClient`: after splitting out work, practices, and prompts it still mixes display copy (`runNextLabel`, `runNextHint`, `nextNote`, `lockNote`, `stagePlace`, `standing`), chat opening and worktree activation, drop-target handling, optimistic move/follow wiring, and run-next dispatch; several independent reasons to change.

## Judgment — `space/kanban/app/src/kanban/ticket/tile-client.ts`

### `use-consistent-naming` — Fail
- tile-client.ts:60 `change`: `ticket: string` (a name) in `change`/`openOn`/`isOpen`/`close`/`pin`/`hoverOut`, but `ticket: TicketClient` in `toggle` (line 81) and `TileSpot.ticket`; one name, two types.

## Judgment — `space/kanban/board.py`

### `keep-classes-single-responsibility` — Fail
- board.py:104 `Board`: beyond finding columns, tickets, and items it lists repository folders for a workpath picker (`folders`, line 325), serves practice help (`help`, line 332), retries saves (`save_again`), and keeps a chat-fix preference (`set_sends_fixes_directly`); unrelated reasons to change on one class.

## Judgment — `space/kanban/ticket.py`

### `keep-classes-single-responsibility` — Fail
- ticket.py:109 `Ticket`: 28 public operations spanning parent/child tree, chat assignment and links, file listings, format and overlay choices, activation/closing/archiving, stage moves, tagging/text, and violations reporting; many reasons to change.

## Judgment — `space/repo/mock_repo.py`

### `limit-operation-parameters` — Fail
- mock_repo.py:154 `commit`: four values (`checkout`, `paths`, `message`, `untracked`); `checkout` is state the calling `MockRepo` already holds (`self.root`), so the fake takes setup a per-checkout object should carry.

## Judgment — `space/repo/repo.py`

### `keep-classes-single-responsibility` — Fail
- repo.py:77 `Repo`: reads repository state (branches, refs, dirty, current commit) and also runs the publish workflows `push_commit`, `push_work`, `merge_to_main`, `push_to_main`, `push` (lines 269-337); querying git and the publishing process change for different reasons.

## Judgment — `space/repo/repos.py`

### `use-explicit-dependencies` — Fail
- repos.py:116 `CddConfig`: builds its `JsonFile` (and a default `CddHome()`) inside `__init__`, so the file store cannot be swapped for a fake; only the home folder can be.

## Judgment — `space/session/session.py`

### `keep-classes-single-responsibility` — Fail
- session.py:82 `Session`: 32 public operations covering identity and paths, idea text and tags, overlays, guidance selection, file read/write, graph explorer queries, chat context, file comments, loop and log, handoffs, debug, and CDR records; many reasons to change.

## Judgment — `space/session/sessions.py`

### `keep-classes-single-responsibility` — Fail
- sessions.py:111 `Sessions`: the session collection (create, named, load, moved, removed, close) also serves process-wide answer caching (`answer`, `serve_answer`, line 146), the open-state/switch protocol for chats, and board practices; separate reasons to change.

## Judgment — `tools/prompt_notify/ide_toast/watch_notice.js`

### `never-swallow-exceptions` — Fail
- watch_notice.js:12 `messageFromNotice`: `catch { return "" }` substitutes an empty message for any parse failure, so a file that is permanently malformed reads as "no notice" forever, unseen; the half-written case is not told apart from a broken one.

## Judgment — `cdd_guidance/context_setup/context_index.py`

### `use-explicit-dependencies` — Fail
- context_index.py:131 `OpenAIEmbeddingProvider`: its constructor builds the external `OpenAI()` client (line 139) instead of taking it, so the adapter can only ever run against the live OpenAI service.
- context_index.py:183 `ContextIndex`: when no provider was passed it builds `OpenAIEmbeddingProvider()` itself (default hidden behind the `None` at line 158), so the collaborator the constructor seems to take is fetched inside the class anyway.

## Judgment — `cdd_guidance/practices/agent_bdd/agent_cli_bdd.py`

### `use-explicit-dependencies` — Fail
- agent_cli_bdd.py:273 `CliAgentBlock`: its constructor builds `CursorCli()` (line 282), the external command-line client, instead of receiving it; the sibling `ChatAgentBlock` (agent_chat_bdd.py:11) and the base `AgentBlock` (agent_block.py:34) take no such hidden client.

## Judgment — `cdd_guidance/practices/clean_engineering/model/base_class_model.py`

### `keep-classes-single-responsibility` — Fail
- base_class_model.py:119 `OoadClass`: one class is the graph node (update_self, clone, reconcile_children, relationships), the source-fact extractor for rules (take_lines, load_source_facts, held_fields) and the doc-comment writer (doc_comment), three reasons to change.
- base_class_model.py:344 `Module`: the graph node also scans import statements (_import_targets, _without_type_imports) and reads the folder's context files (load_folder_facts, take_public_sources).

## Judgment — `cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py`

### `keep-operations-small-focused` — Fail
- class_layout.py:468 `run`: 50 statements in one loop body that prunes, applies edge rules and prices each step; the speed reason in its docstring does not lift the limit.

### `limit-comments` — Fail
- class_layout.py:471 `run`: the docstring says it takes "the same steps at the same prices as `_steps` and `_price`", but neither method exists anywhere in the file, so the comment points at removed code.

## Judgment — `cdd_guidance/practices/clean_engineering/model/operation.py`

### `keep-classes-single-responsibility` — Fail
- operation.py:88 `Operation`: graph node and signature parser, plus source-span measuring (load_span_facts, take_lines) and body fingerprinting for duplication (_fingerprint, take_body_fingerprint), several jobs on one class.

## Judgment — `cdd_guidance/practices/clean_engineering/model/operation_metrics.py`

### `keep-classes-single-responsibility` — Fail
- operation_metrics.py:169 `SourceText`: 18 unrelated measures over any text, from exception handling and magic numbers to markdown card bullets (markdown_bullet_lines) and prototype swaps; code measures and markdown card reading are separate jobs.

## Judgment — `cdd_guidance/practices/ddd/ddd.py`

### `eliminate-duplication` — Fail
- ddd.py:79 `__init__`: has the same body as ux.py:60 and bdd/bdd.py:35, and differs only in the default fidelity. `PracticeGuidance.__init__` (harness/guidance/guidance.py:297) could read a class attribute for the first fidelity instead of every practice copying a constructor.

## Judgment — `cdd_guidance/practices/ux/ux.py`

### `eliminate-duplication` — Fail
- ux.py:60 `__init__`: the same body as ddd.py:79 and bdd/bdd.py:35, with only the default fidelity `"ia"` differing; the owner is `PracticeGuidance.__init__` at harness/guidance/guidance.py:297.

## Judgment — `cdd_guidance/practices/bdd/bdd.py`

### `eliminate-duplication` — Fail
- bdd.py:35 `__init__`: a third copy of the constructor at ddd.py:79 and ux.py:60, there only to default the fidelity to `"behavior"`; it belongs once in `PracticeGuidance` (harness/guidance/guidance.py:297).

## Judgment — `cdd_guidance/practices/ddd/model/graph_reading.py`

### `use-typed-signatures` — Fail
- graph_reading.py:122 `get_fact`: types `default` and the return value as bare `object`. The method it overrides, `Node.get_fact` (harness/graph/graph.py:546), uses the domain alias `FactValue`, so this override loosens the base's typing.

## Judgment — `cdd_guidance/practices/stories/app/story-map/story-map-views.tsx`

### `limit-operation-parameters` — Fail
- story-map-views.tsx:32 `useStoryMapReading`: takes 4 parameters. `api` is built from `failures` (line 77), and `failures` and `editing` are also handed down to `useStoryMapEdit`.

## Judgment — `cdd_guidance/practices/stories/model/claude_design`

### `conforms-to-schema` — Fail
- claude_design:1 `claude_design`: the package holds only an empty `__init__.py` (0 bytes) and nothing in the repository imports it, so it has no participants; it is a dead folder that should hold classes or be deleted.

## Judgment — `cdd_guidance/practices/ux/story-demo/story-demo-page.js`

### `use-explicit-dependencies` — Fail
- story-demo-page.js:14 `StoryDemoPage`: the frames can be injected, but the constructor always builds `PlayDualRunner` (line 24), the engine that plays stories, along with `PaintReflect` and `ThenFeedback`, so the runner cannot be swapped.

## Judgment — `harness/graph/app/filter_choices_record.py`

### `one-way-deps` — Fail
- filter_choices_record.py:87 `__main__`: harness imports `cdd_guidance.practices` to register practices. AGENTS.md says harness imports nothing from `cdd_guidance`; the practices register themselves from their package `__init__.py`.

## Graph hits judged noise

| File:line | Rule | Why it is noise |
|---|---|---|
| cdd_guidance/patterns/cdd_web_domain_access/access_facts.py:23 | do-not-invent-parallel-object-models | `AccessFile` and OSS `MigrationFile` are different concepts in unrelated patterns; the only shared fields are a file's name, text, and its `SourceText` wrapper, and no behaviour is copied. |
| cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py:267 | eliminate-duplication | `MigrationFile.__init__` is three field assignments matching `AccessFile.__init__`; that is construction, not repeated logic, and the classes model different things. |
| cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py:194 | simplify-control-flow | `_brace_end` nests for → elif → if, three levels; the scanner counts the `elif` as an extra level. |
| cdd_guidance/patterns/oss_portal_domain_driven/graph_overlay.py:187 | use-typed-signatures | `_set_facts` is a private helper on the private `_OssReading`; the rule covers public signatures. |
| cdd_guidance/patterns/oss_portal_domain_driven/graph_overlay.py:191 | use-typed-signatures | `_file_node` is private on the private `_OssReading`; the rule covers public signatures (the real problem, `practice` held on self, is a hold-state Fail). |
| harness/guidance/practice_catalogue.py:89 | prefer-instance-operations | `create_all` is a creation factory (makes a new instance of every practice), a variant of the exempt `create`. |
| harness/guidance/stages.py:26 | limit-operation-parameters | `StageScope.__init__` is the constructor of a plain value whose four fields are its full field set; creation that takes the field set needed to construct is exempt. |
| harness/agent_tools/agent_tools.py:585 | prefer-instance-operations | `instantiate` is a creation factory making a toolset from configuration, which the rule exempts. |
| harness/catalog_generator/brand.py:53 | keep-operations-single-responsibility | `apply` only joins a path and copies a folder; no domain calculation. |
| harness/catalog_generator/brand.py:70 | keep-operations-single-responsibility | `copy_commons` is pure copying; no domain calculation mixed in. |
| harness/catalog_generator/generate_cdd_catalog.py:31 | keep-operations-single-responsibility | `main` is the CLI entry point orchestrating parse/load/print; no calculation in it. |
| harness/chat-ui/pane/hooks/chat-bar/chat-bar-client.ts:344 | never-swallow-exceptions | cdd_web_domain_access pattern: failure is shown to the person via `shownAsFailure` and the page stops (fail-loud-on-mcp). |
| harness/chat-ui/pane/hooks/chat-bar/session-client.ts:36 | never-swallow-exceptions | cdd_web_domain_access pattern: shows the failure, then answers null so the page stops (`CddApi.post` answers null after showing). |
| harness/chat-ui/pane/hooks/health/cdd-version-client.ts:102 | never-swallow-exceptions | cdd_web_domain_access fail-loud-on-mcp: an unreachable server's reason is kept as `problem` and shown on the badge; other failures call `showFailure`. |
| harness/chat-ui/pane/hooks/health/cdd-version-client.ts:135 | never-swallow-exceptions | cdd_web_domain_access pattern: non-JSON text is a failure; the caller turns null into `showFailure` with the server's text. |
| harness/chat-ui/pane/hooks/health/server-health-client.ts:138 | never-swallow-exceptions | cdd_web_domain_access pattern: null becomes a `tools-missing` answer carrying the server's text as `problem`, shown on the health panel. |
| harness/graph/graph_rules_collection.py:18 | extensions-live-with-the-domain | graph sits above guidance; moving `GraphRule` into harness/guidance would make guidance import graph, inverting the one-way dependency. Not a domain extension hosted in a framework. |
| harness/installation/data_class.py:177 | use-typed-signatures | Reflective serializer: `data(instance)` takes any annotated object by design; no narrower domain type exists. |
| harness/installation/data_class.py:185 | use-typed-signatures | Same reflective serializer (`reference`); any data class instance is the contract. |
| harness/installation/data_class.py:194 | use-typed-signatures | Private helper `_identity_data`; the rule covers public signatures. |
| harness/installation/data_class.py:200 | use-typed-signatures | Private helper `_referenced`; not a public signature. |
| harness/installation/data_class.py:212 | use-typed-signatures | `data_of(subject)` is the one any-value-to-JSON function; its input is any value by definition. |
| harness/installation/language_adapter.py:522 | limit-comments | The "comment" is a line of generated TypeScript inside a string list, not a Python comment. |
| harness/installation/repository_toolsets.py:93 | prefer-instance-operations | `of_running_checkout` is a creation factory returning a new instance. |
| harness/mcp/mcp_server.py:607 | never-swallow-exceptions | Protocol boundary: logs with `logger.exception` and returns an MCP error result naming the failure type and text. |
| harness/mcp/mcp_server.py:607 | use-exceptions-properly | Returns `isError` with the failure's name, not a default or fallback value; the only handler at the MCP boundary. |
| harness/mcp/mcp_server.py:792 | use-typed-signatures | Private `_content_blocks`; its input is whatever any tool returned. |
| harness/mcp/tool_calls.py:93 | use-typed-signatures | On private `_RunningCall`; holds any tool's return value. |
| harness/mcp/tool_calls.py:152 | never-swallow-exceptions | The failure is recorded with `started.fail(failure)` and re-raised to waiting callers or logged by `log_unheard_failure`. |
| harness/mcp/tool_calls.py:152 | use-exceptions-properly | Not a fallback: the caught failure is kept and delivered to the caller of `answer`. |
| scripts/unit_guard:1 | no-module-per-class | The folder holds no class at all, only `sitecustomize.py`, which must sit alone in its own folder so `test.ps1` can put it first on PYTHONPATH. |
| space/kanban/app/src/kanban/board/side-panel-client.ts:31 | use-typed-signatures | `panel` is annotated `(panel: SidePanel)` on line 31, and `ReportPanel` in the callback type on line 30. |
| space/kanban/app/src/kanban/ticket/files-panel-client.ts:44 | keep-classes-single-responsibility | Every operation changes the one files panel's state (open, filter, tab, reload, save); comments are already split out to `OpenFileComments`. |
| space/kanban/app/src/kanban/ticket/files-panel-client.ts:58 | use-typed-signatures | `panel` is annotated `(panel: SidePanel)`; the callback's `panel` is typed `FilesPanel` on line 57. |
| space/kanban/app/src/kanban/ticket/files-panel-client.ts:63 | use-typed-signatures | `source` comes from a destructured parameter typed `Pick<FilesChoice, 'source' \| 'progress'>` on line 61. |
| space/kanban/app/src/kanban/ticket/open-card-client.ts:12 | shape-classes-around-resources | `RequiredFidelity` is Python's wire data (`ColumnData['work_required']`), which cdd_web_domain_access supplies as data; behaviour stays in Python, and `OpenCardClient` only passes it through. |
| space/kanban/app/src/kanban/ticket/report-client.ts:45 | shape-classes-around-resources | `ViolationData` is the `{Object}Data` that cdd_web_domain_access generates from Python's plain result; `ReportClient` wraps the report it owns and only formats violations into prompts. |
| space/kanban/app/src/kanban/ticket/ticket-work.ts:21 | shape-classes-around-resources | `RequiredFidelity` is cdd_web_domain_access wire data from Python; `progressOn` only reads its slug to find the ticket's own progress. |
| space/kanban/app/src/kanban/ticket/tile-client.ts:61 | use-typed-signatures | `tile` is annotated `(tile: Tile)` on line 61. |
| space/kanban/app/src/session-board/http-exception.ts:31 | limit-operation-parameters | Express (lern_domain_driven) recognises error middleware only by its four-argument signature `(err, req, res, next)`. |
| space/kanban/backlog_item.py:46 | keep-classes-single-responsibility | Each operation acts on the item itself: its file, its place in the Backlog (move, nest, leave), and starting a ticket from it; one resource. |
| space/repo/mock_repo.py:69 | keep-classes-single-responsibility | `MockGit` is the fake for git; its operations mirror the git behaviour it stands in for, which is its one reason to change. |
| space/session/practice_session_output.py:255 | keep-classes-single-responsibility | `FidelitySessionOutput` is one fidelity's output (root, formats, files); 10 operations, all on that output, with format choice already in `FidelityFormats`. |
| tools/prompt_log/prompt_log.py:133 | use-typed-signatures | `_preview` is a private helper, not a public signature; it takes whatever a hook payload field holds. |
| cdd_guidance/catalog/commons/catalog-approach.js:79 | state-change-returns-record-or-named-failure | `ApproachPage` is a constructor function: `new` returns the object it builds, and it coordinates no state change. The file is also a generated copy of harness/catalog_generator/templates/commons/catalog-approach.js |
| cdd_guidance/catalog/commons/catalog-drawio.js:87 | state-change-returns-record-or-named-failure | `StoryMapZoom` is a constructor that only sets its own fields. The file is also a generated copy of harness/catalog_generator/templates/commons/catalog-drawio.js |
| cdd_guidance/catalog/commons/catalog-foundry-tour.js:196 | state-change-returns-record-or-named-failure | `FloatingTooltips` is a constructor that sets three null fields. Note: this file has no source template under harness/catalog_generator/templates/commons, so it is generated output with no generator source |
| cdd_guidance/catalog/commons/catalog-nav.js:255 | state-change-returns-record-or-named-failure | `NavDrawer` is a constructor that only looks up three elements. The file is also a generated copy of harness/catalog_generator/templates/commons/catalog-nav.js |
| cdd_guidance/catalog/examples/ddd/tactics.ts:479 | eliminate-duplication | Teaching example. `authenticateAccount` and `register` share only a four-line guard-then-`becomeUser` shape, with different requirement checks, error keys and repository verbs; the shared part already lives in `repository()` and `becomeUser()` |
| cdd_guidance/context_setup/context_setup.py:138 | keep-operations-single-responsibility | `_markdown_of` reads or converts one file and does no domain calculation; picking by file suffix is part of the read |
| cdd_guidance/practices/agent_bdd/agent_cli_bdd.py:290 | errors-out-of-existence | A missing or unauthenticated `cursor-agent` is a broken environment, not an ordinary edge, so raising is right |
| cdd_guidance/practices/clean_engineering/model/code_class_model.py:104 | keep-classes-single-responsibility | Every method is one step of writing a class declaration in one language: hooks each language subclass overrides. That is one job |
| cdd_guidance/practices/clean_engineering/model/graph_reading.py:216 | keep-operations-single-responsibility | `_model_in` reads a file and hands it to the format's parse in one line; it calculates nothing itself |
| cdd_guidance/practices/clean_engineering/model/operation_metrics.py:442 | keep-classes-single-responsibility | Every method measures the same Python syntax tree; the different jobs are already split out into `CatchClause`, `Constructions` and `OwnObjects` |
| cdd_guidance/practices/clean_engineering/model/property.py:60 | keep-classes-single-responsibility | Its methods all describe one field: its signature, notes, relationship and owner. The count includes the base node's clone, save, as_record and update_self overrides |
| cdd_guidance/practices/stories/app/story-map/story-map-failures.ts:7 | use-explicit-dependencies | The transport (`send`) comes in through the constructor. `StoryMapApi` is built in a factory over the base's own `notTold` callback, which no caller could supply, the same seam `PageFailures` uses (space/kanban/app/src/kanban/board/page-failures.ts:14) |
| cdd_guidance/practices/stories/model/javascript/seeds:1 | conforms-to-schema | A folder of seed files that are read as text to start a new tree's step library (javascript_story_model.py:83), not a code package with participants |
| cdd_guidance/practices/stories/model/json/nodes.py:304 | keep-operations-single-responsibility | `from_workspace` finds and reads the file, then hands the text to `parse_file`; no calculation is mixed in |
| cdd_guidance/practices/stories/model/markdown/nodes.py:424 | keep-operations-single-responsibility | `_read_file` reads, then delegates to `parse` and adds the file name to the error; no domain calculation |
| cdd_guidance/practices/ux/story-demo/mount-generated-mockup.js:527 | use-explicit-dependencies | A `WeakSet` is the class's own bookkeeping built from nothing outside, not a collaborator |

