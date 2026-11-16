---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Navigate The Story Tree

### Domain terms

- ++story tree++ — the story explorer's panel: epic, sub-epic, story, scenario and step, each collapsible.
- ++open request++ — text naming a story's or scenario's `path:line`, which an agent uses to open it in the file viewer.

> In steps: ++example++ names a row of a table below; ${field} is a column of the scenario's Examples.

## Examples

### explorer links

| link | story | scenario | step |
| --- | --- | --- | --- |
| ++Activate Ticket's first step++ | Activate Ticket | Activate a ticket with no branch | 1 |
| ++Open Ticket Session's first step++ | Open Ticket Session | Open the ticket's session | 1 |

## Story: Open The Explorer At A Story, Scenario And Step

### Evidence

| Source | Note |
|--------|------|
| `harness/design_canvas/.context/story-map.md` | Open The Explorer At A Story, Scenario And Step (`explorer.dc.html`) |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario Outline: The explorer opens at the story, scenario and step it was sent to

*Given* checkout-flow's stories have design canvas screens  
*When* the Person opens the explorer at ${story}, scenario "${scenario}", step ${step}  
*Then* the story tree selects ${story} › ${scenario} › step ${step}  
  *And* the frame shows that step's design canvas screen

##### Examples

| story | scenario | step |
| --- | --- | --- |
| Activate Ticket | Activate a ticket with no branch | 1 |
| Activate Ticket | Activate a ticket with no branch | 4 |
| Open Ticket Session | Open the ticket's session | 1 |

## Story: Collapse And Reset The Story Tree

### Evidence

| Source | Note |
|--------|------|
| `harness/design_canvas/.context/story-map.md` | the explorer's Collapse all and Reset buttons (`explorer.dc.html`) |

#### Scenario: Collapse all closes the tree to its epics

*Given* the story tree is open at ++Activate Ticket's first step++  
*When* the Person collapses the whole story tree  
*Then* the tree shows only its epics

#### Scenario: Reset returns the tree to its first story

*Given* the story tree is open at ++Open Ticket Session's first step++  
*When* the Person resets the story tree  
*Then* the tree selects the first story's first step

## Story: Keep The Selected Story In View

### Evidence

| Source | Note |
|--------|------|
| `harness/design_canvas/.context/story-map.md` | the explorer scrolls the selected entry into view (`explorer.dc.html`) |

#### Scenario: The selected story scrolls into view

*Given* the story tree is longer than its panel  
*When* the selection moves to a story below the panel's edge  
*Then* the selected story scrolls into view

## Story: Copy A Request To Open A Story In Its File

### Evidence

| Source | Note |
|--------|------|
| `harness/design_canvas/.context/story-map.md` | `copyOpenRequest` in `explorer.dc.html`; each story and scenario carries its `path:line` |

#### Scenario: The open request names the story's file and line

*Given* Activate Ticket's scenarios are in its scenarios file at line 12  
*When* the Person copies Activate Ticket's open request  
*Then* the copied request names Activate Ticket's scenarios file and line 12

## Story: Pick An Outline Scenario's Example

### Evidence

| Source | Note |
|--------|------|
| `harness/design_canvas/.context/story-map.md` | Intended (`claude_design.md` outline-rows): the explorer does not list example rows yet |

#### Scenario: Picking an example loads it on the design canvas screen

*Given* a scenario outline in the story tree has three examples  
*When* the Person picks the second example  
*Then* the design canvas screen loads the second example's values
