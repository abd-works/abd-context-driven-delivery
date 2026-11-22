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
| `harness/chat-ui/pane/hooks/chat-bar/session-card-view.tsx` `FidelityCellView` | observed: one button holds the fidelity's coloured square and its name, and its press calls `toggleGuidance` for the fidelity's practice (`session.toggle_guidance`, part practice); the state after the name is plain text, and a button of its own only while the fidelity has violations, when its press opens the report. Settled 2026-11-22: the bar is right, and the scenario, which said the whole line picked the fidelity for the action button, was changed to match it |
| `harness/chat-ui/pane/test/move-work-forward-from-chat-bar/see-work-in-chat-bar/display-session-card/display_session_card_story.test.ts` | the story test that plays these scenarios |

#### Scenario: List each folder once

*Given* checkout-flow is in Discovery with its five practices all writing under harness  
*When* the Person opens the session card for checkout-flow  
*Then* harness is listed once, beside the first fidelity  
  *And* every fidelity of Discovery is still listed

## Story: Add Active Ticket To System Prompt

#### Scenario: Name the active ticket and its next guidance in the system prompt

*Given* checkout-flow, titled Checkout flow, is the active [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card), in Discovery, with stories-story-map next
*When* a chat with the cdd-board mod loaded composes its system prompt
*Then* the system prompt holds CDD session board: you are working on ticket checkout-flow (Checkout flow), in Discovery. Its next guidance is stories-story-map.
*And* it says each fidelity goes through generate, then validate

#### Scenario: Say a done ticket waits for a person to move it

*Given* the active [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) ready-to-move is in Discovery's Done with no next guidance
*When* the chat composes its system prompt
*Then* the system prompt says Its stage is done and waits for a person to move it.

#### Scenario: Add nothing with no active ticket

*Given* no [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) is active
*When* the chat composes its system prompt
*Then* the system prompt holds no session board section

#### Scenario: Name the ticket's text file in the system prompt

Intended (`.sessions/session-board/ticket-enhancements.md`, commit b08bfe47e: "A session's instructions refer to that file, so the board and the agent read the same text"); `Ticket.agent_context` does not name the file today.

*Given* checkout-flow is the active [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card)
*And* its session folder holds checkout-flow.md
*When* the chat composes its system prompt

```realization
checkout-flow.agent_context
  -> self.session.text_file
  <- the system prompt section naming .sessions/checkout-flow/checkout-flow.md
```

*Then* the system prompt names .sessions/checkout-flow/checkout-flow.md as the ticket's text
