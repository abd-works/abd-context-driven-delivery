# cdd_guidance/practices/ux
*Ux* (user experience) defines how users reach the domain, from journey and information architecture to screen navigation. Its fidelities deepen one UX map: *information architecture* decides which screens exist and how users move between them (`ux-ia`); *mockup* locks screens as runnable greybox with typed controls and key interactions (`ux-mockup`); *front-end code* ships the product UI talking to a real backend (`ux-front-end-code`). `ux.instructions` is the practice's guidance at its current fidelity.

The UX map is written as draw.io, HTML, markdown, JSON, or Claude Design, and `render(format, content)` converts between them. *ClaudeDesignStoryModel* (`model/claude_design/story_canvas.py`) draws the Claude Design canvas a stakeholder plays: the story map, the story explorer, and the screens each story is shown on, read from the story model and the UX map. `ensure_javascript(practice, source_format, content)` gets the Stories or Clean Engineering JavaScript a mockup needs, rendering it through this session's own copy of that practice when it is missing.

- **Purpose:** Keep screens, navigation, and interactions in one hierarchy that the diagram, the mockup, and the front-end code all follow, in the domain's words.
- **Seam (terms):** Ux, `ux.instructions`, `ux-ia`, `ux-mockup`, `ux-front-end-code`, `render`, `ensure_javascript`
- **Dependencies (one-way):** `cdd_guidance/practices/ux/model` (the UX map and its formats, loaded by format name), `cdd_guidance/practices/stories` (*Stories* and its story model), `harness/guidance` (*PracticeGuidance*, *PracticeCatalogue*), `harness/graph` (its screen rules; *Ux* names the node types the graph offers for it), `harness/agent_tools`. Stories imports nothing of UX.

## Constraint

Name screens and controls in the domain's words, not the layout's. Get another practice's JavaScript through `ensure_javascript`, never by writing it in a UX artifact. Run lifecycle steps through the actions with this practice as guidance, not as methods on *Ux*.
