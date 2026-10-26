---
name: actions-improvement-repair
description: >-
  Open a domain repair on each listed guidance and instruct the fix.
  asset: path to the file under repair. Pass the file. Do not paste its body.
  violation: the rule name, or a path to the violation report. Do not paste the asset.
  
  guidance: the slugs you type, such as stories, clean-engineering-model, or bdd-behavior. A list runs this action once per slug. A module:Class ref is that slug after lookup. Any other string is text this action runs once.
---

Open a domain repair on each listed guidance and instruct the fix.
asset: path to the file under repair. Pass the file. Do not paste its body.
violation: the rule name, or a path to the violation report. Do not paste the asset.

guidance: the slugs you type, such as stories, clean-engineering-model, or bdd-behavior. A list runs this action once per slug. A module:Class ref is that slug after lookup. Any other string is text this action runs once.

Use MCP tool: `improvement.repair(guidance: 'GuidanceArg', asset: 'str' = '', violation: 'str' = '')`
