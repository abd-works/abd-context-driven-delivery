# Round 6: practices-ce-bdd (Clean Engineering, BDD, agent BDD, and the graph rule scanners)

Area: `cdd_guidance/practices/clean_engineering`, `cdd_guidance/practices/bdd` and `cdd_guidance/practices/agent_bdd`, without `_examples`, plus the graph rule scanners (`clean_engineering/rules`, `clean_engineering/model/rules_shared`, `clean_engineering/model/production_code.py`, `harness/graph/skipped_folders.py`). Worktree `ensure-domain-orientation-refactor` at b91a73eb; the CDD MCP host serves 8a91c49f, which has the same code. Judged against `validate-brief.md`, `validate-brief-round5.md` and `validate-brief-round6.md`. No code was edited.

Each round-5 finding in `round5-practices-ce-bdd.md` and each item of the "Scanner defects" section of `round5-report.md` was checked against the code. The fix commits for this area are 9cda3343 (CE/BDD) and c0c7f1c8 (scanners).

## The graph check

**One call ran.** `validate(guidance="clean-engineering-modules", graph=true, paths=[.../clean_engineering, .../bdd, .../agent_bdd])` answered "still running" once, then returned the report: `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\validation-reports\clean-engineering-modules-20261108T081310.md` (with its `.json`), **270 graph hits** (1289 in round 5). The judgment of the cross-file hits is appended to that report.

**The second call failed.** `validate(guidance="clean-engineering-code", graph=true, same paths)` first answered "still running". The next identical call returned `MCP server "plugin:cdd:cdd" is not connected`, and the client then reported `ECONNREFUSED`. Aborted runs left 0-byte reports: `clean-engineering-code-20261108T081711.md`, `clean-engineering-code-20261108T081743.md` and `clean-engineering-modules-20261108T081631.md` (the last is the Stories/UX/DDD agent's). Following `.claude/rules/mcp-fail-loud.md`, I made no more graph calls and did not run validate any other way. `cdd_ping` answered `pong` again at the end of the round. The modules run already reports every Clean Engineering graph rule, code rules included (its `.json` holds hits for `keep-operations-small-focused`, `limit-operation-parameters` and so on), so the missing code run loses only its AI prompt text, not graph hits. This is the B10 symptom: one graph build at a time no longer crashes the host on its own, but two agents' builds back to back still take the port down.

### Hit counts per cross-file rule

| rule | hits | confirmed | dismissed |
|---|---|---|---|
| `one-way-deps` | 7 | 2 (N3, N7) | 5 |
| `deep-module` | 1 | 1 (N4) | 0 |
| `shape-classes-around-resources` | 1 | 1 (N5) | 0 |
| `no-module-per-class` | 1 | 0 | 1 |
| `use-explicit-dependencies` | 12 | 0 | 12 |
| `source-parses` | 4 | 0 | 4 |
| `eliminate-duplication`, `low-coupling`, `missing-module-context`, `use-consistent-naming`, `public-seam-only` | 0 | – | – |

The other 244 hits are per-file code rules (`keep-operations-small-focused` 51, `limit-operation-parameters` 44, `use-typed-signatures` 43, …), outside this round's cross-file scope. 26 of them are on spec files; 12 of those are on `class_channel.feature.py` (scanner issue S2).

**The 6-module cycle.** `one-way-deps` puts `model`, `drawio`, `markdown`, `typescript`, `diagram` and `scanners` (all under `clean_engineering/model`) into one cycle. Read edge by edge:
- `model` → `drawio` and `model` → `typescript` come only from `model/class_channel.feature.py:20-22`, a mamba spec the scanner reads as production (S2). Dismissed.
- `drawio` → `model`, `drawio` → `markdown` and `drawio` → `diagram` are real one-way imports; they close a loop only through that spec. Dismissed.
- `model` → `markdown` is real: `model/graph_reading.py:22` imports `MarkdownCleanEngineeringModel`, and `markdown_class_model.py` imports `base_class_model`. Confirmed (N3).
- `drawio` → `scanners` is real: `drawio/drawio.py:15` imports `scanners/_drawio_base`, and eleven scanners import `drawio/drawio_page.py`. Confirmed (N7).
- Both confirmed loops run between a module's own folder and a package inside it (`markdown` and `scanners` have no module card), and neither is a cycle between files. So I grade them medium and low, not high.
- No file cycle was reported, and the folder `model` no longer cycles with `clean_engineering` (round 5 H3 and H4 are gone).

## Findings, most severe first

| # | file:line | concern | check | status | finding | fix (one line) | severity |
|---|---|---|---|---|---|---|---|
| N1 | `clean_engineering/model/graph_reading.py:212-214`, `:217-224` | 5 | AI | new | A getter's property node takes its type from its own name, capitalised (`hint = prop.name[:1].upper() + prop.name[1:]`), not from the getter's `return_type`. So `clean_engineering_practice -> CleanEngineering` (`bdd/model/graph_reading.py:44`) gets no `hasType`/`dependsOn` edge, and a getter that happens to share a class's name gets one whatever it returns. The coupling and class-graph rules read those edges, so they undercount without saying so. | Use `prop.return_type` for a getter, as `_operation` does for `returns`. | high |
| M10 | `clean_engineering/model/graph_reading.py:213` `prop.type = "Property"`, `:230` `node.set_fact("parameters", …)`; read by `model/rules_shared/operation_checks.py:306` | 2, 5 | AI | left (partly) | `public_properties` now lives on `OoadClass` and `_GETTER_MEASURES` is gone. But the reader still rewrites a getter `Operation`'s node type to `Property`, so one object stands as both kinds, and it still copies each operation's parameters into a `parameters` fact beside the `Parameter` nodes it links with `hasParameter`. | Let a getter `Operation` say it is read as a property; rules read parameters through `hasParameter`; delete the fact. | medium |
| N2 | `clean_engineering/model/production_code.py:18-19, 22` `is_test_code`; `bdd/model/spec_source.py:13-20` `is_spec_file`; `bdd/model/graph_reading.py:73-75` `_is_test_support` | 1 | both | new | Three definitions of "this is a spec or test support", and they disagree: only BDD knows `.e2e.`, `test-utils` and `page-driver`; only Clean Engineering knows `fixtures` and `test_*.py`; none knows `*.feature.py`. The `.feature.py` gap is scanner issue S2. | One `is_test_code` that both practices call, with `.feature.py` and the BDD names added. | medium |
| N3 | `clean_engineering/model/graph_reading.py:22`, `:292` | 7, 5 | both | new | `GraphReading._read_model_documents` imports the markdown format and builds a new `MarkdownCleanEngineeringModel()` for every model document, instead of using the practice's own `markdown` format (the one `CleanEngineering.drawio` already gets through `_live_adapter("markdown")`). That import is the real edge of the `model` ↔ `model/markdown` loop. | Read model documents with `self.format_for(file)` or the practice's held markdown adapter; drop the import. | medium |
| N4 | `clean_engineering/model/rules_shared/*.py`; `clean_engineering/rules/__init__.py:3-13` | 6 | graph | new scope | `deep-module`: `model` shows 44 of its 109 classes to other modules. Fourteen are rule classes (`HideInnerDetails`, `LimitComments`, `UseTypedSignatures`, `PutLogicOnOwningResource`, …) that live in `model/rules_shared` but belong to the practice's `rules` package, which imports them to build `BY_SLUG`. The practice's rules have two homes, and the model module's seam carries one of them. | Move `rules_shared` under `clean_engineering/rules`; the model keeps only the measures the rules read. | medium |
| N5 | `bdd/model/code_spec_model.py:308-345` (`_tree`, `_child_blocks`, `_node`) and `:355-364` `DescribeCall` | 5 | graph | new | `shape-classes-around-resources`: `TypeScriptBddModel` nests the `DescribeCall`s (`_tree`), maps their kind to describe/context/it, and slices their lines, while `DescribeCall` only holds the numbers. | `DescribeCall.adopt(child)` and `DescribeCall.behavior_kind(parent)`; the model asks the call. | medium |
| N6 | `clean_engineering/model/module_context_files.py:40-70`; `base_class_model.py:501-517` (`_IS_A`, `_CHILD_PARENT`, `_internal_design_in`), `:56-66` `_documentation_in`; `graph_reading.py:88-107`, `:120-141` | 9, 5 | AI | new | The module card is read by `ModuleContext`, which reads the file again in each of its five questions, and is interpreted by `Module.load_folder_facts`, which applies its own card patterns (`*is a type of*`, `Child : Parent`). Each `.py` file is read and `ast.parse`d by `_parsed_modules`, again by `_documentation_in`, and read once more by `_read_unparsed` when a scope is set. | `ModuleContext` reads its card once and answers every card question; `Module` gets its documentation from the parsed module it already holds. | medium |
| M17 | `bdd/model/bdd_model.py:74`, `clean_engineering/model/drawio/drawio_class_model.py:135`, `json/json_class_model.py:148`, `markdown/markdown_class_model.py:605`, `sketch/sketch_class_model.py:265`, `code_class_model.py:189` | 5 | AI | left (known skip) | The `render` signatures still disagree: `(canonical, previous)`, `(canonical)`, `(canonical=None)`. The harness `PracticeGuidance` render convention owns this. | With the harness render convention: `render(previous)` on the held model. | medium |
| M3 | `harness/graph/graph.py:34` `_FILE_LANGUAGES`; `clean_engineering/model/code_body.py:325` `SOURCE_SUFFIXES` vs `PracticeGuidance.readable_suffixes` | 2 | AI | left (partly) | Fixed for both practices' reading: they read `readable_suffixes`, made from their formats, and the Java gap is closed. Two tables remain: the graph's `_FILE_LANGUAGES` (no `.java`, so a Java node's `file_language` is `graph` and BDD's `_is_python` treats it as script), and `SOURCE_SUFFIXES`, which `Module.load_folder_facts` (`base_class_model.py:505`) counts files by. | The practice tells each node its language when it adds it; `load_folder_facts` takes the practice's suffixes. | low |
| M4 | `bdd/model/code_spec_model.py:257`, `:339`, `:367-377` `_behavior_node` | 1 | AI | left (partly) | `GraphBddModel` now follows the graph's edges and calls `DescribeBlock.add_child`, and the sketch reader uses it too. The Python and TypeScript code readers still build and attach nodes through their own `_behavior_node`. | Both code readers call `add_description` / `add_child`; delete `_behavior_node`. | low |
| L8 | `clean_engineering/clean_engineering.py:82` `_live_adapter("markdown")` | 5 | AI | left (known skip) | The two cited sites (`Drawio.source_format`, `model_in(format: str)`) are gone; the practice still reaches its format by a name string. | With the Format follow-up. | low |
| N7 | `clean_engineering/model/drawio/drawio.py:15` ↔ `model/drawio/scanners/*.py` → `drawio/drawio_page.py` | 7 | graph | new | The `drawio` folder and its `scanners` package import each other: the toolset imports `DrawioScanner`, and the scanners import `DrawioPage` from the folder above. No file cycle. | Put `drawio_page.py` and `diagram_node.py` where both read them (e.g. `drawio/page/`), so `scanners` depends one way. | low |
| N8 | `clean_engineering/clean_engineering.py:5`, `:13` | 11 | AI | new | `OoadNode` is imported twice: from its new module and through `base_class_model`, which re-exports it after H3's move. | Delete line 5. | low |
| N9 | `clean_engineering/model/.context/module-context.md` (Dependencies line) | 11 | AI | new | The card still says the model's "per-language rule packages import the practice's rules" and that the model and the practice "depend on each other — the one cycle left". No such packages exist, and the model no longer imports the practice. It also says "about 39 of its 89 classes (43%)"; the scanner counts 44 of 109. | Rewrite the dependency line from the current imports. | low |
| N10 | `clean_engineering/model/c_family_parse.py:291` `_top_level_index` vs `type_refs.py:38` `split_top_level`; `c_family_parse.py:371` `_brace_body` vs `operation_metrics.py:139` `SourceText.braced` | 1 | AI | new | The round-5 brace matching is fixed (one `SourceText.closing_bracket`). Two smaller copies are left: the bracket-depth walk that finds a mark at the top level, and `_brace_body`, which is `braced` after a scan to the next `{`. | One `SourceText.top_level_index(mark)`; `_brace_body` calls `braced`. | low |
| N11 | `clean_engineering/model/sketch/sketch_class_model.py:306` `_property_notes(prop)`, `:311` `_operation_line(operation)` | 5 | AI | new | The sketch reader is now on `SketchModule`/`SketchOoadClass` (M15 fixed), but writing a member's sketch line is still a free function handed the `Property` or `Operation`. The code formats give each part its own `lines()`. | `SketchOperation`/`SketchProperty` (or the sketch class) spell their own line. | low |
| N12 | `bdd/model/graph_bdd_model.py:89-97` `_code_member`, `:100` `_returned` | 5, 1 | AI | new | `_code_member` scans every Operation and Property node for each call it follows, though `ObservationLinks` (`bdd/model/graph_reading.py:88-91`) already builds the same index by owner and name. `_returned(described)` is a free function on the member's own data. | One member index on the Clean Engineering practice's part of the graph; `Operation`/`Property` answer what they return. | low |
| N13 | `agent_bdd/spec_helpers.py:156` `run_skill`, `:194` `expect_ok_tool`, `:207` `expect_tools_exclude`, `:227` `expect_instructions_contain_any`; `bdd/rules/rule_examples.py:24` `violations_for_spec_source`; `clean_engineering/model/call_graph.py:54` `CallGraph.of_callees` (one spec only); tracked runtime logs `agent_bdd/log-action-requests.txt`, `bdd/.context/.agent_bdd_sessions/logs/*` (8 files), `clean_engineering/.context/.agent_bdd_sessions/logs/*` (18 files) | 3 | AI | new | No use: no spec, template or production file calls the five helpers, `of_callees` is reached only by its spec, and the logs are July agent-run output committed into `.context`. | Delete them; ignore `.agent_bdd_sessions/` in git. | low |
| N14 | `clean_engineering/clean_engineering.py:26-27`, `bdd/bdd.py:20-21` | 10 | AI | new | Round 5 M7 is fixed (one `SketchLens`, owned by the sketch format). Each practice still states it twice, `sketch_lens = X.lens` and `sketch_titles = sketch_lens.titles`, because `harness/guidance/guidance.py:296-297` rebuilds the lens from the titles. | The harness reads `sketch_lens` only; practices set one field. | low |
| N15 | `clean_engineering/model/graph_reading.py:38-40` | 5 | AI | new | `_model_documents: dict = {}` is a class attribute, a dict shared by every instance until `_read_model_documents` replaces it. The current order of calls always replaces it first, so nothing breaks today. | Set it in the practice's `__init__`. | low |

### Scanner findings

| # | scanner file:line | status | finding | fix (one line) | severity |
|---|---|---|---|---|---|
| S1 | `harness/graph/skipped_folders.py:16-39` | new (found by the lead) | `catalog-examples` is not skipped, so `cdd_guidance/practices/*/catalog-examples/` is read as production code (54 hits at Stories/UX/DDD). This area has no `catalog-examples`, but `templates/` is not skipped either: `bdd/templates/bdd.py:32` and `clean_engineering/templates/clean_engineering.py:32` are placeholder sources (`from {domain_module} import …`) and give the 4 `source-parses` hits, and `agent_bdd/templates/agent_bdd.py` is judged as production. | Add `catalog-examples` and `templates` to `SKIPPED_FOLDERS`. | medium |
| S2 | `clean_engineering/model/production_code.py:19` `_TEST_FILE` | new | `*.feature.py` is not test code. `model/class_channel.feature.py` is a mamba spec; it gives 12 production-rule hits and 4 of the 7 `one-way-deps` hits (the `model` → `drawio`/`typescript` edges that make the 6-module cycle). The Stories/UX/DDD agent found the same for their two `.feature.py` files. | Match `\.feature\.py$`, through the one `is_test_code` of N2. | medium |
| S3 | `clean_engineering/model/rules_shared/operation_checks.py:118-124`, `class_graph.py:94-99` | left (round 5 dismissed the same 15) | `use-explicit-dependencies` still flags owned parts a class builds from itself or from nothing: `CodeBody`, `ModelChildren`, `CallGraph`, `SourceText` (10 hits), and a toolset's own model (`Drawio` → `DrawIOCleanEngineeringModel`). The value test only accepts standard types or stereotyped value objects. | Accept a type built only from `self` or literals, or stereotype these parts as value objects. | low |
| S4 | `clean_engineering/rules/module_naming_rules.py:64-66` `_holds_modules` | new | `no-module-per-class` flags `bdd`: it counts only child folders with a module card, so a practice folder whose classes sit in its `model/` and `rules/` packages reads as a one-class module. | Count child packages too. | low |
| S5 | `clean_engineering/rules/practice_wide_rules.py:135` | new | The `deep-module` message rounds 44/109 (40.4%) to "40%, max 40%", so a failing hit reads as within the limit. | Print one decimal, or the counts against the allowed count. | low |
| S6 | `use-intention-revealing-names`, `limit-operation-parameters`, `keep-operations-small-focused` | left (partly) | Round 5's "code rules judging specs" is fixed for the four rules named in c0c7f1c8; other production-code rules still judge spec files (14 hits on `*_spec.py` and spec support such as `spec_helpers.py` and `rule_examples.py`). | Decide per rule whether specs are judged, and say so on the rule. | low |

Not repeated from round 5 because they are fixed: spec and `_examples` imports in the cycle scanner, `_examples`/`fixtures` folders scanned, `deep-module` counting fixtures and only in-scope callers, `eliminate-duplication` matching only identical bodies (`near_copies.py` now compares three-token runs; it found no near copy in this area), `use-explicit-dependencies` on `Path`, `prefer-instance-operations` on factories, `use-intention-revealing-names` on setter `value`, module naming counting spec classes, `public-seam-only` matching its own literal, and the repaired `_examples` failing their rule. The TypeScript reader reading `cdd-connection.ts` twice is outside this area's paths and was not rechecked.

Also seen in the saved `.json`, outside this area: the DDD practice reads Clean Engineering code and reports `every-class-carries-ddd-stereotype` on 7 of its classes (for example `CodeOperation` as a value object). DDD's tactical rules should not judge framework code that no bounded context claims.

## Fixed since round 5

- **H1:** `model_member`, `described_members` and the `model_members` fact are gone. `GraphBddModel` asks `CleanEngineering.described_member(owner, name)` and reads the parsed `Operation`/`Property` (`callees`, `parameters`, `return_type`).
- **H2:** the draw.io graph registration (`drawio/rules/__init__.py`, `_DrawioScannerRule`) and its stand-in spec are deleted; the layout rules run through `Drawio.scan`. Only an untracked `__pycache__` is left in `drawio/rules/`.
- **H3:** `OoadNode` is in `model/ooad_node.py`; `operation.py` and `property.py` no longer import `base_class_model`.
- **H4:** each practice registers itself on its model (`OoadNode.register_practice(CleanEngineering)`, `BddModel`/`BehaviorNode.register_practice(Bdd)`), no model file imports its practice, and Bdd's `formats` are class references.
- **M1:** one `SourceText.closing_bracket`; the copies in BDD, Stories and `c_family_parse` call it (two small leftovers are N10).
- **M2:** `BraceCall` is in `code_body.py`; `DescribeCall` and `BraceStoryReader` use it.
- **M5:** practices are found by class: `graph.practice_of(Bdd)`, `graph.loaded(CleanEngineering)`; the spec support gets its practice from its own `Graph`.
- **M6:** the file-iterator `load(path)` protocol is deleted.
- **M7:** one `SketchLens` per practice, owned by its sketch format (a leftover second field is N14).
- **M8:** one `Geometry` with `overlaps`, plus `segments_cross`, shared by `DrawioPage` and the layout writer.
- **M9:** `Operation.from_signature` and `Property.from_signature`; draw.io's card reading uses `class_name_in`.
- **M11:** `BddGraphReading` is a mixin on `Bdd`, like Clean Engineering's `GraphReading`.
- **M12:** `_is_python` asks the node's `file_language`.
- **M13:** `Drawio` no longer builds a `CleanEngineering`; it takes a class model or makes its own markdown model.
- **M14:** `RunResponse.as_record()`; one `YamlFence`, one `ToolsRunYaml` and one `CursorCli` per block, held.
- **M15:** `SketchModule` and `SketchOoadClass` read their own lines; `Property.take_relationship`; draw.io's dependency reading is a method.
- **M16:** `harness/graph/rule_fixture.py` (`RuleFixture`, `RulePair`) is the one rule-check helper; `_temp_dir` is no longer written from outside.
- **L1–L7:** `python_type` once; `clone`/`take_code_from` deleted; the `markdown` format is `BddModel` itself; one `SIGNATURE` marker; `load_fenced` wrapper deleted; Miro mention gone; `multi_language_examples.py` moved to `rules/fixtures/`.

## Counts

This summary table is headed "by concern" so `concern_counts.py` counts only the finding rows above.

| by concern | high | medium | low |
|---|---|---|---|
| 1 duplicated functionality | – | N2 | M4, N10, N12 |
| 2 duplicated shapes | – | M10 | M3 |
| 3 no use | – | – | N13 |
| 5 wrong-shape runtime relationships | N1 | M10, N3, N5, N6, M17 | L8, N11, N12, N15 |
| 6 seams that leak | – | N4 | – |
| 7 dependency direction | – | N3 | N7 |
| 9 one file, several owners | – | N6 | – |
| 10 names | – | – | N14 |
| 11 legacy and stale docs | – | – | N8, N9 |

**20 finding rows** (round 5: 29): 1 high, 7 medium, 12 low. **By status:** 5 left (M3, M4, M10, M17, L8; M17 and L8 are known skips), 14 new, 1 new scope (N4), 0 regressions. 24 round-5 findings are fixed. **By check:** 15 AI only, 5 graph or both (N2, N3, N4, N5, N7). Plus 6 scanner findings (S1–S6: 2 medium, 4 low).

Nothing was found for concerns 4, 8 or 12.

## Goal-class counts

A row counts once in each class it names (N6 and M10 count twice, N12 in two classes).

| goal class | round 5 | round 6 left | round 6 new | round 6 new scope | round 6 total |
|---|---|---|---|---|---|
| bad resource orientation (5 + 9) | 12 (H1, H2, M4, M5, M10, M11, M12, M13, M14, M15, M17, L8) | 3 (M10, M17, L8) | 7 (N1, N3, N5, N6, N11, N12, N15) | 0 | 10 |
| shadow models (2) | 8 (H1, H4, M2, M3, M7, M8, M10, L3) | 2 (M10, M3) | 0 | 0 | 2 |
| duplicated functions (1 + 12) | 9 (M1, M4, M5, M6, M8, M9, M16, L1, L4) | 1 (M4) | 3 (N2, N10, N12) | 0 | 4 |

From 29 class entries to 16. One high (N1) remains in the resource-orientation class. Every left entry is partly fixed; most new entries are small and in code the round-5 fixes touched or wrote (N3, N5, N12, N15).

## What would make this area's next round cheaper

1. **The fix lands at the named site, and its twin elsewhere stays.** `add_child` was made, but the code readers still use `_behavior_node`; `Parameter` nodes are read, but the `parameters` fact stays; the suffix list moved to the formats, but the graph keeps `_FILE_LANGUAGES`; `is_test_code` was made, but BDD keeps `is_spec_file` and `_is_test_support`. A fix brief should say "grep for every other place that does this job and fold it in", with the grep in the commit message.
2. **Scanner fixes are tested on invented fixtures, not on this repository's real file and folder names.** `.feature.py`, `templates/` and `catalog-examples/` all slipped through the round-5 scanner fix. A heavy spec that loads `cdd_guidance/practices` itself and asserts that no hit lands in a spec, template or example file would have caught all three.
