---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

### Domain terms

- ++Module++ — source-module Node
- ++OoadClass++ — class Node

### Evidence

| Source | Note |
|--------|------|
| knowledge-graph-explorer-sketch.md | Nest Class Folder |
| chat defects D, F | classes belong in subfolders |

## Behaviors

#### Scenario: classes sit in their subfolder, not the parent Module

*Given* catalog folder harness that contains ++Module++ guidance under harness/guidance  
*When* the **Engineer** opens harness  
*Then* harness children include the guidance folder  
  *And* do not list Guidance as a direct child  
  *And* harness is a ++Package++  
  *And* do not list Guidance as a direct child

#### Scenario: a class lists its operations

*Given* a class ++Node++ that owns operations  
*When* the **Engineer** opens the class in the PracticeGraph  
*Then* the class children include those operations
