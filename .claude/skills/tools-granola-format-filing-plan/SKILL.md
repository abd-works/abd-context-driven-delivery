---
name: tools-granola-format-filing-plan
description: >-
  Render a filing plan for the user to confirm.
  plan: JSON list of {"note_id", "title", "date", "folder", "new_folder": bool, "reason"}.
  Returns markdown grouped by folder, new folders marked (new), with a total count.
  Every note appears exactly once; a note with an empty folder is listed under Review Before Filing.
---

Render a filing plan for the user to confirm.
plan: JSON list of {"note_id", "title", "date", "folder", "new_folder": bool, "reason"}.
Returns markdown grouped by folder, new folders marked (new), with a total count.
Every note appears exactly once; a note with an empty folder is listed under Review Before Filing.

Use MCP tool: `granola.format_filing_plan(plan: 'str')`
