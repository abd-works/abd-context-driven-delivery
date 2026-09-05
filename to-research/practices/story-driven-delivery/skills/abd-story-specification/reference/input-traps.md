# Input traps — abd-story-specification

Assumptions, ambiguities, and missing context that commonly produce bad specification scenarios. Check each trap against available input before generating — flag gaps honestly; do not invent scenarios to fill them.

- **Concrete enough to disagree** — if you showed these examples to a domain expert and a developer, would they argue about whether the output is correct? If not, the examples might be too vague to catch real misunderstandings.
- **Values from where** — are the example values representative of real domain data, or generic placeholders? Realistic values surface edge cases that "John Doe, $100" never will.
- **Missing state combinations** — what combinations of Given conditions have we not explored? The dangerous bugs live in states nobody thought to combine.
- **Assumed preconditions** — what has to be true before each scenario starts — and does everyone agree on that starting state, or are there hidden setup assumptions?
- **Boundary behaviors** — what happens at the edges — zero, one, many, max, just-over-max? Have we specified what the system does at the limits, or just in the comfortable middle?
- **Stubbed services** — if the scenario involves an external service or system whose response is hardcoded in a stub, is the stub declared in Given, the invocation and response expressed in When, and only the business outcome in Then? Or has the service response leaked into Then as though it were a business result?
