---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Advance Ticket State

**Story type:** user

**Actor:** Practitioner

**Sources / context:** `utilities/swarm/.context/story-map.md`; `utilities/swarm/.context/grill-answers.md` ticks 15–16, 25; `utilities/workflow/.context/module-context.md`

### Domain terms

- *Advance* — FIFO-move the ticket into the next **Workflow** state on its flow **Project**
- *Turn* — created by that move; work + commit for that ticket in that state
- *Batch* — agent may move related tickets together when they share one change (default remains FIFO)

## Behaviors

### Scenario: Moving into the next state creates a real Turn

*Given* **Ticket** *#14* is on flow **Project** *small-work-board* in state *Root Cause*  
  *And* that state’s **Turn** is *Done*  
*When* the operator advances **Ticket** *#14* into state *Fix*  
*Then* **Ticket** *#14* Status on that **Project** is *Fix*  
  *And* a new **Turn** exists for **Ticket** *#14* in state *Fix*

### Scenario: FIFO is the default order

*Given* **Ticket**s *#14* and *#15* are on flow **Project** *small-work-board* waiting for state *Fix*  
  *And* *#14* entered the board before *#15*  
*When* the agent advances the next ticket under FIFO  
*Then* **Ticket** *#14* enters *Fix* before **Ticket** *#15*

### Scenario: Agent may batch related tickets

*Given* **Ticket**s *#14*, *#15*, *#16*, and *#17* touch the same code change  
  *And* the agent holds context across those tickets  
*When* the agent finishes that shared fix  
*Then* those **Ticket**s may move together into the next state  
  *And* the agent decides when that batch is done

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Moving into the next state creates a real Turn | grill-answers.md | ticks 15–16 |
| FIFO is the default order | grill-answers.md | ticks 16, 25 |
| Agent may batch related tickets | grill-answers.md | tick 25 |
