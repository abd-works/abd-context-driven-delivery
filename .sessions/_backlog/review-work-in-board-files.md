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

## Epic: Move Work Forward On Session Board

### Feature: Work Fidelity Outputs On Board → Review Fidelity Outputs On Board

#### Story: List Ticket Context Files

*Person*. Intended (`.sessions/_backlog/review-work-in-board-files.md` "include ticket context file and folders with list - folder-files; separate section"): the files panel lists the ticket's own context file and folders in a section of their own.

#### Story: Open Session Files From Details

*Person*. Intended (`.sessions/_backlog/review-work-in-board-files.md` "session information -> link to file or folders"): each file or folder the session information names opens from where it is named. Built today (checked 2026-11-10): the details open the session folder, the stage's files and the latest handoff (`details-view.tsx:37-55`). Missing: the workpath link opens the root chooser rather than the folder.

#### Story: View Files In Rich Viewer

*Person*. Intended (`.sessions/_backlog/review-work-in-board-files.md` "integrate with monaco viewer OR native file rendering"): files open in an editor-grade viewer, or rendered as the file type.

#### Story: Comment On File Selection

*Person*. Intended (`.sessions/_backlog/review-work-in-board-files.md` "select some text in file view and add comment that gets sent to chat like in design view"): a person selects text in a file and sends a comment on it to the chat.

#### Story: Show AI Changes As Diff

*Board App*. Intended (`.sessions/_backlog/review-work-in-board-files.md` "change viewer from ai change like vscode / cursor"): the viewer marks what the agent changed in a file, as VS Code and Cursor do.
