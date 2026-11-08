# Story model

*StoryModel* is one story map: epics, the sub-epics nested under them, the stories in each, and the increments that slice them, then each story's backgrounds and scenarios down to steps and examples. A nested epic is an epic whose parent is an epic. An increment is a thin slice: a name, an outcome, slicing notes, a decision, and the stories in that slice. Every node is a graph node (*ModelNode*), so a loaded model is also the stories practice's part of the knowledge graph.

Each format is a *StoryModel* subclass with its own node subclasses, listed by `Stories` under `formats`: sketch, markdown, json, drawio, miro, python, typescript, java, javascript. `StoryModel(source)` copies any model into the subclass's node types, and a format's `copy_of(source)` makes that copy with the format's own settings (it is asked of a model, not its class, because a code format copies with its own `tests_root`; a UX map's `copy_of` is asked the same way); each story, scenario, and background makes its parts through its format's `scenario_type`, `background_type`, and `step_type`. `parse` reads text in that format and `render(canonical, previous)` writes a model out. *StoryMapFiles* (`story_map_files.py`) is the one place that knows a story map's file name and a story's own file name, and finds the story map in or above a folder (`nearest`), the markdown maps below it (`markdown_below`), each story's own file below it (`story_files_below`), and the files scenarios are written in (`scenario_files_below`), entering each folder's `.context` and no folder a working-copy scan never enters (`skips_folder`). The Stories practice registers itself on *StoryNode* (`StoryNode.register_practice(Stories)`), so the model never imports its practice. Markdown, JSON, and the code formats carry scenarios, steps, and examples; the diagram formats (drawio, miro) stop at stories and still read increments. The Claude Design story canvas, which shows the stories on their screens, is a *DiagramStoryModel* the UX practice draws (`practices/ux/model/claude_design/story_canvas.py`).

```
story_map = Stories().read_folder(folder)       # story-map.md (or .json), increments, scenarios
drawio = DrawIOStoryModel().render(story_map)
```

# practices/stories/model

- **Purpose:** Keep stakeholder behaviour as one story model — epics, stories, and increments, then scenarios and steps — so a markdown file, a diagram, and a test file stay the same hierarchy every later fidelity reads.
- **Seam (terms):** StoryNode, StoryModel, Epic, Increment, Story, StoryType, Background, Scenario, Step, StepType, Example, Examples, SourceLocation, and one StoryModel subclass per format
- **Dependencies (one-way):** harness/graph (*ModelNode*, *Graph*), harness/annotations (*Name*), practices/clean_engineering/model (*CodeBody*, *CodeLanguage*, *WrittenBlock*, *CallGraphEntry*), practices/sketch_document (*SketchOutline*), harness/guidance (*SketchLens*)

These dependencies are owned by the modules named; this model only uses them. Each node writes itself onto the stories practice graph (`StoryModel.record`, through a *StoryRecording*); cross-practice links from steps and examples to Clean Engineering nodes are recorded there.

## StoryNode : ModelNode

Every epic, increment, story, background, scenario, step, and example. It carries the facts story-map graph rules read.

+ StoryNode(name: str, sequential_order: int, graph: Graph | None = None)
------
+ name: str
+ sequential_order: int
+ estimate: str
	// shaping size, such as "approx 2-3 more stories"; meaningful on an epic
+ written: WrittenBlock | None
	// how this node was written in code: a sub-epic file, a story, a background, or a scenario. None outside code
+ setup: CodeBody
	// the code inside a story or scenario that is not a background, scenario, or step
+ opening_token, opening_class, child_count, child_label, child_band, near_duplicate, generic_handler, shared_verb, one_time_task, artifact_name, camel_case_path
	// the facts graph rules read; load_map_facts fills them
----
+ load_map_facts(): None
+ opens_with_verb(): bool
+ load_child_band(count: int, label: str): None
	// child_band is "error" unless the count is 0 or 4 to 9
+ take_code_from(source: StoryNode): None
	// keeps written and setup when the node is copied into another format or cloned
+ clone(): StoryNode
	// a copy of this node, including its children

## StoryModel : StoryNode

+ StoryModel(source: StoryModel | Graph | None = None, graph: Graph | None = None)
	// source set: each epic and increment becomes this format's epic_type and increment_type, each story its story_type
------
+ epics: list[Epic]
	// composition — an epic has no model outside this story model
+ increments: list[Increment]
	// composition — an increment has no model outside this story model
+ examples: Examples
	// examples shared by the whole map
+ epic_type: type
+ story_type: type
+ increment_type: type
----
+ source_texts: dict[str, str]
	// the text of each file the map was read from, by the path its nodes name
+ links: StoryMapLinks | None
	// where each node links in the folder a render placed the map in
+ take_scenarios(stories: list[Story], file: str): None
	// the scenarios of each story read from a story test go to the map's Story of the same name
+ record(practice, on_node: Callable | None = None): None
	// each epic, story, background, scenario, step, and example adds itself to the stories practice
+ every_epic(): list[Epic]
	// every epic and nested epic, each before its own children
+ every_story(): list[Story]
+ leaf_epics(): list[Epic]
	// each epic's innermost sub-epics, or the epic when it has none
+ stories_named(names: list[str]): list[Story]
	// the map's own stories names name, in that order: how an increment read from a thin slice finds its stories
+ place_in(file: str): None
	// names file on every epic and story that names no file yet
+ append_epic(epic: Epic): None
+ append_increment(increment: Increment): None
+ clone(): StoryModel

## Epic : StoryNode

+ Epic(name: str | Epic, sequential_order: int = 0, story_class: type | None = None)
	// given an epic: copies name, order, estimate, child epics, and stories, each story in story_class
------
+ epics: list[Epic]
+ stories: list[Story]
+ examples: Examples
+ has_epics: bool
+ depth: int
+ is_sub_epic: bool
	// its parent is an epic; it records as a SubEpic
+ top_epic: Epic
	// the epic of the map it sits under; itself when it is one
----
+ estimate_label(): str
	// "* {estimate}". Load strips the star and any HTML
+ every_epic(): list[Epic]
+ every_story(): list[Story]
+ leaf_epics(): list[Epic]
	// the epics whose stories sit in columns: its innermost sub-epics, or itself when it has none
+ append_epic(epic: Epic): None
+ append_story(story: Story): None
+ place_in(file: str): None
	// names file on this epic and everything under it that names no file yet
+ span_columns(): int
+ diagram_span_columns(): int
+ tree_depth(): int

## Increment : StoryNode

+ Increment(name: str | Increment, sequential_order: int = 0, stories: list[Story] | None = None, story_class: type | None = None)
------
+ outcome: str
+ slicing_notes: str
+ decision_prompt: str
+ source: SourceLocation | None
+ stories: list[Story]
	// the stories in this thin slice. Each story still belongs to its epic, and records this increment
----
+ clone(): Increment

## Story : StoryNode

+ Story(name: str | Story, sequential_order: int = 0, story_type: StoryType = StoryType.USER)
	// given a story: copies name, order, type, actors, domain terms, evidence, backgrounds, and scenarios
------
+ story_type: StoryType
+ increment: Increment | None
+ actors: list[str]
+ domain_terms: list[str]
+ evidence: list[str]
+ backgrounds: list[Background]
+ scenarios: list[Scenario]
+ scenario_type: type
	// the scenario class this story's format copies scenarios into
+ top_epic: Epic | None
	// the epic of the map it sits under
+ code_key: tuple
	// name, actors, evidence, and backgrounds: while it is the key the story was read with, its code stands
----
+ load_map_facts(): None
	// also flags a near-duplicate of a later sibling
+ clone(): Story

## StoryType

+ USER = "user"
+ SYSTEM = "system"
+ TECHNICAL = "technical"
------
+ outline_mark: str
	// (S), (S:system), or (S:technical)
----
+ from_mark(kind: str | None): StoryType

## Background : StoryNode

+ Background(name: str | Background = "background", sequential_order: int = 1)
------
+ steps: list[Step]
+ examples: Examples
+ code_key: tuple
----
+ clone(): Background

## Scenario : StoryNode

+ Scenario(name: str | Scenario = "", sequential_order: int = 0)
	// its story is its parent; a scenarios file links a scenario to its story only by the name its section is headed with
------
+ backgrounds: list[Background]
+ steps: list[Step]
+ examples: Examples
+ is_outline: bool
+ evidence: list[str]
+ source: SourceLocation | None
+ code_key: tuple
----
+ steps_in(step_type: StepType): list[Step]
+ when_then_runs(): list[tuple]
	// a When after a Then starts the next run
+ clone(): Scenario

## Step : StoryNode

+ Step(text: str | Step, step_type: StepType | None = None, sequential_order: int = 0, keyword: str = "", concepts, values, actor: str = "", source: SourceLocation | None = None, name: str = "")
------
+ text: str
+ step_type: StepType | None
	// given, when, or then. An and keeps the step type of the step it continues
+ keyword: str
	// Given, When, Then, And, or But
+ ands: list[Step]
+ concepts: list[str]
+ values: list[str]
+ actor: str
+ source: SourceLocation | None
+ call_graph: list[CallGraphEntry]
+ body: CodeBody
	// the step's test code as read, in the language it was written in. Empty outside code
+ is_continuation: bool
+ phase: str
+ callees: list[str]
	// the capitalised concepts the step names: the domain classes it reaches
+ code_key: tuple
	// keyword, text, and body
----
+ clone(): Step

## StepType

+ GIVEN = "given"
+ WHEN = "when"
+ THEN = "then"

## Example : StoryNode

+ Example(name: str, value: Any = None, sequential_order: int = 0, scope: StoryNode | None = None)
------
+ value: Any
	// a field map by default
+ scope: StoryNode | None
	// the node that shares this example: a background, a scenario, a sub-epic, an epic, or the story map
----
+ cells(): dict
+ as_code(): str
+ clone(): Example

## Examples : dict

Example name to value, for one scope.

+ Examples(scope: StoryNode | None = None)
------
+ scope: StoryNode | None
----
+ table(): list[dict]
+ clone(scope: StoryNode | None = None): Examples

## SourceLocation

+ SourceLocation(file: str, line: int = 0, end_line: int = 0, text: str = "")
----
+ render(): str
	// file:line-end_line

---

## Formats

Each format class below is a *StoryModel* subclass. Its node subclasses (`MarkdownEpic`, `DrawIOStory`, …) set the node types `StoryModel(source)` copies into; a format overrides only what it reads or writes differently.

## SketchStoryModel : StoryModel

The `sketch` format: the stories section of an integrated sketch. Nodes: SketchEpic, SketchStory, SketchScenario, SketchBackground, and SketchStep, which write their own sketch lines (`sketch_lines`) and read the lines nested under their own (`read_lines`, from a *SketchLines*: each entry `under()` gives is the line naming a node, `text`, then the lines `nested` under it).

------
+ epic_type: SketchEpic
+ story_type: SketchStory
----
+ parse(text: str): SketchStoryModel
	// fills this map and returns it
	-> SketchOutline.body_for
	-> read_lines
+ render(canonical: StoryModel | None = None, previous: str | None = None): str
	// copies canonical into a sketch map, which writes itself
	-> save
+ save(): str
	-> SketchEpic.sketch_lines

## MarkdownStoryModel : StoryModel

The `markdown` format: `story-map.md`, the scenario files beside it, and the increments file. Nodes: MarkdownEpic, MarkdownStory, MarkdownIncrement, MarkdownScenario, MarkdownStep.

------
+ epic_type: MarkdownEpic
+ story_type: MarkdownStory
----
+ from_workspace(root: Path, project: Path | None = None): MarkdownStoryModel | None
	// each story takes the scenarios of the scenario-file sections headed with its name (`MarkdownScenario.sections_in`, *StorySection*), and the increments of `StoryMapFiles.thin_slicing`
+ parse(text: str, file: str = ""): MarkdownStoryModel
	// read from file, each epic, sub-epic, story, and scenario names the line it is read on, as it is read
+ render(canonical: StoryModel, previous: str | None = None, workspace: str | None = None): str
	// in a workspace folder, each story that has its own markdown file links to it
+ save(): str

## JsonStoryModel : StoryModel

The `json` format. Nodes: JsonEpic, JsonStory, JsonIncrement, JsonScenario, JsonBackground, JsonStep; each reads its own record (`from_record`) and writes it (`as_record`).

----
+ from_workspace(root: Path): JsonStoryModel | None
	// every epic and story names story-graph.json (`place_in`)
+ parse(text: str): JsonStoryModel
	// fills this map and returns it
+ render(canonical: StoryModel, previous: str | None = None): str
	// copies canonical into a JSON map, which writes itself
	-> save
+ save(): str
	// this map as story-graph.json text

## DiagramStoryModel : StoryModel

The layout shared by the diagram formats. Nodes: DiagramEpic, DiagramStory, DiagramIncrement, each also a *DiagramStoryNode*.

------
+ max_sub_epic_depth: int
+ actor_y: int

## DiagramStoryNode

+ x: int
+ y: int
+ width: int
+ height: int
----
+ place(side: str, destination: DiagramStoryNode): None
	// side is above, below, after, or before
+ add(child: DiagramStoryNode): None
	// the child sits under its parent and to the right of the previous child, then stretch()
+ stretch(): None
	// width becomes the sum of the children's widths, then the parent stretches
+ role(): str
	// epic, subepic:{depth}, story:{type}, actor, or estimate

## DrawIOStoryModel : DiagramStoryModel

The `drawio` format. Nodes: DrawIOEpic, DrawIOStory, DrawIOIncrement.

----
+ parse(text: str): DrawIOStoryModel
	-> load(text)
+ load(text: str): DrawIOStoryModel
	// reads cells by where they sit, not their order in the file
+ render(canonical: StoryModel | None = None, previous: str | None = None, workspace: str | None = None): str
	// in a workspace folder, each cell links to its story-map.md entry
+ save(): str

## MiroStoryModel : DiagramStoryModel

The `miro` format: a canvas-composer SVG, with increments as a thin-slice table. Nodes: MiroEpic, MiroStory, MiroIncrement.

----
+ parse(text: str): MiroStoryModel
	-> load(text)
+ load(text: str): MiroStoryModel
+ render(canonical: StoryModel | None = None, previous: str | None = None): str
	-> save
+ save(): str

## CodeStoryModel : StoryModel

A story map written as test code: one file per sub-epic holding its stories, under epic folders. Nodes: CodeEpic, CodeStory, CodeScenario, CodeIncrement, each also a *CodeStoryNode* (`slug`, `snake`, `pascal`, `camel`, `name_from_slug`).

------
+ language: CodeLanguage | None
	// each language model sets its instance
+ tests_root: str
+ story_file_suffixes: tuple[str, ...]
	// how a story file in this language ends; the first is the one it writes
----
+ is_story_file(path): bool
	// class operation: a file this language reads stories from; Java and TypeScript also leave out helpers and examples
+ parse(external: dict[str, str], on_file=None): CodeStoryModel
	// external is the path-to-content map of the test tree
+ load(external: dict[str, str], on_file=None): CodeStoryModel
	// the one load for every language: each story file under the tests root is one sub-epic
	-> story_type.load_all(text)
	-> story_file(text).read(stories, path)
+ render(canonical: StoryModel, previous: dict[str, str] | None = None): dict[str, str]
	Invariant: previous is the path-to-content map already on disk, never one text
	// each epic, story, scenario, and step without code in this language takes the previous tree's code for the same names
	-> parse(previous)
	-> adopt_code
+ save(): dict[str, str]
+ adopt_code(kept: CodeStoryModel): None
+ story_lines(story: Story): list[str]
	// read in this language and story.code_key unchanged: every line as read; otherwise the generic spelling
+ scenario_lines(scenario: Scenario, indent: str): list[str]
+ step_lines(clause: StepClause, indent: str): list[str]
+ story_file(content: str): StoryFile | None
	// the file as this language finds its blocks; None for Java, whose stories are written generically
+ file_name, file_header, folder_files, story_open, story_close, story_background_lines, no_scenarios_lines, scenario_open, scenario_close, scenario_background_lines, examples_lines, clauses, verb, step_open, step_close, and_open, and_body_indent, and_close, step_placeholder, empty_block
	// each language overrides the spelling operations; none of them decides what a body holds

## CodeStoryModelError : Exception

## PythonStoryModel : CodeStoryModel

The `python` format: Mamba story tests. Nodes: PythonEpic, PythonStory, PythonScenario. Its blocks are found by *PythonStoryFile*.

## BraceStoryModel : CodeStoryModel

The spelling TypeScript and JavaScript share, with the file header that imports the story-test helpers (`story_test_import`). Nodes: BraceStory, BraceScenario. Its blocks are found by *BraceStoryFile*.

## TypeScriptStoryModel : BraceStoryModel

The `typescript` format. Nodes: TypeScriptEpic, TypeScriptStory, TypeScriptScenario.

------
+ story_test_folder: str
	// the step library folder: the stories workspace root, else the deploy root, unless named
+ story_test_import_path: str
	// property: the import every story file uses for story-test
+ story_test_file_path: str
	// property: where the shared story-test.ts seed is written

## JavaScriptStoryModel : BraceStoryModel

The `javascript` format. Nodes: JavaScriptEpic, JavaScriptStory, JavaScriptScenario.

## JavaStoryModel : CodeStoryModel

The `java` format. Nodes: JavaEpic, JavaStory, JavaScenario.

## CodeStory : Story, CodeStoryNode

A story read from a story file. Each language gives its patterns (`_NAME`, `_STORY_START`, `_STORY_MARK`); reading is one way for every language.

----
+ load_all(content: str): list[CodeStory]
	// class operation: the file split where each story starts; BraceStory also splits at each story call
+ load(content: str): CodeStory
	// class operation: name, description (actor, kind, domain terms, evidence), backgrounds, and scenarios
+ read_code(block: CodeBlock, lead: list[str]): None
	// this story's own code from the block it was written as: background step bodies, setup, written, then each scenario's
	-> CodeScenario.read_code(block, lead)

## CodeScenario : Scenario, CodeStoryNode

----
+ scenario_blocks(content: str): list[tuple]
	// class operation over the language's `_SCENARIO`; BraceScenario reads balanced braces
+ example_names(content: str): list[str]
	// class operation over the language's `_IMPORT` and `_EXAMPLES_LINE`
+ read_code(block: CodeBlock, lead: list[str]): None
	// background and step bodies, setup, and written from the scenario's own block
	-> Step.read_code(block)

## StoryFile

One story file's text as its language finds its blocks: the file's own code above the first story and below the last, and each story block, handed to the story written in it, which reads its own code. *PythonStoryFile* and *BraceStoryFile* find the blocks.

+ StoryFile(language: CodeLanguage, content: str)
----
+ story_blocks(): list[CodeBlock] | None
+ read(stories: list[Story], path: str): WrittenBlock | None
	-> CodeStory.read_code(block, lead)

## CodeBlock

One block of a story file: a story, background, scenario, or step call. *PythonBlock* and *BraceBlock* answer it for their language.

----
+ name, line_span, inside_lines, body
+ written(lead): WrittenBlock
+ split_inside(children): tuple
+ scenarios(), backgrounds(scenarios), steps(skip): list[CodeBlock]
+ setup(children): CodeBody

## StoryRecording

One writing of a story map onto the practice that holds Stories: the practice and graph it writes to, where each node
sits in the map's own file texts, and how many stories it has announced. Each node's `record` adds itself through it.

+ StoryRecording(story_map: StoryModel, practice, on_node: Callable | None)
----
+ write(): None
+ add(story_object, node_id, at: SourceLocation, facts=None): Node
	// named by the object's recorded_name and typed by its recorded_type, at the lines at names
+ name_span(file, name, folder): SourceLocation
+ span_of(node, file, fallback_text=""): SourceLocation

Each node's `record` is handed the node its parent was added as (and the file a background, scenario, or step sits in), not read from `parent`: a story test's scenarios are shared by every Story of that name in a merged map, and an example's graph parent is the scenario that uses it, not its scope (`stories/.context/cdr/0004-a-node-records-under-the-parent-that-walks-it.md`).

## StoryMapLinks

The `story-map.md` entry and story file each epic, sub-epic, and story links to.

+ StoryMapLinks.from_workspace(story_map: StoryModel, root: Path): StoryMapLinks
	// made once for the map placed in the folder root
----
+ story_file(story: Story): str
+ entry_for(node): str
