---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Steer Sessions

### Domain terms

- ++handoff++ — a note in the session folder saying what was done and what to do next.

## Story: Display Latest Session Handoff

### Evidence

| Source | Note |
|--------|------|
| `harness/.context/story-map-v2.md` | Requested 2026-11-06: the chat bar shows the active session's latest handoff, as the Session Board does |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: Opening a session shows its latest handoff in the chat panel

*Given* checkout-flow's session folder holds handoffs from 5 and 6 November  
*When* the Person opens the checkout-flow session  
*Then* the chat panel shows the 6 November handoff's next step and open violations  
  *And* it offers Open handoff

#### Scenario: A session with no handoff shows none

*Given* billing-report's session folder holds no handoff  
*When* the Person opens the billing-report session  
*Then* the chat panel shows no handoff card
