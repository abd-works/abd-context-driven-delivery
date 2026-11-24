---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Choose Session Practices And Overlays In Chat Bar

### Domain terms

- ++pattern++ — a stack pattern under `cdd_guidance/patterns/`, such as lern_domain_driven, that a session's graph can apply on top of the practices (`PatternOverlays`).
- ++overlay++ — a pattern the session has chosen; its graph applies it, and the chat bar shows its icon.
- ++overlay icon++ — the pattern's first and last letter in capitals, shown on the chat bar after the + and before the format chips.

> In steps: ++example++ names a row of a table below.

## Examples

### patterns

| pattern | icon |
| --- | --- |
| ++cdd_claude_mod++ | CD |
| ++cdd_web_domain_access++ | CS |
| ++lern_domain_driven++ | LN |
| ++mern_domain_driven++ | MN |

## Story: List Available Patterns

### Evidence

| Source | Note |
|--------|------|
| User, 2026-11-11 | "opens a list box for LERN, MERN eg all patterns we have (how can we set this list dynamically based on contents of folder)" |
| `cdd_guidance/patterns/__init__.py` | registers each pattern with `REGISTERED_PATTERNS.register` |
| `harness/graph/pattern_overlays.py` | `PatternOverlays` holds the registered pattern classes by their `pattern` name |

#### Scenario: Offer every pattern the patterns folder holds

*Given* the patterns folder holds ++cdd_claude_mod++, ++cdd_web_domain_access++, ++lern_domain_driven++ and ++mern_domain_driven++, each defining its pattern  
  *And* checkout-flow's session has chosen no overlays  
*When* the chat bar asks checkout-flow for its overlay choices  
*Then* it receives one choice per pattern in name order, each with its ++overlay icon++  
  *And* none of them is chosen  
  *And* the Person goes on to Choose Graph Overlays

#### Scenario: Leave out a folder that defines no pattern

*Given* the patterns folder also holds domain_driven_stack, which defines no pattern of its own  
*When* the chat bar asks checkout-flow for its overlay choices  
*Then* domain_driven_stack is not among them

## Story: Choose Graph Overlays

### Evidence

| Source | Note |
|--------|------|
| User, 2026-11-11 | "right after practices we need + overlay button where we can add one or more graph overlays ... can select more than one" |
| `harness/graph/graph.py` | `Graph.overlays` applies the patterns named; validate checks the rules they add |

#### Scenario: Choose a pattern as the session's overlay

*Given* checkout-flow's session has chosen no overlays  
*When* the Person chooses ++lern_domain_driven++ as an overlay of checkout-flow  
*Then* checkout-flow's overlay choices show ++lern_domain_driven++ chosen  
  *And* checkout-flow's session.json keeps lern_domain_driven among its overlays  
  *And* the chat bar goes on to Display Overlay Icons

#### Scenario: Choose a second pattern beside the first

*Given* checkout-flow's session has chosen ++lern_domain_driven++  
*When* the Person also chooses ++cdd_web_domain_access++  
*Then* checkout-flow's overlay choices show lern_domain_driven and cdd_web_domain_access chosen

#### Scenario: Take a chosen pattern out

*Given* checkout-flow's session has chosen ++lern_domain_driven++ and ++cdd_web_domain_access++  
*When* the Person takes lern_domain_driven out of checkout-flow's overlays  
*Then* checkout-flow's overlay choices show only cdd_web_domain_access chosen

#### Scenario: Apply the chosen overlays to the session's graph

*Given* checkout-flow's session has its graph open with no overlays  
*When* the Person chooses ++lern_domain_driven++ as an overlay of checkout-flow  
*Then* checkout-flow's graph applies lern_domain_driven

#### Scenario: Refuse a name that is no pattern

*Given* checkout-flow's session has chosen no overlays  
*When* the Person chooses astrology as an overlay of checkout-flow  
*Then* the choice is refused, naming astrology as no pattern  
  *But* checkout-flow's overlays are not changed

Intended: the request names no refusal; a name that is no pattern would otherwise be kept as an overlay that applies nothing.

## Story: Display Overlay Icons

### Evidence

| Source | Note |
|--------|------|
| User, 2026-11-11 | "adds a new icon to bar, pushing action and format", "icon is first and last letter of pattern" |
| `harness/chat-ui/pane/hooks/chat-bar/chat-bar-view.tsx` | `LineView` draws the fidelity dots, the format chips, then the action button |

#### Scenario: Show each overlay's icon between the + and the format chips

*Given* checkout-flow's session has chosen ++lern_domain_driven++ and ++cdd_web_domain_access++  
*When* the chat bar draws checkout-flow's line  
*Then* after the fidelity dots it shows the +, then LN and CS  
  *And* the format chips and the action button follow them  
  *And* LN names lern_domain_driven on hover

#### Scenario: Show only the + with no overlay chosen

*Given* checkout-flow's session has chosen no overlays  
*When* the chat bar draws checkout-flow's line  
*Then* the + follows the fidelity dots with no overlay icon after it

Evidence still missing: the chat bar's TypeScript story tests were removed in commit 8c56ab052, so this story's drawing is checked by eye on the live chat bar; its icons and choices come from the Ticket, whose answers the Python acceptance tests check.

## Story: Choose Session Practices

### Evidence

| Source | Note |
|--------|------|
| `harness/chat-ui/pane/hooks/chat-bar/session-card-view.tsx` `FidelityCellView` | observed: one button holds the fidelity's coloured square and its name, and its press calls `toggleGuidance` for the fidelity's practice (`session.toggle_guidance`, part practice) |
| `.sessions/chat-ui-defects/chat-ui-defects.md` | Observed 2026-11-07: in the card's FIDELITY list only the fidelity's name could be pressed; the coloured square and the whole line, status text included, pick that fidelity too. Settled 2026-11-22: the press turns the fidelity's practice on or off, and Select Fidelity keeps picking a fidelity from the dots on the line |

#### Scenario: Turn a fidelity's practice on or off from its square and name

*Given* the session card for checkout-flow is open, with Clean Engineering on for the session  
*When* the Person presses the square or the name of clean-engineering-model  
*Then* Clean Engineering is turned off for checkout-flow, and a second press turns it on again  
  *And* the press covers the square and the name, not the state after them  
  *And* the state of a fidelity with violations is a button of its own, whose press opens the validation report
