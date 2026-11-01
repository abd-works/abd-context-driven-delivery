---
fidelity: [discovery]
artifact: [story-map]
format: md
section: body
---

# Story Map — Session Board

**Sources / context:** `harness/kanban/board.py`; `harness/kanban/ticket.py`; `harness/kanban/backlog_item.py`; `harness/kanban/kanban.py`; `harness/kanban/kanban_spec.py`; `harness/kanban/kanban_tools_spec.py`; `harness/kanban/pane/hooks/register.tsx`; `harness/kanban/pane/hooks/ticket-card.tsx`; `harness/kanban/pane/hooks/split-grip.tsx`; `harness/kanban/pane/hooks/register.test.tsx`; `harness/kanban/.context/module-context.md`; `harness/kanban/.context/kanban-model.md`; the Board Pane canvas, Version 72 (https://claude.ai/artifact/LGLk189R4aZ14bgwcWRiPN, `project/Main.dc.html`) and its comment threads of 2026-10-31.

**Acceptance criteria:** A stack of cards on the story map is one Story. The top card is the Story and the cards under it are its acceptance criteria, listed under it here.

**Evidence:** The line under each Story says where it stands. **Observed** means the code and specs do it today. **Intended** means only the canvas does it, so it is not built. **Observed, then intended** means the code does part of it and the canvas changes or extends it.

**Actors:** Person, Board Pane, Claude Code.

---

# (E) Move Work Forward On Session Board

## (E) Display Board And Details For Repo

### (S) Person --> Open Board

Observed: the `/board` command in `register.tsx`.

### (S) Board Pane --> Display Board

Observed: `columnView`; register.test "the board pane shows every column and the tickets in them, on every surface".

**Acceptance criteria:**

- Display Connected Status: with the cdd server not connected, the pane says so and asks for it. Observed: register.test "with the cdd server not connected, the status line says so and the pane asks for it".
- Draw Board Columns: Backlog, Discovery, Specification, Implementation, and Complete, in that order, with In progress and Done inside each stage. Observed: `columnView`.
- Refresh Board After Tool Calls: after a session starts, a prompt is sent, or a cdd tool call finishes, the board shows the state it is in then. Observed: register.test "a prompt sent reads the board again".
- Announce Ticket Changes: a toast shows when a ticket moves or a fidelity is reviewed. Observed: `announceChanges`; register.test "a session open and closed under one name raises no toast on each read of the board".

### (S) Person --> Arrange Board And Details

Observed: `split-grip.tsx`, `splitBar`.

**Acceptance criteria:**

- Resize Board And Details: a drag on the split bar gives one region more rows and cannot close either. Observed: register.test "a drag on the split bar gives the board more rows", "a drag cannot close either region".
- Expand Board Or Details: one region takes the whole pane and Show both brings the other back. Observed: `splitBar`; register.test "Expand board gives the whole pane to the board and Show both brings the details back".

### (S) Board Pane --> Display Backlog Items As Tickets

Observed: the Backlog column shows the title of each file in `.sessions/_backlog/`; kanban_spec "should show each backlog item in the Backlog column".

### (S) Board Pane --> Display Ticket Card

Observed, then intended: `ticket-card.tsx` draws title, age, and progress segments. The canvas stacks the blocks on the card's right side and dims work not done.

**Acceptance criteria:**

- Display Sessions As Tickets: each work session shows as one ticket and the main session is not on the board. Observed: kanban_spec "should show every work session as a ticket", "should leave main off the board".
- Place Ticket In Column: a ticket shows in the stage of its latest move, or before any move in the earliest stage its session shows work in. Observed: kanban_spec "should be in Specification".
- Display Active Ticket: the active ticket has a thick orange outline. Observed, then intended: kanban_spec "should name the ticket of the current session as active"; the outline is on the canvas.
- Show Active Ticket On Status Line: the status line names the active ticket, its stage, its next guidance, and its violations. Observed: `statusOf`; register.test "the status line names the active ticket, its stage, its next guidance, and its violations".

### (S) Board Pane --> Display Ticket Details

Observed: `detailView`, `practiceGrid`; register.test "a press anywhere on a card shows that ticket".

**Acceptance criteria:**

- A press anywhere on a card shows that ticket in the details region below the board.
- The details show the ticket's practices with their fidelity progress and its latest validation reports. Observed: kanban_tools_spec "should show that fidelity's latest report".
- Expand Ticket: the expanded card sits over the closed one, shows the same tiles as the details, and only one is expanded at a time. Intended: canvas `toggleCard`.

### (S) Person --> Set Stage WIP Limit

Intended: canvas `wipVals`; the count turns red when a stage holds more tickets than its limit.

### (S) Person --> Arrange Side Panel

Intended: the report, files, and help panels (comment "its draggable border and expand collapse").

**Acceptance criteria:**

- Resize Side Panel: a drag grip on the panel's left edge sets its width. Intended: canvas.
- Expand Side Panel: one panel is expanded at a time and it takes the board's width less the other open panels. Intended: canvas `togglePaneExpanded`.
- Close Side Panel: × closes the panel. Intended: canvas.
- Scroll Fixed Columns: columns and tiles keep their width and scroll sideways when a panel opens. Intended: canvas `.column-grid`, comment "We should just scroll more instead".

## (E) Tickets

### (S) Person --> Add Backlog Item

Intended: the + on the Backlog heading opens a form with a title and text, and canvas `addToBacklog` writes them to one markdown file in `.sessions/_backlog/` (comment "put both the title and the text in it"). Today a person adds that file by hand.

**Acceptance criteria:**

- Start Backlog Item: the → arrow on a backlog card opens a ticket in Discovery, and a ticket that was moved to the Backlog comes back with its work. Observed, then intended: `BacklogItem.start`; kanban_spec "should open a ticket in Discovery"; comment "we just need a right arrow".

### (S) Person --> Open Ticket Session

Observed: `Board.new_ticket`, `Kanban.new`; kanban_tools_spec "should return the new ticket in Discovery".

**Acceptance criteria:**

- Create Ticket Branch And Worktree: they are created when a ticket that has none is activated. Intended: canvas `confirmSwitch`.

### (S) Person --> Close Active Session

Observed, then intended: `/ticket close <ticket>` in `register.tsx` closes the ticket into Complete. On the canvas `confirmClose` ends the working session and the ticket stays in its column, which differs from `Ticket.close`.

### (S) Person --> Restrict Actions To Active Session

Intended: canvas `isLocked`; with Active session only on, every ticket that is not the active session disables what changes its work (comment "All buttons and list boxes should be disabled"). Information stays open: files, the report, expand, help, Activate, and Switch to (comment "you should still be able to get information").

### (S) Person --> Move Ticket

Observed: the arrows on a card move its ticket whatever its session's work; kanban_tools_spec "should show the ticket in that stage all the same".

**Acceptance criteria:**

- Move Ticket To Next Column: the forward arrow moves it one column on. Observed: `Ticket.move_next`; register.test "an arrow on a card moves its ticket to the next column".
- Move Ticket To Previous Column: the back arrow moves it one column back. Observed: `Ticket.move_previous`; kanban_tools_spec "should show the ticket in Discovery"; register.test "an arrow on a card moves its ticket to the previous column".
- A ticket moved out of Implementation closes into Complete. Observed: kanban_tools_spec "should show the ticket in Complete", "should close the ticket".
- A ticket moved back out of Complete reopens in Implementation. Observed: kanban_tools_spec "should reopen the ticket in Implementation".
- A ticket moved back out of Discovery goes to the Backlog with its work. Intended: canvas `toBacklog`, comment "We should be able to move tickets into the backlog".

### (S) Person --> Activate Ticket

Observed, then intended: Switch to and `/ticket switch <ticket>` call `session.switch`; register.test "Switch to makes the chosen ticket the current session". The canvas asks first in a dialog with what to do on leaving and on opening.

**Acceptance criteria:**

- Commit, push, and merge into main are chosen when the session is left. Intended: canvas `leaveGroup`.

### (S) Person --> Split Ticket Into Child Tickets

Observed: the Split button fills the prompt and `Kanban.new` records the parent; register.test "Split fills the prompt with the ticket to split"; kanban_tools_spec "should name the ticket it was split from".

### (S) Person --> Archive Ticket

Observed: `Ticket.archive`; kanban_spec "should be off the board".

### (S) Person --> Write Ticket Handoff

Observed: the Handoff button fills the prompt with `/space-handoff-handoff-session` in `ticketActions`.

### (S) Board Pane --> Display Latest Handoff

Observed: `Ticket.latest_handoff`; kanban_tools_spec "should show the latest handoff".

## (E) Practices

### (S) Board Pane --> Display Fidelity Progress

Observed, then intended: `practiceGrid`; kanban_spec "should show Validate done for that fidelity"; the canvas dims work not done.

**Acceptance criteria:**

- Each fidelity shows Generate, Validate, and Review as to do, in progress, or done.

### (S) Person --> Open Practice Tile

Intended: canvas `hoverIn`; a tile expands after a short hover on that tile, closes on leaving, and a click inside keeps it open (comment "we have to hover over generate first").

### (S) Person --> Choose Ticket Practices

Intended: canvas `togglePractice` saves the choice to the ticket's `session.json`.

### (S) Person --> Run Action Across Practices

Intended: canvas card menu and stage head run one action on every enabled practice in a stage (comment "we generate all for a ticket").

### (S) Person --> Mark Ticket Done In Stage

Intended: canvas `moveForward`; the arrow takes an In progress ticket to Done before it crosses a column. Today Done is derived from the session's work, so the override needs a session log line the ticket can read back.

### (S) Board Pane --> Add Active Ticket To System Prompt

Observed: `prompt.compose` handler; register.test "the system prompt names the active ticket and its next guidance".

### (S) Person --> Open Help

Intended: canvas `helpVals`; the ? on a tile or a practice name opens help in a scrollable side panel.

**Acceptance criteria:**

- Fidelity help shows its overview, guidance, and rules.
- Practice help shows its overview, guidance, and shared rules.
- The Forge link opens the fidelity's or practice's page.

### (S) Person --> Run Next Step

Observed, then intended: Run next fills the prompt in `ticketActions`.

**Acceptance criteria:**

- Name Next Fidelity: the button names the step that runs next. Observed, then intended: `Ticket.next`; kanban_spec "should name Generate on story_map as next"; the name on the button is on the canvas.
- Run next steps generate, validate, review for each practice in order. Intended: comment "goes through generate validate review for each practice in order".
- Run next holds on fix violations until they are fixed. Intended: canvas.

## (E) Generate

### (S) Person --> Choose Action And Formats

Intended: canvas action list and format icons on a tile.

### (S) Claude Code --> Resolve Fidelity Output Paths

Observed: `Generate` and `Session.fidelity_outputs` take the outputs a fidelity declares, with the `session.json` overrides; `harness/guidance/fidelity_outputs_spec.py`, `space/session/session_spec.py`.

### (S) Person --> Generate Fidelity Output

Observed, then intended: a generate line in the session log counts as Generate done; kanban_spec "should show Generate done and Validate and Review remaining for that fidelity". The canvas runs it from a tile, and `generate` has no format argument yet.

**Acceptance criteria:**

- When a fidelity uses a different format from the one before it, the earlier fidelity is rendered into that format first. Intended: canvas `renderBeforeGenerate`.

### (S) Person --> Render Fidelity Format

Intended: canvas `renderFormats` turns existing output into another format from a tile.

### (S) Person --> Send Sketch Iterate Or Document

Intended: canvas `sendFor` sends sketch, iterate, or document for a fidelity to the chat.

## (E) Validate

### (S) Person --> Validate Fidelity

Observed, then intended: a validate line counts as done only when it names no graph-rule violations; kanban_spec "should still need Validate for that fidelity". The canvas runs it from a tile and marks the result.

### (S) Claude Code --> Save Validation Report

Observed: `Validate` saves `.sessions/<session>/validation-reports/<practice>-<fidelity>-<date>.md`; `cdd_guidance/actions/validate/validate_spec.py`.

### (S) Person --> Open Validation Report

Observed, then intended: `Ticket.reports`; kanban_tools_spec "should show that fidelity's latest report". On the canvas `reportVals` opens the report in a side panel from a card or tile.

### (S) Person --> Fix Report Violations

Intended: canvas `violationVals` and `reportRule` send `/actions-satisfy` for one violation or every violation of a rule, and the report updates.

### (S) Person --> Satisfy Violations From Band

Observed: register.test "Satisfy on the band fills the prompt with the fidelities that have violations".

**Acceptance criteria:**

- Show Violations Band: the band above the prompt shows the active ticket's violations. Observed: `AbovePrompt`; register.test "the band above the prompt names the active ticket's violations".

## (E) Review

### (S) Person --> List Ticket Files

Intended: canvas list mode of the files panel, for the card's or tile's fidelities; clicking a file opens it (comment "List files you can click on").

### (S) Person --> Browse Ticket Folder

Intended: canvas `folderGroups`, the folder mode of the files panel.

### (S) Person --> View Files

Intended: canvas `paneTabs`; one tab per format the fidelity offers, generated or not (comment "2 tabs for this use case; md and drawio"), and `closeFileTab` closes one.

### (S) Person --> Review Fidelity

Observed, then intended: a review line completes a fidelity; kanban_spec "should show the fidelity done". The canvas adds a review button that needs a clean validate.

**Acceptance criteria:**

- Ignore Early Review: a review before a clean validate does not count. Observed: kanban_spec "should not count the review".
- Complete Stage Work: when every fidelity of a stage is reviewed, the ticket shows in that stage's Done part. Observed: `Ticket.is_done`; kanban_spec "should be done, waiting in its stage's done part".

---

## Scope boundary

**In scope:** what a Person does on the Session Board and what the Board Pane shows them, from the code today and from the canvas at Version 72.

**Out of scope:** animation on the canvas, because it is not repeatable behaviour.
