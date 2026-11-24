# cdd_guidance/practices/ux

*Ux* is the practice: information architecture, mockups, and front-end code. *UxReading* is its part in the knowledge graph: it names the node types a UX map is made of and checks its screen rules on them. The whole model of this module, internals included, is `cdd_guidance/practices/ux/model/.context/ux-model.md`; that document is canonical, and this section shows only the classes other modules use.

- **Purpose:** Keep screens, navigation, and interactions in one hierarchy that the diagram, the mockup, and the front-end code all follow.
- **Seam (terms):** Ux, UxReading, NoJavascriptPractice, UxOutsideSession
- **Dependencies (one-way):** harness/annotations, harness/agent_tools, harness/guidance, harness/graph, harness/installation, harness/design_canvas, cdd_guidance/practices/stories

## Ux : PracticeGuidance

The UX practice: information architecture, mockup, and front-end code.

+ Ux(fidelity: str = 'ia', format: str | None = None)
------
+ reading_type: type
	// UxReading
----
+ ensure_javascript(practice: str, source_format: str, content: Any): dict
+ javascript_practice(key: str): PracticeGuidance
	// the session's own Stories or Clean Engineering, at the fidelity and format it works at there
---<<raises>>--> UxOutsideSession
---<<raises>>--> NoJavascriptPractice
---<<reads the graph with>>--> UxReading
---<<registers with>>--> UxNode

## UxReading : PracticeReading

The UX practice's node types and its screen rules; a working-copy load reads no UX files yet.

------
+ node_types: tuple[str, ...]
----

## NoJavascriptPractice : ValueError

ensure_javascript was asked for JavaScript from a practice that does not write the JavaScript a mockup imports.

------
----

## UxOutsideSession : ValueError

ensure_javascript was asked of a Ux that works in no session, so it has no Stories or Clean Engineering of its own to render the JavaScript through.

------
----
