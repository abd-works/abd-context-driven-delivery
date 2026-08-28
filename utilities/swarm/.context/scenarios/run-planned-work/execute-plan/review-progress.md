---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Review Progress

**Story type:** user

**Actor:** Practitioner

**Sources / context:** `utilities/swarm/.context/plan-and-swarm-sketch.md`; `utilities/plan/.context/module-context.md`

### Domain terms

- *Plan* — shows **Turn** **TicketState**, **result**, **HILCheck** validation, **JudgeResult**
- *Turn* — In Progress while progress is reviewed

## Behaviors

### Scenario: Progress and results are on the Plan

*Given* a **Turn** *In Progress* with **result**  
  *And* a **HILCheck** validation  
  *And* a **JudgeCheckpoint** **JudgeResult**  
*When* the operator reviews progress  
*Then* that **Plan** shows that **Turn** **TicketState**  
  *And* that **Plan** shows that **Turn** **result**  
  *And* that **Plan** shows the **HILCheck** validation  
  *And* that **Plan** shows the **JudgeResult**

### Scenario: Review after HIL only

*Given* a **Turn** *In Progress* with **result**  
  *And* a **HILCheck** validation  
*When* the operator reviews progress  
*Then* that **Plan** shows that **Turn** **result**  
  *And* that **Plan** shows the **HILCheck** validation

### Scenario: Review after Judge only

*Given* a **Turn** *In Progress* with **result**  
  *And* a **JudgeCheckpoint** **JudgeResult**  
*When* the operator reviews progress  
*Then* that **Plan** shows that **Turn** **result**  
  *And* that **Plan** shows the **JudgeResult**

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Progress and results are on the Plan | plan-and-swarm-sketch.md | Execute Plan / Review Progress |
| Review after HIL only | plan-and-swarm-sketch.md | Execute Plan / Review Progress |
| Review after Judge only | plan-and-swarm-sketch.md | Execute Plan / Review Progress |
