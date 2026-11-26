---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Epic: Review Files In Files App

Map: [story-map.md](../../../.context/story-map.md#e-review-generated-work-in-file-viewer). Acceptance tests: `story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review-files-in-files-app.story.shared.py`, replayed by `.story.domain.spec.py` and `.story.server.spec.py` beside it, for what the session answers; `harness/files_app/app/files/*.spec.ts` for what only the page shows; `review-files-in-files-app.story.ui_e2e_spec.py` beside it runs the examples named ++another project++ in a real browser.

Consolidated on 2026-11-14 from the board's Review Files In Viewer scenarios (this file, moved from `story_tests/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-files-in-viewer/`), the chat bar's View Fidelity Files scenarios (`story_tests/move-work-forward-from-chat-bar/guide-work-through-practices/guide_work_through_practices_story.test.md`), the Story UI's acceptance-test link (`.../integrate_practice_content_editor_apps_in_chat_bar_story.test.md`), and the graph's source view stories (`harness/graph/.context/story-map.md`, Open Node Source, Unfold Calls And Classes In Source, Open Violation In Source). Scenario names kept from those sources are unchanged, so the shared steps still find them.

### Domain terms

- [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card): one session on the board.
- [session](../../../space/kanban/.context/kanban-model.md#session): the work behind a ticket. It works in its workpath, and its files are named from there. The Files app reaches no file outside the session's roots.
- [chat](../../../space/kanban/.context/kanban-model.md#chat): a Claude Code chat whose cdd-board mod checks in. Its queue holds the messages sent to it. A message is done once the chat's turn that worked on it has ended.
- [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets): the file viewer as an app of its own, on its own server and port, opened beside the chat by a link that names the files to show and the chat that opened it (`harness/files_app/files_app.py`). It never reads the board.
- [practice](../../../harness/files_app/.context/files-app-model.md#session-practicesessionoutput-python-spacesession): a lens the session works through (Stories, DDD, UX, Clean Engineering, BDD), on or off for the session, with its own colour (`practice_session_output.py`).
- file manager: the session's reader and writer of the files under its roots (`space/session/files/file_manager.py`).
- [file comment](../../../harness/files_app/.context/files-app-model.md#filecommentsactions-filesfile-comments-actionsts): a comment a person writes on lines of a file, kept in the session's folder. It is not sent, then sent, then processed.

### Evidence

| Source | Note |
|--------|------|
| `.sessions/review-work-in-board-files/review-work-in-board-files.md`, request of 2026-11-12 | A shared Monaco viewer typed on the file manager's file shape. Edit and Save. Comments go to the chat with the selected text and the file's name. |
| `.sessions/review-work-in-board-files/file-viewer-research.md`, "Recommendation" | Comments go through the chat queue, `chat.send`. A comment is anchored as `path:Lstart-Lend`. Send all sends every open comment at once. |
| The person, 2026-11-12 | "chat process comment and changes files then viewer is updated to reflect changes and comment is at processed stage; comment --> not sent, sent, processed; a send all open comment button top left of viewer and a clear processed comments button" |
| `.context/story-map.md`, Browse Ticket Files By Practice, 2026-11-12 | "put the filter toggles on the top"; filters preset when opening the files from the chat bar; the person can toggle them; coloured by practice. |
| The person, 2026-11-14 | "the patterns should be toggles at the top; be the practice color; and allow us to toggle the practice filter here (also toggles the command bar so they stay in sync)"; the toggles are practices. |
| The person, 2026-11-14 | "clicking on drawio --> open in new tab works but orig tab also getting moved to drawio; leave it on file explorer" |
| Walk of the Files app in the browser pane, 2026-11-14 | Observed: a file opens in the source view; Add comment, its marker, edit, delete and Send all work; a sent comment lands in the chat's prompt box; a `.drawio` file opens in the draw.io viewer. |
| `harness/chat/chat.py` `send`, `check_in` | `send(kind, text)` queues a command; a chat that has not checked in raises `ChatNotConnectedError`; a shown message moves to done when the chat's turn that worked on it ends. |
| The person, 2026-11-17, fixed in 331cdab19 | The Files app opened on *pml-web* showed *src/.context/domain-model.drawio* as a blank *Page-1*: the one draw.io viewer on 8791 had been started from `~/.cdd/runtime`, and was sent the file's path from *pml-web*'s root, which it looked for under its own. |

In every scenario, the [session](../../../space/kanban/.context/kanban-model.md#session) of [ticket](../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow works in *src/checkout*, in its Discovery stage, with Stories on and DDD off. Its *order.py* reads, at lines 12 to 14:

```
12 |     def place(self, cart: Cart) -> Order:
13 |         if not cart.items:
14 |             raise EmptyCartError(cart.id)
```

### Example: another project

A chat working in a repository other than the CDD checkout opens the Files app on that repository, while the Files app's server was started for the CDD checkout, and the one draw.io viewer every project shares runs from whichever project started it. A scenario's example named ++another project++ runs it that way, and everything the page shows must come from the project its link names.

| example | the Files app's server started for | the draw.io viewer started from | the page opened on |
| --- | --- | --- | --- |
| ++another project++ | the CDD checkout | a folder of its own, holding no diagram | a project other than the CDD checkout, whose checkout-flow session holds *space/kanban/ticket.py* (the class Ticket, its close and delete) and whose design-review session, working in *design*, holds *design/.context/story-map.drawio*, one page named *Checkout Story Map* with one cell, *Place Order* |

---

## Sub-epic: Open Files In Files App

## Story: Open Stage Files From Chat Bar

#### Scenario: Open the files beside the chat, never in it

*Given* checkout-flow's Discovery stage holds the fidelities stories-story-map and ddd-bounded-context
*And* checkout-flow is assigned the chat *checkout-chat*
*When* the Person opens the stage's files from *checkout-chat*'s chat bar
*Then* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) opens beside the chat, naming checkout-flow and *checkout-chat*
*And* its link names both fidelities, stories-story-map and ddd-bounded-context, the [practice](../../../harness/files_app/.context/files-app-model.md#session-practicesessionoutput-python-spacesession) turned off among them
*And* the chat bar draws no file, and no diagram is read into the chat
*And* the Person can Toggle Practice In Files App there

## Story: Open Session Folder From Chat Bar

#### Scenario: List the session's own folder

*Given* checkout-flow's session folder *.sessions/checkout-flow* holds *session.log* and a handoff
*When* the Person opens the session's folder from *checkout-chat*'s chat bar
*Then* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) opens on *.sessions/checkout-flow*, listing *session.log* and the handoff

#### Scenario: Leave out what a change to session.json leaves beside it

Requested 2026-11-22. Observed (`space/session/files/session_files_spec.py`). The list is built by `SessionFiles.in_folder`, which asks the session's record which files a change leaves beside it (`SessionRecord.is_left_beside`).

*Given* a change to checkout-flow's *session.json* left its lock file *session.json.lock* in *.sessions/checkout-flow*
*And* a killed writer left its staged text *session.json.4242.1.tmp* there
*When* the Person opens the session's folder from *checkout-chat*'s chat bar
*Then* the Files app lists *session.json* and *session.log*
*But* neither *session.json.lock* nor *session.json.4242.1.tmp* is listed
*And* a person's own file *notes.lock* in the folder is listed

#### Scenario: Leave out what a change to session.json leaves beside it from the folder tree

Requested 2026-11-22. Observed (`space/session/files/file_manager_spec.py`). The folder tree is listed by `file-manager.list`, which asks the same `SessionRecord.is_left_beside`, so the folder's file list and its tree leave out the same files.

*Given* checkout-flow's practice root holds its session folder *.sessions/checkout-flow*
*And* a change to *session.json* left its lock file *session.json.lock* there
*And* a killed writer left its staged text *session.json.4242.1.tmp* there
*When* the Person opens *.sessions/checkout-flow* in the Files app's folder tree
*Then* the tree lists *session.json*
*But* neither *session.json.lock* nor *session.json.4242.1.tmp* is listed
*And* a person's own file *notes.lock* in the folder is listed

## Story: Open File From Another Page

#### Scenario: Open the file a page sent the chat

*Given* the Story UI editor was opened from *checkout-chat* on checkout-flow's story map
*And* the story *Open Story UI* has its acceptance test at *move-work-forward-from-chat-bar/open_story_ui_story.test.py*
*When* the Person opens the acceptance-test link of *Open Story UI* there
*Then* *checkout-chat* gets an open_file naming *move-work-forward-from-chat-bar/open_story_ui_story.test.py*
*And* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) opens on checkout-flow's session folder with *open_story_ui_story.test.py* open
*But* the Story UI editor opens no file of its own

## Story: List Files The Link Names

#### Scenario: List each file once, without reading the board

*Given* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets)'s link names stories-story-map, whose files are *story-map.md* and *story-map.drawio*
*When* the Files app opens
*Then* it lists *story-map.md* and *story-map.drawio*, each once
*And* opens *story-map.md*, the first file that is not a diagram
*But* it reads nothing from the board

#### Scenario: List a file not generated yet, which cannot be opened

*Given* stories-story-map declares *story-map.md*, which is not on disk yet
*When* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) opens
*Then* it lists *story-map.md* as not generated yet
*And* the Person cannot open it

#### Scenario: List a file whose name holds letters outside ASCII

Found on 2026-11-19 (exploratory testing, pixel-02): git writes such a name in quotes with octal escapes unless asked for NUL-ended entries, so the file was dropped from the list and from the branch's changed files, with no word that a file was left out. Acceptance tests: `harness/git/git_spec.py` for the reading of git's listing; `space/session/files/session_files_heavy_spec.py` and `space/repo/repo_heavy_spec.py` on a real git repository.

*Given* checkout-flow's branch committed *src/ünïcödé_日本.py* in a git project
*When* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) lists every file under the session's root
*Then* it lists *src/ünïcödé_日本.py* by the name it has on disk
*And* the files the session's branch changed name it the same way

#### Scenario: Say so when the project folder the link names is not there

Found on 2026-11-19 (exploratory testing, pixel-04): the page said the cdd server was not connected because `python.exe` was not found, which sent the person to repair a Python and a cdd server that were both fine. Acceptance tests: `harness/files_app/app/files-server.spec.ts` for the Files server and `harness/files_app/app/files/cdd-connection.spec.ts` for every other page's connection; `open-files-in-files-app.story.ui_e2e_spec.py` for the page.

*Given* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets)'s link names a project folder that is not there, such as a ticket's worktree removed while its Files tab stayed open
*When* the Files app opens
*Then* it says the files did not list because that project folder is not there, naming the folder
*But* the page holds no word of Python or of the cdd server

## Story: Open Diagram In Files App

Requested (the person, 2026-11-15): the app's browser pane opens no tab of its own from a page, so a diagram opened in a new tab took the Files app's place there. It opens beside the file list instead.

#### Scenario: Open a diagram beside the file list

*Given* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) lists *story-map.drawio*
*When* the Person opens *story-map.drawio*
*Then* the draw.io editor shows *story-map.drawio* in the Files app's file view
*And* the file list still shows beside it
*And* a ↗ link beside it opens *story-map.drawio* in the draw.io editor in a tab of its own, where the browser opens one
*And* nothing is sent to the chat

##### Example: another project

*Given* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) is opened on ++another project++ and lists design-review's *story-map.drawio*
*And* the draw.io viewer is already running from a folder of its own, which holds no *story-map.drawio*
*When* the Person opens *story-map.drawio*
*Then* the draw.io editor shows the cell *Place Order*, from the project the Files app is opened on
*And* its page is named *Checkout Story Map*, not a blank *Page-1*

#### Scenario: Say so when the draw.io viewer does not start

Required by the cdd_web_domain_access rule `fail-loud-on-mcp` this session overlays: when a call fails, the page shows the person what failed instead of an empty view.

*Given* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) lists *story-map.drawio*
*But* the draw.io viewer does not start
*When* the Person opens *story-map.drawio*
*Then* the file view says *story-map.drawio did not open in the draw.io viewer*, with the reason
*And* the chat that opened the Files app is told the same

## Story: Open File In File Browser

Requested (the person, 2026-11-15): "add right click to file and folder -> open in explorer (windows) or whatever mac is based on os".

#### Scenario: Show a file in the system's file browser

*Given* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) lists *story-map.md*
*When* the Person right-clicks *story-map.md*
*Then* a menu shows where the Person clicked, its one choice named for the system: *Open in Explorer* on Windows, *Reveal in Finder* on a Mac, *Open in file manager* elsewhere
*When* the Person chooses it
*Then* the system's file browser opens with *story-map.md* selected, or on its folder where the browser cannot select a file
*And* the menu closes

#### Scenario: Open a folder in the system's file browser

*Given* the Files app shows its files in their folders
*When* the Person right-clicks the *.context* folder and chooses to open it
*Then* the system's file browser opens on *.context*

#### Scenario: Say so when the file browser does not open

Required by the cdd_web_domain_access rule `fail-loud-on-mcp` this session overlays.

*Given* the system's file browser does not start
*When* the Person chooses to open *story-map.md* in it
*Then* the chat that opened the Files app is told *story-map.md did not open in the file browser*, with the reason

## Story: Switch File Bar Between Folders And List

Requested (the person, 2026-11-14): "expand collapse file bar with buttons to swap a folder view and file list". Only the page shows it: the session answers the same files either way.

#### Scenario: Collapse the file bar to give the open file the page

*Given* the [Files app](../../../harness/files_app/.context/files-app-model.md#filebar-filesfile-barts) lists *story-map.md* and *src/checkout/order.py*, with *order.py* open
*When* the Person collapses the file bar
*Then* the file bar shows only its buttons, and *order.py* takes the page's width
*When* the Person expands the file bar
*Then* the file bar lists *story-map.md* and *order.py* again

#### Scenario: Show the files in their folders, the open file's folder open

*Given* the [Files app](../../../harness/files_app/.context/files-app-model.md#filebar-filesfile-barts) lists *.context/story-map.md*, *src/checkout/order.py* and *src/checkout/cart.py*, with *order.py* open
*When* the Person shows the file bar as folders
*Then* the file bar shows the folders *.context* and *src/checkout*
*And* *src/checkout* is open, showing *cart.py* and *order.py*
*And* *.context* is open too, as every folder starts open
*When* the Person shows the file bar as a list
*Then* the file bar lists *story-map.md*, *order.py* and *cart.py* again, in the order the link names them

#### Scenario: Close and open a folder

Requested (the person, 2026-11-15): "keep folder the default view and not reset it every time we change a filter".

*Given* the [Files app](../../../harness/files_app/.context/files-app-model.md#filebar-filesfile-barts) shows its files as folders, its default, *.context* open
*When* the Person closes *.context*
*Then* *.context* shows no file
*When* a filter changes the files listed
*Then* *.context* stays closed
*When* the Person opens *.context*
*Then* *.context* shows *story-map.md*

## Sub-epic: Filter Files In Files App

## Story: Resize File Bar

Requested (the person, 2026-11-15): "can allow drag resize for folder pane in file viewer". Only the page shows it, so it has no step in the Python story tiers.

#### Scenario: Drag the file bar wider

*Given* the Files app shows its file bar at its usual width, 288 pixels
*When* the Person drags the line between the file bar and the open file to 420 pixels
*Then* the file bar is 420 pixels wide
*And* the next Files page this browser opens shows it 420 pixels wide

#### Scenario: Stop at the narrowest and widest widths

*Given* the Files app shows its file bar
*When* the Person drags the line to 20 pixels, then to 5000
*Then* the file bar stops at 160 pixels, then at 900

## Story: List This Session Or All Session Files

Requested (the person, 2026-11-15): two buttons. All session files lists every file under the session's root; This session lists the files the session's branch changed against main. The stages, practices and formats selected narrow both: a file shows in a format selected, and when it belongs to a fidelity of a stage and practice selected, or to no fidelity at all. So a person can list, for example, every drawio file, or only this session's markdown and code. The session answers each file with its format and the fidelities it belongs to; the page filters.

#### Scenario: List all session files, then this session's

*Given* the [Files app](../../../harness/files_app/.context/files-app-model.md#filebar-filesfile-barts) has Discovery selected, and the session's root holds *.context/stories-story-map.md* of the story map, *specs/checkout.md* of Specification's scenarios, and *notes/plain.txt* and *src/order.py* of no fidelity, the branch having changed only *order.py*
*When* the Person lists All session files
*Then* the file bar lists *stories-story-map.md*, *plain.txt* and *order.py*
*And* leaves out *checkout.md*, whose stage is not selected
*When* the Person lists This session
*Then* the file bar lists *order.py* alone

#### Scenario: List the files again on each press

Found on 2026-11-19 (exploratory testing, pixel-01): the files were listed once as the page opened, so a file renamed on disk kept its old name in the list until the page was loaded again. Acceptance tests: `harness/files_app/app/files/files-page.spec.ts`; `open-files-in-files-app.story.ui_e2e_spec.py` for the page.

*Given* the file bar lists *src/order.py*, and *order.py* was renamed *basket.py* on disk since the page opened
*When* the Person lists All session files again
*Then* the file bar lists *src/basket.py*
*And* lists *src/order.py* no longer as a file to open

##### Example: another project

*Given* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) is opened on ++another project++, its link naming design-review's stories-story-map
*When* the Person lists All session files
*Then* the file bar lists that project's *story-map.drawio* and *story-map.whiteboard* as the story map files on disk, not a file of the CDD checkout, since a diagram is drawn in draw.io and on a whiteboard
*And* marks the story map files it does not hold, such as *thin-slice.whiteboard*, as not generated yet

#### Scenario: List this session's own files in a folder with no git

Reported (Nov 18 demo, 2026-11-18): in a plain folder This session listed nothing, since with no branch no file is ever changed; and the Files app opened without the sketch just written, since no fidelity declares it. The sketch holds a section for each practice, so it is every fidelity's.

*Given* the [Files app](../../../harness/files_app/.context/files-app-model.md#filebar-filesfile-barts) is opened on a project in a plain folder, with no git repository, whose session's root holds its story map *.context/story-map.md*, the session's sketch *.context/{session}-sketch.md*, and *notes/plain.txt* of no fidelity
*When* the Person lists This session
*Then* the file bar lists *story-map.md*, the file the session's story map fidelity declares, and the session's sketch
*And* leaves out *plain.txt*

##### Example: a plain folder

*Given* the Files app is opened on ++a plain folder++, its link naming plain-work's stories-story-map
*When* the Person lists This session
*Then* the file bar lists *.context/plain-work-sketch.md* and *.context/story-map.md*

#### Scenario: List all session files in the formats selected

*Given* the Files app has Discovery and the markdown format selected
*When* the Person lists All session files
*Then* the file bar lists only the Discovery markdown files

#### Scenario: Keep a published design canvas

*Given* the Files app lists a design canvas published at its link, unchanged, and *cart.py*, unchanged
*When* the Person lists This session
*Then* the file bar lists the design canvas alone, which opens at its link

## Story: Toggle Practice In Files App

#### Scenario: Show each practice as a toggle in its colour

*Given* checkout-flow works on Stories and has DDD turned off
*When* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) opens
*Then* the top of the page shows a Stories toggle filled in Stories' colour, *#6BCB77*
*And* a DDD toggle drawn as an outline in DDD's colour, *#6C5CE7*

#### Scenario: List only the files of the practices turned on

*Given* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets)'s link names stories-story-map and ddd-bounded-context
*But* checkout-flow has DDD turned off
*When* the Files app opens
*Then* it lists *story-map.md*
*But* not *bounded-context-map.md*

#### Scenario: Turn a practice on to show its files

*Given* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) shows the DDD toggle as an outline
*When* the Person turns DDD on
*Then* checkout-flow's session works on DDD, saved in its session.json
*And* the DDD toggle fills in DDD's colour
*And* the Files app lists *bounded-context-map.md* beside *story-map.md*
*And* the Files app can Keep Chat Bar Practices In Sync

#### Scenario: Turn a practice off to hide its files

*Given* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) shows the Stories toggle filled
*When* the Person turns Stories off
*Then* checkout-flow's session no longer works on Stories
*And* the Stories toggle shows as an outline
*And* the Files app no longer lists *story-map.md*

#### Scenario: Turn a practice off before any stage is selected

Round 3 of exploratory testing (r3-lens-05): with no stage selected yet the page listed every fidelity its link names, whatever practices were on, so a practice turned off kept its files in the list and its tree in the graph view. The page: `harness/files_app/app/files/files-page.spec.ts`.

*Given* the Files app's link names stories-story-map and ddd-bounded-context, and no stage was selected for checkout-flow yet
*When* the Person turns DDD off
*Then* the Files app lists *story-map.md*
  *But* no longer *bounded-context-map.md*

## Story: Keep Chat Bar Practices In Sync

#### Scenario: Show a practice turned on in the Files app on the chat bar

*Given* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) was opened from *checkout-chat*, which has checked in
*When* the Person turns DDD on in the Files app
*Then* *checkout-chat*'s chat bar, waiting on [session.guidance_selection_after](../../../space/session/session.py), shows ddd-bounded-context's dot
*And* no refresh message is sent to *checkout-chat*

#### Scenario: Show a practice turned off on the chat bar in the Files app

*Given* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) shows the DDD toggle filled
*When* the Person turns DDD off on the chat bar
*Then* within a second, with no press in the Files app, the DDD toggle shows as an outline
*And* the Files app no longer lists *bounded-context-map.md*

---

## Sub-epic: View Files In Source View

## Story: View File In Source View

#### Scenario: Show a code file in the viewer with its lines numbered

*Given* checkout-flow's session holds *order.py*
*When* the Person views *order.py*
*Then* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) shows *order.py* in the source view as Python, with line 12 reading *def place(self, cart: Cart) -> Order:*
*And* the source view is read-only
*And* the Person can Add Comment To File Selection from there

##### Example: another project

*Given* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) is opened on ++another project++, whose checkout-flow session holds *space/kanban/ticket.py*, as the CDD checkout also does
*When* the Person views *ticket.py*
*Then* the source view shows that project's *ticket.py*, its first line reading *class Ticket:*, not the CDD checkout's

#### Scenario: Switch a rendered file to its source and back

*Given* the Files app shows *README.md* rendered
*When* the Person presses Source
*Then* the source view shows *README.md*'s text, its first line reading *# Checkout*, with Wrap lines beside the toggle
*When* the Person presses Rendered
*Then* the Files app shows *Checkout* as a heading again

#### Scenario: Open a rendered file as source at the lines asked for

The lines of a node selected in the graph view, its comments and its broken rules are marked on the source view's lines, which a rendered page has none of.

*Given* the Person selects, in the graph view, a story of *.context/story-map.md*
*When* the Files app opens *story-map.md* at that story's lines
*Then* it opens in the source view with those lines shown, and Rendered a press away

#### Scenario: Show only the source view for a file with no rendered form

*Given* checkout-flow's session holds *order.py*
*When* the Person views *order.py*
*Then* the Files app shows it in the source view, with no Rendered or Source toggle

#### Scenario: A file from an older server lane opens without callouts

Found on 2026-11-16 (debug report `debug-20261116T225500.md`): a page reaching a cdd server lane older than the page (the pinned stable lane, whose `session.file` answers no callouts) stopped with "Cannot read properties of undefined (reading 'map')".

*Given* checkout-flow's session holds *order.py*, and the cdd server the page reaches answers *order.py* with its text but without callouts, steps or violations
*When* the Person views *order.py*
*Then* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) shows *order.py* in the source view, with no callout and no broken rule
*And* a server answer that is no file at all, such as the text of a call it cannot run, is shown and told as *order.py* not opening, and the page keeps working

#### Scenario: Say so when a listed file is gone

Found on 2026-11-19 (exploratory testing, pixel-01): a file deleted or moved on disk after the page listed it opened as one empty line in a live editor, exactly as an empty file opens, so the next save would bring it back empty. Acceptance tests: `space/session/session_graph_spec.py` and `space/session/files/file_manager_spec.py` for what the session answers; `open-files-in-files-app.story.ui_e2e_spec.py` for the page.

*Given* the file bar lists *src/order.py*, and *order.py* was deleted on disk since the page listed it
*When* the Person views *order.py*
*Then* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) says *src/order.py* did not open because nothing is at that path, naming the path and the project it was read from
*And* shows no editor for it, so nothing can be saved over it

#### Scenario: Refuse a file longer than the viewer shows

Found on 2026-11-19 (exploratory testing, pixel-03): the source view is as tall as its file and draws every line, so a file of 90,000 lines left the page answering after twelve seconds and one of 360,000 crashed its tab, with every open file and comment not yet sent. The viewer shows at most 30,000 lines (`VIEWER_SHOWS_LINES` in `space/session/files/session_file.py`). Acceptance tests: `space/session/session_graph_spec.py`; `open-files-in-files-app.story.ui_e2e_spec.py` for the page.

*Given* the file bar lists *src/big.py*, which has 90,000 lines
*When* the Person views *big.py*
*Then* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) says *src/big.py* did not open, naming its lines and the most the viewer shows
*And* the next file the Person views opens as before

## Story: Render File As A Page

#### Scenario: Render a markdown file as the page it describes

Requested 2026-11-19: scenarios, story maps and domain models are read as pages, and their text is a press away. Markdown is rendered with the `marked` and `DOMPurify` the page already loads with Monaco, so nothing the file holds runs a script. Only the page draws it: `harness/files_app/app/files/file-rendering.spec.ts`.

*Given* checkout-flow's session holds *README.md*, which starts *# Checkout*
*When* the Person views *README.md*
*Then* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) shows *Checkout* rendered as a heading, not as *# Checkout*
*And* its Rendered toggle is pressed and its Source toggle is not
*And* a link to a file that is not there keeps the Files app where it is, *README.md* the one open file

#### Scenario: Render each format the page can draw

*Given* checkout-flow's session holds <file>, reading <text>
*When* the Person views <file>
*Then* the Files app shows <rendered>, with Source a press away

| file | text | rendered |
| --- | --- | --- |
| *notes/page.html* | `<h1>Checkout</h1><script>parent.hacked = 1</script>` | the page in a frame apart from the Files app, *Checkout* as its heading, its script reaching nothing outside the frame |
| *design/cart.svg* | `<svg xmlns="http://www.w3.org/2000/svg"><circle r="4"/><script>alert(1)</script></svg>` | the drawing, its circle and no script |
| *data/cart.json* | `{"items":[1,2]}` | the object laid out two spaces to a level, *"items": [* on its second line |
| *data/broken.json* | `{"items":` | its text, and a note that it is not valid JSON |

#### Scenario: Walk a generated UX mockup in its frame

Answered by the person on 2026-11-23 (round 3 of exploratory testing, r3-pixel-08): a UX mockup is runnable greybox, so the Files app shows it as a person can walk it. Every HTML page runs its own scripts in a frame of its own, which gives it no origin, so nothing it runs reaches the Files app; the Files server serves the scripts it names from its own folder of the project, under a key the server made for the project, and the Story Demo scripts of the CDD install it names from */practices/ux/story-demo* (`harness/files_app/app/page-files.ts`, `files/page-frames.ts`).

*Given* checkout-flow's session holds *ordering.html*, a mockup the UX mockup fidelity wrote, with its Catalog, Cart and Cart - Saved screens, its Browse button going to the Cart, and its story module *stories/place_order.js* beside it, whose story lists the Product *Tiny Tales*
*When* the Person views *ordering.html*
*Then* the Files app shows the mockup with its Site Map Explorer listing *catalog*, *cart* and *cart-saved*
*When* the Person presses *Browse <all>*
*Then* the mockup shows the Cart screen
*When* the Person zooms the mockup in
*Then* the mockup shows at 110%
*When* the Person plays the next story step
*Then* the Catalog's Products list *Tiny Tales*
*But* nothing the mockup runs reaches the Files app

#### Scenario: Show text in angle brackets that is no HTML tag

Round 3 of exploratory testing (r3-pixel-01): a class model writes a class's stereotypes and what a collection holds in angle brackets, and the page dropped them as HTML tags it did not know. Only the page draws it: `harness/files_app/app/files/file-rendering.spec.ts`.

*Given* checkout-flow's session holds *domain-model.md*, with the heading *#### Cart <<Aggregate Root>> <<Entity>>* and the line *+ carts: Collection<Cart>*
*When* the Person views *domain-model.md*
*Then* the Files app shows the heading *Cart <<Aggregate Root>> <<Entity>>* and the line *carts: Collection<Cart>*, as the file writes them
*But* HTML the file holds in lower case, such as *<details>*, is still drawn as HTML

#### Scenario: Show a file's front matter as its facts, under no heading

Round 3 of exploratory testing (r3-pixel-02): every generated practice file starts with front matter, which the page drew as its biggest heading.

*Given* *story-map.md* starts with the front matter *fidelity: [discovery]*, *artifact: [story-map]*, *format: md* between two *---* rules, then *# Story Map - Bookshop*
*When* the Person views *story-map.md*
*Then* the Files app shows the three lines of front matter small above the page
*And* the page's only heading reads *Story Map - Bookshop*

#### Scenario: Underline a scenario's domain terms and examples

Round 3 of exploratory testing (r3-pixel-09): a scenario marks a domain term and an example with `++`, which the page printed.

*Given* a scenario file's step reads *\*Given\* the Bookshop sells ++Book++ ++Tiny Tales++*
*When* the Person views it
*Then* the Files app shows *Book* and *Tiny Tales* underlined, and prints no plus sign

#### Scenario: Keep the levels of an indented tree

Round 3 of exploratory testing (r3-pixel-07): a BDD realization nests its states two spaces a level, each observation's call graph fenced under its state, and the page drew every line at the left edge.

*Given* *bookshop-bdd-realization.md* reads *a shipment*, under it *that has been created for a paid order*, and under that a fenced call graph of two lines
*When* the Person views it
*Then* the Files app shows *that has been created for a paid order* indented two spaces under *a shipment*
*And* the call graph as a block indented four spaces, each of its lines on a line of its own

## Story: Follow Links And Callouts In A File

#### Scenario: Open a callout in place on a rendered page

Answered by the person on 2026-11-20 (round 3 of exploratory testing, r3-pixel-03 to 05): the Rendered view and the Source view both show callouts, and a callout is traversable as the graph tree is. The session answers each file's callouts (`session.file`, Open Linked Sections In Place in `switch_files_app_between_files_and_graph_story.test.md`); the page draws them: `harness/files_app/app/files/rendered-callouts.spec.ts`.

*Given* the Files app shows the story map rendered, its story *Add Book To Cart* linked to its scenario file, whose Given links the domain term *Book* to the domain model
*When* the Person presses the mark at the end of *Add Book To Cart*'s line
*Then* the scenario file shows under the story's line, rendered as a page and shaded once, headed by its file and lines
*When* the Person presses the mark at the end of the Given's line, inside it
*Then* the *Book* section of the domain model shows under the Given, one shade deeper
*And* a second press on a mark closes what it opened

#### Scenario: Open what a step observes, then an operation it calls, in place

*Given* the Files app has read the session's graph, and shows the story map rendered with Cross-file on
*When* the Person opens *Add Book To Cart*'s scenario in place, then the example its Given observes
*Then* the example's code shows under the Given, with a mark on each line that calls an operation the graph holds
*When* the Person presses one
*Then* that operation's code shows under the line that calls it

#### Scenario: Follow a link on a rendered page

Changed by the person's answer on 2026-11-20: a link to another file was left where it was, with nothing to follow.

*Given* the Files app shows the story map rendered
*When* the Person presses the link *Add Book To Cart*
*Then* the Files app opens the scenario file at the lines the link names
*When* the Person presses a link to a web page
*Then* the web page opens in a tab of its own and the Files app stays where it is

#### Scenario: Say what is not there for a link to a heading or a file that is missing

*Given* a scenario file links *Cart Line* to a heading the domain model does not have
*When* the Person views it, rendered or as source
*Then* the line's mark shows as missing, and opened it says *.context/domain-model.md has no heading #cartline-entity*
*And* pressing the link opens no file

#### Scenario: Show the callouts the file view's filters select

Answered by the person on 2026-11-20: which callouts show follows the file view's filters, the practices chosen and the graph's connectors. Changed the same day, in the third wave: the session decides it, by the filter that narrows the graph view's trees, and the page sends its filters with the read of the file and draws what comes back. What the session answers for each filter: Filter Callouts Like The Graph in `../switch-files-app-between-files-and-graph/switch_files_app_between_files_and_graph_story.test.md`. What the page sends, and that it reads its open files again when a filter changes: `harness/files_app/app/files/file-callouts.spec.ts`, `files-page.spec.ts`.

*Given* the Files app shows a scenario file whose Given links the domain model, a file of DDD, and observes an example
*When* the Person turns DDD off
*Then* the Given's line no longer carries the callout into the domain model, in the rendered view and the source view alike
*When* the Person leaves *observes* out of the graph view's connectors
*Then* the Given's line no longer carries the example it observes

#### Scenario: Follow a link in the source view

*Given* the Files app shows the story map in the source view, *Add Book To Cart*'s line carrying its callout
*When* the Person presses the link's text with Ctrl held
*Then* the Files app opens the scenario file at the lines the link names
*And* Go to file on the open callout does the same

## Story: Lay Out Lines In Source View

#### Scenario: Scroll a long line sideways

Requested by the person on 2026-11-16: the source view is as tall as its file, so the page scrolls up and down and a long line ran off the page.

*Given* checkout-flow's session holds *order.py*, whose line 14 is wider than the source view
*When* the Person scrolls sideways over the source view, or scrolls with shift held
*Then* the [source view](../../../harness/graph/app/source/SourceView.tsx) scrolls *order.py*'s lines sideways, and the page stays as wide as the window
*And* the wheel without shift still scrolls the page up and down

#### Scenario: Wrap long lines in the source view

Requested by the person on 2026-11-16.

*Given* the Files app shows *order.py* with its long lines unwrapped
*When* the Person turns on Wrap lines
*Then* the [source view](../../../harness/graph/app/source/SourceView.tsx) wraps line 14 onto the lines below it, and grows as tall as the wrapped file
*And* the Files app keeps Wrap lines on for the next file the Person opens

#### Scenario: Show the source view in Cursor's default colours with an orange cursor

Requested 2026-11-16 by the person: "Format the viewer using ABD branding", then, on seeing it, "ugly", "use default Cursor coloring", and orange only for the selected node's line, the line number and the cursor. The code takes Cursor's default looks, Cursor Dark and Cursor Light (Cursor's theme-cursor extension); abd.works orange (`harness/catalog_generator/templates/commons/site.css`) marks only the cursor, the current line number and the selected node's line. Only the page draws it: `harness/files_app/app/files/files-theme.spec.ts`.

*Given* the Files app shows *order.py* in its dark look
*When* the Person views *order.py*
*Then* the source view draws *order.py* in Cursor Dark's colours, #181818 behind #F0F0F0 text, its keywords, strings and numbers in Cursor Dark's token colours
  *And* the cursor and the current line number are abd.works orange
  *And* selected text sits on Cursor Dark's grey and folded lines carry no tint
*When* the Person turns the dark look off
*Then* the source view draws *order.py* in Cursor Light's colours, #FCFCFC behind #141414 text, with the same orange cursor and current line number

## Story: Fold Classes And Operations

Changed by the person on 2026-11-16 ("native expand collapse for class functions, heading levels in markdown etc like a real IDE"): the source view folds as Monaco folds the file's language, with or without Rules, in place of folds drawn by hand from the session's graph. Only the page folds, so these scenarios have no step in the Python story tiers; `harness/graph/app/app.test.tsx` holds them.

#### Scenario: Fold the file's class, its operations and their blocks

Inherited from the graph's Unfold Calls And Classes In Source: the Files app reuses the graph explorer's source view (`harness/graph/app/source/SourceView.tsx`).

*Given* checkout-flow's session holds *order.py*, its class *Order* on lines 5 to 41, its operation *place* on lines 12 to 14, and the *if* on line 13
*When* the Person views *order.py*
*Then* the source view offers a fold of *Order*, of *place* and of the *if*, each at its first line, as an IDE does

#### Scenario: Fold a markdown file by its headings

*Given* checkout-flow's session holds *README.md*, whose *# Checkout* holds *## Place an order* and *## Pay*
*When* the Person views *README.md*
*Then* the source view offers a fold of each heading over its section, *# Checkout* over both of the others
*But* a heading inside a code block folds nothing

#### Scenario: Fold the file with Folds on and Rules off

Requested by the person on 2026-11-18: "Code folds is a separate toggle." Changed by the person the same day ("in the graph folds and rules are on by default"): both toggles are on by default, as the graph shows them. The board's file viewer has a Folds toggle and a Rules toggle: Folds shows the folds of the file's classes and operations, Rules its broken rules, each without the other.

*Given* checkout-flow's session holds *order.py*
*And* checkout-flow's graph places the class *Order* on lines 5 to 41 of *order.py*, and found *vocabulary-traces-to-source* broken on lines 12 to 14
*When* the Person views *order.py* with Folds on and Rules off
*Then* the viewer offers a fold of *Order* over lines 5 to 41, and a fold of *place* over lines 12 to 14
*And* it marks no broken rule

## Story: Fold With Keyboard Shortcuts

Requested by the person on 2026-11-16: "Cursor-equivalent keyboard shortcuts (or VS Code, configurable in a context config json), e.g. Ctrl+K Ctrl+0, Ctrl+M etc." The project's keys sit in `.context/files-app-keybindings.json`, written as VS Code's and Cursor's keybindings.json writes them. Only the page binds keys: `harness/files_app/app/files/files-fold-keys.spec.ts`.

Changed 2026-11-16 by the person: "Expand/collapse folds keyboard shortcuts use Cursor defaults." Cursor ships VS Code's fold keys with its chord leader moved off Ctrl+K, which Cursor keeps for inline edit, to Ctrl+M on Windows and Linux (Cmd+R on a Mac): Ctrl+Shift+[ and ] fold and unfold the region, Ctrl+M Ctrl+0 folds all, Ctrl+M Ctrl+J unfolds all, Ctrl+M Ctrl+[ and ] fold and unfold recursively, Ctrl+M Ctrl+L toggles a fold, Ctrl+M Ctrl+1 to 7 fold that level. These are the keys a project with no keybindings file gets.

#### Scenario: Fold with Cursor's chords

Requested 2026-11-16 by the person, in place of VS Code's Ctrl+K chords.

*Given* the project has no *.context/files-app-keybindings.json*
*When* the Person presses Ctrl+M Ctrl+0 in *order.py*
*Then* every fold of *order.py* closes
*When* the Person presses Ctrl+M Ctrl+J
*Then* every fold opens again
*When* the Person presses Ctrl+Shift+[ on line 12
*Then* the fold of *place* closes

#### Scenario: Fold with the keys the project's keybindings file gives

*Given* *.context/files-app-keybindings.json* gives Ctrl+M Ctrl+M to *editor.toggleFold*
*When* the Person presses Ctrl+M Ctrl+M on line 12 of *order.py*
*Then* the fold of *place* closes

#### Scenario: Keep Cursor's chords when the keybindings file is wrong

Required by the cdd_web_domain_access rule `fail-loud-on-mcp` this session overlays. Changed 2026-11-16 by the person: the keys kept are Cursor's.

*Given* *.context/files-app-keybindings.json* is not a list of keys and fold commands
*When* the Files app opens
*Then* a toast says the file is not used, with why
*And* Ctrl+M Ctrl+0 still folds every fold

## Story: Open Calls And Classes In Place

Requested by the person on 2026-11-16: "we are being too aggressive on the shading and double shading, e.g. the callout label then the actual callout content. On expand, hide the callout label and show the content; on collapse, bring it back. Only shade once." Only the page shows it: `harness/graph/app/app.test.tsx`.

#### Scenario: Label a call while it is closed

*Given* the Files app shows *order.py*, whose line 13 calls *cart.is_empty()*, after the graph view read checkout-flow's members
*When* the Person views *order.py*
*Then* line 13 ends with the label *▸ Cart.is_empty*, and nothing of *Cart.is_empty* shows under it

#### Scenario: Open a call in place of its label, shaded once

*Given* the Files app shows *order.py* with line 13 labelled *▸ Cart.is_empty*
*When* the Person presses the label or its mark
*Then* the lines of *Cart.is_empty* show under line 13, shaded once, without the marks the graph puts after each call
*And* the label is hidden
*When* the Person presses the mark again
*Then* the lines of *Cart.is_empty* close and the label comes back

#### Scenario: Open a call inside an open call one shade deeper

*Given* the lines of *Cart.is_empty* show under line 13 of *order.py*, and they call *Cart.items*
*When* the Person presses the mark beside that call
*Then* the lines of *Cart.items* show under it, one shade deeper

#### Scenario: Open nothing a comment or a docstring names

*Given* *order.py*'s docstring and a comment name the class *Cart*
*When* the Person views *order.py*
*Then* neither line carries a label or a mark

## Story: Mark Lines A Broken Rule Names

#### Scenario: Mark the lines a broken rule names

Inherited from the graph's Open Violation In Source.

*Given* checkout-flow's session holds *order.py*
*And* checkout-flow's graph found *vocabulary-traces-to-source* broken on lines 12 to 14 of *order.py*
*When* the Person views *order.py* with Rules turned on
*Then* the source view marks lines 12 to 14 with *vocabulary-traces-to-source*: *EmptyCartError should say which cart and why*

#### Scenario: Browse a file with Rules off

Requested (the person, 2026-11-15): Rules and Cross-file toggles at the top, off by default, so browsing files never pays for reading the graph.

*Given* checkout-flow's session holds *order.py*
*And* checkout-flow's graph found *vocabulary-traces-to-source* broken on lines 12 to 14 of *order.py*
*When* the Person views *order.py* with Rules off
*Then* the source view shows *order.py* with no broken rules, folding only as its language folds

## Story: Save Edited File

#### Scenario: Save the edited text to the file on disk

Intended in the Files app: the board's files panel did it until 2026-11-21, when that panel was removed (design proposal 24); the Files app is read-only today, so no page saves an edited file.

*Given* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) shows *order.py* of checkout-flow, read with its version
*And* the Person has edited line 14 to read *raise EmptyCartError(cart.id, "a cart needs one item to be placed")*
*When* the Person saves the file with the version it was read with
*Then* *order.py* on disk reads that line 14
*And* the source view is read-only again, showing the saved text

#### Scenario: Save a file into the session's own folder, naming the session by its name

Requested 2026-11-16: a chat in checkout-flow's worktree ran the debug skill, which writes its report as *debug/debug-{time}.md* in the session's folder with session.write_file. The tool refused the session's name, which sessions.switch had opened it by, and then refused the session's folder, which sits in the main checkout's *.sessions*, outside the worktree and its practices' folders. Only the session's own folder is added: a path outside it and outside the session's roots is still refused. Realized by `space/session/files/session_files_spec.py`.

*Given* checkout-flow works in its ticket's worktree, its session folder *.sessions/checkout-flow* in the main checkout
*When* an agent saves *debug/debug-20261116T225500.md* in checkout-flow's folder with session.write_file, naming the session *checkout-flow*
*Then* the report is on disk in *.sessions/checkout-flow/debug*
*But* a file named outside the session's folder and its roots is still refused

#### Scenario: Refuse to save over the session's own session.json

Requested 2026-11-22 (the person: the session's record has one writer). Observed (`space/session/files/session_files_spec.py`). Every change to *session.json* holds the file from its read to its write (Keep Every Change To Session Record), and a whole-file save would drop a change another chat made.

*Given* checkout-flow's session folder *.sessions/checkout-flow* holds its *session.json*
*When* an agent saves *.sessions/checkout-flow/session.json* with session.write_file
*Then* the save is refused, naming *session.json* as the session's record and saying to change it with the session's tools
*And* *session.json* is as it was
*And* the same save is refused when the path is absolute, opens with *./*, goes through a folder and back (*debug/../session.json*), is written with backslashes, or is in another case where the file system reads that as the same file
*But* session.read_file still reads *session.json*
*And* a file named *session.json* in another folder, such as *.sessions/checkout-flow/debug/session.json*, is saved

#### Scenario: Refuse to save over a file changed on disk since it was read

Found on 2026-11-23 (exploratory testing, pixel-06; the person's answer: refuse it and say so). session.write_file replaced a file someone changed on disk between the read and the write, and the change was lost with no word. session.read_file now answers the file's *version*, a hash of its content, and session.write_file takes it back. Acceptance tests: `space/session/files/session_files_spec.py`.

*Given* the viewer shows *order.py* of checkout-flow, read with its version
*And* someone else has since changed *order.py* on disk
*When* the Person saves the file with the version it was read with
*Then* the save is refused, saying *order.py* changed on disk since it was read
*And* *order.py* on disk keeps the change someone else made
*But* a save of a file not there yet, with no version, is saved

#### Scenario: Refuse to read or save a file inside the repository's .git folder

Found on 2026-11-23 (exploratory testing, pixel-05; the person's answer: refuse it, naming the path). session.write_file wrote *.git/pixel-probe* and session.read_file answered the whole of *.git/config*; a hook written under *.git* runs on the person's next commit. Acceptance tests: `space/session/files/session_files_spec.py`.

*Given* checkout-flow's repository holds *.git/config*
*When* the Person reads *.git/config*, or saves *.git/hooks/pre-commit*
*Then* each is refused, naming the path as inside a *.git* folder, which holds git's own record
*And* nothing is written under *.git*
*But* a file whose name only starts with *.git*, such as *.gitignore*, is read and saved as any other

---

## Sub-epic: Review Files With Comments

## Story: Add Comment To File Selection

#### Scenario: Mark a comment beside the selection's first line

*Given* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) shows *order.py* of checkout-flow
*And* the Person has selected lines 12 to 14
*When* the Person adds the [file comment](../../../harness/files_app/.context/files-app-model.md#filecommentsactions-filesfile-comments-actionsts) *an empty cart should say which cart and why* to the selection
*Then* a comment marker shows beside line 12, not sent
*And* checkout-flow's file comments hold *order.py:L12-L14* with that comment
*And* the Person can Send File Comments To Chat with it

#### Scenario: Keep file comments when the page reloads

*Given* checkout-flow's file comments hold *order.py:L12-L14*
*When* the Person views *order.py* again after the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) reloads
*Then* the comment marker still shows beside line 12

## Story: Open Edit And Delete File Comment

#### Scenario: Open a file comment from its marker

*Given* checkout-flow's file comments hold *order.py:L12-L14*, *an empty cart should say which cart and why*
*When* the Person opens the comment at the marker beside line 12
*Then* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) shows *an empty cart should say which cart and why* under lines 12 to 14, with its state

#### Scenario: Edit a file comment

*Given* checkout-flow's file comments hold *order.py:L12-L14*, *an empty cart should say which cart and why*, not sent
*When* the Person edits that comment to read *say which cart is empty and why*
*Then* checkout-flow's file comments hold *order.py:L12-L14* reading *say which cart is empty and why*, not sent

#### Scenario: Delete a file comment

*Given* checkout-flow's file comments hold *order.py:L12-L14*, not sent
*When* the Person deletes that comment
*Then* no comment marker shows beside line 12
*And* checkout-flow's file comments no longer hold *order.py:L12-L14*

## Story: Send File Comments To Chat

#### Scenario: Add a comment to the chat's queue

*Given* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) was opened from the [chat](../../../space/kanban/.context/kanban-model.md#chat) *checkout-chat*, which has checked in
*And* checkout-flow's file comments hold *order.py:L12-L14*, *an empty cart should say which cart and why*, not sent
*When* the Person sends that comment to the chat
*Then* the *checkout-chat* queue holds a fill that reads:

```
src/checkout/order.py:12-14: an empty cart should say which cart and why
> 12 |     def place(self, cart: Cart) -> Order:
> 13 |         if not cart.items:
> 14 |             raise EmptyCartError(cart.id)

session=.sessions/checkout-flow/session.json
```

*And* the comment marker beside line 12 shows the comment as sent
*And* the chat can Mark File Comment Processed once it has worked on it

#### Scenario: Send every open comment at once

*Given* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) was opened from *checkout-chat*, which has checked in
*And* checkout-flow's file comments hold *order.py:L12-L14* and *order.py:L30-L31*, both not sent
*And* *order.py:L40-L41* already sent
*When* the Person sends checkout-flow's open file comments to the chat
*Then* the *checkout-chat* queue holds one fill naming *order.py:12-14* and *order.py:30-31*, each with its lines and comment
*And* the markers beside lines 12 and 30 show their comments as sent
*But* *order.py:L40-L41* is not sent again

#### Scenario: Keep the comment unsent when the chat is not connected

*Given* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) was opened from *checkout-chat*
*And* checkout-flow's file comments hold *order.py:L12-L14*, not sent
*But* *checkout-chat* has not checked in
*When* the Person sends the comment *order.py:L12-L14* to the chat
*Then* a toast says *chat 'checkout-chat' is not connected: is the cdd-board mod loaded in it?*
*And* the comment marker beside line 12 shows the comment as not sent

## Story: Mark File Comment Processed

#### Scenario: Mark a comment processed once the chat has worked on it

*Given* checkout-flow's [file comment](../../../harness/files_app/.context/files-app-model.md#filecommentsactions-filesfile-comments-actionsts) *order.py:L12-L14* is sent, as a message to *checkout-chat*
*And* *checkout-chat* has shown that message and its turn is working on it
*When* *checkout-chat*'s turn ends
*Then* checkout-flow's file comments show *order.py:L12-L14* as processed
*And* the comment marker beside line 12 shows the comment as processed
*And* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) can Show Changed File After Comment

#### Scenario: Keep a comment sent while the chat still works on it

*Given* checkout-flow's [file comment](../../../harness/files_app/.context/files-app-model.md#filecommentsactions-filesfile-comments-actionsts) *order.py:L12-L14* is sent, as a message to *checkout-chat*
*But* *checkout-chat*'s turn has not ended
*When* the Person views *order.py*
*Then* the comment marker beside line 12 shows the comment as sent

## Story: Show Changed File After Comment

#### Scenario: Show the agent's change to the open file

*Given* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) shows *order.py* of checkout-flow, read-only
*And* the chat's turn changed line 14 of *order.py* to *raise EmptyCartError(cart.id, "a cart needs one item to be placed")*
*When* the [file comment](../../../harness/files_app/.context/files-app-model.md#filecommentsactions-filesfile-comments-actionsts) *order.py:L12-L14* is marked processed
*Then* the source view shows line 14 as *raise EmptyCartError(cart.id, "a cart needs one item to be placed")*
*And* the comment marker still shows beside line 12, processed

## Story: Clear Processed File Comments

#### Scenario: Clear the processed comments, keeping the rest

*Given* checkout-flow's file comments hold *order.py:L12-L14* processed, *order.py:L30-L31* sent, and *order.py:L40-L41* not sent
*When* the Person clears checkout-flow's processed file comments
*Then* no comment marker shows beside line 12
*And* the markers beside lines 30 and 40 still show, sent and not sent

## Story: Show AI Changes As Diff

Intended in the Files app (`.sessions/_backlog/review-work-in-board-files.md`, "change viewer from ai change like vscode / cursor"); the session answers the changes (`SessionFile.changes`, `space/session/files/session_file.py`) and the board's files panel drew them until it was removed on 2026-11-21 (design proposal 24). What counts as the chat's change is the difference between the file as it read when the comment was sent and the file once the comment is processed.

#### Scenario: Mark the line the chat changed, with the line it replaced

*Given* checkout-flow's [file comment](../../../harness/files_app/.context/files-app-model.md#filecommentsactions-filesfile-comments-actionsts) *order.py:L12-L14* was sent while line 14 read *raise EmptyCartError(cart.id)*
*And* the chat's turn changed line 14 to *raise EmptyCartError(cart.id, "a cart needs one item to be placed")*
*When* the file comment *order.py:L12-L14* is marked processed
*Then* the source view marks line 14 as changed by the chat
*And* shows the line it replaced, *raise EmptyCartError(cart.id)*, as removed above it

#### Scenario: Mark the lines the chat added

*Given* checkout-flow's [file comment](../../../harness/files_app/.context/files-app-model.md#filecommentsactions-filesfile-comments-actionsts) *order.py:L12-L14* was sent
*And* the chat's turn added two lines after line 14
*When* the file comment *order.py:L12-L14* is marked processed
*Then* the source view marks lines 15 and 16 as added by the chat
*But* marks no line before them as changed

#### Scenario: Mark nothing when the chat left the file as it was

*Given* checkout-flow's [file comment](../../../harness/files_app/.context/files-app-model.md#filecommentsactions-filesfile-comments-actionsts) *order.py:L12-L14* was sent
*And* the chat's turn changed no line of *order.py*
*When* the file comment *order.py:L12-L14* is marked processed
*Then* the source view marks no line of *order.py* as changed

#### Scenario: Stop marking the changes once the processed comment is cleared

*Given* the source view marks line 14 of *order.py* as changed by the chat for the processed comment *order.py:L12-L14*
*When* the Person clears checkout-flow's processed file comments
*Then* the source view marks no line of *order.py* as changed
*And* line 14 still reads *raise EmptyCartError(cart.id, "a cart needs one item to be placed")*

## Story: Add File Or Selection To Chat Context

Requested (2026-11-15, "on right click of file we also need an add to context option; same with selected text in file viewer; adds to chat context like Claude functionality does in file viewer"). The file or the selection goes to the chat as a fill, as a file comment does, so it waits in the chat's prompt box and goes with the person's next prompt rather than being sent on its own, as an `@` mention from Claude's own file viewer does.

#### Scenario: Add a file to the chat's context

*Given* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) was opened from the [chat](../../../space/kanban/.context/kanban-model.md#chat) *checkout-chat*, which has checked in
*And* it lists *order.py*
*When* the Person adds *order.py* to the chat's context
*Then* the *checkout-chat* queue holds a fill that reads `@src/checkout/order.py `
*And* the fill waits in *checkout-chat*'s prompt box, to go with the person's next prompt

#### Scenario: Add selected lines to the chat's context

*Given* the Files app was opened from *checkout-chat*, which has checked in
*And* it shows *order.py* with lines 12 to 14 selected
*When* the Person adds the selection to the chat's context
*Then* the *checkout-chat* queue holds a fill that reads:

```
src/checkout/order.py:12-14
> 12 |     def place(self, cart: Cart) -> Order:
> 13 |         if not cart.items:
> 14 |             raise EmptyCartError(cart.id)
```

*And* the fill waits in *checkout-chat*'s prompt box, to go with the person's next prompt

#### Scenario: Say so when the chat is not connected

Required by the cdd_web_domain_access rule `fail-loud-on-mcp` this session overlays.

*Given* the Files app was opened from *checkout-chat*
*But* *checkout-chat* has not checked in
*When* the Person adds *order.py* to the chat's context
*Then* a toast says *chat 'checkout-chat' is not connected: is the cdd-board mod loaded in it?*
