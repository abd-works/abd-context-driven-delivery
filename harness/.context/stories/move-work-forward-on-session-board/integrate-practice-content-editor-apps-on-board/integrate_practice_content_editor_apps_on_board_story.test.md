---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Integrate Practice Content Editor Apps On Board

### Domain terms

Each term links to its class in the model, [editor-apps-model.md](../../../editor-apps/.context/editor-apps-model.md).

- ++ticket++ — a card on the CDD Kanban with its own session; the active ticket is the one every view shows.
- ++session++ — the ticket's folder of work, with the practices enabled for it and the stories it names: the ticket's scope.
- ++practice++ — a lens enabled on a session: Stories, DDD, UX, Clean Engineering or BDD.
- ++practice row++ — one fidelity's row in a ticket's practice grid ([FidelityProgress](../../../editor-apps/.context/editor-apps-model.md#fidelityprogress-extended)).
- ++editor widget++ — the small control on the Stories story-map row that opens the Story UI editor ([BoardFidelity.editor](../../../editor-apps/.context/editor-apps-model.md#boardfidelity-extended)).
- ++graph widget++ — the control on a ticket, beside its folder and file icons, that opens the Graph app on the ticket ([Graph.load_practice_roots](../../../editor-apps/.context/editor-apps-model.md#graph-extended)).
- ++story map++ — the session's epics, sub-epics and stories, shown by the Story UI editor ([StoryModel](../../../editor-apps/.context/editor-apps-model.md#storymodel-extended)).
- ++knowledge graph++ — the practice trees the Graph app loads from a session's practice roots.
- ++practice root++ — the folder a session names for one of its enabled practices ([PracticeGuidance.session_root](../../../editor-apps/.context/editor-apps-model.md#practiceguidance-extended)).
- ++generated adapter++ — the `{Object}Adapter` and `{Object}ClientGenerated` the cdd_web_domain_access pattern generates for a Python domain object.

> In steps: ++example++ names a row of a table below; ${field} is a column of the scenario's Examples.

## Examples

### tickets ([Ticket](../../../editor-apps/.context/editor-apps-model.md#ticket-extended), [PracticeGuidance.session_root](../../../editor-apps/.context/editor-apps-model.md#practiceguidance-extended))

| ticket | stage | practices | practice roots | stories its session names |
| --- | --- | --- | --- | --- |
| ++checkout-flow++ | Implementation | Stories, UX, Clean Engineering | harness/.context/stories, harness/.context/ux, harness/.context | Open Story UI Side Panel From Chat Bar, Open Kanban Side Panel From Chat Bar |
| ++billing-report++ | Discovery | Stories, DDD | billing/.context/stories, billing/.context | Report Billing By Month |
| ++search-orders++ | Backlog | none: no session yet | none | none |

### practice rows ([BoardFidelity.editor](../../../editor-apps/.context/editor-apps-model.md#boardfidelity-extended))

| practice row | editor widget |
| --- | --- |
| ++Stories story map++ | Story UI editor |
| ++Stories scenarios++ | none |
| ++UX mockup++ | none |
| ++Clean Engineering model++ | none |

### graph openings ([Graph.load_practice_roots](../../../editor-apps/.context/editor-apps-model.md#graph-extended))

| opened from | graph scope | practice trees |
| --- | --- | --- |
| ++billing-report's graph widget++ | billing-report's practice roots | Stories, DDD |
| ++checkout-flow's graph widget++ | checkout-flow's practice roots | Stories, UX, Clean Engineering |
| ++the board header++ | the board's repository | every practice on the board |

### generated adapters

| domain object | generated client |
| --- | --- |
| ++Board++ | BoardClientGenerated |
| ++Ticket++ | TicketClientGenerated |
| ++FidelityProgress++ | FidelityProgressClientGenerated |
| ++BacklogItem++ | BacklogItemClientGenerated |

## Story: Open Story UI On Ticket Scope

### Evidence

| Source | Note |
|--------|------|
| `harness/.context/stories/story-map.md:575-577` | Requested (2026-11-06): the board opens the Story UI editor on the part of the story map the ticket covers; Requested (2026-11-12): a small editor widget on the ticket's Stories story-map row opens it |
| `space/kanban/app/src/kanban/ticket/practice-grid-view.tsx` | Observed: the ticket's practice grid, one row per fidelity |
| `cdd_guidance/practices/stories/model/story_model.py:1110` | Observed: *StoryModel.stories_named*, which the ticket's scope reads |

#### Scenario: The story-map row's editor widget opens the Story UI editor on the ticket's stories

*Given* ++checkout-flow++'s session names Open Story UI Side Panel From Chat Bar and Open Kanban Side Panel From Chat Bar  
  *And* its ++Stories story map++ row shows harness/.context/stories/story-map.md  
*When* the Person opens the Story UI editor from the ++Stories story map++ row's editor widget  
*Then* the Story UI editor opens on harness/.context/stories/story-map.md  
  *And* it shows Open Story UI Side Panel From Chat Bar and Open Kanban Side Panel From Chat Bar under Integrate Practice Content Editor Apps In Chat Bar  
  *And* it shows no other story of the map

#### Scenario Outline: Only the Stories story-map row carries the editor widget

*Given* ++checkout-flow++'s card is open on the board  
*When* the Person looks at the ++${practice row}++ row  
*Then* the row shows ${editor widget}

##### Examples

| practice row | editor widget |
| --- | --- |
| Stories story map | the editor widget for the Story UI editor |
| Stories scenarios | no editor widget |
| UX mockup | no editor widget |
| Clean Engineering model | no editor widget |

#### Scenario: A backlog item without a session has no editor widget

*Given* ++search-orders++ is in the Backlog  
  *But* ++search-orders++ has no session yet  
*When* the Person looks at ++search-orders++ on the board  
*Then* ++search-orders++ shows no practice rows and no editor widget

## Story: Filter Knowledge Graph To Ticket Scope

### Evidence

| Source | Note |
|--------|------|
| `harness/.context/stories/story-map.md:579-581` | Requested (2026-11-06): the Graph app loads only the ticket's session folders; Requested (2026-11-12): a graph widget on the ticket, beside its folder and file icons, opens the graph on the ticket's scope |
| `space/session/session.py:222-243` | Observed: a session's graph holds only the practices it enabled |

#### Scenario: The ticket's graph widget opens the graph on the ticket's practice roots

*Given* ++checkout-flow++'s practice roots are harness/.context/stories, harness/.context/ux and harness/.context  
*When* the Person opens the knowledge graph from ++checkout-flow++'s graph widget  
*Then* the Graph app opens on ++checkout-flow++'s practice roots: harness/.context/stories, harness/.context/ux and harness/.context  
  *And* no folder of ++billing-report++ is loaded

#### Scenario: Another ticket's graph widget rescopes the open graph

*Given* the knowledge graph is open on ++checkout-flow++'s practice roots  
*When* the Person opens the knowledge graph from ++billing-report++'s graph widget  
*Then* the Graph app shows ++billing-report++'s practice roots: billing/.context/stories and billing/.context  
  *And* no folder of ++checkout-flow++ is loaded

## Story: Filter Knowledge Graph To Ticket Practices

### Evidence

| Source | Note |
|--------|------|
| `harness/.context/stories/story-map.md:583-585` | Requested (2026-11-06): the Graph app opens with its practice filter set to the practices the ticket has turned on, or every practice on the board when opened from the board header |
| `harness/.context/stories/thin-slice.md` | increment 2 |

#### Scenario Outline: The graph shows only the practices of what it was opened from

*Given* ++billing-report++ has Stories and DDD enabled  
  *And* ++checkout-flow++ has Stories, UX and Clean Engineering enabled  
*When* the Person opens the knowledge graph from ++${opened from}++  
*Then* the graph shows the ${practice trees} trees  
  *And* it shows no tree of a practice not listed

##### Examples

| opened from | practice trees |
| --- | --- |
| billing-report's graph widget | Stories, DDD |
| checkout-flow's graph widget | Stories, UX, Clean Engineering |
| the board header | Stories, DDD, UX, Clean Engineering, BDD |

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
| `harness/.context/stories/story-map.md:587-589` | Requested (2026-11-06, non-functional): the Graph app runs on the same app server and instance as the board's state |
| `harness/.context/stories/thin-slice.md` | increment 2; non-functional, so it has no screen |

#### Scenario: The Graph app shares the board's state

*Given* ++checkout-flow++ is the board's active ticket  
*When* the Agent deploys the Graph app with the board's state  
*Then* the Graph app works on the same session and graph as the board's active ticket  
*When* the session open in the project becomes ++billing-report++'s, which the board then shows as active  
*Then* the board's active ticket is ++billing-report++  
  *And* the graph shows ++billing-report++'s practice roots on its next read, without a reload

## Story: Refactor Kanban Board To Web Domain Access

### Evidence

| Source | Note |
|--------|------|
| `harness/.context/stories/story-map.md:591-593` | Requested (2026-11-12, non-functional, "like above but for kanban board"): the CDD Kanban follows cdd_web_domain_access and lern_domain_driven; its backend is the MCP-generated domain objects through the TypeScript adapter, not calls of its own |
| `space/kanban/app/src/kanban/board/board-api.ts` | Observed: *BoardApi* is the board's own call layer, posting to `/api/...` paths it names itself |
| `space/kanban/app/packages/session-board/app.ts:41-60` | Observed: hand-written routes `/api/update`, `/api/claude/open`, `/api/build` beside the generated ones |
| `harness/graph/app/graph/GraphClient.ts:1-6` | Observed: the Graph app's finished shape (`GraphApi implements CddApi`, the server mounting the generated routes) |

#### Scenario: Every board call reaches the domain through its generated adapter

*Given* the cdd_web_domain_access pattern has generated the adapters for ++Board++, ++Ticket++, ++FidelityProgress++ and ++BacklogItem++  
*When* the Agent refactors the CDD Kanban  
*Then* every call the CDD Kanban makes to the CDD domain goes through that object's generated client  
  *And* the board's server mounts only the generated routes for the domain  
  *And* the CDD Kanban keeps no route or call of its own to the domain's tools

#### Scenario: A move the agent makes shows on the board without a copy kept in the page

*Given* the CDD Kanban shows ++checkout-flow++ in Implementation In progress  
*When* the Agent moves ++checkout-flow++ to Implementation Done through the ticket's tools  
*Then* the CDD Kanban shows ++checkout-flow++ in Implementation Done on its next read of the board

#### Scenario: A board whose cdd server is down says so instead of drawing old state

*Given* the CDD Kanban is open  
  *But* the cdd server is not answering  
*When* the CDD Kanban reads the board  
*Then* the CDD Kanban says the cdd server is not answering and how to start it  
  *And* it shows no column as current

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
