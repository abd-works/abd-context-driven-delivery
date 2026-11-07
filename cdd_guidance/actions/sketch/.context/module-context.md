# cdd_guidance/actions/sketch
*Sketch* is a rough draft of the formal artifacts, kept in one file for the session — `{session root}/.context/{session name}-sketch.md`, with one section per practice — so the shape of the solution is agreed before anything formal is generated. `sketch.sketch(guidance)` (slash `/sketch`) writes a high-level shell, asks three or four questions per theme, sketches the answers into the same file, and pauses for review.

The MCP tools `sketch.find_template`, `sketch.save_sketch`, `sketch.list_sketches`, and `sketch.review_sketch` find the practice's sketch template, save the sketch file, list sketch files, and stop for the person to confirm the sketch before the next question.

*SketchOutline* reads one practice's section of a sketch as indented lines, and *SketchLens* names that practice (`SketchLens.of("stories")`), so a practice's sketch format can read its own section without parsing headings itself.

- **Purpose:** Agree the rough shape of a solution in a saved file, reviewed after each theme, before formal generation.
- **Seam (terms):** Sketch, SketchOutline, SketchLens, `sketch.sketch`, `sketch.find_template`, `sketch.save_sketch`, `sketch.list_sketches`, `sketch.review_sketch`
- **Dependencies (one-way):** `cdd_guidance/actions/grill_context` (*GrillContext*), `cdd_guidance/actions` (*PathsFromProject*), `harness/guidance_actions` (*GuidanceAction*, *GuidanceArg*), `harness/guidance` (*PracticeGuidance*, `load_document`), `harness/agent_tools`, `harness/installation`, `harness/mcp`

## Constraint

Save the sketch in the same turn it is written and call `review_sketch` after every save; a sketch left only in chat is lost. Ask the next theme only after the person confirms the sketch, and carry every mistake they named into the next version. Pass the sketch to `save_sketch` by path, not as a body on the MCP call.
