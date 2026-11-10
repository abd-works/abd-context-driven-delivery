---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Frame Design Canvas Screens In Explorer

### Domain terms

- ++design canvas screen++ — an artboard on the Claude Design canvas, drawn in the explorer's frame through `dc-import`.
- ++screenshot++ — a captured image of a screen, used when no design canvas screen runs for a step.

> In steps: ${field} is a column of the scenario's Examples.

## Examples

### which screen a step shows

| step has | its scenario has | its story has | frame shows |
| --- | --- | --- | --- |
| its own design canvas screen | any | any | the step's design canvas screen |
| none | a design canvas screen | any | the scenario's design canvas screen |
| none | none | a design canvas screen | the story's design canvas screen |
| none | none | none, but a screenshot | the screenshot |

## Story: Show Design Canvas Screen As Explorer Frame

### Evidence

| Source | Note |
|--------|------|
| `harness/design_canvas/.context/story-map.md` | Display Live Scenario Screen In Explorer (`_imports` in `nodes.py`) |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: The design canvas artboard fills the explorer's frame

*Given* Activate Ticket's Session Board screen is an artboard on the design canvas  
*When* the story explorer opens on Activate Ticket  
*Then* the Session Board design canvas artboard fills the explorer's frame  
  *And* it runs live, with its own buttons working

## Story: Choose The Screen For A Step

### Evidence

| Source | Note |
|--------|------|
| `harness/design_canvas/.context/story-map.md` | a step shows its own screen, else its scenario's, else its story's (`_screen_of` in `nodes.py`) |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario Outline: The frame shows the nearest design canvas screen for the step

*Given* a step has ${step has}  
  *And* its scenario has ${its scenario has}  
  *And* its story has ${its story has}  
*When* the explorer reaches that step  
*Then* the frame shows ${frame shows}

##### Examples

| step has | its scenario has | its story has | frame shows |
| --- | --- | --- | --- |
| its own design canvas screen | any | any | the step's design canvas screen |
| no screen | a design canvas screen | any | the scenario's design canvas screen |
| no screen | no screen | a design canvas screen | the story's design canvas screen |

## Story: Join A Step Without A Screen To The Next Step

### Evidence

| Source | Note |
|--------|------|
| `harness/design_canvas/.context/story-map.md` | `_story_entry` in `nodes.py` groups a step with no screen with the next one that has one |

#### Scenario: A step with no screen joins the next step that has one

*Given* Activate Ticket's step 2 has no design canvas screen of its own  
  *And* step 3 has one  
*When* the explorer lists Activate Ticket's steps  
*Then* steps 2 and 3 show as one entry  
  *And* picking it shows step 3's design canvas screen

## Story: Show A Screenshot When No Screen Runs

### Evidence

| Source | Note |
|--------|------|
| `harness/design_canvas/.context/story-map.md` | the step's screenshot when no prototype applies, skipping blank captures (`_blank` in `nodes.py`) |

#### Scenario: The frame shows the step's screenshot

*Given* a step has a screenshot  
  *But* no design canvas screen applies to it  
*When* the explorer shows that step  
*Then* the frame shows the step's screenshot

#### Scenario: A blank capture is skipped

*Given* a step's only screenshot is a blank capture  
  *But* no design canvas screen applies to it  
*When* the explorer shows that step  
*Then* the frame says there is no screen for this step yet

## Story: Keep Each Screen's Own Stylesheets

### Evidence

| Source | Note |
|--------|------|
| `harness/design_canvas/.context/story-map.md` | `_stylesheets` in `nodes.py` links every stylesheet the prototype screens use |

#### Scenario: A design canvas screen keeps its look inside the explorer

*Given* the Session Board design canvas screen links its own stylesheet  
*When* the explorer draws the Session Board screen  
*Then* the screen looks as it does on its own artboard  
  *And* the explorer's panel styles do not reach it
