# harness/installation

The *Installer* publishes every annotated member of a repository's toolsets into one IDE folder, one *InstallRun* at a time, through an *Installation* for each channel, each writing through the install's *InstallPlace*; then it starts the servers its *RegisteredChannel*s point at (*ChannelServer*) and diagnoses what it deployed (*InstallDiagnosis*); *RepositoryToolsets* finds every toolset a repository defines. The module also reads and writes a project's CDD configuration files (*ContextConfig*, *JsonFile*, *AppPorts*) and holds the annotations that say what an object's data is.

- **Purpose:** Install one repository into one IDE folder through every channel, from one walk of the repository, and start the servers that install points at; give every channel the annotations, the data, and the writer it publishes a member with.
- **Seam (terms):** Installer, InstallRun, InstallChannels, ServerChannels (`SERVER_CHANNELS`), InstallRecord, LastInstall, InstallLock, InstallAlreadyRunning, UnknownIde, NotAnInstallFolder, JsonFileBusy, InstallDiagnostics, Deployed, DeployedChanges, InstallDiagnosis, InstallPlace, Installation, RegisteredChannel, ChannelServer, StandUp, FileInstallation, SkillInstallation, CommandInstallation, RulesInstallation, LanguageAdapters, SkippedTool, SkippedTools, IdeLayout, RepositoryToolsets, ContextConfig, JsonFile, JsonFileUnreadable, AppPorts, SourceFile, DataClass, NamedDestination, Skill, Command, Rules, DataField, Identity, LanguageAdapter; `data_of`, `CONTEXT_FOLDER`, `is_temporary`
- **Dependencies (one-way):** harness/annotations, harness/agent_tools, harness/markdown

## Installer

Publish every annotated member of the toolsets a repository defines into one IDE folder, through the installation of each channel its annotations name, then start the servers the installed files point at. Each install is one *InstallRun*, kept as `last_run`. harness/mcp and harness/hooks register their channels with `SERVER_CHANNELS` when they are imported, so this module imports neither.

+ Installer(target: InstallTarget, toolsets: RepositoryToolsets, last_install: LastInstall)
------
+ target: InstallTarget
+ repo: Path
+ ide: str
+ layout: IdeLayout
+ path: Path
+ << composition >> record: InstallRecord
+ << association >> last_install: LastInstall
+ << composition >> lock: InstallLock
	// one install or clean runs in the folder at a time
+ << association >> diagnostics: InstallDiagnostics
+ << association >> toolsets: RepositoryToolsets
+ << composition >> last_run: InstallRun | None
	// the install this installer ran last; none before its first
----
+ create(ide: str | None = None, path: str | Path | None = None, repo: str | Path): Installer
	// an IDE name is matched whatever its case; a name that is no IDE raises UnknownIde, and a path that is empty or a file raises NotAnInstallFolder, before anything is written
+ load(project: Path | str): Installer
+ clean(): list[str]
+ install(toolsets: Iterable[ToolsetReference | AgentToolSet] | None = None, replace: bool = True): InstallChannels
+ install_self(): InstallChannels
	// the Installer's own commands and the toolsets the registered channels publish, added to the last install
+ write_language_adapters(): list[Path]
+ repository_toolsets(): list[ToolsetReference]
+ diagnosis_of(channels: InstallChannels, published: dict[str, list[str]]): InstallDiagnosis
+ red_report(diagnosis: InstallDiagnosis): str
+ install_latest(): int
+ diagnose_install(): str
+ diagnose_instructions(): str
---<<runs each install as>>--> InstallRun
---<<reads toolsets with>>--> RepositoryToolsets
---<<names each toolset with>>--> ToolsetReference
---<<diagnoses an install as>>--> InstallDiagnosis
---<<writes sections with>>--> InstallDiagnostics
---<<holds the folder with>>--> InstallLock
---<<hands the last install's files to its record through>>--> LastInstall
---<<raises>>--> UnknownIde
---<<raises>>--> NotAnInstallFolder
---<<annotated with>>--> NoCatalog

## InstallRecord

`.install-state.json` in the IDE folder an install writes into: the IDE, the folder's whole path, and every file the install wrote, relative to the folder. Each folder keeps its own, and it is saved as each file is written, so an install stopped halfway still lists what it wrote and a clean removes it.

+ InstallRecord(target: InstallTarget)
------
+ folder: Path
+ ide: str
+ path: Path
+ installed_files: list[str]
+ saved: dict[str, Any]
----
+ track(written: Path): None
+ forget(relative: str): None
+ keep_existing(): None
+ adopt(installed_files: list[str]): None
	// takes the list an earlier CDD kept for this folder outside it, and saves
+ save(): None
+ remove_installed(): list[str]
+ prune_empty_parents(removed: Path): None
+ prune_empty_skill_folders(): None
---<<reads and writes through>>--> JsonFile

## LastInstall

The IDE and folder a checkout last installed into, kept in one file beside the installer, so an install or a clean that names neither goes there. An install into a temporary folder is not remembered.

+ LastInstall(path: Path)
------
+ saved: dict[str, Any]
----
+ remember(target: InstallTarget): None
+ hand_over_to(record: InstallRecord): None
	-> InstallRecord.adopt

## InstallLock : LockFile

The *LockFile* `.install-lock` in a folder installs write into, held for the process that installs into it or cleans it. harness/mcp's *ClaudeMarketplace* holds one on the cdd home while it publishes the mods. A second install says what it waits for and how long, waits for the first, then runs; the steps of one install share its lock.

+ InstallLock(folder: Path, wait_seconds: float = WAIT_SECONDS)
------
+ folder: Path
----
---<<raises>>--> InstallAlreadyRunning

## InstallAlreadyRunning : LockFileHeld

Another process is still installing into, or cleaning, the same folder after the wait.

+ InstallAlreadyRunning(folder: Path, holder: int, waited_seconds: float)
------
+ folder: Path
+ holder: int
+ waited_seconds: float
----

## UnknownIde : ValueError

An install named an IDE CDD does not install into. Nothing is written.

+ UnknownIde(ide: str, known: list[str])
------
+ ide: str
+ known: list[str]
----

## NotAnInstallFolder : ValueError

An install was told to write into something that cannot be an IDE folder: an empty path or a file. Nothing is written.

+ NotAnInstallFolder(path: Path | str, reason: str)
------
+ path: Path | str
----

## InstallRun

One install of toolsets into an installer's IDE folder, every toolset the repository defines when none are named: it writes every channel's files, tidies the folder and saves the install record, stands each channel's server up and starts it, then diagnoses what it deployed and records the diagnosis. replace wipes the previous install first.

+ InstallRun(installer: Installer, toolsets: Iterable[ToolsetReference | AgentToolSet] | None, replace: bool)
------
+ << composition >> channels: InstallChannels
+ diagnosis: InstallDiagnosis | None
----
+ run(): InstallChannels
	// holds the folder's lock, so a second install into the folder waits for it
+ publish(): None
+ stand_up(): None
	// a run inside one of the servers, as an install through MCP runs inside the cdd server, starts none
+ ensure_running(): list[str]
---<<makes each toolset with>>--> ToolsetReference
---<<hands each member to>>--> Installation
---<<stands up and starts>>--> ChannelServer
---<<records its diagnosis in>>--> InstallDiagnostics
---<<reads the names of>>--> InvokeLine
---<<raises>>--> ToolsetInstallFailed

## InstallChannels

The installations of one install, made once and used for every member of every toolset: one of each file channel, one of each registered channel, and the language adapters.

+ InstallChannels(installer: Installer, registered: Iterable[type[RegisteredChannel]])
------
+ << composition >> registered: list[RegisteredChannel]
+ << composition >> files: list[FileInstallation]
	// a SkillInstallation, a CommandInstallation, and rules
+ << composition >> rules: RulesInstallation
+ << composition >> language_adapters: LanguageAdapters
+ toolsets: list[AgentToolSet]
	// the toolsets the registered channels publish into every install, such as the hooks that start the cdd server
+ deployed: list[str]
	// the toolsets the install deployed, by their references
+ servers: list[ChannelServer]
+ published: dict[str, list[str]]
	// what each registered channel published, by its channel
----
+ of(kind: type[RegisteredChannel]): RegisteredChannel
+ for_tool(tool: AgentTool): list[Installation]
	// each registered channel that accepts tool, then each file channel install publishes it to
---<<asks whether its destination publishes>>--> AgentTool
---<<creates each registered>>--> RegisteredChannel

## ServerChannels

The kinds of registered channel every install publishes through, beside its file channels; the process keeps one, `SERVER_CHANNELS`.

+ ServerChannels()
------
+ kinds: list[type[RegisteredChannel]]
----
+ register(kind: type[RegisteredChannel]): None
---<<raises>>--> ServersNotRegistered

## InstallDiagnostics

`diagnostics.json` in one IDE folder: each install appends its diagnosis, what it deployed on every channel coloured by how much changed since the last install, and the diagnostics probes write their own sections beside that history.

+ InstallDiagnostics(folder: Path)
------
+ folder: Path
+ path: Path
----
+ record(diagnosis: InstallDiagnosis): None
+ last_deployed(): Deployed | None
	// what the latest install recorded it deployed; none before the first install
+ write_section(section: str, results: dict[str, Any]): None
+ installed_items(channel: str): list[str]
---<<reads and writes through>>--> JsonFile
---<<reads back>>--> Deployed

## Deployed

What an IDE folder holds on each channel an install reports: the toolsets it deployed, its skills, commands, rules, agents, and language adapters, and what each registered channel published.

+ Deployed(items: dict[str, list[str]])
------
+ CHANNELS: tuple[str, ...]
----
+ of_folder(target: InstallTarget, toolsets: list[str], published: dict[str, list[str]]): Deployed
+ items(channel: str): list[str]
+ changes_since(last: Deployed | None): DeployedChanges
---<<creates>>--> DeployedChanges

## DeployedChanges

What changed on each channel between the last install's deployment and this one's, and the colour of how much changed; the first install is green.

+ DeployedChanges(current: Deployed, last: Deployed | None)
------
+ colour: str
	// green when at most 10% of the compared items changed, yellow at most 50%, else red
+ report: str
----
+ added(channel: str): list[str]
+ removed(channel: str): list[str]

## InstallDiagnosis

One install's diagnosis: what it deployed, what changed since the last install, and the status each registered channel reports. Its report is written from its fields, never read back.

+ InstallDiagnosis(deployed: Deployed, changes: DeployedChanges, server_status: list[str])
------
+ << composition >> deployed: Deployed
+ << composition >> changes: DeployedChanges
+ server_status: list[str]
+ colour: str
+ is_red: bool
+ report: str
----

## InstallPlace

Where one install writes: the IDE folder with its layout, the record of every file the install wrote there, and the repository being installed. Every channel of one install writes through one place.

+ InstallPlace(target: InstallTarget, record: InstallRecord, repository: RepositoryToolsets | None = None)
------
+ << association >> target: InstallTarget
+ << association >> install_record: InstallRecord
+ << association >> repository: RepositoryToolsets | None
+ layout: IdeLayout
+ path: Path
+ repo: Path | None
+ is_temporary: bool
----
+ into(target: InstallTarget, repository: RepositoryToolsets | None = None): InstallPlace
	// a place that keeps its own record, for a writer outside an install run
+ wrote(written: Path): None
	-> InstallRecord.track
+ relative_folder(install_folder: Path): Path

## Installation : InstallPlace

Writes one channel's files into one IDE folder; a subclass names its `destination`, the *DestinationKind* that is its channel, and defines `write`.

------
+ destination: DestinationKind | None
----
+ install(tool: AgentTool): None
+ write(tool: AgentTool): None

## RegisteredChannel : Installation

A channel a module registers with the Installer beside the file channels: the MCP channel and the hook channel. A channel whose files point the IDE at a server holds it; the hook channel holds none.

------
+ toolsets: tuple[type, ...]
	// toolset classes every install publishes through this channel, such as the hooks that start the cdd server
+ << composition >> server: ChannelServer | None
+ published: list[str]
----
+ create(target: InstallTarget, record: InstallRecord, repository: RepositoryToolsets | None = None): RegisteredChannel
+ into(target: InstallTarget, repository: RepositoryToolsets | None = None): RegisteredChannel
+ accepts(tool: AgentTool): bool
	-> AgentTool.is_published_to(destination)
+ write_once_recorded(): None
+ status(): list[str]

## ChannelServer

The server a channel's installed files point the IDE at, as an install handles it: stood up in the install's process over what was installed, to check it loads, then started.

------
+ stood_up: StandUp | None
+ runs_this_process: bool
----
+ stand_up(): StandUp
+ ensure_running(): list[str]
---<<creates>>--> StandUp

## StandUp

What a channel's server answered when an install stood it up: the tools it serves, and the tools it skipped so it could serve the rest.

+ StandUp(tools: list[str], skipped: SkippedTools)
------
+ tools: list[str]
+ << association >> skipped: SkippedTools
+ notice: str
----

## FileInstallation : Installation

Write the markdown files of one file channel where the IDE reads them; each subclass says where a tool's file goes, the front matter that opens it, and its body. A tool also published where a server answers an agent's calls gets a file that tells the agent to call that tool.

------
----
+ relative_path(toolset: AgentToolSet, name: str): Path
+ front_matter(tool: AgentTool, relative: Path, parts: list[str], text: str): str
+ body(tool: AgentTool): str
+ write(tool: AgentTool): None
---<<calls invoke_line on>>--> AgentTool
---<<asks which destination answers calls>>--> AnnotationKinds
---<<creates>>--> Name

## SkillInstallation : FileInstallation

Write each `@skill` operation as `skills/<name>/SKILL.md`, opened by its name and the first paragraph of its toolset's overview.

------
+ destination: Skill
----
---<<writes the SKILL.md for>>--> Skill

## CommandInstallation : FileInstallation

Write each `@command` operation as a slash command in the IDE's commands folder.

------
+ destination: Command
----
---<<writes the slash command for>>--> Command

## RulesInstallation : FileInstallation

Write what each `@rules` member answers as a rules file, and the always-on rules of `cdd_guidance/rules`, each opened by front matter that says which files it applies to.

------
+ destination: Rules
----
+ write_standing_rule(source: Path): None
---<<creates>>--> FrontMatter
---<<writes the rules file for>>--> Rules

## LanguageAdapters : InstallPlace

The TypeScript language adapters of one install: a place, not a channel, since they are written from whole toolsets annotated `@language_adapter` rather than from a member's destination.

------
----
+ record(toolset: AgentToolSet): None
+ write_all(whole: bool = False): list[Path]
---<<reads the annotation>>--> LanguageAdapter

## SkippedTool : Exception

One published tool, handler, or toolset a server skipped so it could serve the rest: its toolset could not be loaded, its name or arguments were wrong, or it raised while answering.

+ SkippedTool(tool: str, reason: str, cause: BaseException | None = None)
------
+ tool: str
+ reason: str
+ cause: BaseException | None
----

## SkippedTools

What one server skipped while it stood up or answered, so it kept serving the rest: the cdd server's tools, the hook server's handlers. A diagnosis reports them, and the notice names them for whoever started the server.

+ SkippedTools(server: str, kind: str)
------
+ as_data: list[dict[str, str]]
+ notice: str
----
+ skip(tool: str, error: BaseException): None
+ clear(): None
+ notify(): None
---<<keeps>>--> SkippedTool

## IdeLayout

How one IDE lays out the folder CDD installs into: the folder's name in a project, where its slash commands and rules go, and the shape of a rule file.

+ IdeLayout(ide: str)
------
+ ide: str
+ folder_name: str
+ is_claude_code: bool
+ rule_suffix: str
+ commands_folder: str
+ nests_skills: bool
+ scopes_rules_by_paths: bool
+ runs_hooks: bool
+ user_settings_folder: Path | None
+ user_mcp_config: Path | None
+ mcp_servers_key: str
+ names_mcp_transport: bool
----
+ every(): list[IdeLayout]
+ guidance_kind_of(path: str): str

## RepositoryToolsets

*RepositoryToolsets* finds every toolset class in one repository by reading its source, without importing it, and puts the folders that load those classes on the import path.

+ RepositoryToolsets(root: Path | str)
------
+ GUIDANCE_FOLDER: str
+ IMPORT_FOLDERS: tuple[str, ...]
	// RUNNING_CHECKOUT, a module constant beside it, is the CDD checkout this code was imported from
+ root: Path
+ unloadable: list[ToolsetUnloadable]
+ agents_folder: Path
+ standing_rules_folder: Path
+ references_folder: Path
----
+ import_path_entries(): list[str]
+ pythonpath(): str
+ pycache_prefix(): str
+ use_for_this_process(): None
+ ensure_import_path(): None
+ references(): list[ToolsetReference]
	// reads the repository's source without importing it, so the installer, the hook server, and the MCP host publish the same toolsets
+ classes(): list[type]
---<<creates>>--> ToolsetReference
---<<recognizes toolsets by the names of>>--> Annotation
---<<creates>>--> Name

## ContextConfig

One project's `.context/config.json`: the guidelines that apply to it, each `enabled` or `disabled`, and the folder each practice writes in. `CONTEXT_FOLDER` names the `.context` folder once.

+ ContextConfig(root: Path | str)
------
+ root: Path
+ path: Path
----
+ exists(): bool
+ load(): dict[str, Any]
+ save(configuration: Mapping[str, Any]): Path
+ update(**sections): dict[str, Any]
+ guideline(pattern: str): str
+ practice_folder(practice: str): str | None
---<<reads and writes through>>--> JsonFile
---<<raises>>--> MalformedContextConfigError

## JsonFile

One file holding a JSON object, read and written whole by its owner. A missing file reads as empty; a file holding anything but a JSON object raises the owner's kind of *JsonFileUnreadable*, so an owner never saves over what a person wrote.

+ JsonFile(path: Path, unreadable: type[JsonFileUnreadable] = JsonFileUnreadable, compact: bool = False)
------
+ path: Path
----
+ exists(): bool
+ read(): dict[str, Any]
+ write(data: Mapping[str, Any]): Path
+ held(): Iterator[None]
	// holds the file for one change, from its read to its write, through a LockFile beside it, one per hold, so a change another thread or process makes waits its turn; the lock ends with its holder's process
---<<raises>>--> JsonFileUnreadable
---<<raises>>--> JsonFileBusy

## JsonFileUnreadable : ValueError

A JSON file holds something other than a JSON object. Nothing is written over it, so what it holds stays for a person to repair; each owner raises its own kind.

+ JsonFileUnreadable(path: Path, cause: Exception)
------
+ path: Path
+ cause: Exception
----
+ message(path: Path, cause: Exception): str

## JsonFileBusy : LockFileHeld

Another holder kept a JSON file for longer than a change waits for it, so the change was not made.

+ JsonFileBusy(file: Path, holder: int, waited_seconds: float)
------
+ file: Path
----

## AppPorts

The ports an app's servers answer on, as the one `ports.json` beside them gives them: each server's ports, in the order it tries them.

+ AppPorts(file: Path)
------
+ file: Path
----
+ of(server: str): tuple[int, ...]
---<<reads through>>--> JsonFile

## SourceFile : Annotation

Marks a data field that holds a path in the session's workspace: `path: Annotated[str, SourceFile]`.

------
----

## DataClass

What the annotations on one class declare about its objects' data: the properties that are its data (`@data_field`), the fields that name one object (`@identity`), and the languages its operations are typed in (`@language_adapter`). `data_of(value)` sends an object's data by it.

+ DataClass(data_class: type)
------
+ data_class: type
+ fields: dict[str, property]
+ identity: tuple[str, ...]
+ languages: tuple[str, ...]
+ shares_file_views: bool
----
+ of(data_class: type): DataClass
+ edited_by(operation: Any): tuple[str, ...]
+ sends_by_identity(field: property): bool
+ data(value: Any): dict[str, Any]
+ reference(value: Any): dict[str, Any]
---<<reads the data fields annotated>>--> DataField
---<<reads the identity fields annotated>>--> Identity
---<<reads the languages annotated>>--> LanguageAdapter

## NamedDestination : Destination

A file destination whose annotation may name what it installs: `@skill("name")`, `@command(name="name")`, or bare `@skill` for the operation's own name.

------
----

## Skill : NamedDestination

`@skill` or `@skill("name")` on an operation or instructions: install writes `{ide}/skills/{toolset}-{operation}/SKILL.md` (nested folders where the IDE reads them), which the IDE offers as a skill.

------
----

## Command : NamedDestination

`@command` or `@command(name="name")`: install writes the slash command `{ide}/commands/{toolset}/{name}.md` (`prompts` for VS Code).

------
----

## Rules : Destination

`@rules` on a practice's or fidelity's rules: install writes `{ide}/rules/{practice}/{fidelity}.mdc` (`.md` scoped by `paths` for Claude Code), which the IDE applies by path.

------
----

## DataField : Annotation

`@data_field` under `@property`: the property is part of the object's data, in every tool answer and in the language adapter's types; `key=` names it in the data when it differs from the property, and `reference=True` sends the object it returns by its identity alone.

------
----
+ annotate(getter: Any): Any

## Identity : NamesAnnotation

`@identity("field", ...)` on a class: the data fields that name one object, which a language adapter passes to the class's `@tool_subject` loader.

+ Identity(*fields)
------
----

## LanguageAdapter : Annotation

`@language_adapter(language="typescript")` on a toolset: install generates typed code in `{ide}/language-adapters/typescript/` that reaches the toolset's MCP operations from outside Python; `shares_file_views=True` marks the toolset whose client the shared file views read files through.

+ LanguageAdapter(language: str, shares_file_views: bool = False)
------
+ language: str
+ shares_file_views: bool
----
+ annotate(toolset: Any): Any
