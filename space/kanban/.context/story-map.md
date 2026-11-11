---
fidelity: [discovery]
artifact: [story-map]
format: md
section: body
---

# Story Map — CDD Kanban

**Sources / context:** `.sessions/session-board/ticket-enhancements.md` (the ticket enhancements, from the board notes now in `.sessions/_backlog/*.md, one per thin-slice increment` and the board notes of 2026-11-05); `space/kanban/board.py`; `space/kanban/ticket.py`; `space/kanban/backlog_item.py`; `space/kanban/kanban_spec.py`; `space/kanban/kanban_tools_spec.py`; `space/kanban/app/src/kanban/` and its `*.spec.ts`; `space/kanban/app/tests/` (`story-actions.spec.ts`, `board-surface.spec.ts`, and the `tests/kanban/` sub-epics); `harness/chat-ui/pane/hooks/register.ts`; `space/kanban/.context/module-context.md`; `space/kanban/.context/kanban-model.md`; the Board Pane canvas, Version 72 (https://claude.ai/artifact/LGLk189R4aZ14bgwcWRiPN, `project/Main.dc.html`) and its comment threads of 2026-10-31.

**Evidence:** The line under each Story says where it stands. **Observed** means the code and specs do it today. **Inferred** means the code does it but no spec presses it. **Intended** means a source asks for it and the code does not do it yet. The spec signatures behind each Story are in [session-board-behavior.md](session-board-behavior.md), under the Story's name. Each Story heading links to its scenario file. Pane-era observations are kept in `retired/harness/kanban/`.

**Actors:** Person, Board App, Claude Code.

---

# (E) Move Work Forward On Session Board

## (E) See Work On Session Board

### (S) Person --> [Open Board](../../../harness/.context/stories/move-work-forward-on-session-board/see-work-on-session-board/see_work_on_session_board_story.test.md#story-open-board)

Observed: `board-page.ts` `start()` and `board-header-view.tsx` read the board when the page opens. Inferred: the `board` command in `harness/chat-ui/pane/hooks/register.ts` opens the board from the chat.

### (S) Board App --> [Display Board](../../../harness/.context/stories/move-work-forward-on-session-board/see-work-on-session-board/see_work_on_session_board_story.test.md#story-display-board)

Observed: `board-columns-view.tsx`.

### (S) Person --> [Arrange Board And Details](../../../harness/.context/stories/move-work-forward-on-session-board/see-work-on-session-board/see_work_on_session_board_story.test.md#story-arrange-board-and-details)

Observed.

### (S) Board App --> [Display Backlog Items As Tickets](../../../harness/.context/stories/move-work-forward-on-session-board/see-work-on-session-board/see_work_on_session_board_story.test.md#story-display-backlog-items-as-tickets)

Observed: the Backlog column shows the title of each file in `.sessions/_backlog/`.

### (S) Board App --> [Display Ticket Card](../../../harness/.context/stories/move-work-forward-on-session-board/see-work-on-session-board/see_work_on_session_board_story.test.md#story-display-ticket-card)

Observed: `ticket-card-view.tsx` draws the title and age, with one segment per enabled fidelity, dim while its work is not started.

### (S) Board App --> [Display Ticket Details](../../../harness/.context/stories/move-work-forward-on-session-board/see-work-on-session-board/see_work_on_session_board_story.test.md#story-display-ticket-details)

Observed: `details-view.tsx`, `practice-grid-view.tsx`. Intended (`.sessions/session-board/ticket-enhancements.md`): a click on any empty area of a card expands it.

### (S) Person --> [Set Stage WIP Limit](../../../harness/.context/stories/move-work-forward-on-session-board/see-work-on-session-board/see_work_on_session_board_story.test.md#story-set-stage-wip-limit)

Observed: `Stage.set_wip_limit`, saved in `.sessions/_board.json`.

### (S) Person --> [Arrange Side Panel](../../../harness/.context/stories/move-work-forward-on-session-board/see-work-on-session-board/see_work_on_session_board_story.test.md#story-arrange-side-panel)

Observed: `side-panels-view.tsx` and `drag-grip.ts` hold the report, files, and help panels.

### (S) Person --> [Restrict Actions To Active Session](../../../harness/.context/stories/move-work-forward-on-session-board/steer-ticket-sessions/steer_ticket_sessions_story.test.md#story-restrict-actions-to-active-session)

Observed. With Active session only on, every ticket that is not the active session disables what sends commands to a chat (comment "All buttons and list boxes should be disabled"). Moving, activating, and information stay open: files, the report, expand, and help (comment "you should still be able to get information").

## (E) Steer Ticket Sessions

### (S) Person --> [Open Ticket Session](../../../harness/.context/stories/move-work-forward-on-session-board/steer-ticket-sessions/steer_ticket_sessions_story.test.md#story-open-ticket-session)

Observed: `Ticket.create` calls `Sessions.create`; `board-page.ts` `openNewTicket`.

### (S) Person --> [Close Active Session](../../../harness/.context/stories/move-work-forward-on-session-board/steer-ticket-sessions/steer_ticket_sessions_story.test.md#story-close-active-session)

Observed: Close on the active ticket's card sends `/space:session:close-session` to the chat, which calls `Session.close`; the ticket stays in its column. Moving the active ticket into Complete asks what to do with its work, then `Ticket.close` calls `Session.close` and moves the folder to `_complete/`, so the ticket shows in Complete.

Requested 2026-11-09: main is the default session, the session of every chat in the repository's own folder, which stays on the default branch. Main is a ticket on the board like any other, in its stage's column (Discovery while it has no work), with the practices its session.json names; it never closes, archives, or goes to the Backlog.

### (S) Person --> [Move Ticket](../../../harness/.context/stories/move-work-forward-on-session-board/steer-ticket-sessions/steer_ticket_sessions_story.test.md#story-move-ticket)

Observed: the arrows on a card, or a drag, move its ticket whatever its session's work.

### (S) Person --> [Activate Ticket](../../../harness/.context/stories/move-work-forward-on-session-board/steer-ticket-sessions/steer_ticket_sessions_story.test.md#story-activate-ticket)

Requested 2026-11-10: sessions open only from main. Activating a ticket opens it in its own worktree, on its own branch, made when missing, after the session folders not yet committed are committed on main and pushed; a ticket opened before keeps its worktree. The chat that asked stays on main, and the ticket's own chat works in the worktree: a chat there works on that ticket. No chat moves, and nothing is left: another ticket is another chat and worktree.

### (S) Person --> [Delete Ticket Branch](move-work-forward-on-session-board/steer-ticket-sessions/delete-ticket-branch/delete_ticket_branch_story.test.md)

Requested 2026-11-09: closing a session offers delete branch whenever its branch is in git, checked out or not. Deleting the branch deletes it here and on origin without merging it, and deletes the worktree that has it checked out. Merge is its own choice.

### (S) Person --> [Write Ticket Handoff](../../../harness/.context/stories/move-work-forward-on-session-board/steer-ticket-sessions/steer_ticket_sessions_story.test.md#story-write-ticket-handoff)

Observed: the Handoff button fills the prompt with `/space-session-handoff-session`.

### (S) Board App --> [Display Latest Handoff](../../../harness/.context/stories/move-work-forward-on-session-board/steer-ticket-sessions/steer_ticket_sessions_story.test.md#story-display-latest-handoff)

Observed: `Session.latest_handoff`, sent as the `handoff` of a ticket's session.

## (E) Maintain Tickets

### (S) Person --> [Add Backlog Item](../../../harness/.context/stories/move-work-forward-on-session-board/maintain-tickets/maintain_tickets_story.test.md#story-add-backlog-item)

Observed: the + on the Backlog heading opens a form with a title and text, and `BacklogItem.create` writes them to one markdown file in `.sessions/_backlog/`.

### (S) Person --> Edit Ticket Text

Intended (`.sessions/session-board/ticket-enhancements.md`): a double click on a card's text edits it. A backlog item's text is its markdown file in `.sessions/_backlog/`; a session ticket's text is a markdown file kept in its session folder, which the session's instructions refer to, so the board and the agent read the same text.

### (S) Person --> Reorder Tickets In Column

Intended (`.sessions/session-board/ticket-enhancements.md`): a ticket dragged up or down within its column keeps that place.

### (S) Person --> [Archive Ticket](../../../harness/.context/stories/move-work-forward-on-session-board/maintain-tickets/maintain_tickets_story.test.md#story-archive-ticket)

Observed: `Ticket.archive`, called as the `ticket.archive` tool (kanban_spec 'that has been archived'; kanban_tools_spec 'that archives a ticket'). The board app has no Archive button. Intended (`.sessions/session-board/ticket-enhancements.md`): Archive on a card.

### (S) Person --> Delete Ticket

Intended (`.sessions/session-board/ticket-enhancements.md`): Delete on a card removes the ticket and its session folder from the board.

## (E) Organize Ticket Hierarchy

### (S) Person --> [Split Ticket Into Child Tickets](../../../harness/.context/stories/move-work-forward-on-session-board/organize-ticket-hierarchy/organize_ticket_hierarchy_story.test.md#story-split-ticket-into-child-tickets)

Observed: `Ticket.create` records the parent (kanban_tools_spec 'that opens a ticket split from another'). Inferred: Split on a card fills the prompt through `fillSplit` in `ticket-client.tsx`; no spec presses Split. Intended (`.sessions/session-board/ticket-enhancements.md`): a split goes to the AI, which slices the ticket thinly into the child tickets it proposes.

### (S) Person --> Add Child Ticket

Intended (`.sessions/session-board/ticket-enhancements.md`): a person adds a child ticket to a parent by hand.

### (S) Board App --> Display Child Tickets In Parent

Intended (`.sessions/session-board/ticket-enhancements.md`): a parent's card holds its child tickets stacked inside it, with the parent's title small above them.

### (S) Person --> Expand Parent Ticket

Intended (`.sessions/session-board/ticket-enhancements.md`): a parent collapses to its own card and expands to show its children.

### (S) Person --> Detach Child Ticket

Intended (`.sessions/session-board/ticket-enhancements.md`): a child pulled out of its parent becomes a ticket of its own beside it and moves independently.

### (S) Person --> Move Child Ticket To Another Parent

Intended (`.sessions/session-board/ticket-enhancements.md`): a ticket added as a child of a different parent leaves its old parent.

### (S) Claude Code --> Nest Child Branch And Session

Intended (`.sessions/session-board/ticket-enhancements.md`): a child ticket's branch and session nest under its parent's, so the hierarchy holds in git and in `.sessions/` as on the board.

## (E) Guide Work Through Practices

### (S) Board App --> [Display Fidelity Progress](../../../harness/.context/stories/move-work-forward-on-session-board/guide-work-through-practices-on-board/guide_work_through_practices_on_board_story.test.md#story-display-fidelity-progress)

Observed: the step marks on a tile, ○ to do, … in progress, ✓ done.

### (S) Person --> [Open Practice Tile](../../../harness/.context/stories/move-work-forward-on-session-board/guide-work-through-practices-on-board/guide_work_through_practices_on_board_story.test.md#story-open-practice-tile)

Observed: a tile opens after a short hover, closes on leaving, and a press keeps it open.

### (S) Person --> [Choose Ticket Practices](../../../harness/.context/stories/move-work-forward-on-session-board/guide-work-through-practices-on-board/guide_work_through_practices_on_board_story.test.md#story-choose-ticket-practices)

Observed: `PracticeSessionOutput.enable` saves the choice to the ticket's `session.json`.

### (S) Person --> [Send Action To Stage Practices](../../../harness/.context/stories/move-work-forward-on-session-board/guide-work-through-practices-on-board/guide_work_through_practices_on_board_story.test.md#story-send-action-to-stage-practices)

Observed: the stage head sends one action for every enabled practice in a stage. Several tiles and stage heads can be open at once.

### (S) Person --> [Mark Ticket Done In Stage](../../../harness/.context/stories/move-work-forward-on-session-board/guide-work-through-practices-on-board/guide_work_through_practices_on_board_story.test.md#story-mark-ticket-done-in-stage)

Observed: the arrow takes an In progress ticket to Done without crossing a column, written as a `done <stage>` session log line the ticket reads back, and back from Done as `in-progress <stage>`.

### (S) Board App --> [Add Active Ticket To System Prompt](../../../harness/.context/stories/move-work-forward-from-chat-bar/see-work-in-chat-bar/see_work_in_chat_bar_story.test.md#story-add-active-ticket-to-system-prompt)

Inferred: the `prompt.compose` handler in `harness/chat-ui/pane/hooks/register.ts` names the active ticket and its next guidance, and leaves the prompt unchanged with no active ticket. No spec covers it.

### (S) Person --> [Open Help](../../../harness/.context/stories/move-work-forward-on-session-board/guide-work-through-practices-on-board/guide_work_through_practices_on_board_story.test.md#story-open-help)

Observed: `FidelityProgress.help` on a tile's ?, `Board.help` on a practice name; either opens help in a side panel. The Forge link is the page the catalog generator names.

### (S) Person --> [Send Next Fidelity Action](../../../harness/.context/stories/move-work-forward-on-session-board/guide-work-through-practices-on-board/guide_work_through_practices_on_board_story.test.md#story-send-next-fidelity-action)

Observed: on generate, Run next sends `/actions-generate` for the fidelity in its stage's default format; on validate or review it fills the prompt.

## (E) Generate Fidelity Outputs

### (S) Person --> [Choose Action And Formats](../../../harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/generate-fidelity-outputs-on-board/generate_fidelity_outputs_on_board_story.test.md#story-choose-action-and-formats)

Observed: the tile's action bar lists the actions and format chips. A tile opens with the default format's chip picked unless that output exists, a chip stands for a group and each fidelity uses one format from it, and a generated chip is marked. Run stays off with no format, on a render with nothing to render, with no chat connected, and on a locked ticket.

### (S) Claude Code --> [Resolve Fidelity Output Paths](../../../harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/generate-fidelity-outputs-on-board/generate_fidelity_outputs_on_board_story.test.md#story-resolve-fidelity-output-paths)

Observed: `Generate` and `FidelityGuidance.output_paths` take the outputs a fidelity declares, with the `session.json` overrides.

### (S) Person --> [Generate Fidelity Output](../../../harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/generate-fidelity-outputs-on-board/generate_fidelity_outputs_on_board_story.test.md#story-generate-fidelity-output)

Observed: a generate line in the session log counts as Generate done. Run on a tile sends `/actions-generate <fidelities> format=<formats>`. `generate` has no format argument of its own yet, so the format is passed in the command's words.

### (S) Person --> [Render Fidelity Format](../../../harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/generate-fidelity-outputs-on-board/generate_fidelity_outputs_on_board_story.test.md#story-render-fidelity-format)

Observed: Render on a tile sends `/actions-render`.

### (S) Person --> [Send Tile Action To Chat](../../../harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/generate-fidelity-outputs-on-board/generate_fidelity_outputs_on_board_story.test.md#story-send-tile-action-to-chat)

Observed: Run on a tile sends `/actions-sketch`, `/actions-iterate`, or `/actions-document` to the chosen chat.

## (E) Validate Fidelity Outputs

### (S) Person --> [Validate Fidelity](../../../harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/validate-fidelity-outputs-on-board/validate_fidelity_outputs_on_board_story.test.md#story-validate-fidelity)

Observed: a validate line counts as done only when it names no graph-rule violations. Validate on a tile sends `/actions-validate` and the tile marks the result.

### (S) Claude Code --> [Save Validation Report](../../../harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/validate-fidelity-outputs-on-board/validate_fidelity_outputs_on_board_story.test.md#story-save-validation-report)

Observed: `Validate` saves `.sessions/<session>/validation-reports/<practice>-<fidelity>-<date>.md` and the graph it checked under the same name in `.json`.

### (S) Person --> [Open Validation Report](../../../harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/validate-fidelity-outputs-on-board/validate_fidelity_outputs_on_board_story.test.md#story-open-validation-report)

Observed: `FidelityProgress.report` opens the latest report in a side panel from the details or a tile.

### (S) Person --> [Fix Report Violations](../../../harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/validate-fidelity-outputs-on-board/validate_fidelity_outputs_on_board_story.test.md#story-fix-report-violations)

Observed: `FidelityProgress.report` builds the rules from the graph saved beside the report, and a report with no saved graph says so. Fix sends the chat one message with the rule, the error at its file and line, and the content that failed; Fix all sends every violation of the rule in one such message; Fix all violations sends every violation of every rule in the report in one message; and an open report is read again after a cdd tool call.

### (S) Board App --> [Display Violations Band](../../../harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/validate-fidelity-outputs-on-board/validate_fidelity_outputs_on_board_story.test.md#story-display-violations-band)

Observed.

## (E) Review Fidelity Outputs

### (S) Person --> [List Ticket Files](../../../harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-fidelity-outputs-on-board/review_fidelity_outputs_on_board_story.test.md#story-list-ticket-files)

Observed: `FidelityProgress.files`, the files mode of the files panel (`FILE_VIEWS` in `file-views-view.tsx`), for the tile's or ticket's fidelities and no others; pressing a file opens it. On a ticket whose work is in the whole repository, a pattern lists only what its branch changed. A list that cannot be read says so in a toast.

### (S) Person --> [Browse Ticket Folder](../../../harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-fidelity-outputs-on-board/review_fidelity_outputs_on_board_story.test.md#story-browse-ticket-folder)

Observed: the folder mode of the files panel groups the files under their folders.

### (S) Person --> [View Fidelity Files](../../../harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-fidelity-outputs-on-board/review_fidelity_outputs_on_board_story.test.md#story-view-fidelity-files)

Observed: `Session.read_file` and `file-views-view.tsx`; one tab per format the fidelity offers, generated or not, and × closes one.

### (S) Person --> [Review Fidelity](../../../harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-fidelity-outputs-on-board/review_fidelity_outputs_on_board_story.test.md#story-review-fidelity)

Observed: a review line completes a fidelity. Reviewed on a tile is off until a clean validate.

---

## Scope boundary

**In scope:** what a Person does on the CDD Kanban and what the Board App shows them, from the code today and from the canvas at Version 72.

**Out of scope:** animation on the canvas, because it is not repeatable behaviour.
