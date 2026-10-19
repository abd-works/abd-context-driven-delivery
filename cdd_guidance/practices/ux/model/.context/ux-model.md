# UX map

*UxMap* reads one file into screens, then each screen's regions, controls, and interactions, and into transitions, content types, nav components, and one context. JSON and HTML continue through controls and interactions. Draw.io stops at regions and also reads transitions. Markdown stops at context. Every channel uses the same walk. A channel only differs in how the next node is taken out of the file.

Callers use the base nodes. `UxModelFactory.load` takes a file or a folder, chooses the channel UX map, and returns a `UxMap`.

```
ux_map = UxModelFactory.load(path)
```

# practices/ux/model

- **Purpose:** Keep the information architecture as one UX map — screens, regions, controls, and the transitions between screens — so a diagram, a JSON file, and an HTML mockup stay the same hierarchy every later fidelity reads.
- **Seam (terms):** UxModelFactory, UxMap, Screen, Region, Control, StoryDemoControl, Interaction, Transition, ContentType, NavComponent, UxContext
- **Dependencies (one-way):** *(none)*

## UxModelFactory

+ load(path: str): UxMap
	// path is a file, or a folder of files
	// the file type, or the files in the folder, selects the channel UX map
	// that map loads itself
	// the return is a UxMap

## UxMap

+ UxMap(source: UxMap)
	// source empty: the map is empty until load
	// source set: screens, transitions, content types, and nav components are this channel's types
	// the source context becomes this channel's context
	// the new map does not keep the source's channel types
------
+ file: str
+ scope: str
+ story_references: list[str]
	// paths to story JavaScript. A path is stored once
+ object_references: list[str]
	// paths to object-model JavaScript. A path is stored once
+ screens: list[Screen]
	// composition — a screen has no map outside this UX map
+ transitions: list[Transition]
	// composition
+ content_types: list[ContentType]
	// composition
+ nav_components: list[NavComponent]
	// composition
+ context: UxContext
	// composition — the map has one context
+ screen_type: type
+ transition_type: type
+ content_type: type
+ nav_component_type: type
+ context_type: type
----
+ load(file: str): UxMap
	// stores file, then runs the same walk for every channel
	self.file = file
	self.load_ux_map_content()
	self.load_screens()
	self.load_transitions()
	self.load_content_types()
	self.load_nav_components()
	self.load_context()
+ save(): str
	// every channel writes its file with this operation
+ append_screen(screen: Screen): None
+ remove_screen(name: str): Screen
+ find_screen(name: str): Screen
	// a screen name is unique on the map
+ append_transition(transition: Transition): None
+ append_content_type(content_type: ContentType): None
+ append_nav_component(nav_component: NavComponent): None
+ all_story_names(): list[str]
	// the story names on the screens, each name once
- load_ux_map_content(): None
	// channel prepares its cursor over file
- load_screens(): None
	// while has_more_screen: append_screen(load_next_screen())
- has_more_screen(): bool
- load_next_screen(): Screen
	// screen = get_next_screen_from_file()
	// -> screen.load_regions()
- get_next_screen_from_file(): Screen
	// channel: the next screen shell from file, in screen_type
- load_transitions(): None
	// while has_more_transition: append_transition(load_next_transition())
- has_more_transition(): bool
- load_next_transition(): Transition
	// transition = get_next_transition_from_file()
- get_next_transition_from_file(): Transition
	// channel: the next transition, in transition_type
- load_content_types(): None
	// while has_more_content_type: append_content_type(load_next_content_type())
- has_more_content_type(): bool
- load_next_content_type(): ContentType
- get_next_content_type_from_file(): ContentType
- load_nav_components(): None
	// while has_more_nav_component: append_nav_component(load_next_nav_component())
- has_more_nav_component(): bool
- load_next_nav_component(): NavComponent
- get_next_nav_component_from_file(): NavComponent
- load_context(): None
	// context = get_context_from_file()
- get_context_from_file(): UxContext
	// channel: the context shell from file, in context_type

## Screen

+ Screen(source: Screen)
	// copies name, order, slug, layout, description, and chrome
	// each source region becomes this channel's region
------
+ name: str
+ sequential_order: int
+ slug: str
+ layout: str
+ description: str
+ chrome_of: str
+ inactive_tabs: list[str]
+ story_names: list[str]
+ domain_terms: list[str]
+ domain_concepts: list[str]
+ regions: list[Region]
	// composition — a region has no screen outside this screen
+ region_type: type
----
+ apply_layout(layout: str): None
	// sets layout. The caller appends the regions. This does not create regions
+ append_region(region: Region): None
+ attach_story_name(story_name: str): None
	// a story name is stored once
+ attach_domain_term(term: str): None
	// a term is stored once
- load_regions(): None
	// while has_more_region: append_region(load_next_region())
- has_more_region(): bool
- load_next_region(): Region
	// region = get_next_region_from_file()
	// -> region.load_controls()
- get_next_region_from_file(): Region
	// channel: the next region shell from the file, in region_type

## Region

+ Region(source: Region)
	// copies name, order, and slot
	// a source StoryDemoControl becomes this channel's story demo control
	// any other source control becomes this channel's control
------
+ name: str
+ sequential_order: int
+ slot: str
+ controls: list[Control]
	// composition
+ control_type: type
	// the channel class that builds the next control. The string on Control is the widget kind
+ story_demo_control_type: type
	// the channel class used when the next control carries story steps
----
+ append_control(control: Control): None
- load_controls(): None
	// while has_more_control: append_control(load_next_control())
- has_more_control(): bool
- load_next_control(): Control
	// control = get_next_control_from_file()
	// -> control.load_interactions()
- get_next_control_from_file(): Control
	// channel: the next control shell, in control_type or story_demo_control_type

## Control

+ Control(source: Control)
	// copies name, order, control type, label, and states
	// each source interaction becomes this channel's interaction
------
+ name: str
+ sequential_order: int
+ control_type: str
	// what the control is on the screen: button, field, list
+ label: str
+ states: list[str]
+ interactions: list[Interaction]
	// composition
+ interaction_type: type
----
+ append_interaction(interaction: Interaction): None
- load_interactions(): None
	// while has_more_interaction: append_interaction(load_next_interaction())
- has_more_interaction(): bool
- load_next_interaction(): Interaction
- get_next_interaction_from_file(): Interaction

## StoryDemoControl : Control

+ StoryDemoControl(source: StoryDemoControl)
	// copies the control fields, then the story-demo bindings
------
+ bound_field: str
	// the expose path this control displays. The control does not own the domain value
+ story_steps: list
	// each entry is a kind and a label. Play emphasizes that step. Interactive runs the When
+ set_input: str
+ item_story_steps: list
+ item_value: str
+ item_label: str

## Interaction

+ Interaction(source: Interaction)
	// copies name, order, trigger, effect, and destination screen
------
+ name: str
+ sequential_order: int
+ trigger: str
+ effect: str
+ destination_screen: str
	// association by screen name

## UxComponent

+ UxComponent(source: UxComponent)
	// copies name and order
------
+ name: str
+ sequential_order: int

## Transition : UxComponent

+ Transition(source: Transition)
	// copies name, order, the two screens, trigger, and nav type
------
+ from_screen: str
+ to_screen: str
+ trigger: str
+ nav_type: str

## ContentType : UxComponent

+ ContentType(source: ContentType)
	// copies name, order, hierarchy, and key actions
------
+ hierarchy: str
+ key_actions: list[str]

## NavComponent : UxComponent

+ NavComponent(source: NavComponent)
	// copies name, order, UX type, and destinations
------
+ ux_type: str
+ destinations: list[str]

## UxContext

+ UxContext(source: UxContext)
	// copies notes and invariants
------
+ notes: list[str]
+ invariants: list[str]

## MarkdownUxNode

+ strip_markup(text: str): str

## MarkdownUxMap : UxMap

+ MarkdownUxMap(source: UxMap)
------
+ screen_type: MarkdownScreen
+ context_type: MarkdownUxContext
----
- load_ux_map_content(): None
	// cursor is the markdown headings in file
- has_more_screen(): bool
	// a markdown file has no screens
- has_more_transition(): bool
- has_more_content_type(): bool
- has_more_nav_component(): bool
- get_context_from_file(): MarkdownUxContext
+ save(): str
	// scope, invariants, and notes

## MarkdownScreen : Screen, MarkdownUxNode

## MarkdownUxContext : UxContext, MarkdownUxNode

## JsonUxNode

+ record(): dict
	// this node's JSON object

## JsonUxMap : UxMap

+ JsonUxMap(source: UxMap)
------
+ screen_type: JsonScreen
+ transition_type: JsonTransition
+ content_type: JsonContentType
+ nav_component_type: JsonNavComponent
+ context_type: JsonUxContext
----
- load_ux_map_content(): None
	// cursor is the JSON object in file
- has_more_screen(): bool
- get_next_screen_from_file(): JsonScreen
- has_more_transition(): bool
- get_next_transition_from_file(): JsonTransition
- has_more_content_type(): bool
- get_next_content_type_from_file(): JsonContentType
- has_more_nav_component(): bool
- get_next_nav_component_from_file(): JsonNavComponent
- get_context_from_file(): JsonUxContext
+ save(): str

## JsonScreen : Screen, JsonUxNode

+ region_type: JsonRegion
----
- has_more_region(): bool
- get_next_region_from_file(): JsonRegion

## JsonRegion : Region, JsonUxNode

+ control_type: JsonControl
+ story_demo_control_type: JsonStoryDemoControl
----
- has_more_control(): bool
- get_next_control_from_file(): JsonControl

## JsonControl : Control, JsonUxNode

+ interaction_type: JsonInteraction
----
- has_more_interaction(): bool
- get_next_interaction_from_file(): JsonInteraction

## JsonStoryDemoControl : StoryDemoControl, JsonUxNode

## JsonInteraction : Interaction, JsonUxNode

## JsonTransition : Transition, JsonUxNode

## JsonContentType : ContentType, JsonUxNode

## JsonNavComponent : NavComponent, JsonUxNode

## JsonUxContext : UxContext, JsonUxNode

## HtmlUxMap : JsonUxMap

+ HtmlUxMap(source: UxMap)
	// HtmlScreen for each screen, then the JSON child types under Html names
------
+ screen_type: HtmlScreen
+ transition_type: HtmlTransition
+ content_type: HtmlContentType
+ nav_component_type: HtmlNavComponent
+ context_type: HtmlUxContext
----
- load_ux_map_content(): None
	// cursor is the ux-map-json comment in file. The reads are the JSON reads
+ save(): str
	// the mockup shell, with the JSON map embedded

## HtmlScreen : JsonScreen

+ region_type: HtmlRegion

## HtmlRegion : JsonRegion

+ control_type: HtmlControl
+ story_demo_control_type: HtmlStoryDemoControl

## HtmlControl : JsonControl

+ interaction_type: HtmlInteraction

## HtmlStoryDemoControl : JsonStoryDemoControl

## HtmlInteraction : JsonInteraction

## HtmlTransition : JsonTransition

## HtmlContentType : JsonContentType

## HtmlNavComponent : JsonNavComponent

## HtmlUxContext : JsonUxContext

## DrawioUxNode

+ strip_html(value: str): str
+ matches_screen(cell): bool
	// a site-map vertex whose value is a screen name
+ matches_region(cell): bool
	// a detailed-IA vertex whose parent is a screen
+ matches_transition(cell): bool
	// a site-map edge between two screens

## DrawioUxMap : UxMap

+ DrawioUxMap(source: UxMap)
------
+ screen_type: DrawioScreen
+ transition_type: DrawioTransition
----
- load_ux_map_content(): None
	// cursor is the Site Map page, then the Detailed IA page, in file
- has_more_screen(): bool
- get_next_screen_from_file(): DrawioScreen
- has_more_transition(): bool
- get_next_transition_from_file(): DrawioTransition
- has_more_content_type(): bool
	// a draw.io file has no content types
- has_more_nav_component(): bool
+ save(): str
	// Site Map and Detailed IA

## DrawioScreen : Screen, DrawioUxNode

+ region_type: DrawioRegion
----
- has_more_region(): bool
- load_next_region(): DrawioRegion
	// returns the region and stops. No controls or interactions
- get_next_region_from_file(): DrawioRegion

## DrawioRegion : Region, DrawioUxNode

## DrawioTransition : Transition, DrawioUxNode

JSON continues through screens, regions, controls, interactions, transitions, content types, nav components, and context. HTML extends those JSON types. `HtmlUxMap.load_ux_map_content` takes the embedded JSON comment as its cursor, and `save` writes the mockup shell. Draw.io extends `UxMap` and stops at regions: `load_next_region` returns the region and does not call `load_controls`. Draw.io also reads transitions from site-map edges. Markdown stops at context. A markdown file has no screens, so `has_more_screen` is false, and `save` writes scope, invariants, and notes. A channel overrides only `has_more_*` and `get_next_*_from_file` for the nodes its file contains. `UxMap` loads screens, transitions, content types, nav components, and context. `Screen` loads regions. `Region` loads controls. `Control` loads interactions. `apply_layout` sets the layout name and does not create regions. `StoryDemoControl` is the control that carries `bound_field` and `story_steps`. Every UX map implements `save(): str`.
