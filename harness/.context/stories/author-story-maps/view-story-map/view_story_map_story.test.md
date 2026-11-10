---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: View Story Map

### Domain terms

- ++story map++ — epics, sub-epics and stories, drawn in lanes by the Story UI editor.
- ++node++ — an epic, sub-epic, story or scenario on the map.

> Evidence for this sub-epic: `C:\dev\story-ui\.context\story-map.md` (Intended stories of the Story UI app). The values below are examples, not observed data.

## Examples

### story maps in the workspace

| story map | file |
| --- | --- |
| ++checkout-flow story map++ | .sessions/checkout-flow/story-map.md |
| ++billing-report story map++ | .sessions/billing-report/story-map.md |

## Story: Pick Story Map From Dashboard

### Evidence

| Source | Note |
|--------|------|
| `C:\dev\story-ui\.context\story-map.md` | Story Map Dashboard for choosing which map to open |

#### Scenario: The dashboard lists every story map to pick from

*Given* the workspace holds the ++checkout-flow story map++ and the ++billing-report story map++  
*When* the Story Designer opens the dashboard  
*Then* both story maps are listed

#### Scenario: Picking a story map opens it

*Given* the dashboard lists both story maps  
*When* the Story Designer picks the ++billing-report story map++  
*Then* the editor opens the ++billing-report story map++

## Story: Browse Nested SubEpic Lanes

### Evidence

| Source | Note |
|--------|------|
| `C:\dev\story-ui\.context\story-map.md` | nested sub-epic lanes |

#### Scenario: A nested sub-epic shows its lanes under it

*Given* the epic Connect Sessions Across Channels And Apps holds the sub-epic Check Work In Generate  
*When* the Story Designer opens Check Work In Generate  
*Then* its stories show in a lane under it

## Story: Inspect Selected Node Fields

### Evidence

| Source | Note |
|--------|------|
| `C:\dev\story-ui\.context\story-map.md` | node inspector |

#### Scenario: Selecting a story shows its fields

*Given* the ++checkout-flow story map++ is open  
*When* the Story Designer selects the story Activate Ticket  
*Then* the inspector panel shows its name, actor and evidence

## Story: Show And Hide Scenarios And Examples

### Evidence

| Source | Note |
|--------|------|
| `C:\dev\story-ui\.context\story-map.md` | show and hide scenarios |

#### Scenario: Hiding scenarios leaves only the stories

*Given* the story Activate Ticket shows its scenarios and examples  
*When* the Story Designer hides scenarios  
*Then* the scenarios and examples are hidden  
  *And* the story card stays
