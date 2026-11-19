# validate with `graph: true` and no paths answers "No graph checked", though the same folder named in `paths` has three graph violations

- **Charter:** Round 1 - generate, validate, render and the fidelity output choices as an agent that spells names every way
- **Tester:** Widget
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers validate's graph argument.
- **Module and class:** `cdd_guidance/actions/validate/validate.py` `Validate._check` / `_graph_section`, `checked_graph.py` (`NamedToCheck`).
- **Severity:** wrong result (the graph rules the caller asked for are not run, and the call succeeds)

## Steps
Sandbox `repo`, session `main`; Clean Engineering writes to `src`, which holds `order.py` (class Order, an untyped parameter, no module-context.md). `drv\c12.json`:

    validate.validate {"guidance": "clean-engineering-code", "paths": ["src"]}     -> report: Total graph violations: 3
    validate.validate {"guidance": "clean-engineering-code", "graph": true}        -> report: No graph checked.
    validate.validate {"guidance": "clean-engineering-code"}                       -> report: No graph checked.

Reports: `repo\.sessions\main\validation-reports\clean-engineering-code-20261119T181726*.md`.

## Expected
The tool's own description: "graph: true for the session's graph (graph.json in the session's own folder, created for the session and loaded when it is missing) ... When set, append a graph-rule report for each guidance's practice", and "With no paths and no graph, the folders holding the fidelity's written output are checked". Both calls report the three violations `paths: ["src"]` finds.

## Actual
Both saved reports say "**No graph checked.** The judgment covers the checked files." and list no file. No graph.json is made in `.sessions\main`. The same answer came for `stories-story-map` with `graph: true` and no paths. A string that is no file (`"graph": "yes"`, or a project-relative `.sessions/main/graph.json`) fails with a raw `FileNotFoundError: [Errno 2] No such file or directory: 'yes'`, read from the server's folder rather than the project's root.

## Tier that should catch it
Heavy (`validate_heavy_spec.py`): its examples pass paths; none asks for the session's graph with `graph: true` alone on a project whose graph was never built.
