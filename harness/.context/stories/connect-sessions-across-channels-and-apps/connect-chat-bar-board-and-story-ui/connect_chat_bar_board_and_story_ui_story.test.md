---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Connect Chat Bar Board And Story UI

### Domain terms

- ++format++ — what an action writes: diagram (drawio), markdown, or code (python, typescript, javascript, java, html).
- ++increment++ — a slice of the story map's stories built together.
- ++backlog ticket++ — a ticket in the board's BACKLOG column, with its own session.

> In steps: ++example++ names a row of a table below; ${field} is a column of the scenario's Examples.

## Examples

### tickets

| ticket | practices |
| --- | --- |
| ++checkout-flow++ | Stories, UX, Clean Engineering |
| ++billing-report++ | Stories, DDD |

### increments of checkout-flow's story map

| increment | stories | ticket name |
| --- | --- | --- |
| ++Increment 1: Start Ticket Work++ | Open Ticket Session, Activate Ticket, Add Backlog Item | checkout-flow story map · Increment 1: Start Ticket Work |
| ++Increment 2: Maintain Tickets++ | Move Ticket, Ticket Archive, Delete Ticket | checkout-flow story map · Increment 2: Maintain Tickets |

## Story: Open Board Side Panel From Chat Bar

### Evidence

| Source | Note |
|--------|------|
| user request, 2026-11-06 | "chat band -> board side panel" |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: The board opens beside the chat with the active ticket outlined

*Given* ++checkout-flow++ is the active ticket  
  *But* the board is not open  
*When* the Person opens the board from the chat band  
*Then* the board opens beside the chat  
  *And* ++checkout-flow++'s tile has the thick orange outline

## Story: Sync Chat Bar With Board Selection

### Evidence

| Source | Note |
|--------|------|
| artifact comments, 2026-11-06 | "and on the chat panel"; "and practices enabled for that session" |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: Every view switches to the ticket picked on the board

*Given* ++checkout-flow++ is the active ticket  
  *And* ++billing-report++'s session has Stories and DDD enabled  
*When* the Person makes ++billing-report++ the active ticket on the board  
*Then* the band, the chat panel, the story map and the Inspector all switch to ++billing-report++  
  *And* the band shows ++billing-report++'s enabled practices, Stories and DDD

#### Scenario: Switching back restores the first ticket's practices

*Given* ++billing-report++ is the active ticket  
*When* the Person makes ++checkout-flow++ the active ticket on the board  
*Then* the band shows ++checkout-flow++'s Stories, UX and Clean Engineering squares  
  *And* the chat panel shows ++checkout-flow++'s chat

## Story: Keep Chosen Formats Across Actions In A Fidelity

### Evidence

| Source | Note |
|--------|------|
| artifact comment, 2026-11-06 | "have format saved across actions in fidelity" |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario Outline: The picked formats stay picked when the action changes

*Given* ++checkout-flow++ is the active ticket  
  *And* the diagram, markdown and code formats are picked for its fidelity  
*When* the Person switches the band's action from generate to ${action}  
*Then* the diagram, markdown and code formats stay picked  
  *And* ${action} writes those formats

##### Examples

| action |
| --- |
| render |
| sketch |
| iterate |
| document |

#### Scenario: Turning a format off applies to every later action

*Given* the diagram, markdown and code formats are picked  
*When* the Person turns the code format off  
*Then* generate, render, sketch, iterate and document all write diagram and markdown only

## Story: Start Ticket Session From Increment

### Evidence

| Source | Note |
|--------|------|
| artifact comment, 2026-11-06 | "increment view of story ui → create a ticket on board on demand in backlog with proper naming reference to story map increment" |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario Outline: Creating a ticket from an increment adds a backlog ticket named after it

*Given* ++checkout-flow++'s story map shows Story UI's Increment View  
  *But* ${increment} has no ticket  
*When* the Person creates a ticket for ${increment}  
*Then* a ticket named "${ticket name}" appears in the board's BACKLOG  
  *And* it has its own session for ${stories}

##### Examples

| increment | ticket name | stories |
| --- | --- | --- |
| Increment 1: Start Ticket Work | checkout-flow story map · Increment 1: Start Ticket Work | Open Ticket Session, Activate Ticket, Add Backlog Item |
| Increment 2: Maintain Tickets | checkout-flow story map · Increment 2: Maintain Tickets | Move Ticket, Ticket Archive, Delete Ticket |

## Story: Show Increment Ticket In Story UI

### Evidence

| Source | Note |
|--------|------|
| artifact comment, 2026-11-06 | "add" on Show Increment Ticket In Story UI |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: An increment with a ticket shows it and offers no second one

*Given* ++Increment 2: Maintain Tickets++ has the ticket "checkout-flow story map · Increment 2: Maintain Tickets" in BACKLOG  
*When* the Person switches the story map to Story UI's Increment View  
*Then* ++Increment 2: Maintain Tickets++ shows its ticket in BACKLOG  
  *And* creating a ticket is disabled for it

#### Scenario: An increment without a ticket still offers one

*Given* ++Increment 2: Maintain Tickets++ has a ticket  
  *But* ++Increment 1: Start Ticket Work++ has none  
*When* the Person switches the story map to Story UI's Increment View  
*Then* ++Increment 1: Start Ticket Work++ offers Create ticket
