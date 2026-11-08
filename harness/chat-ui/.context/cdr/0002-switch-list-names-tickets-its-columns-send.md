# The switch list names the tickets the board's columns send whole

`board.show` answers with the board's columns, each sending its tickets whole, and with `open_tickets`, the tickets a person can switch to, in column order. The chat bar's session list shows `open_tickets`, and `ChatBarClient.ticketNamed` finds each one among the columns' tickets by its name. Round 7 (R7-L1, round 6's L2) flagged finding the active ticket by its name; `Board.active` is now sent whole, so the chat bar reads the active session from it directly and no longer looks it up.

## Decision

Keep `open_tickets` as references (`@data_field(reference=True)`), resolved against the columns of the same answer.

- **Python decides which tickets are open.** `Board.open_tickets` holds the rule (a ticket in a stage, neither a backlog item nor a closed ticket). The chat bar only shows the list in the order Python sends it, so no rule moves into TypeScript.
- **Sending them whole would send every open ticket twice.** Each ticket carries its progress on every fidelity, with that fidelity's guidance and rules, and the columns already send each one whole. The chat bar reads `board.show` after every cdd call and every prompt, so doubling that answer costs every chat on every turn. The active ticket is one ticket, so sending it whole costs little and takes the lookup off the path every draw takes.
- **The name is a reference inside one answer, not a lookup in a registry.** The names and the tickets they name come from the same `board.show` answer, so a name never points at a ticket from another read.

## Consequences

If the board's answer stops sending tickets in its columns, or a second reader needs the open tickets whole, `open_tickets` should be sent whole and `ticketNamed` deleted. Renaming `open_tickets` or changing what a column sends means updating `chat-bar-client.ts` in the same change.
