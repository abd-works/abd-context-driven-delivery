# Story map

*StoryMap* reads one file into epics, stories, and increments. A nested epic is an epic whose parent is an epic. An increment is a thin slice: a name, an outcome, slicing notes, a decision, and the stories in that slice. Markdown, JSON, and the code languages continue through one background, then scenarios, steps, and examples. Draw.io and Miro stop at stories, and they still read increments. Every channel uses the same walk. A channel only differs in how the next node is taken out of the file.

Callers use the base nodes. `StoryModelFactory.load` takes a file or a folder, chooses the channel story map, and returns a `StoryMap`.

```
story_map = StoryModelFactory.load(path)
```

# practices/stories/model

- **Purpose:** Keep stakeholder behaviour as one story map — epics, stories, and increments, then scenarios and steps — so a markdown file, a diagram, and a test file stay the same hierarchy every later fidelity reads.
- **Seam (terms):** StoryNode, StoryModelFactory, StoryMap, Epic, Increment, Story, StoryType, Background, Scenario, Step, StepType, Example, MiroApiClient
- **Dependencies (one-way):** *(none)*

## StoryNode

Every epic, increment, story, background, scenario, step, and example is a StoryNode. A channel node extends the same base, so a MarkdownEpic and a DrawIOEpic share name, order, parent, and estimate.

+ name: str
+ sequential_order: int
+ parent: StoryNode
+ estimate: str
----
+ semantic_type(): str
	// Epic, Story, Step, and the other node kinds
+ clone(): StoryNode
	// a copy of this node, including its children

## StoryModelFactory

+ load(path: str): StoryMap
	// path is a file, or a folder of files
	// the file type, or the files in the folder, selects the channel story map
	// that map loads itself
	// the return is a StoryMap

## StoryMap

+ StoryMap(source: StoryMap)
	// source empty: the map is empty until load
	// source set: epics, stories, and increments are this channel's types, built from source. A nested epic uses epic_type. An increment uses increment_type
	// the new map does not keep the source's channel types
------
+ file: str
+ epics: list[Epic]
	// composition — an epic has no map outside this story map
	// a nested epic is an epic whose parent is an epic
+ increments: list[Increment]
	// composition — an increment has no map outside this story map
+ epic_type: type
+ story_type: type
+ increment_type: type
----
+ load(file: str): StoryMap
	// stores file, then runs the same walk for every channel
	self.file = file
	self.load_story_map_content()
	self.load_epics()
	self.load_increments()
+ save(): str
	// every channel writes its file with this operation
+ append_increment(increment: Increment): None
- load_story_map_content(): None
	// channel prepares its cursor over file
- load_epics(): None
	// while has_more_epic: append load_next_epic()
- has_more_epic(): bool
	// channel: another epic remains in file
- load_next_epic(): Epic
	// epic = get_next_epic_from_file()
	// -> epic.load_epics()
	// -> epic.load_stories()
- get_next_epic_from_file(): Epic
	// channel: the next epic shell from file, in epic_type
- load_increments(): None
	// while has_more_increment: append_increment(load_next_increment())
- has_more_increment(): bool
	// channel: another increment remains in the file
- load_next_increment(): Increment
	// increment = get_next_increment_from_file()
	// -> increment.load_stories()
- get_next_increment_from_file(): Increment
	// channel: the next increment shell from file, in increment_type

## Increment

+ Increment(source: Increment)
	// copies name, order, outcome, slicing notes, and decision
	// each source story becomes this channel's story
------
+ name: str
+ sequential_order: int
+ outcome: str
+ slicing_notes: str
+ decision_prompt: str
+ stories: list[Story]
	// the stories in this thin slice. Each story still belongs to its epic
----
+ append_story(story: Story): None
- load_stories(): None
	// while has_more_story: append_story(load_next_story())
- has_more_story(): bool
- load_next_story(): Story
	// story = get_next_story_from_file()
	// a slice names the story. It does not load a background or scenarios
- get_next_story_from_file(): Story
	// channel: the next story name in this slice, in the map's story_type

## Epic

+ Epic(source: Epic)
	// copies name, order, and estimate
	// a nested epic is an epic whose parent is an epic
	// each source child epic becomes this channel's epic
	// each source story becomes this channel's story
------
+ name: str
+ sequential_order: int
+ estimate: str
+ epics: list[Epic]
+ stories: list[Story]
----
+ estimate_label(): str
	// "* {estimate}". A nested epic writes the same label. Load strips the star and any HTML
+ append_epic(epic: Epic): None
+ append_story(story: Story): None
- load_epics(): None
	// while has_more_epic: append_epic(load_next_epic())
- has_more_epic(): bool
	// channel: another child epic remains in the file
- load_next_epic(): Epic
	// child = get_next_epic_from_file()
	// -> child.load_epics()
	// -> child.load_stories()
- get_next_epic_from_file(): Epic
	// channel: the next child epic, in the map's epic_type
- load_stories(): None
	// while has_more_story: append_story(load_next_story())
- has_more_story(): bool
- load_next_story(): Story
	// story = get_next_story_from_file()
	// -> story.load_background()
	// -> story.load_scenarios()
- get_next_story_from_file(): Story
	// channel: the next story shell from the file, in the map's story_type

## Story

+ Story(source: Story)
	// copies name, order, and story type
	// the source background becomes this channel's background
	// each source scenario becomes this channel's scenario
------
+ name: str
+ sequential_order: int
+ story_type: StoryType
	// user, system, or technical. StoryMap.story_type is the channel class, not this value
+ background: Background
+ scenarios: list[Scenario]
----
- load_background(): None
	// background = get_background_from_file()
	// -> background.load_step()
	// -> background.load_examples()
- get_background_from_file(): Background
- load_scenarios(): None
	// while has_more_scenario: append the next scenario
- has_more_scenario(): bool
- load_next_scenario(): Scenario
	// scenario = get_next_scenario_from_file()
	// -> scenario.load_steps()
	// -> scenario.load_examples()
- get_next_scenario_from_file(): Scenario

## StoryType

+ user
+ system
+ technical

## Background

+ Background(source: Background)
	// copies name and order
	// the source step becomes this channel's step, ands included
	// each source example becomes this channel's example
------
+ name: str
+ sequential_order: int
+ step: Step
+ examples: list[Example]
----
- load_step(): None
	// step = get_step_from_file()
	// -> step.load_ands()
- get_step_from_file(): Step
- load_examples(): None
	// while has_more_example: append load_next_example()
- has_more_example(): bool
- load_next_example(): Example
- get_next_example_from_file(): Example

## Scenario

+ Scenario(source: Scenario)
	// copies name, order, and story name
	// each source step and example becomes this channel's step and example
------
+ name: str
+ sequential_order: int
+ steps: list[Step]
+ examples: list[Example]
----
- load_steps(): None
- has_more_step(): bool
- load_next_step(): Step
	// step = get_next_step_from_file()
	// -> step.load_ands()
- get_next_step_from_file(): Step
- load_examples(): None
- has_more_example(): bool
- load_next_example(): Example
- get_next_example_from_file(): Example

## Step

+ Step(source: Step)
	// copies text, step type, keyword, and order
	// each source and becomes this channel's and
------
+ text: str
+ step_type: StepType
	// given, when, or then. An and keeps the step type of the step it continues
+ keyword: str
	// Given, When, Then, And, or But
+ sequential_order: int
+ ands: list[Step]
----
- load_ands(): None
	// while has_more_and: append the next and
- has_more_and(): bool
- load_next_and(): Step
- get_next_and_from_file(): Step

## StepType

+ given
+ when
+ then

## Example

+ Example(source: Example)
	// copies name and value
------
+ name: str
+ value: str

## MarkdownStoryNode

+ strip_backticks(text: str): str
+ strip_markup(text: str): str
	// backticks, then the surrounding stars. Increment, scenario, and the story map all read names through this

## MarkdownStoryMap : StoryMap

+ MarkdownStoryMap(source: StoryMap)
------
+ epic_type: MarkdownEpic
+ story_type: MarkdownStory
+ increment_type: MarkdownIncrement
----
- load_story_map_content(): None
	// cursor is the markdown headings in file. Increments are the headings in thin-slicing.md, thin-slice.md, thin-slices.md, or increments.md
- has_more_epic(): bool
- get_next_epic_from_file(): MarkdownEpic
- has_more_increment(): bool
- get_next_increment_from_file(): MarkdownIncrement
+ save(): str

## MarkdownIncrement : Increment, MarkdownStoryNode

- has_more_story(): bool
- get_next_story_from_file(): MarkdownStory
	// a bullet under Stories. Outcome, slicing notes, and decision are the fields on this increment

## MarkdownEpic : Epic, MarkdownStoryNode

- has_more_epic(): bool
- get_next_epic_from_file(): MarkdownEpic
- has_more_story(): bool
- get_next_story_from_file(): MarkdownStory

## MarkdownStory : Story, MarkdownStoryNode

- get_background_from_file(): MarkdownBackground
- has_more_scenario(): bool
- get_next_scenario_from_file(): MarkdownScenario

## MarkdownBackground : Background, MarkdownStoryNode

- get_step_from_file(): MarkdownStep
- has_more_example(): bool
- get_next_example_from_file(): MarkdownExample

## MarkdownStep : Step, MarkdownStoryNode

+ display_text(): str
	// step text without a leading And or But
+ prose(step: Step): str
----
- has_more_and(): bool
- get_next_and_from_file(): MarkdownStep

## MarkdownScenario : Scenario, MarkdownStoryNode

- read(body: str): None
	// steps, the one background, and example rows from a scenario file
- has_more_step(): bool
- get_next_step_from_file(): MarkdownStep
- has_more_example(): bool
- get_next_example_from_file(): MarkdownExample

## JsonStoryNode

+ record(): dict
	// this node's JSON object

## JsonStoryMap : StoryMap

+ JsonStoryMap(source: StoryMap)
------
+ epic_type: JsonEpic
+ story_type: JsonStory
+ increment_type: JsonIncrement
----
- load_story_map_content(): None
	// cursor is the JSON epic array in file. Increments are the increments array in the same file
- has_more_epic(): bool
- get_next_epic_from_file(): JsonEpic
- has_more_increment(): bool
- get_next_increment_from_file(): JsonIncrement
+ save(): str

## JsonIncrement : Increment, JsonStoryNode

- has_more_story(): bool
- get_next_story_from_file(): JsonStory

## JsonEpic : Epic, JsonStoryNode

- has_more_epic(): bool
- get_next_epic_from_file(): JsonEpic
- has_more_story(): bool
- get_next_story_from_file(): JsonStory

## JsonStory : Story, JsonStoryNode

- get_background_from_file(): JsonBackground
- has_more_scenario(): bool
- get_next_scenario_from_file(): JsonScenario

## JsonBackground : Background, JsonStoryNode

- get_step_from_file(): JsonStep
- has_more_example(): bool
- get_next_example_from_file(): JsonExample

## JsonScenario : Scenario, JsonStoryNode

- has_more_step(): bool
- get_next_step_from_file(): JsonStep
- has_more_example(): bool
- get_next_example_from_file(): JsonExample

## JsonStep : Step, JsonStoryNode

- has_more_and(): bool
- get_next_and_from_file(): JsonStep

## DiagramStoryNode

+ x: int
+ y: int
+ width: int
+ height: int
----
+ place(side: str, destination: DiagramStoryNode): None
	// side is above, below, after, or before
+ add(child: DiagramStoryNode): None
	// place(below, this): the child sits under its parent
	// place(after, previous child): the child sits to the right of the previous child
	// then stretch()
+ stretch(): None
	// width becomes the sum of the children's widths. A story is one pitch wide. An estimate on a leaf epic adds columns
	// then parent.stretch(), so the parent and the grandparent grow when a story or a nested epic is added
	// the next sibling reads this width, so it shifts right
+ role(): str
	// epic, subepic:{depth}, story:{type}, actor, or estimate
	// Draw.io writes this as the style prefix. Miro writes it as data-role. Load matches the same word

## DiagramStoryMap : StoryMap

+ DiagramStoryMap(source: StoryMap)
	// children are DiagramEpic and DiagramStory. A nested epic is a DiagramEpic whose parent is a DiagramEpic. An increment is a DiagramIncrement
------
+ epic_type: DiagramEpic
+ story_type: DiagramStory
+ increment_type: DiagramIncrement
+ actor_y: int
----
+ save(): str

## DiagramIncrement : Increment, DiagramStoryNode

+ label_width: int
+ lane_height: int
+ lane_gap: int
	// the thin-slice lane. Draw.io and Miro place the stories of this increment in that lane

## DiagramEpic : Epic, DiagramStoryNode

## DiagramStory : Story, DiagramStoryNode
	// width is the story pitch. height is the story size

## DrawIOStoryNode : DiagramStoryNode

+ slug(): str
	// the same name-to-slug on an epic and a story. A nested epic uses it too
+ cell_id(): str
	// {parent.cell_id}/{slug}. The epic is the root and returns slug. A story appends a count when a sibling shares the slug
+ style(): str
	// role, then the shared tail: whiteSpace=wrap, html, overflow, fillColor, strokeColor, fontColor
+ cell(): Vertex
	// one mxCell from cell_id, name, x, y, width, height, and style
+ cells(): list
	// this cell, then each child's cells
+ matches(style: str): bool
	// the style starts with this node's role. Load uses that to choose an epic, a nested epic, a story, an actor, or an estimate

## DrawIOStoryMap : DiagramStoryMap

+ DrawIOStoryMap(source: StoryMap)
	// DrawIOEpic for each epic, including a nested epic, then DrawIOStory. An increment is a DrawIOIncrement
------
+ epic_type: DrawIOEpic
+ story_type: DrawIOStory
+ increment_type: DrawIOIncrement
----
- load_story_map_content(): None
	// cursor is the vertex cells in file. Increments are the inc-lane cells
- has_more_epic(): bool
- get_next_epic_from_file(): DrawIOEpic
- has_more_increment(): bool
- get_next_increment_from_file(): DrawIOIncrement
+ save(): str
	// writes this map's cells

## DrawIOIncrement : DiagramIncrement, DrawIOStoryNode

- has_more_story(): bool
- get_next_story_from_file(): DrawIOStory
	// an increment-story cell in this lane

## DrawIOEpic : DiagramEpic, DrawIOStoryNode

- place(side: str, destination: DiagramStoryNode): None
	// parent is the map: the epic bar and the estimate row
	// parent is an epic: the nested bar. height stays the diagram height
- estimate_label(): str
	// writes Epic.estimate_label as the estimate cell
----
- has_more_epic(): bool
- get_next_epic_from_file(): DrawIOEpic
- has_more_story(): bool
- load_next_story(): DrawIOStory
	// returns the story and stops. No background, scenarios, steps, or examples
- get_next_story_from_file(): DrawIOStory

## DrawIOStory : DiagramStory, DrawIOStoryNode

- place(side: str, destination: DiagramStoryNode): None
	// story cell under its epic

## MiroApiClient

The Miro REST API. `MiroStoryMap.upload` posts shapes through `create_shape`. `clear` deletes by id. `clear_story_map` lists the board and deletes shapes whose fill this map paints.

+ create(token: str): MiroApiClient
	// token, else MIRO_TOKEN, else ~/.miro-token, else .cursor/miro-token.txt
+ create_shape(board_id: str, x: float, y: float, w: float, h: float, fill: str, stroke: str, stroke_width: int, content: str, rx: int, font_size: int): dict
+ delete_shape(board_id: str, shape_id: str): None
+ list_shapes(board_id: str): list

## MiroStoryNode : DiagramStoryNode

+ slug(): str
	// the same name-to-slug on an epic and a story. A nested epic uses it too
+ shape(): dict
	// id, x, y, w, h, rx, fill, stroke, stroke_width, content, role, font_size
	// save writes that dict as a rect: data-role, data-content, and data-actor
	// load reads those attributes back into the node
	// upload turns the same dict into a board box
+ shapes(): list
	// this shape, then each child's shapes. A story adds the actor shape when the actor changes
+ fills(): set
	// the fill colors this node paints. A board clear finds story-map shapes by these fills
+ matches(role: str): bool
	// data-role equals this node's role. Load uses that to choose an epic, a nested epic, or a story

## MiroStoryMap : DiagramStoryMap

+ MiroStoryMap(source: StoryMap)
------
+ epic_type: MiroEpic
+ story_type: MiroStory
+ increment_type: MiroIncrement
----
- load_story_map_content(): None
	// cursor is the Miro items in file. Increments are the rows of the thin-slice table
- has_more_epic(): bool
- get_next_epic_from_file(): MiroEpic
- has_more_increment(): bool
- get_next_increment_from_file(): MiroIncrement
+ save(): str
+ upload(board_id: str, client: MiroApiClient): dict
	// each shape goes to the board through client.create_shape. Miro places a shape by its centre
+ clear(board_id: str, client: MiroApiClient, miro_ids: list[str]): int
+ clear_story_map(board_id: str, client: MiroApiClient): int
	// list_shapes, then delete the shapes whose fill this map paints

## MiroIncrement : DiagramIncrement, MiroStoryNode

- has_more_story(): bool
- get_next_story_from_file(): MiroStory
	// a cell in this table row, after the increment name

## MiroEpic : DiagramEpic, MiroStoryNode

- place(side: str, destination: DiagramStoryNode): None
	// parent is the map: the epic bar
	// parent is an epic: the nested bar
----
- has_more_epic(): bool
- get_next_epic_from_file(): MiroEpic
- has_more_story(): bool
- load_next_story(): MiroStory
	// returns the story and stops. No background, scenarios, steps, or examples
- get_next_story_from_file(): MiroStory

## MiroStory : DiagramStory, MiroStoryNode

- place(side: str, destination: DiagramStoryNode): None

## CodeStoryNode

+ slug(): str
	// kebab folder name
+ snake(): str
+ pascal(): str
+ camel(): str
+ name_from_slug(slug: str): str
	// the name read back from a folder

## CodeStoryMap : StoryMap

+ CodeStoryMap(source: StoryMap)
	// file for load is the path-to-content map of the source tree
	// a test tree has no increment files. Increments arrive when this map is built from a source that already has them
------
+ epic_type: CodeEpic
+ story_type: CodeStory
+ increment_type: CodeIncrement
----
- load_story_map_content(): None
	// cursor is epic folders, then nested epic folders, then story files
- has_more_epic(): bool
- get_next_epic_from_file(): CodeEpic
- has_more_increment(): bool
	// false for a test tree
- get_next_increment_from_file(): CodeIncrement
+ save(): str
	// one story file per story, under the epic folders

## CodeIncrement : Increment, CodeStoryNode

- has_more_story(): bool
- get_next_story_from_file(): CodeStory

## CodeEpic : Epic, CodeStoryNode

+ write(parent: str, files: dict, tests_root: str): None
	// an epic with child epics writes a folder, then each child writes into that folder
	// a sub-epic that has stories writes one file in the parent folder, named for the sub-epic
	// that file holds every story. The sub-epic does not get a folder
- has_more_epic(): bool
- get_next_epic_from_file(): CodeEpic
- has_more_story(): bool
- get_next_story_from_file(): CodeStory

## CodeStory : Story, CodeStoryNode

+ scenario_type: CodeScenario
+ write(parent: str, files: dict, tests_root: str): None
	// create() is this story's text inside the sub-epic file. The sub-epic file is the one the epic writes
----
- fill(content: str): None
	// -> scenario_type.backgrounds_in
	// -> scenario_type.example_names
	// -> scenario_type.scenario_blocks, then add_scenario
- load(content: str, story_slug: str): CodeStory
	// each language overrides this
- create(story: Story): str
	// each language overrides this
- get_background_from_file(): Background
- has_more_scenario(): bool
- get_next_scenario_from_file(): CodeScenario

## CodeScenario : Scenario, CodeStoryNode

- read(body: str): None
	// -> calls_in, then steps_from. Example names found in the body become examples
- calls_in(body: str): list
	// each language reads its own call spelling
- steps_from(calls: list): list[Step]
	// and and but become ands on the previous step
- scenario_blocks(content: str): list
- backgrounds_in(content: str): list[Background]
- example_names(content: str): list[str]
- create(scenario: Scenario): list[str]
- balanced(text: str, open_at: int): str
	// the brace body a language uses to cut a scenario out of a file
- has_more_step(): bool
- get_next_step_from_file(): Step
- has_more_and(): bool
- get_next_and_from_file(): Step
- has_more_example(): bool
- get_next_example_from_file(): Example

## PythonStoryMap : CodeStoryMap

+ PythonStoryMap(source: StoryMap)
------
+ epic_type: PythonEpic
+ story_type: PythonStory
+ increment_type: PythonIncrement
----
+ save(): str

## PythonIncrement : CodeIncrement

## PythonEpic : CodeEpic

## PythonStory : CodeStory

+ scenario_type: PythonScenario

## PythonScenario : CodeScenario

- get_next_step_from_file(): Step
	// reads `with given`, `with when`, `with then`, and `with and_` from the story file
- get_next_and_from_file(): Step
- get_next_example_from_file(): Example

## TypeScriptStoryMap : CodeStoryMap

+ TypeScriptStoryMap(source: StoryMap)
------
+ epic_type: TypeScriptEpic
+ story_type: TypeScriptStory
+ increment_type: TypeScriptIncrement
----
+ save(): str

## TypeScriptIncrement : CodeIncrement

## TypeScriptEpic : CodeEpic

## TypeScriptStory : CodeStory

+ scenario_type: TypeScriptScenario

## TypeScriptScenario : CodeScenario

- get_next_step_from_file(): Step
- get_next_and_from_file(): Step
- get_next_example_from_file(): Example

## JavaScriptStoryMap : CodeStoryMap

+ JavaScriptStoryMap(source: StoryMap)
------
+ epic_type: JavaScriptEpic
+ story_type: JavaScriptStory
+ increment_type: JavaScriptIncrement
----
+ save(): str

## JavaScriptIncrement : CodeIncrement

## JavaScriptEpic : CodeEpic

## JavaScriptStory : CodeStory

+ scenario_type: JavaScriptScenario

## JavaScriptScenario : CodeScenario

- get_next_step_from_file(): Step
- get_next_and_from_file(): Step
- get_next_example_from_file(): Example

## JavaStoryMap : CodeStoryMap

+ JavaStoryMap(source: StoryMap)
------
+ epic_type: JavaEpic
+ story_type: JavaStory
+ increment_type: JavaIncrement
----
+ save(): str

## JavaIncrement : CodeIncrement

## JavaEpic : CodeEpic

## JavaStory : CodeStory

+ scenario_type: JavaScenario

## JavaScenario : CodeScenario

- get_next_step_from_file(): Step
- get_next_and_from_file(): Step
- get_next_example_from_file(): Example

Python, TypeScript, JavaScript, and Java extend the code types: story map, increment, epic, story, and scenario. There is no language step type. A language scenario reads the step, the and, and the example. A nested epic is an epic whose parent is an epic. `StoryMap` loads the top epics, then the increments. `Increment` loads the stories in that slice. `Epic` loads its child epics and its stories, and `estimate_label` writes the estimate. `load_background` and `load_scenarios` stay on `Story`. A story has one background. `load_step` stays on `Background`. A background has one step, and that step loads its ands. `load_steps` and `load_examples` stay on `Scenario`. `load_examples` also stays on `Background`. `load_ands` stays on `Step`. Every story map implements `save(): str`. Draw.io and Miro extend `DiagramStoryMap` and stop at stories. `DiagramStoryNode.add` places the child below its parent and to the right of the previous child, then `stretch` widens that node and every parent above it. Draw.io and Miro override `width` and `y` where the bar differs. A Draw.io node is a `DrawIOStoryNode`: `slug`, `cell_id`, `style`, `cell`, `cells`, and `matches`. A Miro node is a `MiroStoryNode`: `slug`, `shape`, `shapes`, `fills`, and `matches`. Both write `role` and read it back. A code node is a `CodeStoryNode`: `slug`, `snake`, `pascal`, `camel`, and `name_from_slug`. `CodeScenario` reads calls into steps and ands. Each language overrides `calls_in`, `scenario_blocks`, `backgrounds_in`, `example_names`, `create`, and `CodeStory.load`. A markdown node is a `MarkdownStoryNode`: `strip_backticks` and `strip_markup`. `MarkdownStep` owns `display_text`. `MarkdownScenario` reads the scenario file. A channel overrides only the `has_more_*` and `get_next_*_from_file` reads for the nodes its file contains.
