# Stories Perspective

**Key:** `stories`

**What it answers:** What are the features, actors, systems, and interactions that make up the solution?

**Agent:** [Product Owner](../../../practices/kanban/agents/product-owner/AGENT.md)

**Skills by fidelity:**

| Fidelity | Skill | Mode |
|---|---|---|
| Shaping | `abd-story-mapping` | outline |
| Discovery | `abd-story-mapping` | full |
| Discovery | `abd-thin-slicing` | slice-ordering |
| Exploration | `abd-story-acceptance-criteria` | acceptance-criteria |
| Specification | `abd-story-specification` | spec-by-example |
| Engineering | `abd-story-acceptance-test` | acceptance-tests |

**Supporting:** `story-graph-ops`, `drawio-story-sync`, `miro-story-sync`.

---

## Shared reference (practice level)

| File | Role |
| --- | --- |
| [`handling-incomplete-context.md`](./handling-incomplete-context.md) | Gap discipline — do not fabricate to fill holes |
| [`new-vs-existing-system.md`](./new-vs-existing-system.md) | Spec-first vs reverse-engineering mode |
| [`diagram-workflow.md`](./diagram-workflow.md) | Shared Draw.io render/sync from `story-graph.json` |
| [`domain-input-priority.md`](./domain-input-priority.md) | Domain artifact read order for AC, spec, tests |
| [`validate-checklist.md`](./validate-checklist.md) | Cross-skill validate items |

---

## Per skill (skill level)

| File | Role |
| --- | --- |
| `reference/input-traps.md` | Pre-flight ambiguity checks — every run, not grill |
| `reference/grill-me.md` | Grill interview questions — grill mode only |
| `reference/generate.md` | Orchestration only — mapping, thin-slicing, spec, acceptance-test |
| `reference/diagram-workflow.md` | Mode + output path — mapping, AC, thin-slicing only |
| `reference/output.md` | Non-default output path — acceptance-test only |

**SKILL.md index sections:** Bootstrap, Read, Input traps, Grill me, Generate, Validate — plus Diagram workflow / Output when those `reference/` files exist. Bootstrap includes decision records via [`common/reference/decision-record.md`](../../../common/reference/decision-record.md) in [`common/reference/skill-workflow.md`](../../../common/reference/skill-workflow.md) § Bootstrap. Validate links [`common/reference/rule-checklist.md`](../../../common/reference/rule-checklist.md) (practice items in [`validate-checklist.md`](./validate-checklist.md)).
