# Judgment, round 2: Stories, UX, actions, patterns, align, context setup, diagnostics

**Judged:** 2026-11-24, on branch `release-1-2-fixes` at commit `5d16245ff`, read only. No production code, test, or document was changed.

**Area:** the 139 production files of `stories-ux-actions-patterns.txt` changed since 2026-11-21 (base commit `66f410de3`): `cdd_guidance/practices/stories` (practice classes, `model/` and its format adapters, graph reading, rules, templates, the Story UI app), `cdd_guidance/practices/ux` (model, format adapters, views, rules), `cdd_guidance/practices/template_checks.py`, `cdd_guidance/actions`, `cdd_guidance/align`, `cdd_guidance/context_setup`, `cdd_guidance/diagnostics`, and `cdd_guidance/patterns` (without `oss_portal_domain_driven`).

**Read:** every listed file in full at its current content (the large `story-map-views.tsx` and `drawio_ux.mjs` included), with the Clean Engineering code, model and modules rules, `.claude/rules/coding.md`, the refactor guardrails, the module card and model of each module, and the first round's judgment of this area.

**How it was judged:** the area was read in seven parts (Stories core; Stories graph reading, files, rules and templates; Stories format adapters; Story UI app and UX core; UX format adapters and views; actions; patterns, align, context setup, diagnostics), each file judged whole, not only its changed lines. Every "unused", "no caller" or "only used inside" claim was checked with a grep over `cdd_guidance`, `harness`, `space`, `tools`, `scripts` and `story_tests`, specs included. A finding the first round also made (same file, same rule, same problem) ends with "(still open from round 1)"; round-1 findings were matched across the renames since (`story_model.py` to `story_map.py`, `StoryModel` to `StoryMap`, `*_story_model.py` to `*_story_map.py`). Nothing was run. Line numbers are those of `5d16245ff`.

## Counts

| Measure | Count |
|---|---|
| Files read | 139 |
| Files with no findings | 26 |
| Findings | 420 |
| Findings still open from round 1 | 206 |
| New findings | 214 |
| Design proposals | 44 |

Round 1 made 393 findings in this area over a wider file set (it also covered `builders`, `desktop_walk`, the Story Demo JavaScript and files since deleted or renamed); this round judges only the files changed since `66f410de3`.

**Findings by part:**

| Part | Files | Findings | Still open from round 1 |
|---|---|---|---|
| Stories core (`stories.py`, `story_map.py`, code story maps, writing, recording) | 21 | 60 | 44 |
| Stories graph reading, files, rules, templates | 21 | 64 | 21 |
| Stories format adapters (draw.io, whiteboard, Miro, JSON, markdown, sketch) | 20 | 66 | 34 |
| Story UI app and UX core | 17 | 69 | 37 |
| UX format adapters and views | 13 | 53 | 28 |
| Actions | 23 | 68 | 32 |
| Patterns, align, context setup, diagnostics | 24 | 40 | 10 |

**Findings by theme:** [1] module boundaries 47, [2] the same work in different shapes 106, [3] resource orientation 176, [4] domain orientation 84 (a few bullets carry no theme).

**Findings by rule:**

| Rule | Findings |
|---|---|
| eliminate-duplication | 86 |
| hold-state-on-the-object-not-in-parameters | 33 |
| use-typed-signatures | 28 |
| hide-inner-details | 24 |
| prefer-class-operations | 23 |
| put-logic-on-the-owning-resource | 22 |
| use-intention-revealing-names | 19 |
| use-consistent-naming | 17 |
| provide-meaningful-context | 14 |
| low-coupling | 12 |
| no-legacy-api-after-refactor | 11 |
| limit-operation-parameters | 11 |
| keep-operations-single-responsibility | 11 |
| use-explicit-dependencies | 10 |
| delete-unused-operations | 10 |
| class-not-property-instance-or-subtype | 10 |
| shape-classes-around-resources | 9 |
| errors-out-of-existence | 9 |
| abstraction-focus | 6 |
| temporal-independence | 5 |
| single-boundary | 5 |
| prefer-instance-operations | 5 |
| limit-comments | 5 |
| write-interactions | 4 |
| use-property-not-accessor | 4 |
| keep-classes-single-responsibility | 4 |
| use-exceptions-properly | 2 |
| seam-names-current-code | 2 |
| one-way-deps | 2 |
| make-module-only-operations-private | 2 |
| keep-operations-small-focused | 2 |
| high-cohesion | 2 |
| avoid-vague-parameter-names | 2 |
| no-module-per-class | 1 |
| never-swallow-exceptions | 1 |
| merge-one-class-packages | 1 |
| limit-function-lines | 1 |
| limit-class-methods | 1 |
| general-purpose-surface | 1 |
| domain-nouns-only | 1 |
| delete-unused-classes | 1 |
| deep-module | 1 |

## Defects found while judging

None was run; each needs a failing test before a fix.

- **Story UI, drop at the end does nothing:** dragging a story or sub-epic to the end of a row, or into an empty sub-epic or epic, does nothing and shows nothing (`story-map-views.tsx:661`, `moveInto`).
- **Story UI, step keyword never saved:** the keyword dropdown on a step changes only local state, so a changed keyword reverts on the next read (`story-map-views.tsx:1406`).
- **Story UI, Show Scenarios does nothing:** `StoryHierarchyView` never reads `showScenarios`.
- **Story UI, "And" saved as "Then":** an And or But step is always saved as a Then (`story-map-nodes.ts:206`).
- **`CodeStoryMap.load` overrides `StoryMap.load` with another meaning:** an instance method reading a dict of story files replaces the class-level tool that opens a map in a session, so `PythonStoryMap.load(file, call=...)` would take the file as `self` (`code_story_map.py:562`).
- **Thin slice read with the wrong project:** `markdown/nodes.py:396` passes the map's folder as the project (`ThinSlice.from_folder(root, self, root)`), so increments name `thin-slice.md` relative to that folder, not the project root.
- **Drawn thin slices are never read back:** the draw.io, Miro and whiteboard `load_thin_slice` readers are called only from specs, so lanes a person edits in a drawn thin slice never reach the story map.
- **Thin-slice stories matched by name:** `ThinSliceLayout._by_column` and the whiteboard's `_map_story` match an increment's stories by name, so two stories of one name in different sub-epics share a column or a card.
- **An unreadable drawing is overwritten silently:** `_KeptPlaces.from_text` and `actions/render/kept_document.py:60` treat a draw.io or whiteboard file they cannot parse as "nothing kept", and the save writes over it (still open from round 1).
- **Two story-map rules check different files:** `ExamplesExportDataNotRepository` checks the story test's own path while `DomainFixtureExampleFiles` checks the file the example comes from; `templates_and_rules_heavy_spec.py:57-61` already lists both rules' example pairs as not holding.
- **Any `.json` source is taken for a saved graph** (`actions/render/source_files.py:13`), so `render.py:136` saves it as a document built from a graph although `render` offers `json` as a source format.
- **Wrong line on LERN repositories:** `patterns/lern_domain_driven/fact_files.py:185` counts `raw_io` lines from the start of a joined snippet, not the file, so `NodeRepositoryParsesOnRead` names the wrong line.
- **A syntax error stops the whole graph read:** a `.py` file carrying `@language_adapter(` that does not parse makes `patterns/cdd_web_domain_access/access_facts.py:83` raise `SyntaxError`, uncaught at `harness/graph/graph_build.py:453`.
- **Stale guidance:** both scenario templates name rules that no longer exist (`then-and-chaining`, `artifacts-mirror-story-hierarchy`); `ux-model.md` still describes the removed `NoJavascriptPractice` refusal; `patterns-model.md` still lists `LernDomainDriven.test_setup_text` and names Clean Engineering as the home of `SourceText`.

## Findings

Theme tags: [1] module boundaries, [2] the same work in different shapes, [3] resource orientation, [4] domain orientation.

### cdd_guidance/practices/stories/model/brace_story_file.py

- brace_story_file.py:16-21 `_STORY`, `_SCENARIO`, `_BACKGROUND`, `_STEP`, `_CHAINED` — eliminate-duplication — the same calls are still matched by a second set of patterns in `BraceSyntax` (brace_story.py:21-33: `_CALL`, `scenario_pattern`, `_BACKGROUND`, `_CALL_NAME`), and both sets still run on one file: a story's steps are read from text by `BraceSyntax.steps_in` (code_story_map.py:204) and then matched to these blocks by position (`read_step_code`, story_file.py:118-121). A change to how a step call is written must be made in both. [2] (still open from round 1)
- brace_story_file.py:101-102, 109-110, 127-128, 140-144 `BraceBlock.inside_lines`, `language`, `split_inside`, `setup` — eliminate-duplication — `inside_lines`, `language` and `split_inside` are the same lines as `PythonBlock` (python/story_file.py:69-71, 77-79, 95-96), and `setup` differs from python/story_file.py:108-114 only in the comment filter and the blank-line squeeze; the shared base `StoryBlock` (story_file.py:23) now exists and could hold them once. [2] (still open from round 1)

### cdd_guidance/practices/stories/model/code_story_map.py

- code_story_map.py:83-193 `StorySyntax` with story_file.py:158-185 `BlockStoryFile` — eliminate-duplication — a story file is still read by two parsers. `CodeStory.from_block` (304-310) builds the story's backgrounds and steps from text through the regexes (`load` → `_fill` → `syntax.backgrounds_in` 349, `syntax.steps_in` 204), then `read_code` (312-324) attaches each node's code from the blocks by position: `zip(self.backgrounds, backgrounds)` (316), `zip(self.scenarios, scenarios, leads)` (321) and `read_step_code` (story_file.py:120), with `Step.read_code` guarding a mismatch (story_map.py:627). [2] (still open from round 1)
- code_story_map.py:174-193 `StorySyntax._balanced`, `_outside_scenarios` — abstraction-focus — the base syntax of every language finds `scenario(`, `=>` and `{`, which only the brace languages write; only `BraceSyntax` calls them (brace_story.py:45, 53, 77, 94) and Python inherits them unused. [2] (still open from round 1)
- code_story_map.py:76-80 `CodeStoryNode` — class-not-property-instance-or-subtype — the mixin is now one method, `snake()`, with one caller (story_writing.py:187), yet it is mixed into `CodeScenario`, `CodeStory`, `CodeIncrement` and `CodeEpic` (196, 258, 369, 373); `Name(story.name).title_snake` at the call site does the job. [3] (still open from round 1)
- code_story_map.py:71 `unescaped` — prefer-class-operations — a module function imported by three other files (brace_story.py:11, brace_story_file.py:13, python/nodes.py:7); each caller is a syntax or a story-file reader of one language, which should own its unescaping. [3] (still open from round 1)
- code_story_map.py:637 `_take_stories(holder, stories, written, content, source_file)` — limit-operation-parameters — five parameters, four of which are the one `StoryFile` the caller already holds at 616-617 (`story_file.stories`, `story_file.own_code`, its text and its path). [3] (still open from round 1)
- code_story_map.py:488 `_write_epic(epic, parent, examples_folder, files)` — limit-operation-parameters — four parameters; `files` is an output dict threaded through the recursion (472, 493, 496). [3] (still open from round 1)
- code_story_map.py:570, 482-486 `self.project = project` — hold-state-on-the-object-not-in-parameters — `load` stores its argument on the map so `story_file` can read it back, while `story_file` also takes `project` as a parameter and falls back to the field; the same fallback `project if project is not None else self.project` is written four times (code_story_map.py:486, brace_story.py:179, python/python_story_map.py:75, script_story_map.py:81). [3] (still open from round 1)
- code_story_map.py:376-389 `CodeEpic.order_path` — hide-inner-details — walks parents with `hasattr`/`getattr` for `sequential_order`, `parent` and `epics` on nodes that are always an `Epic` or a `StoryMap`; its only caller is `StoryFilePlace.orders` (story_writing.py:69). [3] (still open from round 1)
- code_story_map.py:512-560 `_adopt_code`, `_take_story_code`, `_take_children_code`, `_take_code`, `_take_step_bodies` — put-logic-on-the-owning-resource — the map reaches into each node to overwrite `written`, `setup`, `file_written` and step bodies, while each node holding code is a `CodeHeld` with its own `take_code_from` (story_map.py:314); "take the code of this other node in my language" is the node's operation. [3] (still open from round 1)
- code_story_map.py:562 `CodeStoryMap.load(self, external, *, on_file, project)` — use-consistent-naming — overrides `StoryMap.load(cls, file, *, call)` (story_map.py:1323-1325), the classmethod tool subject that opens a map in a session, with an instance operation that reads a dict of story files. One name on one class hierarchy carries two contracts, so `PythonStoryMap.load(file, call=...)` would bind the file as `self`. [2]
- code_story_map.py:352 `getattr(background, "body", "")` — use-consistent-naming — `Background` declares no `body`; `BraceSyntax.backgrounds_in` sets one from outside as a `str` (brace_story.py:66), while `Step.body` is a `CodeBody` (story_map.py:573) and `CodeHeld.take_code_from` copies `body` by `hasattr` (story_map.py:319-320). One attribute name holds two types and is read reflectively. [4]
- code_story_map.py:335-337 `_take_background_examples` — errors-out-of-existence — a `background-examples:` comment whose JSON is not an object is read as no examples (`return` at 337), and one that does not parse raises a bare `JSONDecodeError` naming no file; a wrong shape should be refused with the file named, not read as empty. [4]

### cdd_guidance/practices/stories/model/javascript/javascript_story_map.py

- javascript_story_map.py:29 `seed_file` — one-way-deps — the JavaScript step library is read from `parents[2] / "templates" / "js" / "story-test.js"`, reaching out of the model package into the practice's templates, while the TypeScript one sits in the model package (typescript/typescript_story_map.py:26, `model/typescript/seeds/story-test.ts`); two homes for the same kind of file. [2] (still open from round 1)

### cdd_guidance/practices/stories/model/javascript/nodes.py

- javascript/nodes.py:10-22 `JavaScriptScenario`, `JavaScriptStory`, `JavaScriptEpic` — class-not-property-instance-or-subtype — `JavaScriptScenario` is empty, `JavaScriptEpic` only names its story class, and `JavaScriptStory` adds `language = JAVASCRIPT`, which nothing reads (the map's own `language` is the one read, code_story_map.py:466-557; no `story.language` read in the package). Three classes mirror typescript/nodes.py:10-22 to carry one value the map already holds. [2] (still open from round 1)

### cdd_guidance/practices/stories/model/python/nodes.py

- python/nodes.py:15-39 `PythonSyntax` — eliminate-duplication — reads scenarios (16), step calls (15, 34-39) and the background (23-32) by regex, while `PythonStoryFile`/`PythonBlock` read the same `with` blocks through `ast` (python/story_file.py:20-27, 98-106); both run on every Python story test and are joined by position (the two-parser problem of code_story_map.py:83). [2]

### cdd_guidance/practices/stories/model/python/python_story_map.py

- No findings.

### cdd_guidance/practices/stories/model/python/shared_story_file.py

- shared_story_file.py:143 `_search` — use-explicit-dependencies — the folders an examples module is looked for in fall back to `Path.cwd()` and `sys.path`, so what a read in the MCP server finds depends on where the server was started. [3] (still open from round 1)
- shared_story_file.py:35 `_EXAMPLES_MODULE` — eliminate-duplication — `re.compile(r"examples$")` is defined again at graph_reading.py:43. [2] (still open from round 1)
- shared_story_file.py:55-58 `FixtureExample.clone` — eliminate-duplication — repeats the field list of `Example._copy_fields` (story_map.py:362-364: the value copied when a dict, order, scope) and bypasses the one copy path every node shares (`StoryNode.clone` → `_copy_fields`, story_map.py:184-189); overriding `_copy_fields` to add `fixture_facts` and `_declared` would keep one list. Round 1 reported the same copy under no-redundant-relationship-paths. [2]
- shared_story_file.py:267 `is_shared_story_file` — prefer-class-operations — a module function with one caller (python/python_story_map.py:74) that answers whether a text is a `SharedStoryFile`; it belongs on that class. [3]

### cdd_guidance/practices/stories/model/python/story_file.py

- python/story_file.py:126-127 `_is_inside(blocks: Sequence[StoryBlock])` — use-typed-signatures — the signature says any `StoryBlock`, but the body reads `block.node.lineno` and `block.node.end_lineno`, which only `PythonBlock` has (`StoryBlock` declares no `node`, story_file.py:23-110); the type promises what the body cannot take. [4]

### cdd_guidance/practices/stories/model/reshaped_story_file.py

- reshaped_story_file.py:89, 125 `self._writing._scenario_lines`, `self._writing._step_lines` — hide-inner-details — calls two private operations of `StoryWriting` (story_writing.py:274, 240) from another class, so their signatures are a seam nobody declared. [1] (still open from round 1)

### cdd_guidance/practices/stories/model/script_story_map.py

- script_story_map.py:24-26 `script_story_file_suffixes` — prefer-class-operations — a module function called only to fill a class attribute of the two subclasses (typescript_story_map.py:25, javascript_story_map.py:28) from `LEAF_EXTENSION`, which `ScriptStoryMap` already declares (39). [3] (still open from round 1)
- script_story_map.py:55-60 `_default_story_test_folder` — provide-meaningful-context — the literal `"stories"` workspace root decides where the step library goes, with no name saying which convention it is. [4] (still open from round 1)
- script_story_map.py:62-75 `story_test_folder`, `story_test_import_path` — use-intention-revealing-names — "story test" names the step library `story-test` here while a story test is a `{story}_story.test` file (21); the docstrings have to say "step library", and `Stories.story_test_folder` (stories.py:91) carries the name into the practice. [4] (still open from round 1)
- script_story_map.py:29-32 `ScriptStory` — class-not-property-instance-or-subtype — an empty subclass of `BraceStory` whose docstring is written twice (30, 32); its only subclasses are `TypeScriptStory` and `JavaScriptStory`, which add nothing read (see javascript/nodes.py). [2]

### cdd_guidance/practices/stories/model/story_copies.py

- story_copies.py:12-30 `StoryCopies` — class-not-property-instance-or-subtype — made and used in one statement by its only caller (story_map.py:1310) to finish `StoryMap._copy_fields`; the zip of original and copied stories is multi-step work of that operation, which private steps on `StoryMap` would hold without a second type. [3]

### cdd_guidance/practices/stories/model/story_file.py

- story_file.py:113-121 `flat_steps`, `read_step_code` — prefer-class-operations — module functions that take a scenario's or background's steps and walk them; `flat_steps` is imported by code_story_map.py:49, python/python_story_map.py:15 and reshaped_story_file.py:26, and story_map.py:730 `_steps_key` writes the same "step, then its ands" walk again. "My steps with their ands" is a question `Scenario` and `Background` answer. [3] (still open from round 1)

### cdd_guidance/practices/stories/model/story_map.py

- story_map.py:1329-1336 `StoryMap.load` — write-interactions — reaches through five parts of the session in eight lines (`session.paths.path_named`, `session.session_files.file_manager`, `files.read(os.path.relpath(path, files.workpath))`, `session.graph.practices.of(...)`, `session.checkout.root`), and the `files.read` at 1332 is called only for its side effect, its result thrown away. [1] (still open from round 1)
- story_map.py:1344-1349 `StoryMap.open_in_session` — put-logic-on-the-owning-resource — picks "the first fidelity" by iteration order (`next(iter(stories.fidelities))`, 1345) and the first existing file of its declared output; which file is a session's story map is the Stories practice's knowledge. [3] (still open from round 1)
- story_map.py:1273, 1279 `self.links = None`, `self.slicing = None` — use-typed-signatures — two collaborators typed only by comments (the model document names `links: StoryMapLinks | None`), and `new_increment` (1389) and the opened map's save call into whatever was assigned. [4] (still open from round 1)
- story_map.py:54, 366-383, 401-414 `ExampleValue = Any` — use-typed-signatures — an example's value is a dict, a class, a string or any object, and `cells`, `edit_field` and `rename` each branch on `isinstance` over the same set of shapes. [3] (still open from round 1)
- story_map.py:439-489 `Examples(dict)` — hide-inner-details — the examples of a scope are a `dict` subclass, so every caller may use any dict operation; `rename` (458-463) rebuilds the dict with `dict.clear`/`dict.update` to keep order, and `drop` exists beside `del`. [3] (still open from round 1)
- story_map.py:222, 595, 844, 999, 1133, 1405 `holding(part)` — hide-inner-details — a public operation that hands out a node's private mutable list (`self._ands`, `self._steps`, `self._epics`); its only callers are `move_before`, `_leave` and `Step.segment` in this file (280, 297, 589). [1] (still open from round 1)
- story_map.py:730 `_steps_key`, 1523 `_renumber` — prefer-class-operations — module functions used only by classes in this file; `_steps_key` repeats the step-then-ands walk of `flat_steps` (story_file.py:113). [2] (still open from round 1)
- story_map.py:343, 709, 767, 886, 1048, 1164, 1418 `record` — use-consistent-naming — one verb, five signatures: `Example.record(recording, scenario, lines)`, `Step`/`Background.record(recording, file, parent)`, `Scenario.record(recording, story, parent)`, `Story`/`Epic.record(recording, parent)`, `StoryMap.record(practice, *, on_node)`; the recording cannot ask a node to record itself without knowing its kind. [4] (still open from round 1)
- story_map.py:314-320 `CodeHeld.take_code_from` — put-logic-on-the-owning-resource — the base class copies `body` only `if hasattr(self, "body")`, reading `getattr(source, "body", CodeBody())`: a `Step`'s field handled by reflection in its base, and also taken by a `Background` that was given a `str` body from outside (brace_story.py:66). `Step` should add its body in its own override. [3]
- story_map.py:176-182 with 1290-1295 `copy_of` — use-consistent-naming — `StoryNode.copy_of` is a classmethod factory (`cls(source.name)`), while `StoryMap.copy_of` overrides it as an instance operation that needs the map's settings; `_as_part_class` (69-71) calls `part_class.copy_of(part)` on a class, which works for every node but a story map. One name, two binding kinds. [2]
- story_map.py:1514-1520 `StoryTestScenarios._same_named` — keep-operations-single-responsibility — a query that pairs read stories with the map's stories also sets every read scenario's `source` (1516-1518); the mutation is hidden in the answer, and `take` (1499) is its only caller. [3]

### cdd_guidance/practices/stories/model/story_node_types.py

- story_node_types.py:9, 51-55 `NodeEvidence`, `"Module"`, `"OoadClass"`, `"Operation"`, `"Property"` — low-coupling — imports `NodeEvidence` from `clean_engineering/reading/node_evidence.py`, which the reading package's card does not offer as a term (cdd_guidance/practices/clean_engineering/reading/.context/module-context.md:13), and names Clean Engineering's node types by string to filter a module's members. Stories depends on the inside of Clean Engineering's reading. [1]

### cdd_guidance/practices/stories/model/story_recording.py

- story_recording.py:50, 75, 343 `example_source_file`, `imported_files`, `file_of` — prefer-class-operations — `example_source_file` and `imported_files` take a `StorySource`'s `file` and `imported_modules` as parameters and are wrapped by `StorySource.example_source` (146-148) and `imported_example_files` (150-154) a few lines below; `file_of(node)` is the node's own file, imported by story_map.py:34 and called eight times there. [3] (still open from round 1)
- story_recording.py:242-256 `_align` — put-logic-on-the-owning-resource — a five-way switch on `node.type` strings decides how each kind of node finds its lines, its step set `{"Step", "Given", "When", "Then"}` written again beside `STEP_TYPES` (story_tree.py:16); each node kind should say how it is aligned, as `Example.declaration` already does. [3] (still open from round 1)
- story_recording.py:212-218 `story_map`, `practice`, `graph`, `on_node`, `story_at`, `story_total` — hide-inner-details — six public attributes; nodes use only `graph`, and the progress counters are the recording's own. [1] (still open from round 1)
- story_recording.py:213 `self.practice` — delete-unused-operations — set and never read, inside the class or outside it (no `recording.practice` anywhere in the repository; the class reads `practice.reading` only in its constructor). [3]
- story_recording.py:214 `self.graph` with story_map.py:350, 715, 773, 901, 1062, 1173 — write-interactions — every node records an edge by reaching through the recording into the graph's edge store (`recording.graph.edges.link(kind, parent, node)`); the recording that adds the node (`add`, 232) should offer the link too. [3]
- story_recording.py:89-180 `StorySource` — keep-classes-single-responsibility — one class reads script imports, Python imports, exported constants, domain class names, declared examples in two languages (`_EXAMPLE_DECLARATIONS`, 37-44, chosen by suffix) and a docblock's evidence, all by regex over the text; the per-language knowledge sits beside, not in, each language's syntax. [2] (still open from round 1)
- story_recording.py:30-32, 75-86, 156-172 `_NAMED_IMPORT`, `_PYTHON_FROM_IMPORT`, `imported_files`, `_script_imports`, `_python_imports` — eliminate-duplication — a file's imports are read a second way beside `BraceSyntax.import_pattern` (brace_story.py:27) and `PythonSyntax.import_pattern` (python/nodes.py:17), and a third beside `source_code`, which the Stories card names as a dependency and which already reads Python and script imports (`PythonImports`, `ScriptImportClauses`, script_imports.py:127-175) and exports a different `imported_files` of the same name (script_imports.py:41). [2] (still open from round 1)

### cdd_guidance/practices/stories/model/story_writing.py

- story_writing.py:37, 72, 77, 94, 101, 110, 124, 131 — prefer-class-operations — eight module functions (`example_names_of`, `as_read`, `story_description`, `story_notes_lines`, `background_examples_line`, `scenario_examples_lines`, `own_backgrounds`, `_step_texts`) each take a story, scenario or background and read its fields; they are called from `StoryWriting` and its subclasses (python/python_story_map.py:39-48, brace_story.py:14) and `CodeStoryMap` (code_story_map.py:504), and `own_backgrounds(scenario)` and `scenario_examples_lines(scenario)` are questions a `Scenario` answers about itself. [3] (still open from round 1)
- story_writing.py:72-74, 252-253 `as_read`, `_is_as_read` (and story_map.py:310-311 `written`, `file_written`) — use-intention-revealing-names — `written` means "the lines this node was read with" throughout, so the word for output names input and `_is_as_read` has to translate it. [4] (still open from round 1)
- story_writing.py:298-300 `_callback` — abstraction-focus — the writing every language shares spells a JavaScript arrow function (`"async () => {"`); Python inherits it and never uses it, since its templates have no `{callback}` (python/python_story_map.py:31-33). [2] (still open from round 1)

### cdd_guidance/practices/stories/model/typescript/__init__.py

- typescript/__init__.py:1-3 `TypeScriptStoryMap` — no-legacy-api-after-refactor — a package re-export nothing uses: the practice names the class by its module path (stories.py:30, `typescript.typescript_story_map`), no file imports `stories.model.typescript` as a package, and the `python` and `javascript` packages have no such `__init__.py`. A second entry point to one class. [2]

### cdd_guidance/practices/stories/model/typescript/nodes.py

- typescript/nodes.py:10-22 `TypeScriptScenario`, `TypeScriptStory`, `TypeScriptEpic` — class-not-property-instance-or-subtype — `TypeScriptScenario` is empty, `TypeScriptEpic` only names its story class, and `TypeScriptStory` adds `language = TYPESCRIPT`, which nothing reads; the same three classes are written again for JavaScript (javascript/nodes.py:10-22). [2] (still open from round 1)

### cdd_guidance/practices/stories/model/typescript/typescript_story_map.py

- No findings.

### cdd_guidance/practices/stories/stories.py

- stories.py:140-144 `story_tests` — use-typed-signatures — returns `dict[str, list[str]]` (file path to story names): `ProjectStoryFiles.story_tests` turns the stories it read into name strings (project_story_files.py:53), and `OpenedStoryMap` (opened_story_map.py:118) matches them back by name. [3] (still open from round 1)
- stories.py:102-103 function-level imports in `markdown_values` — one-way-deps — `stories.rules` and `harness.graph.practice_rule` are imported inside the property though no cycle forces it (`stories/rules/__init__.py` imports only the rule modules, and none of them imports stories.py; only `rules/rule_examples.py` and specs do), so two dependencies of the practice class are hidden from the top of the file. [1] (still open from round 1)

### cdd_guidance/practices/stories/stories_formats.py

- stories_formats.py:29-30 `ThinSlicedMap.semantic_type` — use-property-not-accessor — a method that returns the constant `"ThinSlice"` so the wrapper passes for an object model; `render` (104) then switches on `isinstance(request.content, ThinSlicedMap)` to route it. [3] (still open from round 1)
- stories_formats.py:51-55 `SpecifiedStories._keeps` — keep-operations-single-responsibility — answers whether an epic holds a specified story and, while answering, removes stories and sub-epics from it (53-54); a predicate that mutates surprises every later caller. [3] (still open from round 1)
- stories_formats.py:71-75, 147 `ScenariosOnTheirMap.read_by(markdown)` — hold-state-on-the-object-not-in-parameters — the markdown story map is handed to the only operation by the only caller (147), which got it by name; the object holds the map file, the files and the project already and could be built with the reader too. [3] (still open from round 1)
- stories_formats.py:131, 147 `adapter_class("markdown")`, `adapter("markdown")` — hold-state-on-the-object-not-in-parameters — formats looked up by a name string where the caller means one known class, repeating a key of `_FORMAT_ADAPTERS` (stories.py:24), so a renamed format breaks at run time only. [3] (still open from round 1)
- stories_formats.py:95-97, 139-141 — eliminate-duplication — "the files under each named entry of the project" is written twice, with different globbing (`rglob("*")` plus `is_file` in `read`, `rglob("*.md")` in `_scenarios_on_their_map`). [2] (still open from round 1)


### cdd_guidance/practices/stories/model/graph_reading.py

- graph_reading.py:19, 419, 440, 487 `MODULE_FUNCTION_HOLDER`, `self.clean.code_index.members_named`, fact `"owner"` — low-coupling — `StoryLinks` still reads Clean Engineering's code index, its `owner` fact and a constant from `clean_engineering/model`; the Clean Engineering card (clean_engineering/.context/module-context.md:27) lists none of the three as terms other packages use. [1] (still open from round 1)
- graph_reading.py:284, 358 `ImportedFiles`, `StoryLinks` — high-cohesion — the file still holds the practice's reading, `ImportedFiles` and the 140-line `StoryLinks`, while the sibling link writers `TermLinks` and `RealizationLinks` each have a file of their own (term_links.py, realization_links.py); only `read_working_copy` (159) constructs `StoryLinks`. [1] (still open from round 1)
- graph_reading.py:191, 257 `_story_map`, `_story_maps` — use-typed-signatures — still no return types on the two operations that decide which story map the graph is built from (145 `_story_files` has none either). [4] (still open from round 1)
- graph_reading.py:46-49 `CALLS_REACH_*` — use-typed-signatures — four string constants still stand for one closed set; rules/acceptance_tests.py:81 imports two of them and the fact name `"calls_reach"` is written as a literal at 422 and again at rules/acceptance_tests.py:177, while realization_links.py:23-25 repeats the same pattern for `realization_reach`. [4] (still open from round 1)
- graph_reading.py:233 `_story_tests` — hold-state-on-the-object-not-in-parameters — still builds a second adapter per language with `type(language)(tests_root=_MAP_LESS_TESTS_FOLDER)`, dropping the settings the practice's own adapter holds; project_story_files.py:190 does the same with `STORY_TESTS_FOLDER`. [3] (still open from round 1)
- graph_reading.py:86-89 `StoriesReading.steps` — eliminate-duplication — the same body as `StoryTree.every_step` (story_tree.py:82-84): every node of `in_graph` whose type is a step type; space/session/files/session_file.py:313 calls one, the link writers the other. [2]
- graph_reading.py:132-136 `_files_held` and 391-394 `StoryLinks.story_files` — eliminate-duplication — both walk `in_graph.nodes()` for nodes with a `source.file`; `WrittenStoryNodes._nodes_by_file` (story_tree.py:246-253) is a third copy. [2]
- graph_reading.py:143, 145-147 `_is_story_file`, `_story_files` — put-logic-on-the-owning-resource — `_story_files()` builds a new `ProjectStoryFiles` on every call (stories.py:135-138), and `read_with` (128) calls `_is_story_file` once per refreshed path, each building it and its `code_readers` list again; `_take_code_scenarios` (219), `_script_readers` (245) and `_story_maps` (261) build it again in the same read. The reading should hold one. [3]
- graph_reading.py:34-36, 448-453 `_MEMBER_CALL`, `_FUNCTION_CALL`, `_classes_built_for` — put-logic-on-the-owning-resource — Stories reads calls and receiver classes out of TypeScript and Python step bodies with its own regexes (`x = new Class(`), while reading code is the work of `cdd_guidance/practices/source_code` and Clean Engineering's reading, which resolve calls and receivers themselves (clean_engineering/reading/code_file.py:1371-1374). Two readers of one language answer differently. [2]
- graph_reading.py:50-51 — limit-comments — an orphan comment ("A story map's epic is recorded as an Epic, or as a SubEpic … calls every epic an Epic") describes no line: the constant it once sat on moved to story_tree.py:18 (`EPIC_TYPES`). [4]

### cdd_guidance/practices/stories/model/modelled_areas.py

- modelled_areas.py:47-50 `ExampleObservations.examples` — eliminate-duplication — a cached wrapper of `self.tree.examples()` written again word for word at graph_reading.py:377-380 (`StoryLinks.examples`) and as `TermLinks._examples_by_file` (term_links.py:118-121); `StoryTree` could keep the read once. [2] (still open from round 1)
- modelled_areas.py:82 `_of_story_file` — hide-inner-details — rebuilds the graph's node id format by hand (`f"stories:Example:{step.source.file}:{example.name}"`) to tell which example is the step's own; a change to how the graph forms ids breaks this silently. The node's `source.file` already says it. [1]
- modelled_areas.py:31 `_is_markdown` — prefer-class-operations — a module function used only by `ExampleObservations._names` (69). [3]

### cdd_guidance/practices/stories/model/name_facts.py

- name_facts.py:54-88 `opening_of`, `_class_of`, `_names_generic_handler`, `_file_name_facts`, `_camel_case` — prefer-class-operations — a file of functions over a name or path whose only caller is `NameFacts.__init__` (102-104; `opening_of` is public and has no other caller, grep); they are `NameFacts`' own work. [3] (still open from round 1)
- name_facts.py:104, 122 `opens_with_generic_handler`, `judge(generic_handler=…)` — hold-state-on-the-object-not-in-parameters — `NameFacts` computes `opens_with_generic_handler` itself, then the node hands it straight back as a parameter (story_map.py:160 `facts.judge(generic_handler=facts.opens_with_generic_handler)`, 1015 the same); two fields hold one fact. [3]
- name_facts.py:120 `"error"` — provide-meaningful-context — the value of `child_band` that marks a count outside its band is a bare literal here and again in rules/story_map.py:44 (`if severity != "error"`). [4]

### cdd_guidance/practices/stories/model/opened_story_map.py

- opened_story_map.py:46 `session.graph.practices.of(story_map.practice_kind)` — eliminate-duplication — the session's Stories practice is still found twice for one open: `StoryMap.load` finds it (story_map.py:1333) and constructs `OpenedStoryMap(model, path, session)` (1335), which finds it again. [3] (still open from round 1)
- opened_story_map.py:150-168 `UnopenedStoryMap` — class-not-property-instance-or-subtype — still has no `fidelity`, so `StoryMap.formats` (story_map.py:1362, `self.opened.fidelity.session_output`) raises `AttributeError` on a map opened from no file; the two classes share no base stating what "opened" answers. [3] (still open from round 1)
- opened_story_map.py:61 `fidelity` — errors-out-of-existence — `next(...)` with no default: a file no fidelity declares ends in a bare `StopIteration` from a property (and `refusal` at 78 calls it), not a named failure that says which file. [4]
- opened_story_map.py:110-118 `acceptance_tests_of`, `_acceptance_tests` — hold-state-on-the-object-not-in-parameters — `Stories.story_tests` turns each story test's stories into name strings (project_story_files.py:53) and this class matches the story in hand by `story.name in names`; the stories were objects and are looked up again by name. [3]

### cdd_guidance/practices/stories/model/project_story_files.py

- project_story_files.py:36, 167, 214 `formats`, `opened`, `reader_of` — use-typed-signatures — the constructor's `formats` has no type, and `opened` and `reader_of` (both public) have no return type; `opened` answers either a merged map or a format's `opened_from` result. [4] (still open from round 1)
- project_story_files.py:81-82 `adapter("json")`, `adapter("markdown")` — hold-state-on-the-object-not-in-parameters — formats are still looked up by name string where one known class is meant, and `code_readers` (44) iterates format names to look each adapter up again; a renamed format breaks at run time only. [3] (still open from round 1)
- project_story_files.py:190 `_code_map` — hold-state-on-the-object-not-in-parameters — `type(reader)(tests_root=STORY_TESTS_FOLDER)` builds a second adapter per language, dropping the settings the practice's adapter was made with, as graph_reading.py:233 does. [3] (still open from round 1)
- project_story_files.py:46-54 `story_tests` — use-typed-signatures — still returns `dict[str, list[str]]`, file path to story names, which opened_story_map.py:113 reads back by name. [3] (still open from round 1)
- project_story_files.py:106-139, 195-205 `_take_stories_only_code_holds`, `_epic_along`, `_epics_above`, `_merge_epics` — put-logic-on-the-owning-resource — finding or making an epic by name under a map, walking up a story's epics, and merging two maps' epics are a story map's and an epic's own work (`StoryMap.descendants.stories_by_name` is used at 112); here they reach into `holder.epics` and `epic.stories` lists from outside. [3]
- project_story_files.py:65 `os.path.relpath(path, self.project).replace("\\", "/")` — eliminate-duplication — the same "path from the project" the file computes with `path_from` at 53, 155 and 211; graph_reading.py:252 writes the relpath form again. [2]
- project_story_files.py:102, 114 `_take_story_test`, `_story_map_of_code_unheard` — eliminate-duplication — `story_map_of` reads and parses every story test once (`_read_story_test`, 102) and then reads and parses them all again through `_code_map` (114, 189-192) to find the stories the map lacks; one read could answer both. [2]
- project_story_files.py:171 ``(``read_files``)`` — no-legacy-api-after-refactor — the docstring of `opened` sends readers to `read_files`, which no longer exists anywhere in the code (grep finds only this line and a note in harness/.context/editor-apps). [4]

### cdd_guidance/practices/stories/model/realization_links.py

- realization_links.py:99, 102 `operation.get_fact("owner")` — low-coupling — reads the Clean Engineering / DDD reading's `owner` fact by its string name to decide which class declares an operation; no card offers that fact as a term. [1]
- realization_links.py:23-25 `REALIZATION_REACH_FACT`, `REALIZATION_REACHES_*` — use-typed-signatures — a second closed set of outcome strings beside `CALLS_REACH_*` (graph_reading.py:46-49), both read by the same rule `CodeStepsInvokeCode` (rules/acceptance_tests.py:175-186). [4]
- realization_links.py:43 `ModelHeadings(stories_root, model)` — put-logic-on-the-owning-resource — a `ModelHeadings` is built per model here and again for the DDD model in `TermLinks` (term_links.py:96), so in one `read_working_copy` (graph_reading.py:162, 165) the same model documents are read and the same node index built twice. [3]

### cdd_guidance/practices/stories/model/screen_spec_file.py

- screen_spec_file.py:32 `_SEED` — provide-meaningful-context — a Given is still any statement calling a function whose name starts with `write`, `seed` or `reset`, a test-library convention stated only as this regex. [4] (still open from round 1)
- screen_spec_file.py:99 `is_screen_spec` — prefer-class-operations — a module function deciding what a screen spec's text looks like, with one caller (script_story_map.py:80); it is `ScreenSpecFile`'s own knowledge, beside `_DESCRIBE`. [3]

### cdd_guidance/practices/stories/model/story_channel.feature.py

- story_channel.feature.py:1-6 — no-module-per-class — still a 534-line mamba spec in the production package under a name no tier collects; `scripts/test.ps1` no longer names it at all (round 1 cited test.ps1:365), its docstring command names `practices/stories/model/...`, which does not exist, and only the story map (`.context/story-map.md:2398`) mentions it, so nothing runs it while the graph judges it as production code. [1] (still open from round 1)

### cdd_guidance/practices/stories/model/story_map_files.py

- story_map_files.py:16, 22, 46, 53 `source_at`, `path_from`, `is_story_map_file`, `preferred_maps` — prefer-class-operations — still four module functions beside `StoryMapFiles`; `is_story_map_file` and `preferred_maps` are what `StoryMapFiles` knows. [3] (still open from round 1)
- story_map_files.py:128 `scenario_files_below` — keep-operations-small-focused — still one 260-character comprehension with four nested clauses and a one-element `for kind in [...]` used as an assignment. [3] (still open from round 1)
- story_map_files.py:32 `CONTEXT_FOLDER = ".context"` — eliminate-duplication — redefines `harness/installation/context_config.py:9` `CONTEXT_FOLDER`, which the Stories card names as its dependency on `harness/installation`; harness/guidance/declared_outputs.py:22, ddd/reading/graph_reading.py:72 and ux/model/graph_reading.py:38 each keep another copy. [2]
- story_map_files.py:64, 172-174 `_SCENARIO_FOLDERS`, `_SCENARIO_FOLDERS[:1]`, `[1:]` — provide-meaningful-context — one tuple holds two folders that mean two different kinds of scenario file, told apart by slicing it by position; each needs its own name. [4]

### cdd_guidance/practices/stories/model/story_tree.py

- story_tree.py:41-42 `of_graph` — prefer-instance-operations — a `@staticmethod` that is not a creation factory (`of_graph` is not `from_*`); it finds the practice through the class attribute `StoryNode.practice_class` and a function-level import (44). [3]
- story_tree.py:151-152 `key_of` — prefer-instance-operations — a `@staticmethod` called as `StoryTree.key_of(...)` from five places (story_tree.py:205, ux/model/story_link.py:50, 75, ux/model/graph_reading.py:367, claude_design/story_canvas.py:334), with its walk up the tree done by module functions instead of the instance's `_above`. [3]
- story_tree.py:256-279 `_story_name`, `_ancestor`, `_is_under`, `_parent` — eliminate-duplication — module functions that walk up a node's parents a second way (through `node.parent`, then edges) beside `StoryTree._above` (177-181) and `area_of` (113-121), which walk the graph's edges; two walks answer "the story above this node". [2]
- story_tree.py:246-253 `WrittenStoryNodes._nodes_by_file` — eliminate-duplication — word for word the body of `ModelHeadings._nodes_by_file` (term_links.py:77-85), only the reading differs; graph_reading.py:132-136 and 391-394 walk the same nodes for their files too. [2]
- story_tree.py:223 `text = key.split(KEY_SEPARATOR)[-1]` — hold-state-on-the-object-not-in-parameters — a key built from a node by `key_of` is handed back as a string and parsed apart to find the step's text again; ux/model/graph_reading.py:367 splits it the same way. [3]

### cdd_guidance/practices/stories/model/term_links.py

- No findings.

### cdd_guidance/practices/stories/rules/__init__.py

- __init__.py:67 `BY_SLUG` — eliminate-duplication — the same slug index `{rule.slug: rule for rule in RULES}` is written in 12 rules packages (grep), and is read only by spec support (rules/rule_examples.py:20, template_checks.py:131 through `importlib`); the practice already holds its rules (stories.py:102), which could answer a rule by slug once for every practice. [2]

### cdd_guidance/practices/stories/rules/acceptance_tests.py

- acceptance_tests.py:124-127 `_fixture_path` — put-logic-on-the-owning-resource — the rule still recomputes which file an example comes from with `example_source_file` and the node's saved `imported_modules`, which the recording already computes (`StorySource.example_source`, story_recording.py:147-148) and could save as a fact. [3] (still open from round 1)
- acceptance_tests.py:154-157 `ExamplesExportDataNotRepository.check` — put-logic-on-the-owning-resource — judges `node.source.file`, the story test, where the sibling rule judges the file the example comes from (`_fixture_path`, 124); two rules give two answers to "which file is this example's", and templates_and_rules_heavy_spec.py:57-61 records both rules' example pairs as not holding. [2]
- acceptance_tests.py:91-96 `_EXAMPLES_FILE_ENDINGS` — eliminate-duplication — what names an examples file is written here as three endings and again in graph_reading.py:41 as `_EXAMPLES_MODULE_FILE = re.compile(r"examples\.\w+$")` (and 43 for the module form); the two can disagree on a file. [2]
- acceptance_tests.py:98 `ACCEPTANCE_TESTS_FIDELITY = "acceptance_tests"` — eliminate-duplication — the fidelity's name is a constant here but a literal where it is recorded (graph_reading.py:181, with `"scenarios"` and `"story_map"` at 176, 181); the fidelity objects the practice holds are not used for either. [4]

### cdd_guidance/practices/stories/rules/rule_examples.py

- rule_examples.py:93 `FILE_PAIRS` — seam-names-current-code — the Stories card (stories/.context/module-context.md, second paragraph) says the small story maps are in `MARKDOWN_PAIRS`; no such name exists, the dict is `FILE_PAIRS`. [4]

### cdd_guidance/practices/stories/rules/scenarios.py

- scenarios.py:101-103, 212, 224, 269, 334 — eliminate-duplication — five rules still open with the same gate ("its keyword is X or empty, or its node type is X"), once as two nested `if`s (101-103); `StepRule.is_a` (58) holds only half of it. [2] (still open from round 1)
- scenarios.py:39, 165, 194, 306-316 `_OWNED_PART_TYPES`, `_DOMAIN_CLASS_TYPES`, `"Aggregate"`, edges `"root"`, `"owns"` — low-coupling — two rules still reach through `context.practice.reading.domain_model` into DDD's graph by DDD node-type and edge strings written in a Stories rule file. [1] (still open from round 1)
- scenarios.py:125, 258 `node.facts.get(...)` — use-consistent-naming — still read `is_outline` and `evidence` through `node.facts.get` where every other rule uses `node.get_fact`. [4] (still open from round 1)
- scenarios.py:50-56 `StepRule.text`, `StepRule.phase` — eliminate-duplication — the same reads as `StoryTree.step_text` and `step_phase` (story_tree.py:133-139), and they already differ: the tree falls back to the step's name when it has no `text` fact, the rule answers empty. [2]
- scenarios.py:400, 412 — eliminate-duplication — "looks like an identifier" (`text.isidentifier() or (text.replace("_", "").isalnum() and " " not in text)`) is written in `PlainEnglishGwtSteps` and again in `GwtStepsTraceToDomainOperations`. [2]
- scenarios.py:285-297 `_earlier_steps` — eliminate-duplication — finds a step's scenario by scanning every `steps` edge of the graph (`context.edges("steps")`), where `StoryTree.scenario_of` (story_tree.py:99-101), already used two lines later, answers it. [2]
- scenarios.py:149 `ExamplesTraceDomainModel.domain_concepts` — make-module-only-operations-private — public, but its only callers are its own class (147) and stories_rules_spec.py:103. [1]

### cdd_guidance/practices/stories/rules/story_map.py

- story_map.py:15-18 `_VERB_OPENINGS`, `_GENERIC_VERB` — use-typed-signatures — the classes of a name's opening word are a closed set written as strings in two files (`"verb"`, `"unlisted"`, `"generic-verb"` here; name_facts.py:46-50 and 68-70 where they are made); a renamed label passes every rule silently. [4]
- story_map.py:61-63 `StoryScenariosAtMostSeven.check` — eliminate-duplication — the story's scenario count is kept as two facts, `scenario_count` and `child_count` with `child_label == "scenarios"` (both set at story_map.py:1012-1014), and the rule reads one and falls back on the other. [2]
- story_map.py:53 `StoryScenariosAtMostSeven` — use-intention-revealing-names — the class names the number seven, while the module card says the number is held once on the model (`MOST_SCENARIOS`, read at 67) so a change is one edit; the class name goes wrong on that edit. [4]

### cdd_guidance/practices/stories/templates/py/acceptance_tests.py

- No findings.

### cdd_guidance/practices/stories/templates/py/scenarios.py

- scenarios.py:91, 112 `artifacts-mirror-story-hierarchy`, `then-and-chaining` — no-legacy-api-after-refactor — the template cites two rule names stories.md no longer has (the chaining rule is `and-chaining`, rules/__init__.py:51; grep finds `then-and-chaining` only in stories-guidance-assessment.md and `artifacts-mirror-story-hierarchy` only in a fixture), so an author is sent to rules that are gone. [4]

### cdd_guidance/practices/stories/templates/ts/acceptance-tests.ts

- No findings.

### cdd_guidance/practices/stories/templates/ts/scenarios.ts

- scenarios.ts:4, 29 `artifacts-mirror-story-hierarchy`, `then-and-chaining` — no-legacy-api-after-refactor — the same two removed rule names as the Python template (py/scenarios.py:91, 112). [4]

### cdd_guidance/practices/template_checks.py

- template_checks.py:66-68 `TemplateCheck.checked` — delete-unused-operations — no caller anywhere (grep `\.checked()` finds none; templates_and_rules_heavy_spec.py uses `findings`, `unread`, `unfilled_markers`). [3]
- template_checks.py:129-132 `RuleExamples(practice_key: str)` — hold-state-on-the-object-not-in-parameters — takes the practice's key and imports `cdd_guidance.practices.{key}.rules` by a built string, while its caller holds the practice itself (templates_and_rules_heavy_spec.py:71-72 builds `TemplateCheck(self.practice)`, 86 `RuleExamples(self.key)`); the practice should answer its rules and pairs. [3]
- template_checks.py:42, 124 `TemplateCheck`, `RuleExamples` — delete-unused-classes — spec support kept under a production name in the production package: the only caller is templates_and_rules_heavy_spec.py:72, 86, and a call from a spec is no use under the rule, so the graph judges both as unused production classes; name or place it as spec support, as the Stories, BDD and Clean Engineering `rules/rule_examples.py` files are meant to be. [1]


### cdd_guidance/practices/stories/model/diagram_story_map.py

- diagram_story_map.py:53-93 `DiagramStoryNode.width` / `height` / `y` / `x` — shape-classes-around-resources — one mixin answers for a story, an epic and an increment by testing `isinstance(self, Story)` and `isinstance(self, Epic)` in every property, although `DiagramStory` (:158) and `DiagramEpic` (:171) exist to hold that difference; `LaidOutStory` (:198-207) and `LaidOutEpic` (:214-228) override it for every drawn format, so the base grid is reached only by the UX Claude Design canvas (`ux/model/claude_design/story_canvas.py:49`, `:89`). [3] (still open from round 1)
- diagram_story_map.py:44, :51 `DiagramStoryNode._story_line_y` / `_sub_epic_bar_y` — use-explicit-dependencies — a node on no map builds a throwaway `DiagramStoryMap()` to answer a default line; `DrawIOStoryMap.sub_epic_top` and `story_floor` (drawio/nodes.py:368-374) differ from the base, so a detached draw.io node gets the base answer with no error. [3] (still open from round 1)
- diagram_story_map.py:104 `DiagramStoryCell` — use-intention-revealing-names — "cell" is draw.io's word for what is also a Miro rect (`miro/nodes.py:182`) and a whiteboard shape (`whiteboard/nodes.py:216`); its `role` and `kind` are strings (`"epic"`, `"subepic"`, `"story"`, `"actor"`) compared by `place_cells` (:250, :254, :264-265) where the model has `StoryType` and `Epic`. [4] (still open from round 1)
- diagram_story_map.py:406-414 `ThinSliceLayout._by_column` — hold-state-on-the-object-not-in-parameters — finds each increment's story by comparing `held.name == story.name` over every sub-epic's stories, although a copied map's increments already deliver the copy's own story objects (`story_copies.py:26-30`); two stories of one name under different sub-epics land in the same column. [3]
- diagram_story_map.py:420 `ThinSliceLayout.epic_headers` — use-typed-signatures — answers `List[tuple]` of (epic, x, width) unpacked by position at :436 (`surface.epic_header(*next(headers))`), beside the named `ThinSliceColumn` (:376) and `ThinSliceLane` (:386) that replaced the other tuples; `_by_column` takes `pairs: List[tuple]` (:406). [3]
- diagram_story_map.py:447-454 `ThinSliceSurface.epic_header(epic, x, width)` / `lane(lane, layout)` — hold-state-on-the-object-not-in-parameters — the surface is handed layout state it holds or ignores: `_ThinSliceDrawing` drops `x` and `width` and asks its own places (`drawio/nodes.py:604-607`), drops `layout` and counts lanes itself to find the lane's index (`drawio/nodes.py:614-617`); `_ThinSliceBoard` holds `self.layout` (`whiteboard/nodes.py:181`) yet reads the parameter (`:201`, `:205`). [3]
- diagram_story_map.py:381 `ThinSliceColumn.sub` — use-intention-revealing-names — an abbreviation for the sub-epic, read as `column.sub` across three files (`drawio/nodes.py:538`, `:610`, `whiteboard/nodes.py:193`). [4]

### cdd_guidance/practices/stories/model/drawio/__init__.py

- __init__.py:1 `DrawIOStoryMap` — no-legacy-api-after-refactor — a second import path for the class nobody uses: `stories.py:26` names `model.drawio.nodes`, and every importer, specs included, imports from `.nodes` (repository grep finds no `from ...stories.model.drawio import`). Two entry points for one class. [1]

### cdd_guidance/practices/stories/model/drawio/nodes.py

- nodes.py:403-413 `DrawIOStoryMap.parse` — use-consistent-naming — builds and answers a hard-coded `DrawIOStoryMap()`, leaving `self` empty, where `JsonStoryMap.parse` (`json/nodes.py:296-306`) and `SketchStoryMap.parse` (`sketch/sketch_story_map.py:251-257`) fill `self` and return it; Miro (`miro/nodes.py:288`) and the whiteboard (`whiteboard/nodes.py:141`) also answer a hard-coded new map, and markdown a `type(adapter)()` (`markdown/map_reading.py:67`). One adapter operation, two contracts, and a subclass of the draw.io map loses its type on parse. [2] (still open from round 1)
- nodes.py:438 `DrawIOStoryMap.load_thin_slice`, :447 `_lanes_in` — delete-unused-operations — called only by specs (`drawio/drawio_story_map_spec.py:311`, `thin_slice_render_spec.py:135`, `:163`); `StoriesFormats` draws a thin slice to a drawing (`stories_formats.py:104-106`) but nothing in production reads a drawn thin slice back, so lanes a person edits on `thin-slice.drawio` are never read. [1]
- nodes.py:168-169 `DrawIOEpic._estimate_cell` — eliminate-duplication — writes the `* {estimate}` label inline, which `EpicColumns.estimate_label` (`diagram_story_map.py:332-339`) already writes and `_epic_cells` (:189) calls eight lines further down. [2]
- nodes.py:152-164, :181-196 `DrawIOEpic.cells` / `_epic_cells` — eliminate-duplication — the same sequence twice (the bar's vertex linked to the node, each story's cells, each child's cells, an estimate cell), differing only in the box and which estimate cell is drawn. [2]
- nodes.py:312-336 `DrawIOStoryMap.Vertex` — shape-classes-around-resources — a nested data holder changed from outside by three objects: `linked` sets `node`, `take_links` sets `link`/`entry`/`code_link`, and `_KeptPlaces.place` (:292-297) overwrites `x`, `y`, `width`, `height` with the raw geometry strings of the kept drawing. The vertex owns its box but not the rule for keeping it. [3] (still open from round 1)
- nodes.py:326 `DrawIOStoryMap.Vertex.make` — prefer-instance-operations — a `@classmethod` whose name is not one of the factory names the rule allows (`create`, `from_*`, `load`, …), taking seven untyped parameters; it is called at :98, :103, :155, :175, :182, :190, :607, :612, :619, :620, :622. [3]
- nodes.py:262-272 `_KeptPlaces.from_text` — errors-out-of-existence — catches `UnreadableDrawio` and answers no places, so a story map or thin slice drawing that does not read is treated as no drawing and the render (:383, :435) draws over it, losing the layout the person gave it without a word. [3]
- nodes.py:254-297 `_KeptPlaces` — eliminate-duplication — keeps each cell's raw geometry dict and converts it again (`box_of` :274-279 with `_measure` :247), where `DrawioCell.box` (`harness/drawio/drawio.py:116-121`) already answers a cell's box and Clean Engineering keeps places through `DrawioPage.positions` (`drawio_class_model.py:343`, `:444`). [2] (still open from round 1)
- nodes.py:207 `_PlacedCell.style` — delete-unused-operations — set from the cell's style text and never read: every reader of a style reads the harness cell's `style` (:206, :453), and no other file names `_PlacedCell`. [1]
- nodes.py:465-487 `_ThinSlicePlaces.cards` — hide-inner-details — a public `List[List[Tuple[str, Story, Box]]]` that `_ThinSliceDrawing.lane` unpacks by position (:621); `_named_cards` (:516-519) builds another positional tuple of three. [3]
- nodes.py:28 imports `StoryMapLinks` from `model/markdown/links.py` — high-cohesion — the draw.io adapter depends on the markdown adapter package for links that are draw.io's own: `code_link` (`markdown/links.py:108-124`) writes the draw.io editor attributes and `CODE_LINK = "hedietLinkedDataV1"` (`links.py:58`) lives in the markdown package. One format package imports another. [1] (still open from round 1)

### cdd_guidance/practices/stories/model/json/__init__.py

- __init__.py:1 `JsonStoryMap`, `JsonParseError` — no-legacy-api-after-refactor — a re-export nobody imports through: `stories.py:25` names `model.json.nodes`, and no file imports from the package. [1]

### cdd_guidance/practices/stories/model/json/nodes.py

- nodes.py:65 `_example_records`, :75 `_take_examples` — prefer-class-operations — module functions taking `Examples` first, called from five classes (:124, :133, :179, :191, :253, :266, :289, :304); the same four lines ("records = _example_records(...); if records: payload['examples'] = records") are repeated at :124-126, :179-181, :253-255 and :289-291. They are the examples' own `as_records()` and `take(record)`. [3] (still open from round 1)
- nodes.py:60 `type JsonDocument = object`, and every `as_record` / `from_record` on `Dict[str, Any]` — use-typed-signatures — public operations on seven classes pass untyped dictionaries, so a misspelt key (`"sequentialOrder"`) is found at run time; `JsonDocument = object` names a type that says nothing. [4] (still open from round 1)
- nodes.py:111 `JsonStep.all_from` — prefer-instance-operations — a `@classmethod` named outside the factory names the rule allows (`from_*` is allowed, `all_from` is not), called from `JsonBackground.from_record` (:132) and `JsonScenario.from_record` (:190). [3]

### cdd_guidance/practices/stories/model/markdown/__init__.py

- __init__.py:1 `MarkdownStoryMap`, `MarkdownParseError` — no-legacy-api-after-refactor — a re-export nobody imports through: `stories.py:24` and every importer (e.g. `project_story_files.py`, `fixtures/pack_orders_project.py`) name `model.markdown.nodes`. [1]

### cdd_guidance/practices/stories/model/markdown/links.py

- links.py:50 `heading_anchor` — eliminate-duplication — the same anchor rule as `harness/markdown/markdown.py:113` `heading_anchor` (links taken to their words, lower case, punctuation dropped, spaces as hyphens); only `_Anchors.next` (:68) uses the Stories copy. [2] (still open from round 1)
- links.py:21-27 `_LINK` / `unlink` — eliminate-duplication — "a link read as its words" is `link_words` in `harness/markdown/markdown.py:104-110` and `_LINK` again in `ux/model/whiteboard/nodes.py:37`; the Stories copy is imported by six files of this package. [2] (still open from round 1)
- links.py:126-136 `StoryMapLinks._heading_line` — keep-operations-single-responsibility — `code_link`, asked for every drawn vertex (`drawio/nodes.py:352`, `:397`), re-reads and re-scans the whole `story-map.md` to find one heading's line, although the class says its links are "made once, when the map is placed in the folder" (:76) and `_entries_of` (:148-159) already walks every heading in order. [3] (still open from round 1)

### cdd_guidance/practices/stories/model/markdown/map_reading.py

- map_reading.py:37 `is_outline`, :42 `has_map_structure`, :48 `read_map`, :54 `read_at`, :270 `described` — prefer-class-operations — five public module functions beside the reading classes; `is_outline` re-scans the same text three times in one `MarkdownStoryMap.parse` (`markdown/nodes.py:510` and twice through `_looks_like_scenario_document` :510, :514/:521) and twice more per render (`:460`, `:468`). A read text that knew its notation would hold the answer once. [3] (still open from round 1)
- map_reading.py:26-28 `_OUTLINE_EPIC_PATTERN`, `_OUTLINE_STORY_PATTERN`, `_OUTLINE_ESTIMATE_PATTERN` — eliminate-duplication — the outline notation (`(E) name`, `(S:kind) actor --> name`, `* estimate`) is parsed again by `sketch/sketch_story_map.py:32-34`, the actor split twice (`_actor_and_name` :356-361 here, `SketchStory.from_match` `sketch_story_map.py:168-174`), and the story heading written three times: `MarkdownStory.outline_lines` (`markdown/nodes.py:175-176`), `SketchStory.sketch_lines` (`sketch_story_map.py:201-203`) and `StoryMapLinks._entries_under` (`links.py:166-167`), which rebuilds it only to compute an anchor, so a change to the heading breaks every link silently. [2] (still open from round 1)

### cdd_guidance/practices/stories/model/markdown/markup.py

- markup.py:114 `step_prose`, :119 `step_line`, :124 `step_lines` — prefer-class-operations — module functions over a `Step`: `step_prose` switches on `isinstance(step, MarkdownStep)` and `step_lines` probes `getattr(step, "call_graph", None)` although every `Step` holds a `call_graph` (`story_map.py:572`). They are how a step writes itself in markdown. [3] (still open from round 1)
- markup.py:86 `MarkdownStep.markdown_line: Optional[tuple]` — hide-inner-details — a positional `(keyword, text, line)` tuple, read by index at :104-106, beside `ExampleRowLine` (:38), the named form of the same idea in the same file. [3] (still open from round 1)

### cdd_guidance/practices/stories/model/markdown/nodes.py

- nodes.py:443-490 `MarkdownStoryMap._map_text`, `_should_render_outline`, `_sub_tree_has_outline_signal`, `_is_discovery_story_map` — put-logic-on-the-owning-resource — `render` copies the map into `story_map` and then runs four methods of the adapter that take `story_map` (or one of its epics) as a parameter and never read `self`; they are that map's and that epic's own questions. [3] (still open from round 1)
- nodes.py:98 `_example_tables`, :112 `example_table_lines`, :261 `_outlined` — prefer-class-operations — module functions taking the examples or the node first; `_outlined(node, heading)` only forwards to `node.outline.written(node, heading)`, and `_example_tables` answers `List[tuple]` of (group, headers, cells) unpacked at :117. [3] (still open from round 1)
- nodes.py:60, :138 `MarkdownScenario.read_lines`, `MarkdownStory.read_lines` — hide-inner-details — public fields that `ScenarioFileReading` fills from outside (`scenario_file.py:201`, and `:208` makes the scenario's list its `container` and appends to it) and `_take_section` sets (:574). The markdown parts replaced the old `markdown_parts` tuples, but the reading still writes the node's storage directly. [3] (still open from round 1)
- nodes.py:93, :155, :279-280 `heading_written` — hide-inner-details — each node unpacks `read.said` by its own shape: `(name, is_outline)` for a scenario, a bare name for a story, `(level, name)` for an epic, each written by the reading (`scenario_file.py:201`, `scenario_parts.py:30`, `scenario_file.py:184`). [3] (still open from round 1)
- nodes.py:396 `MarkdownStoryMap._attach_markdown` — hold-state-on-the-object-not-in-parameters — the project is handed down `_read_at` → `_read_workspace` → `_attach_markdown` as `base`, and at the last step `ThinSlice.from_folder(root, self, root)` passes the map's folder as the project, so increments read with a folder name `thin-slice.md` from that folder (`thin_slice.py:110`, `story_map_files.py:22-27`), not from the project as `opened_from` does (:336). A rule hit on an increment then names a path a reader cannot open from the project. Read, not run. [3]

### cdd_guidance/practices/stories/model/markdown/read_lines.py

- read_lines.py:39, :72, :84, :131 `HeadingLine(node: Any, said: Any, …)`, `HeldLines(node: Any)`, `SectionSteps(held: Sequence[Any])`, `ReadScenarioDocument(holder: Any, …, story_class: type)` — use-typed-signatures — the public constructors of the round trip take `Any`; `said` carries three shapes (a name for a story, `(name, is_outline)` for a scenario, `(level, name)` for an epic heading) that only the reader of each knows. [4]
- read_lines.py:41, :73 `HeadingLine.node`, `HeldLines.node` — hide-inner-details — made with `None` or a section and set afterwards from outside by `MarkdownStoryMap` (`markdown/nodes.py:542`, `:573`, `:576`); a line written before that assignment calls `heading_written` on `None`. [3]
- read_lines.py:79-110 `SectionSteps` — shape-classes-around-resources — a writer keyed by `id(owner)` that counts each owner's step lines down (`_left`, `_pending`) to decide where pending steps are written; the step lines belong to their scenario or background, which could write its own. Moved here from `markdown/nodes.py` `_SectionLines`. [3] (still open from round 1)
- read_lines.py:120 `written_lines` — prefer-class-operations — a module function that builds a `SectionSteps` and writes the lines with it, called from three classes (`markdown/nodes.py:89`, `:149`, here :138); it is the lines' own operation. [3]

### cdd_guidance/practices/stories/model/markdown/scenario_file.py

- scenario_file.py:115-134 `ScenarioFileReading` — hide-inner-details — eighteen public mutable fields; after `read()` the caller picks through the working state (`document_lines`, `tree_heading`, `tree_heading_line`, `document_examples`, at `markdown/nodes.py:534-555`) and changes it (`reading.tree_heading.node = holder`, :542). The reading has no result object. [3] (still open from round 1)
- scenario_file.py:92, :115 `scenario_class: type` — hold-state-on-the-object-not-in-parameters — the class to build is handed from `MarkdownStoryMap` (`markdown/nodes.py:390`, `:530`) through `ScenarioFiles.sections` into every `ScenarioFileReading`, always `MarkdownScenario`. [3] (still open from round 1)
- scenario_file.py:38 `_PHASES`, :262-278 `_take_step` — eliminate-duplication — `_PHASES` is `StepType(word)` written as a table (json reads it that way, `json/nodes.py:103`), and the same table is in `sketch/sketch_story_map.py:37`, `code_story_map.py:64` and `python/shared_story_file.py:32`; `_take_step` builds the And/But step onto the step before by hand where `Step.continue_with` (`story_map.py:657-663`) does it and `SketchStep.chain` calls it, and the continuation words are listed again at :267, `sketch_story_map.py:38` and `story_map.py:669`. [2] (still open from round 1)
- scenario_file.py:35 `_ITALIC_STEP` — eliminate-duplication — the `*Given* text` step line is matched by `STEP_LINE` in `markup.py:19`, by this pattern, and a third way in `MarkdownStoryMap._looks_like_scenario_document` (`markdown/nodes.py:524`, `startswith(("*Given*", "*When*", "*Then*"))`, which misses an `*And*` line). [2]

### cdd_guidance/practices/stories/model/markdown/scenario_parts.py

- scenario_parts.py:162 `BackgroundReading.heading(kind, name, in_scenario, read_at)` — limit-operation-parameters — four parameters, one a boolean the caller derives from its own state (`scenario_file.py:209`, `:233`); `ExamplesTable.heading(kind, level, title)` (:94) is the same heading cut into other pieces beside it. A heading (kind, level, title, line) is one unnamed concept passed as loose values. [3] (still open from round 1)
- scenario_parts.py:94, :162 `kind: str` — provide-meaningful-context — the heading kinds (`"story"`, `"scenario"`, `"tree"`, `"story-background"`, `"background"`, `"examples"`, `"heading"`) are literals declared in `scenario_file.py:47-55` and compared by string in three classes (`scenario_file.py:179-188`, `:228`, here :98-105, :167-176). [4]
- scenario_parts.py:34 `StorySection.scenarios: list`, :108 `ExamplesTable.row -> Optional[dict]`, :126 `_fields -> dict` — use-typed-signatures — untyped list and dicts on public members read by `MarkdownStory.load_scenarios` (`markdown/nodes.py:224`) and `ScenarioFileReading._read_text` and `_record_example` (`scenario_file.py:248-249`, `:280-290`). [4]

### cdd_guidance/practices/stories/model/markdown/thin_slice.py

- thin_slice.py:37, :40 `IncrementLines.said`, `bullets: List[tuple]` — hide-inner-details — positional `(name, number)` and `(raw, story, name)` tuples, appended from outside by `_ThinSliceReading._read_bullet` (:201) and unpacked by index at :64, :77-78; `above`, `described` and `below` are public lists the reading appends to (:188-193). [3] (still open from round 1)
- thin_slice.py:51 `MarkdownIncrement.__init__(*args, **kwargs)` — use-typed-signatures — the constructor hides the increment's parameters; callers pass them positionally (:170). [4]

### cdd_guidance/practices/stories/model/miro/__init__.py

- __init__.py:1 `MiroStoryMap`, `MiroParseError` — no-legacy-api-after-refactor — a re-export nobody imports through: `stories.py:27` names `model.miro.nodes`. [1]

### cdd_guidance/practices/stories/model/miro/nodes.py

- nodes.py:292-313 `_svg_root`, `_cards_in_order`, `_local_name`, `_foreign_object` — shape-classes-around-resources — four methods of the story map that never read the map; they read the SVG document, the Miro counterpart of the harness draw.io file the draw.io adapter uses. [3] (still open from round 1)
- nodes.py:74 `MiroIncrement.table_row(column_count, story_column)` — hold-state-on-the-object-not-in-parameters — the increment is handed the table's width and a name-to-column dictionary its owner built (:219-223), and finds its own stories' columns by `story.name`. [3] (still open from round 1)
- nodes.py:216-234 `MiroStoryMap.save_thin_slice`, `_thin_slice_columns` — eliminate-duplication — Miro lays out its thin slice by a column rule of its own (a column for an epic's own stories, then each leaf sub-epic), while draw.io (`drawio/nodes.py:591`) and the whiteboard (`whiteboard/nodes.py:181`) share `ThinSliceLayout` (`diagram_story_map.py:393`), whose column is each sub-epic or an epic with none. [2] (still open from round 1)
- nodes.py:251 `MiroStoryMap.load_thin_slice` — delete-unused-operations — called only by specs (`miro_story_map_spec.py:320`, `:343`); nothing in production reads a Miro thin slice. [1]
- nodes.py:186 `_MiroCell.ROLES` — eliminate-duplication — the same tuple as `_BoardCell.ROLES` (`whiteboard/nodes.py:220`); both name the roles `DiagramStoryMap.place_cells` reads (`diagram_story_map.py:250-265`), which owns that vocabulary. [2]
- nodes.py:3 module docstring — limit-comments — says "load reads a canvas-composer SVG"; the class has no `load` (reading is `parse`, :282). [4]

### cdd_guidance/practices/stories/model/sketch/__init__.py

- __init__.py:1-3 `SketchStoryMap` — no-legacy-api-after-refactor — a re-export with `__all__` nobody imports through: `stories.py:15` and `:23` name `model.sketch.sketch_story_map`. [1]

### cdd_guidance/practices/stories/model/sketch/sketch_story_map.py

- sketch_story_map.py:41 `_epic_name`, :119 `_read_steps` — prefer-class-operations — module functions; `_read_steps(lines, take)` hands each step to a callback (`SketchScenario.take_step` :150, `SketchStory._take_step` :181) instead of being the owner's own reading. [3] (still open from round 1)
- sketch_story_map.py:217-232 `SketchEpic.read_lines`, :259-272 `SketchStoryMap.read_lines` — eliminate-duplication — the same "story line or epic line" branch twice: match `_STORY` against `_epic_name(entry.text)`, make a `SketchStory.from_match` and read its nested lines, else make a `SketchEpic` and read its nested lines. [2] (still open from round 1)
- sketch_story_map.py:103, :157, :200, :204, :235, :238 `"    "` — provide-meaningful-context — the indent of one level is written as a literal six times beside `_NESTING_INDENT = 4` (:29), which the reading uses (:61, :255). [4]

### cdd_guidance/practices/stories/model/whiteboard/__init__.py

- __init__.py:1 `WhiteboardStoryMap` — no-legacy-api-after-refactor — a re-export (with `# noqa: F401`) nobody imports through: `stories.py:28` and the specs name `model.whiteboard.nodes`. [1]

### cdd_guidance/practices/stories/model/whiteboard/nodes.py

- nodes.py:211-213 `_ThinSliceBoard._map_story` — hold-state-on-the-object-not-in-parameters — looks each card's story up by name across the whole map (`held.name == story.name`), although the copied map's increments already deliver its own `WhiteboardStory` objects (`story_copies.py:26-30`); a story of a repeated name gets the first one's card, and `lane` drops silently any story that is not a `WhiteboardStory` (:207). [3] (still open from round 1)
- nodes.py:76, :81, :111, :190, :195 — provide-meaningful-context — the card and bar looks (`"yellow"`, `"purple"`, `"green"`, `kind="rounded"`, `size="body"`/`"small"`) are written out at five call sites; the thin slice's headers (:189-195) repeat `WhiteboardEpic.bar` (:107-111) instead of asking the epic for its bar. [3] (still open from round 1)
- nodes.py:138-143 `WhiteboardStoryMap.take_board` — use-consistent-naming — answers a hard-coded new `WhiteboardStoryMap()`, while `WhiteboardBoundedContextMap.take_board` (`ddd/model/whiteboard/whiteboard_bounded_context_map.py:84-90`) fills itself. One operation name, two contracts. [2] (still open from round 1)
- nodes.py:151 `WhiteboardStoryMap.load_thin_slice` — delete-unused-operations — called only by specs (`whiteboard_story_map_spec.py:84`, `thin_slice_render_spec.py:146`); nothing in production reads a thin-slice board back. [1]
- nodes.py:66, :75 `board_box` / `board_elements` — use-consistent-naming — "the elements this node draws" is `board_elements` here, `cells` on draw.io (`drawio/nodes.py:93`, `:152`) and `shapes` on Miro (`miro/nodes.py:95`, `:147`), for three subclasses of the same `LaidOutStory` and `LaidOutEpic`. [2]


### cdd_guidance/practices/stories/app/story-map-routes.ts

- story-map-routes.ts:16 — seam-names-current-code — the comment says the routes are mounted "under STORY_MAP_API", a constant private to `story-map/story-map-api.ts:4`; the server that mounts them (`space/kanban/app/packages/session-board/app.ts:20-21`) cannot name it, and `STORY_MAP_PAGE`'s own comment (`story-map-page.ts:2`) says the Python that registers the app reads it, while `space/kanban/board_app.py:24`, `space/kanban/editor_apps_examples.py:34` and `space/kanban/story_ui_page_heavy_spec.py:20` each write `"/story-map"` again. [4] (still open from round 1)
- story-map-routes.ts:11, :18 `storyMapRoutes` — use-intention-revealing-names — the generated `storyMapRoutes` (the story map object's own routes) is imported under the alias `storyMapObjectRoutes` so that this file can export a different list (every route the editor needs) under the same name; one name, two lists, told apart only by an import alias. [4]

### cdd_guidance/practices/stories/app/story-map/story-map-client.ts

- story-map-client.ts:62-73 `reorder(siblings, order)` — put-logic-on-the-owning-resource — the client is handed the whole new order as id strings and works out which node moved by comparing joined id lists (:65-66), then, for a drop at the end, moves every passed sibling before the moved one, one server call each (:71); the views already know the dragged node and the node it was dropped before (`DropEdge.beforeId`, `story-map-views.tsx:194`, `commitDropFromEdge` :679-694). [3] (still open from round 1)
- story-map-client.ts:52, :56 `addEpic`, `addIncrement` — eliminate-duplication — both write `this.newX(name).then(map => map?.toJSON() ?? null)` to turn the generated client's answer back into data so `answerTo` can turn it into a client again; the round trip is written per call instead of once in `answerTo`. [2]
- story-map-client.ts:86-89 `chooseFormat` — hold-state-on-the-object-not-in-parameters — builds a new `FidelitySessionOutputClientGenerated` from `this.formats` on every toggle and then re-reads the whole map with `show()`; the formats object is a part of the map's answer that the client could hold like its nodes (`nodes()`, :76-82). [3]

### cdd_guidance/practices/stories/app/story-map/story-map-nodes.ts

- story-map-nodes.ts:35 `addedBefore(map, addition, created, before, moved)` — put-logic-on-the-owning-resource — "add this node before that one" is done in the page as add-last, read the new node's address as the last child of the answer (`epicIn` :42, `.at(-1)` at :119, :125), then a second call to move it; two server calls and a guess at which node is new, because the story model's `new_epic` / `new_story` take a name only (`stories/model/story_map.py:1138-1148`). Moved here from `MapEditing.addThenPlace` in the views. [3] (still open from round 1)
- story-map-nodes.ts:35 `addedBefore` — limit-operation-parameters — five parameters, two of them callbacks that each caller writes out in full (:63, :119, :125); it is also a module function taking the map as its first argument (prefer-class-operations), which belongs on `StoryMapClient` or `StoryNodeOnPage`. [3]
- story-map-nodes.ts:103-106 `EpicOnPage.of` — hide-inner-details — an epic's own stories are shown as a made-up row (an `EpicOnPage` whose id is the epic's id), so the views must tell the real sub-epic from the fake one by comparing ids (`story-map-views.tsx:877`, `:965`); and each own story is made twice, once for the row (:104) and once for the epic's `stories` (:106), so two `StoryOnPage` objects stand for one story. Moved here from `EpicViewModel.of`. [4] (still open from round 1)
- story-map-nodes.ts:105 with :139 `storiesUnder` — prefer-class-operations — a module function that flattens the stories of every epic nested under a sub-epic into its row, so a third-level epic is never drawn as a row and its stories appear under the row of its parent; the flattening is a view decision written as a free function over `EpicData`. Moved here from `story-map-view-models.ts`. [3] (still open from round 1)
- story-map-nodes.ts:206-208 `ScenarioOnPage.newStep` — put-logic-on-the-owning-resource — the page decides that an And or But step is written as a Then (`keyword === 'and' || keyword === 'but' ? 'then'`), so an And typed under a Given is saved as a Then; the story model holds `ands` on a step (`story_map.py:566`) but `Scenario.new_step` (`story_map.py:851`) accepts only given, when or then, so the rule for where an And goes lives in neither place correctly. [4]
- story-map-nodes.ts:20 `STEP_KEYWORDS` — use-consistent-naming — the page's step vocabulary is `'given' | 'when' | 'then' | 'and' | 'but'`, the model's `StepType` is given/when/then with `ands` held under a step, and UX calls the same thing `kind` (`ux/model/nodes.py:27`) and `stepKind` (`ux/model/explorer_tree.py:67`); one idea, three shapes. [4]

### cdd_guidance/practices/stories/app/story-map/story-map-views.tsx

- story-map-views.tsx:362, :407, :451 `makeStoryDragHandlers`, `makeSubEpicDragHandlers`, `makeEpicDragHandlers` — eliminate-duplication — three functions of about forty lines whose bodies differ only in the kind string and list key; `makeEmptyParentDropZone` (:492) repeats the same `onDragOver` a fourth time and `makeDragHandlers` (:155) is a fifth, simpler drag implementation for increments, scenarios and steps. [2] (still open from round 1)
- story-map-views.tsx:368, :413, :497 `onMove` — limit-operation-parameters — the story, sub-epic and empty-parent handlers take six or seven positional parameters, and `onMove` is never read in any of the three bodies (the commit happens in `commitDropFromEdge`, :679); callers still build and pass it (:734, :889, :910, :987). [3]
- story-map-views.tsx:661-666 `moveInto` — errors-out-of-existence — a story or sub-epic dropped last in a row, or into an empty sub-epic or epic through `makeEmptyParentDropZone` (whose comment, :490-491, promises it "appends at the end"), finds no next sibling and does nothing, with no failure shown; the page answers the drop as done. The map's own `reorder` (`story-map-client.ts:62`) handles a drop at the end, so the two drop paths behave differently for the same gesture (eliminate-duplication as well). [3]
- story-map-views.tsx:612-1102 `StoryHierarchyView` — keep-operations-small-focused — one component of about 490 lines holds the drag state, the drop commit, the column layout, and the markup of four kinds of row; the callback props round 1 counted are gone, the size is not. [3] (still open from round 1)
- story-map-views.tsx:598, :616 `showScenarios` — errors-out-of-existence — the prop is taken and never read inside `StoryHierarchyView` (the comment at :1202 says scenarios show "regardless of Show Scenarios toggle"), so the toolbar's Show Scenarios button (:1659) lights up and changes nothing. [4]
- story-map-views.tsx:1406-1429 `StepEditor` — errors-out-of-existence — the keyword select (:1412-1419) only sets local state and `save` sends only `editText`; a keyword changed and left is never saved and reverts on the next read, with no message. The step's tools (`Step.edit_text`, `story_map.py:605`) offer no keyword change, so the page shows a control the model cannot honour. [4]
- story-map-views.tsx:1110, :1145, :1243, :1353 `NodeNameInput`, `IncrementLabel`, `StoryNameEditor`, `ScenarioPanel` name input — eliminate-duplication — four copies of rename-in-place (local name state, save when changed, Enter/Tab saves, Escape restores) with small differences in which keys stop propagation; `IncrementOnPage` and `ScenarioOnPage` extend `StoryNodeOnPage`, so `NodeNameInput` already serves them. [2]
- story-map-views.tsx:38 `StoryMapPageCalls`, :94 — shape-classes-around-resources — a holder of `api`, `failures` and an `editing` ref passed to two hooks that take it apart; `useStoryMapPage` builds a second `StoryMapApi` although `main.tsx:15` already built one inside `StoryMapFailures` for the same failures. [3] (still open from round 1)
- story-map-views.tsx:1561 `NEW_NAMES.subEpic = 'New SubEpic'` — use-consistent-naming — "SubEpic" (:893, :1561), "SUB-EPIC" (:947), `'sub-epic'` (:199) and `subEpics` are four spellings of one term, and the model has no sub-epic type at all (`Epic.is_sub_epic`, `story_map.py:1151`). [4] (still open from round 1)
- story-map-views.tsx:1636, :1639-1645 `StoryMapCanvasProps` — limit-operation-parameters — `StoryMapWorkspaceView` hands twenty-one separate props to `StoryMapCanvasView`, which spreads them again into the toolbar (:1696); the view state from `useStoryMapViewState` is one object taken apart and passed piece by piece. [3]
- story-map-views.tsx:531, :652-653, :792-793 — limit-comments — the column-layout comment names a `SubEpicModel` that exists nowhere in the app or its Python model; the doc comment for `renderStoryCard` sits above `rowsById` (:655) instead; the grid comment says increment rows start at `4 + 2*i` while `incLabelRow` is `5 + 2 * i` (:648). [4]
- story-map-views.tsx:1665 `expandDescendants('all-epics', …)` — use-intention-revealing-names — Expand All passes a made-up node id, `'all-epics'`, into the set of opened node ids so it can reuse the per-node operation. [4]

### cdd_guidance/practices/ux/model/__init__.py

- No findings.

### cdd_guidance/practices/ux/model/collections.py

- collections.py:13 `UxComponentCollection` beside `ModelChildren` — class-not-property-instance-or-subtype — screens, regions, controls and interactions are plain `ModelChildren` with `append_*` on the owner (`nodes.py:198, 246, 286`, `ux_map.py:251`); transitions, content types and nav components get a wrapper class that re-implements `__iter__`, `__len__`, `__getitem__`, `__bool__` around a `ModelChildren`. Two shapes for one ordered child list (round 1 judged it as a parallel object model). [2] (still open from round 1)
- collections.py:30 `self._owner._renumber(self._items)` — hide-inner-details — the collection calls a private method of the map that holds it; `_renumber` (`ux_node.py:31`) never reads `self`, so it is a list operation kept on the wrong object. [3]

### cdd_guidance/practices/ux/model/explorer_tree.py

- explorer_tree.py:15 `type ExplorerEntry = dict`, :37, :41, :50, :55, :61 — use-typed-signatures — the tree is built as untyped dictionaries with string keys (`kind`, `screenName`, `scenarioKey`, `stepKind`) that `story-demo/screen-tree.js` reads by the same strings; and `placed_entry` (:41) answers `tuple[int, dict]` read by position (:127-128, :131). [4] (still open from round 1)
- explorer_tree.py:87 `shown[0].practice.reading.story_tree` — low-coupling — reaches from the first linked story node through its practice to Stories' reading; `StoryTree.of_graph(graph)` (`stories/model/story_tree.py:42`) is the seam the rest of UX uses (`nodes.py:161`, `graph_reading.py:271`). [1] (still open from round 1)
- explorer_tree.py:67-68 `step.get_fact("phase")`, `step.get_fact("text")` — single-boundary — reads Stories' saved fact names directly although the `StoryTree` it holds answers `step_phase` and `step_text` (`story_tree.py:133, :137`). [1]
- explorer_tree.py:123-131 `_placed` — keep-operations-single-responsibility — named for the entries it returns, it also records `screen_keys` the first time a screen is placed, so the order `_epic_entries` walks decides which keys are kept. [3] (still open from round 1)
- explorer_tree.py:76 `ExplorerTree` against `claude_design/story_canvas.py:307 _explorer`, :320 `_story_entry`, :324 `_scenario_entry` — eliminate-duplication — two builders of the story explorer's tree (epic, sub-epic, story, scenario, steps), one from graph nodes with readable keys, one from story model objects with one-letter keys. [2] (still open from round 1)

### cdd_guidance/practices/ux/model/graph_reading.py

- graph_reading.py:43 `_NAME_MARKS`, :130 `_UxMapFile.place_of` — single-boundary — the reading holds how every format spells a node's name (`"name": "{}"`, `value="{}"`, `"text": "**{}**"`) to guess the line a node sits on; each format already writes those names and goes wrong here, without a failing test, when it changes its spelling. [1] (still open from round 1)
- graph_reading.py:192 `_format_of -> tuple[UxMap, str] | None`, unpacked at :177 as `format[1], format[0]` — shape-classes-around-resources — `_UxMapFile` exists to hold a file's format and text, yet a bare tuple carries them one step first, read back by position in reversed order. [3] (still open from round 1)
- graph_reading.py:114 `_UxMapFile(..., format: UxMap)`, :160 `self._formats` — use-intention-revealing-names — an adapter instance of `UxMap` is a "format" here, a "reader" at :201, and an "adapter" at :161 and in `ux.py:58`; one object, three words. [4] (still open from round 1)
- graph_reading.py:50 `_SHOWN` — eliminate-duplication — the triple (kind, edge, fact) for stories, scenarios and steps is written here, again as `Served.KINDS` (`served.py:18`), again as the nine members `show_story` … `step_keys` on `ServesStories` (`nodes.py:89-126`) and the fact names in `graph_facts` (`nodes.py:179, :255`); adding a fourth kind means finding all four. [2]
- graph_reading.py:59-60 `UxNodeTypes.child_lists` / `edge_order` `"ands"` — single-boundary — UX declares Stories' `ands` child list (a step's And steps), which Stories already declares (`stories/model/story_node_types.py:24`); no UX model object records `ands`. [1]
- graph_reading.py:366-367 `_steps_reading` — hold-state-on-the-object-not-in-parameters — finds a step's story by building its key and splitting it on `KEY_SEPARATOR` (state written into a string and parsed back), while `StoryTree.story_of(step)` (`story_tree.py:103`) answers it; the name `_steps_reading` returns steps, not a reading (use-intention-revealing-names). [3]
- graph_reading.py:370-375 `_screen_of` — eliminate-duplication — walks `edges.direct_parent` up to a type, the walk `StoryTree._above` and `story_tree._ancestor` (`story_tree.py:177, :261`) already write; and it answers the control itself when no screen holds it, so the caller then reads `story_keys` off a control as if it were the screen. [2] (still open from round 1)
- graph_reading.py:326-342 `_class_named` / `_domain_practices`, :377-392 `_property_at` — low-coupling — each walks into another practice's reading (`reading.class_types`, `reading.in_graph.nodes(kind)`, `nodes("Property")`, the fact `owner`) instead of asking DDD or Clean Engineering a question they answer ("the class called this", "the property of this class called this"). [1] (still open from round 1)

### cdd_guidance/practices/ux/model/nodes.py

- nodes.py:89-126, :146 `show_story`, `show_scenario`, `show_step`, `shows`, `shows_scenarios`, `shows_steps`, `story_keys`, `scenario_keys`, `step_keys`, `story_links` — eliminate-duplication — ten members that each forward one of three strings to `show`, `_shown_nodes`, `_keys` or `_links`; `story_links` exists only for stories, and `show(kind, …)` and `links_of(kind)` are public beside them, so every kind is offered twice. [2] (still open from round 1)
- nodes.py:59-66 `Interaction.trigger`, :349-356 `Transition.trigger` — eliminate-duplication — the same property and setter ("its name while it names none") written twice. [2] (still open from round 1)
- nodes.py:290 `Screen.apply_layout` — delete-unused-operations — no production caller (only `ux_spec.py` and `drawio_ux_map_heavy_spec.py`); every format assigns `screen.layout`, and its docstring is guidance about files to open, not behaviour (round 1 judged it under hide-inner-details). [3] (still open from round 1)
- nodes.py:267 `domain_concepts` beside :266 `domain_terms` — use-consistent-naming — two lists for one idea; `domain_concepts` is only copied (`ux_map.py:122`), written to JSON and used as a fallback for `domain_terms`; nothing links or checks it. [4] (still open from round 1)
- nodes.py:24-28 `StoryStep` (`kind`, `label`) — use-consistent-naming — the step's words are `label` here and `text` in Stories (`StoryTree.step_text`), its phase `kind` here, `phase` in Stories and `stepKind` in the explorer's JSON. [4] (still open from round 1)
- nodes.py:183, :186 `control_type`, `states` — use-typed-signatures — the kinds of control and the visual states are free strings on the model; the values that mean something are defined only in the formats (`html/nodes.py`, `drawio/nodes.py`). Navigation now has `NavType`; controls have nothing like it. [4] (still open from round 1)
- nodes.py:305 `UxComponent`, :375 `NavComponent.ux_type` — use-intention-revealing-names — "component" names a transition, a content type or a nav component, three things with nothing in common; `ux_type` says nothing about the kind of navigation it holds, which `Control` calls `control_type`. [4] (still open from round 1)
- nodes.py:128 `lists`, :132 `show_what` — use-intention-revealing-names — the domain verb is *serves* (`ServesStories`, `Served`); `lists(node)` means "serves this node" and `show_what(other)` means "serve what other serves". [4] (still open from round 1)
- nodes.py:156-164 `_links` — keep-operations-single-responsibility — every read of `story_links`, `shows`, `shows_scenarios` or `shows_steps` also resolves and stores each link's node (`link.resolved_in(...)`, :163), building `StoryTree.of_graph` on each read; a property read changes the links it reports. [3]

### cdd_guidance/practices/ux/model/reference_paths.py

- reference_paths.py:16 `add`, :38 `__contains__`, :47 `__getitem__`, :50 `__eq__` against a list, `__len__`, `__repr__` — deep-module — production code calls only `replace`, `as_list`, iteration and truthiness (`ux_map.py:240, :249`, `json/nodes.py:287-288`, `html/nodes.py:227-231`); the rest is surface no caller uses. [1] (still open from round 1)

### cdd_guidance/practices/ux/model/served.py

- served.py:25, :29, :33 `Served.stories`, `scenarios`, `steps` — delete-unused-operations — no caller in production or specs (grep `served.stories`, `served.scenarios`, `served.steps`); every caller uses `serve`, `kind_headed`, `as_lines` or `read_lines`. [3]
- served.py:18, :40 `KINDS`, `serve(kind: str, …)` — use-typed-signatures — the kind of thing served is a bare string (`"Story"`, `"Scenario"`, `"Step"`) passed from here to `ServesStories.show` and on to `StoryLink` and `LINKED_TYPES[kind]` (`story_link.py:75`), where a wrong string fails as a `KeyError` far from the caller; `kind_headed` answers `""` for an unknown heading, which `serve` then passes on as a kind (`drawio/nodes.py:332`). [3]

### cdd_guidance/practices/ux/model/story_link.py

- story_link.py:28 `StoryLink.__init__(kind: str, …)`, :36 `from_shown(kind, …)` — use-typed-signatures — `kind` is one of three strings used as a dictionary key at :75 (`LINKED_TYPES[self.kind]`) and passed to `nodes_keyed` / `node_written_at`; a wrong string fails as a `KeyError` far from the caller. [3] (still open from round 1)
- story_link.py:33, :45 `self.target = ""` set after construction — hide-inner-details — a public field the factory writes after the constructor ran; `target` cannot be given to `__init__`, so the object is made in two steps. [3] (still open from round 1)
- story_link.py:53 `written` — use-intention-revealing-names — `written` is the link as a file writes it; with `lists` and `show_what` on `ServesStories`, the link's operations do not use the domain verb *serves*. [4] (still open from round 1)

### cdd_guidance/practices/ux/model/ux_map.py

- ux_map.py:179 `keep_served_by`, :193 `keep_what_only` — use-intention-revealing-names — both mean "merge what the file already holds into this map"; neither says merge, and "what only" cannot be read without the docstring. [4] (still open from round 1)
- ux_map.py:94-177 `copy_of` with `_screen_copy`, `_region_copy`, `_control_copy`, `_interaction_copy`, `_take_components` — put-logic-on-the-owning-resource — the map copies every field of every node type itself, so a field added to `Screen` or `Control` must be added here too; `StoryDemoControl.take_story_fields` (`nodes.py:228`) shows the node copying its own fields. `_interaction_copy` (:154) also builds a plain `Interaction` while every other copy goes through the format's node type. [3] (still open from round 1)
- ux_map.py:88 `create(name: str | Graph = "UxMap", …)` — limit-operation-parameters — one positional parameter that is a name or, in its place, a graph, chosen by type (`rules/rule_examples.py:27` relies on it). [3] (still open from round 1)
- ux_map.py:47-62 `holds_screens`, `map_file_suffixes`, `not_a_map_failures`, `content_beside` on `UxMap` — keep-classes-single-responsibility — `UxMap` is the domain root, the base of every format adapter (`parse`, `render` through `FormatAdapter`), and the description of each format's files; an adapter is an empty map whose only job is to make other maps (`type(self).create`, :99). [3] (still open from round 1)
- ux_map.py:37-43 `control_type` … `content_type_type` — use-intention-revealing-names — `control_type` on `UxMap` is a class while `control_type` on `Control` (`nodes.py:183`) is a string such as "button"; `content_type_type` repeats the word. [4] (still open from round 1)
- ux_map.py:255 `find_screen` against `json/nodes.py:270 screen_named` — use-consistent-naming — two lookups of a screen by name, one raising `ScreenNotOnMap`, one answering none for a blank name. [4]

### cdd_guidance/practices/ux/model/ux_map_spec_fixture.py

- ux_map_spec_fixture.py:118 `_name` — eliminate-duplication — "a screen's name, blank for none" again, beside the properties the nodes already offer for it (`Transition.from_name` / `to_name`, `Interaction.destination_name`, `Screen.chrome_of_name`, `nodes.py:69, :282, :331, :336`), which `outline` could read instead. [2]
- ux_map_spec_fixture.py:21-27 `made(…, **fields)` — use-explicit-dependencies — sets any keyword as an attribute with `setattr`, so a misspelled field (`trigger` vs `_trigger`, `nav_type` vs `_nav_type`) silently becomes a new attribute and the round-trip specs compare a field no format writes. [3]

### cdd_guidance/practices/ux/rules/rule_examples.py

- rule_examples.py:38, :48, :58-60 `ScreenPair(slug, …)` — hold-state-on-the-object-not-in-parameters — each pair is given a rule's slug and looks the rule up again in `BY_SLUG`, while `EXAMPLE_PAIRS` writes each slug twice, once as the key and once as the argument; the pair could hold the rule object. [3]

### cdd_guidance/practices/ux/rules/screen_rules.py

- screen_rules.py:1 — limit-comments — the module docstring says the rules come "from cdd_guidance.practices/ux/scanners (main history)", a folder that does not exist; it describes where the code came from, not what it does. [4]
- screen_rules.py:39 `{"screen", "page", "view", "home", "main"}` — provide-meaningful-context — the generic labels a screen must not be named are an unnamed literal inside `check`; a named constant would say these are the words that are not domain terms. [4]

### cdd_guidance/practices/ux/ux.py

- ux.py:119-130 `ensure_javascript` / `_javascript_practice` — errors-out-of-existence — the docstring allows only `'stories' | 'clean_engineering'`, but any key is looked up (`self.session.practices[key]`), so `ddd` is rendered to javascript through DDD and an unknown key fails as a bare lookup error; the `NoJavascriptPractice` refusal the model still describes (`ux/.context/ux-model.md:6, :22, :34`) no longer exists, and the model still lists `javascript_practice` as public (:19). [3]
- ux.py:68 `UxFormats._incoming` — hide-inner-details — overrides a private hook of the framework's `PracticeFormats` to switch off "text that starts with a brace is JSON" for views; the difference is expressed by overriding another module's underscore method. [1] (still open from round 1)
- ux.py:133 `UxNode.practice_class = Ux` — use-explicit-dependencies — the practice class is written onto the base node class as a module-level side effect when `ux.py` is imported, so a UX node made before that import has no practice class and nothing says so. [1]


### cdd_guidance/practices/ux/model/claude_design/fixture_screen.py

- fixture_screen.py:13, :28, :101 `BAR`, `METHODS`, `EDIT_LINK` — hide-inner-details — the bar's markup, its shared methods and the Edit link are public module names, yet `harness/design_canvas/.context/cdr/0001-recipe-called-canvas-api.md:19-20` records them as "private to" `FixtureScreen` and `ScenarioSource`; a repository-wide grep finds no reader outside this file, specs included (the specs import only `FIXTURE_TRIES`, `FIXTURE_WAIT_MILLISECONDS`, `FixtureScreen`, `ScenarioSource`). [1]
- fixture_screen.py:105 `_bar`, :112 `_methods` — prefer-class-operations — two module functions only `FixtureScreen` calls (:174, :184); `_methods(story, scenario, path)` is handed the three fields of `ScenarioSource`, which `_component` unpacks first (:181), so the source's own text is written by a free function instead of by `ScenarioSource` or the screen. [3]
- fixture_screen.py:14-15, :101-102 `BAR`, `EDIT_LINK` — eliminate-duplication — the bar hard-codes the abd look's colours (`#0B0B0B`, `#E5531A`, `#2A2A2A`, `#E8E8ED`), which `look.py:11-12` names `BACKGROUND` and `ACCENT` and `look.py:15-20` uses for the same surfaces; a change of the look has to be found in both files. [2]

### cdd_guidance/practices/ux/model/claude_design/look.py

- No findings.

### cdd_guidance/practices/ux/model/claude_design/nodes.py

- nodes.py:146 `names(files)`, :151 `title`, :154 `page_of`, :158 `pages(files)`, :166 `boards(files)` — hold-state-on-the-object-not-in-parameters — every listing operation is handed the screen artboards already in the canvas folder, which the caller reads and passes on each call (`story_canvas.py:181` and `:188` both call `self._screen_files()` to pass it); `names` and `title` still do not say they name prototype artboards. (still open from round 1) [3]
- nodes.py:67 `JsonUxMap.create().copy_of(self)`, :84 `HtmlUxMap.from_document(...)`, :112 `HtmlUxMap.create().carried_document(page)`, :129 `HtmlUxMap.create().reads_file(...)` — put-logic-on-the-owning-resource — `ClaudeDesignUxMap` builds a fresh JSON or HTML map on every call, one per screen in `files` and `parse`, only to reach a method that reads no state of that map (`carried_document`, `reads_file` use constants alone, `html/nodes.py:182-198`); the HTML page format is a part this format should hold once, not rebuild per call. [3]
- nodes.py:56-57 `width = 1600`, `height = 1100` — eliminate-duplication — a desktop screen's size on the canvas is written again as `FixtureScreen.width` and `height` (`fixture_screen.py:168-169`); a screen board and the screen drawn on it can drift to two sizes. [2]

### cdd_guidance/practices/ux/model/claude_design/story_canvas.py

- story_canvas.py:25-30, :343, :408-412 — low-coupling — UX subclasses Stories' `DiagramStoryMap`, `DiagramEpic`, `DiagramStory` and reads `step.keyword`, `step.text`, `epic.leaf_epics()` and, through `getattr(step, "ands", [])`, an attribute it is not sure exists; the Stories card (`stories/.context/module-context.md:25-26`) offers none of these as terms other packages use. (still open from round 1) [1]
- story_canvas.py:130 `ClaudeDesignStoryMap` — domain-nouns-only — the class draws the Claude Design canvas (story-map artboard, explorer, context panels) and is a story map only by inheritance; its `parse` (:166) refuses, the file and the card call it the story canvas. The rename `StoryModel` -> `StoryMap` kept the misnaming. (still open from round 1) [4]
- story_canvas.py:118 `StoryCanvasSetup` — shape-classes-around-resources — three fields and no behaviour, made only to carry `workspace`, `ux_map` and `sources` into the constructor (:145) and kept so `blank` (:156-158) can build a second canvas from it. (still open from round 1) [3]
- story_canvas.py:166-167 `parse` — use-exceptions-properly — "this format is not read back" is raised as a bare `NotImplementedError`, while the Claude Design screens format beside it names its refusals (`nodes.py:34 NotAClaudeDesignCanvas`, `:42 ClaudeDesignScreenMissing`). (still open from round 1) [4]
- story_canvas.py:399 `shown_on`, :408 `_steps_of` — prefer-class-operations — two module functions; `shown_on(node, screens)` reaches into a story node's graph edges, `_steps_of` walks a scenario's steps and their `ands`; both are questions the story node (or Stories' `StoryTree`) should answer. (still open from round 1) [3]
- story_canvas.py:69 `shown_screens(...) -> List[tuple]`, :82 `_step_screens -> Iterable[tuple]`, :336 `_step_groups -> tuple[List[dict], str]`, :356 `_screen_of -> tuple`, :246 `spans: Dict[int, list]` — use-typed-signatures — results read by position (`found[2]` at :290, `(scenario, step, screen)` at :292, `span[2]` at :250). (still open from round 1) [3]
- story_canvas.py:311, :322, :333, :348 — use-intention-revealing-names — the explorer's data is written with one-letter keys (`n`, `u`, `s`, `f`, `c`, `b`, `p`, `t`, `x`, `i`), read back by `explorer.dc.html` and by this class itself (`_context_story_lines` :235-237 reads `["c"]`, `["n"]`, `["t"]`, `["x"]`). (still open from round 1) [4]
- story_canvas.py:61 `(self.actors or ["Customer"])[0]` — provide-meaningful-context — a story with no actor is drawn as "Customer", one product's word, as an unnamed default. (still open from round 1) [4]
- story_canvas.py:307 `_explorer`, :320 `_story_entry`, :324 `_scenario_entry`, :336 `_step_groups` — eliminate-duplication — a second builder of the story explorer's tree (epic, sub-epic, story, scenario, steps, screens) beside `ExplorerTree` (`explorer_tree.py:76`, used by `html/nodes.py:211`), one from graph nodes with readable keys, this one from story-map objects with one-letter keys. (still open from round 1) [2]
- story_canvas.py:36 `_SHOWN_ON = "shownOn"`, :402 `node.graph.edges.from_parent(_SHOWN_ON, node)` — low-coupling — UX reads a Stories node's graph edges by an edge name written a third time as a literal (`graph_reading.py:301` writes it, `stories/model/story_node_types.py:26` declares it); nothing ties the three strings, and the call reaches past the story node into the graph's edge store. [1]
- story_canvas.py:37-45 `_CONTEXT_PANEL_STYLE` — eliminate-duplication — the panel's style writes the fonts `'JetBrains Mono'` and `'Inter'` and the surface colours by hand, which `look.py:6-7` names `MONO` and `SANS`, and reaches the accent as `LOOK['epic']['color']` (:42) when `look.py:12` exports `ACCENT`. [2]
- story_canvas.py:109 and :279; :282 and :297 — eliminate-duplication — where a story's column starts, `index * (ClaudeDesignStory.width_px + ClaudeDesignStory.gap_px)`, is computed in `ClaudeDesignEpic.header_parts` and again in `_add_epic_thumbnails`, and where a thumbnail row starts, `thumbs_top + row * (thumb_px + thumb_gap_px)`, in `_add_epic_thumbnails` and again in `_thumbnails`; the story class holds the sizes but not the arithmetic. [2]
- story_canvas.py:154 `DesignCanvas(..., setup.project)` — use-explicit-dependencies — the constructor builds the canvas over the project folder itself, and the class then reads that folder's files through it (`_screen_files` :375, `_fixture_scripts` :381, `_stylesheets` :385, `_blank` :388), so the canvas cannot be drawn against anything but the real folder. [3]

### cdd_guidance/practices/ux/model/drawio/drawio_ux.mjs

- drawio_ux.mjs:765-931 `open`, `clear`, `add-screen`, `add-chrome`, `add-list`, `add-form`, `connect`, `add-callout`, `save`, `templates`, `status`, with `load`, `persist`, `STATE_FILE` (:229-238) — delete-unused-operations — the only caller runs `write` (`drawio/nodes.py:452`); a repository-wide grep (instructions, specs and `specifications/` included) finds no run of any other command. They build a second, older shape of the state by hand (a screen with `stories` and `terms` only, :800-807, no `scenarios`, `steps`, `served`, `uxLayout`), so the file holds two ways to make a drawing. [2]
- drawio_ux.mjs:506 `generateXml` (160 lines), :446 `renderRegion` (58), :672 `generateSiteMapPage` (85) — limit-function-lines — `generateXml` lays out screens, writes each screen's cell, regions, footers and callout, routes lanes and merges two-way edges in one function. [3]
- drawio_ux.mjs:600-619 and :715-730; :364-373 and :684-700 — eliminate-duplication — merging A->B with B->A into one two-way arrow (the key sets, the reverse lookup, the "there / back" label) is written once per page, and grouping screens by column is written twice with different defaults for a screen with no row (`0` at :372, `999` at :699). [2]
- drawio_ux.mjs:341-348 and :551-557 — eliminate-duplication — the tallest column of a screen is measured twice: `screenHeight` measures each region at its column's width, `generateXml` calls `regionH(r)` with no width (the full body width, :299), so a list whose action strip wraps in a narrow column is measured shorter where the footers are placed than where the screen's height was set. [2]
- drawio_ux.mjs:568-572 — eliminate-duplication — the callout's notation (`Stories:`, `Scenarios:`, `Steps:`, `Domain terms:`, `<by> serves <kind>:`, the separator ` · `) and the style keys (`uxLayout`, `uxArea`, `uxControls`, `uxNames`, `uxNav`) are written here and again in Python where they are read back (`served.py:18-19`, `drawio/nodes.py:42`, `:49-51`), with nothing tying the two. [2]
- drawio_ux.mjs:446 `renderRegion(r, cells, counter, sid, rx, ry, rw)` — limit-operation-parameters — seven parameters: the region, two accumulators threaded through every call, the screen's id and a box as three loose numbers. [3]
- drawio_ux.mjs:179 `S`, :246 `esc`, :446 `r`, `sid`, `rx`, `ry`, `rw`, :458 `vH`, `rh`, :543 `cw`, `cry`, :812 `pos_` — use-intention-revealing-names — single letters and abbreviations for the styles, a region, a screen id and its box. [4]
- drawio_ux.mjs:286 `5.8`, :288 `15`, `6`, :627 `30`, :691 `5000`, :699 `999`, :470 `8` — provide-meaningful-context — pixel widths per character, line height, padding, waypoint offset, the Site Map's first cell id and the "no row" sort value are bare numbers, while the file names its other measures (:151-170). [4]
- drawio_ux.mjs:145-757 — prefer-class-operations — the drawing is written by twenty free functions that hand the state, the cell list and a counter object (`{ v: number }`, :509) to one another; a screen, a region and a page that write their own cells would hold what is threaded through every call. [3]

### cdd_guidance/practices/ux/model/drawio/nodes.py

- nodes.py:467 `_is_annotation`, :477 `_plain_text` — prefer-class-operations — two module functions that read a cell's text, called from `DrawioControl`, `DrawioRegion`, `DrawioScreen` and `Callout`; `UxCellStyle` (:86) already wraps the cell and now answers `corner`, so the cell's style and its text are still read by separate owners. (still open from round 1) [3]
- nodes.py:285 and :296 `f"{region.name}{KEY_SEPARATOR}{control.name}"` — use-consistent-naming — Stories' story-key separator is reused to name a control by its region, a different idea, and the place name is built twice in one class (`_served_by_controls`, `control_at`). (still open from round 1) [4]
- nodes.py:199 `DrawioRegion.cli_record`, :265 `DrawioScreen.cli_record` — abstraction-focus — the public operations of the drawing's nodes are named for the command line they feed, not for what they answer (this region or screen as the drawing shows it). (still open from round 1) [4]
- nodes.py:229 `read_detail(detailed, ux_map)`, :246 `_read_regions(detailed, boxes, ux_map)`, :191 `read_controls(cell, control_type)` — hold-state-on-the-object-not-in-parameters — the map is passed down so a screen can ask it for node types (`ux_map.control_type`, `ux_map.region_type`), then the control type alone one layer further; a screen on a map already has the map as its parent. (still open from round 1) [3]
- nodes.py:424 `drawn.cli_timeout_seconds = self.cli_timeout_seconds` — hold-state-on-the-object-not-in-parameters — the adapter copies its own setting onto the map it makes, because the adapter and the map it writes are two instances of one class. (still open from round 1) [3]
- nodes.py:308 `Callout.under` — prefer-instance-operations — a class method that finds the annotation under a box on the page; `under` is not one of the factory names the rule allows (`from_*`, `create`, `load`), and it is the page, not the callout, that knows where its cells are. [3]
- nodes.py:278 `list(self.domain_terms or self.domain_concepts)` — eliminate-duplication — "the terms a screen names" is worked out here and again in `whiteboard/nodes.py:149`; it is a property of `Screen`. [2]

### cdd_guidance/practices/ux/model/html/nodes.py

- html/nodes.py:162 `_CONTROL_WRITERS` — put-logic-on-the-owning-resource — a module dictionary from a control type's string to an unbound method of `HtmlControl`, looked up at :38 and called as `writer(self, visual)` (:40); the control finds its own markup by name in a table outside itself. (still open from round 1) [3]
- html/nodes.py:35 `HtmlControl.html()` — use-property-not-accessor — a derived value with no parameters written as an operation (read at :259). (still open from round 1) [3]
- html/nodes.py:254 `f'<p class="screen-stories">Stories: {_text(" . ".join(stories))}'` — eliminate-duplication — the page writes the "what this screen serves" line by hand, with ` . ` as its separator and stories only, while `Served` (`served.py:13-19, :46`) is "the one notation every text format lists it in", with ` · ` and the scenarios and steps as well. [2]

### cdd_guidance/practices/ux/model/json/nodes.py

- json/nodes.py:55, :67, :120, :135, :142, :176, :209 `from_record(record, index, ux_map)`, `read_states_and_interactions(record, ux_map)`, `read_record(record, ux_map)` — hold-state-on-the-object-not-in-parameters — the map is handed down every layer (map -> region -> control -> interactions) so each node can look screens up by name and pick node types; `JsonScreen.from_record` (:135) takes `ux_map` and never reads it. (still open from round 1) [3]
- json/nodes.py:58 `(ux_map.story_demo_control_type if demo else cls)(...)` — put-logic-on-the-owning-resource — a factory on the plain control's class builds a different class the record chooses, asking the map it was handed for that class; which node type a record makes is the map's decision, and the map already holds the types. [3]
- json/nodes.py:212 `ux_map.find_screen(name)` against :73, :145, :179 `ux_map.screen_named(...)` (defined :270) — use-consistent-naming — two lookups of a screen by name on one map: `find_screen` raises for a missing name (`ux_map.py:255-259`), `screen_named` answers none for a blank one; navigation destinations use one, every other link the other. (still open from round 1) [4]
- json/nodes.py:39-47 `story_names`, `scenario_names`, `step_names` — use-consistent-naming — the model and the graph call these lists `story_keys`, `scenario_keys`, `step_keys` (read at :47 itself); one list, two names, and "names" is wrong for a scenario written as a key or a markdown link. (still open from round 1) [4]

### cdd_guidance/practices/ux/model/markdown/nodes.py

- No findings.

### cdd_guidance/practices/ux/model/view/front_end_view.py

- front_end_view.py:384 `TypeAnnotations._statement_end` against :151 `ViewText.statement_end`; bracket-depth loops at :143-148, :154-160, :507-511, :880-887 `_top_level_parts`; :524 `_past_blank` against :176 `past_space` — eliminate-duplication — "where does this statement end" is written twice with different rules (braces only against all three brackets), "outside every bracket" four times, and "skip the blanks" twice; all belong on `ViewText` beside `closing` and `line_end`. (still open from round 1) [2]
- front_end_view.py:688 `self._annotations = TypeAnnotations(text)` — keep-classes-single-responsibility — `TypeAnnotations` is "the annotations of a view, as the edits that drop them" (:296), but `Component` builds one only to ask where a function's body opens (`body_after` :694, :792, :826; `arrow_after` :823); finding a function's body is reading code, `ViewText`'s job. (still open from round 1) [3]
- front_end_view.py:689-773 `Component.opening`, `start`, `lead`, `props_braces`, `new_handlers_at`, `new_hooks_at`, `indent_of(position)`, `indent_below(position)` — hide-inner-details — a component's public seam is character positions in the view's text, which `ReshapedView` combines with the raw text (`reshaped_view.py:100-111` slices `self._existing.text[opening:closing]`); a caller must know that `props_braces` are indices of `{` and `}`. (still open from round 1) [4]
- front_end_view.py:295 `TypeAnnotations` — limit-class-methods — 34 methods (counted from :298 to :664), past the limit of 30; the statement, function, class, declaration, import and type-reading groups are each a part the class could hold. [3]
- front_end_view.py:693 `Component.props` and :698 `props_named` — use-intention-revealing-names — `props` is the props taken apart in braces only, `props_named` the props a component takes either way; `FrontEndView.props` (:856) answers `props_named`, while `ReshapedView` reads `held.props` (`reshaped_view.py:84-92`), so two names for "its props" mean different lists. [4]

### cdd_guidance/practices/ux/model/view/reshaped_view.py

- reshaped_view.py:40 `ReshapedView.reshaped` — shape-classes-around-resources — the result is built by appending to `_edits`, `_kept`, `_added`, `_new_components` (:32-38) while `reshaped()` runs; calling it twice doubles every edit and every entry. (still open from round 1) [3]
- reshaped_view.py:65-79 `_keep`, `_add` reading `member.lead`, `member.start`, `member.is_hook`, `member.written_new` — hide-inner-details — `ComponentMember` (`front_end_view.py:671`) is three text positions, a flag and a string, and cannot say "mark me" or "write me into this component", so the merge logic lives in the doer `ReshapedView`. (still open from round 1) [3]
- reshaped_view.py:69-70 and :90-91; :68 against :89 — eliminate-duplication — the marking line `// ---- {KeptMark.WORDS}: ... ----` is written by hand twice, though `KEPT_MARK.line_for(member, then)` (`harness/guidance/practice_formats.py:162-164`) is "the one definition ... of the marking line"; and "is it marked already" is asked once through `Component.marked` (`front_end_view.py:763`) and once inline with `KEPT_MARK.marks(line) and named in line` over `held.marks`. [2]

### cdd_guidance/practices/ux/model/view/view_formats.py

- No findings.

### cdd_guidance/practices/ux/model/whiteboard/nodes.py

- whiteboard/nodes.py:307 `_lines_of`, :311 `_listed`, :318 `_card_height` — prefer-class-operations — three module functions; `_card_height` is how tall a card of given text is drawn, called from `WhiteboardControl.height` (:86) and `WhiteboardScreen` (:155, :162); the text and its height belong to one card object. (still open from round 1) [3]
- whiteboard/nodes.py:311 `_listed`, :31 `_TERMS_HEADING` against `drawio/nodes.py:334 Callout._listed`, `drawio/nodes.py:49 _TERMS`, and `served.py:53-56 Served.read_lines` — eliminate-duplication — "what the line that starts with this heading lists after it" is written three times (one splits on `Served.BESIDE`, one returns the raw rest, one serves it), and the Domain terms heading is a constant in each format file; `Served` now owns the stories, scenarios and steps but not the domain terms line. (still open from round 1) [2]
- whiteboard/nodes.py:288 `_Drawn` — use-intention-revealing-names — a board's elements by role in reading order, named with a bare participle, beside `DrawnNode` (:57) and `DrawnServed` (`drawio/nodes.py:122`), where "drawn" means unrelated things. (still open from round 1) [4]


### cdd_guidance/actions/document/document.py

- document.py:35 `document` — eliminate-duplication — the step "join the non-blank parts, stripped, with a blank line between" is written word for word four times: here (`"\n\n".join(part.strip() for part in (...) if part and part.strip())`), `generate.py:118` `_generate_item`, `sketch.py:50` `_sketch_text`, and `validate.py:237` inside `create_rule`; each is the text one listed guidance gives the recipe, which belongs on the guidance (or *WorkList*) as one operation. [2]
- document.py:37 `document` — hold-state-on-the-object-not-in-parameters — every action hands its own name to its own base class as a string on each call: `self.run(on, action="document")` here, `generate.py:44` `action="generate"`, `partition.py:145` `action="partition"`, `validate.py:116` `action="validate"`, `validate.py:239` `action="create_rule"`, `iterate.py:33` `log_running("iterate")`, `satisfy.py:27` `log_running("satisfy")`; `Validate._log` (validate.py:211-216) then compares the string back (`action != "validate"`). The action is the object that knows its name (the operation, or `Name` of the class); a misspelt string logs the wrong action and the session board reads it. [3]
- document.py:50 `_paths_to_scan` — eliminate-duplication — names each found path from the session's root by hand (`path.relative_to(root).as_posix() if root is not None and path.is_relative_to(root) else path.as_posix()`), which the session's files already answer (`session.session_files.from_root`, used at `checked_fidelity.py:83` and `checked_graph.py:265`). [2]

### cdd_guidance/actions/generate/generate.py

- generate.py:17 — low-coupling — still imports `WHITEBOARD` from `render/rendered_file.py`, a file-saving helper of another action, to ask whether a fidelity writes a whiteboard (`_writes_whiteboard`, 149); the fact is about *Format*. (still open from round 1)
- generate.py:80 `_earlier_renders`, generate.py:84 `_earlier_render` — eliminate-duplication — `_listed_fidelities` (63-66) now answers the fidelities of the listed practices, yet `_earlier_renders` walks `self.listed()` filtering `PracticeGuidance` again and `_earlier_render` asks `self.work.fidelity_of(practice)` again; `validate.py:88,106,154` builds the same list three more ways. The fidelities a call works at are state of the action's work list. [2] (still open from round 1)
- generate.py:99 `_fidelity_before` — put-logic-on-the-owning-resource — still takes a practice and one of its fidelities and walks `practice.fidelities.entries` by position to find the one before; nothing in `harness/guidance` answers a fidelity's predecessor (grep `def .*before|def previous|def earlier` finds none), so the stage order is read here by index arithmetic. [3] (still open from round 1)
- generate.py:28 `@on_stage(1, ...)` — provide-meaningful-context — Document names its place (`DOCUMENT_RANK_ON_STAGE`, document.py:12) but every other action still gives a bare number: here `1`, `validate.py:52` `2`, `iterate.py:26` `3`, `sketch.py:112` `4`, `render.py:56` `5`, `partition.py:127` `0`; the order of actions on a stage is six literals in six files, so moving one means reading all six. [4] (still open from round 1)

### cdd_guidance/actions/iterate/iterate.py

- iterate.py:21 `mark_iterate_round` — abstraction-focus — an `@mcp @agent_tool` that changes nothing and returns the fixed word `"iterate-round"`; it exists so its docstring reaches the agent, and is published on MCP as something callable that records nothing, though its docstring says "Record that ... is due". [4] (still open from round 1)

### cdd_guidance/actions/partition/partition.py

- partition.py:132 `partition` — avoid-vague-parameter-names — `mode: str = "one_go"` still changes nothing: it is only passed to `_finished` (154) and printed in the closing sentence (159). [4] (still open from round 1)
- partition.py:47 `context_setup`, partition.py:52 `context_index` — use-typed-signatures — both public properties still answer `Any` on purpose (comment 44-45) so the installer does not publish Context Setup's tools again under partition; the installer's rule leaks into the type of the seam. [4] (still open from round 1)
- partition.py:38 `__init__` — use-explicit-dependencies — builds its collaborator `ContextSetup()` when none is handed (`context_setup if context_setup is not None else ContextSetup()`); Context Setup holds the embedding provider and the converter, an external system the class can then only run against that one implementation of, and every production construction takes the built-in one. [3]
- partition.py:69 `verify_segment_completeness` — errors-out-of-existence — a segment path that is not there is answered as text (`"completeness: FAIL\nerror: segment not found: ..."`), the same shape as a real completeness failure, while the rest of the action refuses a missing path by name through the session's files (`self.files.path_named`, `session_files.existing`, *NamedPathNotFoundError*); a caller that greps for `FAIL` cannot tell a typo from a stub segment. [3]
- partition.py:112 `segment` (and partition.py:98 `index`) — abstraction-focus — both are `@mcp @agent_tool` operations that write nothing; `segment` is documented "Write verbatim source chunks ... into segment files" and answers "Verbatim source chunks written ... Named-entry completeness verified", although nothing was written or verified. An instruction published as a tool reports success for work it never did. [4]

### cdd_guidance/actions/partition/segment.py

- segment.py:78 `PartitionFile` — class-not-property-instance-or-subtype — the base's `path` and `text` properties still have no production reader (grep: only `partition_spec.py:369,447,450`); *Segment* reads `self._path` / `self._text` directly and *PartitionIndex* neither; the base shares three assignments and one used property (`completeness`, `partition.py:71`). [2] (still open from round 1)
- segment.py:66 `SegmentEntry.status`, segment.py:180 `_entry_for` — use-intention-revealing-names — abbreviated locals `n`, `short_ok`, `idxs` (and `i`) in otherwise fully named code. [4]
- segment.py:106 `_FAIL_FOOTER` — general-purpose-surface — the report every practice's partition gets says "do not lock story inventory from this chunk", a Stories step; Partition runs once per listed practice (module card, `actions/partition`), so a DDD or Clean Engineering partition is told about a story inventory it does not keep. [1]

### cdd_guidance/actions/render/kept_document.py

- kept_document.py:51 `onto` — shape-classes-around-resources — one class still switches on the format's name (`"markdown"` 56, `"drawio"` 59, else whiteboard) to do three unrelated merges: markdown lines, draw.io XML cells, whiteboard JSON elements, while each practice's drawing adapter already keeps layout from `previous`. [2] (still open from round 1)
- kept_document.py:118 `_whiteboard` — low-coupling — still reads and writes the whiteboard file as raw JSON (`before["elements"]`, `after["order"]`, `x`, `y`, `text`) though `harness/whiteboard` owns that file (`Whiteboard.from_text`, used by `rendered_file.py:185-186` in the same save); a change to the board file's layout must be made in two modules. [1] (still open from round 1)
- kept_document.py:60 `onto` — never-swallow-exceptions — `except (ET.ParseError, json.JSONDecodeError, KeyError, TypeError): return Reshaped(rendered, [], [])` still answers the bare render when the file already there cannot be read, and `RenderedFile.save` (rendered_file.py:173-175) then writes it over that file with nothing reported; `KeyError`/`TypeError` also hide a mistake in this class. [3] (still open from round 1)
- kept_document.py:90 `_are_mostly_drawn`, :95 `_drawn_new`, :137 `_placed_new` — use-typed-signatures — `held: dict, drawn: dict` stand for cells by id in one caller and board elements by name in the other; the untyped dictionaries follow from working on raw XML and JSON. [3] (still open from round 1)
- kept_document.py:95 `_drawn_new`, kept_document.py:137 `_placed_new` — eliminate-duplication — the same algorithm twice ("each drawn thing whose words the file's things do not say, as `name 'words'`"), and `_drawio` (75-88) and `_whiteboard` (118-135) repeat the same steps (said, keeps_names, only_in_file, moved, kept) over two raw shapes. [2]

### cdd_guidance/actions/render/render.py

- render.py:99 `_render_files` — hold-state-on-the-object-not-in-parameters — `format`, `paths` and `source` still travel as loose strings from `render` to `_render_files` to `_saved_by_declared_paths` (127, five parameters) to `_saved_code` (149), though `RenderRequest` (`harness/guidance/practice_formats.py`) is the object that carries one render. [3] (still open from round 1)
- render.py:78 `render` — hold-state-on-the-object-not-in-parameters — *Format* is "made once ... so its holder never parses it again" (`harness/markdown/format.py:13-16`), yet `Format(format)` is built five times (78, 83, 107, 109, 110) and `Format(source)` four (109, 135, 142 twice, 146) in one call. [3] (still open from round 1)
- render.py:127 `_saved_by_declared_paths` — keep-operations-single-responsibility — still decides among five outcomes (code, saved graph, sections, beside itself, code again when `rendered.content` is a dict), and `_render_files` (99-116) decides four more (canvas, declared paths, answered content, saved file for a fidelity or not); where a render is saved is chosen in two operations. [3] (still open from round 1)
- render.py:83 `render` — use-consistent-naming — "is this the whiteboard / a diagram / a canvas" is still asked by string in five places: `Format(format).name == WHITEBOARD` (here, `generate.py:149`, `rendered_file.py:177`), `.group == CANVAS` with `CANVAS = "canvas"` (26, 107), `format.group != "diagram"` (`rendered_file.py:128`), `format.group == "diagram"` (`render_order.py:109`), `SAVED_GROUPS` (`rendered_file.py:25`); *Format* already holds the groups (`Format.GROUPS`) and should answer these as properties. [4] (still open from round 1)
- render.py:145 `_saved_by_declared_paths` — use-typed-signatures — the result type is now typed, but which kind of render came back is still found by sniffing `isinstance(rendered.content, dict)` here and in `RenderedCode._placed(content: object)` (`rendered_code.py:120-122`); `Rendered.content` is a text in one case and a file map in the other with no type saying which. [3]
- render.py:205 `_drawn_from` — hold-state-on-the-object-not-in-parameters — holds the *FidelityGuidance* it found (`fidelity`) and passes its slug back to `self._work_on(fidelity.slug)`, which looks the fidelity up again by name (`GuidanceCommand.from_guidance`, `harness/guidance_actions/guidance_actions.py:762`); the guardrails' "hold references, never look up by name". [3]
- render.py:236 `record_board` — use-exceptions-properly — refuses a file that is not a `.whiteboard` with a bare `ValueError` and a string, while the same file declares named failures for its other refusals (`BoardNotKept` 31, `FormatNotDeclared` 41). [3]

### cdd_guidance/actions/render/render_order.py

- render_order.py:50 `RenderOrder` — class-not-property-instance-or-subtype — still a `RenderRequest` (format, content, source, previous, folder) plus the fidelity's slug and module: `from_request` (57-69) copies the fields one by one into a `RenderOrderDocument` and `request_at` (85-90) copies them back; `RenderRequest` could write and read itself, the order adding only where to find the fidelity. [2] (still open from round 1)

### cdd_guidance/actions/render/render_result.py

- render_result.py:21 `DECIDE_EACH` — eliminate-duplication — the instruction "go through every entry ... moved somewhere, so move it there ... merged into something else, so fold it in ... no longer needed, so remove it; or ... the source is behind, so put it back in the source and render again ... who added it ... plays no part ... ask the person" is written twice, here and in `Render.place_rendered`'s text (`render.py:176`), and a third time in shorter form in `render`'s docstring; a change to how an agent decides a migration has to be made in all three. [2]
- render_result.py:149 `SavedFile.migrate`/`decide`, render_result.py:200 `SavedFiles.migrate`/`decide` — eliminate-duplication — the two properties are word for word the same in both classes (`list(self._migrate)`; `DECIDE_EACH if self._migrate else ""`), and `RenderResult` already declares `migrate` as the shared answer. [2]
- render_result.py:169 `SavedBoard.__init__`, render_result.py:182 `batches`, render_result.py:132 `AnsweredContent.content` — use-typed-signatures — the public fields answer `list` and `Any`; `rendered_file.py:182` `_board_writes -> list` hands the same untyped list on, so the shape of a board's store writes is known only to `Whiteboard.batches`. [3]
- render_result.py:107 `RenderResult.rendered` — hide-inner-details — a public mutable attribute read only inside this file (112, 133, 221; grep finds no reader outside); a private field with the properties already there would do. [3]

### cdd_guidance/actions/render/render_worker.py

- render_worker.py:25 `_fidelity_of` — put-logic-on-the-owning-resource — still a module function that takes the order and makes its fidelity through `WorkList(None)`, `GuidanceCommand.from_guidance(order.fidelity)` and `work.each(lambda worked: worked)[0]`, running an identity function over a work list to get one object; resolving the fidelity from the slug belongs on *RenderOrder* (whose `fidelity` answers only the slug). [3] (still open from round 1)

### cdd_guidance/actions/render/rendered_canvas.py

- No findings.

### cdd_guidance/actions/render/rendered_code.py

- rendered_code.py:73 `RenderedCode.__init__` — hold-state-on-the-object-not-in-parameters — six parameters, four of them read off one fidelity by the caller (`render.py:155-159`: `worked.session_output.root`, `worked.declared.placement`, the format's adapter's `reshape`, the source's stem); holding the fidelity, the format and the source would be three. [3] (still open from round 1)
- rendered_code.py:116 `_migration` — avoid-vague-parameter-names — still reads the owner of a kept member out of a string with `kept.rpartition(".")`, over `Reshaped.left_to_move` (`harness/guidance/practice_formats.py`), a list of strings that holds member names and also the sentence `"3 line(s) set apart"`; a sentence is read as a member with no owner. [3] (still open from round 1)
- rendered_code.py:50 `_BANNER` — low-coupling — Render still finds each piece of rendered code by a banner comment (`# === Ordering · Cart ===`) that Clean Engineering's code class model writes; the two agree only through this regular expression and the separators at 52-54. [1] (still open from round 1)
- rendered_code.py:143 `_sections` — eliminate-duplication — cutting a text at marker lines into `(name, text)` pairs (`starts`, `ends = [*starts[1:], len(lines)]`, `zip`, `"\n".join(...).rstrip("\n") + "\n"`) is written again in `RenderedSections._sections` (`rendered_file.py:81-89`), differing only in the marker (a banner here, `# ` there). [2]

### cdd_guidance/actions/render/rendered_file.py

- rendered_file.py:22 `WHITEBOARD`, rendered_file.py:25 `SAVED_GROUPS` — single-boundary — two facts about formats are still module constants of one action's helper file that other modules import from it: `generate/generate.py:17`, `render/render.py:7`, `align/format_alignment.py:39`. They belong with *Format* in `harness/markdown`, which already holds `GROUPS`. [1] (still open from round 1)
- rendered_file.py:27 `_SKETCH` — eliminate-duplication — the sketch format is named twice in this package, `_SKETCH = "sketch"` here and `_SKETCH = Format("sketch")` at `source_files.py:16`, while *Format* already knows the sketch (`_FILE_NAME_ENDINGS`, `Format.names`). [2]
- rendered_file.py:69 `RenderedSections.save`, rendered_file.py:173 `RenderedFile.save` — eliminate-duplication — the same save is written twice: `KeptDocument(self.format).onto(before, text)`, `mkdir(parents=True, exist_ok=True)`, `write_text(kept.text)`, `[KeptMember(file, each, kept.added) for each in kept.kept]`; `RenderedCode.save` (`rendered_code.py:100-104`) and `RenderedCanvas.save` (`rendered_canvas.py:52-54`) repeat the write loop. [2]
- rendered_file.py:163 `from_graph` — hold-state-on-the-object-not-in-parameters — hands three pieces of one fidelity to the saved graph, `SavedGraph.scope_name(fidelity.practice_guidance.key, placement, root)`, and reads `fidelity.declared.placement`, `fidelity.session_output.root(s)` and `fidelity.practice_guidance.key` itself; the fidelity is the object that should answer the scope it fills from a graph. [3]
- rendered_file.py:114 `RenderedFile.path`, `RenderedFile.format` — hide-inner-details — public mutable attributes; `render.py:143` reads `own.path`. [3]

### cdd_guidance/actions/render/reshaped_code.py

- reshaped_code.py:210 `ReshapedCode.__init__` — eliminate-duplication — `"#" if language.name == _PYTHON else "//"` restates `CodeLanguage.line_comment` (`cdd_guidance/practices/source_code/code_body.py:54`), and `CodeOutline` picks its parser by `language.name == _PYTHON` (89); `source_files.py:6` already imports `CODE_LANGUAGES` from that module, so the render package holds language knowledge twice. [1] (still open from round 1)
- reshaped_code.py:117 `_python_member` — limit-operation-parameters — four parameters (`start`, `last`, `opened`, `floor`) for a private parser step. [3] (still open from round 1)
- reshaped_code.py:327 `_FileEdit._set_apart` — eliminate-duplication — writes the marking line by hand (`f"... ---- {KeptMark.WORDS}: {owner}.{op}, kept from lines ..."`) although `KeptMark.line_for` is "the one definition ... of the marking line" (`harness/guidance/practice_formats.py:150-165`) and `spec_reshape.py:167` and `reshaped_story_file.py:135` use it. [2]
- reshaped_code.py:226 `ReshapedCode._edited` — temporal-independence — `_FileEdit.kept`, `added` and `changed` (237-239) are public lists that stay empty until `text()` runs, which fills them as a side effect; `Reshaped(edit.text(...), sorted(edit.kept), ...)` is correct only because Python evaluates arguments left to right. [3]
- reshaped_code.py:255 `_FileEdit._class_lines` — keep-operations-single-responsibility — one operation records what was kept, added and changed (264-266, mutating the edit's lists) and builds the class's new lines (269-280). [3]
- reshaped_code.py:65 `CodeMember` — hide-inner-details — `operations`, `is_class`, `body` and `properties` are public mutable fields that *CodeOutline* sets after construction (`member.is_class = True`, 129-132, 168-170); a member is not whole until another class finishes it. [3]
- reshaped_code.py:41, reshaped_code.py:91 — limit-comments — the comment "Words that open a statement with a parenthesis and are no operation" sits above `_PYTHON_PROPERTY`, not `_STATEMENTS` (44) which it describes, and the comment at 91 about a class's operations trails the last statement of `__init__`, describing `_python_members` rather than anything there. [4]

### cdd_guidance/actions/render/source_files.py

- source_files.py:36 `SourceFiles.__init__` — use-typed-signatures — `worked: object`, then reached by `getattr(self._worked, "format", Format())` (69), `self._worked.slug` (82) and `isinstance(self._worked, FidelityGuidance)` (88); the type is `WorkedGuidance`, and the getattr hides the dependency from the graph. [3]
- source_files.py:90 `_rendering_formats` — eliminate-duplication — "the formats that read the fidelity's files: its practice's, else its Clean Engineering companion's" is the same choice `FidelityGuidance.formats_without_an_adapter` makes (`harness/guidance/guidance.py:816-819`); the fidelity should answer its reading formats once. [2]
- source_files.py:13 `SAVED_GRAPH_SUFFIX` — single-boundary — the action decides that any `.json` file is a saved graph (here 103, and `render.py:136` routes it to `RenderedFile.from_graph`), a fact about *SavedGraph* (`harness/graph/saved_graph.py`, `GRAPH_FILE_NAME`), while `render`'s own docstring offers `json` as a source format; a practice's json file named as a source is read as a graph. [1]

### cdd_guidance/actions/satisfy/satisfy.py

- No findings.

### cdd_guidance/actions/sketch/sketch.py

- sketch.py:101 `review_sketch` — abstraction-focus — an `@mcp @agent_tool` that does nothing and returns the fixed word `"sketch-review"`; it exists so its docstring reaches the agent, published as a callable tool that changes no state. [4] (still open from round 1)

### cdd_guidance/actions/validate/checked_fidelity.py

- checked_fidelity.py:89 `_written_at` — eliminate-duplication — "a declared path that names no one file" is tested as `declared.partition("{")` here, as `DeclaredFile(path).names_one_path` eight lines above (81), as `_NOT_ONE_FOLDER = re.compile(r"[{*?]")` in `generate.py:21`, a word-for-word copy of `_FILLED_IN` in `harness/guidance/declared_outputs.py:18`; `DeclaredFile` should answer the folders a templated path names too. [2] (still open from round 1)

### cdd_guidance/actions/validate/checked_graph.py

- checked_graph.py:23 `NamedToCheck` — use-intention-revealing-names — still a frozen bag of one call's arguments (`paths`, `graph`, `call`, now `judge_all`) under a name that reads as an adjective; it exists to keep the constructor at three parameters. [4] (still open from round 1)
- checked_graph.py:114 `violations`, :119 `accepted`, :124 `found` — use-property-not-accessor — derived values with no parameters, recomputed on every call (each filters the accepted-violations file again): `violations()` at `report_text.py:80,113` and `validate.py:190`, `found()` once more for each fidelity through `found_by` (90). [3] (still open from round 1)
- checked_graph.py:55 `__init__`, checked_graph.py:223 `_session_saved`, :215 `_built_from_written`, :229 `_read_named` — keep-operations-single-responsibility — the constructor refreshes the session's graph and writes a graph file (`_graph_files` → `_built_at`, 253-257), and the operations that answer the files also set `_checked`, and `_built_from_written` reassigns `_built_from` (218), so a query changes the state the other queries read. [3]
- checked_graph.py:254 `_built_at` — write-interactions — reaches through the session's parts, `self._session.graph.reads.hold_whole(...)`, `self._session.graph.reads.refreshed(...)`, as at `self._session.folder.violation_history` (87) and `self._session.session_practices.every` (166), instead of asking the session through a named operation. [3]
- checked_graph.py:128 `found`, checked_graph.py:175 `unread` — eliminate-duplication — `[checked.fidelity.practice_guidance.key for checked in self._checked_fidelities]` is built twice, and `found_by` (198) and `_scoped_practices` (165) read the same practice off each checked fidelity again; *CheckedFidelity* could answer its practice. [2]

### cdd_guidance/actions/validate/report_files.py

- report_files.py:44 `graph_file` — delete-unused-operations — the branch for a call with no report (a temporary `edited-graph-*.json` in the session folder, 44-46) is never reached: `graph_file` is called only from `checked_graph.py:210,221`, each behind `self._checked_fidelities` being non-empty, and *ReportFiles* claims one report for each checked fidelity (34); the docstring promises behaviour nobody gets, and the branch would leave a file behind each time. [3]
- report_files.py:55 `where` — use-property-not-accessor — a derived value with no parameters, under a name that does not say it is the saved reports' paths. [4]

### cdd_guidance/actions/validate/report_text.py

- report_text.py:36 `_RULE_BULLET`, report_text.py:213 `RulePlaces` — eliminate-duplication — still a second parser of a rule bullet in a practice's markdown; `Rule._from_bullet` (`harness/guidance/rule.py:107-121`) parses the same bullet with its own two patterns. Where a rule is written is a fact the *Rule* could keep when it is read. [2] (still open from round 1)
- report_text.py:114 `_summary_lines`, report_text.py:159 `_hit_lines` — eliminate-duplication — the split of hits into violations and candidates (`not violation.is_candidate` / `violation.is_candidate`) is written here twice and again at `validate.py:197`; the checked graph, or `Violation`, should answer it once. [2]

### cdd_guidance/actions/validate/validate.py

- validate.py:209 `_log_graph_validation` — hide-inner-details — still sets the base class's private flag `self._logged_session_action = "validate"` (declared at `harness/guidance_actions/guidance_actions.py:701`) to stop a second log line; the subclass depends on how *GuidanceAction* remembers what it logged. [1] (still open from round 1)
- validate.py:228 `create_rule` — no-legacy-api-after-refactor — `@noDeploy` (with `@mcp @skill` stacked under it), no caller in production code (grep: only this file, specs, and the module card and model naming it), and its answer still says "Write a new named rule into this tool" and "run collection validate". Either it is published or it goes. [4] (still open from round 1)
- validate.py:88 `_rule_named`, validate.py:106 `_check`, validate.py:154 `_fidelities` — eliminate-duplication — the listed guidance at its fidelity is built three ways in one call: filtered by `isinstance(item, Guidance)` (88), by `not isinstance(item, str)` (106), and `_fidelities` filtering again (154). [2] (still open from round 1)
- validate.py:47 `__init__` — temporal-independence — `_graph`, `_report_of` and `_rule` start as `None` and are set inside `validate()` (78-79); `_saved`, `_report`, `_rules_text`, `_overlay_section` and `_judging_instruction` dereference `self._graph` / `self._report_of` as if set, so any of them called before `_check` fails with `AttributeError` on `None`; the order is known only to `validate`. [3]

### cdd_guidance/actions/validate/validate_examples.py

- No findings.


### cdd_guidance/align/__init__.py

- No findings.

### cdd_guidance/align/callout_alignment.py

- callout_alignment.py:29 `_CalloutGap` — class-not-property-instance-or-subtype — a second shape of one gap: `CalloutAlignment.gaps` (86) answers a private NamedTuple (kind, file, message) that another file unpacks and rebuilds as an *AlignmentGap* (`format_alignment.py:474` `self._callout_gap(*gap)`, `:506-507`); its three kinds are constants here (19-22) while *AlignmentGap.kind* documents them in the other file (`format_alignment.py:93-94`). An *AlignmentGap* with an empty fidelity is already what each one becomes. [2]
- callout_alignment.py:90-102 `gaps`, `_read_graph` — eliminate-duplication — the guard (no files, or no working practice, answers nothing) and the call `graph.load_files(str(session.checkout.root.resolve()), session.session_practices.working, files, graph.overlays, call)` are the body of `SessionExplorer._read_listed` (`space/session/files/session_explorer.py:52-58`) written again; the class docstring even says it reads them "as the Files app's graph view reads them". A fix to how the session reads listed files into its graph has to be made twice. [2]
- callout_alignment.py:102 `_read_graph` — hold-state-on-the-object-not-in-parameters — hands the graph its own `graph.overlays` back as an argument of `graph.load_files`, and hands the session's working practices as names the graph looks up again (`harness/graph/graph.py:1399` `self.practices.named(key)`). [3]
- callout_alignment.py:106 `_read_graph` — eliminate-duplication — `Path(practice.source_root) if practice.source_root else session.checkout.root` is `SavedPractice.root_in(folder)` (`harness/graph/saved_graph.py:197-199`) written out again. [2]
- callout_alignment.py:86-93, :109 `gaps` — temporal-independence — `gaps()` fills `self._callouts` and `_read_graph` appends to `self._nodes_in` with `setdefault(...).append` and never clears it, so a second `gaps()` on the same object holds every placed node twice; `_missing_targets`, `_unmatched` and `_is_shown` read `self._callouts[file]` and work only after `gaps` has set it. [3]
- callout_alignment.py:97-112 `_read_graph` — keep-operations-single-responsibility — one operation loads the files into the session's graph (I/O and mutation of a shared graph), saves it to a *SavedGraph*, places each node in its project file, indexes nodes by file, and computes the edges that cross files. [3]
- callout_alignment.py:114-117, :142-143, :23, :26 `_holds_links`, `_is_document` — put-logic-on-the-owning-resource — whether a format is a document (`Format.from_extension(...).group == "markdown"`, written twice) and whether its text holds links (code, except a private set `{"html"}`) are facts about a format, decided here on file names, while *Format* already answers `is_code` and `group` (`harness/markdown/format.py:69-75`). [3]

### cdd_guidance/align/format_alignment.py

- format_alignment.py:39, :333, :440 `SAVED_GROUPS` — low-coupling — imports a constant from inside the Render action's helper file (`cdd_guidance/actions/render/rendered_file.py:25`), not from Render's seam; which format groups a render saves is a fact about *Format*. Round 1 reported the exporting side (`rendered_file.py:24`, single-boundary), when the importer was `space/session/format_alignment.py:36`; the import moved here with the module. [1]
- format_alignment.py:65, :334, :435 `_DOCUMENT_GROUP` — eliminate-duplication — "is this the document format" is `Format(name).group != "markdown"`, sorted on twice in this file, with the same literal kept a third time as `_MARKDOWN` in `callout_alignment.py:23` and a fourth in `cdd_guidance/practices/template_checks.py:28`. [2]
- format_alignment.py:333-334, :435, :440 `_compared_formats`, `_code_formats_missing` — put-logic-on-the-owning-resource — the session output's `chosen_formats` are strings, and each operation builds `Format(name)` from them again on every use (four builds in two operations); the refactor guardrails name "a Format built from a string" as a part to build once and keep. [3]
- format_alignment.py:343, :436, :504 `_documents`, `_code_formats_missing`, `_files_of` — eliminate-duplication — "the files of the chosen formats that are there" (`entry.path for name in chosen for entry in listed.get(name, []) if entry.exists`) is written three times here, and again at `cdd_guidance/actions/generate/generate.py:107` and `cdd_guidance/practices/stories/model/story_map.py:1346`; it belongs on the fidelity's written files, which own the listing. [2]
- format_alignment.py:440 `_code_formats_missing` — eliminate-duplication — `any(path.endswith("/") for path in paths.get(name, []))` decides which code formats are written as a folder for each module, which `DeclaredOutputs.code_folders()` already answers (`harness/guidance/declared_outputs.py:198-202`) and `practice_session_output.py:518-519` calls. [2]
- format_alignment.py:364, :379, :389 `_document_gaps`, `_differences`, `_read` — hold-state-on-the-object-not-in-parameters — one document is a `dict[str, Path]` handed around, and its `placed_at` name and leading format (`next(iter(there))`) are handed from `_document_gaps` to `_differences` to `_read` for every file; a document object would hold its files, its leading format and where it is placed. [3]
- format_alignment.py:401 `_compared` — limit-operation-parameters — takes six values (`lead`, `leading`, `other`, `reading`, and a tuple packing two format names), over the project's limit of 3 (`.context/config.json:92`); the two files and their readings are one document's state. `_read`, `_lacks` and `_source_lacks` (389, 420, 424) take four each. [3]
- format_alignment.py:81 `AlignmentGap.__init__` — limit-operation-parameters — seven parameters, four of them optional strings defaulted to empty, so a gap made for a callout (506-507) and one made for a fidelity share one constructor whose arguments mean different things for each. [3]
- format_alignment.py:482, :492 `align`, `_rendered` — hold-state-on-the-object-not-in-parameters — `align` makes the same `Render(self._session, self._call)` again for every gap and hands it to `_rendered` as a parameter, and `_rendered` hands Render the fidelity's slug (`[gap.fidelity]`) so Render looks the fidelity up again, though `_FidelityAlignment` held the *FidelityGuidance* object (318-319) when it made the gap. [3]
- format_alignment.py:466 `diagnose` — write-interactions — reaches three objects deep, `self._session.session_files.file_manager.search_again()`, instead of asking the session through an operation of its own. [3]
- format_alignment.py:468 `diagnose` — use-explicit-dependencies — reaches the process-wide `PRACTICE_CATALOGUE` and makes a new instance of every practice on each diagnosis, though the module's instructions say a session makes the practices' instances once; the comparison graph's practices cannot be handed in. [3]
- format_alignment.py:216 `follow_up` — provide-meaningful-context — compares the format to the literal `"whiteboard"`, while `WHITEBOARD` is named at `rendered_file.py:22` and *Format* is the owner of format names. [4]

### cdd_guidance/context_setup/context_setup.py

- context_setup.py:70, :101-108 `_converter` — use-explicit-dependencies — the document converter is class-level state shared by every instance and built inside a property, so it cannot be handed in and specs must patch the class. (still open from round 1)
- context_setup.py:168, :190, :210 `smoke_test`, `scout_app`, `complete_capture` — eliminate-duplication — the three tools build the same `LiveAppCapture(repo_path, capture_repo, surface, base_url, …)` and `_in_project` (95-99) then rebuilds it with `dataclasses.replace`; `complete_capture` passes `missing_pages` in the position named `entry_paths`, so one field means "paths to scout" in two tools and "paths that failed" in the third. (still open from round 1)
- context_setup.py:75 `__init__` — use-explicit-dependencies — constructs its collaborator `ContextIndex()` inside construction when none is given, so the toolset the cdd server builds with no arguments always runs against the default index and embedding provider. [3]

### cdd_guidance/diagnostics/__init__.py

- No findings.

### cdd_guidance/diagnostics/session_diagnostics.py

- No findings.

### cdd_guidance/diagnostics/session_probe.py

- session_probe.py:18, :36, :49, :76-90 `ProbeReport`, `run`, `_report` — use-typed-signatures — the probe answers `dict[str, Any]` with string keys `"color"`, `"report"`, `"checks"`, `"tail"` and the colours written as literals `"red"` / `"green"`, read back by key in `session_diagnostics.py:38-40`; *ProbeOutcome* (`harness/diagnostics/probe_outcome.py:23-30`) already names `GREEN` and `RED` and owns the colour rule. [2]
- session_probe.py:21, :64, :71, :82 — provide-meaningful-context — `_SESSION_PROBE_NAME = "guidance-probe"` is named, yet the same literal is written again for the chat pointer (64), the transcript's file name (71) and the check (82); renaming one leaves the check reading the other. [2]
- session_probe.py:30-34, :51 `__init__`, `run` — temporal-independence — the constructor makes the throwaway repository on disk and `run` deletes it in its `finally`, so a second `run` on the same probe works in a folder that is gone; the object is valid for exactly one call, which nothing states. [3]
- session_probe.py:76-84, :96-100 `_report`, `_marks_loops` — keep-operations-single-responsibility — building the report runs `_marks_loops`, which writes two loop markers into the session's log while the check list is being assembled; a check that changes what it checks sits among checks that only read. [3]
- session_probe.py:40-42 `run` — use-explicit-dependencies — imports *RepositoryToolsets* inside the function and acts on the global `RUNNING_CHECKOUT` to fix the import path before probing, instead of being handed what it needs. [3]

### cdd_guidance/patterns/cdd_claude_mod/cdd_claude_mod.py

- No findings.

### cdd_guidance/patterns/cdd_web_domain_access/access_facts.py

- access_facts.py:33-56 `node_type`, `facts` — keep-classes-single-responsibility — one class answers four kinds of file through an if-chain on the name and then a second if-chain on the type string it just answered (`facts` calls `node_type` again, re-running the regular expressions); LERN split the same shape into one *FactFile* subtype per kind (*NodeRootFile*, *RouteFile*, … in `lern_domain_driven/fact_files.py`), web domain access did not. [4]
- access_facts.py:37-54 `node_type` — eliminate-duplication — the node type names `"AccessRoute"`, `"AccessHandWrittenAdapter"`, `"AccessNode"`, `"AccessAnnotatedToolset"` are written here and again in the rules' `node_types` and checks (`practices/ddd/rules/access_rules.py:20, 33, 46, 49, 60`); the fact names were given one home in `fact_names.py`, the node type names were not, so a renamed type makes its rule check nothing, silently. [2]
- access_facts.py:79 `annotated_toolset_facts` — make-module-only-operations-private — public, but its one production caller is `facts` (55); only `access_facts_spec.py:25-38` calls it directly. [1]
- access_facts.py:83 `annotated_toolset_facts` — errors-out-of-existence — `ast.parse(self._source.text)` on a `.py` file carrying `@language_adapter(` raises `SyntaxError` with the file named `<unknown>`, out of `WebDomainAccessOverlay.read` and the whole graph reading, for a file being edited; source that does not parse may be skipped (`source-parses` reports it) or refused naming the file, not raised anonymously. [3]

### cdd_guidance/patterns/cdd_web_domain_access/cdd_web_domain_access.py

- No findings.

### cdd_guidance/patterns/cdd_web_domain_access/fact_names.py

- No findings.

### cdd_guidance/patterns/cdd_web_domain_access/graph_overlay.py

- No findings.

### cdd_guidance/patterns/cdd_web_domain_access/practices/ddd/rules/access_rules.py

- No findings.

### cdd_guidance/patterns/domain_driven_stack/domain_driven_stack.py

- domain_driven_stack.py:8 `DomainDrivenStack` — merge-one-class-packages — a package holding one class of two attributes; the card's reason (so the patterns' `__init__` only registers and no stack imports back into it) holds equally for a file beside `pattern.py` and `fact_file.py`, which already sit at the package's top level, and `_patterns_in_this_folder` (`patterns/__init__.py:16-25`) only reads folders, so a top-level file is never taken for a pattern. [1]

### cdd_guidance/patterns/fact_file.py

- fact_file.py:22, :26 `at`, `facts` — use-typed-signatures — `at(cls, root, path, *held)` passes any further constructor values through an untyped `*held` (a behavior file's node type, a node root's test setup text), and `facts` answers a bare `dict`; the seam every pattern's fact files share says nothing of what either carries. [3]

### cdd_guidance/patterns/lern_domain_driven/fact_files.py

- fact_files.py:56, :59, :63, :74, :176, :185, :251, :271, :276 — use-typed-signatures — every fact is an untyped `dict`, `list[list]` or `list[list[str]]`; the top-level keys now come from `fact_names`, but each node repository is a dict whose keys `"name"`, `"raw_io"`, `"parses_on_read"` (185) are spelled again in the rule that reads them (`practices/ddd/rules/lern_tier_rules.py:28, 31, 33`). (still open from round 1)
- fact_files.py:74 `unreset_instances` — hold-state-on-the-object-not-in-parameters — `setup_text` is handed from `_LernReading.setup_text` to `_AggregateTiers._tier_facts` (`graph_overlay.py:245`) to `NodeRootFile` and to `unreset_instances` (256); *NodeRootFile* even holds it as `self._setup_text` and passes its own field back into its inherited operation (188). (still open from round 1)
- fact_files.py:1-5, :263-279 `AggregateFolder` — eliminate-duplication — the module says each file is read once, but `web_path_literals` reads every `*.ts*` of the folder, the node file is read again as a *NodeRootFile* (`graph_overlay.py:251`), each repository's file again as a *LernFile* (255), and every `.tsx` again for its view export (`graph_overlay.py:274`). (still open from round 1)

### cdd_guidance/patterns/lern_domain_driven/fact_names.py

- No findings.

### cdd_guidance/patterns/lern_domain_driven/graph_overlay.py

- graph_overlay.py:79-80, :110-111 `_LernReading.ddd`, `story_nodes` — temporal-independence — now declared `None` in the constructor but set only inside `read`; `_tier_folders`, `_story_files`, `_parent_story_scope` and `_AggregateTiers.__init__` (203) use them as set, so any of them called before `read` fails on `None`. (still open from round 1)
- graph_overlay.py:27, :32, :167-176, :127, :146 `_TIER_FILES`, `_BEHAVIOR_TIERS`, `_story_semantic` — eliminate-duplication — which node type a file becomes is still decided three ways in this file (a tuple table, a dictionary by suffix, an if-chain) and the caller hands it to `BehaviorFile` and `StoryTestFile` (`fact_files.py:209-211, 227-229`), though *FactFile* says each kind of file says which node type it becomes; *AccessFile* answers it a fourth way (`access_facts.py:33-44`). (still open from round 1)
- graph_overlay.py:27, :33-37, :46-47, :136, :169-175, :219, :226, :263, :269, :277 — eliminate-duplication — LERN's node type names (`"NodeRoot"`, `"ClientRoot"`, `"Route"`, `"StoryShared"`, `"PlaywrightSpec"`, …) are string literals written over and over here, in `fact_files.py:169, 199`, and in every rule's `node_types` (`lern_tier_rules.py`, `shared_story_rules.py`, `shared_behavior_rules.py`); fact names have one home in `fact_names.py`, node type names have none. [2]
- graph_overlay.py:198-208 `_AggregateTiers.__init__` — keep-operations-single-responsibility — the constructor adds the tier nodes to the graph (`in_graph.add_file`, 205) while the object is being made. (still open from round 1)
- graph_overlay.py:135 `_tier_folders` — provide-meaningful-context — `folder.startswith("src/")` fixes LERN's source folder as a literal inside the reading, while the pattern holds its other folders as named attributes (`story_test_folder`, `default_workspace_folder`). (still open from round 1)

### cdd_guidance/patterns/lern_domain_driven/lern_domain_driven.py

- No findings.

### cdd_guidance/patterns/lern_domain_driven/practices/bdd/rules/shared_behavior_rules.py

- No findings.

### cdd_guidance/patterns/lern_domain_driven/practices/ddd/rules/lern_tier_rules.py

- No findings.

### cdd_guidance/patterns/lern_domain_driven/practices/stories/rules/shared_story_rules.py

- No findings.

### cdd_guidance/patterns/mern_domain_driven/mern_domain_driven.py

- mern_domain_driven.py:12 `MernDomainDriven` — eliminate-duplication — MERN shares Express, React, Node and the story test tiers with LERN but still has no `practices/` folder and so none of LERN's graph rules; its markdown restates the rules as text, judged only by reading. (still open from round 1)

### cdd_guidance/patterns/pattern.py

- No findings.


## Design proposals

Each is a change across several files that would end several findings at once. 31 and 39 overlap and are best made as one change.

1. **One reader for a story file in code** (round 1 S1, still not done). Make the block reader the only parser: `StoryBlock` gains `keyword` and `description_lines`, `CodeStory.from_block` builds backgrounds, scenarios and steps from blocks, and `StorySyntax`/`BraceSyntax`/`PythonSyntax` shrink to example names and description marks; the shared block lines move onto `StoryBlock`. Ends: code_story_map.py:83 `StorySyntax`, code_story_map.py:174 `_balanced`/`_outside_scenarios`, brace_story_file.py:16 `_STORY…`, brace_story_file.py:101 `BraceBlock` duplication, python/nodes.py:15 `PythonSyntax`, story_file.py:113 `read_step_code`, code_story_map.py:352 `getattr(background, "body")`, story_map.py:314 `take_code_from`, python/story_file.py:126 `_is_inside`.
2. **A story file's language owns its imports and examples.** Move `StorySource`'s import and declaration reading onto the per-language syntax, reading imports through `source_code`'s `PythonImports`/`ScriptImportClauses`. Ends: story_recording.py:89 `StorySource`, story_recording.py:30 `_NAMED_IMPORT…`, story_recording.py:50 `example_source_file`/`imported_files`, shared_story_file.py:35 `_EXAMPLES_MODULE`.
3. **The recording is the one way onto the graph.** `StoryRecording` offers `link(kind, parent, node)` and keeps its fields private; each node kind gets one `record(recording, parent)` and says how it aligns. Ends: story_recording.py:214 `graph`, story_recording.py:212 public attributes, story_recording.py:213 `practice`, story_recording.py:242 `_align`, story_map.py:343 `record` signatures, story_recording.py:343 `file_of`.
4. **Each code node takes its own code, and a code map holds its project.** `CodeHeld.take_code_in(language, kept)` (with `Step` adding its body), `CodeStoryMap` built with its project, and `StoryFile.stories` taken whole by `_take_stories(holder, file)`. Ends: code_story_map.py:512 `_adopt_code…`, code_story_map.py:570 `self.project`, code_story_map.py:637 `_take_stories`, story_map.py:314 `take_code_from`.
5. **Script languages as values, not subclasses.** One `ScriptStoryMap` instance per language (extension, language, seed file, import line), with the step library kept in one place; delete `ScriptStory`, the TypeScript/JavaScript node classes and the `typescript/__init__.py` re-export. Ends: typescript/nodes.py:10, javascript/nodes.py:10, script_story_map.py:29 `ScriptStory`, script_story_map.py:24 `script_story_file_suffixes`, javascript_story_map.py:29 `seed_file`, typescript/__init__.py:1.
6. **Steps, examples and writing helpers move onto the nodes.** `Scenario`/`Background` answer `flat_steps`, `own_backgrounds`, `examples_lines`; `Examples` holds a dict instead of being one; `holding` and `_renumber` become private node operations. Ends: story_file.py:113 `flat_steps`, story_map.py:730 `_steps_key`/`_renumber`, story_writing.py:37 module functions, story_map.py:439 `Examples(dict)`, story_map.py:222 `holding`.
7. **StoryTree holds every read of the Stories graph once.** Give `StoryTree` the cached reads the link writers each keep (`examples`, `examples_by_file`, nodes by file, the files held, steps), one walk up the tree, and an instance `key_of`/`scenario_of` that the rules and UX call; give `StepRule` the tree instead of its own fact reads. Ends: graph_reading.py:86 `StoriesReading.steps`, graph_reading.py:132/391 `_files_held`/`story_files`, modelled_areas.py:47 `examples`, story_tree.py:41 `of_graph`, story_tree.py:151 `key_of`, story_tree.py:256 `_ancestor`, story_tree.py:246 `_nodes_by_file`, story_tree.py:223 key split, scenarios.py:50 `StepRule.text`, scenarios.py:285 `_earlier_steps`.
8. **One model-link index per model, and named outcome types.** Build one `ModelHeadings` (nodes by file, owner by operation) per model reading and hand it to `StoryLinks`, `TermLinks` and `RealizationLinks`, with an operation's owner asked through a Clean Engineering / DDD seam rather than the `owner` fact; replace `CALLS_REACH_*` and `REALIZATION_REACHES_*` with one enum the rule imports. Ends: graph_reading.py:19 low-coupling, graph_reading.py:46 `CALLS_REACH_*`, realization_links.py:23, realization_links.py:43, realization_links.py:99, story_tree.py:246 (with 1).
9. **The Stories reading holds one `ProjectStoryFiles`, which holds format objects, not names.** Make it once per read in `StoriesReading`; give it the JSON, markdown and code adapters as objects; let each code adapter answer `for_tests_root(folder)` keeping its settings; move epic lookup and merge onto `StoryMap`/`Epic`; return `Story` objects from `story_tests`. Ends: graph_reading.py:143 `_story_files`, graph_reading.py:233 `_story_tests`, project_story_files.py:81, :190, :46, :106-139, :102/114, opened_story_map.py:110.
10. **`NameFacts` owns name reading, with an opening-class enum.** Move the name_facts.py module functions onto `NameFacts`, have it judge `generic_handler` itself, and export the opening classes and the band outcome as enums the story-map rules read. Ends: name_facts.py:54-88, name_facts.py:104/122, name_facts.py:120, rules/story_map.py:15-18.
11. **Spec support named as spec support, run by a tier.** Move `story_channel.feature.py` into the heavy tier (or delete it) and place `template_checks.py` where spec support lives, so the graph stops judging both as production. Ends: story_channel.feature.py:1-6, template_checks.py:42/124, and with the practice answering its rules by slug, rules/__init__.py:67 `BY_SLUG` and template_checks.py:129.
12. **One markdown text vocabulary from `harness/markdown`.** Stories uses `link_words` and `heading_anchor` from `harness/markdown/markdown.py` and deletes its own `unlink`, `_LINK` and `heading_anchor`; `StoryMapLinks` keeps each heading's line from the one walk `_entries_of` already makes. Ends links.py:50 `heading_anchor`, links.py:21-27 `unlink`, links.py:126-136 `_heading_line`.
13. **One outline notation object.** A `StoryOutlineLine` (or one class per node kind on the story map) that both parses and writes `(E) name`, `(S:kind) actor --> name` and `* estimate`, used by the markdown outline reading, the sketch, `outline_lines` and `StoryMapLinks._entries_under`; the sketch's indent becomes that notation's depth. Ends map_reading.py:26-28 patterns, sketch_story_map.py:217-232 / :259-272 branch, sketch_story_map.py:103… `"    "`, sketch_story_map.py:41 `_epic_name`, and the anchor rebuild in links.py:161-171.
14. **Step keywords owned by `StepType` and `Step`.** Read a keyword with `StepType(word)`, chain And/But with `Step.continue_with`, and name the continuation words once on `Step`. Ends scenario_file.py:38 `_PHASES` / :262-278 `_take_step`, scenario_file.py:35 `_ITALIC_STEP` (with one step-line pattern in markup), and the same tables in sketch, `code_story_map.py` and `python/shared_story_file.py`.
15. **One thin slice, by identity, drawn by every format; read back or deleted.** `ThinSliceLayout` matches increments' stories by identity and hands each surface typed headers; a surface holds its layout and places, so `epic_header` and `lane` take only the node; Miro draws `ThinSliceLayout` too; the three `load_thin_slice` readers are either wired into the render of a thin slice drawing or deleted with their specs. Ends diagram_story_map.py:406-414 `_by_column`, :420 `epic_headers`, :447-454 `ThinSliceSurface`, whiteboard nodes.py:211-213 `_map_story`, miro nodes.py:74 `table_row`, miro nodes.py:216-234, drawio nodes.py:438, miro nodes.py:251, whiteboard nodes.py:151 `load_thin_slice`.
16. **A scenarios file read into typed lines and returned as one result.** `ScenarioFileReading.read()` answers the `ReadScenarioDocument` (lines, tree heading, examples, sections) with its scenario class held, not passed; each heading line is made with its node and a typed "what it said" per node kind; step lines belong to their scenario or background; `IncrementLines` and `MarkdownStep` keep named values instead of tuples. Ends scenario_file.py:115-134, :92 `scenario_class`, read_lines.py:39… `Any`, read_lines.py:41/:73 `.node`, read_lines.py:79-110 `SectionSteps`, read_lines.py:120 `written_lines`, markdown nodes.py:60/:138 `read_lines`, nodes.py:93/:155/:279 `heading_written`, thin_slice.py:37/:40, markup.py:86.
17. **One format adapter contract for the drawn story maps.** `parse` and `take_board` fill and answer `self` in every format (or `type(self)()` everywhere); one name for the elements a node draws; Miro's SVG reading becomes a small document class like `harness.drawio`'s file; the cell roles are a value of `DiagramStoryCell`, named once; `_KeptPlaces` reads boxes from `DrawioCell.box` and refuses a drawing it cannot read. Ends drawio nodes.py:403-413 `parse`, whiteboard nodes.py:138-143 `take_board`, whiteboard nodes.py:66/:75 naming, miro nodes.py:292-313, miro nodes.py:186 `ROLES`, diagram_story_map.py:104 `DiagramStoryCell`, drawio nodes.py:254-297 and :262-272 `_KeptPlaces`.
18. **Format packages export through one path.** Delete the six package `__init__.py` re-exports (or make the package path the one every importer uses, `stories.py` included), and move `StoryMapLinks` and `CODE_LINK` beside `story_map_files.py` so draw.io imports no markdown module. Ends the six `__init__.py` findings and drawio nodes.py:28.
19. **Typed node edits in the Story UI, with move and add-before on the model.** Give the Python story model `move_to_end` (or `move_before(None)` under a parent) and a `before` argument on `new_epic` / `new_story`, and an And-step tool and a keyword edit on `Step`; let the views commit a drop as one call with the dragged node and the node it lands before. Ends: story-map-client.ts:62 `reorder`, story-map-nodes.ts:35 `addedBefore` (both findings), story-map-nodes.ts:206 `newStep`, story-map-views.tsx:661 `moveInto`, story-map-views.tsx:1406 `StepEditor`.
20. **One drag controller for the hierarchy.** One parameterised drag handler (kind, list key, id) held by a small drag object instead of five functions, and the empty-row zone as the same handler with no target. Ends: story-map-views.tsx:362/407/451 duplication, :368 `onMove` parameters, and most of :612 `StoryHierarchyView`'s size.
21. **A real row (lane) on the page.** Model the row of an epic's own stories as its own class (or a property of `EpicOnPage`) instead of a fake `EpicOnPage` with the epic's id, and draw nested epics as rows rather than flattening them. Ends: story-map-nodes.ts:103 `EpicOnPage.of`, :105 `storiesUnder`, story-map-views.tsx:877/:965 id comparisons.
22. **One served-kind type.** A `ServedKind` enumeration (Story, Scenario, Step) carrying its heading, edge, fact and linked Stories types, used by `Served`, `ServesStories`, `StoryLink` and `UxReading`. Ends: graph_reading.py:50 `_SHOWN`, nodes.py:89-126 forwarders, nodes.py:128/132 naming, served.py:18 `KINDS`, served.py:25-33 unused properties, story_link.py:28 `kind: str`.
23. **Ask Stories, DDD and Clean Engineering through their trees.** Use `StoryTree` (`story_of`, `step_text`, `step_phase`, `_above`) and give DDD and Clean Engineering one "class named" / "property of class" question each. Ends: explorer_tree.py:87, :67-68, graph_reading.py:366 `_steps_reading`, :370 `_screen_of`, :326/:377 low-coupling, :59 `ands`.
24. **Split format description from the map.** Move `map_file_suffixes`, `not_a_map_failures`, `holds_screens`, `content_beside`, the name spellings `_NAME_MARKS` needs, and node copying onto a format object each adapter owns, and let each node copy its own fields. Ends: ux_map.py:47 SRP, ux_map.py:94 `copy_of`, graph_reading.py:43 `_NAME_MARKS`, graph_reading.py:192 tuple, graph_reading.py:114 format/reader/adapter naming.
25. **`Served` owns the whole "what this serves" notation.** Give `Served` the Domain terms line, the "line under a heading" reader, and a control's place name (region and control joined by a separator of UX's own), give `Screen` the property for the terms it names, and have the draw.io callout, the board card, the HTML page and the drawio-ux state all write and read lines through it (the command line receives finished lines, as it already does for links). Ends: whiteboard/nodes.py:311 `_listed`; drawio/nodes.py:278 terms; drawio/nodes.py:285/:296 `KEY_SEPARATOR`; html/nodes.py:254 Stories line; drawio_ux.mjs:568-572 notation.
26. **One story explorer tree.** `ClaudeDesignStoryMap` draws its explorer and its context panels from `ExplorerTree`, whose entries are typed and keyed by name, and Stories answers "the screens a node is shown on" and "a scenario's steps with their ands". Ends: story_canvas.py:307 duplicate builder, :311 one-letter keys, :69/:356 tuples, :399 `shown_on`/`_steps_of`, :36 `shownOn` string, part of :25-30 coupling.
27. **Format nodes reach their map as their parent; formats hold the formats they use.** A screen, region or control read from a file asks its parent map for node types and screens, so `ux_map` and `control_type` stop being passed; the map chooses which control class a record makes; one screen lookup by name; the Claude Design format holds its HTML page format as a part instead of building JSON and HTML maps per call; the draw.io adapter's timeout is read, not copied. Ends: json/nodes.py:55 (hold-state), :58, :212; drawio/nodes.py:229, :424; claude_design/nodes.py:67.
28. **`ViewText` reads code; `Component` and `ComponentMember` write their own edits.** Move statement end, bracket depth, blank skipping and function-body finding onto `ViewText`; let a member answer its marking edit (through `KEPT_MARK.line_for`) and its insertion edit, and a component its prop edits, so `ReshapedView` only pairs components and collects results once. Ends: front_end_view.py:384 duplication, :688, :689-773, :295 method count; reshaped_view.py:40, :65-79, :69-70.
29. **The abd look and the desktop screen size in `look.py`.** Export the palette and fonts there and have the fixture bar, the context panel and the screen boards use them. Ends: fixture_screen.py:14-15; story_canvas.py:37-45; claude_design/nodes.py:56-57.
30. **`drawio_ux.mjs` as the `write` command only.** Delete the interactive commands and the cwd state file, and split the writer into screen, region and edge writers that share one two-way edge merge, one column grouping and one column-height measure. Ends: drawio_ux.mjs:765-931, :506 function lengths, :600-619 duplication, :341-348 duplication, :446 parameters, :145-757 free functions.
31. **Format answers its own groups.** Give *Format* `is_whiteboard`, `is_diagram`, `is_canvas`, `is_sketch` and `is_saved_by_render` (from `Format.GROUPS`), take a *Format* (not `str`) at every render seam, and delete `WHITEBOARD`, `SAVED_GROUPS`, `CANVAS` and both `_SKETCH` constants. Ends: render.py:83 (use-consistent-naming), render.py:78 `render` (Format rebuilt), rendered_file.py:22 `WHITEBOARD`/`SAVED_GROUPS`, rendered_file.py:27 `_SKETCH`, generate.py:17 (low-coupling).
32. **The render holds its request and its fidelity.** Let `RenderRequest` carry format, source, paths and the *FidelityGuidance*, write and read itself for the worker, and answer its placement, root, reshape and scope; `RenderedCode`, `RenderedFile.from_graph` and the worker take the request. Ends: render.py:99 `_render_files`, render.py:127 `_saved_by_declared_paths`, render.py:205 `_drawn_from`, render_order.py:50 `RenderOrder`, render_worker.py:25 `_fidelity_of`, rendered_code.py:73 `RenderedCode.__init__`, rendered_file.py:163 `from_graph`.
33. **One saved-file writer and one kept-content merge per drawing type.** A single "write onto the file already there and list what was kept" operation used by `RenderedFile`, `RenderedSections`, `RenderedCode` and `RenderedCanvas`; `KeptDocument` split into a markdown keeper and drawing keepers that work on `harness/whiteboard`'s and the draw.io document's objects, with one "drawn new" step; one cutter of a text into headed sections. Ends: rendered_file.py:69/173 (save duplication), rendered_code.py:143 `_sections`, kept_document.py:51 `onto`, kept_document.py:118 `_whiteboard`, kept_document.py:60 (swallowed parse), kept_document.py:90 (untyped dicts), kept_document.py:95/137 (duplication), render_result.py:149/200 (`migrate`/`decide` on the base).
34. **The work list answers the listed fidelities and their text; the action knows its own name.** `WorkList` answers `fidelities` and `text_of(item)` (the non-blank-parts join) once, and `GuidanceAction` logs under its own operation's name. Ends: document.py:35, document.py:37, generate.py:80, validate.py:88/106/154, validate.py:209 `_logged_session_action`.
35. **Declared paths and fidelity stages answer for themselves.** `DeclaredFile` answers the folders a templated path names (replacing `partition("{")` and `_NOT_ONE_FOLDER`), the fidelity collection answers a fidelity's predecessor, and the fidelity answers its reading formats. Ends: checked_fidelity.py:89 `_written_at`, generate.py:99 `_fidelity_before`, source_files.py:90 `_rendering_formats`.
36. **CheckedGraph as a value built once.** Build the graph in a factory, keep `found`, `violations`, `accepted` and the violation/candidate split as cached properties, and let *CheckedFidelity* answer its practice. Ends: checked_graph.py:114/119/124, checked_graph.py:55 (queries that mutate), checked_graph.py:128/175, report_text.py:114/159, report_files.py:44 (dead branch, once the graph file is chosen in one place).
37. **Instructions are instructions, not tools.** Drop the no-op tools `review_sketch`, `mark_iterate_round`, `partition.index` and `partition.segment` into the recipes' text (or make them record something real). Ends: sketch.py:101, iterate.py:21, partition.py:112.
38. **One gap type in its own file of `cdd_guidance/align`.** Move *AlignmentGap* (with its kinds as one enumeration, and a factory for a callout's gap) below both files, have *CalloutAlignment* answer it, and drop `_CalloutGap` and `SessionAlignment._callout_gap`. Ends callout_alignment.py:29 `_CalloutGap`, format_alignment.py:81 `AlignmentGap.__init__`.
39. **Format and the written files answer what alignment asks today with strings.** (Overlaps 31: together they are one change to *Format*.) *Format* gains `is_document`, `is_saved_by_render` (replacing `SAVED_GROUPS`) and `holds_links`; the fidelity's written files gain "the files there of these formats", and alignment uses `DeclaredOutputs.code_folders()`. The chosen formats are held as *Format* objects. Ends format_alignment.py:39 `SAVED_GROUPS`, :65 `_DOCUMENT_GROUP`, :333 `_compared_formats`, :343 `_documents`, :440 `_code_formats_missing`, :216 `follow_up`, callout_alignment.py:114 `_holds_links`.
40. **The session reads listed files into its graph through one operation.** Make `SessionExplorer._read_listed` (or an operation on the session's graph) the one public way, holding the overlays and working practices itself; *CalloutAlignment* asks it and uses `SavedPractice.root_in`, and splits what remains of `_read_graph` into placing nodes and finding crossing edges, made once in its constructor. Ends callout_alignment.py:90 `gaps`, :102 `_read_graph` (hold-state), :106 `_read_graph`, :97 `_read_graph` (single responsibility), :86 `gaps` (temporal-independence).
41. **A document object inside format alignment.** `_FidelityAlignment._documents` answers objects holding one document's files by format, its leading format and its `placed_at`, with `gaps`, `read` and `compared` on it; *SessionAlignment* holds one *Render* and hands it each gap's *FidelityGuidance*, not its slug. Ends format_alignment.py:364 `_document_gaps`, :401 `_compared`, :482 `align`.
42. **Each fact file decides its own kind and node type, from the file's name before it is read.** `FactFile.of(root, path)` picks the subtype by name (LERN's *NodeRootFile*, *RouteFile*, *BehaviorFile* per tier, *StoryTestFile* per tier; web access's *AccessRoute*, *AccessNode*, … as subtypes of *AccessFile*), each with its node type as a class constant that `fact_names.py` (or a `node_types.py` beside it) names once and the rules import. Ends access_facts.py:33 `node_type`/`facts`, access_facts.py:37 node type literals, graph_overlay.py:27 `_TIER_FILES`/`_BEHAVIOR_TIERS`/`_story_semantic`, graph_overlay.py node type literals, fact_file.py:22 `at` (`*held`).
43. **The LERN reading keeps one fact file per path.** `_LernReading` reads each file once into a cache of *LernFile*s by path, holds the test setup text it gives *NodeRootFile* at construction, and *AggregateFolder* asks that cache. Ends fact_files.py:74 `unreset_instances`, fact_files.py:263 `AggregateFolder`, and with the reading built whole in its constructor, graph_overlay.py:79 `ddd`/`story_nodes` and :198 `_AggregateTiers.__init__`.
44. **The session probe answers a typed section and makes its repository in `run`.** A probe result built with *ProbeOutcome*'s colours (or a small typed record) replaces `ProbeReport`; the throwaway repository is made and removed inside `run`; loop marking happens in `_run_actions` before the checks read the log. Ends session_probe.py:18 `ProbeReport`, :30 `__init__`, :76 `_report`, :21 literal.
