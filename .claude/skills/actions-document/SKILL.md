---
name: actions-document
description: >-
  Record what already exists for the listed guidance without correcting it. Read contexts and templates, and write the observed state under the session path so violations are flagged, not fixed.
  paths: the files and folders to scan.
  
  guidance: the slugs you type, such as stories, clean-engineering-model, or bdd-behavior. A list runs this action once per slug. A module:Class ref is that slug after lookup. Any other string is text this action runs once.
---

Record what already exists for the listed guidance without correcting it. Read contexts and templates, and write the observed state under the session path so violations are flagged, not fixed.
paths: the files and folders to scan.

guidance: the slugs you type, such as stories, clean-engineering-model, or bdd-behavior. A list runs this action once per slug. A module:Class ref is that slug after lookup. Any other string is text this action runs once.

Use MCP tool: `document.document(guidance: 'GuidanceArg', paths: 'list[str]')`
