---
rule: templates-use-parameterized-placeholders
kind: quality
fidelity: [engineering]
artifact: template/**/*.md
scanner: templates-use-parameterized-placeholders-scanner.py
---

# Rule: Templates Use Parameterized Placeholders

All template files must use `{placeholder}` syntax for every value that must be filled in when instantiating the template. Angle-bracket (`<>`), TODO, or blank placeholders are not allowed.

## DO

- Write `{capability}` wherever the capability name should appear
- Write `{one sentence description}` for the description slot
- Write `{Action 1}` for command names that the author must fill in

## DON'T

- Use `<capability>`, `<description>`, or `<TODO>` as placeholders
- Leave slots blank or write `TODO` as a filler
- Use square brackets `[placeholder]` for substitution slots
