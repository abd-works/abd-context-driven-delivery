---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Manage HIL Checks

**Story type:** user

**Actor:** Practitioner

**Sources / context:** `utilities/swarm/.context/plan-and-swarm-sketch.md`; `utilities/plan/.context/module-context.md`

### Domain terms

- *HILCheck* — human-in-the-loop check hanging on a **Turn** (not its own turn)
- *Turn* — existing **workspace.Turn**; optional **HILCheck** and **JudgeCheckpoint**

## Behaviors

### Scenario: Add a HIL Check

*Given* a **Plan** with a **Turn** *Stories generate story_map*  
*When* the operator adds a **HILCheck** to that **Turn**  
*Then* that **Turn** has the **HILCheck**  
  *And* the **Plan** still has that one **Turn**

### Scenario: Edit a HIL Check

*Given* a **Turn** that already has a **HILCheck**  
*When* the operator edits that **HILCheck**  
*Then* that **Turn** still has one **HILCheck**

### Scenario: Delete a HIL Check

*Given* a **Turn** that already has a **HILCheck**  
*When* the operator deletes that **HILCheck**  
*Then* that **Turn** has no **HILCheck**

### Scenario: HIL Check stays when a Judge Checkpoint is added

*Given* a **Turn** that already has a **HILCheck**  
*When* the operator adds a **JudgeCheckpoint** to that **Turn** against rubric *stories-scenarios*  
*Then* that **Turn** has the **HILCheck**  
  *And* that **Turn** has the **JudgeCheckpoint**

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Add a HIL Check | plan-and-swarm-sketch.md | Compose Plan / Manage HIL Checks |
| Edit a HIL Check | plan-and-swarm-sketch.md | Compose Plan / Manage HIL Checks |
| Delete a HIL Check | plan-and-swarm-sketch.md | Compose Plan / Manage HIL Checks |
| HIL Check stays when a Judge Checkpoint is added | plan-and-swarm-sketch.md | Compose Plan / Manage HIL Checks |
