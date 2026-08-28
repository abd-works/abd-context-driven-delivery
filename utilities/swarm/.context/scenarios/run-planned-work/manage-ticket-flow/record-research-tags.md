---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Record Research Tags

**Story type:** user

**Actor:** Practitioner

**Sources / context:** `utilities/swarm/.context/plan-and-swarm-sketch.md`; `utilities/git/.context/module-context.md`

### Domain terms

- *ResearchTag* — label on an existing **Ticket** for research/flow metadata
- *Ticket* — keyed by GitHub issue number on **Repo**

## Behaviors

### Scenario: Research tags live on the existing Ticket

*Given* a **Repo** with a **Ticket** number *23*  
*When* the operator records a **ResearchTag** *specification* on that **Ticket**  
*Then* that **Ticket** holds **ResearchTag** *specification*  
  *And* that **Ticket** number is still *23*

### Scenario: A second Research Tag stays on the same Ticket

*Given* that **Ticket** already holds **ResearchTag** *specification*  
*When* the operator records a **ResearchTag** *workflow* on that **Ticket**  
*Then* that **Ticket** holds **ResearchTag** *specification*  
  *And* that **Ticket** holds **ResearchTag** *workflow*  
  *And* that **Ticket** number is still *23*

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Research tags live on the existing Ticket | plan-and-swarm-sketch.md | Manage Ticket Flow / Record Research Tags |
| A second Research Tag stays on the same Ticket | plan-and-swarm-sketch.md | Manage Ticket Flow / Record Research Tags |
