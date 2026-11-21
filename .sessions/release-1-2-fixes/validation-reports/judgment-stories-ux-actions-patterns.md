# Judgment: Stories, UX, actions, patterns, builders, context setup, desktop walk

**Judged:** 2026-11-21, on branch `release-1-2-fixes`, read only. No production code, test, or document was changed.

**Area:** `cdd_guidance/practices/stories` and `cdd_guidance/practices/ux` (practice classes, `model/` packages and their format adapters, graph readings, rules, the Story UI app and the Story Demo JavaScript), `cdd_guidance/actions`, `cdd_guidance/patterns` (without `oss_portal_domain_driven`), `cdd_guidance/builders`, `cdd_guidance/context_setup`, `cdd_guidance/desktop_walk`. `_examples`, templates, fixtures, and practice markdown were left out. Clean Engineering, DDD, BDD and `harness/guidance`, `harness/whiteboard`, `harness/graph` were read only as the other side of a comparison.

**How it was judged:** the area was read in four parts, each file in full (the large TypeScript and JavaScript view files: classes and exported functions closely, markup skimmed). Every finding cites a file and line that was read; every "no caller" or "internal only" claim was checked with grep over `cdd_guidance`, `harness`, `space` and `tools`, specs included. Nothing was run, apart from importing `WhiteboardStoryModel` to confirm one missing operation. Line numbers are those of commit `bba27fc5b`.

**Findings by theme** (393 bullets; a few carry no theme because they only point at another bullet):

| Theme | Findings |
|---|---|
| 1. Module boundaries | 58 |
| 2. The same work done in different shapes | 97 |
| 3. Resource orientation | 165 |
| 4. Domain orientation | 73 |

**Two defects found while judging** (neither was run end to end; each needs a failing test before a fix):

- `WhiteboardStoryModel` (`stories/model/whiteboard/nodes.py`) declares the `.whiteboard` suffix but has no `from_workspace`; only the markdown, JSON and draw.io story models define one. `stories.py:199` and `:253` call `from_workspace` on whichever adapter owns the file's suffix, so reading a `.whiteboard` story map through either would raise `AttributeError`.
- `MernDomainDriven` works only because it has no `practices/` folder: adding one would raise `AttributeError` at `harness/graph/pattern_overlays.py:152`, because the class has no graph overlay.

## Answers to the specific questions asked

**Which graph leads were real.** Of the 68 mechanical hits in the area (34 distinct, each reported twice), the cycle, the parameter counts on `render.py`, `BraceStoryWriting` on `StoryFilePlace`, and the small module-function and classmethod hits are real or point at a real problem nearby; the hits on `story-model.md` and `ux-model.md`, `StoryMapClient` on `Edit`, `StoriesReading` on `ScriptStoryModel`, `_align`, and `DesktopWalk` constructing `NewRepository` are noise. Section D gives the reason for each.

**The same constant in five files.** `NO_LONGER_IN_MODEL = "no longer in the model"` is defined at `actions/render/kept_document.py:33`, `actions/render/reshaped_code.py:37`, `stories/model/reshaped_story_file.py:34`, `ux/model/view/reshaped_view.py:29` and `bdd/model/spec_reshape.py:26`. It marks the five places that each write a render onto a file that is already there (proposal R1).

**Where another module reaches past the Stories seam.** `desktop_walk/desktop_walk.py:18-21` imports `MarkdownScenario`, `ScenarioFileReading`, `flat_steps` and `StoryMapFiles` from inside the Stories model; `ux/model/claude_design/story_canvas.py:25-30` subclasses the Stories diagram model classes; `ux/model/story_link.py` and `ux/model/graph_reading.py` walk `stories.reading.in_graph`; `actions/validate/checked_graph.py:16-18` names the Stories practice by string and copies its node types. The Stories module card offers none of these as terms other packages use. Proposals S4, U2, R3 and R5 give them one seam.

### The UX import cycle and what UX imports from other practices

**(1) The import cycle of four packages (model, drawio, html, json).** These imports make it:

| From | To | Import |
|---|---|---|
| `model` | `drawio` | `model/graph_reading.py:24` `from cdd_guidance.practices.ux.model.drawio.nodes import UnreadableDrawio` |
| `model` | `html` | `model/graph_reading.py:25` `from cdd_guidance.practices.ux.model.html.nodes import UxMapNotEmbedded` |
| `drawio` | `model` | `model/drawio/nodes.py:26-28` (`model.nodes`, `model.story_link`, `model.ux_map`) |
| `html` | `model` | `model/html/nodes.py:10,12,13,14` (`explorer_tree`, `nodes`, `reference_paths`, `ux_map`) |
| `html` | `json` | `model/html/nodes.py:11` (`JsonControl`, `JsonStoryDemoControl`, `JsonUxMap`) |
| `json` | `model` | `model/json/nodes.py:13-25` (`model.nodes`, `model.ux_map`) |

The format packages importing the model is the right direction. The only imports that point the wrong way are the two in `graph_reading.py`, and each brings in one exception class, used once, in the tuple `_NOT_A_MAP` (`graph_reading.py:39`). `UxReading` already gets the format adapters themselves through `reading.practice.formats` (`graph_reading.py:151-155`), so it needs no format package by name. Fix: declare one base failure, `UxMapUnreadable`, in `model/ux_map.py` beside `ScreenNotOnMap`; `UnreadableDrawio` and `UxMapNotEmbedded` subclass it; `graph_reading.py` catches the base and drops both imports. See proposal U1. No import inside a function or through `importlib` takes part in this cycle (the function-level imports in the area go to other practices, listed next).

**(2) What UX imports from other practices.**

| File:line | Imports | Through the seam? |
|---|---|---|
| `model/story_link.py:84`, `:159` (inside functions) | `Stories` from `stories/stories.py` | The class is the seam, but the code then walks `stories.reading.in_graph.nodes(...)` and `.source_root` (`:90`, `:162`, `:168`, `:176-178`), which is Stories' graph reading, not a named seam operation. |
| `model/graph_reading.py:346` (inside a function) | `Stories` | Same: `stories.reading.in_graph` (`:351`). |
| `model/graph_reading.py:322-323` (inside a function) | `CleanEngineering`, `Ddd` | Class is the seam; then reads `practice.reading.class_types` and `reading.in_graph.nodes(kind)` (`:313-315`). |
| `model/graph_reading.py:368` (inside a function) | `CleanEngineering` | Then `clean.reading.in_graph.nodes("Property")` and the fact `owner` (`:377-378`). |
| `model/explorer_tree.py:10` (`TYPE_CHECKING` only) | `StoryTree` from `stories/model/graph_reading.py` | Not an import that runs, but `explorer_tree.py:87` reaches it as `shown[0].practice.reading.story_tree`. `StoryTree`'s own docstring says other practices should ask it, so this one is intended; the card of Stories does not list it as a term other packages use. |
| `model/claude_design/story_canvas.py:25-30` (module level) | `DiagramEpic`, `DiagramStory`, `DiagramStoryModel` from `stories/model/diagram_story_model.py`; `Background`, `Scenario`, `Step`, `StoryModel`, `StoryNode` from `stories/model/story_model.py` | No. These are Stories' model classes. The Stories card lists only the TypeScript app's names under "Terms other packages use" (card line 21), so UX subclasses a Stories model class the card does not offer. |

Who imports UX model classes from outside UX: no production code. The only hits are specs: `actions/sketch/sketch_spec.py:246` and `practices/sketch_document/sketch_outline_spec.py:23` (the `Ux` class), `stories/model/story_model_spec.py:928` (`Screen`), and `harness/graph/model_node_spec.py:22` (`made` from `ux_map_spec_fixture.py`). No action and no pattern imports a UX model class. `ClaudeDesignStoryModel` has no Python caller outside its spec; it is reached through the markdown recipe beside it.

### Actions, render, patterns: the questions asked

1. **Actions reaching into a practice's model.** No production file under `cdd_guidance/actions` imports a class from `cdd_guidance.practices.*`; the only import is the registration import `import cdd_guidance.practices` at `actions/__init__.py:14`. The reach is by knowledge instead of by import: `validate/checked_graph.py:16-18` names the Stories practice and its node types as strings; `render/render.py:120` finds a practice adapter's `reshape` with `getattr`; `render/kept_document.py` and `render/reshaped_code.py` hold format knowledge (draw.io cells, whiteboard elements, Python and TypeScript members) that the practices' format adapters also hold. The one module that does import past a practice's seam is `desktop_walk/desktop_walk.py:18-21` (four Stories model modules). Patterns import Clean Engineering's `SourceText` and `CODE_LANGUAGES` from its model package, and import `Ddd`, `Stories`, `Bdd` inside functions.
2. **Render.** The same job, writing a rendered shape onto a file that is already there and marking what the model dropped, is written five times: `actions/render/reshaped_code.py`, `actions/render/kept_document.py`, `stories/model/reshaped_story_file.py`, `ux/model/view/reshaped_view.py`, `bdd/model/spec_reshape.py`. The arithmetic on declared paths is written in `harness/guidance/declared_outputs.py` and again in `rendered_file.py`, `rendered_code.py`, `checked_graph.py`, and `generate.py`. `RenderOrder` is a second shape of `RenderRequest`.
3. **LERN, MERN, web domain access.** There is no Python duplication between LERN and MERN, because MERN has none of it: `MernDomainDriven` is 15 lines, has no `graph_overlay`, no `tier_facts`, and no graph rules. It reuses LERN through `DomainDrivenStack` only for the default folder and the format. LERN's `TierFile` and web domain access's `AccessFile` are two shapes of one idea (a file read once into `SourceText`, answering fact dictionaries), and they decide a file's node type in two different places.
4. **Doers and bags.** See `Render` (loose values handed through four layers, result dictionaries), `CheckedGraph` and `ReportFiles` (two objects passed to each other, parallel lists), `TierFile` (one class answering facts for five kinds of file, chosen by the caller), `_LernReading` (fields set in `read`), `DesktopScenario.read_steps`.
5. **Domain language.** Docstrings still say "context tool" for Guidance; the repair action is the class `Improvement`; `render_worker.py` and `worker_render.py` mirror each other's names; `prefixes`, `NamedToCheck`, `Member`, `TierFile` (for story files), `AccessFile.tier()` do not say what they are.
6. **Graph hits.** Judged in section D and in the findings: 13 real, 6 noise or wrongly aimed.

## Findings

Theme tags: [1] module boundaries, [2] the same work in different shapes, [3] resource orientation, [4] domain orientation.

### cdd_guidance/practices/stories/stories.py

- stories.py:87-279 `Stories` — keep-classes-single-responsibility — AGENTS.md says a practice is "a thin `{practice}.py`", yet 190 of this file's 282 lines read story maps and story tests from disk, merge them, and place stories under epics (`read_files`, `_take_stories_only_code_holds`, `_epic_along`, `_merge_epics`, `_maps_beside`, `_named_map`). The practice class changes whenever the file layout changes. [1]
- stories.py:103-279 `project` — hold-state-on-the-object-not-in-parameters — `project` is handed through eleven operations of one class (`read_files`, `_take_stories_only_code_holds`, `_maps_to_read`, `_read_story_test`, `_take_story_test`, `_story_map_of_code`, `_texts_by_reader`, `_story_map_file`, `_maps_beside`, `_named_map`, `story_test_sources`) and `on_file` through five. The missing object is one read of a project's story files, which would hold both. [3]
- stories.py:244-249 `_story_test_reader` — eliminate-duplication — the expression "each adapter of `self.formats` that is a `CodeStoryModel`" is written again in `StoriesReading._code_readers` (graph_reading.py:133-135), so the list of code formats is computed in two classes. [2]
- stories.py:192, 246 function-level imports — one-way-deps — `MarkdownStoryModel` and `CodeStoryModel` are imported inside `open_file` and `_story_test_reader`. Neither module imports `stories.py`, so no cycle forces this; the imports hide two dependencies of the practice class from the top of the file. [1]
- stories.py:197 `open_file` — put-logic-on-the-owning-resource — `isinstance(adapter, MarkdownStoryModel)` decides how a file is opened for editing. Only the markdown format has `opened_from`; the practice asks the adapter what it is instead of asking every format to open its own file. [3]
- stories.py:98-99, 199, 253 `from_workspace` — use-consistent-naming — one name carries three contracts: `JsonStoryModel.from_workspace(root)` takes a folder and no `on_file` (json/nodes.py:304), `MarkdownStoryModel.from_workspace(root, on_file=, project=)` takes a folder (markdown/nodes.py:416), `DrawIOStoryModel.from_workspace(path, ...)` takes a file (drawio/nodes.py:428). `_story_map_file` (253) passes `on_file=` and `project=` to whichever format reads the extension, which the JSON signature would refuse. `StoryModel` declares none of them, so nothing states the contract. [2]
- stories.py:98-99 `adapter_class("json")`, `adapter_class("markdown")` — hold-state-on-the-object-not-in-parameters — formats are looked up by name string in `stories.py` (98, 99) and `stories_formats.py` (131, 147) where the caller means one known class. The strings repeat the keys of `_FORMAT_ADAPTERS` (31-41), so a renamed format breaks at run time only. [3]
- stories.py:187 `open_file` — use-typed-signatures — no return type, and line 199 returns `adapter.from_workspace(...) or adapter`: the format adapter itself stands in for an empty story map, so the caller cannot tell a read map from the reader. [4]
- stories.py:232-242 `story_tests` — use-typed-signatures — returns `dict[str, list[str]]` (file path to story names); `OpenedStoryMap._acceptance_tests` (opened_story_map.py:116) reads it back by name. The stories are in hand as objects and are turned into name strings to be matched again. [3]

### cdd_guidance/practices/stories/stories_formats.py

- stories_formats.py:55 `_is_read_from_files(self, node)` — use-typed-signatures — `node` has no annotation; it is a `Story | Scenario`. [4]
- stories_formats.py:28 `ThinSlicedMap.semantic_type` — prefer-instance-operations / use-property-not-accessor — a method that returns the constant `"ThinSlice"` only so the object passes `PracticeFormats._is_object_model`; the class is a wrapper that exists to route one render (`render` line 105 switches on `isinstance(request.content, ThinSlicedMap)`). The drawing choice belongs on the diagram adapter the request already names. [3]
- stories_formats.py:44-53 `SpecifiedStories.kept_in`, `_keeps` — keep-operations-single-responsibility — `_keeps` answers a question (does the epic hold a specified story) and, while answering, removes stories and sub-epics from the epic (lines 51-52). A predicate that mutates surprises every later caller. [3]
- stories_formats.py:69 `ScenariosOnTheirMap.read_by(markdown: type)` — hold-state-on-the-object-not-in-parameters — the markdown adapter class is passed in by the only caller (147), which got it by name string; the object could be built with it, or the read could be an operation of the markdown story model. [3]
- stories_formats.py:95-99, 139-141 — eliminate-duplication — "the files under each named entry of the project" is written twice (`read` 97-98 and `_scenarios_on_their_map` 140-141) with slightly different globbing. [2]

### cdd_guidance/practices/stories/model/story_model.py

- story_model.py:77-287 `StoryNode` — keep-classes-single-responsibility — one base class holds five jobs: the story hierarchy; the code a node was read with (`written`, `file_written`, `setup`, 119-123, set on every node including `Example` and `Increment`, which never hold code); eleven rule facts (`_start_map_facts`, 126-138) with the logic that computes them (`load_map_facts`, 140-161); graph recording (`recorded_name`, `recorded_type`); and the MCP edit tools (247-279). A change to a rule fact, to code rendering, or to an edit tool all edit this class. [3]
- story_model.py:43-52, 1508-1562 `EpicColumns` and `_ESTIMATE_*` — layer-separation — how many columns an epic's bar spans on a drawn map, in characters per column, sits in the core story model. Its only callers are the diagram formats (drawio/nodes.py:192, 380; miro/nodes.py:252; diagram_story_model.py:332) and the UX story canvas. The core model changes when a drawing's column width changes. [1]
- story_model.py:710, 777-778, 1110-1111, 1291-1292, 1401 `step_type`, `story_type`, `scenario_type`, `background_type`, `epic_type`, `increment_type` — use-consistent-naming — `Scenario.step_type` (777) and `Background.step_type` (710) are the *class* steps are made with, while `Step.step_type` (556) is the *StepType* value Given/When/Then; `StoryModel.story_type` (1292) is a class while `Story.story_type` (1124) is the *StoryType* value user/system/technical. `Scenario.new_step(step_type: str, ...)` (835) then means the enum on an object whose `step_type` attribute means the class. `Epic.__init__` names the same hook `story_class` (937) and the local `build_story` (953): three words for one idea. [4]
- story_model.py:482-499, 545-567, 713-724, 782-799, 937-957, 1113-1142, 1294-1328 and `clone` at 329, 534, 699, 752, 897, 1049, 1266, 1439 — eliminate-duplication — every node has two copy paths: a copy-constructor (`Epic(source)`, `Scenario(source)`) and `clone()`. `Step.clone` (701) and `Increment.clone` (536) already call the constructor; `Scenario` (794-799 against 897-908), `Story` (1133-1142 against 1266-1277), `Epic` (950-957 against 1049-1063), `Background` (721-724 against 752-757) and `StoryModel` (1322-1328 against 1439-1446) list the same fields twice, about 60 lines. A field added to one path and not the other is lost on one kind of copy. [2]
- story_model.py:482, 545, 713, 782, 937, 1115 `name: "str | Epic"` — avoid-vague-parameter-names — the first parameter of each constructor is either the node's name or a node to copy, so `name` is a node half the time; `StoryModel.__init__(source: StoryModel | Graph)` (1294-1297) and `CodeStoryModel.__init__(source: StoryModel | str)` (code_story_model.py:420-423, where a `str` silently becomes `tests_root`) overload the same way. [4]
- story_model.py:1283 `StoryModel` — use-intention-revealing-names — the domain word is *story map* (the class docstring opens "A story map", every operation doc says "the story map", `OpenedStoryMap`, `story_map` property, `StoryMapEditRefused`), but the class is `StoryModel`, so its published toolset is `story-model.*` (`story-model.new_epic`, `story-model.show`) beside `epic.*` and `story.*`. A user of the tools meets a technical word for the thing the practice calls a story map. [4]
- story_model.py:1336-1343 `StoryModel.load` — write-interactions — reaches through the session's parts: `session.paths.path_named`, `session.session_files.file_manager`, `files.read(os.path.relpath(path, files.workpath))`, `session.graph.practices.of(...)`, `session.repo_path`. Five session internals in eight lines; the session should hand over "the Stories file at this name, read" in one call. [1]
- story_model.py:1345-1356 `StoryModel.open_in_session` — put-logic-on-the-owning-resource — picks "the first fidelity" (`next(iter(stories.fidelities))`, 1352) and walks `declared.files().values()` for the first existing entry. Which file is a session's story map is the Stories practice's (or the fidelity's) knowledge, written here as iteration order. [3]
- story_model.py:1312, 1318 `links = None`, `slicing = None` — use-typed-signatures — two collaborators typed only by a comment; `OpenedStoryMap._write_formats` calls `slicing.write(increments)` (opened_story_map.py:97) on whatever was assigned. [4]
- story_model.py:305-361, 379-392 `Example.value: ExampleValue = Any` — use-typed-signatures — the value is a dict, a class, a string, or any object, and `cells` (334-351), `as_code` (353-361), `edit_field` (379) and `rename` (388-392) each branch on `isinstance`. Four places must agree on the set of shapes. [3]
- story_model.py:353 `Example.as_code` — no use, delete — no caller anywhere (`git grep as_code` finds only this definition and unrelated `as_code_writes`). [3]
- story_model.py:999 `Epic.has_epics` — no use, delete — the only reference is story_model_spec.py:391. [3]
- story_model.py:417 `Examples(dict)` — hide-inner-details — the examples of a scope are a `dict` subclass, so every caller may use any dict operation; `rename` (436-441) has to rebuild the dict with `dict.clear`/`dict.update` to keep order, and `drop` exists beside `del`. [3]
- story_model.py:210, 589, 828, 981, 1178, 1415 `holding(part)` — hide-inner-details — a public operation that hands out the node's private mutable list (`self._steps`, `self._epics`). Its only production callers are `move_before`, `_leave` and `Step.segment` in this file (268, 285, 583); it can be private. [1]
- story_model.py:155 `_load_child_band(count, label, fewest, most)` — limit-operation-parameters — four values, two of which (`fewest`, `most`) are one band that `_child_band_for_layer` (1073) already returns as a tuple and line 1070 unpacks with `*`. [3]
- story_model.py:704 `_steps_key` and 1604 `_renumber` — prefer-class-operations — module functions used only from classes in this file; `_steps_key` repeats the "step then its ands" walk that `story_file.flat_steps` also writes. [2]
- story_model.py:140-161, 858-866, 1065-1071, 1188-1197 `load_map_facts` — eliminate-duplication — four overrides each call `_load_opening()` and `_load_path_case()` and reset the same three flags by hand before setting their own. [2]
- story_model.py:874, 685, 742 `record(recording, story, parent)` / `record(recording, file, parent)` / `record(recording, parent)` — use-consistent-naming — one verb, four signatures (`Epic` and `Story` take `(recording, parent)`, `Scenario` takes `(recording, story, parent)`, `Step` and `Background` take `(recording, file, parent)`, `Example` takes `(recording, scenario, lines)`), so the recording cannot call `record` on a node without knowing its kind. [4]

### cdd_guidance/practices/stories/model/code_story_model.py

- code_story_model.py:92-203 `StorySyntax` with story_file.py:40 `StoryFile` — eliminate-duplication — a story file is read twice by two parsers. `CodeStory.load` (303) reads the text with the regexes of `StorySyntax` to make the story, scenarios and steps; `CodeStory.read_code` (320) then reads the same text through `StoryFile` blocks to attach each node's code, and the two results are joined by position (`zip(self.scenarios, scenarios, leads)` at 329, `read_step_code` in story_file.py:36) with a guard for the case they disagree (`Step.read_code`, story_model.py:619). The module comment of story_file.py says "no story is matched to a block by its name"; its steps are still matched to blocks by place. [2]
- code_story_model.py:183-202 `StorySyntax._balanced`, `_outside_scenarios` — abstraction-focus — the base syntax of "every language" finds `scenario(`, `=>` and `{`, which only the brace languages write; Python inherits brace matching it never calls. [2]
- code_story_model.py:79-89 `CodeStoryNode` — class-not-property-instance-or-subtype — a mixin of three name forms. `camel()` has no caller at all; `pascal()` is passed to a template (story_writing.py:175) that no language's `file_name_template` uses (`{snake}` only); `snake()` has that one call. One call does not earn a mixin on four classes. [3]
- code_story_model.py:689 `stories_of(...) -> tuple` — use-typed-signatures — returns an untyped pair (stories, the file's own code) that five callers index with `[0]` (stories.py:185, graph_reading.py:200, reshaped_story_file.py:48, and two specs). The pair is a story file as read; it has no type. [3]
- code_story_model.py:646 `_take_stories(holder, stories, written, content, source_file)` — limit-operation-parameters — five parameters, four of which describe one read story file. [3]
- code_story_model.py:498 `_write_epic(epic, parent, examples_folder, files)` — limit-operation-parameters — four parameters; `files` is an output dict threaded through the recursion and `examples_folder` is derivable from the epic's top epic (`Epic.top_epic` exists, story_model.py:1012). [3]
- code_story_model.py:580 `self._project = project` — hold-state-on-the-object-not-in-parameters — `load` stores its `project` argument on the model so `_read_story_file` (626) can read it back, a field set for one call. [3]
- code_story_model.py:289-318 `CodeStory.load_all`, `load_file`, `load`, `from_block` — prefer-instance-operations — four class-level factories make the story *class* the thing passed around: `StoryFile.stories(story_type, ...)`, `SharedStoryFile.stories(story_type)`, `ScreenSpecFile.stories(story_type)` each take the class as a parameter and call back into it. The model that holds `story_type` should make its stories. [3]
- code_story_model.py:334 `add_scenario`, 355 `fill`, 272 `read_description` — deep-module — public, called only from `CodeStory.load` in the same class (308, 307, 365). [1]
- code_story_model.py:385-391 `CodeEpic.order_path` — hide-inner-details — walks parents with `hasattr`/`getattr` for `sequential_order`, `parent`, `epics` on objects that are always `Epic` or `StoryModel`; the reflective access hides that this is "my index among my siblings, then my parent's". [3]
- code_story_model.py:74 `unescaped` — prefer-class-operations — a module function imported by three other files (brace_story.py:9, brace_story_file.py:13, python/nodes.py:9); it belongs on `StorySyntax`, which every one of those callers already holds or is. [3]
- code_story_model.py:522-570 `_adopt_code`, `_take_story_code`, `_take_children_code`, `_take_code`, `_take_step_bodies` — put-logic-on-the-owning-resource — the model reaches into each node to copy `written`, `setup`, `file_written` and step bodies from another node of the same name. Each node knows which code it holds; "take the code of this other node" is a node operation (`StoryNode.take_code_from` already exists at story_model.py:163 for the unconditional case). [3]

### cdd_guidance/practices/stories/model/story_file.py

- story_file.py:23 `CodeBlock = Any` — use-typed-signatures — the type every block-reading signature names is `Any`, with its thirteen members listed in a comment (16-22). `BraceBlock` and `PythonBlock` share no base, so nothing checks that a new language's block answers them. [2]
- story_file.py:29 `flat_steps`, 34 `read_step_code` — prefer-class-operations — module functions that take a scenario's or background's steps and walk them. `flat_steps` is imported by four other files, one of them in another module (`cdd_guidance/desktop_walk/desktop_walk.py:20`), so desktop walk depends on a helper of the story-file reader to list a scenario's steps. [1]
- story_file.py:53 `stories(story_type, path, project)` — hold-state-on-the-object-not-in-parameters — the file is built for one text and one language but is told its path, its project and its story class on the call; each is fixed for the file's life. [3]

### cdd_guidance/practices/stories/model/brace_story.py and brace_story_file.py

- brace_story.py:18-30 `BraceSyntax` regexes with brace_story_file.py:16-21 — eliminate-duplication — the same calls are matched by two sets of patterns: `scenario_pattern` (brace_story.py:22) and `_SCENARIO` (brace_story_file.py:18); `_BACKGROUND` (23) and `_BACKGROUND` (19); `_CALL` (18) and `_STEP` + `_CHAINED` (20-21); `_CALL_NAME` (30) and `_STORY` (17). A change to how a step call is written must be made in both. About 80 lines of `BraceSyntax` (14-94) repeat what `BraceStoryFile`/`BraceBlock` (145 lines) find. [2]
- brace_story.py:38-43, 48-50, 72-74, 88-91 — eliminate-duplication — "find `=>`, then `{`, then the balanced body" is written four times in `BraceSyntax` and once more in `StorySyntax._outside_scenarios` (code_story_model.py:196-201). [2]
- brace_story.py:133, story_writing.py:163-181 `StoryWriting.file_header(place)`, `story_file(place, written)` — shape-classes-around-resources — the graph hit is right in substance: `StoryFilePlace` (story_writing.py:49) holds the epic, the stories and the folders, and the writing computes the file's path and header from it. The path of a story file is the place's own fact; only the spelling is the language's. [3]
- brace_story.py:147-161 `story_background_lines`, `scenario_background_lines` — eliminate-duplication — two operations build the same `background(scope, ({ given }) => {` block with different indent and closing; the scope fallback differs (`"each"` against `"background"`) with no stated reason. [2]
- brace_story_file.py:123-124, 136-140 with python/story_file.py:93-94, 106-112 — eliminate-duplication — `split_inside` is the same line in `BraceBlock` and `PythonBlock`; `setup` and `inside_lines` differ only in the Python comment filter and the blank-line squeeze. About 25 lines that a shared block base would hold once. [2]

### cdd_guidance/practices/stories/model/script_story_model.py, typescript/, javascript/

- typescript/typescript_story_model.py:19-21 and javascript/javascript_story_model.py:21-23 `__init__(language, helpers)` — eliminate-duplication — identical constructors (the graph hit). `ScriptStoryModel.writing` (script_story_model.py:101) calls `self.writing_type(self.language, self.story_test_import_path)` with two arguments, but `BraceStoryWriting`, the declared default `writing_type` (brace_story.py:167), takes one: the base class's contract only holds because both subclasses add the same constructor. [2]
- typescript/nodes.py:10-20 and javascript/nodes.py:10-20 — class-not-property-instance-or-subtype — `TypeScriptScenario`/`JavaScriptScenario` and `TypeScriptEpic`/`JavaScriptEpic` are empty subclasses; `TypeScriptStory`/`JavaScriptStory` differ from `ScriptStory` by one attribute (`language`) that the model already holds. Six classes carry one value; `PythonEpic` (python/nodes.py:69) and `CodeIncrement` (code_story_model.py:377) are empty too. [2]
- script_story_model.py:34-39 and 85-88; python/nodes.py:53-66 and python/python_story_model.py:71-74 — eliminate-duplication — "is this text a screen spec / a shared story file" is asked twice per language, once in the story class's `load_all`/`load_file` and once in the model's `story_file`, and the two answers must stay opposite. `ScreenSpecFile` and `SharedStoryFile` are story files that are not `StoryFile`s, each with its own `stories(story_type)`. [2]
- script_story_model.py:25 `script_story_file_suffixes` — prefer-class-operations — a module function called only to fill a class attribute of the two subclasses (typescript_story_model.py:29, javascript_story_model.py:32) from `LEAF_EXTENSION`, which the base class already declares. [3]
- script_story_model.py:71, 76, 81 `story_test_folder`, `story_test_import_path`, `story_test_file_path` — use-intention-revealing-names — "story test" names two things: a story's test file (`{story}_story.test.ts`) and the step library `story-test.ts`. `story_test_folder` is the step library's folder (its own docstring has to say so), and `Stories.story_test_folder` (stories.py:79) carries the confusion to the practice's constructor. `story_test_file_path` is used only inside the class (92). [4]
- script_story_model.py:63-68 `_default_story_test_folder` — provide-meaningful-context — the literal `"stories"` workspace root decides where the step library goes, with no name saying which convention it is. [4]
- javascript/javascript_story_model.py:33 `seed_file` — one-way-deps — the JavaScript step library is read from `stories/templates/js/story-test.js` while the TypeScript one is read from `model/typescript/seeds/story-test.ts`; two homes for the same kind of file. [2]

### cdd_guidance/practices/stories/model/python/

- python/nodes.py:64 and python/shared_story_file.py:130 `Path.cwd()`, `sys.path` — use-explicit-dependencies — the folders an examples module is looked for in default to the process's working directory and import path, written in two places. A read in the MCP server then depends on where the server was started. [3]
- python/nodes.py:53-57 `PythonStory.load_all` — keep-operations-single-responsibility — overrides `load_all` to call `load_file(content, None)`, whose last line calls `super().load_all(content)`: two operations that call each other across the class hierarchy to add one `if`. [3]
- python/shared_story_file.py:37-57 `FixtureExample` — no-redundant-relationship-paths — a second `Example` class carrying `fixture_facts` and `_declared`, with its own `clone` (54-57) repeating `Example.clone` (story_model.py:329-332). The base `Example` already has the two hooks (`recorded_facts`, `declaration`); the subclass exists to hold two values. [2]
- python/shared_story_file.py:34 `_EXAMPLES_MODULE` — eliminate-duplication — `re.compile(r"examples$")` is defined again in graph_reading.py:40; story_recording.py:31-33 (`_NAMED_IMPORT`, `_PYTHON_FROM_IMPORT`) reads a story file's imports a second way beside `BraceSyntax.import_pattern` (brace_story.py:24) and `PythonSyntax.import_pattern` (python/nodes.py:20). [2]
- python/story_file.py:33 `call_of` — prefer-class-operations — a module function used only by `PythonStoryFile` and `PythonBlock` in the same file. [3]

### cdd_guidance/practices/stories/model/story_writing.py

- story_writing.py:37, 72, 77, 89, 98, 112, 119 — prefer-class-operations — seven module functions (`example_names_of`, `as_read`, `story_description`, `background_examples_line`, `scenario_examples_lines`, `own_backgrounds`, `_step_texts`) each take a story or scenario and read its fields. Six are called only from `StoryWriting` and its subclasses (brace_story.py:134, 144-145; python_story_model.py:38, 44, 47); `own_backgrounds(scenario)` and `scenario_examples_lines(scenario)` are questions a `Scenario` answers about itself. [3]
- story_writing.py:72-74, 234 `as_read`, `_is_as_read` (and story_model.py:119-122 `written`, `file_written`) — use-intention-revealing-names — `written` means "the lines this node was read with" throughout (`as_read(written, ...)`, `story.written`, `story.file_written`, `WrittenBlock`), so the word for output names input; `_is_as_read` (234) has to translate. [4]
- story_writing.py:183 `story_text` — no use, delete — called only from two specs (code_story_behaviours_spec.py:98, typescript_story_model_spec.py:94). [3]
- story_writing.py:280-282 `_callback` — abstraction-focus — the base writing of every language spells a JavaScript arrow function (`"async () => {"`); Python inherits it and never uses it because its templates have no `{callback}`. [2]

### cdd_guidance/practices/stories/model/reshaped_story_file.py

- reshaped_story_file.py:93, 130 `self._writing._scenario_lines`, `self._writing._step_lines` — hide-inner-details — calls two private operations of `StoryWriting` from another class, so their signatures are a seam nobody declared. [1]
- reshaped_story_file.py:129 — eliminate-duplication — `self._writing.verbs.get(step.keyword) or self._writing.default_verb or step.step_type.value` rewrites `StoryWriting._verb` (story_writing.py:220) with a different last fallback. [2]
- reshaped_story_file.py:34 `NO_LONGER_IN_MODEL` — eliminate-duplication — the same string constant is defined in five files (`actions/render/kept_document.py:33`, `actions/render/reshaped_code.py:37`, `bdd/model/spec_reshape.py:26`, `ux/model/view/reshaped_view.py:29`, and here), with a comment that "the Render action reads the same words". It belongs beside `Reshaped` in `harness/guidance/practice_formats.py`, which all five already import or serve. [2]
- reshaped_story_file.py:53-54 `kept`, `added` — hide-inner-details — public mutable lists that only `reshaped()` reads back into a `Reshaped`; no other caller reads them. [1]

### cdd_guidance/practices/stories/model/story_recording.py

- story_recording.py:56, 75, 81, 95, 354, 361, 369 — prefer-class-operations — seven module functions. `step_semantic(step)` is called only by `Step.recorded_type` (story_model.py:683) and `step_checksum` only by `Step._node_id` (697): both are Step's own. `file_of(node)` is called with a story node every time and is the node's own file. `folder_of` is called once (story_model.py:1020). `example_source_file` and `imported_files` take a `StorySource`'s `file` and `imported_modules` as parameters and are wrapped by `StorySource.example_source` (158) and `imported_example_files` (162) a few lines below. [3]
- story_recording.py:253-267 `_align` — put-logic-on-the-owning-resource — a five-way switch on `node.type` strings decides how each kind of node finds its lines, and the Example branch asks the story object for `declaration`. Each story node kind should say how it is aligned, as `Example.declaration` already begins to. [3]
- story_recording.py:226-280 `self.practice.reading.in_graph` — hold-state-on-the-object-not-in-parameters — the chain is walked seven times (234, 246, 249, 265, 267, 277 and `.graph` at 226); the recording should hold the practice's part of the graph once. [3]
- story_recording.py:224-229 `story_map`, `practice`, `graph`, `on_node`, `story_at`, `story_total` — hide-inner-details — six public attributes; nodes use only `graph` (story_model.py:317, 691, 748, 889, 1025, 1243). The progress counters are the recording's own. [1]
- story_recording.py:101-192 `StorySource` — keep-classes-single-responsibility — one class reads TypeScript/JavaScript imports, Python imports, exported constants, domain class names, declared examples in two languages, and a docblock's evidence, all by regex over the text, choosing by file suffix (`_EXAMPLE_DECLARATIONS`, 38-45). The per-language knowledge sits beside, not in, the per-language `StorySyntax`. [2]

### cdd_guidance/practices/stories/model/graph_reading.py, modelled_areas.py, term_links.py

- graph_reading.py:96, 105 function-level imports of `CleanEngineering` and `Ddd` — one-way-deps — Stories names two sibling practice classes inside properties. Neither practice imports Stories, so there is no cycle, but the imports are hidden from the top of the file and the card lists only Clean Engineering "for code formats" as a dependency, not DDD (`rules/rule_examples.py:17` imports `Ddd` at the top). [1]
- graph_reading.py:17, 434, 455, 502 `MODULE_FUNCTION_HOLDER`, `self.clean.code_index.members_named`, facts `"owner"` — low-coupling — `StoryLinks` reads Clean Engineering's code index and its `owner` fact and compares it with a constant from `clean_engineering/model/base_class_model.py`. The Clean Engineering card lists as terms other packages use only *CleanEngineeringModel, UnreadableSource, Module, OoadClass, Property, Operation, Parameter, Relationship, CodeBody*; none of these three is among them. [1]
- graph_reading.py:373-385 `StoryLinks`, modelled_areas.py:33-44 `ExampleObservations`, modelled_areas.py:103-113 `ModelledAreas`, term_links.py:25-37 `TermLinks` — eliminate-duplication — four classes each hold the Stories reading and its graph, each walks `stories.in_graph.nodes()` filtering by a private copy of `_STEP_TYPES` (graph_reading.py:33, modelled_areas.py:18, term_links.py:20), two copy `_EPIC_TYPES` (graph_reading.py:49, modelled_areas.py:20), two define `_step_body` word for word (graph_reading.py:504, modelled_areas.py:98) and `examples` (graph_reading.py:392, modelled_areas.py:46). `StoryTree` (graph_reading.py:260) already exists to answer these questions and answers only four of them. [2]
- modelled_areas.py:141 `_area_of` with graph_reading.py:269 `StoryTree.epic_of` — eliminate-duplication — both walk `direct_parent` upward looking for an epic type; one stops at the nearest, one at the outermost. [2]
- graph_reading.py:373-513 `StoryLinks` in graph_reading.py — high-cohesion — the file holds the practice's reading (55-257), the tree (260-296), `ImportedFiles` (299-370) and `StoryLinks` (373-513), while the sibling link writers have files of their own (`term_links.py`, `modelled_areas.py`). `ImportedFiles` and `StoryLinks` are 215 lines that only `read_working_copy` constructs. [1]
- graph_reading.py:78, 140 `recorded_map = None` — hide-inner-details — a public class attribute assigned in `read_working_copy` and read by nothing else in production (`git grep "\.recorded_map"` finds only lines 140 and 142). [1]
- graph_reading.py:161 `_story_map`, 232 `_story_maps` — use-typed-signatures — no return types on the two operations that decide which story map the graph is built from. [4]
- graph_reading.py:43-46 `CALLS_REACH_*` — use-typed-signatures — four string constants stand for one closed set of values; `CodeStepsInvokeCode` imports two of them (rules/acceptance_tests.py:11). An enum would let the rule and the reading share the set. [4]
- graph_reading.py:202-215 `_story_tests` — hold-state-on-the-object-not-in-parameters — builds a second adapter per language with `type(language)(tests_root=_MAP_LESS_TESTS_FOLDER)`, discarding the settings the practice's own adapter was made with (step library folder), where `copy_of`-style construction on the adapter would keep them. `Stories._story_map_of_code` (stories.py:208) does the same with `STORY_TESTS_FOLDER`. [3]
- modelled_areas.py:125 `_record(node, fact, value)` — avoid-vague-parameter-names — `value` is the fact's new value, a `list[str] | bool`; the graph hit is right and the fix is a rename. [4]
- term_links.py:43-51 `_link_step` — simplify-control-flow — three nested `for` loops with four edge writes in the innermost; the "example named after the term" loop is a separate thought from "link the step to the class". [3]

### cdd_guidance/practices/stories/model/story_map_files.py, opened_story_map.py, name_facts.py

- story_map_files.py:16, 22, 46, 53 `source_at`, `path_from`, `is_story_map_file`, `preferred_maps` — prefer-class-operations — four module functions in the file that holds `StoryMapFiles`. `source_at` is a thin constructor wrapper over the graph's `Source` imported by ten files; `preferred_maps` and `is_story_map_file` are what `StoryMapFiles` knows. [3]
- story_map_files.py:133 `scenario_files_below` — keep-operations-small-focused — one 300-character comprehension with four nested clauses and a single-element `for kind in [...]` used as an assignment. [3]
- opened_story_map.py:46 `session.graph.practices.of(story_map.practice_kind)` and story_model.py:1340 — eliminate-duplication — the session's Stories practice is looked up twice for one open: `StoryModel.load` finds it (1340) and then builds `OpenedStoryMap(model, path, session)`, which finds it again (46). [3]
- opened_story_map.py:150-168 `UnopenedStoryMap` — class-not-property-instance-or-subtype — a null object with no `fidelity`, so `StoryModel.formats` (story_model.py:1369, `self.opened.fidelity.session_output`) raises `AttributeError` on a map opened from no file, while `file`, `refusal` and `scope` answer quietly. The two classes share no base that states what "opened" must answer. [3]
- name_facts.py:73 `opens_with_verb` — no use, delete — no caller in production or specs. [3]
- name_facts.py:54-95 — prefer-class-operations — a file of functions that take a node's name or source and return facts the node then stores on itself (story_model.py:144, 150, 153, 1191). The verb lists are data; the functions are the node's. [3]

### cdd_guidance/practices/stories/model/screen_spec_file.py

- screen_spec_file.py:42-57 `ScreenSpecFile.stories(story_type: type) -> list` — use-typed-signatures — untyped class in, untyped list out, and `stories: dict[str, object]` inside. [4]
- screen_spec_file.py:30 `_SEED` — provide-meaningful-context — a Given is any statement calling a function whose name starts with `write`, `seed` or `reset`. The convention is the test library's and is stated only as a regex here. [4]

### cdd_guidance/practices/stories/rules/scenarios.py

- scenarios.py:82-84, 197-199, 210-212, 258-259, 330-331 — eliminate-duplication — six rules open with the same gate ("its keyword is X or empty, or its node type is X") written out each time, once as two nested `if`s (82-84). The gate exists because the rules list `("When", "Step")` as node types and then filter the steps back out. [2]
- scenarios.py:408-420 `_keyword`, `_text`, `_phase` and 110 `scenario_domain_concepts` — prefer-class-operations — module functions over a step node used by every rule in the file; `scenario_domain_concepts` is public and has one caller (142). A shared step-rule base would hold all four. [3]
- scenarios.py:291-298, 385-405 — eliminate-duplication — "the background steps of the story a scenario belongs to" is found two ways: `GivenNamesComplexStateRootFirst._background_steps` scans `context.edges("scenarios")`; `ScenariosShape._parent_story` first walks `getattr(node, "parent")` and then scans the same edges. `StoryTree` has neither. [2]
- scenarios.py:178-183, 300-304 `context.practice.reading.domain_model` — low-coupling — two rules reach through the context to the Stories reading and from it into DDD's graph by node-type strings (`"EntityRoot"`, `"Aggregate"`, edges `"root"`, `"owns"`). DDD's node types are written as literals in a Stories rule file (lines 40, 149). [1]
- scenarios.py:435-437 `PlainEnglishGwtSteps.check` — limit-comments (dead code) — `if ...: return []` followed by `return []`; the last condition and `_PLAIN_ENGLISH` (23) decide nothing. [3]
- scenarios.py:106-108, 245-248 `node.facts.get(...)` — use-consistent-naming — two rules read `node.facts.get("is_outline")` and `node.facts.get("evidence")` where every other rule in the file uses `node.get_fact(...)`. [4]

### cdd_guidance/practices/stories/rules/story_map.py and acceptance_tests.py

- story_map.py:42-43 `ChildCountFitsLayer.check` — dead code — `if node.type in {"Story", "Scenario"}: return []` can never hold: `node_types` is `("Epic", "SubEpic")` (line 39). [3]
- acceptance_tests.py:51-54 `_fixture_path` — put-logic-on-the-owning-resource — the rule recomputes which file an example comes from by calling `example_source_file` with the node's saved `imported_modules`; the recording already computes the same thing (`StorySource.example_source`, story_recording.py:158) and could save it as a fact. [3]

### cdd_guidance/practices/stories/model/story_channel.feature.py

- story_channel.feature.py:1-6 — no-module-per-class / source layout — a 534-line mamba spec kept in the production package under a name no test tier collects (`*_spec.py`, `*_story.test.py`, `*_heavy_spec.py`, `*_e2e_spec.py`), so it only runs when someone runs it by hand, and the command in its docstring names a path (`practices/stories/model/...`) that no longer exists. The story map (`.context/story-map.md:2317`) and `scripts/test.ps1:365` both name it as the story channel check, so it is meant to stay; the finding is that nothing runs it, the graph scanners judge it as production code, and it is the only user of `Stories.read_folder` outside `graph_reading.py`. Clean Engineering and DDD keep the same kind of file (`class_channel.feature.py`, `ddd_channel.feature.py`). Decide once for all three: rename them into the heavy tier, or delete them. [1]

### cdd_guidance/practices/stories/model/.context/story-model.md

- story-model.md:146 `Increment(name, sequential_order, stories, story_class)` — seam-names-current-code — the model document gives `Increment` a `story_class` parameter the code does not have (story_model.py:480-485 takes three). This is what the graph's "takes 4 parameters" hit on the document is seeing. [4]

### cdd_guidance/practices/stories/model/diagram_story_model.py

- diagram_story_model.py:92 `DiagramStoryNode.place`, :96 `add`, :108 `stretch`, :113 `role`, :124 `_placed_children` — eliminate-duplication (no use, delete) — none of the five has a caller outside this class, in production or in a spec; `place` only stores `_place_side` and `_place_destination`, which nothing reads. About 35 lines of unused placement API on the base every drawn format inherits. [1]
- diagram_story_model.py:43-69 `DiagramStoryNode.width` / `height` / `y` / `x` — shape-classes-around-resources — one mixin answers for a story, an epic, and an increment by testing `isinstance(self, Story)` and `isinstance(self, Epic)` in every property, although `DiagramEpic` and `DiagramStory` exist to hold exactly that difference. The draw.io, Miro, and whiteboard formats all use `LaidOutEpic` and `LaidOutStory`, which override every one of these, so the base grid (`base_width`, `row_height`, `actor_y`) is only reached by the Claude Design canvas in `ux/model/claude_design/story_canvas.py`. [3]
- diagram_story_model.py:33, :40 `DiagramStoryNode._story_line_y` / `_sub_epic_bar_y` — use-explicit-dependencies — a node on no map builds a throwaway `DiagramStoryModel()` to ask for a default line. The fallback hides that the answer depends on the format's own model (`DrawIOStoryModel.sub_epic_top` differs), so a detached draw.io node gets the wrong line without an error. [3]
- diagram_story_model.py:131 `DiagramStoryCell` — use-intention-revealing-names — "cell" is draw.io's word; the class is also the read form of a whiteboard shape and would be the read form of a Miro card. `role`, `kind`, and `depth` are strings and integers parsed from ids (`"subepic"`, `"story"`), where the model already has `StoryType` and `Epic`. A name such as `DrawnCard` with a typed role would say what it is in the story-map language. [4]
- diagram_story_model.py:305-326 `thin_slice_columns` / `thin_slice_lanes` / `thin_slice_widths` — use-typed-signatures — the three public operations pass `List[tuple]` and `dict` between each other and to two callers (`_ThinSliceDrawing`, `_ThinSliceBoard`), and `thin_slice_lanes` takes `columns` back as a parameter although the model computes it. A column (epic, sub-epic, width) and a lane (increment, stories by column) are unnamed concepts of the thin slice. [3]
- diagram_story_model.py:300 `DiagramStoryModel.save_thin_slice` — errors-out-of-existence — raises `NotImplementedError` on the base, which `ClaudeDesignStoryModel` (ux) inherits without overriding; `ThinSlicedMap.drawn_by` (`stories_formats.py:33`) calls it on any `DiagramStoryModel`. [1]

### cdd_guidance/practices/stories/model/drawio/nodes.py

- nodes.py:423 `DrawIOStoryModel.parse` — no-legacy-api-after-refactor / use-consistent-naming — `parse` is a one-line alias of `load` ("same as load"). Miro does the same (`miro/nodes.py:233`), and the whiteboard writes the same body twice (`whiteboard/nodes.py:136` and `:140`). `load` is called only by specs, `story_channel.feature.py`, and `from_workspace`; every production path uses `parse`. Two names for one job. [2]
- nodes.py:445 `DrawIOStoryModel.load` — use-consistent-naming — builds a new hard-coded `DrawIOStoryModel()` and returns it, leaving `self` untouched, where `JsonStoryModel.parse` (`json/nodes.py:291`) and `SketchStoryModel.parse` (`sketch_story_model.py:250`) fill `self` and return it, and `MarkdownStoryModel.parse` (`markdown/nodes.py:583`) returns a new one. Callers cannot know whether the adapter they hold is the map they read. [2]
- nodes.py:502-511 `load_thin_slice` — eliminate-duplication — parses the XML and finds the `mxGraphModel` a second time, with its own error text, instead of calling `_graph_model` (:457-469) eight lines above it. [2]
- nodes.py:145 `DrawIOEpic.story_xs` — eliminate-duplication (no use, delete) — its only caller is its own recursion at :151. [1]
- nodes.py:453 `DrawIOStoryModel.placed_cells` — hide-inner-details — public, returns the private `_PlacedCell`, and is called only by `load` and by `drawio_round_trip_spec.py:88,101`. A public operation that hands out a private type. [1]
- nodes.py:334-374 `DrawIOStoryModel.Vertex` — shape-classes-around-resources — a nested data holder built by a seven-argument classmethod `make` (:349, untyped parameters) and then changed from outside by three other objects: `linked` sets `node`, `take_links` sets `link`/`entry`/`code_link`, and `_KeptPlaces.place` (:299-311) overwrites `x`, `y`, `width`, `height`. The vertex owns its box but not the rule for keeping it. [3]
- nodes.py:281-320 `_KeptPlaces` and `_drawn_geometries` — eliminate-duplication — the Stories version of "keep the cards where the person moved them" for draw.io. Clean Engineering has its own in `clean_engineering/model/drawio/drawio_class_model.py:425-434` (`_previous_pages`) with `DrawioPage.positions` (`drawio/page/drawio_page.py:62-73`); the whiteboard has one shared version in `harness/whiteboard/whiteboard.py:414` (`Whiteboard.keep_places`). See proposal A2. [2]
- nodes.py:250-278 `_DrawIOPage`, :457-488 `_graph_model` / `_vertices` — eliminate-duplication — Stories' own writer and reader of the draw.io file envelope (`mxfile`, `diagram`, `mxGraphModel`, `UserObject`, `mxGeometry`). UX reads the same envelope in `ux/model/drawio/nodes.py:365-387` (`_diagram_of`, `_page_named`) with `CellStyle` (:90-118); Clean Engineering in `DrawioPage` (`drawio_page.py:20-58`), `cell_box` (:164), `style_value` (:206), `_diagram_xml` (`drawio_class_model.py:118-123`). Three parse failures name the same fault: `DrawIOParseError` (:204), `UnreadableDrawio` (`ux/model/drawio/nodes.py:71`), `UnreadableSource` (Clean Engineering). [2]
- nodes.py:211-223 `_PlacedCell.__init__` — keep-operations-single-responsibility — the role, depth, and story kind are cut out of the style string with three separate `split(":")` expressions, and UX cuts styles its own way in `CellStyle`. One style reader would serve both. [2]
- nodes.py:15-26 imports `StoryMapLinks` from `model/markdown/links.py` — one-way-deps / high-cohesion — the draw.io adapter depends on the markdown adapter package for links that are not markdown-specific (`code_link` at `links.py:88` writes draw.io editor attributes, `CODE_LINK = "hedietLinkedDataV1"` at :38). The links of a story map belong beside `story_map_files.py` in `model/`, so one format package does not import another. [1]
- nodes.py:428 `from_workspace` — use-consistent-naming — takes a file `path`; `MarkdownStoryModel.from_workspace` (`markdown/nodes.py:416`) takes a folder or a file and `on_file`/`project`; `JsonStoryModel.from_workspace` (`json/nodes.py:304`) takes a folder and neither keyword; the Miro, whiteboard, and sketch models have none. `stories.py:199` and `:253` call `formats.for_file(path).from_workspace(path, …)` on whichever adapter reads the extension. `WhiteboardStoryModel` declares `suffixes = (".whiteboard",)` and has no `from_workspace` (confirmed by importing it), so opening a `.whiteboard` story map through either line raises `AttributeError`. [2]

### cdd_guidance/practices/stories/model/whiteboard/nodes.py

- nodes.py:34-44 `_BoardStoryNode.board_key` — eliminate-duplication — a ten-character SHA-1 of the node's path. `ux/model/whiteboard/nodes.py:63-76` (`DrawnNode.board_key`, `KEY_LENGTH = 10`) is the same loop over `parent`, and `clean_engineering/model/whiteboard/whiteboard_class_model.py:79-80` (`_key`, `KEY_LENGTH = 12`) is the same hash. The lane and card keys at :75 and :210 hash a third and fourth time inline. `harness/whiteboard.WhiteboardNode` is the one base all three extend and holds no key. [2]
- nodes.py:107 `WhiteboardEpic.bars` — eliminate-duplication (no use, delete) — called only by its own recursion at :109. [1]
- nodes.py:136-142 `parse` and `load` — eliminate-duplication — identical bodies. [2]
- nodes.py:147 `take_board` — use-consistent-naming — returns a new hard-coded `WhiteboardStoryModel()`; `WhiteboardUxMap.take_board` (`ux/model/whiteboard/nodes.py:277`) fills `self` and returns nothing; `WhiteboardBoundedContextMap.take_board` (ddd) returns itself. One operation name, three contracts. [2]
- nodes.py:175-224 `_ThinSliceBoard` — eliminate-duplication — the same drawing as `_ThinSliceDrawing` (`drawio/nodes.py:536-581`): the header loop (:194-202 here, :556-563 there) and the lane loop (:208-220 here, :566-581 there) differ only in how a box becomes an element. Miro draws a third thin slice with its own column rule (`miro/nodes.py:247-255`) that ignores `DiagramStoryModel.thin_slice_columns`. About 40 duplicated lines; see proposal A3. [2]
- nodes.py:197-201, :71, :76, :105 — provide-meaningful-context — the colours (`"purple"`, `"green"`, `"yellow"`) and the element-id shapes (`epic.<key>`, `subepic.<depth>.<key>`, `story.<kind>.<key>`) are written out at five call sites for writing and re-parsed by position in `_BoardCell.__init__` (:235-240). The id format has no single owner. [3]
- nodes.py:222 `_ThinSliceBoard._map_story` — hold-state-on-the-object-not-in-parameters — looks a story up by name across the whole map for every card (`story.name == held.name`) because the increment's stories were not copied as whiteboard stories; the object is found again by its name string. [3]

### cdd_guidance/practices/stories/model/miro/nodes.py

- nodes.py:178-216 `_MiroReading` — eliminate-duplication — reads the cards in file order with an "open epic, open sub-epics" stack, where draw.io and the whiteboard read by position through `DiagramStoryModel.place_cells`. A Miro card carries the same facts (`x`, `y`, `width`, `height`, `data-role="subepic:2"`), so it could be a `DiagramStoryCell`. The stack itself is the third copy of `MapReading._open_epic` / `_open_sub_epic` (`markdown/map_reading.py:82-97`) and the sketch's recursion. A card a person drags on a Miro board is read back under the wrong epic, which the module card says a drawing never does. [2]
- nodes.py:44 `MiroShape` — hide-inner-details — public dataclass used only inside this file (grep finds no other importer). [1]
- nodes.py:313-334 `_svg_root`, `_cards_in_order`, `_local_name`, `_foreign_object` — shape-classes-around-resources — four methods of the story map that never read the map; they are a reader of the SVG document, the Miro equivalent of `_DrawIOPage`, kept on the model. [3]
- nodes.py:72 `MiroIncrement.table_row(column_count, story_column)` — hold-state-on-the-object-not-in-parameters — the increment is handed the table's column count and a name-to-column dictionary built by its owner, and finds its own stories' columns by `story.name`. [3]

### cdd_guidance/practices/stories/model/json/nodes.py

- nodes.py:61 `_example_records`, :71 `_take_examples` — prefer-class-operations — two module functions that take `Examples` as their first parameter and are called from six classes; they are operations of the examples (`examples.as_records()`, `examples.take(record)`). [3]
- nodes.py:56 `type JsonDocument = object`, and every `as_record` / `from_record` returning `Dict[str, Any]` — use-typed-signatures — public operations on seven classes pass untyped dictionaries; a missing or misspelt key (`"sequentialOrder"`) is found at run time. Acceptable at a file boundary, but `JsonDocument = object` is a type that says nothing. [4]
- nodes.py:304 `from_workspace` and :312 `parse_file` — use-consistent-naming — see the `from_workspace` finding under draw.io: this one takes neither `on_file` nor `project`, so `stories.py:98` calls the JSON and markdown adapters on adjacent lines with different arguments. [2]

### cdd_guidance/practices/stories/model/markdown/nodes.py

- nodes.py:521-568 `MarkdownStoryModel._map_text`, `_should_render_outline`, `_sub_tree_has_outline_signal`, `_is_discovery_story_map` — put-logic-on-the-owning-resource — `render` copies the canonical map into a `MarkdownStoryModel` called `story_map` and then runs four methods of `self` that take `story_map` as a parameter and never read `self`. The adapter instance acts as a doer on another instance of its own class; these are that map's own operations. [3]
- nodes.py:102 `_example_tables`, :116 `example_table_lines`, :268 `_outlined` — prefer-class-operations — module functions that take the examples or the node as their first argument; `_outlined(node, heading)` only forwards to `node.outline.written(node, heading)`. [3]
- nodes.py:58-59, :142-143 `markdown_heading: Optional[tuple]`, `markdown_parts: Optional[list]` — hide-inner-details — public fields holding positional tuples (`(name, is_outline, line)` on a scenario, `(name, line)` on a story) that `ScenarioFileReading` writes from outside (`scenario_file.py:173-174`) and `document_text` unpacks by position (:89, :163). The same idea is a named class for outlines (`OutlineLines`) and for increments (`IncrementLines`); here it is two loose fields, on two classes, with different tuple shapes. [3]
- nodes.py:341-380 `_SectionLines` — shape-classes-around-resources — a writer keyed by `id(owner)` that reaches into `(STEP_LINE, owner)` tuples and counts them down. It exists because a document part is `object` (`scenario_parts.py:20`): a string, a tuple, an example, a section, or a scenario, told apart by `isinstance` at :93, :162-166, :334-338, :362-364. [3]
- nodes.py:48 `_SCENARIOS_FILE_SUFFIX = "_story.test.md"` — single-boundary — the suffix is already `STORY_FILE_SUFFIXES[0]` in `story_map_files.py:38`, the file that owns story file names. [2]
- nodes.py:404 `opened_from`, :416 `from_workspace` — use-consistent-naming — two ways to read a markdown file into a map, with different results (one keeps the thin slice writable, one merges folders), chosen by an `isinstance(adapter, MarkdownStoryModel)` test in `stories.py:197`. [2]
- nodes.py:22 imports `cdd_guidance.practices.sketch_document.discovery_document` and `scenario_parts.py:11` imports `clean_engineering.model.call_graph.CallGraph` — low-coupling — the markdown adapter reaches into two other practices' packages; `CallGraph` is a Clean Engineering model class used here as the body of a `realization` fence. Each is a single class through a public name, so this is a note for the cross-practice list, not a breach by itself. [1]

### cdd_guidance/practices/stories/model/markdown/map_reading.py

- map_reading.py:37 `is_outline`, :42 `has_map_structure`, :48 `read_map`, :54 `read_at`, :270 `described` — prefer-class-operations — five public module functions beside three reading classes. `read_map(format, lines, file)` picks the reading and calls it; `is_outline(lines)` is asked five times on the same text by `MarkdownStoryModel.parse` and `render` (`nodes.py:538, 546, 588, 599`), each re-scanning every line. A text that knows its notation would hold the answer once. [3]
- map_reading.py:64 `MapReading.__init__(format, file)` — use-intention-revealing-names — `format` here is a `MarkdownStoryModel` instance used as a factory for epic and story types, not a format; it also shadows the builtin. The domain word "format" already means `markdown`, `drawio`, and so on. [4]
- map_reading.py:26-28 `_OUTLINE_EPIC_PATTERN`, `_OUTLINE_STORY_PATTERN`, `_OUTLINE_ESTIMATE_PATTERN` — eliminate-duplication — the outline notation (`(E) name`, `(S:kind) actor --> name`, `* estimate`) is parsed again in `sketch/sketch_story_model.py:31-33` (`_STORY`, `_OUTLINE_EPIC`, `_ESTIMATE`), with the actor split written twice (`_actor_and_name` :356 here, `SketchStory.from_match` :167 there), and written three times: `MarkdownStory.outline_lines` (`nodes.py:184`), `SketchStory.sketch_lines` (`sketch_story_model.py:203`), and `StoryMapLinks._entries_under` (`links.py:147`), which rebuilds the heading text only to compute its anchor and silently breaks every link if the heading format changes. [2]

### cdd_guidance/practices/stories/model/markdown/links.py

- links.py:30 `heading_anchor` — eliminate-duplication — an exact duplicate of `harness/markdown/markdown.py:100` `heading_anchor` (same regex, same lower-casing); DDD already imports the harness one (`ddd/model/nodes.py:17`). Only `_Anchors.next` (:48) uses the Stories copy. [2]
- links.py:25 `unlink` and `_LINK` (:21) — eliminate-duplication — the same "link to its label" regex exists as `_LINK_IN_HEADING` in `harness/markdown/markdown.py` and as `_LINK` in `ux/model/whiteboard/nodes.py:42`. [2]
- links.py:69 `StoryMapLinks.story_files`, :67-68 `map_file`, `base` — hide-inner-details — public mutable fields; no reader outside the class (`grep story_files` finds only `StoryMapFiles.story_files_below`). [1]
- links.py:106 `_heading_line` — keep-operations-single-responsibility — `code_link`, asked once for every drawn cell, re-reads and re-scans the whole `story-map.md` file to find one heading's line. The links object was "made once, when the map is placed in the folder" (class docstring) but does file reading per cell. [3]

### cdd_guidance/practices/stories/model/markdown/markup.py

- markup.py:112 `step_prose`, :117 `step_line`, :122 `step_lines` — prefer-class-operations — module functions over a `Step`, with `step_prose` switching on `isinstance(step, MarkdownStep)` and `step_lines` probing `getattr(step, "call_graph", None)`. They are how a step writes itself in markdown, kept off `MarkdownStep` because non-markdown steps are passed in. [3]
- markup.py:84 `MarkdownStep.markdown_line: Optional[tuple]` — hide-inner-details — a third positional tuple (`(keyword, text, line)`) for "the line I was read from", next to `ExampleRowLine` (:36), which is the named form of the same idea in the same file. [3]

### cdd_guidance/practices/stories/model/markdown/scenario_file.py and scenario_parts.py

- scenario_file.py:105-128 `ScenarioFileReading` — hide-inner-details — eighteen public mutable fields; `MarkdownStoryModel._scenario_document_map` (`nodes.py:608-624`) reads five of them after `read()` (`tree_heading`, `tree_heading_line`, `document_examples`, `document_parts`, and the returned sections). The reading has no result object, so the caller picks through its working state. `tree_heading` is a positional tuple `(level, name, line)` unpacked at `nodes.py:318` and `:611`. [3]
- scenario_file.py:87, :110 `scenario_type: type` — hold-state-on-the-object-not-in-parameters — the class to build is threaded from `MarkdownStoryModel._attach_markdown` through `ScenarioFiles.sections` into every `ScenarioFileReading`, always as `MarkdownScenario`. [3]
- scenario_file.py:53 `heading_of`, :58 `inferred_story_name` — prefer-class-operations — public module functions used only inside this file (grep: no other importer). [1]
- scenario_parts.py:20 `type DocumentPart = object` — use-typed-signatures — the central type of the round trip is `object`; see `_SectionLines` above. [4]
- scenario_parts.py:152 `BackgroundReading.heading(kind, name, in_scenario, read_at)` — limit-operation-parameters — four parameters including a boolean the caller derives from its own state; `ExamplesTable.heading(kind, level, title)` (:84) is the same call made beside it with the heading cut into different pieces. The heading (kind, level, title, line) is one unnamed concept passed as loose values to three objects. [3]
- scenario_file.py:37 `_PHASES` — eliminate-duplication — the keyword-to-`StepType` table is repeated as `_STEP_TYPES` in `sketch/sketch_story_model.py:36`; the "And/But continues the step before" rule is written in `_take_step` (:234-250) and again in `SketchStep.chain` (`sketch_story_model.py:110`). [2]

### cdd_guidance/practices/stories/model/markdown/thin_slice.py

- thin_slice.py:119 `thin_slice_in` — prefer-class-operations — a public module function that reads the file, builds the private `_ThinSliceReading`, appends increments to the map, and constructs `ThinSlice(path, reading, text)`. It is `ThinSlice`'s creation factory, kept outside the class, and `ThinSlice.__init__` (:91) takes the private reading only to copy two fields out of it. [3]
- thin_slice.py:123 `"thin-slice.md"` — single-boundary — the file name is one of `THIN_SLICING_FILES` in `story_map_files.py:43`. [2]
- thin_slice.py:35, :38 `IncrementLines.said`, `bullets: List[tuple]` — hide-inner-details — positional tuples (`(name, number)`, `(raw, story, name)`) unpacked at :75-81. [3]

### cdd_guidance/practices/stories/model/sketch/sketch_story_model.py

- sketch_story_model.py:46 `read_sketch_lines`, :119 `_read_steps`, :40 `_epic_name` — prefer-class-operations — module functions; `read_sketch_lines` is `SketchLines`' creation factory and `_read_steps(lines, take)` takes a callback to hand each step to its caller. [3]
- sketch_story_model.py:215-230 `SketchEpic.read_lines` and :258-271 `SketchStoryModel.read_lines` — eliminate-duplication — the same "story line or epic line" branch twice, about ten lines each. [2]

### cdd_guidance/practices/stories/app/story-map/story-map-client.ts

- story-map-client.ts:78-132 `StoryMapNode` — shape-classes-around-resources — one class stands for an epic, sub-epic, story, scenario, step, or increment, told apart by a `kind` string and an `if` chain in `client()` (:124-131). Half its operations ignore `kind` and assume one: `newSubEpic` and `newStory` always build an epic client, `newScenario` a story client, `newStep` a scenario client, `editText` a step client, so `held.nodeAt(step, 'step').newStory(…)` compiles and sends an epic call with a step's address. The generated clients (`EpicClientGenerated`, `StoryClientGenerated`, …) are already the typed objects. [3]
- story-map-client.ts:43 `nodeAt(address, kind)` — hold-state-on-the-object-not-in-parameters — every edit finds its node again from an address string and a kind string. The page first maps id to kind (`StoryMapViewModel.kinds`, `story-map-view-models.ts:135-139`; `MapEditing.kindOf`, `story-map-views.tsx:1772`, which falls back to `'epic'` for an id it does not know), then passes both back in. Callers pass `'epic'` for a sub-epic at `story-map-views.tsx:1818-1822`, because the kind is only a hint. [3]
- story-map-client.ts:135-166 `StoryMapExample`, `StoryMapIncrement` — class-not-property-instance-or-subtype — two more wrapper classes whose every method is `this.map.answerTo(XClientGenerated.named(this.map.api, this.address).op(…))`; the same line is written sixteen times across the three wrappers. [2]
- story-map-client.ts:14 `NodeKind`, and `SemanticType` (`story-map-view-models.ts:13`) — use-consistent-naming — two type names for "which kind of story node", one including `'story-map'`, one including `'step'`; `'sub-epic'` is a kind in both although the model has one `Epic`. [4]
- story-map-client.ts:57 `reorder(before, after, kind)` — put-logic-on-the-owning-resource — the client is handed two lists of ids and works out which one moved by string comparison (:58-59), because the views report a whole new order rather than the move the person made; the drop handlers already know the dragged id and the id it was dropped before (`DropEdge.beforeId`, `story-map-views.tsx:188`). [3]

### cdd_guidance/practices/stories/app/story-map/story-map-view-models.ts

- story-map-view-models.ts:15 `StepRowDto`, :26-39 `StoryNodeViewModel` fields `parent_id`, `sequential_order`, `semantic_type`, `story_type`, `acceptance_tests`, `sub_epics` — use-intention-revealing-names — a transfer-object suffix and Python snake_case in TypeScript classes, where the generated data (`StoryData.acceptance_tests`) is the only thing that needs the wire spelling. `semantic_type` is the graph's word, not the story map's. [4]
- story-map-view-models.ts:54-55 `sent`, `placeOf`, :58 `placesUnder`, :60 `stepRowsOf`, :67 `exampleTableOf`, :98 `storiesUnder` — prefer-class-operations — six module functions that take a view model or its data and rebuild it; `EpicViewModel.within` (:126) turns view models back into "sent" nodes to construct copies. [3]
- story-map-view-models.ts:121 `EpicViewModel.of` — hide-inner-details — an epic's own stories are shown as a made-up sub-epic whose id is the epic's id and whose order is 0. The views then treat an epic id as a sub-epic id, which is why the edits pass `'epic'` for sub-epics and why `kinds` cannot tell them apart. [4]

### cdd_guidance/practices/stories/app/story-map/story-map-views.tsx

- story-map-views.tsx:343, :388, :432 `makeStoryDragHandlers`, `makeSubEpicDragHandlers`, `makeEpicDragHandlers` — eliminate-duplication — three functions of about forty lines whose bodies differ in one string (`'story'`, `'sub-epic'`, `'epic'`) and the list key; each takes six or seven positional parameters (`dragRef`, `dragKindRef`, id, parent id, `getTargetIds`, `onMove`, `visuals`). About 80 duplicated lines. `makeDragHandlers` (:149) is a fourth, simpler drag implementation used for increments, scenarios, and steps. [2]
- story-map-views.tsx:575-622 `StoryHierarchyViewProps` and :623-1147 `StoryHierarchyView` — general-purpose-surface / keep-operations-small-focused — one component of about 525 lines takes thirty-six callbacks, one for each edit of each kind of node (`onAppendEpic`, `onInsertEpicAfter`, `onPrependSubEpic`, `onInsertSubEpicAfter`, …), each identified by loose id strings; several pass ids the handler ignores (`onRemoveSubEpic: (_epic, sub)`, `onRemoveStory: (_sub, story)`, `onUpdateStep: (_story, _scenario, step, …)` at :1806, :1823, :1840). The surface is shaped by the old store the page no longer has. [3]
- story-map-views.tsx:1766-1795 `MapEditing` and :1798-1856 `epicEditsOf` / `storyEditsOf` / `scenarioEditsOf` / `incrementEditsOf` — shape-classes-around-resources — a holder of (view model, edit function) plus four module functions that translate the thirty-six callbacks into client calls, looking each node up again by id through `find` over the whole map (:1777, :1781, :1818, :1833). This is the doer layer between the views and the model that typed nodes would remove. [3]
- story-map-views.tsx:1785 `MapEditing.addThenPlace` — put-logic-on-the-owning-resource — "add after this node" is done in the page as add-last, re-read the whole map into view models, find the new id as the last sibling, then move it; two server calls and an inference about which node is new. The story model's tools take a name only, so the rule lives in the page. [3]
- story-map-views.tsx:566 `colTemplate(totalCols, _leadCols)` and :521 `ColumnLayout.leadCols` — eliminate-duplication (no use, delete) — the parameter is unused and `leadCols` is always an empty set (:534, "no dedicated lead columns"). [1]
- story-map-views.tsx:32 `StoryMapPageCalls` — shape-classes-around-resources — a data holder (`api`, `failures`, `editing` ref) passed to two hooks that take it apart; `useStoryMapPage` (:85) builds a second `StoryMapApi` although `main.tsx:15` already built one for the same failures. [3]
- story-map-views.tsx:1676 `NEW_NAMES.subEpic = 'New SubEpic'`, :1509 `STEP_TYPES` — use-consistent-naming — "SubEpic", "sub-epic", "sub_epics", and "subEpic" are four spellings of one term across the app; `STEP_TYPES` repeats `KEYWORDS` (`story-map-view-models.ts:57`). [4]

### cdd_guidance/practices/stories/app/story-map-routes.ts and story-map-page.ts

- story-map-routes.ts:16 — seam-names-current-code — the comment says the routes are mounted "under STORY_MAP_API", a constant that is private to `story-map-api.ts:4`; the only exported address is `STORY_MAP_PAGE` in `story-map-page.ts:3`, a file that exists for that one line. `space/kanban/story_ui_page_heavy_spec.py:20` writes `"/story-map"` again by hand. [4]

### cdd_guidance/practices/ux/model/graph_reading.py

- graph_reading.py:24 `UnreadableDrawio` import, :25 `UxMapNotEmbedded` import — one-way-deps — the model package imports two of its format packages, and both import the model back, which is the four-package cycle the graph reports; the two exception classes are used only in `_NOT_A_MAP` at :39. [1]
- graph_reading.py:322 `_domain_practices`, :346 `_steps_reading`, :368 `_property_at` — one-way-deps / low-coupling — three imports of other practices' classes sit inside functions; the rule counts them as imports, and each is followed by a walk into that practice's reading (`reading.in_graph.nodes("Property")`, the fact `owner`) rather than a question that practice answers. [1]
- graph_reading.py:46 `_STEP_TYPES` — eliminate-duplication / single-boundary — the tuple `("Step", "Given", "When", "Then")` is Stories' knowledge of how it types a step, and UX holds it twice: here and as `_NODE_TYPES["Step"]` in `story_link.py:24`. When Stories adds a step type, both copies must be found. [2]
- graph_reading.py:343 `StoryDemoControlLinks._steps_reading` — put-logic-on-the-owning-resource — "the steps whose text is this label" is a question about Stories' nodes, answered here by reading the `text` fact of every step type; `explorer_tree.py:67-68` and `story_link.py:135,191` read the same facts (`text`, `phase`). Four UX files know the names of Stories' saved facts. [1]
- graph_reading.py:357 `StoryDemoControlLinks._screen_of` — eliminate-duplication — walks `edges.direct_parent` up to a type, the same walk as `story_link.py:204 _ancestor`, written a second time. [2]
- graph_reading.py:102 `UxMapFile`, :144 `UxMapFiles`, :189 `RecordedMap`, :248 `LinksAcrossPractices`, :256 `ServedStoryLinks`, :296 `DomainTermLinks`, :329 `StoryDemoControlLinks` — deep-module — seven public classes that only `UxReading.read_working_copy` (:86-99) makes; grep finds no other user, spec or production. They widen the module's surface for no caller. [1]
- graph_reading.py:177 `UxMapFiles._format_of` returns `tuple[UxMap, str] | None`, unpacked at :162 as `format[1], format[0]` — shape-classes-around-resources — `UxMapFile` exists to hold a file's format and text, yet a bare tuple carries them one step first, read back by position in reversed order. [3]
- graph_reading.py:105 `UxMapFile.__init__(..., format: UxMap)`, :151 `self._formats` — use-intention-revealing-names — an adapter instance of `UxMap` is called a "format" here, a "loader" in `ux_map.py:234`, and an "adapter" in `ux.py:80`; one object, three words. [4]
- graph_reading.py:42 `_NAME_MARKS`, :121 `UxMapFile.place_of` — single-boundary — the reading holds a list of how every format spells a node's name (`"name": "{}"`, `value="{}"`, `"text": "**{}**`) to guess the line a node sits on. Each format already knows how it writes a name; the list goes wrong, without a failing test, when a format changes its spelling. [1]

### cdd_guidance/practices/ux/model/story_link.py

- story_link.py:184 `key_of`, :199 `_story_name`, :204 `_ancestor`, :211 `_parent` — prefer-class-operations — four module functions that take a Stories node and reach into its type, facts, and edges to build the key a story, scenario, or step is listed by. Callers outside the file import `key_of` as a function (`graph_reading.py:27`, `claude_design/story_canvas.py:23`). [3]
- story_link.py:184 `key_of` — single-boundary / low-coupling — how a scenario or a step is keyed (`Story › Scenario › Step`) is a fact about the story map, built here in UX from Stories' node types and facts. Stories' `StoryTree` (`stories/model/graph_reading.py:260`) already answers "the epic of", "the scenarios of", "the steps of" for the same nodes; the key belongs beside them. [1]
- story_link.py:21 `_NODE_TYPES` — single-boundary — a second copy, inside UX, of which Stories node types count as a scenario (`Scenario`, `Background`) and a step. [2]
- story_link.py:93 `StoryTargets` — shape-classes-around-resources — a finder that indexes Stories' nodes by file (`_nodes_by_file` :172), reads Stories' markdown files itself (`_document` :151), and decides which node a heading names (`_under_heading` :126, `_stories_written_in` :138). The state is Stories' and the rule ("a story file's heading names the story its scenarios belong to") is Stories'; UX holds both. [3]
- story_link.py:68 `StoryLink.resolved_on(graph, written_in)` — hold-state-on-the-object-not-in-parameters — makes a new `StoryTargets(graph)` on every call with a target (:73), so the by-file index of every Stories node is rebuilt for each link; `ServedStoryLinks` works round this by holding its own `StoryTargets` and calling `node_at` directly (`graph_reading.py:266-268, 280`). Two paths to one answer. [3]
- story_link.py:39 `StoryLink.__init__(kind: str, ...)`, :47 `from_shown(kind, shown)` — use-typed-signatures / lookups by name string — `kind` is one of three strings (`"Story"`, `"Scenario"`, `"Step"`) used as a dictionary key at :80, :89, :124; a wrong string fails as a `KeyError` far from the caller. The same strings are passed through `nodes.py:80-88, 128, 154`. [3]
- story_link.py:44 `self.target = ""` set after construction at :56 — hide-inner-details — a public field the factory writes after the constructor ran; `target` cannot be given to `__init__`, so the object is made in two steps. [3]
- story_link.py:64 `written`, :104 `node_at(link, written_in)`, `nodes.py:117 lists`, `nodes.py:121 show_what` — use-intention-revealing-names — `written` is the link as a file writes it, `lists(node)` means "serves this node", `show_what(other)` means "serve everything other serves". The domain verb is *serves* (the class is `ServesStories`); the operations use *show*, *list*, and *written* for it. [4]

### cdd_guidance/practices/ux/model/nodes.py

- nodes.py:38 `story_steps_from` — prefer-class-operations — a module function used by one production class (`json/nodes.py:97, 99`) and the spec fixture; it only maps `StoryStep.from_value` over a list. [3]
- nodes.py:27 `StoryStep.from_value`, :21 `StoryStep` (`kind`, `label`) — use-consistent-naming — the step's words are `label` here and `text` in Stories (the fact read at `story_link.py:135`); its phase is `kind` here, `phase` in Stories (`explorer_tree.py:67`), and `stepKind` in the page's JSON. One step, three vocabularies. [4]
- nodes.py:78-88 `show_story`, `show_scenario`, `show_step`; :91-101 `shows`, `shows_scenarios`, `shows_steps`; :104-115 `story_keys`, `scenario_keys`, `step_keys`; :136 `story_links` — eliminate-duplication / use-property-not-accessor — ten members that each forward one of three strings to `_show`, `_shown_nodes`, `_keys`, or `_links`. `story_links` exists only for stories, so the three kinds are not even offered the same way. [2]
- nodes.py:55-62 `Interaction.trigger`, :313-320 `Transition.trigger` — eliminate-duplication — the same property and setter ("its name while it names none") written twice. [2]
- nodes.py:273 `Screen.apply_layout` — hide-inner-details — a method that strips a string and assigns `self.layout`; production code never calls it (only `ux_spec.py:32` and `drawio_ux_map_heavy_spec.py:28`), and every format assigns `screen.layout` directly. Its docstring instructs the reader about files to open, which is guidance, not behaviour. [3]
- nodes.py:254-255 `domain_terms`, `domain_concepts` — use-consistent-naming — two lists for one idea. `domain_concepts` is only copied (`ux_map.py:121`), written to JSON (`json/nodes.py:148, 164`), and used as a fallback for `domain_terms` (`drawio/nodes.py:268`, `whiteboard/nodes.py:167`); nothing links it or checks it. [4]
- nodes.py:174 `states`, :253 `inactive_tabs`, :296 `nav_type`, :171 `control_type` — use-typed-signatures — the kinds of control, the visual states, and the kinds of navigation are free strings on the model; the values that mean something are defined only in the formats (`html/nodes.py:29 _VISUAL_STATES`, `:163 _CONTROL_WRITERS`, `drawio/nodes.py:40-44`, `whiteboard/nodes.py:48`). The domain language for navigation (action, tab, top nav) has no home in the model. [4]
- nodes.py:288 `UxComponent` — use-intention-revealing-names — "component" is the name for "a transition, a content type, or a nav component", three things with nothing in common but living in a list on the map; `NavComponent` then uses the same word for something else. [4]
- nodes.py:339 `NavComponent.ux_type` — use-intention-revealing-names — the kind of navigation component (tabs, menu, breadcrumb) named `ux_type`, which says nothing; `Control` calls the same idea `control_type`. [4]

### cdd_guidance/practices/ux/model/ux_map.py

- ux_map.py:231 `from_workspace`, :238 `workspace_text`, :243 `workspace_file`, :46 `workspace_files` (and the five overrides: `drawio/nodes.py:342`, `html/nodes.py:180`, `json/nodes.py:219`, `markdown/nodes.py:26`, `whiteboard/nodes.py:231`) — no use, delete — grep finds no caller of `UxMap.from_workspace`, `workspace_text`, or `workspace_file` anywhere, spec or production; `UxReading` finds files through `map_file_suffixes` and `reads_file`. About 45 lines that describe a second, unused way to find a map's file. [3]
- ux_map.py:279 `_name_of` — eliminate-duplication / prefer-class-operations — "the screen's name, or blank for none" is written here, again at `json/nodes.py:292`, again as a method at `html/nodes.py:226`, and inline at `drawio/nodes.py:447-448`. [2]
- ux_map.py:159-162 and :224-229 — eliminate-duplication — copying a transition (new node, `trigger`, `nav_type`, `joining` the copied screens) is written twice, once in `_take_components` and once in `_keep_transitions_only`. [2]
- ux_map.py:93 `copy_of` with :116 `_screen_copy`, :133 `_region_copy`, :140 `_control_copy`, :152 `_interaction_copy`, :158 `_take_components` — put-logic-on-the-owning-resource — the map copies every field of every node type itself, so a field added to `Screen` or `Control` must also be added here, in each format's reader, and in each format's writer. `StoryDemoControl.take_story_fields` (`nodes.py:216`) shows the other shape: the node copies its own fields. [3]
- ux_map.py:174 `keep_served_by`, :188 `keep_what_only` — use-intention-revealing-names — both mean "merge what the file already holds into this map"; neither name says merge, and "what only" is not a phrase a reader can parse without the docstring. [4]
- ux_map.py:86 `create(name: str | Graph = "UxMap", ...)` — limit-operation-parameters — the first parameter is a name or, in place of a name, a graph; one positional parameter with two meanings chosen by type. [3]
- ux_map.py:58 `reads_file`, :46-56 `workspace_files`, `holds_screens`, `map_file_suffixes` on `UxMap` — keep-classes-single-responsibility — `UxMap` is the domain root (screens, transitions, context), the base of every format adapter (`parse`, `render`, `save`), and the description of each format's files. A `DrawioUxMap` used as an adapter is an empty map whose only job is to make other maps (`type(self).create()` at `drawio/nodes.py:361`, `json/nodes.py:237`, `markdown/nodes.py:36`, `whiteboard/nodes.py:273`). [3]
- ux_map.py:36-42 `screen_type` … `nav_component_type`, including `content_type_type` — use-intention-revealing-names — `control_type` on `UxMap` is a class, while `control_type` on `Control` (`nodes.py:171`) is a string such as "button"; `drawio/nodes.py:181` takes a parameter `control_type: type[DrawioControl]` two lines from code that reads `control.control_type` as a string. [4]

### cdd_guidance/practices/ux/model/ux_node.py and collections.py

- ux_node.py:31 `UxNode._renumber(nodes)` — hold-state-on-the-object-not-in-parameters — a method that never reads `self`; every caller passes one of the node's own lists (`nodes.py:188, 236, 271`, `ux_map.py:270`, `collections.py:30, 36`, where another object calls the owner's private method). The list should renumber itself when it changes. [3]
- collections.py:32 `UxComponentCollection.remove`, :40 `find` — no use, delete — no caller in production or specs. [3]
- collections.py:13 `UxComponentCollection` beside `ModelChildren` — do-not-invent-parallel-object-models — screens, regions, controls, and interactions are plain `ModelChildren` lists with `append_*` methods on the owner; transitions, content types, and nav components get a second list class that wraps a `ModelChildren` and re-implements `__iter__`, `__len__`, `__getitem__`, `__bool__`. Two shapes for "an ordered list of children the node owns". [2]
- reference_paths.py:26 `clear`, :16 `add` (as a public operation), :41-53 `__contains__`, `__getitem__`, `__eq__` against a list — deep-module — `ReferencePaths` is a de-duplicated list of strings with eleven members; production code calls only `replace`, `as_list`, iteration, and truthiness. `clear` has no caller at all. [1]
- model/__init__.py:3-36 — no-legacy-api-after-refactor / deep-module — the package re-exports sixteen names, and no file anywhere imports from `cdd_guidance.practices.ux.model` itself; every importer names the file. The list is a second, unused seam that must be kept in step by hand (it already lacks `ServesStories`, `StoryStep`, `StoryLink`). [1]

### cdd_guidance/practices/ux/model/json/nodes.py

- json/nodes.py:53, :119, :134, :175, :194, :208 `from_record(record, index, ux_map)` — hold-state-on-the-object-not-in-parameters — six class methods each handed the map so they can look screens up by name (`ux_map.screen_named`) and pick node types (`ux_map.control_type`). `JsonContentType.from_record` (:194) takes `ux_map` and never uses it. [3]
- json/nodes.py:54 `JsonControl.from_record` returns `ux_map.story_demo_control_type` or `cls` — prefer-instance-operations — a factory on one class that builds a different class chosen by the record; the choice of node type belongs to the map, which holds the types. [3]
- json/nodes.py:211 `ux_map.find_screen(name)` against :72, :144, :178 `ux_map.screen_named(...)` — use-consistent-naming — two lookups of a screen by name on one object: `find_screen` raises for a missing name, `screen_named` returns none for a blank one. Nav destinations use one, everything else the other. [4]
- json/nodes.py:37-46 `read_served` / `served_record` write `story_names`, `scenario_names`, `step_names`; the model calls them `story_keys`, `scenario_keys`, `step_keys` (`nodes.py:104-115`) and the graph facts use the `_keys` names (`nodes.py:167`) — use-consistent-naming — one list, two names, and the JSON name ("names") is wrong for a scenario, which is written as a key or a markdown link. [4]
- json/nodes.py:245 `JsonUxMap.read_record`, :275 `map_record` — deep-module — public, called only from `parse` (:238) and `save` (:273) of the same class. [1]

### cdd_guidance/practices/ux/model/html/nodes.py

- html/nodes.py:163 `_CONTROL_WRITERS` — lookups by name string — a module dictionary from a control type's string to an unbound method of `HtmlControl`, called as `writer(self, visual)` at :41. The control looks its own method up by name in a table outside itself. [3]
- html/nodes.py:226 `HtmlUxMap._name_of` — eliminate-duplication — third copy of the same helper (see `ux_map.py:279`). [2]
- html/nodes.py:266 `_text` — prefer-class-operations — a module function; small, used by two classes in the file. Reported for completeness with the other module functions; acceptable where it is if the two classes stay in one file. [3]
- html/nodes.py:36 `HtmlControl.html()`, :49 `data_attributes()`, :53 `input_key()` — use-property-not-accessor — three derived values with no parameters written as operations; `data_attributes` and `input_key` have no caller outside the class. [3]
- html/nodes.py:207 `ExplorerTree(list(self.screens)).as_json()` — see explorer_tree.py. [—]

### cdd_guidance/practices/ux/model/explorer_tree.py

- explorer_tree.py:15 `type ExplorerEntry = dict`, and every method returning `dict` (:37, :41, :50, :55, :61, :93) — use-typed-signatures — the story explorer's tree is built as untyped dictionaries with string keys (`kind`, `screenName`, `scenarioKey`, `stepKind`), which the JavaScript reads by the same strings (`story-demo/screen-tree.js`). Nothing ties the two sides together. [4]
- explorer_tree.py:87 `shown[0].practice.reading.story_tree` — low-coupling — reaches from the first linked story node through its practice to Stories' reading to its story tree; four steps into another practice from a node. [1]
- explorer_tree.py:41 `ExplorerScreen.placed_entry(order, place)` with :123 `ExplorerTree._placed` writing `self.screen_keys` as a side effect at :130 — keep-operations-single-responsibility — a method named for what it returns also records, the first time each screen is seen, the keys that open it. [3]
- explorer_tree.py:76 `ExplorerTree` against `claude_design/story_canvas.py:302 _explorer`, :315 `_story_entry`, :319 `_scenario_entry` — eliminate-duplication — two builders of "the story explorer's tree" for two pages: this one from graph nodes with readable keys, the other from story model objects with one-letter keys (`n`, `u`, `s`, `c`, `t`, `x`, `i`, `p`, `b`, `f`). About 60 lines each do the same walk (epic, sub-epic, story, scenario, steps). [2]

### cdd_guidance/practices/ux/model/drawio/nodes.py

- drawio/nodes.py:311 `Callout._corner` — prefer-instance-operations — a classmethod that takes a cell and returns its corner; it is a classmethod only because `Callout.under` (:299) needs it before a callout exists. The cell is the owner; `CellStyle` (:90) already wraps a cell. [3]
- drawio/nodes.py:480 `_is_annotation`, :489 `_plain_text` — prefer-class-operations — two module functions that read a cell's text, called from four classes; with `CellStyle` and `_corner` they are four separate readers of one `mxCell`. A single drawn-cell object would own style, text, corner, and "is an annotation". [3]
- drawio/nodes.py:36 `_BESIDE`, :49 `_SERVED_HEADINGS`, :128 `DrawnServed.serve_listed`, :332 `Callout._listed`, :414 `_nav_type_of` against `whiteboard/nodes.py:33 _BESIDE`, :35 `_SERVED_HEADINGS`, :90 `ServedOnCard.read_served_lines`, :330 `_listed`, :215 `read_arrow` — eliminate-duplication — the drawing's callout and the board's card write what a screen serves in the same notation (`Stories: A · B`, `Domain terms: X · Y`, a dashed line is a tab) and each file holds its own constants, writer, and reader for it. About 40 lines twice. [2]
- drawio/nodes.py:26 imports `Control` … and :27 `KEY_SEPARATOR` used at :275 and :286 for `"{region.name} › {control.name}"` — use-consistent-naming — the separator that joins a story key's parts is reused to join a region and a control into a place name, a different idea that happens to share a character. [4]
- drawio/nodes.py:189 `DrawioRegion.cli_record`, :255 `DrawioScreen.cli_record`, :440 `DrawioUxMap.cli_state` — abstraction-focus — the public operations of the drawing's nodes are named for the mechanism (a command line and its state file), not for what they give: this region, screen, or map as the drawing shows it. [4]
- drawio/nodes.py:372 `read_pages`, :440 `cli_state` — deep-module — public, called only inside `DrawioUxMap` (`parse` :362, `save` :464); no spec calls either. [1]
- drawio/nodes.py:219 `DrawioScreen.read_detail(detailed, ux_map)`, :181 `DrawioRegion.read_controls(cell, control_type)` — hold-state-on-the-object-not-in-parameters — the map is passed down so a screen can ask it for node types (`ux_map.control_type`, `ux_map.region_type`), and then the control type alone is passed one layer further. A screen that is on a map already has that map as its parent. [3]
- drawio/nodes.py:437 `drawn.cli_timeout_seconds = self.cli_timeout_seconds` — hold-state-on-the-object-not-in-parameters — the adapter copies its own setting onto the copy it makes, because the adapter and the map it writes are two instances of one class. [3]

### cdd_guidance/practices/ux/model/whiteboard/nodes.py

- whiteboard/nodes.py:30 `KEY_LENGTH`, :70 `DrawnNode.board_key` — eliminate-duplication — a node's id on a board as a SHA-1 of its path, cut to a length, is written here, in `stories/model/whiteboard/nodes.py:30, 38-44`, and in `clean_engineering/model/whiteboard/whiteboard_class_model.py:47, 80`. `harness/whiteboard/whiteboard.py:283 WhiteboardNode` is the shared base all three extend and holds none of it. [2]
- whiteboard/nodes.py:209 — eliminate-duplication — the same hash is written out a second time inline for a transition's id. [2]
- whiteboard/nodes.py:326 `_lines_of`, :330 `_listed`, :337 `_card_height` — prefer-class-operations — three module functions; `_card_height` is how tall a card of given text is drawn, called from `WhiteboardControl.height` (:107) and `WhiteboardScreen` (:173, :180). The text and its height belong to one card object. [3]
- whiteboard/nodes.py:180 `self._serves_box` — temporal-independence — `WhiteboardScreen.board_elements` (:190) reads `_serves_box`, which exists only after `lay_out` (:176) ran; `box` has a class default (:67) and `_serves_box` has none, so calling `board_elements` first raises `AttributeError`. [3]
- whiteboard/nodes.py:307 `_Drawn` — use-intention-revealing-names — a board's elements sorted in reading order, named with a bare participle; `DrawnNode` (:63) and `DrawnServed` (`drawio/nodes.py:120`) use "drawn" for unrelated things. [4]
- whiteboard/nodes.py:259 `board`, :277 `take_board` — deep-module — `take_board` is public and called only from `parse` (:274). [1]

### cdd_guidance/practices/ux/model/markdown/nodes.py

- markdown/nodes.py:40 `read_context`, :75 `written_onto` — deep-module — public, called only from `parse` (:37) and `render` (:73) of the same class; no UX spec calls them. [1]
- markdown/nodes.py:75 `written_onto(previous, held)` — limit-operation-parameters — `held` is always `self.parse(previous)` (:73); the caller passes a text and the map read from that same text. [3]

### cdd_guidance/practices/ux/model/claude_design/nodes.py and story_canvas.py

- story_canvas.py:25-30 — low-coupling — UX subclasses Stories' `DiagramStoryModel`, `DiagramEpic`, and `DiagramStory` and reads `Scenario`, `Step`, `Background` attributes (`step.keyword`, `step.text`, `step.ands` at :338-339, :407), none of which the Stories card offers to other packages. Stories cannot rename `ands` or `columns.leaf_epics()` without breaking UX. [1]
- story_canvas.py:128 `ClaudeDesignStoryModel` — domain-nouns-only / use-intention-revealing-names — the class draws a canvas (story map page, story explorer, screens, context panels); it is a `StoryModel` only by inheritance, and its `parse` (:160) raises. The card and the file name both call it the story canvas. [4]
- story_canvas.py:116 `StoryCanvasSetup` — shape-classes-around-resources — three fields and no behaviour, made to carry `workspace`, `ux_map`, and `sources` into a constructor (:144) and into `render` (:153), which then makes a second `ClaudeDesignStoryModel` from them (:157). The adapter and the thing it draws are again two instances of one class. [3]
- story_canvas.py:153 `render(canonical, previous, setup)` — limit-operation-parameters — `previous` is accepted and never read. [3]
- story_canvas.py:394 `shown_on`, :403 `_steps_of` — prefer-class-operations — two module functions; `shown_on(node, screens)` takes a story node and the screens and reaches into `node.graph.edges`; `_steps_of` uses `getattr(step, "ands", [])` to read a Stories attribute it is not sure exists. [3]
- story_canvas.py:68 `shown_screens(screens: List) -> List[tuple]`, :81 `_step_screens`, :236 `_story_map() -> tuple`, :351 `_screen_of(...) -> tuple` — use-typed-signatures — bare `tuple` and `List` results read by position (`found[2]` at :285; `(scenario, step, screen)` at :287). [3]
- story_canvas.py:306, :317, :328, :343 — use-intention-revealing-names — the explorer's data is written with one-letter keys (`n`, `u`, `s`, `f`, `c`, `b`, `p`, `t`, `x`, `i`); the reader is `explorer.dc.html`. Neither side names what a key holds. [4]
- story_canvas.py:291 `f"{scenario.name} › {step.text}"` — eliminate-duplication — the key separator written as a literal one import away from `key_of`, which the file already uses at :329. [2]
- story_canvas.py:60 `(self.actors or ["Customer"])[0]` — provide-meaningful-context — a story with no actor is drawn as "Customer", a word from one product's domain, as an unnamed default. [4]
- claude_design/nodes.py:53 `names(files)`, :58 `title(name)`, :61 `page_of(name)`, :65 `pages(files)`, :68 `boards(files)` — hold-state-on-the-object-not-in-parameters / use-intention-revealing-names — every operation takes the artboard files already in the canvas folder, which the caller reads and passes each time (`story_canvas.py:175, 182`); `names` and `title` say nothing about what they name (prototype artboards). [3]
- claude_design/nodes.py:20 `ClaudeDesignScreensNotReadable(NotImplementedError)` against `story_canvas.py:161` bare `NotImplementedError` — use-exceptions-properly / use-consistent-naming — the same refusal ("this format is not read back") is a named failure in one file and a bare built-in in the file beside it. [4]

### cdd_guidance/practices/ux/model/view/front_end_view.py, reshaped_view.py, view_formats.py

- reshaped_view.py:56 `Component`, front_end_view.py:669 `FrontEndView.components` — put-logic-on-the-owning-resource — a view's components are the heart of a view, yet `FrontEndView.components` returns names, `props` returns a dictionary, and `declared_components()` (:693) returns `(name, position)` pairs for someone else to build the real `Component` from (`reshaped_view.py:213-215`). The object that models a component lives in the file about merging. [3]
- front_end_view.py:693 `declared_components() -> list[tuple[str, int]]`, :653 `taken_apart(opening: int)`, :649 `scanned` — hide-inner-details — the public seam of a view is character positions in its text and the scanner itself (`view.scanned.text`, `.code`, `.line_start`, read at `reshaped_view.py:62-69, 221, 272`). A caller must know that `opening` is the index of a `(`. [4]
- reshaped_view.py:63 `self._annotations = TypeAnnotations(view.scanned)` — keep-classes-single-responsibility — `TypeAnnotations` is "the annotations of a view, as the edits that drop them", but `Component` makes one only to ask where a function's body opens (`body_after`, `arrow_after`, `front_end_view.py:280, 289`). Finding a function's body is reading the code, which is `ViewText`'s job. [3]
- front_end_view.py:349 `TypeAnnotations._statement_end` and reshaped_view.py:186 `Component._statement_end`; bracket-depth loops at front_end_view.py:472-476, :717-722 and reshaped_view.py:134-139, :189-195 — eliminate-duplication — "where does this statement end" and "which characters sit outside every bracket" are each written more than once across the two files, with small differences (one counts only braces, the other all three brackets). About 35 lines; both belong on `ViewText` beside `closing` and `line_end`. [2]
- reshaped_view.py:169 `_empty_function_from(self, value: int)` — avoid-vague-parameter-names — `value` is the position where the assigned expression starts. [4]
- reshaped_view.py:43 `ComponentMember` (`lead`, `start`, `end`, `written_new`) — hide-inner-details — a frozen record of three text positions and a string, which `ReshapedView._keep` and `_add` (:237-251) read to build edits; the member cannot say "mark me" or "write me into this component", so the merge logic lives in the doer `ReshapedView`. [3]
- reshaped_view.py:199 `ReshapedView` with :208-209 public `kept`, `added` — shape-classes-around-resources — the result is built by side effect on public lists while `reshaped()` (:211) runs; calling `reshaped()` twice doubles every entry. [3]
- front_end_view.py:645 `FrontEndView.semantic_type()` — use-property-not-accessor — returns a constant string; no production caller in UX (the other practices' `semantic_type` comes from `ModelNode`). Kept for a caller that may live in the framework; verify before deleting. [3]
- view_formats.py:12 `ViewFormat.reshape` calls `self.parse`, which `ViewFormat` does not declare — hide-inner-details — the base relies on a method only its two subclasses define; `ViewFormat` used on its own fails with `AttributeError`. [3]

### cdd_guidance/practices/ux/ux.py

- ux.py:98 `javascript_practice` — deep-module — public, called by `ensure_javascript` (:96) and one spec (`ux_spec.py:207`). [1]
- ux.py:50 `UxFormats._incoming` — hide-inner-details — overrides a private hook of the framework's `PracticeFormats` (`harness/guidance/practice_formats.py:308`) to switch off "a code format's text that starts with a brace is JSON". The framework rule is right for Stories' and Clean Engineering's file trees and wrong for a view; the difference is expressed by overriding an underscore method of another module. [1]

### cdd_guidance/practices/ux/story-demo/mount-generated-mockup.js

- mount-generated-mockup.js:272 `paintCharacterTree`, :282 `paintAbilities`, :486-488 — general-purpose-surface — the generic mockup runner paints a `character` and its `abilities` into `[data-character-tree]` and `[data-ability-list]`. No UX format writes either attribute (grep: these two lines are the only hits in the repository), so the code serves one old product's hand-written page. [4]
- mount-generated-mockup.js:23 `SESSION_KEYS = ["cart", "product", "catalog", "paymentMethod"]` — general-purpose-surface — which domain values carry from one story to the next is a fixed list of one shop's nouns inside the shared runner; a mockup for any other domain carries nothing. [4]
- mount-generated-mockup.js:25-131 and :272-354 — prefer-class-operations — sixteen module functions (`readBound`, `isBoundListHost`, `controlsOn`, `explorerChromeOn`, `itemStoryStepsFor`, `pickNameOf`, `formatItemLabel`, `paintBoundFields`, `showScreensForStory`, `showScreen`, `selectWithinRegion`, …) beside six classes; most take `root` or `snapshot` as a parameter that `GeneratedMockup` (:527) and `ProductPanel` (:477) already hold. [3]
- mount-generated-mockup.js:479 `ProductPanel(mockup)`, :362 `ExplorerPanel(mockup, chrome, expansion)` — hide-inner-details — each panel is handed the whole `GeneratedMockup` and reads through it (`this.mockup.page.runner.scenario`, `this.mockup.frame.emphasis`, `this.mockup.root` at :484-492). The panels and the mockup know each other's insides both ways. [3]
- mount-generated-mockup.js:527 `GeneratedMockup` (24 methods, :533-731) — keep-classes-single-responsibility — one class activates stories, carries values between stories, plays steps, wires clicks on controls, list lines, navigation, and screens, and repaints. [3]

### cdd_guidance/practices/ux/story-demo/paint-reflect.js, play-dual-runner/play-dual-runner.js, story-demo-page.js

- paint-reflect.js:8 `PaintReflect` — layer-separation — a class whose one method forwards to `storyDemoFrame.bind(snapshot)` (:13-14). [2]
- play-dual-runner/play-dual-runner.js:73-74 and story-demo-page.js:109-110 — eliminate-duplication — because `PaintReflect.apply` only calls the frame's `bind`, each of these two places gives the same snapshot to the same frame twice in succession (`paintReflect.apply(snapshot)` then `storyDemoFrame.bind(snapshot)`). [2]
- play-dual-runner/play-dual-runner.js:13 `PlayDualRunner` — use-intention-revealing-names — "dual" refers to running in the browser and under Node, which is `story-test-core`'s concern; the class plays one scenario's steps. `PaintReflect` and `ThenFeedback` are likewise named as verb pairs, not things. [4]
- play-dual-runner/play-dual-runner.js:32 `start(story, scenarioIndex)` sets `scenario.index = 0`, and :57 `scenario.index += 1` — put-logic-on-the-owning-resource — the runner advances a counter that belongs to `CollectedScenario` (`story-test-core.js:66-71`), which has `currentStep` but no "play next step" of its own. [3]
- story-demo-page.js:50 `static load(createStory, collectMode, demoSetup)` and :56 `load(createStory, collectMode)` — use-consistent-naming — a static and an instance operation with one name and different results (a page; a story). [4]
- story-demo-page.js:132 `playNextInvocations`, :33 `_playNextCount` — no use in production — a counter kept only so a spec can read it. [3]

### cdd_guidance/practices/ux/story-demo/control.js, story-demo-frame.js, explorer-frame.js

- control.js:71 `trigger === "create character" ? "click" : trigger` — general-purpose-surface — one product's trigger text is special-cased in the shared control reader. [4]
- control.js:43-44 `this.bound_field`, `this.story_steps` beside `controlType`, `fromBoundList`, `inputKey` — use-consistent-naming — two fields keep the Python spelling inside a class that is otherwise camelCase; `story-demo-frame.js:28, 35-36` and `story-test-core.js` read them by those spellings. [4]
- control.js:10 `Control` / :32 `StoryDemoControl` against `model/nodes.py:162, 191` — do-not-invent-parallel-object-models — the JavaScript classes share names with the model's and hold a different set of fields (`element`, `value`, `emphasized`, `tinted`); nothing generates one from the other, and `interactions` holds `{trigger, effect}` where `effect` is a function in one place (`story-demo-page.js:36-41`) and a string in another (`control.js:72`). [2]
- story-demo-frame.js:26 `controlFor(whenLabel)` and control.js:117 `matchesStep(step)` and `story-test-core.js:122 stepMatching` — eliminate-duplication — "does this control run this step" is compared by `kind` and `label` in three places. [2]
- explorer-frame.js:63 `showStory` stores the story as `this.storyTree`; :11 `StoryMapList` is stored as `this.storyMap` — use-intention-revealing-names — a single story is called a tree, and a list of story titles is called the story map. [4]
- explorer-frame.js:73 `showsStepLabels`, :82 `currentStepHighlighted`, :94 `messageVisible`; story-demo-frame.js:41 `shows`, :75 `emphasizedFor`, :88 `hasTint` — no use in production — six query methods read only by `story-demo.spec.js`; the page draws from the fields directly. [3]

### cdd_guidance/practices/ux/story-demo/play-dual-runner/story-test-core.js, map-mockup-boot.js, bind-flow-zoom.js, screen-tree.js

- story-test-core.js:12 `activeCollector`, :14 `testBackend`, :21 `setTestBackend` — use-explicit-dependencies — two module-level variables decide what `story()` and `scenario()` do; a story file's behaviour depends on which module was imported first. This is the documented design (browser and Node from one story file), so it is recorded as a known cost rather than a defect to fix now. [3]
- story-test-node.js:35-40 `input`, `session` — eliminate-duplication — the Node backend re-implements `CollectedScenario.input` and `session` (`story-test-core.js:97-108`) with different behaviour (defaults only). [2]
- map-mockup-boot.js:108 `mountMapMockup`, bind-flow-zoom.js:85 `bindFlowZoom` — prefer-class-operations — module functions that only construct one class and call one method; acceptable as page entry points, noted so they are not counted as a pattern to copy. [3]
- map-mockup-boot.js:47 `_treeHandlers` and mount-generated-mockup.js:410 `_treeHandlers`; map-mockup-boot.js:40 `_paintTree` and mount-generated-mockup.js:388 `_paintScreenTree` — eliminate-duplication — two pages each build the screen tree's model and handlers for `ScreenTree`; the IA page's version is the mockup page's with the story handlers empty (`onStory() {}`, `onScenario() {}`). [2]
- screen-tree.js:21-123 — prefer-class-operations — eight module functions (`svgEl`, `glyph`, `nounPattern`, `appendNouns`, `stepLabel`, `childList`, `emptyItem`, `readExplorerTree`) that `ScreenTree` (:188) alone uses, apart from `readExplorerTree`. [3]

### cdd_guidance/actions/render/render.py

- render.py:69 `_render_files` — hold-state-on-the-object-not-in-parameters — `format`, `paths` and `source` are handed from `render` to `_render_files` to `_saved_by_declared_paths` to `_saved_code` as loose strings, though `harness/guidance` already has `RenderRequest` to carry one render; every layer is another place to pass the wrong one. The graph's three parameter-count hits on this file (lines 69, 86, 109) are real. [3]
- render.py:77 `_render_files` — hold-state-on-the-object-not-in-parameters — `Format(format)` is built four times in six lines (77, 78 twice, 79) and `Format(source)` three more times in `_saved_by_declared_paths` (94, 98, 102); the guardrails name "a Format built from a string" as a part to build once and keep. [3]
- render.py:45 `render` — use-typed-signatures — the public operation returns a bare `list` of dictionaries whose keys differ by path taken (`path` or `paths`, `migrate`, `board`, `batches`, `content`); `_saved_by` (105) and line 101 (`isinstance(rendered.get("content"), dict)`) then sniff the keys to learn which kind of result they hold. The graph's "generic container" hit on `result` is real. [3]
- render.py:120 `_saved_code` — low-coupling — `getattr(formats.adapter(format), "reshape", None)` reaches for an operation that is not on the `FormatAdapter` protocol (`harness/guidance/practice_formats.py:31-39`), so the seam between Render and a practice's adapter is a name nobody declared; an adapter that misspells `reshape` silently falls back to the generic writer. [1]
- render.py:115 `_saved_code` — eliminate-duplication — the normalisation `{label: [names] if isinstance(names, str) else list(names) ...}` of a fidelity's outputs is written here, at `rendered_file.py:112`, and twice in `harness/guidance/declared_outputs.py` (111, 119); `DeclaredOutputs` should answer the paths of a format once. [2]
- render.py:86 `_saved_by_declared_paths` — keep-operations-single-responsibility — one operation decides among five outcomes (code, saved graph, beside the source, the file itself, a file for each name) with nested conditions on the result's shape; `_render_files` above it decides three more. The choice of where a render is saved is spread over two operations and two classes (`RenderedFile.from_sources`, `RenderedFile.beside_itself`, `RenderedFile.from_graph`, `RenderedCode`). [3]
- render.py:62 `render` — use-consistent-naming — "is this the whiteboard format" is asked as `Format(format).name == WHITEBOARD` here, at `generate.py:133`, and at `rendered_file.py:144`, and "is this a diagram" as `format.group == "diagram"` at `rendered_file.py:63`, `worker_render.py:107` and through `SAVED_GROUPS` at `render.py:78`; the question belongs on `Format` as a property. [4]
- render.py:1 module docstring, render.py:37 class docstring — use-consistent-naming — "context tool" is an earlier word for Guidance; the same phrase is at `generate.py:1,25`, `document.py:1,17`, `satisfy.py:19`, `validate.py:1,42`. A reader who searches for Guidance does not find these, and one who reads them looks for a class that is gone. [4]

### cdd_guidance/actions/render/rendered_file.py

- rendered_file.py:66 `from_sources` — put-logic-on-the-owning-resource — deciding which declared file a source belongs to and where its counterpart in another format goes is the fidelity's knowledge (`DeclaredOutputs.includes`, `file_name_beside`, `saved_beside`); this factory repeats the decision around those calls with its own conditions (84-92), so the placement rule has two authors. [2]
- rendered_file.py:105 `from_graph` — put-logic-on-the-owning-resource — filling a declared path's named part (`_NAMED_PART.sub(scope, declared[0])`, 120) duplicates `DeclaredFile.named_with` (`harness/guidance/declared_outputs.py:53`); `_NAMED_PART` itself is defined here (22) and again at `rendered_code.py:55`. [2]
- rendered_file.py:123 `_scope_of` — prefer-instance-operations — a classmethod that is not a factory: it opens a `SavedGraph`, picks the practice's node files and names a folder. It takes `graph_file`, `fidelity` and `declared`, none of which the class holds, which shows it belongs to the saved graph and the fidelity. The graph hit is real. [3]
- rendered_file.py:24 `WHITEBOARD`, rendered_file.py:27 `SAVED_GROUPS` — single-boundary — two facts about formats are module constants of one action's helper file, and other modules import them from there: `generate/generate.py:16` and `space/session/format_alignment.py:36`. A fact about formats that `space` needs belongs with `Format` in `harness/markdown`, not in an action's private file. [1]
- rendered_file.py:135 `save` — use-typed-signatures — takes `rendered: dict` and returns `dict`; the graph's "generic container" hit is real, and it is the same missing result type as in `render.py:45`. [3]

### cdd_guidance/actions/render/rendered_code.py

- rendered_code.py:99 `RenderedCode.__init__` — hold-state-on-the-object-not-in-parameters — seven parameters, six of them read off one fidelity by the only caller (`render.py:113-121`: `worked.session_output.root`, `worked.declared.outputs` twice, the format's adapter, the source's stem). Holding the fidelity, the format and the source would be three. The graph hit is real. [3]
- rendered_code.py:59 `own_name`, rendered_code.py:76 `_says_where_name_ends` — prefer-class-operations — two module functions that read a name off a declared path; `own_name` is called from `rendered_file.py:130` and from `RenderedCode` (195, 225). They take the declared paths as a parameter because they are not on the object that holds them: `DeclaredFile` already has `parts_of` and `pattern` for the same purpose. [3]
- rendered_code.py:147 `_placed` — keep-operations-single-responsibility — five ways to place rendered code are chosen by the shape of `content` (dictionary or text, banners or none, one source or none); together with `_section_file`, `_named_for_source`, `_counterpart_of` and `_beside_source` (181-233) this is about 90 lines of declared-path arithmetic outside `DeclaredOutputs`. [2]
- rendered_code.py:141 `_migration` — avoid-vague-parameter-names — reads the owner of a kept member out of a string with `kept.rpartition(".")`; `Reshaped.kept` is a list of strings that mean a member name in one writer and a sentence such as "3 line(s) set apart" in another (`reshaped_code.py:248`, `kept_document.py:70`), so this parse can read a sentence as a member. [3]
- rendered_code.py:50 `_BANNER` — low-coupling — Render finds each piece of rendered code by a banner comment (`# === Ordering · Cart ===`) that Clean Engineering's code class model writes; the two agree only through this regular expression and the separators at lines 52-54, so a change to the banner in the practice breaks the save without any type error. [1]

### cdd_guidance/actions/render/reshaped_code.py

- reshaped_code.py:85 `CodeOutline` — eliminate-duplication — an outline of a code file's members by line (name, first comment line, start, end, indent) is written here and three more times: `SpecBlock`/`SpecOutline` (`bdd/model/spec_reshape.py:32,58`), `ComponentMember`/`Component` (`ux/model/view/reshaped_view.py:44,56`), `CodeBlock` (`stories/model/story_file.py`, used by `reshaped_story_file.py:26`). Each has its own `_lead_of` (here :100, `spec_reshape.py:72`, `reshaped_view.py:122`). [2]
- reshaped_code.py:37 `NO_LONGER_IN_MODEL` — eliminate-duplication — the marker text is defined five times: here, `kept_document.py:33`, `bdd/model/spec_reshape.py:26`, `stories/model/reshaped_story_file.py:34`, `ux/model/view/reshaped_view.py:29`. A later render recognises a kept member by this text, so one copy changed alone makes every render keep the member again. [2]
- reshaped_code.py:340 `_is_marked`, reshaped_code.py:344 `_set_apart` — eliminate-duplication — "was this member already set apart" and "the line that marks it" are written again at `spec_reshape.py:171,174`, `reshaped_view.py:114,241`, `reshaped_story_file.py:132-140`. [2]
- reshaped_code.py:235 `ReshapedCode._set_apart` — eliminate-duplication — the fall-back that puts the file's unplaced lines below the render is the same algorithm as `KeptDocument._markdown` (`kept_document.py:59-70`): find the heading, carry what an earlier render set apart, collect lines the render lacks, write them under the heading. About 12 lines each. [2]
- reshaped_code.py:223 `onto` — eliminate-duplication — the test "is this line anywhere in the new text" (`any(line.strip() in kept for kept in held)`) is written at 223 and 242 and at `kept_document.py:64,65`; it compares every line with every line, and it is the rule that decides whether a render may be written. [2]
- reshaped_code.py:216 `ReshapedCode.__init__` — eliminate-duplication — `"#" if language.name == "python" else "//"` restates `CodeLanguage.line_comment` (`clean_engineering/model/code_body.py:50`), and `CodeOutline` chooses between two parsers by `language.name == _PYTHON` (92). The action holds language knowledge that a practice model already owns. [1]
- reshaped_code.py:63 `Member` — use-intention-revealing-names — `Member` stands for a class, a function or an operation of a code file by its line numbers; the name says none of that, and Clean Engineering's model already uses class, operation and property. `_FileEdit` (251) is likewise named for mechanism. [4]
- reshaped_code.py:123 `_python_member` — limit-operation-parameters — four parameters (`start`, `last`, `opened`, `floor`) for a private parser step; the graph hit is real but small. [3]

### cdd_guidance/actions/render/kept_document.py

- kept_document.py:47 `onto` — shape-classes-around-resources — one class switches on the format's name (52, 55) to do three unrelated jobs: merge markdown lines, merge draw.io XML cells, merge whiteboard JSON elements. Each practice's draw.io and whiteboard adapter already takes `previous` and keeps layout (for example `stories/model/drawio/nodes.py:281,394-404`, and 20 `render(..., previous=...)` adapters across the practices); the module docstring says this class then keeps "whatever the adapter did". Kept layout is therefore handled twice for every drawing. [2]
- kept_document.py:109 `_whiteboard` — low-coupling — reads and writes the whiteboard file as raw JSON (`before["elements"]`, `after["order"]`, `x`, `y`, `text`) although `harness/whiteboard` owns that file through `Whiteboard.from_text` and `BoardElement.place` / `placed_at` (`harness/whiteboard/whiteboard.py:130,152,174,397`), which `rendered_file.py:152-153` uses in the same save. A change to the board file's layout must now be made in two modules. [1]
- kept_document.py:56 `onto` — never-swallow-exceptions — `except (ET.ParseError, json.JSONDecodeError, KeyError, TypeError): return Reshaped(rendered, [], [])` answers the bare render when the existing file cannot be read, and `RenderedFile.save` then writes it over the file. A drawing a person made that this reader cannot parse is replaced with nothing reported; `KeyError` and `TypeError` also hide a mistake in this class itself. [3]
- kept_document.py:87 `_are_mostly_drawn`, kept_document.py:75-76 — use-typed-signatures — the graph's hits on `held` and `drawn` (plain dictionaries of cells by id) are real but local; they follow from this class working on raw XML and JSON rather than on a drawing object. [3]

### cdd_guidance/actions/render/worker_render.py and render_worker.py

- worker_render.py:50 `RenderOrder` — class-not-property-instance-or-subtype — a render order is a `RenderRequest` (`format`, `content`, `source`, `previous`, `folder`: the same five fields, `harness/guidance/practice_formats.py:89-93`) plus the fidelity's slug and its practice's module; `from_request` (57) and `request` (84) copy the fields one by one. `RenderRequest` could write and read itself, and the order would only add where to find the fidelity. [2]
- render_worker.py:24 `_fidelity_of` — put-logic-on-the-owning-resource — a module function that takes the order and resolves its fidelity through `WorkList(None)`, `GuidanceCommand.from_guidance` and `work.each(lambda worked: worked)[0]`; the order's own `fidelity` property answers only the slug. Resolving the fidelity belongs on `RenderOrder`, and asking a work list to run an identity function to get it exposes mechanism. [3]
- worker_render.py / render_worker.py file names — use-intention-revealing-names — two files whose names are each other's words reversed: one holds the order and the server side, the other is the process entry. `render_order.py` for the first would say what it holds. [4]

### cdd_guidance/actions/validate/checked_graph.py

- checked_graph.py:16 `_STORIES`, checked_graph.py:18 `_STORY_MAP_TYPES` — single-boundary — Validate names the Stories practice by a string and copies its ten node types (`Epic` … `Background`), which Stories' own model defines (`stories/model/graph_reading.py`, `story_model.py`); a node type added to Stories is not scoped here until someone remembers this list. This is the clearest case of an action holding a practice's concept. [1]
- checked_graph.py:112 `_on_session_stories` — hide-inner-details — `getattr(self.session, "stories", None)` asks the session for an attribute that is not on `ActionSession` (`harness/guidance_actions/guidance_actions.py:47-68`); `SessionBrief._story_scope` does the same at `guidance_actions.py:625`. The session's story scope is a real concept reached twice by `getattr`. [3]
- checked_graph.py:44 `__init__` — use-typed-signatures — `fidelities: list[Any]`, while `ReportFiles.__init__` types the same list `list[FidelityGuidance]` (`report_files.py:41`); `Validate._fidelities` returns bare `list` (`validate.py:148`). [3]
- checked_graph.py:49 `_formats` — no-redundant-relationship-paths — the fidelities and the format each is checked in are two parallel lists joined with `zip` at 158, 225, 237 and 246; one object for "a fidelity as this call checks it" (the fidelity and its checked format) would hold the pair once. [3]
- checked_graph.py:221 `_other_format_files`, checked_graph.py:233 `_checked_format_files` — eliminate-duplication — two ten-line operations that differ only in `format != checked` against `.get(format)`. [2]
- checked_graph.py:229 — eliminate-duplication — "a declared path that names no one file" is tested as `"{" not in path` (229, 239), `declared.partition("{")` (255), `_NOT_ONE_FOLDER` in `generate.py:20`, and `_NAMED_PART` in the render files, while `DeclaredFile.names_one_path` exists for it (`harness/guidance/declared_outputs.py:35`). [2]
- checked_graph.py:73 `check_beside` — temporal-independence — `files` is empty and `_checked` is none until `check_beside(reports)` runs, so `violations()`, `found()`, `unread` and `held_beside` answer "nothing" rather than failing when called first; the order is known only to `Validate._check`. `prefixes` is also reassigned later by `_built_from_written` (173). [3]
- checked_graph.py:55-58 public fields `edited`, `prefixes`, `files`, `checked_files`, `unchecked_files`, `session` — hide-inner-details — six public mutable attributes; `ValidationReport` takes the session from `checked.session` (`validation_report.py:44`) and `Validate` reads `edited or prefixes` (`validate.py:143`). `prefixes` holds files and folders the graph is built from; the name describes how they are matched, not what they are. [4]
- checked_graph.py:25 `NamedToCheck` — use-intention-revealing-names — a frozen bag of the three arguments of one call (`paths`, `graph`, `call`) under a name that reads as an adjective; it exists only to keep the constructor at three parameters. [4]

### cdd_guidance/actions/validate/report_files.py

- report_files.py:58 `save` and checked_graph.py:73 `check_beside` — write-interactions — the two classes are handed to each other: `CheckedGraph.check_beside(reports)` asks `reports.graph_file()`, and `ReportFiles.save(report, graph)` asks `graph.save_at`, `graph.found_by`, `graph.prefixes`. Neither holds the other, so `Validate` must pass each to the other at the right moment (`validate.py:95,103`). [3]
- report_files.py:80 `_drop_older_checked_graphs` — hold-state-on-the-object-not-in-parameters — reads the fidelity's name back out of the report's file name (`report.stem.rsplit("-", 1)[0]`) although `save` iterates `(fidelity, path)` and holds the fidelity. [3]
- report_files.py:21 `_CONTEXT_FOLDER` — eliminate-duplication — `.context` is also `harness.installation.context_config.CONTEXT_FOLDER` (imported at `rendered_code.py:45`) and a literal in `partition_index.py:47,50,53`, `segment.py:24,26`, `grill_context.py:54`. [2]
- report_files.py:25 `_writable_then_retried` — prefer-class-operations — a module function used only by `ReportFiles._drop_older_checked_graphs` (84). [3]

### cdd_guidance/actions/validate/validation_report.py

- validation_report.py:30 `_RULE_BULLET`, validation_report.py:186 `RulePlaces` — eliminate-duplication — a second parser of rule bullets in a practice's markdown; `Rule.from_bullet` (`harness/guidance/rule.py:110-119`) parses the same bullet with its own two patterns. Where a rule is written is a fact about the rule, and a `Rule` that kept its document and line would make this class unnecessary. [2]
- validation_report.py:52 `for_judge`, validation_report.py:63 `for_saving` — use-property-not-accessor — both, with `CheckedGraph.violations()`, `accepted()`, `found()`, are derived values that take no parameters; `violations()` is recomputed (and filters the accepted-violations file again) at 74, 106 and `validate.py:188`. Low. [3]

### cdd_guidance/actions/validate/validate.py

- validate.py:203 `_log_graph_validation` — hide-inner-details — sets the base class's private flag `self._logged_session_action = "validate"` to stop a second log line; the subclass depends on how `GuidanceAction` remembers what it logged. [1]
- validate.py:222 `create_rule` — no-legacy-api-after-refactor — a `@noDeploy` operation whose result text still says "Write a new named rule into this tool" and "run collection validate"; grep finds no caller in production code (only `validate.py` itself and specs). Either it is published or it goes. [4]
- validate.py:84 and :104 — eliminate-duplication — `[self.work.at_fidelity(item) for item in self.listed() if ...]` is built twice in one call, once filtering `isinstance(item, Guidance)` and once `not isinstance(item, str)`. [2]

### cdd_guidance/actions/generate/generate.py

- generate.py:58, :115, :126, :132 — eliminate-duplication — `worked = [self.work.fidelity_of(item) for item in self.listed() if isinstance(item, PracticeGuidance)]` is written four times in one class; the fidelities a call works at are state of the action's work list. [2]
- generate.py:93 `_fidelity_before` — put-logic-on-the-owning-resource — takes a practice and one of its fidelities and walks `practice.fidelities.entries` to find the one before; a fidelity (or its collection) should answer its predecessor. [3]
- generate.py:16 — low-coupling — imports `WHITEBOARD` from `render/rendered_file.py`, a file-saving helper, to ask whether a fidelity writes a whiteboard. [1]

### cdd_guidance/actions/partition/partition.py, segment.py, partition_index.py

- partition.py:130 `partition` — avoid-vague-parameter-names — `mode: str = "one_go"` changes nothing: it is read once, to be printed in the closing sentence (158). A parameter that names a choice with no behaviour misleads the caller. [4]
- partition.py:46 `context_setup`, partition.py:51 `context_index` — use-typed-signatures — both properties are typed `Any` on purpose (comment at 43-44) so the installer does not publish Context Setup's tools again under partition; the installer's rule is leaking into the type of a public property. [4]
- segment.py:147 `entries` — use-property-not-accessor — a derived value with no parameters, recomputed by `is_complete` (153) and `completeness_report` (163). [3]
- segment.py:187 `_entry_for` — hold-state-on-the-object-not-in-parameters — takes `lines`, which is the segment's own `_content_lines`; `_body_after_header` (195) takes them again. [3]
- segment.py:226 `_report_table_lines` — keep-operations-single-responsibility — on a pass it appends a line with four cells (`| - | (all expected entries) | OK | >=N |`) to a table whose header has three (183-184); the report's shape is decided in two operations that disagree. [3]
- segment.py:81 `PartitionFile` — class-not-property-instance-or-subtype — a base whose three read-only properties are used by callers only for `completeness` (`partition.py:70`, specs); `path` and `text` have no production reader outside the two subclasses' own private use. The base adds a class to share three assignments. Low. [2]

### cdd_guidance/actions/sketch/sketch.py, iterate/iterate.py, improvement/improvement.py, grill_context/grill_context.py, satisfy, document, diagnose

- sketch.py:34 `sketch_template` — no-legacy-api-after-refactor — the property's only readers are `sketch_spec.py:57,68`; production reads the guidance's own `sketch_template` (`sketch.py:53`). Code kept alive by its own spec. [3]
- sketch.py:105 `review_sketch`, iterate.py:21 `mark_iterate_round` — abstraction-focus — two `@agent_tool` operations that do nothing and return a fixed word (`"sketch-review"`, `"iterate-round"`); they exist so their docstring reaches the agent. An instruction dressed as a tool is published on MCP as something callable that changes no state. [4]
- improvement/improvement.py:13 `Improvement` — domain-nouns-only — the action every document calls repair (AGENTS.md's action list, the `/repair` command, the `repair` operation) lives in the folder `improvement` as the class `Improvement`; `grill_context/GrillContext` likewise holds the action called grill. A reader looking for the repair action finds no folder of that name. [4]
- improvement.py:59 `verify_fix` — avoid-vague-parameter-names — calls `_work_on(guidance)` and then returns a sentence built only from `theme`; the guidance it takes changes nothing in the answer. [4]
- grill_context.py:28 `_appended_answers_content` and :77 `write_grill_answer` — shape-classes-around-resources — the grill answers file (path at 23, text composed at 28, read and written at 83-86) is a small resource handled as three loose steps on the action. Low. [3]
- document.py:12 `DOCUMENT_RANK_ON_STAGE` — provide-meaningful-context — the only action that names its rank; the others write `@on_stage(0)` … `@on_stage(5)` as bare numbers (`partition.py:126`, `generate.py:27`, `validate.py:53`, `iterate.py:26`, `sketch.py:116`, `render.py:39`), so the order of actions on a stage is six literals in six files. [4]

### cdd_guidance/patterns/lern_domain_driven/tier_facts.py

- tier_facts.py:48 `TierFile` — keep-classes-single-responsibility — one class answers the facts of five kinds of file (`node_root_facts`, `route_facts`, `behavior_facts`, `story_facts`, and the aggregate's `request_reads` / `web_path_literals`); the caller picks which with a table of lambdas (`graph_overlay.py:203`). Its docstring admits the name is wrong: "a tier file, a behavior file, or a story file". [4]
- tier_facts.py:63, :83, :113, :122 — use-typed-signatures — every fact is an untyped `dict` or `list[list]`, and each key is a string written twice: once here and once in the rule that reads it with `node.get_fact("…")` (`lern_tier_rules.py:25,50,55,59,72,75,88,104`, `shared_story_rules.py:24,37,51,65,82`, `shared_behavior_rules.py:24,35,50,64`). A key renamed on one side makes the rule pass silently, because `get_fact` answers the empty default. [3]
- tier_facts.py:1-4, :48-51 — eliminate-duplication — the docstrings say each file is read once, but a node file is read by `AggregateFolder.web_path_literals` (251), again by `TierFile.at` for its node facts (`graph_overlay.py:207`), and a repository's file again at `graph_overlay.py:209`; view files are read a further time at `graph_overlay.py:228`. [3]
- tier_facts.py:12 — low-coupling — `SourceText` is imported from `cdd_guidance/practices/clean_engineering/model/operation_metrics.py`, three packages into a practice. The patterns card documents the dependency, but Clean Engineering's seam does not offer it; a general "text with line numbers" class sits inside one practice's metrics module. `graph_overlay.py:17` reaches `clean_engineering/model/code_body.py` the same way for `CODE_LANGUAGES`. [1]
- tier_facts.py:104 `unreset_instances` — hold-state-on-the-object-not-in-parameters — `setup_text` is handed from `_LernReading.read` to `_AggregateTiers._tier_facts` to `node_root_facts` to `unreset_instances`; it is one value for the whole reading. [3]

### cdd_guidance/patterns/lern_domain_driven/graph_overlay.py

- graph_overlay.py:65-66, :85 `read`, `_behaviors` — one-way-deps — `Ddd`, `Stories` and `Bdd` are imported inside functions, as `cdd_web_domain_access/graph_overlay.py:15,22` imports `Ddd` and its own `AccessFile`. `patterns/__init__.py:13` already imports `cdd_guidance.practices` at the top, so nothing is gained by hiding these; the rule counts them as imports either way. [1]
- graph_overlay.py:73-75 `read` — temporal-independence — `self.ddd`, `self.story_nodes` and `self.setup_text` are first set inside `read`, not in the constructor, and `_AggregateTiers` reads them through `reading.ddd`, `reading.root`, `reading.setup_text` (157, 199, 217). An `_AggregateTiers` made before `read` fails with an attribute error. [3]
- graph_overlay.py:246 `_record_screen_stories`, :254 `_story_key` — prefer-class-operations — module functions used only from `_LernReading.read` (81), taking `story_nodes`, which the reading holds. The graph hit is real. [3]
- graph_overlay.py:90, :98, :108 — eliminate-duplication — `scanned_files(self.root)` walks the working copy three times in one reading (behaviours, tier folders, story files). [3]
- graph_overlay.py:21 `_TIER_FILES`, :24 `_BEHAVIOR_TIERS`, :133 `_story_semantic` — eliminate-duplication — "which node type does this file become" is decided three ways in this file (a tuple table, a dictionary by suffix, an if-chain) and a fourth way in `AccessFile.tier()` (`access_facts.py:37`), which lets the file itself answer. [2]
- graph_overlay.py:152 `_AggregateTiers.__init__` — keep-operations-single-responsibility — the constructor adds nodes to the graph (`in_graph.add_file`, 159) while it is being made; building the object changes the graph. [3]
- graph_overlay.py:101 — provide-meaningful-context — `folder.startswith("src/")` fixes LERN's source folder as a literal inside the reading, while the pattern class holds its other folders as named attributes (`default_workspace_folder`, `story_test_folder`). [4]

### cdd_guidance/patterns/lern_domain_driven/lern_domain_driven.py

- lern_domain_driven.py:35 `test_setup_text` — put-logic-on-the-owning-resource — the pattern's guidance class reads working-copy files for a `root` it is handed; its only production caller is the reading (`graph_overlay.py:75`), which holds that root. Reading a working copy belongs to the reading. [3]

### cdd_guidance/patterns/cdd_web_domain_access/access_facts.py

- access_facts.py:37 `tier` — use-intention-revealing-names — `tier()` answers a node type and its facts as `tuple[str, dict] | None`; "tier" is LERN's word for node, client and routes, and here it names four kinds of access file. [4]
- access_facts.py:23 `AccessFile` and tier_facts.py:48 `TierFile` — eliminate-duplication — two classes of one shape: hold a `SourceText`, offer an `at(...)` factory (with different signatures: `at(path)` against `at(root, path)`), answer fact dictionaries from regular-expression hits, and both recognise `-routes.ts` and `-node.ts`. About 25 shared lines today; `OssFile` is a third. [2]
- access_facts.py:49-70 `route_facts`, `node_facts`, `is_hand_written_adapter`, `is_annotated` — deep-module — public, but called only from `tier()` in production; specs call `tier()` and `annotated_toolset_facts()` only (`access_facts_spec.py:25-49`). [1]

### cdd_guidance/patterns (package), mern_domain_driven, cdd_claude_mod, domain_driven_stack

- patterns/__init__.py:24 — class-not-property-instance-or-subtype — a pattern is recognised by a class attribute string (`getattr(value, "pattern", "") == folder.name`), and `GraphOverlay.name` reads it back with `getattr` (`harness/graph/pattern_overlays.py:49`). There is no `Pattern` class, although "pattern" is a first-class word in AGENTS.md and the builders have their `Builder` base. [4]
- cdd_claude_mod.py:22-28, cdd_web_domain_access.py:24-30, domain_driven_stack.py:15-16 — eliminate-duplication — three classes each write `super().__init__(format="typescript")`, a `default_workspace_folder`, and (two of them) a cached `graph_overlay`; the shared part of being a pattern has no home. [2]
- mern_domain_driven.py:12 `MernDomainDriven` — temporal-independence — has no `graph_overlay`, while `PatternOverlays.graph_overlays` reads `pattern.graph_overlay` of every applied pattern (`harness/graph/pattern_overlays.py:152`). MERN is safe only because it has no `practices/` folder and so is never applied (`_holds_practices`, :143); adding one rule folder to MERN raises `AttributeError`. `CddClaudeMod` writes the base overlay by hand to avoid this. [1]
- mern_domain_driven.py:12 — eliminate-duplication (absence) — MERN shares Express, React, Node and the story test tiers with LERN but gets none of LERN's 14 graph rules; `mern_domain_driven_spec.py:75` checks that its markdown "names every ported rule slug", so the rules were copied as text and are judged by reading only. Of LERN's rules only `node-repository-parses-on-read` is about lowdb. [2]

### cdd_guidance/patterns/lern_domain_driven/practices/stories/model/claude_design/fixtures.py

- fixtures.py:23 `LernCanvasFixtures` — no-legacy-api-after-refactor — grep finds the class only in its own module and `fixtures_spec.py`; `.context/model/repo-review/README.md:46` records it as kept deliberately. It still has no production caller in this worktree, so it is code its spec keeps alive; the product owner's earlier decision stands unless a caller is named. [3]

### cdd_guidance/desktop_walk/desktop_walk.py

- desktop_walk.py:18-21 — low-coupling — imports four modules from inside Stories' model (`markdown.nodes.MarkdownScenario`, `markdown.scenario_file.ScenarioFileReading`, `story_file.flat_steps`, `story_map_files.StoryMapFiles` and `STORY_TESTS_FOLDER`). Stories' card names its seam as `Stories`, its instructions, its fidelities and `render`; none of these four is on it, so any reshaping of Stories' markdown reading breaks the walk. [1]
- desktop_walk.py:51 `DesktopStep`, :91 `DesktopScenario` — single-boundary — a second scenario and step model (`story`, `name`, `keyword`, `text`) copied from the story model's scenario and step, to add `do` and `see` lines and a key. The card says Stories already reads a desktop story test as a scenarios file; the walk reads it again into its own classes. [2]
- desktop_walk.py:127 `read_steps` — temporal-independence — a scenario is made empty and filled by a second call that takes the file's lines; `steps` answers an empty list in between. [3]
- desktop_walk.py:120, :138 — eliminate-duplication — `"/".join(Path(self._file).parts[1:-1])` is written in `sub_epic` and again in `is_under`. [2]
- desktop_walk.py:55 `DesktopStep.__init__` — limit-operation-parameters — five parameters, three of which (`number`, `keyword`, `text`) describe the story model's step the caller already holds (`read_steps`, 130-134); the graph hit on this constructor is real, small. [3]
- desktop_walk.py:29 — one-way-deps — `cdd_guidance/desktop_walk` imports `space.repo.new_repository`; the card documents it, but it is the only place in this area where guidance imports the work layer at run time (the actions name `Session` under `TYPE_CHECKING` only). [1]

### cdd_guidance/context_setup/context_setup.py, live_app_capture.py, context_index.py

- context_setup.py:70 `_converter` — use-explicit-dependencies — the document converter is class-level state shared by every instance and built inside a property (101-108); the comment explains the cost it avoids, but a converter fetched from the class cannot be swapped, and the specs must patch the class. [3]
- context_setup.py:154, :173, :195 — eliminate-duplication — three tools take the same five values and build the same `LiveAppCapture(...)` before `_in_project` rebuilds it with `dataclasses.replace` (95-99); `complete_capture` passes `missing_pages` in the position named `entry_paths` (210), so one field means "paths to scout" in two tools and "paths that failed" in the third. [2]
- context_setup.py:290 — use-consistent-naming — `tools(self.context_index.embed())` is written as a call with no arguments, where every other recipe names the operation (`tools(self.search)` at `context_index.py:240`, `tools(self.context_index.embed)` at `partition.py:152`). [4]
- live_app_capture.py:110 `surface: str` — use-typed-signatures — `'web' | 'desktop' | 'api'` is a string compared in `_is_browsable` (169), where `api` is treated as a page to open in a browser and screenshot (235-245); the three surfaces are a domain concept with no type and one of them has no behaviour of its own. [4]
- live_app_capture.py:171 `_app_url` — keep-operations-single-responsibility — a getter that also finds and stores `base_url` on first use, on a dataclass whose fields read as the call's inputs. [3]
- context_index.py:132 `_openai_client` — prefer-class-operations — a module function used only as `OpenAIEmbeddingProvider`'s default factory (145). Low. [3]

### cdd_guidance/builders

- No findings. `Builder`, `CreateAgentToolset` and `CreatePracticeGuidance` are 12 lines each and hold only what the framework needs.

## Fixes that change no design

Each fix stays inside one class or file, or removes an exact duplicate, and changes no seam another module calls. They are numbered inside each group; a reference such as "UX fix 7" or "Stories core fix 8" points here.

### Stories core fixes — Stories Python core

1. **Delete `name_facts.opens_with_verb`** (name_facts.py:73-76). Callers: none. Specs: none. Risk: none.
2. **Delete `Example.as_code`** (story_model.py:353-361). Callers: none. Specs: none (`git grep as_code`). Risk: none.
3. **Delete `Epic.has_epics`** (story_model.py:998-1000) and the assertion at story_model_spec.py:391. Risk: none.
4. **Delete `CodeStoryNode.camel` and `pascal`** (code_story_model.py:85-89); drop `pascal=story.pascal()` from story_writing.py:175. Callers: none for `camel`; `pascal` only feeds a template key no language uses. Specs: check `story_channel.feature.py` (imports `CodeStoryNode`, uncollected). Risk: low.
5. **Delete `StoryWriting.story_text`** (story_writing.py:183-184) and change code_story_behaviours_spec.py:98 and typescript_story_model_spec.py:94 to `"\n".join(writing.story_lines(story) + [""])`. Risk: low.
6. **Remove dead branches**: story_map.py:42-43 (`ChildCountFitsLayer`); scenarios.py:435-436 and the unused `_PLAIN_ENGLISH` (23). Specs: none change. Risk: none.
7. **Move the shared constructor up**: give `BraceStoryWriting.__init__(self, language, helpers)` (brace_story.py:114) and delete the two identical ones (typescript_story_model.py:19-21, javascript_story_model.py:21-23). Callers: `ScriptStoryModel.writing` already passes both. Risk: none; it makes the base contract true.
8. **One `_step_body`, one `_STEP_TYPES`, one `_EPIC_TYPES`**: add `step_body(step)` to `StoryTree` (graph_reading.py:260) and keep the two frozensets in graph_reading.py; delete modelled_areas.py:18, 20, 98-100, term_links.py:20 and graph_reading.py:504-506; callers `ExampleObservations._observed_by` (57, 59) and `StoryLinks._link_step` (432) call `self.tree.step_body(step)`. modelled_areas.py imports graph_reading only under `TYPE_CHECKING` today, and graph_reading imports modelled_areas, so the constants must sit in a file both can import (put `StoryTree` and the constants in a new `story_tree.py`, or keep them in modelled_areas.py and import from there). Specs: none name these. Risk: low; watch the import direction.
9. **Rename `value` to `held`** in `ModelledAreas._record` (modelled_areas.py:125) and annotate `node: Story | Scenario` in `SpecifiedStories._is_read_from_files` (stories_formats.py:55). Risk: none.
10. **Make internal-only operations private**: `CodeStory.add_scenario`, `fill`, `read_description` (code_story_model.py:334, 355, 272; callers 365, 308, 307); `ScriptStoryModel.story_test_file_path` (script_story_model.py:81; caller 92); `StoriesReading.recorded_map` (graph_reading.py:78, 140, 142); `ReshapedStoryFile.kept`/`added` (reshaped_story_file.py:53-54 and their uses in the file). Specs: `git grep` shows none call them. Risk: low.
11. **Move single-class module functions onto their class**: `step_semantic` and `step_checksum` onto `Step` (story_recording.py:369, 95; callers story_model.py:683, 697); `folder_of` onto `Epic` (story_recording.py:361; caller story_model.py:1020); `call_of` onto `PythonStoryFile` (python/story_file.py:33); `scenario_domain_concepts` onto `ExamplesTraceDomainModel` (scenarios.py:110, 142); `_steps_key` as a property of `Scenario`/`Background` (story_model.py:704, 736, 872). Specs: check `story_model_spec.py` for `step_semantic` (none found). Risk: low.
12. **Hold the graph part once in `StoryRecording`**: `self._in_graph = practice.reading.in_graph` in `__init__` (story_recording.py:223) and use it at 234, 246, 249, 265, 267, 277. Risk: none.
13. **Use `_verb` in `ReshapedStoryFile._empty_step`** (reshaped_story_file.py:129): make `StoryWriting._verb` public as `verb_of(step)` with the phase fallback, and call it. Callers: story_writing.py:216. Risk: low; the two fallbacks differ (`step.keyword.lower()` against `step.step_type.value`), so confirm with reshaped_story_file_spec.py which one an And step needs.
14. **One home for `NO_LONGER_IN_MODEL`**: define it once beside `Reshaped` in `harness/guidance/practice_formats.py` and import it in the five files that define it now. Specs: any that import it from its current files. Risk: low; it touches four other modules, so it is listed here only because no class or seam changes.
15. **Top-level imports in stories.py**: move `MarkdownStoryModel` (192) and `CodeStoryModel` (246) to the top of the file. Risk: `_FORMAT_ADAPTERS` exists to import format modules on first use; importing the markdown adapter at module load costs its import time on every start. Measure before doing it; if the cost matters, keep 192 and move only 246 (code_story_model is already imported by graph_reading at load).
16. **Correct story-model.md:146** to the constructor the code has. Risk: none.

### Stories adapters and app fixes — Stories format adapters and the Story UI app

1. **Delete the unused placement API on `DiagramStoryNode`.** Remove `place`, `add`, `stretch`, `role`, `_placed_children` (`diagram_story_model.py:92-128`). Callers: none (grep `\.stretch\(|_place_side|\.role\(\)|_placed_children` and `\.add\(|\.place\(` under `stories/` and `ux/model/claude_design/`). Specs: none use them. Risk: none found; run `diagram_story_model_spec.py` and the three format specs.
2. **Delete `DrawIOEpic.story_xs`** (`drawio/nodes.py:145-153`) and **`WhiteboardEpic.bars`** (`whiteboard/nodes.py:107-109`). Callers: only their own recursion. Risk: none.
3. **Delete the `colTemplate` parameter and `ColumnLayout.leadCols`** (`story-map-views.tsx:521, 534, 566, 679-680`). Callers: one call site. Risk: none.
4. **Use the harness `heading_anchor`.** Delete `heading_anchor` from `stories/model/markdown/links.py:30-34` and import `harness.markdown.markdown.heading_anchor` in `_Anchors.next`. Check first that the harness regex `_LINK_IN_HEADING` strips links the same way as `unlink` (both reduce `[label](target)` to the label). Callers: `links.py:48` only. Specs: `markdown_story_map_round_trip_spec.py`, the drawio link specs. Risk: low; an anchor that differs would break `story-map.md#…` links, which the specs cover.
5. **Make `load_thin_slice` call `_graph_model`** (`drawio/nodes.py:505-511` → `tree = self._graph_model(text)`). The error text for a root that is neither `mxfile` nor `mxGraphModel` changes from "No mxGraphModel found" to "Root element must be <mxGraphModel>"; check `drawio_story_model_spec.py` for an assertion on that text. Risk: low.
6. **One name for reading a drawing.** Keep `parse` (what `PracticeFormats` calls), delete `load` from `DrawIOStoryModel`, `MiroStoryModel`, and `WhiteboardStoryModel`, and move the body into `parse`. Callers to change: `drawio/nodes.py:436` (`from_workspace`), `story_channel.feature.py:230, 271, 273, 275`, `drawio_round_trip_spec.py` (five calls), `drawio_story_model_spec.py` (three or more), `miro_story_model_spec.py`, `whiteboard_story_model_spec.py`. Do not touch `CodeStoryModel.load`, which takes a dictionary of files and is a different operation. Risk: low, mechanical; about 25 call sites.
7. **Make internal-only names private.** `MiroShape` → `_MiroShape`; `heading_of` and `inferred_story_name` → private (`scenario_file.py:53, 58`); `StoryMapLinks.story_files`, `map_file`, `base` → `_story_files`, `_map_file`, `_base`; `DrawIOStoryModel.placed_cells` → `_placed_cells` with `drawio_round_trip_spec.py:88, 101` changed to read the redrawn file through `parse` or the private name. Risk: low.
8. **Use the constants that own the file names.** `markdown/nodes.py:48` → `STORY_FILE_SUFFIXES[0]`; `thin_slice.py:123` → a named constant in `story_map_files.py` beside `THIN_SLICING_FILES` (the name a new thin slice is written under). Risk: none.
9. **Move module functions onto their only class.** `_drawn_geometries` → `_KeptPlaces` (graph hit, `drawio/nodes.py:314`); `read_sketch_lines` and `_depth` → `SketchLines.from_raw` (callers: `sketch_story_model.py:289` and `sketch_story_model_spec.py` if it imports it — grep before changing); `thin_slice_in` → `ThinSlice.in_folder(folder, story_map, project)` (callers: `markdown/nodes.py:411, 470`); `_example_tables` / `example_table_lines` stay until A5. Risk: low.
10. **Collapse the three cross-parent drag handler factories** in `story-map-views.tsx:343-470` into one `makeCrossParentDragHandlers(kind, id, listKey, getTargetIds, visuals, refs)`; the unused `onMove` parameter goes (the drop is committed at the container, per the comments at :381 and :426). Callers: three call sites inside `StoryHierarchyView`. Specs: the board's `*.story.ui.spec.ts` drag scenarios and the app's own view specs. Risk: medium only because drag behaviour is hard to see in a unit test; run the e2e tier.
11. **Rename `MapReading`'s `format` parameter and field** to `story_map_type` or pass the epic and story types (`map_reading.py:48, 64, 84, 94, 101, 111, 177, 205, 281`). Callers: `read_map` only. Risk: none.
12. **Give `WhiteboardStoryModel` the missing `from_workspace`** only as part of A1; as a local stopgap, `stories.py:199, 253` can fall back to `adapter.parse(path.read_text())` for an adapter without one. This is a defect fix, so it needs a failing test first (`open_file` on a `.whiteboard` story map).

### UX fixes — UX

Each of these stays inside one class or file and changes no seam another module calls.

1. **Delete the unused workspace lookup on `UxMap`.** Remove `from_workspace`, `workspace_text`, `workspace_file` (`ux_map.py:231-248`) and the attribute `workspace_files` (`ux_map.py:46-48`) with its five overrides (`drawio/nodes.py:342-350`, `html/nodes.py:180`, `json/nodes.py:219`, `markdown/nodes.py:26`, `whiteboard/nodes.py:231`). Callers: none. Specs: none. Card: check `ux/.context/module-context.md` and `model/.context/ux-model.md` for the names. Risk: low; this also brings `UxMap` under the public-operation budget the graph reports.
2. **Delete `UxComponentCollection.remove` and `find`** (`collections.py:32-44`) and `ReferencePaths.clear` (`reference_paths.py:26-27`). Callers: none, specs included. Risk: none.
3. **Empty `model/__init__.py` of its re-exports** (lines 3-36). No file imports from the package itself. Risk: low; a tool that imports `cdd_guidance.practices.ux.model` for its side effects still gets the package.
4. **Make internal-only names private.** `UxMapFile`, `UxMapFiles`, `RecordedMap`, `LinksAcrossPractices`, `ServedStoryLinks`, `DomainTermLinks`, `StoryDemoControlLinks` in `graph_reading.py` (used only at :86-99). `DrawioUxMap.read_pages`, `cli_state`; `WhiteboardUxMap.take_board`; `MarkdownUxMap.read_context`, `written_onto`; `JsonUxMap.read_record`, `map_record`; `HtmlControl.data_attributes`, `input_key`; `Ux.javascript_practice` (one spec line, `ux_spec.py:207`, moves to asserting through `ensure_javascript`). Each is called on an instance of its own class from inside the class. Specs: `ux_spec.py:207` only. Risk: low. Check the UX card and `ux-model.md` for any of these names and change them in the same pass.
5. **Rename the vague parameter.** `reshaped_view.py:169` `_empty_function_from(self, value)` → `assigned_at`. Private; one caller at :166. Risk: none.
6. **One copy of the transition copy.** In `ux_map.py`, extract `_transition_copy(transition, screens, order)` and call it at :160-162 and :227-229. Risk: none.
7. **One copy of "the screen's name or blank".** Give `Transition` two read-only properties (`from_name`, `to_name`), `Interaction` one (`destination_name`), `Screen` one (`chrome_of_name`), and delete `ux_map.py:279 _name_of`, `json/nodes.py:292 _name_of`, `html/nodes.py:226 _name_of`, and the inline version at `drawio/nodes.py:447-448`. Callers: `ux_map.py:223, 225`; `json/nodes.py:85, 160, 183-184`; `html/nodes.py:212`. Risk: low.
8. **One copy of the Stories step types inside UX.** Delete `graph_reading.py:46 _STEP_TYPES` and read `story_link.py`'s `_NODE_TYPES["Step"]` through a public name until proposal U2 moves it to Stories. Callers: `graph_reading.py:352`. Risk: none.
9. **Move `story_steps_from` onto `StoryStep`** as `StoryStep.from_values(values)` (a mapping factory, which the rule allows as a class method). Callers: `json/nodes.py:23, 97, 99`; `ux_map_spec_fixture.py:18`; `story_demo_control_spec.py:17`. Risk: none.
10. **Move `_ancestor`, `_parent`, `_name_of` off the module** — partly covered by 7 and by U2. For `story_link.py`, the smallest local fix is to make `_parent`, `_ancestor`, `_story_name` private methods of `StoryTargets` and have `key_of` become `StoryTargets.key_of(node)`; this changes `key_of`'s three importers, so it is better done once, inside U2.
11. **`Callout._corner` off the class method.** Let `CellStyle` keep its cell and answer `corner` as a property; `Callout.under` calls `CellStyle(cell).corner`. One file, `drawio/nodes.py:90-117, 299-317`. Risk: none.
12. **Initialise `WhiteboardScreen._serves_box`** as a class default beside `DrawnNode.box` (`whiteboard/nodes.py:67`) so `board_elements` no longer depends on `lay_out` having run. Risk: none.
13. **Use `KEY_SEPARATOR` at `story_canvas.py:291`** instead of the literal. Risk: none.
14. **Name the "not read back" failure once.** `story_canvas.py:161` raises `ClaudeDesignScreensNotReadable` (or a sibling named for the canvas) instead of a bare `NotImplementedError`. Risk: none.
15. **Drop the unused parameters.** `JsonContentType.from_record`'s `ux_map` (`json/nodes.py:194`; caller `:260`) — keep only if the uniform signature is wanted, and say so in a comment; `ClaudeDesignStoryModel.render`'s `previous` (`story_canvas.py:153`) — check first that `PracticeFormats` does not pass it by keyword (`harness/guidance/practice_formats.py:279`); the class is not a registered adapter today, so it should be safe.
16. **Story Demo: delete the one-product code.** Remove `paintCharacterTree`, `paintAbilities`, and the three lines that call them (`mount-generated-mockup.js:272-295, 486-488`), and the `"create character"` special case (`control.js:71`). No UX format writes `data-character-tree` or `data-ability-list`. Specs: `story-demo.spec.js` and `story_demo_control_spec.py` use a "Create Character" control as test data; check whether any assertion depends on the special case before deleting. Risk: medium only for any hand-written mockup outside this repository that relies on the two attributes.
17. **Story Demo: delete `PaintReflect`.** Remove `paint-reflect.js`; in `play-dual-runner.js:73` and `story-demo-page.js:109` drop the `paintReflect.apply(snapshot)` line (the next line already calls `storyDemoFrame.bind(snapshot)`); drop the `paintReflect` constructor option (`story-demo-page.js:20, 24, 27`; `play-dual-runner.js:18`). This removes a class, so strictly it is a design change, but it is an exact duplicate with one caller pattern. Specs: `story-demo.spec.js`, `play-dual-runner.spec.js` where they pass or assert `paintReflect`. Card: the `ux/story-demo` section does not name it. Risk: low.
18. **Story Demo: camelCase the two fields.** `control.js:43-44` `bound_field` → `boundField`, `story_steps` → `storySteps`, with readers `story-demo-frame.js:28, 35-36`, `story-demo-page.js:103`, `mount-generated-mockup.js` (grep `story_steps`, `bound_field`), and both JavaScript specs. Risk: low, mechanical.

### Actions and patterns fixes — Actions, patterns, builders, context setup, desktop walk

1. **One `NO_LONGER_IN_MODEL`.** Keep the constant in one place both the actions and the practices may import (beside `Reshaped` in `harness/guidance/practice_formats.py`) and import it in `actions/render/reshaped_code.py:37`, `actions/render/kept_document.py:33`, `bdd/model/spec_reshape.py:26`, `stories/model/reshaped_story_file.py:34`, `ux/model/view/reshaped_view.py:29`. Callers: none change behaviour. Specs: any spec that imports the constant from one of the five files (`reshaped_code_spec.py`, `kept_document_spec.py`). Risk: low; the text is identical in all five.
2. **Move `_record_screen_stories` and `_story_key` onto `_LernReading`** (`graph_overlay.py:246-256`) as `_record_screen_stories(self)` reading `self.story_nodes`. Caller: line 81. Specs: `screen_story_rule_spec.py` only if it calls the module function (it does not import it; grep finds no outside reference). Risk: low.
3. **Move `test_setup_text` from `LernDomainDriven` to `_LernReading`** as a private property that reads `self.root` and `self.overlay.pattern.story_test_folder`. Callers: `graph_overlay.py:75`; `lern_tier_rules_spec.py:161,165,171` call `LernDomainDriven().test_setup_text(...)` and must build the text through the reading or a small helper. Risk: low; three spec lines.
4. **Set `ddd`, `story_nodes`, `setup_text` in `_LernReading.__init__`** (as `None`/empty) and return early in `read` as today; walk the working copy once (`files = list(scanned_files(self.root))`) and hand that list to `_behaviors`, `_tier_folders`, `_story_files`. Callers: none outside the file. Risk: low; a faster reading, same nodes.
5. **Top-level imports in the overlays.** Move `from cdd_guidance.practices.ddd.ddd import Ddd` and the Stories, Bdd and `AccessFile` imports to the top of `lern_domain_driven/graph_overlay.py` and `cdd_web_domain_access/graph_overlay.py`. Risk: medium-low; run the unit tier, since an import cycle through `cdd_guidance.practices` would show at import. If a cycle shows, that is the real finding and should be reported, not hidden again.
6. **Make `AccessFile.route_facts`, `node_facts`, `is_hand_written_adapter`, `is_annotated` private** (`access_facts.py:49-68`). Callers: only `tier()`. Specs: none call them. Risk: none. Leave `annotated_toolset_facts` public or change `access_facts_spec.py:25-38` to go through `tier()`.
7. **Delete `Sketch.sketch_template`** (`sketch.py:33-36`) and change `sketch_spec.py:57,68` to call `find_template()`. Risk: none.
8. **Rename `worker_render.py` to `render_order.py`.** Callers: `render.py:7`, `render_worker.py:14`, `render_worker_heavy_spec.py`, the actions card. `WORKER_MODULE` stays. Risk: low; rename every reference in one pass.
9. **Replace "context tool(s)" with "guidance"** in the docstrings at `generate.py:1,25`, `document.py:1,17`, `render.py:1,37`, `satisfy.py:19`, `validate.py:1,42`. The class docstrings may be published as toolset descriptions, so reinstall afterwards and check any spec that matches the old text (`fidelity_text_spec.py`). Risk: low.
10. **`segment.py`**: make `entries` a cached property; drop the `lines` parameter of `_entry_for` and `_body_after_header` and read `self._content_lines` (cache it); fix the pass line at 226-229 to three cells. Callers: `completeness_report`, `is_complete`; `partition_spec.py` calls `entries()` if at all through the report (grep shows only `is_complete`, `expected_names`, `has_expected_names`, `completeness`). Risk: low; check the spec's expected report text for the pass line.
11. **`checked_graph.py`**: merge `_other_format_files` and `_checked_format_files` into one private operation taking whether to keep the checked format; type `fidelities: list[FidelityGuidance]`; replace the `"{" not in path` tests with `DeclaredFile(path).names_one_path`. `validate.py:148` returns `list[FidelityGuidance]`. Risk: low; `checked_graph_spec.py` and `validate_spec.py` cover both operations.
12. **`report_files.py`**: move `_writable_then_retried` onto `ReportFiles`; hand `_drop_older_checked_graphs` the fidelity (its slug) from the loop at 63 instead of parsing the file name; import `CONTEXT_FOLDER` from `harness.installation.context_config`. Risk: low.
13. **`generate.py`**: one private property `_worked_fidelities_listed` (or reuse the base's `_worked_fidelities` if it answers the same objects; it answers session outputs, so a new property is needed) replacing the four copies at 58, 115, 126, 132. Risk: none.
14. **`kept_document.py:56`**: catch only `ET.ParseError` and `json.JSONDecodeError`, and name the unreadable file in the result (`migrate`) instead of answering the bare render silently; let `KeyError` and `TypeError` raise. Callers: `RenderedFile.save`. Specs: `kept_document_spec.py` has no case for an existing file that cannot be read (grep finds none), so one must be added with the fix. Risk: medium; this changes what a person sees when their drawing cannot be read, which is the point.
15. **Remove `Partition.partition`'s `mode` parameter** or give it behaviour. It is in the published tool's signature, so removing it changes the MCP schema and the skill text; `partition_spec.py` and `partition_documents_flow_spec.py` name `mode`. Risk: low, but it is a published parameter: ask before removing.
16. **`desktop_walk.py`**: compute the folders once (`_folders` private property used by `sub_epic` and `is_under`). Risk: none.
17. **`context_setup.py:290`**: write `tools(self.context_index.embed)`. Check `context_setup_heavy_spec.py:129-131` (the expanded recipe) still lists the tool. Risk: low.

## Proposed design changes

Twenty-four proposals follow. Each is self-contained: the problem with evidence, the class model before and after (`+` added, `-` removed, `~` changed, `→` moved), the callers affected, the size, and what could go wrong. The letter says which part of the area the proposal belongs to: **S** Stories Python core, **A** Stories format adapters and the Story UI app, **U** UX, **R** actions, render, patterns and desktop walk.

Several proposals are parts of one change and are cheaper approved together:

| Group | Proposals | What the group does | Rough size |
|---|---|---|---|
| **One Stories seam for questions about the story graph** | S4, U2, R3, R5 | `StoryTree` (and the `Stories` practice) answer how a node is keyed, which story a step belongs to, which node types are steps and epics, and what steps a scenario file holds. The UX classes `StoryTargets` and `key_of`, the copies of the step and epic type sets in the Stories link writers, UX and Validate, and the four imports desktop walk makes from inside the Stories model all go. | about 15 files, 300 lines moved, 200 removed |
| **One format contract, one draw.io document, one board key** | A1, A2, U7, U6, R1 (first pass) | Every format adapter has the same `parse`, `render`, `read_file` and a declared `reshape`; draw.io file reading, cell styles, kept layout and the board element key are written once in the harness beside `harness/whiteboard`. Removes the `parse`/`load` aliases, the `isinstance` branches in `stories.py`, the `inspect.signature` probing in `harness/guidance/practice_formats.py`, and the five copies of "no longer in the model". | 30+ files across every practice and the harness; each contract change must go in one commit, because the no-legacy rule forbids a pass that accepts both shapes |
| **Render knows less** | R2, R1 (second pass) | The declared outputs of a fidelity say where a render is saved and a render answers a typed `RenderResult`; `KeptDocument` keeps markdown only. | 8 to 12 files, about 500 lines; most of the cost is `render_spec.py` |
| **A story test in code is read once** | S1, S2, S3, S5 | One reader for a story file in code, a thin `Stories` class, and a `StoryNode` that holds only the story map. | about 25 files; S1 alone is 12 files, 250 lines removed |

**Suggested order, most value for the least cost first:**

1. **U1** — break the UX import cycle with one base failure in `ux_map.py` (4 files, about 15 lines). It removes six graph errors and has almost no risk.
2. **The Stories seam group (S4, U2, R3, R5)** — the largest gain on themes 1 and 2 together, and each proposal in it can go alone; Stories core fix 8 is the first step.
3. **S1** — a story test is parsed twice today and the two results are joined by position; one typed reader removes about 250 lines and the `CodeBlock = Any` type. The regex path is the fallback today for files the block reader cannot parse, so specs for that fallback come first.
4. **A2 with U7** — one draw.io document in the harness and one board key; the key alone is 4 files and can go first.
5. **R1 first pass, then A1** — the shared member record, kept marker and lost-line check, then the full format contract.
6. **R2, S2, U3, A5, U4, A3, R4** — each stays inside one module.
7. **A4 and U5** — the Story UI and the Story Demo runner; the largest view changes, to be verified on screen (Flow A in the TDD rules).
8. **S6 and S7** — renames across 40 to 60 files (`StoryModel` → `StoryMap`, which renames the `story-model.*` MCP tools and needs a reinstall for every IDE; code-text types out of the Clean Engineering model package). Worth doing only when nothing else is in flight.

**Honest cost notes.** U2 grows `StoryTree` from 5 to about 11 public methods, so the deep-module share of Stories must be measured after it. The second pass of R1 removes the safety net that keeps a cell a person drew on a drawing (the defect fixed in commit `134df3e88`); do only the first pass unless every adapter has a heavy spec for kept layout. U6 is recorded for a later decision and is not recommended on its own. The metrics gate in the refactor guardrails applies to every one of these: moving behaviour onto `StoryTree`, `DeclaredOutputs` or `FrontEndView` is right only if the receiving class is then split into parts it holds.

### S1. One reader for a story file in code

**Problem.** A story test is parsed twice and the results joined by position. `StorySyntax` (code_story_model.py:92-203, plus `BraceSyntax` brace_story.py:14-94 and `PythonSyntax` python/nodes.py:14-42) reads the text by regex to build stories, scenarios and steps. `StoryFile` (story_file.py:40-91, `BraceStoryFile`/`BraceBlock` 145 lines, `PythonStoryFile`/`PythonBlock` 130 lines) reads the same text into blocks to attach each node's code. `CodeStory.read_code` zips the two (code_story_model.py:320-332; story_file.py:34-37), and `Step.read_code` guards the mismatch (story_model.py:619). Two more file kinds, `ScreenSpecFile` and `SharedStoryFile`, are readers of their own outside `StoryFile`, chosen by a check that is written twice per language. The block type is `Any`. Estimated duplicated reading: about 220 lines (the three syntax classes) against about 300 lines of block reading.

**Before**

```
CodeStoryModel
  story_type: type[CodeStory]
  story_file(content) -> StoryFile | None        # None for screen spec / shared file
  stories_of(content, source_file, project) -> tuple   # (stories, WrittenBlock | None)
  _read_story_file / _take_stories(holder, stories, written, content, source_file)

CodeStory (classmethods)                          StorySyntax (per language, regex)
  load_all(content) / load_file(content, project)   steps_in, steps_from, scenario_blocks,
  load(content, scenario_blocks)                    backgrounds_in, example_names,
  from_block(block, lead, text)                     story_name, story_texts, _balanced,
  read_code(block, lead, scenarios)                 _outside_scenarios
  fill / add_scenario / read_description
  -> calls syntax.*, then zips with blocks

StoryFile(language, content)                      CodeBlock = Any
  story_blocks() -> list[CodeBlock] | None          BraceBlock / PythonBlock (no shared base)
  stories(story_type, path, project) -> tuple | None

ScreenSpecFile(text, language).stories(story_type)     # not a StoryFile
SharedStoryFile(text, search).stories(story_type)      # not a StoryFile
is_screen_spec(text) asked in ScriptStory.load_all AND ScriptStoryModel.story_file
is_shared_story_file(text) asked in PythonStory.load_file AND PythonStoryModel.story_file
```

**After**

```
CodeStoryModel
  story_file(path, content) -> StoryFile              ~ always answers; picks the kind once
- stories_of(...) -> tuple                             → StoryFile.stories / StoryFile.own_code
~ _take_stories(holder, file: StoryFile)

StoryFile(model, path, content)                        ~ holds its model (story class, language, project) and its path
  stories -> list[CodeStory]                           ~ property; built from blocks, no story_type parameter
  own_code -> WrittenBlock | None                      + the file's code around its stories
  + BlockStoryFile (abstract: story_blocks())          BraceStoryFile, PythonStoryFile
  + ScreenSpecFile(StoryFile)                          ~ now a StoryFile kind; own_code is None
  + SharedStoryFile(StoryFile)                         ~ now a StoryFile kind; own_code is None

+ StoryBlock (abstract base)                           replaces CodeBlock = Any
    name, line_span, opening_line, is_chained, body, text
    inside_lines, split_inside(children), setup(children)     → shared here from BraceBlock/PythonBlock
    scenarios(), backgrounds(scenarios), steps(skip), written(lead)   abstract
    + keyword                                          + a step block says its own Given/When/Then/And/But
    + description_lines                                + the comment above a story block
  BraceBlock(StoryBlock), PythonBlock(StoryBlock)

CodeStory
+ from_block(block: StoryBlock)                        builds name, description, backgrounds, scenarios, steps AND code from the block
- load_all / load_file / load(content, scenario_blocks) / read_code / fill
CodeScenario
+ from_block(block: StoryBlock)
- read(body, example_names) / read_code

StorySyntax                                            ~ shrinks to what is not block structure:
  example_names, example_imports, story_name (tier suffix), description marks
- steps_in, _calls_in, scenario_blocks, backgrounds_in, story_texts, _balanced, _outside_scenarios
- BraceSyntax._CALL, scenario_pattern, _BACKGROUND, _CALL_NAME, without_background, _inside_scenario
- PythonSyntax._CALL, scenario_pattern, backgrounds_in
- is_screen_spec / is_shared_story_file second call sites (script_story_model.py:37, python/nodes.py:63)
```

**Callers affected.** `Stories._take_story_test` (stories.py:185) and `story_tests` (241); `StoriesReading._take_code_scenarios` (graph_reading.py:200); `ReshapedStoryFile.__init__` and `_story_blocks` (reshaped_story_file.py:48, 76); `CodeStoryModel._read_story_file`; the three language packages; specs `code_story_behaviours_spec.py`, `code_story_model_spec.py`, `reshaped_story_file_spec.py`, `typescript_story_model_spec.py`, the python and javascript model specs, `example_facts_spec.py`.

**Size.** About 12 production files; roughly 250 lines removed and 120 added. Specs that call `load_all`/`stories_of` directly change (about 10 call sites).

**What could go wrong.** A file the block reader cannot parse (a Python story test with a syntax error, `PythonStoryFile._tree is None`) is read today by the regex path as a fallback; with one reader that file reads as no stories unless a fallback is kept on purpose. A story file with no `story(...)` block is read today as one story from its text (story_file.py:62-63); that case needs a block-free path too. The regex path also tolerates brace code the block reader skips when a call is not "whole" (`BraceCall.is_whole`, brace_story_file.py:38). These three behaviours must be pinned by specs before the regex path is deleted; if they cannot be met by blocks, keep `StorySyntax` as the named fallback and still do the `StoryBlock` base and the `StoryFile` kinds, which carry no such risk.

### S2. A project's story files read by one object, and a thin `Stories`

**Problem.** `Stories` (stories.py:87-279) is 190 lines of file reading with `project` threaded through eleven operations and `on_file` through five; `StoriesReading` repeats parts of it (`_code_readers`, `_take_code_scenarios`, `_story_tests`, graph_reading.py:133-257) with its own root. Two classes each decide which code adapter reads a path and each build fresh adapters with a different tests root (stories.py:208; graph_reading.py:208).

**Before**

```
Stories(PracticeGuidance)
  read_folder(root, on_file) -> StoryModel
  read_files(files, project, on_file) -> StoryModel
  open_file(path, project)
  story_tests(project) -> dict[str, list[str]]
  story_test_sources(test, project) -> StorySources
  _take_stories_only_code_holds(merged, tests, project)   _epic_along(merged, story)
  _maps_to_read(paths, tests, project)                     _maps_beside(tests, project)
  _story_map_of_code(tests, project, on_file)              _named_map(test, project)
  _texts_by_reader(tests, project)                         _story_test_reader(path)
  _read_story_test(path, project, on_file)                 _take_story_test(merged, test, project)
  _story_map_file(path, project, on_file)                  _merge_epics(holder, epics)

StoriesReading
  _code_readers, _script_readers, _take_code_scenarios(model), _story_tests(), _script_texts(reader)
```

**After**

```
Stories(PracticeGuidance)                                  ~ thin
  story_files(project, on_file=None) -> ProjectStoryFiles  + the one way in
- read_folder / read_files / open_file / story_tests / story_test_sources and the twelve private helpers
                                                           → ProjectStoryFiles

+ ProjectStoryFiles  (model/project_story_files.py)        the story maps and story tests of one project
    __init__(formats: StoriesFormats, project: Path, on_file)
    code_readers -> list[CodeStoryModel]                   → from Stories._story_test_reader and StoriesReading._code_readers
    reader_of(path) -> CodeStoryModel | None
    story_map_in(folder) -> StoryModel                     ← read_folder
    story_map_of(files) -> StoryModel                      ← read_files
    opened(path) -> StoryModel                             ← open_file
    story_tests(written_files) -> dict[Path, list[Story]]  ~ answers stories, not names
    sources_of(test: StorySource) -> StorySources          ← story_test_sources
    take_code_scenarios(model, edited)                     ← StoriesReading._take_code_scenarios
    (private: the merge and map-finding helpers, none taking project or on_file)

StoriesReading
~ read_working_copy uses self.practice.story_files(self.root, on_file=...)
- _code_readers, _take_code_scenarios                      → ProjectStoryFiles
```

**Callers affected.** `StoriesFormats.read` (stories_formats.py:99); `StoryModel.load` (story_model.py:1341); `OpenedStoryMap._acceptance_tests` (opened_story_map.py:118); `StoriesReading` (graph_reading.py:130-257); `harness/diagnostics/desktop_walk_question.py:97` (`story_tests(`); specs `stories_spec.py:84, 110, 144`, `space/kanban/kanban_spec.py:489`, `example_facts_spec.py`.

**Size.** 5 production files, one new; about 200 lines moved, 30 removed (the threaded parameters and the duplicate reader list). No behaviour changes.

**What could go wrong.** `StoriesReading` passes its reading root as "project" while `StoriesFormats` passes the session's repository; the two are not always the same folder (graph_reading.py:192 computes a separate `project` from `graph.scope.folder`). The new object must take the root files are named from and the project imports are resolved in as two named values where they differ, or node file paths will change and saved graphs will not match. The harness reads `reading_type`, `formats_type` and `first_fidelity` from the practice class; none of that moves.

### S3. `StoryNode` keeps the story map; code, rule facts and drawing widths move to the parts that use them

**Problem.** `StoryNode` (story_model.py:77-287) is the hierarchy, the kept code, eleven rule facts, the recording names, and the edit tools. `EpicColumns` and six layout constants (43-52, 1508-1562) are drawing concerns in the core file. `Example` and `Increment` carry `written`, `file_written`, `setup` and eleven fact fields they never use.

**Before**

```
StoryNode
  name, sequential_order, estimate, description_text, evidence
  written, file_written, setup                       # code as read
  opening_token, opening_class, child_count, child_label, child_band, child_target,
  near_duplicate, generic_handler, shared_verb, artifact_name, camel_case_path
  load_map_facts(), _load_opening(), _load_path_case(), _load_child_band(count, label, fewest, most)
  take_code_from(source)
  rename / edit_description / move_before / remove    # tools
Epic
  columns: EpicColumns      # leaf_epics, estimate_label, has_estimate, span, diagram_span, tree_depth
name_facts.py               # opening_of, names_generic_handler, file_name_facts (functions)
```

**After**

```
StoryNode
  name, sequential_order, estimate, description_text, evidence
+ facts: NameFacts                                   + one part; graph_facts reads through it
- opening_token … camel_case_path (11 fields)        → NameFacts
- _load_opening, _load_path_case, _load_child_band   → NameFacts
~ load_map_facts()                                   ~ each kind sets only what differs (child band, near duplicate, shared verb)
  rename / edit_description / move_before / remove

+ NameFacts(node)            (name_facts.py; the verb lists stay as its data)
    opening_token, opening_class, generic_handler, artifact_name, camel_case_path
    child_count, child_label, child_target, child_band
    near_duplicate, shared_verb
    load(children: ChildBand)                        ← _load_child_band(count, label, fewest, most)
- opening_of(), names_generic_handler(), file_name_facts()   → NameFacts (private)

+ CodeHeld (mixin or part on Epic, Story, Background, Scenario, Step only)
    written, file_written, setup, take_code_from(source), take_code_in(language, kept)
                                                     ← CodeStoryModel._take_code / _take_step_bodies
- Example.written/file_written/setup, Increment.written/file_written/setup

Epic
- columns: EpicColumns                               → DiagramEpic.columns (diagram_story_model.py)
EpicColumns, _ESTIMATE_* constants                   → diagram_story_model.py
```

**Callers affected.** `graph_facts` consumers in `harness/graph/model_node.py` (how a node's facts are read by name; needs a look at whether a nested part is supported or the facts stay as delegating properties); the seven story-map rules read facts by name from the graph, so they do not change; `drawio/nodes.py:192, 380`, `miro/nodes.py:252`, `diagram_story_model.py:332`, `ux/model/claude_design/story_canvas.py:216, 242, 305` for `columns`; `CodeStoryModel._adopt_code` and helpers (code_story_model.py:522-570); specs `story_model_spec.py:968, 975`, `child_count_fits_layer_spec.py:37`, `story_scenario_count_spec.py:77`.

**Size.** About 8 production files; 150 lines moved, 30 removed. Three separable steps: (a) `EpicColumns` to the diagram model, smallest and safest; (b) `NameFacts`; (c) code held only by nodes that hold code.

**What could go wrong.** (a) The UX story canvas builds `EpicColumns` answers from a plain `StoryModel` it copies into diagram types; if it ever calls `columns` on a base `Epic`, the move breaks it, so check story_canvas.py:216-305 first. (b) If the graph reads facts with `getattr(node, name)`, the eleven names must remain readable on the node (delegating properties), which keeps the surface and only moves the logic. (c) `take_code_from` uses `getattr(source, "written", None)` (story_model.py:165-169) because sources may be of any node kind; narrowing which nodes hold code needs every copy path checked, which S5 would make one path.

### S4. `StoryTree` answers every question the graph's link writers and rules ask

**Problem.** Four link writers (`StoryLinks`, `ExampleObservations`, `ModelledAreas`, `TermLinks`) and the scenario rules each walk the Stories graph themselves: three copies of `_STEP_TYPES`, two of `_EPIC_TYPES`, two `_step_body`, two `examples`, two upward epic walks (graph_reading.py:269; modelled_areas.py:141), two "story of a scenario" lookups in the rules (scenarios.py:291, 396) and a third in `ExampleObservations._givens_of` (modelled_areas.py:81-91). `StoryTree` exists and answers four questions.

**Before**

```
StoryTree(stories)
  epic_of(node), sub_epics(epic), stories_under(epic), scenarios(story), steps(scenario)

StoryLinks(stories, clean, tree)         graph, examples, _step_body, story_files, …
ExampleObservations(stories, tree)       graph, examples, _step_body, _givens_of, _backgrounds_of
ModelledAreas(stories)                   graph, _area_of
TermLinks(stories, model)                graph, _examples_by_file
rules/scenarios.py                       _keyword/_text/_phase functions; _background_steps; _parent_story
```

**After**

```
StoryTree(stories)                       (own file, story_tree.py)
  epic_of(node), sub_epics(epic), stories_under(epic), scenarios(story), steps(scenario)
+ every_step() -> list[Node]             ← the four `nodes() if type in _STEP_TYPES` walks
+ examples() -> list[Node]               ← StoryLinks.examples, ExampleObservations.examples
+ examples_of_file(file) -> list[Node]   ← TermLinks._examples_by_file
+ step_body(step) -> str                 ← both _step_body
+ scenario_of(step), story_of(scenario)  ← _givens_of walk; rules' _parent_story / _background_steps
+ background_steps(story)                ← ExampleObservations._backgrounds_of; two rules
+ area_of(node)                          ← ModelledAreas._area_of
+ STEP_TYPES, EPIC_TYPES                 the one definition

StoryLinks(tree, clean)                  ~ takes the tree; reads stories and graph from it
ExampleObservations(tree)                ~
ModelledAreas(tree)                      ~
TermLinks(tree, model)                   ~
+ StepRule(PracticeGraphRule)            (rules/scenarios.py) keyword(), text(), phase(), is_a("when")
                                         ← _keyword/_text/_phase and the six repeated gates
```

**Callers affected.** `StoriesReading.read_working_copy` (graph_reading.py:137-151); `ux/model/explorer_tree.py` (already uses `story_tree`); thirteen rule classes in scenarios.py; `RuleCheckContext` would need a way to reach the tree (`context.practice.reading.story_tree` exists today).

**Size.** 5 production files; about 70 lines removed, 50 added. Stories core fix 8 above is the first slice of this and can go alone.

**What could go wrong.** Rules run on a graph reloaded from `graph.json` where nodes are plain; `StoryTree` is written for that (its docstring says so), but `ScenariosShape._parent_story` also reads `node.parent` first, which only parsed objects have. Dropping that branch is only safe if the `scenarios` edge is always recorded; `Scenario.record` (story_model.py:889) does record it.

### S5. One copy path per node, and class hooks named apart from `StoryType` and `StepType`

**Problem.** Each node has a copy-constructor and a `clone()` that list the same fields (about 60 duplicated lines; see the story_model.py finding), and the hooks that say which class to build are named `step_type`, `story_type`, `scenario_type`, `background_type`, `epic_type`, `increment_type`, `writing_type` beside the domain values `Step.step_type: StepType` and `Story.story_type: StoryType`, with `story_class` and `build_story` for the same idea in `Epic.__init__`.

**Before**

```
Scenario(name: str | Scenario, sequential_order)     clone()            # two field lists
Story(name: str | Story, sequential_order, story_type)   _copy_from(); clone()
Epic(name: str | Epic, sequential_order, *, story_class) clone()
Background(name: str | Background, sequential_order)     clone()
StoryModel(source: StoryModel | Graph, graph)            _copy_from(); clone()
Scenario.step_type = Step; Scenario.background_type = Background
Story.scenario_type = Scenario; Story.background_type = Background
StoryModel.epic_type = Epic; .story_type = Story; .increment_type = Increment
CodeStoryModel.writing_type = StoryWriting
```

**After**

```
Scenario(name: str, sequential_order)                ~ name is a name
+ Scenario.copy_of(source: Scenario) -> Scenario     + classmethod factory (mapping factory, allowed static); the one field list
~ clone() = type(self).copy_of(self)
  (the same for Story, Epic, Background, Step, Increment, StoryModel)
- Epic.__init__(story_class=)                        → the story class comes from the map: story_map.story_class
~ step_type → step_class; background_type → background_class; scenario_type → scenario_class
~ epic_type → epic_class; story_type (on StoryModel) → story_class; increment_type → increment_class
~ writing_type → writing_class
  Step.step_type: StepType, Story.story_type: StoryType   unchanged
```

**Callers affected.** Every format package (`markdown`, `json`, `drawio`, `miro`, `whiteboard`, `sketch`, `python`, `typescript`, `javascript`) sets these hooks and calls the copy-constructors; `ux/model/claude_design/story_canvas.py`; `patterns/lern_domain_driven/.../fixtures.py`; most stories specs.

**Size.** About 20 production files, mostly one-line renames; 60 lines removed in story_model.py. Mechanical but wide.

**What could go wrong.** `Epic(source)` builds each story with the *map's* story class (converting formats) while `Epic.clone()` keeps each child's own class; they are not the same operation today. `copy_of` must take the target classes from the receiving map, and `clone` must pass "same classes as the source". Getting this wrong turns a `MarkdownStory` into a base `Story` on clone, which loses format behaviour silently; the round-trip specs (`story_channel.feature.py` if revived, and each format's model spec) are the guard. Per the no-legacy rule, the rename has to land in one pass across all formats.

### S6. Name the class `StoryMap`

**Problem.** The practice's language is *story map* everywhere a person reads it: the fidelity (`story_map`), the file (`story-map.md`), the class's own docstring, `OpenedStoryMap`, `StoryMapFiles`, `StoryMapEditRefused`, `node.story_map`, the app's `StoryMapClient`. The root class is `StoryModel`, so the published MCP toolset is `story-model.*` (`story-model.show`, `story-model.new_epic`, `story-model.open_in_session`) beside `epic.*`, `story.*`, `increment.*`, and nine adapters are `MarkdownStoryModel`, `JsonStoryModel`, and so on. `domain-nouns-only` warns against generic `*Model` names for exactly this reason.

**Before / After**

```
StoryModel                  ~ StoryMap
CodeStoryModel              ~ CodeStoryMap          (and Brace…, Script…, Python…, TypeScript…, JavaScript…)
DiagramStoryModel           ~ DiagramStoryMap       (DrawIO…, Miro…, Whiteboard…)
MarkdownStoryModel, JsonStoryModel, SketchStoryModel   ~ …StoryMap
MCP toolset  story-model.*  ~ story-map.*
TypeScript   StoryModelClientGenerated  ~ StoryMapClientGenerated (generated)
model/story_model.py        ~ model/story_map.py    (module path)
```

**Callers affected.** Every file in `stories/model`, `stories/app` (generated client and its subclass), `ux/model/claude_design/story_canvas.py`, `space/kanban`, `space/session`, `harness/diagnostics`, the installed skills and commands that name `story-model.*`, session documents that name the tools, and every stories spec.

**Size.** 60+ files, almost all mechanical. A reinstall for every IDE, since tool names change.

**What could go wrong.** Saved chats, handoffs and board comments that name `story-model.*` tools stop resolving; by the repository's no-legacy rule no alias may be kept. The semantic type string `"StoryModel"` (`_semantic_type_name`, story_model.py:1290) is saved in graphs, so saved `graph.json` files need a rebuild or the string is left as is (and then it is a second name). This is the costliest proposal for a naming gain only; worth doing at a version boundary together with S5, not alone.

### S7. Code-language types Stories uses get a home outside Clean Engineering's model package

**Problem.** Seventeen Stories files import from `cdd_guidance/practices/clean_engineering/model/` : `code_body` (`CodeBody`, `CodeLanguage`, `WrittenBlock`, `WrittenKey`, `BraceCall`, `InsideLines`, `PYTHON`, `TYPESCRIPT`, `JAVASCRIPT`), `bracket_structure` (`BracketStructure`), `call_graph` (`CallGraph`), `base_class_model` (`MODULE_FUNCTION_HOLDER`). Clean Engineering's card names only *CodeBody* among the terms other packages use, so eleven of twelve names are reached past its seam. None of them is about classes or operations; they are about source text in a language.

**Before**

```
clean_engineering/model/code_body.py          CodeBody, CodeLanguage, WrittenBlock, WrittenKey, BraceCall, InsideLines, PYTHON, TYPESCRIPT, JAVASCRIPT
clean_engineering/model/bracket_structure.py  BracketStructure
clean_engineering/model/call_graph.py         CallGraph
stories/model/* (17 files)  ──imports──▶  clean_engineering/model/*
```

**After**

```
+ cdd_guidance/practices/code_text/           (a module with its own card; name to be agreed)
    code_body.py, bracket_structure.py        → moved, unchanged
    Seam: CodeBody, CodeLanguage, WrittenBlock, BraceCall, InsideLines, BracketStructure, the language constants
clean_engineering/model/*   ──imports──▶  code_text
stories/model/*             ──imports──▶  code_text
CallGraph, MODULE_FUNCTION_HOLDER             stay in Clean Engineering and are added to its card's terms,
                                              since they are its model (a step's realization, a function's holder)
```

**Callers affected.** Every importer of `code_body` and `bracket_structure` in `clean_engineering`, `stories`, `bdd`, `ux`, and `actions/render` (outside this area; the lead should count them across slices).

**Size.** Two files moved, import lines changed in 40+ files, one new card, one card edited. No logic changes.

**What could go wrong.** Little in behaviour. The cheaper alternative is to add the twelve names to Clean Engineering's card as terms other packages use; that makes the dependency honest without moving anything, but leaves Stories' code formats unable to load without the whole Clean Engineering model package.

### A1. One story-map format contract: every format reads a file and writes a file the same way

**Problem.** `harness/guidance/practice_formats.py:31-38` declares `FormatAdapter` as a Protocol with `parse(content)` and `render(model, **options)`, and `_call_render` (:272-283) inspects each adapter's `render` signature to find out whether it takes `previous` and `workspace`. The Stories formats therefore each have their own shape:

| Format | render | parse result | load | from_workspace |
|---|---|---|---|---|
| markdown (`markdown/nodes.py:503, 583, 416`) | `(canonical, previous, workspace)` | new model | — | `(root, on_file, project)` → Optional |
| json (`json/nodes.py:278, 291, 304`) | `(canonical, previous)` | fills self | — | `(root)` → Optional |
| drawio (`drawio/nodes.py:391, 423, 441, 428`) | `(canonical=None, previous, workspace)` | new hard-coded model | alias | `(path, on_file, project)` |
| whiteboard (`whiteboard/nodes.py:120, 136, 140`) | `(canonical=None, previous)` | new hard-coded model | copy | none — `AttributeError` at `stories.py:199, 253` |
| miro (`miro/nodes.py:229, 233, 303`) | `(canonical=None, previous)` | new hard-coded model | alias | none |
| sketch (`sketch_story_model.py:291, 250`) | `(canonical=None, previous)` | fills self | — | none |

`stories.py:98-99, 197-199, 253` choose between these with `isinstance` tests and differing keyword arguments. UX has the same spread (`JsonUxMap.render(canonical)` without `previous`; `UxMap.from_workspace(root)`).

**Before**

```
StoryModel
  copy_of(source)
MarkdownStoryModel(StoryModel)      render(canonical, previous, workspace); parse(text, file) -> new
                                    from_workspace(root, on_file, project); opened_from(path, project)
JsonStoryModel(StoryModel)          render(canonical, previous); parse(text) -> self
                                    from_workspace(root); parse_file(file, text)
DrawIOStoryModel(DiagramStoryModel) render(canonical?, previous, workspace); parse = load(text) -> new
                                    from_workspace(path, on_file, project)
WhiteboardStoryModel                render(canonical?, previous); parse(text); load(text)   (no from_workspace)
MiroStoryModel                      render(canonical?, previous); parse = load(text)        (no from_workspace)
Stories.open_file / _story_map_file -> formats.for_file(path).from_workspace(...)   (isinstance MarkdownStoryModel)
PracticeFormats._call_render        -> inspect.signature(target.render)
```

**After**

```
StoryModel
  copy_of(source)
+ render(canonical, written: Written) -> str      # one signature; Written holds previous text and the folder
+ parse(text, file="") -> Self                    # always fills and returns self
+ read_file(path, project, on_file=None) -> Self  # default: parse(path.read_text(), file) + sources + place_in
MarkdownStoryModel   ~ render(canonical, written)   ~ parse fills self
                     ~ from_workspace → read_file (file) and read_folder (folder merge), opened_from kept
JsonStoryModel       ~ render(canonical, written)   - parse_file → read_file
DrawIOStoryModel     ~ render(canonical, written)   - load   - from_workspace → inherited read_file
WhiteboardStoryModel ~ render(canonical, written)   - load   + inherited read_file  (fixes the AttributeError)
MiroStoryModel       ~ render(canonical, written)   - load   + inherited read_file
+ Written (harness/guidance, beside RenderRequest): previous: str, folder: Path | None
PracticeFormats._call_render  ~ target.render(parsed, request.written)   - inspect.signature
```

**Callers affected.** `stories.py` (three call sites lose their `isinstance` and keyword differences), `stories_formats.py`, `harness/guidance/practice_formats.py` (`_call_render`), and — because the contract is in the harness — the UX, Clean Engineering, DDD, and BDD adapters' `render` signatures (about 20 classes), plus every spec that calls `render(canonical, previous=…)` by keyword (those keep working if `Written` is built from the same keywords at the spec's edge, but the cleaner change edits them).

**Size.** About 12 production files in Stories, 1 in the harness, 15–20 adapter classes in the other practices; roughly 250 changed lines and 60–80 spec call sites. Can be done in two passes: Stories first with `_call_render` accepting both shapes for one pass is **not** allowed by the no-legacy rule, so the harness and all adapters change together.

**What could go wrong.** `parse` filling `self` changes behaviour where a caller parses twice on one adapter instance (`MarkdownStoryModel._replaced_outline` builds a fresh instance already; `DrawIOStoryModel.render` would need the same care). The harness change touches every practice in one commit, so it needs the heavy tier. If the product owner wants a smaller step, do only the Stories-side unification (`read_file` on `StoryModel`, delete `load`, `parse` fills `self`) and leave `render`'s signature and the `inspect` call alone; that fixes the whiteboard defect and removes three `isinstance` branches for about 100 lines.

### A2. One draw.io document and one board key, shared by every practice

**Problem.** Three practices each read and write the draw.io file envelope and each keep the layout a person made:

| Job | Stories | UX | Clean Engineering (DDD inherits it) |
|---|---|---|---|
| Parse text to the diagram root, name the failure | `drawio/nodes.py:457-469`, again at :505-511; `DrawIOParseError` :204 | `ux/model/drawio/nodes.py:365-370`; `UnreadableDrawio` :71 | `drawio_class_model.py:118-123`; `UnreadableSource` |
| Pages by name | one page assumed | `_page_named` :386 | `DrawioPage.pages_in` `drawio_page.py:40-48` |
| Cells with `UserObject` wrapping | `_vertices` :471-488, `_drawn_geometries` :314-320 | `iter("mxCell")` :392, :401 | `DrawioPage.cell` :58 |
| Style string to values | `_PlacedCell.__init__` :216-219 | `CellStyle` :90-118 | `style_value`, `style_number` `drawio_page.py:206-217` |
| Cell box | `_PlacedCell` :220-223 | `Callout._corner` :311 | `cell_box` :164, `positions` :62 |
| Write a page | `_DrawIOPage` :250-278 | external CLI | `_add_diagram_page` `drawio_class_model.py:436` |
| Keep a person's layout | `_KeptPlaces` :281-311 | `keep_what_only(held)` | `_previous_pages` :425-434 |
| Whiteboard element key | `_BoardStoryNode.board_key` `whiteboard/nodes.py:34-44` (+ :75, :210) | `DrawnNode.board_key` `ux/model/whiteboard/nodes.py:63-76` | `_key` `whiteboard_class_model.py:79-80` |

Estimated duplicated lines: about 130 for draw.io (Stories 95, UX 45, against the Clean Engineering versions) and about 30 for the board key. The whiteboard side already shows the target shape: `harness/whiteboard` owns `Whiteboard`, `BoardElement`, `Box`, and `keep_places`, and all four practices use them.

**Before**

```
harness/whiteboard:  Whiteboard(from_text, keep_places, draw, save)  BoardElement  Box  WhiteboardNode(board_box, board_elements, board_shape)
stories/drawio:      _DrawIOPage(add, text)  _KeptPlaces(from_text, place)  _PlacedCell  DrawIOStoryModel.Vertex  DrawIOParseError
ux/drawio:           CellStyle  UnreadableDrawio  DrawioUxMap._diagram_of/_page_named
clean_engineering/model/drawio/page:  DrawioPage(pages_in, whole, cell, positions)  cell_box  style_value
stories/whiteboard:  _BoardStoryNode.board_key   KEY_LENGTH=10
ux/whiteboard:       DrawnNode.board_key          KEY_LENGTH=10
clean_engineering/whiteboard:  _key(*names)       KEY_LENGTH=12
```

**After**

```
+ harness/drawio (new module, beside harness/whiteboard):
    + DrawioFile(from_text -> raises UnreadableDrawio, pages, page(name), save)        ← DrawioPage.pages_in/whole, _graph_model, _diagram_of
    + DrawioPage(cells, cell(id), add(cell), positions)                                 ← clean_engineering DrawioPage (geometry parts), _DrawIOPage, _vertices
    + DrawioCell(id, label, style: CellStyle, box: Box, link)                           ← DrawIOStoryModel.Vertex, _PlacedCell's reading, cell_box
    + CellStyle(get, role, number)                                                      → moved from ux/model/drawio/nodes.py:90; style_value/style_number fold in
    + DrawioFile.keep_places(previous)                                                  ← _KeptPlaces.place, _previous_pages
  harness/whiteboard:
    + WhiteboardNode.board_key(path: Sequence[str]) / Whiteboard.key(*names)            ← three hash functions
stories/drawio:   - _DrawIOPage  - _KeptPlaces  - _drawn_geometries  - DrawIOParseError  ~ _PlacedCell reads a DrawioCell  ~ Vertex → DrawioCell
ux/drawio:        - CellStyle (→ harness/drawio)  - UnreadableDrawio  - _diagram_of  - _page_named
clean_engineering/model/drawio/page: ~ DrawioPage keeps only edge routing (segments, edges_by_ends) over harness DrawioPage
stories/ux/clean_engineering whiteboard: - board_key bodies, - KEY_LENGTH ×3
```

**Callers affected.** `stories/model/drawio/nodes.py`, `ux/model/drawio/nodes.py`, `clean_engineering/model/drawio/drawio_class_model.py`, `drawio/page/drawio_page.py`, the Clean Engineering drawio scanners that call `cell_box` / `style_value` (about eight files), `ddd/model/drawio/*` through inheritance, the three whiteboard adapters, and the specs that catch `DrawIOParseError` / `UnreadableDrawio` by name. A new `harness/drawio/.context/module-context.md` and a line in the root card.

**Size.** One new harness module of about 200 lines; about 180 lines removed across the practices; 12–15 files touched; the element-key change alone is 4 files and about 30 lines and can go first.

**What could go wrong.** Changing `KEY_LENGTH` or the hashed path changes every element id, so an existing `.whiteboard` file would no longer keep its places on the next render — keep each practice's key input and length exactly (Clean Engineering keeps 12) and move only the hashing. The keep-layout rules differ in a real way (Stories widens an epic that grew, `drawio/nodes.py:310`; Clean Engineering also keeps edges), so `keep_places` needs a hook for "this cell may grow", or Stories keeps that one rule. Clean Engineering's `DrawioPage` is used by eleven scanners; moving its geometry half is the riskiest part and is outside the area this report was asked to judge, so the product owner may prefer to do Stories and UX first and leave Clean Engineering on its own page class until its own round.

### A3. The thin slice as one layout that each drawn format only turns into its own elements; Miro reads by position like the others

**Problem.** `DiagramStoryModel` already owns the thin slice's arithmetic (`thin_slice_columns`, `thin_slice_lanes`, `thin_slice_widths`, :305-326), but returns tuples and dictionaries, so `_ThinSliceDrawing` (`drawio/nodes.py:536-581`, 46 lines) and `_ThinSliceBoard` (`whiteboard/nodes.py:175-224`, 50 lines) each walk them again with the same two loops, and Miro ignores them and builds a table from its own column rule (`miro/nodes.py:237-270`). Miro also reads a story map by file order (`_MiroReading`, :178-216) while the other two read by position (`place_cells`), so a card moved on a Miro board lands under the wrong epic.

**Before**

```
DiagramStoryModel
  thin_slice_columns() -> List[tuple]            # (epic, sub)
  thin_slice_lanes(columns) -> List[tuple]       # (increment, {column index: [stories]})
  thin_slice_widths(lanes, pitch, gap) -> List[int]
  save_thin_slice() -> raises NotImplementedError
  place_cells(cells)
_ThinSliceDrawing(story_map, page)   text(), _headers(), _lane()       # drawio
_ThinSliceBoard(story_map, drawing)  board(), _draw_lane(), _map_story() # whiteboard
MiroStoryModel  save_thin_slice(), _thin_slice_columns(epic), _thin_slice_svg(), load() -> _MiroReading
_MiroReading(story_map)  read(element), _sub_epic(), _story()
```

**After**

```
+ ThinSliceLayout (stories/model/diagram_story_model.py), built by DiagramStoryModel.thin_slice(pitch, gap)
    + columns: List[ThinSliceColumn]     # epic, sub_epic, left, width   (names what the tuples held)
    + lanes: List[ThinSliceLane]         # increment, top, cards: List[(story, left)]
    + epic_headers() / sub_epic_headers()  -> boxes with their node
    + draw_on(surface)                   # calls surface.header(node, box), surface.lane(increment, box), surface.card(story, box)
DiagramStoryModel
  - thin_slice_columns  - thin_slice_lanes  - thin_slice_widths   → ThinSliceLayout
  ~ save_thin_slice(): concrete here: self.thin_slice(...).draw_on(self.thin_slice_surface()); formats override thin_slice_surface()
DrawIOStoryModel       - _ThinSliceDrawing  + _DrawioThinSliceSurface(page)   (header/lane/card → Vertex, ~15 lines)
WhiteboardStoryModel   - _ThinSliceBoard    + _BoardThinSliceSurface(board)   (~15 lines)   - _map_story (layout hands over the map's own story)
MiroStoryModel         ~ save_thin_slice keeps its table but reads columns from ThinSliceLayout   - _thin_slice_columns
                       - _MiroReading   ~ parse: rects → DiagramStoryCell → place_cells
```

**Callers affected.** `stories_formats.py:33` (`ThinSlicedMap.drawn_by`) is unchanged; `ux/model/claude_design/story_canvas.py` inherits a `save_thin_slice` that now needs either a surface or an explicit "does not draw thin slices" answer instead of `NotImplementedError`. Specs: `drawio_story_model_spec.py` (thin slice section), `whiteboard_story_model_spec.py`, `miro_story_model_spec.py` (its thin-slice table columns for nested sub-epics are named `Epic / … / Leaf` today; if Miro adopts the shared columns those headers change, so decide whether Miro keeps its header text).

**Size.** 4 production files, about 120 lines removed and 90 added; Miro reading by position is a further 40 removed and 15 added.

**What could go wrong.** Miro by position changes what a hand-edited SVG reads as when cards overlap or sit outside every bar; `owner_among` already has rules for that (story id names its bar), but Miro ids are built differently (`epic-1-slug/sub-1-slug-d0/story-1-slug`, :97, :148), so `owner_among`'s "id names its bar" rule needs the Miro id shape or Miro ids need to become the shared shape — the second breaks round trips of existing Miro boards. The drawio and whiteboard thin slices have small layout differences today (label on the left outside the columns vs inside the lane); the surface must keep each, or the pictures change.

### A4. Story UI: typed story nodes instead of an address, a kind string, and thirty-six callbacks

**Problem.** The page keeps three parallel descriptions of a node: the generated data (`EpicData`, `StoryData`), a view model (`EpicViewModel`, …) that knows its kind but has no behaviour, and `StoryMapNode(address, kind)` that has behaviour but is told its kind by the caller. Between them sit `StoryMapViewModel.kinds`, `MapEditing.kindOf` (defaulting to `'epic'`), the `if` chain in `StoryMapNode.client()`, thirty-six callbacks in `StoryHierarchyViewProps` (`story-map-views.tsx:575-622`), and four `…EditsOf` functions (:1798-1856) that turn ids back into nodes. Evidence of the cost: `nodeAt(sub, 'epic')` for sub-epics (:1818-1822); ignored id parameters (:1806, :1823, :1840); `newStory` callable on a step; `addThenPlace` inferring the new node as "the last sibling" (:1785-1794).

**Before**

```
StoryMapClient(StoryModelClientGenerated)
  nodeAt(address, kind) -> StoryMapNode ; exampleAt(address) ; incrementAt(address)
  reorder(before[], after[], kind) ; answerTo(edit) ; takeOn(read) ; chooseFormat(format, isChosen)
StoryMapNode(map, address, kind)      rename, describe, remove, moveBefore, newSubEpic, newStory, newScenario, newStep, editText, client()
StoryMapExample(map, address)         editField, remove
StoryMapIncrement(map, address)       deliver, stopDelivering
StoryNodeViewModel(id, parent_id, name, description, sequential_order, semantic_type)
  EpicViewModel(sub_epics)  SubEpicViewModel(stories)  StoryViewModel(scenarios, acceptance_tests)  ScenarioViewModel(steps: StepRowDto[], examples)
  IncrementViewModel(stories: string[])   StoryMapViewModel(epics, increments, kinds, incrementOf)
MapEditing(storyMap, edit)            kindOf, subEpicsOf, storiesOf, addThenPlace
epicEditsOf / storyEditsOf / scenarioEditsOf / incrementEditsOf -> HierarchyEdits (36 callbacks)
StoryHierarchyView(props: 36 callbacks)
```

**After**

```
StoryMapClient
  ~ epics: EpicOnPage[] ; increments: IncrementOnPage[]        # built once from each answer, replacing StoryMapViewModel.of
  - nodeAt  - exampleAt  - incrementAt  - reorder
  answerTo, takeOn, chooseFormat unchanged
+ StoryNodeOnPage (abstract: map, data)          name, description, rename(name), describe(text), remove(), moveBefore(other: StoryNodeOnPage)
  + EpicOnPage      subEpics, stories ; newSubEpic(name, after?), newStory(name, after?)        ← EpicViewModel + SubEpicViewModel + StoryMapNode(epic)
  + StoryOnPage     scenarios, acceptanceTests, increment ; newScenario(name)                   ← StoryViewModel + StoryMapNode(story)
  + ScenarioOnPage  steps, examples ; newStep(keyword, text)                                    ← ScenarioViewModel
  + StepOnPage      keyword, text ; editText(text)                                              ← StepRowDto
  + ExampleOnPage   fields ; editField(field, text), remove()                                   ← StoryMapExample
  + IncrementOnPage stories ; deliver(story: StoryOnPage), stopDelivering(story)                ← IncrementViewModel + StoryMapIncrement
- StoryMapNode  - StoryMapExample  - StoryMapIncrement  - NodeKind  - SemanticType  - StoryMapViewModel.kinds
- MapEditing  - epicEditsOf  - storyEditsOf  - scenarioEditsOf  - incrementEditsOf  - HierarchyEdits
StoryHierarchyView(props: storyMap, view state, edit(change))   ~ each card calls its own node: edit(() => story.rename(name))
```

Each `…OnPage` class holds its generated client (`EpicClientGenerated.named(api, data.node)`) made once, so `client()` and its `if` chain go. "Add after" becomes `epic.newStory(name, after)`, which still does add-then-move, but in one place that knows the answer's shape; a later Python change (`new_story(name, before=…)`) would then remove the second call without touching the views.

**Callers affected.** All four files of `app/story-map/` and `main.tsx`; the app's specs (`story-map-client` and view-model specs, and the board's `*.story.ui.spec.ts` that drive the page); nothing in Python.

**Size.** The largest proposal here: `story-map-client.ts` and `story-map-view-models.ts` rewritten (about 330 lines → about 300), about 150 lines removed from `story-map-views.tsx` (`MapEditing`, the four functions, the props interface) and several hundred lines of markup touched to call nodes instead of callbacks. Realistically 600–800 changed lines and most of the app's specs.

**What could go wrong.** React identity: view models are rebuilt on every two-second read (`READ_EVERY_MILLISECONDS`), so node objects must not be used as keys or held across renders — keep `data.node` as the key. The ticket scope filter (`EpicViewModel.within`) builds filtered copies; with behaviour on the nodes, a filtered epic must still edit the real epic. The "epic's own stories shown as a sub-epic" trick (`EpicViewModel.of`, :121) has to become an explicit display grouping rather than a fake node, or the confusion moves into the new classes. Drag and drop is the area with the least unit coverage. A smaller first step that removes most of the risk of wrong calls: keep the view models, replace `nodeAt(address, kind)` with `epicAt(address)`, `storyAt`, `scenarioAt`, `stepAt` returning four small typed classes (about 80 lines), and delete `kinds` / `kindOf`.

### A5. A read markdown document keeps typed lines, not `object` parts and positional tuples

**Problem.** The markdown adapter's promise is "a file is written back as read, except where the model changed". It is implemented four ways in one package: `OutlineLines` on epics, stories, and the map (`map_reading.py:213`); `IncrementLines` (`thin_slice.py:28`); `ExampleRowLine` (`markup.py:36`); and, for scenarios files, untyped parts — `DocumentPart = object` (`scenario_parts.py:20`), `(STEP_LINE, owner)` tuples, the `HEADING_LINE` string marker, `markdown_heading` tuples of two different shapes on `MarkdownScenario` and `MarkdownStory`, `MarkdownStep.markdown_line`, `tree_heading`, all unpacked by position and told apart by `isinstance` in `_SectionLines.write`, `MarkdownStory._document_part`, `_ScenarioDocument._written_part`, and `MarkdownScenario.document_text`. `ScenarioFileReading` exposes eighteen working fields for its caller to collect the result from.

**Before**

```
ScenarioFileReading(text, rel, scenario_type)   read() -> sections ; public: document_parts, tree_heading(tuple), tree_heading_line, document_examples, …
StorySection(name, heading, line, file)         parts: list[object], scenarios, background, story_backgrounds
MarkdownScenario  markdown_heading: (name, is_outline, line) ; markdown_parts: list ; document_text()
MarkdownStory     markdown_heading: (name, line) ; markdown_parts: list ; document_text() ; _document_part(part, steps)
MarkdownStep      markdown_line: (keyword, text, line)
_ScenarioDocument(parts, holder, tree_heading)  text(), _written_part()
_SectionLines(parts)                            write(part) keyed by id(owner)
```

**After**

```
+ ReadLine (abstract)                     written() -> str                       # one line of a read scenarios file
  + KeptLine(text)                        written: the text as read
  + HeadingLine(node, said, text)         written: as read while node says `said`, else node's heading now     ← markdown_heading ×2, tree_heading, HEADING_LINE
  + StepLines(owner)                      written: owner's steps, each as read while unchanged                  ← (STEP_LINE, owner), _SectionLines
  + ExampleLine(example)                  written: example.line()                                               ← MarkdownExample in parts
+ ReadScenarioDocument                    lines: list[ReadLine | story], holder, tree: HeadingLine | None, examples ; text()
                                                                                                                ← _ScenarioDocument + the five fields read off ScenarioFileReading
ScenarioFileReading   ~ read() -> ReadScenarioDocument ; working fields private
MarkdownScenario  - markdown_heading  - markdown_parts  + read_lines: list[ReadLine] | None
MarkdownStory     - markdown_heading  - markdown_parts  + read_lines ; - _document_part
MarkdownStep      ~ markdown_line → read: StepLineRead(keyword, text, line)   (as ExampleRowLine already is)
- _SectionLines   - DocumentPart   - HEADING_LINE   - STEP_LINE
```

**Callers affected.** Only `stories/model/markdown/` (`nodes.py`, `scenario_file.py`, `scenario_parts.py`, `markup.py`) and their specs (`markdown_scenario_round_trip_spec.py`, `markdown_story_model_spec.py`). No other module reads these fields (grep `markdown_parts|markdown_heading|document_parts`).

**Size.** 4 files, about 200 lines rewritten, net roughly even.

**What could go wrong.** This is the code that guarantees a hand-written scenarios file survives an edit byte for byte; the round-trip specs are the safety net and must pass unchanged. `_SectionLines` has a subtle rule (the last step line of an owner writes every step still pending, so steps added on the model follow the owner's last line); `StepLines` must keep it, and it is easy to lose. Low value to callers outside the package, so this ranks below A1–A4.

### U1. One named failure for "this file is not a UX map", so the reading imports no format package

**Problem.** `model/graph_reading.py:24-25` imports `drawio.nodes` and `html.nodes` for one exception class each. Those two imports are the only ones that run from the model package into a format package, and they close the four-package cycle the graph reports (model → drawio → model, model → html → model, html → json → model). The tuple at :39 also lists `json.JSONDecodeError` and `ScreenNotOnMap`, so the reading knows how each format fails.

**Before**
```
model/ux_map.py
  ScreenNotOnMap(KeyError)
model/drawio/nodes.py
  UnreadableDrawio(ValueError)
model/html/nodes.py
  UxMapNotEmbedded(ValueError)
model/json/nodes.py
  JsonUxMap._document_of(content)        raises json.JSONDecodeError
model/graph_reading.py
  imports UnreadableDrawio, UxMapNotEmbedded          (model → drawio, model → html)
  _NOT_A_MAP = (JSONDecodeError, UnreadableDrawio, UxMapNotEmbedded, ScreenNotOnMap)
  UxReading.read_working_copy()   catches _NOT_A_MAP
```

**After**
```
model/ux_map.py
+ UxMapUnreadable(ValueError)            file text is not a UX map in its format
  ScreenNotOnMap(KeyError)
model/drawio/nodes.py
~ UnreadableDrawio(UxMapUnreadable)
model/html/nodes.py
~ UxMapNotEmbedded(UxMapUnreadable)
model/json/nodes.py
~ JsonUxMap._document_of(content)        raises + UnreadableJson(UxMapUnreadable) from JSONDecodeError
model/graph_reading.py
- import of drawio.nodes, html.nodes
~ _NOT_A_MAP = (UxMapUnreadable, ScreenNotOnMap)
```

**Callers affected.** `graph_reading.py` only. Specs that expect `json.JSONDecodeError` from `JsonUxMap.parse` (check `json_ux_map_spec.py`, `html_ux_map_spec.py`) change to the named failure; `UnreadableJson` can also subclass `json.JSONDecodeError`'s parent `ValueError`, which `UxMapUnreadable` already is, so `except ValueError` callers keep working.

**Size.** 4 files, about 15 lines.

**What could go wrong.** A caller outside UX that catches `json.JSONDecodeError` from a UX render (grep found none in `actions/render`; confirm before merging). The graph's cycle check should be run again after the change; no other import closes the cycle.

### U2. Stories answers how its nodes are keyed and found; UX's `StoryLink` asks it

**Problem.** UX holds its own copy of Stories' rules for its nodes: which node types are a scenario or a step (`story_link.py:21-25`, `graph_reading.py:46`), how a scenario or step is keyed (`key_of`, `story_link.py:184-196`), how to walk from a step to its story (`_ancestor`, `_parent`, :204-215; again at `graph_reading.py:357-362`), which file each Stories node was read from and which node a heading names (`StoryTargets`, :93-181), and the names of Stories' saved facts (`text`, `phase`: `story_link.py:135, 191`; `explorer_tree.py:67-68`; `graph_reading.py:352`). It reaches them through `graph.practices.loaded(Stories).reading.in_graph` from inside functions (`story_link.py:84-90, 159-162`; `graph_reading.py:346-351`). Stories already has the object made for this: `StoryTree` (`stories/model/graph_reading.py:260`), whose docstring says "every reader of Stories' nodes, in this practice or another, asks it". It answers `epic_of`, `sub_epics`, `stories_under`, `scenarios`, `steps` — but not the key, the story of a step, or the node at a file and heading, so UX wrote those itself.

**Before**
```
stories/model/graph_reading.py
  StoryTree(stories: PracticeReading)
    epic_of(node) / sub_epics(epic) / stories_under(epic) / scenarios(story) / steps(scenario)

ux/model/story_link.py
  _NODE_TYPES {Story, Scenario, Step → Stories node types}
  StoryLink(kind: str, key, node)
    key / written / target
    resolved_on(graph, written_in)        makes StoryTargets(graph) per call
    names(node)
    _candidates(graph)                    imports Stories, walks reading.in_graph
  StoryTargets(graph)
    node_at(link, written_in)
    _nodes_by_file / _read_folders / _document(file) / _under_heading / _stories_written_in / _is_under
    _stories_read                         imports Stories
  key_of(node)  _story_name(node)  _ancestor(node, kinds)  _parent(node)      module functions

ux/model/graph_reading.py
  _STEP_TYPES
  ServedStoryLinks._targets → StoryTargets(graph)
  StoryDemoControlLinks._steps_reading(label, control)   imports Stories, reads fact "text"
  StoryDemoControlLinks._screen_of(control)              parent walk again

ux/model/explorer_tree.py
  ExplorerTree.story_tree = node.practice.reading.story_tree
  ExplorerScreen._step_entry        reads facts "phase", "text"

ux/model/claude_design/story_canvas.py
  imports key_of
```

**After**
```
stories/model/graph_reading.py
  StoryTree(stories: PracticeReading)
    epic_of(node) / sub_epics(epic) / stories_under(epic) / scenarios(story) / steps(scenario)
+   key_of(node) -> str                   → moved from ux story_link.key_of
+   story_of(node) -> Node | None         → moved from ux _story_name / _ancestor
+   stories() / scenarios_and_backgrounds() / steps_of_every_phase()      the nodes of each kind
+   steps_saying(text) -> list[Node]      → moved from ux StoryDemoControlLinks._steps_reading
+   step_text(step) / step_phase(step)    the two facts UX reads today
+   node_written_at(kind, file, heading, key) -> Node | None
                                          → moved from ux StoryTargets (_nodes_by_file, _under_heading,
                                            _stories_written_in, _document)
+ KEY_SEPARATOR                           → moved from ux story_link

ux/model/story_link.py
- _NODE_TYPES
~ StoryLink(kind, key, node, target)      target given to the constructor
    key / written
~   resolved_in(story_tree, written_in)   asks story_tree.node_written_at or the node with its key
~   names(node)
-   _candidates
- StoryTargets                            (the file-and-heading part → Stories; the folder order
                                           "written_in, then the graph's folder" stays as a small
                                           private method of StoryLink)
- key_of, _story_name, _ancestor, _parent

ux/model/graph_reading.py
- _STEP_TYPES
~ LinksAcrossPractices holds + story_tree (None while the graph reads no Stories), found once
~ ServedStoryLinks._link_served           link.resolved_in(self._story_tree, folders)
~ StoryDemoControlLinks._steps_reading    self._story_tree.steps_saying(label), filtered by story_of
- StoryDemoControlLinks._screen_of        uses the graph's own parent walk once (one helper on the base)

ux/model/explorer_tree.py
~ ExplorerTree(screens, story_tree)       given the tree; no reach through node.practice.reading
~ ExplorerScreen._step_entry              story_tree.step_phase(step), story_tree.step_text(step)

ux/model/claude_design/story_canvas.py
~ key for a scenario from the story model object it already holds (or story_tree.key_of)
```

How UX gets the `StoryTree` without importing Stories inside functions: the one place that needs it, `UxReading`, already declares `reads_after = ("stories", …)`. It asks its graph for the loaded Stories practice once (the single function-level import that remains, or better a framework lookup by the catalogue key `"stories"` that `reads_after` already uses) and hands the tree to the three link builders and to nodes that resolve links.

**Callers affected.** UX only on the calling side: `nodes.py:119-152` (`ServesStories.lists`, `show_what`, `_links`), `graph_reading.py:256-362`, `explorer_tree.py:24-88`, `html/nodes.py:207`, `claude_design/story_canvas.py:23, 329`, `drawio/nodes.py:27` (imports `KEY_SEPARATOR`; see U4 for its other use). Stories gains about six methods on `StoryTree`. Specs: `story_link_spec.py` (uses `key_of`), `graph_reading_spec.py`, `html_ux_map_spec.py`; new specs for the moved methods belong beside Stories' reading specs. Cards: the Stories card should list `StoryTree` under terms other packages use.

**Size.** About 6 files in UX and 1 in Stories; roughly 130 lines move from UX to Stories and about 60 lines of UX shrink or go. `StoryTree` grows from 5 to about 11 public methods, so check Stories' deep-module share after the move.

**What could go wrong.** `StoryLink.resolved_on` is called for detached maps and for nodes read back from a saved graph in a worker process; the present code is careful that both paths give the same answer (`graph_reading.py:256-263` docstring). The moved code must keep reading facts and edges, not parsed objects. `StoryTargets` caches its by-file index per instance; on `StoryTree` the cache must be dropped when Stories reads again. This crosses two practices, so it needs the heavy specs for both.

### U3. A front-end view hands out its components; the scanner owns reading code

**Problem.** `FrontEndView` (`front_end_view.py:636`) exposes text positions (`declared_components()` returns `(name, index of "(")`, `taken_apart(opening)`, `scanned`), while the object that models a component — its props, hooks, handlers, where it starts and ends — is `Component` in `reshaped_view.py:56`, the file about merging. `Component` builds a `TypeAnnotations` only to ask where a function body opens (`reshaped_view.py:63, 69, 149, 180-183`), and statement-end and bracket-depth scanning is written in both files (`front_end_view.py:349, 472, 717`; `reshaped_view.py:134, 186`). `ReshapedView` is then a doer over `Component` and `ComponentMember` records.

**Before**
```
front_end_view.py
  ViewText(text)            code / names / closing / past_space / line_start / line_end / edited(edits)
  Edit(start, end, replacement)
  TypeAnnotations(view)     dropped()   arrow_after(closing)   body_after(closing)   _statement_end   _type_end …
  FrontEndView(text, typed)
    scanned                                 exposes ViewText
    components -> list[str]
    props -> dict[str, list[str]]
    handlers -> list[str]
    declared_components() -> list[(name, opening)]
    taken_apart(opening) -> list[str]
    without_types

reshaped_view.py
  ComponentMember(name, lead, start, end, is_hook, written_new)        frozen record
  Component(view, name, opening)
    props / members / start / end / lead / text / marks / opening_line / props_braces
    new_handlers_at / new_hooks_at / marked(member) / indent_of(position)
    _statement_end / _own_line_starts / _function_at / _declared_at / _empty_function_from
  ReshapedView(rendered, existing)
    kept / added (public lists filled as it runs)
    reshaped() -> Reshaped
    _reshape / _keep / _add / _reshape_props / _take_props
```

**After**
```
front_end_view.py
  ViewText(text)
+   statement_end(position)               → merged from TypeAnnotations._statement_end and Component._statement_end
+   top_level_line_starts(opening, closing)   → moved from Component._own_line_starts; also used by
                                               TypeAnnotations._member_annotations and FrontEndView._top_level_parts
+   function_body_after(closing) / arrow_after(closing)    → moved from TypeAnnotations
  TypeAnnotations(view)     dropped()      (only dropping annotations; - arrow_after, - body_after)
+ Component(view_text, name, opening)      → moved from reshaped_view.py, with ComponentMember
+   props / members / text                 the reading half
  FrontEndView(text, typed)
~   components -> list[Component]
~   props      (derived from components)
    handlers
    without_types
-   scanned
-   declared_components()
-   taken_apart(opening)

reshaped_view.py
  ReshapedView(rendered, existing)
~   reshaped() -> Reshaped                 builds kept and added locally; - public kept / added lists
    (the writing half stays here: where a new hook or handler goes, the marking line, taking new props)
```

**Callers affected.** `view_formats.py:19`; `reshaped_view.py` throughout; specs `front_end_view_spec.py:95-143` (`view.components` is compared with a list of names: becomes `[component.name for …]`) and `view_reshape_spec.py`. Nothing outside `ux/model/view` imports these classes (grep: no hits in actions, patterns, harness, space).

**Size.** 3 files, about 120 lines moved, about 35 duplicate lines removed.

**What could go wrong.** The two `_statement_end` versions differ on purpose in one detail (one counts only braces for depth, the other all brackets, and one returns the line end rather than the semicolon). Merging them needs the existing reshape specs to pin both behaviours first. This is text scanning with many edge cases; do it test-first (Flow B: `view_reshape_spec.py` and `front_end_view_spec.py` already cover the area).

### U4. One notation for "what this serves", and navigation kinds as a value of the model

**Problem.** The drawing's callout and the board's card write the same lines — `Stories: A · B`, `Scenarios: …`, `Steps: …`, `Domain terms: …` — and each format package has its own separator constant, headings table, writer, and reader (`drawio/nodes.py:36, 49, 120-136, 322-335`; `whiteboard/nodes.py:33-36, 82-94, 193-198, 330-334`). JSON has a third mixin for the same three lists (`json/nodes.py:33-46`). Each is a mixin over `ServesStories` that reaches its private `_show` and `_keys` (`drawio/nodes.py:132`; `whiteboard/nodes.py:87, 94`). Separately, a transition's kind of navigation is a free string with the meaning spread over the formats: `"action"` as the default in `nodes.py:305` and `json/nodes.py:177`, `_ACTION`/`"tab"` in `drawio/nodes.py:44, 418, 450`, `_ACTION`, `_TAB` in `whiteboard/nodes.py:48, 208, 219`, both deciding "a dashed line is a tab" on their own.

**Before**
```
model/nodes.py
  ServesStories   show_story/scenario/step · shows/shows_scenarios/shows_steps · story_keys/scenario_keys/step_keys
                  story_links · links_of(kind) · lists(node) · show_what(other) · _show(kind, shown) · _keys(kind)
  Transition      nav_type: str = "action"
model/drawio/nodes.py
  _BESIDE, _SERVED_HEADINGS, _TERMS, _ACTION
  DrawnServed(ServesStories)      drawn(kind) · serve_listed(kind, items) · _markup(link)
  Callout                         annotate(screen) · _listed(heading)
  DrawioUxMap._nav_type_of(edge)
model/whiteboard/nodes.py
  _BESIDE, _SERVED_HEADINGS, _TERMS_HEADING, _ACTION, _TAB
  ServedOnCard(ServesStories)     served_lines() · read_served_lines(lines)
  _listed(lines, heading)
  WhiteboardTransition.read_arrow(arrow)
model/json/nodes.py
  JsonServesStories(ServesStories)   read_served(record) · served_record()
```

**After**
```
model/nodes.py
+ Served                          the stories, scenarios, and steps one screen or control serves,
+                                 held by ServesStories as `served`
+   stories / scenarios / steps -> list[StoryLink]
+   serve(kind, shown) / serve_all(other) / serves(node)
+   as_lines(link_text) -> list[str]        "Stories: A · B" lines; link_text says how one link is shown
+   read_lines(lines)                       the reverse
~ ServesStories                   keeps show_story/scenario/step and the *_keys graph facts, delegating to `served`
-                                 _show, _keys reached from format mixins
+ NavType                         ACTION, TAB, and a named kind such as "top nav";  is_tab;  from_drawn(kept, dashed)
~ Transition.nav_type: NavType
model/drawio/nodes.py
- _BESIDE, _SERVED_HEADINGS (for screens), _ACTION, DrawnServed.serve_listed, Callout._listed, _nav_type_of
~ DrawnServed.drawn(kind)         served.as_lines(self._markup)
model/whiteboard/nodes.py
- _BESIDE, _SERVED_HEADINGS, _ACTION, _TAB, ServedOnCard, _listed
~ WhiteboardTransition.read_arrow    NavType.from_drawn(named kind, arrow.dash)
model/json/nodes.py
~ JsonServesStories               reads and writes through `served`
```

**Callers affected.** `ux_map.py:124, 147, 179, 185` (`show_what`), `drawio/nodes.py:120-136, 265-280, 319-335, 414-418, 450-451`, `whiteboard/nodes.py:82-123, 160-219`, `json/nodes.py:33-46, 177`, `claude_design/story_canvas.py:73, 400` (`lists`), `explorer_tree.py:30`, `html/nodes.py:242`. Specs: the round-trip specs of all four formats and `render_onto_existing_spec.py`.

**Size.** 6 files; about 80 lines removed across the formats, about 60 added in the model.

**What could go wrong.** The drawing escapes links as HTML anchors and the board writes markdown links; `as_lines` must take the link's rendering from the format, or the two files read each other's output wrongly. The drawing's control lines (`Region › Control serves steps: …`, `drawio/nodes.py:51, 272-288`) are a drawio-only addition and stay there. `nav_type` is saved as a graph fact (`nodes.py:296`) and in JSON; `NavType` must write the same strings it reads so saved graphs and existing files still load.

### U5. The Story Demo runner knows no product, and one page object owns what it paints

**Problem.** The shared runner contains one product's nouns: `paintCharacterTree`, `paintAbilities` (`mount-generated-mockup.js:272-295`), the `"create character"` trigger (`control.js:71`), and `SESSION_KEYS = ["cart", "product", "catalog", "paymentMethod"]` (`mount-generated-mockup.js:23`), which decides what Interactive carries from one story to the next. Around them, `mount-generated-mockup.js` is 750 lines: sixteen module functions taking `root` or `snapshot`, and `GeneratedMockup` with 24 methods whose two panels each hold the whole mockup and read through it. `PaintReflect` forwards one call, so the frame is given every snapshot twice.

**Before**
```
mount-generated-mockup.js
  SESSION_KEYS (fixed shop nouns)
  readBound / isBoundListHost / controlsOn / explorerChromeOn / itemStoryStepsFor / pickNameOf / formatItemLabel
  paintCharacterTree / paintAbilities / boundFieldText / paintBoundFields
  showScreensForStory / showScreen / selectWithinRegion                      (functions of root)
  BoundListHost(element)   BoundListLine(host, lineItem)   StoryCatalog(entries)
  ExplorerPanel(mockup, chrome, expansion)      reads mockup.page, mockup.catalog
  ProductPanel(mockup)                          reads mockup.page.runner.scenario, mockup.frame, mockup.root
  GeneratedMockup(root, catalog, {frame, chrome, expansion})    24 methods: stories, carry-over, play, wiring, repaint
paint-reflect.js      PaintReflect(frame).apply(snapshot) → frame.bind(snapshot)
play-dual-runner.js   PlayDualRunner._reflect: paintReflect.apply(snapshot); storyDemoFrame.bind(snapshot)
story-demo-page.js    onControlTrigger: paintReflect.apply(snapshot); storyDemoFrame.bind(snapshot)
```

**After**
```
mount-generated-mockup.js
- SESSION_KEYS            → the carried keys come from the page: a `data-session-keys` attribute the
                            mockup shell writes, else every key the scenario exposes
- paintCharacterTree, paintAbilities
+ ProductScreens(root)    → owns showScreensForStory / showScreen / selectWithinRegion as methods
~ ProductPanel(root, frame, screens)     given what it paints with; paint(scenario)
+   paintBoundFields / paintBoundLists as methods (boundFieldText, readBound → a small Snapshot value
+   Snapshot(exposed).at(path)                         that reads a dotted path)
~ ExplorerPanel(chrome, expansion)       paint(page, catalog, currentScreen)
~ GeneratedMockup         keeps story activation and play; wiring moves to
+ ControlWiring(mockup)   wireInteractive / wireLineSelect / product navigation / screen clicks / goto links
- paint-reflect.js (PaintReflect)
~ PlayDualRunner._reflect, StoryDemoPage.onControlTrigger       one frame.bind(snapshot)
```

**Callers affected.** `story-demo.spec.js`, `play-dual-runner.spec.js`; the shell template `templates/html/mockup_shell.html` (to write `data-session-keys`, from a new optional field on the UX map or left to "every exposed key"); `HtmlUxMap._shell_values` (`html/nodes.py:202`) if the attribute comes from the map. The UX card's `ux/story-demo` section names none of the removed parts.

**Size.** 5 JavaScript files; about 60 lines deleted outright, about 250 lines moved inside `mount-generated-mockup.js`. The deletions (character, abilities, `PaintReflect`, the trigger special case) are UX fixes 16-17 and can go first without the rest.

**What could go wrong.** Any mockup outside this repository that relies on `[data-character-tree]` or `[data-ability-list]` stops painting them. Carrying "every exposed key" between stories may carry more than the four names did; the conservative option is the attribute with the present four names as what the bookshop example writes. The file has browser-only behaviour with thin automated coverage (the specs stub the DOM), so this is Flow A for the page: run a generated mockup in the browser and have a person walk it before the unit specs are trusted.

### U6. A format adapter is not also an empty map (recorded for a later decision)

**Problem.** In UX the format adapter and the domain root are one class: `Ux.format_adapters` names `DrawioUxMap`, `JsonUxMap`, and the rest (`ux.py:80-89`), the framework makes an instance of each, and that instance is an empty `UxMap` whose `parse` makes another map of its own class and whose `render` copies the given map into a third (`drawio/nodes.py:359-363, 434`; `json/nodes.py:233-239, 268-270`; `whiteboard/nodes.py:244, 271-275`; `markdown/nodes.py:34-38, 70`). The cost shows in several findings above: file-description attributes on the domain root (`ux_map.py:46-61`), settings copied from the adapter onto the copy (`drawio/nodes.py:437`), `ClaudeDesignStoryModel.render` making a second model from a `StoryCanvasSetup` (`story_canvas.py:153-158`), and `UxMapFile.format` holding "a map" that is never used as one (`graph_reading.py:105`). Stories has the same shape (`StoryModel` subclasses as adapters), so the two practices should be decided together; the fork judging Stories has the other half.

**Before**
```
UxMap(UxNode)                              domain root + format adapter + file description
  screens / transitions / content_types / nav_components / context / scope
  copy_of(source) / keep_served_by(held) / keep_what_only(held)
  screen_type … nav_component_type         node types of this format
  map_file_suffixes / holds_screens / reads_file(file, text)
DrawioUxMap(UxMap)     parse(content) · render(canonical, previous) · save() · cli_timeout_seconds
JsonUxMap(UxMap)       parse · render · save
…
```

**After (sketch)**
```
UxMap(UxNode)                              domain root only
  screens / transitions / content_types / nav_components / context / scope
  copy_of(source) / merge_served_from(held) / merge_missing_from(held)        ~ renamed from keep_*
+ UxMapFormat                              one per format; what PracticeFormats makes
+   map_type: type[UxMap]                  DrawioUxMap, JsonUxMap, … (the node types stay on the map class)
+   file_suffixes / holds_screens / reads_file(file, text)       → moved from UxMap
+   parse(content) -> UxMap                → moved from each *UxMap.parse
+   render(canonical, previous) -> str     → moved from each *UxMap.render; settings such as the timeout live here
DrawioUxMap(UxMap)     save() and the reading of its own pages; no parse/render/reads_file
```

**Callers affected.** `ux.py:80-89`, every `model/*/nodes.py`, `graph_reading.py:102-186`, every format spec (`DrawioUxMap.create().render(...)` becomes the format's `render`). The framework's `PracticeFormats` needs no change: it calls `parse` and `render` on whatever `format_adapters` names.

**Size.** About 9 production files and 8 specs in UX; 200 to 300 lines moved, few written. Larger if Stories follows.

**What could go wrong.** It is a wide mechanical change for a gain that is mostly clarity; the present shape works and an earlier review accepted "every UX format adapter subclasses the domain class it represents" (`.context/model/repo-review/practices.md:73`). The proposal does not contradict that (the map subclasses stay); it separates the adapter from them. Do it only if Stories is changed the same way, or the two practices diverge.

### U7. A node's id on a board is made once, in the whiteboard framework (cross-practice, see also A2)

**Problem.** Stories, UX, and Clean Engineering each compute a board element's id as a SHA-1 of the node's path cut to a fixed length: `ux/model/whiteboard/nodes.py:30, 70-76` (and again inline at :209), `stories/model/whiteboard/nodes.py:30, 38-44, 75, 210`, `clean_engineering/model/whiteboard/whiteboard_class_model.py:47, 80`. All three extend `harness/whiteboard/whiteboard.py:283 WhiteboardNode`, which has `board_box`, `board_elements`, and `board_shape` but no key.

**Before**
```
harness/whiteboard  WhiteboardNode      board_box() · board_elements() · board_shape(id, …)
ux         DrawnNode.board_key          sha1(path)[:10]        + KEY_LENGTH = 10
stories    (its node base).board_key    sha1(path)[:10]        + KEY_LENGTH = 10
clean eng. module function             sha1(names)[:12]       + KEY_LENGTH = 12
```

**After**
```
harness/whiteboard  WhiteboardNode
+   board_path() -> list[str]            each practice says the names that make its path (overridden)
+   board_key -> str                     the one hash of board_path(), one length
+   key_of_words(*words) -> str          for ids not made from a node's path (a transition, a lane)
ux / stories / clean eng.               - board_key, - KEY_LENGTH, - inline hashlib calls
```

**Callers affected.** The three whiteboard packages and their specs.

**Size.** 4 files, about 30 lines removed, 12 added.

**What could go wrong.** Clean Engineering uses 12 hex digits and the others 10. A board keeps "where people put each element" by id (`WhiteboardUxMap.render`, `whiteboard/nodes.py:250`), so changing a practice's key length makes every existing board of that practice lose its kept places on the next render. Either keep the length as a class attribute each practice sets, or accept one re-layout for Clean Engineering boards and say so in the release notes.

### R1. One way to write a render onto a file that is already there

**Problem.** Five classes do the same job with five outlines and five copies of the marker: `ReshapedCode` + `CodeOutline` + `_FileEdit` (`actions/render/reshaped_code.py`, 363 lines), `KeptDocument` (`actions/render/kept_document.py`, 126), `ReshapedStoryFile` (`stories/model/reshaped_story_file.py`, 168), `ReshapedView` + `Component` (`ux/model/view/reshaped_view.py`, 283), `SpecReshape` + `SpecOutline` (`bdd/model/spec_reshape.py`, 176). Shared in all of them: a member with name, lead line, start, end and indent; "comments and decorators above it" (`_lead_of` ×3); "is it already marked" (×4); the marking line (×4); "set apart what could not be placed" (×2); "does the new text hold every old line" (×3 call sites). I estimate 150 to 200 duplicated lines out of about 1,100. The seam between Render and a practice's own writer is `getattr(adapter, "reshape", None)` (`render.py:120`), and for documents and drawings the adapter keeps layout through `previous` and `KeptDocument` then keeps it again.

**Before**

```
harness/guidance/practice_formats.py
  FormatAdapter (Protocol)        parse(content), render(model, **options)
  Reshaped                        text, kept[str], added[str], changed{str:str}

actions/render
  Render._saved_code              getattr(adapter, "reshape", None)  -> RenderedCode(..., reshape)
  RenderedCode._written_onto      ReshapedCode(format, reshape).onto(existing, rendered)
  ReshapedCode                    onto(), _edited(), _set_apart()          NO_LONGER_IN_MODEL
    CodeOutline / Member          Python by indent, braces by regex        _lead_of
    _FileEdit                     _is_marked, _set_apart, kept/added/changed
  RenderedFile.save               KeptDocument(format).onto(before, rendered)
  KeptDocument                    _markdown, _drawio, _whiteboard          NO_LONGER_IN_MODEL

practices
  stories ReshapedStoryFile       reshaped()   CodeBlock                    NO_LONGER_IN_MODEL
  ux      ReshapedView/Component  reshaped()   ComponentMember, _lead_of    NO_LONGER_IN_MODEL
  bdd     SpecReshape/SpecOutline onto()       SpecBlock, _lead_of          NO_LONGER_IN_MODEL
```

**After**

```
harness/guidance/practice_formats.py
  FormatAdapter (Protocol)        parse, render
                                  + reshape(rendered, existing) -> Reshaped | None   (optional, declared)
  Reshaped                        text, kept, added, changed
                                  + set_apart: int          (lines kept below the text; no longer a sentence in kept)
  + ExistingText                  the file as it was: lines
                                  + holds_every_line_of(other) -> list[str] missing   (one copy of the check)
                                  + set_apart_below(rendered, comment) -> Reshaped    (one copy of the fall-back)
  + KeptMark                      NO_LONGER_IN_MODEL
                                  + marks(lines above a member) -> bool
                                  + line_for(member, where, comment) -> str
  + OutlinedMember                name, lead, start, end, indent     (the shared record)
                                  + lead_of(lines, start, indent)    → moved from CodeOutline/SpecOutline/Component

actions/render
  Render._saved_code              ~ asks formats.adapter(format).reshape  (no getattr)
  ReshapedCode                    ~ uses ExistingText, KeptMark, OutlinedMember
    CodeOutline                   ~ Member → OutlinedMember; comment sign from the language, not "#"/"//" by name
  - KeptDocument._drawio          → the practice's draw.io adapter keeps layout and unknown cells (it already takes previous)
  - KeptDocument._whiteboard      → harness/whiteboard: Whiteboard.keeping(previous)
  KeptDocument                    ~ markdown only, through ExistingText.set_apart_below

practices
  stories ReshapedStoryFile       ~ uses KeptMark, ExistingText
  ux      ReshapedView            ~ ComponentMember extends OutlinedMember; uses KeptMark
  bdd     SpecReshape             ~ SpecBlock extends OutlinedMember; uses KeptMark
```

**Callers affected.** `render.py:109-121`, `rendered_code.py:134-145`, `rendered_file.py:135-146`, the three practice reshapers and their adapters' `reshape` (`bdd/model/code_spec_model.py:293,376`, `stories/model/code_story_model.py:465`, `ux/model/view/view_formats.py:15`), every draw.io and whiteboard adapter that takes `previous` (to confirm each keeps cells it does not draw, which today only `KeptDocument` guarantees), and the specs `reshaped_code_spec.py`, `kept_document_spec.py`, `rendered_code_spec.py`, the three practice reshape specs.

**Size.** About 12 production files, 300 to 400 lines changed, net removal of roughly 150. It can be done in two passes: the shared record, marker and line check first (no behaviour change), the draw.io and whiteboard move second.

**What could go wrong.** The second pass moves a safety net: `KeptDocument` today keeps a person's cell whatever the adapter does, including for an adapter someone writes later. If a practice adapter forgets, a person's note on a drawing is lost, which is a defect this branch already fixed once (commit 134df3e88). Keep the heavy spec for that case running against every practice's draw.io and whiteboard adapter before removing `_drawio` and `_whiteboard`; if that cannot be guaranteed, do only the first pass. The practice reshapers differ in real ways (nested `with` blocks, React components), so the shared part must stay the record and the marker, not a shared algorithm.

### R2. The fidelity says where a render is saved; a render answers a typed result

**Problem.** "Where does this render go" is decided in `Render._render_files` and `_saved_by_declared_paths` (`render.py:69-103`), `RenderedFile.from_sources`, `beside_itself`, `from_graph`, `_scope_of` (`rendered_file.py:65-133`), and `RenderedCode._placed` with four helpers (`rendered_code.py:147-233`), about 230 lines, all reading `fidelity.declared.outputs` and redoing parts of `DeclaredOutputs` / `DeclaredFile` (`harness/guidance/declared_outputs.py`: `includes`, `file_name_beside`, `file_beside`, `saved_beside`, `parts_of`, `named_with`, `names_one_path`). `RenderedCode` takes seven constructor values read off one fidelity. Results are dictionaries whose keys the caller sniffs. `Validate` and `Generate` also redo declared-path tests (`checked_graph.py:229,239,255`, `generate.py:20`).

**Before**

```
harness/guidance
  DeclaredOutputs   outputs{label: str|[str]}; includes, file_name_beside, file_beside, saved_beside, output_paths
  DeclaredFile      pattern, parts_of, named_with, names_one_path, start_of
  FidelityGuidance  render, render_files, files_to_render, render_request      -> dict
  RenderRequest     format, content, source, previous, folder, fidelity

actions/render
  Render            _render_files(worked, format, paths, source)
                    _saved_by_declared_paths(worked, format, sources, paths, source)
                    _saved_code(worked, format, sources, written_in) -> RenderedCode(7 values)
                    _saved_by(result: dict), _format_named_by(sources)
  RenderedFile      from_sources(sources, source, format, declared), beside_itself(...), from_graph(...), _scope_of(...)
                    previous, save(rendered: dict) -> dict
  RenderedCode      (root, declared, format, source, source_declared, source_name, reshape)
                    save(rendered: dict) -> dict; _placed, _section_file, _named_for_source, _counterpart_of, _beside_source
  own_name(), _says_where_name_ends()      module functions
```

**After**

```
harness/guidance
  DeclaredOutputs   + paths_in(format) -> [str]                    (the one normalisation)
                    + place_of(sources, source_format, format) -> RenderPlace | None
                         → moved from RenderedFile.from_sources / beside_itself and RenderedCode._counterpart_of,
                           _named_for_source, _beside_source
                    + place_for_scope(scope, format) -> Path        → moved from RenderedFile.from_graph
  DeclaredFile      + own_name_of(source) -> str | None             → moved from rendered_code.own_name,
                                                                       _says_where_name_ends
                    + filled_with(names) -> str                     → moved from RenderedCode._section_file
  + RenderPlace     path(s) a render is saved at, and whether each is the fidelity's own file
  + RenderResult    format; saved: [Path]; migrate: [Migration]; content (data formats only); board, batches
  + Migration       file, kept | signature_differs, may_have_replaced_it | model_has
  FidelityGuidance  ~ render_request(request) -> RenderResult

harness/graph
  SavedGraph        + scope_name(practice_key) -> str               → moved from RenderedFile._scope_of

actions/render
  Render            ~ render(...) -> list[RenderResult]
                    ~ _render_files(worked, request)                (RenderRequest carries format, source, paths)
                    - _saved_by_declared_paths  - _saved_code  - _saved_by
  RenderedFile      ~ (place, request)   save(rendered) -> RenderResult
                    - from_sources  - beside_itself  - from_graph  - _scope_of
  RenderedCode      ~ (fidelity, format, source)   save(rendered) -> RenderResult
                    - _named_for_source  - _counterpart_of  - _beside_source  - _section_file
                    _placed  ~ cuts sections at banners, asks fidelity.declared for each place
  - own_name()  - _says_where_name_ends()
```

**Callers affected.** `render.py` (whole), `rendered_file.py`, `rendered_code.py`, `generate.py:16,130-133`, `checked_graph.py:221-264`, `space/session/format_alignment.py:36,358,457` (imports `SAVED_GROUPS`; give `Format` an `is_saved_by_render` property and import nothing from the action), anything that reads a render's dictionary result: the Files app's format alignment (`space/session/format_alignment.py`), `harness/files_app` (reads `migrate`, `path`, `board`), the `place_rendered` and `publish_board` instruction texts, and `render_spec.py` (825 lines), `rendered_code_spec.py`, `render_saves_beside_source_heavy_spec.py`, `declared_outputs_spec.py`.

**Size.** 8 to 10 production files, about 500 lines moved or changed; the specs are the larger part, since most of `render_spec.py` asserts dictionary keys. The MCP answer stays JSON with the same keys if `RenderResult` writes itself as today's dictionary, which I recommend so that no installed skill text changes.

**What could go wrong.** This moves about 150 lines into `harness/guidance`, and the guardrails warn that an owner that receives behaviour must be split into parts, not left to grow: `DeclaredOutputs` is 115 lines today, so put placement in a part it holds (`RenderPlace` made by a small `RenderPlacement` object), and run the metrics gate. The five placement cases in `rendered_code.py`'s docstring were each added for a reported defect; every one needs its spec case kept green through the move. The framework must not learn about banners (`# === … ===`), which are Clean Engineering's; cutting text into sections stays in the action or, better, the code adapter answers a file for each name so the banner parse can go.

### R3. Validate asks the session and the practice for the story scope, and holds one checked-fidelity object

**Problem.** `CheckedGraph` names Stories and copies its node types (`checked_graph.py:16-18`), reads the session's stories with `getattr` (112), keeps fidelities and formats as two parallel lists zipped four times, exposes six mutable fields, and is passed to `ReportFiles` while `ReportFiles` is passed to it.

**Before**

```
Validate            _check: CheckedGraph(session, fidelities, NamedToCheck(paths, graph, call))
                            ReportFiles(session, fidelities); graph.check_beside(reports)
                    _saved: reports.save(report_text, graph)
CheckedGraph        session, edited, prefixes, files, checked_files, unchecked_files   (public, mutable)
                    _fidelities[], _formats[]   (parallel)
                    _STORIES, _STORY_MAP_TYPES;  getattr(session, "stories")
                    check_beside(reports), violations(), accepted(), found(), found_by(fidelity), save_at(path)
ReportFiles         _claimed_for[(fidelity, path)], paths; graph_file(), save(report, graph), where()
NamedToCheck        paths, graph, call
ActionSession       (no stories)
```

**After**

```
harness/guidance_actions
  ActionSession     + stories: Sequence[str]            (declared; SessionBrief._story_scope reads it too)

harness/guidance (PracticeReading) or the Stories practice
  + scope_types     the node types a practice scopes by the session's work; Stories answers its ten types,
                    every other practice none          → moved from checked_graph._STORY_MAP_TYPES

actions/validate
  + CheckedFidelity fidelity, format (read once)
                    + checked_files, other_format_files, written_folders      → moved from CheckedGraph
                    + report: Path                                            → moved from ReportFiles._claimed_for
  CheckedGraph      ~ (session, checked: [CheckedFidelity], named: NamedToCheck)
                    ~ holds its ReportFiles (made in the constructor); - check_beside(reports) → built on first read
                    ~ files_built_from  (renamed from prefixes);  fields private, read through properties
                    - _STORIES  - _STORY_MAP_TYPES
                    ~ _on_session_stories: for each practice of the saved graph, outside(session.stories, practice.scope_types)
  ReportFiles       ~ save(report) — asks the CheckedGraph that holds it; no graph parameter
  ValidationReport  ~ (session, guidance, checked, only)  — no longer reads checked.session
```

**Callers affected.** `validate.py:95-105,143,148-154`, `validation_report.py:42-50`, `report_files.py`, `harness/guidance_actions/guidance_actions.py:47-68,625`, `space/session/session.py` (already has `stories`; nothing to add), Stories' graph reading (one attribute), `checked_graph_spec.py`, `validate_spec.py:554-576` (it patches `CheckedGraph.check_beside` to order two calls; that case needs another hook), `validation_report_spec.py`.

**Size.** 5 production files in the actions, 2 in harness, 1 in Stories; about 200 lines changed.

**What could go wrong.** `check_beside` is separate today for a reason the code states: the report files are claimed before the graph is built, so a path that does not exist is refused before any file is created (`checked_graph.py:53`). Building on first read must keep that order, or a refused call leaves an empty report file behind. The scope-types seam adds one member to every practice reading; if only Stories ever scopes by session, a simpler version keeps the types in Stories and has `SavedGraph` ask each practice, which is the same cost.

### R4. A `Pattern` class, and fact files that say what they are

**Problem.** A pattern is recognised by a class attribute string (`patterns/__init__.py:24`); three classes repeat the same constructor; MERN has no overlay and would fail if it gained a rule folder; `TierFile` answers five kinds of file and the overlay picks the facts with a lambda table; `AccessFile` is the same shape again; every fact name is a string written in the fact file and in the rule.

**Before**

```
PracticeGuidance
  DomainDrivenStack        default_workspace_folder, __init__(format="typescript")
    LernDomainDriven       pattern="lern_domain_driven", story_test_folder, graph_overlay, test_setup_text(root)
    MernDomainDriven       pattern="mern_domain_driven"                      (no graph_overlay)
  CddWebDomainAccess       pattern=..., default_workspace_folder, __init__, graph_overlay
  CddClaudeMod             pattern=..., default_workspace_folder, __init__, graph_overlay = GraphOverlay(self)

TierFile(text, relative)   node_root_facts(setup_text), route_facts(), behavior_facts(), story_facts(),
                           request_reads(), web_path_literals(), unreset_instances(names, setup_text),
                           error_handling_facts()      -> dict / list[list]
AggregateFolder(root, folder)  core_request_reads(), web_path_literals()
AccessFile(name, text)     tier() -> (type, dict) | None; route_facts, node_facts, is_hand_written_adapter, ...
_LernReading               _TIER_FILES, _BEHAVIOR_TIERS, _story_semantic  (which node type a file becomes)
rules                      node.get_fact("ad_hoc_throws", []) ...
```

**After**

```
PracticeGuidance
  + Pattern                + pattern (the folder's name, read once from the module's folder)
                           + graph_overlay -> GraphOverlay(self)   (default; cached)
                           + __init__(format="typescript")
    DomainDrivenStack      ~ extends Pattern;  - __init__
      LernDomainDriven     ~ graph_overlay -> LernOverlay(self);  - test_setup_text → _LernReading
      MernDomainDriven     (inherits the default overlay)
    CddWebDomainAccess     ~ extends Pattern;  - __init__
    CddClaudeMod           ~ extends Pattern;  - __init__  - graph_overlay

+ FactFile(relative, text)          holds SourceText;  + node_type -> str | None;  + facts -> dict
                                    + at(root, path)   (one factory signature)
  + NodeRootFile, RouteFile         facts = today's node_root_facts / route_facts          → split from TierFile
  + BehaviorFile                    node_type from _BEHAVIOR_TIERS; facts = behavior_facts → split from TierFile
  + StoryTestFile                   node_type from _story_semantic; facts = story_facts    → split from TierFile
  AccessFile                        ~ extends FactFile;  ~ tier() → node_type + facts
- TierFile
AggregateFolder                     ~ holds the FactFiles of its folder, each read once
_LernReading                        ~ for each scanned file: FactFile.of(file) -> add node, set facts
                                    - _TIER_FILES lookup spread, - _BEHAVIOR_TIERS, - _story_semantic (→ the file classes)
+ fact names                        one module of constants per pattern (AD_HOC_THROWS = "ad_hoc_throws"),
                                    imported by the fact file and by the rule
```

**Callers affected.** `patterns/__init__.py`, the four pattern classes, `lern_domain_driven/graph_overlay.py`, `tier_facts.py`, `access_facts.py`, `cdd_web_domain_access/graph_overlay.py`, the 14 LERN rules and 4 access rules (constant names only), `harness/graph/pattern_overlays.py:49` (`getattr(self.pattern, "pattern", None)` can read `Pattern.pattern`, but supplements also own overlays, so the `getattr` may have to stay), and `oss_portal_domain_driven`, which imports `TierFile` and `AggregateFolder` (`oss_portal_domain_driven/graph_overlay.py`, `tier_facts.py`) and would need the same rename although it is otherwise out of scope. Specs: `lern_tier_rules_spec.py` (222 lines, builds `TierFile(text)` directly), `shared_behavior_rules_spec.py`, `access_facts_spec.py`, `lern_domain_driven_spec.py`, `mern_domain_driven_spec.py`, `cdd_claude_mod_spec.py`.

**Size.** About 12 production files and 6 specs; 350 to 450 lines changed. The `Pattern` base alone (first box) is 5 files and under 60 lines and can be approved separately.

**What could go wrong.** Splitting `TierFile` adds four classes where one works; the model rule `class-not-property-instance-or-subtype` asks for a subtype only when property and instance do not fit, and here the kinds differ in behaviour (which facts), so a subtype fits, but if the product owner prefers fewer classes, a single `FactFile` with a `kind` chosen at `at(...)` gives the same seam. A shared `FactFile` base needs a home below both patterns; `domain_driven_stack` is the wrong place for web domain access, so it means a new small package under `patterns/` or putting `SourceText` and `FactFile` in `harness/graph`, which also answers the finding about importing `SourceText` from inside Clean Engineering. Whether MERN should receive LERN's graph rules is a separate product decision: MERN's files are named `-server.ts` under `packages/` and LERN's reading looks for `-node.ts` under `src/` (`graph_overlay.py:100-101`), so sharing the rules needs the tier file names made attributes of the stack. I have not costed that; it is at least the size of this proposal again.

### R5. Desktop walk reads its steps from Stories

**Problem.** `desktop_walk.py:18-21` imports four modules from inside Stories' model and then copies each scenario and step into `DesktopScenario` and `DesktopStep`, filling them in a second call. Stories' card says it already reads a desktop story test as a scenarios file.

**Before**

```
DesktopWalk._scenarios_in(file)   ScenarioFileReading(text, named, MarkdownScenario).read()
                                  DesktopScenario(story, name, file); scenario.read_steps(read.steps, lines)
DesktopScenario                   story, name, file, sub_epic, steps; read_steps(steps, lines); is_under(target)
DesktopStep                       (scenario, number, keyword, text, directions) key, keyword, text, do, see
imports                           stories.model.markdown.nodes, .markdown.scenario_file, .story_file, .story_map_files
```

**After**

```
Stories (seam)                    + desktop_story_tests(project) -> [DesktopStoryTest]
                                       each: story, file, scenarios (the story model's own Scenario and Step,
                                       each step with the lines written below it)
                                    (wraps StoryMapFiles.desktop_story_tests_below and ScenarioFileReading; named on the card)
DesktopWalk.scenarios             ~ asks Stories; no file reading of its own
DesktopScenario                   ~ (scenario from Stories, file)  - read_steps;  steps made in the constructor
DesktopStep                       ~ (scenario, number, step from Stories)  do/see read from the step's lines below
imports                           - four model modules;  + cdd_guidance.practices.stories.stories
```

**Callers affected.** `desktop_walk.py`, Stories (`stories.py` or a small file in `stories/model/`, plus its card), `desktop_walk_spec.py` (167 lines), `scripts/test.ps1 -Suite desktop` if it lists the files through `StoryMapFiles`.

**Size.** 3 production files, about 80 lines.

**What could go wrong.** `DesktopStep` and `DesktopScenario` are `@data_field` classes sent over MCP, so their published fields (`key`, `keyword`, `text`, `do`, `see`, `story`, `name`, `file`, `sub_epic`, `steps`) must stay exactly as they are. Proposal S1 or A5 may propose reshaping `ScenarioFileReading`; this proposal should follow that one rather than fix a seam that is about to move.

## Graph hits judged noise

| File:line | Rule | Why it is noise |
|---|---|---|
| cdd_guidance/practices/stories/model/story_recording.py `_align` (253) | simplify-control-flow (nests 5 deep) | The body is one flat `if / elif / elif / elif / elif` chain; the scanner counts each `elif` as a nested `if`. Real nesting depth is one. (The type switch itself is a real finding, listed above under another rule.) |
| cdd_guidance/practices/stories/model/graph_reading.py `StoriesReading` acts on data bag `ScriptStoryModel` | shape-classes-around-resources | `ScriptStoryModel` has behaviour of its own (`save`, `story_file`, `copy_of`, `writing`) and inherits `load`, `parse`, `render`, `reshape`. The scanner saw only its three declared properties. `StoriesReading` asks it to parse; that is collaboration. |
| cdd_guidance/practices/stories/model/python/shared_story_file.py `__init__` takes 4 parameters (41) | limit-operation-parameters | `FixtureExample.__init__(name, example_value, facts, declared)` is a constructor called from one place (205); creation is exempt. (The class itself is questioned above under another rule.) |
| cdd_guidance/practices/stories/model/.context/story-model.md parameters `practice`, `path`, `content`, `block`, `children`, `file`, `node`, `node` missing a type annotation | use-typed-signatures | Hits on the model document's listing, not on code; the scanner reads prose signatures. The matching code parameters that do lack a type are reported on their code lines. |
| cdd_guidance/practices/stories/app/story-map/story-map-client.ts (`StoryMapClient` acts on data bag `Edit`) | shape-classes-around-resources | `Edit` is a type alias for `Promise<StoryModelData \| null>` (:17), not a class holding state; `answerTo(edit)` awaits it. The real resource problem in this file is `StoryMapNode` and its `kind` string, reported above. |
| cdd_guidance/practices/stories/model/markdown/scenario_parts.py (`__init__` takes 4 parameters) | limit-operation-parameters | `StorySection.__init__(name, heading, line, file)` is construction of a value read from one heading; creation is exempt from the count. (The neighbouring hit on `BackgroundReading.heading`, also 4 parameters, is real and is reported above.) |
| cdd_guidance/practices/stories/model/drawio/nodes.py:314 (`_drawn_geometries` only used from `_KeptPlaces`) | prefer-class-operations | Not noise — real but trivial; listed under fixes (item 9) and removed entirely by A2. |
| cdd_guidance/practices/ux/story-demo/mount-generated-mockup.js:545 (`GeneratedMockup` constructs `ExplorerPanel`) | use-explicit-dependencies | `ExplorerPanel` and `ProductPanel` are parts the mockup builds once from itself (`new ExplorerPanel(this, chrome, expansion)`); nothing a caller could hand in differs. The rule exempts such parts. The real problem there is the panels holding the whole mockup, reported above. |
| cdd_guidance/practices/ux/model/story_link.py:204 `_ancestor`, :211 `_parent` ("only used from `StoryTargets`") | prefer-class-operations | As worded it is wrong: both are also called by the module functions `key_of` (:190) and `_story_name` (:200), which `StoryLink` and two other files use. Moving them onto `StoryTargets` alone would break `key_of`. The real finding is the whole group of module functions, handled by U2. |
| cdd_guidance/practices/ux/model/ux_map.py:32 (`UxMap` exposes 11 public operations) | keep-classes-single-responsibility | Half noise. Three of the eleven (`from_workspace`, `workspace_text`, `workspace_file`) have no caller and go with UX fix 1, which brings the class to 8, under the budget. The split the message asks for is not needed for the count; the mixed roles are a separate, real finding (U6). |
| cdd_guidance/practices/ux/model/.context/ux-model.md (`name`, `sequential_order` missing a type annotation) | use-typed-signatures | The scanner read a model document's class box as code. The constructors in code are typed (`ux_node.py:28`). Fix the document's notation if wanted; it is not a code defect. |
| cdd_guidance/practices/ux/model (cycle, six lines: `model`↔`drawio`, `model`↔`html`, `html`→`json`, `json`→`model`) | one-way-deps | Not noise: real, and all six lines are one cycle with one cause (`graph_reading.py:24-25`). Listed here so the six are counted once. |
| cdd_guidance/actions/render/rendered_code.py:87 (`RenderHasNoDeclaredPlace.__init__`, 4 parameters) | limit-operation-parameters | A domain exception carrying the piece, the format, the declared paths and the reason is what `domain-exception-carries-context` asks for; constructors of failures are creation, which the rule exempts. |
| cdd_guidance/actions/render/reshaped_code.py:67 (`Member.__init__`, 5 parameters) | limit-operation-parameters | A value record of four line positions and a name, built in three places inside one parser; packing them would hide the same values. The real issue is that this record exists four times (finding under `reshaped_code.py:85`). |
| cdd_guidance/actions/render/rendered_code.py:76 (`_says_where_name_ends` "only used from RenderedCode") | prefer-class-operations | The premise is wrong: the module function `own_name` (line 66) also calls it, and `own_name` is called from `rendered_file.py:130`. Moving it onto `RenderedCode` would break that caller. The function is misplaced, but it belongs on `DeclaredFile` (R2), not where the hit points. |
| cdd_guidance/desktop_walk/desktop_walk.py:177 (`DesktopWalk.__init__`, 4 parameters) | limit-operation-parameters | Three of the four are collaborators with defaults (`opener`, `test_chats_folder`, `make_repository`), passed through the constructor as `use-explicit-dependencies` asks; only `project` is required. |
| cdd_guidance/desktop_walk/desktop_walk.py:182 (`DesktopWalk` constructs `NewRepository` inside its constructor) | use-explicit-dependencies | The constructor does not build a `NewRepository`; it stores a default function that builds one when `open_test_chat` runs, and a caller can hand in `make_repository` instead (the specs do). The collaborator is injectable, which is what the rule protects. |
| cdd_guidance/actions/render/rendered_code.py:115 (`rendered` generic container) and :147 (`content`) | use-typed-signatures | Not noise in substance, but not a separate finding: both are the same missing `RenderResult` type reported once under `render.py:45`; fixing these two parameters alone would add a type the framework's `render` does not return. |

### Graph hits in the area judged real, for the record

Stories core: `ExampleObservations` copies fields of `StoryLinks` (modelled_areas.py); `_step_body` duplicated (modelled_areas.py); `__init__` duplicated (typescript_story_model.py); `value` (modelled_areas.py); `node` untyped (stories_formats.py:55); `_write_epic` 4 parameters and `_take_stories` 5 (code_story_model.py); `_load_child_band` 4 (story_model.py); `BraceStoryWriting` acts on `StoryFilePlace` (brace_story.py); `Increment` takes 4 parameters in story-model.md (the document is wrong, the code takes 3).

`drawio/nodes.py:311 _corner` classmethod (UX fix 11), `ux_map.py:279 _name_of` (UX fix 7), `view/reshaped_view.py:169 value` (UX fix 5), and the cycle (U1).

`render.py` `_render_files` (4), `_saved_by_declared_paths` (5), `_saved_code` (4); `RenderedCode.__init__` (7); `ReshapedCode`'s `_python_member` (4, small); `DesktopStep.__init__` (5, small); `RenderedFile._scope_of` classmethod; `_record_screen_stories` module function; generic containers `drawn`, `held` (kept_document.py), `result` (render.py), `rendered` (rendered_file.py).
