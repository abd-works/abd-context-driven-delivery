---
alwaysApply: false
globs:
  - "src/**/*.ts"
---

- **`cross-practice-edge-resolves-registered-node`** - An edge query may name a node_id already registered on another practice. `load_edges` resolves that node on the same `CodeQLKnowledgeGraph` and records the edge on the practice that ran the query.
