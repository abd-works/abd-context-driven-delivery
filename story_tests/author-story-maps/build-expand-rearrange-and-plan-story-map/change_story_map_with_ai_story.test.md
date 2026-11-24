---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Author Story Changes With AI

### Domain terms

- ++AI chat panel++ — a chat beside the story map that takes requests for map changes.
- ++proposal++ — the map changes the AI suggests, shown before they apply.

> Evidence for this sub-epic: `C:\dev\story-ui\.context\story-map.md` (Intended stories of the Story UI app). The values below are examples, not observed data.

## Examples

### proposals

| proposal | change |
| --- | --- |
| ++split Move Ticket++ | Move Ticket becomes Move Ticket Forward and Move Ticket Back |

## Story: Open AI Chat Panel

### Evidence

| Source | Note |
|--------|------|
| `C:\dev\story-ui\.context\story-map.md` | AI chat panel |

#### Scenario: The AI chat opens beside the story map

*Given* the checkout-flow story map is open  
*When* the Story Designer opens the AI chat  
*Then* the AI chat panel opens beside the map

## Story: Request AI Story Change

### Evidence

| Source | Note |
|--------|------|
| `C:\dev\story-ui\.context\story-map.md` | request an AI story change |

#### Scenario: A request becomes a proposal

*Given* the AI chat panel is open on the checkout-flow story map  
*When* the Story Designer asks for Move Ticket to be split  
*Then* the AI proposes ++split Move Ticket++

## Story: Review Proposed Map Changes

### Evidence

| Source | Note |
|--------|------|
| `C:\dev\story-ui\.context\story-map.md` | review proposed changes |

#### Scenario: Each proposed change shows before it applies

*Given* the AI has proposed ++split Move Ticket++  
*When* the Story Designer opens the proposal  
*Then* Move Ticket shows as replaced by Move Ticket Forward and Move Ticket Back  
  *But* the story map is not changed yet

## Story: Apply AI Change To Story Map

### Evidence

| Source | Note |
|--------|------|
| `C:\dev\story-ui\.context\story-map.md` | apply an AI change |

#### Scenario: Accepting the proposal writes it to the story map

*Given* the Story Designer has reviewed ++split Move Ticket++  
*When* the Story Designer accepts it  
*Then* Move Ticket Forward and Move Ticket Back replace Move Ticket on the story map

#### Scenario: Rejecting the proposal leaves the story map as it was

*Given* the Story Designer has reviewed ++split Move Ticket++  
*When* the Story Designer rejects it  
*Then* Move Ticket stays on the story map
