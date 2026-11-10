# Maintain Tickets On Board

Analysis and planning: the stories here are not built yet, or only partly built where a story says so. This is one increment of the thin slice, which sets the order of the increments, [harness/.context/stories/thin-slice.md](../../harness/.context/stories/thin-slice.md); its epics, features and stories are on the story map, [harness/.context/stories/story-map.md](../../harness/.context/stories/story-map.md). Each requirement sits under the story it belongs to.

**Outcome:** a person edits, orders, tags and removes tickets, and arranges them as parents and children.

**Slicing notes:** mod-ideas build order 4, finish the Kanban: board-enhancements "Tickets Enhancements".

## Notes from the backlog

From `board-enhancements.md`, "Tickets Enhancements":

> - edit ticket text
> - reorder tickets in column
> - show parent child relaionships for tckets; anable pulling a child out of a parent to move indenpendentaly, expand and colapse a parent to view  children
> - nest branches and sessions for hierarchical tickets
> - break up tickets using smart thin clicing
> - tagging sessions
> - click any empty  area  to expand ticket

"break up tickets using smart thin slicing" is the Intended part of Split Ticket Into Child Tickets, which is built today: the board splits a ticket, and the AI slicing it thinly is still to come.

From `mod-ideas.md`, "Kanban and session tracking" (build order 4, "Finish the Kanban alongside all of these"):

> `cdd-board` in `harness/kanban/pane` already has the Board pane, toasts, the status line, the violations band, and `/board` and `/ticket`. It still has layout gaps against the Claude Design canvas. Content tracking can build on `ticket.files` and `ticket.report`.

## Epic: Move Work Forward On Session Board

### Feature: Maintain Tickets

#### Story: Edit Ticket Text

*Person*. Intended (`.sessions/session-board/ticket-enhancements.md`): a double click on a card's text edits it; a session ticket's text is a markdown file in its session folder that the session's instructions refer to, so the board and the agent read the same text.

#### Story: Reorder Tickets In Column

*Person*. Intended (`.sessions/session-board/ticket-enhancements.md`): a ticket dragged up or down within its column keeps that place.

#### Story: Tag Ticket Session

*Person*. Intended (`.sessions/_backlog/maintain-tickets-on-board.md` "tagging sessions"): a person adds tags to a ticket's session, and the card shows them.

#### Story: Delete Ticket

*Person*. Intended (`.sessions/session-board/ticket-enhancements.md`): Delete on a card removes the ticket and its session folder.

### Feature: See Work On Session Board

#### Story: Expand Ticket From Empty Area

*Person*. Intended (`.sessions/_backlog/maintain-tickets-on-board.md` "click any empty area to expand ticket"): a press anywhere on a card that is not a control expands it.

### Feature: Organize Ticket Hierarchy

#### Story: Add Child Ticket

*Person*. Intended (`.sessions/session-board/ticket-enhancements.md`): a person adds a child ticket to a parent by hand. Built today (checked 2026-11-10): `ticket.create(parent=…)` records the parent (`ticket.py:94`, `sessions.py:268-275`) and Split asks the chat for one child per story. Missing: adding a single child by hand on the board.

#### Story: Display Child Tickets In Parent

*Board App*. Intended (`.sessions/session-board/ticket-enhancements.md`): a parent's card holds its child tickets stacked inside it, with the parent's title small above them.

#### Story: Expand Parent Ticket

*Person*. Intended (`.sessions/session-board/ticket-enhancements.md`): a parent collapses to its own card and expands to show its children.

#### Story: Detach Child Ticket

*Person*. Intended (`.sessions/session-board/ticket-enhancements.md`): a child pulled out of its parent becomes a ticket of its own beside it and moves independently.

#### Story: Move Child Ticket To Another Parent

*Person*. Intended (`.sessions/session-board/ticket-enhancements.md`): a ticket added as a child of a different parent leaves its old parent.

#### Story: Nest Child Branch And Session

*Claude Code*. Intended (`.sessions/session-board/ticket-enhancements.md`): a child ticket's branch and session nest under its parent's, so the hierarchy holds in git and in `.sessions/` as on the board.
