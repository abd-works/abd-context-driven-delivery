---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Create Plan

**Story type:** user

**Actor:** Practitioner

**Sources / context:** `utilities/swarm/.context/story-map.md`; `utilities/swarm/.context/grill-answers.md` ticks 14–16; `utilities/plan/.context/module-context.md`; `utilities/workflow/.context/module-context.md`

### Domain terms

- *Plan* — a **Workflow** plus the ticket set (serial or parallel per Plan); no planned-turn list
- *Workflow* — states on its own GitHub **Project**
- *Workspace* — working folder; not the **Repo**

## Behaviors

### Scenario: Plan is Workflow plus tickets on the Workspace

*Given* a **Workspace** and saved **Workflow** *small-work*  
*When* the operator creates a **Plan** from that **Workflow** with tickets *#14* and *#15*  
*Then* that **Plan** is associated with that **Workspace**  
  *And* that **Plan** is based on **Workflow** *small-work*  
  *And* that **Plan** names tickets *#14* and *#15*  
  *And* that **Plan** holds no planned ticket×state turn list

### Scenario: Second Plan is its own Plan

*Given* a **Workspace** that already has a **Plan** *small-work-theme*  
*When* the operator creates a **Plan** *hotfix-batch* based on a **Workflow** with its own tickets  
*Then* that **Workspace** has both **Plan**s  
  *And* each **Plan** names its own **Workflow** and tickets

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Plan is Workflow plus tickets on the Workspace | grill-answers.md | ticks 14–16 |
| Second Plan is its own Plan | story-map.md | Compose Plan / Create Plan |
