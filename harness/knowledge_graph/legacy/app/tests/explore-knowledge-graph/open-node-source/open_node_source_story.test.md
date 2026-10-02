---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

### Domain terms

- ++Node++ — typed practice instance on the graph
- ++source++ — file plus range for a Node
- ++OoadClass++ — class Node
- ++Operation++ — operation Node

### Evidence

| Source | Note |
|--------|------|
| knowledge-graph-explorer-sketch.md | Open Node Source |
| chat defects H, I, J | rules-only pane; missing graph source; header-only class |

## Behaviors

#### Scenario: file Node opens source and highlights range

*Given* a ++KnowledgeGraph++ with a file ++Node++ that has a source file and range  
*When* the **Engineer** selects the file ++Node++  
*Then* the source file is shown  
  *And* the ++Node++ range is highlighted

#### Scenario: class Node shows the whole class

*Given* a class ++Node++ whose graph source is missing or only the header  
*When* the **Engineer** selects the class ++Node++  
*Then* the source pane shows the whole class body  
  *And* rule problems sit below that excerpt

#### Scenario: a class pane lists nested operations

*Given* a class ++Node++ that owns operations  
*When* the **Engineer** selects the class ++Node++  
*Then* the source pane lists those operations under the class

#### Scenario: operation Node shows the whole operation

*Given* an operation ++Node++ whose graph source is missing or only the header  
*When* the **Engineer** selects the operation ++Node++  
*Then* the source pane shows the whole operation  
  *And* not the enclosing class
