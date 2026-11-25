# Round 9: practices-stories-ux-ddd

Area: `cdd_guidance/practices/stories`, `cdd_guidance/practices/ux` and `cdd_guidance/practices/ddd`, without `_examples` and `catalog-examples`. Worktree `ensure-domain-orientation-refactor` at 5f36e6a2; the CDD MCP host serves the same commit. No code was edited.

Every round-8 finding was checked against the code. The fixes for this area are in b8b68e4e (round-8 practices, merged in 5f36e6a2) and the graph hotfix c5404b75 (merged in 78e11cbf). New decision records since round 8: `stories/.context/cdr/0004-a-node-records-under-the-parent-that-walks-it.md` and `harness/graph/.context/cdr/0002-graph-readers-read-saved-facts.md`.

## The graph check ran

The call was `validate` with `clean-engineering-modules`, `graph: true` and the three practice folders, at 01:45 UTC. The host answered "still running" four times and then the result: **439 graph hits on 19 rules** (round 8: 702 on 22), 21 AI rules in scope. No crash.
- Report: `C:\Users\jeffa\.cdd\runtime\.sessions\ensure-domain-orientation-refactor\validation-reports\clean-engineering-modules-20261109T014559.md`, graph JSON beside it.
- **No hits** for `one-way-deps`, cycles, `deep-module`, `low-coupling`, missing module context, module naming, `extensions-live-with-the-domain` or `shape-classes-around-resources`.

Hits by rule: use-typed-signatures 105, keep-operations-small-focused 62, prefer-class-operations 48, prefer-instance-operations 38, limit-operation-parameters 35, use-intention-revealing-names 32, keep-operations-single-responsibility 24, provide-meaningful-context 19, simplify-control-flow 18, hide-inner-details 15, keep-classes-single-responsibility 12, avoid-vague-parameter-names 10, use-property-not-accessor 6, do-not-invent-parallel-object-models 5, state-change-returns-record-or-named-failure 3, use-explicit-dependencies 3, eliminate-duplication 2, limit-comments 1, never-swallow-exceptions 1.

## R8-H1 probed again: fixed

The round-8 probe was run again (`C:\Users\jeffa\AppData\Local\Temp\claude\a5c5bdbb8e4b6072\1da33504-c4b4-4a29-9c7f-0741c828af02\scratchpad\r9_stories_restore_probe.py`): Clean Engineering and Stories over the TypeScript story example (555 steps), saved, opened from the saved graph, then `src/wallet.ts` refreshed. Both refreshes now pass, in process and in a worker; the 555 steps come back as plain `Node`s.

A second probe (`...\scratchpad\r9_stories_restore_probe2.py`) compares a fresh build with each refresh: the Stories links (777 `observes` edges) and the Stories rule violations (25, on 6 rules) are the same, twice in a row in process and twice in a worker.

A third probe (`...\scratchpad\r9_explorer_restore_probe.py`) renders a UX map's HTML on the same graph, fresh and opened from its save. The fresh render passes; the render on the opened graph fails (R9-H1).

## Findings, most severe first

| # | file:line | concern | check | status | finding | fix (one line) | severity |
|---|---|---|---|---|---|---|---|
| R9-H1 | `ux/model/explorer_tree.py:17-67, 92-123` `ExplorerScreen.__init__`, `_story_entry`, `_scenario_entry`, `ExplorerTree._epic_entries`, `_epic_entry` | 5, wrong behaviour | AI + probe | new (made by the R8-M3 fix) | The explorer tree Python now writes into the mockup page is read from the Stories graph nodes each screen's links hold (`link.node`), through attributes only a parsed story object has: `story.scenarios`, `story.top_epic`, `epic.epics`, `sub_epic.stories`, `scenario.steps`, `step.step_type`, `step.text`. A graph opened from its save holds those nodes as plain `Node`s, so `HtmlUxMap.render` fails with `AttributeError: 'Node' object has no attribute 'scenarios'` (`html/nodes.py:188`); the probe shows it. CDR 0002 calls reading an attribute off a node a defect and lists UX's `StoryLink` as fixed; `key_of` in `story_link.py:65-96` already reads a node through its type, facts and edges. Fix rule "fix every sibling" was missed. | Read the tree through the graph's edges and saved facts, as `key_of` does, or have Stories answer the epic, scenarios and steps of a node; add a spec that renders on a graph opened from its save. | high |
| R9-M1 | `stories/model/code_story_model.py:98-230, 255-350` `CodeScenario.calls_in`, `scenario_blocks`, `backgrounds_in`, `example_names`, `CodeStory.load_all`, `name_in`, `fill`, `:68-73` `_quoted_name_line`; `brace_story.py:12-115`; `python/nodes.py:11-35`, `java/nodes.py:11-50` vs `story_file.py:21-72` `paired`, `StoryFile.read`; `brace_story_file.py:24-120`; `python/story_file.py:17-112` | 1 | AI | new | Each code story file is read twice. Regular expressions over the text build the stories, scenarios, backgrounds and steps; then `BraceStoryFile` or `PythonStoryFile` parses the same text again into blocks (story, scenario, background and step calls), and `paired` joins the two readings by name ("the name is what the two readings share"). The brace scenario regexes and `BraceStoryFile`'s call patterns find the same calls; a story's line is searched for by its name (`_quoted_name_line`) though its block knows its span. The R8-M4 fix made each node read its own block, which is right, but kept both readers. | Build the nodes from the blocks of the one `StoryFile` reader (name, span, step calls, body), and delete the text regexes and `paired`. | medium |
| R9-M2 | `stories/model/code_story_model.py:376-811` `CodeStoryModel` (55 methods, total complexity 151, 20 dependencies) | 5 | metrics + graph (keep-classes-single-responsibility) | new scope | The class holds three jobs. (1) The folder layout: `load`, `parse`, `_ordered_paths`, `epic_for`, `sub_epic_for`, `_read_story_file`, `_take_stories`, `is_story_file`, `_under_tests_root`. (2) How a language spells a story: about twenty hooks (`story_open`, `story_close`, `scenario_open`, `step_open`, `and_open`, `and_close`, `step_placeholder`, `empty_block`, `file_header` ...) that `PythonStoryModel` (13 unrelated jobs by the metrics), `BraceStoryModel` (8) and `JavaStoryModel` override. (3) Keeping the code a story was read with on a render: `_adopt_code`, `_take_story_code`, `_take_children_code`, `_take_code`, `_take_step_bodies`, `_is_as_read`. | Make the language's spelling a part each format holds beside its `StoryFile` reader, so the model keeps the layout and the code it adopts. | medium |
| R9-M3 | `stories/model/markdown/nodes.py` `MarkdownStoryModel` (37 methods, complexity 179) and `MarkdownScenario` (32 methods, complexity 161); the module is 1107 lines | 5 | metrics + AI | new scope | The map reads three notations (heading map, outline map, scenario document) in one class, keeping the reading position on the domain node (`_current`, `_line_index`, `_current_story`). `MarkdownScenario`, one scenario, holds the reader of a whole scenario file with many stories (`parse_file`, `sections_in`, `_accept_story_heading`, `_story_name`, `_shared_background`, `_clause_source`). The functions over 20 paths in this area are mostly here (`MarkdownIncrement.parse` 23, `_parse_document_lines` 21, `document_text` 20). | A scenario-file reader that the scenario file owns, and per-notation readers that hand each epic and story its own lines, as the sketch format does with `SketchLines`. | medium |
| R9-M4 | `ux/story-demo/screen-tree.js:71-104` `DOMAIN_NOUNS`, `appendNouns`, `stepLabel` | 12 | AI | new | The explorer underlines domain nouns in step labels from a list fixed in the JavaScript: "My Paradise", "Mavenir shopping cart", "Apple Pay", "Cognito", "Vouchera", "Twilio" and others from one project. Which words are the domain's nouns is a rule of the model; `Screen.domain_terms` already holds a screen's terms in Python, and every other project gets one project's nouns marked. | `ExplorerTree` writes each screen's domain terms into the page; the JavaScript only marks the terms it is given. | medium |
| R9-M5 | `stories/model/source_location.py:9-25` `SourceLocation`; `story_recording.py:209-240` `span_of`, `place`, `file_of`; `harness/graph/graph.py:93-104` `Source`, `:615-619` `Node.place` | 2 | graph (do-not-invent-parallel-object-models) + AI | new | Stories keeps its own class for where a node sits in its file (`file`, `line`, `end_line`, `text`), beside the graph's `Source` (`file`, `start_line`, `end_line`), and a story node's `source` changes from one to the other when the graph adds it. `span_of` reads `getattr(source, "line")`, which a `Source` does not have, so a node already on a graph is found again by searching the file's text for its name. No other practice keeps a second location class. | One location type for a node: the model's nodes hold the graph's `Source` (or the graph adopts `SourceLocation`), and `span_of` reads it without `getattr`. | medium |
| R9-L1 | `ux/story-demo/mount-generated-mockup.js:196-210` `itemStoryStepsFor` | 12 | graph (never-swallow-exceptions) + AI | left (R8-M3, partly; fix rule "fix every sibling") | R8-M3's `readStoryOutline` now raises on a page that is not JSON, but its sibling still turns a JSON parse failure of the step template Python writes (`html/nodes.py` `_steps_json`) into an empty list. | Raise, as `readExplorerTree` does. | low |
| R9-L2 | `stories/model/drawio/nodes.py:151-171` `DrawIOEpic.x`; `miro/nodes.py:108-128` `MiroEpic.x`; `diagram_story_model.py:63-80` `DiagramStoryNode.x` | 1 | metrics (function clones) + AI | new | The draw.io and Miro epics place themselves with the same walk over their siblings, line for line except the story pitch class; the diagram base has a third version of the same walk. | One `DiagramEpic.x` that reads the format's story pitch and margins. | low |
| L5 | `.context/repo-model.md`, `.context/repo-runtime.md`, `.context/repo-model-disconnected.md` | 11 | AI | left | The root cards still name `StoriesGraph`, `DddGraph` and `DiagramCard` (7, 11 and 1 mentions). The fix brief keeps these files off-limits to fix agents. | Regenerate the three root cards. | low |

## Decided (not counted)

- **H1, M1, M4** (round 6; `ddd/.context/cdr/0001`, `0002`, `0003`): no change, and I still agree with each reason.
- **R8-L8, the `record` half** (`stories/.context/cdr/0004`): each story node keeps receiving the graph node of the parent that walks it, because a scenario read from a story test is shared by every same-named story of a merged map, so its model `parent` is only the last of them. I agree: reading the parent from `parent` would link a shared scenario under one story only. The `add` half is fixed.

## Fixed since round 8

- **R8-H1:** `StoryLinks` reads each step's `body_text` and `callees` facts and finds its epic up the graph's edges (`stories/model/graph_reading.py:117-163`); examples are linked from their saved `source_names` and `source_reads`. The probes above pass in process and in a worker, twice each, with the same links and violations as a fresh build. `harness/graph/graph_build_spec.py:25, 259-260` now refreshes a graph holding every practice, Stories included.
- **R8-M1:** `stories/rules/rule_examples.py` reads each example folder through the shared `RuleFixture(Stories, files)`, the live working-copy build; the regexes and `StoryFixture` are gone, and every example is in the story-test layout (`tests/<epic>/..._story.test.ts`).
- **R8-M2:** one `CodeStoryModel.load` with `is_story_file` reading each language's `not_story_paths`; `example_names` and `scenario_blocks` live once on `CodeScenario`, `unescaped` once in `code_story_model.py`; the three format `load`s are gone. (The brace format's own `scenario_blocks` reads a different syntax.)
- **R8-M3:** `ExplorerTree` writes the explorer tree into the page and `screen-tree.js` only draws it; `readExplorerTree` raises on a page with no tree. Its sibling `itemStoryStepsFor` is left (R9-L1), and the new Python tree reads parsed attributes off graph nodes (R9-H1).
- **R8-M4:** `StoryReader` and `brace_story_reader.py` are gone; each story, scenario and step reads its own block (`read_code`). The two readings this leaves are R9-M1.
- **R8-M5:** markdown nodes take their `SourceLocation` as each line is read (`_read_here`, `markdown/nodes.py:1100-1104`); the private `_stamp_*` calls and `attach_source_locations` are gone; `place_in` is the one public way to stamp a subtree.
- **R8-L1:** `Scenario.story_name` is gone; only the scenario file's section keeps the story's name while it is read.
- **R8-L2:** `Epic.top_epic` and `Epic.leaf_epics` on the story model; the Claude Design, Miro and `UxMap` copies are gone.
- **R8-L3:** one `DomainClass(DomainNode, OoadClass)` base with the shared constructor.
- **R8-L4:** `DddReading` keeps each aggregate's `bare_classes` as a fact; `EveryClassCarriesDddStereotype` only reads it; the folder is spelled once (`_folder_of`).
- **R8-L5:** a `DomainClass` holds its `TacticalClass`; a `BuildingBlock` holds the one made for its class. The two left (`_grouped`, `ClassCard.from_code`) each make one per class for one conversion.
- **R8-L6:** `SketchLines` answers `nested` and `under`, and each sketch node reads it.
- **R8-L7:** `StoryMapFiles.thin_slicing()` finds the thin-slicing file with the same folder skips.
- **R8-L8, the `add` half:** `StoryRecording.add(story_object, node_id, at, facts)` reads the name and type from the object.
- **R8-L9:** the DDD model card's Integration section lists `context`, `aggregate`, `entity`, `held_by`, `PARTS`, `target_name` and `keeps_one`; `BuildingBlock` lists `named_for_its_kind`.

## The round-8 fix rules

- **Grep the whole repository for a removed name.** Met for code, specs and `.context` cards: `StoryReader`, `brace_story_reader`, `_stamp_*`, `attach_source_locations`, `StoryFixture`, `_top_epic` and `readStoryOutline` appear in no source or card. The deleted explorer JavaScript (`buildScreenNodes`, `nestScreens`, `keysForCurrentScreen`, `placeScreens`) is still embedded in `ux/catalog-examples/mockup.html` and the generated catalog pages that copy it; `catalog-examples` is outside this area, so it is not counted here.
- **Fixes carried to every fidelity and sibling.** Missed twice: CDR 0002's rule reached `StoryLinks` and `StoryLink`, not the new `ExplorerTree` (R9-H1); R8-M3's raise reached `readStoryOutline`, not `itemStoryStepsFor` (R9-L1).
- **Two served calls in a row give the same answer.** Met for the Stories refresh: two refreshes in process and two in a worker give the fresh build's links and violations.
- **Metrics gate.** The merged code passed. No fix in this area made a guarded metric worse that I could find; `CodeStoryModel` went from 36 to 35 public operations.

## Code metrics as evidence

`measure_revision.measure(..., 'r9')['offenders']`, filtered to this area:
- **Classes over 100 total complexity:** `MarkdownStoryModel` 179, `MarkdownScenario` 161, `CodeStoryModel` 151 (R9-M2, R9-M3) and `MarkdownAggregate` 129. `MarkdownAggregate`'s jobs are its own notation and its conversion to and from a class model, which `ddd/.context/cdr/0002-markdown-nodes-are-the-map-every-format-reads.md` decides belong on the markdown nodes; not counted.
- **Classes over 30 methods:** `CodeStoryModel` 55, `MarkdownStoryModel` 37, `MarkdownScenario` 32.
- **Functions over 20 paths:** none in this area; the most are `ClaudeDesignStoryModel._story_entry` and `DrawioUxMap.cli_record` at 20.
- **Duplicated helpers:** the only body clone touching this area is `DrawIOEpic.x` / `MiroEpic.x` (R9-L2). Free-function names in several modules: `_name_of` in `ux/model/html/nodes.py:250` and `ux/model/json/nodes.py:279` (one line each, `screen.name if screen else ""`), `_folder_of` (`ddd/model/graph_reading.py:276` and `harness/guidance/guidance.py:910`, which do different jobs), `_slug` (different bodies). Not counted: each is one line or a different job.
- `story_channel.feature.py` shows in the offenders (`_grouped` 23 paths, 439 lines); it is a spec run by hand, so it is not counted.

## Graph hits: confirmed, dismissed, not counted

**Confirmed and filed:** do-not-invent-parallel-object-models on `SourceLocation` (R9-M5); never-swallow-exceptions on `itemStoryStepsFor` (R9-L1); keep-classes-single-responsibility on `CodeStoryModel` (R9-M2).

**Dismissed:**
- do-not-invent-parallel-object-models: `DddReading` "copies the fields" of `StoriesReading` (`graph`, `practice`, `root`), as in round 8: each is its own practice's reader. `MarkdownBoundedContext.module_name` is the name a document writes for the code folder; no `Module` is on hand when the text is read. `ExplorerTree.screen_keys` is the page's `screenKeys` JSON being built. `StoryModel.source_texts` is a scanner false positive (below).
- eliminate-duplication, 2: `StoryLinks.__init__` (three assignments) and `MarkdownStory.__init__` against another small `__init__`.
- hide-inner-details, 15: the ten JavaScript hits are the page's own frames and controls; the five Python hits are a scanner false positive (below).
- use-explicit-dependencies, 3: `UxMap` builds its `ReferencePaths` value; the two JavaScript hits are the page building its own frames.
- state-change-returns-record-or-named-failure, 3: JavaScript functions that wire event handlers; outside the twelve concerns.
- prefer-class-operations, 48, and prefer-instance-operations, 38: almost all are pure text helpers (`_slug`, `_quoted`, `_indent`, `bar_y`) or the regex classmethods R9-M1 would delete. `DddReading`'s six module functions are the ones the metrics gate commit made functions to lower its class's complexity.

**Not counted (code-level rules outside the twelve concerns):** keep-operations-small-focused 62, use-intention-revealing-names 32, keep-operations-single-responsibility 24, provide-meaningful-context 19, simplify-control-flow 18, avoid-vague-parameter-names 10, limit-comments 1, use-typed-signatures 105 (all Python), limit-operation-parameters 35 (constructors of model nodes and the JavaScript painters; `record`'s parent is decided by CDR 0004), and the 6 DDD `get_next_*_from_file` names.

## Scanner false positives

1. **`clean_engineering/model/operation_metrics.py:226-235`** (`reaches_peer_private`, rule `hide-inner-details`): a Python local or loop variable of the body's own class counts as a peer, because only `self`, `cls`, parameters typed as the class and `new`-built locals count as the class itself. Hits: `PythonBlock.backgrounds`, `steps` and `_within` (`item._is_inside` on another `PythonBlock`), `CodeStoryModel.render` (`model = type(self)(...)`, then `model._adopt_code`), `Epic._has_estimate` (`child._has_estimate()` over its own epics), and `Step.__init__` (`origin._keyword` of the `Step` it copies). This is round 8's false positive 2, still open.
2. **`clean_engineering/rules/coupling_rules.py:152-163`** (`_member_keyed_by_name`, rule `do-not-invent-parallel-object-models`): `StoryModel.source_texts: Dict[str, str]`, each file's text keyed by its path, is reported as "one value per Source keyed by its name" because the field's first word names a class. The key is a file path, not a `Source`'s name.

Round 8's false positives 1 (JavaScript parameters in `use-typed-signatures`), 3 (`extensions-live-with-the-domain` on nested format packages) and 4 (constructors in `state-change-returns-record-or-named-failure`) are gone: no such hit this round.

## Counts

This summary table is headed "by concern", not "concern", so `concern_counts.py` counts only the findings table above.

| by concern | high | medium | low |
|---|---|---|---|
| 1 duplicated functionality | – | R9-M1 (1) | R9-L2 (1) |
| 2 duplicated shapes | – | R9-M5 (1) | – |
| 5 wrong-shape runtime relationships | R9-H1 (1) | R9-M2, R9-M3 (2) | – |
| 11 legacy and stale docs | – | – | L5 (1) |
| 12 Python and TypeScript | – | R9-M4 (1) | R9-L1 (1) |

There are 9 findings: 1 high, 5 medium, 3 low. By status: 2 left (R9-L1, L5), 5 new (R9-H1, R9-M1, R9-M4, R9-M5, R9-L2), 2 new scope (R9-M2, R9-M3), 0 regressions. Of the 16 round-8 findings, 14 are fixed (R8-M3 except its sibling, carried as R9-L1), R8-L8 is half fixed and half decided, and L5 is left. Nothing was found for concerns 3, 4, 6, 7, 8, 9 or 10. Of the new findings, one was made by a round-8 fix (R9-H1, by the R8-M3 fix); the other four were in the code at round 8.

## Goal-class counts

Each finding counts once in every class it names.

| goal class | round 8 total | round 9 left | round 9 new | round 9 new scope | round 9 total |
|---|---|---|---|---|---|
| bad resource orientation (5 + 9) | 7 | 0 | 1 (R9-H1) | 2 (R9-M2, R9-M3) | 3 |
| shadow models (2) | 0 | 0 | 1 (R9-M5) | 0 | 1 |
| duplicated functions (1 + 12) | 7 | 1 (R9-L1) | 3 (R9-M1, R9-M4, R9-L2) | 0 | 4 |

Summed over the classes, the area went from 14 in round 8 to 8 in round 9. Without the 2 new-scope findings, which come from reading the metrics offenders for the first time, it is 6: 1 left and 5 new. One high finding remains in the goal classes: R9-H1, the R8-H1 crash again, now in UX's explorer tree.

## What would make this area's next round cheaper

1. **Every reader of another practice's nodes must be run on a graph opened from its save.** R8-H1's fix reached Stories, and CDR 0002 names UX's `StoryLink` as fixed, but the explorer tree written in the same round reads `story.scenarios` off a graph node and fails the same way. A spec that renders a UX map, and runs every other reader that holds a Stories node, on a graph opened from its save (as `r9_explorer_restore_probe.py` does) would have caught it. A grep for attribute reads on `link.node`, `in_graph.nodes(...)` results and `graph.direct_parent(...)` results would find the rest.
2. **When a node learns to read its own block, delete the reader it replaced.** The R8-M4 fix gave each code story node its own block but kept the regex reading that builds the nodes, so the story file is parsed twice and joined by name (R9-M1). The same pattern is behind the two location classes (R9-M5). The brief should ask the fix agent to name, for each reader it adds, the reader it deletes.
