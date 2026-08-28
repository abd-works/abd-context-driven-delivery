---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Evaluate Results

**Story type:** user

**Actor:** Judge

**Sources / context:** `utilities/swarm/.context/plan-and-swarm-sketch.md`; `utilities/plan/.context/module-context.md`; `context_tools/agent_bdd/.context/module-context.md`

### Domain terms

- *JudgeCheckpoint* — **ai_judge** runs on **Turn** result against **rubric**
- *JudgeResult* — held on **JudgeCheckpoint** after evaluation

## Behaviors

### Scenario: Judge Checkpoint evaluates the Turn result

*Given* a **Turn** *In Progress* with a **JudgeCheckpoint** rubric *stories-scenarios*  
  *And* that **Turn** holds **result**  
*When* the Judge evaluates that **Turn**  
*Then* **ai_judge** runs on that **Turn** result against rubric *stories-scenarios*  
  *And* that **JudgeCheckpoint** holds the **JudgeResult**  
  *And* that **Turn** **TicketState** is *In Progress*

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Judge Checkpoint evaluates the Turn result | plan-and-swarm-sketch.md | Execute Plan / Evaluate Results |
