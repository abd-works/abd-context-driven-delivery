# Review Work In Board Files

Analysis and planning: the stories here are not built yet, or only partly built where a story says so. This is one increment of the thin slice, which sets the order of the increments, [harness/.context/stories/thin-slice.md](../../harness/.context/stories/thin-slice.md); its epics, features and stories are on the story map, [harness/.context/stories/story-map.md](../../harness/.context/stories/story-map.md). Each requirement sits under the story it belongs to.

**Outcome:** a person reads a ticket's context and changed files in a proper viewer, comments on them to the chat, and reads clean reports.

**Slicing notes:** board-enhancements "Files" and the report fixes under "Actions".

## Notes from the backlog

From `board-enhancements.md`, "Files":

> - include ticket context file and folders with list - folder-files; separate section
> - session information -> link to file or folders
> - ityregrate with monaco viewer OR native file rendering
> - easy way to select some trxt in file view and add comment hat gets sent  to chat like in design view
> - change viewer from ai change like vscode / cursor

From `board-enhancements.md`, "Actions":

> - kill weird MD area  a top of violatin report
> - violation report not showing code fences for errors

Both are built: Display Report Without Header Noise and Display Report Errors In Code Fences are in Built Today.

From the person, 2026-11-11, on a screenshot of the board's bottom panel showing "stories-scenarios files" (a grid of chips, one per file, with the chosen file rendered below):

> the bottom panel grid from the board is a perfect v2 file viewer; add tabs on top of file groupings for each stage; dimensions are roots of the knowledge graph eg each practice; click to select, check box to multi select

- The board's files panel (its chip grid of a fidelity's files above the rendered file) is the model for the v2 file viewer.
- Tabs across the top, one per stage (Discovery, Specification, Implementation), each holding that stage's file groupings.
- The groupings' dimensions are the roots of the knowledge graph, such as each practice.
- A click on a file selects it; a check box on each file selects several at once.

From the person, 2026-11-11, on the same chip grid:

> color coding files and higlithginh the ares thast have chnged to make agent revew easy

From the person, 2026-11-12, on the same files panel:

> list a shoterend form/ image of each practice stop to bottom on left side , filters preset when clicking fiels buttin in vhat ui , user can toggle them top has file tabls like now but colored to practice

- Along the top (the person, 2026-11-12: "just put the filter toggles on the top it will waste less space"), a filter for each practice the ticket works on, by a short form or image. Every file is a tab along the top, grouped by practice and colored by practice (the person, 2026-11-12: "these are just filters on left; all files are shown in tabs above grouped by practice colored by practice color"). This replaces grouping by folder.
- Opening the files from the chat bar's Files button presets the practice filters to the practice the chat bar is on, as it works today ("it works like it currently does", 2026-11-12). The person can toggle each one.
- Open files are tabs along the top, as now, each colored by its practice.
- Story: Browse Ticket Files By Practice (was Browse Ticket Folder).

- Colour-code the file chips, so a person sees at a glance which files the agent changed.
- Inside an open file, highlight the areas that changed, so reviewing the agent's work is quick. This joins Show AI Changes As Diff below.

From the person, 2026-11-12:

> I want to use the graph app file viewer for this -make this a common component under tools/files_manager with a typed file shape along with typescript monaco viewer that renders
>
> clicking edit opens in edit mode and can be saved;
>
> do research on the feasibility of somke kind of comments fucntionality like the design canvas; i have seen an comment bar somethines popu in broswer pane; maybe this isthe solutun; we want the comments to be sent to chat same way as design canvas but beinging the selected text that is attached to the comment along with file namke of cours eand any thoer nec contenxt
>
> do iths research first

- Take the graph app's file viewer and make it one shared component under `tools/files_manager`, with a typed file shape and a TypeScript Monaco viewer that renders the file.
- Clicking Edit opens the file in edit mode, and the edit can be saved.
- Research first whether comments can work the way the design canvas's do. The comment bar that sometimes pops up in the browser pane may be the way to do it.
- A comment goes to the chat the same way a design canvas comment does, carrying the selected text it is attached to, the file's name, and any other context the agent needs.
- Research findings: [file-viewer-research.md](file-viewer-research.md).
- The file manager is a workspace concept, so the shared viewer and its typed file shape live in `space/` beside `space/session/file_manager.py`, not in `tools/files_manager` (the person, 2026-11-12). The apps import it straight through a path alias; it is ordinary TypeScript, so no installer step is needed to share it.
- harness, space, and tools are the lower layer together and may import each other; cdd_guidance is built on them (the person, 2026-11-12; recorded in the root, harness and tools `.context/module-context.md`). So the graph app may import the viewer from `space/`.
- Files are resolved from the session's workpath. Where a tool needs a full path, `SessionFiles` returns the absolute path rather than a path named from the project top.

## Epic: Move Work Forward On Session Board

### Feature: Work Fidelity Outputs On Board → Review Fidelity Outputs On Board

#### Story: List Ticket Context Files

*Person*. Intended (`.sessions/_backlog/review-work-in-board-files.md` "include ticket context file and folders with list - folder-files; separate section"): the files panel lists the ticket's own context file and folders in a section of their own.

#### Story: Browse Ticket Files By Practice

*Person*. Requested (2026-11-12): the practice filters sit along the top, each by its short form, to waste less space. Every file is a tab along the top, grouped by practice and colored by practice. Opening the files from the chat bar's Files button presets the filters, which the person toggles.

#### Story: Open Session Files From Details

*Person*. Intended (`.sessions/_backlog/review-work-in-board-files.md` "session information -> link to file or folders"): each file or folder the session information names opens from where it is named. Built today (checked 2026-11-10): the details open the session folder, the stage's files and the latest handoff (`details-view.tsx:37-55`). Missing: the workpath link opens the root chooser rather than the folder.

### Feature: Review Files In Viewer

#### Story: View Files In Rich Viewer

*Person*. Intended (`.sessions/_backlog/review-work-in-board-files.md` "integrate with monaco viewer OR native file rendering"): files open in an editor-grade viewer, or rendered as the file type.

#### Story: Save Edited File

*Person*. Requested (2026-11-12, "clicking edit opens in edit mode and can be saved"): Edit turns the viewer's file editable, and Save writes the text to the file on disk through the file manager.

#### Story: Add Comment To File Selection

*Person*. Intended (`.sessions/_backlog/review-work-in-board-files.md` "select some text in file view and add comment that gets sent to chat like in design view"): a person selects text in a file and sends a comment on it to the chat.

#### Story: Send File Comments To Chat

*Person*. Requested (2026-11-12, "finish editing press enter; added to chat q"): Enter finishes a comment and adds it to the chat queue with the file's path, the selected lines, the selected text and the comment. Send all, at the top left of the viewer, sends every comment not yet sent (2026-11-12).

#### Story: Mark File Comment Processed

*Chat*. Requested (2026-11-12, "chat process comment and changes files ... comment is at processed stage; comment --> not sent, sent, processed"): a sent comment becomes processed once the chat's turn that worked on it has ended.

#### Story: Show Changed File In Viewer

*Board App*. Requested (2026-11-12, "then viewer is updated to reflect changes"): when a comment on the open file is processed, the viewer shows the file's new text.

#### Story: Clear Processed File Comments

*Person*. Requested (2026-11-12, "a clear processed comments button"): clearing removes the processed comments and keeps the rest.

#### Story: Show AI Changes As Diff

*Board App*. Intended (`.sessions/_backlog/review-work-in-board-files.md` "change viewer from ai change like vscode / cursor"): the viewer marks what the agent changed in a file, as VS Code and Cursor do.
