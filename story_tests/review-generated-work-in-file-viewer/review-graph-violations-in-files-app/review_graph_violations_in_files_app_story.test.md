---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Review Graph Violations In Files App

### Domain terms

- ++live graph++ — the session's knowledge graph as it stands now, read again for a file when that file changes (`Session.file_alone`), holding every violation found in the files read.
- ++violation++ — a rule a node breaks, with its practice, file and the lines it covers.
- ++graph view++ — the Files app's file bar showing the practice trees of the session's graph for the files it lists.
- ++fix++ — the action the chat runs for a violation, a rule, or every violation shown, with the node, file and lines, rule, excerpt and message.
- ++fidelity dot++ — a coloured square on the chat bar for a fidelity of the stages shown; a red number on it is its violation count.

> In steps: ++example++ names a row of a table below; ${field} is a column of the scenario's Examples.

> Evidence: every scenario here is Intended. The Files app on release-2 marks the open file's broken rules with the Rules toggle on (Built 2026-11-15), and the Graph app does the rest in its own page (Observed, `.context/story-map.md` Review Violations In Graph App); the board and the chat bar count violations from the last validation report today.

## Examples

### checkout-flow violations

| violation | practice | rule | file | lines |
| --- | --- | --- | --- | --- |
| ++Ticket Archive name++ | Stories | verb-noun-format | .context/story-map.md | 311 to 313 |
| ++Ticket Deletion name++ | Stories | verb-noun-format | .context/story-map.md | 315 to 317 |

*Ticket Deletion name* replaced *Delete Ticket name* on 2026-11-16 (agreed by the person): *Delete Ticket* is a verb and a noun, so the real verb-noun-format check passes it; *Ticket Deletion* names no verb and breaks it.
| ++Move Ticket size++ | Stories | right-size-story-nodes | .context/story-map.md | 269 to 271 |
| ++Ticket details budget++ | UX | screen-story-budget | harness/.context/information-architecture.drawio | 8 to 10 |
| ++Activate Ticket name++ | Clean Engineering | use-intention-revealing-names | space/kanban/ticket.py | 460 to 460 |

### checkout-flow violation counts

| fidelity | count |
| --- | --- |
| Stories story map | 3 |
| UX information architecture | 1 |
| Clean Engineering code | 1 |

## Story: Show Only Violating Nodes In Files App

### Evidence

| Source | Note |
|--------|------|
| user request, 2026-11-15 | "we basically ingest all of the stories and functionality that the Graph application can do" |
| Graph app, Show Only Violations, Filter Violations By Rule (Observed) | `FilterView.tsx`, `Filter._fails_selected_rule` |
| person's decision, 2026-11-16 | Violations is a node filter: it applies together with the file list, narrowing the nodes of the files listed, never replacing the list. |

#### Scenario: The Violations switch keeps only nodes that break a rule

*Given* the Files app shows checkout-flow's graph with Stories, UX and Clean Engineering on  
*When* the Person turns on Violations  
*Then* the graph view holds only the nodes of Ticket Archive name, Ticket Deletion name, Move Ticket size, Ticket details budget and Activate Ticket name

#### Scenario: Choosing a rule keeps only the nodes that break it

*Given* the Files app shows checkout-flow's violating nodes  
*When* the Person chooses the rule verb-noun-format  
*Then* the graph view holds only Ticket Archive name and Ticket Deletion name

## Story: See Rules Under Node In Files App

### Evidence

| Source | Note |
|--------|------|
| user request, 2026-11-15 | "we basically ingest all of the stories and functionality that the Graph application can do" |
| Graph app, See Rules Under Node, Hover Violating Rule For Message (Observed) | `Node.rule_category`, `GraphView.tsx` `violationHint` |

#### Scenario: A node lists its passing, broken and prompt rules

*Given* the Files app shows checkout-flow's graph  
*When* the Person opens the rules of the Ticket Deletion story  
*Then* verb-noun-format shows broken  
  *And* its other rules show passing, or as prompts where they have no check  
  *And* Ticket Deletion is marked in the tree as breaking a rule

#### Scenario: Hovering a broken rule shows its message

*Given* the rules of the Ticket Deletion story are open  
*When* the Person hovers over verb-noun-format  
*Then* the graph view shows Ticket Deletion name's message

## Story: Open Violation In Files App Source

### Evidence

| Source | Note |
|--------|------|
| user request, 2026-11-15 | "we basically ingest all of the stories and functionality that the Graph application can do" |
| Graph app, Open Violation In Source (Observed); Files app, Mark Lines A Broken Rule Names (Built) | `SourceView.tsx`, `session.file` violations |

#### Scenario: Selecting a broken rule opens its lines unfolded

*Given* the rules of the Activate Ticket node are open  
*When* the Person selects use-intention-revealing-names  
*Then* ticket.py opens at line 460, unfolded  
  *And* the rule and Activate Ticket name's message show above the line

## Story: Fix Graph Violations From Files App

### Evidence

| Source | Note |
|--------|------|
| user request, 2026-11-06 | "board and chat ... fix"; "/fix is a first class action; fix rule; file; default across all rules / files" |
| artifact comment, 2026-11-06 | "fix button belongs on rule not top" |
| Graph app, Copy Correct Prompt (Observed) | `source/violation-prompt.ts` |

#### Scenario: Fixing one violation sends it alone to the chat

*Given* the Files app shows checkout-flow's violating nodes, opened from the chat  
*When* the Person fixes Ticket Archive name  
*Then* the chat that opened the page receives the fix for Ticket Archive name, with its node, file, lines, rule, excerpt and message  
  *And* Ticket Deletion name stays unfixed

#### Scenario: Fixing a rule sends every violation of it

*Given* verb-noun-format holds Ticket Archive name and Ticket Deletion name  
*When* the Person fixes the rule verb-noun-format  
*Then* the chat receives one fix for both verb-noun-format violations

#### Scenario: Fixing all sends every violation the graph view shows

*Given* the graph view shows only the Stories practice's 3 violations  
*When* the Person fixes all  
*Then* the chat receives one fix for Ticket Archive name, Ticket Deletion name and Move Ticket size  
  *But* not for the UX or Clean Engineering violations, which the graph view does not show

#### Scenario: A fixed violation leaves the graph view once its file is read again

*Given* the chat has worked on the fix for Ticket Archive name  
*When* the Files app reads story-map.md again  
*Then* Ticket Archive name leaves the graph view  
  *And* Ticket Deletion name stays

## Story: Fix Graph Violations From Chat Bar

### Evidence

| Source | Note |
|--------|------|
| user request, 2026-11-06 | "board and chat ... fix" |

#### Scenario: Fix in the action picker fixes the selected fidelities' violations

*Given* checkout-flow's live graph holds 5 violations  
  *And* only the Stories story map dot is selected on the chat bar  
*When* the Person runs Fix from the action picker  
*Then* the chat receives the fix for Ticket Archive name, Ticket Deletion name and Move Ticket size

## Story: Count Session Violations From Live Graph

### Evidence

| Source | Note |
|--------|------|
| user request, 2026-11-06 | "default is to have a graph and just read the violations"; "board and chat generate" |

#### Scenario: Each fidelity dot counts its violations from the live graph

*Given* checkout-flow's live graph holds 5 violations  
*When* the chat bar reads checkout-flow's session  
*Then* the Stories story map dot shows 3, the UX information architecture dot 1 and the Clean Engineering code dot 1

#### Scenario: A file read again updates the dots without a validate

*Given* the Stories story map dot shows 3  
  *But* no validate has run since  
*When* the Files app reads story-map.md again, after Ticket Archive name was fixed  
*Then* the Stories story map dot shows 2

#### Scenario: A session not generated yet shows no counts

*Given* billing-report is the active ticket  
  *But* no change has been generated for billing-report  
*When* the chat bar reads billing-report's session  
*Then* billing-report's dots show no counts

## Story: Count Fidelity Violations From Live Graph

### Evidence

| Source | Note |
|--------|------|
| user request, 2026-11-06 | "default is to have a graph and just read the violations"; "board and chat generate" |
| backlog, `.sessions/_backlog/fully-integrated-app-flow.md` | "better graph integration - load up front on session open, show all violations as a result of graph, no need for explicit run" |

#### Scenario Outline: Each tile counts its fidelity's violations from the live graph

*Given* checkout-flow's live graph holds 5 violations  
*When* the board shows checkout-flow's ${fidelity} tile  
*Then* the tile shows ${count} violations

##### Examples

| fidelity | count |
| --- | --- |
| Stories story map | 3 |
| UX information architecture | 1 |
| Clean Engineering code | 1 |
