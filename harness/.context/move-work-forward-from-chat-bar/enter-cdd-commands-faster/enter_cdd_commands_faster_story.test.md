---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Enter CDD Commands Faster

### Domain terms

- ++next command++ — the action and fidelity the session should run next, from `ticket.generate_commands`.
- ++action list++ — the chat band's ▶ ▾ list box: generate, render, sketch, iterate, document and fix.

> In steps: ${field} is a column of the scenario's Examples.

## Story: Suggest Next Command

### Evidence

| Source | Note |
|--------|------|
| `.sessions/_backlog/mod-ideas.md` | "Next-step suggestion": `$.prompt.suggest` fills in the next command from `ticket.generate_commands` |
| artifact comment, 2026-11-06 | "the list box of actions should be on the next action recommended; it's not shown anywhere in chat panel but there" |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: The action list recommends the next command after a fidelity is generated

*Given* checkout-flow is the active ticket  
  *And* its story map fidelity has just been generated  
*When* the chat finishes the generate  
*Then* the band's action list marks generate as recommended, for the scenarios fidelity  
  *And* ▶ is set to it, and its tip says recommended next: scenarios  
  *And* the chat panel shows no suggestion of its own

#### Scenario Outline: The recommendation follows the fidelity that was just generated

*Given* checkout-flow is the active ticket  
  *And* its ${generated} fidelity has just been generated  
*When* the chat finishes the generate  
*Then* the band's action list recommends generate for the ${next} fidelity

##### Examples

| generated | next |
| --- | --- |
| story map | scenarios |
| scenarios | acceptance tests |
| bounded context | model |
