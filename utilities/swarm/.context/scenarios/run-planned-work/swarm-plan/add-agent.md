---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Add Agent

**Story type:** user

**Actor:** Supervisor

**Sources / context:** `utilities/swarm/.context/plan-and-swarm-sketch.md`; `utilities/swarm/.context/story-map.md`; `utilities/swarm/.context/grill-answers.md` ticks 5, 10, 12, 14–16; `utilities/cli_agent/.context/module-context.md`

### Domain terms

- *Agent* — **CliAgent** under one **Hypothesis**; registered at Add Agent
- *Hypothesis* — first-order approach toward **Supervisor** **Outcome**
- *CliAgent* — interactive CLI worker; **CliAgent.launch_sessions** starts at **Plan.start**
- *WorkSession* — each **Agent** opens its own; not the Plan start session
- *Shared flow/ticket slice* — tickets selected once on the **Swarm**; each **Agent** runs that same slice on its **WorkSession** (no planned-turn list)
- *JudgeCheckpoint* — hangs on the **Turn** created when a ticket enters a flow state; filled by **CliAgent** doer-judge

## Behaviors

### Scenario: Agent holds the Hypothesis and is not launched yet

*Given* a **Supervisor** with **Outcome** *Plan-started*  
*When* the **Supervisor** adds an **Agent** with **Hypothesis** *Stories generate story_map*  
*Then* that **Agent** owns **Hypothesis** *Stories generate story_map*  
  *And* that **Agent** is a **CliAgent**  
  *And* **CliAgent.launch_sessions** has not started yet  
  *And* the **Supervisor** still owns **Outcome** *Plan-started*

### Scenario: Second Agent holds a different Hypothesis

*Given* a **Supervisor** with an **Agent** that owns **Hypothesis** *Stories generate story_map*  
*When* the **Supervisor** adds an **Agent** with **Hypothesis** *CleanEngineering generate modules*  
*Then* that **Agent** owns **Hypothesis** *CleanEngineering generate modules*  
  *And* the first **Agent** still owns **Hypothesis** *Stories generate story_map*

### Scenario: Agent opens its own WorkSession

*Given* an **Agent** that owns **Hypothesis** *Stories generate story_map*  
  *And* **Swarm** tickets are *#14* only on **Workflow** *small-work*  
*When* that **Agent** starts the **Plan**  
*Then* **CliAgent.launch_sessions** starts on that **Agent** **WorkSession**  
  *And* **Workspace.openWorkSession** has a **WorkSession** for that **Agent**  
  *And* that **WorkSession** is not the Plan start **WorkSession**

### Scenario: Agent runs the shared flow/ticket slice on its WorkSession

*Given* an **Agent** that owns **Hypothesis** *Stories generate story_map*  
  *And* that **Agent** **WorkSession** is open  
  *And* **Swarm** tickets are *#14* only  
*When* that **Agent** runs the **Plan** on its **WorkSession**  
*Then* that **Agent** takes *#14* through the **Workflow** states (each move creates a **Turn**)  
  *And* Validate with Human, Evaluate Results, Review Progress, Advance Ticket State, and Fix and Rerun apply as those same stories

### Scenario: Agent does not run tickets outside the shared slice

*Given* **Swarm** tickets are *#14* only  
  *And* a **Supervisor** with an **Agent** that owns **Hypothesis** *Stories generate story_map*  
*When* that **Agent** starts the **Plan** on its **WorkSession**  
*Then* that **Agent** runs ticket *#14* on the flow  
  *And* that **Agent** does not run ticket *#15*

### Scenario: Second Agent runs the same shared flow/ticket slice

*Given* **Swarm** tickets are *#14* only  
  *And* a **Supervisor** with two **Agent**s with different **Hypothesis**es  
*When* each **Agent** starts the **Plan** on its **WorkSession**  
*Then* each **Agent** **WorkSession** runs ticket *#14* on the same **Workflow**  
  *And* neither **Agent** holds a planned-turn list

### Scenario: Supervisor may add an Agent while the Swarm is running

*Given* a **Supervisor** with an **Agent** that is still running the **Plan**  
*When* the **Supervisor** adds an **Agent** with **Hypothesis** *CleanEngineering generate modules*  
*Then* that new **Agent** owns **Hypothesis** *CleanEngineering generate modules*  
  *And* **CliAgent.launch_sessions** has not started for that new **Agent** yet  
  *And* the first **Agent** is still running  
  *And* the **Supervisor** still owns **Outcome** *Plan-started*

### Scenario: Mid-run add launches when that Agent starts Plan

*Given* a **Supervisor** with an **Agent** still running the **Plan**  
  *And* a new **Agent** with **Hypothesis** *CleanEngineering generate modules*  
  *And* **CliAgent.launch_sessions** has not started for that new **Agent** yet  
*When* that new **Agent** starts the **Plan** on its **WorkSession**  
*Then* **CliAgent.launch_sessions** starts on that new **Agent** **WorkSession**  
  *And* the first **Agent** is still running

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Agent holds the Hypothesis and is not launched yet | story-map.md | Swarm Plan / Add Agent |
| Second Agent holds a different Hypothesis | plan-and-swarm-sketch.md | Swarm Plan / Add Agent |
| Agent opens its own WorkSession | story-map.md | CliAgent worker |
| Agent runs the shared flow/ticket slice on its WorkSession | grill-answers.md | ticks 10, 14–16 |
| Agent does not run tickets outside the shared slice | grill-answers.md | ticks 10, 16 |
| Second Agent runs the same shared flow/ticket slice | grill-answers.md | ticks 10, 16 |
| Supervisor may add an Agent while the Swarm is running | grill-answers.md | tick 6 |
| Mid-run add launches when that Agent starts Plan | story-map.md | CliAgent.launch_sessions |
