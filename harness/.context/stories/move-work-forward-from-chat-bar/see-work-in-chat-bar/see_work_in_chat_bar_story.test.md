---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: See Work In Chat Bar

### Domain terms

- ++session card++ — the card the session name opens above the chat bar: the shown stage's fidelities under FIDELITY, each with its state, and the folders their practices write to.

## Story: Display Session Card

### Evidence

| Source | Note |
|--------|------|
| `.sessions/chat-ui-defects/chat-ui-defects.md` | Observed 2026-11-07: the card's folder list for Discovery showed harness five times instead of each folder once |
| `harness/chat-ui/pane/test/move-work-forward-from-chat-bar/see-work-in-chat-bar/display-session-card/display_session_card_story.test.ts` | the story test that plays these scenarios |

#### Scenario: List each folder once

*Given* checkout-flow is in Discovery with its five practices all writing under harness  
*When* the Person opens the session card for checkout-flow  
*Then* harness is listed once, beside the first fidelity  
  *And* every fidelity of Discovery is still listed

## Story: Add Active Ticket To System Prompt

#### Scenario: Name the active ticket and its next guidance in the system prompt

*Given* checkout-flow, titled Checkout flow, is the active [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card), in Discovery, with stories-story-map next
*When* a chat with the cdd-board mod loaded composes its system prompt
*Then* the system prompt holds CDD session board: you are working on ticket checkout-flow (Checkout flow), in Discovery. Its next guidance is stories-story-map.
*And* it says each fidelity goes through generate, validate, then review by a person

#### Scenario: Say a done ticket waits for a person to move it

*Given* the active [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) ready-to-move is in Discovery's Done with no next guidance
*When* the chat composes its system prompt
*Then* the system prompt says Its stage is done and waits for a person to move it.

#### Scenario: Add nothing with no active ticket

*Given* no [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) is active
*When* the chat composes its system prompt
*Then* the system prompt holds no session board section

## Story: Select Fidelity

### Evidence

| Source | Note |
|--------|------|
| `.sessions/chat-ui-defects/chat-ui-defects.md` | Observed 2026-11-07: in the card's FIDELITY list only the fidelity's name could be pressed; the coloured square and the whole line, status text included, pick that fidelity too |

#### Scenario: Pick a fidelity from anywhere on its line

*Given* the session card for checkout-flow is open  
*When* the Person presses the line of clean-engineering-model  
*Then* the press covers the square, the name and the state, the whole line  
  *And* clean-engineering-model is the fidelity the action button acts on
