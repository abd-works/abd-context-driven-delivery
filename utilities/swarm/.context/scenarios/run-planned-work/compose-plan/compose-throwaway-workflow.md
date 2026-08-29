---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Compose Throwaway Workflow

**Story type:** user

**Actor:** Practitioner

**Sources / context:** `utilities/swarm/.context/story-map.md`; `utilities/swarm/.context/grill-answers.md` ticks 14, 21, 29, 32; `utilities/workflow/.context/module-context.md`

### Domain terms

- *Throwaway Workflow* — temp GitHub **Project** + `workflow/flows/{name}.yaml` for one Plan run; deleted on `/finish-plan`
- *Kit + board only* — no GitHub Actions move cards

## Behaviors

### Scenario: Throwaway run uses a temporary Project and yaml

*Given* the operator composes a one-off **Workflow** *tmp-theme* without saving for reuse  
*When* that **Plan** starts  
*Then* a temporary GitHub **Project** for *tmp-theme* exists  
  *And* `workflow/flows/tmp-theme.yaml` exists for the run  
  *And* tickets move off the inbox onto that **Project**

### Scenario: Kit moves cards without GitHub Actions

*Given* throwaway **Workflow** *tmp-theme*  
*When* a ticket enters the next state  
*Then* the kit writes Project Status  
  *And* that move creates the **Turn**  
  *And* no GitHub Action is required

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Throwaway run uses a temporary Project and yaml | grill-answers.md | ticks 21, 29 |
| Kit moves cards without GitHub Actions | grill-answers.md | tick 18 |
