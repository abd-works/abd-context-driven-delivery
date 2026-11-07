# UX map

*UxMap* is one information architecture: screens, then each screen's regions, controls, and interactions, then the transitions between screens, the content types and nav components the screens share, and one context of notes and invariants. Every node is a graph node (*BoundNode*), so a map is also the UX practice's part of the knowledge graph.

Each format is a *UxMap* subclass, listed by `Ux` under `formats`: drawio, html, markdown, json, claude_design. A format adds no node types of its own; it reads with `parse(content)` into a new map of its class and writes with `render(ux_map)`. JSON and HTML carry the whole map. Draw.io carries screens, their regions, and transitions. Markdown carries the scope and the context. Claude Design places the prototype screens on a canvas and is never read back.

```
ux_map = JsonUxMap.from_workspace(folder)       # ux-map.json or ux.json in the folder
drawio = DrawioUxMap.create().render(ux_map)
```

# practices/ux/model

- **Purpose:** Keep the information architecture as one UX map — screens, regions, controls, and the transitions between screens — so a diagram, a JSON file, and an HTML mockup stay the same hierarchy every later fidelity reads.
- **Seam (terms):** UxMap, Screen, Region, Control, StoryDemoControl, StoryStep, Interaction, UxComponent, Transition, ContentType, NavComponent, UxContext, ReferencePaths, and one UxMap subclass per format
- **Dependencies (one-way):** harness/graph (*BoundNode*, *BoundChildren*, *Graph*), harness/name (*Name*); the Claude Design story canvas also uses practices/stories/model (*DiagramStoryModel*, *StoryModel*) and harness/design_canvas (*DesignCanvas*)

These dependencies are owned by the modules named; this model only uses them. A screen names the stories, scenarios, and steps it shows as text keyed the way Stories keys them; the graph turns each name into a `shownOn` edge from the Stories node to the screen (`harness/graph/schema_edges.py`). A link from one screen to another — a transition, a tab's chrome, an interaction's destination, a nav destination — holds the *Screen* itself, so renaming a screen keeps it.

## UxNode : BoundNode

Every node of the map. Each child belongs to its owner on the graph: a screen, transition, content type, nav component, and context to the map; a region to its screen; a control to its region; an interaction to its control.

+ UxNode(name: str, sequential_order: int, graph: Graph | None = None)

## UxMap : UxNode

+ UxMap(name: str = "UxMap", sequential_order: int = 0, graph: Graph | None = None)
------
+ scope: str
+ story_references: ReferencePaths
	// paths to story JavaScript. A path is stored once
+ object_references: ReferencePaths
	// paths to object-model JavaScript. A path is stored once
+ screens: list[Screen]
	// composition — a screen has no map outside this UX map
+ transitions: Transitions
	// composition
+ content_types: ContentTypes
	// composition
+ nav_components: NavComponents
	// composition
+ context: UxContext
	// composition — the map has one context
+ workspace_files: tuple[str]
	// class field: where this format's map sits in a folder, as glob patterns tried in order
----
+ create(name: str | Graph = "UxMap", sequential_order: int = 0, graph: Graph | None = None): UxMap
	// class operation: a new map, or, given a graph, the map already on that graph
+ from_workspace(root: Path): UxMap | None
	// class operation: the map this format reads from its file in root; none when the folder has no such file
	-> workspace_file(root)
	-> parse
+ workspace_file(root: Path): Path | None
+ parse(content: str): UxMap
	// each format: a new map of this class read from content
+ render(ux_map: UxMap): str
	// each format: ux_map written in this format
+ append_screen(screen: Screen): None
+ remove_screen(screen_name: str): Screen
+ find_screen(name: str): Screen
	// raises ScreenNotOnMap when the map has no screen of that name
+ all_story_names(): list[str]
	// the story names on the screens, each name once
+ story_outline(): list[dict]
	// the epics and sub-epics above the stories the screens show on the map's graph, for the story explorer

## ScreenNotOnMap : KeyError

+ name: str

## Screen : UxNode

+ Screen(name: str, sequential_order: int, slug: str = "", layout: str = "", description: str = "", chrome_of: Screen | None = None, graph: Graph | None = None)
	// slug defaults to the name's title slug
------
+ slug: str
+ layout: str
+ description: str
+ chrome_of: Screen | None
	// the screen whose chrome this tab shares
+ inactive_tabs: list[str]
+ shows: list[Story]
	// the stories on the screen's graph it shows; each records shownOn this screen
+ shows_scenarios: list[Scenario]
+ shows_steps: list[Step]
+ story_keys: list[str]
	// the stories it shows as the formats write them, by name
+ scenario_keys: list[str]
	// as Story › Scenario
+ step_keys: list[str]
	// as Story › Scenario › Step
+ domain_terms: list[str]
+ domain_concepts: list[str]
+ image: str
	// a capture of the screen
+ prototype: str
	// the screen's Claude Design artboard; it wins over image wherever both exist
+ regions: list[Region]
	// composition — a region has no screen outside this screen
----
+ apply_layout(layout_id: str): None
	// sets layout. The caller appends the regions. This does not create regions
+ append_region(region: Region): None
+ show_story(story: Story | str): None
+ show_scenario(scenario: Scenario | str): None
+ show_step(step: Step | str): None
	// the node, or its key; each is held once as a StoryLink, and the graph's shows and shownOn edges follow it
+ lists(node: Story | Scenario | Step): bool
	// true for a node it shows, or one with that node's key drawn on another graph
+ attach_domain_term(term: str): None

## StoryLink

A story, scenario, or step a screen shows: the Stories node once it is on the screen's graph, so a renamed story keeps its screens; until then the key the formats store.

+ kind: str
	// Story, Scenario, or Step
+ node: Story | Scenario | Step | None
+ key: str
	// the node's key once it holds the node, else the key it was given
----
+ from_item(kind: str, item: Story | Scenario | Step | str): StoryLink
+ resolved_on(graph: Graph): Story | Scenario | Step | None
	// finds the node with its key on graph and holds it from then on
+ names(node: Story | Scenario | Step): bool

## Region : UxNode

+ Region(name: str, sequential_order: int, area: str = "", graph: Graph | None = None)
------
+ area: str
+ controls: list[Control]
	// composition
----
+ append_control(control: Control): None

## Control : UxNode

+ Control(name: str, sequential_order: int, control_type: str = "", label: str = "", bound_field: str = "", graph: Graph | None = None)
------
+ control_type: str
	// what the control is on the screen: button, field, list
+ label: str
	// the name when none is given
+ bound_field: str
	// the expose path this control displays. The control does not own the domain value
+ states: list[str]
+ interactions: list[Interaction]
	// composition
----
+ append_interaction(interaction: Interaction): None

## StoryDemoControl : Control

A control that runs story steps in the Story Demo's Play and Interactive modes.

+ StoryDemoControl(name, sequential_order, control_type = "", label = "", bound_field = "", story_steps = None, set_input = "", item_story_steps = None, item_value = "", item_label = "", graph = None)
------
+ story_steps: list[StoryStep]
	// Play emphasizes that step. Interactive runs the When
+ set_input: str
	// the scenario input this control's value fills
+ item_story_steps: list[StoryStep]
	// the When each item of a bound list runs
+ item_value: str
+ item_label: str

## StoryStep

A story step a control runs: its kind (given, when, then) and the step text Stories wrote. Frozen.

+ kind: str
+ label: str
----
+ from_value(value: StoryStep | Mapping): StoryStep
	// class operation: a step from a file's {kind, label} object, or the step itself
+ as_dict(): dict

## Interaction : UxNode

+ Interaction(name: str, sequential_order: int, trigger: str = "", effect: str = "", destination: Screen | None = None, graph: Graph | None = None)
------
+ trigger: str
	// the name when none is given
+ effect: str
+ destination: Screen | None
	// association to a screen on the same map

## UxComponent : UxNode

A structural peer of the screens on the map: a transition, a content type, or a nav component.

## Transition : UxComponent

+ Transition(name: str, sequential_order: int, from_screen: Screen | None = None, to_screen: Screen | None = None, trigger: str = "", nav_type: str = "action", graph: Graph | None = None)
------
+ from_screen: Screen | None
+ to_screen: Screen | None
+ trigger: str
+ nav_type: str
	// "tab" draws dashed on the site map

## ContentType : UxComponent

+ ContentType(name: str, sequential_order: int, hierarchy: str = "", graph: Graph | None = None)
------
+ hierarchy: str
+ key_actions: list[str]

## NavComponent : UxComponent

+ NavComponent(name: str, sequential_order: int, ux_type: str = "", graph: Graph | None = None)
------
+ ux_type: str
+ destinations: list[Screen]

## UxContext : UxNode

+ UxContext(name: str = "context", sequential_order: int = 0, graph: Graph | None = None)
------
+ notes: list[str]
+ invariants: list[str]

## UxComponentCollection

One kind of *UxComponent* on the map. Appending records the map's edge to the component and renumbers the collection. *Transitions*, *ContentTypes*, and *NavComponents* each accept only their own type.

+ UxComponentCollection(owner: UxNode)
----
+ append(component: UxComponent): None
	// raises TypeError for a component of another kind
+ remove(name: str): UxComponent
+ find(name: str): UxComponent

## ReferencePaths

Ordered paths to story or object-model JavaScript, each stored once.

+ ReferencePaths(paths: Iterable[str] | None = None)
----
+ add(path: str): None
+ replace(paths: Iterable[str]): None
+ clear(): None
+ as_list(): list[str]

---

## Formats

Each format class below is a *UxMap* subclass. It overrides `parse`, `render`, and `workspace_files`, and builds the base node types; a reader or writer class beside it holds the steps.

## JsonUxMap : UxMap

The `json` format: the whole map as one JSON document; every other format can round-trip through it. Files: `ux-map.json`, `ux.json`.

----
+ parse(content: str | dict): UxMap
	-> JsonUxMapReader.read
+ render(ux_map: UxMap): str
	-> JsonUxMapWriter.map_record

## JsonUxMapReader

+ JsonUxMapReader(ux_map: UxMap, data: dict)
----
+ read(): UxMap
	Invariant: every screen is on the map before any link to a screen is read, so a transition, a tab, or a destination names a screen that is already there

## JsonUxMapWriter

+ map_record(ux_map: UxMap): dict
	// a link to a screen is written as that screen's name

## HtmlUxMap : UxMap

The `html` format: the mockup review page, product screens on the left and the story explorer on the right, with the JSON map embedded in a `ux-map-json` comment. Files: `{folder}.html`, `index.html`, `mockup.html`, `ux.html`.

----
+ parse(content: str): UxMap
	// raises UxMapNotEmbedded when the page carries no ux-map-json comment
	-> JsonUxMap.parse
+ render(ux_map: UxMap): str
	// fills templates/html/mockup_shell.html; each control carries the data attributes the Story Demo runner reads

## UxMapNotEmbedded : ValueError

## DrawioUxMap : UxMap

The `drawio` format: a Site Map page and a Detailed IA page, written through the vendored drawio-ux command line (`drawio_ux.mjs`). Files: `information-architecture.drawio`, `ia.drawio`, `site-map.drawio`, any `.drawio` in the folder.

------
+ cli_timeout_seconds: float
----
+ parse(content: str): UxMap
	// JSON content reads through JsonUxMap; otherwise raises UnreadableDrawio when content is not XML
	-> DrawioUxMapReader.read
+ render(ux_map: UxMap): str
	// raises DrawioCliMissing, DrawioCliFailed, or DrawioCliTimedOut
	-> ux_map_to_cli_state

## DrawioUxMapReader

+ DrawioUxMapReader(ux_map: UxMap, root_element: Element)
----
+ read(): UxMap
	// screens from the Site Map page, then each screen's regions from the Detailed IA page, then the transitions drawn between screens. An edge labelled "there / back" is two transitions

## MarkdownUxMap : UxMap

The `markdown` format: the scope, then the invariants and notes as bullet lists under their own headings. It carries no screens. Files: `.context/ux-context.md`, `ux-context.md`, `.context/context.md`, `context.md`.

----
+ parse(content: str): UxMap
	-> MarkdownContextReader.read
+ render(ux_map: UxMap): str

## MarkdownContextReader

+ MarkdownContextReader(ux_map: UxMap)
----
+ read(content: str): None
	// any line outside the scope, or a bullet under any other heading, is a note

## ClaudeDesignUxMap : UxMap

The `claude_design` format: one board per prototype screen, each on its own canvas page.

------
+ folder: str
+ page: str
+ width: int
+ height: int
----
+ render(ux_map: UxMap): str
	// the boards as JSON
+ parse(content: str): UxMap
	// raises ClaudeDesignScreensNotReadable: screens are placed from the UX map and edited on the canvas
+ prototype_names(screens): list[str]
+ names(screens, files = ()): list[str]
+ title(name: str): str
+ page_of(name: str): str
+ pages(screens, files = ()): list[dict]
+ boards(screens, files = ()): dict[str, dict]

## ClaudeDesignStoryModel

The Claude Design story canvas — the story map, the story explorer, and the screens each story is shown on — is a Stories *DiagramStoryModel* drawn in `claude_design/story_canvas.py`, described in `claude_design/story_canvas.md`. It reads this map's screens and *ClaudeDesignUxMap*'s page and folder.
