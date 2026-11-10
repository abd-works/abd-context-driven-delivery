---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Steer Ticket Sessions

### Domain terms

- ++ticket chat++ — the Claude Code chat a ticket's session ran in.

## Story: Open Ticket Chat On Session Open

### Evidence

| Source | Note |
|--------|------|
| `.sessions/_backlog/suggest-the-next-step.md` | "open associated chat on session open / manually" |
| https://claude.ai/artifact/HCCiMNSTMhwB9zQT8tVV8p | the story explorer plays the first scenario on the integrated journey screen |

#### Scenario: Making a ticket active opens its chat

*Given* checkout-flow is the active ticket  
  *And* billing-report has a ticket chat  
*When* the Person makes billing-report the active ticket on the board  
*Then* billing-report's chat opens in the chat panel with the session  
  *And* the chat panel shows billing-report's last messages
