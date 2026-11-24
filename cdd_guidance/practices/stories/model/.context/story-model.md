# Story model

*StoryMap* is one story map: epics, the sub-epics nested under them, the stories in each, and the increments that slice them, then each story's backgrounds and scenarios down to steps and examples. A nested epic is an epic whose parent is an epic. An increment is a thin slice: a name, an outcome, slicing notes, a decision, and the stories in that slice. Every node is a graph node (*ModelNode*), so a loaded model is also the stories practice's part of the knowledge graph.

Each format is a *StoryMap* subclass with its own node subclasses, listed by `Stories` under `formats`: sketch, markdown, json, drawio, miro, python, typescript, javascript. A format's `copy_of(source)` copies any model into the format's node classes, starting from the format's `blank()` map, so the copy keeps the format's own settings (it is asked of a map, not its class, because a code format copies with its own `tests_root`; a UX map's `copy_of` is asked the same way); each epic, story, scenario, and background copied makes its parts as its class's `story_class`, `scenario_class`, `background_class`, and `step_class`. A `clone()` keeps each part's own class instead. Both read the node's one field list, `_copy_fields`. Every format meets the one format contract (*FormatAdapter*, harness/guidance), which *StoryMap* extends: `parse(text, file)` reads text in that format, `read_file(path, project, on_file)` opens a file of it, each node naming the file (`placed_in`), `opened_from(path, project)` is the map an edit to the file writes back, and `render(canonical, written)` writes a model out onto the file as it is now (*Written*). *StoryMapFiles* (`story_map_files.py`) is the one place that knows a story map's file name and a story's own file name, and finds the story map in or above a folder (`nearest`), the story map saved as JSON in it (`story_graph`, read by `JsonStoryMap.read_file`), the markdown maps below it (`markdown_below`), each story's own file below it (`story_files_below`), and the files scenarios are written in (`scenario_files_below`), entering each folder's `.context` and no folder a working-copy scan never enters (`skips_folder`). The Stories practice names itself on *StoryNode* (`StoryNode.practice_class = Stories`), so the model never imports its practice. Markdown, JSON, and the code formats carry scenarios, steps, and examples; the diagram formats (drawio, miro) stop at stories and still read increments. The Claude Design story canvas, which shows the stories on their screens, is a *DiagramStoryMap* the UX practice draws (`practices/ux/model/claude_design/story_canvas.py`).

```
story_map = Stories().story_files(folder).story_map_in(folder)     # story-map.md (or .json), increments, scenarios
drawio = DrawIOStoryMap().render(story_map)
```

# practices/stories/model

- **Purpose:** Keep stakeholder behaviour as one story model — epics, stories, and increments, then scenarios and steps — so a markdown file, a diagram, and a test file stay the same hierarchy every later fidelity reads.
- **Seam (terms):** StoryNode, StoryMap, Epic, Increment, Story, StoryType, Background, Scenario, Step, StepType, Example, Examples, and one StoryMap subclass per format; where a node sits is the graph's *Source*
- **Dependencies (one-way):** harness/graph (*ModelNode*, *Graph*), harness/annotations (*Name*), practices/clean_engineering/model (*CodeBody*, *CodeLanguage*, *WrittenBlock*, *CallGraphEntry*), practices/sketch_document (*SketchOutline*), harness/guidance (*SketchLens*)

These dependencies are owned by the modules named; this model only uses them. Each node writes itself onto the stories practice graph (`StoryMap.record`, through a *StoryRecording*); cross-practice links from steps and examples to Clean Engineering nodes are recorded there.

## StoryNode : ModelNode

Every epic, increment, story, background, scenario, step, and example. It keeps the facts story-map graph rules read (*NameFacts*) as its own facts, which the graph saves with it.

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
----
+ load_map_facts(): None
	// keeps its NameFacts as its own facts: each kind of node sizes its children and judges its name, an epic against the band of its layer, a story by its scenarios, a scenario by its steps
- _name_facts(): NameFacts
	// what its name and file say
+ take_code_from(source: StoryNode): None
	// keeps written and setup when the node is copied into another format or cloned
+ copy_of(source: StoryNode): StoryNode
	// class operation: source made as this class, each of its parts made as the class this class holds that part as; how a map is copied into another format
+ clone(): StoryNode
	// a copy of this node as its own class, each of its parts a clone keeping its own class, so a markdown story under a plain epic stays a markdown story
- _copy_fields(original: StoryNode, copy_part: CopyPart): None
	// the one list of a node's fields that copy_of and clone share; copy_part makes each part

## NameFacts

What a story node's name, file and children say about it, as the story map's rules read them. The node keeps its facts as its own, so the graph saves them with it.

+ NameFacts(name: str, file: str)
------
+ opening_token, opening_class: str
	// the first word of the name and its class: a verb, a generic verb, an actor noun, a gerund, a nominalisation, a single word, unlisted
+ artifact_name: str
+ camel_case_path: bool
+ child_count: int
+ child_label, child_target, child_band: str
	// child_band is "error" when the count is past the band of the node's layer; a node of no layer holds no band
+ generic_handler, near_duplicate: bool
+ shared_verb: str
+ opens_with_generic_handler: bool
+ facts: dict[str, str | int | bool]
	// the eleven facts by the names the rules read
----
+ count(children: int, band: ChildBand | None = None, label: str = "children"): None
	// counts the children against band, the band of the node's layer
+ judge(generic_handler: bool = False, near_duplicate: bool = False, shared_verb: str = ""): None
	// keeps what the node judges from its name and its place in the map

## StoryMap : StoryNode

+ StoryMap(graph: Graph | None = None)
------
+ epics: list[Epic]
	// composition — an epic has no model outside this story model; numbered in the order they stand (*NumberedChildren*), so one appended takes the next number
+ increments: list[Increment]
	// composition — an increment has no model outside this story model; numbered the same way
+ examples: Examples
	// examples shared by the whole map
+ epic_class: type
+ increment_class: type
+ story_class: type
	// its epic class's story_class
----
+ sources: StorySources
	// each file the map was read from (a StorySource: its path and text, and the imports, exports, examples and evidence it declares)
+ links: StoryMapLinks | None
	// where each node links in the folder a render placed the map in
+ descendants: Descendants
	// part: every epic and story under the map, the stories a thin slice names, the node a path names
+ test_scenarios: StoryTestScenarios
	// part: the scenarios its stories take from the story tests that specify them
+ opened: OpenedStoryMap | UnopenedStoryMap
	// where it was opened in a session, which saves it after every edit (`save`); nowhere for a map read any other way
+ record(practice, on_node: Callable | None = None): None
	// each epic, story, background, scenario, step, and example adds itself to the stories practice
+ blank(): StoryMap
	// a map of this format holding nothing, with this map's settings; a code map keeps its tests root, a Claude Design canvas its setup
+ copy_of(source: StoryMap): StoryMap
	// asked of a map: source copied into this format's node classes, each epic as epic_class and each increment as increment_class, delivering the copies of its stories
+ clone(): StoryMap
	// from blank(), each epic and increment a clone keeping its own class

## Descendants

The epics and stories under an epic or a story map, at any depth, in map order.

+ Descendants(holder: Epic | StoryMap)
----
+ epics(): list[Epic]
	// every epic nested under its holder, each before its own children
+ stories(): list[Story]
	// every story its holder and its nested epics hold
+ stories_named(names: list[str]): list[Story]
	// its stories names name, in that order: how an increment read from a thin slice finds its stories
+ stories_by_name(): dict[str, Story]
+ place_in(file: str): None
	// names file on every epic and story that names no file yet
+ node_at(path: str): StoryNode
	// the node a tool's path names below its holder; StoryNodeNotFound for one it does not hold

## StoryTestScenarios

The scenarios a story map's stories take from the story tests that specify them: every Story of a story test's story's name takes them.

+ StoryTestScenarios(story_map: StoryMap)
----
+ take(stories: list[Story], file: str): None
	// in place of the scenarios and backgrounds each Story holds
+ add(stories: list[Story], file: str): None
	// after the ones each Story holds
+ drop(): None

## OpenedStoryMap / UnopenedStoryMap

Where a story map was opened in a session: its file, the session's stories, its acceptance tests, and `save()`, which writes the map back and answers it. *UnopenedStoryMap* is a map read any other way: no file, no stories, and every save refused with StoryMapEditRefused.

## Epic : StoryNode

+ Epic(name: str, sequential_order: int = 0)
------
+ epics: list[Epic]
+ stories: list[Story]
+ examples: Examples
+ story_class: type
	// the story class this format's epics hold; an epic copied into this format makes its stories of it
+ depth: int
+ is_sub_epic: bool
	// its parent is an epic; it records as a SubEpic
+ top_epic: Epic
	// the epic of the map it sits under; itself when it is one
+ descendants: Descendants
	// part: every epic and story under it; place_in(file) names file on it and everything under it that names none
----
+ leaf_epics(): list[Epic]
	// the epics whose stories sit in columns: its innermost sub-epics, or itself when it has none
+ new_epic(name), new_story(name)
	// tools; a sub-epic or story is added with `epics.append` / `stories.append`, which makes this epic its parent

## CodeHeld : StoryNode

The code a node was read with in a language: the block it was written as (`written`), the story file a story was read with (`file_written`), and the code its scenarios or steps share (`setup`). Epic, Story, Background, Scenario, and Step extend it; an Example and an Increment are written with no code of their own.

+ written: WrittenBlock | None
+ file_written: WrittenBlock | None
+ setup: CodeBody
----
+ take_code_from(source: CodeHeld): None

## EpicColumns (diagram_story_map.py)

How many story columns an epic spans on a drawn map, and how deep its sub-epics nest: a drawing's concern, so only a *DiagramEpic* holds one (`columns`).

+ EpicColumns(epic: DiagramEpic)
----
+ estimate_label(): str
	// "* {estimate}". Load strips the star and any HTML
+ has_estimate(): bool
+ span(): int
+ diagram_span(): int
+ tree_depth(): int

## Increment : StoryNode

+ Increment(name: str, sequential_order: int = 0, stories: list[Story] | None = None)
------
+ outcome: str
+ slicing_notes: str
+ decision_prompt: str
+ source: Source | None
+ stories: list[Story]
	// the stories in this thin slice. Each story still belongs to its epic, and records this increment
----
+ clone(): Increment

## Story : StoryNode

+ Story(name: str, sequential_order: int = 0, story_type: StoryType = StoryType.USER)
------
+ story_type: StoryType
+ increment: Increment | None
+ actors: list[str]
+ domain_terms: list[str]
+ evidence: list[str]
+ backgrounds: list[Background]
+ scenarios: list[Scenario]
+ scenario_class: type
+ background_class: type
	// the scenario and background classes a story copied into this format makes its parts of
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

+ Background(name: str = "background", sequential_order: int = 1)
------
+ steps: list[Step]
+ step_class: type
+ examples: Examples
+ code_key: tuple
----
+ clone(): Background

## Scenario : StoryNode

+ Scenario(name: str = "", sequential_order: int = 0)
	// its story is its parent; a scenarios file links a scenario to its story only by the name its section is headed with
------
+ backgrounds: list[Background]
+ steps: list[Step]
+ examples: Examples
+ is_outline: bool
+ evidence: list[str]
+ source: Source | None
+ code_key: tuple
+ step_class: type
+ background_class: type
	// the step and background classes a scenario copied into this format makes its parts of
----
+ steps_in(step_type: StepType): list[Step]
+ when_then_runs(): list[tuple]
	// a When after a Then starts the next run
+ clone(): Scenario

## Step : StoryNode

+ Step(text: str, step_type: StepType | None = None, sequential_order: int = 0)
	// what a format reads beyond that — its keyword, concepts, values, actor, and source — is set on the step afterwards
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
+ source: Source | None
+ call_graph: list[CallGraphEntry]
+ body: CodeBody
	// the step's test code as read, in the language it was written in. Empty outside code
+ continuation: bool
	// an And or But line, which continues the clause before it
+ phase: str
+ callees: list[str]
	// the capitalised concepts the step names: the domain classes it reaches
+ code_key: tuple
	// keyword, text, and body
----
+ continue_with(keyword: str, text: str): Step
	// an And or But line chained onto this step, of its type
+ clone(): Step

## StepType

+ GIVEN = "given"
+ WHEN = "when"
+ THEN = "then"

## Example : StoryNode

+ Example(name: str, example_value: ExampleValue = None)
	// its scope is set by the Examples that holds it
------
+ value: Any
	// a field map by default
+ scope: StoryNode | None
	// the node that shares this example: a background, a scenario, a sub-epic, an epic, or the story map
----
+ cells(): dict
+ clone(): Example

## Examples : dict

Example name to value, for one scope.

+ Examples(scope: StoryNode | None = None)
------
+ scope: StoryNode | None
----
+ table(): list[dict]
+ clone(scope: StoryNode | None = None): Examples

Where a node sits is the graph's *Source* (`harness/graph/graph.py`): its `file`, `start_line`, and `end_line`, 0 while the line is not known. A reader names the lines it read a node on, and the graph keeps the same object type when it adds the node, so a node has one location type before and after it is on the graph. Every Stories reader makes it through `source_at(file, start, end)` (`story_map_files.py`).

---

## Formats

Each format class below is a *StoryMap* subclass. Its node subclasses (`MarkdownEpic`, `DrawIOStory`, …) set the node classes `copy_of(source)` copies into; a format overrides only what it reads or writes differently.

## SketchStoryMap : StoryMap

The `sketch` format: the stories section of an integrated sketch. Nodes: SketchEpic, SketchStory, SketchScenario, SketchBackground, and SketchStep, which write their own sketch lines (`sketch_lines`) and read the lines nested under their own (`read_lines`, from the *SketchLines* that `SketchLines.from_raw(raws)` reads: each entry `under()` gives is the line naming a node, `text`, then the lines `nested` under it).

------
+ epic_class: SketchEpic
----
+ parse(text: str): SketchStoryMap
	// fills this map and returns it
	-> SketchOutline.body_for
	-> read_lines
+ render(canonical: StoryMap | None = None, previous: str | None = None): str
	// copies canonical into a sketch map, which writes itself
	-> save
+ save(): str
	-> SketchEpic.sketch_lines

## MarkdownStoryMap : StoryMap

The `markdown` format: `story-map.md`, the scenario files beside it, and the increments file. Nodes: MarkdownEpic, MarkdownStory, MarkdownIncrement, MarkdownScenario, MarkdownStep. The text is read by a reading made for each read, which keeps where the read is so no node or format holds it: *HeadingMapReading* or *OutlineMapReading* (`map_reading.py`, chosen by `read_map`, sharing *MapReading*'s epic and sub-epic placement) for a story map, and *ScenarioFileReading* (`scenario_file.py`, holding the parts in `scenario_parts.py`: a *BackgroundReading*, an *ExamplesTable*, and a *RealizationFence*, taking each step line onto its scenario or background) for a scenarios file; a scenarios document becomes a map through *MarkdownStoryMap*'s parse, and writes itself back through its *ReadScenarioDocument* (`read_lines.py`): each line it was read with is a *ReadLine* that writes itself as the model now stands, a *KeptLine* as written, a *HeadingLine* (the node, what it said, the line) its node writes back as read or anew, the *StepLines* of one owner, an *ExampleLine*, and the *HeldLines* of a scenario or story held in place; a section's step lines are written by one *SectionSteps*, whose owner's last line writes every step still pending. `markup.py` holds MarkdownStep (whose `read_from(line)` keeps its line and the concepts, values and actor its markup names), `step_prose`, and how a name loses its links and emphasis.

------
+ epic_class: MarkdownEpic
----
+ read_file(path: Path, project: Path, on_file: OnFile = None): MarkdownStoryMap
+ read_folder(folder: Path, project: Path, on_file: OnFile = None): MarkdownStoryMap | None
	// the markdown story maps the folder holds, merged; each story takes the scenarios of the scenario-file sections headed with its name (*ScenarioFiles*, *StorySection*, each file read by its own *ScenarioFileReading*), and the increments of `StoryMapFiles.thin_slicing`
+ parse(text: str, file: str = ""): MarkdownStoryMap
	// read from file, each epic, sub-epic, story, and scenario names the line it is read on, as it is read
+ render(canonical: StoryMap, written: Written = Written()): str
	// written in a folder, each story that has its own markdown file links to it
+ save(): str

## JsonStoryMap : StoryMap

The `json` format. Nodes: JsonEpic, JsonStory, JsonIncrement, JsonScenario, JsonBackground, JsonStep; each reads its own record (`from_record`) and writes it (`as_record`).

----
+ read_file(path: Path, project: Path, on_file: OnFile = None): JsonStoryMap
	// every epic and story names story-graph.json (`placed_in`); text that does not read names the file
+ parse(text: str, file: str = ""): JsonStoryMap
	// fills this map and returns it
+ render(canonical: StoryMap, written: Written = Written()): str
	// copies canonical into a JSON map, which writes itself
	-> save
+ save(): str
	// this map as story-graph.json text

## DiagramStoryMap : StoryMap

The layout shared by the diagram formats. Nodes: DiagramEpic, DiagramStory, DiagramIncrement, each also a *DiagramStoryNode*.

------
+ max_sub_epic_depth: int
+ actor_y: int
----
+ place_cells(cells: list[DiagramStoryCell]): list[DiagramStoryCell]
	// reads the epics and stories by where their cells sit: the one reading draw.io, the whiteboard, and Miro share

## ThinSliceLayout

A map's increments laid out as a thin slice, the one layout the drawn formats draw (draw.io's page and the whiteboard):
a column for each sub-epic, or epic with none, each as wide as the most stories any increment puts in it, and a lane
for each increment. Each format draws it on its own *ThinSliceSurface* (epic_header, sub_epic_header, lane).

+ ThinSliceLayout(story_map: DiagramStoryMap, pitch: float, gap: float, left: float)
------
+ columns: list[ThinSliceColumn]
	// epic, sub, x, width
+ lanes: list[ThinSliceLane]
	// increment, stories by column
+ width: float
----
+ epic_headers(): list[tuple[Epic, float, float]]
+ sub_epic_headers(): list[ThinSliceColumn]
+ draw_on(surface: ThinSliceSurface): None
	// each epic's header, then its sub-epics', column by column, then each lane

## DiagramStoryNode

+ first_x, epic_spacing, story_pitch: int
	// how a format lays out its epics: where the first starts, the space between two, and how far each story an epic holds itself pushes its sub-epics; the base diagram gives 0 for each
+ x: int
	// the one walk every diagram format places its epics and stories by
+ y: int
+ width: int
+ height: int

## DrawIOStoryMap : DiagramStoryMap

The `drawio` format. Nodes: DrawIOEpic, DrawIOStory, DrawIOIncrement.

----
+ parse(text: str): DrawIOStoryMap
	// reads cells by where they sit, not their order in the file
+ render(canonical: StoryMap | None = None, previous: str | None = None, workspace: str | None = None): str
	// in a workspace folder, each cell links to its story-map.md entry
+ save(): str

## MiroStoryMap : DiagramStoryMap

The `miro` format: a canvas-composer SVG, with increments as a thin-slice table. Nodes: MiroEpic, MiroStory, MiroIncrement.

----
+ parse(text: str): MiroStoryMap
	// reads cards by where they sit (place_cells), as the other drawn formats do; the thin-slice table keeps its own headings
+ render(canonical: StoryMap | None = None, previous: str | None = None): str
	-> save
+ save(): str

## CodeStoryMap : StoryMap

A story map written as test code: a folder for each epic and sub-epic, and one file for each story in a folder of the story's own, as the acceptance tests fidelity declares them; the stories read together from one file go back to it together. Nodes: CodeEpic, CodeStory, CodeScenario, CodeIncrement, each also a *CodeStoryNode* (`slug`, `snake`, `pascal`, `camel`). The model keeps the layout of the story files and the code a render adopts; how its language writes a story file is the *StoryWriting* it holds (`writing`), beside the reader of its story files (`story_file`).

------
+ language: CodeLanguage | None
	// each language model sets its instance
+ writing_class: type[StoryWriting]
+ writing: StoryWriting
	// made once, with the model's language; TypeScript's also holds the import of its step library
+ tests_root: str
+ story_file_suffixes: tuple[str, ...]
	// how a story file in this language ends; the first is the one it writes
+ not_story_paths: re.Pattern
	// a path that ends like a story file but holds none: TypeScript's examples folders
----
+ is_story_file(path): bool
	// a file this language reads stories from, by its suffixes and the paths it leaves out
+ parse(external: dict[str, str], on_file=None): CodeStoryMap
	// external is the path-to-content map of the test tree
+ load(external: dict[str, str], on_file=None): CodeStoryMap
	// the one load for every language: each story file under the tests root is one sub-epic
	-> story_file(path, text).stories, .own_code
	// each file read once: a story made from each story block; a file the language cannot read in blocks (Python that does not parse) is read from its text (`StoryFile.read_text`, the named fallback over *StorySyntax*)
+ render(canonical: StoryMap, previous: dict[str, str] | None = None): dict[str, str]
	Invariant: previous is the path-to-content map already on disk, never one text
	// each epic, story, scenario, and step without code in this language takes the previous tree's code for the same names
	-> parse(previous)
	-> adopt_code
+ save(): dict[str, str]
+ adopt_code(kept: CodeStoryMap): None
+ project: Path | None
	// the folder a story file's own reads, such as its examples module, are found in; set by each load
+ story_file(path: str, content: str, project: Path | None = None): StoryFile
	// always answers, the kind picked once: a block reader (Python, brace), a screen spec, a shared story file, or the text kind for a language that reads no blocks
+ read_from_code: bool
	// property: some sub-epic or story in this tree was read from a file in this language

## StoryWriting

How one language writes stories (`story_writing.py`): the one generic render, which writes a node read in this language and unchanged exactly as read, and the spelling the language gives as data (file name template, indents, the lines a story or scenario with nothing in it holds, the templates that open and close a scenario, a step, and an And step, the verbs, whether a repeated phase chains) or, where a template cannot say it, as its own operation. *PythonStoryWriting*, *BraceStoryWriting* (with *TypeScriptStoryWriting* and *JavaScriptStoryWriting*, which differ only in `story_test_import`), and *JavaStoryWriting* (doc comments, no code) are the languages.

+ StoryWriting(language: CodeLanguage | None)
----
+ story_file(epic, parent, written): tuple[str, str]
	// the path and text of the file holding a sub-epic's stories
+ story_lines(story): list[str]
+ verb_alone(step): str
	// the verb a step opens with when written as a statement of its own: the one listed for its keyword, else its phase
+ file_header, story_open, story_background_lines, scenario_background_lines
	// the parts a language spells as its own operation, with the protected `_step_lines(clause: StepClause, indent)`, `_clauses(steps)` and `_quoted(text)` it spells them with

## StorySyntax

How one language's story files write stories, scenarios and steps (`code_story_map.py`): the patterns a story test is read by. *BraceSyntax*, *PythonSyntax* and *JavaSyntax* are the languages; a language's story and scenario classes hold the one syntax (`syntax`).

----
+ steps_in(body), steps_from(calls): list[Step]
+ scenario_blocks(content): list[tuple]
+ backgrounds_in(content): list[Background]
+ example_names(content), example_imports(content)
+ story_name(content): str
	// without the tier a story test names after it
+ story_texts(content): list[str]
	// the text of each story in one file

## CodeStoryMapError : Exception

## PythonStoryMap : CodeStoryMap

The `python` format: Mamba story tests. Nodes: PythonEpic, PythonStory, PythonScenario. Its blocks are found by *PythonStoryFile*.

## BraceStoryMap : CodeStoryMap

The model TypeScript and JavaScript share; they write with a *BraceStoryWriting*. Nodes: BraceStory, BraceScenario. Its blocks are found by *BraceStoryFile*.

## ReshapedStoryFile

The scenarios a render brings, written onto the story file already there (`CodeStoryMap.reshape(rendered, existing)`, which the Render action asks of a format's adapter). The file is edited where it stands, matched story to story, scenario to scenario and step to step by their words: a member both hold stays as the file has it; one only the render holds is written in empty; one only the file holds stays with its code under a line saying it is no longer in the model. Only lines are added, so the same scenarios written onto the result change nothing. A file the language finds no story block in, such as a step library, is left as it is.

------
+ reshaped(): Reshaped
	// the text to save, the members kept and the members added, each named story.scenario.step

## ScriptStoryMap : BraceStoryMap

The story tree of a script language, TypeScript or JavaScript, which hold the same story files: a story test (`_story.test`), a shared story file (`.story.shared`), a screen spec (`.story.ui.spec`, read by *ScreenSpecFile* as one story for each `test.describe`), and the step library every story file imports. Nodes: ScriptStory. A language names its extension, its code language, its step library seed, and how a story file imports the step library.

------
+ story_test_folder: str
	// the step library folder: the stories workspace root, else the deploy root, unless named
+ story_test_import_path: str
	// property: the step library as a path from the workspace root, without its extension
- _story_test_file_path: str
	// property: where the step library a new tree is seeded with is written
+ seed_file: Path
	// the step library a new tree in this language is seeded with

## TypeScriptStoryMap : ScriptStoryMap

The `typescript` format. Nodes: TypeScriptEpic, TypeScriptStory, TypeScriptScenario. A story file imports the step library by its path from the workspace root.

## JavaScriptStoryMap : ScriptStoryMap

The `javascript` format. Nodes: JavaScriptEpic, JavaScriptStory, JavaScriptScenario. A story file imports the step library by the path from its own folder, with the file's extension.

## CodeStory : Story, CodeStoryNode

A story read from a story file. Each language gives its patterns (`_NAME`, `_STORY_START`, `_STORY_MARK`); reading is one way for every language.

----
+ from_block(block: StoryBlock, lead: list[str], text: str): CodeStory
	// class operation: the story one story block holds, with one scenario per scenario block, its code read from the same block
+ load_all(content: str): list[CodeStory]
	// class operation: a file read from its text, split where each story starts (a file the language cannot read in blocks)
+ load(content: str, scenario_blocks: list[StoryBlock] | None = None): CodeStory
	// class operation: name, description (actor, kind, domain terms, evidence), backgrounds, and scenarios
+ read_code(block: StoryBlock, lead: list[str], scenarios: list[StoryBlock]): None
	// this story's own code from the block it was written as: background step bodies, setup, written, then each scenario's from its block, in order
	-> CodeScenario.read_code(block, lead)

## CodeScenario : Scenario, CodeStoryNode

----
+ scenario_blocks(content: str): list[tuple]
	// class operation over the language's `_SCENARIO`; BraceScenario reads balanced braces
+ example_imports(content: str): str
	// class operation: the lines of a story file that import its examples
+ example_names(content: str): list[str]
	// class operation over the language's `_IMPORT` and `_EXAMPLES_LINE`
+ read_code(block: StoryBlock, lead: list[str]): None
	// background and step bodies, setup, and written from the scenario's own block
	-> Step.read_code(block)

## StoryFile

One story file in code, read once into its stories and the file's own code around them; no story is matched to a block by its name. Its model picks its kind once (`CodeStoryMap.story_file`). This kind reads the stories from the text alone, as a language that reads no blocks does.

+ StoryFile(model: CodeStoryMap, path: str, content: str, project: Path | None = None)
------
+ stories: list[CodeStory]
+ own_code: WrittenBlock | None
----
+ story_blocks(): list[StoryBlock] | None
	// none for this kind
+ read_text(): list[CodeStory]
	// the named fallback: the stories the text writes, read with *StorySyntax*

## BlockStoryFile : StoryFile

A story file whose language finds its blocks: each story is made from its block and placed on its lines, and the file's own code above, between, and below them is kept. A file whose blocks cannot be read (a Python story test that does not parse) falls back to `read_text`. *PythonStoryFile* and *BraceStoryFile* are its kinds; *ScreenSpecFile* and *SharedStoryFile* are kinds of *StoryFile* that read their own shapes.

----
+ story_blocks(): list[StoryBlock] | None
+ comment_above(block): str
	// the comment lines right above a block, which describe its story
	-> CodeStory.from_block(block, lead, text)

## StoryBlock

One block of a story file: a story, background, scenario, or step call, an abstract class *PythonBlock* and *BraceBlock* extend for their language.

----
+ name, line_span, opening_line, is_chained, inside_lines, body, body_text, text
+ written(lead): WrittenBlock
+ split_inside(children): tuple
+ scenarios(), backgrounds(scenarios), steps(skip): list[StoryBlock]
+ setup(children): CodeBody

## StoryRecording

One writing of a story map onto the practice that holds Stories: the practice and graph it writes to, where each node
sits in the files the map was read from (its *StorySources*), and how many stories it has announced. Each node's
`record` adds itself through it, and sets on its node the facts it does not hold itself.

+ StoryRecording(story_map: StoryMap, practice: PracticeGuidance, on_node: Callable | None)
----
+ write(): None
+ add(story_object, node_id, lines: Source): Node
	// named by the object's recorded_name and typed by its recorded_type, at lines
+ source_of(file): StorySource
	// the file the map was read from at file; an empty one when it was read from none there
+ name_span(file, name, folder): Source
+ span_of(node, file, fallback_text=""): Source
	// the lines its reader named on the node (its source's start and end line), else the next line of file holding its text

Each node's `record` is handed the node its parent was added as (and the file a background, scenario, or step sits in), not read from `parent`: a story test's scenarios are shared by every Story of that name in a merged map, and an example's graph parent is the scenario that uses it, not its scope (`stories/.context/cdr/0004-a-node-records-under-the-parent-that-walks-it.md`).

## StoryMapLinks

The `story-map.md` entry and story file each epic, sub-epic, and story links to.

+ StoryMapLinks(story_map: StoryMap, root: Path)
	// made once for the map placed in the folder root
----
+ story_file(story: Story): str
+ entry_for(node): str
