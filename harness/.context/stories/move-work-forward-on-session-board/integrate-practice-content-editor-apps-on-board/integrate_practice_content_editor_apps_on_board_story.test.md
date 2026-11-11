---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Integrate Practice Content Editor Apps On Board

### Domain terms

- ++ticket++ — a card on the CDD Kanban with its own session; the active ticket is the one every view shows.
- ++session++ — the ticket's folder of work, with the practices enabled for it.
- ++practice++ — a lens enabled on a session: Stories, DDD, UX, Clean Engineering or BDD.
- ++story map++ — the session's epics, sub-epics and stories, shown by the Story UI app.
- ++knowledge graph++ — the practice trees the Graph app loads from a session's folders.

> In steps: ++example++ names a row of a table below; {field} is a column of the scenario's Examples.

## Examples

### tickets

| ticket | stage | practices | story map epic |
| --- | --- | --- | --- |
| ++checkout-flow++ | Implementation | Stories, UX, Clean Engineering | Move Work Forward On Session Board |
| ++billing-report++ | Discovery | Stories, DDD | Report Billing |
| ++search-orders++ | Backlog | none: no session yet | none |

## Story: Open Story UI On Ticket Scope

### Evidence

| Source | Note |
|--------|------|
| `harness/.context/stories/story-map.md` | Move Work Forward On Session Board > Integrate Practice Content Editor Apps On Board > Person --> Open Story UI On Ticket Scope |
| `harness/.context/stories/thin-slice.md` | increment 2 |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: The story map shows the chosen ticket's epics and stories

*Given* ++checkout-flow++ is the active ticket  
  *And* ++billing-report++'s session has Stories and DDD enabled  
*When* the Person makes ++billing-report++ the active ticket on the board  
*Then* the story map shows ++billing-report++'s epic, Report Billing, and its stories  
  *And* the band shows ++billing-report++'s Stories and DDD squares

#### Scenario: A ticket without a session leaves the story map where it was

*Given* ++checkout-flow++ is the active ticket  
  *But* ++search-orders++ has no session yet  
*When* the Person picks ++search-orders++ on the board  
*Then* the story map still shows ++checkout-flow++'s stories  
  *And* the band says only tickets with a session can be opened

## Story: Filter Knowledge Graph To Ticket Scope

### Evidence

| Source | Note |
|--------|------|
| `harness/.context/stories/story-map.md` | Move Work Forward On Session Board > Integrate Practice Content Editor Apps On Board > Person --> Filter Knowledge Graph To Ticket Scope |
| `harness/.context/stories/thin-slice.md` | increment 2 |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: The graph shows only the active ticket's session folders

*Given* ++checkout-flow++ is the active ticket  
*When* the Person opens the knowledge graph  
*Then* the graph shows only ++checkout-flow++'s session folders  
  *And* no other ticket's folders are listed

#### Scenario: Changing the active ticket rescopes an open graph

*Given* the knowledge graph is open on ++checkout-flow++  
*When* the Person makes ++billing-report++ the active ticket  
*Then* the graph shows only ++billing-report++'s session folders

## Story: Filter Knowledge Graph To Ticket Practices

### Evidence

| Source | Note |
|--------|------|
| `harness/.context/stories/story-map.md` | Move Work Forward On Session Board > Integrate Practice Content Editor Apps On Board > Person --> Filter Knowledge Graph To Ticket Practices |
| `harness/.context/stories/thin-slice.md` | increment 2 |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: The graph shows only the practices enabled for billing-report

*Given* ++billing-report++ is the active ticket  
  *And* its session has Stories and DDD enabled  
*When* the Person opens the knowledge graph  
*Then* the graph shows ++billing-report++'s Stories and DDD trees  
  *And* it shows no UX or Clean Engineering tree

#### Scenario: The graph shows only the practices enabled for checkout-flow

*Given* ++checkout-flow++ is the active ticket  
  *And* its session has Stories, UX and Clean Engineering enabled  
*When* the Person opens the knowledge graph  
*Then* the graph shows ++checkout-flow++'s Stories, UX and Clean Engineering trees  
  *And* it shows no DDD tree

## Story: Invoke Story Explorer In Session Context

### Evidence

| Source | Note |
|--------|------|
| `harness/.context/stories/story-map.md` | Move Work Forward On Session Board > Integrate Practice Content Editor Apps On Board > Person --> Invoke Story Explorer In Session Context |
| `harness/.context/stories/thin-slice.md` | increment 4 |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: The explorer plays the active ticket's stories on their design canvas screens

*Given* ++checkout-flow++ is the active ticket  
  *And* its story map shows Screen frames, with Activate Ticket on the CDD Kanban design canvas screen  
*When* the Person explores ++checkout-flow++'s stories from its story map  
*Then* the story explorer opens below the story map on Activate Ticket  
  *And* its frame shows the CDD Kanban design canvas screen

#### Scenario: Another ticket's explorer plays that ticket's stories

*Given* the story explorer is open on ++checkout-flow++'s Activate Ticket  
*When* the Person makes ++billing-report++ the active ticket  
*Then* the story explorer closes  
  *And* ++billing-report++'s story map shows in its place

## Story: Deploy Knowledge Graph App With Board State

### Evidence

| Source | Note |
|--------|------|
| `harness/.context/stories/story-map.md` | Move Work Forward On Session Board > Integrate Practice Content Editor Apps On Board > Agent --> Deploy Knowledge Graph App With Board State |
| `harness/.context/stories/thin-slice.md` | increment 2; non-functional, so it has no screen |

#### Scenario: The Graph app shares the board's state

*Given* the board's state runs on its app server instance  
*When* the Agent deploys the Graph app  
*Then* the Graph app runs on the same app server and instance as the board's state  
  *And* a ticket made active on the board is the ticket the graph shows, without a reload

## Story: Refactor Knowledge Graph App To Web Domain Access

### Evidence

| Source | Note |
|--------|------|
| `harness/.context/stories/story-map.md` | Move Work Forward On Session Board > Integrate Practice Content Editor Apps On Board > Agent --> Refactor Knowledge Graph App To Web Domain Access |
| `cdd_guidance/patterns/cdd_web_domain_access` | the TypeScript language adapter the pattern generates |

#### Scenario: The Graph app reaches the CDD domain only through the generated adapter

*Given* the cdd_web_domain_access pattern has generated the TypeScript language adapter  
*When* the Agent refactors the Graph app  
*Then* every call the Graph app makes to the CDD domain goes through the generated adapter  
  *And* the Graph app keeps no calls of its own to the domain's tools
