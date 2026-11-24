---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Close And Hand Off Ticket Sessions

### Domain terms

- ++ticket chat++ — the Claude Code chat a ticket's session ran in.

## Story: Close Active Session

#### Scenario: Close the active session from its card

*Given* checkout-flow is the active [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card), In progress in Discovery, with a chat connected
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

*Given* checkout-flow is the active [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card)
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

## Story: Protect Work When Closing Session

#### Scenario: Offer to commit a branch open in its worktree

> From `story_tests/move-work-forward-on-session-board/steer-ticket-sessions/steer-ticket-sessions.story.shared.py`, generated 2026-11-16 from the story test's code.

*Given* checkout-flow is the active ticket, its branch open in its own worktree  
*When* the Person closes checkout-flow  
*Then* the close dialog offers a handoff, and to commit and push checkout-flow

#### Scenario: Leave what the repository's own folder holds uncommitted out of the close

> Test: heavy: space/kanban/ticket_work_heavy_spec.py 'that a ticket is closed with its branch merged while the clone's own folder holds an edit nobody committed'.

> Evidence: exploratory-testing defect gizmo-17. space/kanban module-context: the repository's own folder stays on main, and a ticket's worktree's branch carries only the work.

*Given* checkout-flow is open in its own worktree, with work in it
*And* the repository's own folder holds an edit to README.md that nobody committed
*When* the Person closes checkout-flow, committing, pushing, merging, and deleting its branch and worktree
*Then* main on origin holds checkout-flow's work
*But* main on origin does not hold the edit to README.md
*And* that edit is still uncommitted in the repository's own folder

#### Scenario: Warn that deleting a worktree without a commit loses its work

> Test: heavy: space/kanban/ticket_work_heavy_spec.py 'that a ticket is closed with only its worktree deleted while that worktree holds work nobody committed'.

> Evidence: exploratory-testing question gizmo-12, answered 2026-11-23: a close does only what was picked, and warns that uncommitted work will be lost.

*Given* checkout-flow is open in its own worktree
*And* that worktree holds a change to README.md and a new file notes.txt that nobody committed
*When* the Person asks what closing checkout-flow can do
*Then* closing warns that deleting the worktree without a commit loses the work in README.md and notes.txt
*When* the Person closes checkout-flow, deleting only its worktree
*Then* nothing is committed on the checkout-flow branch
*And* nothing of checkout-flow is pushed to origin
*And* the worktree folder is gone
*And* the close's answer names README.md and notes.txt as the work that went with it

#### Scenario: Keep the ticket open when its branch does not merge into main

> Test: heavy: space/kanban/ticket_work_heavy_spec.py 'that a ticket is closed with its branch merged into a main it conflicts with'.

> Evidence: exploratory-testing defect gizmo-14. `Ticket.close` promises its branch is merged before anything moves.

*Given* checkout-flow is open in its own worktree
*And* its branch and main on origin each changed the same line
*When* the Person closes checkout-flow, committing, pushing, merging, and deleting its branch and worktree
*Then* the board says checkout-flow does not merge into main
*And* main has no merge half done
*And* checkout-flow still has its worktree
*And* checkout-flow stays In progress in Discovery

#### Scenario: Refuse to call a ticket closed while a program holds its worktree open

> Test: heavy, Windows: space/repo/worktree_heavy_spec.py 'whose folder a running program holds open'.

> Evidence: exploratory-testing defect gizmo-15. `Worktrees.remove` promises `WorktreeNotRemovedError` for a folder still there.

*Given* checkout-flow is open in its own worktree
*And* a running program works in that worktree's folder
*When* the Person closes checkout-flow, committing, pushing, and deleting its worktree
*Then* the board says the worktree could not be removed, naming its folder
*And* checkout-flow's work is committed on its branch on origin
*When* that program has ended and the Person activates checkout-flow
*Then* checkout-flow has its own worktree again

#### Scenario: Refuse to close main

> Test: unit: space/session/session_spec.py 'that is main and is closed'.

> Evidence: exploratory-testing question gizmo-11, answered 2026-11-23: session.close on main is refused as ticket.close is.

*Given* main is the active session
*When* the Person closes main's session
*Then* the close is refused, saying main is the default session and stays open
*And* main is still the active session

#### Scenario: Warn on the board before a close deletes work nobody committed

*Given* checkout-flow is open in its own worktree, which holds a change to app/checkout/order.py and a new file notes.txt that nobody committed
*When* the Person closes checkout-flow, choosing to delete its worktree
*Then* the close dialog warns that deleting the worktree without a commit loses the work in app/checkout/order.py and notes.txt
*When* the Person also chooses to commit checkout-flow
*Then* the close dialog no longer warns of lost work

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
  *But* closing offers no commit or push of main  
*When* the Person closes checkout-flow, deleting its branch  
*Then* the checkout-flow branch is gone  
  *And* checkout-flow shows in Complete

## Story: Write Ticket Handoff

#### Scenario: Ask the chat to write a handoff

*Given* checkout-flow is the active [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card) and a chat is connected
*When* the Person asks for a handoff on checkout-flow
*Then* the chat's prompt holds Write a handoff for ticket checkout-flow with /space-session-handoff-session.
*And* a toast says Queued for the prompt, for you to review

#### Scenario: Hold the handoff until the chat's turn ends

*Given* the connected chat is running a turn
*When* the Person asks for a handoff on checkout-flow
*Then* a toast says the fill goes in when this turn ends
*And* the prompt receives the text once the turn has ended

#### Scenario: Keep Handoff off with no chat

*Given* checkout-flow is the active [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card)
*But* no chat is connected
*When* the session board draws checkout-flow's card
*Then* Handoff is off
*And* the header says No chat connected: load the cdd-board mod in a chat to send commands

## Story: Display Latest Handoff

#### Scenario: Show the latest handoff

*Given* checkout-flow's [session](../../../../space/kanban/.context/kanban-model.md#session) folder holds handoff-20261101T120000.md and an earlier handoff
*When* the Person selects checkout-flow
*Then* the details read Latest handoff: .sessions/checkout-flow/handoff-20261101T120000.md
*When* the Person opens the handoff
*Then* the Files app opens on the handoff, its text # Handoff

#### Scenario: Say a ticket has no handoff

*Given* billing-report's [session](../../../../space/kanban/.context/kanban-model.md#session) folder holds no handoff
*When* the Person selects billing-report
*Then* the details say No handoff yet
