---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Fix and Rerun

**Story type:** user

**Actor:** Practitioner

**Sources / context:** `utilities/swarm/.context/plan-and-swarm-sketch.md`; `utilities/plan/.context/module-context.md`; `utilities/workspace/.context/module-context.md`

### Domain terms

- *Mistake* / *Correction* — recorded on **Turn** via **recordMistake** / **recordCorrection**
- *Repair* — held on **WorkSession.repairs**
- *Turn* — stays In Progress after Fix and Rerun

## Behaviors

### Scenario: Human asks to fix now

*Given* a **Turn** with a **HILCheck** validation that calls for a fix  
  *And* that **Turn** holds **result**  
  *And* that **Turn** **TicketState** is *In Progress*  
*When* the operator **recordMistake** on that **Turn**  
  *And* **recordCorrection** on that **Turn**  
  *And* **WorkSession.repairs** holds the **Repair**  
  *And* the operator executes that **Turn** again  
*Then* that **Turn** holds the **Mistake**  
  *And* that **Turn** holds the **Correction**  
  *And* that **Turn** holds a new **result**  
  *And* that **Turn** **TicketState** is *In Progress*

### Scenario: Judge evaluation can also drive Fix and Rerun

*Given* a **Turn** with a **JudgeResult** that calls for a fix  
*When* the operator **recordMistake** on that **Turn**  
  *And* **recordCorrection** on that **Turn**  
  *And* **WorkSession.repairs** holds the **Repair**  
  *And* the operator executes that **Turn** again  
*Then* that **Turn** holds the **Mistake** and the **Correction**  
  *And* that **Turn** holds a new **result**  
  *And* that **Turn** **TicketState** is *In Progress*

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Human asks to fix now | plan-and-swarm-sketch.md | Execute Plan / Fix and Rerun |
| Judge evaluation can also drive Fix and Rerun | plan-and-swarm-sketch.md | Execute Plan / Fix and Rerun |
