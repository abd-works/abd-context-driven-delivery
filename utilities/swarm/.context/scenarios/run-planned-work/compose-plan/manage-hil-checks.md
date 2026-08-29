---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Manage HIL Checks

**Story type:** user

**Actor:** Practitioner

**Sources / context:** `utilities/swarm/.context/grill-answers.md` ticks 26–27; `utilities/workflow/.context/module-context.md`; `utilities/plan/.context/module-context.md`

### Domain terms

- *HILCheck* — human-in-the-loop check on a **Turn** when the entered state marks `hil` in the flow yaml
- *State mark* — `hil: true` or a HIL prompt under that state in `workflow/flows/{name}.yaml`

## Behaviors

### Scenario: Marking a state hil attaches HILCheck when entered

*Given* `workflow/flows/small-work.yaml` marks state *Review* with `hil: true`  
*When* **Ticket** *#14* enters state *Review*  
*Then* the created **Turn** has a **HILCheck**  
  *And* the agent cannot leave that state until the human finishes the loop

### Scenario: Without hil on the state the agent may mark Done

*Given* **Workflow** *small-work* has no state marked hil  
  *And* **Ticket** *#14* finished the last flow state  
*When* the agent completes that work  
*Then* the agent may move that ticket toward Done on the flow  
  *And* inbox Done still waits for operator `/finish-plan`

### Scenario: Clearing hil on a state removes future HILChecks

*Given* state *Review* was marked hil  
*When* the operator removes the hil mark from that state in the flow yaml  
*Then* a later enter of *Review* creates a **Turn** with no **HILCheck**

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Marking a state hil attaches HILCheck when entered | grill-answers.md | ticks 26–27 |
| Without hil on the state the agent may mark Done | grill-answers.md | tick 26 |
| Clearing hil on a state removes future HILChecks | grill-answers.md | tick 27 |
