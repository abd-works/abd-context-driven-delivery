---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Check CDD Server Health On Board

Story map: [Check CDD Server Health On Board](../../../.context/story-map.md#e-check-cdd-server-health-on-board). These scenarios were split from Display Board, which held eleven (`story-scenarios-at-most-seven`), on 2026-11-24; their text is as it was there. Their story tests stay where they ran: the browser tier in `see-work-on-session-board/see-work-on-session-board.story.ui.spec.ts`, and the Python story tests in this folder's `display-board-server-health/` and `update-board-and-cdd/`.

## Story: Display Board Server Health

#### Scenario: Say the cdd server is not connected

*Given* the cdd server behind the session board is not connected
*When* the session board reads the [board](../../../space/kanban/.context/kanban-model.md#board)
*Then* a band across the top of the page says The cdd server is not connected
*And* the header offers Update

#### Scenario: Show a failing tool in a toast

> A session.json that does not read no longer fails `board.show` (Display Board's scenario Show the other tickets when one ticket's session file does not read), so the failing tool here is a child ticket whose title makes the name of a ticket already there, which `ticket.add_child` refuses.

*Given* the [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card)s checkout-flow and billing-report are on the [board](../../../space/kanban/.context/kanban-model.md#board)
*When* the Person adds a child titled Billing report to checkout-flow
*Then* a toast says cdd ticket.add_child failed: TicketNameTakenError: a ticket named billing-report already exists; give 'Billing report' another title
*But* no band says the cdd server is lost

#### Scenario: Show a server failure on one line

*Given* the cdd server answers with a Python traceback
*When* the session board draws its server band
*Then* the band shows the traceback's exception line
*And* the whole traceback is behind Details

#### Scenario: Say a slow call is still running

*Given* the cdd server is busy
*When* a ticket call has run for eight seconds
*Then* a toast says the board is still waiting on it

## Story: Update Board And CDD

#### Scenario: Install the board again

*Given* the board is open
*When* the Person presses Update
*Then* the Kanban app is installed again through App.install, which installs its packages and rebuilds its page
*And* the page loads again from the new build

#### Scenario: Say why the board's install failed

*Given* npm cannot install the Kanban app
*When* the Person presses Update
*Then* a toast says the Kanban install failed, with the reason and the fix
*And* the page keeps running as it was
