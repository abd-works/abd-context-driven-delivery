---
name: actions-satisfy
description: >-
  Run validate for each listed guidance against the content; apply generate_fixes_from_validate, then validate again when done.
  
  guidance: the slugs you type, such as stories, clean-engineering-model, or bdd-behavior. A list runs this action once per slug. A module:Class ref is that slug after lookup. Any other string is text this action runs once.
---

Run validate for each listed guidance against the content; apply generate_fixes_from_validate, then validate again when done.

guidance: the slugs you type, such as stories, clean-engineering-model, or bdd-behavior. A list runs this action once per slug. A module:Class ref is that slug after lookup. Any other string is text this action runs once.

Use MCP tool: `satisfy.satisfy(guidance: 'GuidanceArg')`
