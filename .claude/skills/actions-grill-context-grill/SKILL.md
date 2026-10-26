---
name: actions-grill-context-grill
description: >-
  Interview the plan against codebase context until questions are grounded in files you have read, then generate each listed guidance. Ask one framed question at a time and write each resolved insight to grill-answers.md.
  
  guidance: the slugs you type, such as stories, clean-engineering-model, or bdd-behavior. A list runs this action once per slug. A module:Class ref is that slug after lookup. Any other string is text this action runs once.
---

Interview the plan against codebase context until questions are grounded in files you have read, then generate each listed guidance. Ask one framed question at a time and write each resolved insight to grill-answers.md.

guidance: the slugs you type, such as stories, clean-engineering-model, or bdd-behavior. A list runs this action once per slug. A module:Class ref is that slug after lookup. Any other string is text this action runs once.

Use MCP tool: `grill-context.grill(guidance: 'GuidanceArg')`
