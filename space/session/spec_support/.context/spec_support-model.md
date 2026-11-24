# space/session/spec_support

What a spec works in; only specs import it.

- **Purpose:** Give every spec that runs actions a project and a cdd home of its own.
- **Seam (terms):** ThrowawayProject, ExampleHome, OPEN_PROJECTS
- **Dependencies (one-way):** harness/mcp

## ThrowawayProject

An empty project named by `CDD_PROJECT` while a spec runs, so the actions a spec runs write to their own session log instead of the log of whoever is working in the repository.

+ ThrowawayProject(name: str = '')
------
+ root: Path
+ folder: Path
----
+ close_all(): None
+ close(): None
