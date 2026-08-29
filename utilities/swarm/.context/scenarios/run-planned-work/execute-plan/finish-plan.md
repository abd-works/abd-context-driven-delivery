---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Finish Plan

**Story type:** user

**Actor:** Practitioner

**Sources / context:** `utilities/swarm/.context/story-map.md`; `utilities/swarm/.context/grill-answers.md` ticks 30–33; `utilities/plan/.context/module-context.md`

### Domain terms

- */finish-plan* — operator gate after the flow is done: move tickets to inbox Done, close issues, close session
- *Flow-done* — tickets stay on the flow **Project** until `/finish-plan` (no auto-return)
- *Throwaway* — temp **Project** + `workflow/flows/{name}.yaml` deleted on `/finish-plan`
- *Saved Workflow* — **Project** + yaml survive `/finish-plan`; only tickets move

## Behaviors

### Scenario: Flow-done cards stay on the flow board until /finish-plan

*Given* every ticket on **Plan** *small-work-theme* has finished the last flow state  
*When* the agent completes that flow work  
*Then* those **Ticket**s remain on the flow **Project**  
  *And* the agent does not move them to inbox **Project** *1* by itself

### Scenario: /finish-plan moves tickets, closes issues, and closes the session

*Given* flow-done **Ticket**s *#14* and *#15* on **Project** *small-work-board*  
  *And* the operator has scanned the board  
*When* the operator runs `/finish-plan`  
*Then* those **Ticket**s are on inbox **Project** *1* as *Done*  
  *And* issues *#14* and *#15* are closed  
  *And* the **WorkSession** is closed

### Scenario: Throwaway Project and yaml are deleted on /finish-plan

*Given* a throwaway **Workflow** with temp **Project** *tmp-flow* and file `workflow/flows/tmp-flow.yaml`  
*When* the operator runs `/finish-plan` after tickets are on the inbox and issues are closed  
*Then* **Project** *tmp-flow* is deleted  
  *And* `workflow/flows/tmp-flow.yaml` is deleted

### Scenario: Saved Workflow survives /finish-plan

*Given* saved **Workflow** *small-work* with **Project** *small-work-board* and `workflow/flows/small-work.yaml`  
*When* the operator runs `/finish-plan`  
*Then* **Project** *small-work-board* still exists  
  *And* `workflow/flows/small-work.yaml` still exists  
  *And* only the tickets moved

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Flow-done cards stay on the flow board until /finish-plan | grill-answers.md | ticks 30–31 |
| /finish-plan moves tickets, closes issues, and closes the session | grill-answers.md | ticks 30–31 |
| Throwaway Project and yaml are deleted on /finish-plan | grill-answers.md | ticks 32, 21, 29 |
| Saved Workflow survives /finish-plan | grill-answers.md | tick 33 |
