---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Comparative Association

**Story type:** user

**Actor:** Supervisor

**Sources / context:** `utilities/swarm/.context/plan-and-swarm-sketch.md`; `utilities/swarm/.context/grill-answers.md` tick 11

### Domain terms

- *Comparative Association* — **Supervisor.associate** under **Supervisor** rubric toward **Outcome**
- *Outcome* — overarching result owned by **Supervisor**
- *Hypothesis* — still owned by each **Agent** after association

## Behaviors

### Scenario: Association follows streamed Judge compare

*Given* **Supervisor.compare** just streamed a **JudgeCheckpoint** evaluation  
  *And* a **Supervisor** rubric for **Outcome** *Plan-started*  
*When* that compare event completes  
*Then* **Supervisor.associate** updates under that rubric toward **Outcome** *Plan-started*  
  *And* each **Agent** still owns its **Hypothesis**

### Scenario: Association includes a second Agent as it arrives

*Given* **Supervisor.associate** already holds the *Stories* **Agent** under the **Supervisor** rubric  
  *And* the *CleanEngineering* **Agent** **JudgeCheckpoint** has just finished  
*When* **Supervisor.compare** streams that **JudgeCheckpoint** evaluation  
*Then* **Supervisor.associate** includes both **Agent**s under the **Supervisor** rubric toward **Outcome** *Plan-started*

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Association follows streamed Judge compare | grill-answers.md | tick 11 |
| Association includes a second Agent as it arrives | grill-answers.md | tick 11 |
