---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Manage Judge Checkpoints

**Story type:** user

**Actor:** Practitioner

**Sources / context:** `utilities/swarm/.context/plan-and-swarm-sketch.md`; `utilities/plan/.context/module-context.md`; `context_tools/agent_bdd/.context/module-context.md`

### Domain terms

- *JudgeCheckpoint* — AI judge on a **Turn**; **rubric** is the same argument **ai_judge** already takes
- *Turn* — existing **workspace.Turn**; optional **JudgeCheckpoint** and **HILCheck**

## Behaviors

### Scenario: Add a Judge Checkpoint

*Given* a **Plan** with a **Turn** *Stories generate story_map*  
*When* the operator adds a **JudgeCheckpoint** to that **Turn** against rubric *stories-scenarios*  
*Then* that **Turn** has the **JudgeCheckpoint**  
  *And* that **JudgeCheckpoint** rubric is *stories-scenarios*  
  *And* the **Plan** still has that one **Turn**

### Scenario: Later Turn can have its own Judge Checkpoint

*Given* a **Turn** that already has **JudgeCheckpoint** *stories-scenarios*  
  *And* a later **Turn** *CleanEngineering generate modules*  
*When* the operator adds a **JudgeCheckpoint** to the later **Turn** against rubric *plan-modules*  
*Then* the first **Turn** still has *stories-scenarios*  
  *And* the later **Turn** has *plan-modules*

### Scenario: Edit a Judge Checkpoint

*Given* a **Turn** with **JudgeCheckpoint** *stories-scenarios*  
*When* the operator edits that **JudgeCheckpoint** rubric to *stories-validate*  
*Then* that **Turn** **JudgeCheckpoint** rubric is *stories-validate*

### Scenario: Delete a Judge Checkpoint

*Given* a **Turn** with a **JudgeCheckpoint**  
*When* the operator deletes that **JudgeCheckpoint**  
*Then* that **Turn** has no **JudgeCheckpoint**

### Scenario: Judge Checkpoint stays when a HIL Check is added

*Given* a **Turn** that already has a **JudgeCheckpoint**  
*When* the operator adds a **HILCheck** to that **Turn**  
*Then* that **Turn** has the **JudgeCheckpoint**  
  *And* that **Turn** has the **HILCheck**

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Add a Judge Checkpoint | plan-and-swarm-sketch.md | Compose Plan / Manage Judge Checkpoints |
| Later Turn can have its own Judge Checkpoint | plan-and-swarm-sketch.md | Compose Plan / Manage Judge Checkpoints |
| Edit a Judge Checkpoint | plan-and-swarm-sketch.md | Compose Plan / Manage Judge Checkpoints |
| Delete a Judge Checkpoint | plan-and-swarm-sketch.md | Compose Plan / Manage Judge Checkpoints |
| Judge Checkpoint stays when a HIL Check is added | plan-and-swarm-sketch.md | Compose Plan / Manage Judge Checkpoints |
