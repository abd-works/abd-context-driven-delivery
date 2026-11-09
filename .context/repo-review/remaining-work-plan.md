# Remaining work after round 9, and how to reach the metric targets

The fix-and-revalidate loop on `ensure-domain-orientation-refactor` ended after round 9 (2026-11-09), at commit a4440c7f. This plan records what is unfinished and how the code metrics can reach their targets without changing the intended architecture.

The numbers come from `measure_revision.py` on a4440c7f. [code-metrics-trend.md](code-metrics-trend.md) has the full tables, and [trend-rounds-1-5.md](trend-rounds-1-5.md) has the AI findings.

## Where the loop ended

- **AI findings:**
  - In round 5 there were 150 findings in the three goal classes. In round 9 there were 27 in the scope round 8 checked, and 56 including new scope.
  - Round 9's fixes addressed every round-9 finding except those listed below.
  - The round-9 high finding was the UX explorer crashing on a reopened graph. It is fixed, and every reader of another practice's facts now has a reopen spec.
  - No validation round has run since the round-9 fixes. So the final count is not measured.
- **Code metrics:** round 9 was the first round gated by the metrics. Nothing got worse, and 16 of the 23 guarded numbers improved. The ones still short of their targets are in the table under "Reaching the targets".

## Unfinished work

| Item | Where | What is left | Why it stopped |
|---|---|---|---|
| Final validation | all areas | Run round 10 with round 9's checks and nothing wider, then count it against the stop rule: under 30 goal findings in round 9's scope, and no high finding in a goal class | Cost; the user ended the loop after round 9 |
| R9-M1, part | `cdd_guidance/practices/stories/model` | Java story files, and Python story files that do not parse, are still read by the text regex reader. Scenario steps and backgrounds inside a story block are read from the block's text, not its step blocks | Spend limit |
| `FidelityGuidance` | `harness/guidance/guidance.py` | 51 methods, total complexity 131. The next step is a declared-outputs part and a templates part | Decision record `harness/guidance/.context/cdr/0004` |
| `GuidanceAction` | `harness/guidance_actions` | 36 methods | Decision record `harness/guidance_actions/.context/cdr/0002` |
| `TypeScriptToolset` | `harness/installation/language_adapter.py` | 37 methods, total complexity 101 | Decision record `harness/installation/.context/cdr/0002` |
| `Ticket` | `space/kanban/ticket.py` | 33 methods. 32 of them are the 15 MCP tools and 15 fields it publishes, so a part cannot take them without renaming the tools | Decision record `space/kanban/.context/cdr/0004` |
| Repository cards | `.context/repo-model.md`, `repo-model.drawio`, `.context/repo-runtime.md` | They still name removed methods (`instantiate_all`, `working_fidelity`, `working_format`, `_current_fidelity`, `clean_engineering_companion`, `result_template`, the old `GuidanceAction` constructor) | Off-limits to the fix agents; the user's to update |
| Server pause during a validate (B10) | `harness/graph` | The worker now writes a validate's checked nodes, so the server no longer packs them. A heavy spec times six chats validating while pings are timed; its first run is in the round-9 heavy run | Needs that heavy result confirmed |
| `tools` harness steps | `tools/.context/cdr/0001` | The harness steps this record depends on have not landed for three rounds | Outside the loop's goal classes |
| Agent BDD secrets spec | `cdd_guidance/practices/agent_bdd` | `agent_bdd_spec` "should load the agent's secrets" fails in any checkout without the git-ignored `conf/.secrets` | An environment gap, not a code fault: give the spec a skip when the file is absent, or a fixture file |

## Reaching the targets

**Target:** "good", as set in `metrics_gate.py`. **Great:** the level a well-kept codebase usually holds.

| Metric | Round 9 | Target | Great |
|---|---|---|---|
| Functions with more than 10 paths | 100 of 6,062 | 60 | 30 |
| Functions with more than 20 paths | 3 | 0 | 0 |
| Hard-to-read functions (readability score above 15) | 43 | 30 | 15 |
| Functions taking more than 5 parameters | 35 | 15 | 5 |
| Modules with a poor maintainability score | 29 of 386 | 15 | 8 |
| Lines in the longest module | 1,018 | 800 | 500 |
| Total complexity of the most complex class | 192 | 100 | 50 |
| Most methods in one class | 51 | 30 | 20 |
| Classes doing several unrelated jobs | 44.8% | 40% | 20% |
| Classes depending on more than 14 others | 42 | 25 | 10 |
| Classes where one call can set off more than 50 methods | 76 | 50 | 25 |
| Most modules importing one module | 60 | 40 | 30 |
| Copied blocks | 18 | 15 | 10 |
| Helper names written separately in several modules | 12 | 5 | 0 |
| Class names in more than one module | 2 | 0 | 0 |
| Unrelated classes holding the same fields | 2 | 0 | 0 |

### The architecture these strategies keep

- `harness/` imports nothing from `space/`, `tools/` or `cdd_guidance/`; those register with it.
- The practice, fidelity and action shape stays as it is.
- Behaviour sits on the object that owns the data. When an owner grows too large, it holds parts it creates once, rather than handing work to helper modules. Round 9 split `Graph` and `PracticeGuidance` this way.
- Every change passes the metrics gate against the commit it started from.

### Strategies, in order of effect for the effort

Each estimate is from the measured offenders, not a promise. Re-measure after each step.

**1. Make the gate recognise a move (tooling, small).**
- **The problem:** the gate names offenders by file and name. Moving a class to a new module therefore reads as one item gone and a new item past a limit. Round 9's agents kept `Filter`, `Inventory` and `GraphExplorer` in `graph.py` for that reason alone.
- **The change:** in `metrics_gate.py`'s `worse_items`, match an item by its class and function name when its file changed, and judge the moved item against its old value.
- **What it enables:** strategy 4, and any split of a long module.
- **Delta:** no metric moves by itself.

**2. Split the remaining over-limit classes into held parts.**
- **Delta:**
  - most complex class: 192 → about 100
  - most methods in one class: 51 → about 30
  - unrelated-jobs share: 44.8% → about 42%
  - classes over 100 total complexity: 7 → 0 or 1

| Class | Now (total complexity / methods) | Parts it should hold | Estimate after |
|---|---|---|---|
| `RecipeExpansion` (`harness/agent_tools/recipe.py`) | 192 / 45 | The validators call it one job. Its size is argument reading and text writing together. Split out a held `RecipeArguments` part (what the call supplies, defaults, required checks) and a `RecipeText` part (placeholders, tails) | about 90 / 25 |
| `FidelityGuidance` (`harness/guidance/guidance.py`) | 131 / 51 | Declared outputs, and templates, as decision record 0004 says | about 75 / 30 |
| `MarkdownAggregate` (`ddd/model/markdown/nodes.py`) | 129 / 26 | A reading object made for each read, as round 9 did for the Stories markdown readers | about 50 / 12 |
| `FileInstallation` (`harness/installation/files.py`) | 129 / 30 | One part per kind of file it installs (skills, rules, MCP config) | about 70 / 20 |
| `ArrowRouter` (`clean_engineering/model/diagram/class_layout.py`) | 115 / 22 | Route search, and crossing checks, each a part | about 60 / 14 |
| `MarkdownOoadClass` (`clean_engineering/model/markdown/markdown_class_model.py`) | 104 / 17 | A per-read reading object, as for Stories | about 45 / 10 |
| `TypeScriptToolset` | 101 / 37 | Interface writing and client writing | about 60 / 22 |

- **Classes that publish MCP tools** (`Ticket`, the toolsets): these can only get under 30 methods if a part may publish a tool under its owner's name. That means changing `@tool_subject` and the toolset rehosting in `harness/agent_tools`. Weigh it against keeping tool names stable, and decide it in a decision record before anyone starts.

**3. Make the readers and parsers use a table of line kinds (Clean Engineering, Stories, DDD).**
- **Where they are:**
  - Of the 100 functions with more than 10 paths: 37 are in `cdd_guidance/practices/clean_engineering`, 14 in `stories` and 7 in `ddd`.
  - Of the 43 hard-to-read functions: 15, 12 and 4 are in the same three folders.
  - Almost all are parsers: `markdown_class_model.read_body` (21 paths), `sketch_class_model._classes_in` (21), `c_family_parse`, the markdown and draw.io readers.
- **The change:** a reader that tests each line against a long `if`/`elif` chain becomes a small table from line kind to the method that handles it, on the per-read reading object.
- **The pattern is already proven:** the Stories markdown readings in round 9 took `MarkdownStoryModel` from 179 to 85 total complexity this way.
- **Delta:**
  - functions with more than 10 paths: 100 → about 60
  - hard-to-read functions: 43 → about 25
  - modules with poor maintainability: 29 → about 18. Three of the worst modules (`class_layout.py`, `drawio_class_model.py`, `markdown_class_model.py`, each scoring 0) are in this group.
  - functions with more than 20 paths: 3 → 1. The last is `scripts/instances.py:run`, which is strategy 6.

**4. Split the three long modules along the parts they already hold (needs strategy 1).**
- `harness/graph/graph.py` (1,018 lines): `Filter`, `Inventory` and `GraphExplorer` move to `harness/graph/explorer.py`.
- `harness/agent_tools/agent_tools.py` (895 lines): the toolset rehosting moves beside `ToolsetMembers`.
- `stories/model/story_model.py` (860 lines): `Epic` and its tree move to their own module.
- **Delta:**
  - longest module: 1,018 → about 700
  - most modules importing one module: 60 → about 45. The module most imported is `graph.py`, and the explorer's users stop importing it.

**5. Narrow what rules depend on (coupling).**
- **The problem:**
  - `PracticeGraphRule` depends on 70 classes, `Graph` on 60, `Node` on 54, `PracticeGuidance` on 44, `RuleCheckContext` on 36 and `ProductionCodeRule` on 31.
  - The rule classes reach the whole graph, when they only need the context of one check.
- **The change:** rules ask `RuleCheckContext` for what they read, and `RuleCheckContext` holds the narrow answers. Type hints that only annotate are quoted and imported for type checking alone, as round 8 did for `ExplorerTree`.
- **Delta:**
  - classes depending on more than 14 others: 42 → about 32
  - classes where one call can set off more than 50 methods: 76 → about 65

**6. Clear the small duplicates.** Each is a short, specific change.
- **Helper names in several modules (12 → about 3):**
  - `class_channel.feature.py` and `story_channel.feature.py` share 8 helper names (`walk`, `_write`, `load_source`, `save_channel`, `_write_channel`, `_read_channel`, `_open`, `_grouped`). One channel test fixture should own them.
  - `_name_of` is written three times, in `operation_metrics.py` and the two UX node readers.
  - `_folder_of` is written twice, in DDD's `graph_reading.py` and `guidance.py`.
- **Class names in more than one module (2 → 0):** `Scenario` and `Step` in `space/kanban/story_test.py` repeat the Stories model's names. Rename them to what they are there, the test runner's own records, or use the Stories model.
- **Unrelated classes holding the same fields (2 → 0):**
  - `Edge` and `SavedEdge`: the saved form should be written by `Edge` itself.
  - `CodeBody` and `StoryFile`: one shape for "text of a file at a path".
- **Identical functions (1 → 0):** `_first_pong` in `scripts/instances.py` and `scripts/start.py`. One owner, which `scripts/instances.py:run` (21 paths) also uses when it is split.
- **Copied blocks (18 → about 12):** most copies are in `scripts/` (`install.py`, `guidance-diagnostics.py`, `clean-engineering-validate.py`, `start.py`, `start_graph_app.py`) and two draw.io scanners. The scripts should call one shared start-up helper, and the two scanners one base check.

**7. Hold what a constructor is given (parameters).**
- **The problem:**
  - 35 functions take more than 5 parameters. Most are constructors of the model objects: `story_model.__init__` (9), `base_class_model.__init__` (8), `graph_build.__init__` (8), `code_body`, `operation`, `class_layout` and UX `nodes` (7 each).
  - `design_canvas/canvas.py` adds four drawing functions with 7–8 parameters.
- **The change:**
  - Group what travels together into one value object it already describes: a position and size become a box, and a name, owner and source become the node's identity.
  - In the canvas, a drawing style the canvas holds replaces the style values passed to every call.
- **Delta:** functions taking more than 5 parameters: 35 → about 15.

**Not a strategy: the abstractness balance.**
- The measure counts a folder as abstract only by its abstract classes, and it scores the framework folders as plain concrete code (12 folders far from the balance).
- That misreads the design: toolsets, tools and guidance are declared with decorator annotations, practices extend the one `PracticeGuidance` base, and code built on the framework registers with it instead of being imported by it.
- Adding abstract classes or protocols to raise this number would add interfaces with one implementation and no second user. So it is reported for information only. The coupling numbers in strategies 4 and 5 track the real risk, a change to a widely used folder reaching its users.

### Expected result

Strategies 1–3 and 6 reach most targets on their own, in about two fix rounds:
- the most complex class
- functions with more than 10 and more than 20 paths
- hard-to-read functions
- the duplicate counts

Strategies 4, 5 and 7 bring the module length, coupling and parameter counts to their targets.

The code would then be "good" on every measure. "Great" needs the class limits halved again (total complexity about 50, methods about 20) and the unrelated-jobs share under 20%. That means continuing the same split-into-held-parts work across the next hundred or so classes.
