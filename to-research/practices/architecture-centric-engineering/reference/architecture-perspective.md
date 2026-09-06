# Architecture Perspective

**Key:** `architecture`

**What it answers:** What is the technology that will implement the solution? Platform, layers, components, cross-cutting concerns, and the principles that govern how code is built.

**Agent:** [Engineer](../../../practices/kanban/agents/engineer/AGENT.md)

**Skills by fidelity:**

| Fidelity | Skill | Mode |
|---|---|---|
| Shaping | `abd-architecture-outline` | system-context |
| Discovery | `abd-architecture-blueprint` | blueprint |
| Discovery | `abd-architecture-blueprint` | scaffold *(opt-in: seeds folder skeleton + stub `architecture-context.md` files; see [skill modes](../skills/abd-architecture-blueprint/SKILL.md#modes))* |
| Exploration | `abd-architecture-specification` | document |
| Specification | `abd-architecture-template` | project *(default: one runnable parameterized reference module per project at `docs/architecture/templates/<project-slug>/`)* |
| Specification | `abd-architecture-template` | mechanism *(opt-in: one runnable reference module per named mechanism at `docs/architecture/templates/<mechanism-slug>/`; see [skill modes](../skills/abd-architecture-template/SKILL.md#modes))* |
| Engineering | `abd-architecture-code` | production-code |

---

## Shared reference (practice level)

| File | Role |
| --- | --- |
| [`architecture-context-model.md`](./architecture-context-model.md) | Canonical model for the whole family — centralized documents (outline + blueprint + specification) and how they fan out to per-folder `architecture-context.md` files, three tiers, vocabulary chain, existing-vs-new flow, higher-level rules, skill-level handoff summary |
| [`architecture-mechanism.md`](./architecture-mechanism.md) | What an architecture mechanism is and how each skill in the family uses the concept |
| [`validate-checklist.md`](./validate-checklist.md) | Cross-skill validate items |
| [`diagram-workflow.md`](./diagram-workflow.md) | Shared `arch-drawio.ps1` init/export/verify |
| [`common/reference/record-all-architecture-violations.md`](../../../common/reference/record-all-architecture-violations.md) | Violation workflow for existing systems |

---

## Per skill (skill level)

| File | Role |
| --- | --- |
| `reference/input-traps.md` | Pre-flight ambiguity checks — every run, not grill |
| `reference/grill-me.md` | Grill interview questions — grill mode only |
| `reference/generate.md` | Orchestration — element inventory, mechanisms, violations |
| `reference/diagram-workflow.md` | Skill-specific diagram set and verify steps |
| `reference/concepts.md` | Teaching reference (existing on most skills) |

**SKILL.md index sections:** Bootstrap, Read, Input traps, Grill me, Generate, Validate — plus Diagram workflow when applicable. Validate links [`common/reference/rule-checklist.md`](../../../common/reference/rule-checklist.md) (practice items in [`validate-checklist.md`](./validate-checklist.md)).
