---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Integrate Practice Content Editor Apps In Chat Bar

### Domain terms

- ++chat band++ — the strip under the Claude Code chat: the session, the practice squares, the action, the formats and the view icons.
- ++view++ — a pane beside the chat: board, story map, story explorer, knowledge graph or Inspector.
- ++violation++ — a rule a node in the latest graph breaks, with its file and the lines it covers.
- ++design canvas screen++ — an artboard on the Claude Design canvas that the story explorer shows as a story's frame.

> In steps: ++example++ names a row of a table below; ${field} is a column of the scenario's Examples.

## Examples

### views

| view | opened beside the chat as |
| --- | --- |
| ++board++ | the CDD Kanban with the active ticket outlined |
| ++story map++ | the active ticket's epics and stories |
| ++knowledge graph++ | the active ticket's practice trees |
| ++Inspector++ | the active ticket's files as tabs |

### violations

| violation | rule | file | lines | story |
| --- | --- | --- | --- | --- |
| ++Ticket Archive name++ | verb-noun-format | harness/.context/stories/story-map.md | 86 to 88 | Ticket Archive |
| ++Move Ticket size++ | right-size-story-nodes | harness/.context/stories/story-map.md | 148 to 150 | Move Ticket |

### design canvas screens

| story | design canvas screen |
| --- | --- |
| ++Activate Ticket++ | CDD Kanban |
| ++Open Ticket Session++ | Ticket Details |
| ++Move Ticket++ | none |

## Story: Open Story UI Side Panel From Chat Bar

### Evidence

| Source | Note |
|--------|------|
| `harness/.context/stories/story-map.md` | Move Work Forward From Chat Bar > Integrate Practice Content Editor Apps In Chat Bar > Person --> Open Story UI Side Panel From Chat Bar |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: The story map opens beside the chat on the active ticket

*Given* checkout-flow is the active ticket  
  *But* the story map is not open  
*When* the Person opens the story map from the chat band  
*Then* the story map opens beside the chat  
  *And* it shows checkout-flow's epics and stories

#### Scenario Outline: Each view opens beside the chat from the chat band

*Given* checkout-flow is the active ticket  
*When* the Person opens the ++${view}++ from the chat band  
*Then* the ++${view}++ opens beside the chat as ${opened beside the chat as}  
  *And* the chat band marks the ++${view}++ as open

##### Examples

| view | opened beside the chat as |
| --- | --- |
| board | the CDD Kanban with the active ticket outlined |
| story map | the active ticket's epics and stories |
| knowledge graph | the active ticket's practice trees |
| Inspector | the active ticket's files as tabs |

#### Scenario: A fifth view closes the oldest

*Given* the board, the story map, the story explorer and the Inspector are open beside the chat  
*When* the Person opens the knowledge graph from the chat band  
*Then* the knowledge graph opens beside the chat  
  *And* the board, the oldest view, closes

## Story: Invoke Claude Design Story Explorer From Chat Bar

### Evidence

| Source | Note |
|--------|------|
| `harness/.context/stories/story-map.md` | Move Work Forward From Chat Bar > Integrate Practice Content Editor Apps In Chat Bar > Person --> Invoke Claude Design Story Explorer From Chat Bar |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: The story explorer opens below the story map on a story's design canvas screen

*Given* checkout-flow is the active ticket  
  *And* its story map shows Screen frames  
*When* the Person explores ++Activate Ticket++  
*Then* the story explorer opens below the story map  
  *And* its frame shows ++Activate Ticket++'s CDD Kanban design canvas screen

#### Scenario: A story with no design canvas screen cannot be explored

*Given* checkout-flow's story map shows Screen frames  
  *But* ++Move Ticket++ has no design canvas screen  
*When* the Person tries to explore ++Move Ticket++  
*Then* the story explorer stays closed  
  *And* the band says ++Move Ticket++ has no screen yet

## Story: Deploy Story UI App With Board State

### Evidence

| Source | Note |
|--------|------|
| `harness/.context/stories/story-map.md` | Move Work Forward From Chat Bar > Integrate Practice Content Editor Apps In Chat Bar > Agent --> Deploy Story UI App With Board State |
| `harness/.context/stories/thin-slice.md` | increment 2; non-functional, so it has no screen |

#### Scenario: The Story UI app shares the board's state

*Given* the board's state runs on its app server instance  
*When* the Agent deploys the Story UI app  
*Then* the Story UI app runs on the same app server and instance as the board's state  
  *And* a ticket made active on the board is the ticket the story map and the story explorer show, without a reload

## Story: Refactor Story UI App To Web Domain Access

### Evidence

| Source | Note |
|--------|------|
| `harness/.context/stories/story-map.md` | Move Work Forward From Chat Bar > Integrate Practice Content Editor Apps In Chat Bar > Agent --> Refactor Story UI App To Web Domain Access |
| `cdd_guidance/patterns/cdd_web_domain_access` | the TypeScript language adapter the pattern generates |

#### Scenario: The Story UI app reaches the CDD domain only through the generated adapter

*Given* the cdd_web_domain_access pattern has generated the TypeScript language adapter  
*When* the Agent refactors the Story UI app  
*Then* every call the Story UI app makes to the CDD domain goes through the generated adapter  
  *And* the Story UI app keeps no calls of its own to the domain's tools

## Story: Open UX Design In Claude Design

### Evidence

| Source | Note |
|--------|------|
| `harness/.context/stories/story-map.md` | Move Work Forward From Chat Bar > Integrate Practice Content Editor Apps In Chat Bar > Person --> Open UX Design In Claude Design |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: The ticket's UX design opens as a design canvas

*Given* checkout-flow has UX enabled  
  *And* checkout-flow has a UX design canvas  
*When* the Person opens checkout-flow's UX design from its ticket  
*Then* the UX design opens as a design canvas in Claude Design

#### Scenario: A ticket without UX has no design to open

*Given* billing-report has Stories and DDD enabled  
  *But* UX is not enabled for billing-report  
*When* the Person looks at billing-report's ticket  
*Then* the ticket offers no UX design

## Story: Trace Story Through Artifacts

### Evidence

| Source | Note |
|--------|------|
| `harness/.context/stories/story-map.md` | Move Work Forward From Chat Bar > Integrate Practice Content Editor Apps In Chat Bar > Person --> Trace Story Through Artifacts |
| `.sessions/_backlog/integrate-practice-content-editor-apps.md` | "Trace pane": a story's scenarios, tests, code and diagrams, read from the knowledge graph |

#### Scenario Outline: The Inspector traces a violation's story through its artifacts

*Given* checkout-flow is the active ticket  
  *And* generate has reloaded checkout-flow's graph  
*When* the Person opens the ++${violation}++ violation in the Inspector  
*Then* ${file} opens at lines ${lines}  
  *And* the trace under the file names ${story}, its scenarios, tests and code from the graph

##### Examples

| violation | file | lines | story |
| --- | --- | --- | --- |
| Ticket Archive name | harness/.context/stories/story-map.md | 86 to 88 | Ticket Archive |
| Move Ticket size | harness/.context/stories/story-map.md | 148 to 150 | Move Ticket |
| Activate Ticket name | space/kanban/ticket.py | 212 to 213 | Activate Ticket |
