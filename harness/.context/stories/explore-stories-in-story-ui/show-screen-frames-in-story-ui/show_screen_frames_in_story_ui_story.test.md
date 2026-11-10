---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Show Screen Frames In Story UI

### Domain terms

- ++screen frame++ — the space under a story card on the story map that shows the story's design canvas screen.
- ++design canvas screen++ — an artboard on the Claude Design canvas that a story is shown on.

> In steps: ++example++ names a row of a table below; ${field} is a column of the scenario's Examples.

## Examples

### design canvas screens of checkout-flow's stories

| story | design canvas screen | frame shows |
| --- | --- | --- |
| ++Activate Ticket++ | Session Board | ▶ Session Board |
| ++Open Ticket Session++ | Ticket Details | ▶ Ticket Details |
| ++Move Ticket++ | none | no screen |

## Story: Switch Story Map To Screen Frames View

### Evidence

| Source | Note |
|--------|------|
| `harness/design_canvas/.context/story-map.md` | Show One Screen Thumbnail Under Each Story |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: Screen frames show under every story

*Given* checkout-flow's story map is open  
*When* the Person switches the story map to Screen frames  
*Then* a design canvas screen frame shows under each story

#### Scenario: Switching back hides the frames

*Given* checkout-flow's story map shows Screen frames  
*When* the Person switches Screen frames off  
*Then* the stories show without frames

## Story: Show Screen Frame Under Each Story

### Evidence

| Source | Note |
|--------|------|
| `harness/design_canvas/.context/story-map.md` | Show One Screen Thumbnail Under Each Story; Mark A Thumbnail With No Screenshot |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario Outline: Each story's frame names its design canvas screen

*Given* checkout-flow's story map shows Screen frames  
  *And* ${story} is shown on ${design canvas screen}  
*When* the story map draws ${story}  
*Then* ${story}'s frame shows ${frame shows}

##### Examples

| story | design canvas screen | frame shows |
| --- | --- | --- |
| Activate Ticket | the Session Board design canvas screen | ▶ Session Board |
| Open Ticket Session | the Ticket Details design canvas screen | ▶ Ticket Details |
| Move Ticket | no design canvas screen | no screen |

## Story: Mark Story Without A Screen

### Evidence

| Source | Note |
|--------|------|
| `harness/design_canvas/.context/story-map.md` | Mark A Thumbnail With No Screenshot |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: A story with no design canvas screen says so

*Given* checkout-flow's story map shows Screen frames  
  *But* ++Move Ticket++ has no design canvas screen  
*When* the story map draws ++Move Ticket++  
*Then* ++Move Ticket++'s frame says no screen  
  *And* exploring ++Move Ticket++ is disabled

## Story: Open Story Explorer From Screen Frame

### Evidence

| Source | Note |
|--------|------|
| `harness/design_canvas/.context/story-map.md` | Open The Story Explorer From A Thumbnail |
| artifact comment, 2026-11-06 | "this should be another pane that opens up; default pos is below the story map" |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: The story explorer opens as its own view below the story map

*Given* checkout-flow's story map shows Screen frames  
  *But* the story explorer is not open  
*When* the Person explores ++Activate Ticket++ from its frame  
*Then* the story explorer opens below the story map on ++Activate Ticket++  
  *And* its frame shows the Session Board artboard from the design canvas  
  *And* ++Activate Ticket++'s frame reads in explorer

#### Scenario: Exploring another story changes the open explorer

*Given* the story explorer is open on ++Activate Ticket++  
*When* the Person explores ++Open Ticket Session++ from its frame  
*Then* the explorer moves to ++Open Ticket Session++  
  *And* its frame shows the Ticket Details artboard from the design canvas
