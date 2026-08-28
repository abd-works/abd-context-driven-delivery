---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Start Plan

**Story type:** user

**Actor:** Practitioner

**Sources / context:** `utilities/swarm/.context/plan-and-swarm-sketch.md`; `utilities/plan/.context/module-context.md`; `utilities/workspace/.context/module-context.md`

### Domain terms

- *Plan.start* — opens a **WorkSession**; first Backlog **Turn** becomes In Progress
- *TicketState* — Backlog | In Progress | Done on **Turn**

## Behaviors

### Scenario: Start opens a WorkSession and moves the first Backlog Turn to In Progress

*Given* a **Plan** *compose-judged-plan* associated with a **Workspace**  
  *And* that **Plan** has a **Turn** *Stories generate story_map*  
  *And* that **Turn** **TicketState** is *Backlog*  
*When* the operator starts that **Plan**  
*Then* **Workspace.openWorkSession** has a **WorkSession** for that **Plan**  
  *And* that **WorkSession** openTurn is that **Turn**  
  *And* that **Turn** **TicketState** is *In Progress*

### Scenario: Later Backlog Turn stays Backlog

*Given* that **Plan** also has a later **Turn** *CleanEngineering generate modules*  
*When* the operator starts that **Plan**  
*Then* the *Stories* **Turn** **TicketState** is *In Progress*  
  *And* the *CleanEngineering* **Turn** **TicketState** is *Backlog*

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Start opens a WorkSession and moves the first Backlog Turn to In Progress | plan-and-swarm-sketch.md | Execute Plan / Start Plan |
| Later Backlog Turn stays Backlog | plan-and-swarm-sketch.md | Execute Plan / Start Plan |
