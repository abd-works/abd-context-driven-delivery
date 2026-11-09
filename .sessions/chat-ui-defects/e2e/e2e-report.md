# End-to-end test of the CDD apps after the chat UI defect fixes

Tester: independent e2e agent. Repository `C:\dev\abd-context-driven-delivery`, branch `main`, commit `fc39fd0ec`. Date 2026-11-07 (EST).
Expected behaviour came from the design canvas (`harness/design/project/*.dc.html`, `canvas.json` notes; the artifact read of `Fv63emedWtR8CoLL5QGevW` returned only the type instructions, so the local files were used), the board's scenarios under `space/kanban/.context/**/_story.test.md`, the harness scenarios `harness/.context/**/*_story.test.md`, `harness/.context/ux-context.md` and `harness/.context/thin-slice.md`.
Screenshots are in `screens/`; helper scripts are beside this report.

## 0. Setup, and two things found before any click

| Finding | Evidence | Impact |
|---|---|---|
| **The Session Board the user already has open on port 8778 runs stale code.** Process 73312 (`node --import tsx packages/session-board/serve.ts`) serves `assets/index-DTRkiZG0.js`, the build in the untracked leftover `harness/kanban/app/dist` dated Nov 6. The source moved to `space/kanban/app`, which had no `node_modules` and no `dist` at all. | `curl 127.0.0.1:8778/` shows `index-DTRkiZG0.js`; `harness/kanban/app/dist/assets/index-DTRkiZG0.js` dated Nov 6 14:02 | Anyone looking at the 8778 board sees the board from before the fixes (for example e502c9963, the out-of-date report notice). |
| **The cdd MCP server is not pinned to fc39fd0ec.** `~/.cdd/runtime.json` pins `d71e0b20`, a sibling of fc39fd0ec (both branch off `c3b62192`). | `git diff --stat fc39fd0ec d71e0b20` changes only `clean_engineering/model/drawio/drawio.py` and `installer_heavy_spec.py` | Nothing the board or chat bar uses differs, so the results below still apply to fc39fd0ec. |
| **The shared cdd server stalls again and again.** `/ping` went unanswered for 1 to 3 minutes several times (20:49, 20:51 to 20:53, 21:08 EST). Calls during a stall fail with `The cdd server is not connected: fetch failed` or `chat.list is still running after 10 seconds`. One `fidelity-progress.report` call took 68 s. | `~/.cdd/server.log` (ClientDisconnect tracebacks), ping loop output | Every app was slow and some calls failed while I tested. I retried after each stall. Failures caused only by a stall are marked as such below. |

To change nothing in the real repository, the board ran against a **sandbox git repository** (`<scratchpad>/board-sandbox`, with a bare `origin`). It holds copies of `.sessions/{chat-ui-defects, integrated-harness-flow, main, us-taxes, _complete, _backlog}`, `harness/.context` and `space/kanban/.context`, with workpaths rewritten to the sandbox. The board was built from `space/kanban/app` (`npm ci`, `vite build --outDir e2e/board-dist`) and served by `serve-board-sandbox.ts` on port 8790, with **Update disabled**.

**Every command the board sends to a chat was blocked in the page and recorded, never delivered.** The chat list holds the user's real Claude chats, so a fetch wrapper in the page refused `/api/chat/*/send|resend|remove|confirm|finish|check-in`, `/api/claude/open` and `/api/update`. The page shows "E2E: blocked, not sent" when it refuses one. Each "sent" text below is the payload the board would have sent.

## 1. Session Board (`space/kanban/app`): driven in the browser

Sources for "expected": S = board scenario (`space/kanban/.context/...`), M = the `space/kanban/.context/module-context.md` constraint, BP = `BoardPane.dc.html`, OC = `OptionC.dc.html` and the canvas "Try it" notes.

| Control | Action | Expected (source) | Observed | Result |
|---|---|---|---|---|
| Board load | Open page | Board shows Backlog, Discovery, Specification, Implementation, Complete with tickets (S Display Board) | 4 tickets, 9 backlog items, WIP 1/3; the `integrated-harness-flow` ticket loaded although its report predates graph shape 2 (screens/01) | Pass |
| Chat picker (list box) | Leave alone | Target is the chat the person picked, else the first connected one (code comment in `chat-client.tsx`) | With nothing picked, the selection jumped by itself between "Draw.io rendering", "board-desktop", "PSEA", "Ensure domain refactoring", "Harness installation" and "Digital-gov" as their recency changed | **Fail** (see defect B1) |
| Chat picker | Pick "PSEA" | The pick sticks | Stuck after 12 s and several board reads | Pass |
| Active session only (switch) | Off, then on | When on, only the active ticket's buttons work (S Restrict Actions To Active Session) | On with nothing active: ▷ ⇥ ⏻ and Run dimmed. Off: enabled | Pass |
| Messages (button) | Press | Shows what was sent to the chosen chat | "Nothing sent to this chat yet" (correct, since every send was blocked) | Pass |
| + Ticket (button) | Press | Ticket created from the board | Fills the chat prompt with `Open a new ticket with ticket.create, titled: ` (blocked); no form on the board | Pass with note: no scenario asks for a form. Canvas BoardPane has none either. |
| Update (button) | Not pressed | Pulls, rebuilds, pins cdd | Disabled in the sandbox on purpose (it pulls main and repins the shared server) | Not tested |
| Expand board / Collapse (⤢) | Press twice | Board fills the window, then returns (S Arrange Board And Details) | Works | Pass |
| Drag handle between board and details | Not dragged | Resize (S Arrange Board And Details) | Not exercised | Not tested |
| Backlog + (button) | Press, type title and text, Add | Form, item added (S Add Backlog Item) | Form with Title/Text/Add/Cancel; `backlog-item.create`; toast "E2E sandbox item added to Backlog"; details show the item with Start (screens/12) | Pass |
| Backlog item (card) | Press | Details show the item | Shows title, file `.sessions/_backlog/e2e-sandbox-item.md`, Start | Pass |
| Backlog item checkbox | Not pressed | — | Not exercised | Not tested |
| Start (backlog item) | Press | Workpath dialog, then a ticket in Discovery (S Add Backlog Item, module-context) | "Where E2E sandbox item works" dialog with Up, harness/, space/; harness has "No folders inside"; Use harness → ticket in Discovery 2/3, then the "Roots of …" dialog with Change per practice and Done (screens/13) | Pass. The workpath dialog stayed open about 10 s after the ticket appeared. |
| WIP limit (Discovery 1/3) | Press, type 4, Enter | `stage.set_wip_limit` (S Set Stage WIP Limit) | `POST /stage/Discovery/set-wip-limit {"limit":4}`; header shows 2/4 | Pass |
| Ticket card (press, no chat yet) | Press the card | BP: "a press on a ticket makes it the active session". Code: opens the ticket's chat | Selects the ticket and runs `ticket.open_worktree`, which **creates a git worktree** beside the repo. Then it tries `claude://code/new?folder=…` to start a new chat (blocked). Toasts "Opening the chat of …" and "Confirm the folder and send in the Claude app". It does **not** make the ticket active. | Differs from canvas (planned, Inc 4 *Sync Chat Bar With Board Selection*). Note: the press has side effects (worktree, new chat). |
| Ticket ▾ (Actions for …) | Press | BP ▾ menu: Files · whole ticket, ▶ generate, fix, UX design ↗, per-practice Files | Expands the card into its practice tiles (story-map, bounded-context, ia, modules, behavior). None of the canvas menu items are there. | Differs from canvas (planned, Inc 4 and Inc 7) |
| Tile inside the expanded card | Press story-map | Opens the tile's action bar | Opens the action bar, **and** triggers the open-chat flow again (screens/11) | Pass with note |
| ▷ Run next (card) | Press | Sends the next action with `session=` and `format=` (S Send Next Fidelity Action) | Text `/actions-generate ddd-bounded-context format=markdown session=.sessions/integrated-harness-flow/session.json`, **sent to chat "Ensure domain refactoring (busy)"**, not the ticket's chat | Text Pass; target **Fail** (B1) |
| ⇥ Handoff (card) | Press | Asks the chat to write a handoff (S Write Ticket Handoff) | Fill `Write a handoff for ticket integrated-harness-flow with /space-session-handoff-session.` to chat "Draw.io rendering". No `session=`, wrong chat. | Partial: text has no session param; wrong target (B1) |
| ⏻ Activate (card, nothing active) | Press, Activate | Dialog, then the ticket is active with a thick orange outline (S Activate Ticket) | First try: `ticket.branch` hung for 2 min during a server stall, with no feedback. Retry: dialog "Activate integrated harness flow" with OPEN only (branch and worktree already exist, both disabled). Activate → orange outline, status line "integrated-harness-flow · Discovery · violations: stories-scenarios", ⏻ becomes ✕ (screens/04, 05) | Pass. Note: sent `leaving:["handoff"]` with nothing to leave; a later activation from nothing toasted ": handoff written · … is now active" with an empty name (B5). |
| ⏻ Activate (another ticket active) | Press on E2E sandbox item | Switch dialog with LEAVE (Create handoff on by default, commit, push; merge off) and OPEN (S Activate Ticket, defect 8) | "Switch from integrated harness flow to E2E sandbox item": Create handoff ☑, Commit changes on main ☑, Push main to origin ☑, **"Merge main into main" ☐**, Create branch ☑, Create worktree ☐ (screens/14) | Checkboxes Pass. "Merge main into main" **Fail** (B3) |
| Dialog checkboxes | Press the box and the label | Each toggles (defect 2) | Box and label both toggle; state read back from the DOM matched (screens/15) | Pass |
| Switch → Activate | Confirm | Leaves with handoff, commit, push; opens with branch | `activate {"leaving":["commit","push","handoff"],"opening":["branch"]}`; toast "integrated harness flow: handoff written, committed, pushed · E2E sandbox item: branch created · E2E sandbox item is now active". Sandbox git shows commit `integrated-harness-flow: leave session` pushed to origin, the handoff file written, branch `e2e-sandbox-item` checked out (screens/16) | Pass |
| ✕ Close (active card) | Press | The chat is sent `/space:session:close-session` (S Close the active session from its card) | `/space:session:close-session` sent to chat "Draw.io rendering" (blocked), with no `session=` | Text Pass per scenario; target **Fail** (B1) |
| Drag card to Specification | HTML5 drag (synthesized in the page; a mouse drag in the pane does not fire HTML5 drag events) | `ticket.move_to` (S Move Ticket) | `move-to {"stage":"Specification","done":false}`; card moved to 2/3 | Pass |
| Drag active card to Complete | HTML5 drag | Dialog "Close session X" offering commit and push, chosen; then Complete, toast, no ticket active (S Complete the active ticket with its work committed) | Dialog: Create handoff ☑, Commit ☑, Push ☑, Merge ☐ (screens/19). Close session → Complete, "Latest handoff: .sessions/_complete/e2e-sandbox-item/handoff-…", active none (screens/21) | Pass, but see B4: the folder move to `_complete` is left uncommitted and the closed ticket's branch stays checked out |
| Drag a session-on-main ticket to Complete | HTML5 drag, then Cancel | Defect 7: offers commit and push of main; no merge, no worktree removal | Dialog for integrated-harness-flow said "branch **none yet**" although its branch exists (the activation dialog said "Branch integrated-harness-flow already exists"). It offered "Commit changes on integrated harness flow", "Push integrated harness flow to origin" and "Merge integrated harness flow into main", all off (screens/20). Cancel left the card in place. | **Fail** (B3). The case was muddied: the sandbox still had the closed ticket's branch checked out (B4), so "main" was not checked out here. |
| Cancel (dialog) | Press | Closes, nothing changes | Works | Pass |
| Split (◁) | Press | Split into child tickets (S Split Ticket Into Child Tickets) | Fill: `Split ticket e2e-sandbox-item into child tickets … ticket.create with parent e2e-sandbox-item for each story.` | Pass |
| Folder icon / files icon (card) | Press files | Files panel with tabs per declared file (S List Ticket Files, View Fidelity Files) | Panel "FILES_" with tabs story-map.md, story-map.drawio, bounded-context-map.md, ux-context.md, information-architecture…; text with line numbers (screens/08) | Pass |
| Files panel: drawio tab | Press | OC/Inspector: shows as its diagram (Inc 4 *Display Drawio File As Diagram*) | Raw XML on two very long lines (screens/09) | Differs from canvas (planned, Inc 4) |
| Files panel: folder/files toggle | Press folder | Folder tree (S Browse Ticket Folder) | `harness/` once, with 4 files (screens/10) | Pass |
| Files panel ×, expand | Press | Close, expand | Work | Pass |
| Tile (details grid) | Press story-map | Action bar: action list, format chips, Run, validate, review | Shown (screens/11) | Pass |
| Action list box | Read options | generate, render, sketch, iterate, document, fix (OC note 1) | generate, iterate, sketch, render, document. No fix (fix comes from the report). | Pass with note |
| Format chips (tile) | Toggle diagram, then Run | `format=` lists the chosen formats (S Choose Action And Formats) | `/actions-generate stories-story-map format=drawio,markdown session=.sessions/integrated-harness-flow/session.json` | Pass |
| Format chips after Run | Look | — | Both chips cleared and Run disabled | Planned (Inc 4 *Keep Chosen Formats Across Actions In A Fidelity*) |
| validate (tile) | Press | `/actions-validate …` (S Validate Fidelity) | `/actions-validate stories-story-map session=.sessions/integrated-harness-flow/session.json` | Pass |
| review (tile) | Press | `fidelity-progress.finish_review` (S Review Fidelity) | Called; ✓ shown | Pass |
| Stage ▾ (details, Discovery) | Press | Stage action bar (S Send Action To Stage Practices) | generate list, diagram "2 of 3", markdown "2 of 4", code chip, Run, validate (screens/17) | Pass |
| Stage Run | Press | Generates every enabled fidelity of the stage | `/actions-generate stories-story-map ddd-bounded-context ux-ia clean-engineering-modules bdd-behavior format=python session=.sessions/e2e-sandbox-item/session.json` | **Fail** (B6): the code chip is chosen by default, so a whole Discovery stage is asked for `format=python` |
| Practice switch (DDD off) | Press | `practice-session-output.enable false`; counts drop (S Choose Ticket Practices) | Called; chip counts went from "2 of 4" to "2 of 3" | Pass |
| Hide practices not enabled | Press | Hides disabled rows | Chevron turned; rows collapsed | Pass |
| Workpath / roots button | Press | Roots dialog (module-context) | "Roots of integrated harness flow" with Change and Done | Pass. Note: the details header names the project "context-driven-delivery" although the board project is `board-sandbox` (B9). |
| Help ? (tile) | Press | Help panel: overview, guidance, rules, Forge link (S Open Help) | Help for story-map with Forge, expand, close (screens/18) | Pass (Forge not pressed) |
| violations link (scenarios tile) | Press | Report opens in the side panel (S Open Validation Report) | Opened after about 60 s (server). VALIDATION REPORT, 4 violations, 4 rules hit (screens/06) | Pass |
| Report: out-of-date notice | Look | Old report opens and says it is out of date, offering Validate again (defect 10) | "This report's saved graph is out of date, so its graph's rules are not shown. Validate again to read them." plus a Validate again button | Pass |
| Report: Validate again | Press | `/actions-validate stories-scenarios session=…` | Exactly that | Pass |
| Report: Fix all violations / Fix all (rule) / Fix | Press each | Fix prompts naming the report, every format, and session | All three carry the report path, "Fix every format of the fidelity: its documents, its diagrams, and its code", and `session=` | Pass |
| Report: rule ▾ fold | Press | Folds the rule | Folds (› shown) (screens/07) | Pass |
| Report: expand / × | Press | Expand to full window, close | Work | Pass |
| cdd disconnected banner | Seen during a stall | Board says cdd is down (S Display Board Server Health) | Red banner plus a **full Python traceback** filling a third of the screen (screens/03) | Pass with note (B8: raw traceback). Inc 7 *Display Report Errors In Code Fences* and Inc 8 health stories are planned. |
| Complete ticket details | Look | — | A closed ticket still shows enabled-looking Run on its tiles | Note, not verified further |

## 2. Knowledge graph app (`harness/graph/app`): driven in the browser

Run: `server.ts` on 3010 with `GRAPH_PROJECT` set to the sandbox, Vite on 5183 (`graph-vite.config.mjs`, proxy to 3010). The sandbox path itself was too long for Windows: `load_working_copy` failed with FileNotFoundError on a path over 260 characters, which is an artifact of my sandbox location. I then loaded `C:\dev\abd-context-driven-delivery\space\kanban`; that writes only the git-ignored `space/kanban/.context/graph.json`.

| Control | Action | Expected (source) | Observed | Result |
|---|---|---|---|---|
| Repository folder field + Enter | Type path, Enter | Loads the working copy (Inc 0 *Load Working Copy Into Graph*) | "Loading the graph… · 0:09" timer, then the tree with stories, ddd, ux, clean_engineering, bdd (screens/23) | Pass |
| Load failure | Long sandbox path | Failure with Copy for AI (Inc 0 *Copy Load Failure For Agent*) | "Copy for AI" plus diagnosis text (screens/22) | Pass |
| Load progress | Watch | Load steps while loading (Inc 0 *Show Load Steps While Loading*) | Only the elapsed time; no steps listed | Partial |
| Repo folder (button) | Not pressed | Opens a native folder dialog on this machine | Not pressed: it opens an OS dialog outside the browser | Not tested |
| ▼ (recent folders) | Not pressed | Reopen last folder | Not exercised | Not tested |
| Practice tree ▶ | Expand stories, epic, sub-epic | Expand Practice Tree | Expanded to stories under Steer Ticket Sessions | Pass |
| Node (press) | Select epic, story, class Board, class Column | Source opens with the node's file and lines (Inc 0 *Open Node Source*; canvas KnowledgeGraph shows SOURCE and RULES ON THIS NODE) | Node highlighted; the source pane stays "Select a node". `graph/source` returned `null` (HTTP 200) for `clean_engineering:OoadClass:board.py:Board`. During a stall it returned 500 and the page threw an **uncaught** `GraphCallFailure`, with nothing on screen (screens/24) | **Fail** (B10) |
| Violations switch | On | Only violating nodes (Inc 0 *Show Only Violations*) | All five practices with no children, although `Board` was drawn red a moment earlier (screens/25) | **Fail** (B10) |
| Practice filter (list box) | Pick stories | Narrows node, connector and rule lists | Node → Epic, Story, SubEpic; connector → decomposedInto; rules → stories.* (screens/26) | Pass |
| Node / Connector / Rule lists, ALL / NONE | Seen updating | Filter choices | Updated with the practice filter; ALL/NONE not pressed one by one | Partial |
| Executive / Engineering | Press | Switch display theme | Light ↔ dark | Pass |
| Pattern overlay buttons, Add folder… | Not pressed | Add Named Overlay From Catalog | Not pressed: each rebuilds the graph on the shared server, which was stalling | Not tested |
| Force reload | Not pressed | — | Not pressed, for the same reason | Not tested |
| Graph state across apps | After board activations in the sandbox | Graph stays loaded | `graph/inventory` later reported `node_counts: {}` for every practice; the tree lost its children with no message. The sandbox session log shows the graph tools ran under the session the board had just activated. Likely cause (not proven): switching the open session on the shared server drops the loaded graph. | **Fail** (B10) |

## 3. Story UI (`C:\dev\story-ui`, a separate repository): driven in the browser

Run with its in-memory dev server (`packages/story-map-workspace/serve-dev.ts`, no MongoDB) on 3021 and Vite on 5193 (`storyui-vite.config.mjs`), so nothing reached the user's `story_map` database. It shows the seeded "default" map, not a session's story map.

| Control | Action | Expected (source: harness/.context/story-map.md Author Story Maps; canvas StoryUiEditor) | Observed | Result |
|---|---|---|---|---|
| Load | Open | Map of epics, sub-epics and stories; status "synced" | Two epics, two sub-epics, two stories; "synced" (screens/27) | Pass |
| Show Scenarios / Show Examples | Press | Show the scenario and example areas | Toggled; SCENARIOS rows appeared | Pass |
| Expand All / Collapse All | Press | All cards open or closed | Work | Pass |
| ▼/▲ on a story | Press | Expand one card | Works | Pass |
| SCENARIOS + | Press | Add scenario | "New Scenario" with STEPS + and EXAMPLES + | Pass |
| STEPS + | Press | Add step with keyword list | "GIVEN ▾ New step" (screens/28) | Pass |
| EXAMPLES + | Press | Add example with fields and rows | "NEW EXAMPLE", field…, + Row | Pass |
| Scenario − | Press | Remove scenario | Removed (no confirmation) | Pass |
| Increment View / Map View | Press | Increment lanes; an Unassigned lane | "UNASSIGNED — DROP HERE TO REMOVE FROM INCREMENT" (screens/29) | Pass |
| Rename inline (double-click) | Rename a story | Rename Node Inline | Renamed; "synced" | Pass |
| Story + | Press, type title, Enter | Add story at chosen position | "E2E Added Story" added after it (screens/30) | Pass |
| Story − | Press | Remove story | Removed | Pass |
| Executive / Engineering | Press | Switch colour mode | Works | Pass |
| Drag / reorder, add increment, ↕ on epics | Not done | — | Not exercised (HTML5 drag needs synthesized events; time) | Not tested |
| Canvas items: session header, "Save to session", "+ Epic", opened from the board | Look | StoryUiEditor.dc.html | None of these exist; the app edits its own Mongo or in-memory map | Differs from canvas (planned, Inc 2 *Open Story UI On Ticket Scope*, *Deploy Story UI App With Board State*; Inc 5) |

## 4. Chat bar and chat band (`harness/chat-ui/pane`): verified by test and reading, not clicked

- `claude plugin validate harness/chat-ui/pane` (run with the desktop app's `claude.exe`; `claude` is not on the Bash PATH): **passed with warnings**. Warnings: no author; no LICENSE (the plugin directory would refuse a submission); no icon; gating hooks `tool.call`, `prompt.submit` and `ui.close` have no `.catch` (`plugin-validate.txt`).
- `claude plugin test harness/chat-ui/pane`: **69 pass, 0 fail**, 21 files (`plugin-test.txt`).

| # | Defect | Status | Evidence |
|---|---|---|---|
| 1 | Every chat bar action carries `session=` and `format=` | **Fixed** (verified by test and reading, not clicked) | `fidelity-progress-client.ts` `actionCommand` is the one builder: `/actions-{action} {slug}[ format={defaultFormat}] session={sessionFile}`. Tests: Invoke Next Fidelity Action (validate and generate carry both), Choose Fidelity Action (iterate), Write Session Handoff (`session=`). Caveat: `format=` is left out when a fidelity has no default format. On the **board**, Handoff, Split, + Ticket and ✕ Close send no `session=` (observed). |
| 2 | Session switch dialog checkboxes not clickable | **Fixed** | Chat bar: each choice is a `Button` that toggles it (`session-dialogs-view.tsx` `ChoiceView`); tests "Choose what switching does" and "Choose what closing does" pass. Board: clicked the box and the label in both dialogs, and both toggled (screens/15). |
| 3 | Files button or folder reads files into the chat | **Fixed**, with a note | `fidelity-files-client.ts` opens pane `cdd-files` with `$.ui.open` and reads text with `session.read_file`; diagrams are never read. Test "Open the files beside the chat, never in it" passes. Note: the diagram tab's "Open in draw.io" still does `$.prompt.submit` of `Open <path> in the draw.io viewer.` as the user. That is a chat message, though not file contents. |
| 4 | Discovery folder list shows harness five times | **Fixed** | `chatBar.foldersListedBeside` lists a folder only beside its first fidelity; test "List each folder once" passes. The board's folder view also listed `harness/` once. |
| 5 | Only the fidelity name is clickable on the FIDELITY line | **Fixed** (test only) | `FidelityRowView` lays an absolutely positioned `Button` over the whole row width (square, name and state); test "Pick a fidelity from anywhere on its line" passes. That the overlay takes the press in the real renderer was not checked by clicking. |
| 6 | Violation report opens in the chat | **Fixed** | `openReport` puts the report in the files pane; test "Read the violations from their count" passes. |
| 7 | Closing a session on main should commit and push main, not delete a worktree | **Fixed for close; a related fault remains in switch** | `CloseView` offers handoff plus commit and push of the checked-out branch, never merge or worktree; Python `Ticket.leave` skips merge on the default branch. Tests "Close a session whose work is on main" (chat bar) and `close_active_session_story.test.py` pass. But the **switch** dialogs still offer merge when the work is on main: the board's says "Merge main into main" (screens/14), and the chat bar's `ActivateView` always lists `merge`. The board's close dialog also said "branch none yet" for a ticket whose branch exists (screens/20). |
| 8 | Close and switch dialogs need Create handoff, on by default | **Fixed** | Chat bar `FIRST_LEAVING = ['handoff','commit','push']`, and close has `HANDOFF_ONLY` or more; tests pass. Board: both dialogs showed Create handoff ☑; a confirmed switch wrote `handoff-20261108T020313.md` for the session left. |
| 9 | ▶ and ▾ disappear with the story map fidelity picked | **Fixed** (test and reading) | `actionOf` falls back to the stage's first action when the fidelity has no next action; test "Keep the action button on a done fidelity" passes. |
| 10 | SavedGraphOutdated breaks the session list | **Fixed** on the server and the board; **not verifiable** in the chat bar | `report.py` now reports `is_out_of_date` instead of raising; direct call returned `has_saved_graph: true, is_out_of_date: true, violation_count: 4` for `stories-scenarios-20261107T001054`. `board.show` loaded with that report present. The board shows the notice and Validate again (screens/06). Python "Say a report's saved graph is out of date" and "Read the board with an out-of-date report" pass. No chat bar test covers it, and the chat bar's report tab shows `report.text` only, with no out-of-date notice. |

Chat band against `ChatBand.dc.html` and OptionC (reading `chat-bar-view.tsx` and related files):

| Canvas element | Chat bar today | Classification |
|---|---|---|
| Toast line | Toasts through `$.ui.toast` | Present |
| Health ✓ mark | Present (health tests) | Present |
| Session name ▾ list, each with its stage | Present (`SessionListView`), plus a "New session name" field | Present |
| Practice squares that pick which practices the next action runs on | Fidelity dots per stage fidelity; pressing one selects that fidelity only | Planned (Inc 9 *Choose Session Practices*; Inc 4) |
| ▶ ▾ action with tooltip | Present (`ActionButtonView`, `PickerView`) | Present |
| Format chips (diagram, markdown, code) | None; the default format is used | Planned (Inc 6 *Choose Format*) |
| View icons that open and close the board, story map, explorer, graph and Inspector beside the chat | None | Planned (Inc 2 *Open Story UI Side Panel From Chat Bar*; Inc 4 *Open Board Side Panel From Chat Bar*) |

## 5. Python story tests

Run with `--format progress`. With `--format documentation` the same runs printed only 166 and 13 examples and no failure list, so those counts are not reliable.

| Suite | Result |
|---|---|
| `space/kanban/*.story.domain.spec.py` + `*.story.server.spec.py` | **310 ran, 1 failed**: "Validate Fidelity (domain) › Count Validate done only with no graph-rule violations › the story_map tile marks Validate as violations again". Expected `('in_progress','violations')`, got `('done','in_progress')`. It fails the same way twice in a row, and also in the `chat-ui-defects-cef4bc` worktree at d1294624c, so it predates the merge into main. It is **not** one of the 7. |
| `space/kanban/kanban_tools_spec.py` | **161 ran, 7 failed. These are the same 7 judged-report findings as before:** list each rule the judgment fails after the graph's rules; count each finding of a judged rule; not read passing rules as findings; give a judged finding its file and line; show source lines around a judged finding; a finding with no line gives its message; and (sign-up) count each finding of the judgment (`{}` instead of `{"stories-story-map": 5}`). |
| `space/kanban/kanban_spec.py` (extra) | 70 ran, 0 failed |

Outputs: `py-story-tests-progress.txt`, `py-kanban-tools-progress.txt` (and the documentation-format `py-story-tests.txt` and `py-kanban-tools.txt`).

## 6. Defects found that are not planned increments

- **B1 Board commands go to the wrong chat.** With no chat picked, the target is `chats[0]`, which reorders by recency. Run next for integrated-harness-flow was addressed to "Ensure domain refactoring (busy)". Handoff, close-session and the report's fix prompts went to "Draw.io rendering", none of them that ticket's chat. A press of ✕ would ask an unrelated chat to close whatever session it has open.
- **B2 The 8778 board is stale.** See §0.
- **B3 Switch dialogs offer "Merge main into main"** (board), and the chat bar's switch always offers merge. The board's close dialog showed "branch none yet" for a ticket whose branch exists in a worktree, and labelled the choices with the ticket title instead of a branch name.
- **B4 Close leaves the repository half done.** The close commit is made before the session folder moves to `.sessions/_complete/`, so the move stays uncommitted (`D .sessions/e2e-sandbox-item/*`, `?? .sessions/_complete/e2e-sandbox-item/`). The closed ticket's branch stays checked out, and the next activation then records `{"branch": "e2e-sandbox-item", "session": "integrated-harness-flow"}`.
- **B5 Activating with nothing active** sends `leaving:["handoff"]` and toasts ": handoff written · …" with an empty session name. No handoff file was written.
- **B6 Stage Run defaults to format=python** for the whole Discovery stage.
- **B7 Pressing a ticket card has side effects.** It creates a git worktree and starts a new Claude chat when the ticket has none, including when the press lands on a tile.
- **B8 Server-down banner dumps a raw Python traceback** across the top of the board.
- **B9 The details header shows "context-driven-delivery"** for the board-sandbox project.
- **B10 Graph app.** Node source never appears (`graph.source` returns null for loaded nodes, and a failed call becomes an uncaught promise with nothing on screen). The Violations switch shows nothing. The loaded graph silently empties after a session switch made from another app on the same cdd server.
- **B11 The shared cdd server stalls** for minutes at a time (§0). Board calls such as `ticket.branch` then hang with no feedback (Activate showed nothing for 2 minutes).
- **Python:** the Validate Fidelity domain failure in §5.

## 7. Where the running apps differ from the design canvas (planned increments)

| Canvas shows | Running app | Increment (thin-slice.md) |
|---|---|---|
| Chat is home, with up to four views beside it, layout ▾ and ◀▶▲▼ view arrows; a fifth view closes the oldest (OptionC) | Board, graph app and Story UI are separate pages | Inc 4 Fully Integrated App Flow |
| A press on a board ticket makes it the active session in every view (BoardPane, OC note 3) | The press selects the ticket and opens its chat; activation needs ⏻ and a dialog | Inc 4 *Sync Chat Bar With Board Selection* |
| Ticket ▾ menu: Files whole ticket and per practice, ▶ generate, fix, UX design ↗ (BoardPane) | ▾ expands the card into its tiles | Inc 4 *Fix Graph Violations From Board*, *Open UX Design In Claude Design*; Inc 7 |
| Inspector: file tabs, folding headings, violation cards grouped by rule, Show violations switch, drawio as a diagram with the violating shape red (InspectorPane) | Board files panel: plain text tabs, drawio as raw XML; violations live only in the separate report panel | Inc 4 *Display Drawio File As Diagram*; Inc 7 *View Files In Rich Viewer* |
| Generate reloads the graph, and violations appear on band, tiles, story map and Inspector at once (OC note 1) | Violations come from saved validation reports | Inc 4 *Refresh Graph After Generate*, *Read Fidelity Violations From Latest Graph* |
| Story map pane with screen frames that open the story explorer (StoryMapPane, StoryExplorerPane) | Not present; the story explorer exists only as the Claude Design canvas `HCCiMNSTMhwB9zQT8tVV8p` (local copy `.sessions/integrated-harness-flow/design-canvas/version-1/`) | Inc 4 *Switch Story Map To Screen Frames View*, *Open Story Explorer From Screen Frame*, etc. |
| Knowledge Graph pane scoped to the ticket; "opened on the session's files" (KnowledgeGraphPane, KnowledgeGraph) | Graph app opens on a typed folder | Inc 2 *Filter Knowledge Graph To Ticket Scope*, *Deploy Knowledge Graph App With Board State* |
| Story UI opened from the board with session header and "Save to session" (StoryUiEditor) | Story UI edits its own Mongo or in-memory map | Inc 2 *Open Story UI On Ticket Scope*; Inc 5 |
| Chat band practice squares, format chips, view icons | See §4 | Inc 9, Inc 6, Inc 2 and Inc 4 |
| Formats stay chosen across actions | Chips cleared after Run | Inc 4 *Keep Chosen Formats Across Actions In A Fidelity* |

## 8. What I could not test, and why

- **The chat bar and chat band were not clicked.** They run inside the Claude desktop app. They are verified by the plugin's tests and by reading the code.
- **Delivery of any board command to a chat was not tested.** Every send was blocked on purpose, because the chat list holds the user's real chats. Payloads were recorded.
- **Update was not pressed:** it pulls main and repins the shared cdd server. **Forge** was not pressed: it opens an external page.
- **Graph app:** Repo folder (native OS dialog), overlays and Force reload (each rebuilds on a stalling shared server) were not pressed, and ALL/NONE were not pressed one by one.
- **Story UI:** drag and reorder, increment add, and ↕ were not exercised. It ran on the in-memory server, not MongoDB.
- **Board:** the resize handle and the backlog item checkbox were not exercised. Drags were synthesized HTML5 events, not real pointer drags.
- **Defect 7 on a clean "on main" case** was not reached on the board: after the sandbox close, the closed ticket's branch stayed checked out (B4).
- **Timing:** many results were slowed and some calls failed while the shared cdd server stalled (§0). Results marked Fail were rechecked after the server answered `/ping` again.
- **Story explorer:** read from the canvas only. There is no runnable explorer app in the repository yet.

## Files written for this test

`e2e/serve-board-sandbox.ts`, `start-board.sh`, `start-graph.sh`, `graph-vite.config.mjs`, `start-storyui.sh`, `storyui-vite.config.mjs`, `board-dist/` (board build), `screens/` (30 screenshots), test outputs (`py-*.txt`, `plugin-*.txt`, `report-stories-scenarios.json`, `board-show.json`). Outside the e2e folder: `.claude/launch.json` (three e2e launch entries; `.claude/` is git-ignored), `space/kanban/app/node_modules` (git-ignored), `space/kanban/.context/graph.json` (git-ignored, written by the graph load), and the sandbox repo, its origin and the `board-s-integrated-harness-flow` worktree in the scratchpad. Nothing was committed and nothing was deleted. All three servers I started are stopped. The user's own processes on 8778, 3000, 5173 and 47800 were left running.
