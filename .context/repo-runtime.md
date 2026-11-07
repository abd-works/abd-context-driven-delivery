**Repository runtime relationships**

What each class of the repository model does to another class when the code runs, traced from the code: the operation that acts, then each `-> Other.operation` it calls, creates (`Other()`), reads, or raises, with the interaction in words and the line that does it, and `<- Type` where what comes back matters. A dashed labelled arrow in `.context/repo-model.drawio` stands for each class pair here. Only classes in `.context/repo-model.md` appear as targets; calls into a class outside the model are left out. The judgement of each relationship (right as a dependency, or the code has the wrong shape) is in `.context/repo-model-disconnected.md`.

Read `annotation_kinds` as the one private registry of annotation kinds in harness/annotations; `_InstallChannels` as the Installer's private holder of its run's installations.

# Traced chains

## Install: the Installer walks the toolsets, reads each member's destination annotations, and hands the member to the installation of each channel

- `Installer.install` `-> Installer._install_run` calls · harness/installer/installer.py:132
- `Installer._install_run` `-> RepositoryToolsets.collect` reads the toolset references from the source · harness/installer/installer.py:145
-   `<- list[str]` toolset references `module:Class` · harness/installer/installer.py:145
- `Installer._install_run` `-> _InstallChannels(installer)` creates McpInstallation, HookInstallation, LanguageAdapterInstallation once per run · harness/installer/installer.py:144
- `Installer._install_all` `-> AgentToolSet.instantiate` loads each toolset · harness/installer/installer.py:168
- `Installer._install_toolset` `-> AgentToolSet.tools` reads every published member · harness/installer/installer.py:180
-   `<- dict[str, AgentTool]` · harness/installer/installer.py:180
- `Installer.installations_for` `-> AgentTool.destinations` reads the channels the member is annotated for · harness/installer/installer.py:100
- `AgentTool.destinations` `-> AgentTool.install_to(channel)` asks once per listed channel · harness/agent_tools/agent_tools.py:744
- `AgentTool.install_to` `-> annotation_kinds.publishes(channel, callable)` reads the Destination annotation of that channel (Skill, Command, Rules, Mcp, Hook) and NoDeploy · harness/agent_tools/agent_tools.py:740
-   `<- list[str]` the channels it publishes to · harness/agent_tools/agent_tools.py:744
- `Installer.installations_for` `-> FileInstallation(ide, path, destination)` creates one per skill, command, or rules channel · harness/installer/installer.py:105
- `Installer.installations_for` `-> _InstallChannels.mcp` uses the run's McpInstallation for the MCP channel · harness/installer/installer.py:102
- `Installer.installations_for` `-> _InstallChannels.hook` uses the run's HookInstallation for the hook channel · harness/installer/installer.py:109
-   `<- list[Installation]` · harness/installer/installer.py:98
- `Installer._install_toolset` `-> Installation.install(tool)` hands the member to each installation · harness/installer/installer.py:182
- `Installation.install` `-> FileInstallation.write | McpInstallation.write | HookInstallation.write` writes the member's channel · harness/installation/destination.py:274
- `Installer._install_toolset` `-> LanguageAdapterInstallation.record(toolset)` records a toolset annotated @language_adapter · harness/installer/installer.py:183
- `LanguageAdapterInstallation.record` `-> DataClass.languages` reads the LanguageAdapter annotation · harness/installation/language_adapter.py:825
- `Installer._install_run` `-> LanguageAdapterInstallation.write_all` writes `{ide}/language-adapters/typescript/` · harness/installer/installer.py:147
- `Installer._install_run` `-> Installer._install_agents` copies `cdd_guidance/agents/*.md` to `{ide}/agents/` without reading any annotation · harness/installer/installer.py:148
- `Installer._install_run` `-> Installer._install_standing_rules -> FileInstallation.write_standing_rule` writes each `cdd_guidance/rules` file · harness/installer/installer.py:149

## Destination and the installation that writes it, matched by the destination's channel

- `FileInstallation.write` `-> Skill (channel SKILL)` writes `{ide}/skills/{toolset}-{operation}/SKILL.md` · harness/installation/files.py:93
- `FileInstallation.write` `-> Command (channel COMMAND)` writes `{ide}/commands/{toolset}/{name}.md` · harness/installation/files.py:96
- `FileInstallation.write` `-> Rules (channel RULE)` writes `{ide}/rules/{practice}/{fidelity}.mdc` (`.md` for Claude Code) · harness/installation/files.py:99
- `McpInstallation.write` `-> Mcp (channel MCP)` records the operation, then writes the IDE's `cdd` MCP entry · harness/mcp/mcp_server.py:154
- `HookInstallation.write` `-> Hook (channel HOOK)` adds the event to `hooks.json` and the operation to `hook-handlers.json` · harness/hooks/hooks.py:227
- `LanguageAdapterInstallation.record` `-> LanguageAdapter (class annotation, no channel)` generates TypeScript for the toolset · harness/installation/language_adapter.py:825
- `PromptNotify._has_toast` `-> Toast (no channel)` nothing is installed; the notifier toasts the call · tools/prompt_notify/prompt_notify.py:264
- `RepositoryToolsets` `-> Agent, AgentGuidance (no channel)` only counted as signs that a class is a toolset; no installation writes them · harness/installation/repository_toolsets.py:58

## A chat's tool call: McpHost to ToolCall to the toolset's operation

- `McpHost.dispatch` `-> McpServer.resolve_call_name` maps the chat's tool id to `toolset.operation` · harness/mcp/mcp_server.py:694
- `McpHost.dispatch` `-> ToolCall.sent(arguments, project, tool, mcp_host)` creates the call · harness/mcp/mcp_server.py:757
- `McpHost.answer` `-> McpHost._answer_between_restarts` · harness/mcp/mcp_server.py:767
- `McpHost._answer_between_restarts` `-> McpHost.server_for(call.project)` finds the project's McpServer · harness/mcp/mcp_server.py:776
- `McpServer.answer_tool` `-> AgentTool.answer(call)` · harness/mcp/mcp_server.py:533
- `AgentTool.answer` `-> AgentToolSet.for_call(call)` the toolset as the call works on it · harness/agent_tools/agent_tools.py:801
- `AgentTool.answer` `-> AgentTool.log_session_invocation(call) -> ToolCall.session` logs the call in the session open in its project · harness/agent_tools/agent_tools.py:802
- `ToolCall.session` `-> ToolCall._sessions.open_in(call)` the opener space/session registered (`ToolCall.open_sessions_with`) · harness/agent_tools/tool_call.py:89
- `AgentTool.answer` `-> toolset operation(**arguments)` runs the annotated operation with its coerced arguments · harness/agent_tools/agent_tools.py:803
-   `<- object` the operation's result, sent back to the chat · harness/agent_tools/agent_tools.py:803

## A session's practice and its graph: Session to PracticeSessionOutput to Graph, PracticeGraph, and Node

- `Session.practices` `-> PracticeCatalogue.keys` lists every practice · space/session/session.py:264
- `Session.practices` `-> PracticeSessionOutput(name, session)` creates one per practice, kept by key · space/session/session.py:265
- `PracticeSessionOutput.graph` `-> Graph.of_practice(repo_path, name, folder)` loads the practice's graph once · space/session/practice_session_output.py:111
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
- `GuidanceAction.listed` `-> AgentToolSet.instantiate_all(items)` builds each PracticeGuidance, then has the session's practice adopt it · harness/guidance_actions/guidance_actions.py:244
-   `<- list[PracticeGuidance]` · harness/guidance_actions/guidance_actions.py:248
- `Validate._fidelities` `-> PracticeGuidance.fidelities.current` the FidelityGuidance each guidance is at · cdd_guidance/actions/validate/validate.py:100
- `Validate.validate` `-> CheckedGraph(session, checked, graph_practices)` builds the graph from the checked files · cdd_guidance/actions/validate/validate.py:57
- `Validate.validate` `-> GuidanceAction.run(on, action="validate")` runs once per listed guidance and logs the action · cdd_guidance/actions/validate/validate.py:80
- `Validate.listed_rules -> _rules_text` `-> PracticeGuidance.checked_rule_collections` the shared rules, then the current fidelity's · cdd_guidance/actions/validate/validate.py:218
- `PracticeGuidance.checked_rule_collections` `-> FidelityGuidance.rules` <- list[RulesCollection] · harness/guidance/guidance.py:118
- `Validate.validate` `-> ReportFiles(session, fidelities).save(report, graph_paths)` writes the report in the session · cdd_guidance/actions/validate/validate.py:83

# harness/name

No class of this module acts on another class of the model at run time.

# harness/annotations

No class of this module acts on another class of the model at run time.

# harness/process

## StoppableProcess

- `StoppableProcess.stop`
  - `-> raise ProcessNotStopped` raises · harness/process/stoppable_process.py:38
- `StoppableProcess._wait_until_ended`
  - `-> raise ProcessNotStopped` raises · harness/process/stoppable_process.py:46

## Git

- `Git.run`
  - `-> raise RepoConnectError` raises · harness/process/git.py:39
- `Git._executable`
  - `-> raise RepoConnectError` raises · harness/process/git.py:58

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
- `AgentTool.registration_name`
  - `-> AgentToolSet.registration_name` reads registration name of · harness/agent_tools/agent_tools.py:760
- `AgentTool.deploy_name`
  - `-> InstallDestination.COMMAND` reads constants of · harness/agent_tools/agent_tools.py:765
  - `-> InstallDestination.SKILL` reads constants of · harness/agent_tools/agent_tools.py:766
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

- `FileInstallation.__init__`
  - `-> IdeLayout()` creates · harness/installation/files.py:87
- `FileInstallation.relative_path`
  - `-> Name()` creates · harness/installation/files.py:92
  - `-> InstallDestination.SKILL` reads constants of · harness/installation/files.py:93
  - `-> IdeLayout.nests_skills` reads nests skills of · harness/installation/files.py:95
  - `-> InstallDestination.COMMAND` reads constants of · harness/installation/files.py:96
  - `-> IdeLayout.commands_folder` reads commands folder of · harness/installation/files.py:98
  - `-> InstallDestination.RULE` reads constants of · harness/installation/files.py:99
- `FileInstallation.write`
  - `-> AgentTool.kind` reads kind of · harness/installation/files.py:104
  - `-> AgentTool.toolset` reads toolset of · harness/installation/files.py:107
  - `-> AgentTool.deploy_name` reads deploy name of · harness/installation/files.py:107
  - `-> InstallDestination.RULE` reads constants of · harness/installation/files.py:110
  - `-> MarkdownText()` creates · harness/installation/files.py:111
  - `-> InstallDestination.SKILL` reads constants of · harness/installation/files.py:113
- `FileInstallation.write_standing_rule`
  - `-> IdeLayout.scopes_rules_by_paths` reads scopes rules by paths of · harness/installation/files.py:121
  - `-> FrontMatter()` creates · harness/installation/files.py:122
  - `-> FrontMatter.fields` reads fields of · harness/installation/files.py:123
  - `-> FrontMatter.content` reads content of · harness/installation/files.py:123
  - `-> IdeLayout.rule_suffix` reads rule suffix of · harness/installation/files.py:126
- `FileInstallation._parts`
  - `-> AgentTool.name` reads name of · harness/installation/files.py:135
  - `-> AgentTool.toolset` reads toolset of · harness/installation/files.py:135
  - `-> AgentTool.invoke_line` calls invoke_line on · harness/installation/files.py:136
- `FileInstallation._guidance_slug`
  - `-> Name()` creates · harness/installation/files.py:152
- `FileInstallation._rule_path`
  - `-> IdeLayout.rule_suffix` reads rule suffix of · harness/installation/files.py:155
- `FileInstallation._kebab_folder`
  - `-> Name()` creates · harness/installation/files.py:168
- `FileInstallation._skill_operations`
  - `-> Name()` creates · harness/installation/files.py:182
- `FileInstallation._schema_guide`
  - `-> AgentTool.name` reads name of · harness/installation/files.py:197
  - `-> AgentTool.toolset` reads toolset of · harness/installation/files.py:199
- `FileInstallation._instructions_at_install`
  - `-> AgentTool.toolset` reads toolset of · harness/installation/files.py:209
  - `-> AgentTool.name` reads name of · harness/installation/files.py:209
  - `-> AgentTool.docstring` reads docstring of · harness/installation/files.py:214
- `FileInstallation._body_for`
  - `-> AgentTool.docstring` reads docstring of · harness/installation/files.py:219
  - `-> AgentTool.kind` reads kind of · harness/installation/files.py:220
  - `-> InstallDestination.RULE` reads constants of · harness/installation/files.py:222
  - `-> AgentTool.toolset` reads toolset of · harness/installation/files.py:223
  - `-> AgentTool.name` reads name of · harness/installation/files.py:223
- `FileInstallation._shell_command`
  - `-> AgentTool.deploy_name` reads deploy name of · harness/installation/files.py:244
  - `-> AgentTool.toolset` reads toolset of · harness/installation/files.py:247
  - `-> AgentTool.name` reads name of · harness/installation/files.py:248
- `FileInstallation._needs_shell_invoke`
  - `-> AgentTool.kind` reads kind of · harness/installation/files.py:255
  - `-> AgentTool.install_to_mcp` reads install to mcp of · harness/installation/files.py:255
  - `-> InstallDestination.SKILL` reads constants of · harness/installation/files.py:255
  - `-> InstallDestination.COMMAND` reads constants of · harness/installation/files.py:255
- `FileInstallation._fidelity_invoke_parts`
  - `-> InstallDestination.MCP` reads constants of · harness/installation/files.py:268
- `FileInstallation._with_installed_references`
  - `-> IdeLayout.rule_suffix` reads rule suffix of · harness/installation/files.py:278
- `FileInstallation._rules_front_matter`
  - `-> IdeLayout.scopes_rules_by_paths` reads scopes rules by paths of · harness/installation/files.py:333
- `FileInstallation` `-> Skill` writes the SKILL.md for · harness/installation/files.py:93
- `FileInstallation` `-> Command` writes the slash command for · harness/installation/files.py:96
- `FileInstallation` `-> Rules` writes the rules file for · harness/installation/files.py:99

## LanguageAdapterInstallation

- `LanguageAdapterInstallation.record`
  - `-> DataClass()` creates · harness/installation/language_adapter.py:825
- `LanguageAdapterInstallation._typescript_toolsets`
  - `-> InstallDestination.MCP` reads constants of · harness/installation/language_adapter.py:860
- `LanguageAdapterInstallation` `-> LanguageAdapter` generates TypeScript for · harness/installation/language_adapter.py:825
- `LanguageAdapterInstallation` `-> SourceFile` draws a file link for fields annotated · harness/installation/language_adapter.py:196

## RepositoryToolsets

- `RepositoryToolsets._toolset_refs_in_file`
  - `-> AgentToolSet.HOSTED_ONLY_CLASS_NAMES` reads constants of · harness/installation/repository_toolsets.py:130
- `RepositoryToolsets._class_is_installable`
  - `-> Name()` creates · harness/installation/repository_toolsets.py:167
- `RepositoryToolsets` `-> Agent` recognizes toolsets by · harness/installation/repository_toolsets.py:58
- `RepositoryToolsets` `-> AgentGuidance` recognizes toolsets by · harness/installation/repository_toolsets.py:58

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
  - `-> StoppableProcess().stop` creates · harness/hooks/hook_daemon.py:204
  - `-> StoppableProcess()` creates · harness/hooks/hook_daemon.py:204
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

## HookInstallation

- `HookInstallation.dispatch_command`
  - `-> PythonInterpreter()` creates · harness/hooks/hooks.py:206
- `HookInstallation.write`
  - `-> AgentTool.install_to_hook` reads install to hook of · harness/hooks/hooks.py:227
  - `-> AgentTool.hook_event` reads hook event of · harness/hooks/hooks.py:227
  - `-> AgentTool.toolset` reads toolset of · harness/hooks/hooks.py:229
  - `-> AgentTool.name` reads name of · harness/hooks/hooks.py:231
  - `-> AgentTool.registration_name` reads registration name of · harness/hooks/hooks.py:231
- `HookInstallation.standup`
  - `-> HookServer.from_handlers` loads · harness/hooks/hooks.py:283
  - `<- HookServer`
- `HookInstallation` `-> Hook` enrolls in hooks.json · harness/hooks/hooks.py:227

# harness/mcp

## McpHost

- `McpHost.__init__`
  - `-> McpServer.project` reads project of · harness/mcp/mcp_server.py:607
- `McpHost.server_for`
  - `-> McpServer.get` keeps · harness/mcp/mcp_server.py:622
  - `-> McpServer.for_project` loads · harness/mcp/mcp_server.py:624
  - `<- McpServer`
- `McpHost._register_handlers`
  - `-> McpServer.prompts` reads prompts of · harness/mcp/mcp_server.py:653
- `McpHost.handle_get_prompt`
  - `-> McpServer.prompts` reads prompts of · harness/mcp/mcp_server.py:653
- `McpHost._tool_list`
  - `-> McpServer.tools` reads tools of · harness/mcp/mcp_server.py:673
  - `-> McpServer.prompts` reads prompts of · harness/mcp/mcp_server.py:673
- `McpHost._call_from_chat`
  - `-> McpServer.resolve_call_name` resolves call name · harness/mcp/mcp_server.py:694
  - `-> ToolCall.sent` loads · harness/mcp/mcp_server.py:695
- `McpHost._answer_off_loop`
  - `-> McpServer.call_seconds` calls seconds · harness/mcp/mcp_server.py:700
  - `-> ToolCall.tool` reads tool of · harness/mcp/mcp_server.py:700
- `McpHost._requested_project`
  - `-> UserMcpConfig()` creates · harness/mcp/mcp_server.py:740
- `McpHost.dispatch`
  - `-> McpServer.resolve_call_name` resolves call name · harness/mcp/mcp_server.py:756
  - `-> ToolCall.sent` loads · harness/mcp/mcp_server.py:757
- `McpHost.answer`
  - `-> ToolCall.tool` reads tool of · harness/mcp/mcp_server.py:762
- `McpHost._answer_between_restarts`
  - `-> ToolCall.project` reads project of · harness/mcp/mcp_server.py:776
  - `-> ToolCall.arguments` reads arguments of · harness/mcp/mcp_server.py:778
  - `-> ToolCall.tool` reads tool of · harness/mcp/mcp_server.py:779
- `McpHost._ping_tool`
  - `-> McpServer.enrolled` calls enrolled on · harness/mcp/mcp_server.py:788
- `McpHost._log_failure`
  - `-> ToolCall.session` reads session of · harness/mcp/mcp_server.py:793
  - `-> ToolCall.tool` reads tool of · harness/mcp/mcp_server.py:795
- `McpHost.serve`
  - `-> McpServer.repo` reads repo of · harness/mcp/mcp_server.py:807
- `McpHost.http_app`
  - `-> McpServer.repo` reads repo of · harness/mcp/mcp_server.py:830
- `McpHost.ping`
  - `-> McpServer.repo` reads repo of · harness/mcp/mcp_server.py:830
- `McpHost.restart`
  - `-> McpServer.restarted` calls restarted on · harness/mcp/mcp_server.py:846
  - `-> McpServer.project` reads project of · harness/mcp/mcp_server.py:848
  - `-> McpServer.tools` reads tools of · harness/mcp/mcp_server.py:849
  - `-> McpServer.skipped` reads skipped of · harness/mcp/mcp_server.py:850
  - `-> McpServer.prompts` reads prompts of · harness/mcp/mcp_server.py:850
- `McpHost.notice`
  - `-> McpServer.skipped` reads skipped of · harness/mcp/mcp_server.py:864
- `McpHost.from_repo`
  - `-> RepositoryToolsets().collect` creates · harness/mcp/mcp_server.py:880
  - `-> RepositoryToolsets()` creates · harness/mcp/mcp_server.py:880
  - `<- McpHost`
- `McpHost.from_refs`
  - `-> McpServer()` creates · harness/mcp/mcp_server.py:895
  - `-> McpServer.start` starts · harness/mcp/mcp_server.py:897
  - `<- McpHost`

## McpServer

- `McpServer.enroll`
  - `-> AgentTool.mcp_name` reads mcp name of · harness/mcp/mcp_server.py:411
  - `-> AgentTool.input_schema` reads input schema of · harness/mcp/mcp_server.py:419
  - `-> AgentTool.kind` reads kind of · harness/mcp/mcp_server.py:423
- `McpServer.start`
  - `-> AgentTool.clear` keeps · harness/mcp/mcp_server.py:433
- `McpServer._loaded`
  - `-> AgentToolSet.from_items` loads · harness/mcp/mcp_server.py:443
- `McpServer._enroll_toolset`
  - `-> InstallDestination.MCP` reads constants of · harness/mcp/mcp_server.py:486
- `McpServer.enrolled`
  - `-> AgentTool.get` keeps · harness/mcp/mcp_server.py:510
  - `<- AgentTool | None`
- `McpServer.call_seconds`
  - `-> LongCall.annotates` reads the annotation · harness/mcp/mcp_server.py:518
- `McpServer.invoke_tool`
  - `-> ToolCall()` creates · harness/mcp/mcp_server.py:522
- `McpServer.invoke_prompt`
  - `-> ToolCall()` creates · harness/mcp/mcp_server.py:526
- `McpServer` `-> Mcp` serves the operations annotated · harness/mcp/mcp_server.py:486

## McpInstallation

- `McpInstallation.__init__`
  - `-> CddHome()` creates · harness/mcp/mcp_server.py:147
  - `-> IdeLayout()` creates · harness/mcp/mcp_server.py:148
- `McpInstallation.write`
  - `-> AgentTool.install_to_mcp` reads install to mcp of · harness/mcp/mcp_server.py:154
- `McpInstallation.record_operation`
  - `-> AgentTool.install_to_mcp` reads install to mcp of · harness/mcp/mcp_server.py:160
  - `-> AgentTool.append` keeps · harness/mcp/mcp_server.py:162
- `McpInstallation.user_config`
  - `-> UserMcpConfig()` creates · harness/mcp/mcp_server.py:167
  - `-> UserMcpConfig.path` reads path of · harness/mcp/mcp_server.py:168
  - `<- UserMcpConfig | None`
- `McpInstallation.manifest_path`
  - `-> IdeLayout.is_claude_code` reads is claude code of · harness/mcp/mcp_server.py:187
- `McpInstallation.write_mcp_manifest`
  - `-> IdeLayout.is_claude_code` reads is claude code of · harness/mcp/mcp_server.py:196
  - `-> UserMcpConfig.folder` reads folder of · harness/mcp/mcp_server.py:197
- `McpInstallation._server_manifest`
  - `-> IdeLayout.names_mcp_transport` reads names mcp transport of · harness/mcp/mcp_server.py:274
- `McpInstallation.standup`
  - `-> McpHost.from_repo` loads · harness/mcp/mcp_server.py:316
  - `<- McpHost`
- `McpInstallation` `-> Mcp` publishes as a cdd MCP tool · harness/mcp/mcp_server.py:154

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

- `CddHome._mirror_origin`
  - `-> Git().succeeds` creates · harness/mcp/cdd_home.py:213
  - `-> Git()` creates · harness/mcp/cdd_home.py:213
- `CddHome._git`
  - `-> Git().run` creates · harness/mcp/cdd_home.py:227
  - `-> Git()` creates · harness/mcp/cdd_home.py:227

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
  - `-> InstallDestination.SKILL` reads constants of · harness/guidance/action_catalogue.py:79
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
- `GuidanceAction.listed`
  - `-> AgentToolSet.instantiate_all` instantiates every action with · harness/guidance_actions/guidance_actions.py:244
- `GuidanceAction._session_practice`
  - `-> PracticeCatalogue.has` checks a practice name with · harness/guidance_actions/guidance_actions.py:263
- `GuidanceAction.inject_rules`
  - `-> ToolCall()` creates · harness/guidance_actions/guidance_actions.py:374
  - `-> HookPayload.tool_input` reads tool input of · harness/guidance_actions/guidance_actions.py:374
  - `-> HookPayload.project` reads project of · harness/guidance_actions/guidance_actions.py:374
  - `-> Name()` creates · harness/guidance_actions/guidance_actions.py:378
- `GuidanceAction._payload_is_this_action`
  - `-> HookPayload.tool_name` reads tool name of · harness/guidance_actions/guidance_actions.py:395
  - `-> InstallDestination.MCP` reads constants of · harness/guidance_actions/guidance_actions.py:398
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

# harness/installer

## Installer

- `Installer.__init__`
  - `-> IdeLayout.DEFAULT_IDE` reads constants of · harness/installer/installer.py:77
  - `-> IdeLayout()` creates · harness/installer/installer.py:78
  - `-> RepositoryToolsets()` creates · harness/installer/installer.py:83
- `Installer.track`
  - `-> Installation.track_writes_with` tracks writes with · harness/installer/installer.py:96
- `Installer.installations_for`
  - `-> AgentTool.destinations` reads destinations of · harness/installer/installer.py:100
  - `-> InstallDestination.MCP` reads constants of · harness/installer/installer.py:101
  - `-> InstallDestination.SKILL` reads constants of · harness/installer/installer.py:103
  - `-> InstallDestination.COMMAND` reads constants of · harness/installer/installer.py:103
  - `-> InstallDestination.RULE` reads constants of · harness/installer/installer.py:103
  - `-> FileInstallation()` creates · harness/installer/installer.py:105
  - `-> Installation.append` keeps · harness/installer/installer.py:107
  - `-> IdeLayout.runs_hooks` reads runs hooks of · harness/installer/installer.py:108
  - `-> InstallDestination.HOOK` reads constants of · harness/installer/installer.py:108
  - `<- list[Installation]`
- `Installer._install_run`
  - `-> RepositoryToolsets.ensure_import_path` ensures import path · harness/installer/installer.py:143
  - `-> RepositoryToolsets.collect` collects · harness/installer/installer.py:145
- `Installer._install_all`
  - `-> AgentToolSet.instantiate` loads · harness/installer/installer.py:168
  - `-> AgentToolSet.child_toolsets` calls child_toolsets on · harness/installer/installer.py:170
- `Installer._install_standing_rules`
  - `-> FileInstallation()` creates · harness/installer/installer.py:222
  - `-> FileInstallation.write_standing_rule` writes standing rule · harness/installer/installer.py:225
- `Installer.ensure_runtimes`
  - `-> IdeLayout.runs_hooks` reads runs hooks of · harness/installer/installer.py:266
- `Installer._ensure_hook_server`
  - `-> HookDaemon()` creates · harness/installer/installer.py:285
  - `-> HookDaemon.ensure` ensures · harness/installer/installer.py:286
  - `-> HookDaemon.live_address` calls live_address on · harness/installer/installer.py:287
- `Installer._runtime_status_report`
  - `-> HookDaemon().live_address` creates · harness/installer/installer.py:329
  - `-> HookDaemon()` creates · harness/installer/installer.py:329
  - `-> HookInstallation()` creates · harness/installer/installer.py:331
  - `-> HookInstallation.registered_events` reads registered events of · harness/installer/installer.py:332
  - `-> HookInstallation.registered_operations` reads registered operations of · harness/installer/installer.py:332
- `Installer._last_or_default_folder`
  - `-> IdeLayout.folder_name` reads folder name of · harness/installer/installer.py:345

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
  - `-> AgentToolSet.instantiate` loads · harness/diagnostics/guidance_probe.py:86
- `GuidanceProbe._action_toolset`
  - `-> AgentToolSet.instantiate` loads · harness/diagnostics/guidance_probe.py:96
  - `-> AgentToolSet.tools` reads tools of · harness/diagnostics/guidance_probe.py:99

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
  - `-> NoCatalog.annotates` reads the annotation · harness/catalog_generator/catalog_generator.py:84
  - `<- list[CatalogPractice]`
- `CatalogPractice._card_of`
  - `-> Name()` creates · harness/catalog_generator/catalog_generator.py:90
- `CatalogPractice.key`
  - `-> PracticeGuidance.key` reads key of · harness/catalog_generator/catalog_generator.py:97
- `CatalogPractice.fidelities`
  - `-> PracticeGuidance.fidelities` reads fidelities of · harness/catalog_generator/catalog_generator.py:137
  - `-> NoCatalog.annotates` reads the annotation · harness/catalog_generator/catalog_generator.py:137
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
- `Repo.has_ref`
  - `-> Git.succeeds` calls succeeds on · space/repo/repo.py:200
- `Repo.is_dirty`
  - `-> Git.run` runs · space/repo/repo.py:207
- `Repo.commit`
  - `-> Git.run` runs · space/repo/repo.py:222
- `Repo.push_upstream`
  - `-> Git.run` runs · space/repo/repo.py:229
- `Repo.needs_push`
  - `-> Git.run` runs · space/repo/repo.py:237
- `Repo.fetch`
  - `-> Git.run` runs · space/repo/repo.py:240
- `Repo.pull`
  - `-> Git.run` runs · space/repo/repo.py:243
- `Repo.merge_from`
  - `-> Branch.name` reads name of · space/repo/repo.py:247
  - `-> Git.run` runs · space/repo/repo.py:249
- `Repo._checkout`
  - `-> raise RepoConnectError` raises · space/repo/repo.py:261
- `Repo._saved_worktree`
  - `-> Worktree.from_checkout` loads · space/repo/repo.py:288
- Annotations it carries: `AgentToolSetAnnotation` · space/repo/repo.py:106; `LanguageAdapter` · space/repo/repo.py:105; `ToolSubject` · space/repo/repo.py:116; `Mcp` · space/repo/repo.py:300; `LongCall` · space/repo/repo.py:300; `Command` · space/repo/repo.py:369

## Branch

- `Branch.exists`
  - `-> Repo.has_ref` asks whether a ref exists through · space/repo/repo.py:477
- `Branch.is_checked_out`
  - `-> Repo.current_branch` reads current branch of · space/repo/repo.py:483
- `Branch.is_default`
  - `-> Repo.default_branch` reads default branch of · space/repo/repo.py:487
- `Branch.worktree`
  - `-> Repo.worktrees` reads worktrees of · space/repo/repo.py:492
  - `<- Worktree | None`
- `Branch.start_point`
  - `-> Repo.has_ref` asks whether a ref exists through · space/repo/repo.py:497
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
  - `-> Repo.has_ref` asks whether a ref exists through · space/repo/repo.py:567

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
  - `-> Repo.primary_root` calls primary_root on · space/session/sessions.py:68
- `Sessions.load`
  - `-> Session.load` loads · space/session/sessions.py:98
  - `<- Session`
- `Sessions.create`
  - `-> Session()` creates · space/session/sessions.py:115
  - `-> Name()` creates · space/session/sessions.py:116
  - `-> Session.name` reads name of · space/session/sessions.py:118
  - `-> Session.save` saves · space/session/sessions.py:119
  - `-> Session.save_fields` saves fields · space/session/sessions.py:120
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
  - `-> ToolCall.open_sessions_with` opens sessions with · space/session/sessions.py:184
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
- `Session.from_project`
  - `-> Repo.path_from_top` calls path_from_top on · space/session/session.py:159
- `Session.move_to_backlog`
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
  - `-> Session.session_path` reads session path of · space/session/session_log.py:184
- `SessionLog.error_path`
  - `-> Session.session_path` reads session path of · space/session/session_log.py:190
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
  - `-> Session.from_file` loads · space/session/practice_session_output.py:64
  - `<- PracticeSessionOutput`
- `PracticeSessionOutput.session_file`
  - `-> Session.session_file_from_project` reads session file from project of · space/session/practice_session_output.py:79
- `PracticeSessionOutput.guideline`
  - `-> PracticeCatalogue.create` loads · space/session/practice_session_output.py:86
  - `-> PracticeGuidance.work_in` calls work_in on · space/session/practice_session_output.py:93
  - `<- PracticeGuidance`
- `PracticeSessionOutput.fidelities`
  - `-> PracticeGuidance.fidelities` reads fidelities of · space/session/practice_session_output.py:103
  - `<- GuidanceCollection`
- `PracticeSessionOutput.graph`
  - `-> Graph.of_practice` loads · space/session/practice_session_output.py:111
  - `-> Session.repo_path` reads repo path of · space/session/practice_session_output.py:111
  - `<- Graph`
- `PracticeSessionOutput.root_node_name`
  - `-> Graph.practices` reads practices of · space/session/practice_session_output.py:118
- `PracticeSessionOutput._saved`
  - `-> Session.fields` reads fields of · space/session/practice_session_output.py:125
- `PracticeSessionOutput._save`
  - `-> Session.fields` reads fields of · space/session/practice_session_output.py:128
  - `-> Session.save_fields` saves fields · space/session/practice_session_output.py:129
- `PracticeSessionOutput._current_fidelity`
  - `-> PracticeGuidance.fidelities` reads fidelities of · space/session/practice_session_output.py:147
- `PracticeSessionOutput.working_format`
  - `-> PracticeGuidance.format` reads format of · space/session/practice_session_output.py:158
- `PracticeSessionOutput.keep_format`
  - `-> PracticeGuidance.format` reads format of · space/session/practice_session_output.py:164
- `PracticeSessionOutput.log_validation`
  - `-> Session.log` reads log of · space/session/practice_session_output.py:178
- `PracticeSessionOutput._chosen_outputs`
  - `-> Session.fields` reads fields of · space/session/practice_session_output.py:184
- `PracticeSessionOutput._save_chosen_outputs`
  - `-> Session.fields` reads fields of · space/session/practice_session_output.py:187
  - `-> Session.save_fields` saves fields · space/session/practice_session_output.py:188
- `PracticeSessionOutput._chosen_or_configured_root`
  - `-> ContextConfig().practice_folder` creates · space/session/practice_session_output.py:194
  - `-> ContextConfig()` creates · space/session/practice_session_output.py:194
  - `-> Session.repo_path` reads repo path of · space/session/practice_session_output.py:194
- `PracticeSessionOutput.folder`
  - `-> PracticeGuidance.default_workspace_folder` reads default workspace folder of · space/session/practice_session_output.py:200
  - `-> Session.root` reads root of · space/session/practice_session_output.py:201
- `PracticeSessionOutput.output_root`
  - `-> Session.root` reads root of · space/session/practice_session_output.py:208
- `PracticeSessionOutput.root`
  - `-> Session.from_project` loads · space/session/practice_session_output.py:215
- `PracticeSessionOutput.choose_root`
  - `-> Session.repo_path` reads repo path of · space/session/practice_session_output.py:228
  - `<- PracticeSessionOutput`
- `PracticeSessionOutput.keep_root`
  - `-> Session.root` reads root of · space/session/practice_session_output.py:237

## SessionDiagnostics

- `SessionDiagnostics.__init__`
  - `-> ToolCall()` creates · space/session/session_diagnostics.py:19
- `SessionDiagnostics.session_diagnostics`
  - `-> Installer()` creates · space/session/session_diagnostics.py:36

# space/kanban

## Board

- `Board.load`
  - `-> Repo().primary_root` creates · space/kanban/board.py:97
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
- `Board.ticket`
  - `-> Sessions.named` loads · space/kanban/board.py:179
  - `-> Ticket()` creates · space/kanban/board.py:180
  - `<- Ticket | None`
- `Board.open_ticket`
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
  - `-> ApproachStage.actions` reads actions of · space/kanban/board.py:305
- `Stage.producing_actions`
  - `-> ApproachStage.producing_actions` reads producing actions of · space/kanban/board.py:311
- `Stage.actions_with_formats`
  - `-> ApproachStage.actions_with_formats` reads actions with formats of · space/kanban/board.py:317
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
  - `-> Session.reopen` calls reopen on · space/kanban/ticket.py:278
  - `<- Ticket | BacklogItem`
- `Ticket.close`
  - `-> Session.close` closes · space/kanban/ticket.py:288
  - `-> Session.move_to_closed` moves to closed · space/kanban/ticket.py:289
  - `<- Ticket`
- `Ticket.archive`
  - `-> Session.close` closes · space/kanban/ticket.py:296
  - `-> Session.move_to_archive` moves to archive · space/kanban/ticket.py:297
  - `<- Ticket`
- `Ticket.violations`
  - `-> Session.from_project` loads · space/kanban/ticket.py:306
  - `-> Session.reports_folder` reads reports folder of · space/kanban/ticket.py:306
- `Ticket._reopen`
  - `-> Session.reopen` calls reopen on · space/kanban/ticket.py:310
- `Ticket._return_to_backlog`
  - `-> Session.close` closes · space/kanban/ticket.py:319
  - `-> Session.move_to_backlog` moves to backlog · space/kanban/ticket.py:320
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
  - `-> AgentToolSet.from_items` loads · tools/prompt_notify/prompt_notify.py:208
  - `-> Installer()` creates · tools/prompt_notify/prompt_notify.py:208
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
  - `-> HookServer.show_toasts_with` shows toasts with · tools/prompt_notify/prompt_notify.py:380
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
- `MarkdownCleanEngineeringModel.load_class`
  - `-> OoadClass.name` reads name of · cdd_guidance/practices/clean_engineering/model/markdown/markdown_class_model.py:291
  - `-> OoadClass.sequential_order` reads sequential order of · cdd_guidance/practices/clean_engineering/model/markdown/markdown_class_model.py:291
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
  - `-> StoryModel.load_files` loads · cdd_guidance/practices/stories/stories.py:76
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
  - `-> StoryModel.load` loads · cdd_guidance/practices/stories/graph_practice.py:75
  - `-> StoryModel.load_files` loads · cdd_guidance/practices/stories/graph_practice.py:76
- `StoriesGraph.<module>`
  - `-> GraphPractices.register` registers with · cdd_guidance/practices/stories/graph_practice.py:184

## StoryModel

- `StoryModel.__init__`
  - `-> ModelChildren()` creates · cdd_guidance/practices/stories/model/story_model.py:913
- `StoryModel.append_epic`
  - `-> Epic.append` keeps · cdd_guidance/practices/stories/model/story_model.py:1080

## Epic

- `Epic.__init__`
  - `-> ModelChildren()` creates · cdd_guidance/practices/stories/model/story_model.py:639
- `Epic.append_story`
  - `-> Story.append` keeps · cdd_guidance/practices/stories/model/story_model.py:725

## Story

- `Story.__init__`
  - `-> ModelChildren()` creates · cdd_guidance/practices/stories/model/story_model.py:826
  - `-> Scenario.append` keeps · cdd_guidance/practices/stories/model/story_model.py:834

## Scenario

- `Scenario.__init__`
  - `-> ModelChildren()` creates · cdd_guidance/practices/stories/model/story_model.py:524
  - `-> Step.append` keeps · cdd_guidance/practices/stories/model/story_model.py:535
  - `-> Step()` creates · cdd_guidance/practices/stories/model/story_model.py:535
- `Scenario.when_then_runs`
  - `-> StepType.WHEN` reads constants of · cdd_guidance/practices/stories/model/story_model.py:569
  - `-> Step.append` keeps · cdd_guidance/practices/stories/model/story_model.py:572
  - `-> StepType.THEN` reads constants of · cdd_guidance/practices/stories/model/story_model.py:573
- `Scenario` `-> Example` keeps its examples as · cdd_guidance/practices/stories/model/story_model.py:470

## Step

- `Step.__init__`
  - `-> ModelChildren()` creates · cdd_guidance/practices/stories/model/story_model.py:375
  - `-> CodeBody()` creates · cdd_guidance/practices/stories/model/story_model.py:383
  - `-> ModelChildren.append` keeps · cdd_guidance/practices/stories/model/story_model.py:387
- `Step.code_key`
  - `-> CodeBody.text` reads text of · cdd_guidance/practices/stories/model/story_model.py:392
- `Step.phase`
  - `-> StepType.value` reads value of · cdd_guidance/practices/stories/model/story_model.py:426

## DiagramStoryModel

- `DiagramStoryModel.sub_epic_top`
  - `-> DiagramEpic.nested_row_y` reads nested row y of · cdd_guidance/practices/stories/model/diagram_story_model.py:170
- `DiagramStoryModel.sub_epic_y`
  - `-> DiagramEpic.bar_height` reads bar height of · cdd_guidance/practices/stories/model/diagram_story_model.py:179
  - `-> DiagramEpic.depth_gap` reads depth gap of · cdd_guidance/practices/stories/model/diagram_story_model.py:179
- `DiagramStoryModel.story_y`
  - `-> DiagramEpic.bar_height` reads bar height of · cdd_guidance/practices/stories/model/diagram_story_model.py:186
- `DiagramStoryModel` `-> DiagramStory` makes its stories as · cdd_guidance/practices/stories/model/diagram_story_model.py:154

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

## DomainDrivenStack

- `DomainDrivenStack._stories`
  - `-> Stories()` creates · cdd_guidance/patterns/domain_driven_stack.py:29

# cdd_guidance/builders

No class of this module acts on another class of the model at run time.

# cdd_guidance/context_setup

## ContextSetup

- `ContextSetup.__init__`
  - `-> Stories()` creates · cdd_guidance/context_setup/context_setup.py:72
  - `-> CleanEngineering()` creates · cdd_guidance/context_setup/context_setup.py:73
  - `-> Ddd()` creates · cdd_guidance/context_setup/context_setup.py:74
  - `-> Ux()` creates · cdd_guidance/context_setup/context_setup.py:75
  - `-> Partition()` creates · cdd_guidance/context_setup/context_setup.py:76
  - `-> ContextIndex()` creates · cdd_guidance/context_setup/context_setup.py:77
- `ContextSetup.for_call`
  - `-> ToolCall.session` reads session of · cdd_guidance/context_setup/context_setup.py:84
  - `<- ContextSetup`
- `ContextSetup.session`
  - `-> raise ActionWorksInNoSession` raises · cdd_guidance/context_setup/context_setup.py:90
