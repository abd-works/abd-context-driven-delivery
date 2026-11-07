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
| `harness/.context/story-map-v2.md` | Requested 2026-11-06: the chat bar shows the active session's latest handoff, as the Session Board does |
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
| `harness/chat-ui/pane/test/move-work-forward-from-chat-bar/steer-sessions/close-active-session/close_active_session_story.test.ts` | the story test that plays these scenarios |

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
