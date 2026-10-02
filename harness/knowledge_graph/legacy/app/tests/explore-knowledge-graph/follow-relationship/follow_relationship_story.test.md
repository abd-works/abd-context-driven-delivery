---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

### Domain terms

- ++Node++ — typed practice instance on the graph
- ++Relationship++ — connector from one Node to another
- ++properties++ — Node-type fields listed as a collapsed child
- ++relationships++ — Node-type listing of Relationship kinds and targets

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

#### Scenario: a Class lists Relationship kinds including demonstratedThrough

*Given* a ++Class++ ++Node++ demonstrated through a stories ++Example++  
*When* the **Engineer** opens ++relationships++ on that ++Class++  
*Then* every Relationship kind is listed  
  *And* demonstratedThrough lists the ++Example++  
*When* the **Engineer** follows demonstratedThrough to that ++Example++  
*Then* the ++Example++ ++Node++ is selected
