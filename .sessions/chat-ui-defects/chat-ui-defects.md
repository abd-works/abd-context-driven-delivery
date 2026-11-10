# Chat UI defects
- every action the chat bar sends must include the session param and the format param
- the checkboxes in the session switch dialog (LEAVE commit / push / merge, OPEN create branch / create worktree) are not clickable
- pressing a folder or the Files button in the chat bar's expanded panel reads the files into the chat: it shows file tabs (story-map.md, story-map.drawio) over a session.read_file error, 96,711 characters over the token limit; files must never be added to the chat, they open in a file window as the board does
  ![screenshot](chat-ui-defects/files-read-into-chat.png)
- the expanded panel's folder list for Discovery shows harness five times instead of each folder once
- in the ticket card's FIDELITY list, only the fidelity's name is clickable; the coloured square and the whole line, status text included, should pick that fidelity too
  ![screenshot](chat-ui-defects/fidelity-list-clickable.png)
- opening a violation report (e.g. stories-scenarios-20261107T001054.md) shows it inside the chat interface; it should open in the side panel
  ![screenshot](chat-ui-defects/violation-report-in-chat.png)
- closing a session that is on main should commit and push main, as switching a branch does, and not try to delete a worktree; main has no worktree to delete
- the close and switch dialogs need a Create handoff checkbox, on by default; when it is on, closing or switching writes a handoff for the session being left
- with the story map fidelity picked, the ▶ action button and its ▾ action list box disappear from the chat band; only the fidelity squares and the view icons show
- the chat bar shows "The board did not answer: SavedGraphOutdated … stories-scenarios-20261107T001054.json is in shape None, not 2; load the working copy again" when a session's saved validation report predates the graph shape change; an old report should open, or say it is out of date and offer to validate again, not break the session list
  ![screenshot](chat-ui-defects/saved-graph-outdated.png)

## Found by the end-to-end test (e2e/e2e-report.md)

Still open from the fixes above:
- the board's Handoff, Split, + Ticket and ✕ Close send no `session=`; every board command must carry the session as the chat bar's do
- the chat bar's diagram tab "Open in draw.io" submits a prompt to the chat as the user; it should open the draw.io viewer directly, with no chat message
- the switch dialogs offer merge when the work is on main: the board's says "Merge main into main", and the chat bar's switch always lists merge; offer merge only when the branch is not the default branch
- the chat bar's report tab shows no out-of-date notice for a report whose saved graph predates the graph shape; show the notice and Validate again, as the board does

New:
- B1 board commands go to the wrong chat: with no chat picked the target is the most recently active chat, so Run next, handoff, close and fix prompts reach an unrelated chat; send each command to the ticket's own chat, and ask when it has none
- B3 the board's close dialog shows "branch none yet" for a ticket whose branch exists in a worktree, and labels the choices with the ticket title instead of the branch name
- B4 closing commits before the session folder moves to `.sessions/_complete/`, so the move stays uncommitted, and the closed ticket's branch stays checked out; commit after the move and return to the default branch
- B5 activating with nothing active sends a handoff for no session and toasts ": handoff written" with an empty name; skip the handoff when nothing is being left
- B6 the stage Run button defaults to format=python for the whole Discovery stage; use each fidelity's default format
- B7 pressing a ticket card, or a tile on it, creates a git worktree and starts a new Claude chat when the ticket has none; pressing a card only selects it
- B8 the server-down banner dumps a raw Python traceback across the top of the board; show a one-line message, with the details behind a toggle
- B9 the details header shows "context-driven-delivery" whatever project the board runs in; show the board's own project name
- B10 graph app: node source never appears (`graph.source` returns null, and the failed call is an uncaught promise), and the Violations switch shows nothing. The graph emptying after a session switch is the refactor's per-session graph; round 6 moved graph builds into a worker process
- B11 the shared cdd server stalled for minutes during parallel graph validates, and board calls such as `ticket.branch` then hang with no feedback; round 6 runs graph builds one at a time. Show progress or a timeout message on the board when a call is slow

Found while testing the chat bar by hand:
- the chat bar shows "no session" and an empty session list: the cdd header names the folder the chat connected from (the desktop app's `spare-*` folder), not the folder it works in now. Fixed: every chat bar call sends `chat_folder` (`$.session.root()`), and `ToolCall.sent` makes it the call's project, so sessions follow the chat's branch and worktree
- switching away from us-taxes with delete worktree and delete branch left the branch and kept us-taxes active: the chat bar asked the agent to move the chat out of the worktree and called `ticket.activate` before the move landed, so the chat held the folder open and `WorktreeNotRemovedError` stopped the switch halfway. The error was a passing toast, the chat moved anyway, and the error was logged inside the worktree being deleted. Fixed: the switch and close wait until the chat is out of the worktree, a failed action stays in red above the line with Fix (sends it to the chat) and ✕, and a failed switch does not move the chat. Still open: the server logs a call's failure in the session of the call's own folder, which a worktree delete removes
- the chat bar offers "Move this chat there" in a chat that runs in its own worktree, but the desktop app never moves such a chat, so the button always fails; hide it, or say the chat can't move and offer to open a new chat in that folder
