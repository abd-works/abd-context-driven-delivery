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

#### Scenario: The open request of a scenario a story test in code writes names the line of its call

Observed (`cdd_guidance/practices/ux/model/claude_design/bookshop_explorer_spec.py`). Defect widget-6.

*Given* Pack Order's scenario Pack a paid order is written in ++pack_order_story.test.py++ by its `scenario` call  
*When* the Person copies Pack a paid order's open request  
*Then* the copied request names ++pack_order_story.test.py++ and the line of that `scenario` call

#### Scenario: Each row of a scenario a shared story file and its screen spec both write opens its own file

Observed (`bookshop_explorer_spec.py`). Defect widget-6.

*Given* Cancel Order's scenario Cancel a submitted order is written in ++confirm-order.story.shared.ts++ and in ++confirm-order.story.ui.spec.ts++  
*When* the Person copies the open request of each of its two rows  
*Then* one request names ++confirm-order.story.shared.ts++ and the other ++confirm-order.story.ui.spec.ts++, each at the line of its call  
  *And* Cancel Order's own open request names ++confirm-order.story.shared.ts++ at its `story` call

## Story: Pick An Outline Scenario's Example

### Evidence

| Source | Note |
|--------|------|
| `harness/design_canvas/.context/story-map.md` | Intended (`claude_design.md` outline-rows): the explorer does not list example rows yet |

#### Scenario: Picking an example loads it on the design canvas screen

*Given* a scenario outline in the story tree has three examples  
*When* the Person picks the second example  
*Then* the design canvas screen loads the second example's values

## Story: Open A Step's Domain Term As Its Class Card

### Evidence

| Source | Note |
|--------|------|
| `cdd_guidance/practices/ux/model/claude_design/class_cards.py` | `ClassCard.from_section` reads the card from the class model section the term links to (commit 9a3cd7d28) |
| `cdd_guidance/practices/ux/model/claude_design/class_cards_spec.py` | exploratory-testing defect widget-7 |

#### Scenario: A step's domain term opens its class card

Observed (`cdd_guidance/practices/ux/model/claude_design/story_explorer_heavy_spec.py`, commit 9a3cd7d28).

*Given* Add Book To Cart's step names the domain term ++Cart++, linked to the Cart heading of the bookshop's class model  
*When* the Person opens the term ++Cart++ in the step  
*Then* Cart's class card shows below the story tree, with Cart's properties and operations

#### Scenario: A class card shows the model's words without their markdown marks

Observed (`class_cards_spec.py`). Defect widget-7: the card showed `**Cart** «Aggregate Root»` and `*Cart*`.

*Given* the bookshop's class model writes the Cart heading as `**Cart** «Aggregate Root»` and its lines with `*Cart*` and `**Lines.**`  
*When* the Person opens the term ++Cart++ in a step  
*Then* the card's title reads Cart «Aggregate Root»  
  *And* its lines read Cart and Lines. as plain words
