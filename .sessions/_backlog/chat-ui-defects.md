# Chat UI defects

Each defect a person reported in the chat UI, and where it stands.

## A diagram not drawn yet opens empty in draw.io

Reported 2026-11-12. The chat bar's files view listed `.context/modules.drawio` for Clean Engineering modules and offered
Open in draw.io, which opened an empty diagram: the fidelity declares the file, but no one had drawn it.

Fixed on branch `class-diagram-improvements`: each tab carries whether its file exists, and a diagram not drawn yet says
"… is not drawn yet." with no Open in draw.io button (`harness/chat-ui/pane/hooks/chat-bar/fidelity-files-view.tsx`).

## Opening a ticket from the chat bar: "you are on Remote Control", no chat started

Reported 2026-11-12, several times. Opening a ticket from the main chat's chat bar types a request into the main chat
asking its agent to start the ticket's chat with `start_session`. The desktop app refused it each time, saying the person
is working over Remote Control, though they were at the desktop.

Cause: Remote Control is switched on for the main chat (`remoteControlActive: true`). With it on, the app cannot tell
whether a message it did not see the person type came from the desktop or a phone, so it refuses to start a session from
a message the chat bar typed. A message the person types themselves starts it.

Open: turn Remote Control off on the main chat while working at the desktop, or have the chat bar start the chat some way
that does not depend on the agent's turn.

## Dragging a Backlog item onto another puts it above, never makes it a child

Reported 2026-11-12, ticket `ticket-maintanance-defects`. In the Backlog, dragging one card onto another put it just
above the other card instead of making it the other's child: a backlog item had no parent, so the drop only called
`backlog-item.move_before`.

Fixed on branch `ticket-maintanance-defects`: a drop near a Backlog card's top edge puts the item above it, near its
bottom edge below it (`backlog-item.move_after`), and in the middle makes it the card's child (`backlog-item.nest_under`).
A parent is a folder, `_backlog/<parent>/`, whose `<parent>.md` holds its text; every other markdown file in it is a child,
stacked as a row in the parent's card. Dragging a child onto the Backlog list takes it out (`backlog-item.leave_parent`),
and starting the parent starts its children as its child tickets. A folder kept with a ticket's work (a session.json)
neither takes children nor becomes one. Live once the branch is merged and the cdd server repinned.
## A Backlog card's Edit text field sits under the text, showing it twice

Reported 2026-11-12, ticket `ticket-maintanance-defects`. On a selected Backlog card, Edit text opened a one-line field
under the item's read-only text, so the same text showed twice and the field cut it to one line.

Fixed on branch `ticket-maintanance-defects`: the field opens in the text's place, as a box of several lines holding the
whole text; Enter saves, Shift+Enter adds a line, Escape puts it away (`backlog-item-view.tsx`, `ItemTextView`).
## A Backlog card's "More in <file>" is plain text

Reported 2026-11-12, ticket `ticket-maintanance-defects`. A selected Backlog card ends its text with "More in
<file>", which could not be opened.

Fixed on branch `ticket-maintanance-defects`: it is a link, on every selected Backlog card, that opens the item's file in
the app the computer opens markdown with (`backlog-item.open_file`). Opening it in the Claude app's file viewer is not
done: the board has no way to reach that viewer yet.

## The roots dialog keeps showing the old root after Change

Reported 2026-11-12, ticket `ticket-maintanance-defects`. In a ticket's Roots dialog, choosing a new folder for the
session or a practice saved it, but the row still showed the old root ("harness · default").

Fixed on branch `ticket-maintanance-defects`: the dialog drew the ticket object it was opened with; it now draws the ticket
as the board read it last (`root-choice-client.ts`).

## Activating a ticket on the board opens its worktree but starts no chat

Reported 2026-11-12 through the main board's chat, ticket `ticket-maintanance-defects`. Pressing Activate on "Integrate
Practice Content Editor Apps" made its worktree and recorded it, but no chat was started on it; the board only said to
open its chat from its card.

Fixed on branch `ticket-maintanance-defects`: with no chat working in the worktree, Activate starts one there, as the
card's chat button does (`activation-client.ts`); the new chat's prompt asks it to call `sessions.switch` with the
ticket's name first (`newChatLink` in `chat-client.tsx`).

## Starting a Backlog item by dragging it into Discovery starts no chat

Reported 2026-11-12, ticket `ticket-maintanance-defects`. Dragging a Backlog item into Discovery started its ticket, but
no worktree or chat opened.

Fixed on branch `ticket-maintanance-defects`: starting an item, by drag or by Start, now activates its ticket as Activate
does, so its worktree opens and its chat starts there (`root-choice-client.ts`).
