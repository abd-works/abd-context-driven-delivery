# Judgment: harness applications and tools

Scope: `harness/diagnostics`, `harness/chat`, `harness/chat-ui`, `harness/catalog_generator`, `harness/design_canvas`, `harness/whiteboard`, `harness/e2e_review`, `harness/files_app`, and `tools/` (prompt_queue, prompt_notify, prompt_log, error_display, granola, drawio_viewer, sub_agent, echo). Judged against the Clean Engineering modules, model and code rules, the refactor guardrails, and, for the two Claude Code mods, the `cdd_claude_mod` pattern's own rules. Read only: nothing was changed.

How to read it. Each finding names the file and line it was checked at. Tags: **[1]** module boundaries, **[2]** the same work done in different shapes, **[3]** resource orientation, **[4]** domain orientation. A caller count such as "no production caller" was checked with `git grep` over `*.py`, `*.ts`, `*.tsx`, leaving out specs, story tests and `.sessions`.

Two things the rules do not ask for, and which are therefore not findings:

- The mods (`harness/chat-ui/pane`, `tools/prompt_queue/hooks`) write each action as a plain function taking `$` first. The `cdd_claude_mod` pattern requires that (`actions-are-plain-functions`, `client-only-displays`), so a file of such functions is the mod's prescribed form, not a miss of `prefer-class-operations`.
- The diagnostics probes keep arguments and skips by each operation's published MCP name. Decision `harness/diagnostics/.context/cdr/0001` accepts that.

## Findings

### harness/chat/chat.py

- chat.py:281 `Chat.send` — seam-names-current-code — the docstring describes a `select` kind ("has its chat bar select the fidelities text names"); `CommandKind` (chat.py:50) has no `select`, and the chat bar refuses any kind it does not know (`harness/chat-ui/pane/hooks/chat-bar/check-in-client.ts:48-53`). A sender who follows the docstring gets a failed message. [4]
- chat.py:310 `Chat.show` — deep-module — no production code calls it: the only mention is a type member in `harness/chat-ui/pane/hooks/board-chat/board.ts:18` that nothing posts. It is one of the 27 seam methods. [1]
- chat.py:359 `Chat.title`, chat.py:374 `Chat.is_connected` — deep-module — read only inside this file (`ChatLinks._join_opener_section`, `Chats.list`, `ChatMailbox.queue`); both can be private. [1]
- chat.py:186 `ChatLinks.hand_over` — deep-module — public only because `space/repo/repos.py:79,92` builds the link with `link_to_new` and then hands it over itself, which is what `open_new` (chat.py:151) already does in one call. [1]
- chat.py:135-144 `ChatsFolder`, `CHATS_FOLDER` — single-boundary — `tools/prompt_queue/prompt_queue.py:150` builds `CHATS_FOLDER.path / chat / QUEUE_FILE` itself, so the layout of a chat's own folder is known in two modules. The chat should answer its folder. [1]
- chat.py:147-213 `ChatLinks`, `hand_over`, `links_of_run`, `Chats.opener` — abstraction-focus — the card calls this "the opener"; the class is named after its mechanism (a link), and the attribute that holds it is a public mutable field (chat.py:227). [4]
- chat.py:210 `links_of_run` — prefer-class-operations — a module-level factory that every caller calls afresh (`space/kanban/ticket.py:574`, `space/repo/repos.py:79,92`, `cdd_guidance/desktop_walk/desktop_walk.py:214`) instead of asking the roster that already holds the opener (`Chats.opener`). [3]
- chat.py:176-177 `ChatLinks._join_opener_section` — use-explicit-dependencies — reads the global `CALLS_BEING_ANSWERED.current` and loads the calling chat itself. `Chats.open` is the tool the call arrives at and can hand the opening chat in; a link built outside a call silently gets no "join this section" text. [3]
- chat.py:261-263 `Chat.clock`, `Chat.kept_messages` — use-explicit-dependencies — class-level values that specs replace on the class (`chat_spec.py:61,274`), so every chat in the process shares them. [3]
- chat.py:388-390 `ChatMailbox.__init__`, chat.py:497 `ChatStateFile.__init__` — hold-state-on-the-object-not-in-parameters — each is given the chat and, again, the folder or file that chat already holds. [3]
- chat.py:414-466 `ChatMailbox.confirm/finish/resend/finish_worked_on` — shape-classes-around-resources — a message's life (waiting, taken, shown, done, failed, its reason, whether it is worked on) is changed by the mailbox editing raw dicts; `ChatMessage` (chat.py:103) is a read-only view built afterwards. The states are also defined three times: five constants and a tuple (chat.py:35-40) and a `Literal` (chat.py:51). [3]
- chat.py:82, 317-344 `message: str`; chat.py:274 `load(chat: str)` — use-intention-revealing-names — `message` and `chat` hold ids, while `ChatMessage` and `Chat` are the objects; a reader cannot tell which a signature takes. [4]
- chat.py:266 `_folder` against chat.py:370 `folder` — use-consistent-naming — the first is the chat's own folder under the chats folder, the second the folder the chat works in. One word, two things, on one class. [4]
- chat.py:535-542 `ChatStateFile._while_windows_holds` — eliminate-duplication — repeats the retry `JsonFile` already does on a held file (`harness/installation/json_file.py:125-153`); `harness/diagnostics/test_runs.py:325-335` is a third copy. [2]
- chat.py:147-184 — do-not-invent-parallel-object-models — "a new chat on a folder with its first prompt" is modelled four times: as two strings here (`open_new(folder, prompt)`), as `NewChat` in `space/repo/repos.py:64`, as `Ticket.chat_link` in `space/kanban/ticket.py:565-574`, and as `TestChat` in `cdd_guidance/desktop_walk/desktop_walk.py:145`. Each writes its own first prompt and its own fallback. [2]

### harness/chat-ui/pane/hooks/board-chat/board.ts

- board.ts:13-21 `ChatRequest` — no-legacy-api-after-refactor — declares `select`, `show`, `show-stages` and `list-stages`; `chat.select`, `chat.show_stages` and `chat.list_stages` do not exist in `harness/chat/chat.py`, and nothing in the mod posts any of the four. [1]
- board.ts:45-47 `post` — state-change-returns-record-or-named-failure — always answers `ok: true`, so the `answer.ok ? … : []` branch in `chat-bar/check-in-client.ts:125` can never run; the result shape promises a refusal it never gives. [4]

### harness/chat-ui/pane/hooks/board-chat/chat-turns.ts

- chat-turns.ts:7-14 `isBusy`, `unfinished`, `turnsStarted`, `idleTicks`; chat-name.ts:8 `chatName`; chat-bar/check-in-client.ts:97 `failedCheckIns` — no-state-in-module-variables (the mod pattern) — what the chat is working on is kept in module variables, which a reload empties. The Python side already carries the workaround: `ChatMailbox.finish_worked_on` (`harness/chat/chat.py:457-466`) exists because "a mod that reloads mid-turn forgets it". [3]

### harness/chat-ui/pane/types/index.d.ts

- index.d.ts:16 `TestRunJson`, :23 `E2eReviewJson`, :27 `DesktopWalkQuestionJson` — contract-comes-from-the-adapter — hand copies of `TestRunData`, `E2eRunReviewData` and `DesktopWalkQuestionData`, which the adapter generates (`.claude/language-adapters/typescript/harness/diagnostics/server-health.ts:13-28`). The same file types the report itself as `object | null` and casts where it is read, which is the form that needs no copy. [2]
- index.d.ts:81 `RepoRowJson`, :86 `FormatChoiceJson`, :89 `OverlayChoiceJson` — contract-comes-from-the-adapter — field-by-field copies of what `repos.siblings`, `ticket.format_choices` and `ticket.overlay_choices` answer. [2]

### harness/chat-ui/pane/hooks/chat-bar/chat-bar-client.ts

- chat-bar-client.ts:28 `ChatBarClient` — client-mirrors-python-domain — mirrors no Python class: it joins the board overview, the active ticket and the guidance selection, and decides things the header comment says live in Python: which stages show (77-92), whether a practice is on (137-140), and "what every action runs on" (145-149, none selected meaning all). The agent's own tools cannot see those answers. [1]
- chat-bar-client.ts:58 `sessionName` and :117 `ticketName`; :145 `fidelities` and :193 `actionFidelities`; fidelity-progress-client.ts:136 `practice` and :141 `key` — use-consistent-naming — each pair returns the same value under two names. [4]
- chat-bar-client.ts:123, :128 — contract-comes-from-the-adapter — casts that add `session_path` and `actions_with_formats` by hand; the generated types already carry both (`.claude/language-adapters/typescript/space/kanban/ticket.ts:78`, `board.ts:99`). [2]
- chat-bar-client.ts:169 `formatChoices` — eliminate-duplication — writes its return shape out again; it is `FormatChoiceJson`. [2]

### harness/chat-ui/pane/hooks/chat-bar/fidelity-progress-client.ts

- fidelity-progress-client.ts:175-180 `commandOn` — hold-state-on-the-object-not-in-parameters — builds the command for several fidelities by replacing the first fidelity's slug inside the command string Python gave for one. State is written into a string and edited back; a change to how `FidelityProgress` words a command breaks it without a failing type. [3]
- fidelity-progress-client.ts:129 `STATES_BY_PROGRESS` — domain-lives-in-python — the order "violations count as less done than work under way" is a rule about progress, decided in the mod. [1]

### harness/chat-ui/pane/hooks/chat-bar/guidance-client.ts

- guidance-client.ts:51-55 `startStage` — domain-lives-in-python — "before any stage was selected, select the stage the ticket is in" is applied by the chat bar. The Files app follows the same selection and does not apply it (`harness/files_app/app/files/guidance-selector.ts:61-71`), so what a session's first selection is depends on which of the two read it first. [1]
- guidance-client.ts:75-100 `toggle`, `flipped`, `accept` — eliminate-duplication — the same press (draw the flip at once, send the whole selected list, ignore an older answer by version) is written again in `harness/files_app/app/files/guidance-selector.ts:37-59,73-88`. Both exist because `session.update_guidance_selection` takes whole lists, so each caller works out the new list. [2]

### harness/chat-ui/pane/hooks/chat-bar/bar-columns.ts

- bar-columns.ts:9-10 `FORMAT_GLYPHS`, `formatGlyphOf` — eliminate-duplication — copied in `harness/files_app/app/files/format-chips.ts:3-5`, whose comment says the two must look the same; the fallbacks already differ (first and last letter here, the whole label there). [2]

### harness/chat-ui/pane/hooks/shared/debug-command.ts

- debug-command.ts:3 `debugCommandOf` — eliminate-duplication — the fix command (`/space-session-debug-session choice=fix details=…`) is put together here, again in `error-display/failure-client.ts` (`FailureClient.fixPrompt`, class at line 25), and in Python (`tools/error_display/failure.py:20,184-185`). The card explains why the mod cannot ask Python while the server is down; the three still have to be changed together. [2]

### harness/whiteboard/whiteboard.py

- whiteboard.py:67 `BoardElement.record`, :98 `from_record`, :117 `whole_id`, :121 `pieces`, :125 `joined`, :130 `place`; :318 `Whiteboard.order`, :385 `meta`, :423 `writes` — deep-module — none is read outside this file (`writes` only through `batches`, whiteboard.py:436). Nine of the 36 seam methods. [1]
- whiteboard.py:308 `Whiteboard.versions` — hide-inner-details — a public mutable dict that only this file and its spec write (`whiteboard_spec.py:132,162`). [1]
- whiteboard/__init__.py:4 — low-coupling — the package exports five names, but callers reach past it for `MAX_SIDE` and `UnreadableBoard` (`cdd_guidance/practices/clean_engineering/model/whiteboard/whiteboard_class_model.py:22`, `model/code_read.py:15`) and for `Box` (`cdd_guidance/practices/stories/model/miro/nodes.py:14`). [1]
- whiteboard.py:332-347 `sections`, `shapes`, `labels`, `arrows` — use-typed-signatures — each answers `List[BoardElement]`, but every caller reads members only the kind has: `.box` (`stories/model/whiteboard/nodes.py:161`), `.from_id` and `.to_id` (`whiteboard_class_model.py:627`). The card hides the kinds; the callers depend on them anyway, untyped. [4]
- whiteboard.py:388 `Whiteboard.save` — use-intention-revealing-names — answers the board's text and writes nothing; its pair is `from_text` (whiteboard.py:397). [4]
- whiteboard.py:112 `BoardElement.role` — hide-inner-details — an element answers the first part of its id but not the rest, so each practice splits ids itself (`whiteboard_class_model.py:592,606`; `stories/model/whiteboard/nodes.py:235`; `ux/model/whiteboard/nodes.py:155`) and each hashes a node's key itself with its own length: `KEY_LENGTH = 10` (`stories/…/nodes.py:30,38-44`, `ux/…/nodes.py:30,70-76`) and `12` (`whiteboard_class_model.py:47,79-80`). The card says the id "names the kind of practice node and a stable key of that node"; the module that owns that rule does not write it. [2]
- whiteboard.py:414 `keep_places` — eliminate-duplication — every practice's `render` repeats "draw, then `keep_places(Whiteboard.from_text(previous))`, then `save()`" (`stories/…/nodes.py:120-125`, `whiteboard_class_model.py:545-553`, `ux/…/nodes.py:239-254`). [2]
- whiteboard.py:459-493 `BoardLinks` — do-not-invent-parallel-object-models — the same record as `PublishedLinks` in `harness/design_canvas/versions.py:29-51` (a file's or version's name to the address it was published at, kept in one JSON file beside them); its own docstring says so. Two classes, two file readers. [2]
- whiteboard.py:487-493 `BoardLinks._all` with :483-485 `record` — never-swallow-exceptions — a `whiteboards.json` that does not read is taken as holding nothing, and the next `record` writes over it, losing every other board's address. [3]
- whiteboard.py:474 `of(file)`, :483 `record(file, url)` — hold-state-on-the-object-not-in-parameters — both callers write `BoardLinks.beside(file).of(file)` (`cdd_guidance/actions/render/rendered_file.py:151`, `space/session/practice_session_output.py:655`): the file is handed over twice. [3]

### harness/design_canvas/canvas.py

- canvas.py:54 `DesignCanvas.launch_page` — deep-module — read only by `_canvas_json` (canvas.py:116). [1]
- canvas.py:101 `DesignCanvas.write` — seam-names-current-code — no production caller (the Claude Design render returns `files()`, `cdd_guidance/practices/ux/model/claude_design/story_canvas.py:158,166`); only `design_canvas_spec.py:41` calls it. The card's Constraint still says "Write a canvas only through `DesignCanvas.write`". [1]
- canvas.py:44-95 `DesignCanvas` — keep-classes-single-responsibility — two jobs on one class: the canvas being drawn (pages, boards, files) and what a project folder already holds (`artboards_in`, `holds`, `size_of`, `stylesheets_linked_by`). The second needs `project`, which is optional, so four operations quietly answer nothing for a canvas made without it. [3]
- canvas.py:60 `add_board(name, board, text)` with :26 `CanvasBoard`, :48 `_pages: List[dict]` — shape-classes-around-resources — the card says a practice "hands artboards to a DesignCanvas", but the canvas is handed a path string, a dict and a text; `Artboard` (canvas.py:251) never reaches it. [3]
- canvas.py:125 `stem` — prefer-class-operations — a module function about an artboard's file name, used by the UX practice four times (`story_canvas.py:198,341,355,362`). [3]

### harness/design_canvas/versions.py

- versions.py:68 `CanvasVersions.numbers` — deep-module — read only by `latest` (versions.py:77). [1]
- versions.py:79, :99, :121, :125, :129 `folder(number)`, `release(number, name)`, `title(number, name)`, `link(number)`, `record_link(number, url)` — hold-state-on-the-object-not-in-parameters — five operations take the version's number so the receiver can find the version again; `working()`, `unpublished()` and `start_next()` answer a bare `int`. A version is a thing with a folder, a link and a title, and is not modelled. [3]
- versions.py:29-51 `PublishedLinks` with :125-130 — no-redundant-relationship-paths — a version's link is reached two ways: `canvas.link(canvas.latest)` (`space/session/practice_session_output.py:183`) and `CanvasVersions(version.parent).published.of(version.name)` (the same file, line 659). [1]

### harness/design_canvas/fixture_bar.py and look.py

- fixture_bar.py:117-191 `ScenarioSource`, `FixtureScreen`, `bar`, `methods`; look.py:26-33 `LOOK` — extensions-live-with-the-domain — a screen that plays a story's scenario fixtures, and a look keyed by `epic`, `sub_epic`, `actor` and `story`, are the UX practice's Claude Design format, not the canvas "the same for every practice" the card's Constraint describes. Their only user is `cdd_guidance/practices/ux/model/claude_design` (its recipe and `story_canvas.py:19`). [1]
- fixture_bar.py:104 `bar`, :111 `methods` — prefer-class-operations — module functions that serve `FixtureScreen` alone in Python. [3]

### harness/diagnostics (module)

- `.context/module-context.md` — high-cohesion — one module holds four unrelated jobs: reporting health and probing an install (`server_health.py`, the probes), the registry of web apps with their npm install and node servers (`app.py`), the CDD version and its GitHub release (`cdd_version.py`, `release.py`, `github_cli.py`), and running the slow test tiers on a timer (`test_runs.py`, `desktop_walk_question.py`). The card gives the reason App is here as "`app.open` is an MCP operation and harness/installation imports no harness/mcp", which is where it could not go, not why it belongs. `harness/files_app/files_app.py:7` and `space/kanban` import `harness.diagnostics` only to register an app. [1]
- server_health.py:11, test_runs.py:486-489 — seam-names-current-code — diagnostics depends on `harness/e2e_review`; the card's Dependencies do not list it, and the second import sits inside a function. [1]

### harness/diagnostics/app.py

- app.py:279-298 `AppPackage`, `AppPage` with :346-353 `App.__init__` — shape-classes-around-resources — the two are built only to be taken apart: `App` copies `package.folder`, `package.file`, `package.sources`, `package.npm`, `page.server` and `page.path` into its own fields and keeps neither. Installing (stamps, `npm install`, the build, app.py:439-489) is the package's work and sits on `App`. [3]
- app.py:362 `App.load(app, *, project)` — limit-operation-parameters — `project` is never read. [3]
- app.py:65-71 `AppNotStarted` — use-intention-revealing-names — the docstring and every raise (app.py:428, 436, 478-482) are about an install that failed. [4]
- app.py:494-495 `GRAPH_APP` — extensions-live-with-the-domain — the Graph app is made and registered here because `harness/graph` sits below this module; the Files app and the Kanban register their own. [1]
- app.py:147-148 `AppServer.__init__` — use-explicit-dependencies — builds `PortProbe()` and `ServerLane.from_home()` when none is given. [3]

### harness/diagnostics/test_runs.py

- test_runs.py:303-335 `TestRunRecord._read/_write/_while_busy`, :248-267 `claimed` — eliminate-duplication — reads JSON, puts the file in place whole and retries while Windows holds it, all of which `JsonFile` does (`harness/installation/json_file.py:60-90,125-153`), and holds a claim file where `JsonFile.held()` (json_file.py:90) holds the file. [2]
- test_runs.py:542-543, :618 `TestCadence.start_due`, `_settled` — put-logic-on-the-owning-resource — the cadence sets `run.outcome` and writes `run._summary`, a private field of `TestRun`, to say a run did not start or was abandoned. [3]
- test_runs.py:73 `_counted_every_file_passed`, :457 `main_checkout`, :481 `e2e_run_name`, :486 `_review_screens`, :652 `default_record_folder` — prefer-class-operations — module functions that belong to `TestRun` (the first and third take or serve one), the checkout, and the record. [3]
- test_runs.py:100-109 with :159-191 `TestRun` — eliminate-duplication — the same four facts under two names each (`tier`/`name`, `outcome`/`state`, `started_at`/`started`, `_summary`/`summary`), and two ways out: `to_json` (124) for the file and the data fields for the report. [2]
- test_runs.py:339 `SCHEDULED_RELEASE` and `harness/e2e_review/e2e_review.py:325` `ScheduledReview.RELEASE`; test_runs.py:481-483 and e2e_review.py:252,367 (`run-` plus the same time format); `desktop_walk_question.py:19` `STORY_TESTS` and e2e_review.py:30 — eliminate-duplication — the scheduled run's folder name, a run's name and the story tests folder are each written in two modules. [2]
- test_runs.py:611-614 `_reviewed` — use-exceptions-properly — catches `Exception` and turns it into a line of the run's summary, so a bug in the review reads as "not started". [3]
- test_runs.py:654, agent_tools_diagnostics.py:27, guidance_diagnostics.py:27, agent_tools_probe.py:77 — one-way-deps — imports inside functions; none hides a cycle (`CddHome`, the probes and `McpHost` import nothing from these files), so each can move to the top. [1]
- test_runs.py:500-502 `TestCadence.__init__` — limit-operation-parameters — seven parameters, five of them test seams (`clock`, `review`, `wait`, `say`, `runner`). [3]

### harness/diagnostics/desktop_walk_question.py

- desktop_walk_question.py:17-23 `DESKTOP_STORY_TESTS`, `STORY_TESTS`, `WALK_COMMAND` — the guardrail "the framework does not know the practices" — the framework names the Stories practice's desktop output (`*_story.desktop.md` under `story_tests`) and the `/desktop-walk` command of `cdd_guidance/desktop_walk`. [1]
- desktop_walk_question.py:28-105 `DesktopWalkQuestion` — keep-classes-single-responsibility — one class is the file that keeps the question, the question as the dialog shows it (`open` answers `self` or `None`, line 67), and the wording of the run's summary (`closed_for`, 53-64, writes the answer and returns a sentence). `ask`, `answer` and `closed_for` each take `run_id` to match what the file holds. [3]

### harness/diagnostics/cdd_version.py and release.py

- cdd_version.py:49 `Release` against release.py:83 `CddRelease` — use-intention-revealing-names — the first is a version number (major, minor) and the second the act of releasing. [4]
- cdd_version.py:22,26,131-141 and release.py:15,19,136-140 — eliminate-duplication — `pyproject.toml`'s version is read by `Release.from_pyproject`, rewritten by a regex in `set_next`, and read by a second regex in `CddRelease.version`; `PYPROJECT` and `_VERSION_LINE` are declared in both files. [2]
- release.py:18 `COMPLETE_SESSIONS` — single-boundary — `.sessions/_complete` is where `space/kanban` moves a finished ticket; the framework reads that layout to write release notes. [1]
- release.py:93-94 `url`, `is_published` with :153-162 `release_url`, `published` — use-consistent-naming — each fact has a public field and a data field under another name. [4]

### harness/diagnostics/agent_tools_probe.py, probe_arguments.py, cdd_diagnostic_bridge.py

- agent_tools_probe.py:48 `agent_tools_toolset_ref` — prefer-class-operations — a module function used only by `AgentToolsProbe.toolset_refs` (86-90). [3]
- cdd_diagnostic_bridge.py:37 `probe_arguments -> tuple[dict[str, Any], list[str]] | None`, probe_arguments.py:73 `work_session -> Any` — use-typed-signatures — the first is `OperationArguments` (probe_arguments.py:18) unnamed, and `agent_tools_probe.py:171` rebuilds one from it. [4]

### harness/e2e_review/e2e_review.py

- e2e_review.py (module) — named-seam-and-constraint — the folder has no `.context/module-context.md`, though `harness/diagnostics` depends on it and it publishes five MCP operations. It also names `space/kanban/app` (e2e_review.py:32) and `story_tests` (30), which the framework is meant not to know. [1]
- e2e_review.py:316-318 `_baseline_of`, :127-129 `verdicts`, :122-124 `rows` — do-not-invent-parallel-object-models — `baseline.json`, `review.json` and `results.json` are read here, in `report/review.ts:28-33,50-53` and again in `report/report.ts:252-259,278-279`. The copies already differ: the TypeScript baseline is none when the accepted run's folder is gone; the Python one answers a path that is not there. The verdict words are written in both languages (e2e_review.py:34-35,112-113; `report.ts:18`, `review.ts:18`). [2]
- e2e_review.py:122 `rows -> list[dict]`, :127 `verdicts -> dict[str, dict]`, :263 `changed_pairs -> list[dict]` — use-typed-signatures — a step and a pair are dicts with string keys on a published seam. [4]
- e2e_review.py:344-349 `ScheduledReview.start` — hide-inner-details — reaches `self.review._baseline_of` and `self.review._tool` four times. [1]
- e2e_review.py:278-295 `E2eReview.record_verdict` — keep-operations-single-responsibility — three operations chosen by which words the verdict is: judge a step a test ran, record a walked step, or record a review of a changed pair, each using a different half of the eight parameters. [3]
- e2e_review.py:65-71 `folder` and `run_folder`; :154 `run` and :190 `review_id` — use-consistent-naming — the same value under two names. [4]
- e2e_review.py:367 `_stamp`, :371 `_start_in_background`, :376 `_start_review_agent` — prefer-class-operations — module functions used from one class each. [3]

### harness/e2e_review/report/review.ts and report.ts

- review.ts:28-115 `baselineOf(subEpicDir)`, `changedPairs(runDir, againstDir)`, `recordVerdict(runDir, againstDir, …)`, `judgeStep(runDir, …)`, `openPairs`, `isReviewed`, `acceptRun` — hold-state-on-the-object-not-in-parameters — every function is handed the run's folder, and most the accepted run's too; a run and its sub-epic are not objects here, though Python has `E2eRun`. [3]
- report.ts:252-265 `previousRunOf`, :278-279 `checkedRows` — eliminate-duplication — read `baseline.json` and `review.json` by literal name instead of through `review.ts`, because `review.ts` imports `report.ts` and the two would form a cycle. [2]

### harness/files_app/app/files/whiteboard-canvas.ts

- whiteboard-canvas.ts:15-91 `WhiteboardCanvas.from`, `blockOf`, `labelOf`, `arrowOf` — single-boundary — a second reader of the `.whiteboard` file, with the store's own words written again (`shape`, `container`, `text`, `arrow`, `from`, `to`, `dash`, `rounded`), which `harness/whiteboard/whiteboard.py:58-60,139,211,222,230` owns. A new element kind or field has to be added in both. [2]

### harness/files_app/app/files/files-page.ts and file-bar.ts

- files-page.ts:31-57 `listedBy`, `selectedFormatsOf`, `filesShown`, `rootFilesShown`, `isNoPracticeSelected`; file-bar.ts:99-104 `isSessionWork` — single-boundary — which files a session lists for a selection, and which count as the session's own work, are decided in the page. The card says the Files app "holds no rule of its own"; the board and the agent's tools get a different answer or none. [1]
- file-bar.ts:25-37 `publishedOf`, `CANVAS_VERSION` — single-boundary — works out from a path that a file is a whiteboard or a design canvas version (`design-canvas/<version>/project/canvas.json`), a layout `harness/design_canvas` owns; the session already answers the link (`space/session/practice_session_output.py:655-659`) and could answer the kind with it. [2]

### harness/files_app/app/files (other files)

- failure-fixes.ts:12 `FailureKindName` — contract-comes-from-the-adapter — the six kind names of `tools/error_display/failure.py:67-134` typed out by hand. [2]
- failure-fixes.ts:62 `dismiss(failure)`, :68 `fix(failure)`, :84 `changed(failure, …)` — hold-state-on-the-object-not-in-parameters — a shown failure is found again by its message text each time; the view that calls already holds it. [3]
- files-notices.ts:13-51 `FilesNotices` — eliminate-duplication — `harness/graph/app/graph/graph-failures.ts:21-56` `GraphFailures` is the same class for the Graph app: `fail(failure, context)`, `toast(text)`, a set of failures already told, and `chat.send('failure', …)`. [2]
- chat-context.ts:5, failure-fixes.ts:8, file-browser.ts:6, files-graph.ts:11, files-notices.ts:9, files-page.ts:26, files-theme.ts:108, format-alignment.ts:3, guidance-selector.ts:9 `reasonOf`; files-graph.ts:37 and source-of-file.ts:38 `saidBy` — eliminate-duplication — one line copied nine times, and one function copied twice. [2]
- code-outline.ts:28 `memberLines` — eliminate-duplication — finds each class's members by regular expression, while the session already answers a file's folds from the graph (`space/session/session_file.py:36-49` `Fold`) and the catalog finds them a third way (`harness/catalog_generator/source_folds.py:27`). [2]
- guidance-selector.ts:21, file-comments-actions.ts:16 — low-coupling — each part is given the whole `FilesPage` and reaches `page.store`, `page.session`, `page.notices` and `page.showSelected()`, while the page builds them; the other parts are given only what they use. [1]

### tools/prompt_queue/prompt_queue.py

- prompt_queue.py:57-67 `QueuedPrompt`, :50 `PromptStep` with :198-301 — shape-classes-around-resources — a prompt and a step are dicts, and the queue does their work: ten operations take `prompt: str`, find the dict by id (`if item["id"] == prompt`, written fourteen times), and rebuild the list. Marking done, reopening, assigning a robot, planning steps and attaching a file are a prompt's operations. This is why the class has 17 public operations. [3]
- prompt_queue.py:303-314 `queue_handoff`, :374-392 `handoff_steps` — single-boundary — the queue parses the handoff's "Approach for Next Agent" section; `space/session` owns the handoff and its format, and its only caller is `space/session/open_sessions.py:15`. [1]
- prompt_queue.py:150 `of_chat` — low-coupling — builds the path inside the chat's folder itself (see `harness/chat/chat.py:135`). [1]
- prompt_queue.py:208 `to`, :295 `data` — avoid-vague-parameter-names — `to` is a place counted from 0 and `data` is a file's bytes in base64. [4]

### tools/prompt_queue/hooks/queue/prompt-queue.ts

- prompt-queue.ts:636-660 `removeStep`, `moveStep`, `changeSteps`; :852-900 `pointerOf`, `movePointerUp/Down`, `stepPointerOf`, `moveStepPointerUp/Down` — domain-lives-in-python — which prompt is next (not done and not a decision card, line 853), and which step becomes `in_progress` when the pointer moves, are decided in the mod, which then sends Python the whole step list with `set_steps`. The agent working the queue through `prompt-queue.done` and `step_done` follows a different, simpler rule. [1]
- prompt-queue.ts:45-77 — domain-folder-in-the-mod — one file holds nineteen atoms and about eighty functions for at least four things: the queue's cards, play and the decision wait, sub-agent robots and their tasks, and following the agent's plan. [1]
- prompt-queue.ts:125 `answeringServer` — no-state-in-module-variables — a module variable. [3]
- queue-order.ts:4 `PromptQueue` — client-mirrors-python-domain — a class with the Python toolset's name that holds three getters (`isEmpty`, `size`, `texts`) and none of the queue's operations; the file is named `queue-order.ts` and also holds reply parsing. [4]

### tools/prompt_queue/types/index.d.ts

- index.d.ts:3-9 `QueuedPrompt`, `StepState`, `PromptStep`, `QueueJson` — contract-comes-from-the-adapter — hand copies of the Python `TypedDict`s (`prompt_queue.py:43-67`), which the adapter generates as `PromptQueueData`. The comment gives the reason (the contract file imports nothing); the chat bar's contract file shows the form without a copy (`object` in the contract, the adapter's type where it is read). [2]

### tools/prompt_notify/prompt_notify.py

- prompt_notify.py:62, :74, :123-124 — one-way-deps — imports inside functions; line 123 imports `AgentToolSet` a second time (it is already imported at line 21). [1]
- prompt_notify.py:256-269 `_mcp_aliases`, `_name_matches` — eliminate-duplication — rebuilds the names a tool is published and called under; `AgentTool.mcp_name` and `AgentTool.is_called` own that (`harness/agent_tools/agent_tools.py:1012,1019`). [2]
- prompt_notify.py:179, :201, :241-243, :275 `getattr(toolset, "tools"/"slug"/"child_toolsets", …)` — low-coupling — reads a toolset by attribute name and a default, past `AgentToolSet`'s typed seam. [1]
- prompt_notify.py:43-44 with :54-57, :141-147 `_catalog`, `_installed_extension` — use-explicit-dependencies — state kept on the class through `type(self)`, shared by every instance in the process. [3]
- prompt_notify.py:88 `handle(payload, toolsets)`, :98 `detect_echo(payload, toolsets)` — hold-state-on-the-object-not-in-parameters — both take the toolsets the object already holds as `echo_toolsets` (117); production passes exactly that (82). [3]
- prompt_notify.py:292-342 `ToastFile._joined_with_previous`, `_is_rules_notice`, `_guidance_names`, `_join_arrow_toasts` — hold-state-on-the-object-not-in-parameters — a toast is written as a sentence and then read back by splitting on the arrow and the word "rules" to join two toasts. [3]
- prompt_notify.py:98, :157, :236 `detect_echo`, `_log_echo`, `_echo_kind_label`, `echo_toolsets` against `show_toast`, `_begin_toast`; :218, :226 `_haystacks`, `hay`, `token` — use-consistent-naming — "echo" and "toast" name one thing (and `tools/echo` is another toolset); `hay` and `token` are search mechanics, not what a tool call names. [4]
- prompt_notify.py:94-96, :150 `tuple[str, str]`; :79, :88 `-> dict`; :88 `toolsets: list` — use-typed-signatures — the kind and label a call toasts is an unnamed pair passed through seven methods. [4]
- prompt_notify.py:129-132 `show_toast` — layer-separation — forwards to `show_ide_toast` (134) and adds nothing. [1]

### tools/granola/granola.py, tools/error_display/failure.py, tools/prompt_log/prompt_log.py

- granola.py:28-48 `MeetingNote`, `PlannedNote`, `GranolaNote` with :95-107 `_folder_of(note)`, `_plan_line(note)` — shape-classes-around-resources — three dict shapes of a note, and the toolset does the note's work for it. [3]
- granola.py:64 `Granola.root` — deep-module — no caller anywhere, specs included. [1]
- failure.py:54 `FailureKinds.every` — deep-module — read only by `failure_spec.py:45,48`. [1]
- prompt_log.py:155 `PromptLog.log_for` — deep-module — read only by `_append` (163). [1]

### harness/catalog_generator

- drawio_diagram.py:37 `is_story_map` and catalog_examples.py:246 — eliminate-duplication — the same test of a file's stem against `story_map`, twice, in a module that otherwise finds the Stories practice by what its card says (`catalog_practice.py:28`). [2]
- catalog_generator.py:113 `toolset -> object`, :120 `tool -> object | None`; catalog_examples.py:263 `fidelity` (no type); approach_page.py:364 `practices: list`; catalog_practice.py:117 `-> dict[str, Any]` — use-typed-signatures. [4]
- catalog_practice.py:28 `giving_stage_examples` — prefer-class-operations — a module function over a list of `CatalogPractice`. [3]

No findings in `tools/drawio_viewer`, `tools/echo` or `tools/sub_agent`.

## Fixes that change no design

Each is local: no class is added or removed and no seam another module calls changes shape, except where a caller is named.

| # | Change | Callers and specs that change with it | Risk |
|---|---|---|---|
| F1 | `harness/chat/chat.py:281`: take the `select` sentence out of `Chat.send`'s docstring. | The installed tool description (reinstall). | None. |
| F2 | `harness/chat-ui/pane/hooks/board-chat/board.ts:17-20`: delete the `select`, `show`, `show-stages`, `list-stages` members of `ChatRequest` and fix the comment at 13. | None post them. | None. |
| F3 | `chat.py:359,374`: rename `title` to `_title` and `is_connected` to `_is_connected`. | `chat.py:178,181,241,395`; `chat_spec.py` where it reads either. | Low. `_is_connected` is then read by `Chats` and `ChatMailbox` in the same file, which Python allows; say so in a comment or keep `is_connected` and take only `title`. |
| F4 | `chat.py:186`: make `hand_over` private (`_hand_over`, also in `RecordedChatLinks`, chat.py:200) and have `space/repo/repos.py:89-95` `NewChat.open` call `links_of_run().open_new(str(self._root), self.first_prompt)`. | `repos.py:79,92`; `repos` specs that fake `hand_over`. | Low. `NewChat.link` stays for `instructions`. |
| F5 | `chat.py:535-542`: delete `_while_windows_holds` and call `self._file.read()` / `write()` directly; keep `_read_once`'s handling of `JsonFileUnreadable`. | `chat_heavy_spec.py` (two check-ins at once). | Medium: `JsonFile` gives up after its own time limit; run the heavy spec before and after. |
| F6 | `harness/whiteboard/whiteboard.py`: make private `BoardElement.record`, `from_record`, `whole_id`, `pieces`, `joined`, `place`, and `Whiteboard.order`, `meta`, `writes`, `versions`. | `whiteboard_spec.py` (reads `writes`, `versions`, `record`); the card's Seam line and Constraint, which name `writes` (name `batches` instead). | Low. Brings the seam from 36 to 27 of 54; the limit is 18, so proposals D3 and D4 are still needed. |
| F7 | `harness/whiteboard/__init__.py:4`: also export `MAX_SIDE` and `UnreadableBoard`, and change the three imports that reach into `.whiteboard`. | `whiteboard_class_model.py:22`, `code_read.py:15`, `stories/model/miro/nodes.py:14`. | None. |
| F8 | `whiteboard.py:388`: rename `save` to `text` (a property) or `as_text()`. | `stories/…/nodes.py:125`, `whiteboard_class_model.py:553`, `ux/…/nodes.py:246,254,257`, `rendered_file.py`; specs. | Low; every caller in the same change (no alias). |
| F9 | `whiteboard.py:487-493`: `_all` raises a named failure (`BoardLinksUnreadable`, carrying the file) when the record exists and does not read; a missing file still answers none. | `practice_session_output.py:655`, `rendered_file.py:151`, `render.py:181,204` decide whether to show it; `whiteboard_spec.py`. | Low. Adds one exception class, no other shape. |
| F10 | `harness/design_canvas/canvas.py:54`, `versions.py:68`: `_launch_page`, `_numbers`. | `design_canvas_spec.py`, `versions_spec.py` if they read them. | None. |
| F11 | `harness/design_canvas/canvas.py:101`: delete `DesignCanvas.write` and its example in `design_canvas_spec.py:41`, and correct the card's Constraint to say the render returns `files()` and the Render action places them. | The card; the spec. | Low. Check the UX recipe (`story_canvas.md`) does not tell an agent to call it. |
| F12 | `harness/diagnostics/app.py:362`: drop the unused `project` parameter of `App.load`. | Check `tool_subject` does not require it by name for every subject. | Low; confirm with the app heavy spec. |
| F13 | `test_runs.py:654`, `agent_tools_diagnostics.py:27`, `guidance_diagnostics.py:27`, `agent_tools_probe.py:77`, `prompt_notify.py:62,74,123-124`: move the imports to the top of the file; delete the repeated `AgentToolSet` import. | None. | Low: an import cycle would show at once on import; the unit tier catches it. |
| F14 | `test_runs.py:73,481`: move `_counted_every_file_passed` and `e2e_run_name` onto `TestRun` (`TestRun.folder_name`), and `agent_tools_probe.py:48` onto `AgentToolsProbe`. | `test_runs.py:140,556`; `test_runs_spec.py`. | None. |
| F15 | `test_runs.py:542-543,618`: give `TestRun` `not_started(reason)` and `abandoned()` and call them from `TestCadence`. | `test_runs_spec.py`. | None. |
| F16 | `test_runs.py:339` and `e2e_review.py:325`: keep the word `scheduled` once (`ScheduledReview.RELEASE`) and import it; the run-name format once (`E2eRun` or `TestRun`). | `server_health.py:10,28`. | None. |
| F17 | `cdd_version.py:22,26` and `release.py:15,19`: declare `PYPROJECT` and the version line once and import it. (The owning object is proposal D8.) | None. | None. |
| F18 | `release.py:93-94,153-162`: keep `_url` and `_is_published` private behind the two data fields. | `cdd_version_spec.py` / release specs that read `.url`. | None. |
| F19 | `e2e_review.py:65-71`: keep `folder` private behind `run_folder`, or drop `run_folder` if the report does not read it; `e2e_review.py:344-349`: make `baseline_of` and a `report(run, against)` operation part of `E2eReview` so `ScheduledReview` stops reading `_baseline_of` and `_tool`. | `e2e_review_spec.py`. | Low. |
| F20 | `harness/files_app/app/files`: one `reason.ts` exporting `reasonOf` and one `saidBy`, imported by the nine and two files that copy them. | None outside the folder. | None. |
| F21 | `chat-bar-client.ts:123,128`: delete the two casts; `:117` delete `ticketName` and `:193` `actionFidelities`, pointing their six callers at `sessionName` and `fidelities`; `fidelity-progress-client.ts:141` delete `key`. `:169` type `formatChoices` as `FormatChoiceJson[]`. | `fidelity-files-client.ts:63`, `overlay-choices-client.ts:20-28`, `action-button-view.tsx:44,54`, the views that read `dot.key`. | None; `claude plugin validate` and the mod's tests check it. |
| F22 | `harness/chat-ui/pane/types/index.d.ts:16,23,27`: delete `TestRunJson`, `E2eReviewJson`, `DesktopWalkQuestionJson` and read `TestRunData`, `E2eRunReviewData`, `DesktopWalkQuestionData` from the adapter with `import type` in `server-health-client.ts`, `server-health-wording.ts` and `desktop-walk-question-view.tsx`. | Those three files. | Low. The contract file keeps importing nothing. |
| F23 | `harness/files_app/app/files/format-chips.ts`: decide one fallback for a format with no glyph and write it in both copies; the shared home is proposal D6. | `bar-columns.ts:10`. | None. |
| F24 | `tools/prompt_queue/prompt_queue.py:208,295`: rename `to` to `place` and `data` to `base64_bytes`. | Published argument names: `prompt-queue.ts:288` (`move`) and the `attach` call near 427-440; reinstall; `prompt_queue_spec.py`. | Medium: an agent or mod on the old name fails until reinstalled; do it with a release, not between. |
| F25 | `tools/prompt_notify/prompt_notify.py:88,98`: drop the `toolsets` parameter and read `self.echo_toolsets`; specs make the notifier with the toolsets they want. `:129-137`: delete `show_ide_toast` and keep `show_toast` (or the reverse) as the one name. | `prompt_notify_spec.py:133-345`, `cdd_guidance/actions/action_toast_spec.py:21`; `prompt_notify.py:345`. | Low; needs a constructor argument for the toolsets (a field, not a new class). |
| F26 | `tools/prompt_notify/prompt_notify.py:256-269`: replace `_mcp_aliases` and `_name_matches` with `tool.is_called(invoked)`. | `prompt_notify_spec.py` examples for underscore and dotted names. | Medium: check `is_called` accepts every spelling the specs list (bare tool name, `slug_name`, a practice's bare slug) before deleting. |
| F27 | `tools/granola/granola.py:64`: delete `root`. `tools/error_display/failure.py:54`: delete `every` with the two spec examples that read it, or have `FailureKindUnknownError` use it for `known`. `tools/prompt_log/prompt_log.py:155`: `_log_for`. | `failure_spec.py:45,48`. | None. |
| F28 | `harness/catalog_generator`: type the five untyped signatures (`Action`'s toolset and tool types, `FidelityGuidance`, `list[CatalogPractice]`); `DrawioDiagram.is_story_map` used from `catalog_examples.py:246`. | None. | None. |
| F29 | `harness/diagnostics/.context/module-context.md`: add `harness/e2e_review` to Dependencies. Add `harness/e2e_review/.context/module-context.md` (purpose, seam terms, constraint). | Docs only. | None. |

## Proposed design changes

Each stands alone. Sizes are files touched and rough changed lines, specs included.

### D1. A queued prompt is an object that does its own work

**Problem.** `tools/prompt_queue/prompt_queue.py` keeps a prompt and a step as dicts (`QueuedPrompt`, `PromptStep`, lines 50-67) and the queue does everything to them: ten operations take `prompt: str`, look the dict up by id, and rebuild the list (198-301). The rule for which prompt is next and how the step pointer moves lives only in the mod (`hooks/queue/prompt-queue.ts:852-900`), which works out a new step list and sends it whole with `set_steps`, so the mod and the agent follow different rules. `PromptQueue` has 17 public operations.

**Before**
```
PromptQueue (toolset, 17 public)
  chat, prompts: list[dict]
  show add add_all edit move remove clear
  done(prompt) reopen(prompt) assign(prompt, robot) set_steps(prompt, steps)
  add_interruption(prompt, text) step_done(prompt, step) attach(prompt, filename, media_type, data)
  queue_handoff(handoff)        load(chat, call)  of_chat(chat, archive)
QueuedPrompt (TypedDict)  PromptStep (TypedDict)
prompt-queue.ts: pointerOf, movePointerUp/Down, stepPointerOf, moveStepPointerUp/Down,
                 removeStep, moveStep  -> set_steps(whole list)
```
**After**
```
PromptQueue (toolset)
  chat, prompts: list[QueuedPrompt]            ~ typed
  show add add_all move remove clear
  + next: QueuedPrompt | None                  (the pointer rule, from prompt-queue.ts:852)
  + prompt(id) -> QueuedPrompt                 (refuses with PromptNotQueued)
  done reopen assign set_steps add_interruption step_done attach edit
                                               ~ each becomes: self.prompt(id).<same verb>(); MCP names unchanged
  + move_step(prompt, step, place)  + remove_step(prompt, step)
  + step_back(prompt)  + step_on(prompt)       (from moveStepPointerUp/Down)
  - queue_handoff                              → D2
+ QueuedPrompt (class)
    id, text, steps: PromptSteps, attachments, is_done, robot
    edit(text) mark_done() reopen() assign(robot) plan(steps) interrupt(text) attach(file)
    record -> dict                             (what the file keeps)
+ PromptSteps (class)
    done(number) move(step, place) remove(step) back() on()   pointer
- QueuedPrompt, PromptStep TypedDicts
prompt-queue.ts: - the step and pointer arithmetic; each press calls one tool
```
**Callers affected.** `prompt_queue.py`, `prompt_queue_spec.py`, the story tests under `story_tests/…queue…`, `hooks/queue/prompt-queue.ts` (about ten functions get shorter), `queue-view.tsx` (reads `queue.next` instead of `pointerOf`), `types/index.d.ts`, the generated adapter.
**Size.** 6 files, about 350 lines changed, 120 removed from TypeScript. Four new MCP operations.
**What could go wrong.** The queue file is shared by the stable and dev lanes, so its JSON must not change shape: `QueuedPrompt.record` has to write exactly today's keys. The public operation count rises to 21 unless the prompt-scoped tools are republished as `queued-prompt.*`, which would rename tools every chat and `space/session/open_sessions.py:27-30` name; that rename is a separate decision and is not part of this proposal. Flow B work: the heavy spec that changes one queue from two processes already exists.

### D2. The handoff answers its own steps

**Problem.** `tools/prompt_queue/prompt_queue.py:36-39,303-314,374-392` parses the "Approach for Next Agent" section of a handoff. `space/session` owns handoffs and their format (`space/session/handoffs.py`, `HANDOFF-FORMAT.md`), and is the only caller (`open_sessions.py:15`).

**Before**
```
space/session/open_sessions.py --> PromptQueue.queue_handoff(handoff: Path) -> int
tools/prompt_queue: handoff_steps(text), _APPROACH_HEADING, _NUMBERED_STEP, "handoffs" list in the queue file
```
**After**
```
space/session:  + Handoff.next_steps -> list[str]          (→ moved from prompt_queue.handoff_steps)
tools/prompt_queue:  ~ PromptQueue.queue_once(source: str, texts: list[str]) -> int
                       (queues texts unless source was queued before; keeps the "handoffs" list as "queued_once")
                     - handoff_steps, - the three handoff patterns
open_sessions.py: queue.queue_once(handoff.name, handoff.next_steps)
```
**Callers affected.** `open_sessions.py`, `prompt_queue.py`, both specs, the queue story test that queues a handoff.
**Size.** 5 files, about 90 lines.
**What could go wrong.** The key in the queue file changes name unless kept as `handoffs`; keep it, so a queue written before the change still refuses a handoff queued twice.

### D3. One object for "published at this address", and a version that is an object

**Problem.** `BoardLinks` (`harness/whiteboard/whiteboard.py:459-493`) and `PublishedLinks` (`harness/design_canvas/versions.py:29-51`) keep the same record in the same way, one with `JsonFile` and one by hand (and the hand one loses the file when it does not read). `CanvasVersions` passes a version's number into five operations (versions.py:79-130), and callers reach a version's link by two routes (`practice_session_output.py:183` and `:659`). The Files app then works out from a path what kind of published thing a file is (`file-bar.ts:25-37`).

**Before**
```
harness/whiteboard:    BoardLinks(folder)  beside(file) of(file) file_published_to(url) record(file, url)   [reads JSON by hand]
harness/design_canvas: PublishedLinks(record: JsonFile)  all() of(version) record(version, url) rename(version, name)
                       CanvasVersions(root)  numbers latest folder(n) start_next()->int release(n, name)
                                             working()->int unpublished()->int title(n, name) link(n) record_link(n, url)
space/session: BoardLinks.beside(file).of(file);  canvas.link(canvas.latest);  CanvasVersions(v.parent).published.of(v.name)
files_app: publishedOf(entry) by path regex
```
**After**
```
harness/installation (beside JsonFile):
  + PublishedLinks(record: JsonFile)        of(name) named_at(url) record(name, url) rename(name, new)
harness/whiteboard:    - BoardLinks         → PublishedLinks(JsonFile(folder / "whiteboards.json"))
                       + Whiteboard.links_beside(file) -> PublishedLinks    (keeps the file name in one place)
harness/design_canvas: - PublishedLinks     → moved
                       + CanvasVersion      number, folder, link, title(name), publish_at(url), release(name)
                       ~ CanvasVersions     latest -> CanvasVersion | None;  working() / unpublished() / start_next() -> CanvasVersion
                                            - folder(n) - title(n, name) - link(n) - record_link(n, url) - release(n, name) - numbers
space/session: ~ FileEntry answers link and published_kind ("whiteboard" | "design canvas" | "")
files_app: - publishedOf's path regex; reads entry.published_kind
```
**Callers affected.** `render.py:180-204`, `rendered_file.py:151`, `practice_session_output.py:15-19,178-183,650-660`, the UX recipe `story_canvas.md` (lines 5-17, 65: `working().folder` instead of `folder(working())`), `versions_spec.py`, `whiteboard_spec.py`, the editor-apps story test, `file-bar.ts`, the session file model and its adapter. `harness/whiteboard` gains a dependency on `harness/installation`; its card says "Dependencies: none" today.
**Size.** 12 files, about 300 lines.
**What could go wrong.** The recipe is an API agents follow from markdown (decision `design_canvas/.context/cdr/0001`), so the recipe and the class must change in one commit or agents call operations that are gone. `versions.json` and `whiteboards.json` keep their shape. The whiteboard seam falls by four methods (to 23 of about 50 with F6); design_canvas's seam stays near 11 because the recipe needs those operations, so that module still fails `deep-module` until D4.

### D4. The practice-specific canvas code goes to the practice

**Problem.** `harness/design_canvas/fixture_bar.py` (a screen that plays a story's scenario fixtures) and `look.py` (a look keyed by `epic`, `sub_epic`, `actor`, `story`) are the UX practice's Claude Design format; nothing else can use them, and the card's own Constraint says the canvas "stays the same for every practice". `DesignCanvas` also does two jobs (draw a canvas; read what a project folder holds). The module fails `deep-module` at 24 of 38.

**Before**
```
harness/design_canvas: DesignCanvas(title, project?)  add_page add_board(name, dict, text) placed files write
                                                      artboards_in holds size_of stylesheets_linked_by launch_page
                       Artboard, Place(card, thumbnail), stem()
                       FixtureScreen, ScenarioSource, bar(), methods()        look: LOOK, FONTS, BACKGROUND, CardLook
                       CanvasVersions, PublishedLinks
```
**After**
```
harness/design_canvas: DesignCanvas(title)  add_page  ~ add(artboard: Artboard, at: CanvasBoard)  placed  files
                       + CanvasProject(folder)  artboards_in  size_of (None when not held)  stylesheets_linked_by
                                                (→ from DesignCanvas; - holds, folded into size_of)
                       ~ Artboard  + name (its path under project/)  + stem   (→ from stem())
                       Place(card(look: CardLook, …), thumbnail), CardLook
                       CanvasVersions, CanvasVersion (D3)
cdd_guidance/practices/ux/model/claude_design:
                       + fixture_screen.py   FixtureScreen, ScenarioSource (bar and methods become its private parts)   → moved
                       + look.py             LOOK, FONTS, BACKGROUND                                                    → moved
```
**Callers affected.** `story_canvas.py:18-19,158-198,341-383`, `story_canvas.md` (the import lines an agent copies), `production_code_rules_spec.py:126` (names `design_canvas/fixture_bar.py`), `design_canvas_spec.py`, the card.
**Size.** 9 files, about 250 lines, most of them moved.
**What could go wrong.** Agents' saved build scripts in closed sessions import `harness.design_canvas.fixture_bar` (`.sessions/_complete/simple-queue-enhancements/design-canvas/build_explorer.py:34`); they are history and stop running. The seam then counts about 17 of 26 for design_canvas, still over 35%, because a small module whose whole purpose is a file-layout API has little to hide; the honest reading is that the measure fits this module poorly, and the Product Owner may prefer to accept it by decision rather than go further.

### D5. One reader of a `.whiteboard` file and one owner of element ids

**Problem.** Three places know the board's stored shape: `harness/whiteboard/whiteboard.py` (Python), `harness/files_app/app/files/whiteboard-canvas.ts` (TypeScript, with the type and field words typed again), and each practice's adapter, which splits element ids and hashes node keys itself with two different lengths (10 and 12). Each practice also repeats the same three render lines. The public kinds are hidden behind four factories while every caller reads kind-only members untyped; the module fails `deep-module` at 36 of 54.

**Before**
```
harness/whiteboard: BoardElement  shape() section() words() arrow()  role  [kinds Shape/Section/Label/Arrow private]
                    Whiteboard    sections/shapes/labels/arrows -> List[BoardElement]   save()  keep_places(previous)
                    WhiteboardNode  board_box board_elements board_shape
practices: _key(*names) / board_key (sha1, 10 or 12 chars) x3;  element.id.split(".") x4;
           render: board.keep_places(Whiteboard.from_text(previous)); board.save()  x3
files_app: WhiteboardCanvas.from(text)  reads elements[*].type/x/y/w/h/from/to/dash/kind itself
```
**After**
```
harness/whiteboard: + ElementId(role, *parts)   str()  ElementId.of(role, *names) (the one hash and length)  role  parts
                    ~ BoardElement  id: ElementId   - shape() - section() - words() - arrow()
                    ~ Shape, Section, Label, Arrow   public, built directly (a constructor is not a seam method)
                    ~ Whiteboard   sections -> List[Section], shapes -> List[Shape], labels -> List[Label], arrows -> List[Arrow]
                                   + drawn_over(previous_text) -> str   (keep_places + text, the three repeated lines)
                                   + Whiteboard is published with @language_adapter: blocks, labels, arrows as data fields
                    ~ WhiteboardNode  board_key comes from ElementId.of
practices: - _key, - both board_key bodies, - the id splits
files_app: ~ WhiteboardCanvas keeps only the frame and the side an arrow leaves from; reads WhiteboardData
           (the session's file answer carries it for a .whiteboard file)
```
**Callers affected.** The four practice whiteboard adapters (`stories`, `ux`, `clean_engineering`, `ddd`), their specs, `whiteboard_spec.py`, `whiteboard-canvas.ts` and its spec, `files-page-view.tsx:303`, the session file model.
**Size.** 14 files, about 450 lines.
**What could go wrong.** Element ids are how a board already published in Claude is updated in place: if `ElementId.of` produces a different hash for an existing node, the next render deletes and redraws every element and loses where people moved them. The Clean Engineering adapter uses 12 characters and the others 10, so the shared function must take the length from the practice, or the Clean Engineering boards are redrawn once. This is a Flow A change at the store boundary: render onto a real board and compare before stubbing. Seam after F6, D3 and this: about 15 of 50, under the limit.

### D6. Toggling a session's selection is one Python operation, and the page's listing rules move to the session

**Problem.** The chat bar (`harness/chat-ui/pane/hooks/chat-bar/guidance-client.ts:51-100`) and the Files app (`harness/files_app/app/files/guidance-selector.ts:37-88`) each implement the same press, because `session.update_guidance_selection` takes whole lists. Only the chat bar applies the default "select the ticket's stage first". The Files app decides which files a selection lists and which are the session's own work (`files-page.ts:31-57`, `file-bar.ts:99-104`), and `ChatBarClient` decides which fidelities an action runs on and edits Python's command string to say so (`chat-bar-client.ts:77-92,137-149`, `fidelity-progress-client.ts:175-180`).

**Before**
```
Session.update_guidance_selection(stages, practices, formats) -> GuidanceSelection
chat bar:  toggle() flipped() startStage() accept();  ChatBarClient.shownStages/isPracticeOn/fidelities;  commandOn() string replace
files app: GuidanceSelector.toggleStage/togglePractice/toggleFormat/update/accept;  listedBy/filesShown/rootFilesShown/isSessionWork
```
**After**
```
space/session:
  + GuidanceSelection.toggle(part: "stage"|"practice"|"format", name) -> GuidanceSelection      (MCP: session.toggle_guidance)
  ~ GuidanceSelection  applies "the ticket's stage first" itself when nothing was chosen
  + GuidanceSelection.fidelities_for_actions -> list[slug]     (none selected meaning all)
  + GuidanceSelection.command(action) -> str                    (one command for those fidelities)
  + FileEntry.is_listed, FileEntry.is_session_work              (answered for the selection the call names)
chat bar:  - flipped, - startStage, - commandOn, - shownStages/isPracticeOn/fidelities rules;  toggle = draw the answer
files app: - GuidanceSelector's three toggles collapse to one call;  - listedBy, filesShown, rootFilesShown, isSessionWork
```
**Callers affected.** `space/session/session.py` and its guidance selection, `space/kanban` fidelity progress (the command), both clients, their views and tests, the story tests for the chat bar and the Files app.
**Size.** About 16 files, 500 lines; removes roughly 200 lines of TypeScript.
**What could go wrong.** Both clients draw a press at once and correct it from the answer; with the flip in Python the press shows after one round trip (a fraction of a second locally) unless the client keeps drawing the flip itself, which is display and may stay. `space/session` is outside the area judged here, so its owner has to agree the new operations. A selection file written by the old chat bar must still read.

### D7. Apps, releases and the test cadence leave `harness/diagnostics`

**Problem.** `harness/diagnostics` holds four jobs (finding "harness/diagnostics (module)"). Modules that only want to register an app import the diagnostics module (`harness/files_app/files_app.py:7`, `space/kanban`), and diagnostics registers the Graph app on behalf of `harness/graph` (`app.py:492-495`). `AppPackage` and `AppPage` are built to be unpacked.

**Before**
```
harness/diagnostics: ServerHealth; AgentToolsProbe, GuidanceProbe, ProbeArguments, ProbeOutcome, CallDiagnostics
                     App(label, AppPackage, AppPage), Apps/APPS, AppServer, NodeScript, Npm, AppSources, PortProbe, GRAPH_APP
                     CddVersion, Release, CddRelease, ReleaseNotes, GitHubCli
                     TestCadence, TestRun, TestRunRecord, TestRunner, RunWorktree, DesktopWalkQuestion
```
**After**
```
harness/apps (after harness/mcp, before harness/graph):
     App(label, package: AppPackage, page: AppPage)      keeps both; status url open()
     ~ AppPackage  + install() + is_installed + is_current   (→ from App: stamps, npm, build)
     Apps/APPS, AppServer, NodeScript, Npm, AppSources, PortProbe
     - GRAPH_APP                                          → harness/graph registers it
harness/release:
     CddVersion, ~ Version (renamed from Release), CddRelease, ReleaseNotes, GitHubCli
     + ProjectVersion(pyproject)  read() write(version)   (the one reader and writer of the version line)
     TestCadence, TestRun, TestRunRecord (on JsonFile), TestRunner, RunWorktree, DesktopWalkQuestion
harness/diagnostics: ServerHealth (reads APPS, the cadence's latest runs, the e2e review), the probes
```
**Callers affected.** `files_app.py`, `space/kanban` app registration, `harness/graph/graph_app.py`, `server_health.py`, every `@cdd/harness/diagnostics/app` and `…/cdd-version` import in TypeScript (`harness/chat-ui/pane/hooks/health/app-client.ts`, `cdd-version-client.ts`, `shared` types, the Kanban app), `python -m harness.diagnostics.test_runs` in `/release`'s instructions and in `TestRunner.start` (`test_runs.py:429`), the root and module cards.
**Size.** About 30 files, mostly moved code and import lines; 150 lines of real change (`AppPackage.install`, `ProjectVersion`, `TestRunRecord` on `JsonFile`).
**What could go wrong.** MCP names (`app.open`, `cdd-version.check`, `server-health.report`) come from the toolset names and do not change, but the language adapter paths do, so every app and the mod must be rebuilt and reinstalled together. A background test run started by the old server calls the old module path; the first run after the move may be recorded as abandoned. `TestRunRecord` on `JsonFile` changes how two processes wait for the file: run the cadence heavy spec. This is the largest proposal here and the least urgent; it can be done as the move alone first.

### D8. One model of an end-to-end run, in TypeScript, and Python asks it

**Problem.** A run's files are read in three places with rules that already differ (finding under `harness/e2e_review/e2e_review.py`); `review.ts` and `report.ts` pass a run's folder into every function and avoid a cycle by reading the same files twice; Python's `E2eRun` reads them again as untyped dicts.

**Before**
```
e2e_review.py: E2eRun(folder)  rows -> list[dict]  verdicts -> dict  changed_steps  missed_steps  add_walked_step(5 params)
               E2eReview._baseline_of(sub_epic)   record_verdict(8 params, 3 branches)
review.ts:     baselineOf(dir) runsOf(dir) changedPairs(run, against) reviewOf(run) recordVerdict(run, against, key, review)
               judgeStep(run, key, verdict, reason) openPairs isReviewed acceptRun
report.ts:     previousRunOf(run) checkedRows(run) readRows(run) stepPairs(run, against)   [reads baseline.json, review.json itself]
```
**After**
```
report/run.ts (new, imports nothing from report.ts or review.ts):
     + SubEpicRuns(dir)   baseline: Run | undefined   runs: Run[]   accept(run, by)
     + Run(dir)           steps: StepRow[]  review: Review | undefined  previous: Run | undefined
                          pairsAgainst(other) changedAgainst(other) judge(key, verdict, reason)
                          recordVerdict(against, key, review)  addWalkedStep(step)  summary -> RunSummary (JSON)
review.ts:  ~ only the command line: pairs | verdict | judge | walk-step | accept | + summary
report.ts:  ~ only rendering; reads Run
e2e_review.py: ~ E2eRun  reads `summary` once through ReportTool (cached in changed.json as today)
               - rows, - verdicts, - add_walked_step's file writing, - _baseline_of
               ~ E2eReview  + judge_step(run, step, verdict, reason)  + record_walked_step(run, step, …)
                             ~ record_verdict(run, step, verdict, reason, cites, against)   (review verdicts only)
```
**Callers affected.** `e2e_review.py`, `e2e_review_spec.py`, `review.ts`, `report.ts`, both TypeScript specs, the step capture hook that writes `results.json`, the TDD guidance text that tells an agent which tool records which verdict, `REVIEW_AGENT_TOOLS` (e2e_review.py:37).
**Size.** 7 files, about 400 lines.
**What could go wrong.** `server-health.report` reads the latest review after every cdd call; it must not start Node, so the summary has to stay cached in a file as `changed.json` is today. Splitting `record_verdict` changes a published tool that a scheduled background agent calls by name; its prompt (`e2e_review.py:358-364`) changes in the same commit.

### D9. A new chat is one object in `harness/chat`

**Problem.** Four places describe "open a new chat on this folder with this first prompt" (finding under `chat.py:147-184`), and three of them call `links_of_run()` themselves. The opener reads a global to find the chat that asked.

**Before**
```
harness/chat: ChatLinks  open_new(folder, prompt) link_to_new(folder, prompt) hand_over(link)  [_join_opener_section reads CALLS_BEING_ANSWERED]
              links_of_run();  Chats(folder, opener)  open(folder, prompt)
space/repo:   NewChat(root, title, session)  first_prompt link instructions open()
space/kanban: Ticket.chat_link  -> links_of_run().link_to_new(worktree, prompt)
desktop_walk: (opener or links_of_run()).open_new(folder, prompt)
```
**After**
```
harness/chat: + NewChat(folder, prompt, opened_from: Chat | None)    link   open() -> str   (→ from ChatLinks.open_new / link_to_new)
              ~ ChatOpener (renamed from ChatLinks)   open(link)      ~ RecordedChatOpener
              ~ Chats  + new_chat(folder, prompt) -> NewChat   (hands in its opener and the chat the call came from)
                         open(folder, prompt) = self.new_chat(folder, prompt).open()
              - links_of_run as a public name (Chats.load() builds the opener)
space/repo:   ~ NewChat → RepositoryChat: keeps title, session, first_prompt, instructions; holds a harness NewChat for link and open
space/kanban: Ticket.chat_link -> Chats.load().new_chat(worktree, prompt).link
desktop_walk: Chats.load().new_chat(folder, prompt).open()
```
**Callers affected.** `chat.py`, `chat_spec.py`, `repos.py:64-95,225`, `ticket.py:565-574`, `desktop_walk.py:177-214`, their specs, the card.
**Size.** 8 files, about 180 lines. Chat's seam goes from 27 to about 22 of 66 with F2-F4 (limit 23).
**What could go wrong.** `desktop_walk` takes an opener as a constructor argument for its specs; it would take a `Chats` instead. The "join the opener's sidebar section" text is only added when a chat asked, which today is found from the global; `Chats.load` would have to be given the call (as `PromptQueue.load` is, `prompt_queue.py:134`), or the text is lost for links built by the board.

### D10. The mod's working state is kept in atoms

**Problem.** `harness/chat-ui/pane/hooks/board-chat/chat-turns.ts:7-14`, `chat-name.ts:8`, `chat-bar/check-in-client.ts:97` and `tools/prompt_queue/hooks/queue/prompt-queue.ts:125` keep state in module variables, which the mod pattern forbids because a reload empties them. Python works round the first (`harness/chat/chat.py:457-466`).

**Before**
```
chat-turns.ts:  let isBusy, turnsStarted, idleTicks; const unfinished: Map     functions with no $ read and write them
chat.py:        ChatMailbox.finish_worked_on(is_busy)   (finishes what a reloaded mod forgot)
```
**After**
```
types/index.d.ts:  + 'cdd-board'.chatTurns: { isBusy, turnsStarted, idleCheckIns, unfinished: Record<message, turnsBefore> }
                   + 'cdd-board'.chatName: string     + 'cdd-board'.failedCheckIns: number
chat-turns.ts:  ~ every function takes $ and reads or updates the atom
chat.py:        finish_worked_on stays until a heavy spec shows a reload no longer loses a message, then goes
```
**Callers affected.** `chat-turns.ts`, `chat-name.ts`, `check-in-client.ts`, `register.ts`, the mod's tests; `prompt-queue.ts:125-141` the same way.
**Size.** 6 files, about 120 lines.
**What could go wrong.** The check-in runs every second; reading atoms is asynchronous, so `isCheckInDue()` becomes `await`ed inside the clock callback and two callbacks can overlap, which module variables hid. `$.state` outlives a reload but `isBusy` must not: a mod reloaded mid-turn would come back still "busy", so the atom needs to be reset on `session.start`.

## Graph hits judged noise

Of the 143 mechanical hits in this area (97 distinct, since the report lists one block of them twice), these are noise. The rest are either covered by a finding above or are real but minor (the long `renderComparePage`, the 5-parameter `add_walked_step`, the `data` and `to` parameters, `_stamp`).

| File:line | Rule | Why it is noise |
|---|---|---|
| harness/files_app/app/files/failure-fixes.ts:33 | do-not-invent-parallel-object-models | `store`, `api` and `chat` are the collaborators `FilesNotices` hands on to the `FailureFixes` it builds, not a copied model. |
| harness/e2e_review/report/report.ts:762, :772, :775 | never-swallow-exceptions, use-typed-signatures, use-intention-revealing-names | `setMode`, `openAll` and `openTarget` are browser script inside the page template string (`PAGE_TEMPLATE`), not TypeScript of this module. |
| harness/e2e_review/report/report.ts:232, :411, :436, :517 | use-typed-signatures | Each parameter has a default value (`under = ''`, `from = shots.runDir`, `caption = ''`, `title = ''`, `withImages = true`), from which TypeScript takes the type. |
| harness/files_app/app/drawio-viewer.ts:50; files/files-paths.ts:25, :35; files/failure-fixes.ts:44; files/whiteboard-canvas.ts:18; tools/prompt_queue/hooks/queue/prompt-queue.ts:407; icon-button-view.tsx:49 | use-typed-signatures | The same: `project = ''`, `port = DRAWIO_PORT`, `isOnProblemLine = false`, `problem = ''`, `sentId = ''` are typed by their defaults. |
| harness/files_app/app/files/files-graph.ts:97 | never-swallow-exceptions | Each of the three catches shows the failure through `notices.fail` with its reason and context, and draws the problem on the page. |
| harness/files_app/app/files/files-page.ts:307 | never-swallow-exceptions | `readBeside` shows the failure through `notices.fail` and answers no file, which its caller draws as "did not open". |
| harness/files_app/app/files/files-theme.ts:142 | never-swallow-exceptions | `storedWrap` tells the failure through the `fail` it is given; a browser that refuses storage is an ordinary case. |
| tools/prompt_queue/hooks/queue/prompt-queue.ts:144 | never-swallow-exceptions | `changeQueue` shows the failure on the queue's failure line and answers `false`, which every caller checks. |
| harness/files_app/app/files/files-fold-keys.ts:52 | state-change-returns-record-or-named-failure | `read` keeps the keys and tells any problem through notices; nothing needs its answer. |
| tools/prompt_queue/hooks/queue/queue-view.tsx:83-362 (`e`), icon-button-view.tsx:87 (`x`) | use-intention-revealing-names | `e` is the engine's own name for a view's render argument in every mod example (`e.props.bodyColumns`); `x` is a coordinate. |
| tools/prompt_queue/hooks/queue/queue-view.tsx:147-362, icon-button-view.tsx:37; harness/files_app/app/files/file-source-view.tsx:36 | limit-operation-parameters | View functions and a React hook take what they draw; the rule is for domain operations. |
| harness/files_app/app/files/whiteboard-canvas.ts:62, :67, :81, :87; harness/e2e_review/report/report.ts:436 | use-intention-revealing-names | `id` and `value` in private helpers whose one job is converting that value; the real problem in `whiteboard-canvas.ts` is that the file exists (finding and D5). |
| harness/e2e_review/report/report.ts:163, :393, :426; harness/files_app/app/files/files-page-view.tsx:303 | provide-meaningful-context | Luma weights (0.299), the top of a colour channel (255), and layout fractions in drawing code; a name would say no more than the comment beside each. |
| harness/e2e_review/report/report.ts:252, :271, :294; review.ts:28, :50, :74 | keep-operations-single-responsibility | Flagged for mixing file reads with calculation; the real problem is that they take the folder as a parameter and read the same files twice (D8), not the mix inside each. |
| harness/e2e_review/e2e_review.py:200, :327; harness/diagnostics/app.py:144; tools/prompt_queue/prompt_queue.py:108 | limit-operation-parameters | Constructors and an exception's constructor, which take their collaborators or the context they report. |
| harness/e2e_review/e2e_review.py:299 `by` | use-intention-revealing-names | A published tool argument that reads as intended: `accept(run, by)`. |
| harness/files_app/app/files/files-graph.ts:59 | keep-classes-single-responsibility | Eleven public operations on the graph view's one object (read, filter, open, select); they share one purpose. The count is a lead, not a split. |
| tools/prompt_notify/.context/prompt-notify-model.md:1 `file`, `raw` | use-typed-signatures | A model document, not code. |
| harness/diagnostics/desktop_walk_question.py:102 `asked` | use-typed-signatures | A private helper reading the question file's dict; covered by the finding on the class, not a seam. |
