---
fidelity: [discovery]
artifact: [story-map]
format: md
section: body
---

# Story Map — Session Board

**Sources / context:** `harness/kanban/board.py`; `harness/kanban/ticket.py`; `harness/kanban/backlog_item.py`; `harness/kanban/kanban_spec.py`; `harness/kanban/kanban_tools_spec.py`; `harness/kanban/app/src/kanban/` and its `*.spec.ts`; `harness/kanban/app/tests/` (`story-actions.spec.ts`, `board-surface.spec.ts`, and the `tests/kanban/` sub-epics); `tools/chat-mod/hooks/register.ts`; `harness/kanban/.context/module-context.md`; `harness/kanban/.context/kanban-model.md`; the Board Pane canvas, Version 72 (https://claude.ai/artifact/LGLk189R4aZ14bgwcWRiPN, `project/Main.dc.html`) and its comment threads of 2026-10-31.

**Evidence:** The line under each Story says where it stands. **Observed** means the code and specs do it today. **Inferred** means the code does it but no spec presses it. The spec signatures behind each Story are in [session-board-behavior.md](session-board-behavior.md), under the Story's name. Each Story heading links to its scenario file. Pane-era observations are kept in `retired/harness/kanban/`.

**Actors:** Person, Board App, Claude Code.

---

# (E) Move Work Forward On Session Board

## (E) See Work On Session Board

### (S) Person --> [Open Board](move-work-forward-on-session-board/see-work-on-session-board/open-board/open_board_story.test.py)

Observed: `board-page.ts` `start()` and `board-header-view.tsx` read the board when the page opens. Inferred: the `board` command in `tools/chat-mod/hooks/register.ts` opens the board from the chat.

### (S) Board App --> [Display Board](move-work-forward-on-session-board/see-work-on-session-board/display-board/display_board_story.test.py)

Observed: `board-columns-view.tsx`.

### (S) Person --> [Arrange Board And Details](move-work-forward-on-session-board/see-work-on-session-board/arrange-board-and-details/arrange_board_and_details_story.test.py)

Observed.

### (S) Board App --> [Display Backlog Items As Tickets](move-work-forward-on-session-board/see-work-on-session-board/display-backlog-items-as-tickets/display_backlog_items_as_tickets_story.test.py)

Observed: the Backlog column shows the title of each file in `.sessions/_backlog/`.

### (S) Board App --> [Display Ticket Card](move-work-forward-on-session-board/see-work-on-session-board/display-ticket-card/display_ticket_card_story.test.py)

Observed: `ticket-card-view.tsx` draws the title and age, with one block per enabled practice, dim while its work is not started.

### (S) Board App --> [Display Ticket Details](move-work-forward-on-session-board/see-work-on-session-board/display-ticket-details/display_ticket_details_story.test.py)

Observed: `details-view.tsx`, `practice-grid-view.tsx`.

### (S) Person --> [Set Stage WIP Limit](move-work-forward-on-session-board/see-work-on-session-board/set-stage-wip-limit/set_stage_wip_limit_story.test.py)

Observed: `Board.set_wip_limit`, saved in `.sessions/_board.json`.

### (S) Person --> [Arrange Side Panel](move-work-forward-on-session-board/see-work-on-session-board/arrange-side-panel/arrange_side_panel_story.test.py)

Observed: `side-panels-view.tsx` and `drag-grip.ts` hold the report, files, and help panels.

### (S) Person --> [Restrict Actions To Active Session](move-work-forward-on-session-board/see-work-on-session-board/restrict-actions-to-active-session/restrict_actions_to_active_session_story.test.py)

Observed. With Active session only on, every ticket that is not the active session disables what sends commands to a chat (comment "All buttons and list boxes should be disabled"). Moving, activating, and information stay open: files, the report, expand, and help (comment "you should still be able to get information").

## (E) Steer Ticket Sessions

### (S) Person --> [Add Backlog Item](move-work-forward-on-session-board/steer-ticket-sessions/add-backlog-item/add_backlog_item_story.test.py)

Observed: the + on the Backlog heading opens a form with a title and text, and `BacklogItem.add` writes them to one markdown file in `.sessions/_backlog/`.

### (S) Person --> [Open Ticket Session](move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py)

Observed: `Ticket.new` calls `Session.new`; `board-page.ts` `openNewTicket`.

### (S) Person --> [Close Active Session](move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py)

Observed: Close on the active ticket's card sends `/space:session:close-session` to the chat, which calls `Session.close`; the ticket stays in its column. Moving the active ticket into Complete asks what to do with its work, then `Ticket.close` calls `Session.close` and moves the folder to `closed/`, so the ticket shows in Complete.

### (S) Person --> [Move Ticket](move-work-forward-on-session-board/steer-ticket-sessions/move-ticket/move_ticket_story.test.py)

Observed: the arrows on a card, or a drag, move its ticket whatever its session's work.

### (S) Person --> [Activate Ticket](move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py)

Observed: Activate on a card or the details opens a dialog with what to do on leaving and on opening, then calls `ticket.activate`.

### (S) Person --> [Split Ticket Into Child Tickets](move-work-forward-on-session-board/steer-ticket-sessions/split-ticket-into-child-tickets/split_ticket_into_child_tickets_story.test.py)

Observed: `Ticket.new` records the parent (kanban_tools_spec 'that opens a ticket split from another'). Inferred: Split on a card fills the prompt through `fillSplit` in `ticket-client.tsx`; no spec presses Split.

### (S) Person --> [Archive Ticket](move-work-forward-on-session-board/steer-ticket-sessions/archive-ticket/archive_ticket_story.test.py)

Observed: `Ticket.archive`, called as the `ticket.archive` tool (kanban_spec 'that has been archived'; kanban_tools_spec 'that archives a ticket'). The board app has no Archive button.

### (S) Person --> [Write Ticket Handoff](move-work-forward-on-session-board/steer-ticket-sessions/write-ticket-handoff/write_ticket_handoff_story.test.py)

Observed: the Handoff button fills the prompt with `/space-handoff-handoff-session`.

### (S) Board App --> [Display Latest Handoff](move-work-forward-on-session-board/steer-ticket-sessions/display-latest-handoff/display_latest_handoff_story.test.py)

Observed: `Ticket.latest_handoff`.

## (E) Guide Work Through Practices

### (S) Board App --> [Display Fidelity Progress](move-work-forward-on-session-board/guide-work-through-practices/display-fidelity-progress/display_fidelity_progress_story.test.py)

Observed: the step marks on a tile, ○ to do, … in progress, ✓ done.

### (S) Person --> [Open Practice Tile](move-work-forward-on-session-board/guide-work-through-practices/open-practice-tile/open_practice_tile_story.test.py)

Observed: a tile opens after a short hover, closes on leaving, and a press keeps it open.

### (S) Person --> [Choose Ticket Practices](move-work-forward-on-session-board/guide-work-through-practices/choose-ticket-practices/choose_ticket_practices_story.test.py)

Observed: `Ticket.enable_practice` saves the choice to the ticket's `session.json`.

### (S) Person --> [Send Action To Stage Practices](move-work-forward-on-session-board/guide-work-through-practices/send-action-to-stage-practices/send_action_to_stage_practices_story.test.py)

Observed: the stage head sends one action for every enabled practice in a stage. Several tiles and stage heads can be open at once.

### (S) Person --> [Mark Ticket Done In Stage](move-work-forward-on-session-board/guide-work-through-practices/mark-ticket-done-in-stage/mark_ticket_done_in_stage_story.test.py)

Observed: the arrow takes an In progress ticket to Done without crossing a column, written as a `done <stage>` session log line the ticket reads back, and back from Done as `in-progress <stage>`.

### (S) Board App --> [Add Active Ticket To System Prompt](move-work-forward-on-session-board/guide-work-through-practices/add-active-ticket-to-system-prompt/add_active_ticket_to_system_prompt_story.test.py)

Inferred: the `prompt.compose` handler in `tools/chat-mod/hooks/register.ts` names the active ticket and its next guidance, and leaves the prompt unchanged with no active ticket. No spec covers it.

### (S) Person --> [Open Help](move-work-forward-on-session-board/guide-work-through-practices/open-help/open_help_story.test.py)

Observed: `Board.help`; the ? on a tile or a practice name opens help in a side panel.

### (S) Person --> [Send Next Fidelity Action](move-work-forward-on-session-board/guide-work-through-practices/send-next-fidelity-action/send_next_fidelity_action_story.test.py)

Observed: on generate, Run next sends the commands of `ticket.generate_commands` for the fidelity's default format; on validate or review it fills the prompt.

## (E) Generate Fidelity Outputs

### (S) Person --> [Choose Action And Formats](move-work-forward-on-session-board/generate-fidelity-outputs/choose-action-and-formats/choose_action_and_formats_story.test.py)

Observed: the tile's action bar lists the actions and format chips. A tile opens with the default format's chip picked unless that output exists, a chip stands for a group and each fidelity uses one format from it, and a generated chip is marked. Run stays off with no format, on a render with nothing to render, with no chat connected, and on a locked ticket.

### (S) Claude Code --> [Resolve Fidelity Output Paths](move-work-forward-on-session-board/generate-fidelity-outputs/resolve-fidelity-output-paths/resolve_fidelity_output_paths_story.test.py)

Observed: `Generate` and `Session.fidelity_outputs` take the outputs a fidelity declares, with the `session.json` overrides.

### (S) Person --> [Generate Fidelity Output](move-work-forward-on-session-board/generate-fidelity-outputs/generate-fidelity-output/generate_fidelity_output_story.test.py)

Observed: a generate line in the session log counts as Generate done. Run on a tile sends `/actions-generate <fidelities> format=<formats>`. `generate` has no format argument of its own yet, so the format is passed in the command's words.

### (S) Person --> [Render Fidelity Format](move-work-forward-on-session-board/generate-fidelity-outputs/render-fidelity-format/render_fidelity_format_story.test.py)

Observed: Render on a tile sends `/actions-render`.

### (S) Person --> [Send Tile Action To Chat](move-work-forward-on-session-board/generate-fidelity-outputs/send-tile-action-to-chat/send_tile_action_to_chat_story.test.py)

Observed: Run on a tile sends `/actions-sketch`, `/actions-iterate`, or `/actions-document` to the chosen chat.

## (E) Validate Fidelity Outputs

### (S) Person --> [Validate Fidelity](move-work-forward-on-session-board/validate-fidelity-outputs/validate-fidelity/validate_fidelity_story.test.py)

Observed: a validate line counts as done only when it names no graph-rule violations. Validate on a tile sends `/actions-validate` and the tile marks the result.

### (S) Claude Code --> [Save Validation Report](move-work-forward-on-session-board/validate-fidelity-outputs/save-validation-report/save_validation_report_story.test.py)

Observed: `Validate` saves `.sessions/<session>/validation-reports/<practice>-<fidelity>-<date>.md` and the graph it checked under the same name in `.json`.

### (S) Person --> [Open Validation Report](move-work-forward-on-session-board/validate-fidelity-outputs/open-validation-report/open_validation_report_story.test.py)

Observed: `Ticket.report` opens the latest report in a side panel from the details or a tile.

### (S) Person --> [Fix Report Violations](move-work-forward-on-session-board/validate-fidelity-outputs/fix-report-violations/fix_report_violations_story.test.py)

Observed: `Ticket.report` builds the rules from the graph saved beside the report, and a report with no saved graph says so. Fix sends the chat one message with the rule, the error at its file and line, and the content that failed; Fix all sends every violation of the rule in one such message; and an open report is read again after a cdd tool call.

### (S) Board App --> [Display Violations Band](move-work-forward-on-session-board/validate-fidelity-outputs/display-violations-band/display_violations_band_story.test.py)

Observed.

## (E) Review Fidelity Outputs

### (S) Person --> [List Ticket Files](move-work-forward-on-session-board/review-fidelity-outputs/list-ticket-files/list_ticket_files_story.test.py)

Observed: `Ticket.files`, the files mode of the files panel (`FILE_VIEWS` in `file-views-view.tsx`), for the tile's or ticket's fidelities and no others; pressing a file opens it. On a ticket whose work is in the whole repository, a pattern lists only what its branch changed. A list that cannot be read says so in a toast.

### (S) Person --> [Browse Ticket Folder](move-work-forward-on-session-board/review-fidelity-outputs/browse-ticket-folder/browse_ticket_folder_story.test.py)

Observed: the folder mode of the files panel groups the files under their folders.

### (S) Person --> [View Fidelity Files](move-work-forward-on-session-board/review-fidelity-outputs/view-fidelity-files/view_fidelity_files_story.test.py)

Observed: `Ticket.read_file` and `file-views-view.tsx`; one tab per format the fidelity offers, generated or not, and × closes one.

### (S) Person --> [Review Fidelity](move-work-forward-on-session-board/review-fidelity-outputs/review-fidelity/review_fidelity_story.test.py)

Observed: a review line completes a fidelity. Reviewed on a tile is off until a clean validate.

---

## Scope boundary

**In scope:** what a Person does on the Session Board and what the Board App shows them, from the code today and from the canvas at Version 72.

**Out of scope:** animation on the canvas, because it is not repeatable behaviour.
