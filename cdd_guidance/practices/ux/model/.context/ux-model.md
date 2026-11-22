# UX map

*UxMap* is one information architecture: screens, then each screen's regions, controls, and interactions, then the transitions between screens, the content types and nav components the screens share, and one context of notes and invariants. Every node is a graph node (*ModelNode*), so a map is also the UX practice's part of the knowledge graph.

Each format is a *UxMap* subclass, listed by `Ux` under `formats`: drawio, html, markdown, json, claude_design. A format names the node types that write it its own way, and reads with `parse(content)` into a new map of its class and writes with `render(canonical)`. The UX practice registers itself on *UxNode*, so the model never imports its practice. JSON and HTML carry the whole map. Draw.io carries screens, their regions, and transitions. Markdown carries the scope and the context. Claude Design places the prototype screens on a canvas and is never read back.

```
ux_map = JsonUxMap.create().parse(text)         # the text of ux-map.json or ux.json
drawio = DrawioUxMap.create().render(ux_map)
```

# practices/ux/model

- **Purpose:** Keep the information architecture as one UX map — screens, regions, controls, and the transitions between screens — so a diagram, a JSON file, and an HTML mockup stay the same hierarchy every later fidelity reads.
- **Seam (terms):** UxMap, Screen, Region, Control, StoryDemoControl, StoryStep, Interaction, UxComponent, Transition, ContentType, NavComponent, UxContext, ReferencePaths, and one UxMap subclass per format
- **Dependencies (one-way):** harness/graph (*ModelNode*, *ModelChildren*, *Graph*), harness/annotations (*Name*); the Claude Design story canvas also uses practices/stories/model (*DiagramStoryModel*, *StoryModel*) and harness/design_canvas (*DesignCanvas*)

These dependencies are owned by the modules named; this model only uses them. A screen names the stories, scenarios, and steps it shows as text keyed the way Stories keys them; the graph turns each name into a `shownOn` edge from the Stories node to the screen (`harness/graph/schema_edges.py`). A link from one screen to another — a transition, a tab's chrome, an interaction's destination, a nav destination — holds the *Screen* itself, so renaming a screen keeps it.

## UxNode : ModelNode

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
+ map_file_suffixes: tuple[str]
	// class field: the file endings this format's map is written with; none for a format no file is read back from
+ not_a_map_failures: tuple[type[Exception]]
	// class field: what reading a file fails with when the file is not this format's map after all
----
+ create(name: str | Graph = "UxMap", sequential_order: int = 0, graph: Graph | None = None): UxMap
	// class operation: a new map; given a graph in place of a name, a map whose nodes live on that graph
+ reads_file(file: Path, text: str): bool
	// each format: whether file, which holds text, is a UX map in this format
+ parse(content: str): UxMap
	// each format: a new map of this class read from content
+ render(canonical: UxMap): str
	// each format: canonical written in this format
+ append_screen(screen: Screen): None
+ find_screen(name: str): Screen
	// raises ScreenNotOnMap when the map has no screen of that name

## ScreenNotOnMap : KeyError

+ name: str

## Screen : UxNode

+ Screen(name: str, sequential_order: int, graph: Graph | None = None)
	// its slug (from its name while it is given none), layout, description and chrome_of are set once it is made
	// slug defaults to the name's title slug
------
+ slug: str
+ layout: str
+ description: str
+ chrome_of: Screen | None
	// the screen whose chrome this tab shares
+ chrome_of_name: str
	// that screen's name; blank while it is the chrome of none
+ inactive_tabs: list[str]
+ shows: list[Story]
	// the stories on the screen's graph it shows; each records shownOn this screen
+ shows_scenarios: list[Scenario]
+ shows_steps: list[Step]
+ story_keys: list[str]
	// the stories it shows as the formats write them, by name
+ story_links: list[StoryLink]
	// the stories it shows, in order: each link holds its Story once the screen's graph has it, else only its name
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
+ resolved_in(story_tree: StoryTree | None, written_in): Story | Scenario | Step | None
	// finds the node its target or key names in Stories' StoryTree and holds it from then on
+ found_in(written: WrittenStoryNodes, story_tree: StoryTree, written_in): Story | Scenario | Step | None
	// the node it names, through the nodes by file a run of links shares
+ names(node: Story | Scenario | Step): bool

## Region : UxNode

+ Region(name: str, sequential_order: int, graph: Graph | None = None)
	// its area is set once it is made
------
+ area: str
+ controls: list[Control]
	// composition
----
+ append_control(control: Control): None

## Control : UxNode

+ Control(name: str, sequential_order: int, graph: Graph | None = None)
	// its control_type, label (its name while it names none) and bound_field are set once it is made
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

+ StoryDemoControl(name, sequential_order, graph = None)
	// its story fields are set once it is made, or taken from another (`take_story_fields(source)`)
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
+ from_values(steps: Iterable[StoryStep | Mapping] | None): list[StoryStep]
	// class operation: each step a file lists, in its order
+ as_dict(): dict

## Interaction : UxNode

+ Interaction(name: str, sequential_order: int, graph: Graph | None = None)
	// its trigger (its name while it names none), effect and destination are set once it is made
------
+ trigger: str
	// the name when none is given
+ effect: str
+ destination: Screen | None
	// association to a screen on the same map
+ destination_name: str
	// that screen's name; blank while it goes to none

## UxComponent : UxNode

A structural peer of the screens on the map: a transition, a content type, or a nav component.

## Transition : UxComponent

+ Transition(name: str, sequential_order: int, graph: Graph | None = None)
	// joining(from_screen, to_screen) sets the screens it joins; its trigger (its name while it names none) and nav_type are set once it is made
------
+ from_screen: Screen | None
+ to_screen: Screen | None
+ from_name: str
+ to_name: str
	// the names of the screens it joins; blank for a screen it lacks
+ trigger: str
+ nav_type: NavType
	// an action, a tab (drawn dashed on the site map), or a kind a sketch names; saved as the string it is written as

## NavType : str

+ NavType.ACTION, NavType.TAB
+ NavType.from_drawn(kept: str, dashed: bool): NavType
	// the kind a drawn transition keeps by name, else a tab for a dashed line, else an action
------
+ is_tab: bool
+ is_named_on_label: bool
	// every kind but an action and a tab, which a drawing writes before the trigger: `[top nav] Check out`

## Served

What a screen or a control serves (`ServesStories.served`), in the one notation every text format lists it in: a line
for each kind it serves any of, `Stories: Browse Books · Check Out`, the things joined by ` · `.

+ Served(node: ServesStories)
+ Served.kind_headed(heading: str): str
------
+ stories, scenarios, steps: list[StoryLink]
----
+ serve(kind: str, shown: str): None
+ as_lines(link_text: Callable[[StoryLink], str]): list[str]
+ read_lines(lines: list[str]): None

## ContentType : UxComponent

+ ContentType(name: str, sequential_order: int, graph: Graph | None = None)
------
+ hierarchy: str
+ key_actions: list[str]

## NavComponent : UxComponent

+ NavComponent(name: str, sequential_order: int, graph: Graph | None = None)
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

## ReferencePaths

Ordered paths to story or object-model JavaScript, each stored once.

+ ReferencePaths(paths: Iterable[str] | None = None)
----
+ add(path: str): None
+ replace(paths: Iterable[str]): None
+ as_list(): list[str]

---

## Formats

Each format class below is a *UxMap* subclass. It overrides `parse` and `save`, says which files are its own (`map_file_suffixes`, `reads_file`) and what reading a file that is no map fails with (`not_a_map_failures`), and names the node types it is made of (`screen_type`, `region_type`, `control_type`, `story_demo_control_type`, `transition_type`, `content_type_type`, `nav_component_type`), which its reading and `copy_of` make. `render(canonical)` asks the format's own map to copy the map it is given (`copy_of`, an instance method as a story map's is); the copy is detached, keeping the stories each screen shows by key, and writes itself with `save`. Each format's map reads its own file in `parse`, and its screens, regions, and other nodes read their own part of it.

## JsonUxMap : UxMap

The `json` format: the whole map as one JSON document; every other format can round-trip through it. Files: `ux-map.json`, `ux.json`.

----
+ parse(content: str | dict): UxMap
	-> _read_record(data)
- _read_record(data: dict): None
	// its own fields, then each part reading its own record
	-> JsonScreen.from_record, JsonScreen.read_record, JsonTransition.from_record, JsonContentType.from_record, JsonNavComponent.from_record
	Invariant: every screen is on the map before any link to a screen is read, so a transition, a tab, or a destination names a screen that is already there
+ screen_named(name: str): Screen | None
+ render(canonical: UxMap): str
	-> copy_of(canonical).save
- _map_record(): dict
	// this map: each screen, transition, content type, and navigation component writes its own record; a link to a screen is written as that screen's name

Its nodes are JsonScreen, JsonRegion, JsonControl, JsonStoryDemoControl, JsonTransition, JsonContentType, and
JsonNavComponent, each writing its own record (`as_record()`) and reading one back (`from_record`). The HTML format's
controls subclass the JSON controls, since the page carries the JSON document.

## HtmlUxMap : JsonUxMap

The `html` format: the mockup review page, product screens on the left and the story explorer on the right, with the JSON map embedded in a `ux-map-json` comment. It is the JSON format inside a page: parse and render ask the JSON format for the document the page carries. Files: any `.html` page that carries the comment.

----
+ parse(content: str): UxMap
	// raises UxMapNotEmbedded when the page carries no ux-map-json comment
	-> JsonUxMap.parse
+ save(): str
	// fills templates/html/mockup_shell.html; each HtmlControl writes its own markup and the data attributes the Story Demo runner reads
	-> ExplorerTree(screens).as_json()
	-> JsonUxMap.save

## ExplorerTree

The story explorer's tree of a map (`explorer_tree.py`), which the mockup page carries as `#story-explorer-tree` for
`story-demo/screen-tree.js` to draw; the JavaScript decides nothing about where a screen sits. Each epic of the story
map above the stories the screens show comes in the order the screens first show it; under it come its sub-epics at any
depth that hold a shown story, then the screens under each by the stories they show there, ranked by the first of those
in story-map order. A screen whose stories sit on the epic itself hangs on the epic, and a screen can sit under several
epics. With no story map on the map's graph, the screens are listed flat. Each screen holds its stories, their
scenarios, and their steps, read from the story map through Stories' *StoryTree* (`Stories.story_tree`), which reads the
graph's edges and saved facts, so a graph opened from its save gives the tree a fresh build gives. Each step carries its
screen's `domain_terms` (`domainTerms`), the only words the page underlines.

+ ExplorerTree(screens: list[Screen])
------
+ story_tree: StoryTree | None
	// the story map's tree on the graph of the stories the screens show; none when they show none on a graph
+ screens: list[ExplorerScreen]
	// each screen by the slug the page marks it with, holding the stories it shows
+ nodes: list[dict]
	// epic → sub-epic → screen → story → scenario → step, each with its kind, name, and key
+ screen_keys: dict[str, list[str]]
	// for each screen, the keys the explorer opens to show it: its epic's, its sub-epic's, and its own, where it first sits
----
+ as_json(): dict
	// `{nodes, screenKeys}`, as the page carries it

## HtmlControl : Control, HtmlStoryDemoControl : StoryDemoControl, HtmlControl

The HTML page's controls: `html()` writes a visible affordance for the control type with the data attributes its interactions and the Story Demo runner read.

## UxMapNotEmbedded : ValueError

## DrawioUxMap : UxMap

The `drawio` format: a Site Map page and a Detailed IA page, written through the vendored drawio-ux command line (`drawio_ux.mjs`). Files: any `.drawio` the command line wrote, or one with a Site Map or Detailed IA page.

------
+ cli_timeout_seconds: float
----
+ parse(content: str): UxMap
	// raises UnreadableDrawio when content is not XML; JSON content is read with source json
	-> _read_pages
- _read_pages(root_element: Element): None
	// screens from the Site Map page (DrawioScreen.from_cell), then each screen reads its regions from its own box on the Detailed IA page (DrawioScreen.read_regions, DrawioRegion.from_cell), then the transitions drawn between screens. An edge labelled "there / back" is two transitions
+ render(canonical: UxMap): str
	// copies ux_map into a DrawioUxMap (DrawioScreen, DrawioRegion), which draws itself
- _cli_state(target: str): dict
	// its screens' and regions' own cli_record parts, and its transitions
+ save(): str
	// raises DrawioCliMissing, DrawioCliFailed, or DrawioCliTimedOut

## MarkdownUxMap : UxMap

The `markdown` format: the scope, then the invariants and notes as bullet lists under their own headings. It carries no screens. Files: `ux-context.md`.

----
+ parse(content: str): UxMap
	-> _read_context
- _read_context(content: str): None
	// any line outside the scope, or a bullet under any other heading, is a note
+ render(canonical: UxMap): str

## ClaudeDesignUxMap : UxMap

The `claude_design` format: one board per prototype screen, each on its own canvas page.

------
+ folder: str
+ page: str
+ width: int
+ height: int
----
+ render(canonical: UxMap): str
	// the boards as JSON
+ parse(content: str): UxMap
	// raises ClaudeDesignScreensNotReadable: screens are placed from the UX map and edited on the canvas
+ prototype_names(): list[str]
+ names(files = ()): list[str]
+ title(name: str): str
+ page_of(name: str): str
+ pages(files = ()): list[dict]
+ boards(files = ()): dict[str, dict]
	// each over this map's own screens

## ClaudeDesignStoryModel

The Claude Design story canvas — the story map, the story explorer, and the screens each story is shown on — is a Stories *DiagramStoryModel* drawn in `claude_design/story_canvas.py`, described in `claude_design/story_canvas.md`. It holds the UX map it is drawn with as a *ClaudeDesignUxMap*, which places the screens, and its *DesignCanvas*, which answers what the canvas project already holds.
