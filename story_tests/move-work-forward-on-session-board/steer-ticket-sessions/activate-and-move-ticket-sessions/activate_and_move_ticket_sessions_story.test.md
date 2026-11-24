---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Activate And Move Ticket Sessions

### Domain terms

- ++ticket chat++ — the Claude Code chat a ticket's session ran in.

## Story: Activate Ticket

#### Scenario: Open a ticket in its own worktree

*Given* the git [repository](../../../../space/kanban/.context/kanban-model.md#repo) has no branch billing-report
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

#### Scenario: Open a ticket again after its worktree folder was deleted

> Test: heavy: space/repo/worktree_heavy_spec.py 'whose folder was deleted outside CDD'; unit: space/repo/worktree_spec.py.

> Evidence: exploratory-testing defect gizmo-01. space/kanban module-context: a ticket's own worktree is the only way it opens.

*Given* billing-report is open in its own worktree
*But* that worktree's folder is no longer on disk
*When* the Person activates billing-report
*Then* billing-report has its own worktree again, on the branch billing-report

#### Scenario: Reopen a closed ticket by activating it

> Test: heavy: space/kanban/ticket_work_heavy_spec.py 'that a closed ticket is activated'.

> Evidence: exploratory-testing question gizmo-02, answered 2026-11-23: activating a closed ticket reopens it, as moving it back out of Complete does.

*Given* the closed [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card) billing-report is in Complete, its worktree deleted and its branch kept
*When* the Person activates billing-report
*Then* billing-report has its own worktree again, on the branch billing-report
*And* its folder is back in .sessions/billing-report
*And* billing-report is back on the stage it was closed from
*And* a chat in its worktree works on billing-report's session

#### Scenario: Give tickets whose names start alike their own worktrees

> Test: heavy: space/repo/worktree_heavy_spec.py 'with another branch whose name starts with the same 24 characters open in its worktree'; unit: space/repo/worktree_spec.py.

> Evidence: exploratory-testing defect gizmo-03. A worktree folder is named for the branch's first 24 characters (`Worktrees.sibling_folder`).

*Given* customer-order-history-export-monthly is open in its own worktree
*When* the Person activates customer-order-history-export-weekly
*Then* customer-order-history-export-weekly has a worktree of its own, in another folder

#### Scenario: Answer every chat that activates a ticket at the same moment

> Test: heavy: space/repo/worktree_heavy_spec.py 'that two callers open for one branch at the same moment'.

> Evidence: exploratory-testing defect gizmo-08, for chats on one cdd server.

*Given* billing-report has no worktree yet
*When* three chats activate billing-report at the same moment
*Then* each is answered billing-report, in the one worktree

## Story: Find Ticket Branch And Worktree

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

#### Scenario: Refuse to open a ticket onto a folder that is not its checkout

> Test: heavy: space/kanban/ticket_work_heavy_spec.py 'that a ticket is activated while a folder left on no branch is where its worktree goes'.

> Evidence: exploratory-testing defect gizmo-07.

*Given* billing-report's worktree folder is still there, left on no branch
*And* the git [repository](../../../../space/kanban/.context/kanban-model.md#repo) no longer has the branch billing-report
*When* the Person activates billing-report
*Then* the board says billing-report cannot open in a worktree, naming that folder
*And* the folder's files are as they were

## Story: Switch Session

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

#### Scenario: Refuse to switch a chat to a session nobody has

> Test: unit: space/session/current_session_spec.py 'that a chat switches to a name no session has'.

> Evidence: exploratory-testing question gizmo-10, answered 2026-11-23: a switch to an unknown name is refused unless the person asked for a new session.

*Given* the repository has the sessions main and billing-report
*When* a chat switches to billng-report
*Then* the switch is refused, naming main and billing-report as the sessions there are
*And* no session folder or card is made for billng-report
*And* the chat keeps the session it had open
*When* the chat switches to billng-report, asking for a new session
*Then* billng-report is made and is the chat's open session

#### Scenario: Make a session asked for by a name nobody has

> Test: unit: space/session/current_session_spec.py 'that asks for it to be made'.

> Evidence: `OpenSessions.switch` (space/session/open_sessions.py): with create, a name no session has is made by `Sessions.create`, which writes its session.json, and opened for the chat; the board shows every work session as a ticket (Display Ticket Card).

*Given* the [repository](../../../../space/kanban/.context/kanban-model.md#repo) has the [sessions](../../../../space/kanban/.context/kanban-model.md#session) main and billing-report
*When* a chat switches to pet-visits, asking for a new session (sessions.switch name=pet-visits create=true)
*Then* .sessions/pet-visits holds pet-visits' session.json
*And* the board shows pet-visits as a [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card)
*And* pet-visits is the chat's open session

## Story: Restrict Actions To Active Session

#### Scenario: Lock tickets that are not the active session

*Given* Active session only is on
*And* checkout-flow is the active [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card)
*When* the session board draws billing-report's card and tiles
*Then* billing-report's Run next, Run, practice switches, Split, and Handoff are off
*And* billing-report's Run next says Activate this session to run its next step
*And* checkout-flow's actions stay on

#### Scenario: Keep information and moves open on a locked ticket

*Given* Active session only is on
*And* billing-report is not the active [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card)
*When* the Person opens billing-report's files
*Then* the Files app opens on billing-report's files
*When* the Person moves billing-report to Specification
*Then* billing-report moves to Specification
*And* Activate stays on for billing-report

#### Scenario: Unlock every ticket

*Given* Active session only is on
*When* the Person turns Active session only off
*Then* billing-report's actions are on like the active ticket's

## Story: Move Ticket

#### Scenario: Move a ticket on to the next column

*Given* the [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card) ready-to-move is in Discovery's Done
*When* the Person moves ready-to-move on
*Then* ready-to-move is In progress in Specification and selected
*And* its session log ends with move Specification

#### Scenario: Drag a ticket into a stage's Done whatever its work

*Given* the [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card) move-me is In progress in Discovery with nothing done
*When* the Person moves move-me into Implementation's Done
*Then* move-me shows in Implementation's Done and is selected

#### Scenario: Move a ticket back to the previous column

*Given* the [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card) second-spec is In progress in Specification
*When* the Person moves second-spec back
*Then* second-spec shows in Discovery's Done

#### Scenario: Move a ticket into the Backlog with its work

*Given* the [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card) back-to-backlog is In progress in Discovery with its story map generated
*When* the Person moves back-to-backlog into the Backlog
*Then* the Backlog shows the [backlog item](../../../../space/kanban/.context/kanban-model.md#backlogitem--card) Back to backlog and it is selected
*And* a toast says Back to backlog moved to Backlog
*But* no stage shows back-to-backlog

#### Scenario: Close a ticket moved on past Implementation

*Given* the [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card) almost-shipped is in Implementation's Done
*And* almost-shipped is not the active ticket
*When* the Person moves almost-shipped on into Complete
*Then* almost-shipped shows in Complete
*And* its folder is in .sessions/_complete/almost-shipped

#### Scenario: Reopen a ticket moved back out of Complete

*Given* the closed [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card) shipped-work is in Complete
*When* the Person moves shipped-work back
*Then* shipped-work shows in Implementation's Done
*And* its folder is back in .sessions/shipped-work

#### Scenario: Refuse a move into a column that is not a stage

*Given* the [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card) billing-report is In progress in Discovery
*And* billing-report is not the active ticket
*When* the Person tries to move billing-report into Complete
*Then* Complete does not take billing-report
*And* billing-report stays In progress in Discovery
