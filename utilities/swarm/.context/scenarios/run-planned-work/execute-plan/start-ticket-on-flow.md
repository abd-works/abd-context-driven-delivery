---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Start Ticket On Flow

**Story type:** user

**Actor:** Practitioner

**Sources / context:** `utilities/swarm/.context/story-map.md`; `utilities/swarm/.context/grill-answers.md` ticks 20, 24; `utilities/plan/.context/module-context.md`; `utilities/workflow/.context/module-context.md`

### Domain terms

- *Inbox* — Project 1; Backlog / In Progress / Done
- *Flow Project* — the GitHub Project for one **Workflow**; Status columns are that flow’s states
- */start-ticket /{flow} N* — takes issue `#N` off the inbox onto that flow board, enters the first state, creates a real **Turn**
- *Unnamed start* — `/start-ticket` without a flow name leaves the ticket **In Progress** on the inbox

## Behaviors

### Scenario: Named flow start moves the ticket onto the flow board and creates a Turn

*Given* inbox **Project** *1* holds **Ticket** *#14* in *Backlog*  
  *And* **Workflow** *small-work* has **Project** *small-work-board*  
*When* the operator runs `/start-ticket` `/small-work` *14*  
*Then* **Ticket** *#14* is removed from inbox **Project** *1*  
  *And* **Ticket** *#14* is on **Project** *small-work-board* in that flow’s first state  
  *And* a **Turn** exists for **Ticket** *#14* in that state  
  *And* a **WorkSession** is open for that work

### Scenario: Unnamed start stays In Progress on the inbox

*Given* inbox **Project** *1* holds **Ticket** *#14* in *Backlog*  
*When* the operator runs `/start-ticket` *14* without a flow name  
*Then* **Ticket** *#14* **TicketState** is *In Progress* on inbox **Project** *1*  
  *And* **Ticket** *#14* is not on a flow **Project**

### Scenario: Harness puts Projects into prompts

*Given* flow **Project**s *small-work-board* and *hotfix-board* exist  
*When* the harness builds the operator/agent prompt  
*Then* that prompt lists those **Project**s  
  *And* that prompt includes how to `/start-ticket` on a named flow

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Named flow start moves the ticket onto the flow board and creates a Turn | grill-answers.md | tick 24 |
| Unnamed start stays In Progress on the inbox | grill-answers.md | tick 24 |
| Harness puts Projects into prompts | grill-answers.md | tick 24 |
