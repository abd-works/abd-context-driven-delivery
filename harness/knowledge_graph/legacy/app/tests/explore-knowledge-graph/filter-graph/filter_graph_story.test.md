---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

### Domain terms

- ++KnowledgeGraph++ — registry of PracticeGraphs for a working area
- ++Node++ — typed practice instance on the graph
- ++violations++ — Nodes with failing rules
- ++keep-operations-small-focused++ — Clean Engineering code rule

### Evidence

| Source | Note |
|--------|------|
| knowledge-graph-explorer-sketch.md | Filter Graph |
| chat defect G | ancestors, violating-rule-only, red, failed/total |

## Behaviors

#### Scenario: tree lists only Nodes that match the filters

*Given* a ++KnowledgeGraph++ whose source includes a ++Node++ that passes ++keep-operations-small-focused++  
  *And* whose source includes a ++Node++ that fails ++keep-operations-small-focused++  
*When* the **Engineer** filters the ++KnowledgeGraph++ using ++violations++  
  *And* using ++keep-operations-small-focused++  
*Then* the failing ++Node++ is listed  
  *And* the passing ++Node++ is not listed

#### Scenario: keep ancestors of a violating Node

*Given* the same ++KnowledgeGraph++  
*When* the **Engineer** filters using ++violations++  
*Then* ancestors of the failing ++Node++ remain  
  *And* passing siblings drop out

#### Scenario: opening rules lists only the violating rule

*Given* a violating ++Node++ with more than one applicable rule  
*When* the **Engineer** filters using ++violations++  
*Then* the ++Node++ rules list only the violating rule  
  *And* the right pane lists only violating rules

#### Scenario: a folder pane lists nested violating Nodes

*Given* a violating ++Node++ under a parent folder  
*When* the **Engineer** filters using ++violations++  
*Then* selecting the folder lists the violating operations underneath

#### Scenario: a violating class lists only violating operations

*Given* a class that fails keep-classes-single-responsibility with mixed operations  
*When* the **Engineer** filters using ++violations++  
*Then* only operations with violations sit underneath the class

#### Scenario: parents show failed over total and stay red

*Given* a violating ++Node++ under a parent  
*When* the **Engineer** filters using ++violations++  
*Then* the failing ++Node++ and its parents are red  
  *And* (failed / total) sits beside the name
