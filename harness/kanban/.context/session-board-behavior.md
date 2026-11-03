---
fidelity: [behavior]
artifact: [bdd-behavior]
format: md
section: body
---

# BDD Behavior — Session Board

Fidelity: behavior

Each section is one Story on the [story map](story-map.md) and lists the spec signatures that make it executable: the spec file, then the `describe`, `that`, `with`, and `it should` names as they are written there. The story map says what each Story does and whether it is observed or inferred; this file says which signatures press it. A Story with no section here has no spec yet.

Spec files: `board-client.spec`, `ticket-client.spec`, `tile-client.spec`, `side-panel-client.spec`, `activation-client.spec`, `backlog-item-client.spec`, `root-choice-client.spec`, `chat-client.spec`, and `help-text.spec` in `harness/kanban/app/src/kanban/`; `story-actions.spec` in `harness/kanban/app/tests/`; `wip_limits.spec.shared`, `move_ticket.spec.shared`, and `move_ticket.behavior.e2e` under `harness/kanban/app/tests/kanban/`; `kanban_spec` and `kanban_tools_spec` in `harness/kanban/`.

## behavior driven development:

# (E) Display Board And Details For Repo

### Display Board

```
board-client.spec   describe Display Board
board-client.spec   describe Display Connected Status
story-actions.spec  describe Display Connected Status
board-client.spec   describe Refresh Board After Tool Calls
side-panel-client.spec  describe Refresh Board After Tool Calls
tile-client.spec    describe Refresh Board After Tool Calls
story-actions.spec  describe Refresh Board After Tool Calls
board-client.spec   describe Announce Ticket Changes
```

### Arrange Board And Details

```
board-client.spec   describe Arrange Board And Details
story-actions.spec  describe Arrange Board And Details
board-client.spec   describe Resize Board And Details
board-client.spec   describe Expand Board Or Details
```

### Display Backlog Items As Tickets

```
kanban_spec  it should show each backlog item in the Backlog column
```

### Display Ticket Card

```
board-client.spec  describe Display Ticket Card
kanban_spec  it should show every work session as a ticket
kanban_spec  it should leave main off the board
kanban_spec  it should be in Specification
kanban_spec  it should name the ticket of the current session as active
```

### Display Ticket Details

```
board-client.spec   describe Display Ticket Details
ticket-client.spec  describe Display Ticket Details
story-actions.spec  describe Display Ticket Details
story-actions.spec  it should show the ticket of a card pressed anywhere
board-client.spec   it should show the active ticket with no card pressed
kanban_tools_spec   it should show that fidelity's latest report
tile-client.spec    describe Expand Ticket
story-actions.spec  describe Expand Ticket
```

### Set Stage WIP Limit

```
board-client.spec   describe Set Stage WIP Limit
story-actions.spec  describe Set Stage WIP Limit
wip_limits.spec.shared  it should give every stage a limit of 3 tickets until a person sets one
```

### Arrange Side Panel

```
side-panel-client.spec  describe Arrange Side Panel
story-actions.spec      describe Arrange Side Panel
side-panel-client.spec  describe Resize Side Panel
side-panel-client.spec  describe Expand Side Panel
side-panel-client.spec  describe Close Side Panel
story-actions.spec      it should keep the columns' width and scroll them sideways when a panel opens
```

# (E) Steer Ticket Sessions

### Add Backlog Item

```
backlog-item-client.spec  describe Add Backlog Item
story-actions.spec        describe Add Backlog Item
kanban_tools_spec         that adds a backlog item
backlog-item-client.spec  describe Start Backlog Item
kanban_tools_spec         that starts the item again
```

### Open Ticket Session

```
kanban_tools_spec   that opens a new ticket
kanban_tools_spec   that opens a ticket on a folder in the repository
root-choice-client.spec  describe Choose Session Root
story-actions.spec       describe Choose Session Root
```

### Close Active Session

```
activation-client.spec  describe Close Active Session
story-actions.spec      describe Close Active Session
kanban_tools_spec       it should show the ticket in Complete
kanban_tools_spec       it should leave no ticket active
```

### Restrict Actions To Active Session

```
ticket-client.spec  describe Restrict Actions To Active Session
story-actions.spec  describe Restrict Actions To Active Session
```

### Move Ticket

```
ticket-client.spec  describe Move Ticket
move_ticket.spec.shared
kanban_tools_spec   it should show the ticket in the next stage
kanban_tools_spec   it should show the ticket in Discovery's Done
kanban_tools_spec   it should close the ticket
kanban_tools_spec   it should reopen the ticket in Implementation
kanban_tools_spec   it should show an item in the Backlog with the ticket's title
move_ticket.behavior.e2e  it should say in a toast that it moved to the Backlog
```

### Activate Ticket

```
activation-client.spec  describe Activate Ticket
story-actions.spec      describe Activate Ticket
activation-client.spec  it should offer commit and push on leaving and open with merge off
kanban_tools_spec       it should create the ticket's branch when a ticket that has none is activated
activation-client.spec  it should offer a branch to a ticket that has none
```

### Split Ticket Into Child Tickets

```
kanban_tools_spec   it should name the ticket it was split from
ticket-client.spec  it should name a split ticket by its parent
```

### Archive Ticket

```
kanban_spec  that has been archived
```

### Write Ticket Handoff

```
ticket-client.spec  describe Write Ticket Handoff
```

### Display Latest Handoff

```
kanban_tools_spec       with handoffs written for the ticket
kanban_tools_spec       it should show no handoff for a ticket that has none
side-panel-client.spec  it should show the handoff in a tab
```

# (E) Guide Work Through Practices

### Display Fidelity Progress

```
kanban_tools_spec  it should show each fidelity's Generate, Validate, and Review
kanban_spec        with a fidelity generated
```

### Open Practice Tile

```
tile-client.spec    describe Open Practice Tile
story-actions.spec  describe Open Practice Tile
```

### Choose Ticket Practices

```
kanban_tools_spec   that turns a practice off for a ticket
ticket-client.spec  describe Choose Ticket Practices
story-actions.spec  describe Choose Ticket Practices
```

### Send Action To Stage Practices

```
tile-client.spec  describe Send Action To Stage Practices
tile-client.spec  with two stage heads pressed
```

### Mark Ticket Done In Stage

```
kanban_spec        it should be done in its stage, in the same column
kanban_tools_spec  and back from Done
move_ticket.behavior.e2e  it should say in a toast that it is done in its stage
```

### Open Help

```
help-text.spec      describe Open Help
story-actions.spec  describe Open Help
kanban_tools_spec   that opens help on a fidelity
kanban_tools_spec   that opens help on a practice
```

### Send Next Fidelity Action

```
ticket-client.spec  describe Send Next Fidelity Action
kanban_spec         it should name Generate on story_map as next
ticket-client.spec  it should mark its tile as the next one
kanban_spec         with every required fidelity in its stage done
kanban_spec         it should name satisfy as the next action
```

# (E) Generate Fidelity Outputs

### Choose Action And Formats

```
tile-client.spec  describe Choose Action And Formats
tile-client.spec  it should give each fidelity its default format
tile-client.spec  it should keep Run off until a format is chosen
```

### Resolve Fidelity Output Paths

```
harness/guidance/fidelity_outputs_spec.py
space/session/session_spec.py  it should put each format's file under the practice's root folder
```

### Generate Fidelity Output

```
kanban_spec         it should show Generate done and Validate and Review remaining for that fidelity
tile-client.spec    describe Generate Fidelity Output
story-actions.spec  describe Generate Fidelity Output
```

### Render Fidelity Format

```
tile-client.spec  describe Render Fidelity Format
```

### Send Sketch Iterate Or Document

```
tile-client.spec    describe Send Sketch Iterate Or Document
story-actions.spec  describe Send Sketch Iterate Or Document
chat-client.spec    it should choose the only chat connected
```

# (E) Validate Fidelity Outputs

### Validate Fidelity

```
kanban_spec       that has a validate with no violations
tile-client.spec  describe Validate Fidelity
```

### Save Validation Report

```
cdd_guidance/actions/validate/validate_spec.py  it should save a report for each listed guidance
cdd_guidance/actions/validate/validate_spec.py  it should leave an earlier report's saved graph as it was
```

### Open Validation Report

```
side-panel-client.spec  describe Open Validation Report
story-actions.spec      describe Open Validation Report
kanban_tools_spec       with validation reports saved for a fidelity
```

### Fix Report Violations

```
kanban_tools_spec       with a validation report saved without its graph
side-panel-client.spec  describe Fix Report Violations
side-panel-client.spec    with Fix pressed on one violation
                            it should send one message to the chat
                            it should name the rule and what it requires
                            it should give the error at its file and line
                            it should quote the content that failed
                            it should name the ticket's session
side-panel-client.spec    with Fix all pressed on a rule
                            it should send every violation of the rule in one message
story-actions.spec      it should send Fix and Fix all to the chat
```

### Satisfy Violations From Band

```
ticket-client.spec  describe Satisfy Violations From Band
story-actions.spec  describe Satisfy Violations From Band
```

# (E) Review Fidelity Outputs

### List Ticket Files

```
side-panel-client.spec  describe List Ticket Files
kanban_tools_spec       with a fidelity's markdown generated
kanban_tools_spec       with specs in the repository and one changed on the ticket's branch
side-panel-client.spec  with a list that cannot be read
```

### Browse Ticket Folder

```
side-panel-client.spec  describe Browse Ticket Folder
side-panel-client.spec  describe Browse Ticket's Session Folder
```

### View Files

```
side-panel-client.spec  describe View Files
```

### Review Fidelity

```
kanban_tools_spec   with a ticket whose story map has passed validate
ticket-client.spec  describe Review Fidelity
tile-client.spec    describe Review Fidelity
kanban_spec         that was reviewed before its validate passed
kanban_spec         with every required fidelity in its stage done
```
