# What the closing robots added — input for the story map, module cards and class model

Every commit named here is on `release-1-2-fixes`. Read each robot's diff (`git show --stat <commit>`) for the exact files; this list says what to look for.

## Stories and scenarios

| Epic | Sub-epic | Story | New story? | Scenario file |
|---|---|---|---|---|
| Move Work Forward On Session Board | Steer Ticket Sessions | Open Ticket Session; Activate Ticket; Close Active Session | no, scenarios added | `story_tests/move-work-forward-on-session-board/steer-ticket-sessions/steer_ticket_sessions_story.test.md` |
| Move Work Forward On Session Board | Maintain Tickets | Add Backlog Item; Archive Ticket; Delete Ticket | no | `.../maintain-tickets/maintain_tickets_story.test.md` |
| Move Work Forward On Session Board | Organize Ticket Hierarchy | Add Child Ticket | no | `.../organize-ticket-hierarchy/` |
| Move Work Forward On Session Board | See Work On Session Board | Display Board | no | `.../see-work-on-session-board/` |
| Move Work Forward On Session Board | Guide Work Through Practices On Board | Choose Session And Practice Roots | no | `.../guide-work-through-practices-on-board/` |
| Register And Install Toolsets | Install Markdown Files | Store Install State | no | `story_tests/register-and-install-toolsets/install-markdown-files/install_markdown_files_story.test.md` |
| Register And Install Toolsets | Install Markdown Files | Choose Where To Install | **yes** | same file |
| Register And Install Toolsets | Install Markdown Files | Refresh The Installer's Own Commands | **yes** | same file |
| Register And Install Toolsets | Install Markdown Files | Install The Latest Release | **yes** | same file |
| Register And Install Toolsets | Install Markdown Files | Publish Mods For Every Chat | **yes** | same file |
| Move Work Forward From Chat Bar | Check CDD Server Health In Chat Bar | Create Git Repository First | no (on the map, had no scenarios) | `story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/` |
| Deliver Work With Context Guidance | Produce Formal Artifacts | Generate Fidelity Artifact; Render Artifact Into Another Format | no (first scenario files) | `story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/` |
| Deliver Work With Context Guidance | Produce Formal Artifacts | Take Artifact To Another Format And Back | **yes** | `.../produce-formal-artifacts/take_artifact_to_another_format_and_back_story.test.md` |
| Deliver Work With Context Guidance | Check Artifacts Against Rules | Validate Artifact Against Rules | no (first scenario file) | `.../check-artifacts-against-rules/` |
| Deliver Work With Context Guidance | Turn Source Material Into Context | Describe Existing Artifacts | no (first scenario file) | `.../turn-source-material-into-context/` |
| Map Work Into Knowledge Graph | Build Practice Trees From Source | Read Modules Classes And Operations; Read Story Maps And Story Tests | check the map: the file is new | `story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/` |
| Queue Prompts For Later | Build Prompt Queue | Queue Draft Prompt; Edit Queued Prompt | no | `story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md` |
| Queue Prompts For Later | Build Prompt Queue | Refuse Queue File That Holds No Queue | **yes** | same file |
| Queue Prompts For Later | Build Prompt Queue | Name Queue By Chat Id | **yes** | same file |
| Queue Prompts For Later | Nest Prompt Steps In Queue | Set Steps Of Queued Prompt; Add Interruption To Working Prompt | no | `.../nest-prompt-steps-in-queue/` |
| Queue Prompts For Later | Share Queue Among Robots | Group Queue Into Robots | no | `.../share-queue-among-robots/` |
| Review Generated Work In File Viewer | Review Files In Files App | List Files The Link Names; List This Session Or All Session Files; View File In Source View | no | `story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/` |
| Review Generated Work In File Viewer | Switch Files App Between Files And Graph | Open Several Files From Graph Nodes | no | `.../switch-files-app-between-files-and-graph/` |

The test runner (tier runs, the record of runs, the cadence) has no story on the map; its behaviour is in the describe names of `harness/diagnostics/test_runs_spec.py`, `test_runs_heavy_spec.py` and `scripts/test_ps1_heavy_spec.py`. Do not invent an epic for it: say in your report that it has none.

Five stories now hold more than seven scenarios (`story-scenarios-at-most-seven`): Activate Ticket 12, Close Active Session 11, Open Ticket Session 9, Display Board 9, Add Backlog Item 8. Splitting them is a story map decision: propose a split in your report, do not make it.

## Classes and public operations

- **space/kanban** (commits 5e8029f31, 4168896e1): `CardName` (`for_new_card`), `TitleNamesNothingError`, `TitleTooLongError`, `TicketNameTakenError`, `BacklogItemTakenError`, `NAME_LENGTH_LIMIT`; `TicketCheckout.leave_branch`, `free_worktree()` (no argument), `save_work` (commit, push, merge only), `TicketWorktreeBlockedError`; `UnreadableSessionFile`, `Board.unreadable`; `CardPlacement.free_name_for` (now public).
- **space/repo** (5e8029f31, 905ccac2f, b06b79875, 13cc270cb): `WorktreeFolderTakenError`, `Worktrees.remove` raises `WorktreeNotRemovedError`, `MergeRefusedError`; `NewRepository.write_ignores` with `CDD_WRITTEN_PATTERNS`; `Branch.changed_files` reads through `Git.listed`.
- **space/session** (4168896e1, 13cc270cb, dc600d22a): `SessionFolderHeldError`; `Sessions.read_apart()`, `SessionsRead`; `SessionHierarchy.open_child(name, title, scope)`; `FileText.exists`, `VIEWER_SHOWS_LINES`, `FileTooLongToShowError`; `OutputRootRefused`, `PracticeSessionOutput.root_named`.
- **harness/installation** (905ccac2f, b06b79875, e40748768): `UnknownIde`, `NotAnInstallFolder`, `LastInstall`, `InstallLock`, `InstallAlreadyRunning`, `InstallRecord(target)` holding its folder, `InstallRecord.adopt`, `Installer.last_install`, `Installer.lock`; `JsonFile.held()`, `JsonFileBusy`.
- **harness/mcp** (b06b79875): `CddHome._publish_mods` holds an `InstallLock`.
- **harness/diagnostics** (d7b2ce0a2): `TestRunRecordUnreadable`, `RunWorktree`, `TestRun.taken_by`, `TestRun.checkout`, `TestRun.process_started`, `TestRunRecord(folder, checkout)`, `TestRunRecord.new_run`, `TestCadence(record, runner, git, clock, review, wait, say)`, `TestRunner(record)`; removed `TestRun.is_run_by_this_process`.
- **harness/process** (d7b2ce0a2): `RunningProcess.started_at`, `StarterBoundJob` (`take_in`), `JobNotMade`. This folder has no module card of its own; record the names where the root card describes `process`.
- **harness/git** (13cc270cb): `Git.listed`.
- **harness/files_app** (13cc270cb): `ProjectFolderMissingError`, `connectionOf`.
- **cdd_guidance/actions, harness/guidance_actions** (984fffef3): `NothingToRender`, `UnknownRule`, `GuidanceMappingNamesNoToolset`, `ActionFiles.paths_to_read`; `Validate.validate(rule: str | None)`; `ValidationReport(guidance, checked, only=None)`.
- **cdd_guidance/practices** (a4586503d): Stories `DiagramStoryCell.owner_among`, `DrawIOStoryModel.placed_cells`, `StoryModel.unplaced_stories`, rule `ScenariosNameAStoryOnTheMap` (`scenarios-name-a-story-on-the-map`); Clean Engineering `Property.marked_signature`, `DiagramClass.property_lines`, `ClassView.unmarked_properties`, `SourceParses` now checks Module and Package; DDD `WhiteboardBoundedContextMap.take_board`.
- **tools/prompt_queue** (e40748768): `QueueFileUnreadable`, `ChatIdNotAnId`, `StepStateUnknown`, `STEP_STATES`, `PromptQueue.of_chat(chat, archive=None)`; removed `PromptQueue._held`.

Three classes now each claim a file so two processes do not run one thing at once: `InstallLock` (harness/installation), `JsonFile.held` (harness/installation), `_SpawnLock` (harness/hooks/hook_daemon.py), beside `TestRunRecord`'s claim file (harness/diagnostics). Record that in the model as it is; proposing one shared class in `harness/process` goes in your report, not in the model.
