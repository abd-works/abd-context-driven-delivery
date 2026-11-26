# Judgment, round 2: harness applications and tools

Area: harness-apps-tools. The 100 production files of `harness/.context/editor-apps` (model-fidelity Python), `harness/apps`, `harness/diagnostics`, `harness/release`, `harness/design_canvas`, `harness/chat`, `harness/chat-ui/pane`, `harness/catalog_generator`, `harness/e2e_review`, `harness/files_app`, `tools/` (error_display, granola, prompt_log, prompt_notify, prompt_queue) and `scripts/` changed since 2026-11-21 (base `66f410de3`), judged at `5d16245ff` on release-1-2-fixes.

Read: every listed file in full at its current content, the module card and model of each module the files are in, the Clean Engineering code and model rules, `.claude/rules/coding.md`, the refactor guardrails, and, for the two Claude Code mods, the `cdd_claude_mod` pattern's rules. Read only: nothing was changed.

Method: as round 1. Each finding names the file and line it was checked at, and the whole file is judged, not only the changed lines. Tags: **[1]** module boundaries, **[2]** the same work done in different shapes, **[3]** resource orientation, **[4]** domain orientation. Every "no caller", "unused" or "only used inside" claim was checked with `git grep` over `*.py`, `*.ts`, `*.tsx` (and `*.ps1`, `*.sh`, `*.md` for scripts), leaving out specs, story tests and `.sessions`. "(still open from round 1)" marks the same rule and problem as a round-1 finding in the same file, or in the file it moved to (`harness/diagnostics/app.py` is now `harness/apps/app.py`; `test_runs.py`, `cdd_version.py` and `release.py` are now in `harness/release`). As in round 1, the mods' `$`-first plain functions are the pattern's prescribed form, and the diagnostics probes' keying by MCP name is accepted by `harness/diagnostics/.context/cdr/0001`; neither is a finding. `oss_portal_domain_driven` is left out. `scripts/` was not in round 1's area, so none of its findings is still open from round 1; `queue-order.ts` and `code-outline.ts`, which round 1 judged, are not in this round's list.

## Counts

| | Count |
|---|---|
| Files read | 100 |
| Findings | 189 |
| Findings still open from round 1 | 50 |
| New findings | 139 |
| Round-1 findings in these files now fixed | 61 |
| Round-1 findings withdrawn | 1 (`Chat.show` is an `@mcp` tool, which counts as use) |
| Design proposals | 18 |

Findings by part of the area:

| Part | Findings | Still open from round 1 |
|---|---|---|
| Editor-apps models, harness/apps, harness/diagnostics, harness/release, harness/design_canvas, harness/chat | 45 | 19 |
| harness/catalog_generator and harness/e2e_review | 43 | 9 |
| harness/chat-ui (the cdd-board mod) | 25 | 4 |
| harness/files_app | 24 | 6 |
| tools/ | 28 | 12 |
| scripts/ | 24 | 0 |

Findings by rule:

| Rule | Findings |
|---|---|
| eliminate-duplication | 43 |
| hold-state-on-the-object-not-in-parameters | 15 |
| use-explicit-dependencies | 10 |
| one-canonical-model-document | 8 |
| prefer-class-operations | 8 |
| use-consistent-naming | 8 |
| use-typed-signatures | 8 |
| contract-comes-from-the-adapter | 7 |
| seam-names-current-code | 6 |
| single-boundary | 6 |
| low-coupling | 5 |
| make-module-only-operations-private | 5 |
| delete-unused-operations | 4 |
| domain-lives-in-python | 4 |
| errors-out-of-existence | 4 |
| put-logic-on-the-owning-resource | 4 |
| use-intention-revealing-names | 4 |
| limit-comments | 3 |
| one-way-deps | 3 |
| refuse-unreadable-input | 3 |
| shape-classes-around-resources | 3 |
| use-exceptions-properly | 3 |
| do-not-invent-parallel-object-models | 2 |
| domain-exception-carries-context | 2 |
| limit-operation-parameters | 2 |
| no-legacy-api-after-refactor | 2 |
| state-change-returns-record-or-named-failure | 2 |
| avoid-vague-parameter-names | 1 |
| boot-only-in-register | 1 |
| class-not-property-instance-or-subtype | 1 |
| delete-unused-classes | 1 |
| domain-folder-in-the-mod | 1 |
| extensions-live-with-the-domain | 1 |
| hide-inner-details | 1 |
| keep-classes-single-responsibility | 1 |
| keep-operations-single-responsibility | 1 |
| limit-class-methods | 1 |
| mcp-call-follows-the-shared-rules | 1 |
| named-seam-and-constraint | 1 |
| never-swallow-exceptions | 1 |
| no-state-in-module-variables | 1 |
| use-property-not-accessor | 1 |

## Findings

### harness/.context/editor-apps (the increment's model, model-fidelity Python)

- module-context.md:13 Constraint against app.py, graph.py, guidance.py, practice_session_output.py, server_health.py, story_map.py, ticket.py — one-canonical-model-document — the card says "When implementation lands a class, its real module's card and model document take over and the entry here is removed"; every class in all seven files is implemented (`harness/apps/app.py`, `harness/graph/graph.py:1370`, `harness/guidance/guidance.py:308,515,528`, `space/session/practices/practice_session_output.py:175,351,391`, `harness/diagnostics/server_health.py:101`, `cdd_guidance/practices/stories/model/story_map.py:605,1341`, `opened_story_map.py:20`, `space/kanban/ticket_choices.py:77`), and each file was edited in this window (imports moved to `harness.apps.app`) instead of being removed. Each is a second model of a class its module already models. [2]
- app.py:1-116 `App`, `AppServer`, `AppNotStarted` — one-canonical-model-document — says it models "Module: harness/diagnostics" and itself names `Implemented: harness/apps/app.py`, then disagrees with that code: `App(label, folder, server, page)` against `App(label, package: AppPackage, page: AppPage)` (apps/app.py:436); a class-level `_registered` list and `App.registered()` against the `APPS` registry (apps/app.py:397-423); `AppServer(folder, script, ports)` against `AppServer(script: NodeScript, ports, probe, lane)` (:143); `AppNotStarted(self, "install", reason)` with three arguments against two (:67). A reader of the increment's model gets an `App` that does not exist. [2]
- server_health.py:1-18 `ServerHealth.apps` — one-canonical-model-document — the delta is implemented as written (`harness/diagnostics/server_health.py:101-105`) and lists deleted members (`kanban_app_port`, …) as if still pending; the entry should be gone. [2]
- guidance.py:8,15 `PracticeGuidance.editor: ClassVar[App | None]` — one-way-deps — the model has harness/guidance import `harness.apps.app`; the real class types it `ClassVar[Any]` (`harness/guidance/guidance.py:308-311`) precisely so guidance does not import the apps module. The model shows a dependency the code was written to avoid. [1]
- story_map.py:13 `from space.session.practices.practice_session_output import FidelitySessionOutput` — one-way-deps — the card's own Dependencies put `cdd_guidance/practices/stories` "above harness and below space", so a Stories model that imports space/session runs the wrong way. [1]
- ticket.py:12-17 `Ticket.choose_formats` — one-canonical-model-document — the operation lives on `TicketChoices` (`space/kanban/ticket_choices.py:77`), not `Ticket`; and practice_session_output.py:14 models one `FormatNotOfferedError` where the code has two classes of that name (`space/kanban/ticket_choices.py:22`, `space/session/practices/practice_session_output.py:251`; out of this area, noted for whoever judges space). [2]
- story_map.py:25-155 `StoryNode`, `StoryMap`, `Epic`, `Story`, `Scenario`, `Step` — one-canonical-model-document — `cdd_guidance/practices/stories/model/story_map.py` now holds these operations with its own model document; this file is the third description of the story map's edit seam beside that model and the code. [2]
- graph.py:10-18, practice_session_output.py:20-49 — one-canonical-model-document — `Graph.load_practice_roots`, `FidelitySessionOutput.chosen_formats/choose_format` and `PracticeSessionOutput.design_view` are implemented (`graph.py:1370`, `practice_session_output.py:175,351,391`); `design_view` is modelled as `CanvasVersions.in_practice_root(self.output_root).latest.link`, which the code and harness/design_canvas's card now say through *CanvasVersion*. [2]
- guidance.py:17-38 `session_roots`, `work_in`, `format` — one-canonical-model-document — implemented (`harness/guidance/guidance.py:515,528,728`) with a typed `PracticeOutput` / `FidelityOutput` where the model still says "typed Any as today". [2]
- .context/module-context.md:6 Seam — seam-names-current-code — lists "App, AppStatus, AppNotStarted, AppNotRegistered (harness/installation)"; they are in harness/apps, and its Dependencies line says "installation below diagnostics, guidance and graph" for a class that is no longer in either. [1]

### harness/apps/app.py

- app.py:436-441 `App.__init__` with :388-394 `AppPage` — shape-classes-around-resources — `AppPage` is still built only to be taken apart: `App` copies `page.server` into `_server` and `page.path` into a public `page` string and keeps neither the `AppPage`; it also copies `package.folder` into a public `folder` beside the `package` it now keeps. Installing has moved onto `AppPackage` (:320), which ends the rest of the round-1 finding. [3] (still open from round 1)
- app.py:64-70 `AppNotStarted` — use-intention-revealing-names — its docstring ("An app could not be installed") and its one raise (:503, wrapping `PackageNotInstalled`) are about an install that failed; the name says the app did not start. [4] (still open from round 1)
- app.py:143-147 `AppServer.__init__` — use-explicit-dependencies — builds `PortProbe()` and `ServerLane.from_home()` when none is given; `AppPackage.__init__` (:303) does the same with `Npm()`. [3] (still open from round 1)

### harness/diagnostics/server_health.py

- server_health.py:80-84 `ServerHealth.__init__` — use-explicit-dependencies — with no cadence or review handed in, it builds `TestCadence(TestRunRecord(default_record_folder(), main_checkout(...)))` and `E2eReview(...)` itself, so `load` (:88-90) can only ever report against the real cdd home. [3]
- server_health.py:95-99 `ServerHealth.report` — keep-operations-single-responsibility — a read named `report` also starts the overdue test tier (`self._cadence.start_due()`); every health-band refresh in every chat is therefore a possible process start, behind a name that says it reads. [3]

### harness/diagnostics/agent_tools_probe.py, guidance_probe.py, probe_arguments.py

- guidance_probe.py:109-124 `GuidanceProbe._action` — seam-names-current-code — calls each action in this process (`member(**arguments)`, `tool.invoke(arguments)`), while the card's Constraint says "Run a probe through the MCP host answering the diagnostics call … a probe that builds its own host checks code the chats do not run". The guidance probe checks code the chats do not run. [1]
- guidance_probe.py:115-124 against agent_tools_probe.py:176-185 `_called_with` — eliminate-duplication — the same steps written twice: refuse "needs " + missing names, call, `except Exception` → `raised_by_a_bug` re-raise → `ProbeOutcome.from_failure`, then `ProbeOutcome.from_answer(...).called_on(arguments...get("paths") or [])`; the `_ping_one`, `_instructions_of` and `_action_toolset` catches are three more copies of the middle part. [2]
- agent_tools_probe.py:65-71 `AgentToolsProbe.host` — use-explicit-dependencies — builds an `McpHost.from_refs(...)` itself when none was handed in; the module docstring gives the reason (specs and scripts), which is what a constructor argument is for. [3]
- agent_tools_probe.py:60-137 `project`, `host`, `toolset_refs`, `published`, `ping`, `invoke`, `heavy_invoke`; guidance_probe.py:44-61 `prefixes`, `matches` — make-module-only-operations-private — nothing outside the two files calls any of them (only `run`, `instructions`, `actions` and `from_filter` are called, from `agent_tools_diagnostics.py:28` and `guidance_diagnostics.py:28-29`); public fields `installer`, `slugs`, `arguments` likewise. [1]
- probe_arguments.py:73 `work_session -> Any` — use-typed-signatures — the probe's own session is returned untyped; its one caller (`guidance_probe.py:113`) passes it straight to a toolset constructor. [4] (still open from round 1)

### harness/release/cdd_version.py, project_version.py, release.py

- cdd_version.py:121-127 `CddVersion._next_version_from` with :22 `_VERSION_TEXT` — put-logic-on-the-owning-resource — what counts as a version text and what the next minor is are rules about *Version* (`project_version.py:228`), which already parses text (`from_text`) and tags (`from_tag`) with its own regex; here a third regex and the `current.minor + 1` arithmetic sit on the toolset. [3]
- cdd_version.py:91, :160-162, release.py:419-421 `ProjectVersion.of(...)` — hold-state-on-the-object-not-in-parameters (the guardrail "build once, keep it") — `CddVersion` builds a `ProjectVersion` of the checkout on every read of `_running` and of the project in `set_next`, and `CddRelease.version` builds one on every read of `version`, `tag` and `notes`; neither holds the project's version it is about. [3]
- cdd_version.py:118 `CddVersion.release` — use-explicit-dependencies — `self._release or CddRelease(self._project_git, GitHubCli(self._project), TestRunRecord(default_record_folder(), self._project))`: the release, the GitHub command line and the test-run record are built inside the operation when the constructor got none. [3]
- project_version.py:271-273 `ProjectVersion.read` — errors-out-of-existence — a `pyproject.toml` with no `version` line makes `VERSION_LINE.search(...)` answer `None`, and `.group(1)` raises `AttributeError`; the file that cannot be read as a version is not named, and `write` (:275-278) silently writes nothing back for the same file. [3]
- release.py:299 `COMPLETE_SESSIONS` — single-boundary — `.sessions/_complete` is where `space/kanban` moves a finished ticket's session; the framework reads that layout to write release notes. [1] (still open from round 1)
- release.py:300 — limit-comments — "The version line of pyproject.toml's [project] table: the one line /version rewrites and /release reads." sits above `RELEASE_TIERS`; the constant it described moved to `project_version.py:215`, and the comment stayed. [4]

### harness/release/test_runs.py

- test_runs.py:337-369 `TestRunRecord._read`, `_write`, `_while_busy` — eliminate-duplication — reads JSON, puts the file in place whole and retries while Windows holds it, which `JsonFile` does (`harness/installation/json_file.py`); `harness/chat/chat.py:556-563` `_while_windows_holds` is the third copy. The claim now uses `LockFile`, which ends the `claimed` half of the round-1 finding. [2] (still open from round 1)
- test_runs.py:508 `main_checkout`, :532 `_review_screens`, :716 `default_record_folder` — prefer-class-operations — module functions serving the record (`default_record_folder`, built in `server_health.py:82` and `cdd_version.py:118`), the cadence (`_review_screens`, used only as `TestCadence`'s default) and the checkout. `_counted_every_file_passed` and the run's folder name have moved onto `TestRun`. [3] (still open from round 1)
- test_runs.py:95-107 with :187-219 `TestRun` — eliminate-duplication — the same facts under two names each (`tier`/`name`, `outcome`/`state`, `started_at`/`started`, `_summary`/`summary`), and two ways out: `to_json` (:122) for the file and the data fields for the report. [2] (still open from round 1)
- test_runs.py:671-676 `TestCadence._reviewed` — use-exceptions-properly — `except Exception` turns any failure of the review, a bug included, into a "not started:" line of the run's summary. [3] (still open from round 1)
- test_runs.py:543-545 `TestCadence.__init__` — limit-operation-parameters — seven parameters, five of them test seams (`runner`, `git`, `clock`, `review`, `wait`, `say`), and it builds `TestRunner(record)` and `Git(self.checkout)` when none is given. [3] (still open from round 1)
- test_runs.py:381-385 `RunWorktree.__init__` — use-explicit-dependencies — builds its own `Git(self._checkout)` from the record's checkout, beside the `Git` the cadence already holds for that checkout (:551); a run's worktree cannot be handed a fake git, which is why the specs need the heavy tier for it. [3]

### harness/design_canvas/canvas.py and versions.py

- canvas.py:292 `artboard_stem` — prefer-class-operations — `Artboard.stem` (:277) now exists, but the module function stays public and is what the UX practice calls four times on plain path strings (`story_canvas.py:204,346,360,367`); the screen's prototype path is a string that is not an `Artboard`. [3] (still open from round 1)
- versions.py:349-351 with :442-448 `PublishedVersion` — domain-exception-carries-context — the exception carries no field, only a message string, and `unpublished` raises it also when there is no version at all ("no version is published"), a case that is not a published version. [4]
- .context/design_canvas-model.md:6-26 — one-canonical-model-document — the module's model still lists `add_board(name, board: dict, text)`, `write(root)`, `launch_page`, `artboards_in`/`holds` on *DesignCanvas*, a seam of `artboard(...)`, `box(...)`, `stem(...)`, `thumbnail(...)` and `look.py`, and no *CanvasProject*, *CanvasVersion*, *Place* or *CardLook*; the card beside it describes the code as it is, so the model and the card are two different designs. [2]

### harness/chat/chat.py

- chat.py:359-376 `Chat.title`, `Chat.is_connected` — make-module-only-operations-private — read only in this file (`NewChat._join_opener_section` :218-219, `Chats.list` :265, `ChatMailbox.queue` :398). [1] (still open from round 1)
- chat.py:135-144 `ChatsFolder`, `CHATS_FOLDER` — single-boundary — `tools/prompt_queue/prompt_queue.py:18,381,391` imports the folder and builds `CHATS_FOLDER.path / chat / QUEUE_FILE` itself, so the layout of a chat's own folder is known in two modules. [1] (still open from round 1)
- chat.py:274-277 `Chat.clock`, `Chat.kept_messages` — use-explicit-dependencies — class-level values that specs replace on the class (`chat_spec.py:54`, `chat_heavy_spec.py:41`), shared by every chat in the process. [3] (still open from round 1)
- chat.py:282-284, :390-392, :504-506 `ChatMailbox.__init__(chat, folder)`, `ChatStateFile.__init__(chat, file)` — hold-state-on-the-object-not-in-parameters — each is given the chat and, again, the folder or file the chat already holds. [3] (still open from round 1)
- chat.py:414-466 `ChatMailbox.confirm/finish/resend/finish_worked_on` — shape-classes-around-resources — a message's life is changed by the mailbox editing raw dicts read from each file; `ChatMessage` (:103) is a read-only view built afterwards; the states are defined twice (constants and tuple :35-40, `MessageState` Literal :52). [3] (still open from round 1)
- chat.py:274 `load(chat: str)`, :317-347 `message: str` — use-intention-revealing-names — `chat` and `message` hold ids while `Chat` and `ChatMessage` are the objects. [4] (still open from round 1)
- chat.py:279 `_folder` against :370 `folder` — use-consistent-naming — the chat's own folder under the chats folder, and the folder the chat works in: one word, two things, on one class. [4] (still open from round 1)
- chat.py:556-563 `ChatStateFile._while_windows_holds` — eliminate-duplication — repeats the retry on a held file that `JsonFile` and `TestRunRecord._while_busy` (`harness/release/test_runs.py:359-369`) each write. [2] (still open from round 1)
- chat.py:535-545 `ChatStateFile._read_once` — refuse-unreadable-input — catches `JsonFileUnreadable` and answers `{}` for a state file that does not parse; the next check-in then writes over it. The docstring argues the overwrite is harmless, but the checked rule reads the catch as reading an unreadable file as empty, and `title_state` (:520) loses the kept title and transcript the same way. [3]
- chat.py:280-281 `Chat.mailbox` — hide-inner-details — a public field other modules call through (`space/session/session.py:149` `added_to.mailbox.queue("fill", text)`, `space/session/files/file_comments.py:110,254`), so there are two ways to send a chat a command: the published `Chat.send` (:288) and `chat.mailbox.queue`, which answers the message that `send` drops. [1]

### harness/catalog_generator/catalog_generator.py

- catalog_generator.py:620 `Catalog.__init__` — use-explicit-dependencies — with no project given it builds `CatalogProject(Path.cwd())`, the folder the process happens to run in. The card's Constraint says "Take the project from the call … or the constructor, never this module's own folder"; no caller uses the default (`Catalog.load` at :633 and `generate_cdd_catalog.py:85` both pass one), so it only exists to act on the wrong project silently. [3]
- catalog_generator.py:679-681, :869, :878 with approach_page.py:368 `Catalog.board`, `ApproachPage.__init__` — put-logic-on-the-owning-resource — the card says "the catalog board (*HubBoard*) and the approach page both draw that one approach", but `board` is a property that builds a new `ApproachGrids` and `CatalogExamples` on every access, and each `ApproachPage` builds its own `ApproachGrids` again from the same practices and copy. One render makes the approach at least twice; the board and the page can disagree if either is built from different examples (`:869` and `:878` already pass different `CatalogExamples`). [3]
- catalog_generator.py:162-168 `FidelityTemplate.body` — never-swallow-exceptions — catches `OSError`, logs it at debug level and answers `""`. Its caller has already checked the file exists (`_template`, :362), so the catch only turns an unreadable template into an empty code fence on the page. [3]
- catalog_generator.py:506 `CatalogProject.generate_with_own_guidance(out_root, brand)` — hold-state-on-the-object-not-in-parameters — `out_root` is the project's own `out_root` (:481); the only caller (:700) passes `self.out_root`, which is `self.project.out_root`. [3]
- catalog_generator.py:143, :296, :343, :359 `FidelityTemplate.fidelity`, `FidelityPage.fidelity` — use-consistent-naming — on `FidelityTemplate` the name holds a `FidelityGuidance`, on `FidelityPage` a `CatalogFidelity`, so the page reads `self.fidelity.fidelity.section` and `self.fidelity.fidelity.default_format`. The same word names the guidance and the catalog's view of it. [4]
- catalog_generator.py:281, :302, :923 with catalog_practice.py:202 `CatalogPractice.fidelity_href(fidelity)` — hold-state-on-the-object-not-in-parameters — every caller holds a `CatalogFidelity`, unwraps it (`shown.fidelity`) and hands the guidance back to the practice that made the `CatalogFidelity` and is held by it (`catalog_examples.py:266`). The same is done at approach_page.py:356, hub_board.py:213 and space/kanban/board.py:792: six call sites pass state the object already holds. [3]
- catalog_generator.py:744-750 `Catalog.configure_project_approach` — eliminate-duplication (and the guardrail "the framework does not know the practices") — the instruction writes out by hand the five practices and the name of each one's fidelity at each stage (`stories | story map | scenarios | acceptance tests`, …). The catalog already holds that answer (`CatalogPractice.board_fidelities`, `STAGE_COLUMNS`); a practice added or renamed leaves the table an agent follows wrong. [1]
- catalog_generator.py:644 `repo_url`, :679 `board`, :684 `brands`, :783 `write_page` — make-module-only-operations-private — public on the `Catalog` toolset, read only inside catalog_generator.py (`write_page` six times, `repo_url` at :703, :816, :848; `brands` at :714; `board` at :794). The card's seam is `Catalog` and its four MCP operations. [1]
- catalog_generator.py:459 `CatalogNotGenerated` — domain-exception-carries-context — a bare `Exception` subclass with only a message string; the project folder and the generator's output it reports are pasted into the text (:520-526), so a caller cannot read which project failed or why. [4]

### harness/catalog_generator/catalog_practice.py

- catalog_practice.py:28 `giving_stage_examples` — prefer-class-operations — a module function over a list of `CatalogPractice`, used once (`approach_page.py:185`). [3] (still open from round 1)
- catalog_practice.py:117 `_card_of -> dict[str, Any]` — use-typed-signatures — the catalog card is an untyped dict read through six properties by string key. [4] (still open from round 1)
- catalog_practice.py:118 `_card_of` — low-coupling — reads `getattr(practice_class, "catalog_card", None)`, an attribute `PracticeGuidance` does not declare (no `catalog_card` anywhere under `harness/guidance`); the five practices each define a dict of their own (`bdd.py:34`, `clean_engineering.py:37`, `ddd.py:63`, `stories.py:70`, `ux.py:94`). The seam between the catalog and a practice is a name both sides spell by hand, and a misspelled key falls back to `_CARD_DEFAULTS` without a word. [1]
- catalog_practice.py:40, :56-60 `CatalogSkills._FOLDERS` — use-explicit-dependencies — a class-level dict every `CatalogSkills` in the process reads and writes, so the skill folder one catalog worked out answers every later catalog; specs cannot give one catalog its own. The docstring makes it a cache by design, but it is state on the class, not on the object that was handed the install. [3]

### harness/catalog_generator/catalog_examples.py

- catalog_examples.py:247 `ExampleFile._panel_image_classes` — eliminate-duplication — `stem.replace("-", "_") == "story_map"` is the same test as `DrawioDiagram.is_story_map` (`drawio_diagram.py:38`). [2] (still open from round 1)
- catalog_examples.py:47, :239-249 `_ROOT_CLASS_LINE`, `_panel_image_classes` — extensions-live-with-the-domain (the guardrail "the framework does not know the practices") — the framework names the aggregate root of one DDD example (`"export class Customer"`, which is `cdd_guidance/practices/ddd/catalog-examples/tactics.ts:27`) and the file stems of other practices' fidelities (`bounded-context`, `model`, `front-end-code`, `story_map`) to choose how a panel shows them. Renaming the DDD example or a fidelity's file changes the catalog's look with no error. The practice's catalog card is where a practice already tells the catalog how it is shown. [1]
- catalog_examples.py:333, :343, :346 with approach_page.py:291, :299, :422 `ExampleFile` — put-logic-on-the-owning-resource — `CatalogFidelity.example_files` answers bare `Path`s, so an `ExampleFile` is built afresh for each sort key (`_display_order`, called once per file per sort), again in `_preferred`, again in `examples_html`, and again by the approach page. The fidelity's examples are the fidelity's parts and can be built once and kept. [3]
- catalog_examples.py:383 `StageExample.__init__(self, stage, …)` — use-typed-signatures — `stage` has no type (it is a `StageCopy`). [4]
- catalog_examples.py:161, :185, :195 and :197, :215 `ExampleFile.panel_html`, `stage_page_html`, `_figure_inner`, `_scrolled_page_html` — eliminate-duplication — the markdown preview (`<div class="skill-md-preview">{ExampleMarkdown(text).html}</div>`) is written three times and the sandboxed `srcdoc` frame of an HTML example twice, each with its own escaping call. [2]

### harness/catalog_generator/approach_page.py

- approach_page.py:179-183, :364-368, :287, :407, :484 `ApproachGrids`, `ApproachPage` — hold-state-on-the-object-not-in-parameters — both classes take a `CatalogExamples` and take it apart into `catalog_root` and `project_examples`; then `StageExample(stage, stories, project_examples)` is built from those parts in three places here and twice more in `hub_board.py:199,255`, each handing in the practice and the project examples the approach already holds. The approach can answer a stage's example. [3]
- approach_page.py:193-201 `ApproachGrids.html(kind)` — errors-out-of-existence — any `kind` other than `windows`, `descriptions` or `spec` draws the ticket grid, so a principle in the approach copy with a misspelled kind silently shows the library board instead of failing. [4]

### harness/e2e_review/e2e_review.py

- e2e_review.py:28, :260, :322-325 `BASELINE_FILE`, `E2eReview.baseline_of`, `changed_pairs` — do-not-invent-parallel-object-models — the card says "*E2eRun* reads that summary once" and the run's model is TypeScript's, but Python still reads `baseline.json` itself and resolves both screenshots of each pair again. The two rules still differ: `SubEpicRuns.baseline` (run.ts:90-95) answers none when the accepted run's folder is gone, `baseline_of` answers a path that is not there, which `changed_pairs` then joins screenshot names onto. [2] (still open from round 1)
- e2e_review.py:35-36 `WALK_VERDICTS`, `REVIEW_VERDICTS` with run.ts:22-24, :83 — eliminate-duplication — the verdict words are written in both languages, and Python refuses a verdict before `review.ts` is asked, so the TypeScript check that the card names as the one place for the verdict rules never runs from the tools. [2] (still open from round 1)
- e2e_review.py:254 `changed_pairs -> list[dict]` — use-typed-signatures — a pair is a dict with string keys on a published seam; `StepPair` exists in run.ts:61 and has no Python counterpart. [4] (still open from round 1)
- e2e_review.py:69-76 `E2eRun.folder` and `run_folder`; :145 `E2eRunReview.run` and :181 `review_id` — use-consistent-naming — each pair is one value under two names (`run_folder` returns `self.folder`; `run` and `review_id` both return `self._name`). [4] (still open from round 1)
- e2e_review.py:382 `_start_in_background`, :387 `_start_review_agent` — prefer-class-operations — module functions each serving one class (`E2eReview` and `ScheduledReview`) as their default starter. `_stamp` moved onto `E2eReview`; these two did not. [3] (still open from round 1)
- e2e_review.py:243 with harness/release/test_runs.py:168 — eliminate-duplication — a run folder's name, `run-` plus `RUN_STAMP_FORMAT`, is still put together in two modules; the format and the scheduled release are now shared, the prefix is not. [2] (still open from round 1)
- e2e_review.py:391 `_start_review_agent` — one-way-deps — imports `ClaudePlugins` inside the function; `harness/mcp/claude_plugins.py` imports nothing from this module (its imports are `ide_layout`, `json_file`, `cdd_home`), so there is no cycle to hide and the import can go to the top. [1]
- e2e_review.py:389-390 with :368-370 `_start_review_agent`, `ScheduledReview.start` — errors-out-of-existence — when `CDD_AGENT_RUNS_OFF` is set the function returns without starting anything, and `start` still adds "review agent started on N run(s)" to what it reports. The caller is told work was done that was not. [4]
- e2e_review.py:396 `_start_review_agent` — eliminate-duplication — builds `checkout / ".sessions" / ScheduledReview.RELEASE / RESULTS_FOLDER`, which is `E2eReview(checkout, "scheduled").results_root` (:205-206) written again. [2]
- e2e_review.py:38 `REVIEW_AGENT_TOOLS` — eliminate-duplication — spells out the installed MCP names (`mcp__plugin_cdd_cdd__e2e-review_changed_pairs`, …) by hand; the installer derives those names from the toolset and the plugin, so a rename of the plugin or the toolset leaves the scheduled agent with no tools it can call. [2]
- e2e_review.py:294 `_step_verdict(given_by, run, verdict, command, *arguments)` — limit-operation-parameters — four named values plus two to five packed ones; `verdict` is passed twice (once named and again inside `arguments`, :285, :292), and `given_by` and `command` are two words for one choice (judge or walk). [3]
- e2e_review.py:363 `ScheduledReview.start` — hold-state-on-the-object-not-in-parameters — holds the `E2eRun` and hands `changed_pairs` its folder as a string, which `changed_pairs` turns back into an `E2eRun` through `run_of`; `changed_pairs` itself calls `run_of(against)` twice (:258, :260). [3]
- e2e_review.py:195-196, :345-346 `E2eReview.__init__`, `ScheduledReview.__init__` — use-explicit-dependencies — build their collaborators when none is given (`ReportTool()`, `_start_in_background`, `E2eReview(checkout, …)`, `_start_review_agent`); `ReportTool` is the boundary to Node, the external system the card names. [3]
- e2e_review.py:208 `sub_epic_folder`, :215 `run_of` — make-module-only-operations-private — public on the toolset, called only inside this file (and absent from the card's seam). [1]

### harness/e2e_review/report/run.ts

- run.ts:260 `Run.isReviewed` — delete-unused-operations — no caller in production code. [1]
- run.ts:200, :255 against :261, :272 and report.ts:88 `checkedSteps`, `openPairs`, `isReviewed`, `summary` — eliminate-duplication — "which verdicts apply to this comparison" is written four times: `checkedSteps`, `openPairs` and `renderComparePage` keep only a review made against the same run (`review?.against === …`), while `isReviewed` and `summary` take every verdict in `review.json`. So `summary`'s `missed_steps`, which the health report toasts, counts "missed by the tests" verdicts from a review against an earlier baseline. [2]
- run.ts:218-237 `Run.judge`, `Run.addWalkedStep` — eliminate-duplication — the meets-or-misses check is written in each; `judge` refuses an empty reason and `addWalkedStep` does not, though the tool for a walked step asks for the reason too (e2e_review.py:291). [2]

### harness/e2e_review/report/review.ts

- review.ts:53 `accept` command — errors-out-of-existence — `by ?? 'unknown'` accepts a baseline in nobody's name when `--by` is missing, though the card's Constraint is that only the person accepts and `accept` takes their name. The call should be refused. [4]

### harness/e2e_review/report/report.ts

- report.ts:37-44 `writeHistoryReport`, :119 `renderSummaryMarkdown` — delete-unused-operations — no caller in production code; `renderSummaryMarkdown` is reached only through it. [1]
- report.ts:79, :375, :657 `renderComparePage`, `renderPage`, the command line — eliminate-duplication — a run's sub-epic, and the results root three folders up, are worked out from its folder path again each time (`path.dirname(path.dirname(runDir))`, `path.resolve(run.dir, '..', '..', '..')`), though `Run.subEpic` (run.ts:136) holds it. `renderPage` takes `runDir: string` rather than the `Run` its callers hold. [2]
- report.ts:318 `renderStep` — hold-state-on-the-object-not-in-parameters — rebuilds the previous run's folder from the run name a step row carries (`path.join(path.dirname(shots.runDir), step.previous)`); `Run.previous` already holds that run, and the guess is wrong whenever the previous run is a baseline under another folder. [3]
- report.ts:133 `runFolders` — eliminate-duplication — a third walk of the results tree for folders holding `results.json`, beside `SubEpicRuns.runs` (run.ts:98) and `E2eReview.latest` (e2e_review.py:315). [2]
- report.ts:110, :382, :414 — eliminate-duplication — the totals line and its "written … UTC" stamp are put together three times, two of them word for word. [2]

### harness/chat-ui/pane/hooks/board-chat/board.ts

- board.ts:40-43 `post` — state-change-returns-record-or-named-failure — always answers `ok: true` (a failed call throws from `callToolText` instead), so the `answer.ok ? … : []` branch in `chat-bar/check-in-client.ts:127` can never take its second arm; the result shape promises a refusal it never gives. [4] (still open from round 1)

### harness/chat-ui/pane/hooks/chat-bar/check-in-client.ts

- check-in-client.ts:91-93 `failureSentIn` — hold-state-on-the-object-not-in-parameters — a page's failure and its context reach the chat bar written as JSON into a command's `text` (`harness/files_app/app/files-server.ts:89`, `files/files-notices.ts:47` send `JSON.stringify({ failure, context })`; `harness/chat/chat.py:50,301` define the `failure` kind that way) and are parsed back here with an unguarded `JSON.parse`. State is written into a string and read back; a text that is not that JSON throws out of `run`, and `keepInTouch` counts it as a failed check-in rather than naming the bad message. [3]
- check-in-client.ts:101-113 `keepInTouch(…, isCheckIn)` — seam-names-current-code — the comment says that between an idle chat's check-ins it reads the selection; with `isCheckIn` false the body returns at once and reads nothing (the selection is followed by `followGuidance`, `guidance-client.ts:28`). The flag only stands in for the caller not calling (`register.ts:100`). [4]

### harness/chat-ui/pane/hooks/register.ts

- register.ts:48 `shownContext` — no-state-in-module-variables (mod pattern) — the last agent context the system prompt held is a module variable, which a reload empties, so a reloaded mod invalidates the prompt section once more for nothing; every other value the mod keeps between events moved to atoms in this round (`chatTurns`, `chatName`, `failedCheckIns`). [3]
- register.ts:52-90, :171-192 `showStatus`, `readActive`, `readBoardAfterStart`, `readBoardAfterTurn`, `readBoardAfterSubmit`, the `openApp` query — boot-only-in-register (mod pattern) — the file the pattern keeps to connecting events holds the bar's read sequences (read the board, the status line, the overlay choices, the prompt invalidation, the install, the version) and the rule for which query an app page opens with. [1]
- register.ts:74, :75, :83, :88; chat-bar-view.tsx:27 — seam-names-current-code — the failure contexts tell the person the bar was "calling board.show", but the bar calls `board.overview` (`chat-bar-client.ts:285`); the draw comment says the client is "built from board.show". [4]
- register.ts:80-81 `readBoardAfterTurn(…, isMainChat)` — use-consistent-naming — the flag is `!e.agentId`, the chat's own turn as against a sub-agent's; everywhere else in the mod "main" is the main session (`chat-bar-client.ts:22` `MAIN_SESSION`, `:54` `isMain`), so `turnCompleted` reads as skipped in ticket chats, which it is not. [4]
- register.ts:183-187 with board.ts:23-34 — use-consistent-naming — "the project a page opens on" has two answers: `projectPageUrl` sets `project` to the git top level (`checkoutFolder`), and the status row's `openApp` overwrites it with `$.session.root()`. A chat started in a subfolder of a repository opens the Graph and Story UI on that subfolder and the Files app and board pages (`fidelity-files-client.ts:32,44`) on the repository. [2]

### harness/chat-ui/pane/hooks/chat-bar/fidelity-progress-client.ts

- fidelity-progress-client.ts:1-2, :9, :11 — no-legacy-api-after-refactor — `atom`, `read`, `update`, `EngineInterface`, `post` and `clearChosenAction` are imported and never used in the file; they are what `commandOn` used before it was removed. [1]
- fidelity-progress-client.ts:121-123 `STATES_BY_PROGRESS` — domain-lives-in-python (mod pattern) — the order "violations count as less done than work under way" is a rule about progress, decided in the mod, and `PracticeDotClient.least` (140-143) picks a practice's state with it. [1] (still open from round 1)

### harness/chat-ui/pane/hooks/chat-bar/action-button-view.tsx

- action-button-view.tsx:18-31 `actionOf`, `shownActionOf`, with chat-bar-client.ts:177-180 `actionFidelity` — domain-lives-in-python (mod pattern; also views-render-only) — which action the bar offers is decided in a view file: advance once the ticket is done, else the action fidelity's next, else `generate`, partition never by default; and the action fidelity is "the ticket's next among those selected, else the first". `FidelityProgress.next_action` already answers next; the fallback and the choice of fidelity are rules the agent's own tools do not see. [1]
- action-button-view.tsx:37-43 `pressAction` with overlay-choices-client.ts:32-35 `overlayArgumentOf` — hold-state-on-the-object-not-in-parameters — the command the session's guidance selection writes (`chatBar.commandOf`, `GuidanceSelection.commands`) is lengthened in the mod with ` overlays=a,b` built from the overlay chips, so the command Python holds and the one the person sends differ, and the overlays are state written into a string. [3]

### harness/chat-ui/pane/hooks/chat-bar/overlay-choices-client.ts

- overlay-choices-client.ts:52-60 `toggleOverlay` — eliminate-duplication — works out the new overlay list in the mod and sends it whole to `ticket.choose_overlays`, the press shape this round removed for stages, practices and formats by moving the toggle into `session.toggle_guidance` (`guidance-client.ts:54-62`). Overlays are also addressed by the ticket's name (`ticket: chatBar.sessionName`) while the rest of the selection is addressed by the session file. [2]

### harness/chat-ui/pane/hooks/chat-bar/chat-bar-client.ts

- chat-bar-client.ts:159-161 `formatChoices` — contract-comes-from-the-adapter — converts the selection's formats (`GuidanceSelectionData.formats`) into the hand-kept `FormatChoiceJson`, filling `made: 0`; no TypeScript reads `made` (`git grep '\bmade\b'`), and the view's comment (`chat-bar-view.tsx:197-199`) promises a chip "green when every fidelity has a file in it already", which can never draw. [2]
- chat-bar-client.ts:241-244 `MoveRefused`, :342-351 `moveNext`'s answer — delete-unused-classes — `moveNext` answers the new client or a `MoveRefused`, and its one caller (`action-button-view.tsx:40`) returns it to a press handler that discards it; the refusal is already shown through `shownAsFailure`. Nothing reads the class. [1]

### harness/chat-ui/pane/hooks/chat-bar/format-choices-client.ts

- format-choices-client.ts:6-10 `FormatChips`, `currentFormatChips` — class-not-property-instance-or-subtype — a type and a file that wrap `chatBar.formatChoices` in `{ choices }` and add nothing; `register.ts:202` and the view could read the property. [4]

### harness/chat-ui/pane/hooks/chat-bar/chat-bar-view.tsx

- chat-bar-view.tsx:93 `toggleGuidance(…, 'stage', stage.stage.toLowerCase())` — use-consistent-naming — the selection answers stages by title (`space/session/practices/guidance_selection.py:198-202`, `covered_stages`) and toggles them by name, so the mod rebuilds a stage's name by lower-casing its title; a stage whose name is not its lower-cased title cannot be toggled from the bar. [4]
- chat-bar-view.tsx:219-220, :258-262; chat-bar-client.ts:101-104; types/index.d.ts:79-81 — limit-comments — comments that describe other code: the overlay chip "its first and last letter" (it draws `choice.icon`), the line's layout above `RepositoryRequiredView` rather than `LineView`, two orphaned sentences ("Every action a person can run…", "The ticket the session works on, by name") above `designView`, and the action picker's comments above `FormatChoiceJson`. [4]

### harness/chat-ui/pane/hooks/chat-bar/fidelity-files-client.ts

- fidelity-files-client.ts:24-51 `openBoardPage`, `openFilesLink`, `openBoardLink` — eliminate-duplication — the first two are one body (find the server's url or show a failure, build the page link naming the chat, open it in the Browser pane, show why not) with different first steps, and `openBoardLink` only forwards to `openBoardPage`. [2]

### harness/chat-ui/pane/hooks/health/app-client.ts

- app-client.ts:46-52 `installedApp` — mcp-call-follows-the-shared-rules (mod pattern) — calls `callToolText` and `JSON.parse`s the answer itself, beside the shared `callTool` (`shared/cdd-tool.ts:24-31`) every other client uses; a reply that is not JSON throws a bare `SyntaxError` here where `callTool` throws `CddToolFailed` naming the tool. "Still running" is recognised by the first words of the server's text. [2]

### harness/chat-ui/pane/hooks/repo/repo-client.ts

- repo-client.ts:64 `pushTo` with types/index.d.ts:33 `ToMainJson` — use-intention-revealing-names — a push that went through is recorded as state `'installed'`, because `ToMainJson.state` borrows `InstallJson['state']`. [4]

### harness/chat-ui/pane/hooks/health/server-health-client.ts

- server-health-client.ts:50 `appLabelled` — delete-unused-operations — no caller anywhere (`git grep appLabelled`). [1]
- server-health-client.ts:55-67 `testRuns`, `e2eReview` — contract-comes-from-the-adapter — cast the report to `{ test_runs?: TestRunJson[] }` and `{ e2e_review?: E2eReviewJson }`, though `ServerHealthData` already types both fields (`test_runs: TestRunData[]`, `e2e_review: E2eRunReviewData | null`, `.claude/language-adapters/typescript/harness/diagnostics/server-health.ts:6-29`). [2]

### harness/chat-ui/pane/types/index.d.ts

- index.d.ts:16 `TestRunJson`, :23 `E2eReviewJson` — contract-comes-from-the-adapter — hand copies of `TestRunData` and `E2eRunReviewData`, which the adapter generates; read by `server-health-client.ts:7` and `server-health-wording.ts:4`. (`DesktopWalkQuestionJson` went with the desktop walk.) [2] (still open from round 1)
- index.d.ts:77 `RepoRowJson`, :82 `FormatChoiceJson`, :85 `OverlayChoiceJson` — contract-comes-from-the-adapter — field copies of what `repos.siblings`, `ticket.format_choices` and `ticket.overlay_choices` answer; the adapter generates `FormatChoiceData` and `OverlayChoiceData` (`.claude/language-adapters/typescript/space/kanban/ticket.ts:14,22`). [2] (still open from round 1)

No findings in chat-name.ts, chat-turns.ts, changed-artifact-client.ts, guidance-client.ts, session-card-view.tsx, cdd-version-client.ts, server-health-wording.ts beyond the type imports counted above.

### harness/files_app/.context/files-app-model.md

- files-app-model.md:22-27 `FilesPage` — seam-names-current-code — the model still describes `readPractices()`, `isFollowingChatBar`, `isShown(practice)`, a read of the practices "every second", `Chat.show` (`selected_fidelities`) and `Chat.select`, and `Session.update_guidance_selection`; none is in `files-page.ts` or `guidance-selector.ts` (grep finds no `isFollowingChatBar`, `readPractices`, `updateGuidanceSelection`), `harness/chat/chat.py` has no `select`, and the page now presses `Session.toggle_guidance` (`guidance-selector.ts:293-300`). The canonical model of the module describes a page that no longer exists. [1]

### harness/files_app/app/files-server.ts

- files-server.ts:53-58 `ProjectFolderMissingError`, :62-66 `connectionOf` — eliminate-duplication — the same class, with the same message word for word, is exported by the generated connection (`harness/installation/templates/typescript/cdd-connection.ts:32-37`), which makes the same `statSync(...).isDirectory()` check (`cdd-connection.ts:177`). The server's `REFUSALS` (:68) lists only its own class, so a missing folder the connection meets, rather than `connectionOf`, is answered as a 500 failure instead of a 400 refusal. Two classes for one failure means an `instanceof` against either misses the other. [2]

### harness/files_app/app/files/files-link.ts

- files-link.ts:29 `FilesLink` (`sessionFile`) — single-boundary — when a link names no `session`, the page builds `.sessions/<ticket>/session.json` itself: where a ticket's session file lives is `space/session`'s layout, written again in the page. [1]

### harness/files_app/app/files/failure-fixes.ts

- failure-fixes.ts:11 `FailureKindName` — contract-comes-from-the-adapter — the six kind names of `tools/error_display/failure.py` typed out by hand; the adapter types `kind` as `string` (`.claude/language-adapters/typescript/tools/error_display/failure.ts:8`), so a kind renamed in Python still type-checks here. `format-alignment.ts:11` `FailureBand` types a third, narrower copy (`'render' | ''`). [2] (still open from round 1)
- failure-fixes.ts:61 `dismiss(failure)`, :67 `fix(failure)`, :83 `changed(failure, …)` — hold-state-on-the-object-not-in-parameters — a shown failure is found again by its message text each time (`shown.failure === failure`); the band view that calls already holds the `ShownFailure`. [3] (still open from round 1)

### harness/files_app/app/files/files-notices.ts

- files-notices.ts:13-51 `FilesNotices` — eliminate-duplication — keeps its own set of failures told, its own `tellChat` sending `chat.send('failure', …)`, and its own "chat was not told" toast; the Graph app, the Kanban board and the story map now share that in the generated `ChatToldFailures` (`harness/installation/templates/typescript/cdd-page-failures.ts:10-47`; `harness/graph/app/graph/graph-failures.ts:19`, `space/kanban/app/src/kanban/board/page-failures.ts`). The Files app is the one page that still writes it again. [2] (still open from round 1)

### harness/files_app/app/files/reason.ts

- reason.ts:2 `reasonOf`, :5 `saidBy` — eliminate-duplication — the folder's nine copies are now one file (fixed), but `reasonOf` is the generated `cdd-page-failures.ts:5` word for word, and further copies remain inline: `files-server.ts:70` `textOf`, `files-page-view.tsx:594` and `:599`, `files-graph-view.tsx:313`, `file-view.tsx:66` (`(failure as Error).message`). `saidBy` has a second body in `harness/chat-ui/pane/hooks/shared/browser-pane.ts:21`. [2]

### harness/files_app/app/files/format-chips.ts

- format-chips.ts:3-5 `FORMAT_GLYPHS`, `formatGlyphOf` — eliminate-duplication — still a copy of `harness/chat-ui/pane/hooks/chat-bar/bar-columns.ts:9-10` (the fallbacks now agree), kept equal only by the comment. [2] (still open from round 1)

### harness/files_app/app/files/files-page-view.tsx

- files-page-view.tsx:444 `STAGE_ICONS` — eliminate-duplication — copied from `harness/chat-ui/pane/hooks/chat-bar/stage-client.ts:7`, as the comment at :442 says, and already different: the chat bar has `Backlog` and `Complete` and falls back to `·`, this one falls back to the stage's title. The same split as `FORMAT_GLYPHS`. [2]
- files-page-view.tsx:19 `fileNameOf` — eliminate-duplication — "the last name of a path" written four times in the folder: here, `source-of-file.ts:13`, `file-bar.ts:15` `nameOf`, and inline in `chat-context.ts:16`. [2]
- files-page-view.tsx:75-78 `BoardLinkView.open` and :100-103 `PublishedFileView.open` — eliminate-duplication — the same body word for word (prevent default, `page.openPublished(entry)`, else `window.open(published.link…)`). [2]
- files-page-view.tsx:154-155 and :442-449 — limit-comments — comments left above the wrong declarations: "A right-click on a file or folder: its menu" sits over `wrapFailed`, not `menuOn`; "A button for each stage…" sits over `ScopeTogglesView`, not `StageTogglesView`, which has none. [4]

### harness/files_app/app/files/file-bar.ts

- file-bar.ts:28-38 `CANVAS_VERSION`, `publishedOf` — single-boundary — the session now answers what a file is published as (`published_kind`, fixed in part), but the page still parses the design canvas layout `design-canvas/<version>/project/canvas.json` with a regular expression to name the version and the folder it is listed in, a layout `harness/design_canvas` owns. [2] (still open from round 1)
- file-bar.ts:50-85 `folderAt`, `compacted`, `treeOf`, `foldersAbove` — prefer-class-operations — module functions that build and walk the folder tree for `FileBar` alone (`treeOf`'s only caller is `FileBar.tree`, :108); the folder is a plain `FileFolder` record each function takes and rebuilds. [3]

### harness/files_app/app/files/files-page.ts

- files-page.ts:352-362 `FilesPage.attempt` — use-intention-revealing-names — every failure it tells the chat carries the context "A press on a comment in the Files app", and it always reads the open file again; `openPublished` (:347) runs a board's opening through it, so a board that did not open is told as a comment press and the open file is read again for nothing. The name says "attempt any work"; the body is a comment action's wrapper. [4]

### harness/files_app/app/files/guidance-selector.ts and file-comments-actions.ts

- guidance-selector.ts:26 `GuidanceSelector(page)`, file-comments-actions.ts:16 `FileCommentsActions(page)` — low-coupling — each is still handed the whole `FilesPage` and reaches `page.store`, `page.session`, `page.notices`, `page.showSelected()`, `page.api`, `page.link`, `page.state.reads` and `page.attempt`, while every other part (`ChatContext`, `FilesGraph`, `FileBrowser`, `FilesFoldKeys`) is given only what it uses. [1] (still open from round 1)

### harness/files_app/app/files/files-graph.ts

- files-graph.ts:277-295 `FilesGraph.fix` — eliminate-duplication — the same flow as `GraphFailures.fixOne` (`harness/graph/app/graph/graph-failures.ts`): no chat, fail with `NO_CHAT` and answer `NOT_SENT`; ask Python for the prompt; none, fail and `NOT_SENT`; `ChatClientGenerated.named(api, chat).send('fill', prompt)` and `SENT_TO_CHAT`; any throw, fail and `NOT_SENT`. Only the Python operation differs. [2]
- files-graph.ts:55 `isFailing` — eliminate-duplication — restates Python's `GraphRule.is_failing` (`harness/graph/graph_rules_collection.py:136`) from the status words `'violating' || 'candidate'`, because the adapter carries only `status`; the Graph app restates it twice more (`harness/graph/app/graph/GraphView.tsx:75`, `graph-selection.ts:39`). A new status changes three TypeScript files with no failing type. [2]
- files-graph.ts:177-193 `areFiltersShown`, `showFilters`; file-bar.ts:129-149 `resize`, `restoreWidth`; files-theme.ts:111-157 — eliminate-duplication — browser storage is read and written in eight try/catch blocks over three files with two policies: `file-bar.ts` and `files-graph.ts` drop a `DOMException` silently, `files-theme.ts` tells every failure to the chat. Whether a browser that keeps nothing is a failure depends on which preference is stored. `FilesGraph` also carries this storage job beside reading the graph. [2]

### harness/files_app/app/files/files-theme.ts

- files-theme.ts:111 `storedTheme(fail)`, :122 `applyTheme(theme, fail)`, :141 `storedWrap(fail)`, :151 `keepWrap(wrap, fail)` — prefer-class-operations — four module functions that each take the same `fail`; the look and the wrap choice are a stored preference with nothing holding it, so the `fail` is threaded through `files-page-view.tsx:529` and `file-source-view.tsx:88-90`. [3]

### harness/files_app/app/files/source-of-file.ts

- source-of-file.ts:19-35 `fileAnswered`, :49 `LinkCallout` — no-legacy-api-after-refactor — defaults `language`, `rendered_form`, `comments`, `changes`, `folds`, `steps`, `callouts` and `violations` for "a cdd server lane older than the page", and widens the callout type with `link?`/`missing?` for the same reason; the generated `SessionFileData` already carries `link` and `missing` (`.claude/language-adapters/typescript/space/session/session.ts:135-137`). A compatibility shape for an old server, kept beside the current one. [1]
- source-of-file.ts:42-94 `sourceOf`, `calloutsOf`, `isStoryTest`, `rulesOf`, `violationFocusOf`, `monacoLanguageOf` — prefer-class-operations — a file of functions each taking the `SessionFileData` and reaching into it; `rulesOf` (:78) groups the file's violations by rule, which the session could answer. [3]

### harness/files_app/app/files/format-alignment.ts

- format-alignment.ts:30-66 `FormatAlignment` (`held`, `listeners`, `subscribe`, `change`) — eliminate-duplication — a second store with its own state and listeners on a page whose model says `FilesStore` is "the one place the page's state is held and changed"; it is built inside a view (`format-alignment-view.tsx:16`, `useMemo`) rather than held by `FilesPage` as every other part is, so its diagnosis is lost whenever the view remounts. [3]

### harness/files_app/app/files/file-view.tsx

- file-view.tsx:135 `FileView` with file-rendering.ts:9 `RenderedForm` — contract-comes-from-the-adapter — the adapter types `rendered_form` as a string; the page casts it to a hand-written union, so a form Python adds draws as an empty page (no branch of `RenderedFileView` matches) with no failing type. [2]

### tools/prompt_queue/prompt_queue.py

- prompt_queue.py:354 `PromptQueue` — limit-class-methods — 41 methods (28 public: 22 MCP operations, `load`, `of_chat`, `is_kept`, `chat`, `prompts`, `next`, `prompt`, `queue_once`; 12 private), past the limit of 30. Moving the prompt's work onto `QueuedPrompt` (round 1's D1) was right, but each prompt verb was then republished on the queue and the queue's archive stayed on it too. [3]
- prompt_queue.py:616-663 `_take_off`, `_archive`, `_copy_whole_file`, `_taken_off` — keep-classes-single-responsibility — the queue archive is a second resource kept inside the queue: its own folder (`_archive_folder`), its own file names (`WHOLE_FILE_COPY`, the time-stamped names), its writer (`_archive`, `_copy_whole_file`) and its reader (`_taken_off`, which parses every archived file to find when a prompt left). None of these reads the queue's file or prompts except as input. [3]
- prompt_queue.py:517-519 `PromptQueue.set_steps` — eliminate-duplication — repeats the unknown-state refusal `PromptSteps.plan` already makes (prompt_queue.py:149-151) before calling it through `QueuedPrompt.plan`; two places to change if a state is added. [2]
- prompt_queue.py:442, :448 `add`, `add_all` — state-change-returns-record-or-named-failure — both answer the whole queue, not the prompt they queued, so the mod takes "the last card" as the one it added and changes it next (`hooks/queue/prompt-queue.ts:240` `queueForRobot` assigns `.at(-1)`; `:504` `addSentGoal` moves `.at(-1)`). The queue is changed by several processes (its own docstring, :357-359); a card another process adds between the two calls is the one assigned or moved. [4]
- prompt_queue.py:430 `PromptQueue.prompt` — delete-unused-operations — no production caller; only `prompt_queue_spec.py:194,197,243` call it (the queue's own operations use `_found`). The card lists it in the seam. [1]
- prompt_queue.py:394 `is_kept`, :574 `queue_once` — make-module-only-operations-private — each is called only inside this file (`load` at :380, `_queue_latest_handoff` at :678), yet both are public and named in the card's seam. [1]
- prompt_queue.py:391 `PromptQueue.of_chat` — low-coupling — still builds `CHATS_FOLDER.path / chat / QUEUE_FILE` itself, so the layout of a chat's folder is known here and in `harness/chat/chat.py:295`. [1] (still open from round 1)
- prompt_queue.py:461 `move(prompt, to)`, :570 `attach(..., data)` — avoid-vague-parameter-names — `to` is a place counted from 0 and `data` is a file's bytes in base64; `move_step` beside it already says `place`. [4] (still open from round 1)

### tools/prompt_queue/hooks/queue/prompt-queue.ts

- prompt-queue.ts:924-945 `pointerOf`, `movePointerUp`, `movePointerDown`; :672-685 `addStep`, :710-715 `changeSteps`, :997-1010 `editStep` — domain-lives-in-python — the step pointer, step moves and step removal now go to Python (`step_back`, `step_on`, `move_step`, `remove_step`), but the queue's own pointer still does not: "the nearest done card above the pointer opens again" is decided here (931), and adding or editing a step still builds the whole new step list in the mod and sends it with `set_steps`, then reopens with a second call (679-682), work `QueuedPrompt.interrupt` already does in one for interruptions. [1] (still open from round 1)
- prompt-queue.ts:924-927 `pointerOf` — eliminate-duplication — the queue's answer already carries the prompt to do next (`PromptQueue.next`, prompt_queue.py:425, typed as `QueueJson.next` in `types/index.d.ts:15`), and its rule is the one `pointerOf` writes again from `is_waiting`; nothing in the mod reads `next`. [2]
- prompt-queue.ts:29 `DECISION_FLAG`, :40 `INTERRUPTION_MARK`, :622 `keptInterruptions`, :739 `hasInterruptionsToDo`, :756 `groupIntoTasks` — eliminate-duplication — the two marks are written again from `prompt_queue.py:38,40`, and "an interruption not done yet" (739) is the test `PromptSteps.take_off_interruptions` makes (prompt_queue.py:161). Python already publishes `is_waiting` so the mod need not know the decision mark; the interruption facts are not published, so the mod reads the text. [2]
- prompt-queue.ts:596-612 `isSameRobot`, `robotsOf` — eliminate-duplication — "one robot whatever the case and outer spaces, kept under the first spelling the queue holds" is written here and in `PromptQueue._robot_as_spelled` (prompt_queue.py:593-597); the comment at :595 says the two must match. [2]
- prompt-queue.ts:583-592 `robotPromptsOf`, `robotNamedIn`; :572 `robotsNoteOf`; :850 `rememberRobotAgent` — hold-state-on-the-object-not-in-parameters — a card's robot is kept in its `robot` field (`assign`), yet the agent is told to give a robot work by starting the text with `[for <robot name>]` (572), which the mod parses back out of the text (587-591), and a sub-agent's robot is parsed from the text before the first colon of its description (850). State written into a string and read back, while `prompt-queue.assign` exists. [3]
- prompt-queue.ts:499-513 `addSentGoal` — domain-lives-in-python — where a message sent straight to the chat goes on the queue ("above the first prompt not done") is decided in the mod and made with two calls (`add`, then `move`); an agent calling `prompt-queue.add` gets the other rule (the bottom). The rule also disagrees with the queue's own pointer: it places by `!is_done` while play takes the first `is_waiting`, so a message lands above a decision card play passes over. [1]
- prompt-queue.ts:46-80 (module) — domain-folder-in-the-mod — one 1,010-line file holds 21 atoms and about 90 functions for four things: the queue's cards and their calls, play with the decision wait, sub-agent robots and their hand-out, and following the agent's plan. It is also the module's longest file, past limit-module-file-lines (800). [1] (still open from round 1)

### tools/prompt_queue/types/index.d.ts

- index.d.ts:5-15 `QueuedPrompt`, `StepState`, `PromptStep`, `QueueJson` — contract-comes-from-the-adapter — still hand copies of what the adapter generates as `PromptQueueData` and `QueuedPromptData`; the copy has already been widened twice by hand (`is_waiting`, `step_pointer`, `next`) as Python grew. [2] (still open from round 1)

### tools/prompt_queue/hooks/register.tsx

- register.tsx:78, :81, :83, :86 — use-typed-signatures — each engine event is cast `as unknown as Record<string, unknown>` before it is handed on, and `followPlan` (prompt-queue.ts:615) then takes it as a `PlanCall`: the cast through `unknown` turns off the check that the event carries what the function reads. [4]

### tools/prompt_notify/prompt_notify.py

- prompt_notify.py:245-256 `_mcp_aliases`, `_name_matches` — eliminate-duplication — rebuilds the names a tool is called by; `AgentTool.is_called` (`harness/agent_tools/agent_tools.py:991`) is the one rule, and its docstring says a rules hook recognises its tool by it "so the two never disagree". [2] (still open from round 1)
- prompt_notify.py:168, :190, :230, :232, :247, :262 `getattr(toolset, "tools" / "slug" / "child_toolsets", …)` — low-coupling — reads a toolset by attribute name with a default, past `AgentToolSet`'s typed `tools`, `slug` and `child_toolsets` (agent_tools.py:106,170,617); line 226 reads `tool.slug` properly. [1] (still open from round 1)
- prompt_notify.py:47-48 with :63-66, :137-143 `_catalog`, `_installed_extension` — use-explicit-dependencies — state kept on the class through `type(self)`, shared by every instance in the process. [3] (still open from round 1)
- prompt_notify.py:279-329 `ToastFile._joined_with_previous`, `_is_rules_notice`, `_is_rules_rest`, `_guidance_names`, `_join_arrow_toasts` — hold-state-on-the-object-not-in-parameters — a toast is written as a sentence and read back by splitting on `TOAST_ARROW`, "rules :" and ", " to join two toasts. Decision `tools/.context/cdr/0001` names this and the two above as decided, not done. [3] (still open from round 1)
- prompt_notify.py:289-294 `ToastFile._previous` — refuse-unreadable-input — catches `JsonFileUnreadable` and answers `{}`, and `show` (277) then writes over the toast file it could not read. [3]
- prompt_notify.py:103, :118, :146, :167, :225 `detect_echo`, `echo_toolsets`, `_log_echo`, `_echo_on_toolset`, `_echo_kind_label` against `show_toast`, `_begin_toast`; :150-218 `hay`, `haystacks`, `token` — use-consistent-naming — "echo" and "toast" name one thing (and `tools/echo` is another toolset); `hay` and `token` are search mechanics, not what a call names. [4] (still open from round 1)
- prompt_notify.py:103, :113, :150, :167, :183, :225 `tuple[str, str]`; :84, :93 `-> dict`; :53, :118, :258 `list` — use-typed-signatures — the kind and label a call toasts is an unnamed pair passed through six methods, and the toolsets are an untyped `list`. [4] (still open from round 1)

### tools/granola/granola.py

- granola.py:28-48 `MeetingNote`, `PlannedNote`, `GranolaNote` with :90-102 `_folder_of(note)`, `_by_folder`, `_plan_line(note)` — shape-classes-around-resources — three dict shapes of a note, and the toolset does the note's work for it. [3] (still open from round 1)
- granola.py:76-81 `format_filing_plan(plan: str)` — use-typed-signatures — the plan is a JSON list handed over as a string and parsed back with `json.loads` (81); the tool can take `list[PlannedNote]`, as `write_note_context` takes `note: GranolaNote` (118) and `prompt-queue.add_all` takes `list[str]`. [4]

### tools/error_display/failure.py

- failure.py:39 `FailureKind.checks()` — use-property-not-accessor — takes nothing and derives text from `causes` and `title`; a property. [4]

### tools/prompt_log/prompt_log.py

- prompt_log.py:156-164 `_log_for(payload)`, `_append(payload, entry)` — hold-state-on-the-object-not-in-parameters — `_append` is handed the payload and an entry that already holds it (`PromptLogEntry._payload`, :76); each of the five hooks passes the payload twice. [3]

No findings in goal-title.ts, icon-button-view.tsx, queue-view.tsx, prompt_queue_examples.py.

### scripts/install.py

- install.py:257, :264-267 `_RELEASE_TAG`, `_latest_release` — eliminate-duplication — the release-tag pattern is `RELEASE_TAG` in `harness/release/project_version.py:11`, and "the newest release tag, by version" is `CddVersion._latest` (`harness/release/cdd_version.py:165-171`), which runs the same `git tag --list v* --sort=-v:refname` and takes the first tag that matches. Two places choose which release is the latest. [2]
- install.py:295-323 `_VERSION_LINE`, `_match_release_version`, `_committed_version_line` — eliminate-duplication — a third reader and writer of `pyproject.toml`'s version line, while `ProjectVersion` (`project_version.py:55-73`) is documented as "the one reader and writer of its version line". The patterns already differ: here `^version = "…"$`, there `^version\s*=\s*"…"`. A line written `version="1.3.0"` is read by `ProjectVersion` but not here; `_match_release_version` then finds no local line, runs a `re.sub` that matches nothing, and still answers "(set from vX)" though nothing was written. [2]
- install.py:270-323 `_install_from_latest` — named-seam-and-constraint — the card's Constraint says "Keep the work in the framework and the script thin: a script that grows its own logic is code no spec runs". Fetching tags, choosing the latest release, merging it and putting the version line back are logic, and the call runs the wrong way: `Installer.install_latest` (`harness/installation/installer.py:423-440`) runs `scripts/install-latest.py`, which runs this script, so the framework reaches into a script for work that belongs in `harness/release` beside `CddVersion`, which already fetches the tags. [1]
- scripts/.context/module-context.md:4 against install.py:101-107 — seam-names-current-code — the card says `--from-latest` "pulls origin main first"; the code merges the newest `v*` tag, and its own help says "Commits on main after that release are not taken". [4]
- install.py:121-140 `_chat_folder_refusal` — put-logic-on-the-owning-resource — which folders are no place to install into (the home folder, the temporary folder, a desktop spare folder) is decided in the script, while the install target already refuses an unusable folder with `NotAnInstallFolder` (`harness/installation/install_target.py:31`, caught at install.py:183) and owns `is_temporary`. Another caller of `Installer.create` with the same folder gets no refusal. [3]

### scripts/exercise_hooks.py

- exercise_hooks.py:107 `HookExercise._server` — single-boundary — builds the hook server from `.cursor/hook-handlers.json` by literal path. The file name is `HookHandlersFile.NAME` (`harness/hooks/hooks.py:124`) and `HookServer.from_repository` (`harness/hooks/hook_server.py:462-471`) already finds every IDE's install. This checkout has no `.cursor/hook-handlers.json` (nor `.claude/hook-handlers.json`), so on a Claude install the exercised server is built from a file that is not there. [1]
- exercise_hooks.py:176-178 `HookExercise._fire` — single-boundary — writes the session's file layout again: `last-chat-injected-rules.md` and `chat-injections/hook-exercise.md`. `space/session/chat_injections.py:12-13` owns both names (`_FOLDER`, `_LAST_RULES_FILE`) and answers a chat's file through `ChatInjections.path_for(chat)` (line 42, which also makes the chat id safe). [1]
- exercise_hooks.py:133, :263 `getattr(practice, "slug", None)`, `getattr(rule, "slug", None)` — low-coupling — reads the practice and the rule by attribute name with a default, past their typed seams; `PracticeGuidance` and `Rule` (`harness/guidance/rule.py:89`) both have `slug`. [1]
- exercise_hooks.py:253-257 `HookExercise._rank` — use-typed-signatures — annotated `tuple[int, int, str]`, returns four values; its second key `owned` is always 0, since every candidate already passed `_in_practice` in `_is_fidelity_example` (:227). [4]
- exercise_hooks.py:92, :101 `HookExercise._live_injects` — eliminate-duplication — the live check names Clean Engineering's `modules` fidelity and its rule `domain-nouns-only` by literal, while `_exercise_fidelity` (:137-139) works out each fidelity's expected rules from `fidelity.rules`. Renaming that one rule in `clean_engineering.md` makes the live check fail with the hook working. [2]

### scripts/instances.py

- instances.py:54-65, :107-114 `HttpService.answered_by`, `PingAnswers._located` — hold-state-on-the-object-not-in-parameters — the port is written into the origin string and parsed back with `origin.rsplit(":", 1)` twice; and `answered_by` looks the graph's ports up again by its own service name (`untagged_ports[self.expect_service]`) though the same `HttpService` already holds those ports as `preferred_ports` (`GRAPH_WEB`, `GRAPH_APP`, :385-386, both built from `GRAPH_APP_PORTS.of(...)`). [3]
- instances.py:162-173 `RepoProcesses.stop` — eliminate-duplication — `RunningProcess.stop` (`harness/process/process.py:357-367`) already ends a process and raises `ProcessNotStopped` when it cannot; this copy writes `taskkill /T /F` a third time (also `harness/apps/app.py:273`, `harness/git/git.py:103`), does not wait, and says nothing when the process survives, so `ServiceStart._stop` (start.py:119-121) polls the process list instead. [2]
- instances.py:246-253 `RepoProcesses._processes_from_json` — refuse-unreadable-input — a process listing that does not parse is answered as no processes. `HookPing` and `HttpPing` then report `instances: 0` and stop nothing, and `ServiceStart._stop` stops nothing and starts a second copy beside the one running. [3]
- instances.py:129-265 `RepoProcesses`, `PingAnswers` with start.py:53-66 `ServiceStart.graph_app`, `graph_web` — do-not-invent-parallel-object-models — the Graph app is modelled twice. `harness/graph/graph_app.py:16` registers it as an `App` whose `AppServer` knows its folder, its ports by lane, how to start it, stop it and wait for it (`harness/apps/app.py:137-215`), and `install.py --restart-everything` stops it through that (install.py:349). The scripts find it by command line, stop it by process tree, start it with `npm run dev` / `npm run server` in a folder they write again (`repo / "harness" / "graph" / "app"`, where `graph_app.py:15` derives it), and ping `GRAPH_APP_PORTS` as the file writes them. The two already disagree: `AppServer.ports` moves to the dev lane's offset (app.py:146-149) and the scripts do not, and `AppServer` starts `start.ts` where `start.py` starts Vite. [2]
- instances.py:385-386 `GRAPH_APP`, `GRAPH_WEB` against `harness/graph/graph_app.py:16` `GRAPH_APP` — use-consistent-naming — one name for an `HttpService` here and for the registered `App` there; instances.py imports from the very module that defines the other. [4]
- instances.py:307-309 `HookPing._is_daemon` with start.py:135-136 `ServiceStart._hook_command`; instances.py:292-302 with start.py:76-86 — eliminate-duplication — the hook daemon is found by the literal `"harness.hooks.hook_daemon"` in two places (the module `HookDaemon` itself lives in), and the hook's ping report (`ok`, `ping`, `host`, `port`, `pid`, `stopped`) is written out twice. [2]

### scripts/start.py

- start.py:138-162 `ServiceStart._spawn`, `_detached` — eliminate-duplication — starts a detached process itself, taking only `BackgroundStart`'s `creationflags` and `startupinfo`, while `BackgroundStart.run` (`harness/process/process.py:247-277`) is the framework's detached start, including its start outside the job on Windows (`_start_outside_job`), which this path skips. The log stream opened at :140 is never closed. [2]

### scripts/sanity_mcp.py

- sanity_mcp.py:17 `HOST_PING` — eliminate-duplication — `"cdd.ping"` is `BUILTIN_PING_TOOL` (`harness/mcp/mcp_server.py:51`). [2]
- sanity_mcp.py:80-86 `McpSanity._host` — hold-state-on-the-object-not-in-parameters — makes an `Installer` only to turn its `ToolsetReference`s into strings (`str(reference)`) that `McpHost.from_refs` parses back, while `McpHost.from_repo(repo)` (`mcp_server.py:1028-1030`) is "a host over every annotated toolset in repo: in this process, to check it stands up", which is this script's job. [3]

### scripts/names_exist/names_exist.py

- names_exist.py:45 `IMPORT_ROOTS` — eliminate-duplication — `RepositoryToolsets.IMPORT_FOLDERS` (`harness/installation/repository_toolsets.py:65-74`) says it is "the one list of a checkout's import folders"; this copy (and `scripts/test.ps1:96`) leaves out `cdd_guidance/builders`, so an import of a builders package is not recognised as the repository's own and its missing names go unreported. [2]
- names_exist.py:215, :227, :453, :460; :478 and :481 — eliminate-duplication — `git ls-files -z <pattern>` is run and split four times, and the compiler's path `node_modules/typescript/bin/tsc` is written twice. [2]
- names_exist.py:425, :437 `_LiveNames.__init__`, `_take` — use-exceptions-properly — `except Exception` that continues or returns: a bug in reading a module reads as "this module defines nothing", which then reports its members as missing. [3]
- names_exist.py:263 `PythonNames._ruff_undefined` — use-exceptions-properly — raises a bare `RuntimeError`; a named failure carrying the batch of files and ruff's exit would let the heavy spec tell "ruff missing" from "ruff broke". [3]
- names_exist.py:89, :119 `_defined_in`, `_parsed` — prefer-class-operations — module functions; `_defined_in` serves only `PythonNames._known_names`, and `_parsed` only `PythonNames` and `_ModuleIndex.offers`. [3]

## Round-1 findings in these files now fixed

### Editor-apps models, harness/apps, harness/diagnostics, harness/release, harness/design_canvas, harness/chat

1. chat.py `Chat.send` docstring named a `select` kind — sentence gone.
2. chat.py `ChatLinks.hand_over` public for one caller — `ChatLinks` gone; `NewChat.open`.
3. chat.py `ChatLinks`/`links_of_run` named after the mechanism — now `ChatOpener` and `NewChat`.
4. chat.py `links_of_run` module factory — gone; `Chats.new_chat`.
5. chat.py `_join_opener_section` read `CALLS_BEING_ANSWERED` — the asking chat comes in through `Chats.load(call)`.
6. chat.py four models of "a new chat" — one `NewChat`, used by `space/repo/repos.py:73` and `space/kanban/ticket.py:671`.
7. harness/diagnostics module held four jobs — apps to harness/apps, releases and the cadence to harness/release.
8. diagnostics' dependency on harness/e2e_review unlisted and imported inside a function — listed in the card, imported at the top.
9. app.py `App.load(app, *, project)` unused `project` — dropped.
10. app.py `GRAPH_APP` registered by diagnostics — gone; harness/graph registers its own.
- (not counted: part of the AppPage finding still open) app.py installing on `App` instead of the package — `AppPackage.install`, `is_installed`, `is_current` (the `AppPage` half stays open above).
12. test_runs.py `start_due`/`_settled` wrote `TestRun`'s fields — `TestRun.not_started`, `settled`.
- (not counted: part of the module-functions finding still open) test_runs.py `_counted_every_file_passed`, `e2e_run_name` — now `TestRun._counted_every_file_passed`, `TestRun.folder_name`.
14. test_runs.py `SCHEDULED_RELEASE`, run-name format and `STORY_TESTS` written twice — imports `ScheduledReview.RELEASE` and `RUN_STAMP_FORMAT`; desktop_walk_question.py deleted.
15. test_runs.py, agent_tools_diagnostics.py, guidance_diagnostics.py, agent_tools_probe.py imports inside functions — at the top (only `_winapi` stays, platform-only).
16. desktop_walk_question.py framework named the Stories desktop output — file deleted.
17. desktop_walk_question.py `DesktopWalkQuestion` three jobs — file deleted.
18. cdd_version.py `Release` against release.py `CddRelease` — now `Version`.
19. cdd_version.py/release.py `PYPROJECT` and the version regex written twice — one `ProjectVersion`.
20. release.py `url`/`is_published` beside data fields under other names — `_url`, `_is_published`.
21. agent_tools_probe.py `agent_tools_toolset_ref` module function — `AgentToolsProbe._covers`.
22. canvas.py `DesignCanvas.launch_page` public — `_launch_page`.
23. canvas.py `DesignCanvas.write` with no caller — deleted.
24. canvas.py `DesignCanvas` two jobs — `CanvasProject`.
25. canvas.py `add_board(name, dict, text)` never handed an `Artboard` — `add(artboard, at)`.
26. versions.py `CanvasVersions.numbers` public — `_numbers`.
27. versions.py five operations took a version's number — `CanvasVersion`; `PublishedLinks` moved to harness/installation, one path to a version's link (two round-1 findings).
28. fixture_bar.py/look.py the UX practice's format in the framework, and their module functions — moved to `cdd_guidance/practices/ux/model/claude_design` (two round-1 findings).

Withdrawn (1): chat.py `Chat.show` "no production caller" — it is an `@mcp` tool, which `code_reach` counts as use; an agent may call it.

### harness/catalog_generator and harness/e2e_review

- e2e_review.py (module) named-seam-and-constraint: `harness/e2e_review/.context/module-context.md` exists and its Constraint accepts naming `story_tests` and `space/kanban/app`.
- e2e_review.py `rows`, `verdicts` read `results.json` and `review.json` in Python (parallel model, and their untyped `list[dict]`/`dict` signatures): both are gone; Python reads the summary.
- e2e_review.py:344-349 `ScheduledReview.start` reaching `_baseline_of` and `_tool`: it calls public `baseline_of` and `write_report`.
- e2e_review.py:278-295 `record_verdict` doing three operations: split into `record_verdict`, `judge_step`, `record_walked_step`.
- e2e_review.py:367 `_stamp` as a module function: now `E2eReview._stamp`.
- review.ts:28-115 every function handed the run's folder: replaced by *Run* and *SubEpicRuns* in run.ts.
- report.ts:252-265, :278-279 reading `baseline.json` and `review.json` by literal name: reads through *Run*.
- catalog_generator.py:113 `toolset -> object`, :120 `tool -> object | None`: now `AgentToolSet` and `AgentTool | None`.
- catalog_examples.py:263 untyped `fidelity`: `CatalogFidelity.__init__(fidelity: FidelityGuidance, …)`.
- approach_page.py:364 `practices: list`: now `list[CatalogPractice]`.
- test_runs.py:339 `SCHEDULED_RELEASE` and the run time format copied from e2e_review (part of round 1's three-copies finding): test_runs imports `ScheduledReview` and `RUN_STAMP_FORMAT` (the `run-` prefix is still copied; listed above).

### harness/chat-ui (the cdd-board mod)

1. board.ts `ChatRequest` — the `select`, `show`, `show-stages`, `list-stages` members are gone.
2. chat-turns.ts, chat-name.ts, check-in-client.ts module variables — now the atoms `chatTurns`, `chatName`, `failedCheckIns` (round-1 D10).
3. chat-bar-client.ts `ChatBarClient` deciding the stages shown, whether a practice is on and the fidelities actions run on — it now reads `GuidanceSelectionData` (`covered_stages`, `practices`, `fidelities`, `commands`).
4. chat-bar-client.ts / fidelity-progress-client.ts name pairs (`sessionName`/`ticketName`, `fidelities`/`actionFidelities`, `practice`/`key`) — one name each.
5. chat-bar-client.ts casts adding `session_path` and `actions_with_formats` — gone.
6. chat-bar-client.ts `formatChoices` writing its return shape out again — it is typed `FormatChoiceJson[]` (a new problem with it is above).
7. fidelity-progress-client.ts `commandOn` editing Python's command string — gone; the selection writes each command.
8. guidance-client.ts `startStage` — the session applies "the ticket's stage first" itself (`toggle_guidance`'s docstring).
9. guidance-client.ts `toggle`/`flipped`/`accept` duplicated in the Files app — one `session.toggle_guidance` call (round-1 D6).

### harness/files_app

- whiteboard-canvas.ts — single-boundary (second reader of the `.whiteboard` file): fixed, it now draws the `WhiteboardData` Python reads (`whiteboard-file.show`).
- files-page.ts `listedBy`, `filesShown`, `rootFilesShown`, `isNoPracticeSelected`; file-bar.ts `isSessionWork` — single-boundary: fixed, the session answers `is_listed` and `is_session_work`.
- reasonOf copied nine times and saidBy twice in the folder — eliminate-duplication: fixed as `reason.ts` (the copies beyond the folder are a new finding above).
- guidance-selector.ts / chat-ui guidance-client.ts same press written twice — eliminate-duplication: fixed, both call `Session.toggle_guidance`.

(Round-1 `code-outline.ts:28 memberLines` is in a file outside this group's list, not re-judged.)

### tools/

- prompt_queue.py shape-classes-around-resources (prompts and steps as dicts): `QueuedPrompt` and `PromptSteps` are classes that do their own work.
- prompt_queue.py single-boundary (`queue_handoff`, `handoff_steps`): the handoff answers `next_steps`; the queue has `queue_once`.
- prompt-queue.ts no-state-in-module-variables (`answeringServer`): now an atom.
- prompt_notify.py one-way-deps (imports inside functions, repeated `AgentToolSet` import): all at the top.
- prompt_notify.py hold-state (`handle(payload, toolsets)`, `detect_echo(payload, toolsets)`): read `self.echo_toolsets`.
- prompt_notify.py layer-separation (`show_toast` forwarding to `show_ide_toast`): one name.
- granola.py deep-module (`Granola.root`): now `_root`.
- failure.py deep-module (`FailureKinds.every`): deleted.
- prompt_log.py deep-module (`PromptLog.log_for`): now `_log_for`.
- Narrowed, still counted open: prompt-queue.ts domain-lives-in-python — step pointer, `removeStep`, `moveStep` now call Python operations; the queue pointer and step add/edit remain.
- Not judged here: `queue-order.ts` `PromptQueue` (client-mirrors-python-domain) — the file is not in this round's list.

## Design proposals

1. **Retire the increment's model folder.** Delete `harness/.context/editor-apps/*.py` and the entries of `editor-apps-model.md` whose classes are implemented, moving any invariant still worth keeping into the owning module's model (`harness/apps/.context/apps-model.md`, `harness/guidance`, `space/session`, `space/kanban`, the Stories model), and correct `harness/design_canvas/.context/design_canvas-model.md` from the card. Ends the ten editor-apps findings and the design_canvas model finding (11).
2. **One file of state per holder, through `JsonFile`.** `ChatStateFile` and `TestRunRecord` read and write through `JsonFile` (its held-file retry and its `JsonFileUnreadable`), delete `_while_windows_holds` and `_while_busy`, and refuse an unreadable chat state instead of reading it empty. Ends chat.py `_while_windows_holds`, `_read_once`, test_runs.py `_read/_write/_while_busy` (3).
3. **A version owns its arithmetic, and the version toolset holds its parts.** `Version.from_given(text)` (refuses with `VersionNotValid`) and `Version.next_minor`; `ProjectVersion.read` refuses a file with no version line by name; `CddVersion` holds the running checkout's and the project's `ProjectVersion`, and its `CddRelease` built once in `load`. Ends `_next_version_from`, `ProjectVersion.of` built per call, `CddVersion.release` building collaborators, `ProjectVersion.read` (4).
4. **Python reads a run only through Run's answers.** `review.ts pairs` answers each pair's screenshots as absolute paths and the summary carries the baseline's name; `E2eReview.baseline_of`, `BASELINE_FILE`, the screenshot joining in `changed_pairs`, and `WALK_VERDICTS`/`REVIEW_VERDICTS` go (the refusal comes from `ReviewRefused`); `changed_pairs` answers a typed `ChangedPair`; `ScheduledReview` passes `E2eRun`s, not folder strings; the review agent's tools come from the toolset's published names. Ends: e2e_review.py baseline parallel model, verdict words, `changed_pairs -> list[dict]`, `ScheduledReview.start` folder strings, `REVIEW_AGENT_TOOLS`, the log path copy. Also fold `isReviewed`/`summary`/`openPairs` onto one `Run.reviewAgainst(other)` that answers only the verdicts of that comparison, ending the run.ts four-copies finding.
5. **The catalog's approach is made once and its fidelities answer for themselves.** `Catalog` builds one `ApproachGrids` and keeps it (the board and both approach pages draw it); `ApproachGrids.example_of(stage) -> StageExample` replaces the five `StageExample(...)` constructions; `CatalogFidelity` gains `href` and `examples: list[ExampleFile]` built once. Ends: `Catalog.board` building the approach on each access, `fidelity_href(shown.fidelity)` at six call sites, `ExampleFile` rebuilt per sort key, `CatalogExamples` taken apart twice, the `fidelity.fidelity` naming.
6. **A practice's catalog card is a declared, typed part of `PracticeGuidance`.** `PracticeGuidance` declares `catalog_card: CatalogCard` (a typed value with the six keys and their defaults, plus how a panel shows each fidelity's picture and where a code example opens); `CatalogPractice` reads it without `getattr`; `_panel_image_classes`, `_ROOT_CLASS_LINE` and the `story_map` stem test move into the cards of DDD, UX and Stories; `configure_project_approach` draws its table from the practices' board fidelities. Ends: `_card_of -> dict[str, Any]`, the `getattr` low-coupling finding, the `Customer`/stem extensions finding, the `story_map` duplicate, the hand-written practice table.
7. **Overlays join the guidance selection.** `GuidanceSelection` holds the session's overlays, `session.toggle_guidance` takes part `overlay`, and the commands it writes carry them; `ticket.overlay_choices` / `choose_overlays` and the mod's `overlayArgumentOf`, `toggleOverlay` list arithmetic and overlay atom go. Ends: action-button-view.tsx:37-43, overlay-choices-client.ts:52-60, and with them the ticket-name addressing.
8. **The mod's contract file wraps adapter data only.** Delete `TestRunJson`, `E2eReviewJson`, `RepoRowJson`, `FormatChoiceJson`, `OverlayChoiceJson`; give `repos.siblings` a published data type; read `ServerHealthData`'s fields without casts; draw format chips from `GuidanceSelectionData.formats` directly (dropping `made` and `format-choices-client.ts`). Ends: both index.d.ts findings, server-health-client.ts:55-67, chat-bar-client.ts:159-161, format-choices-client.ts.
9. **The bar's read sequence and its next action live in clients, register only boots.** Move `readActive`, `showStatus` and the three `readBoardAfter*` into `chat-bar-client.ts` with the shown context as an atom; have Python answer the offered action and its fidelity (`Ticket` or `GuidanceSelection`: `offered_action`, `action_fidelity`), which `actionOf` then only draws. Ends: register.ts:48, register.ts:52-90, register.ts:80-81, action-button-view.tsx:18-31, and, when the "progress order" goes with it, fidelity-progress-client.ts:121-123.
10. **The Files app uses the shared page failures.** `FilesNotices` extends `ChatToldFailures` (as `GraphFailures` does), `reason.ts` goes and every file imports `reasonOf` from `@cdd/cdd-page-failures`; `FilesGraph.fix` and `GraphFailures.fixOne` share one "send Python's fix prompt to the opening chat" operation on `ChatToldFailures`; the server imports `ProjectFolderMissingError` from `@cdd/cdd-connection`. Ends: files-notices.ts, reason.ts, files-graph.ts:277 `fix`, files-server.ts `ProjectFolderMissingError`.
11. **One home for the chat bar's and the Files app's glyphs and stored preferences.** A shared generated module (beside `cdd-views.tsx`) holds `STAGE_ICONS`, `FORMAT_GLYPHS` and a `BrowserPreference(key, fail)` object with one policy for a browser that keeps nothing; `files-theme.ts`, `file-bar.ts` and `files-graph.ts` hold preferences of that type. Ends: format-chips.ts, files-page-view.tsx:444 `STAGE_ICONS`, the storage-handling finding, files-theme.ts module functions.
12. **The adapter carries what the page restates.** Python publishes `is_failing` on `GraphRuleData`, an enum type for `rendered_form` and the failure kinds, and a `published_name` and `published_folder` on `FileEntry`; the page drops `isFailing`, `RenderedForm`, `FailureKindName`/`FailureBand` and `CANVAS_VERSION`, and `fileAnswered`'s defaults for old lanes. Ends: files-graph.ts:55, file-view.tsx:135, failure-fixes.ts:11, file-bar.ts:28-38, source-of-file.ts:19-35.
13. **The queue answers what the mod now works out.** Publish on `QueuedPrompt` `has_interruptions_to_do`; make `robot` the only way a card belongs to a robot (drop `[for name]` from the agent note and the parsing); give `add` a place and a robot and answer the added prompt (or add `add_at(text, place, robot) -> QueuedPrompt`), so "a sent message goes above the next prompt" is one Python call with the queue's own pointer rule; add `prompt_back` / `prompt_on` for the queue pointer and `add_step(prompt, text)` / `edit_step` that reopen in the same call; the mod reads `queue.next`. Ends: add/add_all state-change-returns-record; pointerOf duplication; marks duplication; isSameRobot duplication; `[for name]` hold-state; addSentGoal domain-lives-in-python; the still-open pointer/step domain-lives-in-python. Then the hand-copied types can be the adapter's (ends the index.d.ts finding).
14. **The queue archive is its own class; the queue's seam shrinks.** `QueueArchive(folder)` with `keep(prompts)`, `copy_whole(record)`, `taken_off(id)`; the queue holds one. Delete `PromptQueue.prompt` (spec reads `prompts`), make `is_kept` and `queue_once` private, drop `set_steps`'s own state check, rename `to` to `place` and `data` to `base64_bytes`, and ask `harness/chat` for the chat's folder. Ends: limit-class-methods, keep-classes-single-responsibility, set_steps duplication, delete-unused-operations, make-module-only-operations-private, of_chat low-coupling, avoid-vague-parameter-names.
15. **Finish decision `tools/.context/cdr/0001`.** Match with `AgentTool.is_called`, read toolsets through their typed members, keep the toast catalogue and extension install on the one notifier instance the hook server makes, take a toast as a value from `harness/hooks` instead of parsing `ToastFile` text (refusing an unreadable toast file rather than writing over it), and name the pair a call toasts. Ends the seven prompt_notify.py findings.
16. **The service scripts start, stop and ping through the framework's apps.** `start.py` and `instances.py` ask `GRAPH_APP` (`harness/graph/graph_app.py`) for its `AppServer` (start, stop, port by lane) and `HookDaemon` for the hook daemon (spawn, running, its own command), and `RepoProcesses` keeps only "stop the extra copies", built on `RunningProcess.stop` and `BackgroundStart.run`. Ends: instances.py parallel Graph app model, `GRAPH_APP` naming, `RepoProcesses.stop`, `_processes_from_json` (gone with the listing, or made to refuse), `answered_by`/`_located`, the hook duplicates, start.py `_spawn`. 7 findings. Risk: the graph web server (`server.ts`) is not a registered app today; it needs an `App` or an `AppServer` of its own first.
17. **Installing the latest release moves into `harness/release`.** `CddVersion` (or a `LatestRelease` beside it) answers the latest tag and merges it; `ProjectVersion` gains "put the version line back to the one commit X holds"; `Installer.install_latest` calls them, and `install.py --from-latest` becomes one call. Correct the card's "pulls origin main". Ends: `_RELEASE_TAG`/`_latest_release`, the version-line copy, the script-grows-logic finding, the card mismatch. 4 findings.
18. **Scripts read the framework's names instead of copying them.** `IMPORT_ROOTS` from `RepositoryToolsets.IMPORT_FOLDERS` (and `test.ps1` from the same, through a printed list), `HOST_PING` from `BUILTIN_PING_TOOL`, `McpHost.from_repo` in `sanity_mcp.py`, `HookServer.from_repository` and `ChatInjections.path_for` in `exercise_hooks.py`. Ends 5 findings (`IMPORT_ROOTS`, `HOST_PING`, `_host`, `_server`, `_fire`).
