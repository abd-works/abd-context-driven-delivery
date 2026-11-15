## Language

The *Files app* shows the files a link names and turns a person's reading into work for the chat that opened it. It keeps no state of its own on disk: the session owns its practices, its files and their comments, and the page only shows what the session answers and asks it to change. Classes are TypeScript in `app/` unless named otherwise; *Session*, *PracticeSessionOutput*, *FileComments* and *Chat* are the Python owners, reached through their generated clients.

### FilesLink (`files/files-link.ts`)

- What the page's link names: the ticket, the fidelities whose files to list (none for a session folder), the session's `session.json`, the file to open first, and the chat that opened the page.
- **Invariant:** a link names a ticket and its session.json, or the page shows that it names no files.

### FilesPage (`files/files-page.ts`)

- The page: the files its link names, read once and kept by fidelity; the session's practices; the one file open; and what went wrong. Holds its *FilesStore*, its session client, and its *FileCommentsActions*.
- `start()` lists the files and reads the practices; it reads the practices and the selection again every second while the page shows, so a practice turned on or off on the chat bar or the board hides or shows its files here, and whenever the person comes back to the page it reads the open file and the practices again.
  - -> Session.folderFiles, or FidelityProgress.files for each fidelity the link names
  - -> Session.show
- `readPractices()` (private) keeps the session's practices, on and off, each with its colour, short name and fidelities, and lists the files of the practices turned on.
  - -> Session.show
- The page follows the chat bar of the chat that opened it: while fidelities it lists are selected there (the chat bar's dots), it shows only their files and its toggles show their practices, disabled, `isFollowingChatBar`; with none selected, the practices turned on. `isShown(practice)` says which a toggle shows.
  - -> Chat.show (`selected_fidelities`: the one selection cdd holds for the chat; the chat bar's dots write it through `Chat.select` and draw it from `Chat.show` at each check-in)
- `toggleFormat(label)` and `formatChips` (`files/format-chips.ts`): a chip for each group of formats the link's fidelities offer, after the practices, with the chat bar's glyphs and colours (orange while chosen, green when every fidelity has a file in it, grey otherwise). A press chooses the format in the session for every fidelity the page lists, the chat bar's own choice, and sends the chat a refresh so its chips read again; while any is chosen the list shows only the files in the formats chosen. Read again every second with the practices.
  - -> Ticket.format_choices, Ticket.choose_formats, Chat.send("refresh", "formats")
- `togglePractice(name)`: a practice the session works on shows or hides its files by selecting or clearing its dots on the opening chat's chat bar (`Chat.select(selected_fidelities), the one selection cdd holds for the chat`), so the bar and the page follow each other both ways; a practice the session does not work on is turned on for it.
- `fail(failure, context, {isShownOnPage})` shows a failure here and sends it to the opening chat once (`Chat.send("failure", {failure, context})`), which shows it on its chat bar as the bar shows its own; every failure on the page goes through it: a call that fails, a file or list that does not read (already in the problem line, so no toast), the look that this browser will not keep, what stopped the page (`FilesFailureView.componentDidCatch`), and any error or rejected promise nothing caught (window `error` and `unhandledrejection`, listened to while the page runs). A failure met again, on a timer or a return to the page, is not sent again.
  - -> Chat.select(selected_fidelities), the one selection cdd holds for the chat, or PracticeSessionOutput.enable and Chat.send("refresh", "practices")
  - **Invariant:** the practices and the selection shown are the session's and the chat bar's; the page keeps no filter of its own.
- `open(path)` opens a file in the source view. A `.drawio` file is a link instead (`drawioPageOf`): the Files server's draw.io page starts the viewer and sends that new tab on to it, a navigation the browser always allows, where a tab opened from a script can be refused; a viewer that does not start is shown in the tab and told to the chat.
  - -> Session.file
  - **Invariant:** a `.drawio` file opens in a tab of its own, so this tab keeps its file list.
- `toggleRules()` and `toggleCrossFile()` each turn one read of the open file on or off, both off by default so browsing never reads a graph: Rules reads the file on its own and shows its folds and its own broken rules, under a second (`Session.file_alone`); Cross-file shows only the rules the whole working copy finds beyond those, linking files and practices, which takes far longer (`Session.file_in_whole`).
  - -> Session.file(path, rules, cross_file)
- `refreshOpen()` (private) reads the open file again, and again every two seconds while a comment on it is sent.
- `attempt(what, work)` runs a call a person started; its failure is a toast naming what failed, and the open file is read again after it.

### FileBar (`files/file-bar.ts`)

- The page's side bar: collapsed to its buttons or expanded, showing the files the page lists as one list or in their folder tree, as Windows Explorer shows it. Holds no files of its own; reads the page's *FilesStore* and keeps what it shows there (`fileBar`: open, view, open folders).
- `tree` is the folder tree of the listed files (`treeOf`): each folder nested in the folder it is in, folders before files, each sorted by name; a folder holding only one folder and no files shows joined to it as one row (`src/checkout`).
- `toggle()` collapses or expands the bar.
- `show(view)` shows the files as a list or in their folder tree.
  - **Invariant:** shown as folders, every folder down to the open file is open.
- `entries` are the files the bar lists: every listed file, or, changed only (`toggleChangedOnly()`), those the session's branch changed and any design canvas published at a link; `changedCount` counts the changed ones for the Changed button. The list and the tree both show `entries`.
- `toggleFolder(path)` opens or closes one folder; `isOpen(folder)` says which it is.

### FidelityFiles (`files/files-state.ts`)

- One fidelity's files as the link names them, kept apart so a practice turned off hides its own. A session folder is one *FidelityFiles* of no fidelity.
- The files of a fidelity are the ones a person reviews for it (`FidelityProgress.files`): UX's front-end code lists its IA's and mockup's files, not its view code, which Clean Engineering's code lists with every other code file the branch changed. A design canvas's `canvas.json` comes with the link its version is published at, and the file bar shows it as a link that opens the canvas in Claude Design.
- `filesShown(byFidelity, practices)` is every file of the fidelities whose practice is on, each once; a fidelity no practice owns is shown.
  - -> PracticeSessionOutput.fidelity_slugs

### FilesStore (`files/files-state.ts`)

- The one place the page's state is held and changed: practices, files by fidelity, the files shown, the open path and its file, the problem, the toasts, and what the file bar shows. A view subscribes and reads it whole.

### FileCommentsActions (`files/file-comments-actions.ts`)

- The comment operations a person presses on the open file: add, add and send, edit, edit and send, send, send all open, remove, clear processed, each through `FilesPage.attempt`.
  - -> FileComments.add, edit, send, send_open, remove, clear_processed

### FilesPageView, PracticeTogglesView, CommentToolbarView (`files/files-page-view.tsx`)

- The page drawn, in the dark engineering look unless the person turned on the light one with the header's ☀ (`files/files-theme.ts`, kept in this browser): the header with the ticket and one toggle per practice, filled in its colour while on and an outline while off; the file list; the open file with Send all open comments and Clear processed above it; the toasts.

### Session, PracticeSessionOutput (Python, `space/session`)

- `Session.show()` answers the session as it stands, changing nothing; its `practices` are every practice, on or off.
- *PracticeSessionOutput* sends `short_name`, `colour` and `fidelity_slugs` from the practice's guidance beside `enabled`; `enable(is_enabled)` saves the change in session.json.

### Chat (Python, `harness/chat`)

- `send("refresh", text)` queues a refresh; the chat's chat bar takes it at its next check-in and reads the board again, with no toast (`board-chat-client.ts` `refreshed`).
