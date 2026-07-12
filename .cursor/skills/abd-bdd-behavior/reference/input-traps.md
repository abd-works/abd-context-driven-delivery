# Input traps — abd-bdd-behavior

Pre-flight only — not grill questions. Check each trap before generating.

- **Missing sub-epic anchor** — Which sub-epics from the story map are in scope? Without a named sub-epic, top-level describe blocks float free of delivery structure.
- **Domain vocabulary gap** — Are concept names from domain language and domain model, or invented here? Names invented in the behavior file will mismatch production code and downstream tests.
- **Observable vs. implementation** — Do leaf `should` lines describe what the system does from a user's view, or what implementation method gets called?
- **Bundle risk** — Does a single `should` line describe multiple distinct behaviors? Each leaf must imply one verifiable outcome.
