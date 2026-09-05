# Grill me — abd-story-specification

**Mechanics:** [`common/reference/grill-me-with-practice-skill.md`](../../../../common/reference/grill-me-with-practice-skill.md) — one question at a time; generate-to-learn when enough is shared.

Ask until examples are concrete enough to disagree on:

- If a domain expert and a developer read these examples, would they argue about correctness — or are they too vague to catch misunderstandings?
- Where do example values come from — real domain data or placeholders like "John Doe, $100"?
- Which Given state combinations have we not explored?
- What must be true before each scenario starts — does everyone agree on that setup?
- What happens at the edges — zero, one, many, max, just-over-max?
- For stubbed external services: is the stub in Given, invocation/response in When, business outcome only in Then?
