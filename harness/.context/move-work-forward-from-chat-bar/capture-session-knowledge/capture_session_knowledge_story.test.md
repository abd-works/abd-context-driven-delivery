---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Capture Session Knowledge

### Domain terms

- ++handoff++ — a note in the session folder saying what was done and what to do next, so the next session never starts cold.
- ++correction++ — a mistake in work Claude just generated and the fix for it, logged in `corrections.log` beside that work.
- ++decision record++ — a CDR in the module's `cdr/` folder saying what was decided and why.
- ++offer++ — a card in the chat panel with its buttons; the Person accepts or skips it.

> In steps: ++example++ names a row of a table below; ${field} is a column of the scenario's Examples.

## Examples

### offers

| offer | card text | buttons | accepted result |
| --- | --- | --- | --- |
| ++handoff written++ | Session ending · handoff written to .sessions/checkout-flow/handoff-20261106T2340.md | Open handoff | the handoff opens in the Inspector |
| ++correction++ | Add the mistake and the correction to harness/.context/corrections.log? | Add entry, Skip | an entry is added to corrections.log |
| ++decision++ | Record it as a decision in harness/.context/cdr/? | Record decision, Skip | a decision record is written in cdr/ |

## Story: Write Handoff When Session Ends

### Evidence

| Source | Note |
|--------|------|
| `.sessions/_backlog/mod-ideas.md` | "Automatic handoff" |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: A handoff is written when the Person closes the session

*Given* checkout-flow is the active ticket  
  *And* work has been done in its session  
*When* the Person closes the session  
*Then* the chat panel says a handoff was written into checkout-flow's session folder  
  *And* it offers Open handoff

#### Scenario: Opening the written handoff shows it in the Inspector

*Given* the chat panel offers the ++handoff written++ card  
*When* the Person opens the handoff  
*Then* the handoff opens in the Inspector  
  *And* the card leaves the chat panel

## Story: Offer Correction Log Entry

### Evidence

| Source | Note |
|--------|------|
| `.sessions/_backlog/mod-ideas.md` | "Correction capture" |
| `.claude/rules/learning-from-corrections.md` | log only a miss in work just generated, in `corrections.log` beside that work |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: Rejecting generated work offers a correction entry

*Given* Claude has just generated checkout-flow's story map  
*When* the Person rejects the generated story map  
*Then* the chat panel offers to add the mistake to harness/.context/corrections.log  
  *And* it offers Add entry and Skip

#### Scenario: Changing work Claude did not just generate offers no correction

*Given* checkout-flow's story map was generated in an earlier session  
*When* the Person asks for a story to be renamed  
*Then* the chat panel offers no correction entry

#### Scenario Outline: The Person answers the correction offer

*Given* the chat panel offers the ++correction++ card  
*When* the Person chooses ${answer}  
*Then* ${result}  
  *And* the card leaves the chat panel

##### Examples

| answer | result |
| --- | --- |
| Add entry | an entry naming the mistake and the correction is added to corrections.log |
| Skip | corrections.log is unchanged |

## Story: Offer Decision Record

### Evidence

| Source | Note |
|--------|------|
| `.sessions/_backlog/mod-ideas.md` | "Correction capture": the same check spots a decision |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: Settling a question offers a decision record

*Given* a design question is open in checkout-flow's chat  
*When* the Person settles the question  
*Then* the chat panel offers to record the decision in harness/.context/cdr/  
  *And* it offers Record decision and Skip

#### Scenario: Recording the decision writes a CDR

*Given* the chat panel offers the ++decision++ card  
*When* the Person records the decision  
*Then* a decision record is written in harness/.context/cdr/ naming what was decided and why  
  *And* the card leaves the chat panel
