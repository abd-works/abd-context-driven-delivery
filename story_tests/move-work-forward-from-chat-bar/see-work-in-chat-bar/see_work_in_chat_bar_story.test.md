---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: See Work In Chat Bar

### Domain terms

- ++session card++ — the card the session name opens above the chat bar: the shown stage's fidelities under FIDELITY, each with its state, and the folders their practices write to.

## Story: Display Stage Strip

### Evidence

| Source | Note |
|--------|------|
| `harness/chat-ui/pane/hooks/chat-bar/chat-bar-view.tsx` `LineView`, `FidelityColumnView` | observed in the code, 2026-11-23: the order of the line |
| `harness/chat-ui/pane/hooks/chat-bar/chat-bar-draw.test.ts` | the plugin test that plays Show why the bar did not draw |
| `.sessions/_backlog/chat-ui-defects.md` "No chat bar and no queue above the prompt after a dev lane repin and /reload-plugins" | reported 2026-11-19: no bar and no red line after a reload |

#### Scenario: Show the active session's stage strip on one line

*Given* checkout-flow is the active [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card), in Discovery
*When* the Chat Bar draws above the prompt
*Then* one line shows the stage icons, then the practice dots, the overlay and format chips, the action button, and the files, handoff and debug buttons
  *And* at its right the line shows checkout-flow's name, the session buttons, the server health mark and the CDD version badge

#### Scenario: Show only the session name, health and version with no active session

*Given* no [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) is active for the chat
*When* the Chat Bar draws above the prompt
*Then* the line shows the session name, the server health mark and the CDD version badge
  *And* it shows no stage icons, practice dots or action button

#### Scenario: Show why the bar did not draw

*Given* checkout-flow is the active [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card)
  *But* the CDD version the bar stored cannot be read after a reload of the mod
*When* the Chat Bar draws above the prompt
*Then* the bar shows "chat bar failed to draw:" in red, with the reason the read gave, in place of the line

## Story: Display Session Fidelity Dots

### Evidence

| Source | Note |
|--------|------|
| `harness/chat-ui/pane/hooks/chat-bar/chat-bar-view.tsx` `PracticeDotView`, `fidelity-progress-client.ts` `PracticeDotClient` | observed in the code, 2026-11-23: one dot per practice, not per fidelity |

#### Scenario: Show one dot for each practice of the shown stage

*Given* checkout-flow is the active [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card), in Discovery, with Stories and DDD turned on for its session
  *And* its story-map is validated while its bounded-context is not generated
*When* the Chat Bar draws the practice dots
*Then* a Stories square shows in Stories' colour, shaded as validated
  *And* a DDD square shows in DDD's colour, shaded as not generated
  *And* hovering the Stories square shows story-map above it

#### Scenario: Show a practice's violations beside its dot

*Given* checkout-flow's story-map has 3 violations from its last validate
*When* the Chat Bar draws the practice dots
*Then* 3 shows in red beside the Stories square
*When* the Person opens the violations of the Stories practice
*Then* story-map's validation report opens

#### Scenario: Draw a practice turned off faint, with no violations

*Given* checkout-flow's session has UX turned off
  *And* its ia has 2 violations
*When* the Chat Bar draws the practice dots
*Then* the UX square is faint
  *And* no violation count shows beside it

#### Scenario: Turn a practice on or off for the session

*Given* checkout-flow's session has DDD turned on
*When* the Person turns DDD off from its dot
*Then* checkout-flow's session holds DDD turned off
  *And* the DDD square is faint

#### Scenario: Say why a practice was not turned on or off

*Given* the cdd server refuses to change checkout-flow's guidance selection
*When* the Person turns DDD off from its dot
*Then* the failure line says "The ddd practice was not changed" with the server's reason and a Fix button

## Story: Display Session Card

### Evidence

| Source | Note |
|--------|------|
| `harness/chat-ui/pane/hooks/chat-bar/session-card-view.tsx` `FidelityCellView` | observed: one button holds the fidelity's coloured square and its name, and its press calls `toggleGuidance` for the fidelity's practice (`session.toggle_guidance`, part practice); the state after the name is plain text, and a button of its own only while the fidelity has violations, when its press opens the report. Settled 2026-11-22: the bar is right, and the scenario, which said the whole line picked the fidelity for the action button, was changed to match it |
| `harness/chat-ui/pane/test/move-work-forward-from-chat-bar/see-work-in-chat-bar/display-session-card/display_session_card_story.test.ts` (removed in 8c56ab052) | the stubbed story test these scenarios were written for; no test plays them now |

#### Scenario: List each folder once

*Given* checkout-flow is in Discovery with its five practices all writing under harness  
*When* the Person opens the session card for checkout-flow  
*Then* harness is listed once, beside the first fidelity  
  *And* every fidelity of Discovery is still listed

## Story: Show Active Session On Status Line

### Evidence

| Source | Note |
|--------|------|
| `harness/chat-ui/pane/hooks/register.ts` `PromptHint` hook and `showStatus`, `chat-bar-client.ts` `statusLine` | observed in the code, 2026-11-23 |
| `.sessions/_backlog/chat-ui-defects.md` "The status line under the prompt went missing after a cdd reinstall" | reported 2026-11-13: gone after a repin, a restart and /reload-plugins |

#### Scenario: Name the repository, branch and folder under the prompt

*Given* checkout-flow is the active [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card), on branch checkout-flow of repository shop, working in C:/dev/shop-checkout-flow/src
*When* the chat draws the hint line under the prompt
*Then* after the engine's own hint the line shows shop\checkout-flow  C:/dev/shop-checkout-flow/src
  *And* the status line below the chat shows the same

#### Scenario: Leave the hint line as the engine wrote it with no active session

*Given* no [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) is active for the chat
*When* the chat draws the hint line under the prompt
*Then* the hint line holds only what the engine writes there

#### Scenario: Keep the status line while the board does not answer

*Given* the hint line shows shop\checkout-flow  C:/dev/shop-checkout-flow/src
  *But* the cdd server is restarting and does not answer the next board read
*When* the chat draws the hint line under the prompt
*Then* the hint line still shows shop\checkout-flow  C:/dev/shop-checkout-flow/src
  *And* the chat bar says the board did not load

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
