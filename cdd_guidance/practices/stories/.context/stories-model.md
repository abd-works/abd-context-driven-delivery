# cdd_guidance/practices/stories

*Stories* is the practice; *StoriesReading* is its part in the knowledge graph, and *StoryTree* is the story map as the graph holds it. A *StoryMap* holds *Epic* and *Story* objects (and their scenarios and steps), and the diagram format extends them as *DiagramStoryMap*, *DiagramEpic*, and *DiagramStory*. The whole model of this module, internals included, is `cdd_guidance/practices/stories/model/.context/story-model.md`; that document is canonical, and this section shows only the classes other modules use.

- **Purpose:** Keep one Epic, Story, Scenario hierarchy that discovery, specification, and tests all read, so scope and behaviour stay traceable from the map to the code.
- **Seam (terms):** Stories, StoriesReading, StoryTree, StoryMap, Epic, Story, DiagramStoryMap, DiagramEpic, DiagramStory
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
+ read_folder(root: Path, on_file = None): StoryMap
+ read_files(files: list[Path], project: Path, on_file = None): StoryMap
	// a story test's scenarios go on the map's Story of the same name; a test with no map listed reads the map in its own folder or the nearest one above it
+ reads_file_at(fidelity: str | None): StoryExampleFiles
	// the story map examples alone at the story map; no whole-map example at the story map or at no fidelity
---<<creates>>--> StoryMap
---<<reads the graph with>>--> StoriesReading
---<<registers with>>--> StoryNode

## StoriesReading : PracticeReading

How Stories takes part in the graph: it reads the story tests under its root, or the story maps there when there are none, writes the story map onto its graph, and links each step to the Clean Engineering operations it calls; it reads after Clean Engineering.

------
+ reads_after: tuple[type[PracticeGuidance], ...]
+ root: Path
+ << composition >> story_tree: StoryTree
+ object_model: PracticeReading | None
	// Clean Engineering's reading, from the same graph
+ domain_model: PracticeReading | None
	// DDD's reading, from the same graph
----
+ read_working_copy(): None
---<<loads>>--> StoryMap
---<<finds a reading with>>--> CleanEngineering
---<<finds a reading with>>--> Ddd
---<<creates>>--> StoryTree

## StoryTree

The story map as the graph holds it (`stories/model/story_tree.py`): each epic's sub-epics and stories, each story's scenarios, each scenario's steps, and the one definition of the step and epic node types (`STEP_TYPES`, `EPIC_TYPES`, `LINKED_TYPES`, `STORY_MAP_TYPES`) and of a node's key (`KEY_SEPARATOR`), and the type of a story's example (`EXAMPLE_TYPE`). UX asks it rather than keeping copies; the Validate action asks each checked practice's node types (`PracticeNodeTypes.scope_types`, Stories' *StoryNodeTypes*) which types a session's stories scope.

+ StoryTree(stories: PracticeReading)
------
+ stories: PracticeReading
----
+ StoryTree.of_graph(graph): StoryTree | None
+ epic_of(node): Node | None
+ sub_epics(epic): list
+ stories_under(epic): list
+ scenarios(story): list
+ steps(scenario): list
+ every_step(): list
+ examples(): list
+ examples_by_file(): dict[str, list]
+ scenario_of(step): Node | None
+ story_of(node): Node | None
+ background_steps(story): list
+ area_of(node): Node
+ step_text(step), step_phase(step), step_body(step): str
+ steps_saying(text): list
+ StoryTree.key_of(node): str
+ nodes_keyed(kind, key): list
+ written_nodes(): WrittenStoryNodes
	// the nodes by the file each was read from, for a run of links that each name a file and a heading

## WrittenStoryNodes

+ WrittenStoryNodes(tree: StoryTree)
----
+ node_written_at(kind, target, key, written_in): Node | None

## StoryMap : StoryNode

One story map: its epics and increments, and the files it was read from (*StorySources*, one *StorySource* each).

+ StoryMap(source: StoryMap | Graph | None = None, graph: Graph | None = None)
------
+ << composition >> epics: list[Epic]
	// numbered in the order they stand: an epic appended takes the next number
+ increments: list[Increment]
+ unplaced_stories: list[Story]
	// the stories a scenarios file specifies that this map does not hold; each is recorded with its scenarios under no epic, so the rule scenarios-name-a-story-on-the-map reports it
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
+ copy_of(source: StoryMap): StoryMap
+ record(practice, on_node: Callable[[str], None] | None = None): None
	// an example's facts are looked up only in sources, the files the story map was read from
+ clone(): StoryMap
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
----
+ leaf_epics(): list[Epic]
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

## DiagramStoryMap : StoryMap

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
