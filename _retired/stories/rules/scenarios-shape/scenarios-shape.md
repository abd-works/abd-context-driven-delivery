---
rule: scenarios-shape
kind: shape
fidelity: [specification, engineering]
artifact: scenarios/*.md
scanner: scenarios-shape-scanner.py
---

# scenarios-shape

Each `scenarios/*.md` file MUST have the fundamental Gherkin skeleton:
a `# Feature:` heading (or feature-titled `#`), at least one `## Scenario:`,
and each scenario MUST contain Given/When/Then steps.

## The rule

1. Exactly one top-level heading; MAY start with `Feature:` prefix.
2. At least one `## Scenario:` heading.
3. Every Scenario section MUST have at least one `- Given`, one `- When`, one
   `- Then` step (case-insensitive step keywords accepted).

## DO

- Structure each scenario as bulleted Given/When/Then steps.
- Use `## Scenario Outline:` for parameterised scenarios (still shape-valid).

## DON'T

- Do not skip step keywords — bare bullets mean nothing.
- Do not have scenarios missing any of Given, When, Then.

## Cross-references

- `scenario-step-quality` — enforces step *quality* (assertable Then, correct
  And/But usage). This rule only verifies presence.
- `scenario-outline-structure` — outlines get additional constraints there.
