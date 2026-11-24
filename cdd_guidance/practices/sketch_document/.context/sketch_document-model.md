# cdd_guidance/practices/sketch_document

*SketchOutline* is the saved sketch read as a document: a header, then one section per practice, each opened by a heading that practice's *SketchLens* opens. *DiscoveryDocument* is the document a practice writes at discovery fidelity from a sketch. It sits below both the practices and the actions, so a practice reads a sketch without importing the Sketch action.

- **Purpose:** Give every practice one reader of the saved sketch, below both the practices and the actions, so a practice reads a sketch without importing the Sketch action.
- **Seam (terms):** SketchOutline, DiscoveryDocument
- **Dependencies (one-way):** harness/guidance

## SketchOutline

A sketch whose hierarchy is carried by markdown headings above fenced detail.

+ SketchOutline(text: str, nesting_indent: int = 2)
------
+ title: str
+ sources: str
----
+ holds(lens: SketchLens): bool
+ body_for(lens: SketchLens): str
	// any practice's lens heading ends the section before it, so every practice is asked for its lens
---<<lists every lens with>>--> PracticeCatalogue
---<<calls opens on>>--> SketchLens

## DiscoveryDocument

A discovery document written from a sketch: its artifact, its heading, and the sketch's title and sources.

+ DiscoveryDocument(artifact: str, heading: str, sketch: str)
------
+ artifact: str
+ heading: str
+ title: str
+ sources: str
----
+ lines(body: str): list[str]
---<<reads title and sources of>>--> SketchOutline
