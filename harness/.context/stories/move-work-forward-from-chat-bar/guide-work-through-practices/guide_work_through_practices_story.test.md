---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Guide Work Through Practices

### Domain terms

- ++files pane++ — the pane the chat bar opens beside the chat, as the CDD Kanban opens its files panel, holding a fidelity's files or its validation report.
- ++action button++ — the band's ▶ chip and its ▾ action list, which run an action on the fidelity the band shows.
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

## Story: View Fidelity Files

### Evidence

| Source | Note |
|--------|------|
| `.sessions/chat-ui-defects/chat-ui-defects.md` | Observed 2026-11-07: the Files button read story-map.md and story-map.drawio into the chat, over a 96,711 character session.read_file answer; files open in a window of their own, as the board's do |
| `harness/chat-ui/pane/test/move-work-forward-from-chat-bar/guide-work-through-practices/view-fidelity-files/view_fidelity_files_story.test.ts` | the story test that plays these scenarios |

#### Scenario: Open the files beside the chat, never in it

*Given* checkout-flow's clean-engineering-model declares chat-bar-model.md and chat-bar-model.drawio  
*When* the Person opens the files of clean-engineering-model  
*Then* the files pane opens beside the chat, titled clean-engineering-model files  
  *And* the chat bar above the prompt draws no file tab  
  *And* the diagram is never read as text

## Story: Read Validation Report From Chat Bar

### Evidence

| Source | Note |
|--------|------|
| `.sessions/chat-ui-defects/chat-ui-defects.md` | Observed 2026-11-07: opening stories-scenarios-20261107T001054.md showed it inside the chat interface; it opens in the side panel |

#### Scenario: Read the violations from their count

*Given* checkout-flow's clean-engineering-model has 7 violations in its latest validation report  
*When* the Person presses the count 7  
*Then* the report opens in its own tab of the side panel  
  *And* its text is drawn as markdown there, not in the chat

## Story: Invoke Next Fidelity Action

### Evidence

| Source | Note |
|--------|------|
| `.sessions/chat-ui-defects/chat-ui-defects.md` | Observed 2026-11-07: every action the chat bar sends must include the session param and the format param; with the story map picked, ▶ and its ▾ action list left the band |
| `harness/guidance_actions/guidance_actions.py` | every guidance action reads a `format=` word and a `session=` word from its guidance |

#### Scenario: Run the next action on the selected fidelity

*Given* checkout-flow's ux-mockup is generated and is the selected fidelity  
*When* the Person runs the next action  
*Then* /actions-validate ux-mockup in markdown, in checkout-flow's session, waits in the prompt box for the Person to send

#### Scenario: Keep the action button on a done fidelity

*Given* checkout-flow's stories-scenarios is done and is the selected fidelity  
*When* the Chat Bar draws checkout-flow  
*Then* the button still shows, offering the stage's first action, generate stories-scenarios  
  *And* its ▾ still opens the action list

## Story: Read Validation Report From Chat Bar (round 2)

### Evidence

| Source | Note |
|--------|------|
| `.sessions/chat-ui-defects/e2e/e2e-report.md` §4 | the chat bar's report tab showed no out-of-date notice; "Open in draw.io" submitted a prompt to the chat as the user |

#### Scenario: Say a report's saved graph is out of date in its tab

*Given* checkout-flow's clean-engineering-model has 7 violations in a report whose saved graph is out of date  
*When* the Person presses the count 7  
*Then* the report's tab says its saved graph is out of date  
  *And* Validate again puts clean-engineering-model's validate command in the prompt

#### Scenario: Open a diagram in the draw.io editor

*Given* the tab pane/.context/chat-bar-model.drawio is open  
*When* the Person opens the diagram in draw.io  
*Then* the draw.io viewer opens on pane/.context/chat-bar-model.drawio, and nothing is sent to the chat

## Story: List Available Patterns

### Evidence

| Source | Note |
|--------|------|
| User, 2026-11-11 | "opens a list box for LERN, MERN eg all patterns we have (how can we set this list dynamically based on contents of folder)" |
| `cdd_guidance/patterns/__init__.py` | registers each pattern with `PatternOverlays.register` |
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

