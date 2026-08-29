---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Start Plan

**Story type:** user

**Actor:** Practitioner (operator composing the **Plan**)

**Sources / context:** `utilities/swarm/.context/plan-and-swarm-utilities-23/grill-answers.md` tick 1; `utilities/workspace/.context/module-context.md` (Workspace, WorkSession, Turn); `utilities/plan/.context/module-context.md`

### Domain terms

- *Plan* — associated with a **Workspace**; starting it opens a **WorkSession**
- *Workspace* — existing seam; owns **WorkSession**s
- *WorkSession* — has actual **Turn**s; not a second session type
- *Turn* — actual turn on the **WorkSession** (`prompt`, `result`, `context`, `toolCalls`, `finish`)
- *PlannedTurn* — what the **Plan** scheduled; after **Turn**.finish, the next **PlannedTurn** runs

> In steps: bold domain concepts (`**<Concept>**`); italic concrete values (`*<value>*`).

## Behaviors

### Scenario: Starting the Plan opens a WorkSession

*Given* a **Plan** *compose judged plan* associated with a **Workspace**  
  *And* that **Plan** has a **PlannedTurn** that names context tool *Stories*, action *generate*, fidelity *story_map*, and context *plan-and-swarm-utilities-23*  
*When* the operator starts that **Plan**  
*Then* that **Workspace** has a **WorkSession** for that **Plan**  
  *And* that **WorkSession** is not a second session type besides **WorkSession**  
  *And* that **Plan** still holds the same **PlannedTurn**s

### Scenario: After the actual Turn finishes the next PlannedTurn is due

*Given* a **Plan** *compose judged plan* associated with a **Workspace**  
  *And* that **Plan** has a first **PlannedTurn** that names context tool *Stories*, action *generate*, fidelity *story_map*, and context *plan-and-swarm-utilities-23*  
  *And* that **Plan** has a later **PlannedTurn** that names context tool *CleanEngineering*, action *generate*, fidelity *modules*, and context *plan-and-swarm-utilities-23*  
  *And* the operator has started that **Plan** so a **WorkSession** is open  
*When* the **WorkSession** **Turn** for the first **PlannedTurn** finishes  
*Then* the next **PlannedTurn** due on that **Plan** is the *CleanEngineering* **PlannedTurn**  
  *And* the finished **Turn** remains an actual **Turn** on the **WorkSession**

### Evidence

| Scenario | Source (document / system) | Location |
| --- | --- | --- |
| Starting the Plan opens a WorkSession | grill-answers.md | tick 1 — start initiates WorkSession |
| After the actual Turn finishes | grill-answers.md | tick 1 — after turn closes, next planned turn |
