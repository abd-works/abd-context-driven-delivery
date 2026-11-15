---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Epic: Review Files In Files App

Map: [story-map.md](../../story-map.md#e-review-generated-work-in-file-viewer). Acceptance tests: `space/session/files_app/review-files-in-files-app.story.shared.py`, replayed by `.story.domain.spec.py` and `.story.server.spec.py` beside it, for what the session answers; `space/session/files_app/app/files/*.spec.ts` for what only the page shows.

Consolidated on 2026-11-14 from the board's Review Files In Viewer scenarios (this file, moved from `harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-files-in-viewer/`), the chat bar's View Fidelity Files scenarios (`harness/.context/stories/move-work-forward-from-chat-bar/guide-work-through-practices/guide_work_through_practices_story.test.md`), the Story UI's acceptance-test link (`.../integrate_practice_content_editor_apps_in_chat_bar_story.test.md`), and the graph's source view stories (`harness/graph/.context/story-map.md`, Open Node Source, Unfold Calls And Classes In Source, Open Violation In Source). Scenario names kept from those sources are unchanged, so the shared steps still find them.

### Domain terms

- [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card): one session on the board.
- [session](../../../../../space/kanban/.context/kanban-model.md#session): the work behind a ticket. It works in its workpath, and its files are named from there. The Files app reaches no file outside the session's roots.
- [chat](../../../../../space/kanban/.context/kanban-model.md#chat): a Claude Code chat whose cdd-board mod checks in. Its queue holds the messages sent to it. A message is done once the chat's turn that worked on it has ended.
- [Files app](../../../../../space/session/files_app/.context/files-app-model.md#filespage-filesfiles-pagets): the file viewer as an app of its own, on its own server and port, opened beside the chat by a link that names the files to show and the chat that opened it (`space/session/files_app/files_app.py`). It never reads the board.
- [practice](../../../../../space/session/files_app/.context/files-app-model.md#session-practicesessionoutput-python-spacesession): a lens the session works through (Stories, DDD, UX, Clean Engineering, BDD), on or off for the session, with its own colour (`practice_session_output.py`).
- file manager: the session's reader and writer of the files under its roots (`space/session/file_manager.py`).
- [file comment](../../../../../space/session/files_app/.context/files-app-model.md#filecommentsactions-filesfile-comments-actionsts): a comment a person writes on lines of a file, kept in the session's folder. It is not sent, then sent, then processed.

### Evidence

| Source | Note |
|--------|------|
| `.sessions/review-work-in-board-files/review-work-in-board-files.md`, request of 2026-11-12 | A shared Monaco viewer typed on the file manager's file shape. Edit and Save. Comments go to the chat with the selected text and the file's name. |
| `.sessions/review-work-in-board-files/file-viewer-research.md`, "Recommendation" | Comments go through the chat queue, `chat.send`. A comment is anchored as `path:Lstart-Lend`. Send all sends every open comment at once. |
| The person, 2026-11-12 | "chat process comment and changes files then viewer is updated to reflect changes and comment is at processed stage; comment --> not sent, sent, processed; a send all open comment button top left of viewer and a clear processed comments button" |
| `harness/.context/stories/story-map.md`, Browse Ticket Files By Practice, 2026-11-12 | "put the filter toggles on the top"; filters preset when opening the files from the chat bar; the person can toggle them; coloured by practice. |
| The person, 2026-11-14 | "the patterns should be toggles at the top; be the practice color; and allow us to toggle the practice filter here (also toggles the command bar so they stay in sync)"; the toggles are practices. |
| The person, 2026-11-14 | "clicking on drawio --> open in new tab works but orig tab also getting moved to drawio; leave it on file explorer" |
| Walk of the Files app in the browser pane, 2026-11-14 | Observed: a file opens in the source view; Add comment, its marker, edit, delete and Send all work; a sent comment lands in the chat's prompt box; a `.drawio` file opens in the draw.io viewer. |
| `harness/chat/chat.py` `send`, `check_in` | `send(kind, text)` queues a command; a chat that has not checked in raises `ChatNotConnectedError`; a shown message moves to done when the chat's turn that worked on it ends. |

In every scenario, the [session](../../../../../space/kanban/.context/kanban-model.md#session) of [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) checkout-flow works in *src/checkout*, in its Discovery stage, with Stories on and DDD off. Its *order.py* reads, at lines 12 to 14:

```
12 |     def place(self, cart: Cart) -> Order:
13 |         if not cart.items:
14 |             raise EmptyCartError(cart.id)
```

---

## Sub-epic: Open Files In Files App

## Story: Open Stage Files From Chat Bar

#### Scenario: Open the files beside the chat, never in it

*Given* checkout-flow's Discovery stage holds the fidelities stories-story-map and ddd-bounded-context
*And* checkout-flow is assigned the chat *checkout-chat*
*When* the Person opens the stage's files from *checkout-chat*'s chat bar
*Then* the [Files app](../../../../../space/session/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) opens beside the chat, naming checkout-flow and *checkout-chat*
*And* its link names both fidelities, stories-story-map and ddd-bounded-context, the [practice](../../../../../space/session/files_app/.context/files-app-model.md#session-practicesessionoutput-python-spacesession) turned off among them
*And* the chat bar draws no file, and no diagram is read into the chat
*And* the Person can Toggle Practice In Files App there

## Story: Open Session Folder From Chat Bar

#### Scenario: List the session's own folder

*Given* checkout-flow's session folder *.sessions/checkout-flow* holds *session.log* and a handoff
*When* the Person opens the session's folder from *checkout-chat*'s chat bar
*Then* the [Files app](../../../../../space/session/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) opens on *.sessions/checkout-flow*, listing *session.log* and the handoff

## Story: Open File From Another Page

#### Scenario: Open the file a page sent the chat

*Given* the Story UI editor was opened from *checkout-chat* on checkout-flow's story map
*And* the story *Open Story UI* has its acceptance test at *move-work-forward-from-chat-bar/open_story_ui_story.test.py*
*When* the Person opens the acceptance-test link of *Open Story UI* there
*Then* *checkout-chat* gets an open_file naming *move-work-forward-from-chat-bar/open_story_ui_story.test.py*
*And* the [Files app](../../../../../space/session/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) opens on checkout-flow's session folder with *open_story_ui_story.test.py* open
*But* the Story UI editor opens no file of its own

## Story: List Files The Link Names

#### Scenario: List each file once, without reading the board

*Given* the [Files app](../../../../../space/session/files_app/.context/files-app-model.md#filespage-filesfiles-pagets)'s link names stories-story-map, whose files are *story-map.md* and *story-map.drawio*
*When* the Files app opens
*Then* it lists *story-map.md* and *story-map.drawio*, each once
*And* opens *story-map.md*, the first file that is not a diagram
*But* it reads nothing from the board

#### Scenario: List a file not generated yet, which cannot be opened

*Given* stories-story-map declares *story-map.md*, which is not on disk yet
*When* the [Files app](../../../../../space/session/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) opens
*Then* it lists *story-map.md* as not generated yet
*And* the Person cannot open it

## Story: Open Diagram In Draw.io Tab

#### Scenario: Open a diagram in a tab of its own, keeping the file list

*Given* the [Files app](../../../../../space/session/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) lists *story-map.drawio*
*When* the Person opens *story-map.drawio*
*Then* the draw.io editor opens on *story-map.drawio* in a new tab
*And* the Files app's tab still shows its file list
*And* nothing is sent to the chat

#### Scenario: Close the new tab when the draw.io viewer does not start

Required by the cdd_web_domain_access rule `fail-loud-on-mcp` this session overlays: when a call fails, the page shows the person what failed instead of an empty tab.

*Given* the [Files app](../../../../../space/session/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) lists *story-map.drawio*
*But* the draw.io viewer does not start
*When* the Person opens *story-map.drawio*
*Then* the new tab closes
*And* a toast says *story-map.drawio did not open in the draw.io viewer*, with the reason

## Story: Switch File Bar Between Folders And List

Requested (the person, 2026-11-14): "expand collapse file bar with buttons to swap a folder view and file list". Only the page shows it: the session answers the same files either way.

#### Scenario: Collapse the file bar to give the open file the page

*Given* the [Files app](../../../../../space/session/files_app/.context/files-app-model.md#filebar-filesfile-barts) lists *story-map.md* and *src/checkout/order.py*, with *order.py* open
*When* the Person collapses the file bar
*Then* the file bar shows only its buttons, and *order.py* takes the page's width
*When* the Person expands the file bar
*Then* the file bar lists *story-map.md* and *order.py* again

#### Scenario: Show the files in their folders, the open file's folder open

*Given* the [Files app](../../../../../space/session/files_app/.context/files-app-model.md#filebar-filesfile-barts) lists *.context/story-map.md*, *src/checkout/order.py* and *src/checkout/cart.py*, with *order.py* open
*When* the Person shows the file bar as folders
*Then* the file bar shows the folders *.context* and *src/checkout*
*And* *src/checkout* is open, showing *cart.py* and *order.py*
*And* *.context* is open too, as every folder starts open
*When* the Person shows the file bar as a list
*Then* the file bar lists *story-map.md*, *order.py* and *cart.py* again, in the order the link names them

#### Scenario: Close and open a folder

Requested (the person, 2026-11-15): "keep folder the default view and not reset it every time we change a filter".

*Given* the [Files app](../../../../../space/session/files_app/.context/files-app-model.md#filebar-filesfile-barts) shows its files as folders, its default, *.context* open
*When* the Person closes *.context*
*Then* *.context* shows no file
*When* a filter changes the files listed
*Then* *.context* stays closed
*When* the Person opens *.context*
*Then* *.context* shows *story-map.md*

## Story: List Only The Files The Branch Changed

Requested (the person, 2026-11-15): add a "changed only" filter, since a session working on the whole repository lists every file a fidelity's pattern matches there. The session answers every file with whether the branch changed it; the page filters.

#### Scenario: List only the changed files, then every file again

*Given* the [Files app](../../../../../space/session/files_app/.context/files-app-model.md#filebar-filesfile-barts) lists *.context/story-map.md*, *src/checkout/order.py* and *src/checkout/cart.py*, and the session's branch changed only *order.py*
*When* the Person turns on Changed, its count 1
*Then* the file bar lists *order.py* alone
*And* as folders it shows only *src/checkout*
*When* the Person turns Changed off
*Then* the file bar lists *story-map.md*, *order.py* and *cart.py* again

#### Scenario: Keep a published design canvas

*Given* the Files app lists a design canvas published at its link, unchanged, and *cart.py*, unchanged
*When* the Person turns on Changed
*Then* the file bar lists the design canvas alone, which opens at its link

## Story: Toggle Practice In Files App

#### Scenario: Show each practice as a toggle in its colour

*Given* checkout-flow works on Stories and has DDD turned off
*When* the [Files app](../../../../../space/session/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) opens
*Then* the top of the page shows a Stories toggle filled in Stories' colour, *#6BCB77*
*And* a DDD toggle drawn as an outline in DDD's colour, *#6C5CE7*

#### Scenario: List only the files of the practices turned on

*Given* the [Files app](../../../../../space/session/files_app/.context/files-app-model.md#filespage-filesfiles-pagets)'s link names stories-story-map and ddd-bounded-context
*But* checkout-flow has DDD turned off
*When* the Files app opens
*Then* it lists *story-map.md*
*But* not *bounded-context-map.md*

#### Scenario: Turn a practice on to show its files

*Given* the [Files app](../../../../../space/session/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) shows the DDD toggle as an outline
*When* the Person turns DDD on
*Then* checkout-flow's session works on DDD, saved in its session.json
*And* the DDD toggle fills in DDD's colour
*And* the Files app lists *bounded-context-map.md* beside *story-map.md*
*And* the Files app can Keep Chat Bar Practices In Sync

#### Scenario: Turn a practice off to hide its files

*Given* the [Files app](../../../../../space/session/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) shows the Stories toggle filled
*When* the Person turns Stories off
*Then* checkout-flow's session no longer works on Stories
*And* the Stories toggle shows as an outline
*And* the Files app no longer lists *story-map.md*

## Story: Keep Chat Bar Practices In Sync

#### Scenario: Show a practice turned on in the Files app on the chat bar

*Given* the [Files app](../../../../../space/session/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) was opened from *checkout-chat*, which has checked in
*When* the Person turns DDD on in the Files app
*Then* *checkout-chat* gets a refresh
*And* *checkout-chat*'s chat bar reads the board again and shows ddd-bounded-context's dot

#### Scenario: Show a practice turned off on the chat bar in the Files app

*Given* the [Files app](../../../../../space/session/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) shows the DDD toggle filled
*When* the Person turns DDD off on the chat bar
*Then* within a second, with no press in the Files app, the DDD toggle shows as an outline
*And* the Files app no longer lists *bounded-context-map.md*

---

## Sub-epic: View Files In Source View

## Story: View File In Source View

#### Scenario: Show a code file in the viewer with its lines numbered

*Given* checkout-flow's session holds *order.py*
*When* the Person views *order.py*
*Then* the [Files app](../../../../../space/session/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) shows *order.py* in the source view as Python, with line 12 reading *def place(self, cart: Cart) -> Order:*
*And* the source view is read-only
*And* the Person can Add Comment To File Selection from there

#### Scenario: Render a markdown file as the page it describes

Intended: the Files app shows markdown as text today.

*Given* checkout-flow's session holds *README.md*, which starts *# Checkout*
*When* the Person views *README.md*
*Then* the [Files app](../../../../../space/session/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) shows *Checkout* rendered as a heading, not as *# Checkout*

## Story: Fold Classes And Operations

#### Scenario: Fold the file's class and its operations

Inherited from the graph's Unfold Calls And Classes In Source: the Files app reuses the graph explorer's source view (`harness/graph/app/source/SourceView.tsx`).

*Given* checkout-flow's session holds *order.py*
*And* checkout-flow's graph places the class *Order* on lines 5 to 41 of *order.py*, and its operation *place* on lines 12 to 14
*When* the Person views *order.py* with Rules turned on
*Then* the source view offers a fold of *Order* over lines 5 to 41, and a fold of *place* over lines 12 to 14

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
*Then* the source view shows *order.py* with no folds and no broken rules

## Story: Save Edited File

#### Scenario: Save the edited text to the file on disk

Intended in the Files app: the board's files panel does it, the Files app is read-only today.

*Given* the [Files app](../../../../../space/session/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) shows *order.py* of checkout-flow
*And* the Person has edited line 14 to read *raise EmptyCartError(cart.id, "a cart needs one item to be placed")*
*When* the Person saves the file
*Then* *order.py* on disk reads that line 14
*And* the source view is read-only again, showing the saved text

---

## Sub-epic: Review Files With Comments

## Story: Add Comment To File Selection

#### Scenario: Mark a comment beside the selection's first line

*Given* the [Files app](../../../../../space/session/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) shows *order.py* of checkout-flow
*And* the Person has selected lines 12 to 14
*When* the Person adds the [file comment](../../../../../space/session/files_app/.context/files-app-model.md#filecommentsactions-filesfile-comments-actionsts) *an empty cart should say which cart and why* to the selection
*Then* a comment marker shows beside line 12, not sent
*And* checkout-flow's file comments hold *order.py:L12-L14* with that comment
*And* the Person can Send File Comments To Chat with it

#### Scenario: Keep file comments when the page reloads

*Given* checkout-flow's file comments hold *order.py:L12-L14*
*When* the Person views *order.py* again after the [Files app](../../../../../space/session/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) reloads
*Then* the comment marker still shows beside line 12

## Story: Open Edit And Delete File Comment

#### Scenario: Open a file comment from its marker

*Given* checkout-flow's file comments hold *order.py:L12-L14*, *an empty cart should say which cart and why*
*When* the Person opens the comment at the marker beside line 12
*Then* the [Files app](../../../../../space/session/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) shows *an empty cart should say which cart and why* under lines 12 to 14, with its state

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

*Given* the [Files app](../../../../../space/session/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) was opened from the [chat](../../../../../space/kanban/.context/kanban-model.md#chat) *checkout-chat*, which has checked in
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

*Given* the [Files app](../../../../../space/session/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) was opened from *checkout-chat*, which has checked in
*And* checkout-flow's file comments hold *order.py:L12-L14* and *order.py:L30-L31*, both not sent
*And* *order.py:L40-L41* already sent
*When* the Person sends checkout-flow's open file comments to the chat
*Then* the *checkout-chat* queue holds one fill naming *order.py:12-14* and *order.py:30-31*, each with its lines and comment
*And* the markers beside lines 12 and 30 show their comments as sent
*But* *order.py:L40-L41* is not sent again

#### Scenario: Keep the comment unsent when the chat is not connected

*Given* the [Files app](../../../../../space/session/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) was opened from *checkout-chat*
*And* checkout-flow's file comments hold *order.py:L12-L14*, not sent
*But* *checkout-chat* has not checked in
*When* the Person sends the comment *order.py:L12-L14* to the chat
*Then* a toast says *chat 'checkout-chat' is not connected: is the cdd-board mod loaded in it?*
*And* the comment marker beside line 12 shows the comment as not sent

## Story: Mark File Comment Processed

#### Scenario: Mark a comment processed once the chat has worked on it

*Given* checkout-flow's [file comment](../../../../../space/session/files_app/.context/files-app-model.md#filecommentsactions-filesfile-comments-actionsts) *order.py:L12-L14* is sent, as a message to *checkout-chat*
*And* *checkout-chat* has shown that message and its turn is working on it
*When* *checkout-chat*'s turn ends
*Then* checkout-flow's file comments show *order.py:L12-L14* as processed
*And* the comment marker beside line 12 shows the comment as processed
*And* the [Files app](../../../../../space/session/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) can Show Changed File After Comment

#### Scenario: Keep a comment sent while the chat still works on it

*Given* checkout-flow's [file comment](../../../../../space/session/files_app/.context/files-app-model.md#filecommentsactions-filesfile-comments-actionsts) *order.py:L12-L14* is sent, as a message to *checkout-chat*
*But* *checkout-chat*'s turn has not ended
*When* the Person views *order.py*
*Then* the comment marker beside line 12 shows the comment as sent

## Story: Show Changed File After Comment

#### Scenario: Show the agent's change to the open file

*Given* the [Files app](../../../../../space/session/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) shows *order.py* of checkout-flow, read-only
*And* the chat's turn changed line 14 of *order.py* to *raise EmptyCartError(cart.id, "a cart needs one item to be placed")*
*When* the [file comment](../../../../../space/session/files_app/.context/files-app-model.md#filecommentsactions-filesfile-comments-actionsts) *order.py:L12-L14* is marked processed
*Then* the source view shows line 14 as *raise EmptyCartError(cart.id, "a cart needs one item to be placed")*
*And* the comment marker still shows beside line 12, processed

## Story: Clear Processed File Comments

#### Scenario: Clear the processed comments, keeping the rest

*Given* checkout-flow's file comments hold *order.py:L12-L14* processed, *order.py:L30-L31* sent, and *order.py:L40-L41* not sent
*When* the Person clears checkout-flow's processed file comments
*Then* no comment marker shows beside line 12
*And* the markers beside lines 30 and 40 still show, sent and not sent

## Story: Show AI Changes As Diff

Intended in the Files app (`.sessions/_backlog/review-work-in-board-files.md`, "change viewer from ai change like vscode / cursor"); the session answers the changes (`SessionFile.changes`, `space/session/session_file.py`) and the board's files panel draws them. What counts as the chat's change is the difference between the file as it read when the comment was sent and the file once the comment is processed.

#### Scenario: Mark the line the chat changed, with the line it replaced

*Given* checkout-flow's [file comment](../../../../../space/session/files_app/.context/files-app-model.md#filecommentsactions-filesfile-comments-actionsts) *order.py:L12-L14* was sent while line 14 read *raise EmptyCartError(cart.id)*
*And* the chat's turn changed line 14 to *raise EmptyCartError(cart.id, "a cart needs one item to be placed")*
*When* the file comment *order.py:L12-L14* is marked processed
*Then* the source view marks line 14 as changed by the chat
*And* shows the line it replaced, *raise EmptyCartError(cart.id)*, as removed above it

#### Scenario: Mark the lines the chat added

*Given* checkout-flow's [file comment](../../../../../space/session/files_app/.context/files-app-model.md#filecommentsactions-filesfile-comments-actionsts) *order.py:L12-L14* was sent
*And* the chat's turn added two lines after line 14
*When* the file comment *order.py:L12-L14* is marked processed
*Then* the source view marks lines 15 and 16 as added by the chat
*But* marks no line before them as changed

#### Scenario: Mark nothing when the chat left the file as it was

*Given* checkout-flow's [file comment](../../../../../space/session/files_app/.context/files-app-model.md#filecommentsactions-filesfile-comments-actionsts) *order.py:L12-L14* was sent
*And* the chat's turn changed no line of *order.py*
*When* the file comment *order.py:L12-L14* is marked processed
*Then* the source view marks no line of *order.py* as changed

#### Scenario: Stop marking the changes once the processed comment is cleared

*Given* the source view marks line 14 of *order.py* as changed by the chat for the processed comment *order.py:L12-L14*
*When* the Person clears checkout-flow's processed file comments
*Then* the source view marks no line of *order.py* as changed
*And* line 14 still reads *raise EmptyCartError(cart.id, "a cart needs one item to be placed")*
