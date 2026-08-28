---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Add Agent

**Story type:** user

**Actor:** Supervisor

**Sources / context:** `utilities/swarm/.context/plan-and-swarm-utilities-23/plan-and-swarm-sketch.md`; `utilities/swarm/.context/plan-and-swarm-utilities-23/grill-answers.md` ticks 5, 10, 12; `utilities/sub_agent/.context/module-context.md`

### Domain terms

- *Agent* — **SubAgent** under one **Hypothesis**; registered at Add Agent
- *Hypothesis* — first-order approach toward **Supervisor** **Outcome**
- *SubAgent* — non-blocking launch seam; **SubAgent.run** launches at **Plan.start**
- *WorkSession* — each **Agent** opens its own; not the Plan Start Plan session

## Behaviors

### Scenario: Agent holds the Hypothesis and is not launched yet

*Given* a **Supervisor** with **Outcome** *Plan-started*  
*When* the **Supervisor** adds an **Agent** with **Hypothesis** *Stories generate story_map*  
*Then* that **Agent** owns **Hypothesis** *Stories generate story_map*  
  *And* that **Agent** is a **SubAgent**  
  *And* **SubAgent.run** has not launched yet  
  *And* the **Supervisor** still owns **Outcome** *Plan-started*

### Scenario: Agent starts Plan launches SubAgent on its WorkSession

*Given* an **Agent** that owns **Hypothesis** *Stories generate story_map*  
  *And* **Swarm** turns are the *Stories* **Turn** only  
*When* that **Agent** starts the **Plan**  
*Then* **SubAgent.run** launches on that **Agent** **WorkSession**  
  *And* **Workspace.openWorkSession** has a **WorkSession** for that **Agent**  
  *And* that **WorkSession** is not the Plan Start Plan **WorkSession**

### Scenario: Second Agent runs the same shared turn slice

*Given* **Swarm** turns are the *Stories* **Turn** only  
  *And* a **Supervisor** with two **Agent**s with different **Hypothesis**es  
*When* each **Agent** starts the **Plan** on its **WorkSession**  
*Then* each **Agent** **WorkSession** openTurn is the *Stories* **Turn**

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Agent holds the Hypothesis and is not launched yet | grill-answers.md | tick 12 |
| Agent starts Plan launches SubAgent on its WorkSession | grill-answers.md | ticks 5, 12 |
| Second Agent runs the same shared turn slice | grill-answers.md | tick 10 |
