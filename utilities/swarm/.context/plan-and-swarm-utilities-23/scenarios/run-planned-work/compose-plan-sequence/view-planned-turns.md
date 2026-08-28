---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: View Planned Turns

**Story type:** user

**Actor:** Practitioner (operator composing the **Plan**)

**Sources / context:** `utilities/swarm/.context/plan-and-swarm-utilities-23/grill-answers.md` tick 1; `utilities/swarm/.context/plan-and-swarm-utilities-23/story-map.md` Increment 1; `utilities/plan/.context/module-context.md`

### Domain terms

- *Plan* — associated with a **Workspace**; holds ordered **PlannedTurn**s
- *PlannedTurn* — one slot on a **Plan**
- *JudgeCheckpoint* — optional on a **PlannedTurn**; not a distinct turn
- *HipCheckpoint* — optional on a **PlannedTurn**; not a distinct turn

> In steps: bold domain concepts (`**<Concept>**`); italic concrete values (`*<value>*`).

## Behaviors

### Scenario: Ordered PlannedTurns show context tool, action, fidelity, and context

*Given* a **Plan** *compose judged plan* with a **PlannedTurn** that names context tool *Stories*, action *generate*, fidelity *story_map*, and context *plan-and-swarm-utilities-23*  
  *And* that **Plan** has a later **PlannedTurn** that names context tool *CleanEngineering*, action *generate*, fidelity *modules*, and context *plan-and-swarm-utilities-23*  
*When* the operator views **PlannedTurn**s on that **Plan**  
*Then* that **Plan** shows the *Stories* **PlannedTurn** before the *CleanEngineering* **PlannedTurn**  
  *And* each **PlannedTurn** shows its context tool, action, fidelity, and context

### Scenario: View shows checkpoints on the PlannedTurn they belong to

*Given* a **Plan** *compose judged plan* whose first **PlannedTurn** names context tool *Stories*, action *generate*, fidelity *story_map*, and context *plan-and-swarm-utilities-23* and has a **JudgeCheckpoint** against rubric *stories-scenarios*  
  *And* that **Plan** has a later **PlannedTurn** that names context tool *CleanEngineering*, action *generate*, fidelity *modules*, and context *plan-and-swarm-utilities-23* and has a **HipCheckpoint**  
*When* the operator views **PlannedTurn**s on that **Plan**  
*Then* that **Plan** shows the **JudgeCheckpoint** on the *Stories* **PlannedTurn**  
  *And* that **Plan** shows the **HipCheckpoint** on the *CleanEngineering* **PlannedTurn**  
  *But* neither checkpoint appears as its own **PlannedTurn**

### Evidence

| Scenario | Source (document / system) | Location |
| --- | --- | --- |
| Ordered PlannedTurns | grill-answers.md | tick 1 — ordered planned turns |
| Checkpoints on the PlannedTurn they belong to | grill-answers.md | tick 1 — checkpoints are not distinct turns |
