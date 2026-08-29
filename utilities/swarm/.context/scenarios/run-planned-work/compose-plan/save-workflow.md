---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Save Workflow

**Story type:** user

**Actor:** Practitioner

**Sources / context:** `utilities/swarm/.context/story-map.md`; `utilities/swarm/.context/grill-answers.md` ticks 14, 19, 23, 33; `utilities/workflow/.context/module-context.md`

### Domain terms

- *Save Workflow* — persist `workflow/flows/{name}.yaml` and keep the flow’s GitHub **Project** for reuse
- *One Project per Workflow* — that Project’s Status columns are the flow’s states

## Behaviors

### Scenario: Saving creates or keeps a dedicated flow Project

*Given* a composed **Workflow** *hotfix-batch* with configured state behavior  
*When* the operator saves that **Workflow**  
*Then* a GitHub **Project** for *hotfix-batch* exists  
  *And* `workflow/flows/hotfix-batch.yaml` exists with owner and project_number  
  *And* that **Project**’s Status columns are the flow’s states

### Scenario: Saved Workflow can be reused by a later Plan

*Given* saved **Workflow** *small-work*  
*When* the operator creates a **Plan** from that **Workflow** with tickets *#20* and *#21*  
*Then* that **Plan** runs **Workflow** *small-work*  
  *And* those tickets use the existing *small-work* **Project**

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Saving creates or keeps a dedicated flow Project | grill-answers.md | ticks 19, 23 |
| Saved Workflow can be reused by a later Plan | grill-answers.md | ticks 14, 33 |
