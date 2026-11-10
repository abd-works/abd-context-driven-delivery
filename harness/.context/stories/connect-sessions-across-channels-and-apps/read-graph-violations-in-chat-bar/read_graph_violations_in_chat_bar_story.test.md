---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Read Graph Violations In Chat Bar

### Domain terms

- ++practice square++ — a coloured square on the chat band for each practice enabled on the session; a red number is its violation count, and an underline means it is picked for the next action.

> In steps: ${field} is a column of the scenario's Examples.

## Examples

### generate by picked practices

| picked | generated | violations shown |
| --- | --- | --- |
| UX | UX | 1, Ticket details budget |
| Stories | Stories | 3 |
| Clean Engineering | Clean Engineering | 1, Activate Ticket name |
| Stories, UX, Clean Engineering | all three | 5 |

## Story: Read Session Violations From Latest Graph

### Evidence

| Source | Note |
|--------|------|
| user request, 2026-11-06 | "default is to have a graph and just read the violations" |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: Each practice square shows its count from the latest graph

*Given* checkout-flow is the active ticket, with Stories, UX and Clean Engineering enabled  
*When* generate reloads checkout-flow's graph  
*Then* the Stories square shows 3, the UX square 1 and the Clean Engineering square 1

#### Scenario: Squares for an ungenerated session show no counts

*Given* billing-report is the active ticket  
  *But* no change has been generated for billing-report  
*When* the Person looks at the chat band  
*Then* the Stories and DDD squares show no counts

## Story: Generate And Judge Fidelity From Chat Bar

### Evidence

| Source | Note |
|--------|------|
| artifact comment, 2026-11-06 | "we're selecting them for the next action; if more than one selected you're going to generate" |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: Only the picked practice is generated

*Given* checkout-flow is the active ticket  
  *And* only the UX square is picked on the band  
*When* the Person generates checkout-flow's files  
*Then* only UX is generated  
  *And* only the Ticket details budget violation appears

#### Scenario Outline: Generate runs on the practices picked on the band

*Given* checkout-flow is the active ticket  
  *And* ${picked} is picked on the band  
*When* the Person generates checkout-flow's files  
*Then* ${generated} is generated  
  *And* the band shows ${violations shown} violations

##### Examples

| picked | generated | violations shown |
| --- | --- | --- |
| Stories | Stories | 3 |
| Clean Engineering | Clean Engineering | 1 |
| Stories, UX, Clean Engineering | all three | 5 |

## Story: Fix Graph Violations From Chat Bar

### Evidence

| Source | Note |
|--------|------|
| artifact comment, 2026-11-06 | "fix button belongs on rule not top" |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: Fixing a rule fixes both of its violations

*Given* checkout-flow's latest graph holds 5 violations  
  *And* verb-noun-format holds Ticket Archive name and Delete Ticket name  
*When* the Person fixes the rule verb-noun-format from the Inspector  
*Then* both verb-noun-format violations are fixed  
  *And* the rule leaves the violation cards  
  *And* 3 violations stay on the latest graph

#### Scenario: Fixing one violation leaves the rest of its rule

*Given* verb-noun-format holds Ticket Archive name and Delete Ticket name  
*When* the Person fixes only Ticket Archive name from its card  
*Then* Ticket Archive name is fixed  
  *And* verb-noun-format still holds Delete Ticket name
