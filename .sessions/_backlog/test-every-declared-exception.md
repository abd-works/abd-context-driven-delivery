# Test Every Declared Exception

Analysis and planning: nothing here is fixed yet. Decided by the lead on 2026-11-22, from the first run of TDD's checked rule `declared-exception-raised-by-a-test` over this repository (`cdd_guidance/practices/tdd/rules/__init__.py`).

**Outcome:** every exception class the code declares is named by a test that breaks the invariant it guards and expects it, so the rule reports nothing on this repository.

## Why it matters

An exception no test names is a failure nobody has seen happen. Its message, and what it carries for the person who reads it, are unchecked until a user meets it.

## What the rule found

68 exception classes that no test file and no test code names, by the module that declares each:

- `cdd_guidance/actions/render/render.py`: BoardNotKept
- `cdd_guidance/context_setup/live_app_capture.py`: CaptureFailed
- `cdd_guidance/practices/agent_bdd/agent_bdd_common.py`: AgentJudgeError, ChatInboxPending
- `cdd_guidance/practices/agent_bdd/cursor_cli.py`: ChatNotCreated, CursorAgentNotAuthenticated, CursorAgentNotFound
- `cdd_guidance/practices/clean_engineering/measures/code_measures.py`: MeasureNotTaken
- `cdd_guidance/practices/clean_engineering/measures/measuring_tools.py`: MeasuringToolNotInstalled, ToolDoesNotTakeMeasure
- `cdd_guidance/practices/clean_engineering/model/translation.py`: TranslationError
- `cdd_guidance/practices/stories/model/opened_story_map.py`: StoryMapEditRefused
- `cdd_guidance/practices/stories/model/story_map.py`: StoryNodeNotFound
- `cdd_guidance/practices/ux/model/drawio/nodes.py`: DrawioCliFailed, DrawioCliMissing
- `harness/agent_tools/recipe.py`: RecipeCallsItself, RecipeNotAFunction
- `harness/agent_tools/tool_call.py`: SessionsNotLoaded
- `harness/apps/app.py`: AppServerNotRestarted, NpmNotFound, NpmTooSlow, PackageNotInstalled
- `harness/catalog_generator/catalog_generator.py`: CatalogNotGenerated
- `harness/chat-ui/pane/hooks/health/app-client.ts`: AppNotOpened
- `harness/chat-ui/pane/hooks/shared/cdd-tool.ts`: CddToolFailed
- `harness/diagnostics/agent_tools_probe.py`: ProbeCallTimedOut
- `harness/files_app/app/drawio-viewer.ts`: DrawioViewerNotStarted
- `harness/files_app/app/file-explorer.ts`: FileNotThere
- `harness/files_app/app/files/files-api.ts`: FilesCallFailure
- `harness/graph/app/graph/graph-api.ts`: GraphCallFailure
- `harness/graph/graph.py`: GraphFailure
- `harness/graph/model_node.py`: ModelWithoutPractice
- `harness/guidance/action_catalogue.py`: ActionsNotRegistered
- `harness/guidance/practice_catalogue.py`: PracticesNotRegistered
- `harness/guidance/practice_formats.py`: NoFormatReads, SourceFormatNotSet
- `harness/guidance_actions/guidance_actions.py`: GuidanceTurnedOff
- `harness/installation/destination.py`: SkippedTool
- `harness/installation/installer.py`: ServersNotRegistered
- `harness/installation/repository_toolsets.py`: ToolsetUnloadable
- `harness/mcp/cdd_home.py`: PinFailed, RuntimeNotInstalled
- `harness/mcp/mcp_address.py`: LaneUnreachable
- `harness/mcp/mcp_server.py`: McpStandupFailed
- `harness/mcp/tool_calls.py`: ToolCallStopped
- `harness/process/process.py`: ProcessNotStopped
- `harness/process/starter_bound_job.py`: JobNotMade
- `space/kanban/board.py`: CardNotInColumnError, FolderOutsideRepositoryError
- `space/kanban/report.py`: ViolationNotInReportError
- `space/kanban/ticket.py`: NoReportToAcceptInError
- `space/kanban/ticket_checkout.py`: TicketBranchUnclearError, TicketWorktreeBlockedError
- `space/kanban/ticket_choices.py`: FormatNotOfferedError
- `space/kanban/ticket_tree.py`: NotAChildError, ParentLoopError, ParentMovesWithChildrenError
- `space/repo/origin.py`: MergeRefusedError
- `space/repo/repo.py`: CommitMessageRequiredError
- `space/repo/repos.py`: InstallFailedError, PublishFailedError, UnknownVisibilityError
- `space/session/files/file_comments.py`: FileCommentNotFoundError
- `space/session/practices/practice_session_output.py`: FidelityNotInPractice, FormatNotOfferedError
- `space/session/session.py`: NotAPatternError
- `space/session/session_folder.py`: SessionFolderHeldError
- `tools/prompt_queue/hooks/queue/prompt-queue.ts`: QueueCallFailed

## How to work it

Take one module at a time and name the scenario or spec that states what the code does today before adding to it. For each exception, write the test that breaks its invariant and expects it, at the fastest tier that can, and see it pass. An exception no code path can raise any more is deleted, not tested. Run `declared-exception-raised-by-a-test` again after each module, so the list above shrinks with the work.
