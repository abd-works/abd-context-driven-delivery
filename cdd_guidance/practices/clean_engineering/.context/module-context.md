# cdd_guidance/practices/clean_engineering
*CleanEngineering* structures a solution into independent modules with small public interfaces and one-way dependencies, then types the objects, then implements them with clean object-oriented code, keeping the same names in every step. Its fidelities are *modules* — each module's public seam and dependencies (`clean-engineering-modules`); *model* — typed classes, operations, and relationships (`clean-engineering-model`); and *code* — working production code behind those seams (`clean-engineering-code`). `clean-engineering.instructions` is the practice's guidance at its current fidelity. Other practices use Clean Engineering as the companion for their class and code work.

The class model is written as a sketch, markdown, JSON, draw.io, Python, TypeScript, Java, or JavaScript, and `render(format, content)` converts between them at the same fidelity; when the format is draw.io, the `generate_output` instructions hand diagram creation to *Drawio*.

- **Purpose:** Keep boundaries, types, and code consistent, so a change stays inside one module instead of spreading to every caller.
- **Seam (terms):** CleanEngineering, `clean-engineering.instructions`, `clean-engineering-modules`, `clean-engineering-model`, `clean-engineering-code`, `render`, `generate_output`
- **Dependencies (one-way):** `cdd_guidance/practices/clean_engineering/model` (the class model and its formats), `cdd_guidance/practices/clean_engineering/model/drawio` (*DrawIOCleanEngineeringModel*), `harness/guidance` (*PracticeGuidance*), `harness/graph` (graph rules), `harness/agent_tools`, `harness/markdown`. `harness/guidance` imports *CleanEngineering* back (guidance.py), and `harness/graph` imports the class model back — cycles tracked in `.sessions/_backlog/break-module-dependency-cycles.md`.

## Constraint

Each `module-context.md` card opens with its language under `# {path}`, then Purpose, Seam (terms), Dependencies, and Constraint; typed class listings wait for the model fidelity. When a `module-context.md` is corrected, name the mistake as a rule in the modules fidelity in the same turn. Run lifecycle steps through the actions with this practice as guidance, not as methods on *CleanEngineering*.
