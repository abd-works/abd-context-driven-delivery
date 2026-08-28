---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Create Plan

**Story type:** user

**Actor:** Practitioner

**Sources / context:** `utilities/swarm/.context/plan-and-swarm-sketch.md`; `utilities/plan/.context/module-context.md`

### Domain terms

- *Plan* — associated with a **Workspace**; holds ordered **Turn**s
- *Workspace* — parent of `.context/`; owns **WorkSession**s

## Behaviors

### Scenario: Plan is on the Workspace

*Given* a **Workspace**  
*When* the operator creates a **Plan** *compose-judged-plan*  
*Then* that **Plan** is associated with that **Workspace**  
  *And* that **Plan** holds no **Turn**s yet

### Scenario: Second Plan is its own Plan

*Given* a **Workspace** that already has a **Plan** *compose-judged-plan*  
*When* the operator creates a **Plan** *ticket-flow-plan*  
*Then* that **Workspace** has both **Plan**s  
  *And* each **Plan** holds its own **Turn**s

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Plan is on the Workspace | plan-and-swarm-sketch.md | Compose Plan / Create Plan |
| Second Plan is its own Plan | plan-and-swarm-sketch.md | Compose Plan / Create Plan |
