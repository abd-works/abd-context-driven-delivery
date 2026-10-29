---
name: harness-graph-read-graph
description: >-
  Return matching graph nodes as JSON, with ancestors, children, and relationships.
  
  filter keys: practice(s), type(s), name, rules, relationships;
  violations: true returns only failing nodes with only their failing rule rows;
  paths: source path prefixes (relative to the folder, e.g. src/orders) a node must sit under.
---

Return matching graph nodes as JSON, with ancestors, children, and relationships.

filter keys: practice(s), type(s), name, rules, relationships;
violations: true returns only failing nodes with only their failing rule rows;
paths: source path prefixes (relative to the folder, e.g. src/orders) a node must sit under.

Use MCP tool: `graph.return_nodes(filter: 'dict | None' = None)`
