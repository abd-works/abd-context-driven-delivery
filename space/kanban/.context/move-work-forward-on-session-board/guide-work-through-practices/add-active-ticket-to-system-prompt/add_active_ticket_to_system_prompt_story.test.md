# (E) Move Work Forward On Session Board
## (E) Guide Work Through Practices
### (S) Board App --> Add Active Ticket To System Prompt

#### Scenario: Name the active ticket and its next guidance in the system prompt

*Given* checkout-flow, titled Checkout flow, is the active [ticket](../../../kanban-model.md#ticket--card), in Discovery, with stories-story-map next
*When* a chat with the cdd-board mod loaded composes its system prompt
*Then* the system prompt holds CDD session board: you are working on ticket checkout-flow (Checkout flow), in Discovery. Its next guidance is stories-story-map.
*And* it says each fidelity goes through generate, validate, then review by a person

#### Scenario: Say a done ticket waits for a person to move it

*Given* the active [ticket](../../../kanban-model.md#ticket--card) ready-to-move is in Discovery's Done with no next guidance
*When* the chat composes its system prompt
*Then* the system prompt says Its stage is done and waits for a person to move it.

#### Scenario: Add nothing with no active ticket

*Given* no [ticket](../../../kanban-model.md#ticket--card) is active
*When* the chat composes its system prompt
*Then* the system prompt holds no session board section
