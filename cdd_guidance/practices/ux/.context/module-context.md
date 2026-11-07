# cdd_guidance/practices/ux
*Ux* (user experience) defines how users reach the domain, from journey and information architecture to screen navigation. Its fidelities deepen one UX map: *information architecture* decides which screens exist and how users move between them (`ux-ia`); *mockup* locks screens as runnable greybox with typed controls and key interactions (`ux-mockup`); *front-end code* ships the product UI talking to a real backend (`ux-front-end-code`). `ux.instructions` is the practice's guidance at its current fidelity.

The UX map is written as draw.io, HTML, markdown, JSON, or Claude Design, and `render(format, content)` converts between them. `ensure_javascript(generator, source_format, content)` gets the Stories or Clean Engineering JavaScript a mockup needs, rendering it through that practice when it is missing; `emit_story_javascript` in `scripts/` does the same for a story file from the command line.

- **Purpose:** Keep screens, navigation, and interactions in one hierarchy that the diagram, the mockup, and the front-end code all follow, in the domain's words.
- **Seam (terms):** Ux, `ux.instructions`, `ux-ia`, `ux-mockup`, `ux-front-end-code`, `render`, `ensure_javascript`
- **Dependencies (one-way):** `cdd_guidance/practices/ux/model` (the UX map and its formats), `cdd_guidance/practices/stories` (*Stories* and its story model), `cdd_guidance/practices/clean_engineering` (*CleanEngineering*, for JavaScript), `harness/guidance` (*PracticeGuidance*), `harness/agent_tools`. `cdd_guidance/practices/stories` imports the UX model back — a cycle tracked in `.sessions/_backlog/break-module-dependency-cycles.md`.

## Constraint

Name screens and controls in the domain's words, not the layout's. Get another practice's JavaScript through `ensure_javascript`, never by writing it in a UX artifact. Run lifecycle steps through the actions with this practice as guidance, not as methods on *Ux*.
