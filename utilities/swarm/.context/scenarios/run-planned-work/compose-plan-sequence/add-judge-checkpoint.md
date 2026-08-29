---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Add Judge Checkpoint

**Story type:** user

**Actor:** Practitioner (operator composing the **Plan**)

**Sources / context:** `utilities/swarm/.context/plan-and-swarm-utilities-23/issue-body.md`; `utilities/swarm/.context/plan-and-swarm-utilities-23/grill-answers.md` tick 1; `utilities/plan/.context/module-context.md` (JudgeCheckpoint)

### Domain terms

- *Plan* — holds ordered **PlannedTurn**s
- *PlannedTurn* — may optionally have a **JudgeCheckpoint** and/or a **HipCheckpoint**
- *JudgeCheckpoint* — AI judge against a rubric on that **PlannedTurn**; not a distinct turn

> In steps: bold domain concepts (`**<Concept>**`); italic concrete values (`*<value>*`).

## Behaviors

### Scenario: JudgeCheckpoint hangs on the PlannedTurn

*Given* a **Plan** *compose judged plan* with a **PlannedTurn** that names context tool *Stories*, action *generate*, fidelity *story_map*, and context *plan-and-swarm-utilities-23*  
*When* the operator adds a **JudgeCheckpoint** to that **PlannedTurn** against rubric *stories-scenarios*  
*Then* that **PlannedTurn** has the **JudgeCheckpoint** against rubric *stories-scenarios*  
  *But* the **Plan** does not gain another **PlannedTurn**  
  *And* that **JudgeCheckpoint** is not a **HipCheckpoint**

### Scenario: Later PlannedTurn can have its own JudgeCheckpoint

*Given* a **Plan** *compose judged plan* with a **PlannedTurn** that already has a **JudgeCheckpoint** against rubric *stories-scenarios*  
  *And* that **Plan** has a later **PlannedTurn** that names context tool *CleanEngineering*, action *generate*, fidelity *modules*, and context *plan-and-swarm-utilities-23*  
*When* the operator adds a **JudgeCheckpoint** to the later **PlannedTurn** against rubric *plan-modules*  
*Then* the first **PlannedTurn** still has the *stories-scenarios* **JudgeCheckpoint**  
  *And* the later **PlannedTurn** has the *plan-modules* **JudgeCheckpoint**  
  *But* neither **JudgeCheckpoint** is its own **PlannedTurn**

### Evidence

| Scenario | Source (document / system) | Location |
| --- | --- | --- |
| JudgeCheckpoint hangs on the PlannedTurn | grill-answers.md | tick 1 — optional on a planned turn |
| Later PlannedTurn can have its own JudgeCheckpoint | grill-answers.md | tick 1 — not distinct turns |
