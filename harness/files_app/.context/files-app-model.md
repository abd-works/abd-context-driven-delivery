## Language

The *Files app* shows the files a link names and turns a person's reading into work for the chat that opened it. It keeps no state of its own on disk: the session owns its practices, its files and their comments, and the page only shows what the session answers and asks it to change. Classes are TypeScript in `app/` unless named otherwise; *Session*, *PracticeSessionOutput*, *FileComments* and *Chat* are the Python owners, reached through their generated clients.

### FilesLink (`files/files-link.ts`)

- What the page's link names: the ticket, the fidelities whose files to list (none for a session folder), the session's `session.json`, the file to open first, and the chat that opened the page.
- **Invariant:** a link names a ticket and its session.json, or the page shows that it names no files.

### FilesPage (`files/files-page.ts`)

- The page: the files its link names, read once and kept by fidelity; the session's practices; the one file open; and what went wrong. Holds its *FilesStore*, its session client, and the parts that each do one job on it: *FileBar*, *GuidanceSelector* (`guidance`), *FileCommentsActions* (`comments`), *FileMenu* (`menu`, with its *FileBrowser*), *ChatContext* (`chatContext`), and *FilesNotices* (`notices`). Its own operations are reading and showing the files: `start`, `showScope`, `toggleRules`, `toggleCrossFile`, `open`, and `attempt`.
- `start()` lists the files and reads the practices; it reads the practices and the selection again every second while the page shows, so a practice turned on or off on the chat bar or the board hides or shows its files here, and whenever the person comes back to the page it reads the open file and the practices again.
  - -> Session.folderFiles, or FidelityProgress.files for each fidelity the link names
  - -> Session.show
- `readPractices()` (private) keeps the session's practices, on and off, each with its colour, short name and fidelities, and lists the files of the practices turned on.
  - -> Session.show
- The page follows the chat bar of the chat that opened it: while fidelities it lists are selected there (the chat bar's dots), it shows only their files and its toggles show their practices, disabled, `isFollowingChatBar`; with none selected, the practices turned on. `isShown(practice)` says which a toggle shows.
  - -> Chat.show (`selected_fidelities`: the one selection cdd holds for the chat; the chat bar's dots write it through `Chat.select` and draw it from `Chat.show` at each check-in)
- `guidance` (*GuidanceSelector*, `files/guidance-selector.ts`) follows the session's guidance selection, the stages, practices, and format groups selected, which the chat bar's stage buttons, practice dots, and format chips show too. One waiting read (`Session.guidance_selection_after(version)`) answers as soon as a change anywhere raises the version. The page's stage, practice, and format buttons call it directly (`toggleStage`, `togglePractice`, `toggleFormat`). A press draws at once, then sends one `Session.update_guidance_selection`; an answer older than the version drawn is ignored, so a late read never undoes a press. The page lists the files of the selection's fidelities (before any stage is chosen, the link's), reading a stage's files the first time it shows, and only those in the format groups selected while any is.
  - -> Session.guidance_selection, Session.guidance_selection_after, Session.update_guidance_selection
- `showScope(scope)`: All session files (▤) lists every file under the session's root, read once as the page opens (`Ticket.root_files`), with the files the fidelities listed declare but have not generated yet; This session (Δ with its count), the default, lists those the session's branch changed against main and any design canvas published at a link. The stages, practices and formats selected narrow both: a file shows in a format selected while any is, and when it belongs to a fidelity listed; a file of no fidelity shows only while no practice is selected (`rootFilesShown`). The two buttons sit first along the top, before the stages, orange while selected. Nothing is read again.
  - -> Ticket.root_files (each file's format and the fidelities it belongs to come from Python)
- `toggleRules()` and `toggleCrossFile()` each turn one read of the open file on or off, both off by default so browsing never reads a graph: Rules reads the file on its own and shows its folds and its own broken rules, under a second (`Session.file_alone`); Cross-file shows only the rules the whole working copy finds beyond those, linking files and practices, which takes far longer (`Session.file_in_whole`).
  - -> Session.file(path, rules, cross_file)
- `refreshOpen()` (private) reads the open file again, and again every two seconds while a comment on it is sent.
- `attempt(what, work)` runs a call a person started; its failure is a toast naming what failed, and the open file is read again after it.

### FileBar (`files/file-bar.ts`)

- The page's side bar: collapsed to its buttons or expanded, showing the files the page lists as one list or in their folder tree, as Windows Explorer shows it. Holds no files of its own; reads the page's *FilesStore* and keeps what it shows there (`fileBar`: open, view, folders closed). It shows folders by default, and every folder starts open: the bar keeps the folders a person closed, so a folder a filter change brings is open and one closed stays closed.
- `tree` is the folder tree of the listed files (`treeOf`): each folder nested in the folder it is in, folders before files, each sorted by name; a folder holding only one folder and no files shows joined to it as one row (`src/checkout`).
- `toggle()` collapses or expands the bar.
- `show(view)` shows the files as a list or in their folder tree.
  - **Invariant:** shown as folders, every folder down to the open file is open.
- `entries` are the files the bar lists: under This session, those the session's branch changed and any design canvas published at a link; under All session files, every listed file. `changedCount` counts the changed ones for the This session button. The list and the tree both show `entries`.
- `toggleFolder(path)` opens or closes one folder; `isOpen(folder)` says which it is.

### FileMenu (`files/file-menu.ts`)

- The menu a right-click on a file or folder shows where the person clicked; it keeps what it is on in the page's *FilesStore* (`menu`). `open(path, left, top)` shows it and `close()` hides it.
- `addToContext()` adds the file it is on, whole, to the chat's context through *ChatContext*.
- `reveal()` shows the file or folder in the system's file browser through *FileBrowser*.

### FileBrowser (`files/file-browser.ts`)

- The system's file browser on this machine: Explorer, Finder, or the desktop's file manager. `reveal(path)` has the Files server start it on the file or folder (`/reveal`, `app/file-explorer.ts`); a browser that does not open is a failure told to the chat.

### ChatContext (`files/chat-context.ts`)

- The context of the chat that opened the page. `add(path, lines?)` has the session put a file, or lines of it, in that chat's prompt box, to go with the person's next prompt; the source view's Add to context calls it for the selected lines.
  - -> Session.add_to_chat_context

### FilesNotices (`files/files-notices.ts`)

- What the page tells the person. `toast(text)` shows a toast once while it shows; `fail(failure, context)` shows a failure and sends it to the chat that opened the page, once, so its chat bar shows it too.
  - -> Chat.send("failure")

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

- `send("refresh", text)` queues a refresh; the chat's chat bar takes it at its next check-in and reads the board again, with no toast (`check-in-client.ts` `refreshed`).
