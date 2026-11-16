# cdd_guidance/practices/ux
*Ux* (user experience) defines how users reach the domain, from journey and information architecture to screen navigation. Its fidelities deepen one UX map: *information architecture* decides which screens exist and how users move between them (`ux-ia`); *mockup* locks screens as runnable greybox with typed controls and key interactions (`ux-mockup`); *front-end code* ships the product UI talking to a real backend (`ux-front-end-code`). `ux.instructions` is the practice's guidance at its current fidelity.

The UX map is written as draw.io, HTML, markdown, JSON, or Claude Design, and `render(format, content)` converts between them. *ClaudeDesignStoryModel* (`model/claude_design/story_canvas.py`) draws the Claude Design canvas a stakeholder plays: the story map, the story explorer, and the screens each story is shown on, read from the story model and the UX map. The mockup fidelity declares that canvas as an output in the `claude_design` format (each version's `design-canvas/{version}/project/canvas.json` in the UX root), so the Session Board and the chat bar offer it as the canvas format chip beside the html. `ensure_javascript(practice, source_format, content)` gets the Stories or Clean Engineering JavaScript a mockup needs, rendering it through this session's own copy of that practice when it is missing.

- **Purpose:** Keep screens, navigation, and interactions in one hierarchy that the diagram, the mockup, and the front-end code all follow, in the domain's words.
- **Seam (terms):** Ux, `ux.instructions`, `ux-ia`, `ux-mockup`, `ux-front-end-code`, `render`, `ensure_javascript`
- **Dependencies (one-way):** `cdd_guidance/practices/ux/model` (the UX map and its formats, loaded by format name), `cdd_guidance/practices/stories` (*Stories* and its story model), `harness/guidance` (*PracticeGuidance*, *PracticeCatalogue*), `harness/graph` (its screen rules; *Ux* names the node types the graph offers for it), `harness/agent_tools`. Stories imports nothing of UX.

## Constraint

Name screens and controls in the domain's words, not the layout's. Get another practice's JavaScript through `ensure_javascript`, never by writing it in a UX artifact. Run lifecycle steps through the actions with this practice as guidance, not as methods on *Ux*.

## Packages

These folders have no card of their own: they are packages of this module, and their classes count in it.

### `ux/model`

*UxMap* is the information architecture as one hierarchy: *Screen*s divided into *Region*s that hold *Control*s, the *Interaction*s a control offers, the *Transition*s between screens, the *ContentType*s and *NavComponent*s screens share, and the *UxContext* notes that apply to the whole map. *StoryDemoControl* is a control that runs story steps when used in a mockup. A diagram, a JSON file, and an HTML mockup are all the same *UxMap*, so every later fidelity reads the same screens. How the map reads a file is written in [ux-model.md](ux-model.md).

Each format is one class of the same map, in this module: *DrawioUxMap* (the default IA diagram, through the drawio-ux command line), *HtmlUxMap* (the mockup review page, product screens beside the story explorer, carrying the JSON model inside it), *JsonUxMap* (the full map as JSON), *MarkdownUxMap* (UX context notes), and *ClaudeDesignUxMap*. Each `render`s a *UxMap* and `parse`s back what it rendered: JSON and HTML carry the whole map, draw.io carries screens, regions, and transitions, and markdown carries the scope and the context notes. The HTML page also carries the story explorer's tree (*ExplorerTree*: which epic and sub-epic each screen sits under, and its stories, scenarios, and steps), which the page's JavaScript only draws. HTML reads only a page it rendered, from the JSON it embeds; Claude Design screens are placed on the canvas and never read back. Every node sits on its map's graph, and a link from one screen to another (a transition, a tab's chrome, a destination) holds the *Screen* itself.

- **Purpose:** Keep one UX map that every UX format and fidelity reads, so converting a diagram to a mockup never changes the screens.
- **Terms other packages use:** UxMap, Screen, Region, Control, StoryDemoControl, Interaction, Transition, ContentType, NavComponent, UxContext, DrawioUxMap, HtmlUxMap, JsonUxMap, MarkdownUxMap, ClaudeDesignUxMap, ExplorerTree
- **Uses:** `harness/graph` (the map's nodes are graph nodes), `harness/annotations` (*Name*), `harness/design_canvas` (*DesignCanvas* and the artboard helpers the story canvas draws with), `cdd_guidance/practices/stories` (the story model the story canvas shows). Neither harness nor Stories imports this module.

**Constraint.**

Convert between formats through *Ux*'s `render` or a format class's `parse` and `render`; do not edit one format to match another by hand. A plain *Control* has no story steps; use *StoryDemoControl* for a control that runs them.

### `ux/story-demo`

*Story Demo* runs a mockup against its stories in the browser, so a person can watch a story play through the screens or drive the screens themselves. `StoryDemoPage.load(createStory, mode)` loads a story into the page in one of two modes: *Play*, where the explorer steps through the story's scenarios with `playNext`, and *Interactive*, where using a *StoryDemoControl* runs the story steps attached to it. The mockup's HTML marks which controls, lists, and inputs take part through `data-` attributes the generated mockup already writes.

*PlayDualRunner* collects a story's Given/When/Then steps and plays them one at a time in the browser, reporting a failed Then without stopping the page. `story-test-core` defines stories with `story`, `scenario`, and `collect` in a form that runs both in the browser and under Node's test runner (`story-test-node`), and `soft-assert` gives browser-safe Then assertions.

- **Purpose:** Show a mockup working through its stories, step by step or by hand, without a backend.
- **Terms other packages use:** StoryDemoPage, PlayDualRunner, StoryDemoControl, `story-test-core`, `story-test-node`, `soft-assert`
- **Uses:** `cdd_guidance/practices/ux/model` (*StoryDemoControl*, which the HTML mockup is rendered from)

**Constraint.**

A plain *Control* has no story steps; only a *StoryDemoControl* runs them. A mockup's HTML imports `story-test-core` only, never the Node backend, so it runs in the browser. Keep the domain objects a story exposes across story switches in the page's session, and reset clears them.
