---
status: Accepted
date: YYYY-MM-DD
stage: outline
---

# ADR-{NNN}: {short title — the decision in five words or fewer}

> **Status:** Proposed / Accepted / Superseded by ADR-NNN / Deprecated
> **Date:** YYYY-MM-DD
> **Stage:** outline / blueprint / specification
> **Deciders:** {names or roles}
> **Consulted:** {names or roles}
> **Informed:** {names or roles}

## Context

{One to three paragraphs. What problem is this decision solving? What forces are at play (business, technical, regulatory, organisational)? What constraints existed when the decision was made? Write so a future reader who was not in the room understands why this was urgent.}

## Decision

{One paragraph stating the chosen option in plain language. Start with "We will…". Be specific enough that a reviewer can tell whether a code change conforms or violates the decision.}

## Options considered

| Option | Pros | Cons | Why rejected (or chosen) |
|---|---|---|---|
| **{Option A — chosen}** | … | … | **Chosen because** … |
| Option B | … | … | Rejected because … |
| Option C | … | … | Rejected because … |

## Consequences

**Positive:**
- {What becomes easier? What problem this decision solves?}
- {What capabilities does the team gain?}

**Negative / trade-offs:**
- {What becomes harder? What flexibility is given up?}
- {What is the lock-in cost?}

**Neutral:**
- {Changes in workflow, naming, or organisation that are not better or worse, just different.}

## Compliance / verification

{How will the team know this decision is being followed? Examples: a lint rule, a code-review checklist item, an architectural fitness function, an automated test. If there is no way to verify, name that explicitly — the decision then relies on culture, which is honest to call out.}

## Notes

{Anything else worth recording: links to discussions, diagrams, prototypes, vendor evaluations.}

---

## Example (filled — for tone)

---
status: Accepted
date: 2026-04-12
stage: outline
---

# ADR-002: Layered architecture with one-way dependencies

> **Status:** Accepted
> **Date:** 2026-04-12
> **Stage:** outline
> **Deciders:** Architect, Tech Lead, Senior Engineer
> **Consulted:** Engineering team
> **Informed:** Product, Operations

## Context

The product is a SaaS platform with a 3-year planning horizon. Two teams (Platform and Growth) work in the same monorepo. In the previous codebase, domain logic and ORM calls intermingled; every change risked breaking unrelated features and the test suite required a live Postgres instance, which slowed CI to 18 minutes. We need a structure that lets two teams modify domain logic without coordinating on infrastructure, and that lets tests run without external services.

## Decision

We will adopt a layered architecture with the dependency rule **Presentation → Application → Domain → Infrastructure interfaces**, and concrete infrastructure classes referenced only inside the Infrastructure layer. The Domain layer is a pure TypeScript package with no `mongoose`, `pg`, or framework imports.

## Options considered

| Option | Pros | Cons | Why rejected (or chosen) |
|---|---|---|---|
| **Layered with strict dependency rule (chosen)** | Tests run without infrastructure; teams move independently. | Requires more interface plumbing; junior engineers need orientation. | **Chosen** for the test-speed and team-independence wins. |
| Hexagonal/ports-and-adapters | Same benefits as layered, more rigorous. | Higher conceptual overhead for a team unfamiliar with the pattern. | Rejected — same benefits, higher onboarding cost. |
| Status quo (no enforced layering) | Zero migration cost. | Test suite stays slow; cross-team contention persists. | Rejected — fails to address either driver. |

## Consequences

**Positive:**
- Domain test suite runs in under 30s without any external service.
- Teams can change their slice of the domain without conflicts in infrastructure code.

**Negative / trade-offs:**
- Every cross-layer call adds an interface; small features have more files than before.
- Onboarding includes a 1-hour session on the dependency rule.

**Neutral:**
- Folder structure changes from feature-oriented to layer-oriented under each module.

## Compliance / verification

- Lint rule: `eslint-plugin-boundaries` blocks `Domain → Infrastructure/*` imports at build time.
- Architectural fitness test: `npm run arch-check` walks the dependency graph; fails CI on violation.
- Code-review checklist item: "Domain file does not import a concrete database/HTTP class."

## Notes

- Discussion thread: #architecture-2026-Q2.
- Prototype branch demonstrating the structure: `proto/clean-layering`.
