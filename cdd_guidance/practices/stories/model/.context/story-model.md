# Story model

*StoryModel* is one story map: epics, the sub-epics nested under them, the stories in each, and the increments that slice them, then each story's backgrounds and scenarios down to steps and examples. A nested epic is an epic whose parent is an epic. An increment is a thin slice: a name, an outcome, slicing notes, a decision, and the stories in that slice. Every node is a graph node (*ModelNode*), so a loaded model is also the stories practice's part of the knowledge graph.

Each format is a *StoryModel* subclass with its own node subclasses, listed by `Stories` under `formats`: sketch, markdown, json, drawio, miro, python, typescript, java, javascript. `StoryModel(source)` copies any model into the subclass's node types; `parse` reads text in that format and `render(canonical, previous)` writes a model out. Markdown, JSON, and the code formats carry scenarios, steps, and examples; the diagram formats (drawio, miro) stop at stories and still read increments. The Claude Design story canvas, which shows the stories on their screens, is a *DiagramStoryModel* the UX practice draws (`practices/ux/model/claude_design/story_canvas.py`).

```
story_map = StoryModel.load(folder)            # story-map.md (or .json), increments, scenarios
drawio = DrawIOStoryModel().render(story_map)
```

# practices/stories/model

- **Purpose:** Keep stakeholder behaviour as one story model — epics, stories, and increments, then scenarios and steps — so a markdown file, a diagram, and a test file stay the same hierarchy every later fidelity reads.
- **Seam (terms):** StoryNode, StoryModel, Epic, Increment, Story, StoryType, Background, Scenario, Step, StepType, Example, Examples, SourceLocation, and one StoryModel subclass per format
- **Dependencies (one-way):** harness/graph (*ModelNode*, *Graph*), harness/annotations (*Name*), practices/clean_engineering/model (*CodeBody*, *CodeLanguage*, *WrittenBlock*, *CallGraphEntry*), actions/sketch (*SketchOutline*, *SketchLens*)

These dependencies are owned by the modules named; this model only uses them. *GraphStoryModel* writes a loaded model onto the stories practice graph; cross-practice links from steps and examples to Clean Engineering nodes are recorded there.

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
+ load(root): StoryModel
	// class operation: the story map, increments, and scenarios in a folder
+ load_files(files, project): StoryModel
	// class operation: the story maps and story tests among files; each node names its file as a path from project
+ every_epic(): list[Epic]
	// every epic and nested epic, each before its own children
+ every_story(): list[Story]
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
----
+ estimate_label(): str
	// "* {estimate}". Load strips the star and any HTML
+ every_epic(): list[Epic]
+ every_story(): list[Story]
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

+ Scenario(name: str | Scenario = "", sequential_order: int = 0, story_name: str = "")
------
+ story_name: str
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

The `sketch` format: the stories section of an integrated sketch. Nodes: SketchEpic and SketchStory, which write their own sketch lines (`sketch_lines(depth)`).

------
+ epic_type: SketchEpic
+ story_type: SketchStory
----
+ parse(text: str): SketchStoryModel
	// fills this map and returns it
	-> SketchOutline.body_for
+ render(story_map: StoryModel | None = None, previous: str | None = None): str
	// copies the story map into a sketch map, which writes itself
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
+ parse(text: str): MarkdownStoryModel
+ render(story_map: StoryModel, previous: str | None = None, links: StoryMapLinks | None = None, workspace: str | None = None): str
	// with links, each story that has its own markdown file links to it
+ save(): str
+ attach_source_locations(text: str, rel_file: str): None

## JsonStoryModel : StoryModel

The `json` format. Nodes: JsonEpic, JsonStory, JsonIncrement, JsonScenario; each reads its own record (`from_record`) and writes it (`as_record`).

----
+ from_workspace(root: Path): JsonStoryModel | None
+ parse(text: str): JsonStoryModel
	// fills this map and returns it
+ render(story_map: StoryModel, previous: str | None = None): str
	// copies the story map into a JSON map, which writes itself
	-> save
+ save(): str
	// this map as story-graph.json text
+ attach_source_locations(file_name: str): None

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
+ render(canonical: StoryModel | None = None, previous: str | None = None, links: StoryMapLinks | None = None, workspace: str | None = None): str
	// with links, each cell links to its story-map.md entry
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
----
+ parse(external: dict[str, str]): CodeStoryModel
	// external is the path-to-content map of the test tree
+ load(external: dict[str, str]): CodeStoryModel
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
+ read_code(content: str, stories: list[Story], path: str): WrittenBlock | None
	// gives each story, background, scenario, and step the code it was written with
+ file_name, file_header, folder_files, story_open, story_close, story_background_lines, no_scenarios_lines, scenario_open, scenario_close, scenario_background_lines, examples_lines, clauses, verb, step_open, step_close, and_open, and_body_indent, and_close, step_placeholder, empty_block
	// each language overrides the spelling operations; none of them decides what a body holds

## CodeStoryModelError : Exception

## PythonStoryModel : CodeStoryModel

The `python` format: Mamba story tests. Nodes: PythonEpic, PythonStory, PythonScenario. Read through *PythonStoryReader*.

## BraceStoryModel : CodeStoryModel

The spelling TypeScript and JavaScript share. Nodes: BraceScenario. Read through *BraceStoryReader*.

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

## StoryReader

Reads one story file: the file's own code around its stories, then each story the file and the model share. *PythonStoryReader* and *BraceStoryReader* spell the blocks.

+ StoryReader(language: CodeLanguage, content: str)
----
+ read(stories: list[Story], path: str): WrittenBlock | None
	// the file's code above the first story and below the last

## GraphStoryModel

One loaded story model, written as graph nodes and edges.

+ GraphStoryModel(model: StoryModel)
----
+ record(practice, on_node: Callable | None = None): None
	// epics, stories, backgrounds, scenarios, steps, and examples onto the stories practice

## StoryMapLinks

The `story-map.md` entry and story file each epic, sub-epic, and story links to.

+ StoryMapLinks.from_workspace(root: Path, base: Path | None = None): StoryMapLinks
----
+ story_file(story: Story): str
+ entries(story_map: StoryModel): dict[int, str]
