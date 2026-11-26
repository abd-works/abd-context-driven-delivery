---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Steer Ticket Sessions

Steer Ticket Sessions holds three sub-epics since 2026-11-24, each with its scenarios in its own folder: [Open Ticket Sessions](open-ticket-sessions/open_ticket_sessions_story.test.md), [Activate And Move Ticket Sessions](activate-and-move-ticket-sessions/activate_and_move_ticket_sessions_story.test.md) and [Close And Hand Off Ticket Sessions](close-and-hand-off-ticket-sessions/close_and_hand_off_ticket_sessions_story.test.md). The stories left below are older copies of stories that [Maintain Tickets](../maintain-tickets/maintain_tickets_story.test.md) and [Organize Ticket Hierarchy](../organize-ticket-hierarchy/organize_ticket_hierarchy_story.test.md) keep in their own files; they stay here unchanged until a person removes them.

### Domain terms

- ++ticket chat++ — the Claude Code chat a ticket's session ran in.

## Story: Add Backlog Item

#### Scenario: Add an idea to the Backlog

> From `story_tests/move-work-forward-on-session-board/steer-ticket-sessions/steer-ticket-sessions.story.shared.py`, generated 2026-11-16 from the story test's code.

*Given* the Backlog column has no backlog item titled Gift cards  
*When* the Person adds the backlog item Gift cards with the text Sell gift cards.  
*Then* the Backlog shows Gift cards with the text Sell gift cards.

#### Scenario: Keep Add off with no title

> From `story_tests/move-work-forward-on-session-board/maintain-tickets/add-backlog-item/add_backlog_item_story.test.py`, generated 2026-11-16 from the story test's code.

*Given* the new backlog item form is open  
  *But* the Person has typed no title  
*When* the Person tries to add the item  
*Then* Add stays off  
  *And* no [backlog item](../../../.context/kanban-model.md#backlogitem--card) is written

## Story: Start Backlog Item

#### Scenario: Start a backlog item in a chosen folder

> From `story_tests/move-work-forward-on-session-board/steer-ticket-sessions/steer-ticket-sessions.story.shared.py`, generated 2026-11-16 from the story test's code.

*Given* the backlog item Gift cards is in the Backlog  
  *And* the repository has the folders src/billing and src/visits  
*When* the Person starts Gift cards  
*Then* the roots dialog lists the top folders of the repository  
  *And* Gift cards is still in the Backlog  
*When* the Person chooses src/visits as its root  
*Then* the ticket gift-cards is In progress in Discovery with root src/visits

#### Scenario: Keep the idea file with the new ticket

> From `story_tests/move-work-forward-on-session-board/steer-ticket-sessions/steer-ticket-sessions.story.shared.py`, generated 2026-11-16 from the story test's code.

*Given* the backlog item Returns and refunds is the file .sessions/_backlog/returns-and-refunds.md  
*When* the Person starts Returns and refunds on the whole repository  
*Then* the ticket returns-and-refunds is In progress in Discovery  
  *And* its session folder holds returns-and-refunds.md, text and all  
  *And* its session log names the item's file  
  *But* the Backlog no longer shows Returns and refunds

#### Scenario: Bring a ticket back from the Backlog with its work

> From `story_tests/move-work-forward-on-session-board/steer-ticket-sessions/steer-ticket-sessions.story.shared.py`, generated 2026-11-16 from the story test's code.

*Given* the ticket sign-up was moved back out of Discovery and waits in the Backlog as the backlog item Sign up  
  *And* its folder .sessions/_backlog/sign-up/ keeps its session log  
*When* the Person starts Sign up  
*Then* sign-up is back on the board with its session log and session.json  
  *But* no new ticket is opened

## Story: Split Ticket Into Child Tickets

#### Scenario: Ask the chat to split a ticket into child tickets

> From `story_tests/move-work-forward-on-session-board/steer-ticket-sessions/steer-ticket-sessions.story.shared.py`, generated 2026-11-16 from the story test's code.

*Given* checkout-flow is the active ticket and a chat is connected  
*When* the chat opens a child ticket Enter card details with parent checkout-flow  
*Then* enter-card-details is In progress in Discovery  
  *And* its details read enter-card-details · story of checkout-flow

#### Scenario: Keep Split off where nothing can take the prompt

> From `story_tests/move-work-forward-on-session-board/organize-ticket-hierarchy/split-ticket-into-child-tickets/split_ticket_into_child_tickets_story.test.py`, generated 2026-11-16 from the story test's code.

*Given* checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card)  
  *But* no chat is connected  
*When* the session board draws checkout-flow's card  
*Then* Split is off

#### Scenario: Keep Split off on a closed ticket

> From `story_tests/move-work-forward-on-session-board/organize-ticket-hierarchy/split-ticket-into-child-tickets/split_ticket_into_child_tickets_story.test.py`, generated 2026-11-16 from the story test's code.

*Given* the [ticket](../../../.context/kanban-model.md#ticket--card) browse-pets is closed in Complete  
*When* the session board draws browse-pets' card  
*Then* Split is off

#### Scenario: Keep Split off on a locked ticket

> From `story_tests/move-work-forward-on-session-board/organize-ticket-hierarchy/split-ticket-into-child-tickets/split_ticket_into_child_tickets_story.test.py`, generated 2026-11-16 from the story test's code.

*Given* Active session only is on  
  *And* billing-report is not the active [ticket](../../../.context/kanban-model.md#ticket--card)  
*When* the session board draws billing-report's card  
*Then* Split is off

## Story: Archive Ticket

#### Scenario: Archive a ticket off the board

> From `story_tests/move-work-forward-on-session-board/steer-ticket-sessions/steer-ticket-sessions.story.shared.py`, generated 2026-11-16 from the story test's code.

*Given* the ticket pet-visits is In progress in Discovery with its story map generated  
*When* the Person archives pet-visits  
*Then* no column shows pet-visits  
  *And* its folder is in .sessions/_archive/pet-visits

#### Scenario: Refuse to archive a ticket the board does not have

> From `story_tests/move-work-forward-on-session-board/steer-ticket-sessions/steer-ticket-sessions.story.shared.py`, generated 2026-11-16 from the story test's code.

*Given* the board shows no ticket named no-such-ticket  
*When* the Person archives no-such-ticket  
*Then* the board says no ticket named 'no-such-ticket' on the board  
  *But* nothing is moved to .sessions/_archive
