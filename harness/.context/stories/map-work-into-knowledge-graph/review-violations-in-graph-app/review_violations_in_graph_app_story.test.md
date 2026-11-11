---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Review Violations In Graph App

### Domain terms

- ++drawio file++ — a diagram file; the Inspector shows it as its diagram, with a Source tab for its XML.
- ++shape++ — a cell in the diagram, tied to the lines of its source.

> In steps: ${field} is a column of the scenario's Examples.

## Examples

### information-architecture.drawio shapes

| shape | source lines | violation |
| --- | --- | --- |
| Ticket details | 8 to 10 | screen-story-budget: the screen shows 7 stories, about 4 fit |
| CDD Kanban | 4 | none |
| Chat Bar | 3 | none |

## Story: Display Drawio File As Diagram

### Evidence

| Source | Note |
|--------|------|
| artifact comment, 2026-11-06 | "inspector doesn't support drawio → add as explicit story; must support drawio" |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: The drawio file shows as its diagram with the violating shape in red

*Given* checkout-flow's latest graph holds the screen-story-budget violation on information-architecture.drawio  
*When* the Person opens information-architecture.drawio in the Inspector  
*Then* it shows as its diagram  
  *And* the Ticket details shape is red with screen-story-budget

#### Scenario Outline: Picking a shape opens its lines in Source

*Given* information-architecture.drawio shows as its diagram in the Inspector  
*When* the Person picks the ${shape} shape  
*Then* the Source tab opens at lines ${source lines}

##### Examples

| shape | source lines |
| --- | --- |
| Ticket details | 8 to 10 |
| CDD Kanban | 4 |
| Chat Bar | 3 |

#### Scenario: With violations hidden the diagram shows no red shape

*Given* information-architecture.drawio shows as its diagram  
  *But* Show violations is off in the Inspector  
*When* the Person looks at the diagram  
*Then* no shape is red

## Story: Test Knowledge Graph Explorer On Session Files

### Evidence

| Source | Note |
|--------|------|
| `harness/.context/stories/story-map.md` | Requested 2026-11-06: the Graph app loads a CDD session's files and its specs run against them |

#### Scenario: Each gap a spec finds becomes an Intended story

*Given* checkout-flow's session folder holds its story map, model and code  
*When* the Agent runs the Graph app's specs on checkout-flow's files  
*Then* every spec that fails names its gap  
  *And* each gap is added to the Graph app's story map as an Intended story
