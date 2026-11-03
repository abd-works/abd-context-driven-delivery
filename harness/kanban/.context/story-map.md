---
fidelity: [discovery]
artifact: [story-map]
format: md
section: body
---

# Story Map — Session Board

**Sources / context:** `harness/kanban/board.py`; `harness/kanban/ticket.py`; `harness/kanban/backlog_item.py`; `harness/kanban/kanban_spec.py`; `harness/kanban/kanban_tools_spec.py`; `harness/kanban/app/src/kanban/` and its `*.spec.ts`; `harness/kanban/app/tests/` (`story-actions.spec.ts`, `board-surface.spec.ts`, and the `tests/kanban/` sub-epics); `tools/chat-mod/hooks/register.ts`; `harness/kanban/.context/module-context.md`; `harness/kanban/.context/kanban-model.md`; the Board Pane canvas, Version 72 (https://claude.ai/artifact/LGLk189R4aZ14bgwcWRiPN, `project/Main.dc.html`) and its comment threads of 2026-10-31.

**Acceptance criteria:** A stack of cards on the story map is one Story. The top card is the Story and the cards under it are its acceptance criteria, listed under it here.

**Evidence:** The line under each Story and each acceptance criterion says where it stands. **Observed** means the code and specs do it today, and names the spec that shows it. **Inferred** means the code does it but no spec presses it. App specs are organised by these stories: a quoted Story name is a `describe` in `board-client.spec`, `ticket-client.spec`, `tile-client.spec`, `side-panel-client.spec`, `activation-client.spec`, `backlog-item-client.spec`, or `story-actions.spec`. Each Story heading links to its scenario file. Pane-era observations are kept in `retired/harness/kanban/`.

**Actors:** Person, Board App, Claude Code.

---

# (E) Move Work Forward On Session Board

## (E) Display Board And Details For Repo

### (S) Person --> [Open Board](move-work-forward-on-session-board/display-board-and-details-for-repo/open-board/open_board_story.test.py)

Observed: `board-page.ts` `start()` and `board-header-view.tsx` read the board when the page opens. Inferred: the `board` command in `tools/chat-mod/hooks/register.ts` opens the board from the chat.

### (S) Board App --> [Display Board](move-work-forward-on-session-board/display-board-and-details-for-repo/display-board/display_board_story.test.py)

Observed: board-client.spec "Display Board"; `board-columns-view.tsx`.

**Acceptance criteria:**

- Display Connected Status: with the cdd server not connected, a band across the page says so and how to reconnect, until the server answers again. Observed: board-client.spec "Display Connected Status"; story-actions.spec "Display Connected Status".
- Draw Board Columns: Backlog, Discovery, Specification, Implementation, and Complete, in that order, with In progress and Done inside each stage. Observed: `board-columns-view.tsx`; board-client.spec "Display Board".
- Refresh Board After Tool Calls: after a cdd tool call finishes, the board, an open tile, and an open Files panel or report show the state they are in then. Observed: board-client.spec, side-panel-client.spec, tile-client.spec, and story-actions.spec "Refresh Board After Tool Calls".
- Announce Ticket Changes: a toast shows when a ticket moves, including from In progress to Done and to the Backlog, or a fidelity is reviewed. Observed: board-client.spec "Announce Ticket Changes".

### (S) Person --> [Arrange Board And Details](move-work-forward-on-session-board/display-board-and-details-for-repo/arrange-board-and-details/arrange_board_and_details_story.test.py)

Observed: board-client.spec and story-actions.spec "Arrange Board And Details".

**Acceptance criteria:**

- Resize Board And Details: a drag on the split bar gives one region more height and cannot close either. Observed: board-client.spec "Resize Board And Details".
- Expand Board Or Details: one region takes the whole page and a second press brings the other back. Observed: board-client.spec "Expand Board Or Details".

### (S) Board App --> [Display Backlog Items As Tickets](move-work-forward-on-session-board/display-board-and-details-for-repo/display-backlog-items-as-tickets/display_backlog_items_as_tickets_story.test.py)

Observed: the Backlog column shows the title of each file in `.sessions/_backlog/`; kanban_spec "should show each backlog item in the Backlog column".

### (S) Board App --> [Display Ticket Card](move-work-forward-on-session-board/display-board-and-details-for-repo/display-ticket-card/display_ticket_card_story.test.py)

Observed: `ticket-card-view.tsx` draws the title and age, with one block per enabled practice, dim while its work is not started; board-client.spec "Display Ticket Card".

**Acceptance criteria:**

- Display Sessions As Tickets: each work session shows as one ticket and the main session is not on the board. Observed: kanban_spec "should show every work session as a ticket", "should leave main off the board".
- Place Ticket In Column: a ticket shows in the stage of its latest move, or before any move in the earliest stage its session shows work in. Observed: kanban_spec "should be in Specification".
- Display Active Ticket: the active ticket has a thick orange outline. Observed: kanban_spec "should name the ticket of the current session as active"; board-client.spec "Display Ticket Card".
- Show Active Ticket On Status Line: the chat's status line names the active ticket, its stage, its next guidance, and its violations. Inferred: `statusOf` in `tools/chat-mod/hooks/register.ts`.

### (S) Board App --> [Display Ticket Details](move-work-forward-on-session-board/display-board-and-details-for-repo/display-ticket-details/display_ticket_details_story.test.py)

Observed: `details-view.tsx`, `practice-grid-view.tsx`; board-client.spec, ticket-client.spec, and story-actions.spec "Display Ticket Details".

**Acceptance criteria:**

- A press anywhere on a card shows that ticket in the details region below the board, and with no card pressed the details show the active ticket. Observed: story-actions.spec "should show the ticket of a card pressed anywhere"; board-client.spec "should show the active ticket with no card pressed".
- The details show the ticket's practices with their fidelity progress and its latest validation reports. Observed: kanban_tools_spec "should show that fidelity's latest report".
- Expand Ticket: the expanded card shows the same tiles as the details, and only one is expanded at a time. Observed: tile-client.spec and story-actions.spec "Expand Ticket".

### (S) Person --> [Set Stage WIP Limit](move-work-forward-on-session-board/display-board-and-details-for-repo/set-stage-wip-limit/set_stage_wip_limit_story.test.py)

Observed: `Board.set_wip_limit`, saved in `.sessions/_board.json`; board-client.spec and story-actions.spec "Set Stage WIP Limit"; wip_limits.spec.shared "should give every stage a limit of 3 tickets until a person sets one".

### (S) Person --> [Arrange Side Panel](move-work-forward-on-session-board/display-board-and-details-for-repo/arrange-side-panel/arrange_side_panel_story.test.py)

Observed: `side-panels-view.tsx` and `drag-grip.ts` hold the report, files, and help panels; side-panel-client.spec and story-actions.spec "Arrange Side Panel".

**Acceptance criteria:**

- Resize Side Panel: a drag grip on the panel's left edge sets its width. Observed: side-panel-client.spec "Resize Side Panel".
- Expand Side Panel: one panel is expanded at a time and it takes the board's width less the other open panels. Observed: side-panel-client.spec "Expand Side Panel".
- Close Side Panel: × closes the panel. Observed: side-panel-client.spec "Close Side Panel".
- Scroll Fixed Columns: columns keep their width and scroll sideways when a panel opens. Observed: story-actions.spec "should keep the columns' width and scroll them sideways when a panel opens".

## (E) Steer Ticket Sessions

### (S) Person --> [Add Backlog Item](move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py)

Observed: the + on the Backlog heading opens a form with a title and text, and `BacklogItem.add` writes them to one markdown file in `.sessions/_backlog/`; backlog-item-client.spec and story-actions.spec "Add Backlog Item"; kanban_tools_spec "that adds a backlog item".

**Acceptance criteria:**

- Start Backlog Item: the → arrow on a backlog card opens a ticket in Discovery, and a ticket that was moved to the Backlog comes back with its work. Observed: `BacklogItem.start`; backlog-item-client.spec "Start Backlog Item"; kanban_tools_spec "that starts the item again".

### (S) Person --> [Open Ticket Session](move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py)

Observed: `Ticket.new` calls `Session.new`; `board-page.ts` `openNewTicket`; kanban_tools_spec "that opens a new ticket", "that opens a ticket on a folder in the repository".

**Acceptance criteria:**

- Choose Session Root: a person browses to the folder the ticket's work goes in, for the whole ticket or one practice, and can go back to the default. Observed: root-choice-client.spec and story-actions.spec "Choose Session Root".

### (S) Person --> [Close Active Session](move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py)

Observed: Close on the active ticket asks what to do with its work, then `Ticket.close` calls `Session.close` and moves the folder to `closed/`, so the ticket shows in Complete; activation-client.spec and story-actions.spec "Close Active Session"; kanban_tools_spec "should show the ticket in Complete", "should leave no ticket active".

### (S) Person --> [Restrict Actions To Active Session](move-work-forward-on-session-board/steer-ticket-sessions/restrict-actions-to-active-session/restrict_actions_to_active_session_story.test.py)

Observed: ticket-client.spec and story-actions.spec "Restrict Actions To Active Session". With Active session only on, every ticket that is not the active session disables what sends commands to a chat (comment "All buttons and list boxes should be disabled"). Moving, activating, and information stay open: files, the report, expand, and help (comment "you should still be able to get information").

### (S) Person --> [Move Ticket](move-work-forward-on-session-board/steer-ticket-sessions/move-ticket/move_ticket_story.test.py)

Observed: the arrows on a card, or a drag, move its ticket whatever its session's work; ticket-client.spec "Move Ticket"; move_ticket.spec.shared.

**Acceptance criteria:**

- Move Ticket To Next Column: the forward arrow moves it one column on from Done. Observed: `Ticket.move_next`; kanban_tools_spec "should show the ticket in the next stage".
- Move Ticket To Previous Column: the back arrow moves it one column back, into that column's Done. Observed: `Ticket.move_previous`; kanban_tools_spec "should show the ticket in Discovery's Done".
- A ticket moved out of Implementation closes into Complete. Observed: kanban_tools_spec "should close the ticket".
- A ticket moved back out of Complete reopens in Implementation. Observed: kanban_tools_spec "should reopen the ticket in Implementation".
- A ticket moved back out of Discovery goes to the Backlog with its work. Observed: `Ticket.move_previous`, `BacklogItem.holding`; kanban_tools_spec "should show an item in the Backlog with the ticket's title"; move_ticket.behavior.e2e "should say in a toast that it moved to the Backlog".

### (S) Person --> [Activate Ticket](move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py)

Observed: Activate on a card or the details opens a dialog with what to do on leaving and on opening, then calls `ticket.activate`; activation-client.spec and story-actions.spec "Activate Ticket".

**Acceptance criteria:**

- Commit, push, and merge into main are chosen when the session is left, and merge starts off. Observed: `Ticket.activate`, `Ticket.close`; activation-client.spec "should offer commit and push on leaving and open with merge off".
- Create Ticket Branch And Worktree: they are created when a ticket that has none is activated, and a ticket that has one is offered neither again. Observed: kanban_tools_spec "should create the ticket's branch when a ticket that has none is activated"; activation-client.spec "should offer a branch to a ticket that has none".

### (S) Person --> [Split Ticket Into Child Tickets](move-work-forward-on-session-board/steer-ticket-sessions/split-ticket-into-child-tickets/split_ticket_into_child_tickets_story.test.py)

Observed: `fillSplit` in `ticket-client.tsx` fills the prompt and `Ticket.new` records the parent; kanban_tools_spec "should name the ticket it was split from"; ticket-client.spec "should name a split ticket by its parent". No spec presses Split.

### (S) Person --> [Archive Ticket](move-work-forward-on-session-board/steer-ticket-sessions/archive-ticket/archive_ticket_story.test.py)

Observed: the Archive button calls `Ticket.archive`; kanban_spec "that has been archived".

### (S) Person --> [Write Ticket Handoff](move-work-forward-on-session-board/steer-ticket-sessions/write-ticket-handoff/write_ticket_handoff_story.test.py)

Observed: the Handoff button fills the prompt with `/space-handoff-handoff-session`; ticket-client.spec "Write Ticket Handoff".

### (S) Board App --> [Display Latest Handoff](move-work-forward-on-session-board/steer-ticket-sessions/display-latest-handoff/display_latest_handoff_story.test.py)

Observed: `Ticket.latest_handoff`; kanban_tools_spec "with handoffs written for the ticket", "should show no handoff for a ticket that has none"; side-panel-client.spec "should show the handoff in a tab".

## (E) Guide Work Through Practices

### (S) Board App --> [Display Fidelity Progress](move-work-forward-on-session-board/guide-work-through-practices/display-fidelity-progress/display_fidelity_progress_story.test.py)

Observed: the step marks on a tile, ○ to do, … in progress, ✓ done; kanban_tools_spec "should show each fidelity's Generate, Validate, and Review"; kanban_spec "with a fidelity generated".

**Acceptance criteria:**

- Each fidelity shows Generate, Validate, and Review as to do, in progress, or done. Observed: kanban_tools_spec "should show each fidelity's Generate, Validate, and Review".

### (S) Person --> [Open Practice Tile](move-work-forward-on-session-board/guide-work-through-practices/open-practice-tile/open_practice_tile_story.test.py)

Observed: a tile opens after a short hover, closes on leaving, and a press keeps it open; tile-client.spec and story-actions.spec "Open Practice Tile".

### (S) Person --> [Choose Ticket Practices](move-work-forward-on-session-board/guide-work-through-practices/choose-ticket-practices/choose_ticket_practices_story.test.py)

Observed: `Ticket.enable_practice` saves the choice to the ticket's `session.json`; kanban_tools_spec "that turns a practice off for a ticket"; ticket-client.spec and story-actions.spec "Choose Ticket Practices".

### (S) Person --> [Run Action Across Practices](move-work-forward-on-session-board/guide-work-through-practices/run-action-across-practices/run_action_across_practices_story.test.py)

Observed: the stage head sends one action for every enabled practice in a stage; tile-client.spec "Run Action Across Practices". Several tiles and stage heads can be open at once: tile-client.spec "with two stage heads pressed".

### (S) Person --> [Mark Ticket Done In Stage](move-work-forward-on-session-board/guide-work-through-practices/mark-ticket-done-in-stage/mark_ticket_done_in_stage_story.test.py)

Observed: the arrow takes an In progress ticket to Done without crossing a column, written as a `done <stage>` session log line the ticket reads back, and back from Done as `in-progress <stage>`; kanban_spec "should be done in its stage, in the same column"; kanban_tools_spec "and back from Done"; move_ticket.behavior.e2e "should say in a toast that it is done in its stage".

### (S) Board App --> [Add Active Ticket To System Prompt](move-work-forward-on-session-board/guide-work-through-practices/add-active-ticket-to-system-prompt/add_active_ticket_to_system_prompt_story.test.py)

Inferred: the `prompt.compose` handler in `tools/chat-mod/hooks/register.ts` names the active ticket and its next guidance, and leaves the prompt unchanged with no active ticket. No spec covers it.

### (S) Person --> [Open Help](move-work-forward-on-session-board/guide-work-through-practices/open-help/open_help_story.test.py)

Observed: `Board.help`; the ? on a tile or a practice name opens help in a side panel; help-text.spec and story-actions.spec "Open Help"; kanban_tools_spec "that opens help on a fidelity", "that opens help on a practice".

**Acceptance criteria:**

- Fidelity help shows its overview, guidance, and rules. Observed: kanban_tools_spec "that opens help on a fidelity".
- Practice help shows its overview, guidance, and shared rules. Observed: kanban_tools_spec "that opens help on a practice".
- The Forge link opens the fidelity's or practice's page. Inferred: `FIDELITIES_WITHOUT_PAGE` in `harness/kanban/board.py` leaves out fidelities with no page.

### (S) Person --> [Run Next Step](move-work-forward-on-session-board/guide-work-through-practices/run-next-step/run_next_step_story.test.py)

Observed: on generate, Run next sends the commands of `ticket.generate_commands` for the fidelity's default format; on validate or review it fills the prompt; ticket-client.spec "Run Next Step".

**Acceptance criteria:**

- Name Next Fidelity: the button names the step that runs next. Observed: `Ticket.next`, `Ticket.next_action`; kanban_spec "should name Generate on story_map as next"; ticket-client.spec "should mark its tile as the next one".
- Run next steps through generate, validate, and review for each practice in order. Observed: `Ticket.next_action`; kanban_spec "with every required fidelity in its stage done".
- Run next holds on fix violations until they are fixed, and says "fix violations". Observed: kanban_spec "should name satisfy as the next action".

## (E) Generate Fidelity Outputs

### (S) Person --> [Choose Action And Formats](move-work-forward-on-session-board/generate-fidelity-outputs/choose-action-and-formats/choose_action_and_formats_story.test.py)

Observed: the tile's action bar lists the actions and format chips. A tile opens with the default format's chip picked unless that output exists, a chip stands for a group and each fidelity uses one format from it, and a generated chip is marked. Run stays off with no format, on a render with nothing to render, with no chat connected, and on a locked ticket. tile-client.spec "Choose Action And Formats", "should give each fidelity its default format", "should keep Run off until a format is chosen".

### (S) Claude Code --> [Resolve Fidelity Output Paths](move-work-forward-on-session-board/generate-fidelity-outputs/resolve-fidelity-output-paths/resolve_fidelity_output_paths_story.test.py)

Observed: `Generate` and `Session.fidelity_outputs` take the outputs a fidelity declares, with the `session.json` overrides; `harness/guidance/fidelity_outputs_spec.py`; `space/session/session_spec.py` "should put each format's file under the practice's root folder".

### (S) Person --> [Generate Fidelity Output](move-work-forward-on-session-board/generate-fidelity-outputs/generate-fidelity-output/generate_fidelity_output_story.test.py)

Observed: a generate line in the session log counts as Generate done; kanban_spec "should show Generate done and Validate and Review remaining for that fidelity". Run on a tile sends `/actions-generate <fidelities> format=<formats>`; tile-client.spec and story-actions.spec "Generate Fidelity Output". `generate` has no format argument of its own yet, so the format is passed in the command's words.

**Acceptance criteria:**

- When a fidelity uses a different format from the one before it, the earlier fidelity is rendered into that format first. Observed: `Ticket.generate_commands`; tile-client.spec "Generate Fidelity Output".

### (S) Person --> [Render Fidelity Format](move-work-forward-on-session-board/generate-fidelity-outputs/render-fidelity-format/render_fidelity_format_story.test.py)

Observed: Render on a tile sends `/actions-render`; tile-client.spec "Render Fidelity Format".

### (S) Person --> [Send Sketch Iterate Or Document](move-work-forward-on-session-board/generate-fidelity-outputs/send-sketch-iterate-or-document/send_sketch_iterate_or_document_story.test.py)

Observed: Run on a tile sends `/actions-sketch`, `/actions-iterate`, or `/actions-document` to the chosen chat; tile-client.spec and story-actions.spec "Send Sketch Iterate Or Document"; chat-client.spec "should choose the only chat connected".

## (E) Validate Fidelity Outputs

### (S) Person --> [Validate Fidelity](move-work-forward-on-session-board/validate-fidelity-outputs/validate-fidelity/validate_fidelity_story.test.py)

Observed: a validate line counts as done only when it names no graph-rule violations; kanban_spec "that has a validate with no violations". Validate on a tile sends `/actions-validate` and the tile marks the result; tile-client.spec "Validate Fidelity".

### (S) Claude Code --> [Save Validation Report](move-work-forward-on-session-board/validate-fidelity-outputs/save-validation-report/save_validation_report_story.test.py)

Observed: `Validate` saves `.sessions/<session>/validation-reports/<practice>-<fidelity>-<date>.md` and the graph it checked under the same name in `.json`; `cdd_guidance/actions/validate/validate_spec.py` "should save a report for each listed guidance", "should leave an earlier report's saved graph as it was".

### (S) Person --> [Open Validation Report](move-work-forward-on-session-board/validate-fidelity-outputs/open-validation-report/open_validation_report_story.test.py)

Observed: `Ticket.report` opens the latest report in a side panel from the details or a tile; side-panel-client.spec and story-actions.spec "Open Validation Report"; kanban_tools_spec "with validation reports saved for a fidelity".

### (S) Person --> [Fix Report Violations](move-work-forward-on-session-board/validate-fidelity-outputs/fix-report-violations/fix_report_violations_story.test.py)

Observed: `Ticket.report` builds the rules from the graph saved beside the report, and a report with no saved graph says so; kanban_tools_spec "with a validation report saved without its graph". Fix and Fix all send `/actions-satisfy` for one violation or every violation of a rule, and an open report is read again after a cdd tool call; side-panel-client.spec "Fix Report Violations", "should send Fix all for every violation of a rule".

### (S) Person --> [Satisfy Violations From Band](move-work-forward-on-session-board/validate-fidelity-outputs/satisfy-violations-from-band/satisfy_violations_from_band_story.test.py)

Observed: ticket-client.spec and story-actions.spec "Satisfy Violations From Band".

**Acceptance criteria:**

- Show Violations Band: the band shows the active ticket's violations, and only when it has some. Observed: `ViolationsBandView` in `board-page-view.tsx`.

## (E) Review Fidelity Outputs

### (S) Person --> [List Ticket Files](move-work-forward-on-session-board/review-fidelity-outputs/list-ticket-files/list_ticket_files_story.test.py)

Observed: `Ticket.files`, the list mode of the files panel, for the tile's or ticket's fidelities and no others; pressing a file opens it; side-panel-client.spec "List Ticket Files"; kanban_tools_spec "with a fidelity's markdown generated". On a ticket whose work is in the whole repository, a pattern lists only what its branch changed: kanban_tools_spec "with specs in the repository and one changed on the ticket's branch". A list that cannot be read says so in a toast: side-panel-client.spec "with a list that cannot be read".

### (S) Person --> [Browse Ticket Folder](move-work-forward-on-session-board/review-fidelity-outputs/browse-ticket-folder/browse_ticket_folder_story.test.py)

Observed: the folder mode of the files panel groups the files under their folders; side-panel-client.spec "Browse Ticket Folder", "Browse Ticket's Session Folder".

### (S) Person --> [View Files](move-work-forward-on-session-board/review-fidelity-outputs/view-files/view_files_story.test.py)

Observed: `Ticket.read_file` and `file-views-view.tsx`; one tab per format the fidelity offers, generated or not, and × closes one; side-panel-client.spec "View Files".

### (S) Person --> [Review Fidelity](move-work-forward-on-session-board/review-fidelity-outputs/review-fidelity/review_fidelity_story.test.py)

Observed: a review line completes a fidelity; kanban_tools_spec "with a ticket whose story map has passed validate"; ticket-client.spec and tile-client.spec "Review Fidelity". Reviewed on a tile is off until a clean validate.

**Acceptance criteria:**

- Ignore Early Review: a review before a clean validate does not count. Observed: kanban_spec "that was reviewed before its validate passed".
- Complete Stage Work: when every fidelity of a stage is reviewed, the ticket shows in that stage's Done part. Observed: `Ticket.is_done`; kanban_spec "with every required fidelity in its stage done".

---

## Scope boundary

**In scope:** what a Person does on the Session Board and what the Board App shows them, from the code today and from the canvas at Version 72.

**Out of scope:** animation on the canvas, because it is not repeatable behaviour.
