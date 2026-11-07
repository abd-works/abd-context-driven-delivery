# cdd_guidance/practices/clean_engineering/model/drawio
*Drawio* turns a Clean Engineering class model into a draw.io diagram — a modules view or a class view, chosen from what the model holds — and checks the diagram against the layout rules in `drawio.md`. `create_diagram(content, path)` writes the diagram; `render(content, path)` creates it, scans it, and, when definite layout failures remain, has the layout generator repaired by a sub-agent; `scan(paths)` reports layout rule violations on existing `.drawio` files. *CleanEngineering* is given a *Drawio* and uses it whenever its format is draw.io.

*DrawIOCleanEngineeringModel* is the draw.io format of the class model: it loads a diagram into the same modules and classes every other format reads, and saves them back. With `keep_positioning`, an updated diagram keeps the positions of the classes and the routes of the relationships already drawn, and lays out only what is new, so a person's arrangement survives regeneration. The diagram's own model is in [drawio-model.md](drawio-model.md).

- **Purpose:** Draw the class model as a readable draw.io diagram, and keep the diagram generator honest against its layout rules.
- **Seam (terms):** Drawio, DrawIOCleanEngineeringModel, `create_diagram`, `render`, `scan`, `keep_positioning`
- **Dependencies (one-way):** `cdd_guidance/practices/clean_engineering/model` (the class model and its shared diagram layout), `harness/agent_tools`, `harness/markdown`. The class model imports this module back to load draw.io files — a cycle tracked in `.sessions/_backlog/break-module-dependency-cycles.md`.

## Constraint

Callers ask *Drawio* to create or scan a path; they never write mxCell attributes, waypoints, or HTML themselves. A layout failure is fixed in the layout generator, not by editing one diagram. Rules in `drawio.md` with no scanner, such as `module-spatial-cohesion`, are judged by validate as written rules.
