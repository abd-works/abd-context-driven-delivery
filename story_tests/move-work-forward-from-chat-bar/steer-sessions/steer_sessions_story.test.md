---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Steer Sessions

### Domain terms

- ++handoff++ — a note in the session folder saying what was done and what to do next.

## Story: Display Latest Session Handoff

### Evidence

| Source | Note |
|--------|------|
| `.context/story-map.md` | Requested 2026-11-06: the chat bar shows the active session's latest handoff, as the CDD Kanban does |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: Opening a session shows its latest handoff in the chat panel

*Given* checkout-flow's session folder holds handoffs from 5 and 6 November  
*When* the Person opens the checkout-flow session  
*Then* the chat panel shows the 6 November handoff's next step and open violations  
  *And* it offers Open handoff

#### Scenario: A session with no handoff shows none

*Given* billing-report's session folder holds no handoff  
*When* the Person opens the billing-report session  
*Then* the chat panel shows no handoff card

## Story: Close Active Session

### Evidence

| Source | Note |
|--------|------|
| `.sessions/chat-ui-defects/chat-ui-defects.md` | Observed 2026-11-07: closing a session on main should commit and push main, as switching a branch does, and not try to delete a worktree; the close and switch dialogs need a Create handoff checkbox, on by default; their checkboxes could not be clicked |
| `harness/chat-ui/pane/test/move-work-forward-from-chat-bar/steer-sessions/close-active-session/close_active_session_story.test.ts` (removed in 8c56ab052) | the stubbed story test these scenarios were written for; no test plays them now |

#### Scenario: Close the session with its work committed

*Given* checkout-flow is the active session, on its own branch  
*When* the Person closes checkout-flow  
*Then* a dialog headed Close session Checkout flow offers Create handoff, commit and push on checkout-flow, all chosen  
*When* the Person confirms  
*Then* a toast says Checkout flow: handoff written, committed, pushed · Session Checkout flow closed  
  *And* no session is active

#### Scenario: Close a session whose work is on main

*Given* checkout-flow is the active session, its work on main  
*When* the Person closes checkout-flow and confirms  
*Then* the dialog offered to commit and push main  
  *And* ticket.close was asked to commit and push, and to merge nothing

#### Scenario: Choose what closing does

*Given* the close dialog for checkout-flow, on its own branch, is open  
*When* the Person unchooses Create handoff and push, and confirms  
*Then* the dialog showed only commit chosen, and ticket.close was asked only to commit

#### Scenario: Warn in the chat bar before a close deletes work nobody committed

*Given* the chat works in checkout-flow's own worktree, which holds a change to app/order.py and a new file notes.txt that nobody committed
*When* the Person closes the session from the chat bar, choosing to delete its worktree
*Then* the close dialog shows the warning that deleting the worktree without a commit loses the work, and lists app/order.py and notes.txt
*When* the Person also chooses to commit
*Then* the warning is gone
*When* the Person closes the session with only the worktree deleted
*Then* a toast names app/order.py and notes.txt as the uncommitted work lost

## Story: Open Session

#### Scenario: Choose what switching does

*Given* the activation dialog for payment-retry is open, leaving checkout-flow  
*When* the Person chooses merge, unchooses the worktree, and confirms  
*Then* the dialog first offered Create handoff, commit and push chosen, merge not, and a branch and worktree chosen  
  *And* each press changed its own choice  
  *And* ticket.activate was asked for those choices

## Story: Close Active Session (round 2)

### Evidence

| Source | Note |
|--------|------|
| `.sessions/chat-ui-defects/e2e/e2e-report.md` §6 B3, B4 | the close dialog said "branch none yet" for a branch open in its worktree; closing left the session folder's move uncommitted and the closed branch checked out |

#### Scenario: Commit the closed session's folder and return to main

*Given* checkout-flow is the active ticket, on its own branch, with its session folder tracked  
*When* the Person closes checkout-flow, committing and pushing  
*Then* nothing is left uncommitted  
  *And* the checkout is back on main

#### Scenario: Offer to commit a branch open in its worktree

*Given* checkout-flow is the active ticket, its branch open in its own worktree  
*When* the Person closes checkout-flow  
*Then* the close dialog offers a handoff, and to commit and push checkout-flow

## Story: Show Backlog Items In Session List

### Evidence

| Source | Note |
|--------|------|
| The person, 2026-11-25 | "Add a section to the session choices for backlog items ... A parent and child can be opened to reveal the child items" |
| The person, 2026-11-26 | on the build: "is there a possibility to use scrolling when list is too long?", then "kill the extra nested child functionality, too cluttered" |
| `harness/chat-ui/pane/hooks/chat-bar/session-dialogs-view.tsx` `SessionListView` | observed 2026-11-25: the session list holds main, the open tickets, and the field that names a new session with its folder button |
| `space/kanban/backlog_item.py` `BacklogItem.children`, `Backlog.items` | a parent keeps its children in its folder; the Backlog lists its items in the order the board keeps |

### Domain terms

- ++[backlog item](../../../space/kanban/.context/kanban-model.md#backlogitem--card)++ — an idea in the Backlog, not yet started; a parent keeps its child items with it.

#### Scenario: Show the Backlog closed when the session list opens

The person, 2026-11-25, on the first build: "it needs to be collapsed on open, it's a collapsed section that opens beside the current list, because it's spilling off the max chat height".

*Given* the [Backlog](../../../space/kanban/.context/kanban-model.md#backlog--column) holds the [backlog items](../../../space/kanban/.context/kanban-model.md#backlogitem--card) Payment retry and Checkout flow
*When* the Person opens the session list in the main chat
*Then* under the field that names a new session, a closed Backlog row says it holds 2 items
  *And* no Backlog item is shown

#### Scenario: Open the Backlog beside the session list

*Given* the session list shows the Backlog closed, holding Payment retry and Checkout flow, in that order
  *And* Checkout flow keeps the child items Address form and Card form
*When* the Person opens the Backlog
*Then* a BACKLOG box opens beside the session list, listing Payment retry, then Checkout flow
  *And* the session list stays as it was, its rows no taller
  *And* Address form and Card form are not shown, and nothing beside Checkout flow opens them

#### Scenario: Close the Backlog again each time the session list opens

*Given* the Person opened the Backlog beside the session list
*When* the Person closes the session list and opens it again
*Then* the Backlog is closed

#### Scenario: Page through a Backlog taller than the chat

*Given* the [Backlog](../../../space/kanban/.context/kanban-model.md#backlog--column) holds 12 items
  *But* the chat bar has room for 7 rows of items above its line
*When* the Person opens the Backlog
*Then* the BACKLOG box shows the first 7 items, and its heading says 1–7 of 12
*When* the Person pages down
*Then* the BACKLOG box shows items 6 to 12, and its heading says 6–12 of 12
*When* the Person pages up
*Then* the BACKLOG box shows the first 7 items again

#### Scenario: Cut a long title short

*Given* the [Backlog](../../../space/kanban/.context/kanban-model.md#backlog--column) holds the [backlog item](../../../space/kanban/.context/kanban-model.md#backlogitem--card) Chat bar shows the robots queue as clearly as a drawn card view
*When* the Person opens the Backlog
*Then* the BACKLOG box shows it as Chat bar shows the robots queu…, so the box stays inside the chat

#### Scenario: Show no Backlog section while the Backlog is empty

*Given* the [Backlog](../../../space/kanban/.context/kanban-model.md#backlog--column) holds no [backlog item](../../../space/kanban/.context/kanban-model.md#backlogitem--card)
*When* the Person opens the session list in the main chat
*Then* the list shows main, the open tickets and the new session's field, and no Backlog row

#### Scenario: Offer no Backlog in a ticket's own chat

*Given* the chat works in checkout-flow's own worktree
  *And* the [Backlog](../../../space/kanban/.context/kanban-model.md#backlog--column) holds Payment retry
*When* the Person looks for the session list
*Then* the chat bar offers no session list, so no Backlog item can be started from a ticket's chat

## Story: Start Backlog Item From Session List

### Evidence

| Source | Note |
|--------|------|
| The person, 2026-11-25 | "If a backlog ticket is started, that is identical to moving a ticket out of the backlog ... the parent or the child can be started"; 2026-11-26: a child item is no longer listed, so it starts with its parent or from the board |
| `space/kanban/app/src/kanban/ticket/root-choice-client.ts` `start` | the board's way out of the Backlog: `backlog-item.start` on the folder chosen, then activation: `ticket.activate`, and a chat started in the ticket's worktree |
| `space/kanban/backlog_item.py` `BacklogItem.start` | a parent's children start with it as story tickets that are its children; an item kept with a ticket's work brings that ticket back |
| `harness/chat-ui/pane/hooks/chat-bar/session-client.ts` `createSession`, `activateTicket` | the session list's new session opens on the folder chosen beside its name, and opens as a ticket picked from the list does |

#### Scenario: Start a Backlog item as the board moves it out of the Backlog

*Given* the session list shows the [backlog item](../../../space/kanban/.context/kanban-model.md#backlogitem--card) Payment retry
  *But* no folder is chosen beside the new session's name
*When* the Person starts Payment retry
*Then* Payment retry is started on the whole repository, as backlog-item.start answers, and its ticket payment-retry is in Discovery
  *And* payment-retry opens in its own worktree, with its chat started there, as Open Session does
  *And* the session list is closed, and Payment retry is no longer in the Backlog

#### Scenario: Start a Backlog item on the folder chosen beside the new session's name

*Given* the session list shows Payment retry
  *And* the folder app/payments is chosen beside the new session's name
*When* the Person starts Payment retry
*Then* payment-retry's session works on app/payments
  *And* no folder is chosen beside the new session's name any more

#### Scenario: Start a parent with its child items

*Given* the session list shows Checkout flow, which keeps the child items Address form and Card form
*When* the Person starts Checkout flow
*Then* the ticket checkout-flow is in Discovery, with the child tickets address-form and card-form
  *And* checkout-flow opens in its own worktree

#### Scenario: Show why a Backlog item did not start

*Given* the session list shows Payment retry
  *But* Payment retry was deleted from the Backlog on the board after the list was read
*When* the Person starts Payment retry
*Then* the failure line says Payment retry did not start, with backlog-item.start's reason
  *And* no ticket is opened, and the Backlog no longer holds Payment retry

#### Scenario: Keep a started item's ticket when it does not open

*Given* the session list shows Payment retry
  *But* ticket.activate refuses to open payment-retry
*When* the Person starts Payment retry
*Then* the ticket payment-retry stays in Discovery, started
  *And* the failure line says payment-retry did not open, with ticket.activate's reason

## Story: Debug A Failure From Chat Bar

### Evidence

| Source | Note |
|--------|------|
| `harness/chat-ui/pane/hooks/chat-bar/chat-bar-client.ts` `runDebug`, `shared/debug-command.ts` `debugCommandOf` | observed in the code, 2026-11-23 |
| `harness/chat-ui/pane/hooks/error-display/failure-client.ts` `fixFailure`, `sentToChat` | observed in the code, 2026-11-23: a slash command runs with `$.command.run`, which the host allows, where `$.prompt.submit` refused it (reported 2026-11-16) |
| `harness/chat-ui/pane/hooks/error-display/failure.test.tsx` | the plugin tests that play Fix on the prompt queue's failure |
| `space/session/debug_spec.py` | the debug session's own spec: what the command writes and asks |

#### Scenario: Put the debug command in the prompt box

*Given* checkout-flow is the active session
*When* the Person asks to debug from the chat bar
*Then* the prompt box holds /space-session-debug-session session=.sessions/checkout-flow/session.json after what it held
  *And* nothing is sent until the Person sends it

#### Scenario: Send a failure to the debug command to fix it

*Given* the failure line shows "The board did not load: connection closed" with Fix
*When* the Person asks to fix the failure
*Then* the chat runs /space-session-debug-session choice=fix with the failure and its context as details
  *And* the failure line no longer shows it

#### Scenario: Show the fix on its way so it is sent once

*Given* the failure line shows "The board did not load: connection closed" with Fix
*When* the Person asks to fix the failure
*Then* until the command is in the chat the failure line shows Sending the fix to Claude in place of Fix

#### Scenario: Say when the fix did not reach the chat

*Given* the failure line shows "The board did not load: connection closed" with Fix
  *But* the chat refuses the debug command
*When* the Person asks to fix the failure
*Then* the failure line says "The fix did not reach the chat" with the chat's reason

#### Scenario: Log the defect with a suggested fix and its status

Requested 2026-11-24, the person: "suggested fix and status include - do on release-1-1-2 branch statsus == raised, resolved, ore to come later".

*Given* the failure line shows "The queue did not change: no connected MCP tool prompt-queue.flush" with Fix
*When* the Person asks to fix the failure
*Then* the debug report and the defect's issue hold a suggested fix and the status raised

#### Scenario: Fix the defect on another branch

*Given* the defect's issue is raised
  *And* the chat release-1-1-2 works the branch release-1-2-fixes
*When* the Person chooses to fix it on release-1-2-fixes
*Then* the fix is on release-1-1-2's prompt queue, with the report, the issue and the suggested fix
  *And* the issue says the fix is queued on release-1-2-fixes, its status still raised

#### Scenario: Resolve the defect once its fix is served

*Given* the defect's fix is pushed and served on its lane
*Then* the debug report and the issue say the status resolved
  *And* the issue is closed

#### Scenario: Leave the defect to come later

*Given* the defect's issue is raised
*When* the Person chooses to fix it later
*Then* the debug report and the issue say the status to come later
  *And* the issue stays open

## Story: Push Work From Chat Bar

#### Scenario: Push a ticket's worktree part way through merging main

*Given* the ticket checkout-flow's branch is checked out in a worktree of its own
*And* a merge of main into that branch stopped on a conflict in `a.py`, which the Person has since resolved
*When* the Person pushes the session's work
*Then* the commit on checkout-flow's branch concludes the merge, with main as its second parent
*And* the branch is pushed with the merge in it
