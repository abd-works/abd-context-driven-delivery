---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Record Planned Turn

**Story type:** user

**Actor:** Practitioner (operator composing the **Plan**)

**Sources / context:** `utilities/swarm/.context/plan-and-swarm-utilities-23/issue-body.md`; `utilities/swarm/.context/plan-and-swarm-utilities-23/grill-answers.md` tick 1; `utilities/swarm/.context/plan-and-swarm-utilities-23/story-map.md` Increment 1; `utilities/plan/.context/module-context.md` (Plan, PlannedTurn)

### Domain terms

- *Plan* — associated with a **Workspace**; holds ordered **PlannedTurn**s; does not launch agents
- *PlannedTurn* — one slot on a **Plan**; invokes context tools, actions, fidelities, and context
- *JudgeCheckpoint* — optional on a **PlannedTurn**; not a distinct turn
- *HipCheckpoint* — optional on a **PlannedTurn**; not a distinct turn

> In steps: bold domain concepts (`**<Concept>**`); italic concrete values (`*<value>*`).

## Behaviors

### Scenario Outline: PlannedTurn is on the Plan with context tool, action, fidelity, and context

*Given* a **Plan** *compose judged plan* associated with a **Workspace**  
*When* the operator records a **PlannedTurn** on that **Plan**  
    with context tool {context_tool}  
    action {action}  
    fidelity {fidelity}  
    and context {context}  
*Then* that **Plan** shows the **PlannedTurn** in sequence  
  *And* that **PlannedTurn** names context tool {context_tool}, action {action}, fidelity {fidelity}, and context {context}  
  *But* that **PlannedTurn** is not a **JudgeCheckpoint**  
  *And* that **PlannedTurn** is not a **HipCheckpoint**

### Examples

| scenario   | context_tool      | action   | fidelity  | context                      |
|------------|-------------------|----------|-----------|------------------------------|
| Scenario 1 | Stories           | generate | story_map | plan-and-swarm-utilities-23  |
| Scenario 2 | CleanEngineering  | generate | modules   | plan-and-swarm-utilities-23  |

### Scenario: Later PlannedTurn follows the earlier PlannedTurn

*Given* a **Plan** *compose judged plan* associated with a **Workspace**  
  *And* that **Plan** already has a **PlannedTurn** with context tool *Stories*, action *generate*, fidelity *story_map*, and context *plan-and-swarm-utilities-23*  
*When* the operator records a **PlannedTurn** on that **Plan**  
    with context tool *CleanEngineering*, action *generate*, fidelity *modules*, and context *plan-and-swarm-utilities-23*  
*Then* that **Plan** shows the *Stories* **PlannedTurn** before the *CleanEngineering* **PlannedTurn**

### Evidence

| Scenario | Source (document / system) | Location |
| --- | --- | --- |
| Scenario Outline | grill-answers.md | tick 1 — Plan holds planned turns |
| Later PlannedTurn follows the earlier PlannedTurn | utilities/plan/.context/module-context.md | ordered sequence of PlannedTurns |
