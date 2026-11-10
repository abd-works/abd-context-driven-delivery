# Round 7: practices-stories-ux-ddd

Area: `cdd_guidance/practices/stories`, `cdd_guidance/practices/ux` and `cdd_guidance/practices/ddd`, without `_examples` and `catalog-examples`. Worktree `ensure-domain-orientation-refactor` at c8921451; the CDD MCP host (`~/.cdd/runtime`, pid 30700, port 47800) serves the same commit. No code was edited.

Every round-6 finding was checked against the code, along with the four decision records the fix agents wrote: `ddd/.context/cdr/0001`–`0003` and `stories/.context/cdr/0001-read-paths-reads-the-calls-source-format.md`. The fix commits for this area are cc2394a6, cfbecf8b, a7b49c63, 7d3efb53 and f02b6485.

## The graph check failed: DDD's graph reading crashes in the graph worker

The call was `validate` with `clean-engineering-modules`, `graph: true` and the three practice folders, at 11:36:58 UTC.
- The host answered "still running" eight times. `cdd_ping` answered `pong` during the build, so a build no longer takes the server off the network (round 6's B10 symptom is gone).
- The ninth answer was `GraphBuildFailed: the graph build's worker process exited with 1`, raised at `cdd_guidance/practices/ddd/model/graph_reading.py:203` (`tactical.inferred_kind(names)`) → `stereotypes.py:98` → `AttributeError: 'Node' object has no attribute 'stereotypes'`.
- The call left an empty report: `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\validation-reports\clean-engineering-modules-20261108T113658.md`, 0 bytes.

Following `.claude/rules/mcp-fail-loud.md`, I stopped and made no further graph call. The cause is a finding in this area (R7-H1 below), so every other finding comes from the **AI** check, plus two local scripts in the scratchpad: one compares each Stories and DDD graph check with the schema that lists its rule (`r7_schema_gaps.py`), and one built the graph in-process for each practice folder to look for the crash (`r7_ddd_crash.py`). The in-process build does not crash, which is how the cause was narrowed to the worker path.

## Rule-versus-schema gaps in Stories and DDD

A check runs on a node only when the schema lists its rule on that node's type: `GraphRulesCollection.from_node` (`harness/graph/graph_rules_collection.py:120-124`) builds a node's rules from `schema.slugs_for(node.type)`, and `record_violation` (`:184-189`) drops a hit for a slug the node's type does not list. The schema maps `given`, `when` and `then` to `Step`, and `subEpic` to `Epic` (`harness/graph/schema_edges.py:46-51`).

| practice | rule | check's node types | schema lists it on | effect |
|---|---|---|---|---|
| Stories | `kebab-case-paths` | Story, Scenario, Epic, SubEpic | nothing | never runs |
| Stories | `domain-operation-in-the-step` | Story, Step | nothing | never runs |
| Stories | `originating-sub-epic-examples` | Example | nothing | never runs |
| Stories | `scenario-names-continuation` | Step (Then) | Scenario | never runs: listed where the check does not apply, absent where it does |
| Stories | `branch-on-mechanical-uniqueness` | Epic, SubEpic, Story | Epic | never runs on a Story |
| DDD | `domain-concepts-not-technical-names` | building blocks, Aggregate | building blocks | never runs on an Aggregate |
| DDD | `screen-interface-not-a-domain-object` | EntityRoot, Entity, ValueObject, DomainService | EntityRoot, Entity, ValueObject | never runs on a DomainService |

The first three rules have no section in `stories.md` either, so they are checks with no rule. Every rule above has a passing spec, because both practices' rule-example support calls the check directly and never asks the schema: `stories/rules/rule_examples.py:73-83` and `:150-158` run `rule.check` on nodes whose type the spec sets by hand, and `ddd/rules/rule_examples.py:61` does the same. The shared rule `scan-fixture-pair` says these supports "run the same graph rule validate runs, so the spec cannot pass while validate fails". For these seven rules the spec passes while validate never runs the check.

## Findings, most severe first

| # | file:line | concern | check | status | finding | fix (one line) | severity |
|---|---|---|---|---|---|---|---|
| R7-H1 | `ddd/model/graph_reading.py:197-203` `_members_by_folder`; `ddd/model/stereotypes.py:72-98` `TacticalClass`; with `harness/graph/graph.py:1041-1053` `restore`, `:1426-1436` `carry_out` | 5, wrong behaviour | graph (call failed) + AI | new | `DddReading` wraps every `OoadClass` node Clean Engineering holds in a `TacticalClass` and reads `oclass.stereotypes`, `oclass.peer_names` and `oclass.name` off the object. In the graph worker added in round 6, `carry_out` first holds the server's graph through `restore`, which brings each node back as a plain `Node` holding its saved facts. When the session's graph already holds Clean Engineering classes, DDD's reading meets those plain nodes and the whole build fails, so `validate` with `graph` fails on this area. In-process builds (no worker) pass, which is why the specs do not catch it. Stories' `StoryLinks` also reads Clean Engineering's nodes and is worth checking for the same assumption. | DDD reads a class's stereotypes and peers as graph facts the class node keeps, or the worker re-reads rather than restores the extended practice's nodes. Add a spec that runs DDD's reading on a restored graph. | high |
| R7-H2 | `stories/model/schema.yaml:28-91, 161-182`; `stories/rules/story_map.py:65-67`, `scenarios.py:217-219, 335-337`, `acceptance_tests.py:66-68`; `ddd/model/schema.yaml:118-123`, no rules block on `aggregate` (`:25`); `ddd/rules/tactical.py:62, 131`; `stories/rules/rule_examples.py:73-83`, `ddd/rules/rule_examples.py:61` | 3, wrong behaviour | AI + local schema script | new scope | The seven rule-versus-schema gaps in the table above: four Stories checks never run in a graph build, one never runs on Stories' Story nodes, and two DDD checks never reach one of their node types. Their specs pass because the rule-example support runs the check without the schema. | List each rule on the node type its check applies to (scenario-names-continuation on `then`), delete the three checks no guidance rule names or write their rules, and make both rule-example supports run a check through `node.rules` so an unlisted rule fails its spec. | high |
| M2 | `ddd/rules/rule_examples.py:27-33, 45`; `ddd/rules/ddd_rules_spec.py:22, 91, 100, 153, 194, 202`; `ddd/model/graph_reading.py:203-205`; `ddd/rules/tactical.py:47-57` | 1, 3 | AI | left (partly) | Parts (a)–(c) are fixed: `_name_says` and its suffix list are gone, the cards ask `kind_named_by`, and the tactical rules read the `named_for_its_kind` fact. Part (d), "rule examples check classes that production would classify differently", is still true and now explicit. `_kind_of` raises for a class the graph names no block for, and six specs pass `node_type="Entity"` for `Plan`, `CartManager`, `Cart`, `Other`, `LonelyType` and `SelectSim`, bare classes the live graph never makes a building block. The consequence: `every-class-carries-ddd-stereotype` can never report in a live graph. The graph makes a building block only from a stereotype or the naming convention (`inferred_kind`), and the rule passes exactly those (`declares_stereotype`), so its failing example (a bare class) is a case validate cannot produce. The same holds for the bare-class examples of the other five rules. The fix-rule "one owner of the job" is missed: the spec, not the graph reading, decides the kind. | Either make the graph read a class in an aggregate's folder as a building block when it has no stereotype (so the stereotype rule can fire), or rewrite those examples so the graph itself names the kind. Remove `node_type=` from the specs. | high |
| R7-M1 | `ux/model/drawio/nodes.py:167-220` `DrawioUxMapReader(ux_map, root_element)`; `ux/model/markdown/nodes.py:48-80` `MarkdownContextReader(ux_map)` | 5 | AI | new | The JSON format lost its outside reader in round 6 (M7): each JSON node now reads its own record. The draw.io and markdown UX formats keep the old shape: a reader class handed the map, which builds screens, regions and transitions, and writes the map's scope and context notes, from outside. The fix covered the format the finding named and not its siblings. | The draw.io map reads its own pages, with `DrawioScreen`/`DrawioRegion` reading their own cells; the markdown map reads its own lines into its context. | medium |
| R7-M2 | `ddd/model/nodes.py:44-92` `Integration` (`target`, `target_parts`, `TARGET`, `as_dependency`, `read_dependency`); `ddd/model/markdown/nodes.py:111-127` `targeting`, `kept_by`; `ddd/model/drawio/drawio_bounded_context_map.py:74-78` | 5 | AI | new | Round 6's H1 moved a class's place into `module_path`, but an arc's target still travels as text. An `Integration` holds `context` and `aggregate` fields *and* a `target` string `Context · Aggregate · Entity` that `target_parts` re-parses on every read. The code formats carry it as `details["to"]` text, which `kept_by` parses back. The draw.io cell rebuilds the string by hand (`f"{integration.context} · {integration.aggregate}"`), a second spelling of the target. | Hold the target as its context, aggregate and entity names; write the `·` text only in the markdown and sketch lines, and keep the parts as separate details in a class model. | medium |
| M7 | `stories/model/markdown/nodes.py:220-235` `MarkdownScenario.lines` vs `:237-253` `document_text`; `:707-732` `MarkdownStory.document_text` vs `:734-770` `scenarios_text`/`_scenario_section_lines`; `stories/model/sketch/sketch_story_model.py:126` `_SketchReader` | 1, 5 | AI | left (partly) | The UX JSON part is fixed (see Fixed). The scenario heading is spelled once, and scenarios now write themselves. Still: a scenario not read from a document is written by `document_text` as its heading and steps only, while `lines()` writes heading, backgrounds, steps and examples, so the two writers disagree on what an unread scenario holds. A story writes a background as `### Background` in one and `### Story Background: name` in the other. The sketch format still fills the map from a reader class. No decision record covers what is left. | `document_text` for an unread scenario returns `lines()`; one story-section writer; sketch nodes read their own lines, as DDD's sketch nodes do. | low |
| M13 | `stories/stories.py:126` `Format(source or self.format).is_code`; `stories/.context/cdr/0001-read-paths-reads-the-calls-source-format.md` | 5 | AI | left (decision overtaken) | The decision record (reason: the practice's format is "held by the framework ... as a name") says that once `harness/guidance` holds the format as a *Format*, the line becomes `Format(source).is_code if source else self.format.is_code`. That has happened: `PracticeGuidance.format` returns a `Format` (`harness/guidance/guidance.py:338-343`). The line still wraps the held `Format` in a new one. | Make the change the record names, and mark the record done. | low |
| R7-L1 | `stories/model/markdown/links.py:19-20, 47-53` `_story_files_below`, `_SKIP_DIRS`; `stories/model/markdown/nodes.py:266-270` `MarkdownScenario.from_workspace`; `stories/model/story_map_files.py:41-46` `markdown_below` | 1 | AI | new | Story files are located in two places: `links.py` walks for `*_story.test.md`/`*_story.spec.md` with its own skip list, and `MarkdownScenario.from_workspace` globs the same suffixes. The M8 fix moved the map search to `StoryMapFiles.markdown_below`, which `rglob`s without skipping any folder, so the search for a map now walks `node_modules`, `.venv` and `.claude` worktree copies that the old walk skipped. `harness/graph/skipped_folders.py` already owns the skip list. | One story-file locator beside `StoryMapFiles`, both walking with `skips_folder`. | low |
| R7-L2 | `stories/rules/scenarios.py:61, 73, 137, 150, 177, 219, 304, 320, 337`; `story_map.py:19, 32, 67, 102`; `stories/rules/rule_examples.py:57, 77-82` | 10 | AI + local schema script | new | Stories' checks name node types the graph never makes: `Given`, `When`, `Then` and `SubEpic`, which the schema maps to `Step` and `Epic`. The rule-example support makes them anyway (`step.type = "Given"`) and runs checks on them, so its specs exercise node types a live build never has. | Checks name `Step` and `Epic` and read the step's kind or the epic's depth as a fact. | low |
| R7-L3 | `ux/model/ux_map.py:63-66` | 5 | AI | new | A map made with no graph now makes a `Graph()` of its own. This is the lazy `Graph()` pattern round 6 flagged in harness-upper (R6-H5): each copy of a map (`copy_of`) is given a fresh graph rather than the graph the map is written for. | The format that copies a map passes the graph the copy lives on. | low |
| L4 | `stories/model/story_model.py:1014` `copy_of(self, source)`; `ux/model/ux_map.py:84-85` `copy_of(cls, source)`; `ux/model/json/nodes.py:261` | 10 | AI | left (partly) | The parameter is now `source` in both. The shape still differs: an instance method in Stories (its docstring now says why: a code format copies with its own settings) and a class method in UX, which `JsonUxMap.render` reaches through `type(self).copy_of`. No decision record. | One shape: the instance method, in both. | low |
| L5 | `.context/repo-model.md:2788, 3112, 3164, 3178, 3357-3373`; `.context/repo-runtime.md:1821-1886`; `.context/repo-model-disconnected.md` | 11 | AI | left | The root cards still name `StoriesGraph`, `DddGraph` and `DiagramCard`; no class of those names exists. | Regenerate or edit the three root cards. | low |
| R7-L4 | `ddd/model/drawio/drawio_bounded_context_map.py:32`; `stories/.context/cdr/0001-*.md` (two files) | 11 | AI | new | `DrawIOContextCell`'s docstring still says it is "a module whose purpose line says it is one"; since the M3 fix the cell's kind is read from its style (`kind=boundedContext;`). Stories has two decision records numbered `0001` (`0001-read-paths-reads-the-calls-source-format.md` and `0001-runnable-story-files-over-pure-data.md`). | Say the style names the kind; renumber the new record `0003`. | low |

## Decided in round 6 (not counted)

- **H1** (the map is not a *CleanEngineeringModel*), `ddd/.context/cdr/0001`. I agree: a code format must hold its own language's classes, and the draw.io map is now itself the diagram (`DrawIOBoundedContextMap(BoundedContextMap, DrawIOCleanEngineeringModel)`). The place is a typed `module_path`, and the arcs are `Relationship` dependencies with details. What is left of the state carried in text is the arc's target, filed as R7-M2.
- **M1** (sketch and draw.io read into the markdown context and aggregate), `ddd/.context/cdr/0002`. I agree: every format renders by asking the map's nodes for their lines, so one set of node fields with one method per notation is not a second model.
- **M4** (`BuildingBlock` is a graph node holding the class), `ddd/.context/cdr/0003`. I agree: subclassing `OoadClass` would put a second class node in the graph, and every Clean Engineering rule would run on it twice.

## Fixed since round 6

- **M3:** a draw.io map cell's kind is written in its style (`kind=aggregate;`, `diagram_node.py:163-197`), and Clean Engineering's reader builds the cell type the style names (`module_cell_types`, `drawio_class_model.py:91, 165`). Spec: "should read each aggregate by the kind its cell's style names", with reworded purpose lines.
- **M8:** `StoryMapLinks.from_workspace` finds the map through `StoryMapFiles(root).markdown_below()`. No spec covers a map kept in `.context/` (see R7-L1 for the folder-skip side effect).
- **M11:** `Ddd._parse_content` asks `self.extended`, the one Clean Engineering practice of its set; `clean_engineering_companion` is gone from `ddd.py`.
- **N1:** the context's private `_map` is gone; each context type names its `aggregate_type`, and `get_next_bounded_context_from_file` makes `type(self)`.
- **N2:** `DomainEvent.map_entry()` writes the event line for both markdown and sketch; `_TYPE_SEPARATORS` is gone in favour of Clean Engineering's `pascal_type_names`.
- **L7:** the draw.io map holds no separate diagram; it is the diagram and draws its own modules.
- **NS1:** the graph readers are typed against `PracticeGuidance` and imported at module top by `ddd.py` and `stories.py`; no model module names its practice.
- **M7, UX JSON part:** `JsonContentType` and `JsonNavComponent` read and write their own records, and the map makes them through `content_type_type` and `nav_component_type`. Spec: "should read each content type and navigation component as the JSON format's own node".

## The round-6 fix rules

- **A spec on the effect of a concern-5 fix:** present for M3 (style kind read back), H1's typed parts (`code_round_trip_spec.py`: module path, intent free of place and integrations, direction and crossing kept), and the JSON nodes. Missing for the M8 locator change (a map in `.context/`).
- **One owner of a duplicated job, twins gone:** met for N2 and M2 (a)–(c). Missed for M2 (d), where the specs now decide a building block's kind (M2 above), and for story-file location (R7-L1).
- **A decision record for each skip:** present for H1, M1, M4 and M13. M13's record states its own trigger, and that trigger has now happened (M13 above). L4, L5 and what is left of M7 have no record.

## Counts

This summary table is headed "by concern", not "concern", so `concern_counts.py` counts only the finding rows above.

| by concern | high | medium | low |
|---|---|---|---|
| 1 duplicated functionality | M2 (1) | – | M7, R7-L1 (2) |
| 3 no use | R7-H2, M2 (2) | – | – |
| 5 wrong-shape runtime relationships | R7-H1 (1) | R7-M1, R7-M2 (2) | M7, M13, R7-L3 (3) |
| 10 names | – | – | R7-L2, L4 (2) |
| 11 legacy and stale docs | – | – | L5, R7-L4 (2) |

There are 13 finding rows: 3 high, 2 medium, 8 low. By status: 5 left (M2, M7, M13, L4, L5), 7 new, 1 new scope (R7-H2), 0 regressions. 8 round-6 findings are fixed, and 3 are decided.

Nothing was found for concerns 2, 4, 6, 7, 8, 9 or 12. For concern 12, the UX JavaScript was again not read line by line. The three scanner false positives round 6 listed are fixed: `production_code.py:33` treats `feature` as a spec role, `practice_wide_rules.py:29` leaves out imports under `if TYPE_CHECKING:`, and `skipped_folders.py:40` skips `catalog-examples`.

## Goal-class counts

Each row counts once in every class it names.

| goal class | round 6 | round 7 left | round 7 new | round 7 new scope | round 7 total |
|---|---|---|---|---|---|
| bad resource orientation (5 + 9) | 6 (H1, M3, M7, M8, M13, L7) | 2 (M7, M13) | 4 (R7-H1, R7-M1, R7-M2, R7-L3) | 0 | 6 |
| shadow models (2) | 4 (H1, M1, M4, M11) | 0 | 0 | 0 | 0 |
| duplicated functions (1 + 12) | 4 (M2, M7, M8, N2) | 2 (M2, M7) | 1 (R7-L1) | 0 | 3 |

Summed over the classes, the area went from 14 in round 6 to 9 in round 7, and from 11 rows to 8 counting each row once. Shadow models are at zero: three are decided with records I agree with, and M11 is fixed. Resource orientation did not shrink. Four of its six are new findings in code round 6 did not look at closely: the DDD reader's crash on restored nodes, the UX draw.io and markdown readers, the arc's target text, and the self-made `Graph()`.

## What would make this area's next round cheaper

1. **Specs that skip the path validate takes.** Both rule-example supports call `rule.check` on a node whose type or kind the spec sets by hand, so a check can pass its spec while validate never runs it (R7-H2) or never meets the case (M2). R7-H1 is the same blind spot one level up: the specs build the graph in-process, and only the worker path restores plain nodes. Fix briefs should require each rule spec to go through `node.rules` on a graph the practice's own reading built, and each graph-reading change to have one spec on a restored graph.
2. **The fix lands on the named format and not its siblings.** The JSON UX reader was folded into its nodes while the draw.io and markdown readers kept the old shape (R7-M1), and the class's place became a typed field while the arc's target stayed text (R7-M2). Each fix brief should name the pattern ("a reader handed the map", "state written into a string and parsed back") and ask the agent to grep every format of the practice for it.
