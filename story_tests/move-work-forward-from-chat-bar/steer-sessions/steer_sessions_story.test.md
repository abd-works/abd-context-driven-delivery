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
