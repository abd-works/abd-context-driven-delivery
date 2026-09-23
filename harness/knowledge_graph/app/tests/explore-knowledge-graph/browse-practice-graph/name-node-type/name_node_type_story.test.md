---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

### Domain terms

- ++Node++ — typed practice instance on the graph
- ++Package++ — folder Node
- ++Module++ — source-module Node

### Evidence

| Source | Note |
|--------|------|
| knowledge-graph-explorer-sketch.md | Name Node Type |
| chat defect C | hover tooltip of Node type |

## Behaviors

#### Scenario: hover names the Node type

*Given* a ++Package++ and a ++Module++ on the PracticeGraph  
*When* the **Engineer** points at the ++Node++ icon or name  
*Then* the tooltip names ++Package++  
  *And* names ++Module++
