---
fidelity: [discovery]
artifact: [story-map]
format: md
section: body
---

# Story Map — Session Board

**Sources / context:** `harness/kanban/board.py`; `harness/kanban/ticket.py`; `harness/kanban/backlog_item.py`; `harness/kanban/kanban_spec.py`; `harness/kanban/kanban_tools_spec.py`; `harness/kanban/pane/hooks/register.tsx`; `harness/kanban/pane/hooks/kanban/`; `harness/kanban/pane/hooks/register.test.tsx`; `harness/kanban/.context/module-context.md`; `harness/kanban/.context/kanban-model.md`; the Board Pane canvas, Version 72 (https://claude.ai/artifact/LGLk189R4aZ14bgwcWRiPN, `project/Main.dc.html`) and its comment threads of 2026-10-31.

**Acceptance criteria:** A stack of cards on the story map is one Story. The top card is the Story and the cards under it are its acceptance criteria, listed under it here.

**Evidence:** The line under each Story says where it stands. **Observed** means the code and specs do it today. Signatures in quotes are in `kanban_tools_spec.py`, `kanban_spec.py`, or `register.test.tsx`, which are organised by these stories. **Live** means it was also pressed in a real Claude Code terminal against the real cdd server. **Differs from the canvas** says where the terminal pane could not do what the canvas does.

**Actors:** Person, Board Pane, Claude Code.

---

# (E) Move Work Forward On Session Board

## (E) Display Board And Details For Repo

### (S) Person --> Open Board

Observed: the `/board` command in `register.tsx`; register.test "the /board command opens the pane and reads the board". Live.

### (S) Board Pane --> Display Board

Observed: `ColumnView`; "should return every column of the board", register.test "every column shows the tickets in it, on every surface". Live.

**Acceptance criteria:**

- Display Connected Status: with the cdd server not connected, the pane says so and asks for it. Observed: register.test "with the cdd server not connected, the status line says so and the pane asks for it".
- Draw Board Columns: Backlog, Discovery, Specification, Implementation, and Complete, in that order, with In progress and Done inside each stage. Observed: `ColumnView`. Live.
- Refresh Board After Tool Calls: after a session starts, a prompt is sent, or a cdd tool call finishes, the board shows the state it is in then. Observed: register.test "a prompt sent reads the board again".
- Announce Ticket Changes: a toast shows when a ticket moves or a fidelity is reviewed. Observed: `announceChanges`; register.test "a ticket that moves raises a toast naming its new column", "a session open and closed under one name raises no toast on each read of the board".

### (S) Person --> Arrange Board And Details

Observed: `split-grip.tsx`, `SplitBarView`. Live, including a real drag.

**Acceptance criteria:**

- Resize Board And Details: a drag on the split bar gives one region more height and cannot close either. Observed: register.test "a drag on the split bar gives the board more rows", "a drag cannot close either region".
- Expand Board Or Details: one region takes the whole pane and Show both brings the other back. Observed: `SplitBarView`; register.test "Expand board gives the whole pane to the board and Show both brings the details back".

### (S) Board Pane --> Display Backlog Items As Tickets

Observed: the Backlog column shows the title of each file in `.sessions/_backlog/`; kanban_spec "should show each backlog item in the Backlog column". Live.

### (S) Board Pane --> Display Ticket Card

Observed: `ticket-card.tsx` draws the title, age, and next step, with one block per enabled practice stacked on the right, dim while its work is not started; register.test "a card shows each enabled practice as a block and dims work not started". Live.

**Acceptance criteria:**

- Display Sessions As Tickets: each work session shows as one ticket and the main session is not on the board. Observed: kanban_spec "should show every work session as a ticket", "should leave main off the board".
- Place Ticket In Column: a ticket shows in the stage of its latest move, or before any move in the earliest stage its session shows work in. Observed: kanban_spec "should be in Specification".
- Display Active Ticket: the active ticket has a thick orange outline. Observed: kanban_spec "should name the ticket of the current session as active"; register.test "the active ticket has a thick orange outline". Live.
- Show Active Ticket On Status Line: the status line names the active ticket, its stage, its next guidance, and its violations. Observed: `statusOf`; register.test "the status line names the active ticket, its stage, its next guidance, and its violations".

### (S) Board Pane --> Display Ticket Details

Observed: `TicketDetailView`, `PracticeGridView`; register.test "a press anywhere on a card shows that ticket". Live.

**Acceptance criteria:**

- A press anywhere on a card shows that ticket in the details region below the board.
- The details show the ticket's practices with their fidelity progress and its latest validation reports. Observed: kanban_tools_spec "should show that fidelity's latest report".
- Expand Ticket: the expanded card sits over the board, shows the same tiles as the details, and only one is expanded at a time. Observed: `CardExpansionView`; register.test "an expanded card shows the same tiles as the details", "only one card is expanded at a time". Live. Differs from the canvas: it spans the pane under the header instead of growing out of the card, because a Box paints over only what was drawn before it.

### (S) Person --> Set Stage WIP Limit

Observed: `Board.set_wip_limit`, saved in `.sessions/_board.json`; "should show the stage over its limit", register.test "a stage over its limit shows its count in red". Live. Differs from the canvas: - and + buttons set the limit in place of an input, because the mobile surface has no Input.

### (S) Person --> Arrange Side Panel

Observed: `side-panel-view.tsx`, `panel-grip.tsx` hold the report, files, and help panels. Live.

**Acceptance criteria:**

- Resize Side Panel: a drag grip on the panel's left edge sets its width. Observed: register.test "a drag on a panel's left edge sets its width". Live, including a real drag.
- Expand Side Panel: one panel is expanded at a time and it takes the board's width less the other open panels. Observed: register.test "an expanded panel takes the board's width, and only one is expanded at a time". Live.
- Close Side Panel: × closes the panel. Observed: register.test "× closes a side panel". Live.
- Scroll Fixed Columns: columns keep their width and scroll sideways when a panel opens. Observed: register.test "columns keep their width and scroll sideways when a panel opens". Live. Differs from the canvas: ◀ and ▶ buttons move the columns one at a time, because a pane has no sideways scrolling.

## (E) Tickets

### (S) Person --> Add Backlog Item

Observed: the + on the Backlog heading opens a form with a title and text in the details region, and `BacklogItem.add` writes them to one markdown file in `.sessions/_backlog/`; "should show the item in the Backlog with its text". Live. The mobile surface has no Input, so it says to add the item elsewhere.

**Acceptance criteria:**

- Start Backlog Item: the → arrow on a backlog card opens a ticket in Discovery, and a ticket that was moved to the Backlog comes back with its work. Observed: `BacklogItem.start`; "should return the new ticket in Discovery", "should bring the ticket back with its work". Live.

### (S) Person --> Open Ticket Session

Observed: `Ticket.new` calls `Session.new`; "should return the new ticket in Discovery", "should leave the current session as it is".

**Acceptance criteria:**

- Create Ticket Branch And Worktree: they are created when a ticket that has none is activated. Observed: `Ticket.activate`; "should create the ticket's branch when a ticket that has none is activated". Both are Live on a real git repository: the worktree opens beside the repository, and a ticket that has one is offered neither again.

### (S) Person --> Close Active Session

Observed: Close on the active ticket asks what to do with its work, then `Ticket.close` calls `Session.close`, so the session ends, and moves the folder to `closed/`, so the ticket shows in Complete; "should show the ticket in Complete", "should leave no ticket active". Live. Differs from the canvas: on the canvas `confirmClose` leaves the ticket in its column.

### (S) Person --> Restrict Actions To Active Session

Observed: `isLocked` in `view-context.ts`, on by default; register.test "with Active session only on, an arrow on another ticket does nothing", "with Active session only on, information about another ticket stays open". Live. With Active session only on, every ticket that is not the active session disables what changes its work (comment "All buttons and list boxes should be disabled"). Information stays open: files, the report, expand, help, Activate, and Switch to (comment "you should still be able to get information").

### (S) Person --> Move Ticket

Observed: the arrows on a card move its ticket whatever its session's work; "should show the ticket in that stage's Done all the same". Live.

**Acceptance criteria:**

- Move Ticket To Next Column: the forward arrow moves it one column on from Done. Observed: `Ticket.move_next`; "should show the ticket in the next stage". Live.
- Move Ticket To Previous Column: the back arrow moves it one column back, into that column's Done. Observed: `Ticket.move_previous`; "should show the ticket in Discovery", "should show the ticket in Discovery's Done". Live.
- A ticket moved out of Implementation closes into Complete. Observed: "should close the ticket".
- A ticket moved back out of Complete reopens in Implementation. Observed: "should reopen the ticket in Implementation".
- A ticket moved back out of Discovery goes to the Backlog with its work. Observed: `Ticket.move_previous`, `BacklogItem.holding`; "should show an item in the Backlog with the ticket's title". Live.

### (S) Person --> Activate Ticket

Observed: Activate on a card or the details opens a dialog with what to do on leaving and on opening, then calls `ticket.activate`; `/ticket activate <ticket>` asks nothing; "should make the chosen ticket the current session". Live on a real git repository.

**Acceptance criteria:**

- Commit, push, and merge into main are chosen when the session is left. Observed: `Ticket.activate`, `Ticket.close`; register.test "the Activate dialog chooses what to do on leaving and opens with merge off". All three are Live against a local bare repository as origin: the merge reached origin's main and the branch was deleted locally and on origin.

### (S) Person --> Split Ticket Into Child Tickets

Observed: the Split button fills the prompt and `Ticket.new` records the parent; "should name the ticket it was split from". Live.

### (S) Person --> Archive Ticket

Observed: the Archive button calls `Ticket.archive`; kanban_spec "should be off the board", "should leave the ticket off the board". Live.

### (S) Person --> Write Ticket Handoff

Observed: the Handoff button fills the prompt with `/space-handoff-handoff-session`; register.test "Handoff fills the prompt with the handoff command". Live.

### (S) Board Pane --> Display Latest Handoff

Observed: `Ticket.latest_handoff`; "should show the latest handoff". Live.

## (E) Practices

### (S) Board Pane --> Display Fidelity Progress

Observed: `PracticeGridView`; kanban_spec "should show Validate done for that fidelity", "should show each fidelity's Generate, Validate, and Review". Live.

**Acceptance criteria:**

- Each fidelity shows Generate, Validate, and Review as to do, in progress, or done.

### (S) Person --> Open Practice Tile

Observed: `tile-hover.tsx`; a tile opens after a short hover, closes on leaving, and a press keeps it open; register.test "a short hover on a tile opens it and leaving closes it", "a press on a tile keeps it open after the pointer leaves". Live. Its bar opens above the grid, at full width, so a tile low in the grid is not clipped.

### (S) Person --> Choose Ticket Practices

Observed: `Ticket.enable_practice` saves the choice to the ticket's `session.json`; "should show the practice off for that ticket". Live.

### (S) Person --> Run Action Across Practices

Observed: the stage head runs one action on every enabled practice in a stage; register.test "a stage head runs one action on every enabled practice in the stage". Differs from the canvas: the stage head alone offers it, with no separate card menu.

### (S) Person --> Mark Ticket Done In Stage

Observed: `Ticket.move_next`; the arrow takes an In progress ticket to Done before it crosses a column, written as a `done <stage>` session log line the ticket reads back, and back from Done as `in-progress <stage>`; kanban_spec "should be done in its stage, in the same column". Live.

### (S) Board Pane --> Add Active Ticket To System Prompt

Observed: `prompt.compose` handler; register.test "the system prompt names the active ticket and its next guidance". Live with a local stand-in for the model: the section was in the system prompt of the request Claude Code sent. No signed-in model has read it, because the Claude Code CLI on this machine has no login.

### (S) Person --> Open Help

Observed: `Board.help`; the ? on a tile or a practice name opens help in a side panel the pane scrolls; "should show the fidelity's rules", "should show the practice's shared rules". Live.

**Acceptance criteria:**

- Fidelity help shows its overview, guidance, and rules.
- Practice help shows its overview, guidance, and shared rules.
- The Forge link opens the fidelity's or practice's page.

### (S) Person --> Run Next Step

Observed: Run next fills the prompt with the command for the ticket's next action. Live.

**Acceptance criteria:**

- Name Next Fidelity: the button names the step that runs next. Observed: `Ticket.next`, `Ticket.next_action`; kanban_spec "should name Generate on story_map as next", "should name generate as the next action", register.test "Run next names the step that runs next". Live.
- Run next steps generate, validate, review for each practice in order. Observed: `Ticket.next_action`.
- Run next holds on fix violations until they are fixed. Observed: "should name satisfy as the next action"; Run next opens the report. Live.

## (E) Generate

### (S) Person --> Choose Action And Formats

Observed: `TileBarView` lists the actions and formats, with a check on formats already generated; register.test "a format already generated carries a check". Live. Differs from the canvas: buttons in place of a list box and icons, because the mobile surface has no Select.

### (S) Claude Code --> Resolve Fidelity Output Paths

Observed: `Generate` and `Session.fidelity_outputs` take the outputs a fidelity declares, with the `session.json` overrides; `harness/guidance/fidelity_outputs_spec.py`, `space/session/session_spec.py`.

### (S) Person --> Generate Fidelity Output

Observed: a generate line in the session log counts as Generate done; kanban_spec "should show Generate done and Validate and Review remaining for that fidelity". Run on a tile sends `/actions-generate <fidelities> format=<formats>`; register.test "should render the earlier fidelity into the new format first". `generate` has no format argument of its own yet, so the format is passed in the command's words.

**Acceptance criteria:**

- When a fidelity uses a different format from the one before it, the earlier fidelity is rendered into that format first. Observed: `Ticket.generate_commands`; "should render the earlier fidelity into the new format first".

### (S) Person --> Render Fidelity Format

Observed: Render on a tile sends `/actions-render`; register.test "Render turns existing output into the chosen format".

### (S) Person --> Send Sketch Iterate Or Document

Observed: Run on a tile runs `/actions-sketch`, `/actions-iterate`, or `/actions-document` through `$.command.run`; register.test "Sketch, Iterate, and Document send their command to the chat". Live with a local stand-in for the model: the skill's text and its argument were in the request Claude Code sent. What a real model then does was not run, because the Claude Code CLI on this machine has no login.

## (E) Validate

### (S) Person --> Validate Fidelity

Observed: a validate line counts as done only when it names no graph-rule violations; kanban_spec "should still need Validate for that fidelity". Validate on a tile runs `/actions-validate` and the tile marks the result; register.test "Validate on a tile sends the fidelity to validate".

### (S) Claude Code --> Save Validation Report

Observed: `Validate` saves `.sessions/<session>/validation-reports/<practice>-<fidelity>-<date>.md` and the graph it checked under the same name in `.json`; `cdd_guidance/actions/validate/validate_spec.py` "should save the graph it checked beside the report, under the same name".

### (S) Person --> Open Validation Report

Observed: `Ticket.report` opens the latest report in a side panel from the details or a tile; "should show that fidelity's latest report". Live.

### (S) Person --> Fix Report Violations

Observed: `Ticket.report` builds the rules from the graph saved beside the report, and a report with no saved graph says so in place of saying it has no violations; "should say a report has no saved graph". Fix and Fix all send `/actions-satisfy` for one violation or every violation of a rule, and an open report is read again after a cdd tool call; "should list each rule the report names with its violations", register.test "an open report is read again after a cdd tool call". The report and its buttons are Live.

### (S) Person --> Satisfy Violations From Band

Observed: register.test "Satisfy on the band fills the prompt with the fidelities that have violations". Live.

**Acceptance criteria:**

- Show Violations Band: the band above the prompt shows the active ticket's violations. Observed: `BandView`; register.test "the band above the prompt names the active ticket's violations". Live.

## (E) Review

### (S) Person --> List Ticket Files

Observed: `Ticket.files`, the list mode of the files panel, for the tile's or ticket's fidelities; pressing a file opens it; "should list the file with whether it exists". Live.

### (S) Person --> Browse Ticket Folder

Observed: `FolderGroupsView`, the folder mode of the files panel; register.test "the folder mode groups the files under their folders".

### (S) Person --> View Files

Observed: `Ticket.read_file`, `FileTabsView`; one tab per format the fidelity offers, generated or not, and × closes one; "should return the file's text", register.test "the files mode opens one tab per format, generated or not". Live.

### (S) Person --> Review Fidelity

Observed: a review line completes a fidelity; kanban_spec "should show the fidelity done". Reviewed on a tile is off until a clean validate; "should not allow Review until Validate is clean".

**Acceptance criteria:**

- Ignore Early Review: a review before a clean validate does not count. Observed: kanban_spec "should not count the review".
- Complete Stage Work: when every fidelity of a stage is reviewed, the ticket shows in that stage's Done part. Observed: `Ticket.is_done`; kanban_spec "should be done, waiting in its stage's done part".

---

## Scope boundary

**In scope:** what a Person does on the Session Board and what the Board Pane shows them, from the code today and from the canvas at Version 72.

**Out of scope:** animation on the canvas, because it is not repeatable behaviour.
