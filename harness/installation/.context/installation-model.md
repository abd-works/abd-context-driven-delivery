# harness/installation

The *Installer* publishes every annotated member of a repository's toolsets into one IDE folder, through an *Installation* for each channel laid out by its *IdeLayout*, then starts the servers its *ServerInstallation* channels point at; *RepositoryToolsets* finds every toolset a repository defines. The module also reads and writes a project's CDD configuration files (*ContextConfig*, *JsonFile*, *AppPorts*) and holds the annotations that say what an object's data is.

- **Purpose:** Install one repository into one IDE folder through every channel, from one walk of the repository, and start the servers that install points at; give every channel the annotations, the data, and the writer it publishes a member with.
- **Seam (terms):** Installer, InstallDiagnostics, Installation, ServerInstallation, FileInstallation, SkippedTool, SkippedTools, IdeLayout, RepositoryToolsets, ContextConfig, JsonFile, JsonFileUnreadable, AppPorts, SourceFile, DataClass, NamedDestination, Skill, Command, Rules, DataField, Identity, LanguageAdapter; `data_of`, `CONTEXT_FOLDER`, `is_temporary`
- **Dependencies (one-way):** harness/annotations, harness/agent_tools, harness/markdown

## Installer

Publish every annotated member of the toolsets a repository defines into one IDE folder, through the installation of each channel its annotations name, then start the servers the installed files point at. harness/mcp and harness/hooks register their server installations with `SERVER_CHANNELS` when they are imported, so this module imports neither.

+ Installer(ide: str | None = None, path: str | Path | None = None, repo: str | Path)
------
+ repo: Path
+ ide: str
+ << composition >> layout: IdeLayout
+ path: Path
+ record: InstallRecord
+ << composition >> diagnostics: InstallDiagnostics
+ << composition >> toolsets: RepositoryToolsets
+ << composition >> deployment: Deployment
----
+ load(project: Path | str): Installer
+ clean(): list[str]
+ install(toolsets: Iterable[Any] | None = None, replace: bool = True): Any
+ install_latest(): int
+ diagnose_install(): str
+ diagnose_instructions(): str
---<<reads toolsets with>>--> RepositoryToolsets
---<<writes sections with>>--> InstallDiagnostics
---<<annotated with>>--> NoCatalog

## Deployment

One installer's publishing of the repository's toolsets into its IDE folder: a run writes every channel's files, saves the install record, stands each server up and diagnoses what it wrote.

+ Deployment(installer: Installer)
------
+ << composition >> channels: InstallChannels
+ diagnosis: list[str]
----
+ run(toolsets: Iterable[ToolsetConfiguration] | None, replace: bool): InstallChannels
+ install_self(replace: bool = False): InstallChannels
+ write_language_adapters(): list[Path]
+ ensure_runtimes(): dict[str, str]
+ diagnose_after_install(): list[str]
---<<loads>>--> AgentToolSet
---<<reads destinations of>>--> AgentTool
---<<creates one of each registered>>--> ServerInstallation
---<<reads the names of>>--> InvokeLine
---<<raises>>--> ToolsetInstallFailed

## ServerChannels

The kinds of server installation every install publishes through; the process keeps one, `SERVER_CHANNELS`.

+ ServerChannels()
------
+ kinds: list[type[ServerInstallation]]
----
+ register(kind: type[ServerInstallation]): None
---<<raises>>--> ServersNotRegistered

## InstallDiagnostics

`diagnostics.json` in one IDE folder: each install appends what it deployed on every channel, coloured by how much changed since the last install, and the diagnostics probes write their own sections beside that history.

+ InstallDiagnostics(folder: Path, layout: IdeLayout)
------
+ folder: Path
+ path: Path
----
+ channels_in_folder(toolsets: list[str], published: dict[str, list[str]]): dict[str, list[str]]
+ deployed(channels: InstallChannels): dict[str, list[str]]
+ diagnosed(channels: InstallChannels): tuple[str, str]
+ record_run(channels: InstallChannels, report: str): None
+ compared(actual: dict[str, list[str]]): tuple[str, str]
+ record_install(actual: dict[str, list[str]], report: str, color: str): None
+ write_section(section: str, results: dict[str, Any]): None
+ installed_items(channel: str): list[str]
---<<reads and writes through>>--> JsonFile

## Installation

Write one channel for one IDE, made with the install's *IdeLayout*; each channel overrides `write`.

+ Installation(layout: IdeLayout, path: Path | str, repo: Path | str | None = None)
------
+ channel: str
+ << association >> layout: IdeLayout
+ path: Path
+ repo: Path | None
+ << composition >> repository: RepositoryToolsets
+ is_temporary: bool
----
+ track_writes_with(tracker: InstallTracker): None
+ track_write(dest: Path): None
+ folder_for(toolset: Any): Path
+ install(tool: Any): None
+ write(tool: Any): None

## ServerInstallation : Installation

An installation whose files point the IDE at a server process: the MCP entry at the cdd server, the hook entries at the hook server. Beside writing its files it stands that server up to check it loads, starts it, and reports it.

------
+ toolsets: tuple[type, ...]
+ published: list[str]
----
+ create(layout: IdeLayout, path: Path | str, repo: Path | str | None = None): ServerInstallation
+ accepts(tool: Any): bool
+ standup(): Any
+ diagnose(): dict[str, Any]
+ ensure_running(): dict[str, str]
+ status(): list[str]
+ serves_this_process(): bool

## FileInstallation : Installation

Write the markdown files of one channel — skills, slash commands, or rules — where the IDE reads them.

+ FileInstallation(layout: IdeLayout, path: Path | str, channel: FileChannel = FileChannel(), repo: Path | str | None = None)
------
+ channel: FileChannel
----
+ relative_path(toolset: Any, name: str): Path
+ write(tool: AgentTool): None
+ write_standing_rule(source: Path): None
---<<calls invoke_line on>>--> AgentTool
---<<creates>>--> FrontMatter
---<<reads constants of>>--> InstallDestination
---<<creates>>--> Name
---<<writes the SKILL.md for>>--> Skill
---<<writes the slash command for>>--> Command
---<<writes the rules file for>>--> Rules

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
---<<raises>>--> JsonFileUnreadable

## JsonFileUnreadable : ValueError

A JSON file holds something other than a JSON object. Nothing is written over it, so what it holds stays for a person to repair; each owner raises its own kind.

+ JsonFileUnreadable(path: Path, cause: Exception)
------
+ path: Path
+ cause: Exception
----
+ message(path: Path, cause: Exception): str

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
