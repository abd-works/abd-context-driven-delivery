---
name: tools-granola-write-note-context
description: >-
  Write one Granola note as an independent context file in {folder}/.context/granola/{date}-{slug}.md.
  date: YYYY-MM-DD of the meeting. content: the note's summary and notes as markdown, verbatim from Granola.
  Front matter marks the file as Granola source with note_id, title, date and url.
  Overwrites the file for the same note so re-running refreshes it. Returns the written path.
---

Write one Granola note as an independent context file in {folder}/.context/granola/{date}-{slug}.md.
date: YYYY-MM-DD of the meeting. content: the note's summary and notes as markdown, verbatim from Granola.
Front matter marks the file as Granola source with note_id, title, date and url.
Overwrites the file for the same note so re-running refreshes it. Returns the written path.

Use MCP tool: `granola.write_note_context(folder: 'str', note_id: 'str', title: 'str', date: 'str', url: 'str', content: 'str')`
