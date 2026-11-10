---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Play Stories In The Explorer

### Domain terms

- ++story explorer++ — the view that plays a story's steps on its design canvas screen.
- ++step++ — one Given, When or Then of a scenario; the explorer moves through them in order.

> In steps: ${field} is a column of the scenario's Examples.

## Examples

### Activate Ticket's steps and what the design canvas frame shows

| step | text | frame shows |
| --- | --- | --- |
| 1 | Given checkout-flow is the active ticket, on its own branch pushed to origin | Checkout flow outlined |
| 4 | Then a dialog offers commit and push, chosen, and merge, not chosen | the switch dialog |
| 6 | Then billing-report is the active ticket with a thick orange outline | Billing report outlined |

## Story: Play The Next Story

### Evidence

| Source | Note |
|--------|------|
| `harness/design_canvas/.context/story-map.md` | the explorer's Play next button (`explorer.dc.html`) |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario Outline: Playing on moves to the next step and its design canvas frame

*Given* the story explorer shows Activate Ticket at step ${from}  
*When* the Person plays the next step  
*Then* step ${step} is selected  
  *And* the design canvas frame shows ${frame shows}

##### Examples

| from | step | frame shows |
| --- | --- | --- |
| 3 | 4 | the switch dialog |
| 5 | 6 | Billing report outlined |

#### Scenario: Playing past the last step moves to the next story

*Given* the story explorer shows Activate Ticket at its last step  
*When* the Person plays the next step  
*Then* the explorer moves to the next story's first step

## Story: Hide And Show The Story Panel

### Evidence

| Source | Note |
|--------|------|
| `harness/design_canvas/.context/story-map.md` | the » and « buttons (`explorer.dc.html`) |

#### Scenario: Hiding the story panel gives the frame the whole explorer

*Given* the story explorer shows its story panel  
*When* the Person hides the story panel  
*Then* the design canvas screen fills the explorer

#### Scenario: Showing the panel again keeps the selected step

*Given* the story panel is hidden at Activate Ticket's step 4  
*When* the Person shows the story panel  
*Then* the panel shows Activate Ticket's step 4 selected

## Story: Return To Story UI Map

### Evidence

| Source | Note |
|--------|------|
| artifact comment, 2026-11-06 | the story explorer is its own view; closing it leaves the story map |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: Closing the explorer leaves the story map where it was

*Given* the story explorer is open below checkout-flow's story map  
*When* the Person closes the story explorer  
*Then* the explorer closes  
  *And* the story map stays where it was, with Screen frames still on

## Story: Test Story Explorer On Session Story Map

### Evidence

| Source | Note |
|--------|------|
| `harness/.context/stories/story-map.md` | Requested 2026-11-06: each app tested on a real session before the board or chat bar invokes it |

#### Scenario: Each gap a spec finds becomes an Intended story

*Given* checkout-flow's session has a story map with scenarios  
*When* the Agent runs the explorer's specs on checkout-flow's story map  
*Then* every spec that fails names its gap  
  *And* each gap is added to the Story UI app's story map as an Intended story
