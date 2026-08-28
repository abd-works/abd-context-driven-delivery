---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Add HIL Check

**Story type:** user

**Actor:** Practitioner (operator composing the **Plan**)

**Sources / context:** `utilities/swarm/.context/plan-and-swarm-utilities-23/issue-body.md`; `utilities/swarm/.context/plan-and-swarm-utilities-23/grill-answers.md` tick 1; `utilities/plan/.context/module-context.md` (HILCheck)

### Domain terms

- *Plan* — holds ordered **PlannedTurn**s
- *PlannedTurn* — may optionally have a **JudgeCheckpoint** and/or a **HILCheck**
- *HILCheck* — human-in-the-loop check on that **PlannedTurn**

> In steps: bold domain concepts (`**<Concept>**`); italic concrete values (`*<value>*`).

## Behaviors

### Scenario: HILCheck hangs on the PlannedTurn

*Given* a **Plan** *compose judged plan* with a **PlannedTurn** that names context tool *Stories*, action *generate*, fidelity *story_map*, and context *plan-and-swarm-utilities-23*  
*When* the operator adds a **HILCheck** to that **PlannedTurn**  
*Then* that **PlannedTurn** has the **HILCheck**  
  *And* the **Plan** still has that one **PlannedTurn**

### Scenario: PlannedTurn can hold both checkpoints

*Given* a **Plan** *compose judged plan* with a **PlannedTurn** that already has a **JudgeCheckpoint** against rubric *stories-scenarios*  
*When* the operator adds a **HILCheck** to that **PlannedTurn**  
*Then* that **PlannedTurn** has the **JudgeCheckpoint** and the **HILCheck**  
  *And* the **Plan** still has one **PlannedTurn**

### Evidence

| Scenario | Source (document / system) | Location |
| --- | --- | --- |
| HILCheck hangs on the PlannedTurn | grill-answers.md | tick 1 — same attachment as judge |
| PlannedTurn can hold both checkpoints | grill-answers.md | tick 1 — judge and/or HIP on a planned turn |
