# cdd_guidance/practices/stories
*Stories* maps user interactions to system behaviours, then defines each behaviour through executable specifications. Its fidelities deepen one hierarchy: the *story map* (epics, sub-epics, and stories; `stories-story-map`), *scenarios* with concrete examples for each story (`stories-scenarios`), and *acceptance tests* that run those scenarios against production code (`stories-acceptance-tests`). `stories.instructions` is the practice's guidance at its current fidelity.

The same story model is written in many formats — sketch, markdown, JSON, draw.io, Miro, Claude Design, Python, TypeScript, Java, and JavaScript — and `render(format, content)` turns a story map or its tests from one format into another without losing the hierarchy.

- **Purpose:** Keep one Epic → Story → Scenario hierarchy that discovery, specification, and tests all read, so scope and behaviour stay traceable from the map to the code.
- **Seam (terms):** Stories, `stories.instructions`, `stories-story-map`, `stories-scenarios`, `stories-acceptance-tests`, `render`
- **Dependencies (one-way):** `harness/guidance` (*PracticeGuidance*), `harness/graph`, `harness/agent_tools`, `harness/markdown`, `harness/name`, `cdd_guidance/actions/sketch` (*SketchOutline*), `cdd_guidance/practices/clean_engineering` (its class model, for code formats). `cdd_guidance/practices/ux` depends on Stories: its screens show the stories, and it draws the Claude Design story canvas from the story model. Stories imports neither UX nor anything that imports it back.

## Constraint

Run lifecycle steps through the actions with this practice as guidance — `generate.generate(guidance=["stories-story-map"])` — not as methods on *Stories*. Write only stories the source describes or the user asks for. Convert between formats with `render`, never by rewriting a format by hand, so every format keeps the same hierarchy.
