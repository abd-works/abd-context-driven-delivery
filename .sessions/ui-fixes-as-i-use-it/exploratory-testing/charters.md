# Charters — ui-fixes-as-i-use-it hardening

Supervisor: Bolt (chat 82179ef0-da0c-4b49-a11d-f0d46aafce7e). Build under test: branch `ui-fixes-as-i-use-it` at 222d97cb5, worktree `C:\dev\abd-cdd-ui-fixes-as-i-use-it`. Defect area: `C:\dev\abd-cdd-ui-fixes-as-i-use-it\.sessions\ui-fixes-as-i-use-it\exploratory-testing\defects\`. Themes and their evidence: `coverage-themes.md` beside this file.

## Rules every charter shares

- **Sandbox and home.** Work only in your sandbox folder. Set `CDD_HOME` to your own throwaway home, `PYTHONUTF8=1`, `PYTHONIOENCODING=utf-8`, and unset `CLAUDE_CODE_SESSION_ID` and `CDD_CHAT_ID` in every shell. Build your throwaway project inside the sandbox (copy the fixtures you need there; `git init` it with no remote).
- **Python.** `C:\dev\abd-context-driven-delivery\.venv\Scripts\python.exe`, run with the working directory `C:\dev\abd-cdd-ui-fixes-as-i-use-it` so the branch's code is imported (or add it first on `PYTHONPATH`). Specs run with `python -m mamba.cli`.
- **Ports.** Only your own. Never touch the person's servers: the cdd server under `~/.cdd`, the draw.io viewer on 8791, the Files app or board the person has open.
- **Out of bounds.** Never write anything under `C:\dev\paradise-mobile\pml-web` (read-only copies under `test-area/pml-web` may be copied into your sandbox). Never publish a board, canvas or artifact to claude.ai or Miro: render unpublished only. Never repin, `--pin-runtime`, install, or restart a server that is not your own. Never send a message to a real chat. Never commit, push, stash or change a file in the worktree outside your sandbox and the defect area. The one write you make outside them is a `[defect]` card on the supervisor's queue (`prompt-queue.add`, chat `82179ef0-da0c-4b49-a11d-f0d46aafce7e`).
- **Report.** Defects as found (one file each in the defect area, then the `[defect]` card). Notes in `notes.md` in your sandbox. At the end, write `report-<robot>.md` in the exploratory-testing folder: what you tested, the defects found, what is still at risk; then answer the supervisor.

## C1 — Pip: chat bar format chips and board sends (theme T1)

Explore the chat bar's format chips and board sends **as a person filtering a session's files by format and sending a board to the chat**, **with a throwaway project that holds a story map in markdown, draw.io and whiteboard formats, a class model in markdown and Python, and a design canvas folder**, **to discover** a chip whose toggle answers with the wrong selection or a stale file list, two toggles racing, a format chosen on a practice the session has turned off, and a board send that is queued or delivered twice.

- Sandbox: `C:\Users\jeffa\AppData\Local\Temp\claude\3f45b772a4732658\82179ef0-da0c-4b49-a11d-f0d46aafce7e\scratchpad\et\chips\sandbox`; `CDD_HOME` `...\et\chips\cdd-home`. Ports 18740-18744.
- What can run for real: the Python the chips call (`session.toggle_guidance`, `ticket.choose_formats`, `session.folder_files` / `session.workpath_files` filtered by format, `fidelity-session-output.choose_format`), and the board-send path's Python and TypeScript logic (`harness/chat-ui/pane/hooks/board-chat/chat-turns.ts`, `render.record_board`) read and, where it runs under node/tsx, run. `claude plugin test` cannot run here (no `claude` CLI): say so in your report and do not count the mod surface as tested.
- Promised in: `story_tests/move-work-forward-from-chat-bar/*`, `story_tests/connect-sessions-across-channels-and-apps/*`, `.sessions/_backlog/chat-ui-defects.md` (chips, filter busy, board send entries).

## C2 — Rivet: queue band — robot rows, themes, + then send, send to another chat (theme T2)

Explore the prompt queue's robot rows, robot themes, + then send, and send to another chat **as a lead handing cards to robots and then to another chat**, **with a throwaway `CDD_HOME` holding two or three fake chats' queues (create them through the queue's own tools with made-up chat ids) and cards done and not done, with steps and attachments**, **to discover** cards lost, duplicated or left behind when sent to another chat (refusals, a chat not connected, the same card twice, a card sent while it is the running one), a theme set on one spelling of a robot and shown on another, and + on an empty prompt box taking a message it should not.

- Sandbox: `...\scratchpad\et\queue\sandbox`; `CDD_HOME` `...\et\queue\cdd-home`. Ports 18745-18749.
- What can run for real: `tools/prompt_queue/prompt_queue.py` (`PromptQueue`, `send_to_chat`, `set_theme`, `set_steps`, `assign`, `split`) through Python in your home, and the server tools against a cdd server you start yourself on your ports with your `CDD_HOME`, if one can be started that way (see `harness/mcp` and `scripts/`). The band's TypeScript (`tools/prompt_queue/hooks/queue/*.ts`) may be read and its pure functions run under tsx; `claude plugin test` cannot run here.
- Promised in: `story_tests/queue-prompts-for-later/*`, `.sessions/_backlog/chat-ui-defects.md` (queue band entries).
- Never call the queue tools on chat `82179ef0-da0c-4b49-a11d-f0d46aafce7e` or any real chat id except to add your `[defect]` cards.

## C3 — Gizmo: Files app right-click menu and All files (theme T3)

Explore the Files app's file menu (delete after confirming, validate, show violations, add to a practice) and its All files scope **as a person tidying a session's files**, **with a throwaway git project holding a session with two practices, a `.gitignore`d folder, a nested folder added as a root of a practice, a file outside every root, a symlink, and file names with spaces and non-ASCII letters**, **to discover** a delete that reaches outside the session's roots or removes a root, its record or `.git`; All files listing an ignored file, a file twice, or nothing; add-to-practice on a file already a root; and a menu action whose answer leaves the list stale.

- Sandbox: `...\scratchpad\et\files\sandbox`; `CDD_HOME` `...\et\files\cdd-home`. Ports 18750-18754: start the Files server as the e2e does (`npx tsx harness/files_app/app/spec-files-server.ts <built page folder> <port> <project> [draw.io port]`, see `story_tests/review-generated-work-in-file-viewer/files_app_browser.py`) and drive it with Playwright from Python.
- Promised in: `story_tests/review-generated-work-in-file-viewer/act-on-files-from-file-menu`, `filter-files-in-files-app`, `harness/files_app/.context/`.

## C4 — Widget: diagrams, story explorer and the scenario reader (theme T4)

Explore draw.io and whiteboard links and arrows, the story explorer's class cards and realizations, the scenario reader and the class-card language **as a person rendering a project's story map, class model and story canvas and following every link**, **with a throwaway copy of `test-area/pml-web` (read only at its source) plus a small project of your own whose stories are in each layout: one story per file, a sub-epic file holding several stories, markdown beside a Python story test, markdown beside a TypeScript story test, code only, and a scenario name that differs between markdown and code**, **to discover** links that do not resolve (a file in a sub-folder, a heading with punctuation or non-ASCII, a file renamed after render), arrows that overlap or double on a bigger model, class-card language that loses paragraphs or bullets in a round trip (markdown to drawio to markdown, Python doc comment), explorer cards or realizations missing for a step, and scenarios dropped, duplicated or taken from the wrong side when markdown and code disagree.

- Sandbox: `...\scratchpad\et\diagrams\sandbox`; `CDD_HOME` `...\et\diagrams\cdd-home`. Ports 18755-18759 (your own draw.io viewer, `tools/drawio_viewer`, if you open one).
- What can run for real: render to drawio, whiteboard (unpublished: the saved board file only) and markdown through the practices' render (see `cdd_guidance/actions/render/` and its specs for how to call it outside the server), the story canvas render (`cdd_guidance/practices/ux/model/claude_design/`), the graph build and validate on your project.
- Promised in: `story_tests/draw-practice-models-on-claude-whiteboard`, `story_tests/explore-stories-in-story-ui/*`, `story_tests/map-work-into-knowledge-graph/*`, `cdd_guidance/practices/clean_engineering/clean_engineering.md` (model fidelity: class card language).
