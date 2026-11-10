---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Read Graph Violations On Board

### Domain terms

- ++ticket tile++ — a ticket's card on the board, with a count of violations for each enabled practice; expanded, it offers Files, generate, fix and its UX design.

> In steps: ${field} is a column of the scenario's Examples.

## Examples

### checkout-flow tile counts after generate

| practice | violations |
| --- | --- |
| Stories | 3 |
| UX | 1 |
| Clean Engineering | 1 |

## Story: Read Fidelity Violations From Latest Graph

### Evidence

| Source | Note |
|--------|------|
| user request, 2026-11-06 | "default is to have a graph and just read the violations" |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario Outline: The tile shows each practice's count from the latest graph

*Given* checkout-flow is the active ticket, with Stories, UX and Clean Engineering enabled  
*When* generate reloads checkout-flow's graph  
*Then* checkout-flow's tile shows ${violations} beside ${practice}

##### Examples

| practice | violations |
| --- | --- |
| Stories | 3 |
| UX | 1 |
| Clean Engineering | 1 |

#### Scenario: A ticket that has not been generated shows no counts

*Given* billing-report is on the board  
  *But* no change has been generated for billing-report  
*When* the Person looks at billing-report's tile  
*Then* its Stories and DDD show no violation counts

## Story: Generate And Judge Fidelity From Board

### Evidence

| Source | Note |
|--------|------|
| user request, 2026-11-06 | "board and chat generate" |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: Generate from the tile runs on the ticket's enabled practices

*Given* checkout-flow is on the board, with Stories, UX and Clean Engineering enabled  
*When* the Person generates checkout-flow from its tile  
*Then* checkout-flow becomes the active ticket  
  *And* its Stories, UX and Clean Engineering files are generated and judged  
  *And* the tile shows each practice's violation count

#### Scenario: Generate from another ticket's tile switches to it first

*Given* checkout-flow is the active ticket  
*When* the Person generates billing-report from its tile  
*Then* billing-report becomes the active ticket  
  *And* its Stories and DDD files are generated and judged

## Story: Fix Graph Violations From Board

### Evidence

| Source | Note |
|--------|------|
| user request, 2026-11-06 | "board and chat ... fix" |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: Fix from the tile fixes the ticket's violations

*Given* checkout-flow's latest graph holds 5 violations  
*When* the Person fixes checkout-flow from its tile  
*Then* `/actions-fix` runs on checkout-flow's violations  
  *And* the tile's counts clear
