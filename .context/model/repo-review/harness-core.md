**Relationship review: harness core**

Modules: harness/name, harness/annotations, harness/process, harness/markdown, harness/agent_tools (with the `@subAgent` annotation, ChatPointer, and ToolCall), harness/installation together with harness/installer (being merged into it), harness/hooks, harness/mcp.

Every line below was checked by reading the code in this worktree as it is on 2026-11-07. Line numbers are the current ones. "Changed from" names the verdict in `.context/repo-model-disconnected.md` (or `.context/repo-runtime.md`) that this review overturns; a blank means the earlier verdict stands, or the relationship was missing from both files ("missed").

How a verdict is read here:

- **R**: the two objects are independent and one asks the other to act: an external system (git, the operating system, a file the IDE owns), a collaborator handed in, a registry it registers with, an annotation an author typed, a named failure it raises, a part made once and kept, or a per-request value such as one tool call.
- **W**: the caller rebuilds the other object on each call from strings it pulls from elsewhere, re-reads what another object already holds, reaches into another object's attributes by name, or builds in itself what should be a held part or a handed-in collaborator.
- Two value classes, `Name` (case conversion) and `Format` (a format's names and extensions), are judged by whose string they convert. Converting a string the caller does not own (a header key, a template folder name, a decorator identifier) is R: no object could hold that value. Converting the caller's own name over and over is W: the owner should expose the converted name as a property.

# 1. Runtime relationships, verified

## harness/name, harness/annotations

`Name` uses nothing in the model. `AnnotationKinds` is the registry every annotation kind registers in when its class is defined (`annotation.py:89`); the one module-level instance `annotation_kinds` (`annotation.py:73`) is read by AgentTool, ToolsetMembers, Collect, MarkdownProperty and FileInstallation. That is a registry an object registers with: R.

## harness/process

| from → to | interaction | file:line | verdict | changed from | reason |
|---|---|---|---|---|---|
| Git → RepoConnectError | raises when git fails, times out, or is missing | harness/process/git.py:39, :41, :43, :58 | R | | Git's own named failure. |
| StoppableProcess → ProcessNotStopped | raises when the signal is refused or the process outlives the wait | harness/process/stoppable_process.py:38, :46 | R | | Its own named failure. |

## harness/markdown

| from → to | interaction | file:line | verdict | changed from | reason |
|---|---|---|---|---|---|
| Markdown → MarkdownText | builds one from the located text on every `extract` and `read_into` | harness/markdown/markdown.py:868, :907 | W | | `raw()` locates and re-reads the file on every call (`markdown.py:862`, called again by `extract` and `read_into`), then wraps the text in a new MarkdownText. **Owner** Markdown; **composition 1**. Markdown reads its section once into the MarkdownText it holds, and `extract`, `read_into` and `without_yaml` read that part. |
| Markdown → AssetLocator | builds one per `raw()` and per `templates_path_map()` | harness/markdown/markdown.py:862, :925 | W | missed | The location of a section depends only on the instance, label, fidelity and format Markdown was made with. **Owner** Markdown; **composition 1**: locate once when the Markdown is made and keep the AssetLocation. |
| Markdown → YamlFields | writes the section's YAML fields onto the instance it reads for, and onto what it builds | harness/markdown/markdown.py:867, :905, :909 | W | missed | Markdown sets attributes on another object by key (`YamlFields(self._instance).assign_yaml`), so the owner's state changes as a side effect of reading prose. **Owner** the guidance or toolset whose section it is; **association**: Markdown answers the section's settings (`markdown.settings`) and the owner applies them to itself. |
| Markdown → Format | turns a template file's folder or extension into a format name | harness/markdown/markdown.py:938-940 | R | W | The string converted is a template file's folder name or suffix, not Markdown's own state; there is no Format for Markdown to own. The earlier redesign ("`markdown.format`") names a property Markdown has no use for. |
| AssetLocator → the guidance or toolset it locates for | reads `practice_guidance`, `module_dir`, `fidelities.current`, `fidelity`, `domain_slug`, `name` by attribute name | harness/markdown/markdown.py:403-411, :421-430, :434-451, :478 | W | missed | The locator reaches into whatever object it is handed and guesses ownership from attribute names (`_declared_name_scope` walks the class order to tell a guidance from a toolset). **Owner** the guidance (PracticeGuidance / FidelityGuidance) and AgentToolSetOrigin; **association 1**: the owner hands its folder, slug and current fidelity to the Markdown it holds, so the locator reads named values instead of probing attributes. |
| AssetLocation → MarkdownFile | builds one to read a section of the file it located | harness/markdown/markdown.py:370 | R | missed | A file it was made to point at, read once per extract; the location is the owner of that file reference. |
| MarkdownCollection → MarkdownText | parses the section text into child blocks in `from_markdown` | harness/markdown/markdown.py:768 | R | W | `from_markdown` is a creation factory: it reads the text it is given once and keeps the entries and `markdown` it made. Nothing is rebuilt later. |
| MarkdownCollection → Markdown | handed one in `from_section`; `as_property` makes the owner's Markdown once per owner and keeps the result on the owner | harness/markdown/markdown.py:779-788, :810-819 | R | W | The Markdown belongs to the owner, not to the collection, and the property caches the collection in `vars(owner)` after the first read. The earlier "MarkdownCollection owns the Markdown objects it makes" names the wrong owner. |

## harness/agent_tools

| from → to | interaction | file:line | verdict | changed from | reason |
|---|---|---|---|---|---|
| AgentToolSet → AgentTool | `tools` rebuilds every enlisted and collection tool on each read | harness/agent_tools/agent_tools.py:537-543, :583, :608 | W | | Every read of `tools`, `tools_for`, `operations` or `instructions` makes new AgentTool objects; the hook server asks for them on every event (`hook_server.py:380`) and MCP on every start. The `description` cache on AgentTool is lost with each rebuild. **Owner** AgentToolSet; **composition 0..\***: discover the tools once per toolset instance and keep them; `for_call` already re-binds a tool to a toolset made for one call. |
| AgentToolSet → AgentOperation | `_discover_operations` on every `operations` and `tools` read | harness/agent_tools/agent_tools.py:561-565 | W | | Same rebuild as above; same redesign. |
| AgentToolSet → AgentInstructions | `_discover_instruction_members` on every `instructions` and `tools` read | harness/agent_tools/agent_tools.py:573-578 | W | | Same rebuild; same redesign. |
| AgentToolSet → ToolSubjectLoader | builds a loader of its own class three times per operation, and once in `_made` | harness/agent_tools/agent_tools.py:506, :568, :570, :571 | W | | The loader is a fact of the toolset class. **Owner** AgentToolSet (its class); **composition 1**, not the earlier 0..\*: one loader per toolset class, read where needed. |
| AgentToolSet → ToolsetMembers | `_members` builds one per read, and ToolsetMembers keeps every class it walked in a class-level dict | harness/agent_tools/agent_tools.py:158-169, :557-559 | W | missed | The per-class cache is global state keyed by type. **Owner** the toolset class; **composition 1**: the class joined by `@agent_toolset` holds its members, so no process-wide dictionary is needed. |
| AgentToolSet → ToolsetReference | parses a `module:Class` string to find the class to make | harness/agent_tools/agent_tools.py:479, :483 | W | missed | Toolsets travel through the installer, the MCP server and the hook server as strings that each one turns back into classes. **Owner** RepositoryToolsets; **aggregation 0..\***: RepositoryToolsets answers the toolset classes it found, and `instantiate` takes a class. (See RepositoryToolsets below.) |
| AgentToolSet → ToolCall | `session_for(call)` reads the session of the call it is handed | harness/agent_tools/agent_tools.py:555 | R | | A per-call value handed in. |
| AgentToolSet → ToolSetCollectionAnnotation, AgentToolSetAnnotation, AgentToolAnnotation, AgentInstructionsAnnotation | reads annotations an author typed | harness/agent_tools/agent_tools.py:516, :564, :577, :644, :649 | R | | Annotations mark members; nothing holds them. (4 relationships) |
| AgentTool → AgentToolSet | reads `slug`, `registration_name`; asks `for_call`, `session_for` | harness/agent_tools/agent_tools.py:756, :760, :801, :835 | R | | The toolset it is held by (dataclass field). |
| AgentTool → Markdown | `description` makes `Markdown.from_label(self.toolset, "")` to expand a one-word docstring | harness/agent_tools/agent_tools.py:879 | W | | The section belongs to the toolset, not to the tool; every tool of a toolset makes its own Markdown of the same file. **Owner** AgentToolSet; **composition 1**: the toolset holds its Markdown, and AgentTool asks `toolset.markdown.expand_docstring(...)`. The earlier "AgentTool holds its Markdown" names the wrong owner. |
| AgentTool → ParameterSchema | builds the schema of its own callable for every `input_schema` read and every `answer` | harness/agent_tools/agent_tools.py:791, :803 | W | missed | The schema depends only on the callable AgentTool holds; MCP reads `input_schema` on every tool list request. **Owner** AgentTool; **composition 1**: made once from `callable`. |
| AgentTool → ToolCall | `invoke(arguments, project)` wraps an in-process call as a ToolCall and answers it | harness/agent_tools/agent_tools.py:796 | R | W | A ToolCall is one request; there is no "ToolCall of the tool" to keep. The earlier `agenttool.tool_call` would make every call share one record. |
| AgentTool → AgentToolAnnotation, AgentInstructionsAnnotation, NoSessionLog, SubAgentAnnotation, TakesCalledProject, NoDeploy | reads annotations on its callable (NoDeploy through `annotation_kinds.publishes`) | harness/agent_tools/agent_tools.py:740, :815, :824, :826, :847-849, :874 | R | | Annotations an author typed. (6 relationships) |
| AgentTool → InstallDestination | names channels by constant | harness/agent_tools/agent_tools.py:724-744, :765-766 | R | | Constants. |
| GuidanceAgentOperation → ToolCall | reads the arguments of the call it is handed | harness/agent_tools/agent_tools.py:962 | R | | Per-call value. |
| GuidanceAgentOperation → GuidanceAction | calls the private `_log_running_action` on its toolset | harness/agent_tools/agent_tools.py:964 | W | missed | A tool reaches a private member of the guidance action. **Owner** GuidanceAction; **association 1** (the toolset it already holds): GuidanceAction exposes a public `log_running(action)` and the operation calls that. |
| AgentInstructions → AgentToolSet | `for_callable` makes a blank `AgentToolSet()` when no instance is given; `member_of` calls the private `_discover_instruction_members` of another toolset; `_expanded_reply` rediscovers itself through `for_callable(self.callable, toolset)` | harness/agent_tools/agent_tools.py:984-992, :1014, :1052 | W | | The blank-toolset branch is reached by no production caller (satisfy.py:34 and every spec pass an instance). `_expanded_reply` rebuilds every instruction member of its own toolset to find the AgentInstructions it already is. **Owner** the target AgentToolSet; **association 1**: drop the blank-toolset branch, have `_expanded_reply` call `self.expand(arguments)`, and have `member_of` read `target.instructions[member]` (public, held once per the AgentToolSet redesign). The earlier "composition 0..\*, AgentInstructions owns the AgentToolSet objects it makes" is wrong: the toolset owns its instructions, not the reverse. |
| AgentInstructions → RecipeExpansion | one expansion per `prompt`, `tools` and `expand` | harness/agent_tools/agent_tools.py:997, :1002, :1036 | R | missed | The class docstring says each expansion runs in a RecipeExpansion of its own, and the expansion holds that run's state. |
| AgentInstructions → RecipeSource | parses its own callable's source on every `result_template` read | harness/agent_tools/agent_tools.py:1026, :1030 | W | missed | **Owner** AgentInstructions; **composition 1**: parse the recipe source once from the callable it holds. |
| AgentInstructions → AgentInstructionsAnnotation, AgentToolAnnotation, AgentToolSetAnnotation | reads annotations | harness/agent_tools/agent_tools.py:974, :1057, :1077 | R | | (3 relationships) |
| AgentInstructions → ToolCall | reads the arguments of the call it is handed | harness/agent_tools/agent_tools.py:1010 | R | | Per-call value. |
| AgentToolSetAnnotation → AgentToolSet | joins the annotated class with AgentToolSet | harness/agent_tools/agent_tools.py:1174 | R | | A class annotation that gives the class its framework base. |
| AgentToolSetAnnotation → ToolsetValidator | validates the joined class as it is defined | harness/agent_tools/agent_tools.py:1175 | R | missed | Runs once per class definition. |
| ToolsetValidator → ToolsetMembers, RecipeSource, _RecipeLinesValidator | reads the class's members and each recipe's source | harness/agent_tools/agent_tools.py:297, :315, :317 | R | missed | Made once per validation and discarded with it. (3 relationships) |
| ToolSubjectLoader → ToolSubject, TakesCalledProject, OnSubject | reads the loader annotation; marks the wrappers it makes | harness/agent_tools/agent_tools.py:665, :674, :683-685, :701 | R | | (3 relationships) |
| ToolCall → ChatPointer | `sent` takes the chat out of the arguments and keeps it as `self.chat` | harness/agent_tools/tool_call.py:54, :65 | R | W | ToolCall already holds its ChatPointer (`self.chat`, composition 0..1), made once in the `sent` factory. The earlier W asked for exactly what the code does. |
| ToolCall → SessionOpener | opens the call's session through the opener space/session registered | harness/agent_tools/tool_call.py:76-78, :89, :97 | R | | A registry the session module registers with at import, so harness never imports space. |
| ChatPointer → Name | normalises a chat file's header keys to kebab case | harness/agent_tools/chat_pointer.py:105 | R | W | The string is a header key read from a file, not ChatPointer's own name; no object could hold it. |

## harness/installation (with harness/installer)

| from → to | interaction | file:line | verdict | changed from | reason |
|---|---|---|---|---|---|
| FileInstallation → IdeLayout | builds `IdeLayout(ide)` in its constructor | harness/installation/files.py:87 | W | R | The Installer already holds `self.layout` for the same IDE (`installer.py:78`), and McpInstallation and UserMcpConfig build their own copies too. Four objects each turn the IDE name string into a layout. **Owner** Installer; **association 1**: Installation (the base) is handed the Installer's IdeLayout instead of an `ide` string. |
| FileInstallation → Name | re-derives kebab names from the operation name, the toolset slug, folder parts, and each tool's deploy name | harness/installation/files.py:92, :152, :168, :182 | W | | The values converted are the tool's and toolset's own names (`toolset.slug` is already kebab through Name). **Owner** AgentTool (its published file name) and AgentToolSet (its slug); **composition 1**, a property on each. The earlier "FileInstallation owns its Name" names the wrong owner. |
| FileInstallation → MarkdownText | strips the YAML blocks from a rules body | harness/installation/files.py:111 | W | | The body came from `getattr(result, "markdown")` on the toolset's rules (`files.py:223-229`). **Owner** the rules collection the toolset holds (RulesCollection, harness/guidance); **composition 1**: it answers its installed text without YAML, and FileInstallation writes it. |
| FileInstallation → FrontMatter | parses a standing rule file's settings | harness/installation/files.py:122 | W | | Standing rules and agent files are both markdown files with settings, and Installer parses agent settings by hand (`installer.py:206-215`). **Owner** MarkdownFile (harness/markdown); **composition 1**: a MarkdownFile holds its FrontMatter, and both installs read `file.front_matter`. |
| FileInstallation → the toolset's attributes | reads `practice_guidance`, `slug`, `schema_guide`, `overview`, `fidelities.entries`, `rules.applies_to`, and the result's `markdown` / `formatted` by attribute name | harness/installation/files.py:97, :149-152, :200-204, :223-229, :233-234, :261-266, :294, :331-332; destination.py:252-254 | W | missed | The installation decides where a practice's files go and what their front matter says by probing the toolset. **Owner** AgentToolSet and PracticeGuidance; **association 1** (the toolset of the tool it is handed): the toolset answers its install folder, file stem, skill overview and rules front matter, and FileInstallation writes them. |
| FileInstallation → AgentTool | reads `kind`, `toolset`, `deploy_name`, `name`, `docstring`, `install_to_mcp`; calls `invoke_line` | harness/installation/files.py:104-107, :135-136, :197-223, :244-255 | R | | The tool it is handed to write. |
| FileInstallation → InstallDestination | names channels by constant | harness/installation/files.py:93, :96, :99, :255, :268 | R | | Constants. |
| FileInstallation → Skill, Command, Rules | writes the channel each annotation names | harness/installation/files.py:93, :96, :99 | R | | Annotations an author typed. (3 relationships) |
| LanguageAdapterInstallation → DataClass | reads the toolset class's `@language_adapter` languages | harness/installation/language_adapter.py:825 | R | W | DataClass is a read of annotations on a class and holds nothing but the class; there is nothing to keep between calls. |
| LanguageAdapterInstallation → InstallDestination, LanguageAdapter | names the MCP channel; reads the annotation | harness/installation/language_adapter.py:825, :860 | R | | (2 relationships) |
| LanguageAdapterInstallation → SourceFile | draws a file link for fields annotated with it (through `_FieldHint`) | harness/installation/language_adapter.py:196 | R | | An annotation on a data field. |
| LanguageAdapterInstallation → TypeScriptToolset of FileManager | picks the file manager's adapter out of the recorded toolsets by the class name string `"FileManager"` | harness/installation/language_adapter.py:30, :838-839 | W | missed | A second registry that names a toolset in tools/file_manager by string. **Owner** the FileManager toolset; **association**: an annotation on FileManager (for example `@language_adapter(language="typescript", shares_file_views=True)`) says it provides the shared file views, and the installation reads that annotation. |
| RepositoryToolsets → Name | normalises a decorator identifier to snake case | harness/installation/repository_toolsets.py:167 | R | W | The string is a decorator name read from source, not RepositoryToolsets' own state. |
| RepositoryToolsets → AgentToolSet.HOSTED_ONLY_CLASS_NAMES | skips classes by name: RulesCollection, MarkdownCollection, GuidanceCollection, PracticeGuidance, FidelityGuidance | harness/installation/repository_toolsets.py:130; also harness/hooks/hook_server.py:352 | W | R | A string list in harness/agent_tools naming classes in harness/guidance and harness/markdown is a second registry: rename a class and install silently publishes it. **Owner** each of those classes; **association**: they carry a class annotation (an OmissionAnnotation, `@hosted_only`) that RepositoryToolsets reads in the AST as it already reads `@agent_toolset`, and the hook server reads with `annotates`. |
| RepositoryToolsets → AgentToolSet (the toolset list) | answers every toolset as a `module:Class` string, which the Installer, McpServer, McpHost and HandlerCatalog each turn back into classes | harness/installation/repository_toolsets.py:110-132 | W | missed | The repository's toolsets are reduced to strings and re-imported by four callers. **Owner** RepositoryToolsets; **aggregation 0..\***: it answers the toolset classes it found (it already imports them in `import_modules`), and the strings remain only where they cross a process boundary (`hook-handlers.json`). |
| RepositoryToolsets → Agent, AgentGuidance | counts `agent` and `agent_guidance` decorator names as signs of a toolset | harness/installation/repository_toolsets.py:58 | D | R | No source in the repository applies `@agent` or `@agent_guidance`, and no code reads their flags; see Agent and AgentGuidance in section 2. Remove both names with the classes. |
| DataClass → DataField, Identity, LanguageAdapter, Edits | reads annotations on the class and its properties | harness/installation/destination.py:152-153, :159, :164, :168, :172 | R | | (4 relationships) |
| Installer → RepositoryToolsets | builds it once in its constructor from its own `repo` | harness/installer/installer.py:83 | R | W | A part made once from the Installer's own repository folder and kept (`self.toolsets`), exactly as IdeLayout at :78 was judged R. The earlier W was a rule applied to the constructor, not to the shape. |
| Installer → AgentToolSet | makes each toolset from its `module:Class` reference while installing | harness/installer/installer.py:168, :170 | W | | **Owner** RepositoryToolsets; **aggregation 0..\***: the Installer walks `self.toolsets.toolset_classes` instead of strings. The earlier "Installer owns the AgentToolSet objects" is wrong: the Installer makes them only to read their tools. |
| Installer → FileInstallation | builds a new FileInstallation for every tool and every file channel, and another for standing rules | harness/installer/installer.py:105, :222 | W | | Thousands of identical installations per run. **Owner** `_InstallChannels` (the run's installations); **composition 1 per file channel** (skill, command, rules, each with and without MCP mode, and the standing-rules writer), made with the MCP, hook and adapter installations it already holds. |
| Installer → HookDaemon | builds `HookDaemon(self.repo)` in `_ensure_hook_server` and again in `_runtime_status_report` | harness/installer/installer.py:285, :329 | W | | **Owner** Installer; **association 1**: the hook daemon of the checkout is made once (or handed in) and kept. |
| Installer → HookInstallation | builds a second HookInstallation to read the registered events and operations | harness/installer/installer.py:331 | W | | The run's hook installation already exists (`_channels_of_run().hook`). **Owner** `_InstallChannels`; read `channels.hook.registered_events`. |
| Installer → Installation | hands each installation a callback that records its writes | harness/installer/installer.py:96 | R | W | The Installer gives every installation the record to write to; it does not own or rebuild them here. The per-tool construction is the FileInstallation row above. |
| Installer → AgentTool | reads `destinations` | harness/installer/installer.py:100 | R | | The tool it is installing. |
| Installer → IdeLayout | builds its layout once | harness/installer/installer.py:78 | R | | Composition 1. |
| Installer → InstallDestination | names channels | harness/installer/installer.py:101-108 | R | | Constants. |
| Installer → InstallRecord, InstallDiagnostics, ClaudePlugins | builds each once in its constructor | harness/installer/installer.py:76, :80-82 | R | missed | Parts made once and kept. (3 relationships) |
| Installer → Installer | each `@hook` operation builds `Installer(repo=_CDD_CHECKOUT)` to start the cdd server | harness/installer/installer.py:377, :381 | W | missed | The hook server already holds an Installer toolset; building another per event hides that the hook server's instance has no repository. **Owner** HandlerCatalog (the hook server's toolsets); **association 1**: the hook server makes the Installer for the checkout it serves (`Installer.load(project=checkout)`), and the hook calls `self.ensure_mcp_server()`. |
| Installer → agent file settings | reads the `name:` line of each agent file by hand | harness/installer/installer.py:206-215 | W | missed | Duplicates FrontMatter. **Owner** MarkdownFile; **composition 1** (see FileInstallation → FrontMatter). |
| _InstallChannels → McpInstallation, HookInstallation, LanguageAdapterInstallation | makes one of each per install run and has the Installer track it | harness/installer/installer.py:58-62 | R | missed | Composition 1 each. (3 relationships) |
| InstallDiagnostics → HookInstallation | builds a HookInstallation only to read `hook-handlers.json` | harness/installer/install_diagnostics.py:37 | W | missed | **Owner** the file, HookHandlersFile; **composition 1**: InstallDiagnostics reads `HookHandlersFile(folder / NAME).operation_names` it holds, or is handed the run's hook installation. |
| ClaudePlugins → UserMcpConfig | builds `UserMcpConfig("Claude")` to find Claude's settings folder | harness/installer/claude_plugins.py:68 | W | missed | Same hard-coded construction as McpHost (below). **Owner** IdeLayout("Claude") held by ClaudePlugins; **composition 1**. |
| ClaudePlugins → CddHome | handed one, or makes one | harness/installer/claude_plugins.py:30 | R | missed | Collaborator injected with a default. |

## harness/hooks

| from → to | interaction | file:line | verdict | changed from | reason |
|---|---|---|---|---|---|
| HookDaemon → StoppableProcess | wraps the pid in the raw state dict to stop a daemon on older code | harness/hooks/hook_daemon.py:200-204 | W | | `replace_stale` reads the address file as a dict, while `live_address` reads the same file into HookDaemonAddress (`:169-172`). **Owner** HookDaemonAddress (the published state, which already holds `pid`; add `stamp`); **composition 1**: the address holds the StoppableProcess of its pid, and `replace_stale` calls `published.process.stop()`. The earlier "composition 0..\*, HookDaemon owns the StoppableProcess objects" names the wrong owner. |
| _SpawnLock → RunningProcess | wraps the pid it reads from the lock file on every check | harness/hooks/hook_daemon.py:130, :134-138 | W | | **Owner** _SpawnLock; **composition 0..1**: the lock reads its holder once and keeps the holder's RunningProcess. |
| HookDaemon → RepositoryToolsets | builds one in `spawn` and another in `_loaded_server` from `self.repo` | harness/hooks/hook_daemon.py:220, :251 | W | | **Owner** HookDaemon; **composition 1** (not the earlier 0..\*): made once from its checkout and kept. |
| HookDaemon → BackgroundStart | starts the daemon process detached | harness/hooks/hook_daemon.py:229 | R | W | BackgroundStart is the operating system's process start, with one flag and no state of the daemon's; making it at the start is the start. |
| HookDaemon → PythonInterpreter | the interpreter running this process, windowless | harness/hooks/hook_daemon.py:230 | R | W | It wraps `sys.executable`, which no object of the model owns. |
| HookDaemon → HookServer | loads the server once when `serve` starts (or is handed one) and hands every event to it | harness/hooks/hook_daemon.py:241, :252, :339 | R | W | Made once per daemon process and passed to the serve loop; `serve(server)` accepts it injected. Not a per-call lookup. |
| HookInstallation → HookServer | stands up a server from the handlers file it wrote, to check it loads | harness/hooks/hooks.py:283 | R | W | A check of its own output, kept in `self.server`. |
| HookInstallation → PythonInterpreter | builds `PythonInterpreter(self.python)` on every `dispatch_command` read | harness/hooks/hooks.py:206 | W | | **Owner** HookInstallation; **composition 1**: hold the interpreter instead of the `python` string. |
| HookInstallation → HookHandlersFile, HooksManifest | builds each file object on every property read | harness/hooks/hooks.py:210, :214 | W | missed | **Owner** HookInstallation; **composition 1 each**: both paths are fixed by `self.path`. |
| HookInstallation → toolset class `_hooks_deploy` | reads the attribute `@hooks` set on the class | harness/hooks/hooks.py:229 | W | missed | `Hooks` sets `_hooks_disabled` / `_hooks_deploy` on the class directly and is not an Annotation, so it bypasses `annotation_kinds`. **Owner** Hooks; make it an Annotation with `disabled_on(toolset)` and `deploys(toolset)`, read through the annotation. |
| HookInstallation → AgentTool | reads `install_to_hook`, `hook_event`, `toolset`, `name`, `registration_name` | harness/hooks/hooks.py:227-231 | R | | The tool it is handed. |
| HookInstallation → Hook | enrolls the event the annotation names | harness/hooks/hooks.py:227 | R | | Annotation. |
| HookServer → HookPayload | parses each event from stdin; `diagnose` dispatches an empty payload | harness/hooks/hook_server.py:538, :574 | R | W | A payload is one event the IDE sent; there is no payload of the server to keep. |
| HookServer → ToolCall | builds `ToolCall(project=self._repo_root)` only to reach the registered session opener | harness/hooks/hook_server.py:520 | W | | A fake call stands in for "the session open in this checkout", read on every event and every debug line. **Owner** the session module's opener (space/session), reached by HookServer through the same registry ToolCall uses; **association 1**: ToolCall exposes `ToolCall.open_session_in(project)` (or HookServer is handed the opener), so no call record is invented. The earlier "HookServer owns its ToolCall, composition 1" would keep one fake call forever. |
| HookServer → ChatInjections | builds one per event from the session it just opened | harness/hooks/hook_server.py:523-526 | W | missed | ChatInjections is the session's `chat-injections` folder. **Owner** the session (space/session Session); **composition 1**: the session holds its chat injections; HookServer asks `session.chat_injections`. |
| HookServer → HandlerCatalog | handed one in its constructor | harness/hooks/hook_server.py:497-499 | R | missed | Collaborator passed in. |
| HookServer → Hook | runs the members annotated | harness/hooks/hook_server.py:380 | R | | Annotation (through `tools_for(HOOK)`). |
| HandlerCatalog → AgentToolSet, RepositoryToolsets, HookHandlersFile | loads toolsets from `hook-handlers.json` references or from `RepositoryToolsets(...).collect()` strings, filtering by `HOSTED_ONLY_CLASS_NAMES` | harness/hooks/hook_server.py:338-352 | W | missed | Same string-reference shape as the Installer. **Owner** RepositoryToolsets (aggregation 0..\* of toolset classes) and the hosted-only annotation, as above. |
| HandlerCatalog → HookHandler | builds a handler per hook tool on every `for_event` | harness/hooks/hook_server.py:371-377 | W | missed | **Owner** HandlerCatalog; **composition 0..\***: build the handlers once when the toolsets load, keyed by event. |
| HookHandler → toolset `_hooks_disabled`, `pattern` | reads attributes by name on the toolset and its class | harness/hooks/hook_server.py:257, :266 | W | missed | **Owner** the toolset (and the Hooks annotation, as above); **association 1** (held through `tool.toolset`): the toolset answers `hooks_enabled` and its pattern through named properties. |
| HookHandler → ContextConfig | reads the guideline setting of the project root the event names | harness/hooks/hook_server.py:304, :309 | R | missed | The project's `.context` configuration file, an outside file whose root changes per event. |

## harness/mcp

| from → to | interaction | file:line | verdict | changed from | reason |
|---|---|---|---|---|---|
| McpHost → McpServer | handed the checkout server; keeps one server per project, started once on the first call that names it | harness/mcp/mcp_server.py:605-607, :619-626, :846, :895 | R | W | McpHost already aggregates its servers by project (`self._servers`, aggregation 1..\*); `from_refs` is the factory. Nothing is rebuilt per call. |
| McpHost → RepositoryToolsets | `from_repo` lists the checkout's toolsets once to build a host | harness/mcp/mcp_server.py:880 | R | W | A creation factory run once. The string references it passes on are the RepositoryToolsets W above. |
| McpHost → ToolCall | makes one ToolCall per chat request and per in-process dispatch | harness/mcp/mcp_server.py:695, :757 | R | W | One call per request is the design (`tool_call.py:33-39`). The earlier "McpHost holds its ToolCall" would make every chat share a call. |
| McpHost → UserMcpConfig | builds `UserMcpConfig("Claude")` per call to compare the named project with Claude's settings folder | harness/mcp/mcp_server.py:740 | W | | A fixed folder recomputed per request from a hard-coded IDE name. **Owner** McpHost; **composition 1**: hold Claude's settings folder (from IdeLayout("Claude")) once. |
| McpHost → _ToolCalls, _RestartGate, _CddProtocolServer | makes each once in its constructor | harness/mcp/mcp_server.py:609-611 | R | missed | Parts made once. (3 relationships) |
| McpServer → AgentToolSet | makes the toolsets for its project from `module:Class` references in `start` and again in `for_project` / `restarted` | harness/mcp/mcp_server.py:443, :459, :468 | W | | Making new toolsets per project is intended (`for_project` docstring), and McpServer keeps their tools. What is wrong is the string reference re-parsed for every project. **Owner** RepositoryToolsets; **aggregation 0..\*** of toolset classes, which McpServer instantiates per project. The earlier "association 1, holds its AgentToolSet" misreads the cardinality. |
| McpServer → ToolCall | `invoke_tool` / `invoke_prompt` wrap an in-process call | harness/mcp/mcp_server.py:522, :526 | R | W | One call per request. |
| McpServer → toolset `practice_guidance` | skips a fidelity toolset by probing `getattr(toolset, "practice_guidance", "missing")` | harness/mcp/mcp_server.py:484 | W | missed | **Owner** the toolset (FidelityGuidance); **association 1**: FidelityGuidance publishes no MCP tools through its own annotations (`@noDeploy` or no `@mcp`), so the server needs no probe. |
| McpServer → AgentTool | keeps the tools it enrolled | harness/mcp/mcp_server.py:424-426, :433 | R | | Composition 0..\*. |
| McpServer → InstallDestination, LongCall, Mcp | channel constant; reads annotations | harness/mcp/mcp_server.py:486, :518 | R | | (3 relationships) |
| McpInstallation → McpHost | stands up a host over its checkout to check it loads | harness/mcp/mcp_server.py:316 | R | W | A check of its own output, kept in `self.host`. |
| McpInstallation → UserMcpConfig | builds a new UserMcpConfig on every `user_config` read (five reads per manifest write) | harness/mcp/mcp_server.py:165-170 | W | | **Owner** McpInstallation; **composition 0..1** (none for a temporary tree), made once. |
| McpInstallation → IdeLayout | builds `IdeLayout(ide)` in its constructor | harness/mcp/mcp_server.py:148 | W | R | Same duplicate layout as FileInstallation. **Owner** Installer; **association 1**, handed to Installation. |
| McpInstallation → McpDaemon | builds `McpDaemon(self.server_home)` on every `_daemon` read | harness/mcp/mcp_server.py:353-355 | W | missed | **Owner** McpInstallation; **composition 1**: made once from its CddHome. |
| McpInstallation → CddHome | handed one, or makes one | harness/mcp/mcp_server.py:147 | R | | Collaborator injected with a default. |
| McpInstallation → AgentTool, Mcp | records the operations annotated `@mcp` | harness/mcp/mcp_server.py:154-162 | R | | (2 relationships) |
| UserMcpConfig → IdeLayout | builds an IdeLayout and forwards three of its properties | harness/mcp/mcp_server.py:110-125 | W | R | UserMcpConfig adds only `project_folder`, a constant; it is a second object for IdeLayout's user-level settings. **Owner** IdeLayout; fold `user_settings_folder`, `user_mcp_config`, `mcp_servers_key` and the `${workspaceFolder}` spelling into IdeLayout and delete UserMcpConfig. |
| CddHome → Git | builds `Git(folder)` per command for the checkout being pinned and for the pinned copy | harness/mcp/cdd_home.py:213, :216, :227 | W | | Only half is wrong: the pinned copy (`pinned_checkout`) is CddHome's own folder, so its Git is a **composition 1** part; the source checkout is an argument, and a Git for it per pin is R. The earlier "composition 0..\*" covers both. |
| McpDaemon → StoppableProcess | wraps the pid in the running server's ping answer to stop it | harness/mcp/mcp_daemon.py:91 | W | missed | Same shape as HookDaemon: the ping answer is a dict. **Owner** the running server's answer, made an object (like HookDaemonAddress) that holds its StoppableProcess, **composition 1**. |
| McpDaemon → BackgroundStart | starts the server detached, or inside the starter's job | harness/mcp/mcp_daemon.py:97, :103 | R | missed | The operating system's process start. |
| McpDaemon → PythonInterpreter | builds `PythonInterpreter(self.home.python)` per start | harness/mcp/mcp_daemon.py:106 | W | missed | The interpreter belongs to the home it serves from. **Owner** CddHome; **composition 1**: CddHome holds its PythonInterpreter instead of the `python` string. |
| SpecServer → CddHome, McpDaemon | makes a throwaway home and its daemon once | harness/mcp/spec_support.py:49-50 | R | | Parts made once. (2 relationships) |
| ThrowawayMachine → UserHome, SpecServer | makes both once and drives them together | harness/mcp/spec_support.py:105-107 | R | missed | Composition 1 each. (2 relationships) |

# 2. Every class has a use

Inbound uses were found with `git grep -w` over Python, TypeScript and markdown (specs and `.retired/` excluded unless named), then read at the line. "Build time" lists how the installer, an import-time registration, or the TypeScript adapter reaches the class. Exceptions are listed with where they are raised.

## harness/name, harness/annotations

| class | used by | uses | build time | verdict |
|---|---|---|---|---|
| Name (name.py:11) | 100 production files, e.g. agent_tools.py:80, files.py:92, chat_pointer.py:105 | nothing | - | in use |
| AnnotationKinds (annotation.py:7) | its instance `annotation_kinds` (annotation.py:73), read at agent_tools.py:121, :740; files.py:268; markdown.py:975 | Annotation, Destination, OmissionAnnotation | every Annotation subclass registers at import (annotation.py:89) | in use |
| Annotation (annotation.py:76) | base of every annotation kind (agent_tools.py:1119-1219, destination.py:108, hooks.py:43 via Destination, mcp_server.py:59, sub_agent/annotation.py:17) | AnnotationKinds | registers kinds at import | in use (base) |
| OmissionAnnotation (annotation.py:115) | NoCatalog, NoDeploy (destination.py:14, :24); `withholds_install` (annotation.py:41) | - | read by install | in use (base) |
| Destination (annotation.py:129) | Rules, Hook, Mcp, Toast, NamedDestination | - | each channel's kind; installer | in use (base) |
| Toast (annotation.py:163) | `@Toast` on guidance_actions.py:321, :368; read by prompt_notify.py:264 | - | annotation an author types | in use |
| NamedDestination (annotation.py:170) | Skill, Command, Agent, AgentGuidance (files.py:18-37) | - | - | in use (base) |

## harness/process

| class | used by | uses | build time | verdict |
|---|---|---|---|---|
| Git (git.py:24) | Repo (space/repo/repo.py:122), CddHome (cdd_home.py:213, :227), Catalog (catalog_generator.py:409, :419) | RepoConnectError | - | in use |
| RepoConnectError (git.py:20) | raised git.py:39-58; caught cdd_home.py:228, project_approach.py:152 | - | - | in use |
| PythonInterpreter (process.py:14) | HookDaemon (hook_daemon.py:230), HookInstallation (hooks.py:206), McpDaemon (mcp_daemon.py:106) | - | - | in use |
| BackgroundStart (process.py:41) | HookDaemon (hook_daemon.py:229), McpDaemon (mcp_daemon.py:97, :103), scripts/start.py:184 | - | - | in use |
| RunningProcess (running_process.py:14) | _SpawnLock (hook_daemon.py:130), scripts/instances.py:85; base of StoppableProcess | - | - | in use |
| StoppableProcess (stoppable_process.py:26) | HookDaemon (hook_daemon.py:204), McpDaemon (mcp_daemon.py:91) | RunningProcess, ProcessNotStopped | - | in use |
| ProcessNotStopped (stoppable_process.py:16) | raised :38, :46; caught hook_daemon.py:205 | - | - | in use |

## harness/markdown

| class | used by | uses | build time | verdict |
|---|---|---|---|---|
| Format (format.py:6) | 20 files, e.g. guidance.py:359, markdown.py:345, generate.py:61 | - | `TEMPLATE_FOLDER_NAMES` at import (format.py:71) | in use |
| FrontMatter (front_matter.py:11) | FileInstallation (files.py:122), catalog_examples.py:76, catalog_generator.py:382 | - | - | in use |
| ExtractedMarkdown (markdown.py:18) | Markdown.coerce (markdown.py:887) | - | - | in use |
| HTML (markdown.py:28) | Markdown.coerce/html (markdown.py:878-885); 19 files, e.g. clean_engineering diagram_node.py:28 | - | - | in use |
| MarkdownText (markdown.py:80) | Markdown (:868, :907), MarkdownCollection (:768), MarkdownFile (:224), FileInstallation (files.py:111), catalog_generator.py:157, guidance.py:670 | YamlFields | - | in use |
| MarkdownFile (markdown.py:214) | AssetLocation (markdown.py:370) | MarkdownText | - | in use |
| AssetLocation (markdown.py:260) | AssetLocator (markdown.py:462-607) | MarkdownFile, Format, Name | - | in use |
| AssetLocator (markdown.py:378) | Markdown (markdown.py:862, :925) | AssetLocation, Format, Name | - | in use |
| YamlFields (markdown.py:614) | MarkdownText (:90), MarkdownCollection (:772), Markdown (:867, :905, :909) | Name | - | in use |
| MarkdownCollection (markdown.py:731) | ToolSetCollection.attach (agent_tools.py:92), `@markdownCollection` (markdown.py:992) used by guidance | Markdown, MarkdownText, YamlFields, MarkdownProperty | named in `HOSTED_ONLY_CLASS_NAMES` | in use |
| MarkdownTypeUnresolved (markdown.py:838) | raised markdown.py:956 | - | - | in use |
| Markdown (markdown.py:848) | AgentTool (agent_tools.py:879), MarkdownCollection (:813), `@markdown` (markdown.py:979) used by Installer (installer.py:352-366) and 27 files | AssetLocator, MarkdownText, YamlFields, HTML, ExtractedMarkdown, Format, MarkdownProperty | - | in use |
| MarkdownProperty (markdown.py:960) | Markdown.as_property (:949), MarkdownCollection.as_property (:822) | AnnotationKinds | copies annotations so wrapped members install | in use |

## harness/agent_tools

| class | used by | uses | build time | verdict |
|---|---|---|---|---|
| CallNamesNoProject (agent_tools.py:32) | raised agent_tools.py:818 | - | - | in use |
| AgentToolValidationError (agent_tools.py:41) | raised agent_tools.py:329, :331, :397 | - | raised at class definition | in use |
| ToolSetCollection (agent_tools.py:62) | joined by `@toolset_collection` (agent_tools.py:1187); checked at :644, :649 | ToolsetMembers, AgentTool, MarkdownCollection, Name | class annotation | in use |
| Collect (agent_tools.py:104) | `@collect` on guidance.py:201, :204, context_setup.py:264 | AnnotationKinds | - | in use |
| ToolsetMembers (agent_tools.py:154) | ToolSetCollection.tools (:97), AgentToolSet._members (:559), ToolsetValidator (:297), AgentInstructions.members_of (:1048) | annotation kinds | - | in use |
| ToolsetReference (agent_tools.py:233) | AgentToolSet.instantiate (:479, :483) | AgentToolSetAnnotation | - | in use |
| ToolsetValidator (agent_tools.py:289) | AgentToolSetAnnotation.annotate (:1175) | ToolsetMembers, RecipeSource, _RecipeLinesValidator | runs at every `@agent_toolset` class definition | in use |
| _RecipeLinesValidator (agent_tools.py:334) | ToolsetValidator (:317) | RecipeSource | at class definition | in use |
| AgentToolSetOrigin (agent_tools.py:400) | base of AgentToolSet only (:437) | Name | - | in use (single-subclass base; could be folded into AgentToolSet) |
| AgentToolSet (agent_tools.py:437) | joined into every `@agent_toolset` class; Installer (installer.py:168), McpServer (mcp_server.py:443), HandlerCatalog (hook_server.py:347), 18 production files | AgentTool, AgentOperation, AgentInstructions, ToolSubjectLoader, ToolsetMembers, ToolsetReference, ToolCall, annotations | every published toolset | in use |
| ToolSubjectLoader (agent_tools.py:652) | AgentToolSet (:506, :568-571), TypeScriptToolset (language_adapter.py:606) | ToolSubject, TakesCalledProject, OnSubject | TypeScript adapter reads the loader | in use |
| InstallDestination (agent_tools.py:704) | AgentTool, FileInstallation, Installer, McpServer, HandlerCatalog, LanguageAdapterInstallation, ActionCatalogue, GuidanceAction | - | channel names | in use |
| AgentToolDestination (agent_tools.py:717) | base of AgentTool only (:748) | AnnotationKinds | - | in use (single-subclass base) |
| AgentTool (agent_tools.py:748) | AgentToolSet, Installer, FileInstallation, McpServer, McpInstallation, HookInstallation, HookHandler | AgentToolSet, ToolCall, ParameterSchema, Markdown, annotations | every published member | in use |
| AgentOperation (agent_tools.py:949) | AgentToolSet._discover_operations (:563), agent_bdd_common.py:582 | - | `@agent_tool` members | in use |
| GuidanceAgentOperation (agent_tools.py:956) | GuidanceAction._discover_operations (guidance_actions.py:207) | ToolCall, GuidanceAction | - | in use |
| AgentInstructions (agent_tools.py:968) | AgentToolSet (:576), satisfy.py:34, RecipeExpansion (recipe.py:325-358) | RecipeExpansion, RecipeSource, RecipePlaceholders, ExpansionResult, AgentToolSet, ToolCall | `@agent_instructions` members | in use |
| AgentToolAnnotation (agent_tools.py:1119) | `@agent_tool` everywhere; read :179, :186, :564, :826, :847 | - | installer, MCP | in use |
| AgentInstructionsAnnotation (agent_tools.py:1125) | `@agent_instructions` everywhere; read :183, :303, :577, :849, :1077 | - | installer, MCP | in use |
| _ClassJoiningAnnotation (agent_tools.py:1131) | base of AgentToolSetAnnotation, ToolSetCollectionAnnotation | - | - | in use (base) |
| AgentToolSetAnnotation (agent_tools.py:1161) | `@agent_toolset` on every toolset; RepositoryToolsets reads the decorator name (repository_toolsets.py:164) | AgentToolSet, ToolsetValidator | installer discovery | in use |
| ToolSetCollectionAnnotation (agent_tools.py:1179) | `@toolset_collection` (guidance.py:183); read :516, :644, :649 | ToolSetCollection | - | in use |
| NoSessionLog (agent_tools.py:1192) | `@noSessionLog` on board.py, ticket.py, chat.py, server_health.py and others; read :824 | - | - | in use |
| ToolSubject (agent_tools.py:1200) | `@tool_subject` on Installer.load (installer.py:89), catalog_generator.py, chat.py, server_health.py; read :665 | - | TypeScript adapter loader | in use |
| OnSubject (agent_tools.py:1211) | set at :685; read language_adapter.py:604 | - | TypeScript adapter | in use |
| TakesCalledProject (agent_tools.py:1219) | set at :684, :701; read :674, :683, :815 | - | - | in use |
| ChatPointer (chat_pointer.py:26) | ToolCall (tool_call.py:65), Chat (harness/chat/chat.py:309), session log readers (7 files) | Name | - | in use |
| ParameterSchema (parameter_schema.py:25) | AgentTool (agent_tools.py:791, :803) | - | MCP input schema | in use |
| RecipeLineFailed, RecipeCallsItself, RecipeNotAFunction (recipe.py:29, :56, :217) | raised recipe.py:360, :513; :283; :137 | - | - | in use |
| ExpansionMode (recipe.py:66) | AgentToolSet.mode (agent_tools.py:459-466), RecipeExpansion | - | - | in use |
| ExpansionResult (recipe.py:88) | AgentInstructions.expand (agent_tools.py:1040) | - | - | in use |
| RecipePlaceholders (recipe.py:94) | AgentInstructions.expand (agent_tools.py:1037) | - | - | in use |
| RecipeSource (recipe.py:123) | ToolsetValidator (:315), AgentInstructions (:1026), RecipeExpansion (recipe.py:249) | - | - | in use |
| _LoopItem (recipe.py:225) | RecipeExpansion (recipe.py:606, :619) | - | - | in use |
| RecipeExpansion (recipe.py:233) | AgentInstructions (agent_tools.py:997, :1002, :1036) | RecipeSource, AgentInstructions, _LoopItem | - | in use |
| SubAgentAnnotation (sub_agent/annotation.py:17) | `@subAgent` on diagnose.py:20; read agent_tools.py:874; tools/sub_agent imports its preamble (sub_agent.py:5) | - | skill and MCP description | in use |
| SessionOpener (tool_call.py:12) | the protocol space/session registers (`ToolCall.open_sessions_with`) | - | registration at import | in use |
| SessionsNotLoaded (tool_call.py:24) | raised tool_call.py:96 | - | - | in use |
| ToolCall (tool_call.py:32) | McpHost, McpServer, AgentTool, HookServer, GuidanceAction, rule.py:174, file_manager.py:140, diagnostics | ChatPointer, SessionOpener | - | in use |

## harness/installation and harness/installer

| class | used by | uses | build time | verdict |
|---|---|---|---|---|
| ContextConfig (context_config.py:21) | HookHandler (hook_server.py:304, :309) and 2 more files | - | - | in use |
| MalformedContextConfigError (context_config.py:12) | raised :37, :44 | - | - | in use |
| NoCatalog (destination.py:14) | `@noCatalog` on Installer and others; read catalog_generator.py:84, :137 | - | catalog | in use |
| NoDeploy (destination.py:24) | `@noDeploy` on validate.py, action_catalogue.py; read through `annotation_kinds.withholds_install` | - | install | in use |
| LanguageAdapter (destination.py:39) | `@language_adapter` on access_facts.py, harness/chat/chat.py; read destination.py:164 | - | TypeScript adapter | in use (not an Annotation subclass: it bypasses `annotation_kinds`) |
| Identity (destination.py:58) | `@identity` on chat.py, guidance.py, kanban classes; read destination.py:159 | - | TypeScript adapter | in use (not an Annotation subclass) |
| ReferenceWithoutIdentityError (destination.py:81) | raised :183 | - | - | in use |
| Edits (destination.py:88) | read by DataClass.edited_by (destination.py:168) from TypeScriptOperation (language_adapter.py:255) | - | TypeScript adapter | in use, but only `harness/installation/_examples/note.py` and a spec carry `@edits`; no production class does |
| DataField (destination.py:108) | `@data_field` on chat.py, server_health.py, explorer.py, kanban; read destination.py:152 | - | TypeScript adapter, `data_of` | in use |
| DataClass (destination.py:137) | `data_of` (destination.py:213), LanguageAdapterInstallation (:825), language_adapter.py (12 sites) | DataField, Identity, LanguageAdapter, Edits | TypeScript adapter | in use |
| SourceFile (destination.py:217) | `Annotated[str, SourceFile]` in harness/graph/violation.py:117, explorer.py:139, tools/file_manager; read language_adapter.py:196 | - | TypeScript adapter | in use |
| Installation (destination.py:225) | base of FileInstallation, McpInstallation, HookInstallation, LanguageAdapterInstallation | - | installer | in use (base) |
| Skill, Command, Rules (files.py:18, :23, :28) | `@skill`, `@command`, `@rules` across cdd_guidance and harness; written by FileInstallation | - | installer channels | in use |
| **Agent** (files.py:33) | none: no source applies `@agent`; its flag `_agent` is read nowhere. The only mention is the string `"agent"` in RepositoryToolsets.ANNOTATIONS (repository_toolsets.py:58). Agents are installed by copying `cdd_guidance/agents/*.md` without any annotation (installer.py:195-204). Checked: `git grep -nE "@agent([^_a-zA-Z]\|$)"` over .py/.md/.ts finds only `@agent-spec-manifest` comments; `_agent` flag read nowhere; no TypeScript or catalog reference. | - | none | **D** |
| **AgentGuidance** (files.py:37) | none: `agent_guidance` alias (files.py:45) is applied nowhere; flag `_agent_guidance` read nowhere; only the string `"agent_guidance"` in RepositoryToolsets.ANNOTATIONS. Same greps as Agent. | - | none | **D** |
| InstructionsUnreadableAtInstall (files.py:52) | raised files.py:211 | - | - | in use |
| FileInstallation (files.py:67) | Installer (installer.py:105, :222) | IdeLayout, Name, MarkdownText, FrontMatter, AgentTool, AnnotationKinds | installer | in use |
| IdeLayout (ide_layout.py:9) | Installer (:78), FileInstallation (files.py:87), McpInstallation (mcp_server.py:148), UserMcpConfig (:112), InstallDiagnostics | - | - | in use |
| PublishedSchema, _SentArguments, _PythonName, _TypeText, _FieldHint, _DataShape, TypeScriptOperation, TypeScriptToolset, TypeScriptViews (language_adapter.py:57-634) | each other and LanguageAdapterInstallation (language_adapter.py:66-684, :849) | DataClass, Name, ToolSubjectLoader, OnSubject, SourceFile | generate the TypeScript adapters | in use |
| MissingIdentityError (language_adapter.py:50) | raised :377 | - | - | in use |
| LanguageAdapterInstallation (language_adapter.py:814) | _InstallChannels (installer.py:60) | DataClass, TypeScriptToolset | installer | in use |
| RepositoryToolsets (repository_toolsets.py:18) | Installer (:83), McpHost (mcp_server.py:880), HookDaemon (:220, :251), HandlerCatalog (hook_server.py:342), bootstrap.py:17, catalog_generator.py:184, agent_bdd conf.py:40 | Name, AgentToolSet constant | installer discovery | in use |
| ClaudePlugins (claude_plugins.py:18) | Installer (installer.py:82) | CddHome, UserMcpConfig | installs the cdd and board plugins | in use |
| InstallDiagnostics (install_diagnostics.py:17) | Installer (installer.py:81) | HookInstallation, IdeLayout | writes diagnostics.json | in use |
| InstallRecord (install_record.py:28), InstallRecordUnreadable (:15) | Installer (installer.py:31, :76, :80); raised :46, :48 | - | - | in use |
| ToolsetInstallFailed, HookServerNotRunning (installer.py:34, :43) | raised installer.py:172-176, :289 | - | - | in use |
| _InstallChannels (installer.py:51) | Installer (:144, :192) | McpInstallation, HookInstallation, LanguageAdapterInstallation | - | in use |
| Installer (installer.py:67) | scripts/install.py, diagnostics (agent_tools_diagnostics.py:36), spec_helpers.py:104, its own hooks | everything above | published toolset (`/install`, `/clean`, hooks) | in use |

## harness/hooks

| class | used by | uses | build time | verdict |
|---|---|---|---|---|
| Hooks (hooks.py:23) | `@hooks` on PromptLog (tools/prompt_log/prompt_log.py:141) and examples; read hooks.py:229, hook_server.py:257 | - | - | in use (not an Annotation subclass) |
| Hook (hooks.py:43) | `@hook` on Installer, PromptNotify, guidance rules; read through `annotation_kinds` | - | installer hook channel | in use |
| HooksFileUnreadable (hooks.py:105) | raised :127, :129, :171 | - | - | in use |
| _HooksJsonFile (hooks.py:115) | base of HookHandlersFile, HooksManifest | - | - | in use (base) |
| HookHandlersFile (hooks.py:137) | HookInstallation (:210), HandlerCatalog (hook_server.py:338, :341) | - | - | in use |
| HooksManifest (hooks.py:161) | HookInstallation (:214) | - | - | in use |
| HookInstallation (hooks.py:182) | _InstallChannels (installer.py:59), Installer (:331), InstallDiagnostics (:37) | HookServer, PythonInterpreter, HookHandlersFile, HooksManifest | installer hook channel | in use |
| HookDaemonNotReady (hook_daemon.py:45) | raised :278 | - | - | in use |
| HookDaemonAddress (hook_daemon.py:53) | HookDaemon (:172), Installer (installer.py:287-290) | _Wire | - | in use |
| _Wire (hook_daemon.py:78) | HookDaemonAddress (:74-75), HookDaemon (:325) | - | - | in use |
| _SpawnLock (hook_daemon.py:105) | HookDaemon (:256) | RunningProcess | - | in use |
| HookDaemon (hook_daemon.py:141) | hook_server.main (:645), Installer (:285, :329), server_health.py:32 | StoppableProcess, RepositoryToolsets, BackgroundStart, PythonInterpreter, HookServer, HookDaemonAddress | the hook command runs it | in use |
| HookPayload (hook_server.py:35) | HookServer, rule.py:155, guidance_actions.py, prompt_notify.py | - | - | in use |
| HookResult (hook_server.py:135) | HookServer, HookHandler, hook_server.main | - | - | in use |
| HookHandler (hook_server.py:243) | HandlerCatalog (:376) | AgentTool, ContextConfig, HookResult | - | in use |
| HandlerCatalog (hook_server.py:320) | HookServer (:505, :511) | HookHandlersFile, RepositoryToolsets, AgentToolSet, HookHandler | - | in use |
| HookIllegitimateHandler (hook_server.py:390) | HookServer (:500, :529) | - | - | in use |
| ChatInjections (hook_server.py:401) | HookServer (:526, :549) | HookResult, HookPayload | - | in use |
| HookServer (hook_server.py:484) | HookDaemon (:252, :339), HookInstallation (hooks.py:283), PromptNotify registers its toaster (prompt_notify.py:380) | HandlerCatalog, HookPayload, ToolCall, ChatInjections, HookResult | registry for toasts at import | in use |

## harness/mcp

| class | used by | uses | build time | verdict |
|---|---|---|---|---|
| CddHome (cdd_home.py:59) | McpInstallation (mcp_server.py:147), ClaudePlugins (:30), SpecServer (:49), mcp/__main__.py | Git | installs `~/.cdd` | in use |
| RuntimeNotInstalled, PinFailed, RuntimeRecordUnreadable (cdd_home.py:33, :41, :49) | raised :163; :205, :229; :244 | - | - | in use |
| _AcceptFailure, _ListeningLoop (listening_loop.py:22, :36) | _ListeningLoop (:83); McpHost.serve (mcp_server.py:810) | - | - | in use |
| ServerDidNotStart, ServerStateUnreadable (mcp_daemon.py:30, :38) | raised :149; :139 | - | - | in use |
| McpDaemon (mcp_daemon.py:47) | McpInstallation (mcp_server.py:355), SpecServer (:50), mcp/__main__.py:27 | StoppableProcess, BackgroundStart, PythonInterpreter, CddHome | - | in use |
| Mcp (mcp_server.py:51) | `@mcp` everywhere; read through `annotation_kinds` | - | installer MCP channel | in use |
| LongCall (mcp_server.py:59) | `@long_call` on graph.py, repo.py, diagnostics; read :518 | - | - | in use |
| McpStandupFailed, McpConfigUnreadable, ToolNotEnrolled, _SkippedTool, ProjectNotNamed, ProjectIsClaudeSettings (mcp_server.py:70-573) | raised :884; :308; :532, :539, :655, :789; :403-421; :744; :741 | - | - | in use |
| UserMcpConfig (mcp_server.py:107) | McpInstallation (:167), McpHost (:740), ClaudePlugins (:68) | IdeLayout | - | in use (see W: fold into IdeLayout) |
| McpInstallation (mcp_server.py:133) | _InstallChannels (installer.py:58) | CddHome, IdeLayout, UserMcpConfig, McpDaemon, McpHost | installer MCP channel | in use |
| McpServer (mcp_server.py:365) | McpHost (:605-626, :895) | AgentToolSet, AgentTool, ToolCall | - | in use |
| _ProjectNamedOnly, _CddProtocolServer (mcp_server.py:543, :587) | McpHost.http_app (:834), McpHost (:611) | - | - | in use |
| McpHost (mcp_server.py:600) | mcp/__main__.py:34, McpInstallation (:316), AgentToolsProbe (agent_tools_probe.py:77) | McpServer, ToolCall, UserMcpConfig, _ToolCalls, _RestartGate | the cdd server | in use |
| _RestartGate (restart_gate.py:14) | McpHost (:609) | - | - | in use |
| UserHome (spec_support.py:20) | ThrowawayMachine (:106), agent_bdd spec_helpers.py:100, heavy specs | - | spec support | in use |
| SpecServer (spec_support.py:44) | ThrowawayMachine (:107), spec_helpers.py:100, `python -m harness.mcp.spec_support` (:127, :131) for specs in other languages | CddHome, McpDaemon | spec support | in use |
| ThrowawayMachine (spec_support.py:101) | installer_heavy_spec.py:177 and 6 more heavy specs | UserHome, SpecServer | spec support | in use (specs only) |
| ToolCallStopped, _StillRunning, _RunningCall, _ToolCalls (tool_calls.py:25-114) | each other; McpHost (mcp_server.py:610, :704) | ToolCall | - | in use |

# 3. Disconnected classes, verified

| class | earlier | verdict | reason / owner and redesign |
|---|---|---|---|
| Annotation, OmissionAnnotation, Destination, NamedDestination | Base | **confirmed Base** | Bases only; the concrete kinds carry the relationships. Add `AnnotationKinds`: it was not listed but is the registry every kind registers with at import (annotation.py:89), so it is connected. |
| RunningProcess | A | **confirmed A**, owner corrected | Used by `_SpawnLock` (hook_daemon.py:130), not by HookDaemon directly. The call is W: the lock holds its holder's RunningProcess (section 1). |
| SourceFile | A | **confirmed A** | Marker in `Annotated[str, SourceFile]` (violation.py:117, explorer.py:139, file_manager), read by `_FieldHint.is_source_file` (language_adapter.py:196). Note it is a bare class, not an Annotation subclass, like LanguageAdapter, Identity and Edits: four annotation kinds bypass `annotation_kinds`. |
| UserHome | B, owner SpecServer | **confirmed B, owner changed** | ThrowawayMachine already composes a UserHome and a SpecServer (spec_support.py:105-107). The duplicate is in `cdd_guidance/practices/agent_bdd/spec_helpers.py:100`, which builds both itself. Owner **ThrowawayMachine** (composition 1 each, as today); spec_helpers should use ThrowawayMachine. Folding UserHome into SpecServer would give the server a second job (rewriting the process's HOME variables). |
| FrontMatter | B, owner Markdown | **confirmed B, owner changed** | Markdown (markdown.py:848) reads a labelled section of an instance's guidance; it never reads a file's settings. The settings belong to a markdown file: owner **MarkdownFile** (composition 1). FileInstallation (files.py:122), the catalog (catalog_generator.py:382, catalog_examples.py:76) and Installer's hand-written parser (installer.py:206-215) then read `file.front_matter`. |
| Format | B, owners FidelityGuidance and PracticeGuidance | **confirmed B for harness/guidance, overturned inside harness/markdown** | The guidance.py constructions (guidance.py:359-814) are another area's and convert the guidance's own format name repeatedly. Inside this area Format converts strings nobody owns: template folder names and extensions (markdown.py:345, :348, :583, :594, :938-940) and `TEMPLATE_FOLDER_NAMES` (format.py:71). Those uses are R. |
| Agent, AgentGuidance | not listed | **new: no use** | See section 2: D. |

# 4. Summary

- Relationships checked: 147 (counting each target of a multi-target row).
- R: 93. W: 52. D: 2 (RepositoryToolsets → Agent, AgentGuidance).
- Overturned: 26 (20 W → R, 4 R → W, 2 R → D). A further 12 earlier W verdicts stand but with a different owner, cardinality or redesign (AgentToolSet → ToolSubjectLoader, AgentTool → Markdown, AgentInstructions → AgentToolSet, FileInstallation → Name / MarkdownText / FrontMatter, Installer → AgentToolSet / FileInstallation, HookDaemon → StoppableProcess / RepositoryToolsets, HookServer → ToolCall, McpServer → AgentToolSet, CddHome → Git).
- Missed by both earlier files: 46 (25 W, 21 R).
- Classes checked: 158 (all production classes in the area, private ones included).
- D: 2 (Agent, AgentGuidance in harness/installation/files.py).
