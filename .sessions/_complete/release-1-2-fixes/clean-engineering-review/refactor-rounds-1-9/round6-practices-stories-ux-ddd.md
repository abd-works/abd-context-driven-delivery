# Round 6: practices-stories-ux-ddd

Area: `cdd_guidance/practices/stories`, `cdd_guidance/practices/ux` and `cdd_guidance/practices/ddd`, without `_examples` and `catalog-examples`. Worktree `ensure-domain-orientation-refactor` at b91a73eb; the CDD MCP host is pinned to 8a91c49f, which has the same code. No code was edited.

Each round-5 finding was checked against the code. The fix commits for this area are 799828b5, 9dad5b2e, c6074ccd and 6c5d1a0d.

## The graph check did not finish

The call was `validate` with `clean-engineering-modules` and `graph: true` on the three practice folders. It started at 08:16 UTC, made after another agent's modules run had finished at 08:15.
- The first three answers were "still running".
- On the fourth try the host answered `MCP server "plugin:cdd:cdd" is not connected`. `cdd_ping` gave the same answer, and the client then reported `ECONNREFUSED`.
- The call left an empty report: `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\validation-reports\clean-engineering-modules-20261108T081631.md`, 0 bytes.
- The host process (pid 10400, `~/.cdd/server.json`, port 47800) was still alive, and its memory grew from 387 MB to 499 MB over five minutes. But port 47800 refused every connection from 08:18 to 08:22 UTC: `curl` exited with code 7, eight times.
- So a graph build still takes the whole server down while it runs. This is the B10 symptom the lead recorded in the harness-upper notes, now as a refused port rather than slow pings.

Following `.claude/rules/mcp-fail-loud.md`, I stopped and did not run validate any other way. Because the runtime is shared, I did not restart the host. Every finding below comes from the **AI** check. The two `one-way-deps` cycles carried from round 5 were checked by reading the imports, using the same rule the scanner uses (`python_class_model.py:176` `import_targets`: every `import` anywhere in a file, `if TYPE_CHECKING:` included). A scratch script listed each edge and where it comes from.

## The two `one-way-deps` cycles: neither is a runtime import cycle

**The DDD cycle of 4 modules** is `ddd`, `ddd/model`, `ddd/model/markdown` and `ddd/model/sketch`.
- The forward edges are real: `ddd.py:9-12` imports markdown, sketch and model, `sketch_ddd_model.py` imports markdown and model, and markdown imports model.
- Only two edges point back:
  - `ddd/model` → `ddd`: only `ddd/model/graph_reading.py:20`, inside `if TYPE_CHECKING:`, which names `Ddd` for an annotation.
  - `ddd/model` → `ddd/model/markdown`: only `ddd/model/ddd_channel.feature.py`, a mamba spec that is "not collected with the other specs".
- With those two left out there is no cycle. With only the spec left out, the type-only reference alone still closes a 4-module loop: `ddd` → `sketch` → `markdown` → `model` → `ddd`.
- **Verdict:** no import cycle at run time. What remains is a type-only reference from the model's graph reader back to its practice (row NS1 below).

**The Stories cycle of 11 modules** is `stories`, `stories/model` and its nine format subpackages: drawio, java, javascript, json, markdown, miro, python, sketch and typescript.
- Every edge from `stories/model` down to a format subpackage comes from `stories/model/story_channel.feature.py`, a spec.
- The edges back to `stories` come from the same spec (`:21`) and from `stories/model/graph_reading.py:15`, inside `if TYPE_CHECKING:`.
- With the spec left out the cycle falls to 3 modules: `stories` → `model/sketch` → `model` → `stories`, and that one closes only through the type-only import. With both left out there is no cycle.
- **Verdict:** not real. Most of its size comes from a scanner false positive: `production_code.py:19` does not treat `*.feature.py` as a spec.

**Round 5's M10 is fixed.**
- Each practice now registers itself on its model: `DomainNode.register_practice(Ddd)` (`ddd.py:102`), `StoryNode.register_practice(Stories)` (`stories.py:215`) and `UxNode.register_practice(Ux)` (`ux.py:92`).
- The sketch lens lives on the sketch format: `SketchDddModel.lens` and `SketchStoryModel.lens`.
- No model module imports its practice at run time.
- The remaining cross-practice imports point one way and are lazy: `stories.py:102` imports `Ddd` and `ux/model/story_link.py:55` imports `Stories`.

## Findings, most severe first

| # | file:line | concern | check | status | finding | fix (one line) | severity |
|---|---|---|---|---|---|---|---|
| H1 | `ddd/model/nodes.py:362` `BoundedContextMap`, `:455` `write_classes`, `:468` `read_class_model`, `:499` `_place_of`; `ddd/model/markdown/class_cards.py:90` `ClassCard.from_code`, `:236` `write_into`; `ddd/model/markdown/nodes.py:244-249`, `:269-275` | 2, 5 | AI | left (partly; down from high) | The double copy is gone: `class_model`, `code_class` and `_code_card` are deleted, and the map writes straight into the code or draw.io format's own classes. But `BoundedContextMap` still subclasses nothing, so each render converts every card into a new format class (`load_class` + `update_self`), and each read builds a new card from each class (`from_code` copies its properties and operations). Where a class lives still rides in the first line of its intent (`_PLACE`, read back by `_place_of`). The aggregate's arcs are still appended to the first class's intent after `Integrations:` and cut back out by `take_code_integrations`. That is state written into a string and parsed back. | Make the map a `CleanEngineeringModel` whose aggregates are its modules. Give the class model typed parts for place and arcs, not intent text. | medium |
| M1 | `ddd/model/drawio/drawio_bounded_context_map.py:154-155`; `ddd/model/sketch/sketch_ddd_model.py:276-277`; `ddd/model/markdown/nodes.py:124-161, 432-501` | 2 | AI | left (partly) | Every format now subclasses `BoundedContextMap`, which holds `context_at`, `aggregate_at`, `wire_events` and `has_class_cards`. But draw.io and sketch still read into the markdown node types (`MarkdownBoundedContext`, `MarkdownAggregate`). Those markdown classes also own the sketch notation: `read_sketch_lines`, `sketch_lines`, `load_sketch` and `sketch_fences`. So one node class serves two formats, and markdown's node is the domain model every format reads into. | Give the sketch format its own `SketchBoundedContext`/`SketchAggregate`. Draw.io reads into the base `BoundedContext`/`Aggregate`. | medium |
| M2 | `ddd/model/stereotypes.py:39` `_VALUE_OBJECT_SUFFIXES` vs `:117-130` `_name_says`; `ddd/model/markdown/class_cards.py:33-34, 108-117` (`_ROOT`, `_REPOSITORY`, `is_root`, `is_repository`); `ddd/rules/tactical.py:92`; `ddd/rules/rule_examples.py:27-34` `_kind_of` | 1 | AI | left (partly) | The stereotype→kind table is now one (`KIND_OF_STEREOTYPE`), and `class_types` and the rules read `BUILDING_BLOCK_KINDS`. Still: (a) `_name_says` keeps its own list of value-object suffixes (`Token, Code, Message, Value`), which disagrees with `_VALUE_OBJECT_SUFFIXES` (`Token, Code, Message, Requirement, Requirements, Operation`). (b) The cards test "aggregate root" and "repository" by their own string compares beside `kind_named_by`. (c) The repository rule re-tests `endswith("Repository")`. (d) The rule-examples support decides a kind its own way: `DomainService` from a `Service` suffix, which the graph reading never infers; an unreachable `Repository` branch; and a default of `Entity`. So rule examples check classes that production would classify differently. | One naming convention on `TacticalClass` (suffix lists named once). Cards ask `kind_named_by`. `_kind_of` calls `inferred_kind` only. | medium |
| M3 | `ddd/model/drawio/drawio_bounded_context_map.py:128, 138, 161, 197, 199` | 5 | AI | left | The cell types `DrawIOContextCell` and `DrawIOAggregateCell` now exist for writing. But a module's kind is still written as its `description` text ("bounded context"/"aggregate"). Parsing dispatches on that string through `self._readers` and compares `module.description == DrawIOAggregateCell.PURPOSE`. | Clean Engineering's draw.io reader builds the cell type, and the cell type reads itself back. | medium |
| M4 | `ddd/model/graph_reading.py:39` `BuildingBlock(Node)`, `:200` `TacticalClass(cls)` | 2 | AI | left (was known skip) | It is unchanged since round 5. The graph's building block is a third shape beside `Entity`/`ValueObject`/`Repository` in `nodes.py`: a `Node` wrapping a `TacticalClass` wrapping the `OoadClass`. It merges facts from both (`facts`, `get_fact`). | The graph adds the DDD building-block node as an `OoadClass` subclass that works out its own tactical facts. | medium |
| M7 | `ux/model/json/nodes.py:142` `JsonUxMapReader`, `:131-139` (content types and nav components written by the map); `stories/model/markdown/nodes.py:1075-1120` `_render_story`/`_render_scenario` vs `:215` `MarkdownScenario.lines`; `stories/model/sketch/sketch_story_model.py:126` `_SketchReader` | 5, 1 | AI | left (partly) | Writing is fixed: `JsonStep`, `JsonBackground`, `JsonScenario`, `JsonScreen`, `JsonControl` and `JsonTransition` write their own `as_record`, and Stories' JSON nodes read `from_record`. Reading in UX JSON is still a separate reader class handed the map and the document, and content types and nav components have no JSON node. The markdown story map still writes each story and scenario from the outside, from the parts it kept on them. Beside that, `MarkdownScenario.lines` writes a scenario a second way, and the `Scenario Outline`/`Scenario` heading is spelled twice (`:217`, `:1116`). | `JsonScreen.from_record` and friends. One scenario writer on `MarkdownScenario` that keeps unchanged lines as read. | medium |
| M8 | `stories/model/markdown/links.py:94-97` `StoryMapLinks.from_workspace` vs `stories/model/story_map_files.py:24` `StoryMapFiles` | 1, 9 | AI | left (partly) | `StoryMapFiles` is now the one locator, and `read_folder`, `_maps_beside` and `MarkdownStoryModel.from_workspace` use it. `StoryMapLinks` still walks for the exact name `story-map.md`, with no `.context` folder, no prefix and no `story_map` spelling. So a map found by `StoryMapFiles` in `.context/` gets no links. | `StoryMapLinks` takes `StoryMapFiles(root).nearest()` or `markdown_below()`. | medium |
| M11 | `ddd/ddd.py:72` `self.extended` and `:88` `self.clean_engineering_companion.practice_guidance` | 2 | AI | left (was known skip) | Unchanged. `Ddd` reaches two Clean Engineering practice objects: the graph's (for rules and building blocks) and the fidelity companion's (for parsing a plain class model). | One Clean Engineering practice per session, held by `Ddd`. | medium |
| M13 | `stories/stories.py:130` `Format(source or self.format).is_code` | 5 | AI | left (was known skip) | The format is still rebuilt from a string on every `read_paths` call. | The fidelity holds a `Format`. | medium |
| N1 | `ddd/model/nodes.py:382, 391`; `ddd/model/markdown/nodes.py:566` | 6 | AI | new | The map sets each context's private `_map` from outside the class, so the context can ask it for `aggregate_type`/`bounded_context_type`. | The context takes its map when it is made, or the map hands it the types through a public method. | low |
| N2 | `ddd/model/markdown/nodes.py:609` and `ddd/model/sketch/sketch_ddd_model.py:105` (event map line); `ddd/model/nodes.py:36` `_TYPE_SEPARATORS` and `ddd/model/markdown/nodes.py:286` | 1 | AI | new | Two small near copies. The `- Event: emitted by P; consumed by A, B` line is built in two formats, while `_wire_event` reads it in one place. The type-hint split regex is written twice. | `DomainEvent.map_entry()`, and one regex. | low |
| L4 | `stories/model/story_model.py:1014` `copy_of(self, canonical)`; `ux/model/ux_map.py:81` `copy_of(cls, source)` | 10 | AI | left (partly) | Render's parameter is now `canonical` everywhere. But "copy this model into my format" is an instance method in Stories and a class method in UX, with the parameter named `canonical` and `source`. | One shape and one parameter name. | low |
| L5 | `.context/repo-model.md:2788, 3164, 3178, 3357-3373`; `.context/repo-runtime.md:1821, 1872-1886, 1952-1956`; `.context/repo-model-disconnected.md:86, 267, 278-280` | 11 | AI | left (partly) | The module cards are now right: `ddd-model.md`, `story-model.md` and DDD's `module-context.md`. The repository-wide cards still name `StoriesGraph`, `DddGraph` and `DiagramCard`, and no class of those names exists. | Regenerate or edit the three root cards. | low |
| L7 | `ddd/model/drawio/drawio_bounded_context_map.py:159, 168-171`; `ddd/model/nodes.py:466` | 5 | AI | left | The held `diagram` has its `modules` replaced on every render, and it renders itself as its own argument (`self.diagram.render(self.diagram)`). So the held part works as a renderer, not as the map's drawing. | Settles with H1. | low |
| NS1 | `ddd/model/graph_reading.py:20, 141`; `stories/model/graph_reading.py:15, 36, 87` | 7 | AI (cycle scanner hit, judged) | new scope | The graph readers in each `model/` package name their practice class for annotations (`DddReading(practice: Ddd)`, `StoriesReading(practice: Stories)`, `StoryLinks(stories: Stories)`). It is not a runtime import, but it is the only back edge left in both reported cycles. The model package is typed against the practice above it. | Annotate with `PracticeGuidance`, or move the readers beside `ddd.py` and `stories.py`. | low |

## Fixed since round 5

- **H2:** `ValueObject.create`, `clone` and `mix` are deleted. The building block keeps `OoadClass.clone`.
- **M5:** one discovery-document header. `cdd_guidance/actions/sketch/discovery_document.py` `DiscoveryDocument` is used by both `MarkdownStoryModel._wrap_story_map_document` and `MarkdownBoundedContextMap._wrap_bounded_context_document`.
- **M6:** one `step_line`, which `_StepLines.line` and `step_lines` both call. `MarkdownScenario.lines` uses `example_table_lines`.
- **M9:** `StoryLinks` reads Clean Engineering's operations, modules and examples once (`cached_property`). It finds an operation's module by walking the graph's parents, and reads `step.body`.
- **M10:** the practices register on their models, and no model imports its practice at run time (see the cycle section).
- **M12:** `BoundedContextMap.load(path)`, `load_bounded_context_map_content`, `UxMap.remove_screen`, `all_story_names`, `_PATTERNS` and `ux/log-action-requests.txt` are all gone.
- **L1:** `_DRAWN_MEMBERS` is gone. The cell's `seam_bullets` is the one limit.
- **L2:** one `StoryNode.slug` (`story_model.py:100`).
- **L3:** `_CONSTRUCTORS` is gone. The rules read `CONSTRUCTOR_NAMES` and `Operation.is_constructor`.
- **L6:** the story canvas reads `self.screen_map.screens` and keeps no second list.

## Counts

This summary table is headed "by concern", not "concern", so `concern_counts.py` counts only the finding rows above. Round 5's file has a summary table headed "concern", and the script counts its 8 summary rows as findings (30 rows for 22 findings).

| by concern | high | medium | low |
|---|---|---|---|
| 1 duplicated functionality | – | M2, M7, M8 (3) | N2 (1) |
| 2 duplicated shapes | – | H1, M1, M4, M11 (4) | – |
| 5 wrong-shape runtime relationships | – | H1, M3, M7, M13 (4) | L7 (1) |
| 6 seams that leak | – | – | N1 (1) |
| 7 dependency direction | – | – | NS1 (1) |
| 9 one file, several owners | – | M8 (1) | – |
| 10 names | – | – | L4 (1) |
| 11 legacy and stale docs | – | – | L5 (1) |

There are 15 finding rows: 9 medium, 6 low, no high. By status: 12 left, 2 new, 1 new scope, 0 regressions. 10 round-5 findings are fixed.

Nothing was found for concerns 3, 4, 8 or 12. For concern 12, the UX JavaScript was again not read line by line.

## Goal-class counts

Each row counts once in every class it names. M7 and M8 fall in two classes, and H1 in two.

| goal class | round 5 | round 6 left | round 6 new | round 6 new scope | round 6 total |
|---|---|---|---|---|---|
| bad resource orientation (5 + 9) | 6 (M3, M7, M8, M9, M13, L7) | 6 (H1, M3, M7, M8, M13, L7) | 0 | 0 | 6 |
| shadow models (2) | 6 (H1, M1, M2, M4, M11, L6) | 4 (H1, M1, M4, M11) | 0 | 0 | 4 |
| duplicated functions (1 + 12) | 8 (H2, M2, M5, M6, M8, L1, L2, L3) | 3 (M2, M7, M8) | 1 (N2) | 0 | 4 |

Counting each row once, the goal classes went from 17 rows in round 5 to 11 rows in round 6. The resource-orientation class did not shrink. M9 was fixed, but H1 now counts there: its remaining problem is state carried in intent text.

## Scanner false positives and scanner issues

- **`cdd_guidance/practices/clean_engineering/model/production_code.py:19` `_TEST_FILE`** does not match `*.feature.py`. `stories/model/story_channel.feature.py` and `ddd/model/ddd_channel.feature.py` are mamba specs, and both say they are not collected with the other specs. Every Clean Engineering production rule judges them as production code. They alone make the Stories cycle 11 modules wide and add the DDD edge from `model` to `markdown`.
- **`cdd_guidance/practices/clean_engineering/model/python/python_class_model.py:176-191` `import_targets`** counts imports inside `if TYPE_CHECKING:` the same as runtime imports. Counting them is defensible, but `one-way-deps` (`practice_wide_rules.py:44-52`) then reports a type-only reference as a "Circular import". It should label a cycle that closes only through type-only imports, so a reader does not hunt for a runtime cycle that is not there.
- **`harness/graph/skipped_folders.py:37` and `production_code.py:18`** list `_examples` but not `catalog-examples`. All three practices in this area have a `catalog-examples/` folder, and the lead counted 54 hits there in round 5's post-fix run. This confirms the lead's note.
- The graph check could not run this round, so no other scanner hit could be judged.

## What would make this area's next round cheaper

1. **Fix agents remove the named function but not the other places that do the same job.** The pattern is: the one locator, table or writer the fix named is made, and a second copy elsewhere is left. Examples:
   - `StoryMapLinks` still searches for `story-map.md` itself.
   - `_name_says` and `_kind_of` keep their own naming lists.
   - The markdown map writes scenarios beside `MarkdownScenario.lines`.
   
   Each fix brief should name the *job*, and the agent should search for the job's literals (the file name, the suffix, the heading text), not only for the function the finding named.
2. **State carried as text survives the reshaping.** A class's place and an aggregate's arcs ride in intent text, and a draw.io cell's kind rides in its description. The code around them was rewritten, but the encoding stayed, because removing it needs Clean Engineering's class model and draw.io reader to carry typed parts. H1, M3 and L7 will stay open until one agent owns that change across both practices.

Also, the graph check has not finished on this area in rounds 5 or 6, except once after round 5's fixes. Until a graph build stops taking the host off the network, this area's graph findings depend on whether the host survives the build.
