# cdd_guidance/practices/ux/model
*UxMap* is the information architecture as one hierarchy: *Screen*s divided into *Region*s that hold *Control*s, the *Interaction*s a control offers, the *Transition*s between screens, the *ContentType*s and *NavComponent*s screens share, and the *UxContext* notes that apply to the whole map. *StoryDemoControl* is a control that runs story steps when used in a mockup. A diagram, a JSON file, and an HTML mockup are all the same *UxMap*, so every later fidelity reads the same screens. How the map reads a file is written in [ux-model.md](ux-model.md).

Each format is one class of the same map, in this module: *DrawioUxMap* (the default IA diagram, through the drawio-ux command line), *HtmlUxMap* (the mockup review page, product screens beside the story explorer, carrying the JSON model inside it), *JsonUxMap* (the full map as JSON), *MarkdownUxMap* (UX context notes), and *ClaudeDesignUxMap*. Each `render`s a *UxMap* and `parse`s back what it rendered: JSON and HTML carry the whole map, draw.io carries screens, regions, and transitions, and markdown carries the scope and the context notes. HTML reads only a page it rendered, from the JSON it embeds; Claude Design screens are placed on the canvas and never read back. Every node sits on its map's graph, and a link from one screen to another (a transition, a tab's chrome, a destination) holds the *Screen* itself.

- **Purpose:** Keep one UX map that every UX format and fidelity reads, so converting a diagram to a mockup never changes the screens.
- **Seam (terms):** UxMap, Screen, Region, Control, StoryDemoControl, Interaction, Transition, ContentType, NavComponent, UxContext, DrawioUxMap, HtmlUxMap, JsonUxMap, MarkdownUxMap, ClaudeDesignUxMap
- **Dependencies (one-way):** `harness/graph` (the map's nodes are graph nodes), `harness/annotations` (*Name*), `harness/design_canvas` (*DesignCanvas* and the artboard helpers the story canvas draws with), `cdd_guidance/practices/stories` (the story model the story canvas shows). Neither harness nor Stories imports this module.

## Constraint

Convert between formats through *Ux*'s `render` or a format class's `parse` and `render`; do not edit one format to match another by hand. A plain *Control* has no story steps; use *StoryDemoControl* for a control that runs them.
