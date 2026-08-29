---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Create Supervisor

**Story type:** user

**Actor:** Supervisor

**Sources / context:** `utilities/swarm/.context/plan-and-swarm-sketch.md`; `utilities/swarm/.context/grill-answers.md` ticks 3, 10, 14–16; `utilities/swarm/.context/module-context.md`

### Domain terms

- *Supervisor* — owns **Outcome** and **rubric**; on a **Plan**
- *Outcome* — overarching result owned by **Supervisor**
- *Swarm* — holds a shared **flow/ticket** slice selected once before any **Agent** runs (not a planned-turn list)
- *Plan* — **Workflow** + tickets; Agents run that same flow/ticket slice on their own **WorkSession**s

## Behaviors

### Scenario: Supervisor holds the Outcome

*Given* a **Plan** *compose-judged-plan* based on **Workflow** *small-work* with tickets *#14* and *#15*  
*When* the operator creates a **Supervisor** with **Outcome** *Plan-started*  
*Then* that **Supervisor** owns **Outcome** *Plan-started*  
  *And* that **Supervisor** is on that **Plan**  
  *And* that **Supervisor** holds no **Agent**s yet

### Scenario: Supervisor rubric hangs on the Supervisor

*Given* a **Supervisor** with **Outcome** *Plan-started*  
*When* the operator sets that **Supervisor** rubric to *plan-started*  
*Then* that **Supervisor** rubric is *plan-started*  
  *And* that **Supervisor** still owns **Outcome** *Plan-started*

### Scenario: Shared flow/ticket slice is selected once

*Given* a **Plan** on **Workflow** *small-work* with tickets *#14* and *#15*  
  *And* a **Supervisor** with **Outcome** *Plan-started*  
  *And* no **Agent** has run yet  
*When* the operator selects tickets *#14* only for the **Swarm** flow slice  
*Then* **Swarm** tickets are *#14* only  
  *And* that **Swarm** holds no planned-turn list

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Supervisor holds the Outcome | grill-answers.md | tick 3 |
| Supervisor rubric hangs on the Supervisor | plan-and-swarm-sketch.md | Swarm Plan / Create Supervisor |
| Shared flow/ticket slice is selected once | grill-answers.md | ticks 10, 14–16 |
