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

*Given* checkout-flow is the active [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card)
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

*Given* the [repository](../../../../../space/kanban/.context/kanban-model.md#repo) has the folder src/billing
*When* the Person opens a ticket titled Billing report on src/billing
*Then* billing-report's [session](../../../../../space/kanban/.context/kanban-model.md#session) works in src/billing
*And* the details show its workpath as src/billing

#### Scenario: Choose a ticket's workpath

*Given* checkout-flow works on the whole [repository](../../../../../space/kanban/.context/kanban-model.md#repo)
*And* the repository has src/billing and src/visits under src
*When* the Person browses src for checkout-flow's workpath
*Then* the roots dialog lists src/billing and src/visits
*When* the Person chooses src/visits as checkout-flow's workpath
*Then* checkout-flow's workpath reads src/visits
*And* each practice's default practice root sits under src/visits

#### Scenario: Choose one practice's root and go back to its default

*Given* checkout-flow's Stories [practice](../../../../../space/kanban/.context/kanban-model.md#practiceguidance) writes under its default root
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

## Story: Activate Ticket

#### Scenario: Open a ticket in its own worktree

*Given* the git [repository](../../../../../space/kanban/.context/kanban-model.md#repo) has no branch billing-report
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

## Story: Close Active Session

#### Scenario: Close the active session from its card

*Given* checkout-flow is the active [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card), In progress in Discovery, with a chat connected
*When* the Person closes checkout-flow's session from its card
*Then* the chat is sent /space:session:close-session
*And* checkout-flow stays In progress in Discovery

#### Scenario: Complete the active ticket with its work committed

*Given* checkout-flow is open in its own worktree
*When* the Person moves checkout-flow into Complete
*Then* a dialog headed Close session Checkout flow offers commit and push, chosen
*When* the Person confirms
*Then* checkout-flow shows in Complete and is selected
*And* a toast says Checkout flow: committed, pushed · Session Checkout flow closed
*And* main is the active ticket

#### Scenario: Complete a ticket that has no branch of its own

*Given* checkout-flow is the active [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card)
*But* it has no branch of its own
*When* the Person moves checkout-flow into Complete and confirms
*Then* checkout-flow shows in Complete
*And* its folder is in .sessions/_complete/checkout-flow
*But* checkout-flow's work is not committed

## Story: Move Ticket

#### Scenario: Move a ticket on to the next column

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) ready-to-move is in Discovery's Done
*When* the Person moves ready-to-move on
*Then* ready-to-move is In progress in Specification and selected
*And* its session log ends with move Specification

#### Scenario: Drag a ticket into a stage's Done whatever its work

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) move-me is In progress in Discovery with nothing done
*When* the Person moves move-me into Implementation's Done
*Then* move-me shows in Implementation's Done and is selected

#### Scenario: Move a ticket back to the previous column

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) second-spec is In progress in Specification
*When* the Person moves second-spec back
*Then* second-spec shows in Discovery's Done

#### Scenario: Move a ticket into the Backlog with its work

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) back-to-backlog is In progress in Discovery with its story map generated
*When* the Person moves back-to-backlog into the Backlog
*Then* the Backlog shows the [backlog item](../../../../../space/kanban/.context/kanban-model.md#backlogitem--card) Back to backlog and it is selected
*And* a toast says Back to backlog moved to Backlog
*But* no stage shows back-to-backlog

#### Scenario: Close a ticket moved on past Implementation

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) almost-shipped is in Implementation's Done
*And* almost-shipped is not the active ticket
*When* the Person moves almost-shipped on into Complete
*Then* almost-shipped shows in Complete
*And* its folder is in .sessions/_complete/almost-shipped

#### Scenario: Reopen a ticket moved back out of Complete

*Given* the closed [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) shipped-work is in Complete
*When* the Person moves shipped-work back
*Then* shipped-work shows in Implementation's Done
*And* its folder is back in .sessions/shipped-work

#### Scenario: Refuse a move into a column that is not a stage

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) billing-report is In progress in Discovery
*And* billing-report is not the active ticket
*When* the Person tries to move billing-report into Complete
*Then* Complete does not take billing-report
*And* billing-report stays In progress in Discovery

## Story: Write Ticket Handoff

#### Scenario: Ask the chat to write a handoff

*Given* checkout-flow is the active [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) and a chat is connected
*When* the Person asks for a handoff on checkout-flow
*Then* the chat's prompt holds Write a handoff for ticket checkout-flow with /space-session-handoff-session.
*And* a toast says Queued for the prompt, for you to review

#### Scenario: Hold the handoff until the chat's turn ends

*Given* the connected chat is running a turn
*When* the Person asks for a handoff on checkout-flow
*Then* a toast says the fill goes in when this turn ends
*And* the prompt receives the text once the turn has ended

#### Scenario: Keep Handoff off with no chat

*Given* checkout-flow is the active [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card)
*But* no chat is connected
*When* the session board draws checkout-flow's card
*Then* Handoff is off
*And* the header says No chat connected: load the cdd-board mod in a chat to send commands

## Story: Display Latest Handoff

#### Scenario: Show the latest handoff

*Given* checkout-flow's [session](../../../../../space/kanban/.context/kanban-model.md#session) folder holds handoff-20261101T120000.md and an earlier handoff
*When* the Person selects checkout-flow
*Then* the details read Latest handoff: .sessions/checkout-flow/handoff-20261101T120000.md
*When* the Person opens the handoff
*Then* the files panel shows the handoff in a tab with its text # Handoff

#### Scenario: Say a ticket has no handoff

*Given* billing-report's [session](../../../../../space/kanban/.context/kanban-model.md#session) folder holds no handoff
*When* the Person selects billing-report
*Then* the details say No handoff yet

## Story: Restrict Actions To Active Session

#### Scenario: Lock tickets that are not the active session

*Given* Active session only is on
*And* checkout-flow is the active [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card)
*When* the session board draws billing-report's card and tiles
*Then* billing-report's Run next, Run, practice switches, Split, and Handoff are off
*And* billing-report's Run next says Activate this session to run its next step
*And* checkout-flow's actions stay on

#### Scenario: Keep information and moves open on a locked ticket

*Given* Active session only is on
*And* billing-report is not the active [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card)
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
