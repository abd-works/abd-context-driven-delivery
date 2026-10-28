---
name: actions-validate
description: >-
  Check artifacts against rules.
  rule: one Rule to check. Omit it to walk each guidance's rules.
  graph: true for the workspace's saved graph (.context/graph.json), or path(s) to graph_return_nodes JSON
  or a saved graph.json. When set, append a graph-rule report for each guidance's practice and still run AI validation.
  paths: optional path prefixes (e.g. src/my-paradise) to scope graph violations.
  
  guidance: the slugs you type, such as stories, clean-engineering-model, or bdd-behavior. A list runs this action once per slug. A module:Class ref is that slug after lookup. Any other string is text this action runs once.
---

Check artifacts against rules.
rule: one Rule to check. Omit it to walk each guidance's rules.
graph: true for the workspace's saved graph (.context/graph.json), or path(s) to graph_return_nodes JSON
or a saved graph.json. When set, append a graph-rule report for each guidance's practice and still run AI validation.
paths: optional path prefixes (e.g. src/my-paradise) to scope graph violations.

guidance: the slugs you type, such as stories, clean-engineering-model, or bdd-behavior. A list runs this action once per slug. A module:Class ref is that slug after lookup. Any other string is text this action runs once.

Use MCP tool: `validate.validate(guidance: 'GuidanceArg', rule: 'Rule | None' = None, graph: 'bool | str | list[str] | None' = None, paths: 'list[str] | None' = None)`
