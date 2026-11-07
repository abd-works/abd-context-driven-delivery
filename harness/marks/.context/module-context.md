# harness/marks
*Mark* is a decorator that marks the operation or class it decorates by setting its flag on it, so install and discovery find what it marks; each kind of mark is a subclass, and together the subclasses are the one list of marks. *OmissionMark* leaves what it marks out of something: `@noCatalog` out of the catalog, `@noDeploy` out of install.
*Destination* is a mark that names where a member is published, its **channel**: a skill, a command, a rules file, an MCP tool, or a hook. Each publisher defines its own kind (`Skill`, `Command`, `Rules` in harness/installation, `Mcp` in harness/mcp, `Hook` in harness/hooks), and the kind registers here by its channel as it is defined. harness/agent_tools asks `Destination.publishes(channel, operation)` to list a tool's destinations without importing a single publisher. *NamedDestination* is a destination whose mark may name what it installs (`@skill("name")`).

- **Purpose:** Hold the marks an author types, and the one place a member's destinations are read, below every module that defines or reads a mark, so the publishers depend on the toolsets and never the other way round.
- **Seam (terms):** Mark, OmissionMark, Destination, NamedDestination, Toast (`@Toast`, which asks the notifier to toast an operation when an agent calls it); `Destination.publishes(channel, operation)`, `Destination.marked_for(channel, operation)`, `Destination.name_given_for(channel, operation)`, `Destination.enlisting(member)`, `Mark.copied_flags()`
- **Dependencies (one-way):** none.

## Constraint

Define a new channel as a *Destination* subclass in the module that publishes it, with its `flag` and `channel`, so the channel joins the list by being imported. Set `enlists_member` only on a destination whose member the IDE calls directly, as a hook is, because such a member becomes a tool of its toolset without `@agent_tool`. A channel whose publisher was never imported marks nothing, which holds by construction: nothing can carry a mark that was never defined.
