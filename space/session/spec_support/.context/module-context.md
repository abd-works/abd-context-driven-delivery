# space/session/spec_support
What a spec works in. Spec files import it; production code never does.

*ThrowawayProject* is an empty project a spec works in, so the actions a spec runs write to their own session log instead of the log of whoever is working in the repository. *ExampleHome* is a cdd home of one example's own, so the open-sessions file every switch reads and prunes holds only what that example opened, not an entry for every throwaway project the run made. *OPEN_PROJECTS* holds the throwaway projects a run opened, so `OPEN_PROJECTS.close_all()` closes them from an `after.each`. `session_roots_examples.py` holds the sessions and practice roots the root-choosing specs share.

- **Purpose:** Give every spec that runs actions a project and a cdd home of its own, so nothing a spec writes lands in the repository being worked in or in the person's home.
- **Seam (terms):** ThrowawayProject, ExampleHome, OpenProjects, OPEN_PROJECTS (`close_all()`), the examples in `session_roots_examples.py`.
- **Dependencies (one-way):** `harness/mcp` (`CDD_HOME_ENV`), and in its examples space/session and space/session/practices. Nothing in production imports it.

## Constraint

Specs that run actions open a *ThrowawayProject* and close it after each example.
