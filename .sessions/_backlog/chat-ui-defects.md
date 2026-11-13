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

Fixed on main, 2026-11-13: the chat bar no longer asks the agent. It hands the ticket's `new_chat_link`, a
`claude://code/new` link that `Ticket` in `space/kanban/ticket.py` builds, to the Claude app with the system's opener
(`shared/system-link.ts`). The app opens a new chat on the worktree with its prompt typed in, and the person sends it, so
Remote Control does not block it and no model turn runs in the main chat. The board's app opens the same link.

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

## The chat bar's + and ⑂ are separate from what they open

Reported 2026-11-12, ticket `ticket-maintanance-defects`. In the main chat the bar showed the session name, then a bare +
for the ticket list and a bare ⑂ for the repo list, three controls for two lists.

Fixed on branch `ticket-maintanance-defects`: "main +" is one button that opens the ticket list (its card still shows on
hover), and "repo +" one button that opens the repo list (`WordPlusButtonView` in `chat-bar-view.tsx`).

## The chat bar's status sits at the right and is cut off

Reported 2026-11-12, ticket `ticket-maintanance-defects`. The host draws a plugin's status line at the right, where
"cdd-board abd-cdd-ticket-maintanance-defec · t…" was cut off; it named the session, not the branch, and the root by its
short path.

Fixed on branch `ticket-maintanance-defects`: the host's status line cannot be set left, so the bar draws its own status
row under its line, from the left: repository · branch · the whole path of the folder the session works in. The Ticket
sends `branch_name` and `root_folder` for it (`ticket.py`); the host's status line is cleared.

## A fidelity's hover tip opens nothing

Reported 2026-11-12, ticket `ticket-maintanance-defects`. Hovering a fidelity dot shows its name; pressing the name did
nothing, where the board's ? opens that fidelity's help.

Fixed on branch `ticket-maintanance-defects`: pressing the tip opens the fidelity's help panel on the board in the
browser, by a new `?help=<ticket>&fidelity=<slug>` link (`openLinkedHelp` in `board-page.ts`, `openHelp` in
`fidelity-files-client.ts`).

## The chat bar's list boxes do not line up with their buttons

Reported 2026-11-12, ticket `ticket-maintanance-defects`. The action picker opened at the overlay +, not the action
button, and the ticket and repo lists sat at the bar's right edge, not under their buttons.

Fixed on branch `ticket-maintanance-defects`: each list box is placed from the cells the line draws before its button
(`bar-columns.ts`): the stage list at the stage button, the overlay list at the +, the action picker at the action
button past the overlay and format chips, and the ticket and repo lists ending under "main +" and "repo +".

## A chat bar list box stays open after a click elsewhere

Reported 2026-11-12, ticket `ticket-maintanance-defects`. An open list of options stayed open until its own button was
pressed again.

Fixed on branch `ticket-maintanance-defects`: a press anywhere else on the bar, or typing or sending in the prompt,
closes every open list box but the pressed one's (`option-lists-client.ts`). The host sends no event for a click in the
transcript, so a click there still leaves it open.

## Opening a ticket while the main chat is busy starts no chat

Reported 2026-11-13, ticket `optimize-unit-tests`. The chat bar showed "No chat started for optimize-unit-tests: the
prompt was removed from the queue before it ran".

Cause: the chat bar asks the main chat's agent to call start_session, and that request waits in the main chat's queue
until its running turn ends. Stopping that turn clears the queue, so the request never ran.

Fixed on main: a request dropped from the queue is sent once more (`requestChatStart` in `chat-folder-client.ts`); a
second drop says the turn was stopped while the request waited.

## Pressing an app on the health panel does nothing

Reported 2026-11-13, ticket `optimize-unit-tests`. Pressing "▦ not running" (Kanban app) or "◈ not running" (Graph app)
on the chat bar's health panel neither starts nor opens the app.

Cause: never built. `PartsView` in `harness/chat-ui/pane/hooks/health/server-health-view.tsx` draws each part as plain
text with no press handler. The story "Open App From Health Panel" (`harness/.context/stories/story-map.md`,
`guard-work-and-recover-fast.md`) is still Intended: pressing an app that is down starts it then opens it, and pressing
one that is up opens it. The `/board` command (`board-server.ts`) already starts and opens the board, so the Kanban part
can reuse it; the Graph app needs its own start and open.

Fixed on branch `open-app-from-health-panel`: each app's icon and value carry a see-through press (`OpenAppView` in
`server-health-view.tsx`) that runs `openApp` (`health/open-app-client.ts`). The Kanban app starts as `/board` starts it
and opens on this repository's board page; the Graph app starts with `scripts/start_graph_web.py` then
`scripts/start_graph_app.py` and opens where they say it answers; one already running just opens. Story test:
`harness/chat-ui/pane/test/move-work-forward-from-chat-bar/check-cdd-server-health/open-app-from-health-panel/`. Live once
the branch is merged and the mod is republished.

## The chat bar froze while a ticket was created

Reported 2026-11-13 ("frozen bar"), while the chat for `open-app-from-health-panel` ran `board.show` and `ticket.create`.
`board.show` answered 960,699 characters on one line, and `ticket.create` ran past its 10 s wait; the first
`ticket.activate` after it failed on `C:/dev/abd-context-driven-delivery/.git/index.lock`, left behind with no git
process running. Removing the stale lock let `ticket.activate` finish. Not yet diagnosed: whether the bar froze on the
long cdd calls, on the lock, or on both, and why `ticket.create` left the lock.

## The status line under the prompt went missing after a cdd reinstall

Reported 2026-11-13 ("what happened to footer put below chat input"), right after the cdd server was repinned to
13b227107 and restarted, and the chat was asked to run `/reload-plugins`. The line under the prompt (repository · branch
· folder) was gone. The `PromptHint` hook in `register.ts` draws it from the active session's ticket in the chat bar's
last board read (`ChatBarClient.statusLine`), and draws nothing while that read holds no active ticket. Not yet
diagnosed: whether the read after the restart or reload failed or had not happened yet, or whether the hook was skipped.
