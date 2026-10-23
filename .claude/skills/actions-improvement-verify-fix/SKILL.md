---
name: actions-improvement-verify-fix
description: >-
  Re-run the regression check for a themed repair bucket on each listed guidance.
  theme: the repair bucket to re-check.
  
  guidance: the slugs you type, such as stories, clean-engineering-model, or bdd-behavior. A list runs this action once per slug. A module:Class ref is that slug after lookup. Any other string is text this action runs once.
---

Re-run the regression check for a themed repair bucket on each listed guidance.
theme: the repair bucket to re-check.

guidance: the slugs you type, such as stories, clean-engineering-model, or bdd-behavior. A list runs this action once per slug. A module:Class ref is that slug after lookup. Any other string is text this action runs once.

Use MCP tool: `improvement.verify_fix(guidance: 'GuidanceArg', theme: 'str')`
