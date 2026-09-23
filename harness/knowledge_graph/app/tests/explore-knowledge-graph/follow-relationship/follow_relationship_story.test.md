---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

### Domain terms

- ++Node++ — typed practice instance on the graph
- ++Relationship++ — connector from one Node to another

### Evidence

| Source | Note |
|--------|------|
| knowledge-graph-explorer-sketch.md | Follow Relationship |

## Behaviors

#### Scenario: following a Relationship focuses the target Node

*Given* a ++Node++ with a ++Relationship++ to a target ++Node++  
*When* the **Engineer** follows the ++Relationship++  
*Then* the target ++Node++ is selected  
  *And* the target source file is shown when the target is a file
