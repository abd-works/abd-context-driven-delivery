---
extends: capability
overrides: [add-a-principle, add-example, analyze]
---

Manage the guiding principles that shape how this project is built.

## Add a principle

Add a new principle to this folder. Each principle is a single `.md` file named after the principle (kebab-case).

```
python principles/__main__.py add-principle <name> "<one-line description>"
```

The file is created with a frontmatter stub and the description as the opening line. Fill in the body with DO / DON'T guidance.

## Add example

Add a concrete context example to an existing principle.

```
python principles/__main__.py add-example <principle-name> "<example text>"
```

The example is appended to the principle file under an `## Examples` section.

## Analyze

Examine a piece of context (a file, folder, or description) and identify which principles it demonstrates or violates. Assign examples to one or more principles.

Given the context, read every principle file in full, then for each principle determine:
- Does the context demonstrate this principle? If so, add it as a passing example.
- Does the context violate this principle? If so, add it as a failing example and explain why.

Emit a summary table:

| Principle | Status | Note |
|---|---|---|
| {principle-name} | demonstrates / violates / not applicable | {brief reason} |
