---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Advance Turn

**Story type:** user

**Actor:** Practitioner

**Sources / context:** `utilities/swarm/.context/plan-and-swarm-sketch.md`; `utilities/plan/.context/module-context.md`; `utilities/workspace/.context/module-context.md`

### Domain terms

- *Plan.advanceTurn* — **Turn.finish**; finished **Turn** is Done; next Backlog becomes In Progress
- *WorkSession.openTurn* — tracks the In Progress **Turn**

## Behaviors

### Scenario: Finished Turn is Done and the next Backlog Turn is In Progress

*Given* a **Plan** with *Stories* then *CleanEngineering* **Turn**s  
  *And* the *Stories* **Turn** **TicketState** is *In Progress*  
  *And* a **WorkSession** is open  
*When* the operator advances  
  *And* the *Stories* **Turn** finish runs  
*Then* the *Stories* **Turn** **TicketState** is *Done*  
  *And* the *CleanEngineering* **Turn** **TicketState** is *In Progress*  
  *And* that **WorkSession** openTurn is the *CleanEngineering* **Turn**

### Scenario: Last Turn advance leaves the Plan on Done

*Given* a **Plan** whose only *In Progress* **Turn** is the last **Turn**  
*When* the operator advances  
  *And* that **Turn** finish runs  
*Then* that **Turn** **TicketState** is *Done*  
  *And* that **WorkSession** openTurn is empty

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Finished Turn is Done and the next Backlog Turn is In Progress | plan-and-swarm-sketch.md | Execute Plan / Advance Turn |
| Last Turn advance leaves the Plan on Done | plan-and-swarm-sketch.md | Execute Plan / Advance Turn |
