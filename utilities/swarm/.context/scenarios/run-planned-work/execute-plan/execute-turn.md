---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Execute Turn

**Story type:** user

**Actor:** Practitioner

**Sources / context:** `utilities/swarm/.context/plan-and-swarm-sketch.md`; `utilities/plan/.context/module-context.md`

### Domain terms

- *Plan.executeTurn* — runs the In Progress **Turn** via **Turn.performTurn**
- *Turn* — holds **action**, **fidelity**, **result**, **toolCalls**

## Behaviors

### Scenario: Execute runs the In Progress Turn

*Given* a **Plan** with a **WorkSession** already open  
  *And* the *Stories* **Turn** **TicketState** is *In Progress*  
*When* the operator executes that **Turn**  
*Then* that **WorkSession** openTurn is that **Turn**  
  *And* that **Turn** runs **performTurn**  
  *And* that **Turn** action is *generate*  
  *And* that **Turn** fidelity is *story_map*  
  *And* that **Turn** holds **result**  
  *And* that **Turn** holds **toolCalls**

### Scenario: Execute leaves TicketState In Progress

*Given* that **Turn** already holds **result**  
*When* the operator reviews that **Turn** **TicketState**  
*Then* that **Turn** **TicketState** is *In Progress*

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Execute runs the In Progress Turn | plan-and-swarm-sketch.md | Execute Plan / Execute Turn |
| Execute leaves TicketState In Progress | plan-and-swarm-sketch.md | Execute Plan / Execute Turn |
