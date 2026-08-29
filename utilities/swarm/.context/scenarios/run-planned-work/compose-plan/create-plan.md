---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Create Plan

**Story type:** user

**Actor:** Practitioner

**Sources / context:** `utilities/swarm/.context/story-map.md`; `utilities/plan/.context/module-context.md`; `utilities/workflow/.context/module-context.md`

### Domain terms

- *Plan* — front-end to git; based on a **Workflow**; associated with a **Workspace**
- *Workflow* — reusable or newly named; Plan loads prebaked **Turn**s from it
- *Workspace* — working folder; not the **Repo**

## Behaviors

### Scenario: Plan is on the Workspace based on a Workflow

*Given* a **Workspace** and a **Workflow** *compose-judged-plan*  
*When* the operator creates a **Plan** from that **Workflow**  
*Then* that **Plan** is associated with that **Workspace**  
  *And* that **Plan** is based on **Workflow** *compose-judged-plan*

### Scenario: Second Plan is its own Plan

*Given* a **Workspace** that already has a **Plan** *compose-judged-plan*  
*When* the operator creates a **Plan** *ticket-flow-plan* based on a **Workflow**  
*Then* that **Workspace** has both **Plan**s  
  *And* each **Plan** holds its own **Turn**s

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Plan is on the Workspace based on a Workflow | story-map.md | Compose Plan / Create Plan |
| Second Plan is its own Plan | plan-and-swarm-sketch.md | Compose Plan / Create Plan |
