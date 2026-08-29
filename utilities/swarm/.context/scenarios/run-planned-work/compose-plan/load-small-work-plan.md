---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Load Small-Work Plan

**Story type:** user

**Actor:** Practitioner

**Sources / context:** `utilities/swarm/.context/story-map.md`; `utilities/plan/.context/module-context.md`; `utilities/workflow/.context/module-context.md`

### Domain terms

- *Plan* — based on a reusable **Workflow** or a **Workflow** named on `/plan`
- *Workflow* — front-end to git; *small-work* is a prebaked named Workflow
- *Workspace* — working folder (not the **Repo**)
- */plan /small-work* — loads the prebaked Workflow into a **Plan**; does not execute tickets

## Behaviors

### Scenario: /plan /small-work loads the prebaked Workflow

*Given* a **Workspace** working folder  
*When* the operator runs `/plan` `/small-work` with context *themed-defects*  
*Then* that **Plan** is based on **Workflow** *small-work*  
  *And* that **Plan** holds the prebaked **Turn**s from that Workflow  
  *And* no GitHub issue was started

### Scenario: Plan is based on a newly named Workflow

*Given* a **Workspace** working folder  
*When* the operator runs `/plan` with workflow *hotfix-batch* and context *login-bug*  
*Then* that **Plan** is based on **Workflow** *hotfix-batch*  
  *And* that **Plan** name is *hotfix-batch*

### Scenario: Small-work Turns do not inject CleanEngineering

*Given* a **Plan** loaded from **Workflow** *small-work*  
*When* the operator reviews the **Turn** tool_keys  
*Then* the behavior **Turn** lists *Bdd*  
  *And* that **Turn** does not list *CleanEngineering* injected by **Plan**

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| /plan /small-work loads the prebaked Workflow | story-map.md | Compose Plan / Load Small-Work Plan |
| Plan is based on a newly named Workflow | story-map.md | Plan based on Workflow |
| Small-work Turns do not inject CleanEngineering | story-map.md | BDD owns CE companions |
