---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Resolve Ticket Number

**Story type:** user

**Actor:** Agent

**Sources / context:** `utilities/swarm/.context/plan-and-swarm-sketch.md`; `utilities/git/.context/module-context.md`

### Domain terms

- *Ticket* — **parseNumber** resolves GitHub issue `#` or issues URL to the number
- *Repo* — holds **Ticket**s keyed by that number

## Behaviors

### Scenario: Ticket number resolves from a GitHub issue ref

*Given* a **Repo**  
*When* the agent resolves ticket ref *#23*  
*Then* **Ticket.parseNumber** is *23*

### Scenario: Issue URL resolves the same number

*Given* a **Repo**  
*When* the agent resolves an issues URL for *23*  
*Then* **Ticket.parseNumber** is *23*

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Ticket number resolves from a GitHub issue ref | plan-and-swarm-sketch.md | Manage Ticket Flow / Resolve Ticket Number |
| Issue URL resolves the same number | plan-and-swarm-sketch.md | Manage Ticket Flow / Resolve Ticket Number |
