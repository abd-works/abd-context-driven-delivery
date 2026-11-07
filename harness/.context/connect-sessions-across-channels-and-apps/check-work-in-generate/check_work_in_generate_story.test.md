---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Check Work In Generate

### Domain terms

- ++generate++ — the action that writes a fidelity's files for the picked practices, then reloads the graph and judges the rules.
- ++latest graph++ — the knowledge graph generate reloads from the session's files, holding every violation.
- ++violation++ — a rule a node breaks, with its practice, file and the lines it covers.
- ++fix++ — the action that sends `/actions-fix` for a violation, a rule, a file or every violation.

> In steps: ++example++ names a row of a table below; ${field} is a column of the scenario's Examples.

## Examples

### checkout-flow violations

| violation | practice | rule | file | lines |
| --- | --- | --- | --- | --- |
| ++Ticket Archive name++ | Stories | verb-noun-format | harness/.context/story-map.md | 86 to 88 |
| ++Delete Ticket name++ | Stories | verb-noun-format | harness/.context/story-map.md | 90 to 92 |
| ++Move Ticket size++ | Stories | right-size-story-nodes | harness/.context/story-map.md | 148 to 150 |
| ++Ticket details budget++ | UX | screen-story-budget | harness/.context/information-architecture.drawio | 8 to 10 |
| ++Activate Ticket name++ | Clean Engineering | use-intention-revealing-names | space/kanban/ticket.py | 212 to 213 |

## Story: Refresh Graph After Generate

### Evidence

| Source | Note |
|--------|------|
| user request, 2026-11-06 | "generate → load refreshed graph based on changes immediately" |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: Generate reloads the graph from the changed files

*Given* checkout-flow is the active ticket, with Stories, UX and Clean Engineering enabled  
  *But* no change has been generated yet  
*When* the Person generates checkout-flow's files  
*Then* the graph reloads from the changed files  
  *And* the band says the latest graph holds 5 violations

#### Scenario: Generate with no practice picked is refused

*Given* checkout-flow is the active ticket  
  *But* no practice is picked on the band  
*When* the Person generates checkout-flow's files  
*Then* nothing is generated and the graph is not reloaded  
  *And* the band says to pick at least one practice

## Story: Attach Violations To Latest Graph

### Evidence

| Source | Note |
|--------|------|
| user request, 2026-11-06 | "violations now attached to latest graph automatically" |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario Outline: The latest graph's violations show on every view

*Given* checkout-flow is the active ticket  
*When* generate reloads the graph  
*Then* the ++${violation}++ violation shows on the band's ${practice} square  
  *And* it shows on checkout-flow's tile, the story map's cards and the Inspector

##### Examples

| violation | practice |
| --- | --- |
| Ticket Archive name | Stories |
| Ticket details budget | UX |
| Activate Ticket name | Clean Engineering |

#### Scenario: A fixed violation leaves every view

*Given* the latest graph holds the ++Ticket Archive name++ violation  
*When* the Person fixes the ++Ticket Archive name++ violation  
*Then* the graph reloads  
  *And* the violation leaves the band, the tile, the story map and the Inspector

## Story: Judge Rules During Generate

### Evidence

| Source | Note |
|--------|------|
| user request, 2026-11-06 | "judge validation must be part of generate, eg merge the two actions" |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: Generate judges the rules and groups the violations by rule

*Given* checkout-flow is the active ticket  
  *But* no change has been generated yet  
*When* generate writes checkout-flow's files  
*Then* each violation card in the Inspector names the rule it broke  
  *And* the cards are grouped by rule, with verb-noun-format holding 2  
  *And* no separate validate run is needed

## Story: Fix Graph Violations

### Evidence

| Source | Note |
|--------|------|
| user request, 2026-11-06 | "fix is a first class action; fix rule; file; default across all rules / files" |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: Fix with nothing picked fixes every violation

*Given* checkout-flow's latest graph holds the 5 ++checkout-flow violations++  
  *And* fix is the band's action  
*When* the Person runs fix  
*Then* `/actions-fix` runs on every violation  
  *And* the graph reloads with none left

#### Scenario Outline: Fix runs on the scope the Person picks

*Given* checkout-flow's latest graph holds the 5 ++checkout-flow violations++  
*When* the Person fixes ${scope}  
*Then* `/actions-fix` runs on ${fixed}  
  *And* ${left} violations stay on the latest graph

##### Examples

| scope | fixed | left |
| --- | --- | --- |
| the rule verb-noun-format | Ticket Archive name and Delete Ticket name | 3 |
| the file space/kanban/ticket.py | Activate Ticket name | 4 |
| the Move Ticket size violation | Move Ticket size | 4 |

#### Scenario: Fix with no violations does nothing

*Given* checkout-flow's latest graph holds no violations  
*When* the Person runs fix  
*Then* no fix is sent  
  *And* the band says the latest graph holds no violations here

## Story: Validate Fidelity On Demand

### Evidence

| Source | Note |
|--------|------|
| artifact comment, 2026-11-06 | "validate is a slash command story only now" |

#### Scenario: Validate runs only as the slash command

*Given* checkout-flow's story map has been written  
*When* the Agent runs `/actions-validate` on harness/.context/story-map.md  
*Then* a validation report is written for story-map.md  
  *And* the board and the chat bar offer no Validate of their own
