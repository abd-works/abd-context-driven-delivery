---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Add Agent

**Story type:** user

**Actor:** Supervisor

**Sources / context:** `utilities/swarm/.context/plan-and-swarm-sketch.md`; `utilities/swarm/.context/story-map.md`; `utilities/cli_agent/.context/module-context.md`

### Domain terms

- *Agent* — **CliAgent** under one **Hypothesis**; registered at Add Agent
- *Hypothesis* — first-order approach toward **Supervisor** **Outcome**
- *CliAgent* — interactive CLI worker; **CliAgent.launch_sessions** starts at **Plan.start**
- *WorkSession* — each **Agent** opens its own; not the Plan Start Plan session
- *Swarm.turns* — shared turn slice selected once; each **Agent** runs that slice
- *JudgeCheckpoint* — hangs on the **Turn**; filled by **CliAgent** doer-judge (not judge-as-agent on **Agent**)

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
  *And* **Swarm** turns are the *Stories* **Turn** only  
*When* that **Agent** starts the **Plan**  
*Then* **CliAgent.launch_sessions** starts on that **Agent** **WorkSession**  
  *And* **Workspace.openWorkSession** has a **WorkSession** for that **Agent**  
  *And* that **WorkSession** is not the Plan Start Plan **WorkSession**

### Scenario: Agent runs Execute Plan on its WorkSession

*Given* an **Agent** that owns **Hypothesis** *Stories generate story_map*  
  *And* that **Agent** **WorkSession** is open  
*When* that **Agent** executes its *In Progress* **Turn**  
*Then* that **Agent** **WorkSession** runs Execute Plan  
  *And* Validate with Human, Evaluate Results, Review Progress, Advance Turn, and Fix and Rerun are those same stories

### Scenario: Agent runs selected Turns from the Plan

*Given* **Swarm** turns are the *Stories* **Turn** only  
  *And* a **Supervisor** with an **Agent** that owns **Hypothesis** *Stories generate story_map*  
*When* that **Agent** starts the **Plan** on its **WorkSession**  
*Then* that **Agent** **WorkSession** openTurn is the *Stories* **Turn**  
  *And* that **WorkSession** does not run the *CleanEngineering* **Turn**

### Scenario: Second Agent runs the same shared turn slice

*Given* **Swarm** turns are the *Stories* **Turn** only  
  *And* a **Supervisor** with two **Agent**s with different **Hypothesis**es  
*When* each **Agent** starts the **Plan** on its **WorkSession**  
*Then* each **Agent** **WorkSession** openTurn is the *Stories* **Turn**

### Scenario: Supervisor may add an Agent while the Swarm is running

*Given* a **Supervisor** with an **Agent** that is still running Execute Plan  
*When* the **Supervisor** adds an **Agent** with **Hypothesis** *CleanEngineering generate modules*  
*Then* that new **Agent** owns **Hypothesis** *CleanEngineering generate modules*  
  *And* **CliAgent.launch_sessions** has not started for that new **Agent** yet  
  *And* the first **Agent** is still running  
  *And* the **Supervisor** still owns **Outcome** *Plan-started*

### Scenario: Mid-run add launches when that Agent starts Plan

*Given* a **Supervisor** with an **Agent** still running Execute Plan  
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
| Agent runs Execute Plan on its WorkSession | plan-and-swarm-sketch.md | Swarm Plan / Add Agent |
| Agent runs selected Turns from the Plan | grill-answers.md | tick 10 |
| Second Agent runs the same shared turn slice | grill-answers.md | tick 10 |
| Supervisor may add an Agent while the Swarm is running | grill-answers.md | tick 6 |
| Mid-run add launches when that Agent starts Plan | story-map.md | CliAgent.launch_sessions |
