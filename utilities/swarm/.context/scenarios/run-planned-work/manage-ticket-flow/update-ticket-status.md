---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Update Ticket Status

**Story type:** user

**Actor:** Practitioner

**Sources / context:** `utilities/swarm/.context/plan-and-swarm-sketch.md`; `utilities/git/.context/module-context.md`

### Domain terms

- *TicketState* — Backlog | In Progress | Done — same type on **Ticket** and on **Turn**
- *Project* — board columns via **stateNamed**

## Behaviors

### Scenario: Ticket status is an existing Project state

*Given* a **Repo** with a **Ticket** number *23*  
  *And* an attached **Project**  
  *And* that **Ticket** **TicketState** is *Backlog*  
*When* the operator sets that **Ticket** status to *In Progress*  
*Then* that **Ticket** **TicketState** is *In Progress*  
  *And* **Project.state_named** *In Progress* is that **TicketState**

### Scenario: Ticket can move to Done

*Given* that **Ticket** **TicketState** is *In Progress*  
*When* the operator sets that **Ticket** status to *Done*  
*Then* that **Ticket** **TicketState** is *Done*  
  *And* **Turn** on a **Plan** uses that same **TicketState** type

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Ticket status is an existing Project state | plan-and-swarm-sketch.md | Manage Ticket Flow / Update Ticket Status |
| Ticket can move to Done | plan-and-swarm-sketch.md | Manage Ticket Flow / Update Ticket Status |
