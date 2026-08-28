---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Validate with Human

**Story type:** user

**Actor:** Practitioner

**Sources / context:** `utilities/swarm/.context/plan-and-swarm-sketch.md`; `utilities/plan/.context/module-context.md`

### Domain terms

- *HILCheck* — presents **Turn** results to the human for validation
- *Turn* — stays In Progress after human validation

## Behaviors

### Scenario: HIL Check presents results to the human

*Given* a **Turn** *In Progress* with a **HILCheck**  
  *And* that **Turn** holds **result**  
*When* the human validates that **Turn**  
*Then* that **HILCheck** holds the human validation  
  *And* that **Turn** still holds **result**  
  *And* that **Turn** **TicketState** is *In Progress*

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| HIL Check presents results to the human | plan-and-swarm-sketch.md | Execute Plan / Validate with Human |
