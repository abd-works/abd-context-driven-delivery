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

*Given* a **Turn** *In Progress* with a **HILCheck** validation that calls for a fix and holds **result**  
*When* the operator **recordMistake** and **recordCorrection** on that **Turn** with **WorkSession.repairs** holding the **Repair**  
  *And* the operator executes that **Turn** again  
*Then* that **Turn** holds the **Mistake**, the **Correction**, and a new **result**  
  *And* that **Turn** **TicketState** is *In Progress*

### Scenario: Judge evaluation can also drive Fix and Rerun

*Given* a **Turn** with a **JudgeResult** that calls for a fix  
*When* the operator **recordMistake** and **recordCorrection** on that **Turn** with **WorkSession.repairs** holding the **Repair**  
  *And* the operator executes that **Turn** again  
*Then* that **Turn** holds the **Mistake**, the **Correction**, and a new **result**  
  *And* that **Turn** **TicketState** is *In Progress*

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Human asks to fix now | plan-and-swarm-sketch.md | Execute Plan / Fix and Rerun |
| Judge evaluation can also drive Fix and Rerun | plan-and-swarm-sketch.md | Execute Plan / Fix and Rerun |
