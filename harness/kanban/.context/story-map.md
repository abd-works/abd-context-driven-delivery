---
fidelity: [discovery]
artifact: [story-map]
format: md
section: body
---

# Story Map — Session Board

**Sources / context:** `harness/kanban/board.py`; `harness/kanban/ticket.py`; `harness/kanban/backlog_item.py`; `harness/kanban/kanban.py`; `harness/kanban/kanban_spec.py`; `harness/kanban/kanban_tools_spec.py`; `harness/kanban/pane/hooks/register.tsx`; `harness/kanban/pane/hooks/ticket-card.tsx`; `harness/kanban/pane/hooks/split-grip.tsx`; `harness/kanban/pane/hooks/register.test.tsx`; `harness/kanban/.context/module-context.md`; `harness/kanban/kanban-model.md`; the Board Pane canvas, Version 72 (https://claude.ai/artifact/LGLk189R4aZ14bgwcWRiPN, `project/Main.dc.html`) and its comment threads of 2026-10-31.

**Evidence:** The line under each Story says where it stands. **Observed** means the code and specs do it today. **Intended** means only the canvas does it, so it is not built. **Observed, then intended** means the code does part of it and the canvas changes or extends it.

**Actors:** Person, Claude Code, Board Pane, Kanban (the cdd MCP tools).

---

# (E) Show Session Board

## (E) Read Board From Sessions

### (S) Kanban --> Read Board Columns

Observed: `Board.to_json`, `Kanban.board`; kanban_tools_spec "should return every column of the board".

### (S) Kanban --> List Tickets From Session Folders

Observed: `Board.tickets`; kanban_spec "should show every work session as a ticket", "should leave default off the board".

### (S) Kanban --> Read Backlog Items

Observed: `Board.backlog_items`, `BacklogItem.title`; kanban_spec "should show each backlog item in the Backlog column".

### (S) Kanban --> Place Ticket In Column

Observed: `Ticket.column` reads the latest move line, or the earliest stage with work; kanban_spec "should be in Specification".

### (S) Kanban --> Read Fidelity Progress From Session Log

Observed: `FidelityProgress.from_log`; kanban_spec "should show Validate done for that fidelity".

### (S) Kanban --> Name Active Ticket

Observed: `Board.active`; kanban_spec "should name the ticket of the current session as active".

### (S) Kanban --> Read Latest Handoff And Reports

Observed: `Ticket.latest_handoff`, `Ticket.reports`; kanban_tools_spec "should show the latest handoff", "should show that fidelity's latest report".

## (E) Draw Board Pane

### (S) Board Pane --> Refresh Board After Tool Calls

Observed: `refresh` on session start, prompt submit, and every cdd tool call in `register.tsx`; register.test "a prompt sent reads the board again".

### (S) Board Pane --> Draw Board Columns

Observed: `columnView`; register.test "the board pane shows every column and the tickets in them, on every surface".

### (S) Board Pane --> Draw Ticket Card

Observed, then intended: `ticket-card.tsx` draws title, age, and progress segments. The canvas stacks the blocks on the card's right side, dims work not done, marks the active ticket with a thick orange outline, and drops the next line and "ready to pull".

### (S) Board Pane --> Report Disconnected Cdd Server

Observed: `callBoard`; register.test "with the cdd server not connected, the status line says so and the pane asks for it".

### (S) Person --> Show Ticket Details

Observed: `detailView`, `practiceGrid`; register.test "a press anywhere on a card shows that ticket".

### (S) Person --> Set Stage WIP Limit

Intended: canvas `wipVals`; the count turns red when a stage holds more tickets than its limit.

## (E) Keep Claude Code Informed

### (S) Board Pane --> Show Active Ticket On Status Line

Observed: `statusOf`; register.test "the status line names the active ticket, its stage, its next guidance, and its violations".

### (S) Board Pane --> Add Active Ticket To System Prompt

Observed: `prompt.compose` handler; register.test "the system prompt names the active ticket and its next guidance".

### (S) Board Pane --> Show Violations Band

Observed: `AbovePrompt` handler; register.test "the band above the prompt names the active ticket's violations".

### (S) Board Pane --> Announce Ticket Changes

Observed: `announceChanges` raises a toast when a ticket moves or a fidelity is reviewed; register.test "a session open and closed under one name raises no toast on each read of the board".

### (S) Person --> Open Board Command

Observed: the `/board` command in `register.tsx`.

## (E) Arrange Pane Layout

### (S) Person --> Resize Board And Details

Observed: `split-grip.tsx`; register.test "a drag on the split bar gives the board more rows", "a drag cannot close either region".

### (S) Person --> Expand Board Or Details

Observed: `splitBar`; register.test "Expand board gives the whole pane to the board and Show both brings the details back".

### (S) Person --> Resize Side Panel

Intended: canvas drag grip on the left edge of the report, files, and help panels (comment "its draggable border and expand collapse").

### (S) Person --> Expand Side Panel

Intended: canvas `togglePaneExpanded`; one panel is expanded at a time and it takes the board's width less the other open panels.

### (S) Person --> Close Side Panel

Intended: canvas × on the report, files, and help panels.

### (S) Board Pane --> Scroll Fixed Columns

Intended: canvas `.column-grid`; columns and tiles keep their width and scroll sideways when a panel opens (comment "We should just scroll more instead").

# (E) Move Tickets Through Stages

## (E) Capture Backlog Items

### (S) Person --> Add Backlog Item

Intended: the + on the Backlog heading opens a form with a title and text, and canvas `addToBacklog` writes them to one markdown file in `.sessions/_backlog/` (comment "put both the title and the text in it"). Today a person adds that file by hand, as `harness/kanban/kanban-model.md` says.

### (S) Person --> Start Backlog Item

Observed, then intended: `BacklogItem.start` opens a ticket in Discovery; kanban_spec "should open a ticket in Discovery". On the canvas the → arrow on a backlog card starts it, replacing the Start button (comment "we just need a right arrow"), and a ticket that was moved to the Backlog comes back with its work.

### (S) Person --> Open New Ticket

Observed: `Board.new_ticket`, `Kanban.new`; kanban_tools_spec "should return the new ticket in Discovery".

### (S) Person --> Move Ticket To Backlog

Intended: canvas `toBacklog` (comment "We should be able to move tickets into the backlog"). `Ticket.move_previous` stops at Discovery today; the ticket keeps its work, and if it was active no session is active afterwards.

## (E) Move Ticket Between Columns

### (S) Person --> Move Ticket To Next Column

Observed: `Ticket.move_next` moves whatever its progress; kanban_tools_spec "should show the ticket in that stage all the same"; register.test "an arrow on a card moves its ticket to the next column".

### (S) Person --> Mark Ticket Done In Stage

Intended: canvas `moveForward`; the arrow takes an In progress ticket to Done before it crosses a column. Today Done is derived from progress, so the override needs a session log line the ticket can read back.

### (S) Person --> Move Ticket To Previous Column

Observed: `Ticket.move_previous`; kanban_tools_spec "should show the ticket in Discovery"; register.test "an arrow on a card moves its ticket to the previous column".

### (S) Person --> Reopen Closed Ticket

Observed: `Ticket._reopen`; kanban_tools_spec "should reopen the ticket in Implementation".

### (S) Person --> Run Ticket Command

Observed, then intended: `/ticket pull|close|switch <ticket>` in `register.tsx`; register.test "/ticket pull asks the cdd server to pull the named ticket". The pull verb goes with Pull (comment "the whole pull concept I think is unnecessary for now").

## (E) Finish Ticket Work

### (S) Person --> Close Ticket Into Complete

Observed: `Ticket.close`, and `Ticket.move_next` out of Implementation; kanban_tools_spec "should show the ticket in Complete", "should close the ticket".

### (S) Person --> Archive Ticket

Observed: `Ticket.archive`; kanban_spec "should be off the board".

### (S) Person --> Split Ticket Into Child Tickets

Observed: the Split button fills the prompt and `Kanban.new` records the parent; register.test "Split fills the prompt with the ticket to split"; kanban_tools_spec "should name the ticket it was split from".

### (S) Person --> Write Ticket Handoff

Observed: the Handoff button fills the prompt with `/space-handoff-handoff-session` in `ticketActions`.

## (E) Switch Active Session

### (S) Person --> Activate Ticket

Observed, then intended: Switch to calls `session.switch`; register.test "Switch to makes the chosen ticket the current session". The canvas asks first in a dialog with what to do on leaving and on opening.

### (S) Person --> Leave Active Session

Intended: canvas `leaveGroup`; commit, push, and merge into main are chosen when the session is left.

### (S) Person --> Create Ticket Branch And Worktree

Intended: canvas `confirmSwitch`; the branch and worktree are created when a ticket that has none is activated.

### (S) Person --> Close Active Session

Intended: canvas `confirmClose`; closing ends the working session and the ticket stays in its column, which differs from `Ticket.close`.

### (S) Person --> Restrict Actions To Active Session

Intended: canvas `isLocked`; with Active session only on, every ticket that is not the active session disables what changes its work: the action list box, format icons, Run, validate, review, the arrows, Run next, Split, Handoff, the practice switches, and Fix (comment "All buttons and list boxes should be disabled"). Reading stays open: files, the report, expand, and help, and Activate and Switch to stay usable (comment "you should still be able to get information").

# (E) Work Ticket Fidelities

## (E) Open Ticket Work

### (S) Person --> Open Ticket Card

Intended: canvas `toggleCard`; the open card sits over the closed one, shows the same tiles as the details, and only one is open at a time.

### (S) Person --> Open Practice Tile

Intended: canvas `hoverIn`; a tile expands after a short hover on that tile, closes on leaving, and a click inside keeps it open (comment "we have to hover over generate first").

### (S) Person --> Choose Ticket Practices

Intended: canvas `togglePractice` saves the choice to the ticket's `session.json`.

### (S) Person --> Run Action Across Practices

Intended: canvas card menu and stage head run one action on every enabled practice in a stage (comment "we generate all for a ticket").

## (E) Generate Fidelity Output

### (S) Person --> Choose Action And Formats

Intended: canvas action list and format icons on a tile.

### (S) Person --> Generate Fidelity Output

Observed, then intended: a generate line in the session log counts as Generate done; kanban_spec "should show Generate done and Validate and Review remaining for that fidelity". The canvas runs it from a tile with the chosen formats, and `generate` has no format argument yet.

### (S) Person --> Render Fidelity Format

Intended: canvas `renderFormats` turns existing output into another format from a tile.

### (S) Claude Code --> Render Earlier Fidelity

Intended: canvas `renderBeforeGenerate`; when a fidelity uses a different format from the one before it, the earlier fidelity is rendered into that format before generating.

### (S) Person --> Send Sketch Iterate Or Document

Intended: canvas `sendFor` sends sketch, iterate, or document for a fidelity to the chat.

### (S) Claude Code --> Resolve Fidelity Output Paths

Observed: `Generate` and `Session.fidelity_outputs` take the outputs a fidelity declares, with the `session.json` overrides; `harness/guidance/fidelity_outputs_spec.py`, `space/session/session_spec.py`.

## (E) Validate Fidelity Output

### (S) Person --> Validate Fidelity

Observed, then intended: a validate line counts as done only when it names no graph-rule violations; kanban_spec "should still need Validate for that fidelity". The canvas runs it from a tile and marks the result.

### (S) Claude Code --> Save Validation Report

Observed: `Validate` saves `.sessions/<session>/validation-reports/<practice>-<fidelity>-<date>.md`; `cdd_guidance/actions/validate/validate_spec.py`.

### (S) Person --> Open Validation Report

Intended: canvas `reportVals`; the report opens in a side panel from a card or tile.

### (S) Person --> Fix Report Violations

Intended: canvas `violationVals` and `reportRule` send `/actions-satisfy` for one violation or every violation of a rule, and the report updates.

### (S) Person --> Satisfy Violations From Band

Observed: register.test "Satisfy on the band fills the prompt with the fidelities that have violations".

## (E) Review And Advance Fidelity

### (S) Person --> Review Fidelity

Observed, then intended: a review line completes a fidelity; kanban_spec "should show the fidelity done". The canvas adds a review button that needs a clean validate.

### (S) Kanban --> Ignore Early Review

Observed: `FidelityProgress.from_log`; kanban_spec "should not count the review".

### (S) Kanban --> Name Next Fidelity

Observed: `Ticket.next`; kanban_spec "should name Generate on story_map as next".

### (S) Kanban --> Complete Stage Work

Observed: `Ticket.is_done`, `Stage.done`; kanban_spec "should be done, waiting in its stage's done part".

### (S) Person --> Run Next Step

Observed, then intended: Run next fills the prompt in `ticketActions`. The canvas steps generate, validate, review for each practice in order, names the step on the button, and holds on fix violations until they are fixed (comment "goes through generate validate review for each practice in order").

## (E) Browse Ticket Files

### (S) Person --> List Ticket Files

Intended: canvas list mode of the files panel, for the card's or tile's fidelities; clicking a file opens it (comment "List files you can click on").

### (S) Person --> Browse Ticket Folder

Intended: canvas `folderGroups`, the folder mode of the files panel.

### (S) Person --> Open File Tabs

Intended: canvas `paneTabs`; one tab per format the fidelity offers, generated or not (comment "2 tabs for this use case; md and drawio").

### (S) Person --> Close File Tab

Intended: canvas `closeFileTab`.

## (E) Read Guidance Help

### (S) Person --> Open Fidelity Help

Intended: canvas `helpVals`; the ? on a tile opens that fidelity's overview, guidance, and rules in a side panel (comment "scrollable side panel").

### (S) Person --> Open Practice Help

Intended: canvas `helpVals`; a practice name opens its overview, guidance, and shared rules.

### (S) Person --> Open Forge Page

Intended: the Forge link in the help panel opens the fidelity's or practice's page.

---

## Scope boundary

**In scope:** what a Person, Claude Code, the Board Pane, and the Kanban tools do on the Session Board, from the code today and from the canvas at Version 72.

**Out of scope:** animation, colours, and other styling on the canvas, because they are not repeatable behaviour. `Ticket.pull`, `Kanban.pull`, and the Pull button are on no Story: the canvas retires them, and moving is the arrows only, so removing them is a change to the code rather than a behaviour on this map.
