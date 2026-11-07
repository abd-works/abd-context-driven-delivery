# harness/name
*Name* is one name, such as a class, an event, or a fidelity, that CDD writes in several cases: `StoryMap`, `story_map`, and `story-map` are the same name, and so are a title's words (`Pet visits`, `pet-visits`, `PetVisits`). Every case conversion in CDD reads it, so a class name, a toolset slug, a published tool name, and a file named after a title always agree.

- **Purpose:** Write one name in every case CDD publishes or saves it under, the same way everywhere.
- **Seam (terms):** Name (`words`, `snake`, `kebab`, `camel`, `spellings`, `title_slug`, `title_snake`, `title_pascal`, `title_camel`)
- **Dependencies (one-way):** none. It is the lowest module of the framework, so harness/markdown, harness/annotations, and everything above them may use it.

## Constraint

Convert a name between cases only through *Name*; a second conversion elsewhere splits words differently (`MCPServer`, `pre-tool-use`) and the published name stops matching the class.
