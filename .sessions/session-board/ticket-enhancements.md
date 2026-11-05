# Ticket Enhancements

The first board enhancements are better ticket management. They come from the backlog item
`.sessions/_backlog/board-enhancements.md` and from notes drawn on the board on 2026-11-05.

## Requirements

- Edit a ticket's text.
- Reorder tickets in a column.
- Break up a ticket using smart thin slicing.
- Show parent and child relationships between tickets:
  - pull a child out of its parent so it moves on its own
  - expand and collapse a parent to see its children
- Nest branches and sessions for tickets in a hierarchy.
- Click any empty area of a ticket to expand it.
- Make a child independent of its parent.
- Add a ticket as a child of a different parent.
- Delete a ticket.
- Archive a ticket.

## Notes drawn on the board

- **Parent and children:** a parent ticket holds its child tickets stacked inside it. The parent's title sits small, above the
  children.
- **Pulling a child:** a child pulled out of its parent becomes a ticket of its own beside it.
- **Split:** splitting a ticket goes to the AI, which proposes the children.
- **Create children:** a person can also add children to a ticket by hand.
- **Backlog item text:** a backlog item's card shows the text of its markdown file, and a double click edits it.
- **Session ticket text:** a session's ticket shows its text the same way, from a markdown file kept in the session
  folder. A session's instructions refer to that file, so the board and the agent read the same text. The board may not
  do this today; check the code, then keep the text in that file and refer to it.
