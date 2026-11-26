---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Open Ticket Sessions

### Domain terms

- ++ticket chat++ — the Claude Code chat a ticket's session ran in.

## Story: Open Ticket Session

#### Scenario: Open a new ticket

*Given* checkout-flow is the active [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card)
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

*Given* the [repository](../../../../space/kanban/.context/kanban-model.md#repo) has the folder src/billing
*When* the Person opens a ticket titled Billing report on src/billing
*Then* billing-report's [session](../../../../space/kanban/.context/kanban-model.md#session) works in src/billing
*And* the details show its workpath as src/billing

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

## Story: Choose Ticket Workpath And Roots

#### Scenario: Choose a ticket's workpath

*Given* checkout-flow works on the whole [repository](../../../../space/kanban/.context/kanban-model.md#repo)
*And* the repository has src/billing and src/visits under src
*When* the Person browses src for checkout-flow's workpath
*Then* the roots dialog lists src/billing and src/visits
*When* the Person chooses src/visits as checkout-flow's workpath
*Then* checkout-flow's workpath reads src/visits
*And* each practice's default practice root sits under src/visits

#### Scenario: Choose one practice's root and go back to its default

*Given* checkout-flow's Stories [practice](../../../../space/kanban/.context/kanban-model.md#practiceguidance) writes under its default root
*When* the Person chooses src/billing for checkout-flow's Stories root
*Then* the Stories root reads src/billing, chosen by the Person
*And* every other practice stays on its default root
*When* the Person puts Stories back on its default root
*Then* the Stories root is the default again

#### Scenario: Choose a ticket's root

> From `story_tests/move-work-forward-on-session-board/steer-ticket-sessions/steer-ticket-sessions.story.shared.py`, generated 2026-11-16 from the story test's code.

*Given* checkout-flow works on the whole repository  
  *And* the repository has src/billing and src/visits under src  
*When* the Person browses src for checkout-flow's root  
*Then* the roots dialog lists src/billing and src/visits  
*When* the Person chooses src/visits as checkout-flow's root  
*Then* checkout-flow's root reads src/visits  
  *And* each practice's default root sits under src/visits

## Story: Refuse Unusable Ticket Title

#### Scenario: Refuse a title that gives a ticket no name

> Test: steer-ticket-sessions.story.shared.py, replayed by the domain spec.

> Evidence: exploratory-testing defect gizmo-04. A ticket's name is its title's letters a to z and digits, joined by hyphens (`Name.title_slug`); the page already keeps Add off with no title.

*Given* the [board](../../../../space/kanban/.context/kanban-model.md#board) shows checkout-flow
*When* the Person opens a new ticket whose title is empty, or 日本語
*Then* the board says the title gives no name, naming the title
*And* no session file is written in .sessions itself

#### Scenario: Refuse a title whose name a ticket already has

> Test: steer-ticket-sessions.story.shared.py, replayed by the domain spec.

> Evidence: exploratory-testing defect gizmo-05. The second ticket was answered as made while the first one's title was written over.

*Given* the [ticket](../../../../space/kanban/.context/kanban-model.md#ticket--card) pet-visits is titled Pet visits
*When* the Person opens a new ticket titled PET VISITS
*Then* the board says a ticket named pet-visits already exists
*And* pet-visits is still titled Pet visits
*When* the Person opens a new ticket titled main
*Then* the board says a ticket named main already exists

#### Scenario: Refuse a title too long for a name

> Test: steer-ticket-sessions.story.shared.py, replayed by the domain spec.

> Evidence: exploratory-testing defect gizmo-06. Evidence gap: no source gives the limit; 64 characters is `NAME_LENGTH_LIMIT`, awaiting the person's decision.

*Given* the [board](../../../../space/kanban/.context/kanban-model.md#board) shows checkout-flow
*When* the Person opens a new ticket whose title makes a name longer than 64 characters
*Then* the board says the title makes too long a name, naming the limit
*And* no session folder is made for it

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
