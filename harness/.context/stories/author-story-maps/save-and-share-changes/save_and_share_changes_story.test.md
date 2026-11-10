---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Save And Share Changes

### Domain terms

- ++save event++ — one record of a save of the story map, listed in its save history.
- ++view state++ — what is open, collapsed and selected in the editor.
- ++real-time session++ — two or more Story Designers on the same map at once.

> Evidence for this sub-epic: `C:\dev\story-ui\.context\story-map.md` (Intended stories of the Story UI app). The values below are examples, not observed data.

## Examples

### saves of the checkout-flow story map

| save | at | change |
| --- | --- | --- |
| ++first save++ | 6 Nov 21:00 | added Maintain Tickets |
| ++second save++ | 6 Nov 22:10 | renamed Ticket Archive |
| ++third save++ | 6 Nov 23:30 | split Move Ticket |

## Story: Test Story UI Editor On Session Story Map

### Evidence

| Source | Note |
|--------|------|
| `harness/.context/stories/story-map.md` | Requested 2026-11-06: each app tested on a real session before the board or chat bar invokes it |

#### Scenario: Each gap a spec finds becomes an Intended story

*Given* checkout-flow's session has a story map  
*When* the Agent runs the editor's specs on checkout-flow's story map  
*Then* every spec that fails names its gap  
  *And* each gap is added to the Story UI app's story map as an Intended story

## Story: Record One Save Event Per Save

### Evidence

| Source | Note |
|--------|------|
| `C:\dev\story-ui\.context\story-map.md` | one save event per save |

#### Scenario: A save records exactly one save event

*Given* the checkout-flow story map has unsaved changes to three stories  
*When* the Story Designer saves  
*Then* one save event is recorded for the three changes

## Story: Browse Save History

### Evidence

| Source | Note |
|--------|------|
| `C:\dev\story-ui\.context\story-map.md` | save history |

#### Scenario: The save history lists every save, newest first

*Given* the checkout-flow story map has the ++first save++, ++second save++ and ++third save++  
*When* the Story Designer opens the save history  
*Then* the three saves are listed, the ++third save++ first, each with its time and change

## Story: Recover Workspace View State

### Evidence

| Source | Note |
|--------|------|
| `C:\dev\story-ui\.context\story-map.md` | recover view state |

#### Scenario: Reopening the workspace restores the view

*Given* the Story Designer closed the workspace with Maintain Tickets open and Activate Ticket selected  
*When* the Story Designer reopens the workspace  
*Then* Maintain Tickets is open again  
  *And* Activate Ticket is selected

## Story: Join Real-Time Story Map Session

### Evidence

| Source | Note |
|--------|------|
| `C:\dev\story-ui\.context\story-map.md` | real-time story map session |

#### Scenario: Two designers see each other's changes as they happen

*Given* a second Story Designer has the checkout-flow story map open  
*When* the Story Designer opens the same story map  
*Then* each sees the other's changes as they happen

## Story: Reconcile Concurrent View State Changes

### Evidence

| Source | Note |
|--------|------|
| `C:\dev\story-ui\.context\story-map.md` | reconcile concurrent view state |

#### Scenario: Both designers' view changes are kept

*Given* two Story Designers are in a real-time session on the checkout-flow story map  
*When* one opens Maintain Tickets while the other collapses Steer Ticket Sessions  
*Then* both changes are kept for both designers
