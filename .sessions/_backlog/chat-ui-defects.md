# Chat UI defects

Each defect a person reported in the chat UI, and where it stands. The earlier list, all fixed, is in `.sessions/_complete/chat-ui-defects/chat-ui-defects.md`.

## The queue band shows a pasted message as the goal's title, with 77 interruptions under it

Reported 2026-11-23. The queue band read "70/77 1. [interruption] <pasted_content id="7250"> ## Notes from the backlog From `board-enhancements…`". The person's first message of the chat was pasted text, so the goal took the raw paste, tags included, as its title. Then every later message, whatever it was about, was filed under that goal as an `[interruption]` step, until it held 77 steps; the main chat had to rename it and mark it done by hand.

Wanted: a goal's title is a short summary of what it asks, never raw pasted text or its `<pasted_content>` tags. A message about new work starts a goal of its own instead of becoming another step of the last one. A goal holding many unrelated interruptions is split, or its finished steps folded away.

Open: queued to release-1-1-2.
