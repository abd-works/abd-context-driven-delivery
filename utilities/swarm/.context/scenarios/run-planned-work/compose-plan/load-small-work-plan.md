---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Load Small-Work Plan

**Story type:** user

**Actor:** Practitioner

**Sources / context:** `utilities/swarm/.context/story-map.md`; `utilities/swarm/.context/grill-answers.md` ticks 14, 22–24; `utilities/plan/.context/module-context.md`; `utilities/workflow/.context/module-context.md`

### Domain terms

- *small-work* — prebaked named **Workflow** (flow **Project** + `workflow/flows/small-work.yaml`)
- */plan /small-work* — loads that Workflow into a **Plan**; does not execute tickets by itself

## Behaviors

### Scenario: /plan /small-work loads the prebaked Workflow

*Given* a **Workspace** working folder  
*When* the operator runs `/plan` `/small-work` with context *themed-defects*  
*Then* that **Plan** is based on **Workflow** *small-work*  
  *And* that **Plan** uses `workflow/flows/small-work.yaml` for per-state behavior  
  *And* no GitHub issue was started by that load

### Scenario: Plan is based on a newly named Workflow

*Given* a **Workspace** working folder  
*When* the operator runs `/plan` with workflow *hotfix-batch* and context *login-bug*  
*Then* that **Plan** is based on **Workflow** *hotfix-batch*  
  *And* that **Plan** name is *hotfix-batch*

### Scenario: Small-work state behavior does not inject CleanEngineering via Plan

*Given* a **Plan** loaded from **Workflow** *small-work*  
*When* the operator reviews state *Fix* tool keys in the flow yaml  
*Then* that state may list *Bdd*  
  *And* **Plan** does not inject *CleanEngineering* (BDD owns CE companions)

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| /plan /small-work loads the prebaked Workflow | story-map.md | Compose Plan / Load Small-Work Plan |
| Plan is based on a newly named Workflow | grill-answers.md | tick 14 |
| Small-work state behavior does not inject CleanEngineering via Plan | story-map.md | BDD owns CE companions |
