---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: See Work On Session Board

See Work On Session Board holds two sub-epics since 2026-11-24, each with its scenarios in its own folder: [Show Tickets On Board](show-tickets-on-board/show_tickets_on_board_story.test.md) and [Arrange Board And Ticket Details](arrange-board-and-ticket-details/arrange_board_and_ticket_details_story.test.md). The story left below is an older copy of Restrict Actions To Active Session, which [Activate And Move Ticket Sessions](../steer-ticket-sessions/activate-and-move-ticket-sessions/activate_and_move_ticket_sessions_story.test.md) keeps; it stays here unchanged until a person removes it.

## Story: Restrict Actions To Active Session

#### Scenario: Lock tickets that are not the active session

> From `story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-and-move-ticket-sessions/restrict-actions-to-active-session/restrict_actions_to_active_session_story.test.py`, generated 2026-11-16 from the story test's code.

*Given* Active session only is on  
  *And* checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card)  
*When* the session board draws billing-report's card and tiles  
*Then* billing-report's Run next, Run, practice switches, Split, and Handoff are off  
  *And* billing-report's Run next says Activate this session to run its next step  
  *And* checkout-flow's actions stay on

#### Scenario: Keep information and moves open on a locked ticket

> From `story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-and-move-ticket-sessions/restrict-actions-to-active-session/restrict_actions_to_active_session_story.test.py`, generated 2026-11-16 from the story test's code.

*Given* Active session only is on  
  *And* billing-report is not the active [ticket](../../../.context/kanban-model.md#ticket--card)  
*When* the Person opens billing-report's files  
*Then* the Files app opens on billing-report's files  
*When* the Person moves billing-report to Specification  
*Then* billing-report moves to Specification  
  *And* Activate stays on for billing-report

#### Scenario: Unlock every ticket

> From `story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-and-move-ticket-sessions/restrict-actions-to-active-session/restrict_actions_to_active_session_story.test.py`, generated 2026-11-16 from the story test's code.

*Given* Active session only is on  
*When* the Person turns Active session only off  
*Then* billing-report's actions are on like the active ticket's
