---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

### Domain terms

- ++KnowledgeGraph++ — registry of PracticeGraphs for a working area
- ++Node++ — typed practice instance on the graph
- ++keep-operations-small-focused++ — Clean Engineering code rule

### Evidence

| Source | Note |
|--------|------|
| knowledge-graph-explorer-sketch.md | Browse / Open / Follow / Filter stories |

## Behaviors

#### Scenario: KnowledgeGraph lists PracticeGraphs and Nodes

*Given* a ++KnowledgeGraph++ whose source includes a ++Node++ that passes ++keep-operations-small-focused++  
  *And* whose source includes a ++Node++ that fails ++keep-operations-small-focused++  
*When* the **Engineer** browses the ++KnowledgeGraph++  
*Then* the passing ++Node++ lists ++keep-operations-small-focused++ as passing  
  *And* the failing ++Node++ lists ++keep-operations-small-focused++ as violating
