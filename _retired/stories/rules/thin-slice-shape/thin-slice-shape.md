---
rule: thin-slice-shape
kind: shape
fidelity: [discovery, exploration, specification, engineering]
artifact: thin-slice.md
scanner: thin-slice-shape-scanner.py
---

# thin-slice-shape

A `thin-slice.md` MUST have at least one Increment section, and every Increment
MUST list at least one story. Without these, downstream scenarios/tests cannot
be sequenced against a delivery plan.

## The rule

1. At least one `## Increment` heading (level-2).
2. Every Increment section MUST contain a `**Stories:**` or `## Stories` block.
3. Every Increment MUST have at least one bullet in its Stories block.

## DO

- Use `## Increment 1: <marketable outcome>` style headings.
- Under each, include a Stories list (bulleted).

## DON'T

- Do not have empty increments (heading with no stories).
- Do not skip the Stories block — the whole point of an increment is to
  enumerate what it delivers.

## Cross-references

- `thin-slice-increment-shape` — enforces the *quality* of the increment header
  and deferred/decision blocks; this shape rule only requires the skeleton.
- `thin-slice-ordering` — enforces that stories exactly match the story map.
