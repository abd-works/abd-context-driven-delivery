---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Compare Swarm Results

**Story type:** user

**Actor:** Supervisor

**Sources / context:** `utilities/swarm/.context/plan-and-swarm-sketch.md`; `utilities/swarm/.context/grill-answers.md` ticks 4, 6, 11; `context_tools/agent_bdd/.context/module-context.md`

### Domain terms

- *Compare Swarm Results* — same judgment shape as Evaluate Results / Review Progress
- *JudgeCheckpoint* — AI judge on a **Turn**; holds **JudgeResult**
- *HILCheck* — human-in-the-loop check on a **Turn**
- *Comparative Association* — automatic after each streamed compare under **Supervisor** rubric toward **Outcome**

## Behaviors

### Scenario: Compare streams after a JudgeCheckpoint and associates

*Given* an **Agent** that owns **Hypothesis** *Stories generate story_map*  
  *And* that **Agent** **WorkSession** **Turn** just finished a **JudgeCheckpoint**  
  *And* another **Agent** is still running  
*When* the **Supervisor** compares swarm results  
*Then* **Supervisor.compare** includes that **JudgeCheckpoint** evaluation  
  *And* **Supervisor.compare** shows progress for every **Agent**  
  *And* **Supervisor.associate** updates under the **Supervisor** rubric toward **Outcome** *Plan-started*  
  *And* the other **Agent** is still running

### Scenario: Compare streams after a HILCheck and associates

*Given* an **Agent** **WorkSession** **Turn** just finished a **HILCheck**  
  *And* another **Agent** is still running  
*When* the **Supervisor** compares swarm results  
*Then* **Supervisor.compare** includes that **HILCheck** validation  
  *And* **Supervisor.compare** shows progress for every **Agent**  
  *And* **Supervisor.associate** updates under the **Supervisor** rubric toward **Outcome** *Plan-started*

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Compare streams after a JudgeCheckpoint and associates | grill-answers.md | ticks 6, 11 |
| Compare streams after a HILCheck and associates | grill-answers.md | ticks 6, 11 |
