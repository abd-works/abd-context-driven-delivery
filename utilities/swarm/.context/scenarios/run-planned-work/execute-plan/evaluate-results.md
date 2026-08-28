---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Evaluate Results

**Story type:** user

**Actor:** Judge

**Sources / context:** `utilities/swarm/.context/story-map.md`; `utilities/plan/.context/module-context.md`; `utilities/cli_agent/.context/module-context.md`

### Domain terms

- *JudgeCheckpoint* — hangs on the **Turn**; filled by **CliAgent** doer-judge (own console, never print mode)
- *JudgeResult* — held on **JudgeCheckpoint** after the doer-judge finishes
- *CliAgent* — worker that runs doer and judge sessions on the same **WorkSession**

## Behaviors

### Scenario: CliAgent doer-judge fills JudgeCheckpoint on the Turn

*Given* a **Turn** *In Progress* with a **JudgeCheckpoint** rubric *stories-scenarios*  
  *And* that **Turn** holds **result**  
*When* **CliAgent** doer-judge evaluates that **Turn**  
*Then* that **JudgeCheckpoint** holds the **JudgeResult**  
  *And* **Plan.evaluate_results** records that **JudgeResult** on the **JudgeCheckpoint**  
  *And* that **Turn** **TicketState** is *In Progress*

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| CliAgent doer-judge fills JudgeCheckpoint on the Turn | story-map.md | JudgeCheckpoint / CliAgent |
