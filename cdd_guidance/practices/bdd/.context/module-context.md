# cdd_guidance/practices/bdd
*Bdd* (behavior-driven development) specifies domain logic through nested describe/it tests that serve both as documentation and as automated tests. Its fidelities deepen one test hierarchy: *behavior* fixes the describe and `it should` names for every observation with no test bodies (`bdd-behavior`); *realization* traces each observation through the domain calls that make it true, as signatures with no bodies (`bdd-realization`); *development* fills the tests red, then green, with production code (`bdd-development`). `bdd.instructions` is the practice's guidance at its current fidelity.

The hierarchy is written as a sketch, markdown, Python, or TypeScript, and `render(format, content)` converts between them; a saved knowledge graph can be rendered to draw the realization. `expect_scan_fails` and `expect_scan_passes` check a failing example and its repaired example against one rule, for rule specs.

- **Purpose:** Turn domain vocabulary into passing tests, locking what is observed before how it is built.
- **Seam (terms):** Bdd, `bdd.instructions`, `bdd-behavior`, `bdd-realization`, `bdd-development`, `render`, `expect_scan_fails`, `expect_scan_passes`
- **Dependencies (one-way):** `harness/guidance` (*PracticeGuidance*), `harness/graph`, `harness/agent_tools`, `cdd_guidance/actions/sketch` (*SketchOutline*), `cdd_guidance/practices/clean_engineering` (class model, for the code a test drives), `cdd_guidance/practices/stories` (story model). `harness/graph` imports Bdd back — a cycle tracked in `.sessions/_backlog/break-module-dependency-cycles.md`.

## Constraint

Agree the describe/it hierarchy at behavior before writing any test body, and keep later fidelities to that hierarchy. Write production classes at Clean Engineering's matching fidelity rather than describing them in BDD artifacts. Run lifecycle steps through the actions with this practice as guidance, not as methods on *Bdd*.
