---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Maintain Tickets

### Domain terms

- ++ticket text++ — what a ticket is about, kept in the markdown file in its session folder (checkout-flow.md), or in a backlog item's file.
- ++tag++ — a word a person puts on a ticket's session; its card shows it.

## Examples

Seed state from `space/kanban/session_board_examples.py`, which the shared stories and the screen specs seed from.

### ticket

| ticket | title | text | tags |
| --- | --- | --- | --- |
| ++checkout-flow++ | Checkout flow | Pay for the basket. |  |
| ++pet-visits++ | Pet visits | Book a visit for a pet. |  |
| ++confirm-order++ | Confirm order | Show the order and take the payment. |  |
| ++sign-up++ | Sign up |  |  |
| ++no-such-ticket++ | (no session folder) |  |  |

### backlog item

| backlog item | text |
| --- | --- |
| ++Gift cards++ | Sell gift cards. |
| ++Returns and refunds++ | Refund an order. |

### tag

| tag |
| --- |
| ++billing++ |
| ++urgent++ |

## Story: Add Backlog Item

#### Scenario: Add an idea to the Backlog

*Given* the Backlog [column](../../../space/kanban/.context/kanban-model.md#column) has no [backlog item](../../../space/kanban/.context/kanban-model.md#backlogitem--card) titled Gift cards
*When* the Person adds the backlog item Gift cards with the text Sell gift cards.
*Then* the Backlog shows Gift cards with the text Sell gift cards.
*And* Gift cards is selected and the form is closed
*And* a toast says Gift cards added to Backlog

#### Scenario: Keep Add off with no title

*Given* the new backlog item form is open
*But* the Person has typed no title
*When* the Person tries to add the item
*Then* Add stays off
*And* no [backlog item](../../../space/kanban/.context/kanban-model.md#backlogitem--card) is written

#### Scenario: Refuse an idea whose title another idea's file has

> Test: maintain-tickets.story.shared.py, replayed by the domain spec.

> Evidence: exploratory-testing defect gizmo-13. space/kanban module-context: a backlog item's file is the only copy of the idea.

*Given* the Backlog keeps the idea Gift cards, with the text Sell gift cards.
*When* the Person adds an idea titled Gift cards with another text
*Then* the board says the Backlog already keeps an idea in .sessions/_backlog/gift-cards.md
*And* that file still says Sell gift cards.

#### Scenario: Refuse an idea whose title gives its file no name

> Test: maintain-tickets.story.shared.py, replayed by the domain spec.

> Evidence: exploratory-testing defect gizmo-13.

*Given* the [board](../../../space/kanban/.context/kanban-model.md#board) shows the Backlog
*When* the Person adds an idea whose title is empty, or 日本語
*Then* the board says the title gives no name
*And* no file named .md is written in the Backlog

## Story: Start Backlog Item

#### Scenario: Start a backlog item in a chosen folder

*Given* the [backlog item](../../../space/kanban/.context/kanban-model.md#backlogitem--card) Gift cards is in the Backlog
*And* the [repository](../../../space/kanban/.context/kanban-model.md#repo) has the folders src/billing and src/visits
*When* the Person starts Gift cards
*Then* the roots dialog lists the top folders of the repository
*And* Gift cards is still in the Backlog
*When* the Person chooses src/visits as its root
*Then* the [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) gift-cards is In progress in Discovery with root src/visits
*And* the roots dialog stays open on gift-cards so its practices' roots can be set
*And* a toast says Gift cards started in Discovery

#### Scenario: Keep the idea file with the new ticket

*Given* the [backlog item](../../../space/kanban/.context/kanban-model.md#backlogitem--card) Returns and refunds is the file .sessions/_backlog/returns-and-refunds.md
*When* the Person starts Returns and refunds on the whole repository
*Then* the [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) returns-and-refunds is In progress in Discovery
*And* its session folder holds returns-and-refunds.md, text and all
*And* its session log names the item's file
*But* the Backlog no longer shows Returns and refunds

#### Scenario: Bring a ticket back from the Backlog with its work

*Given* the [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) sign-up was moved back out of Discovery and waits in the Backlog as the [backlog item](../../../space/kanban/.context/kanban-model.md#backlogitem--card) Sign up
*And* its folder .sessions/_backlog/sign-up/ keeps its session log
*When* the Person starts Sign up
*Then* sign-up is back on the board with its session log and session.json
*But* no new ticket is opened

#### Scenario: Refuse to start an idea whose name a ticket already has

> Test: maintain-tickets.story.shared.py, replayed by the domain spec.

> Evidence: exploratory-testing defect gizmo-13.

*Given* the [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) pet-visits is on the board
*And* the Backlog keeps an idea titled Pet visits
*When* the Person starts that idea
*Then* the board says a ticket named pet-visits already exists
*And* the idea stays in the Backlog

## Story: Edit Ticket Text

### Evidence

| Source | Note |
|--------|------|
| `.sessions/session-board/ticket-enhancements.md` (commit b08bfe47e) | "Edit a ticket's text"; backlog item text and session ticket text, kept in a markdown file the session's instructions refer to |
| `harness/.context/ux/ticket-ui.drawio` | "edit text in markdown file" |
| `space/kanban/backlog_item.py:121-128`, `space/kanban/app/src/kanban/backlog-item/backlog-item-view.tsx:62` | Observed: starting a backlog item moves its file, text and all, into the ticket's session folder; a backlog card shows its file's text |

Intended, not built: a ticket's card does not show its text, no card edits text, and `Ticket.agent_context` does not name the file.
The realizations name the operations these scenarios need; none of them exists yet, so each is Intended. Naming the file in the agent's system prompt is a scenario of Add Active Ticket To System Prompt, the story that composes that prompt.

#### Scenario: Show a ticket's text from its session file

*Given* the [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow's [session](../../../space/kanban/.context/kanban-model.md#session) folder holds checkout-flow.md with the text Pay for the basket.
*When* the Person opens the [board](../../../space/kanban/.context/kanban-model.md#board)

```realization
Board.show()
  -> checkout-flow.text
     -> self.session.text
  <- checkout-flow with the text Pay for the basket.
```

*Then* checkout-flow's card shows Pay for the basket.

#### Scenario: Edit a ticket's text

*Given* the [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow's card shows Pay for the basket.
*When* the Person edits checkout-flow's text to Pay for the basket by card.

```realization
CardPlacement.ticket("checkout-flow")
  <- checkout-flow
checkout-flow.edit_text("Pay for the basket by card.")
  -> self.session.keep_text("Pay for the basket by card.")
  <- checkout-flow with the text Pay for the basket by card.
```

*Then* checkout-flow.md in checkout-flow's [session](../../../space/kanban/.context/kanban-model.md#session) folder holds Pay for the basket by card.
*And* checkout-flow's card shows Pay for the basket by card.

#### Scenario: Write the text file for a ticket that has none

*Given* the [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) pet-visits is on the [board](../../../space/kanban/.context/kanban-model.md#board)
*But* pet-visits' [session](../../../space/kanban/.context/kanban-model.md#session) folder holds no pet-visits.md
*When* the Person edits pet-visits' text to Book a visit for a pet.

```realization
CardPlacement.ticket("pet-visits")
  <- pet-visits
pet-visits.edit_text("Book a visit for a pet.")
  -> self.session.keep_text("Book a visit for a pet.")
  <- pet-visits with the text Book a visit for a pet.
```

*Then* pet-visits.md in pet-visits' session folder holds Book a visit for a pet.
*And* pet-visits' card shows Book a visit for a pet.

#### Scenario: Edit a backlog item's text

*Given* the [backlog item](../../../space/kanban/.context/kanban-model.md#backlogitem--card) Gift cards has the text Sell gift cards.
*When* the Person edits Gift cards' text to Sell gift cards at the till.

```realization
BoardReads.backlog_item_called("Gift cards")
  <- Gift cards
Gift cards.edit_text("Sell gift cards at the till.")
  <- Gift cards with the text Sell gift cards at the till.
```

*Then* Gift cards' file, .sessions/_backlog/gift-cards.md, holds Sell gift cards at the till.
*And* the Backlog shows Gift cards with the text Sell gift cards at the till.

#### Scenario: Open a backlog item's text in the Files app

> Test: browser: maintain-tickets.story.ui.spec.ts. The Files app reads every file through a session; a backlog item has none, so its file opens through main's, the board's default session, as a ticket's file opens through its own.

> Evidence: requested 2026-11-23: a backlog item's text is shown in the Files app, as an in-progress ticket's is. Observed before it: the link under a backlog item's text opened the file in the app the computer opens markdown files with (`BacklogItem.open_file`).

*Given* the [backlog item](../../../space/kanban/.context/kanban-model.md#backlogitem--card) Gift cards has the text Sell gift cards.
*When* the Person opens Gift cards' file from its card

```realization
EditorAppClient.openFilesOn(main, { folder: 'session', file: '.sessions/_backlog/gift-cards.md' })
  -> App.open("Files")
  <- the Files app, opened on .sessions/_backlog/gift-cards.md
```

*Then* the Files app opens .sessions/_backlog/gift-cards.md

#### Scenario: Edit a child's text inside its parent

*Given* the [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow holds its child ticket confirm-order
*And* confirm-order's text is Show the order and take the payment.
*When* the Person edits confirm-order's text inside checkout-flow's card to Show the order, then take the payment.

```realization
CardPlacement.ticket("confirm-order")
  <- confirm-order
confirm-order.edit_text("Show the order, then take the payment.")
  -> self.session.keep_text("Show the order, then take the payment.")
  <- confirm-order with the text Show the order, then take the payment.
```

*Then* confirm-order.md in confirm-order's [session](../../../space/kanban/.context/kanban-model.md#session) folder holds Show the order, then take the payment.
*And* opening confirm-order from checkout-flow's card shows Show the order, then take the payment.

## Story: Reorder Tickets In Column

### Evidence

| Source | Note |
|--------|------|
| `.sessions/session-board/ticket-enhancements.md` (commit b08bfe47e) | "Reorder tickets in a column" |
| `space/kanban/board.py:328` | Observed: the Backlog lists its items by file name; no column keeps a place a person chose |

The realizations name the operations these scenarios need; none of them exists yet, so each is Intended.

#### Scenario: Keep a ticket where it was moved in its column

*Given* the Discovery [column](../../../space/kanban/.context/kanban-model.md#column) shows the [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) pet-visits above sign-up
*When* the Person moves sign-up above pet-visits in Discovery

```realization
CardPlacement.ticket("sign-up")
  <- sign-up
sign-up.move_before(pet-visits)
  <- Discovery with sign-up above pet-visits
```

*Then* Discovery shows sign-up above pet-visits
*And* Discovery still shows sign-up above pet-visits when the [board](../../../space/kanban/.context/kanban-model.md#board) is read again

#### Scenario: Move a ticket above a ticket in another column

*Given* the Discovery [column](../../../space/kanban/.context/kanban-model.md#column) shows the [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) pet-visits In progress
*And* Hardening shows the ticket almost-shipped in its Done
*When* the Person moves pet-visits above almost-shipped

```realization
CardPlacement.ticket("pet-visits")
  <- pet-visits
pet-visits.move_before(almost-shipped)
  -> self.moves.move_beside(almost-shipped)
  <- Hardening's Done with pet-visits above almost-shipped
```

*Then* Hardening shows pet-visits above almost-shipped in its Done
*And* Discovery no longer shows pet-visits

#### Scenario: Close a ticket by moving it above a closed ticket

*Given* the Discovery [column](../../../space/kanban/.context/kanban-model.md#column) shows the [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) pet-visits
*And* Complete shows the closed ticket sign-up
*When* the Person moves pet-visits above sign-up

```realization
CardPlacement.ticket("pet-visits")
  <- pet-visits
pet-visits.move_before(sign-up)
  -> self.moves.move_beside(sign-up)
  <- Complete with pet-visits above sign-up
```

*Then* Complete shows pet-visits above sign-up

#### Scenario: Keep a backlog item where it was moved

*Given* the Backlog shows the [backlog item](../../../space/kanban/.context/kanban-model.md#backlogitem--card) Gift cards above Returns and refunds
*When* the Person moves Returns and refunds above Gift cards

```realization
BoardReads.backlog_item_called("Returns and refunds")
  <- Returns and refunds
Returns and refunds.move_before(Gift cards)
  <- the Backlog with Returns and refunds above Gift cards
```

*Then* the Backlog shows Returns and refunds above Gift cards
*And* the Backlog still shows Returns and refunds above Gift cards when the [board](../../../space/kanban/.context/kanban-model.md#board) is read again

## Story: Archive Ticket

#### Scenario: Archive a ticket off the board

*Given* the [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) pet-visits is In progress in Discovery with its story map generated
*When* the Person archives pet-visits
*Then* no [column](../../../space/kanban/.context/kanban-model.md#column) shows pet-visits
*And* its folder is in .sessions/_archive/pet-visits

#### Scenario: Refuse to archive a ticket the board does not have

*Given* the [board](../../../space/kanban/.context/kanban-model.md#board) shows no [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) named no-such-ticket
*When* the Person archives no-such-ticket
*Then* the board says no ticket named 'no-such-ticket' on the board
*But* nothing is moved to .sessions/_archive

#### Scenario: Archive a ticket that is open in its own worktree

> Test: heavy: space/kanban/ticket_work_heavy_spec.py 'that a ticket open in its own worktree, with work not saved, is archived'.

> Evidence: exploratory-testing defect gizmo-16. Evidence gap: no source says what becomes of an archived ticket's worktree and branch; this takes what closing with delete_worktree does, awaiting the person's decision.

*Given* the [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) pet-visits is open in its own worktree, with work nobody committed
*When* the Person archives pet-visits
*Then* that work is committed on the branch pet-visits on origin
*And* pet-visits's worktree is gone
*And* its folder is in .sessions/_archive/pet-visits

## Story: Delete Ticket

### Evidence

| Source | Note |
|--------|------|
| `.sessions/session-board/ticket-enhancements.md` (commit b08bfe47e) | "Delete a ticket"; Delete on a card removes the ticket and its session folder |
| `space/kanban/ticket.py:352` | Observed: Archive is the nearest operation; there is no delete |
| Request, 2026-11-23 | A selected Backlog card offers Delete, which removes the item (its markdown file, or its folder for a parent) after one confirmation and redraws the Backlog without it. Observed before it: no delete on `BacklogItem`, and a backlog card offers only Edit text and Start |

The realizations name the operations these scenarios need; none of them exists yet, so each is Intended.

Evidence gap: the source does not say what becomes of a deleted ticket's branch and worktree; these scenarios leave them out.

#### Scenario: Delete a ticket and its session folder

*Given* the [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) pet-visits is on the [board](../../../space/kanban/.context/kanban-model.md#board)
*When* the Person deletes pet-visits

```realization
CardPlacement.ticket("pet-visits")
  <- pet-visits
pet-visits.delete()
  -> self.session.folder.remove()
  <- the board without pet-visits
```

*Then* no [column](../../../space/kanban/.context/kanban-model.md#column) shows pet-visits
*And* .sessions/pet-visits is gone

#### Scenario: Refuse to delete a ticket the board does not have

*Given* the [board](../../../space/kanban/.context/kanban-model.md#board) still shows no-such-ticket's card, but its session folder is gone
*When* the Person deletes no-such-ticket

```realization
CardPlacement.ticket("no-such-ticket")
  <- TicketNotFoundError: no ticket named 'no-such-ticket' on the board
```

*Then* the board says no ticket named 'no-such-ticket' on the board
*And* deleting no-such-ticket removes no other ticket's session folder

#### Scenario: Delete a ticket that is open in its own worktree

> Test: heavy: space/kanban/ticket_work_heavy_spec.py 'that a ticket open in its own worktree, with work not saved, is deleted'.

> Evidence: exploratory-testing defect gizmo-16. Evidence gap, as the story's own: no source says what becomes of a deleted ticket's worktree and branch; this takes what closing with delete_worktree does, and keeps the branch, awaiting the person's decision.

*Given* the [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) pet-visits is open in its own worktree, with work nobody committed
*When* the Person deletes pet-visits
*Then* that work is committed on the branch pet-visits on origin
*And* pet-visits's worktree is gone
*And* .sessions/pet-visits is gone

#### Scenario: Keep a ticket whole when its session folder cannot be removed

> Test: heavy, Windows: space/kanban/ticket_work_heavy_spec.py 'that a ticket whose session folder a running program holds open is deleted'.

> Evidence: exploratory-testing defect gizmo-09, as its second charter repeated it on Windows.

*Given* the [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) pet-visits is on the [board](../../../space/kanban/.context/kanban-model.md#board)
*And* a running program works in .sessions/pet-visits
*When* the Person deletes pet-visits
*Then* the board says the session folder could not be removed, naming it
*And* .sessions/pet-visits still holds its session.json and session.log
*And* pet-visits is still on the board

#### Scenario: Delete a backlog item and its file

> Evidence: requested 2026-11-23, after the person had to delete share-read-only-projects-in-the-board-tools-spec from `.sessions/_backlog/` by hand: a selected Backlog card offers Delete, which removes the item after one confirmation.

*Given* the Backlog [column](../../../space/kanban/.context/kanban-model.md#column) shows the [backlog items](../../../space/kanban/.context/kanban-model.md#backlogitem--card) Gift cards and Returns and refunds
*When* the Person deletes Gift cards

```realization
BoardReads.backlog_item_called("Gift cards")
  <- Gift cards
Gift cards.delete()
  -> self._place.remove()
  <- the Backlog without Gift cards
```

*Then* the Backlog shows Returns and refunds and not Gift cards
*And* .sessions/_backlog/gift-cards.md is gone

#### Scenario: Delete a parent backlog item with its children

*Given* the [backlog item](../../../space/kanban/.context/kanban-model.md#backlogitem--card) Gift cards holds its child Returns and refunds
*When* the Person deletes Gift cards
*Then* the Backlog shows neither Gift cards nor Returns and refunds
*And* .sessions/_backlog/gift-cards is gone

#### Scenario: Delete a child backlog item, keeping its parent

*Given* the [backlog item](../../../space/kanban/.context/kanban-model.md#backlogitem--card) Gift cards holds its child Returns and refunds
*When* the Person deletes Returns and refunds
*Then* the Backlog shows Gift cards with no children
*And* .sessions/_backlog/gift-cards/gift-cards.md is still there

## Story: Tag Ticket Session

### Evidence

| Source | Note |
|--------|------|
| `.sessions/_backlog/maintain-tickets-on-board.md` | "tagging sessions" |
| `space/session/sessions.py:276` | Observed: `session.json` holds no tags |

The realizations name the operations these scenarios need; none of them exists yet, so each is Intended.

#### Scenario: Tag a ticket's session

*Given* the [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) pet-visits has no tags
*When* the Person tags pet-visits' [session](../../../space/kanban/.context/kanban-model.md#session) with billing

```realization
CardPlacement.ticket("pet-visits")
  <- pet-visits
pet-visits.tag("billing")
  -> self.session.add_tag("billing")
  <- pet-visits tagged billing
```

*Then* pet-visits' card shows the tag billing
*And* pet-visits' session.json holds the tag billing

#### Scenario: Add a second tag

*Given* the [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) pet-visits is tagged billing
*When* the Person tags pet-visits' [session](../../../space/kanban/.context/kanban-model.md#session) with urgent

```realization
CardPlacement.ticket("pet-visits")
  <- pet-visits
pet-visits.tag("urgent")
  -> self.session.add_tag("urgent")
  <- pet-visits tagged billing and urgent
```

*Then* pet-visits' card shows the tags billing and urgent

## Story: Keep Every Change To Session Record

### Evidence

| Source | Note |
|--------|------|
| The person, 2026-11-22 | "one lock for every session.json update, so two chats or processes changing one session's record at once each keep their change" |
| `space/session/session_record.py` `SessionRecord.update`, before the fix | it read the record, changed it and wrote it with nothing held, so the later of two writes dropped the earlier: four processes each recording twelve modules' test tiers left 12 of the 48 (`space/session/session_record_processes_heavy_spec.py`, run before the fix) |
| `harness/installation/json_file.py` `JsonFile.held` | "a killed holder blocks nobody, and the lock file it leaves holds nothing" |

#### Scenario: Keep the changes two chats make to one ticket at the same moment

Observed (`space/session/session_record_processes_heavy_spec.py`, four real processes; `space/session/session_record_spec.py`, four callers in one process).

*Given* the [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) pet-visits is tagged billing
*When* one chat tags pet-visits' [session](../../../space/kanban/.context/kanban-model.md#session) with urgent and another tags it with legal at the same moment
*Then* pet-visits' `session.json` holds the tags billing, urgent and legal
  *And* neither chat's change is refused

#### Scenario: Make a change wait for the change that holds the record

Observed (`session_record_spec.py`).

*Given* a change to pet-visits' title holds its `session.json`
*When* another chat tags pet-visits with urgent before the first change is written
*Then* the tag waits for the first change
  *And* `session.json` holds the new title and the tag urgent

#### Scenario: Take the next change at once after the holder is killed

Observed (`session_record_processes_heavy_spec.py`).

*Given* a process holding pet-visits' `session.json` for a change is killed before it writes
*When* another chat tags pet-visits with urgent
*Then* `session.json` held what it held before the killed change
  *And* the tag is kept at once, not after the wait a held record allows

#### Scenario: Refuse to change a session.json left half written

Observed (`session_record_processes_heavy_spec.py`, `session_record_spec.py`).

*Given* pet-visits' `session.json` ends partway through its title
*When* a chat tags pet-visits with urgent
*Then* the change is refused, naming `session.json` as not a readable JSON object
  *And* the file is left as it is for a person to repair, never read as empty and written over

#### Scenario: Change the record itself when a killed writer left its staged text beside it

Observed (`session_record_spec.py`).

*Given* a killed writer left `session.json.4242.1.tmp`, half written, beside pet-visits' `session.json`
*When* a chat tags pet-visits with urgent
*Then* `session.json` holds its title and the tag urgent

- **A holder that never lets go:** a change that waits 30 seconds for a live holder is refused, naming the file as held by another caller (`JsonFile.held`, *JsonFileBusy*, covered for the mechanism in `harness/installation/json_file_spec.py`); the record is not changed.
- **A session with no folder yet:** a session with no folder yet has its folder made by the first change, which holds the lock file made beside the new `session.json`.
