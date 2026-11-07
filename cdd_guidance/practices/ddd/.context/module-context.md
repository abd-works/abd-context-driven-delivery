# cdd_guidance/practices/ddd
*Ddd* (domain-driven design) organizes the solution around how the business works, in the words the business already uses. Its fidelities deepen one domain: the *bounded context* map draws where the language changes — business areas, departments, and systems — and the aggregates that protect rules inside each (`ddd-bounded-context`); the *model* draws each aggregate's root, the entities and values it owns, its repository, and its domain operations, with nothing technical (`ddd-model`); *tactics* classifies the remaining building blocks — factories, specifications, domain services, domain events, interfaces to other systems — picks one implementation pattern for each, and implements the domain (`ddd-tactics`). `ddd.instructions` is the practice's guidance at its current fidelity.

*BoundedContextMap* is the domain model every DDD format reads — sketch, markdown, and draw.io. The code formats, Python and TypeScript, write the same domain as Clean Engineering's class model, and `render(format, content)` converts between the bounded-context map and that class model.

- **Purpose:** Keep the software in the business's language, with each rule held in the aggregate that owns it, before any technical detail is added.
- **Seam (terms):** Ddd, BoundedContextMap, `ddd.instructions`, `ddd-bounded-context`, `ddd-model`, `ddd-tactics`, `render`
- **Dependencies (one-way):** `harness/guidance` (*PracticeGuidance*), `harness/graph`, `harness/agent_tools`, `harness/markdown`, `cdd_guidance/actions/sketch` (*SketchOutline*), `cdd_guidance/practices/clean_engineering/model` (class model, its markdown and draw.io formats). The class model imports DDD's stereotypes back and `harness/graph` imports DDD's model back — cycles tracked in `.sessions/_backlog/break-module-dependency-cycles.md`.

## Constraint

Do not restate Clean Engineering's class analysis in DDD artifacts; use the fidelity's Clean Engineering companion. Do not add detail from a deeper DDD fidelity than the active one. Run lifecycle steps through the actions with this practice as guidance, not as methods on *Ddd*.
