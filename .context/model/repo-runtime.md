**Repository runtime relationships**

What each class of the repository model does to another class when the code runs, traced from the code: the operation that acts, then each `-> Other.operation` it calls, creates (`Other()`), reads, or raises, with the interaction in words and the line that does it, and `<- Type` where what comes back matters. A dashed labelled arrow in each module's class model drawing (`{module}/.context/{module}-model.drawio`, such as `harness/graph/.context/graph-model.drawio`) stands for each class pair here. Only classes in the modules' class models (`{module}/.context/{module}-model.md`; `space/kanban/.context/kanban-model.md` for the board) appear as targets; calls into a class outside the model are left out. The judgement of each relationship (right as a dependency, or the code has the wrong shape) was made in the review of the `ensure-domain-orientation-refactor` branch, kept with that session work in `.sessions/release-1-2-fixes/clean-engineering-review/refactor-rounds-1-9/repo-model-disconnected.md`.

Read `annotation_kinds` as the one registry of annotation kinds in harness/annotations; *InstallChannels* as the installations of one *InstallRun*.

# Traced chains

## Install: the Installer walks the toolsets, reads each member's destination annotations, and hands the member to the installation of each channel

- `Installer.install` `-> InstallRun(installer, toolsets, replace)` creates the run and keeps it as `last_run` · harness/installation/installer.py:376
- `InstallRun` `-> InstallChannels(installer, SERVER_CHANNELS.kinds)` creates the run's installations once · harness/installation/installer.py:136
- `InstallChannels` `-> RegisteredChannel.create(target, record, repository)` creates McpInstallation and HookInstallation, each registered channel · harness/installation/installer.py:68
- `InstallChannels` `-> LanguageAdapters(target, record, repository)` creates the language adapters · harness/installation/installer.py:69
- `InstallChannels` `-> SkillInstallation, CommandInstallation, RulesInstallation` creates one installation of each file channel · harness/installation/installer.py:71
- `InstallRun.publish` `-> Installer.repository_toolsets` reads every toolset the repository defines · harness/installation/installer.py:161
-   `<- list[ToolsetReference]` · harness/installation/installer.py:405
- `InstallRun._install_all` `-> ToolsetReference.made` makes each toolset · harness/installation/installer.py:208
- `InstallRun._install_toolset` `-> AgentToolSet.tools` reads every published member · harness/installation/installer.py:222
-   `<- dict[str, AgentTool]` · harness/installation/installer.py:222
- `InstallRun._install_toolset` `-> InstallChannels.for_tool(tool)` finds every installation the member is written through · harness/installation/installer.py:223
- `InstallChannels.for_tool` `-> RegisteredChannel.accepts(tool)` asks each registered channel · harness/installation/installer.py:86
- `InstallChannels.for_tool` `-> AgentTool.is_published_to(installation.destination)` asks each file channel's destination kind · harness/installation/installer.py:87
- `AgentTool.is_published_to` `-> DestinationKind.publishes(callable)` reads that destination's annotation (Skill, Command, Rules, Mcp, Hook) and NoDeploy · harness/agent_tools/agent_tools.py:916
-   `<- list[Installation]` · harness/installation/installer.py:85
- `InstallRun._install_toolset` `-> Installation.install(tool)` hands the member to each installation · harness/installation/installer.py:224
- `Installation.install` `-> FileInstallation.write | McpInstallation.write | HookInstallation.write` writes the member's channel · harness/installation/destination.py:108
- `InstallRun._install_toolset` `-> LanguageAdapters.record(toolset)` records a toolset annotated @language_adapter · harness/installation/installer.py:225
- `LanguageAdapters.record` `-> DataClass.languages` reads the LanguageAdapter annotation · harness/installation/language_adapter.py:862
- `InstallRun.publish` `-> LanguageAdapters.write_all` writes `{ide}/language-adapters/typescript/` · harness/installation/installer.py:165
- `InstallRun.publish` `-> InstallRun._install_agents` copies `cdd_guidance/agents/*.md` to `{ide}/agents/` without reading any annotation · harness/installation/installer.py:166
- `InstallRun.publish` `-> InstallRun._install_standing_rules -> RulesInstallation.write_standing_rule` writes each `cdd_guidance/rules` file · harness/installation/installer.py:250
- `InstallRun.publish` `-> RegisteredChannel.write_once_recorded` writes what a channel writes once every tool is recorded, such as the IDE's `cdd` entry · harness/installation/installer.py:169
- `InstallRun.stand_up` `-> ChannelServer.stand_up` stands each channel's server up over what was installed · harness/installation/installer.py:176
-   `<- StandUp` the tools it serves and the tools it skipped · harness/installation/installer.py:176
- `InstallRun.ensure_running` `-> ChannelServer.ensure_running` starts each server · harness/installation/installer.py:184
- `InstallRun._diagnose` `-> Installer.diagnosis_of` diagnoses what the run deployed against the last install · harness/installation/installer.py:189
- `Installer.diagnosis_of` `-> Deployed.of_folder` reads what the folder holds on each channel · harness/installation/installer.py:410
- `Installer.diagnosis_of` `-> RegisteredChannel.status` reads each registered channel's status · harness/installation/installer.py:411
-   `<- InstallDiagnosis` · harness/installation/installer.py:412
- `InstallRun._diagnose` `-> InstallDiagnostics.record` appends the diagnosis to `diagnostics.json` · harness/installation/installer.py:190

## Destination and the installation that writes it, matched by the installation's destination kind

- `SkillInstallation.write` `-> Skill (destination)` writes `{ide}/skills/{toolset}-{operation}/SKILL.md` · harness/installation/files.py:269
- `CommandInstallation.write` `-> Command (destination)` writes `{ide}/commands/{toolset}/{name}.md` · harness/installation/files.py:327
- `RulesInstallation.write` `-> Rules (destination)` writes `{ide}/rules/{practice}/{fidelity}.mdc` (`.md` for Claude Code) · harness/installation/files.py:339
- `McpInstallation.write` `-> Mcp (destination)` records the operation; `write_once_recorded` writes the IDE's `cdd` MCP entry · harness/mcp/mcp_server.py:327
- `HookInstallation.write` `-> Hook (destination)` adds the event (`Hook.name_given`) to `hooks.json` and the operation to `hook-handlers.json` · harness/hooks/hook_installation.py:67
- `LanguageAdapters.record` `-> LanguageAdapter (class annotation, no channel)` generates TypeScript for the toolset · harness/installation/language_adapter.py:860
- `PromptNotify._has_toast` `-> Toast (no channel)` nothing is installed; the notifier toasts the call · tools/prompt_notify/prompt_notify.py:264

## A chat's tool call: McpHost to ToolCall to the toolset's operation

- `McpHost.dispatch` `-> ProjectToolsets.resolve_call_name` maps the chat's tool id to `toolset.operation` · harness/mcp/mcp_server.py:748
- `McpHost.dispatch` `-> ToolCall.sent(arguments, project, request)` creates the call; a chat's call takes its project and *ToolRequest* from its *ChatRequest* (`project_for`, `tool_request`) · harness/mcp/mcp_server.py:724, :973
- `McpHost.answer` `-> McpHost._answer_between_restarts` · harness/mcp/mcp_server.py:763
- `McpHost._answer_between_restarts` `-> McpHost._server_for(call.project)` finds the project's ProjectToolsets · harness/mcp/mcp_server.py:777
- `ProjectToolsets.answer` `-> AgentTool.answer(call)` · harness/mcp/mcp_server.py:497
- `AgentTool.answer` `-> AgentToolSet.for_call(call)` the toolset as the call works on it · harness/agent_tools/agent_tools.py:801
- `AgentTool.answer` `-> AgentTool.log_session_invocation(call) -> ToolCall.session` logs the call in the session open in its project · harness/agent_tools/agent_tools.py:802
- `ToolCall.session` `-> SESSION_OPENING.open_in(call)` the opener space/session registered (`SESSION_OPENING.open_with`) · harness/agent_tools/tool_call.py:89
- `AgentTool.answer` `-> toolset operation(**arguments)` runs the annotated operation with its coerced arguments · harness/agent_tools/agent_tools.py:803
-   `<- object` the operation's result, sent back to the chat · harness/agent_tools/agent_tools.py:803

## A session's practice and its graph: Session to PracticeSessionOutput to Graph, PracticeGraph, and Node

- `Session.practices` `-> PracticeCatalogue.keys` lists every practice · space/session/session.py:264
- `Session.practices` `-> PracticeSessionOutput(name, session)` creates one per practice, kept by key · space/session/session.py:265
- `PracticeSessionOutput.graph` `-> Graph.of_practice(repo_path, name, folder)` loads the practice's graph once · space/session/practices/practice_session_output.py:111
- `Graph.of_practice` `-> Graph.load_working_copy` · harness/graph/graph.py:1013
- `Graph._build_working_copy` `-> Graph.practice(name) -> PracticeGraph(name)` creates the practice's node store, keyed by the practice name · harness/graph/graph.py:1055
- `Graph._build_working_copy` `-> WorkingCopy(graph).fill` · harness/graph/graph.py:1192
- `WorkingCopy.fill` `-> GraphPractices.in_reading_order` looks up each registered GraphPractice by name · harness/graph/working_copy.py:27
- `WorkingCopy.fill` `-> GraphPractice.read(practice_graph)` reads the practice's files into nodes · harness/graph/working_copy.py:31
- `GraphPractice.read (each practice's subclass)` `-> PracticeGraph.add / add_named -> Node(...)` creates and adds each node · harness/graph/graph.py:836
- `WorkingCopy.fill` `-> GraphPractices.overlay(pattern).read(graph)` adds each pattern's nodes · harness/graph/working_copy.py:36
- `WorkingCopy.fill` `-> PracticeChecks(practice).run` runs the rules · harness/graph/working_copy.py:39
- `PracticeChecks.run` `-> GraphPractice.checks(patterns) -> PracticeGraphRule.check(node, RuleCheckContext)` · harness/graph/rules.py:23
-   `<- Graph` · harness/graph/graph.py:1016

## The catalog: Catalog to practices, actions, and toolsets, to pages

- `Catalog._render_catalog` `-> Catalog.practices -> CatalogPractice.load_all -> PracticeCatalogue.practices` every practice not annotated @noCatalog · harness/catalog_generator/catalog_generator.py:84
- `Catalog._render_catalog` `-> Catalog.lifecycle_actions -> LifecycleAction.load_all -> ActionCatalogue.actions` every action whose toolset is not annotated @noCatalog · harness/catalog_generator/catalog_generator.py:211
- `LifecycleAction.tool` `-> action.toolset_class() -> AgentToolSet.tools` builds the action's toolset once and reads its live AgentTool · harness/catalog_generator/catalog_generator.py:228
- `Catalog._render_catalog` `-> Catalog.utilities -> Utility.load_all -> RepositoryToolsets.collect` every toolset in space and tools not annotated @noCatalog · harness/catalog_generator/catalog_generator.py:184
- `Catalog._render_catalog` `-> PracticePage(practice), ActionPage(action), UtilityPage(utility), FidelityPage(...)` creates one page each · harness/catalog_generator/catalog_generator.py:1064
- `Catalog._write_detail_page` `-> Catalog.write_page(page.href, html)` writes `{out_root}/{href}` · harness/catalog_generator/catalog_generator.py:1101

## An action on guidance: GuidanceAction to PracticeGuidance to FidelityGuidance to rules to Validate

- `GuidanceAction.for_call` `-> ToolCall.session_named` makes the action for the session the call works in · harness/guidance_actions/guidance_actions.py:166
- `Validate.validate` `-> GuidanceAction._work_on(guidance) -> GuidanceArgument(guidance)` takes the guidance the call names · harness/guidance_actions/guidance_actions.py:216
- `GuidanceAction.listed` `-> ToolsetReference.parsed(entry).made(**context)` builds each PracticeGuidance a call names by its reference, then has the session's practice adopt it · harness/guidance_actions/guidance_actions.py:496
-   `<- list[PracticeGuidance]` · harness/guidance_actions/guidance_actions.py:248
- `Validate._fidelities` `-> PracticeGuidance.fidelities.current` the FidelityGuidance each guidance is at · cdd_guidance/actions/validate/validate.py:100
- `Validate.validate` `-> CheckedGraph(session, [CheckedFidelity(session, fidelity)], NamedToCheck(paths, graph, call))` refuses a path that is not there, claims each fidelity's *ValidationReport* (*ReportFiles*), then builds the graph from the checked files · cdd_guidance/actions/validate/validate.py:55
- `Validate.validate` `-> GuidanceAction.run(on, action="validate")` runs once per listed guidance and logs the action · cdd_guidance/actions/validate/validate.py:80
- `Validate.listed_rules -> _rules_text` `-> PracticeGuidance.checked_rule_collections` the shared rules, then the current fidelity's · cdd_guidance/actions/validate/validate.py:218
- `PracticeGuidance.checked_rule_collections` `-> FidelityGuidance.rules` <- list[RulesCollection] · harness/guidance/guidance.py:118
- `Validate.validate` `-> CheckedGraph.save(ReportText.for_saving())` writes the report into each claimed *ValidationReport* (`ReportFiles.save`), the graph's violations and their nodes beside it (`SavedGraph.violated`, at `ValidationReport.saved_graph`), and records the run in `session.folder.violation_history` · cdd_guidance/actions/validate/checked_graph.py

# harness/name

No class of this module acts on another class of the model at run time.

# harness/annotations

No class of this module acts on another class of the model at run time.

# harness/process

Starting, watching, and stopping other processes. Every class here is a leaf: it calls nothing else in the model, and the daemons and the scripts rely on it.

## RunningProcess

- **Used by**
  - `HookDaemon` `-> RunningProcess(pid).alive` checks whether the hook server holding the address file is still alive · harness/hooks/hook_daemon.py:130
  - `scripts/instances.py` `-> RunningProcess(pid).alive` lists live servers · scripts/instances.py:85

## RunningProcess, stopped

- `RunningProcess.stop`
  - `-> raise ProcessNotStopped` when the signal is refused or the process outlives the wait · harness/process/process.py
- `RunningProcess._wait_until_ended`
  - `-> raise ProcessNotStopped` · harness/process/process.py
- **Used by**
  - `ServerDaemon.stop` `-> RunningProcess.stop(STOP_SECONDS)` stops the cdd server before a restart and a hook daemon whose checkout closes · harness/process/server_daemon.py
  - `HookDaemon` `-> RunningProcess.stop(STOP_SECONDS)` replaces a stale hook server · harness/hooks/hook_daemon.py

## PythonInterpreter

- **Used by**
  - `McpDaemon._command` `-> home.interpreter.windowless` the interpreter the cdd server runs under · harness/mcp/mcp_daemon.py
  - `HookDaemon._command` `-> PythonInterpreter().windowless` the interpreter the hook server runs under · harness/hooks/hook_daemon.py
  - `Hooks` `-> PythonInterpreter(python).console` the interpreter each installed hook command calls · harness/hooks/hooks.py:206

## BackgroundStart

- `BackgroundStart.run` `-> RunningProcess` starts a process with no console window that breaks away from the starter's job, or `-> Wmi.create` outside every job where the job refuses breakaway · harness/process/process.py
- **Used by**
  - `ServerDaemon.spawn` `-> BackgroundStart().run` starts the cdd server and the hook server · harness/process/server_daemon.py
  - `scripts/start.py` `-> BackgroundStart().creationflags / .startupinfo` · scripts/start.py:184

# harness/git

Running git. Its class is a leaf: it calls nothing else in the model, and the repository, the catalog, the pinned runtime, and the release rely on it.

## Git

The one way the code runs git, with a timeout and no stdin.

- `Git.run`
  - `-> raise RepoConnectError` when git fails or times out · harness/git/git.py:41
- `Git._executable`
  - `-> raise RepoConnectError` when git is not installed · harness/git/git.py:65
- **Used by**
  - `Repo.git` `-> Git(root)` every branch, commit and worktree operation of a repository · space/repo/repo.py:122
  - `CddHome` `-> Git(folder).run / .succeeds` checks the remote and copies the pinned runtime · harness/mcp/cdd_home.py:69, :146, :177
  - `Catalog` `-> Git(repo_root)` reads the commit its source links cite · harness/catalog_generator/catalog_generator.py:419
  - `ProjectApproach` `-> RepoConnectError` reports a project with no reachable git · harness/catalog_generator/project_approach.py:23

# harness/markdown

## Markdown

- `Markdown.extract`
  - `-> MarkdownText()` creates · harness/markdown/markdown.py:868
- `Markdown.read_into`
  - `-> MarkdownText()` creates · harness/markdown/markdown.py:907
- `Markdown._template_format`
  - `-> Format()` creates · harness/markdown/markdown.py:938
  - `-> Format.from_extension` loads · harness/markdown/markdown.py:940

## MarkdownCollection

- `MarkdownCollection.from_markdown`
  - `-> MarkdownText().section_child_blocks` creates · harness/markdown/markdown.py:768
  - `-> MarkdownText()` creates · harness/markdown/markdown.py:768
  - `<- MarkdownCollection`
- `MarkdownCollection.from_section`
  - `-> Markdown.raw` calls raw on · harness/markdown/markdown.py:782
  - `-> Markdown.extract` calls extract on · harness/markdown/markdown.py:784
  - `-> Markdown.built_by` calls built_by on · harness/markdown/markdown.py:788
- `MarkdownCollection.as_property`
  - `-> Markdown.from_label` loads the prose it needs through · harness/markdown/markdown.py:813
  - `-> Markdown.read_into` reads into · harness/markdown/markdown.py:814
  - `-> Markdown.return_type_of` calls return_type_of on · harness/markdown/markdown.py:814
- `MarkdownCollection.read`
  - `-> Markdown.from_label` loads the prose it needs through · harness/markdown/markdown.py:813
  - `-> Markdown.read_into` reads into · harness/markdown/markdown.py:814
  - `-> Markdown.return_type_of` calls return_type_of on · harness/markdown/markdown.py:814

# harness/agent_tools

## AgentToolSet

- `AgentToolSet._made`
  - `-> ToolSubjectLoader()` creates · harness/agent_tools/agent_tools.py:506
- `AgentToolSet.toolset_collections`
  - `-> ToolSetCollectionAnnotation.annotates` reads the annotation · harness/agent_tools/agent_tools.py:516
- `AgentToolSet.tools`
  - `-> AgentTool.update` keeps · harness/agent_tools/agent_tools.py:538
  - `-> AgentTool.setdefault` keeps · harness/agent_tools/agent_tools.py:541
  - `<- dict[str, AgentTool]`
- `AgentToolSet.tools_for`
  - `-> AgentTool.values` keeps · harness/agent_tools/agent_tools.py:546
  - `<- list[AgentTool]`
- `AgentToolSet.session_for`
  - `-> ToolCall.session` reads session of · harness/agent_tools/agent_tools.py:555
- `AgentToolSet._discover_operations`
  - `-> AgentOperation()` creates · harness/agent_tools/agent_tools.py:563
  - `-> AgentToolAnnotation.annotates` reads the annotation · harness/agent_tools/agent_tools.py:564
- `AgentToolSet._operation_callable`
  - `-> ToolSubjectLoader()` creates · harness/agent_tools/agent_tools.py:568
  - `-> ToolSubjectLoader().given_the_called_project` creates · harness/agent_tools/agent_tools.py:570
  - `-> ToolSubjectLoader().on_subject` creates · harness/agent_tools/agent_tools.py:571
- `AgentToolSet._discover_instruction_members`
  - `-> AgentInstructions()` creates · harness/agent_tools/agent_tools.py:576
  - `-> AgentInstructionsAnnotation.annotates` reads the annotation · harness/agent_tools/agent_tools.py:577
- `AgentToolSet._discover_enlisted_members`
  - `-> AgentTool()` creates · harness/agent_tools/agent_tools.py:583
- `AgentToolSet._discover_collection_tools`
  - `-> AgentTool.update` keeps · harness/agent_tools/agent_tools.py:590
- `AgentToolSet._rehost_collection_tools`
  - `-> AgentTool()` creates · harness/agent_tools/agent_tools.py:608
- `AgentToolSet._is_collection_type`
  - `-> ToolSetCollectionAnnotation.annotates` reads the annotation · harness/agent_tools/agent_tools.py:644
  - `-> AgentToolSetAnnotation.annotates` reads the annotation · harness/agent_tools/agent_tools.py:644
- `AgentToolSet._is_tool_collection`
  - `-> ToolSetCollectionAnnotation.annotates` reads the annotation · harness/agent_tools/agent_tools.py:649
  - `-> AgentToolSetAnnotation.annotates` reads the annotation · harness/agent_tools/agent_tools.py:649

## AgentTool

- `AgentTool.slug`
  - `-> AgentToolSet.slug` reads slug of · harness/agent_tools/agent_tools.py:756
- `AgentTool.destinations`
  - `-> annotation_kinds.destinations_of` reads every destination kind that publishes the callable · harness/agent_tools/agent_tools.py:912
- `AgentTool.is_published_to`
  - `-> DestinationKind.publishes` asks the destination whether it publishes the callable · harness/agent_tools/agent_tools.py:916
- `AgentTool.deploy_name`
  - `-> annotation_kinds.deploy_name_of` reads the name a destination's annotation gave the callable · harness/agent_tools/agent_tools.py:965
- `AgentTool.invoke`
  - `-> ToolCall()` creates · harness/agent_tools/agent_tools.py:796
- `AgentTool.answer`
  - `-> AgentToolSet.for_call` loads · harness/agent_tools/agent_tools.py:801
  - `-> ToolCall.arguments` reads arguments of · harness/agent_tools/agent_tools.py:803
- `AgentTool._called_project`
  - `-> TakesCalledProject.annotates` reads the annotation · harness/agent_tools/agent_tools.py:815
  - `-> ToolCall.project` reads project of · harness/agent_tools/agent_tools.py:817
- `AgentTool.should_log_session_invocation`
  - `-> NoSessionLog.annotates` reads the annotation · harness/agent_tools/agent_tools.py:824
  - `-> AgentToolAnnotation.annotates` reads the annotation · harness/agent_tools/agent_tools.py:826
- `AgentTool.log_session_invocation`
  - `-> ToolCall.arguments` reads arguments of · harness/agent_tools/agent_tools.py:833
  - `-> AgentToolSet.session_for` calls session_for on · harness/agent_tools/agent_tools.py:835
- `AgentTool.kind`
  - `-> AgentToolAnnotation.annotates` reads the annotation · harness/agent_tools/agent_tools.py:847
  - `-> AgentInstructionsAnnotation.annotates` reads the annotation · harness/agent_tools/agent_tools.py:849
- `AgentTool._with_sub_agent_preamble`
  - `-> SubAgentAnnotation.annotates` reads the annotation · harness/agent_tools/agent_tools.py:874
  - `-> SubAgentAnnotation.with_hand_off` reads the annotation · harness/agent_tools/agent_tools.py:874
- `AgentTool.description`
  - `-> Markdown.from_label` loads the prose it needs through · harness/agent_tools/agent_tools.py:879
- `AgentTool` `-> NoDeploy` is kept out of install by · harness/agent_tools/agent_tools.py:740

## GuidanceAgentOperation

- `GuidanceAgentOperation.log_session_invocation`
  - `-> ToolCall.arguments` reads arguments of · harness/agent_tools/agent_tools.py:962

## AgentInstructions

- `AgentInstructions.kind`
  - `-> AgentToolAnnotation.annotates` reads the annotation · harness/agent_tools/agent_tools.py:974
- `AgentInstructions.for_callable`
  - `-> AgentToolSet._discover_instruction_members` calls discover_instruction_members on · harness/agent_tools/agent_tools.py:987
  - `-> AgentToolSet()` creates · harness/agent_tools/agent_tools.py:991
  - `<- AgentInstructions`
- `AgentInstructions.answer`
  - `-> ToolCall.arguments` reads arguments of · harness/agent_tools/agent_tools.py:1010
- `AgentInstructions.member_of`
  - `-> AgentToolSet._discover_instruction_members` calls discover_instruction_members on · harness/agent_tools/agent_tools.py:1052
  - `<- AgentInstructions`
- `AgentInstructions.provider_of`
  - `-> AgentToolSetAnnotation.annotates` reads the annotation · harness/agent_tools/agent_tools.py:1057
- `AgentInstructions.parent_recipe`
  - `-> AgentInstructionsAnnotation.annotates` reads the annotation · harness/agent_tools/agent_tools.py:1077
  - `<- tuple[AgentInstructions, type] | None`

## AgentToolSetAnnotation

- `AgentToolSetAnnotation` `-> AgentToolSet` joins the annotated class with · harness/agent_tools/agent_tools.py:1174

## ToolSubjectLoader

- `ToolSubjectLoader.loader`
  - `-> ToolSubject.annotates` reads the annotation · harness/agent_tools/agent_tools.py:665
- `ToolSubjectLoader.on_subject`
  - `-> TakesCalledProject.annotates` reads the annotation · harness/agent_tools/agent_tools.py:674
  - `-> TakesCalledProject()` creates · harness/agent_tools/agent_tools.py:684
  - `-> OnSubject()` creates · harness/agent_tools/agent_tools.py:685
- `ToolSubjectLoader.given_the_called_project`
  - `-> TakesCalledProject()` creates · harness/agent_tools/agent_tools.py:701

## ToolCall

- `ToolCall.sent`
  - `-> ChatPointer.taken_from` loads · harness/agent_tools/tool_call.py:65
  - `<- ToolCall`
- `ToolCall.identity`
  - `-> ChatPointer.id` reads id of · harness/agent_tools/tool_call.py:72

## ChatPointer

- `ChatPointer._headers`
  - `-> Name()` creates · harness/agent_tools/chat_pointer.py:105

# harness/installation

## FileInstallation

- `FileInstallation.write`
  - `-> FileInstallation.relative_path` asks the channel where the file goes · harness/installation/files.py:129
  - `-> FileInstallation.front_matter` asks the channel what opens the file · harness/installation/files.py:132
  - `-> AgentTool.toolset` reads toolset of · harness/installation/files.py:129
  - `-> AgentTool.deploy_name` reads deploy name of · harness/installation/files.py:129
- `FileInstallation.body`
  - `-> AgentTool.kind` reads kind of · harness/installation/files.py:123
  - `-> AgentTool.docstring` reads docstring of · harness/installation/files.py:125
- `FileInstallation._served`
  - `-> AgentTool.is_published_to(annotation_kinds.answering_calls)` asks whether a server answers the agent's calls to it · harness/installation/files.py:136
- `FileInstallation._parts`
  - `-> AgentTool.invoke_line` calls invoke_line on · harness/installation/files.py:138
- `FileInstallation._shell_command`
  - `-> AgentTool.deploy_name` reads deploy name of · harness/installation/files.py:210
  - `-> AgentToolSet.reference` reads the toolset's reference for `ToolsetReference.parsed(...).made()` · harness/installation/files.py:213
- `FileInstallation._needs_shell_invoke`
  - `-> AgentTool.kind` reads kind of · harness/installation/files.py:220
- `FileInstallation._fidelity_invoke_parts`
  - `-> AgentTool.invoke_line` calls invoke_line on · harness/installation/files.py:231

## SkillInstallation : FileInstallation

- `SkillInstallation.relative_path`
  - `-> Name()` creates · harness/installation/files.py:272
  - `-> IdeLayout.nests_skills` reads nests skills of · harness/installation/files.py:273
- `SkillInstallation._skill_operations`
  - `-> AgentTool.is_published_to(Skill)` reads the skill annotation · harness/installation/files.py:286
- `SkillInstallation._skill_folder`
  - `-> InstallPlace.folder_for` reads the folder the toolset's guidance is installed under · harness/installation/files.py:289
- `SkillInstallation` `-> Skill` writes the SKILL.md for · harness/installation/files.py:269

## CommandInstallation : FileInstallation

- `CommandInstallation.relative_path`
  - `-> IdeLayout.commands_folder` reads commands folder of · harness/installation/files.py:332
- `CommandInstallation` `-> Command` writes the slash command for · harness/installation/files.py:327

## RulesInstallation : FileInstallation

- `RulesInstallation.relative_path`
  - `-> IdeLayout.rule_suffix` reads rule suffix of · harness/installation/files.py:344
- `RulesInstallation.write_standing_rule`
  - `-> FrontMatter.of_file` reads the rule's front matter · harness/installation/files.py:360
  - `-> IdeLayout.scopes_rules_by_paths` reads scopes rules by paths of · harness/installation/files.py:362
  - `-> IdeLayout.rule_suffix` reads rule suffix of · harness/installation/files.py:366
- `RulesInstallation` `-> Rules` writes the rules file for · harness/installation/files.py:339

## LanguageAdapters : InstallPlace

- `LanguageAdapters.record`
  - `-> DataClass.languages` reads the LanguageAdapter annotation · harness/installation/language_adapter.py:862
- `LanguageAdapters` `-> LanguageAdapter` generates TypeScript for · harness/installation/language_adapter.py:860
- `LanguageAdapters` `-> SourceFile` draws a file link for fields annotated · harness/installation/language_adapter.py:196

## RepositoryToolsets

- `RepositoryToolsets._toolset_refs_in_file`
  - `-> AgentToolSet.HOSTED_ONLY_CLASS_NAMES` reads constants of · harness/installation/repository_toolsets.py:130
- `RepositoryToolsets._class_is_installable`
  - `-> Name()` creates · harness/installation/repository_toolsets.py:167

## DataClass

- `DataClass.fields`
  - `-> DataField.annotates` reads the annotation · harness/installation/destination.py:152
  - `-> DataField.flag` reads the annotation · harness/installation/destination.py:153
- `DataClass.identity`
  - `-> Identity.flag` reads the annotation · harness/installation/destination.py:159
- `DataClass.languages`
  - `-> LanguageAdapter.flag` reads the annotation · harness/installation/destination.py:164
- `DataClass.edited_by`
  - `-> Edits.flag` reads the annotation · harness/installation/destination.py:168
- `DataClass.sends_by_identity`
  - `-> DataField.reference_flag` reads the annotation · harness/installation/destination.py:172

# harness/hooks

## HookServer

- `HookServer.session`
  - `-> ToolCall()` creates · harness/hooks/hook_server.py:520
- `HookServer.handle_stdin`
  - `-> HookPayload.from_stdin` loads · harness/hooks/hook_server.py:538
  - `-> HookPayload.hook_event_name` reads hook event name of · harness/hooks/hook_server.py:545
- `HookServer._with_chat_injections`
  - `-> HookPayload.hook_event_name` reads hook event name of · harness/hooks/hook_server.py:553
- `HookServer.dispatch`
  - `-> HookPayload.hook_event_name` reads hook event name of · harness/hooks/hook_server.py:558
  - `-> HookPayload.tool_name` reads tool name of · harness/hooks/hook_server.py:560
  - `-> HookPayload.edited_path` calls edited_path on · harness/hooks/hook_server.py:560
  - `-> HookPayload.conversation_id` reads conversation id of · harness/hooks/hook_server.py:561
- `HookServer.diagnose`
  - `-> HookPayload()` creates · harness/hooks/hook_server.py:574
- `HookServer._show_toast`
  - `-> HookPayload.workspace_roots` reads workspace roots of · harness/hooks/hook_server.py:623
- `HookServer` `-> Hook` runs the members annotated · harness/hooks/hook_server.py:380

## HookDaemon

- `HookDaemon.replace_stale`
  - `-> RunningProcess().stop` creates · harness/hooks/hook_daemon.py:204
  - `-> RunningProcess()` creates · harness/hooks/hook_daemon.py:204
- `HookDaemon.spawn`
  - `-> RepositoryToolsets()` creates · harness/hooks/hook_daemon.py:220
  - `-> RepositoryToolsets.pycache_prefix` calls pycache_prefix on · harness/hooks/hook_daemon.py:224
  - `-> RepositoryToolsets.pythonpath` calls pythonpath on · harness/hooks/hook_daemon.py:225
  - `-> BackgroundStart().run` creates · harness/hooks/hook_daemon.py:229
  - `-> BackgroundStart()` creates · harness/hooks/hook_daemon.py:229
  - `-> PythonInterpreter()` creates · harness/hooks/hook_daemon.py:230
- `HookDaemon._loaded_server`
  - `-> RepositoryToolsets().import_modules` creates · harness/hooks/hook_daemon.py:251
  - `-> RepositoryToolsets()` creates · harness/hooks/hook_daemon.py:251
  - `-> HookServer.from_toolsets` loads · harness/hooks/hook_daemon.py:252
- `HookDaemon._handle`
  - `-> HookServer.handle_stdin` handles stdin · harness/hooks/hook_daemon.py:339
- `HookDaemon` `-> RunningProcess` checks the lock holder is alive with · harness/hooks/hook_daemon.py:130

## HookInstallation : RegisteredChannel

- `HookInstallation.dispatch_command`
  - `-> PythonInterpreter()` creates · harness/hooks/hook_installation.py:36
- `HookInstallation.accepts`
  - `-> RegisteredChannel.accepts` asks whether the tool is published to Hook · harness/hooks/hook_installation.py:45
  - `-> IdeLayout.runs_hooks` reads runs hooks of · harness/hooks/hook_installation.py:45
- `HookInstallation.write`
  - `-> Hook.name_given` reads the event the operation runs on · harness/hooks/hook_installation.py:68
  - `-> AgentTool.is_published_to(Hook)` reads the hook annotation · harness/hooks/hook_installation.py:69
  - `-> AgentTool.toolset` reads toolset of · harness/hooks/hook_installation.py:71
  - `-> AgentTool.name` reads name of · harness/hooks/hook_installation.py:73
  - `-> AgentToolSet.reference` reads the toolset's reference, written as its text · harness/hooks/hook_installation.py:73
- `HookInstallation` `-> Hook` enrolls in hooks.json · harness/hooks/hook_installation.py:68

# harness/mcp

## McpHost

- `McpHost.__init__`
  - `-> ProjectToolsets.project` reads project of · harness/mcp/mcp_server.py:668
- `McpHost._server_for`
  - `-> ProjectToolsets.for_project` loads · harness/mcp/mcp_server.py:689
  - `<- ProjectToolsets`
- `McpHost.tools_listed_for`
  - `-> ServerLane.tools_for` the other lane's tools, when it answers the project · harness/mcp/mcp_server.py:699
  - `-> ProjectToolsets.tools` reads tools of · harness/mcp/mcp_server.py:709
  - `-> ProjectToolsets.prompts` reads prompts of · harness/mcp/mcp_server.py:709
- `McpHost.call_sent`
  - `-> ToolCall.sent` loads, from `tool_call` as it is now · harness/mcp/mcp_server.py:724
- `McpHost.tool_request`
  - `-> ToolRequest()` creates, from `tool_call` as it is now · harness/mcp/mcp_server.py:729
- `McpHost.answer_for_chat`
  - `-> McpHost.answer` answers while the call is the one being answered · harness/mcp/mcp_server.py:742
- `McpHost.dispatch`
  - `-> ProjectToolsets.resolve_call_name` resolves call name · harness/mcp/mcp_server.py:748
  - `-> McpHost.call_sent` creates the call · harness/mcp/mcp_server.py:749
- `McpHost.answer`
  - `-> ToolCall.tool` reads tool of · harness/mcp/mcp_server.py:753
  - `-> McpHost._answer_between_restarts` · harness/mcp/mcp_server.py:763
- `McpHost._answer_between_restarts`
  - `-> McpHost._server_for(call.project)` finds the project's ProjectToolsets · harness/mcp/mcp_server.py:777
  - `-> ToolCall.arguments` reads arguments of · harness/mcp/mcp_server.py:779
  - `-> ProjectToolsets.answer` · harness/mcp/mcp_server.py:781
- `McpHost._ping_tool`
  - `-> ProjectToolsets.enrolled` calls enrolled on · harness/mcp/mcp_server.py:787
- `McpHost._log_failure`
  - `-> ToolCall.session` reads session of · harness/mcp/mcp_server.py:792
- `McpHost.restart`
  - `-> ProjectToolsets.restarted` calls restarted on · harness/mcp/mcp_server.py:801
  - `-> ProjectToolsets.skipped` reads skipped of · harness/mcp/mcp_server.py:806
- `McpHost._publish_mods`
  - `-> ClaudeMarketplace.publish_mods` publishes the mods of the code the server now runs into its own lane's marketplace · harness/mcp/mcp_server.py:812
- `McpHost.from_repo`
  - `-> ProjectToolsets.of_repo` · harness/mcp/mcp_server.py:829
  - `<- McpHost` made with its lanes and cdd home
- `McpHost.from_refs`
  - `-> ProjectToolsets.of_refs` · harness/mcp/mcp_server.py:842
  - `<- McpHost` made with its lanes and cdd home

## ChatProtocol

- `ChatProtocol.__init__`
  - `-> _ToolCalls()` creates, answering each call through `McpHost.answer_for_chat` · harness/mcp/mcp_server.py:854
- `ChatProtocol.handle_list_tools`
  - `-> McpHost.tools_listed_for` · harness/mcp/mcp_server.py:911
- `ChatProtocol.handle_get_prompt`
  - `-> ProjectToolsets.prompts` reads prompts of · harness/mcp/mcp_server.py:938
- `ChatProtocol._call_from_chat`
  - `-> ProjectToolsets.resolve_call_name` resolves call name · harness/mcp/mcp_server.py:971
  - `-> ChatProtocol._chat_request` the request being answered · harness/mcp/mcp_server.py:972
  - `-> ChatRequest.project_for` the project the call works on · harness/mcp/mcp_server.py:973
  - `-> ChatRequest.tool_request` the request the call answers · harness/mcp/mcp_server.py:973
  - `-> McpHost.call_sent` creates the call · harness/mcp/mcp_server.py:973
- `ChatProtocol._chat_request`
  - `-> ChatRequest()` creates, from this module as it is now · harness/mcp/mcp_server.py:982
  - `<- ChatRequest`
- `ChatProtocol._answer_off_loop`
  - `-> ProjectToolsets.call_seconds` calls seconds · harness/mcp/mcp_server.py:991
- `ChatProtocol._progress_reporter`
  - `-> ThrottledReporter()` creates · harness/mcp/mcp_server.py:1017

## HttpEndpoints

- `HttpEndpoints.__init__`
  - `-> ChatProtocol()` creates the protocol it speaks to chats, for its host · harness/mcp/mcp_server.py:1028
- `HttpEndpoints.serve`
  - `-> ProjectToolsets.repo` reads repo of · harness/mcp/mcp_server.py:1036
- `HttpEndpoints.app`
  - `-> ChatProtocol.protocol` serves MCP through · harness/mcp/mcp_server.py:1053
- `HttpEndpoints._answer_lane_call`
  - `-> ToolCall.from_sent` reads the handed-over call back, from `tool_call` as it is now · harness/mcp/mcp_server.py:1074
  - `-> LaneReply.failed` replies with the failure by kind and message · harness/mcp/mcp_server.py:1078
- `HttpEndpoints._answer_off_loop`
  - `-> McpHost.answer_for_chat` · harness/mcp/mcp_server.py:1085
  - `-> raise _LaneCallFailed` carrying the failure back · harness/mcp/mcp_server.py:1087

## ChatRequest

- `ChatRequest.process`
  - `-> ClaudeChatProcess.from_header` the process `X-CDD-Chat-Process` names · harness/mcp/mcp_server.py:546
  - `-> ClaudeChatProcess.from_connection` the process holding the request's connection · harness/mcp/mcp_server.py:549
- `ChatRequest.chat`
  - `-> ChatPointer.from_request` · harness/mcp/mcp_server.py:557
- `ChatRequest.project_for`
  - `-> raise ProjectNotNamed` when no folder is found · harness/mcp/mcp_server.py:572
  - `-> raise ProjectIsClaudeSettings` when the folder is Claude Code's settings folder · harness/mcp/mcp_server.py:574
- `ChatRequest.tool_request`
  - `-> ToolRequest()` creates, answered for this chat · harness/mcp/mcp_server.py:579
- `ChatRequest._folder_of_chat`
  - `-> ChatPointer.from_claude_session` · harness/mcp/mcp_server.py:601

## ProjectToolsets

- `ProjectToolsets.enroll`
  - `-> AgentTool.mcp_name` reads mcp name of · harness/mcp/mcp_server.py:411
  - `-> AgentTool.input_schema` reads input schema of · harness/mcp/mcp_server.py:419
  - `-> AgentTool.kind` reads kind of · harness/mcp/mcp_server.py:423
- `ProjectToolsets.start`
  - `-> ToolsetReference.made` makes each toolset its reference names · harness/mcp/mcp_server.py:399
- `ProjectToolsets._enroll_toolset`
  - `-> AgentToolSet.tools_published_to(Mcp)` reads the operations annotated @mcp · harness/mcp/mcp_server.py:450
- `ProjectToolsets.enrolled`
  - `-> AgentTool.get` keeps · harness/mcp/mcp_server.py:510
  - `<- AgentTool | None`
- `ProjectToolsets.call_seconds`
  - `-> LongCall.annotates` reads the annotation · harness/mcp/mcp_server.py:518
- `ProjectToolsets.invoke`
  - `-> ToolCall()` creates · harness/mcp/mcp_server.py:489
- `ProjectToolsets.of_repo`
  - `-> RepositoryToolsets()` creates · harness/mcp/mcp_server.py:524
  - `-> ProjectToolsets.start` starts every toolset class of the checkout · harness/mcp/mcp_server.py:527
  - `-> raise McpStandupFailed` when it cannot stand up · harness/mcp/mcp_server.py:532
- `ProjectToolsets.of_refs`
  - `-> ProjectToolsets.start` starts the toolsets the references name · harness/mcp/mcp_server.py:540
- `ProjectToolsets` `-> Mcp` serves the operations annotated · harness/mcp/mcp_server.py:450

## McpInstallation : RegisteredChannel

- `McpInstallation.__init__`
  - `-> McpChannelServer()` creates its server · harness/mcp/mcp_server.py:336
- `McpInstallation.write`
  - `-> AgentTool.is_published_to(Mcp)` reads the MCP annotation · harness/mcp/mcp_server.py:351
- `McpInstallation.write_once_recorded`
  - `-> CddEntry.write` once an MCP operation is recorded · harness/mcp/mcp_server.py:357
- `McpInstallation.status`
  - `-> CddEntry.names_running_server` whether the server the entry names runs · harness/mcp/mcp_server.py:365
- `McpInstallation` `-> Mcp` publishes as a cdd MCP tool · harness/mcp/mcp_server.py:327

## McpChannelServer : ChannelServer

- `McpChannelServer.stand_up`
  - `-> McpHost.from_repo` loads every toolset of the served checkout · harness/mcp/mcp_server.py:278
  - `-> StandUp()` creates what the server serves and skipped · harness/mcp/mcp_server.py:280
- `McpChannelServer.ensure_running`
  - `-> McpChannelServer.install_plugins` · harness/mcp/mcp_server.py:304
- `McpChannelServer.install_plugins`
  - `-> ClaudePlugins.install(marketplace.cdd_plugin)` installs the cdd plugin the stable lane publishes · harness/mcp/mcp_server.py:312
  - `-> ClaudePlugins.install` installs each of the served lane's `marketplace.mods` · harness/mcp/mcp_server.py:313

## UserMcpConfig

- `UserMcpConfig.__init__`
  - `-> IdeLayout()` creates · harness/mcp/mcp_server.py:112
- `UserMcpConfig.folder`
  - `-> IdeLayout.user_settings_folder` reads user settings folder of · harness/mcp/mcp_server.py:117
- `UserMcpConfig.path`
  - `-> IdeLayout.user_mcp_config` reads user mcp config of · harness/mcp/mcp_server.py:121
- `UserMcpConfig.servers_key`
  - `-> IdeLayout.mcp_servers_key` reads mcp servers key of · harness/mcp/mcp_server.py:125

## CddHome

- `CddHome.__init__`
  - `-> ClaudeMarketplace()` creates the marketplace it publishes · harness/mcp/cdd_home.py:75
- `CddHome.pin`
  - `-> ClaudeMarketplace.publish_mods` publishes the mods of the code just pinned · harness/mcp/cdd_home.py:188
- `CddHome.serve_from`
  - `-> ClaudeMarketplace.publish_mods` publishes the mods of the checkout served from disk · harness/mcp/cdd_home.py:210
- `CddHome._mirror_origin`
  - `-> Git.succeeds` · harness/mcp/cdd_home.py:193
- `CddHome._git`
  - `-> Git.run` · harness/mcp/cdd_home.py:229

## ClaudeMarketplace

- `ClaudeMarketplace.__init__`
  - `-> InstallLock()` creates, held while one install publishes the mods · harness/mcp/claude_marketplace.py:157
- `ClaudeMarketplace.plugin`
  - `-> PublishedPlugin()` creates · harness/mcp/claude_marketplace.py:160
- `ClaudeMarketplace.mods`
  - `-> PublishedMods.every` the mods the served code declares · harness/mcp/claude_marketplace.py:170
- `ClaudeMarketplace.publish_mods`
  - `-> InstallLock.held` · harness/mcp/claude_marketplace.py:211
  - `-> PublishedMods.every` · harness/mcp/claude_marketplace.py:212
  - `-> PublishedPlugin.publish_from` · harness/mcp/claude_marketplace.py:214
- `PublishedMods.every`
  - `-> PublishedMod()` creates, one for each `cdd-mod.json` · harness/mcp/claude_marketplace.py:72

## ClaudePlugins

- `ClaudePlugins.install`
  - `-> ClaudePlugins.is_watched` · harness/mcp/claude_plugins.py:60
  - `-> PublishedPlugin.version` compares with the installed version · harness/mcp/claude_plugins.py:64
  - `-> PluginInstall()` creates · harness/mcp/claude_plugins.py:61, :65, :73
- `ClaudePlugins.is_watched`
  - `-> ClaudeMarketplace.mod_folder` the folder Claude Code loads the plugin from · harness/mcp/claude_plugins.py:97

## SpecServer

- `SpecServer.__init__`
  - `-> CddHome()` creates · harness/mcp/spec_support.py:49
- `SpecServer.install`
  - `-> CddHome.folder` reads folder of · harness/mcp/spec_support.py:60
  - `-> CddHome.serve_from` serves from · harness/mcp/spec_support.py:63
  - `-> CddHome.install` installs · harness/mcp/spec_support.py:64
- `SpecServer.stop`
  - `-> CddHome.connect_script` reads connect script of · harness/mcp/spec_support.py:73
  - `-> CddHome.folder` reads folder of · harness/mcp/spec_support.py:80

# harness/guidance

## Guidance

- `Guidance.slug`
  - `-> Name()` creates · harness/guidance/guidance.py:75
- `Guidance.overview`
  - `-> Markdown.from_label` loads the prose it needs through · harness/guidance/guidance.py:104
- `Guidance.guidance`
  - `-> Markdown.from_label` loads the prose it needs through · harness/guidance/guidance.py:110
- `Guidance.rules_after_edit`
  - `-> Hook.disabled_on` reads the annotation · harness/guidance/guidance.py:160

## PracticeGuidance

- `PracticeGuidance.project_rules`
  - `-> Name()` creates · harness/guidance/guidance.py:316
- `PracticeGuidance._project_rules_in`
  - `-> RulesCollection.from_markdown` loads · harness/guidance/guidance.py:325
- `PracticeGuidance._activate_fidelity`
  - `-> Format()` creates · harness/guidance/guidance.py:359
- `PracticeGuidance._check_format`
  - `-> Format()` creates · harness/guidance/guidance.py:379
- `PracticeGuidance._guidance_parts`
  - `-> Markdown.from_label` loads the prose it needs through · harness/guidance/guidance.py:423
- `PracticeGuidance.instructions`
  - `-> Guidance.instructions` reads instructions of · harness/guidance/guidance.py:440
- `PracticeGuidance.schema_node_fidelities`
  - `-> Schema().fidelities` creates · harness/guidance/guidance.py:470
  - `-> Schema()` creates · harness/guidance/guidance.py:470
- `PracticeGuidance.schema_fidelity_errors`
  - `-> Schema().fidelities` creates · harness/guidance/guidance.py:476
  - `-> Schema()` creates · harness/guidance/guidance.py:476
- `PracticeGuidance._format_adapter`
  - `-> Format()` creates · harness/guidance/guidance.py:508
- `PracticeGuidance._kept_wording`
  - `-> Format()` creates · harness/guidance/guidance.py:557
- `PracticeGuidance._to_object_model`
  - `-> Format()` creates · harness/guidance/guidance.py:571
- `PracticeGuidance._is_tool`
  - `-> AgentToolSetAnnotation.annotates` reads the annotation · harness/guidance/guidance.py:586
- `PracticeGuidance._instantiate_from_tool`
  - `-> Format()` creates · harness/guidance/guidance.py:589
- `PracticeGuidance._incoming`
  - `-> Format()` creates · harness/guidance/guidance.py:650
- `PracticeGuidance.scoped_markdown`
  - `-> Markdown.from_label` loads the prose it needs through · harness/guidance/guidance.py:663
  - `-> MarkdownText().fidelity_blocks` creates · harness/guidance/guidance.py:670
  - `-> MarkdownText()` creates · harness/guidance/guidance.py:670
- `PracticeGuidance._skip_inactive_fidelity`
  - `-> Name()` creates · harness/guidance/guidance.py:679

## FidelityGuidance

- `FidelityGuidance.format`
  - `-> Format()` creates · harness/guidance/guidance.py:798
- `FidelityGuidance.default_format`
  - `-> Format()` creates · harness/guidance/guidance.py:814
- `FidelityGuidance.clean_engineering`
  - `-> PracticeCatalogue.create` loads · harness/guidance/guidance.py:836
  - `-> Name()` creates · harness/guidance/guidance.py:844
  - `<- FidelityGuidance | None`
- `FidelityGuidance.slug`
  - `-> PracticeGuidance.slug` reads slug of · harness/guidance/guidance.py:849
  - `-> Name()` creates · harness/guidance/guidance.py:850
- `FidelityGuidance.scaffold`
  - `-> Markdown.from_label` loads the prose it needs through · harness/guidance/guidance.py:864
- `FidelityGuidance.section`
  - `-> MarkdownText().fidelity_block` creates · harness/guidance/guidance.py:875
  - `-> MarkdownText()` creates · harness/guidance/guidance.py:875
- `FidelityGuidance.instructions`
  - `-> Markdown.from_label` loads the prose it needs through · harness/guidance/guidance.py:896
- `FidelityGuidance._template`
  - `-> Markdown.from_label` loads the prose it needs through · harness/guidance/guidance.py:926
- Annotations it carries: `Rules` · harness/guidance/guidance.py:89

## GuidanceCollection

- `GuidanceCollection.child`
  - `-> FidelityGuidance()` creates · harness/guidance/guidance.py:199
  - `<- FidelityGuidance`
- Annotations it carries: `ToolSetCollectionAnnotation` · harness/guidance/guidance.py:183

## Rule

- `Rule.from_bullet`
  - `-> Name()` creates · harness/guidance/rule.py:134
  - `<- Rule`

## RulesCollection

- `RulesCollection.inject_rules`
  - `-> HookPayload.edited_path` calls edited_path on · harness/guidance/rule.py:158
  - `-> Hook.disabled_on` reads the annotation · harness/guidance/rule.py:163
  - `-> HookPayload.get` keeps · harness/guidance/rule.py:167
- `RulesCollection._note_session_injected_rules`
  - `-> ToolCall()` creates · harness/guidance/rule.py:174
  - `-> HookPayload.tool_input` reads tool input of · harness/guidance/rule.py:174
  - `-> HookPayload.project` reads project of · harness/guidance/rule.py:174
- `RulesCollection.from_markdown`
  - `-> MarkdownText()` creates · harness/guidance/rule.py:343
  - `-> Rule.from_bullet` loads · harness/guidance/rule.py:347
  - `-> Rule.slug` reads slug of · harness/guidance/rule.py:348
  - `<- RulesCollection`

## ActionCatalogue

- `ActionCatalogue.actions`
  - `-> Action()` creates · harness/guidance/action_catalogue.py:76
  - `-> Skill.publishes` reads the skill annotation of each member · harness/guidance/action_catalogue.py:159
  - `<- tuple[Action, ...]`
- `ActionCatalogue._toolset_in`
  - `-> Name()` creates · harness/guidance/action_catalogue.py:105

# harness/guidance_actions

## GuidanceAction

- `GuidanceAction.for_call`
  - `-> ToolCall.arguments` reads arguments of · harness/guidance_actions/guidance_actions.py:164
  - `-> ToolCall.session` reads session of · harness/guidance_actions/guidance_actions.py:166
  - `-> ToolCall.session_named` calls session_named on · harness/guidance_actions/guidance_actions.py:166
  - `<- GuidanceAction`
- `GuidanceAction.session`
  - `-> raise ActionWorksInNoSession` raises · harness/guidance_actions/guidance_actions.py:182
- `GuidanceAction._discover_operations`
  - `-> GuidanceAgentOperation()` creates · harness/guidance_actions/guidance_actions.py:207
  - `-> AgentToolAnnotation.annotates` reads the annotation · harness/guidance_actions/guidance_actions.py:208
- `GuidanceAction._made`
  - `-> ToolsetReference.parsed` reads the reference a call sends · harness/guidance_actions/guidance_actions.py:498
  - `-> ToolsetReference.made` makes the guidance it names, with its context · harness/guidance_actions/guidance_actions.py:501
- `GuidanceAction._session_practice`
  - `-> PracticeCatalogue.has` checks a practice name with · harness/guidance_actions/guidance_actions.py:263
- `GuidanceAction.inject_rules`
  - `-> ToolCall()` creates · harness/guidance_actions/guidance_actions.py:374
  - `-> HookPayload.tool_input` reads tool input of · harness/guidance_actions/guidance_actions.py:374
  - `-> HookPayload.project` reads project of · harness/guidance_actions/guidance_actions.py:374
  - `-> Name()` creates · harness/guidance_actions/guidance_actions.py:378
- `GuidanceAction._is_this_action`
  - `-> HookPayload.tool_name` reads tool name of · harness/guidance_actions/guidance_actions.py:905
  - `-> AgentToolSet.tools_published_to(annotation_kinds.answering_calls)` reads the tools published where a server answers calls · harness/guidance_actions/guidance_actions.py:905
- Annotations it carries: `Toast` · harness/guidance_actions/guidance_actions.py:321

# harness/graph

## Graph

- `Graph.overlay_patterns`
  - `-> PatternOverlays()` creates · harness/graph/graph.py:1052
- `Graph.practice`
  - `-> PracticeGraph.setdefault` keeps · harness/graph/graph.py:1055
  - `-> PracticeGraph()` creates · harness/graph/graph.py:1055
  - `<- PracticeGraph`
- `Graph.load_working_copy`
  - `-> PatternOverlays()` creates · harness/graph/graph.py:1080
- `Graph.load_files`
  - `-> PatternOverlays()` creates · harness/graph/graph.py:1112
- `Graph.write_json`
  - `-> SavedGraph.from_graph` loads · harness/graph/graph.py:1164
- `Graph.save_json`
  - `-> SavedGraph.from_graph` loads · harness/graph/graph.py:1177
- `Graph._build_working_copy`
  - `-> PracticeGraph.values` keeps · harness/graph/graph.py:1193
- `Graph._load_saved`
  - `-> SavedGraph.practices` reads practices of · harness/graph/graph.py:1203
  - `-> PracticeGraph.values` keeps · harness/graph/graph.py:1208
- `Graph.set_overlays`
  - `-> PatternOverlays()` creates · harness/graph/graph.py:1242
- `Graph.overlay_of`
  - `-> PatternOverlays().root_of` creates · harness/graph/graph.py:1253
  - `-> PatternOverlays()` creates · harness/graph/graph.py:1253
- `Graph.practice_names`
  - `-> PracticeCatalogue.keys` keeps · harness/graph/graph.py:1264
- `Graph.inventory`
  - `-> PatternOverlays()` creates · harness/graph/graph.py:1270
- `Graph._node`
  - `-> PracticeGraph.values` keeps · harness/graph/graph.py:1295
- `Graph._source_members`
  - `-> GraphPractices.named` loads · harness/graph/graph.py:1299
  - `-> PracticeGraph.values` keeps · harness/graph/graph.py:1302
- `Graph.return_nodes`
  - `-> PracticeGraph.values` keeps · harness/graph/graph.py:1318
- `Graph._collect_nodes`
  - `-> Node.name` reads name of · harness/graph/graph.py:1326
  - `-> Node.rules` reads rules of · harness/graph/graph.py:1328
  - `-> Node.children` reads children of · harness/graph/graph.py:1330

## PracticeGraph

- `PracticeGraph.__init__`
  - `-> Node()` creates · harness/graph/graph.py:740
  - `-> Source()` creates · harness/graph/graph.py:740
- `PracticeGraph.rule_labels_for`
  - `-> Node.get` keeps · harness/graph/graph.py:788
- `PracticeGraph.schema`
  - `-> Graph.overlay_patterns` reads overlay patterns of · harness/graph/graph.py:797
- `PracticeGraph.tree`
  - `-> Node.serialize` calls serialize on · harness/graph/graph.py:803
- `PracticeGraph.add`
  - `-> Node.get` keeps · harness/graph/graph.py:810
  - `-> Node.release` calls release on · harness/graph/graph.py:813
  - `-> Node.parent` reads parent of · harness/graph/graph.py:816
  - `-> Node.place` places with · harness/graph/graph.py:818
  - `<- Node`
- `PracticeGraph._holds`
  - `-> Node.get` keeps · harness/graph/graph.py:832
- `PracticeGraph.add_named`
  - `-> Node()` creates · harness/graph/graph.py:836
  - `-> Source.file` reads file of · harness/graph/graph.py:837
  - `-> Source.start_line` reads start line of · harness/graph/graph.py:837
  - `-> Source.end_line` reads end line of · harness/graph/graph.py:837
  - `<- Node`
- `PracticeGraph._register`
  - `-> Node.type` reads type of · harness/graph/graph.py:841
  - `-> Node.setdefault` keeps · harness/graph/graph.py:843
  - `-> Node.node_id` reads node id of · harness/graph/graph.py:844
- `PracticeGraph.restore`
  - `-> Node.node_id` reads node id of · harness/graph/graph.py:851
  - `-> Node.data` reads data of · harness/graph/graph.py:852
  - `-> Node()` creates · harness/graph/graph.py:856
  - `-> Source()` creates · harness/graph/graph.py:856
- `PracticeGraph.registered`
  - `-> Node.get` keeps · harness/graph/graph.py:877
  - `-> Graph.practices` reads practices of · harness/graph/graph.py:882
  - `<- Node | None`
- `PracticeGraph.direct_parent`
  - `-> Node.setdefault` keeps · harness/graph/graph.py:923
  - `<- Node | None`
- `PracticeGraph.node_count`
  - `-> Node.get` keeps · harness/graph/graph.py:936
- `PracticeGraph.rebuild_tree`
  - `-> Node.values` keeps · harness/graph/graph.py:940
  - `-> Node.populate` calls populate on · harness/graph/graph.py:944

## Node

- `Node.fidelities`
  - `-> PracticeGraph.schema` reads schema of · harness/graph/graph.py:600
- `Node.file_language`
  - `-> Source.file` reads file of · harness/graph/graph.py:613
- `Node.place`
  - `-> Source()` creates · harness/graph/graph.py:640
  - `-> PracticeGraph.source_root` reads source root of · harness/graph/graph.py:640
  - `-> GraphPractices.named` loads · harness/graph/graph.py:641
  - `-> PracticeGraph.name` reads name of · harness/graph/graph.py:641
- `Node.populate`
  - `-> PracticeGraph.edge_types` reads edge types of · harness/graph/graph.py:651
- `Node._edges_in_source_order`
  - `-> PracticeGraph.edges_from` calls edges_from on · harness/graph/graph.py:666
- `Node._follows_source`
  - `-> GraphPractices.named` loads · harness/graph/graph.py:679
- `Node._new_kind_node`
  - `-> PracticeGraph.name` reads name of · harness/graph/graph.py:723

## ModelNode

- `ModelNode.__init__`
  - `-> Graph()` creates · harness/graph/model_node.py:86
  - `-> Graph.practice` calls practice on · harness/graph/model_node.py:87
  - `-> Source()` creates · harness/graph/model_node.py:98
- `ModelNode._refill`
  - `-> ModelChildren.kind` reads kind of · harness/graph/model_node.py:149
  - `-> ModelChildren.clear` keeps · harness/graph/model_node.py:150
  - `-> ModelChildren.append` keeps · harness/graph/model_node.py:152
- `ModelNode.batch_schema_sync`
  - `-> Graph.schema_sync_held` calls schema_sync_held on · harness/graph/model_node.py:205

## ModelChildren

- `ModelChildren.append`
  - `-> ModelNode._link` links · harness/graph/model_node.py:29
- `ModelChildren.insert`
  - `-> ModelNode._link` links · harness/graph/model_node.py:37
- `ModelChildren.pop`
  - `-> ModelNode._unlink` calls unlink on · harness/graph/model_node.py:41
- `ModelChildren.__setitem__`
  - `-> ModelNode._refill` calls refill on · harness/graph/model_node.py:46
  - `-> ModelNode._link` links · harness/graph/model_node.py:49

## GraphPractice

- `GraphPractice.checks`
  - `-> GraphPractices.overlay` finds overlays in · harness/graph/graph_practice.py:105
  - `<- dict[str, PracticeGraphRule]`
- `GraphPractice.checks_for`
  - `-> Node.file_language` reads file language of · harness/graph/graph_practice.py:113
  - `-> Node.type` reads type of · harness/graph/graph_practice.py:116
  - `<- dict[str, PracticeGraphRule]`
- `GraphPractice` `-> PracticeGraphRule` loads and runs · harness/graph/graph_practice.py:88

## GraphPractices

- `GraphPractices.register`
  - `-> GraphPractice.name` reads name of · harness/graph/graph_practice.py:157
- `GraphPractices.register_overlay`
  - `-> GraphOverlay.pattern` reads pattern of · harness/graph/graph_practice.py:161
- `GraphPractices.overlay`
  - `-> GraphOverlay()` creates · harness/graph/graph_practice.py:174
  - `<- GraphOverlay`
- `GraphPractices._place`
  - `-> GraphPractice.reads_after` reads reads after of · harness/graph/graph_practice.py:189
  - `-> GraphPractice.append` keeps · harness/graph/graph_practice.py:192
- `GraphPractices._discover`
  - `-> PracticeCatalogue.has` checks a practice name with · harness/graph/graph_practice.py:198
  - `-> PracticeCatalogue.module_of` finds a practice module with · harness/graph/graph_practice.py:198
  - `-> GraphPractice()` creates · harness/graph/graph_practice.py:201

## PracticeGraphRule

- `PracticeGraphRule` `-> RuleCheckContext` checks a node within · harness/graph/practice_rule.py:15

## Violation

- `Violation` `-> SourceFile` annotated with · harness/graph/violation.py:117
- Annotations it carries: `SourceFile` · harness/graph/violation.py:117

## SavedGraph

- `SavedGraph.from_graph`
  - `-> Graph.overlays` reads overlays of · harness/graph/saved_graph.py:179
  - `-> Graph.practices` reads practices of · harness/graph/saved_graph.py:179
  - `<- SavedGraph`
- `SavedGraph.restored_graph`
  - `-> Graph()` creates · harness/graph/saved_graph.py:230
  - `-> Graph.practice` calls practice on · harness/graph/saved_graph.py:232
  - `<- Graph`

# harness/installation: the Installer and its run

## Installer

- `Installer.create`
  - `-> LastInstall()` creates · harness/installation/installer.py:315
  - `-> IdeLayout()` creates · harness/installation/installer.py:317
  - `-> InstallTarget()` creates · harness/installation/installer.py:318
  - `-> RepositoryToolsets()` creates · harness/installation/installer.py:319
  - `<- Installer`
- `Installer.__init__`
  - `-> InstallRecord()` creates · harness/installation/installer.py:295
  - `-> InstallLock()` creates · harness/installation/installer.py:300
- `Installer.install`
  - `-> InstallRun()` creates the run, kept as `last_run` · harness/installation/installer.py:376
  - `-> InstallRun.run` runs it · harness/installation/installer.py:377
- `Installer.repository_toolsets`
  - `-> RepositoryToolsets.classes` imports every toolset class · harness/installation/installer.py:402
  - `-> ToolsetReference.of` names each · harness/installation/installer.py:405
  - `<- list[ToolsetReference]`
- `Installer.write_language_adapters`
  - `-> LanguageAdapters()` creates · harness/installation/installer.py:391
  - `-> LanguageAdapters.write_all` writes · harness/installation/installer.py:397
- `Installer.diagnosis_of`
  - `-> Deployed.of_folder` reads what the folder holds · harness/installation/installer.py:410
  - `-> RegisteredChannel.status` reads each registered channel's status · harness/installation/installer.py:411
  - `-> InstallDiagnostics.last_deployed` reads what the last install deployed · harness/installation/installer.py:412
  - `<- InstallDiagnosis`

## InstallRun

- `InstallRun.__init__`
  - `-> InstallChannels()` creates the run's installations · harness/installation/installer.py:136
- `InstallRun.run`
  - `-> InstallLock.held` holds the folder · harness/installation/installer.py:142
  - `-> RepositoryToolsets.ensure_import_path` ensures import path · harness/installation/installer.py:148
- `InstallRun.publish`
  - `-> Installer.repository_toolsets` reads the toolsets · harness/installation/installer.py:161
  - `-> LanguageAdapters.write_all` writes · harness/installation/installer.py:165
  - `-> RegisteredChannel.write_once_recorded` writes · harness/installation/installer.py:169
- `InstallRun._install_all`
  - `-> ToolsetReference.made` makes each toolset · harness/installation/installer.py:208
  - `-> AgentToolSet.child_toolsets` calls child_toolsets on · harness/installation/installer.py:210
- `InstallRun._install_toolset`
  - `-> InstallChannels.for_tool` finds each installation · harness/installation/installer.py:223
  - `-> Installation.install` hands the member over · harness/installation/installer.py:224
- `InstallRun._install_standing_rules`
  - `-> RulesInstallation.write_standing_rule` writes standing rule · harness/installation/installer.py:250
- `InstallRun.stand_up`
  - `-> ChannelServer.stand_up` stands each server up · harness/installation/installer.py:176
  - `-> ChannelServer.runs_this_process` asks whether the install runs inside one · harness/installation/installer.py:179
- `InstallRun.ensure_running`
  - `-> ChannelServer.ensure_running` starts each server · harness/installation/installer.py:184
- `InstallRun._diagnose`
  - `-> Installer.diagnosis_of` diagnoses the run · harness/installation/installer.py:189
  - `-> InstallDiagnostics.record` records it · harness/installation/installer.py:190

## InstallChannels

- `InstallChannels.__init__`
  - `-> RegisteredChannel.create` creates each registered channel · harness/installation/installer.py:68
  - `-> LanguageAdapters()` creates · harness/installation/installer.py:69
  - `-> RulesInstallation()` creates · harness/installation/installer.py:70
  - `-> SkillInstallation()`, `CommandInstallation()` creates · harness/installation/installer.py:71
  - `-> ToolsetReference.made` makes the toolsets each registered channel publishes into every install · harness/installation/installer.py:73
- `InstallChannels.for_tool`
  - `-> RegisteredChannel.accepts` asks each registered channel · harness/installation/installer.py:86
  - `-> AgentTool.is_published_to` asks each file channel's destination · harness/installation/installer.py:87
- `InstallChannels.servers`
  - `-> RegisteredChannel.server` reads each channel's server · harness/installation/installer.py:93
- `InstallChannels.published`
  - `-> RegisteredChannel.published` reads what each channel published, by its channel · harness/installation/installer.py:99

# harness/diagnostics

## AgentToolsDiagnostics

- `AgentToolsDiagnostics.__init__`
  - `-> ToolCall()` creates · harness/diagnostics/agent_tools_diagnostics.py:17
- `AgentToolsDiagnostics.agent_tools_diagnostics`
  - `-> Installer()` creates · harness/diagnostics/agent_tools_diagnostics.py:36
  - `-> AgentToolsProbe().run` creates · harness/diagnostics/agent_tools_diagnostics.py:37
  - `-> AgentToolsProbe()` creates · harness/diagnostics/agent_tools_diagnostics.py:37

## GuidanceDiagnostics

- `GuidanceDiagnostics.__init__`
  - `-> ToolCall()` creates · harness/diagnostics/guidance_diagnostics.py:17
- `GuidanceDiagnostics.guidance_diagnostics`
  - `-> GuidanceProbe.from_filter` loads · harness/diagnostics/guidance_diagnostics.py:36
  - `-> Installer()` creates · harness/diagnostics/guidance_diagnostics.py:36
  - `-> GuidanceProbe.instructions` calls instructions on · harness/diagnostics/guidance_diagnostics.py:37
  - `-> GuidanceProbe.actions` calls actions on · harness/diagnostics/guidance_diagnostics.py:37

## AgentToolsProbe

- `AgentToolsProbe.host`
  - `-> McpHost.from_refs` loads · harness/diagnostics/agent_tools_probe.py:77

## GuidanceProbe

- `GuidanceProbe.prefixes`
  - `-> PracticeCatalogue.practice_named` finds a practice in · harness/diagnostics/guidance_probe.py:40
  - `-> PracticeCatalogue.slug` reads slug of · harness/diagnostics/guidance_probe.py:41
- `GuidanceProbe._instructions_of`
  - `-> PracticeCatalogue.toolset_ref` finds a toolset reference in · harness/diagnostics/guidance_probe.py:82
- `GuidanceProbe._action_toolset`
  - `-> AgentToolSet.tools` reads tools of · harness/diagnostics/guidance_probe.py:107
  - `-> AgentTool.is_published_to(Mcp)` reads the MCP annotation · harness/diagnostics/guidance_probe.py:107

# harness/health

## ServerHealth

- `ServerHealth.__init__`
  - `-> HookDaemon()` creates · harness/health/server_health.py:37

# harness/catalog_generator

## Catalog

- `Catalog.practices`
  - `-> CatalogPractice.load_all` loads · harness/catalog_generator/catalog_generator.py:926
  - `<- list[CatalogPractice]`

## CatalogPractice

- `CatalogPractice.load_all`
  - `-> PracticeCatalogue.practices` lists practices from · harness/catalog_generator/catalog_generator.py:84
  - `-> noCatalog.annotates` reads the annotation · harness/catalog_generator/catalog_generator.py:84
  - `<- list[CatalogPractice]`
- `CatalogPractice._card_of`
  - `-> Name()` creates · harness/catalog_generator/catalog_generator.py:90
- `CatalogPractice.key`
  - `-> PracticeGuidance.key` reads key of · harness/catalog_generator/catalog_generator.py:97
- `CatalogPractice.fidelities`
  - `-> PracticeGuidance.fidelities` reads fidelities of · harness/catalog_generator/catalog_generator.py:137
  - `-> noCatalog.annotates` reads the annotation · harness/catalog_generator/catalog_generator.py:137
  - `<- list[FidelityGuidance]`
- `CatalogPractice.column_of`
  - `-> FidelityGuidance.stage` reads stage of · harness/catalog_generator/catalog_generator.py:140
- `CatalogPractice.fidelity_href`
  - `-> FidelityGuidance.name` reads name of · harness/catalog_generator/catalog_generator.py:152
- `CatalogPractice.shared_markdown`
  - `-> PracticeGuidance.domain_markdown_path` calls domain_markdown_path on · harness/catalog_generator/catalog_generator.py:159
  - `-> MarkdownText()` creates · harness/catalog_generator/catalog_generator.py:162
  - `-> MarkdownText.headings` calls headings on · harness/catalog_generator/catalog_generator.py:163
  - `-> MarkdownText.slice_heading` calls slice_heading on · harness/catalog_generator/catalog_generator.py:164

# harness/design_canvas

No class of this module acts on another class of the model at run time.

# harness/chat

## Chat

- `Chat._transcript`
  - `-> ChatPointer.from_claude_chat` loads · harness/chat/chat.py:309
  - `-> ChatPointer.transcript` reads transcript of · harness/chat/chat.py:310

# space/repo

## Repo

- `Repo.git`
  - `-> Git()` creates · space/repo/repo.py:124
  - `<- Git`
- `Repo.file_manager`
  - `-> FileManager()` creates · space/repo/repo.py:171
  - `<- FileManager`
- `Repo.branch_named`
  - `-> Branch()` creates · space/repo/repo.py:183
  - `<- Branch`
- `Repo.current_branch`
  - `-> Git.run` runs · space/repo/repo.py:187
- `Repo.current_commit`
  - `-> Git.run` runs · space/repo/repo.py:191
- `Repo.default_start_point`
  - `-> Git.succeeds` calls succeeds on · space/repo/repo.py:197
- `Refs.has`
  - `-> Git.succeeds` calls succeeds on · space/repo/repo.py:200
- `WorkingTree.is_dirty`
  - `-> Git.run` runs · space/repo/repo.py:207
- `WorkingTree.commit`
  - `-> Git.run` runs · space/repo/repo.py:222
- `Origin.push_upstream`
  - `-> Git.run` runs · space/repo/repo.py:229
- `Origin.needs_push`
  - `-> Git.run` runs · space/repo/repo.py:237
- `Repo.fetch`
  - `-> Git.run` runs · space/repo/repo.py:240
- `Repo.pull`
  - `-> Git.run` runs · space/repo/repo.py:243
- `Merges.merge_from`
  - `-> Branch.name` reads name of · space/repo/repo.py:247
  - `-> Git.run` runs · space/repo/repo.py:249
- `Repo._checkout`
  - `-> raise RepoConnectError` raises · space/repo/repo.py:261
- `Repo._saved_worktree`
  - `-> Worktree.from_checkout` loads · space/repo/repo.py:288
- Annotations it carries: `AgentToolSetAnnotation` · space/repo/repo.py:106; `LanguageAdapter` · space/repo/repo.py:105; `ToolSubject` · space/repo/repo.py:116; `Mcp` · space/repo/repo.py:300; `LongCall` · space/repo/repo.py:300; `Command` · space/repo/repo.py:369

## Branch

- `Branch.exists`
  - `-> Refs.has` asks whether a ref exists through · space/repo/repo.py:477
- `Branch.is_checked_out`
  - `-> Repo.current_branch` reads current branch of · space/repo/repo.py:483
- `Branch.is_default`
  - `-> Repo.default_branch` reads default branch of · space/repo/repo.py:487
- `Branch.worktree`
  - `-> Repo.worktrees` reads worktrees of · space/repo/repo.py:492
  - `<- Worktree | None`
- `Branch.start_point`
  - `-> Refs.has` asks whether a ref exists through · space/repo/repo.py:497
  - `-> Repo.default_start_point` reads default start point of · space/repo/repo.py:499
- `Branch.changed_files`
  - `-> Repo.git` reads git of · space/repo/repo.py:506
  - `-> Repo.default_branch` reads default branch of · space/repo/repo.py:507
  - `-> Repo.current_branch` reads current branch of · space/repo/repo.py:508
- `Branch.check_out`
  - `-> Repo.git` reads git of · space/repo/repo.py:516
  - `<- Branch`
- `Branch.open_in_worktree`
  - `-> Repo.worktrees` reads worktrees of · space/repo/repo.py:531
  - `<- Worktree`
- `Branch.delete`
  - `-> Repo.git` reads git of · space/repo/repo.py:566
  - `-> Refs.has` asks whether a ref exists through · space/repo/repo.py:567

## Worktree

- `Worktree.from_repo`
  - `-> Repo.current_branch` reads current branch of · space/repo/worktree.py:53
  - `-> Repo.root` reads root of · space/repo/worktree.py:54
  - `-> Repo.branch_named` calls branch_named on · space/repo/worktree.py:54
  - `<- Worktree`
- `Worktree.__repr__`
  - `-> Branch.name` reads name of · space/repo/worktree.py:72

# space/session

## Sessions

- `Sessions.__init__`
  - `-> Repo()` creates · space/session/sessions.py:41
  - `-> Repo.root` reads root of · space/session/sessions.py:42
- `Sessions.folder_of`
  - `-> Worktrees.primary_root` calls primary_root on · space/session/sessions.py:68
- `HeldSessions.load`
  - `-> Session.load` loads · space/session/sessions.py:98
  - `<- Session`
- `Sessions.create`
  - `-> Session()` creates · space/session/sessions.py:115
  - `-> Name()` creates · space/session/sessions.py:116
  - `-> Session.name` reads name of · space/session/sessions.py:118
  - `-> Session.save` saves · space/session/sessions.py:119
  - `-> SessionRecord.save_fields` saves fields · space/session/sessions.py:120
  - `-> Session.log` reads log of · space/session/sessions.py:121
  - `<- Session`
- `Sessions.open`
  - `-> Session.save` saves with · space/session/sessions.py:128
  - `-> Session.name` reads name of · space/session/sessions.py:129
  - `<- Session`
- `Sessions._name_to_switch_to`
  - `-> Name()` creates · space/session/sessions.py:155
- `Sessions.close`
  - `-> Session.name` reads name of · space/session/sessions.py:162
- `Sessions.<module>`
  - `-> SESSION_OPENING.open_with` opens sessions with · space/session/sessions.py:184
- Annotations it carries: `AgentToolAnnotation` · space/session/sessions.py:135

## Session

- `Session.__init__`
  - `-> SessionLog()` creates · space/session/session.py:74
- `Session.from_file`
  - `-> Repo()` creates · space/session/session.py:93
  - `<- Session`
- `Session.repo`
  - `-> Repo()` creates · space/session/session.py:113
  - `<- Repo`
- `SessionPaths.from_project`
  - `-> Repo.path_from_top` calls path_from_top on · space/session/session.py:159
- `SessionFolder.move_to_backlog`
  - `-> Sessions.backlog_folder` reads backlog folder of · space/session/session.py:224
  - `<- Session`
- `Session._sessions`
  - `-> Sessions()` creates · space/session/session.py:236
- `Session.practice`
  - `-> PracticeCatalogue.has` checks a practice name with · space/session/session.py:254
  - `-> PracticeSessionOutput.append` keeps · space/session/session.py:257
  - `<- PracticeSessionOutput`
- `Session.practices`
  - `-> PracticeCatalogue.keys` keeps · space/session/session.py:264
  - `-> PracticeSessionOutput.setdefault` keeps · space/session/session.py:265
  - `-> PracticeSessionOutput()` creates · space/session/session.py:265
  - `<- dict[str, PracticeSessionOutput]`
- `Session.active_practices`
  - `-> PracticeSessionOutput.values` keeps · space/session/session.py:270
  - `<- list[PracticeSessionOutput]`
- `Session.close`
  - `-> Sessions.close` closes · space/session/session.py:306
- `Session.choose_workpath`
  - `-> PracticeSessionOutput.values` keeps · space/session/session.py:315
  - `<- Session`
- `Session.mark_loop`
  - `-> SessionLog.mark_loop` marks loop · space/session/session.py:345
- `Session.read_loop`
  - `-> SessionLog.read_loop` reads loop · space/session/session.py:355
- `Session.append_log`
  - `-> SessionLog.append_note` appends note · space/session/session.py:375
- Annotations it carries: `Identity` · space/session/session.py:57; `Skill` · space/session/session.py:380; `AgentInstructionsAnnotation` · space/session/session.py:401; `NoSessionLog` · space/session/session.py:332

## SessionLog

- `SessionLog.path`
  - `-> Session.work_folder` reads work folder of · space/session/session_log.py:184
- `SessionLog.error_path`
  - `-> Session.work_folder` reads work folder of · space/session/session_log.py:190
- `SessionLog.entries`
  - `-> LogEntry()` creates · space/session/session_log.py:196
  - `<- list[LogEntry]`
- `SessionLog.guidance_action`
  - `-> Session.workpath` reads workpath of · space/session/session_log.py:239
  - `-> Session.opened_practices` reads opened practices of · space/session/session_log.py:241
- `SessionLog._loop_numbers`
  - `-> LogEntry()` creates · space/session/session_log.py:310
- `SessionLog._lines_of_loop`
  - `-> LogEntry()` creates · space/session/session_log.py:329
- `SessionLog.read_loop`
  - `-> Session.name` reads name of · space/session/session_log.py:353
- `SessionLog._line_chat`
  - `-> Session.chat` reads chat of · space/session/session_log.py:378
- `SessionLog._action_line`
  - `-> Session.opened_practices` reads opened practices of · space/session/session_log.py:383

## LogEntry

- `LogEntry.names`
  - `-> FidelityGuidance.practice_guidance` reads practice guidance of · space/session/session_log.py:76
  - `-> FidelityGuidance.name` reads name of · space/session/session_log.py:78

## PracticeSessionOutput

- `PracticeSessionOutput.load`
  - `-> Session.from_file` loads · space/session/practices/practice_session_output.py:64
  - `<- PracticeSessionOutput`
- `PracticeSessionOutput.session_file`
  - `-> Session.session_file_from_project` reads session file from project of · space/session/practices/practice_session_output.py:79
- `PracticeSessionOutput.guideline`
  - `-> PracticeCatalogue.create` loads · space/session/practices/practice_session_output.py:86
  - `-> PracticeGuidance.work_in` calls work_in on · space/session/practices/practice_session_output.py:93
  - `<- PracticeGuidance`
- `PracticeSessionOutput.fidelities`
  - `-> PracticeGuidance.fidelities` reads fidelities of · space/session/practices/practice_session_output.py:103
  - `<- GuidanceCollection`
- `PracticeSessionOutput.graph`
  - `-> Graph.of_practice` loads · space/session/practices/practice_session_output.py:111
  - `-> Session.repo_path` reads repo path of · space/session/practices/practice_session_output.py:111
  - `<- Graph`
- `PracticeSessionOutput.root_node_name`
  - `-> Graph.practices` reads practices of · space/session/practices/practice_session_output.py:118
- `PracticeSessionOutput._saved`
  - `-> Session.fields` reads fields of · space/session/practices/practice_session_output.py:125
- `PracticeSessionOutput._save`
  - `-> Session.fields` reads fields of · space/session/practices/practice_session_output.py:128
  - `-> SessionRecord.save_fields` saves fields · space/session/practices/practice_session_output.py:129
- `PracticeSessionOutput._current_fidelity`
  - `-> PracticeGuidance.fidelities` reads fidelities of · space/session/practices/practice_session_output.py:147
- `PracticeSessionOutput.working_format`
  - `-> PracticeGuidance.format` reads format of · space/session/practices/practice_session_output.py:158
- `PracticeSessionOutput.log_validation`
  - `-> Session.log` reads log of · space/session/practices/practice_session_output.py:178
- `PracticeSessionOutput._chosen_outputs`
  - `-> Session.fields` reads fields of · space/session/practices/practice_session_output.py:184
- `PracticeSessionOutput._save_chosen_outputs`
  - `-> Session.fields` reads fields of · space/session/practices/practice_session_output.py:187
  - `-> SessionRecord.save_fields` saves fields · space/session/practices/practice_session_output.py:188
- `PracticeSessionOutput._chosen_or_configured_root`
  - `-> ContextConfig().practice_folder` creates · space/session/practices/practice_session_output.py:194
  - `-> ContextConfig()` creates · space/session/practices/practice_session_output.py:194
  - `-> Session.repo_path` reads repo path of · space/session/practices/practice_session_output.py:194
- `PracticeSessionOutput.folder`
  - `-> PracticeGuidance.default_workspace_folder` reads default workspace folder of · space/session/practices/practice_session_output.py:200
  - `-> Session.root` reads root of · space/session/practices/practice_session_output.py:201
- `PracticeSessionOutput.output_root`
  - `-> Session.root` reads root of · space/session/practices/practice_session_output.py:208
- `PracticeSessionOutput.root`
  - `-> SessionPaths.from_project` loads · space/session/practices/practice_session_output.py:215
- `PracticeSessionOutput.choose_root`
  - `-> Session.repo_path` reads repo path of · space/session/practices/practice_session_output.py:228
  - `<- PracticeSessionOutput`
- `PracticeSessionOutput.keep_root`
  - `-> Session.root` reads root of · space/session/practices/practice_session_output.py:237

## SessionDiagnostics

- `SessionDiagnostics.__init__`
  - `-> ToolCall()` creates · cdd_guidance/diagnostics/session_diagnostics.py:19
- `SessionDiagnostics.session_diagnostics`
  - `-> Installer()` creates · cdd_guidance/diagnostics/session_diagnostics.py:36

# space/kanban

## Board

- `Board.load`
  - `-> Repo().worktrees.primary_root` creates · space/kanban/board.py:97
  - `-> Repo()` creates · space/kanban/board.py:97
  - `-> PracticeCatalogue.practices` lists practices from · space/kanban/board.py:98
  - `<- Board`
- `Board.sessions`
  - `-> Sessions()` creates · space/kanban/board.py:107
  - `-> Repo.root` reads root of · space/kanban/board.py:107
  - `<- Sessions`
- `Board.file`
  - `-> Sessions.folder` reads folder of · space/kanban/board.py:112
- `Board.project`
  - `-> Repo.root` reads root of · space/kanban/board.py:117
- `Board.worktrees`
  - `-> Repo.is_clone` reads is clone of · space/kanban/board.py:123
  - `-> Repo.worktrees` reads worktrees of · space/kanban/board.py:125
  - `<- dict[Branch, Worktree]`
- `Board.tickets`
  - `-> Ticket()` creates · space/kanban/board.py:142
  - `-> Sessions.all` calls all on · space/kanban/board.py:142
  - `<- list[Ticket]`
- `Board.backlog_items`
  - `-> Sessions.backlog_folder` reads backlog folder of · space/kanban/board.py:148
  - `-> BacklogItem()` creates · space/kanban/board.py:155
  - `<- list[BacklogItem]`
- `Board.active`
  - `-> Sessions.open_name` reads open name of · space/kanban/board.py:166
  - `<- Ticket | None`
- `CardPlacement.ticket`
  - `-> Sessions.named` loads · space/kanban/board.py:179
  - `-> Ticket()` creates · space/kanban/board.py:180
  - `<- Ticket | None`
- `CardPlacement.open_ticket`
  - `-> Name()` creates · space/kanban/board.py:188
  - `-> Repo.root` reads root of · space/kanban/board.py:189
  - `-> Sessions.create` loads · space/kanban/board.py:191
  - `<- Ticket`
- `Board.folders`
  - `-> Repo.file_manager` reads file manager of · space/kanban/board.py:206
- `Board._build_columns`
  - `-> Stage()` creates · space/kanban/board.py:223

## Column

- `Column.cards`
  - `-> Board.cards` reads cards of · space/kanban/board.py:241
  - `<- list[Card]`

## Stage

- `Stage.__init__`
  - `-> ApproachStage.title` reads title of · space/kanban/board.py:278
- `Stage.load`
  - `-> Board.load` loads · space/kanban/board.py:285
  - `<- Stage`
- `Stage.steps`
  - `-> ApproachStage.steps` reads steps of · space/kanban/board.py:293
- `Stage.scope`
  - `-> ApproachStage.scope` reads scope of · space/kanban/board.py:299
  - `<- StageScope`
- `Stage.actions`
  - `-> ActionCatalogue.on_fidelities` reads the actions run on a fidelity · space/kanban/board.py
- `Stage.producing_actions`
  - `-> ActionCatalogue.producing` reads the actions that write a fidelity's files · space/kanban/board.py
- `Stage.work_required`
  - `-> ApproachStage.name` reads name of · space/kanban/board.py:323
  - `<- list[FidelityGuidance]`

## Card

- `Card._timestamp`
  - `-> SessionLog.timestamp` takes timestamps from · space/kanban/board.py:410

## Ticket

- `Ticket.load`
  - `-> Board.load` loads · space/kanban/ticket.py:74
  - `<- Ticket`
- `Ticket.create`
  - `-> Board.load` loads · space/kanban/ticket.py:85
  - `<- Ticket`
- `Ticket.name`
  - `-> Session.name` reads name of · space/kanban/ticket.py:92
- `Ticket.title`
  - `-> Session.title` reads title of · space/kanban/ticket.py:103
  - `-> Session.name` reads name of · space/kanban/ticket.py:103
- `Ticket.progress`
  - `-> Session.log` reads log of · space/kanban/ticket.py:116
  - `-> FidelityProgress.from_log` loads · space/kanban/ticket.py:117
  - `<- list[FidelityProgress]`
- `Ticket._own`
  - `-> FidelityGuidance.name` reads name of · space/kanban/ticket.py:122
  - `-> Session.practices` reads practices of · space/kanban/ticket.py:122
  - `-> FidelityGuidance.practice_guidance` reads practice guidance of · space/kanban/ticket.py:122
- `Ticket.progress_of`
  - `-> FidelityProgress.from_log` loads · space/kanban/ticket.py:131
  - `-> Session.log` reads log of · space/kanban/ticket.py:131
  - `<- FidelityProgress`
- `Ticket.column`
  - `-> Session.is_closed` reads is closed of · space/kanban/ticket.py:138
  - `<- Column`
- `Ticket.is_closed`
  - `-> Session.is_closed` reads is closed of · space/kanban/ticket.py:150
- `Ticket.next_fidelity`
  - `-> Stage.index` keeps · space/kanban/ticket.py:189
  - `<- FidelityProgress | None`
- `Ticket.last_activity`
  - `-> Session.log` reads log of · space/kanban/ticket.py:194
- `Ticket.open_worktree`
  - `-> Board.load` loads · space/kanban/ticket.py:227
  - `<- Ticket`
- `Ticket.move_to`
  - `-> SessionFolder.reopen` calls reopen on · space/kanban/ticket.py:278
  - `<- Ticket | BacklogItem`
- `Ticket.close`
  - `-> Session.close` closes · space/kanban/ticket.py:288
  - `-> SessionFolder.move_to_closed` moves to closed · space/kanban/ticket.py:289
  - `<- Ticket`
- `Ticket.archive`
  - `-> Session.close` closes · space/kanban/ticket.py:296
  - `-> SessionFolder.move_to_archive` moves to archive · space/kanban/ticket.py:297
  - `<- Ticket`
- `Ticket.violations`
  - `-> SessionPaths.from_project` loads · space/kanban/ticket.py:306
  - `-> Session.reports_folder` reads reports folder of · space/kanban/ticket.py:306
- `Ticket._reopen`
  - `-> SessionFolder.reopen` calls reopen on · space/kanban/ticket.py:310
- `Ticket._return_to_backlog`
  - `-> Session.close` closes · space/kanban/ticket.py:319
  - `-> SessionFolder.move_to_backlog` moves to backlog · space/kanban/ticket.py:320
  - `-> BacklogItem.from_ticket` loads · space/kanban/ticket.py:321
  - `-> BacklogItem.write_if_missing` writes if missing · space/kanban/ticket.py:322
- `Ticket._moved_into`
  - `-> Session.log` reads log of · space/kanban/ticket.py:334
- `Ticket._latest_mark`
  - `-> Session.log` reads log of · space/kanban/ticket.py:340
  - `-> Stage.name` reads name of · space/kanban/ticket.py:341
- `Ticket._mark`
  - `-> Session.log` reads log of · space/kanban/ticket.py:346
  - `-> Stage.name` reads name of · space/kanban/ticket.py:346
- `Ticket._enter`
  - `-> Session.log` reads log of · space/kanban/ticket.py:350
  - `-> Stage.name` reads name of · space/kanban/ticket.py:350
- Annotations it carries: `Identity` · space/kanban/ticket.py:54; `DataField` · space/kanban/ticket.py:88

## BacklogItem

- `BacklogItem.load`
  - `-> Board.load` loads · space/kanban/backlog_item.py:38
  - `<- BacklogItem`
- `BacklogItem.create`
  - `-> Board.load` loads · space/kanban/backlog_item.py:49
  - `-> Board.sessions` reads sessions of · space/kanban/backlog_item.py:50
  - `-> Name()` creates · space/kanban/backlog_item.py:50
  - `<- BacklogItem`
- `BacklogItem.from_ticket`
  - `-> Ticket.board` reads board of · space/kanban/backlog_item.py:58
  - `-> Ticket.name` reads name of · space/kanban/backlog_item.py:59
  - `<- BacklogItem`
- `BacklogItem._ticket_brought_back`
  - `-> Ticket()` creates · space/kanban/backlog_item.py:131

## FidelityProgress

- `FidelityProgress.from_log`
  - `-> Stage.steps` reads steps of · space/kanban/ticket.py:383
  - `<- FidelityProgress`
- `FidelityProgress.load`
  - `-> Ticket.load` loads · space/kanban/ticket.py:391
  - `<- FidelityProgress`
- `FidelityProgress.is_enabled`
  - `-> PracticeGuidance.key` reads key of · space/kanban/ticket.py:423
  - `-> Ticket.session` reads session of · space/kanban/ticket.py:423
- `FidelityProgress._practice`
  - `-> FidelityGuidance.practice_guidance` reads practice guidance of · space/kanban/ticket.py:427
- `FidelityProgress.remaining_actions`
  - `-> Stage.steps` reads steps of · space/kanban/ticket.py:435
- `FidelityProgress._has_files`
  - `-> FidelityGuidance.has_declared_output` calls has_declared_output on · space/kanban/ticket.py:457
- `FidelityProgress.action_states`
  - `-> Stage.steps` reads steps of · space/kanban/ticket.py:481
- `FidelityProgress.report_file`
  - `-> Ticket.session` reads session of · space/kanban/ticket.py:491
- `FidelityProgress.latest_report`
  - `-> Ticket.session` reads session of · space/kanban/ticket.py:497
  - `-> Ticket.board` reads board of · space/kanban/ticket.py:497
- `FidelityProgress.finish_review`
  - `-> Ticket.session` reads session of · space/kanban/ticket.py:510
  - `-> PracticeGuidance.key` reads key of · space/kanban/ticket.py:511
  - `-> FidelityGuidance.name` reads name of · space/kanban/ticket.py:511
  - `<- FidelityProgress`
- `FidelityProgress.files`
  - `-> FidelityGuidance.files` calls files on · space/kanban/ticket.py:534
  - `<- dict[str, list[FileEntry]]`
- `FidelityProgress` `-> FileEntry` lists the declared files as · space/kanban/ticket.py:532

# tools/file_manager

## FileManager

- `FileManager.load`
  - `-> ToolCall()` creates · tools/file_manager/file_manager.py:140
  - `<- FileManager`
- `FileManager.read`
  - `-> FileText()` creates · tools/file_manager/file_manager.py:170
  - `<- FileText`
- `FileManager._inside`
  - `-> raise PathOutsideRootsError` raises · tools/file_manager/file_manager.py:199

# tools/echo

## Echo

- `Echo` `-> Mcp` annotated with · tools/echo/echo.py:23
- `Echo` `-> NoCatalog` annotated with · tools/echo/echo.py:18
- Annotations it carries: `Mcp` · tools/echo/echo.py:23; `NoCatalog` · tools/echo/echo.py:18

# tools/granola

## Granola

- `Granola._slug`
  - `-> Name()` creates · tools/granola/granola.py:48

# tools/prompt_log

## PromptLog

- `PromptLog.log_for`
  - `-> Sessions()` creates · tools/prompt_log/prompt_log.py:158
  - `-> HookPayload.project` reads project of · tools/prompt_log/prompt_log.py:158
- `PromptLog.pre_tool_use`
  - `-> HookPayload.tool_name` reads tool name of · tools/prompt_log/prompt_log.py:180
- Annotations it carries: `Hooks` · tools/prompt_log/prompt_log.py:141; `Hook` · tools/prompt_log/prompt_log.py:167

# tools/prompt_notify

## PromptNotify

- `PromptNotify._practice_names`
  - `-> PracticeCatalogue.practices` lists practices from · tools/prompt_notify/prompt_notify.py:68
- `PromptNotify._action_names`
  - `-> ActionCatalogue.names` lists action names from · tools/prompt_notify/prompt_notify.py:79
- `PromptNotify.on_pre_tool_use`
  - `-> HookPayload.workspace_roots` reads workspace roots of · tools/prompt_notify/prompt_notify.py:88
- `PromptNotify.handle`
  - `-> HookPayload.tool_name` reads tool name of · tools/prompt_notify/prompt_notify.py:92
- `PromptNotify.detect`
  - `-> HookPayload.tool_name` reads tool name of · tools/prompt_notify/prompt_notify.py:117
- `PromptNotify._log_echo`
  - `-> SessionLog.timestamp` takes timestamps from · tools/prompt_notify/prompt_notify.py:156
- `PromptNotify._begin_toast`
  - `-> Name()` creates · tools/prompt_notify/prompt_notify.py:202
- `PromptNotify._load_echo_toolsets`
  - `-> RepositoryToolsets.references` reads the running checkout's toolset references · tools/prompt_notify/prompt_notify.py:124
  - `-> ToolsetReference.made` makes each toolset · tools/prompt_notify/prompt_notify.py:125
- `PromptNotify._compact`
  - `-> Name()` creates · tools/prompt_notify/prompt_notify.py:223
- `PromptNotify._mcp_tool_name`
  - `-> HookPayload.tool_name` reads tool name of · tools/prompt_notify/prompt_notify.py:226
  - `-> HookPayload.tool_input` reads tool input of · tools/prompt_notify/prompt_notify.py:227
- `PromptNotify._paths`
  - `-> HookPayload.tool_input` reads tool input of · tools/prompt_notify/prompt_notify.py:237
- `PromptNotify._haystacks`
  - `-> HookPayload.tool_name` reads tool name of · tools/prompt_notify/prompt_notify.py:246
- `PromptNotify._has_toast`
  - `-> Toast.annotates` reads the annotation · tools/prompt_notify/prompt_notify.py:264
- `PromptNotify._echo_kind_label`
  - `-> Name()` creates · tools/prompt_notify/prompt_notify.py:274
- `PromptNotify.<module>`
  - `-> HOOK_TOASTS.show_with` shows toasts with · tools/prompt_notify/prompt_notify.py:380
- Annotations it carries: `Hook` · tools/prompt_notify/prompt_notify.py:81; `NoCatalog` · tools/prompt_notify/prompt_notify.py:40

# tools/sub_agent

## SubAgent

- `SubAgent` `-> Mcp` annotated with · tools/sub_agent/sub_agent.py:18
- `SubAgent` `-> Skill` annotated with · tools/sub_agent/sub_agent.py:19
- Annotations it carries: `Mcp` · tools/sub_agent/sub_agent.py:18; `Skill` · tools/sub_agent/sub_agent.py:19

# cdd_guidance/actions

## Generate

- `Generate._earlier_render`
  - `-> PracticeGuidance.fidelities` reads fidelities of · cdd_guidance/actions/generate/generate.py:60
  - `-> Format()` creates · cdd_guidance/actions/generate/generate.py:61
  - `-> PracticeGuidance.format` reads format of · cdd_guidance/actions/generate/generate.py:61
- `Generate._fidelity_before`
  - `-> PracticeGuidance.fidelities` reads fidelities of · cdd_guidance/actions/generate/generate.py:77
- `Generate` `-> Render` renders the earlier fidelity with · cdd_guidance/actions/generate/generate.py:50

## Validate

- `Validate.validate`
  - `-> Rule.validate` validates with · cdd_guidance/actions/validate/validate.py:73
- `Validate._graph_practices`
  - `-> PracticeCatalogue.has` checks a practice name with · cdd_guidance/actions/validate/validate.py:148
- Annotations it carries: `NoDeploy` · cdd_guidance/actions/validate/validate.py:196; `Skill` · cdd_guidance/actions/validate/validate.py:196

## Document

- `Document` `-> Skill` annotated with · cdd_guidance/actions/document/document.py:18
- Annotations it carries: `Skill` · cdd_guidance/actions/document/document.py:18

## Satisfy

- `Satisfy.satisfy`
  - `-> AgentInstructions.for_callable` loads · cdd_guidance/actions/satisfy/satisfy.py:34
  - `-> Generate.generate_fixes_from_validate` reads generate fixes from validate of · cdd_guidance/actions/satisfy/satisfy.py:35
- `Satisfy.on`
  - `-> AgentInstructions.for_callable` loads · cdd_guidance/actions/satisfy/satisfy.py:34
  - `-> Generate.generate_fixes_from_validate` reads generate fixes from validate of · cdd_guidance/actions/satisfy/satisfy.py:35

## Sketch

- `Sketch` `-> GrillContext` grills with · cdd_guidance/actions/sketch/sketch.py:46

## SketchOutline

- `SketchOutline._names_a_lens`
  - `-> SketchLens.every` lists every lens with · cdd_guidance/actions/sketch/sketch_outline.py:72
- `SketchOutline._section_for`
  - `-> SketchLens.opens` calls opens on · cdd_guidance/actions/sketch/sketch_outline.py:95
- `SketchOutline._end_after`
  - `-> SketchLens.every` lists every lens with · cdd_guidance/actions/sketch/sketch_outline.py:109

## SketchLens

- `SketchLens.of`
  - `-> PracticeCatalogue.practice_class` finds a practice class in · cdd_guidance/actions/sketch/sketch_outline.py:17
  - `<- SketchLens`
- `SketchLens.every`
  - `-> PracticeCatalogue.keys` keeps · cdd_guidance/actions/sketch/sketch_outline.py:24
  - `<- tuple[SketchLens, ...]`

## Iterate

- `Iterate` `-> GrillContext` grills with · cdd_guidance/actions/iterate/iterate.py:35

## Improvement

- `Improvement` `-> Mcp` annotated with · cdd_guidance/actions/improvement/improvement.py:20
- Annotations it carries: `Mcp` · cdd_guidance/actions/improvement/improvement.py:20

## Diagnose

- Annotations it carries: `SubAgentAnnotation` · cdd_guidance/actions/diagnose/diagnose.py:24

# cdd_guidance/practices/clean_engineering

## CleanEngineering

- `CleanEngineering.drawio`
  - `-> Drawio()` creates · cdd_guidance/practices/clean_engineering/clean_engineering.py:63
  - `<- Drawio`
- `CleanEngineering.generate_output`
  - `-> Drawio.render` renders · cdd_guidance/practices/clean_engineering/clean_engineering.py:78

## CleanEngineeringGraph

- `CleanEngineeringGraph.<module>`
  - `-> GraphPractices.register` registers with · cdd_guidance/practices/clean_engineering/graph_practice.py:425

## CleanEngineeringModel

- `CleanEngineeringModel.__init__`
  - `-> ModelChildren()` creates · cdd_guidance/practices/clean_engineering/model/base_class_model.py:644
- `CleanEngineeringModel._copy_modules_on_graph`
  - `-> Module.append` keeps · cdd_guidance/practices/clean_engineering/model/base_class_model.py:665
- `CleanEngineeringModel.every_class`
  - `-> OoadClass.extend` keeps · cdd_guidance/practices/clean_engineering/model/base_class_model.py:673
  - `<- list[OoadClass]`
- `CleanEngineeringModel.load_modules`
  - `-> Module.append` keeps · cdd_guidance/practices/clean_engineering/model/base_class_model.py:717
- `CleanEngineeringModel.load_module`
  - `-> Module()` creates · cdd_guidance/practices/clean_engineering/model/base_class_model.py:731
  - `-> Module.name` reads name of · cdd_guidance/practices/clean_engineering/model/base_class_model.py:731
  - `-> Module.sequential_order` reads sequential order of · cdd_guidance/practices/clean_engineering/model/base_class_model.py:731
  - `<- Module`

## Module

- `Module.__init__`
  - `-> CodeBody()` creates · cdd_guidance/practices/clean_engineering/model/base_class_model.py:467
  - `-> ModelChildren()` creates · cdd_guidance/practices/clean_engineering/model/base_class_model.py:468
- `Module.load_class`
  - `-> OoadClass()` creates · cdd_guidance/practices/clean_engineering/model/base_class_model.py:538
  - `-> OoadClass.name` reads name of · cdd_guidance/practices/clean_engineering/model/base_class_model.py:538
  - `-> OoadClass.sequential_order` reads sequential order of · cdd_guidance/practices/clean_engineering/model/base_class_model.py:538
  - `<- OoadClass`
- `Module.append_class`
  - `-> OoadClass.append` keeps · cdd_guidance/practices/clean_engineering/model/base_class_model.py:563

## OoadClass

- `OoadClass.__init__`
  - `-> ModelChildren()` creates · cdd_guidance/practices/clean_engineering/model/base_class_model.py:221
  - `-> ModelChildren.extend` keeps · cdd_guidance/practices/clean_engineering/model/base_class_model.py:224
- `OoadClass.load_property`
  - `-> Property.name` reads name of · cdd_guidance/practices/clean_engineering/model/base_class_model.py:319
  - `-> Property.sequential_order` reads sequential order of · cdd_guidance/practices/clean_engineering/model/base_class_model.py:319
  - `<- Property`
- `OoadClass.load_operation`
  - `-> Operation.name` reads name of · cdd_guidance/practices/clean_engineering/model/base_class_model.py:327
  - `-> Operation.sequential_order` reads sequential order of · cdd_guidance/practices/clean_engineering/model/base_class_model.py:327
  - `<- Operation`
- `OoadClass.load_properties`
  - `-> Property.append` keeps · cdd_guidance/practices/clean_engineering/model/base_class_model.py:340
- `OoadClass.load_operations`
  - `-> Operation.append` keeps · cdd_guidance/practices/clean_engineering/model/base_class_model.py:354

## Operation

- `Operation.__init__`
  - `-> ModelChildren()` creates · cdd_guidance/practices/clean_engineering/model/operation.py:124
  - `-> CodeBody()` creates · cdd_guidance/practices/clean_engineering/model/operation.py:130

## MarkdownCleanEngineeringModel

- `MarkdownCleanEngineeringModel.load_module`
  - `-> Module.name` reads name of · cdd_guidance/practices/clean_engineering/model/markdown/markdown_class_model.py:286
  - `-> Module.sequential_order` reads sequential order of · cdd_guidance/practices/clean_engineering/model/markdown/markdown_class_model.py:286
- `MarkdownCleanEngineeringModel.render`
  - `-> CleanEngineeringModel._render_cards` renders cards · cdd_guidance/practices/clean_engineering/model/markdown/markdown_class_model.py:497
- `MarkdownCleanEngineeringModel._apply_module_section`
  - `-> Module.description` reads description of · cdd_guidance/practices/clean_engineering/model/markdown/markdown_class_model.py:590
  - `-> Module.seam` reads seam of · cdd_guidance/practices/clean_engineering/model/markdown/markdown_class_model.py:594
  - `-> Module.seam_terms` reads seam terms of · cdd_guidance/practices/clean_engineering/model/markdown/markdown_class_model.py:602
- `MarkdownCleanEngineeringModel._parse_properties_and_relationships`
  - `-> Property()` creates · cdd_guidance/practices/clean_engineering/model/markdown/markdown_class_model.py:744
  - `-> Property.append` keeps · cdd_guidance/practices/clean_engineering/model/markdown/markdown_class_model.py:747
- `MarkdownCleanEngineeringModel._parse_operations_and_relationships`
  - `-> Operation.append` keeps · cdd_guidance/practices/clean_engineering/model/markdown/markdown_class_model.py:796
  - `-> Operation()` creates · cdd_guidance/practices/clean_engineering/model/markdown/markdown_class_model.py:796

## PythonCleanEngineeringModel

- `PythonCleanEngineeringModel.load_module`
  - `-> Module.name` reads name of · cdd_guidance/practices/clean_engineering/model/python/python_class_model.py:109
  - `-> Module.sequential_order` reads sequential order of · cdd_guidance/practices/clean_engineering/model/python/python_class_model.py:109
- `PythonCleanEngineeringModel._class_from_ast`
  - `-> OoadClass()` creates · cdd_guidance/practices/clean_engineering/model/python/python_class_model.py:137
- `PythonCleanEngineeringModel._attach_top_level_ops`
  - `-> OoadClass()` creates · cdd_guidance/practices/clean_engineering/model/python/python_class_model.py:165
- `PythonCleanEngineeringModel._operations_from_class`
  - `-> Operation.append` keeps · cdd_guidance/practices/clean_engineering/model/python/python_class_model.py:174
- `PythonCleanEngineeringModel._operation_from_function`
  - `-> Operation()` creates · cdd_guidance/practices/clean_engineering/model/python/python_class_model.py:190
  - `-> Operation.load_python_function_facts` loads · cdd_guidance/practices/clean_engineering/model/python/python_class_model.py:208
- `PythonCleanEngineeringModel._body_of`
  - `-> CodeBody()` creates · cdd_guidance/practices/clean_engineering/model/python/python_class_model.py:218
- `PythonCleanEngineeringModel._preamble_of`
  - `-> Module.body` reads body of · cdd_guidance/practices/clean_engineering/model/python/python_class_model.py:231
  - `-> CodeBody()` creates · cdd_guidance/practices/clean_engineering/model/python/python_class_model.py:233
- `PythonCleanEngineeringModel._properties_from_class`
  - `-> Property.append` keeps · cdd_guidance/practices/clean_engineering/model/python/python_class_model.py:265
  - `-> Property()` creates · cdd_guidance/practices/clean_engineering/model/python/python_class_model.py:265
- `PythonCleanEngineeringModel.file_header`
  - `-> CodeBody.lines_in` calls lines_in on · cdd_guidance/practices/clean_engineering/model/python/python_class_model.py:285
- `PythonCleanEngineeringModel.class_open`
  - `-> OoadClass.declared_bases` calls declared_bases on · cdd_guidance/practices/clean_engineering/model/python/python_class_model.py:293
  - `-> OoadClass.name` reads name of · cdd_guidance/practices/clean_engineering/model/python/python_class_model.py:293
  - `-> OoadClass.stereotypes` reads stereotypes of · cdd_guidance/practices/clean_engineering/model/python/python_class_model.py:295
  - `-> OoadClass.intent` reads intent of · cdd_guidance/practices/clean_engineering/model/python/python_class_model.py:296
- `PythonCleanEngineeringModel.property_line`
  - `-> Property.type_hint` reads type hint of · cdd_guidance/practices/clean_engineering/model/python/python_class_model.py:304
  - `-> Property.name` reads name of · cdd_guidance/practices/clean_engineering/model/python/python_class_model.py:306
- `PythonCleanEngineeringModel.signature`
  - `-> Operation.parameters` reads parameters of · cdd_guidance/practices/clean_engineering/model/python/python_class_model.py:318
  - `-> Operation.name` reads name of · cdd_guidance/practices/clean_engineering/model/python/python_class_model.py:321
  - `-> Operation.return_type` reads return type of · cdd_guidance/practices/clean_engineering/model/python/python_class_model.py:321
- `PythonCleanEngineeringModel._decorators`
  - `-> Operation.is_property` reads is property of · cdd_guidance/practices/clean_engineering/model/python/python_class_model.py:335
  - `-> Operation.is_static` reads is static of · cdd_guidance/practices/clean_engineering/model/python/python_class_model.py:336
  - `-> Operation.is_classmethod` reads is classmethod of · cdd_guidance/practices/clean_engineering/model/python/python_class_model.py:337
- `PythonCleanEngineeringModel._receiver`
  - `-> Operation.is_static` reads is static of · cdd_guidance/practices/clean_engineering/model/python/python_class_model.py:343
  - `-> Operation.is_classmethod` reads is classmethod of · cdd_guidance/practices/clean_engineering/model/python/python_class_model.py:345
- `PythonCleanEngineeringModel._needs_abc`
  - `-> CleanEngineeringModel.every_class` calls every_class on · cdd_guidance/practices/clean_engineering/model/python/python_class_model.py:348

## CodeBody

- `CodeBody.__init__`
  - `-> CodeLanguage.is_unfinished` calls is_unfinished on · cdd_guidance/practices/clean_engineering/model/code_body.py:115
- `CodeBody.lines_in`
  - `-> CodeLanguage.comment` calls comment on · cdd_guidance/practices/clean_engineering/model/code_body.py:135

## WrittenBlock

- `WrittenBlock.inside_for`
  - `-> CodeBody()` creates · cdd_guidance/practices/clean_engineering/model/code_body.py:186
  - `-> CodeBody.text` reads text of · cdd_guidance/practices/clean_engineering/model/code_body.py:187
- `WrittenBlock.lead_body`
  - `-> CodeBody()` creates · cdd_guidance/practices/clean_engineering/model/code_body.py:190
  - `<- CodeBody`
- `WrittenBlock.closing_body`
  - `-> CodeBody()` creates · cdd_guidance/practices/clean_engineering/model/code_body.py:193
  - `<- CodeBody`

## DiagramCard

- `DiagramCard.geometry`
  - `-> Geometry()` creates · cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py:75
  - `<- Geometry`

## ArrowRouter

- `ArrowRouter._trouble_on`
  - `-> DiagramArrow.routed` reads routed of · cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py:421
  - `-> DiagramArrow.path` reads path of · cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py:423
- `ArrowRouter._draws`
  - `-> DiagramArrow.source` reads source of · cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py:426
  - `-> DiagramArrow.target` reads target of · cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py:426
- `ArrowRouter._length_between_cards`
  - `-> DiagramArrow.source` reads source of · cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py:429
  - `-> DiagramArrow.target` reads target of · cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py:429
- `ArrowRouter._facing_sides`
  - `-> DiagramArrow.source` reads source of · cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py:433
  - `-> DiagramArrow.target` reads target of · cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py:433
  - `-> DiagramArrow.kind` reads kind of · cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py:434
- `ArrowRouter._assign_ports`
  - `-> DiagramArrow.setdefault` keeps · cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py:469
  - `-> DiagramArrow.items` keeps · cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py:471
- `ArrowRouter._straighten`
  - `-> DiagramArrow.source` reads source of · cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py:486
  - `-> DiagramArrow.target` reads target of · cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py:486
  - `-> DiagramArrow.exit_side` reads exit side of · cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py:487
  - `-> DiagramArrow.exit_point` reads exit point of · cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py:490
  - `-> DiagramArrow.entry_point` reads entry point of · cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py:491
- `ArrowRouter._port`
  - `-> Geometry.x` reads x of · cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py:506
  - `-> Geometry.width` reads width of · cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py:506
  - `-> Geometry.y` reads y of · cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py:507
  - `-> Geometry.height` reads height of · cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py:507
- `ArrowRouter._route_one`
  - `-> DiagramArrow.exit_side` reads exit side of · cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py:512
  - `-> DiagramArrow.entry_side` reads entry side of · cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py:512
  - `-> DiagramArrow.exit_point` reads exit point of · cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py:513
  - `-> DiagramArrow.entry_point` reads entry point of · cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py:514

# cdd_guidance/practices/stories

## Stories

- `Stories.read_paths`
  - `-> Format()` creates · cdd_guidance/practices/stories/stories.py:68
  - `-> StoryMap.load_files` loads · cdd_guidance/practices/stories/stories.py:76
- `Stories._live_adapter`
  - `-> Format()` creates · cdd_guidance/practices/stories/stories.py:92

## StoriesGraph

- `StoriesGraph.read`
  - `-> PracticeGraph.graph` reads graph of · cdd_guidance/practices/stories/graph_practice.py:40
- `StoriesGraph.link`
  - `-> Graph.practices` reads practices of · cdd_guidance/practices/stories/graph_practice.py:49
- `StoriesGraph._typescript_model`
  - `-> PracticeGraph.graph` reads graph of · cdd_guidance/practices/stories/graph_practice.py:55
  - `-> PracticeGraph.source_root` reads source root of · cdd_guidance/practices/stories/graph_practice.py:56
- `StoriesGraph._story_map_model`
  - `-> PracticeGraph.graph` reads graph of · cdd_guidance/practices/stories/graph_practice.py:70
  - `-> PracticeGraph.source_root` reads source root of · cdd_guidance/practices/stories/graph_practice.py:71
  - `-> StoryMap.load` loads · cdd_guidance/practices/stories/graph_practice.py:75
  - `-> StoryMap.load_files` loads · cdd_guidance/practices/stories/graph_practice.py:76
- `StoriesGraph.<module>`
  - `-> GraphPractices.register` registers with · cdd_guidance/practices/stories/graph_practice.py:184

## StoryMap

- `StoryMap.__init__`
  - `-> ModelChildren()` creates · cdd_guidance/practices/stories/model/story_map.py:913
- `StoryMap.epics.append`
  - `-> Epic.append` keeps · cdd_guidance/practices/stories/model/story_map.py:1080

## Epic

- `Epic.__init__`
  - `-> ModelChildren()` creates · cdd_guidance/practices/stories/model/story_map.py:639
- `Epic.append_story`
  - `-> Story.append` keeps · cdd_guidance/practices/stories/model/story_map.py:725

## Story

- `Story.__init__`
  - `-> ModelChildren()` creates · cdd_guidance/practices/stories/model/story_map.py:826
  - `-> Scenario.append` keeps · cdd_guidance/practices/stories/model/story_map.py:834

## Scenario

- `Scenario.__init__`
  - `-> ModelChildren()` creates · cdd_guidance/practices/stories/model/story_map.py:524
  - `-> Step.append` keeps · cdd_guidance/practices/stories/model/story_map.py:535
  - `-> Step()` creates · cdd_guidance/practices/stories/model/story_map.py:535
- `Scenario.when_then_runs`
  - `-> StepType.WHEN` reads constants of · cdd_guidance/practices/stories/model/story_map.py:569
  - `-> Step.append` keeps · cdd_guidance/practices/stories/model/story_map.py:572
  - `-> StepType.THEN` reads constants of · cdd_guidance/practices/stories/model/story_map.py:573
- `Scenario` `-> Example` keeps its examples as · cdd_guidance/practices/stories/model/story_map.py:470

## Step

- `Step.__init__`
  - `-> ModelChildren()` creates · cdd_guidance/practices/stories/model/story_map.py:375
  - `-> CodeBody()` creates · cdd_guidance/practices/stories/model/story_map.py:383
  - `-> ModelChildren.append` keeps · cdd_guidance/practices/stories/model/story_map.py:387
- `Step.code_key`
  - `-> CodeBody.text` reads text of · cdd_guidance/practices/stories/model/story_map.py:392
- `Step.phase`
  - `-> StepType.value` reads value of · cdd_guidance/practices/stories/model/story_map.py:426

## DiagramStoryMap

- `DiagramStoryMap.sub_epic_top`
  - `-> DiagramEpic.nested_row_y` reads nested row y of · cdd_guidance/practices/stories/model/diagram_story_map.py:170
- `DiagramStoryMap.sub_epic_y`
  - `-> DiagramEpic.bar_height` reads bar height of · cdd_guidance/practices/stories/model/diagram_story_map.py:179
  - `-> DiagramEpic.depth_gap` reads depth gap of · cdd_guidance/practices/stories/model/diagram_story_map.py:179
- `DiagramStoryMap.story_y`
  - `-> DiagramEpic.bar_height` reads bar height of · cdd_guidance/practices/stories/model/diagram_story_map.py:186
- `DiagramStoryMap` `-> DiagramStory` makes its stories as · cdd_guidance/practices/stories/model/diagram_story_map.py:154

# cdd_guidance/practices/ddd

## Ddd

- `Ddd._parse_content`
  - `-> Format()` creates · cdd_guidance/practices/ddd/ddd.py:69
  - `-> MarkdownCleanEngineeringModel().parse` creates · cdd_guidance/practices/ddd/ddd.py:75
  - `-> MarkdownCleanEngineeringModel()` creates · cdd_guidance/practices/ddd/ddd.py:75

## DddGraph

- `DddGraph.own_rules`
  - `-> GraphPractices.named` loads · cdd_guidance/practices/ddd/graph_practice.py:30
- `DddGraph.<module>`
  - `-> GraphPractices.register` registers with · cdd_guidance/practices/ddd/graph_practice.py:175

# cdd_guidance/practices/ux

## Ux

- `Ux.javascript_practice`
  - `-> PracticeCatalogue.create` loads · cdd_guidance/practices/ux/ux.py:63
  - `<- PracticeGuidance`

## UxGraph

- `UxGraph.<module>`
  - `-> GraphPractices.register` registers with · cdd_guidance/practices/ux/graph_practice.py:28

# cdd_guidance/practices/bdd

## BddGraph

- `BddGraph.read`
  - `-> PracticeGraph.source_root` reads source root of · cdd_guidance/practices/bdd/graph_practice.py:36
  - `-> PracticeGraph.graph` reads graph of · cdd_guidance/practices/bdd/graph_practice.py:37
- `BddGraph.link`
  - `-> Graph.practices` reads practices of · cdd_guidance/practices/bdd/graph_practice.py:45
- `BddGraph.<module>`
  - `-> GraphPractices.register` registers with · cdd_guidance/practices/bdd/graph_practice.py:186

# cdd_guidance/practices/agent_bdd

## AgentBdd

- `AgentBdd.generate_output`
  - `-> Generate().generate` creates · cdd_guidance/practices/agent_bdd/agent_bdd.py:22
  - `-> Generate()` creates · cdd_guidance/practices/agent_bdd/agent_bdd.py:22
  - `-> Bdd()` creates · cdd_guidance/practices/agent_bdd/agent_bdd.py:22

# cdd_guidance/patterns

No class of this module acts on another class of the model at run time.

# cdd_guidance/builders

No class of this module acts on another class of the model at run time.

# cdd_guidance/context_setup

## ContextSetup

- `ContextSetup.__init__`
  - `-> Partition()` creates · cdd_guidance/context_setup/context_setup.py:76
  - `-> ContextIndex()` creates · cdd_guidance/context_setup/context_setup.py:77
- `ContextSetup.for_call`
  - `-> ToolCall.session` reads session of · cdd_guidance/context_setup/context_setup.py:84
  - `<- ContextSetup`
- `ContextSetup.session`
  - `-> raise ActionWorksInNoSession` raises · cdd_guidance/context_setup/context_setup.py:90
