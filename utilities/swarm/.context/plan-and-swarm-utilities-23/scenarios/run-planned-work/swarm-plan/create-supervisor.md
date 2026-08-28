---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Create Supervisor

**Story type:** user

**Actor:** Supervisor

**Sources / context:** `utilities/swarm/.context/plan-and-swarm-utilities-23/plan-and-swarm-sketch.md`; `utilities/swarm/.context/plan-and-swarm-utilities-23/grill-answers.md` ticks 3, 10; `utilities/swarm/.context/module-context.md`

### Domain terms

- *Supervisor* — owns **Outcome** and **rubric**; on a **Plan**
- *Outcome* — overarching result owned by **Supervisor**
- *Swarm* — holds shared **turns** selected once before any **Agent** runs
- *Turn* — existing `workspace.Turn` on the **Plan**

## Behaviors

### Scenario: Supervisor holds the Outcome

*Given* a **Plan** *compose-judged-plan* with **Turn**s  
*When* the operator creates a **Supervisor** with **Outcome** *Plan-started*  
*Then* that **Supervisor** owns **Outcome** *Plan-started*  
  *And* that **Supervisor** is on that **Plan**  
  *And* that **Supervisor** holds no **Agent**s yet

### Scenario: Shared turn slice is selected once

*Given* a **Plan** with a *Stories* **Turn** and a later *CleanEngineering* **Turn**  
  *And* a **Supervisor** with **Outcome** *Plan-started*  
  *And* no **Agent** has run yet  
*When* the operator selects **Turn**s the *Stories* **Turn** only for the **Swarm**  
*Then* **Swarm** turns are the *Stories* **Turn** only

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Supervisor holds the Outcome | grill-answers.md | tick 3 |
| Shared turn slice is selected once | grill-answers.md | tick 10 |
