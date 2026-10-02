---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

### Domain terms

- ++Node++ — typed practice instance on the graph
- ++rules++ — property on a Node, listed as a collapsed child

### Evidence

| Source | Note |
|--------|------|
| knowledge-graph-explorer-sketch.md | Collapse Node Rules |
| chat defect D | rules dump at the bottom |

## Behaviors

#### Scenario: rules stay collapsed until the rules Node is opened

*Given* a ++Node++ with applicable ++rules++  
*When* the **Engineer** expands that ++Node++ without opening ++rules++  
*Then* rule slugs are not listed  
*When* the **Engineer** opens the ++rules++ child  
*Then* those ++rules++ are listed
