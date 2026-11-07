# cdd_guidance/practices/clean_engineering/model
*CleanEngineeringModel* is the object-oriented analysis and design (OOAD) model behind every Clean Engineering artifact: *Module*s holding *OoadClass*es, each with *Property*s, *Operation*s and their *Parameter*s, and *Relationship*s to other classes. One model is read from and written to every format — markdown, JSON, sketch, Python, TypeScript, Java, JavaScript, draw.io, and Miro — so a module map, a class diagram, and the code always say the same classes. `CleanEngineeringModelFactory.load(path)` takes a file or a folder, chooses the format from it, and returns the model; each format is one class, such as *MarkdownCleanEngineeringModel*, that loads and saves the same nodes. How the model reads a path is written in [ooad-model.md](ooad-model.md).

*CodeBody* is an operation's body as it was read. Rendered in the same language it comes back as written; rendered in another language it comes back commented out above a statement that fails until someone writes it, so moving a model between languages never silently drops code. Stories and BDD use *CodeBody* for their own code formats.

- **Purpose:** Keep one class model that every format and every practice reads, so converting between formats never changes the classes.
- **Seam (terms):** CleanEngineeringModelFactory, CleanEngineeringModel, Module, OoadClass, Property, Operation, Parameter, Relationship, CodeBody
- **Dependencies (one-way):** `harness/graph` (the model's nodes are graph nodes), `harness/agent_tools`, `cdd_guidance/actions/sketch` (*SketchOutline*, for the sketch format), `cdd_guidance/practices/clean_engineering` (the practice and its rules), `cdd_guidance/practices/clean_engineering/model/drawio` (draw.io format). The practice, the draw.io format, and `harness/graph` each import this module back — cycles tracked in `.sessions/_backlog/break-module-dependency-cycles.md`.

## Constraint

Callers work with the base nodes and load through `CleanEngineeringModelFactory.load`; they never pick a format's internals or parse text themselves. Pass the previous file when rendering code from a model that came from markdown or a diagram, so the operation bodies already written are kept.
