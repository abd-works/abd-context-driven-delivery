# cdd_guidance/practices/stories

*Stories* is the practice; *StoriesReading* is its part in the knowledge graph, and *StoryTree* is the story map as the graph holds it. A *StoryModel* holds *Epic* and *Story* objects (and their scenarios and steps), and the diagram format extends them as *DiagramStoryModel*, *DiagramEpic*, and *DiagramStory*. The whole model of this module, internals included, is `cdd_guidance/practices/stories/model/.context/story-model.md`; that document is canonical, and this section shows only the classes other modules use.

- **Purpose:** Keep one Epic, Story, Scenario hierarchy that discovery, specification, and tests all read, so scope and behaviour stay traceable from the map to the code.
- **Seam (terms):** Stories, StoriesReading, StoryTree, StoryModel, Epic, Story, DiagramStoryModel, DiagramEpic, DiagramStory
- **Dependencies (one-way):** harness/annotations, harness/agent_tools, harness/markdown, harness/guidance, harness/graph, cdd_guidance/practices/sketch_document, cdd_guidance/practices/clean_engineering, cdd_guidance/practices/ddd (StoriesReading reads DDD's reading beside its own; DDD imports nothing of Stories)

## Stories : PracticeGuidance

The Stories practice: story map, scenarios, and acceptance tests.

+ Stories(fidelity: str = 'story_map', format: str | None = None, story_test_folder: str | None = None)
------
+ story_test_folder: str | None
+ formats_type: type
	// StoriesFormats
+ reading_type: type
	// StoriesReading
----
+ read_folder(root: Path, on_file = None): StoryModel
+ read_files(files: list[Path], project: Path, on_file = None): StoryModel
	// a story test's scenarios go on the map's Story of the same name; a test with no map listed reads the map in its own folder or the nearest one above it
---<<creates>>--> StoryModel
---<<reads the graph with>>--> StoriesReading
---<<registers with>>--> StoryNode

## StoriesReading : PracticeReading

How Stories takes part in the graph: it reads the story tests under its root, or the story maps there when there are none, writes the story map onto its graph, and links each step to the Clean Engineering operations it calls; it reads after Clean Engineering.

------
+ reads_after: tuple[str, ...]
+ root: Path
+ << composition >> story_tree: StoryTree
+ object_model: PracticeReading | None
	// Clean Engineering's reading, from the same graph
+ domain_model: PracticeReading | None
	// DDD's reading, from the same graph
----
+ read_working_copy(): None
---<<loads>>--> StoryModel
---<<finds a reading with>>--> CleanEngineering
---<<finds a reading with>>--> Ddd
---<<creates>>--> StoryTree

## StoryTree

The story map as the graph holds it: each epic's sub-epics and stories, each story's scenarios, each scenario's steps.

+ StoryTree(stories: PracticeReading)
------
+ stories: PracticeReading
----
+ epic_of(node): Node | None
+ sub_epics(epic): list
+ stories_under(epic): list
+ scenarios(story): list
+ steps(scenario): list

## StoryModel : StoryNode

One story map: its epics and increments, and the files it was read from (*StorySources*, one *StorySource* each).

+ StoryModel(source: StoryModel | Graph | None = None, graph: Graph | None = None)
------
+ << composition >> epics: list[Epic]
	// numbered in the order they stand: an epic appended takes the next number
+ increments: list[Increment]
+ sources: StorySources
	// each file the map was read from: its path and text, and the imports, exports, examples and evidence it declares
+ links: StoryMapLinks | None
+ << composition >> descendants: Descendants
	// every epic and story under the map, the stories a thin slice names, and the node a path names
+ << composition >> test_scenarios: StoryTestScenarios
	// take(stories, file), add(stories, file), drop(): the scenarios its stories take from the story tests that specify them
+ opened: OpenedStoryMap | UnopenedStoryMap
	// where it was opened in a session; save() writes it back after every edit
----
+ copy_of(source: StoryModel): StoryModel
+ record(practice, on_node: Callable[[str], None] | None = None): None
	// an example's facts are looked up only in sources, the files the story map was read from
+ clone(): StoryModel
---<<keeps>>--> Epic
---<<reads its files from>>--> StorySources
---<<records through>>--> StoryRecording

## Epic : StoryNode

An epic; a nested epic is an epic whose parent is an epic.

+ Epic(name: str | Epic, sequential_order: int = 0, story_class: type | None = None)
------
+ epics: list[Epic]
+ << composition >> stories: list[Story]
+ has_epics: bool
+ is_sub_epic: bool
+ top_epic: Epic
+ depth: int
+ << composition >> descendants: Descendants
	// every epic and story under it, and place_in(file)
+ << composition >> columns: EpicColumns
	// leaf_epics(), estimate_label(), has_estimate(), span(), diagram_span(), tree_depth(): how a drawn map lays it out
----
+ record(recording: StoryRecording, parent): None
+ clone(): Epic
+ load_map_facts(): None
---<<keeps>>--> Story

## Story : StoryNode

One story under an epic, with its scenarios.

+ Story(name: str | Story, sequential_order: int = 0, story_type: StoryType = StoryType.USER)
------
+ story_type: StoryType
+ actors: list[str]
+ domain_terms: list[str]
+ backgrounds: list[Background]
+ << composition >> scenarios: list[Scenario]
+ code_key: tuple
+ top_epic: Epic | None
----
+ load_map_facts(): None
+ record(recording: StoryRecording, parent): None
+ clone(): Story

## DiagramStoryModel : StoryModel

Story map whose epics and stories are the diagram types.

------
+ max_sub_epic_depth: int
+ actor_y: int
+ sub_epic_top: int
+ story_floor: int
+ story_y: int
----
+ sub_epic_y(depth: int): int
+ bar_y(top: int, depth: int): int
+ line_y(floor: int, top: int, max_sub_epic_depth: int): int
---<<makes its epics as>>--> DiagramEpic
---<<makes its stories as>>--> DiagramStory

## DiagramEpic : Epic, DiagramStoryNode

An epic as the story map diagram draws it.

------
----

## DiagramStory : Story, DiagramStoryNode

A story as the story map diagram draws it.

------
----
