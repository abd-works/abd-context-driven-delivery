---
fidelity: [discovery]
artifact: [story-map]
format: md
section: body
---

# Story Map — Files App

**Sources / context:** the Files app (`space/session/files_app/`: `files_app.py`, `app/files-server.ts`, `app/files/*.ts(x)`); the chat bar's links to it (`harness/chat-ui/pane/hooks/chat-bar/fidelity-files-client.ts`, `board-chat/board-chat-client.ts`); the session's files and comments (`space/session/session.py`, `file_comments.py`, `practice_session_output.py`); the graph explorer's source view the app reuses (`harness/graph/app/source/SourceView.tsx`); the draw.io viewer (`tools/drawio_viewer/drawio_viewer.py`, `app/drawio-viewer.ts`).

**Inherited from:** this map consolidates every story about viewing a session's files that was spread over three maps, now that the Files app is the one place files are viewed (commit 5aa8569f3 moved the chat bar's files to it and removed the board's `/files` page).

| Was in | Stories taken in |
|---|---|
| `harness/.context/stories/story-map.md`, (E) Review Files In Viewer (board) | View Files In Rich Viewer, Save Edited File, Add Comment To File Selection, Send File Comments To Chat, Mark File Comment Processed, Show Changed File In Viewer, Clear Processed File Comments, Show AI Changes As Diff |
| `harness/.context/stories/story-map.md`, (E) Review Fidelity Outputs On Board | Browse Ticket Files By Practice (its practice filters along the top, preset from the chat bar, coloured by practice) |
| `harness/.context/stories/story-map.md`, (E) Review Fidelity Outputs In Chat Bar, and `harness/chat-ui/.context/story-map.md` | List Session Files, View Session Files / View Fidelity Files |
| `harness/.context/stories/story-map.md`, (E) Review Violations In Graph App, and `harness/graph/.context/story-map.md` | Open Node Source, Unfold Calls And Classes In Source, Open Violation In Source (the source view the Files app reuses), Display Drawio File As Diagram |
| `.../integrate_practice_content_editor_apps_in_chat_bar_story.test.md` | a story's acceptance-test link opening in the chat's file viewer (`open_file`) |

The graph's own stories stay in the graph's map: the graph explorer still shows a node's source there. The board's own files panel (`space/kanban/app/src/kanban/ticket/file-viewer-view.tsx`) still exists beside the Files app; its stories are this map's now.

**Evidence:** **Observed** means the Files app does it today and was walked in the browser pane on 2026-11-14; **Built** means the code and its specs do it but it was not walked; **Intended** means a source asks for it and the Files app does not do it yet.

**Scenarios:** [review_files_in_files_app_story.test.md](review-files-in-files-app/review_files_in_files_app_story.test.md).

---

# (E) Review Files In Files App

## (E) Open Files In Files App

### (S) Person --> [Open Stage Files From Chat Bar](review-files-in-files-app/review_files_in_files_app_story.test.md#story-open-stage-files-from-chat-bar)

Built (2026-11-14): the chat bar's ▤ files button opens the Files app beside the chat on every fidelity of the shown stage, every practice's, so the app's practice toggles filter them (`fidelity-files-client.ts` `openStageFiles`). A folder chip on the session card opens one fidelity's files (`openFiles`). Was the chat bar's List Session Files, which opened a tab per file in the chat bar.

### (S) Person --> [Open Session Folder From Chat Bar](review-files-in-files-app/review_files_in_files_app_story.test.md#story-open-session-folder-from-chat-bar)

Observed (2026-11-14): pressing the session's name opens the Files app on `.sessions/<session>`, listing its log, handoffs, notes and reports (`openSessionFolder`, `session.folder_files`).

### (S) Story UI --> [Open File From Another Page](review-files-in-files-app/review_files_in_files_app_story.test.md#story-open-file-from-another-page)

Built: a page the chat opened, such as the Story UI editor, sends the chat an `open_file`, and the chat opens that file in the Files app on its session folder (`board-chat-client.ts` `shown`, `openFileInViewer`).

### (S) Files App --> [List Files The Link Names](review-files-in-files-app/review_files_in_files_app_story.test.md#story-list-files-the-link-names)

Observed (2026-11-14): the page reads only the files its link names, each once, and never the board (`files-page.ts` `list`); a file not generated yet is listed but cannot be opened. Was View Fidelity Files on the board and the chat bar.

### (S) Person --> [Open Diagram In Draw.io Tab](review-files-in-files-app/review_files_in_files_app_story.test.md#story-open-diagram-in-drawio-tab)

Built (2026-11-14): a press on a `.drawio` file opens the draw.io editor in a new tab, and the Files tab stays on its file list (`files-page.ts` `openDrawio`). Requested (the person, 2026-11-14): "open in new tab works but orig tab also getting moved to drawio; leave it on file explorer". Was the chat bar's Open a diagram in the draw.io editor and the graph's Display Drawio File As Diagram; that story's Source tab and shape marking stay Intended.

### (S) Person --> [Switch File Bar Between Folders And List](review-files-in-files-app/review_files_in_files_app_story.test.md#story-switch-file-bar-between-folders-and-list)

Built (2026-11-14): the file bar collapses to its buttons and expands again, and shows its files as a list or in their folders, the open file's folders open (`file-bar.ts` *FileBar*, `files-page-view.tsx` `FileBarView`). Requested (the person, 2026-11-14): "expand collapse file bar with buttons to swap a folder view and file list".

### (S) Person --> [List Only The Files The Branch Changed](review-files-in-files-app/review_files_in_files_app_story.test.md#story-list-only-the-files-the-branch-changed)

Built (2026-11-15): the file bar's Changed button, with its count, lists only the files the session's branch changed, a published design canvas kept (`file-bar.ts` `toggleChangedOnly`, `entries`). Requested (the person, 2026-11-15): "Yes, add it", to a changed-only filter for a session on the whole repository, where UX's mockup pattern lists about 150 files.

### (S) Person --> Follow Chat Bar Selection In Files App

Built (2026-11-15): the chat bar sends its selected fidelity dots at check-in (`Chat.check_in` `selected_fidelities`, `Chat.show`); the Files app reads them every second and, while any it lists are selected, shows only their files, its practice toggles following the dots (`files-page.ts` `filesShown`, `isShown`). Requested (the person, 2026-11-15): "make sure that the filter in the Files window is inherited from the filter in the chatbar", pointing at the chat bar's fidelity dots.

### (S) Person --> Browse Files Without Reading Rules

Built (2026-11-15): Rules and Cross-file toggles at the top of the Files app, both off by default. With Rules on, `Session.file(rules=True)` reads the open file into the session's live graph when it changed (about 1.5 s) and answers its folds and broken rules, with the last validate's saved findings beside them, as the Graph app's source view shows them; Cross-file has the graph hold the whole working copy first (`Graph.hold_whole`). Requested (the person, 2026-11-15): "I don't see code folding in here I don't see any of the violations", then "toggle at top and have it off by default; for rules; same with cross file that way we don't incur a performance penalty when we just want to browse files".

## (S) Person --> [Toggle Practice In Files App](review-files-in-files-app/review_files_in_files_app_story.test.md#story-toggle-practice-in-files-app)

Built (2026-11-14): the session's practices sit along the top as toggles, each in its practice colour, filled while on and an outline while off; a press turns the practice on or off for the session and the list shows only the files of the practices turned on (`files-page.ts` `togglePractice`, `practice_session_output.enable`). Requested (the person, 2026-11-14): "the patterns should be toggles at the top; be the practice color; and allow us to toggle the practice filter here". Builds on the board's Browse Ticket Files By Practice (2026-11-12): "put the filter toggles on the top".

## (S) Files App --> [Keep Chat Bar Practices In Sync](review-files-in-files-app/review_files_in_files_app_story.test.md#story-keep-chat-bar-practices-in-sync)

Built (2026-11-14): a practice turned on or off in the Files app sends the chat that opened it a `refresh`, and its chat bar reads the board again, so its fidelity dots show the same practices (`chat.send` kind `refresh`, `board-chat-client.ts` `refreshed`); the page reads the practices again every three seconds while it shows (and when the person comes back to it), so a practice turned off on the chat bar or the board hides its files there with no press: a page in a side pane is never focused again (fixed 2026-11-14, the person: "the file filter needs to respect the practice that is toggled"). Requested (the person, 2026-11-14): "also toggles the command bar so they stay in sync".

## (E) View Files In Source View

### (S) Person --> [View File In Source View](review-files-in-files-app/review_files_in_files_app_story.test.md#story-view-file-in-source-view)

Observed (2026-11-14): the open file shows in the graph explorer's Monaco source view, read-only, its lines numbered and coloured by language (`file-source-view.tsx`, `@source-view/SourceView`). Was the board's View Files In Rich Viewer and the graph's Open Node Source. Intended: a markdown file rendered as the page it describes.

### (S) Person --> [Fold Classes And Operations](review-files-in-files-app/review_files_in_files_app_story.test.md#story-fold-classes-and-operations)

Built: the session's graph places each class and operation, and the source view folds each one as a block (`session.file` folds). Was the graph's Unfold Calls And Classes In Source.

### (S) Person --> [Mark Lines A Broken Rule Names](review-files-in-files-app/review_files_in_files_app_story.test.md#story-mark-lines-a-broken-rule-names)

Built: the rules the session's saved graph found broken in the file mark their lines with a rule chip (`session.file` violations). Was the graph's Open Violation In Source.

### (S) Person --> [Save Edited File](review-files-in-files-app/review_files_in_files_app_story.test.md#story-save-edited-file)

Intended: Edit turns the file editable and Save writes it through the file manager (`session.write_file`). The board's panel does it; the Files app is read-only today.

## (E) Review Files With Comments

### (S) Person --> [Add Comment To File Selection](review-files-in-files-app/review_files_in_files_app_story.test.md#story-add-comment-to-file-selection)

Observed (2026-11-14): select lines, right-click, Add comment; Enter adds the comment and sends it, Add keeps it unsent; a marker shows beside the selection's first line (`comment-box-view.tsx`, `file-comments.add`). The menu opened from the keyboard (Shift+F10); a right-click from the browser tool closed it at once, not yet checked by hand.

### (S) Person --> [Open Edit And Delete File Comment](review-files-in-files-app/review_files_in_files_app_story.test.md#story-open-edit-and-delete-file-comment)

Observed (2026-11-14): a press on the marker opens the comment under its lines with its state; Save keeps an edited comment, not sent again; Delete removes it.

### (S) Person --> [Send File Comments To Chat](review-files-in-files-app/review_files_in_files_app_story.test.md#story-send-file-comments-to-chat)

Observed (2026-11-14): a sent comment lands in the prompt box of the chat that opened the page, with its file, lines and session (`file-comments.send`, a fill); Send all open comments sends every comment not yet sent in one message.

### (S) Chat --> [Mark File Comment Processed](review-files-in-files-app/review_files_in_files_app_story.test.md#story-mark-file-comment-processed)

Built: a sent comment is processed once the chat's turn that worked on it has ended; the page reads the open file again every two seconds while a comment on it is sent (`SENT_REFRESH_MILLISECONDS`).

### (S) Files App --> [Show Changed File After Comment](review-files-in-files-app/review_files_in_files_app_story.test.md#story-show-changed-file-after-comment)

Built: when a comment on the open file is processed, the page shows the file as the chat changed it.

### (S) Person --> [Clear Processed File Comments](review-files-in-files-app/review_files_in_files_app_story.test.md#story-clear-processed-file-comments)

Built: Clear processed removes the processed comments and keeps the ones not sent or still sent. Not walked: no comment was processed on 2026-11-14.

### (S) Files App --> [Show AI Changes As Diff](review-files-in-files-app/review_files_in_files_app_story.test.md#story-show-ai-changes-as-diff)

Intended: the page marks what the chat changed in the file, as VS Code and Cursor do (`SessionFile.changes`); the board's panel draws it, the Files app does not yet.
