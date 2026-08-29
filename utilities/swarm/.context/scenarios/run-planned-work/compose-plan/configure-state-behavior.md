---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Configure State Behavior

**Story type:** user

**Actor:** Practitioner

**Sources / context:** `utilities/swarm/.context/story-map.md`; `utilities/swarm/.context/grill-answers.md` ticks 16, 22–23; `utilities/workflow/.context/module-context.md`

### Domain terms

- *Flow file* — `workflow/flows/{name}.yaml`: name, optional owner + project_number, per-state behavior
- *State behavior* — tools (if any), one action (if any), utilities, prose; columns stay on GitHub
- *No planned turns* — Plan does not hold an ahead-of-time ticket×state list

## Behaviors

### Scenario: Per-state behavior is stored in the flow yaml

*Given* **Workflow** *small-work*  
*When* the operator configures state *Fix* with tools *Bdd*, action *generate*, and prose *fix the defect*  
*Then* `workflow/flows/small-work.yaml` records that behavior under state *Fix*  
  *And* the GitHub **Project** columns are unchanged by that write

### Scenario: Flow file holds owner and project number on save

*Given* **Workflow** *small-work* is saved and **Project** *42* is created  
*When* the kit writes the flow file  
*Then* `workflow/flows/small-work.yaml` includes owner and project_number *42*  
  *And* Status columns still come from GitHub

### Scenario: Plan has no planned-turn list

*Given* a **Plan** based on **Workflow** *small-work* with tickets *#14* and *#15*  
*When* the operator inspects that **Plan**  
*Then* that **Plan** names the **Workflow** and those tickets  
  *And* that **Plan** does not hold a planned ticket×state turn list

### Scenario: CliAgent still describes hanging Turn shape

*Given* a hanging **Turn** created by entering state *Fix* with action *generate*  
  *And* **tool_keys** *Stories* and *CleanEngineering*  
*When* **CliAgent** describes that **Turn**  
*Then* **CliAgent** shows that action and those **tool_keys**  
  *And* **CliAgent** does not open that **Turn**  
  *And* **CliAgent** holds no **Plan**

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Per-state behavior is stored in the flow yaml | grill-answers.md | ticks 22–23 |
| Flow file holds owner and project number on save | grill-answers.md | tick 23 |
| Plan has no planned-turn list | grill-answers.md | tick 16 |
| CliAgent still describes hanging Turn shape | grill-answers.md | tick 13 |
