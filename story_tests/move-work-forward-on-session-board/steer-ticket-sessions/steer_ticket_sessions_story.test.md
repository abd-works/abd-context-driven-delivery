---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Steer Ticket Sessions

### Domain terms

- ++ticket chat++ — the Claude Code chat a ticket's session ran in.

## Story: Open Ticket Session

#### Scenario: Open a new ticket

*Given* checkout-flow is the active [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card)
*When* the Person opens a new ticket titled Pet visits
*Then* pet-visits is In progress in Discovery, titled Pet visits
*And* its next step is Generate on stories-story-map
*And* checkout-flow is still the active ticket

#### Scenario: Ask a chat to open a ticket

*Given* a chat is connected to the session board
*When* the Person asks for a new ticket from the board's header
*Then* the chat's prompt holds Open a new ticket with ticket.create, titled: for the Person to finish

#### Scenario: Keep + Ticket off with no chat

*Given* no chat is connected to the session board
*When* the session board draws its header
*Then* + Ticket is off

#### Scenario: Open a ticket on a folder of the repository

*Given* the [repository](../../../space/kanban/.context/kanban-model.md#repo) has the folder src/billing
*When* the Person opens a ticket titled Billing report on src/billing
*Then* billing-report's [session](../../../space/kanban/.context/kanban-model.md#session) works in src/billing
*And* the details show its workpath as src/billing

#### Scenario: Choose a ticket's workpath

*Given* checkout-flow works on the whole [repository](../../../space/kanban/.context/kanban-model.md#repo)
*And* the repository has src/billing and src/visits under src
*When* the Person browses src for checkout-flow's workpath
*Then* the roots dialog lists src/billing and src/visits
*When* the Person chooses src/visits as checkout-flow's workpath
*Then* checkout-flow's workpath reads src/visits
*And* each practice's default practice root sits under src/visits

#### Scenario: Choose one practice's root and go back to its default

*Given* checkout-flow's Stories [practice](../../../space/kanban/.context/kanban-model.md#practiceguidance) writes under its default root
*When* the Person chooses src/billing for checkout-flow's Stories root
*Then* the Stories root reads src/billing, chosen by the Person
*And* every other practice stays on its default root
*When* the Person puts Stories back on its default root
*Then* the Stories root is the default again

#### Scenario: A press on a card only selects it

*Given* checkout-flow has no worktree and no chat
*When* the Person presses checkout-flow's card
*Then* checkout-flow is selected
*But* no worktree is created and no chat is opened; its card's chat button opens them

#### Scenario: Ask for a chat rather than send to an unrelated one

*Given* no chat works on checkout-flow and none is picked
*When* the Person writes checkout-flow's handoff from its card
*Then* nothing is sent
*And* a toast asks to open checkout-flow's chat or pick one in the chat list

#### Scenario: Choose a ticket's root

> From `story_tests/move-work-forward-on-session-board/steer-ticket-sessions/steer-ticket-sessions.story.shared.py`, generated 2026-11-16 from the story test's code.

*Given* checkout-flow works on the whole repository  
  *And* the repository has src/billing and src/visits under src  
*When* the Person browses src for checkout-flow's root  
*Then* the roots dialog lists src/billing and src/visits  
*When* the Person chooses src/visits as checkout-flow's root  
*Then* checkout-flow's root reads src/visits  
  *And* each practice's default root sits under src/visits

#### Scenario: Refuse a title that gives a ticket no name

> Evidence: exploratory-testing defect gizmo-04. A ticket's name is its title's letters a to z and digits, joined by hyphens (`Name.title_slug`); the page already keeps Add off with no title.

*Given* the [board](../../../space/kanban/.context/kanban-model.md#board) shows checkout-flow
*When* the Person opens a new ticket whose title is empty, or 日本語
*Then* the board says the title gives no name, naming the title
*And* no session file is written in .sessions itself

#### Scenario: Refuse a title whose name a ticket already has

> Evidence: exploratory-testing defect gizmo-05. The second ticket was answered as made while the first one's title was written over.

*Given* the [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) pet-visits is titled Pet visits
*When* the Person opens a new ticket titled PET VISITS
*Then* the board says a ticket named pet-visits already exists
*And* pet-visits is still titled Pet visits
*When* the Person opens a new ticket titled main
*Then* the board says a ticket named main already exists

#### Scenario: Refuse a title too long for a name

> Evidence: exploratory-testing defect gizmo-06. Evidence gap: no source gives the limit; 64 characters is `NAME_LENGTH_LIMIT`, awaiting the person's decision.

*Given* the [board](../../../space/kanban/.context/kanban-model.md#board) shows checkout-flow
*When* the Person opens a new ticket whose title makes a name longer than 64 characters
*Then* the board says the title makes too long a name, naming the limit
*And* no session folder is made for it

## Story: Activate Ticket

#### Scenario: Open a ticket in its own worktree

*Given* the git [repository](../../../space/kanban/.context/kanban-model.md#repo) has no branch billing-report
*When* the Person activates billing-report
*Then* billing-report has its own worktree, on the branch billing-report
*And* the repository's own folder stays on main
*And* main is still the session of the chat that activated it

#### Scenario: Save the session folders on main before opening

*Given* billing-report's session folder is not yet committed
*When* the Person activates billing-report
*Then* main on origin holds billing-report's session folder

#### Scenario: Open a ticket again in the worktree it has

*Given* billing-report is open in its own worktree
*When* the Person activates billing-report again
*Then* billing-report keeps that worktree

#### Scenario: Work on the ticket from a chat in its worktree

*Given* billing-report is open in its own worktree
*When* a chat in that worktree asks which session it works on
*Then* the answer is billing-report

#### Scenario: Start the ticket's new chat on the ticket's session

*Given* billing-report is open in its own worktree and no chat works on it
*When* the main chat starts a new chat for billing-report in that worktree
*Then* the new chat's first step is to switch to the session billing-report
*And* its chat bar shows billing-report, not main

#### Scenario: Switching a chat in a ticket's worktree always opens that ticket's session

*Given* billing-report is open in its own worktree
*When* a chat in that worktree switches session, naming no session, main, or another ticket
*Then* the session it opens is billing-report
*And* when it named another session, it is told that its worktree belongs to billing-report

#### Scenario: Find a branch and worktree made outside CDD

*Given* checkout-flow's work is on claude/checkout-flow-cef4bc, open in its own worktree
*But* checkout-flow's session records no branch or worktree
*When* the Person activates checkout-flow
*Then* checkout-flow opens in that worktree, creating nothing
*And* checkout-flow's session records claude/checkout-flow-cef4bc and its worktree

#### Scenario: Correct a branch the session records wrongly

*Given* checkout-flow's work is on claude/checkout-flow-cef4bc, open in its own worktree
*But* checkout-flow's session records a branch the repository no longer has
*When* the Person activates checkout-flow
*Then* checkout-flow's session records claude/checkout-flow-cef4bc and its worktree

#### Scenario: Say which branches could be the session's rather than guess

*Given* the repository has the branches claude/checkout-flow-cef4bc and claude/checkout-flow-9a1b2c
*When* the Person activates checkout-flow
*Then* the Person is told both branches could be checkout-flow's
*And* checkout-flow's session records no branch

#### Scenario: Leave a branch named as another ticket to that ticket

*Given* checkout-flow-retry is a ticket whose work is on the branch checkout-flow-retry
*When* the Person activates checkout-flow
*Then* checkout-flow's session records its own branch checkout-flow

#### Scenario: Open a ticket again after its worktree folder was deleted

> Evidence: exploratory-testing defect gizmo-01. space/kanban module-context: a ticket's own worktree is the only way it opens.

*Given* billing-report is open in its own worktree
*But* a person deleted that worktree's folder outside CDD
*When* the Person activates billing-report
*Then* billing-report has its own worktree again, on the branch billing-report

#### Scenario: Give tickets whose names start alike their own worktrees

> Evidence: exploratory-testing defect gizmo-03. A worktree folder is named for the branch's first 24 characters (`Worktrees.sibling_folder`).

*Given* customer-order-history-export-monthly is open in its own worktree
*When* the Person activates customer-order-history-export-weekly
*Then* customer-order-history-export-weekly has a worktree of its own, in another folder

#### Scenario: Refuse to open a ticket onto a folder that is not its checkout

> Evidence: exploratory-testing defect gizmo-07.

*Given* billing-report's worktree folder is still there, left on no branch
*And* the git [repository](../../../space/kanban/.context/kanban-model.md#repo) no longer has the branch billing-report
*When* the Person activates billing-report
*Then* the board says billing-report cannot open in a worktree, naming that folder
*And* the folder's files are as they were

#### Scenario: Answer every chat that activates a ticket at the same moment

> Evidence: exploratory-testing defect gizmo-08, for chats on one cdd server.

*Given* billing-report has no worktree yet
*When* three chats activate billing-report at the same moment
*Then* each is answered billing-report, in the one worktree

## Story: Close Active Session

#### Scenario: Close the active session from its card

*Given* checkout-flow is the active [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card), In progress in Discovery, with a chat connected
*When* the Person closes checkout-flow's session from its card
*Then* the chat is sent /space:session:close-session
*And* checkout-flow stays In progress in Discovery

#### Scenario: Complete the active ticket with its work committed

*Given* checkout-flow is open in its own worktree
*When* the Person moves checkout-flow into Complete
*Then* a dialog headed Close session Checkout flow offers commit and push, none chosen
*When* the Person confirms
*Then* checkout-flow shows in Complete and is selected
*And* a toast says Checkout flow: committed, pushed · Session Checkout flow closed
*And* main is the active ticket

#### Scenario: Complete a ticket that has no branch of its own

*Given* checkout-flow is the active [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card)
*But* it has no branch of its own
*When* the Person moves checkout-flow into Complete and confirms
*Then* checkout-flow shows in Complete
*And* its folder is in .sessions/_complete/checkout-flow
*But* checkout-flow's work is not committed

#### Scenario: Commit the closed session's folder and return to main

> From `story_tests/move-work-forward-on-session-board/steer-ticket-sessions/steer-ticket-sessions.story.shared.py`, generated 2026-11-16 from the story test's code.

*Given* checkout-flow is open in its own worktree  
*When* the Person closes checkout-flow, committing and pushing  
*Then* nothing is left uncommitted  
  *And* the checkout is back on main

#### Scenario: Offer to commit a branch open in its worktree

> From `story_tests/move-work-forward-on-session-board/steer-ticket-sessions/steer-ticket-sessions.story.shared.py`, generated 2026-11-16 from the story test's code.

*Given* checkout-flow is the active ticket, its branch open in its own worktree  
*When* the Person closes checkout-flow  
*Then* the close dialog offers a handoff, and to commit and push checkout-flow

#### Scenario: Close a session whose work is on main

> From `story_tests/move-work-forward-on-session-board/steer-ticket-sessions/steer-ticket-sessions.story.shared.py`, generated 2026-11-16 from the story test's code.

*Given* checkout-flow is the active ticket, its work on main  
*When* the Person closes checkout-flow  
*Then* the close dialog offers to commit and push main  
*When* the Person confirms  
*Then* main on origin holds the commit checkout-flow: leave session  
  *And* the checkout is still on main  
  *And* checkout-flow shows in Complete

#### Scenario: Write a handoff for the session being closed

> From `story_tests/move-work-forward-on-session-board/steer-ticket-sessions/steer-ticket-sessions.story.shared.py`, generated 2026-11-16 from the story test's code.

*Given* checkout-flow is the active ticket, its story map held on violations  
*When* the Person closes checkout-flow with Create handoff chosen  
*Then* checkout-flow's folder in .sessions/_complete holds a handoff  
  *And* the handoff names stories-story-map as what comes next

#### Scenario: Return to main whatever is chosen

> From `story_tests/move-work-forward-on-session-board/steer-ticket-sessions/steer-ticket-sessions.story.shared.py`, generated 2026-11-16 from the story test's code.

*Given* checkout-flow is open in its own worktree  
*When* the Person closes checkout-flow with nothing chosen  
*Then* the checkout is back on main  
  *And* main is the active ticket

#### Scenario: Leave what the repository's own folder holds uncommitted out of the close

> Evidence: exploratory-testing defect gizmo-17. space/kanban module-context: the repository's own folder stays on main, and a ticket's worktree's branch carries only the work.

*Given* checkout-flow is open in its own worktree, with work in it
*And* the repository's own folder holds an edit to README.md that nobody committed
*When* the Person closes checkout-flow, committing, pushing, merging, and deleting its branch and worktree
*Then* main on origin holds checkout-flow's work
*But* main on origin does not hold the edit to README.md
*And* that edit is still uncommitted in the repository's own folder

#### Scenario: Keep the ticket open when its branch does not merge into main

> Evidence: exploratory-testing defect gizmo-14. `Ticket.close` promises its branch is merged before anything moves.

*Given* checkout-flow is open in its own worktree
*And* its branch and main on origin each changed the same line
*When* the Person closes checkout-flow, committing, pushing, merging, and deleting its branch and worktree
*Then* the board says checkout-flow does not merge into main
*And* main has no merge half done
*And* checkout-flow still has its worktree
*And* checkout-flow stays In progress in Discovery

#### Scenario: Refuse to call a ticket closed while a program holds its worktree open

> Evidence: exploratory-testing defect gizmo-15. `Worktrees.remove` promises `WorktreeNotRemovedError` for a folder still there.

*Given* checkout-flow is open in its own worktree
*And* a running program works in that worktree's folder
*When* the Person closes checkout-flow, deleting its worktree
*Then* the board says the worktree could not be removed, naming its folder
*And* checkout-flow's work is committed on its branch on origin
*When* that program has ended and the Person activates checkout-flow
*Then* checkout-flow has its own worktree again

## Story: Move Ticket

#### Scenario: Move a ticket on to the next column

*Given* the [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) ready-to-move is in Discovery's Done
*When* the Person moves ready-to-move on
*Then* ready-to-move is In progress in Specification and selected
*And* its session log ends with move Specification

#### Scenario: Drag a ticket into a stage's Done whatever its work

*Given* the [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) move-me is In progress in Discovery with nothing done
*When* the Person moves move-me into Implementation's Done
*Then* move-me shows in Implementation's Done and is selected

#### Scenario: Move a ticket back to the previous column

*Given* the [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) second-spec is In progress in Specification
*When* the Person moves second-spec back
*Then* second-spec shows in Discovery's Done

#### Scenario: Move a ticket into the Backlog with its work

*Given* the [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) back-to-backlog is In progress in Discovery with its story map generated
*When* the Person moves back-to-backlog into the Backlog
*Then* the Backlog shows the [backlog item](../../../space/kanban/.context/kanban-model.md#backlogitem--card) Back to backlog and it is selected
*And* a toast says Back to backlog moved to Backlog
*But* no stage shows back-to-backlog

#### Scenario: Close a ticket moved on past Implementation

*Given* the [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) almost-shipped is in Implementation's Done
*And* almost-shipped is not the active ticket
*When* the Person moves almost-shipped on into Complete
*Then* almost-shipped shows in Complete
*And* its folder is in .sessions/_complete/almost-shipped

#### Scenario: Reopen a ticket moved back out of Complete

*Given* the closed [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) shipped-work is in Complete
*When* the Person moves shipped-work back
*Then* shipped-work shows in Implementation's Done
*And* its folder is back in .sessions/shipped-work

#### Scenario: Refuse a move into a column that is not a stage

*Given* the [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) billing-report is In progress in Discovery
*And* billing-report is not the active ticket
*When* the Person tries to move billing-report into Complete
*Then* Complete does not take billing-report
*And* billing-report stays In progress in Discovery

## Story: Write Ticket Handoff

#### Scenario: Ask the chat to write a handoff

*Given* checkout-flow is the active [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) and a chat is connected
*When* the Person asks for a handoff on checkout-flow
*Then* the chat's prompt holds Write a handoff for ticket checkout-flow with /space-session-handoff-session.
*And* a toast says Queued for the prompt, for you to review

#### Scenario: Hold the handoff until the chat's turn ends

*Given* the connected chat is running a turn
*When* the Person asks for a handoff on checkout-flow
*Then* a toast says the fill goes in when this turn ends
*And* the prompt receives the text once the turn has ended

#### Scenario: Keep Handoff off with no chat

*Given* checkout-flow is the active [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card)
*But* no chat is connected
*When* the session board draws checkout-flow's card
*Then* Handoff is off
*And* the header says No chat connected: load the cdd-board mod in a chat to send commands

## Story: Display Latest Handoff

#### Scenario: Show the latest handoff

*Given* checkout-flow's [session](../../../space/kanban/.context/kanban-model.md#session) folder holds handoff-20261101T120000.md and an earlier handoff
*When* the Person selects checkout-flow
*Then* the details read Latest handoff: .sessions/checkout-flow/handoff-20261101T120000.md
*When* the Person opens the handoff
*Then* the files panel shows the handoff in a tab with its text # Handoff

#### Scenario: Say a ticket has no handoff

*Given* billing-report's [session](../../../space/kanban/.context/kanban-model.md#session) folder holds no handoff
*When* the Person selects billing-report
*Then* the details say No handoff yet

## Story: Restrict Actions To Active Session

#### Scenario: Lock tickets that are not the active session

*Given* Active session only is on
*And* checkout-flow is the active [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card)
*When* the session board draws billing-report's card and tiles
*Then* billing-report's Run next, Run, practice switches, Split, and Handoff are off
*And* billing-report's Run next says Activate this session to run its next step
*And* checkout-flow's actions stay on

#### Scenario: Keep information and moves open on a locked ticket

*Given* Active session only is on
*And* billing-report is not the active [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card)
*When* the Person opens billing-report's files
*Then* the files panel lists billing-report's files
*When* the Person moves billing-report to Specification
*Then* billing-report moves to Specification
*And* Activate stays on for billing-report

#### Scenario: Unlock every ticket

*Given* Active session only is on
*When* the Person turns Active session only off
*Then* billing-report's actions are on like the active ticket's

## Story: Open Ticket Chat On Session Open

### Evidence

| Source | Note |
|--------|------|
| `.sessions/_backlog/suggest-the-next-step.md` | "open associated chat on session open / manually" |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: Making a ticket active opens its chat

*Given* checkout-flow is the active ticket  
  *And* billing-report has a ticket chat  
*When* the Person makes billing-report the active ticket on the board  
*Then* billing-report's chat opens in the chat panel with the session  
  *And* the chat panel shows billing-report's last messages

## Story: Add Backlog Item

#### Scenario: Add an idea to the Backlog

> From `story_tests/move-work-forward-on-session-board/steer-ticket-sessions/steer-ticket-sessions.story.shared.py`, generated 2026-11-16 from the story test's code.

*Given* the Backlog column has no backlog item titled Gift cards  
*When* the Person adds the backlog item Gift cards with the text Sell gift cards.  
*Then* the Backlog shows Gift cards with the text Sell gift cards.

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

#### Scenario: Keep Add off with no title

> From `story_tests/move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py`, generated 2026-11-16 from the story test's code.

*Given* the new backlog item form is open  
  *But* the Person has typed no title  
*When* the Person tries to add the item  
*Then* Add stays off  
  *And* no [backlog item](../../../.context/kanban-model.md#backlogitem--card) is written

## Story: Delete Ticket Branch

#### Scenario: Delete the branch on closing without merging it

> From `story_tests/move-work-forward-on-session-board/steer-ticket-sessions/steer-ticket-sessions.story.shared.py`, generated 2026-11-16 from the story test's code.

*Given* checkout-flow is open in its own worktree, with work in it  
*When* the Person closes checkout-flow, committing, pushing, and deleting its branch  
*Then* the checkout-flow branch is gone, here and on origin  
  *But* main on origin does not hold checkout-flow's work  
  *And* checkout-flow shows in Complete

#### Scenario: Delete the branch and the worktree that has it

> From `story_tests/move-work-forward-on-session-board/steer-ticket-sessions/steer-ticket-sessions.story.shared.py`, generated 2026-11-16 from the story test's code.

*Given* checkout-flow is open in its own worktree  
*When* the Person closes checkout-flow, deleting its branch  
*Then* the worktree folder is gone  
  *And* the checkout-flow branch is gone  
  *And* checkout-flow shows in Complete

#### Scenario: Delete a branch checked out nowhere

> From `story_tests/move-work-forward-on-session-board/steer-ticket-sessions/steer-ticket-sessions.story.shared.py`, generated 2026-11-16 from the story test's code.

*Given* checkout-flow has a branch  
  *But* that branch is not checked out  
*When* the Person asks what closing checkout-flow can do  
*Then* closing offers to delete checkout-flow's branch  
*When* the Person closes checkout-flow, deleting its branch  
*Then* the checkout-flow branch is gone  
  *And* checkout-flow shows in Complete

## Story: Split Ticket Into Child Tickets

#### Scenario: Ask the chat to split a ticket into child tickets

> From `story_tests/move-work-forward-on-session-board/steer-ticket-sessions/steer-ticket-sessions.story.shared.py`, generated 2026-11-16 from the story test's code.

*Given* checkout-flow is the active ticket and a chat is connected  
*When* the chat opens a child ticket Enter card details with parent checkout-flow  
*Then* enter-card-details is In progress in Discovery  
  *And* its details read enter-card-details · story of checkout-flow

#### Scenario: Keep Split off where nothing can take the prompt

> From `story_tests/move-work-forward-on-session-board/steer-ticket-sessions/split-ticket-into-child-tickets/split_ticket_into_child_tickets_story.test.py`, generated 2026-11-16 from the story test's code.

*Given* checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card)  
  *But* no chat is connected  
*When* the session board draws checkout-flow's card  
*Then* Split is off

#### Scenario: Keep Split off on a closed ticket

> From `story_tests/move-work-forward-on-session-board/steer-ticket-sessions/split-ticket-into-child-tickets/split_ticket_into_child_tickets_story.test.py`, generated 2026-11-16 from the story test's code.

*Given* the [ticket](../../../.context/kanban-model.md#ticket--card) browse-pets is closed in Complete  
*When* the session board draws browse-pets' card  
*Then* Split is off

#### Scenario: Keep Split off on a locked ticket

> From `story_tests/move-work-forward-on-session-board/steer-ticket-sessions/split-ticket-into-child-tickets/split_ticket_into_child_tickets_story.test.py`, generated 2026-11-16 from the story test's code.

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
