# cdd_guidance/practices/sketch_document
*SketchOutline* is the saved sketch read as a document: a header, whose `# ` line gives its title and whose `source:` line gives its sources, then one section per practice. A section opens at a heading one practice's *SketchLens* opens (harness/guidance, `PracticeGuidance.sketch_lens`), and `SketchOutline(text).body_for(lens)` hands that practice its section, flattened to indentation, so a practice's sketch format never parses headings itself. The outline asks every practice CDD has for its lens, so any of their headings ends the section before it, and the header is every line above the first of them. A sketch that names no lens is all one section and has no header.

*DiscoveryDocument* is the document a practice writes at discovery fidelity from a sketch — front matter naming its artifact, a `# {heading} — {title}` line, the sketch's sources, then the practice's body. It reads the title and sources from the sketch's *SketchOutline*, so the header and the practice sections are found by one rule. Stories' story map and DDD's bounded context map both write theirs through it.

- **Purpose:** Give every practice one reader of the saved sketch, below both the practices and the actions, so a practice reads a sketch without importing the Sketch action.
- **Seam (terms):** SketchOutline, DiscoveryDocument
- **Dependencies (one-way):** `harness/guidance` (*PracticeCatalogue*, *SketchLens*)

## Constraint

The sketch's sections are found only here. A practice that needs its section, or the sketch's title or sources, asks *SketchOutline*; it does not read headings of its own.
