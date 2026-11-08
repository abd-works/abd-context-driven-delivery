# Round 5: practices-ce-bdd (Clean Engineering, BDD, agent BDD)

Area: `cdd_guidance/practices/clean_engineering`, `cdd_guidance/practices/bdd`, `cdd_guidance/practices/agent_bdd`, without `_examples`. Branch `ensure-domain-orientation-refactor` at d71e0b20. Judged against `validate-brief.md`, `validate-brief-round4.md`, `validate-brief-round5.md` and `.sessions/ensure-domain-orientation-refactor/refactor-guardrails.md`. Nothing was edited.

## The graph-rule check did not run

The CDD MCP host failed during this round (other round-5 agents were calling validate at the same time):

- `validate_validate(guidance="clean-engineering-modules", graph=true, paths=[.../clean_engineering, .../bdd, .../agent_bdd])` returned: `MCP server "plugin:cdd:cdd" connection closed before the tool call was answered.`
- `cdd_ping` then returned: `MCP server "plugin:cdd:cdd" is not connected`.
- After the host reconnected, a smaller call (bdd and agent_bdd only) twice answered "still running after 10 seconds", and the third identical call returned `not connected`. Two more retries returned `not connected`.
- No report for these paths was written to `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\validation-reports\`. Several zero-byte `clean-engineering-modules-20261108T01*.md` files are there, left by aborted runs.

Following the MCP fail-loud rule, validate was not run any other way. **Every finding below was found by the AI cross-file check, not by a graph rule.** The modules, model and code guidance with `graph=true` still need to run on this area once the host stays up. With no graph output, the scanner false-positive list at the end is empty.

An import graph of the area was built from the syntax tree (top-level, function-level and `TYPE_CHECKING` imports) to check concern 7.

## Findings, most severe first

Columns: location, concern (1–12), check, status (new / left from the review = in `repo-review/practices.md` and still true / known skip = in `pending-skipped-reshaping.md`), fix, severity.

### High

| # | Location | Concern | Check | Status | Finding | Fix | Sev |
|---|---|---|---|---|---|---|---|
| H1 | clean_engineering/model/base_class_model.py:657 `described_members`; operation.py:323 and property.py:185 `model_member`; model/graph_reading.py:199-203; bdd/model/graph_bdd_model.py:105-107, :238-242 | 2, 5 | AI | left (practices.md CE #29, BDD #61) | The format adapters do not share one domain model here. The Clean Engineering model documents are flattened into a `model_members` dict (`Class.member` → `{kind, interactions, model_parameters, model_returns, model_file}`) and stored as a fact on the practice root. `GraphBddModel` follows interactions through that dict, not through the parsed `Operation`/`Property` objects. Operation now exists three times: as the object, as the code node's `parameters` fact (graph_reading.py:174), and as `model_parameters` in the dict. graph_bdd_model.py:241 has to read both key names. | Keep the parsed `CleanEngineeringModel` objects on the practice. `GraphBddModel` asks the Clean Engineering practice for the member and reads `operation.callees`, `parameters` and `return_type`. Delete `model_member`, `described_members` and the `model_members` fact. | high |
| H2 | clean_engineering/model/drawio/rules/__init__.py:33-40; model/graph_reading.py:15, :42 | 3, 5 | AI | new | `_DrawioScannerRule` runs only on graph nodes whose `source.file` ends with `.drawio`. Clean Engineering's graph reading reads only `CODE_SUFFIXES` files and `*-model.md` documents, and I found no production reader that adds a node from a draw.io file. So the ten draw.io layout rules are registered in `own_graph_checks` but never fire in a validate run. `drawio_rules_spec.py:55,84` reaches them only through `Node(...)` stand-ins with a hand-written `.drawio` source. | Have the practice read `.drawio` files with its `drawio` format adapter (`format_for`) into graph nodes, or drop the graph registration and keep the rules on `Drawio.scan`. | high |
| H3 | clean_engineering/model/base_class_model.py:18-19, :308, :316 ↔ operation.py:21, property.py:8 | 7 | AI (import graph) | new | Import cycle. `operation.py` and `property.py` import `base_class_model` at module level, and `base_class_model` imports `Operation` and `Property` back inside `load_property` and `load_operation` (and under `TYPE_CHECKING`). | Move `OoadNode` into its own module, or put `load_property` and `load_operation` on the classes that own them, so the base module never imports its children. | high |
| H4 | clean_engineering/model/base_class_model.py:131-134; bdd/model/bdd_model.py:25-28; bdd/model/nodes.py:69-72 ↔ clean_engineering.py:5-14, bdd.py:40-48 | 7, 2 | AI (import graph) | new | Model to practice cycle. Each node's `practice_kind()` imports its practice class (`CleanEngineering`, `Bdd`), and the practice imports its adapters, or names them by module-path strings in `formats` (bdd.py:40-48), to avoid the cycle. `sketch_bdd_model.py:7` and `graph_bdd_model.py:15,17` import `Bdd` and `CleanEngineering` at module level. The link is also declared in both directions: the practice lists its node types as strings (`node_types`, `anchor_types`, `class_types`), and each node names its practice. | Have the practice register its node classes (it already declares the set), and have `ModelNode` look the practice up from that registration. Then delete `practice_kind`, and make Bdd's `formats` class references like Clean Engineering's. | high |

### Medium

| # | Location | Concern | Check | Status | Finding | Fix | Sev |
|---|---|---|---|---|---|---|---|
| M1 | Brace matching, 6 copies: clean_engineering/model/c_family_parse.py:252 `_closing_brace_index` and :373 `_brace_body`; operation_metrics.py:244 `SourceText._brace_body`; bdd/model/code_spec_model.py:369 `TypeScriptBddModel._matching`; outside the area, stories/model/brace_story_reader.py:43 `BraceCall._matching` (word for word the same as BDD's) and stories/model/code_story_model.py:186 `balanced` | 1 | AI | new | One job ("index of the bracket that closes this one") is written six times. | Give `SourceText` (or `CodeLanguage`) one `closing_bracket(open_at, opener, closer)` and call it everywhere. | medium |
| M2 | bdd/model/code_spec_model.py:307-325 (`_block` returns a dict: span, inner, lines, children) and stories/model/brace_story_reader.py:25-44 `BraceCall` | 2 | AI | new | One concept, a callback call such as `describe(...)`/`story(...)` with its paren, arrow, brace and end, is modelled twice: a dict in BDD and a class in Stories. The TypeScript describe-tree reading duplicates the Stories brace reader. | Move `BraceCall` to the Clean Engineering code model beside `WrittenBlock`; `TypeScriptBddModel` and `BraceStoryReader` both use it. | medium |
| M3 | File-suffix lists: clean_engineering/model/graph_reading.py:15 `CODE_SUFFIXES`; bdd/model/graph_reading.py:17 `_CODE_SUFFIXES`; bdd/model/spec_source.py:8 `_SPEC_SUFFIXES`; clean_engineering/rules/rule_examples.py:16 `_SUFFIX`; harness/graph/graph.py:32 `_FILE_LANGUAGES`; plus each adapter's `suffixes` | 2 | AI | new | At least five lists of "which suffix belongs to which language", and they disagree. Clean Engineering formats include Java (`JavaCleanEngineeringModel.suffixes = (".java",)`), but `CODE_SUFFIXES` leaves `.java` out, so the graph never reads Java code. `_SPEC_SUFFIXES` accepts `.mjs` and `.java`, which no BDD adapter reads. | Derive the files to read from the practice's `formats` (`adapter.suffixes`), the one table `format_for` already uses, and delete the other lists. | medium |
| M4 | bdd/model/graph_bdd_model.py:50-77 (`_read_spec`, `_add_block`, `_add_observation`); bdd_model.py:227-240 `_SketchReader._read_block`; code_spec_model.py:382-393 `_behavior_node` | 1, 5 | AI | new | The describe tree is built by three separate routines. `GraphBddModel` also works out nesting again from line spans, though `bdd/model/graph_reading.py:56` recorded `descriptions`/`contexts`/`observations` edges for it. | Read the tree by following the edges the graph holds. Give `Description`/`Context` one `add_child(kind, name)` that all three readers call. | medium |
| M5 | Finding a practice in the graph, three ways: bdd/bdd.py:175-181 `clean_engineering_practice` and agent_bdd/agent_bdd.py:25-29 `bdd` (`next(isinstance …)`); bdd/model/graph_bdd_model.py:36-37 `graph.practice_of(Bdd)`; bdd/rules/rule_examples.py:28 and clean_engineering/rules/rule_examples.py:40 `graph.practice("bdd")` by name | 1, 5, 10 | AI | new / known skip (name lookups) | Same job written three ways, one of them a lookup by name string. | Use `graph.practice_of(cls)` everywhere; spec support gets the practice from the `Graph` it loaded. | medium |
| M6 | clean_engineering/model/base_class_model.py:519-559, :693-721 (`load(path)`, `load_content`, `has_more_module`, `get_next_module_from_file`, `load_next_module`, `load_classes`, `get_next_class_from_file`, `load_properties`, `load_operations`, `load_relationships`, `has_more_property`) and the Markdown overrides (markdown_class_model.py:371, :446-457) | 1, 3 | AI | left (practices.md adapters, "every format model … two entry points") | A second way to read a model, a file-iterator `load(path)` protocol beside `parse(text)`. Its only callers are `drawio_class_model_round_trip_spec.py:95` and `ddd_channel.feature.py:77-88`. | Delete the iterator protocol; specs call `parse(path.read_text())`. | medium |
| M7 | clean_engineering/model/sketch/sketch_class_model.py:24 `_LENS = SketchLens(("ce:", …))` and clean_engineering.py:23 `sketch_titles = SketchCleanEngineeringModel.lens.titles` vs harness/guidance/guidance.py:286 (builds `CleanEngineering.sketch_lens` from those titles); bdd/model/sketch/sketch_bdd_model.py:14 `lens = Bdd.sketch_lens` | 2, 10 | AI | new | Clean Engineering has two `SketchLens` objects for one sketch section: its adapter's `_LENS` and the practice's `sketch_lens`. BDD goes the other way: the adapter reads the practice's lens. | Follow BDD: titles on the practice, and the adapter reads `CleanEngineering.sketch_lens`. Delete `_LENS`. | medium |
| M8 | Geometry, twice: clean_engineering/model/drawio/drawio_page.py:14-16 `Box`/`Point`, :181 `box_center`, :196 `segments_cross`, :213 `_turns_left`; model/diagram/geometry.py `Geometry.center`; model/diagram/class_layout.py:663 `_lines_cross`, :668 `_turn` | 1, 2 | AI | new | The layout writer and the layout scanners use different shapes for a box (a `Box` tuple and the `Geometry` named tuple) and their own segment-crossing tests. | One `Geometry` (with `center` and `crosses`) shared by `DrawioPage` and `ArrowRouter`. | medium |
| M9 | UML member-line parsing, three copies: drawio/drawio_class_model.py:863 `_card_operation` and :856 `_card_property`; sketch/sketch_class_model.py:37-38 `_UML_OP`/`_UML_PROP` with `_add_uml_member`; markdown_class_model.py:300, :339; title reading twice: drawio_page.py:122 `class_name_in` and drawio_class_model.py:834 `_class_card_members` | 1 | AI | new | The same `+ name(args): Type` line is read three ways. Draw.io splits parameters on `,` and so breaks generics such as `Map<K, V>`, while Sketch uses `split_top_level`. | One `Operation.from_signature(text)` and `Property.from_signature(text)` on the domain classes; `_class_card_members` uses `class_name_in`. | medium |
| M10 | clean_engineering/model/graph_reading.py:150-158 (getter becomes a `Property` node through `add_named` with `_GETTER_MEASURES` copied as facts), :174 (`parameters` list fact beside `Parameter` nodes), :233 `_merge_fact`, :311 `_properties_of` | 2, 5 | AI | left in part (practices.md CE #26) | The graph reading copies parts of the parsed objects into facts and computes a class's properties in a free function that takes the class. | `OoadClass.public_properties` (fields and getters); the getter's `Operation` is the node; parameters come from `hasParameter` edges. | medium |
| M11 | bdd/model/graph_reading.py:21-56 `read_specs(practice)`, `_add_spec(practice, …)` vs clean_engineering/model/graph_reading.py:21 `GraphReading` mixin | 5, 10 | AI | new | The same job, reading the working copy into the graph, has two shapes: Clean Engineering mixes in a class, BDD hands itself to free functions in another file. | Make BDD's reading methods on `Bdd`, or a mixin like Clean Engineering's. | medium |
| M12 | bdd/model/graph_reading.py:79, :88 `node.source.file.endswith(".py")` | 5 | AI | new | `ObservationLinks` picks the language by file suffix, a second switch beside `format_for`. | Ask the node (or `graph` language of file) once. | medium |
| M13 | clean_engineering/model/drawio/drawio.py:43-50 | 5 | AI | new | `Drawio.practice` builds a new `CleanEngineering()` when no practice composed it, so a toolset made on its own reads sources through a practice that belongs to no session and runs at the default fidelity. | The installer or MCP host hands `Drawio` its practice, or `Drawio` is reached only through `CleanEngineering.drawio`. | medium |
| M14 | agent_bdd/agent_cli_bdd.py:44 `ToolsRunYaml()`, :276 `CursorCli().launcher`; agent_bdd_common.py:312 `CursorCli().create_chat`, :545 `Sessions(project).named(name)`, :240 `YamlFence()` per call, :661 `response_to_dict(response)` | 5 | AI | left (practices.md agent BDD #68, #73, #82) | Parts rebuilt on every call; `response_to_dict` is the owner's data handed to a free function. | `RunResponse.as_record()`; one `CursorCli` held by `AgentSession`; `ToolsRunYaml` passed to `_StreamBuckets` by the block. | medium |
| M15 | clean_engineering/model/drawio/drawio_class_model.py:275 `_mark_relationship_kind(oclass, …)`, :179 `_add_module_dependencies(model, …)`; sketch/sketch_class_model.py:164-418 (`_modules_in`, `_add_classes`, `_merge_class`, `_classes_in`, `_operation_from` …) | 5 | AI | left (practices.md CE #36/#44, Sketch adapter) | Parsing and relationship logic sit in module functions that take the model, class or property as a parameter. | `Property.take_relationship(kind)`; `SketchModule` and `SketchOoadClass` read their own lines. | medium |
| M16 | clean_engineering/rules/rule_examples.py, bdd/rules/rule_examples.py (and ddd, stories) | 1, 6 | AI | new | Four copies of `X_rule_by_slug`, `violations_for_…` and the fault/clean pair assertion. bdd/rules/rule_examples.py:29 also writes `practice._temp_dir` on another object. | One spec helper in harness/graph (rule plus fixture tree gives hits) that each practice calls with its `BY_SLUG`. | medium |
| M17 | Every format's `render(canonical, previous)`: bdd_model.py:75, code_spec_model.py:48, code_class_model.py:189, sketch_class_model.py:103, json_class_model.py:148 (no `previous`), markdown_class_model.py:645, drawio_class_model.py:142 | 5 | AI | known skip (`PracticeGuidance` render convention, owned by harness/guidance) | The Clean Engineering adapters now `translate_from` the canonical model into themselves, which is the right shape. BDD's `render` still writes a model it is handed, and the signatures disagree. | Do it when the harness convention changes: `render(previous)` on the held model. | medium |

### Low

| # | Location | Concern | Check | Status | Finding | Fix | Sev |
|---|---|---|---|---|---|---|---|
| L1 | clean_engineering/model/python/python_class_model.py:40-50 | 1, 11 | AI | new | `python_type` is defined twice, word for word (an edit or merge leftover), and `Function = …` is glued onto the end of the first copy. | Delete one. | low |
| L2 | bdd/model/nodes.py:81-84, :110-163 (`clone`, `take_code_from` on `Description`, `Context`, `Observation`) | 3 | AI | new (its caller `_copy_descriptions_on_graph` was removed) | No caller anywhere, specs included. | Delete. | low |
| L3 | bdd/model/bdd_model.py:139 `MarkdownBddModel(BddModel): pass` | 2, 10 | AI | new | The `markdown` format is another name for the sketch tree, with no behaviour of its own. | Drop the format, or give it a markdown spelling. | low |
| L4 | bdd/model/spec_source.py:9 `_SIGNATURE_MARKERS` vs code_spec_model.py:14 `_SIGNATURE` and `marker_line` | 1 | AI | new | Two definitions of the signature marker. | `has_signature_marker` asks each `CodeLanguage.comment(_SIGNATURE)`. | low |
| L5 | agent_bdd/yaml_fence.py:55 `load_fenced` | 3, 7 | AI | new | A free-function wrapper used only by harness/agent_tools/agent_tools_spec.py:45, which makes a harness spec import cdd_guidance. | Delete the wrapper; the spec uses its own fence helper. | low |
| L6 | clean_engineering/model/diagram/geometry.py:1 "Shared by Draw.io and Miro"; clean_engineering/model/miro/ (untracked `__pycache__` only) | 11 | AI | left (practices.md, `model/miro`) | Stale mentions of the deleted Miro format. | Fix the docstring; delete the folder. | low |
| L7 | clean_engineering/rules/multi_language_examples.py | 3 | AI | new | Fixture data used only by `ce_rules_spec.py`, kept among the production rules. | Move it beside the spec. | low |
| L8 | clean_engineering/model/drawio/drawio.py:37 `source_format = "markdown"`, clean_engineering.py:80 `model_in(format: str, …)` | 5 | AI | known skip (Format as a Format object) | Format passed as a string. | With the Format follow-up. | low |

## Fixed since the review (checked, now right)

- `format_for(file)` replaces the suffix switches `_language_model` and BDD `_add_spec` (practices.md CE #27, BDD #42).
- The code channels subclass the parts (`CodeClass`, `CodeOperation`, `CodeProperty`, and the Python, TypeScript, Java and JavaScript subclasses) and spell their own lines. `render` translates the canonical model into itself once.
- `Drawio` holds one `DrawIOCleanEngineeringModel`, and its own parser table is gone. `DrawioPage` is now shared by the reader and the scanners. `DrawioScanner.discover` is a class method. `_DrawioScannerRule` scans each file once.
- `ClassGraph` is built once per context (`context.index(ClassGraph)`).
- `AgentBdd` generates the session's own `Bdd`. `AgentSpecManifest`, `UpdateReport`, `ModelDescriptions`, `CodeLanguage.named` and `DiagramCard` are deleted.

## Counts

| Concern | High | Medium | Low |
|---|---|---|---|
| 1 duplicated functionality | | 5 (M1, M4, M6, M8, M9, M16 share) | 2 |
| 2 duplicated shapes | 2 (H1, H4) | 5 | 1 |
| 3 no use | 1 (H2) | 1 | 4 |
| 5 wrong-shape relationships | 1 (H2) | 9 | 1 |
| 7 dependency direction / cycles | 2 (H3, H4) | | 1 |
| 10 inconsistent names | | 3 | 1 |
| 11 legacy | | | 2 |

Totals: 4 high, 17 medium, 8 low (29). By check: all AI, because the graph check could not run. By status: 18 new, 7 left from the review, 4 known skip or partly known.

## Scanner false positives

None recorded: the graph scanners did not run on this area this round (see the top of this file).

## Graph check (run after the round)

Run one call at a time after the round: `clean-engineering-modules` with `graph: true` on `cdd_guidance/practices/clean_engineering`, `cdd_guidance/practices/bdd` and `cdd_guidance/practices/agent_bdd`. Report: `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\validation-reports\clean-engineering-modules-20261108T021727.md` (with its `.json`), 1289 graph hits.

`clean-engineering-model` and `clean-engineering-code` were not run. The graph section covers the whole Clean Engineering practice whichever fidelity is named: the space-tools modules and model runs returned the same 285 hits rule for rule.

### Hit counts per cross-file rule

| Rule | Hits | Confirmed |
|---|---|---|
| `one-way-deps` | 48 | 3 pairs (about 25 hits) |
| `low-coupling` | 0 | – |
| `deep-module` | 0 | – |
| `eliminate-duplication` | 0 | – |
| `missing-module-context` | 0 | – |
| `no-module-per-class` | 8 | 0 |
| `use-consistent-naming` | 1 | 0 |
| `public-seam-only` | 2 | 0 |
| `modules-not-model-blocks`, `language-modules-one-section` | 1 each | 0 |
| `do-not-invent-parallel-object-models` | 0 (AI-only rule) | – |
| `use-explicit-dependencies` | 18 | 3 |

The rest are per-file code rules (`state-change-returns-record-or-named-failure` 364, `limit-operation-parameters` 243, and so on). They are outside this round's cross-file scope.

### Findings now marked both

- **H4 (cycle between a model and its practice): both.** `one-way-deps` reports these pairs, and each has a production edge both ways:
  - `model` ↔ `clean_engineering`: `model/base_class_model.py:132` imports `CleanEngineering`.
  - `drawio` ↔ `clean_engineering`: `model/drawio/drawio.py:22`, `:47` import it, and `clean_engineering.py:5-6` imports `Drawio`.
  - `bdd` ↔ `model`: `bdd/model/graph_bdd_model.py:15`, `sketch/sketch_bdd_model.py:6`, `bdd_model.py:26`, `nodes.py:70` and `graph_reading.py:14` import `Bdd`.
- **H3 (base_class_model ↔ operation/property): AI only.** It is a cycle between files inside one folder, which the graph does not measure.
- **M13 (`Drawio.practice` builds `CleanEngineering()`): both.** It is one of the `drawio` ↔ `clean_engineering` cycle's edges.
- **M14 (agent BDD builds its helpers per call): both.** `use-explicit-dependencies` hit `ToolsRunYaml` building `YamlFence` (agent_bdd_common.py), `AgentBlock` building `YamlFence` (agent_block.py), and `_StreamBuckets` building `ToolsRunYaml` (agent_cli_bdd.py).

### Confirmed new findings

None beyond the above.

### Dismissed hits and scanner false positives

- **`one-way-deps`, the remaining hits** (`bdd` ↔ `clean_engineering`, `agent_bdd` ↔ `bdd` / `guidance` / `agent_tools` / `installation` / `mcp` / `markdown` / `generate` / `validate`, `clean_engineering` ↔ `satisfy` / `sketch` / `session`, and every pair through `agent_tools`, `installation` and `mcp`). These are false positives.
  - Clean Engineering imports nothing from `bdd` or `agent_bdd`, and `bdd` imports nothing from `agent_bdd`.
  - `harness/` imports nothing from `cdd_guidance/` in production.
  - The edge back comes from specs and `_examples`.
  - Scanner: `cdd_guidance/practices/clean_engineering/model/graph_reading.py:52` and `rules/practice_wide_rules.py:30`. They put every pair in one strongly connected component of 48 modules, so the three real pairs above are hard to see among the others.
  - The real `agent_bdd` → `space.session` edge (`agent_bdd_common.py:545`) belongs to the cycle between areas that `round5-space-tools.md` #2 names.
- **`no-module-per-class` (8), `use-consistent-naming` (1), `modules-not-model-blocks` (1), `language-modules-one-section` (1), and `public-seam-only` on `_examples/public-seam-only/faulty`.** All of these are in `clean_engineering/model/python/_examples/`. The `faulty` hits are intended. The `repaired` hits (`language-modules-one-section/repaired`, `missing-module-context/repaired`, `modules-not-model-blocks/repaired`, `public-seam-only/repaired`) are scanner false positives: a repaired example should pass. Scanner: `harness/graph/skipped_folders.py:11-34` does not skip `_examples`, and `rules/module_naming_rules.py:52` counts a one-file example folder.
- **`public-seam-only` on `cdd_guidance/practices/clean_engineering/model`** ("mixes internal design into the public seam"). This is a false positive. `model/base_class_model.py:41-48` (`_internal_design_in`) searches the raw text of every `.py` file in the folder, specs included, for `## Internal` or `_ holds `. Line 46 of `base_class_model.py` holds that string literal itself, so the scanner flags its own source.
- **`use-explicit-dependencies`, 15 dismissed:**
  - Owned parts or values built from the object's own fields: `ModelChildren`, `CodeBody`, `CallGraph`, `Geometry`, `SourceText` on BddModel, BehaviorNode, Description, Context, Observation, OoadClass, Module, CleanEngineeringModel, DiagramNode, DiagramClass, DiagramModule and Operation.
  - `Drawio` building its `DrawIOCleanEngineeringModel`, the toolset's own model.
  - `DrawioScanner` building a `Path`. Scanner: `model/rules_shared/operation_checks.py:97-104`.
  - `_examples/use-explicit-dependencies/faulty` `Cart`, an intended fault.
