# harness/annotations
*Annotation* is what an author types on an operation or class to say how CDD treats it — install it, keep it out of the catalog, toast it — so install and discovery find the member by its annotations rather than by a list kept somewhere else; each kind of annotation is a subclass. *OmissionAnnotation* leaves what it annotates out of something: `@noCatalog` out of the catalog, `@noDeploy` out of install.
*Destination* is an annotation that says where a member is published, its **channel**: a skill, a command, a rules file, an MCP tool, or a hook. Each publisher defines its own kind (`Skill`, `Command`, `Rules` in harness/installation, `Mcp` in harness/mcp, `Hook` in harness/hooks). *NamedDestination* is a destination whose annotation may name what it installs (`@skill("name")`). *Toast* (`@Toast`) asks the notifier to toast an operation when an agent calls it.
`annotation_kinds` is the one list of the kinds of annotation, which each kind joins as it is defined: harness/agent_tools asks it whether a channel publishes an operation (`publishes(channel, operation)`, `annotated_for`, `name_given_for`, `enlisting(member)`) and which annotations a wrapper copies (`copied_flags()`, `copy_annotations`), without importing a single publisher.

- **Purpose:** Hold the annotations an author types, and the one place a member's destinations are read, below every module that defines or reads an annotation, so the publishers depend on the toolsets and never the other way round.
- **Seam (terms):** Annotation, OmissionAnnotation, Destination, NamedDestination, Toast, `annotation_kinds`. Every class here is a base a publisher subclasses or an annotation an author types, so the module is all seam by design; the registry's own class stays private behind `annotation_kinds`.
- **Dependencies (one-way):** none.

## Constraint

Define a new channel as a *Destination* subclass in the module that publishes it, with its `flag` and `channel`, so the channel joins `annotation_kinds` by being imported. Set `enlists_member` only on a destination whose member the IDE calls directly, as a hook is, because such a member becomes a tool of its toolset without `@agent_tool`. A channel whose publisher was never imported annotates nothing, which holds by construction: nothing can carry an annotation that was never defined.
