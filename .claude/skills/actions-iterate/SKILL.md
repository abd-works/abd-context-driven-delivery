---
name: actions-iterate
description: >-
  Grill the plan with grill: ask short framed questions and wait for answers. After each small batch of answers, generate or revise only the final deliverable slice those answers unlocked, validate it, apply one fix pass, and get user feedback before asking more. Work in short cycles until the deliverables are agreed. Do not dump the whole product in one tick, and do not sketch — iterate the formal artifacts.
  tools: operation names this cycle may call.
  
  guidance: the slugs you type, such as stories, clean-engineering-model, or bdd-behavior. A list runs this action once per slug. A module:Class ref is that slug after lookup. Any other string is text this action runs once.
---

Grill the plan with grill: ask short framed questions and wait for answers. After each small batch of answers, generate or revise only the final deliverable slice those answers unlocked, validate it, apply one fix pass, and get user feedback before asking more. Work in short cycles until the deliverables are agreed. Do not dump the whole product in one tick, and do not sketch — iterate the formal artifacts.
tools: operation names this cycle may call.

guidance: the slugs you type, such as stories, clean-engineering-model, or bdd-behavior. A list runs this action once per slug. A module:Class ref is that slug after lookup. Any other string is text this action runs once.

Use MCP tool: `iterate.iterate(guidance: 'GuidanceArg', tools: 'list[str]' = None)`
