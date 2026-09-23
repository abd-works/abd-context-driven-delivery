---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

### Domain terms

- ++Module++ — source-module Node
- ++Package++ — disk folder Node

### Evidence

| Source | Note |
|--------|------|
| knowledge-graph-explorer-sketch.md | Show Disk Packages |
| chat defect F | harness subfolders missing |

## Behaviors

#### Scenario: disk folders show under a Module even when they are only Packages

*Given* harness with disk folders guidance and mcp  
*When* the **Engineer** opens harness  
*Then* those folders are listed  
  *And* classes stay inside them
