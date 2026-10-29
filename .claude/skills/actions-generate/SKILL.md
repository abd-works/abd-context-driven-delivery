---
name: actions-generate
description: >-
  Write artifacts for each listed guidance at its current fidelity. The shared rules and that fidelity's rules are part of these instructions. After the artifact is written, call validate with the same guidance and paths set to the files you wrote.
  
  guidance: the slugs you type, such as stories, clean-engineering-model, or bdd-behavior. A list runs this action once per slug. A module:Class ref is that slug after lookup. Any other string is text this action runs once.
---

Write artifacts for each listed guidance at its current fidelity. The shared rules and that fidelity's rules are part of these instructions. After the artifact is written, call validate with the same guidance and paths set to the files you wrote.

guidance: the slugs you type, such as stories, clean-engineering-model, or bdd-behavior. A list runs this action once per slug. A module:Class ref is that slug after lookup. Any other string is text this action runs once.

Use MCP tool: `generate.generate(guidance: 'GuidanceArg')`
