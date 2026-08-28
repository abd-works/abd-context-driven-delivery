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

- *Compare Swarm Results* — **Supervisor.compare** reads **Turn** **JudgeCheckpoint** / **HILCheck** results; does not judge
- *JudgeCheckpoint* — hangs on the **Turn**; filled by **CliAgent** doer-judge
- *HILCheck* — human-in-the-loop check on a **Turn**
- *Comparative Association* — automatic after each streamed compare under **Supervisor** rubric toward **Outcome**

## Behaviors

### Scenario: Compare streams after a JudgeCheckpoint

*Given* an **Agent** that owns **Hypothesis** *Stories generate story_map*  
  *And* that **Agent** **WorkSession** **Turn** just finished a **JudgeCheckpoint**  
  *And* another **Agent** is still running  
*When* the **Supervisor** compares swarm results  
*Then* **Supervisor.compare** includes that **JudgeCheckpoint** evaluation  
  *And* **Supervisor.compare** shows progress for every **Agent**  
  *And* **Supervisor.associate** updates under the **Supervisor** rubric toward **Outcome** *Plan-started*  
  *And* the other **Agent** is still running

### Scenario: Compare streams after a HILCheck

*Given* an **Agent** **WorkSession** **Turn** just finished a **HILCheck**  
  *And* another **Agent** is still running  
*When* the **Supervisor** compares swarm results  
*Then* **Supervisor.compare** includes that **HILCheck** validation  
  *And* **Supervisor.compare** shows progress for every **Agent**  
  *And* **Supervisor.associate** updates under the **Supervisor** rubric toward **Outcome** *Plan-started*

### Scenario: Compare does not wait for all Agents

*Given* two **Agent**s still running Execute Plan  
  *And* the *Stories* **Agent** **Turn** just finished a **JudgeCheckpoint**  
*When* the **Supervisor** compares swarm results  
*Then* **Supervisor.compare** includes that **JudgeCheckpoint** evaluation  
  *And* the *CleanEngineering* **Agent** is still running

### Scenario: Compare can use a Plan JudgeCheckpoint rubric

*Given* a **Plan** **Turn** with **JudgeCheckpoint** rubric *stories-scenarios*  
  *And* an **Agent** **WorkSession** **Turn** just finished that **JudgeCheckpoint**  
*When* the **Supervisor** compares swarm results  
*Then* **Supervisor.compare** includes that **JudgeCheckpoint** rubric evaluation

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Compare streams after a JudgeCheckpoint | grill-answers.md | ticks 6, 11 |
| Compare streams after a HILCheck | grill-answers.md | ticks 6, 11 |
| Compare does not wait for all Agents | plan-and-swarm-sketch.md | Swarm Plan / Compare Swarm Results |
| Compare can use a Plan JudgeCheckpoint rubric | plan-and-swarm-sketch.md | Swarm Plan / Compare Swarm Results |
