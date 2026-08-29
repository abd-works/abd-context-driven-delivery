---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Manage Judge Checkpoints

**Story type:** user

**Actor:** Practitioner

**Sources / context:** `utilities/swarm/.context/grill-answers.md` tick 28; `utilities/workflow/.context/module-context.md`; `utilities/plan/.context/module-context.md`

### Domain terms

- *JudgeCheckpoint* — hangs on a **Turn** when the entered state includes a judge rubric in the flow yaml
- *CliAgent doer-judge* — fills the checkpoint (existing 3-fail); no rubric means no judge on that state

## Behaviors

### Scenario: State rubric attaches JudgeCheckpoint on enter

*Given* `workflow/flows/small-work.yaml` state *Fix* includes judge rubric *small-work-fix*  
*When* **Ticket** *#14* enters state *Fix*  
*Then* the created **Turn** has a **JudgeCheckpoint** against *small-work-fix*  
  *And* **CliAgent** doer-judge runs that checkpoint

### Scenario: No rubric means no judge on that state

*Given* state *Root Cause* has no judge rubric in the flow yaml  
*When* **Ticket** *#14* enters state *Root Cause*  
*Then* the created **Turn** has no **JudgeCheckpoint**

### Scenario: Editing the rubric updates later Turns

*Given* state *Fix* rubric was *small-work-fix*  
*When* the operator changes that rubric to *small-work-fix-v2* in the flow yaml  
*Then* a later enter of *Fix* attaches **JudgeCheckpoint** against *small-work-fix-v2*

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| State rubric attaches JudgeCheckpoint on enter | grill-answers.md | tick 28 |
| No rubric means no judge on that state | grill-answers.md | tick 28 |
| Editing the rubric updates later Turns | grill-answers.md | tick 28 |
