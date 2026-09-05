# ADR-{NNN}: {short title — the decision in five words or fewer}

> **Status:** Proposed / Accepted / Superseded by ADR-NNN / Deprecated
> **Date:** YYYY-MM-DD
> **Deciders:** {names or roles}

This template is shared with `abd-architecture-outline`. See [the outline skill's `decision-record.md`](../../abd-architecture-outline/templates/decision-record.md) for the canonical filled example. The structure is identical — Context / Decision / Options considered / Consequences / Compliance / Notes — and the file name pattern is `ADR-NNN-{slug}.md` under `docs/architecture/decisions/`.

## Context

{One to three paragraphs. What problem is this decision solving at the **blueprint level**? What forces shaped it? What constraints existed?}

## Decision

{One paragraph stating the chosen option in plain language. Start with "We will…". Be specific enough that a reviewer can tell whether a code change conforms.}

## Options considered

| Option | Pros | Cons | Why rejected (or chosen) |
|---|---|---|---|
| **{Option A — chosen}** | … | … | **Chosen because** … |
| Option B | … | … | Rejected because … |
| Option C | … | … | Rejected because … |

## Consequences

**Positive:**
- …

**Negative / trade-offs:**
- …

**Neutral:**
- …

## Compliance / verification

{How does the team know this decision is being followed? Lint rule, fitness function, code-review checklist, scanner — or stated reliance on culture.}

## Notes

{Links to discussion, prototypes, vendor evaluations.}
