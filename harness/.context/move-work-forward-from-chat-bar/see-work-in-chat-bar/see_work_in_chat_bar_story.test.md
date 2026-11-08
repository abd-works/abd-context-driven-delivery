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
