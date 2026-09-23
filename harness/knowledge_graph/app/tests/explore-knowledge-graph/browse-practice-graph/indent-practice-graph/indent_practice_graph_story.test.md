---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

### Domain terms

- ++KnowledgeGraph++ — registry of PracticeGraphs for a working area
- ++Node++ — typed practice instance on the graph
- ++PracticeGraph++ — nested Node tree for one practice

### Evidence

| Source | Note |
|--------|------|
| knowledge-graph-explorer-sketch.md | Indent Practice Graph |
| chat defect B | indent by hierarchy |

## Behaviors

#### Scenario: children sit one indent level under their parent

*Given* a ++KnowledgeGraph++ with a parent ++Node++ and a child ++Node++  
*When* the **Engineer** browses the ++KnowledgeGraph++  
*Then* the child sits one indent level under the parent
