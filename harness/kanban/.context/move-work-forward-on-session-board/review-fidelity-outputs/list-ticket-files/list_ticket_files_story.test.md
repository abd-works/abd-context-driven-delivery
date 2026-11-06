# (E) Move Work Forward On Session Board
## (E) Review Fidelity Outputs
### (S) Person --> List Ticket Files

#### Scenario: List a fidelity's files with whether each exists

*Given* checkout-flow's story map .context/story-map.md is there and .context/story-map.drawio is not
*When* the Person lists checkout-flow's story_map files
*Then* the files panel lists .context/story-map.md as there
*But* no file of another fidelity is listed

#### Scenario: List only what the ticket's branch changed

*Given* the [ticket](../../../kanban-model.md#ticket--card) pet-visits works on the whole [repository](../../../kanban-model.md#repo) on its own branch pet-visits
*And* the repository holds src/theirs_spec.py and its branch added src/mine_spec.py
*When* the Person lists pet-visits' bdd behavior files
*Then* the files panel lists src/mine_spec.py
*But* src/theirs_spec.py is not listed

#### Scenario: Say in a toast when the list cannot be read

*Given* the board shows no ticket named no-such-ticket
*When* the Person lists no-such-ticket's story_map files
*Then* a toast says cdd fidelity-progress.files failed: TicketNotFoundError: no ticket named 'no-such-ticket' on the board
*But* no panel opens
