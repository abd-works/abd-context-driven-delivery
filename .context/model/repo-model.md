**Repository model**

The public seam of every module in this repository, one section per module, grouped harness, space, tools, then cdd_guidance, and lowest layer first within each group: the classes another module's production code imports, with the operations and properties those classes have in the code today, their base classes, and how they relate. Each module's own card (`{module}/.context/module-context.md`) says why a caller uses it and what the caller must honor; this document shows the shape of the types behind those cards. `.context/model/repo-model.drawio` is the same model rendered by the Clean Engineering practice.

Dependencies list the modules a module's production code imports today. One runs against the layering, and is named so no reader takes it for one-way: space/session imports cdd_guidance/actions (its diagnostics run generate and validate). space/kanban's story-test support (`session_board_tiers.py`, `session_board_examples.py`) imports cdd_guidance/actions too, but its production code does not. No module imports another that imports it.

# harness/annotations

An *Annotation* is what an author types on a class or operation to say how CDD treats it; a *Destination* is an annotation that says where a member is published, and an *OmissionAnnotation* leaves a member out. Each publisher defines its own destinations (harness/installation, harness/mcp, harness/hooks), and every kind joins one registry, `annotation_kinds`, as it is defined. *Name* is one name written in every case CDD needs: `StoryMap`, `story_map`, and `story-map` are the same *Name*. `class_folder(cls)` is the folder a class is defined in.

- **Purpose:** Hold the annotations an author types, the one place a member's destinations are read, and the one way a name is written in each case, below every publisher, so publishers depend on toolsets and never the other way round.
- **Seam (terms):** Annotation, OmissionAnnotation, HostedOnly (`@hosted_only`), Destination, NamedDestination, NamesAnnotation, Toast, Name, `annotation_kinds`, `class_folder`
- **Dependencies (one-way):** *(none)*

## Annotation

The base of every annotation an author types: it sets its `flag` on what it annotates, and `annotates(target)` reads it back. Each kind joins `annotation_kinds` as it is defined.

------
+ flag: str
+ copied: bool
----
+ annotates(target: Any): bool
+ written_as(): str
+ installs_member(): bool
+ companion_flags(): tuple[str, ...]
+ annotate(target: Any): Any

## NamesAnnotation : Annotation

An annotation that records a tuple of names on what it annotates and reads them back: the fields that name one object (`@identity`) and the arguments a tool takes from its call (*TakesFromCall*) are its kinds, each naming only its flag.

+ NamesAnnotation(*names: str)
------
----
+ annotate(target: Any): Any
+ names_on(target: Any): tuple[str, ...]

## OmissionAnnotation : Annotation

The base of an annotation that leaves what it annotates out of something: the catalog (`@noCatalog`) or every destination (`@noDeploy`).

------
+ omits_install: bool
----
+ annotates(target: Any): bool

## HostedOnly : OmissionAnnotation

`@hosted_only` on a class whose tools run only through the practice or toolset that holds it, such as a practice's rules or its fidelities: install and the hook server load no toolset of it on its own. It is read on the class it was written on, never inherited, so each practice that subclasses one stays a toolset.

------
----
+ annotates(target: Any): bool

## Destination : Annotation

The base of an annotation that says where install publishes a member, by its `channel`: a skill, a command, a rules file, an MCP tool, or a hook.

------
+ channel: str
+ enlists_member: bool
----
+ name_annotated_on(operation: Any): str
+ disabled_on(operation: Any): bool

## NamedDestination : Destination

A destination whose annotation may name what it installs: `@skill("name")`, `@command(name="name")`, or bare `@skill` for the operation's own name.

------
----

## Toast : Destination

`@Toast` on an operation or instructions: nothing is written at install; the prompt notifier shows a toast naming the operation when an agent calls it.

------
----

## Name

*Name* is one name, such as a class, an event, or a fidelity, that CDD writes in several cases: `StoryMap`, `story_map`, and `story-map` are the same name, and so are a title's words (`Pet visits`, `pet-visits`, `PetVisits`).

+ Name(text: str)
------
+ words: list[str]
+ snake: str
+ kebab: str
+ camel: str
+ spellings: list[str]
+ title_words: list[str]
+ title_slug: str
+ title_snake: str
+ title_pascal: str
+ title_camel: str
----

# harness/process

*BackgroundStart* and *PythonInterpreter* start a server without a console window, *StoppableProcess* ends one by its id, *ExclusivePort* is the one port a server may hold, and *Git* runs every git command in one folder with the same time limits and errors.

- **Purpose:** Start, name, and stop the processes the framework keeps, and run git, the same way on Windows and elsewhere.
- **Seam (terms):** BackgroundStart, PythonInterpreter, ExclusivePort, ListeningPorts, RunningProcess, StoppableProcess, ProcessNotStopped, Git, RepoConnectError
- **Dependencies (one-way):** *(none)*

## BackgroundStart

How a background server is started so it keeps running without a console window.

+ BackgroundStart(breaks_away: bool = True)
------
+ breaks_away: bool
+ creationflags: int
+ startupinfo: subprocess.STARTUPINFO | None
----
+ inside_starters_job(): BackgroundStart
+ run(command: list[str], cwd: str | Path, env: dict[str, str], log: IO[str]): subprocess.Popen

## RunningProcess

A process by its id, to ask whether it is still running.

+ RunningProcess(pid: int)
------
+ pid: int
+ alive: bool
----

## StoppableProcess : RunningProcess

A process by its id that this one may end, such as the server an address file names.

------
----
+ stop(wait_seconds: float): None
	// never signals an id of 0 or this process's own id, so a blank or stale address file cannot end the process that reads it
---<<raises>>--> ProcessNotStopped

## ProcessNotStopped : Exception

A process was asked to stop and is still running.

+ ProcessNotStopped(pid: int, cause: BaseException | None = None)
------
+ pid: int
+ cause: BaseException | None
----

## ExclusivePort

The one port a long-running server of this computer may listen on, claimed by an exclusive bind: two servers cannot both hold one port, and no lock file can promise that once its holder is killed without cleanup.

+ ExclusivePort(host: str, port: int)
------
+ host: str
+ port: int
----
+ claim(): socket.socket | None
+ holder(): StoppableProcess | None
---<<asks the holder of its port>>--> ListeningPorts
---<<names its holder as>>--> StoppableProcess

## ListeningPorts

Which process on this computer listens on which TCP port, as `netstat -ano` (Windows) or `ss -ltnp` (elsewhere) reports it now; `scripts/instances.py` reads it too.

------
----
+ by_process(): dict[int, list[int]]
+ holder(port: int): StoppableProcess | None
---<<creates>>--> StoppableProcess

## PythonInterpreter

One Python on this computer.

+ PythonInterpreter(executable: str | Path | None = None)
------
+ executable: Path
+ windowless: str
+ console: str
----

## Git

The git command line, run in one folder.

+ Git(folder: Path | str)
------
+ folder: Path
----
+ run(*args: str, env: dict[str, str] | None = None, timeout: float | None = None): str
	// every repository operation goes through run, so the time limit, the stop of a hung git, and the RepoConnectError a failure raises are the same for all of them
+ succeeds(*args: str): bool
---<<raises>>--> RepoConnectError

## RepoConnectError : RuntimeError

Raised when git cannot be run, or a git command fails, in a clone.

------
----

# harness/markdown

*Markdown* is the prose a property loads from a folder, file, or section beside its class, located once from the *MarkdownScope* its owner hands over; *MarkdownText* reads a document's headings and sections; *Format* names the channel an artifact is written in. The whole model of this module, internals included, is `harness/markdown/.context/markdown-collection-model.md`; that document is canonical, and this section shows only the classes other modules use.

- **Purpose:** Let a class keep its words in markdown beside it, read them back typed, and convert them to HTML.
- **Seam (terms):** Markdown, MarkdownScope, MarkdownCollection, MarkdownText, OperationProperty, FrontMatter, Format; the annotations `@markdown` and `@markdownCollection`
- **Dependencies (one-way):** harness/annotations

## Markdown

The prose one property loads: the folder or file named after the property, or the section titled after it, located once and read once.

+ Markdown(instance: Any, label: str, fidelity: str | None = None, format: str | None = None)
------
+ location: AssetLocation
+ document: MarkdownText
----
+ from_label(instance: Any, label: str, fidelity: str | None = None, format: str | None = None): Markdown
+ held_by(owner: Any, label: str): Markdown
	// one Markdown per label and scope, kept on the owner, so a second read answers from the text the first found
+ extract(): str
+ expand_docstring(docstring: str | None): str
+ html(): HTML
+ coerce(text: str, return_type: Any): Any
+ built_by(from_markdown: Callable[..., Any], text: str, parent: Any): Any
+ read_into(return_type: Any, build: Callable[..., Any] | None = None): Any
+ return_type_of(fn: Callable[..., Any], default: Any): Any
---<<locates its section from>>--> MarkdownScope
---<<reads sections with>>--> MarkdownText
---<<reads template folders of>>--> Format
---<<creates>>--> Name

## MarkdownScope

Where an owner keeps its markdown and which part of it the owner reads: the folder beside its class, the slug its `{slug}.md` is named by, and the fidelity and format whose templates and examples it reads. An owner that knows these hands them over as its `markdown_scope` property.

+ MarkdownScope(folder: Path, slug: str, fidelity: str | None = None, format: str | None = None, in_fidelity_block: bool = False)
------
+ folder: Path
+ slug: str
+ fidelity: str | None
+ format: str | None
+ in_fidelity_block: bool
----
+ beside(owner_class: type): MarkdownScope
+ of(owner: Any): MarkdownScope
+ at(fidelity: str | None = None, format: str | None = None): MarkdownScope

## MarkdownCollection

Listed or keyed extracts that keep the original markdown. `@markdownCollection` annotates the property that holds one.

+ MarkdownCollection(entries: dict[str, Any] | list[Any] | None = None, parent: Any = None)
------
+ entries: dict[str, Any] | list[Any]
+ parent: Any
+ markdown: str
----
+ child(name: str, body: str = ''): Any
+ from_markdown(text: str, parent: Any = None): MarkdownCollection
+ from_section(markdown: Markdown, return_type: Any, parent: Any = None): Any
+ attach(instance: Any, name: str | None = None): None
---<<calls built_by on>>--> Markdown
---<<creates>>--> MarkdownText
---<<annotated with>>--> HostedOnly

## MarkdownText

A markdown document: headings, slices, and child sections.

+ MarkdownText(text: str)
------
+ text: str
+ yaml_fields: dict[str, Any]
+ without_yaml: str
----
+ headings(): list[tuple[int, int, int, str]]
+ slice_heading(heading: str): str
+ child_blocks(parent_heading: str): list[tuple[str, str]]
+ section_child_blocks(): list[tuple[str, str]]
+ fidelity_blocks(): list[tuple[str, str]]
+ fidelity_block(fidelity_name: str): str
+ named_subsection(heading: str): str

## OperationProperty

A property made from an operation whose body is empty: its value comes from the reader it is given, and it carries the operation's name, docstring, and annotations, so it installs the way the operation would. `@markdown`, `@markdownCollection`, and `@collect` all build their properties with it.

+ OperationProperty(operation: Callable[..., Any])
------
----
+ reading(read: Callable[[Any], Any]): property

## FrontMatter

The settings at the top of a file: a YAML block between `---` lines, or, in a code template, the same block written as `# ---` comment lines.

+ FrontMatter(text: str)
------
+ text: str
+ settings: str
+ fields: dict[str, str]
+ content: str
----
+ of_file(path: Path): FrontMatter

## Format

*Format* is a channel an artifact is written in, such as `markdown`, `python`, or `drawio`.

+ Format(name: str | None)
------
+ name: str
+ short: str
+ extension: str
+ is_code: bool
+ group: str
+ group_order: int
+ file_order: int
+ is_templated: bool
+ template_folder: str
+ template_extension: str
----
+ from_extension(extension: str): Format

# harness/agent_tools

An *AgentToolSet* is an ordinary class an agent can list and run: each `@agent_tool` member is an *AgentOperation* and each `@agent_instructions` member is *AgentInstructions*. A *ToolCall* is one call as a chat made it, with its project and chat. The whole model of this module, internals included, is `harness/agent_tools/.context/agent-tools-model.md`; that document is canonical, and this section shows only the classes other modules use.

- **Purpose:** Let an author publish an ordinary class as operations and instructions an agent can list and use, and let every publisher read those members from one place.
- **Seam (terms):** AgentToolSet, ToolSetCollection, ToolsetMembers, ToolsetReference, AgentTool, AgentOperation, AgentInstructions, InstallDestination, AgentToolAnnotation, AgentInstructionsAnnotation, AgentToolSetAnnotation, ToolSetCollectionAnnotation, Collect, ToolSubject, OnSubject, TakesFromCall, NoSessionLog, PublishedWhereHeld, SubAgentAnnotation, ToolSubjectLoader, RecipePlaceholders, ToolCall, ChatPointer; `tools(...)`, `instructions(...)`, `report_progress`, `reporting_to`, `NO_CHAT`, `SUB_AGENT_CALLER_PREAMBLE`
- **Dependencies (one-way):** harness/annotations, harness/markdown

## AgentToolSet : AgentToolSetOrigin

Injected by @agent_toolset — the operations, instructions, and nested collections of one toolset as the tools it publishes.

------
+ name: str
+ slug: str
+ registration_name: str
+ install_folder: Path
+ description: str
+ parameter_notes: dict[str, str]
+ mode: ExpansionMode
+ toolset_collections: list[Any]
+ << composition >> operations: dict[str, AgentOperation]
+ << composition >> instructions: Mapping[str, AgentInstructions]
+ << composition >> tools: dict[str, AgentTool]
+ is_part_of_practice: bool
+ is_served_on_mcp: bool
+ operation_type: type[AgentOperation]
----
+ instantiate(toolset: Any = None): Any
+ from_items(items: list[Any], context: dict[str, object] | None = None): list[Any]
+ child_toolsets(): None
+ instruction(name: str): AgentInstructions
+ tools_for(destination: str): list[AgentTool]
+ for_call(call: ToolCall): Any
+ session_for(call: ToolCall): Any
---<<creates>>--> AgentInstructions
---<<creates>>--> AgentOperation
---<<keeps>>--> AgentTool
---<<reads its members through>>--> ToolsetMembers
---<<reads session of>>--> ToolCall
---<<loads the prose it needs through>>--> Markdown
---<<creates>>--> Name

## ToolSetCollection : AgentToolSetOrigin

Named child toolsets, iterated in the order they were added; the collection itself may have tools, and it is named and found the way a toolset is.

+ ToolSetCollection(entries: dict[str, Any] | None = None, parent: Any = None)
------
+ entries: dict[str, Any]
+ parent: Any
+ tools: dict[str, AgentTool]
----
+ attach(instance: Any, name: str | None = None): None

## ToolsetMembers

The members of one toolset class and which of them its annotations make tools, held by the class and walked once.

+ ToolsetMembers(owner: type)
------
+ every: list[tuple[str, Any]]
+ annotated: list[tuple[str, Any]]
+ tool_names: set[str]
+ instruction_names: frozenset[str]
+ << composition >> subject_loader: ToolSubjectLoader
+ toolset_collection_names: list[str]
+ collection_names: list[str]
----
+ of(owner: type): ToolsetMembers
+ is_tool(member: Any): bool
+ is_rules(member: Any): bool
+ collections_on(instance: Any): list[tuple[str, Any]]
+ declared(name: str): Any
+ callable_on(instance: Any, name: str, member: Any): Any
---<<reads the annotation>>--> AgentToolAnnotation
---<<reads the annotation>>--> AgentInstructionsAnnotation
---<<reads the annotation>>--> ToolSetCollectionAnnotation

## ToolsetReference

A toolset named `module:Class`, the one way such a reference is written and read back; a module in a hyphenated folder is found under the folders on the import path.

+ ToolsetReference(reference: str)
------
+ module_name: str
+ toolset_class: type
----
+ of(toolset_class: type): ToolsetReference
+ in_module(module: str, class_name: str): ToolsetReference
+ module_file(): Path

## AgentTool : AgentToolDestination

One published member of a toolset: its name in every channel, its input schema, and how a call is answered.

------
+ name: str
+ callable: Callable[..., Any]
+ toolset: AgentToolSet
+ slug: str
+ registration_name: str
+ deploy_name: str
+ mcp_name: str
+ parameter_schema: ParameterSchema
+ input_schema: dict[str, Any]
+ destinations: list[str]
+ hook_event: str
+ kind: str
+ docstring: str
+ description: str
----
+ invoked_names(text: str): list[str]
+ is_invoke_line(line: str): bool
+ spelled(name: str): str
+ is_called(called: str): bool
+ install_to(destination: str): bool
+ invoke_line(): str
+ invoke(arguments: dict[str, Any] | None = None, project: Path | str | None = None): Any
+ answer(call: ToolCall): Any
+ on(toolset: Any): AgentTool
+ should_log_session_invocation(arguments: dict[str, Any] | None): bool
+ log_session_invocation(call: ToolCall): None
---<<loads>>--> AgentToolSet
---<<calls session_for on>>--> AgentToolSet
---<<reads constants of>>--> InstallDestination
---<<asks whether its channel publishes it>>--> Destination
---<<loads the prose it needs through>>--> Markdown
---<<creates>>--> ToolCall
---<<keeps out of the session log the calls annotated>>--> NoSessionLog
---<<prepends the sub-agent hand-off for>>--> SubAgentAnnotation
---<<hands the project or call to callables annotated>>--> TakesFromCall

## AgentOperation : AgentTool

An `@agent_tool` member: an operation an agent calls and gets a result from.

------
+ kind: str
----

## AgentInstructions : AgentTool

An `@agent_instructions` operation: its recipe body, expanded for a call, is the instructions an agent follows.

------
+ kind: str
+ prompt: tuple[str, ...]
+ tools: list[str]
+ recipe_source: RecipeSource
----
+ for_callable(callable: Callable[..., Any], toolset: AgentToolSet): AgentInstructions
+ answer(call: ToolCall): str
+ expand(arguments: dict[str, Any]): ExpansionResult
+ members_of(target: Any): ToolsetMembers
+ member_of(target: AgentToolSet, member: str): AgentInstructions
+ provider_of(owner: Any, provider_name: str): Any
+ parent_recipe(after_class: type | None = None): tuple[AgentInstructions, type] | None
---<<reads members of>>--> ToolsetMembers
---<<fills placeholders with>>--> RecipePlaceholders
---<<reads arguments of>>--> ToolCall

## AgentToolAnnotation : Annotation

`@agent_tool` on a method: an operation an agent calls and gets a result from; its description is the docstring.

------
----
+ installs_member(): bool

## AgentInstructionsAnnotation : Annotation

`@agent_instructions` on a method: instructions an agent reads; the body runs when they are expanded.

------
----
+ installs_member(): bool

## AgentToolSetAnnotation : _ClassJoiningAnnotation

`@agent_toolset` on a class: makes, in its place, a class of the same name that also derives from AgentToolSet, so the class reads as its own domain first.

------
----
+ annotate(toolset_class: type): type
---<<joins the annotated class with>>--> AgentToolSet

## ToolSetCollectionAnnotation : _ClassJoiningAnnotation

`@toolset_collection` on a class or property: the class is a ToolSetCollection, or the property is one of the toolset's collections.

------
----
+ annotate(target: Any): Any
---<<joins the annotated class with>>--> ToolSetCollection

## Collect

`@collect` on a collection's property: answers the same-named property of the collection's children, joined as text or bundled into the property's declared return type.

------
----
+ of(collection: Any): Any
---<<builds its property with>>--> OperationProperty

## InstallDestination

The channels a member is published to, in the order a tool lists them.

------
+ MCP: str
+ HOOK: str
+ SKILL: str
+ COMMAND: str
+ RULE: str
+ LISTED: tuple[str, ...]
----

## ToolSubject : Annotation

`@tool_subject` on the classmethod that loads the object a tool call acts on, so `@agent_tool` can sit on a domain class whose constructor takes collaborators.

------
----

## OnSubject : Annotation

Set by the framework, never typed: the tool made from an instance operation of a `@tool_subject` class loads its object from its leading arguments.

------
----

## TakesFromCall : NamesAnnotation

Set by the framework, never typed: the tool's callable takes the project its ToolCall names, or the call itself, which no caller passes.

------
----

## NoSessionLog : Annotation

`@noSessionLog` on an operation: its calls stay out of the session log, for reads an agent or a mod repeats often.

------
----

## PublishedWhereHeld : Annotation

`@published_where_held` on a collection's tool: only the toolset holding the collection itself publishes it, as a practice publishes its shared rules' injection and not each fidelity's again.

------
----

## SubAgentAnnotation : Annotation

`@subAgent` on an `@agent_tool` or `@agent_instructions` member: its description starts with the hand-off to a non-blocking background sub-agent.

------
----
+ with_hand_off(text: str): str

## ToolSubjectLoader

How a domain class marked `@agent_toolset` finds the object a tool call acts on: its `@tool_subject` classmethod.

+ ToolSubjectLoader(toolset_class: type)
------
+ loader: Callable[..., Any] | None
----
+ on_subject(load: Callable[..., Any], operation: Callable[..., Any]): Callable[..., Any]
+ given_the_call(operation: Any): Any
---<<reads the loader annotated>>--> ToolSubject
---<<annotates the tools it makes with>>--> OnSubject
---<<annotates the tools it makes with>>--> TakesFromCall

## RecipePlaceholders

One call's values for a recipe's placeholders: `{{name}}` takes the argument of a parameter the recipe declares, and `{{self.attribute}}` takes the attribute of the toolset the call runs on.

+ RecipePlaceholders(arguments: dict[str, Any], parameter_names: set[str], toolset: Any = None)
------
----
+ filled(template: str): str

## ToolCall

One call of a tool as its caller made it: the arguments it sent, the folder of the project the calling chat works on, and that chat.

+ ToolCall(arguments: dict[str, Any] | None = None, project: Path | str | None = None, chat: ChatPointer | None = None, tool: str = '', mcp_host: Any = None, answers_a_chat: bool = False)
------
+ arguments: dict[str, Any]
+ project: Path
+ << association >> chat: ChatPointer | None
+ chat_id: str
+ tool: str
+ mcp_host: Any
+ answers_a_chat: bool
+ identity: str
+ named_paths: list[str]
+ session: Any
	// the session open in this call's own project, never the one the process worked on last; a call that names no project works in no session
----
+ sent(arguments: dict[str, Any] | None, project: Path | str | None, tool: str = '', mcp_host: Any = None, answers_a_chat: bool = False): ToolCall
+ answering(): ToolCall | None
+ being_answered(): Iterator[ToolCall]
+ open_sessions_with(opener: SessionOpener): None
+ session_in(project: Path | str): Any
+ session_named(session_file: str): Any
---<<takes the chat out of the arguments with>>--> ChatPointer
---<<opens sessions through>>--> SessionOpener
---<<raises>>--> SessionsNotLoaded

## ChatPointer

Which chat a tool call, and the session.log line it writes, came from, so `read_loop` can put that chat's words back under the line. `NO_CHAT` is the pointer of a call that came from no chat.

+ ChatPointer(id: str, transcript: Path | None = None, lines: str = '')
------
+ id: str
+ transcript: Path | None
+ lines: str
+ working_folder: Path | None
+ is_missing: bool
+ line_range: tuple[int, int]
----
+ of(chat_id: str, transcript: str | Path | None, lines: str = ''): ChatPointer | None
+ taken_from(arguments: dict[str, object] | None): tuple[ChatPointer | None, dict[str, object]]
+ from_claude_chat(chat_id: str): ChatPointer | None
+ from_claude_session(chat_id: str): ChatPointer | None
+ in_log_line(line: str): ChatPointer | None
+ transcript_text(): list[str]

# harness/installation

The *Installer* publishes every annotated member of a repository's toolsets into one IDE folder, through an *Installation* for each channel laid out by its *IdeLayout*, then starts the servers its *ServerInstallation* channels point at; *RepositoryToolsets* finds every toolset a repository defines. The module also reads and writes a project's CDD configuration files (*ContextConfig*, *JsonFile*, *AppPorts*) and holds the annotations that say what an object's data is.

- **Purpose:** Install one repository into one IDE folder through every channel, from one walk of the repository, and start the servers that install points at; give every channel the annotations, the data, and the writer it publishes a member with.
- **Seam (terms):** Installer, InstallDiagnostics, Installation, ServerInstallation, FileInstallation, SkippedTool, SkippedTools, IdeLayout, RepositoryToolsets, ContextConfig, JsonFile, JsonFileUnreadable, AppPorts, SourceFile, DataClass, Skill, Command, Rules, NoCatalog, NoDeploy, DataField, Identity, LanguageAdapter; `data_of`, `CONTEXT_FOLDER`, `is_temporary`
- **Dependencies (one-way):** harness/annotations, harness/agent_tools, harness/markdown

## Installer

Publish every annotated member of the toolsets a repository defines into one IDE folder, through the installation of each channel its annotations name, then start the servers the installed files point at. harness/mcp and harness/hooks register their server installations with `installs_through` when they are imported, so this module imports neither.

+ Installer(ide: str | None = None, path: str | Path | None = None, repo: str | Path)
------
+ repo: Path
+ ide: str
+ << composition >> layout: IdeLayout
+ path: Path
+ record: InstallRecord
+ << composition >> diagnostics: InstallDiagnostics
+ << composition >> toolsets: RepositoryToolsets
+ diagnosis: list[str]
----
+ installs_through(kind: type[ServerInstallation]): None
+ load(project: Path | str): Installer
+ track(installation: Installation): None
+ clean(): list[str]
+ install(toolsets: Iterable[Any] | None = None, replace: bool = True): Any
+ install_self(replace: bool = False): InstallChannels
+ ensure_runtimes(): dict[str, str]
+ diagnose_after_install(): list[str]
+ diagnose_install(): str
+ install_instructions(): str
+ clean_instructions(): str
+ diagnose_install_instructions(): str
+ runtime_instructions(): str
+ diagnose_instructions(): str
---<<loads>>--> AgentToolSet
---<<reads destinations of>>--> AgentTool
---<<creates>>--> FileInstallation
---<<creates one of each registered>>--> ServerInstallation
---<<tracks writes with>>--> Installation
---<<creates>>--> IdeLayout
---<<reads toolsets with>>--> RepositoryToolsets
---<<writes sections with>>--> InstallDiagnostics
---<<raises>>--> ServersNotRegistered
---<<raises>>--> ToolsetInstallFailed
---<<annotated with>>--> NoCatalog

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
+ accepts(tool: Any): bool
+ standup(): Any
+ diagnose(): dict[str, Any]
+ ensure_running(): dict[str, str]
+ status(): list[str]
+ serves_this_process(): bool

## FileInstallation : Installation

Write the markdown files of one channel — skills, slash commands, or rules — where the IDE reads them.

+ FileInstallation(layout: IdeLayout, path: Path | str, destination: str = '', mcp_mode: bool = False, repo: Path | str | None = None)
------
+ destination: str
+ mcp_mode: bool
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
+ installed_guidance_kind(path: str): str

## RepositoryToolsets

*RepositoryToolsets* finds every toolset class in one repository by reading its source, without importing it, and puts the folders that load those classes on the import path.

+ RepositoryToolsets(root: Path | str)
------
+ GUIDANCE_FOLDER: str
+ IMPORT_FOLDERS: tuple[str, ...]
+ root: Path
+ unloadable: list[ToolsetUnloadable]
+ agents_folder: Path
+ standing_rules_folder: Path
+ references_folder: Path
----
+ of_running_checkout(): RepositoryToolsets
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

## NoCatalog : OmissionAnnotation

`@noCatalog` on a class or operation: the catalog leaves it out; install still publishes it.

------
----

## NoDeploy : OmissionAnnotation

`@noDeploy` on an operation: install publishes it to no destination, whatever else annotates it; the catalog can still list it.

------
+ omits_install: bool
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

# harness/hooks

A *Hook* annotation makes a member answer an IDE event; the *HookServer* of a checkout runs every enabled hook for a *HookPayload* and merges their *HookResult*, and the *HookDaemon* keeps that server running. *HookInstallation* is the hook channel's server installation, registered with the Installer when the package is imported. The whole model of this module, internals included, is `harness/hooks/.context/hooks-runtime-model.md`; that document is canonical, and this section shows only the classes other modules use.

- **Purpose:** Let a toolset member answer IDE events, through one hook server per checkout that runs every hooked member and merges their answers.
- **Seam (terms):** Hook, Hooks, HookPayload, HookResult, HookServer, HookDaemon, HookInstallation; `rules_toast`, `TOAST_ARROW`
- **Dependencies (one-way):** harness/annotations, harness/agent_tools, harness/installation, harness/process

## Hook : Destination

`@hook("event")` on an operation: install adds the hook command for that IDE event to `{ide}/hooks.json` and lists the operation in `hook-handlers.json`; the hook server runs it when the IDE fires the event.

------
+ EVENTS: frozenset[str]
----
+ annotate(target: Any): Any
+ companion_flags(): tuple[str, ...]
+ events_served(event: str): tuple[str, ...]
+ disabled_on(operation: Any): bool

## Hooks : Annotation

`@Hooks(disabled=..., deploy=...)` on a toolset class: turns off, or keeps out of install, every hook operation the toolset has.

------
----
+ annotate(toolset_class: type): type
+ disabled_on(toolset: Any): bool
+ deploys(toolset: Any): bool

## HookPayload : Mapping[str, Any]

The fields an IDE sends on stdin for one firing of a hook, such as the tool that just ran and its input, and the tool call and session that firing works in.

+ HookPayload(fields: Mapping[str, Any], checkout: Path | None = None)
------
+ hook_event_name: str
+ conversation_id: str
+ generation_id: str
+ tool_name: str
+ tool_input: dict[str, Any]
+ workspace_roots: list[Path]
+ project: Path | None
+ << composition >> call: ToolCall
	// made once per event, so every handler of the event opens the same session
+ chat_id: str
+ session: Any
+ is_edit: bool
+ invoked_tool: str
----
+ from_stdin(raw: bytes, checkout: Path | None = None): HookPayload
+ received_in(checkout: Path): HookPayload
+ edited_path(): str
---<<creates>>--> ToolCall
---<<calls session_in on>>--> ToolCall

## HookResult

The fields a hook answers the IDE with (`permission`, `continue`, the user and agent messages, `additional_context`), and a `toast` the notifier shows; the results of every hook on one event merge into one.

+ HookResult(permission: str = 'allow', continue_flag: bool | None = None, user_message: Any = None, agent_message: Any = None, followup_message: Any = None, additional_context: Any = None, toast: Any = None)
------
+ permission: str
+ continue_flag: bool | None
+ user_message: Any
+ agent_message: Any
+ followup_message: Any
+ additional_context: Any
+ toast: Any
+ followup_only: bool
----
+ from_handler(raw: Mapping[str, Any] | None): HookResult
+ with_description(description: str): HookResult
+ merge(other: HookResult): HookResult
+ as_dict(): dict[str, Any]

## HookServer

The hooks of one checkout, loaded once: it runs the enabled handlers for each event and merges their answers.

+ HookServer(repo_root: Path, catalog: HandlerCatalog)
------
+ << composition >> skipped: SkippedTools
----
+ show_toasts_with(show: Callable[[str, list[Path]], Any]): None
+ from_repository(toolsets: RepositoryToolsets): HookServer
+ from_handlers(handlers: Path | str, repo: Path | str): HookServer
+ handle_stdin(raw: bytes): HookResult
+ dispatch(payload: HookPayload): HookResult
+ diagnose(): dict[str, Any]
---<<loads>>--> HookPayload
---<<merges>>--> HookResult
---<<runs the members annotated>>--> Hook
---<<skips the members annotated>>--> Hooks
---<<loads the toolsets of>>--> RepositoryToolsets
---<<reads which guideline applies from>>--> ContextConfig

## HookDaemon

The long-running hook server of one checkout, whichever IDE's hook command reaches it; it keeps its address, log, and start lock in the checkout's `.hook-server/` folder.

+ HookDaemon(repo: Path | str, port: int | None = None)
------
+ repo: Path
+ << composition >> toolsets: RepositoryToolsets
+ folder: Path
+ log_path: Path
+ port: int
+ source_stamp: str
----
+ live_address(): HookDaemonAddress | None
+ is_running(): bool
+ ensure(): HookDaemonAddress
	// starts the daemon, or replaces one that loaded older hook code, and answers its address
+ replace_stale(): None
+ stop(): None
+ spawn(): None
+ serve(server: HookServer | None = None): None
+ claim_port(): socket.socket | None
---<<creates>>--> BackgroundStart
---<<creates>>--> PythonInterpreter
---<<loads>>--> HookServer
---<<handles stdin>>--> HookServer
---<<claims its port with>>--> ExclusivePort
---<<creates>>--> StoppableProcess
---<<checks the lock holder is alive with>>--> RunningProcess
---<<raises>>--> HookPortTaken

## HookInstallation : ServerInstallation

Write the IDE's `hooks.json`, which runs the hook command for each event a hook operation serves, and `hook-handlers.json`, which lists those operations for the hook server; then start the checkout's hook server.

+ HookInstallation(layout: IdeLayout, path: Path | str, python: str | None = None, repo: Path | str | None = None)
------
+ << association >> server: HookServer | None
+ << composition >> daemon: HookDaemon
+ interpreter: PythonInterpreter
+ dispatch_command: str
+ handlers_file: HookHandlersFile
+ manifest: HooksManifest
+ published: list[str]
+ registered_events: list[str]
+ registered_operations: list[str]
----
+ accepts(tool: AgentTool): bool
+ write(tool: AgentTool): None
+ write_handlers(): None
+ write_hooks_manifest(): None
+ standup(): HookServer
+ ensure_running(): dict[str, str]
+ status(): list[str]
+ diagnose(): dict[str, Any]
---<<reads hook event of>>--> AgentTool
---<<loads>>--> HookServer
---<<enrolls in hooks.json>>--> Hook
---<<registers with>>--> Installer
---<<raises>>--> HookServerNotRunning

# harness/mcp

The *McpHost* is the one cdd server every chat talks to; it keeps one *McpServer* per project, and *McpInstallation* writes each IDE's `cdd` entry and starts the server from *CddHome*.

- **Purpose:** Let any chat, in any project, call the operations authors annotate `@mcp`, through one long-running server that keeps each project's toolsets apart.
- **Seam (terms):** Mcp, LongCall, McpHost, McpServer, McpInstallation, CddHome, ThrottledReporter
- **Dependencies (one-way):** harness/annotations, harness/agent_tools, harness/installation, harness/hooks, harness/process

## McpHost

The cdd server's MCP side: one *McpServer* for each project a chat works on, answering every chat.

+ McpHost(checkout_server: McpServer)
------
+ << composition >> checkout_server: McpServer
+ projects: list[Path]
----
+ server_for(project: Path): McpServer
	// one McpServer per project, so one project's toolsets never answer another project's call
+ dispatch(name: str, arguments: dict[str, object] | None = None, project: Path | None = None): object
+ answer(call: ToolCall): object
+ serve(daemon: McpDaemon, listener: socket.socket): None
+ http_app(port: int): Any
+ ping(): str
+ restart(): dict[str, Any]
+ diagnose(): dict[str, Any]
+ from_repo(repo: Path | str): McpHost
+ from_refs(toolset_refs: tuple[str, ...], repo: str | None = None, project: str | None = None): McpHost
---<<loads>>--> McpServer
---<<resolves call name>>--> McpServer
---<<creates>>--> RepositoryToolsets
---<<creates>>--> ToolCall
---<<reports progress through>>--> ThrottledReporter
---<<answers with the data of>>--> DataClass

## McpServer

The toolsets one project's calls are answered by: every `@mcp` operation of the toolsets it was started with, published under its MCP name, made for that project.

+ McpServer(repo: str | Path | None = None, project: str | Path | None = None)
------
+ repo: Path | None
+ project: Path | None
+ started: bool
+ tools: dict[str, AgentTool]
+ prompts: dict[str, AgentTool]
+ << composition >> skipped: SkippedTools
----
+ enroll(tool: AgentTool): None
+ start(toolsets: Iterable[Any]): None
+ for_project(project: Path): McpServer
+ restarted(): McpServer
+ resolve_call_name(name: str): str
+ enrolled(name: str): AgentTool | None
+ call_seconds(name: str): float
+ invoke_tool(mcp_name: str, arguments: dict[str, object] | None = None): object
+ invoke_prompt(mcp_name: str, arguments: dict[str, object] | None = None): object
+ answer_tool(mcp_name: str, call: ToolCall): object
	-> AgentTool.answer
+ answer_prompt(mcp_name: str, call: ToolCall): object
---<<keeps>>--> AgentTool
---<<loads>>--> AgentToolSet
---<<reads constants of>>--> InstallDestination
---<<reads arguments of>>--> ToolCall
---<<waits longer for operations annotated>>--> LongCall
---<<serves the operations annotated>>--> Mcp

## McpInstallation : ServerInstallation

Record `@mcp` operations, write each IDE's `cdd` entry, and start the one cdd server from `~/.cdd`; it names *CddServerHooks*, the hooks that start the server when a chat starts, as a toolset every install publishes.

+ McpInstallation(layout: IdeLayout, path: Path | str, repo: Path | str | None = None, home: CddHome | None = None)
------
+ << association >> server_home: CddHome
+ << composition >> daemon: McpDaemon
+ << composition >> claude_plugins: ClaudePlugins
+ << association >> host: McpHost | None
+ mcp_operations: list[AgentTool]
+ toolsets: tuple[type, ...]
+ published: list[str]
+ manifest_path: Path
----
+ write(tool: AgentTool): None
+ record_operation(tool: AgentTool): None
+ write_mcp_manifest(): None
+ allow_cdd_tools(settings: Path): None
+ drop_project_cdd_server(): None
+ drop_user_cdd_server(): None
+ standup(): McpHost | None
+ diagnose(): dict[str, Any]
+ ensure_running(): dict[str, str]
+ status(): list[str]
+ ensure_server(): str
+ pin_server(): str
+ keep_pinned_current(): str | None
+ serve_from_checkout(): str
+ serves_this_process(): bool
---<<keeps>>--> AgentTool
---<<creates>>--> CddHome
---<<loads>>--> McpHost
---<<publishes as a cdd MCP tool>>--> Mcp
---<<publishes the server-starting hooks with>>--> Hook
---<<registers with>>--> Installer

## CddHome

The user's cdd folder: which checkout the one server runs, the pinned copy of it, the Python it runs on, and the server's address.

+ CddHome(folder: Path | str | None = None)
------
+ folder: Path
+ state_path: Path
+ log_path: Path
+ connect_script: Path
+ claude_plugins: Path
+ runtime_record: Path
+ pinned_checkout: Path
+ is_installed: bool
+ source: Path
+ mode: str
+ interpreter: PythonInterpreter
+ install_command: list[str]
+ server_environment: dict[str, str]
----
+ write_claude_plugin(server: dict[str, object]): list[Path]
+ write_board_plugin(): None
+ is_pinned_to(checkout: Path | str): bool
+ install(checkout: Path | str, connect_script: Path | str): None
+ pin(checkout: Path | str): str
+ serve_from(checkout: Path | str): None
---<<creates>>--> Git
---<<creates>>--> PythonInterpreter
---<<takes the import path from>>--> RepositoryToolsets
---<<reads and writes through>>--> JsonFile

## ThrottledReporter

Passes a tool's progress on to its chat at most four times a second.

+ ThrottledReporter(reporter: Reporter, seconds: float = _REPORT_SECONDS)
------
----

## Mcp : Destination

`@mcp` on an operation: install publishes it as the MCP tool `{toolset}.{operation}` of the one `cdd` server, whose entry McpInstallation writes to the IDE's MCP config (`.mcp.json`, `~/.claude.json`).

------
----

## LongCall : Annotation

`@long_call` on an MCP operation: the cdd server waits `LONG_CALL_SECONDS` (600) for its answer instead of `CALL_SECONDS` (10) before telling the chat it is still running.

------
----

# harness/guidance

A *PracticeGuidance* is one practice: its *FidelityGuidance* fidelities, its *Rule* lists, templates, and examples, read from its markdown, and three parts made once (*PracticeFormats*, *PracticeReading*, *Schema*). *PracticeCatalogue* and *ActionCatalogue* are registries the practices and actions join when their packages are imported; *ApproachStage* is a stage of the approach. The whole model of this module, internals included, is `harness/guidance/.context/practice-guidance-model.md`; that document is canonical, and this section shows only the classes other modules use.

- **Purpose:** Let a practice be one class plus its markdown, with fidelities, rules, templates, and examples an agent can follow and a validator can check against.
- **Seam (terms):** Guidance, PracticeGuidance, FidelityGuidance, GuidanceCollection, SketchLens, DeclaredFile, PracticeFormats, RenderRequest, PracticeReading, Rule, RulesCollection, Schema, PracticeCatalogue, UnknownPractice, ActionCatalogue, Action, ApproachStage, StageScope; `STAGES`, `DISCOVERY`, `SPECIFICATION`, `IMPLEMENTATION`, `GENERATE`, `VALIDATE`, `RENDER`, `REVIEW`; `load_document`, `document_in`, `rules_in`
- **Dependencies (one-way):** harness/annotations, harness/agent_tools, harness/markdown, harness/installation, harness/hooks, harness/mcp

## Guidance : AgentToolSet

Words and rules an agent follows, read from markdown beside the class.

+ Guidance(format: str | None = None)
------
+ default_format: str
+ name: str | None
+ domain_slug: str | None
+ format: str | None
+ session: Any
+ module_dir: Path
+ markdown_scope: MarkdownScope
+ overview: str
+ guidance: str
+ << aggregation >> listed_rules: list[Rule]
+ sketch_template: str
+ schema: Schema
+ instructions: str
----
+ section_text(label: str): str
+ rules(): RulesCollection
+ checked_rule_collections(): list[RulesCollection]
+ checked_rules(): list[Rule]
+ checked_rules_text(): str
+ every_rule(): list[Rule]
+ templates(): str
+ rules_after_edit(payload: Any): str
+ schema_guide(): str
---<<loads the prose it needs through>>--> Markdown
---<<published as rules by>>--> Rules
---<<published as a skill by>>--> Skill
---<<published as an MCP prompt by>>--> Mcp
---<<creates>>--> Name

## PracticeGuidance : Guidance

One practice as a class plus its markdown: its identity, overview, shared rules, fidelities, templates, examples, and the set of practices it works with. It holds three parts, each made once: its formats, its part in the knowledge graph, and its schema.

+ PracticeGuidance(format: str | None = None, fidelity: str | None = None, default_workspace_folder: str = '.', formats: dict[str, Any] | None = None)
------
+ sketch_lens: SketchLens
+ SHORT_NAME: str
+ COLOUR: str
+ shows_every_fidelity: bool
+ formats_type: type[PracticeFormats]
+ reading_type: type[PracticeReading]
+ extends: str
+ << association >> extended: PracticeGuidance | None
+ << association >> companion: PracticeGuidance | None
+ default_workspace_folder: str
+ << composition >> formats: PracticeFormats
+ << composition >> reading: PracticeReading
+ format: Format
+ markdown_scope: MarkdownScope
+ document: MarkdownText
+ << composition >> schema: Schema
+ set_keys: tuple[str, ...]
+ key: str
+ practice_slug: str
+ short_name: str
+ colour: str
+ fidelity_slugs: list[str]
+ guidance: str
+ instructions: str
----
+ rules(): RulesCollection
+ checked_rule_collections(): list[RulesCollection]
+ every_rule(): list[Rule]
+ class_key(): str
+ hold_set(practices: dict[str, PracticeGuidance]): None
+ answers_to(slug: str): PracticeGuidance | FidelityGuidance | None
+ fidelity_called(name: str): FidelityGuidance | None
+ work_in(session_output: Any): None
+ generate_output(): str
+ fidelities(): GuidanceCollection
+ domain_markdown_path(): Path
+ examples(): str
+ render(format: str, content: Any = '', source: str | None = None, previous: str = ''): dict
	-> PracticeFormats.render
+ scoped_markdown(): str
---<<creates>>--> PracticeFormats
---<<creates>>--> PracticeReading
---<<creates>>--> Schema
---<<creates>>--> RenderRequest
---<<creates>>--> Format
---<<loads>>--> GuidanceCollection
---<<loads>>--> RulesCollection
---<<keeps>>--> SketchLens
---<<annotated with>>--> Identity
---<<annotated with>>--> HostedOnly

## FidelityGuidance : Guidance

One fidelity of a practice, such as the story map: its stage, its outputs, its rules, its template, and the actions that work on it.

+ FidelityGuidance(name: str = '', stage: str = '', default_format: str = '', clean_engineering: FidelityGuidance | None = None)
------
+ session_output: Any
+ judged_on: str
+ name: str
+ stage: str
+ approach_stage: ApproachStage | None
+ is_judged_on_graph: bool
+ outputs: dict[str, str | list[str]]
+ << association >> practice_guidance: PracticeGuidance | None
+ format: Format
+ default_format: Format
+ << association >> clean_engineering: FidelityGuidance | None
+ companion_instructions: str
+ slug: str
+ markdown_scope: MarkdownScope
+ module_dir: Path
+ install_folder: Path
+ scaffold: str
+ section: str
+ titled_section: str
+ examples: str
+ templates: str
+ template_file: Path | None
+ << composition >> actions: FidelityActions
+ instructions: str
----
+ apply_settings(settings: dict[str, Any]): None
+ work_in(session_output: Any): None
+ output_paths(): dict[str, list[str]]
+ files(): dict[str, list]
+ has_declared_output(): bool
+ declares(path: str, format: str = ''): bool
+ schema_guide(): str
+ rules(): RulesCollection
+ checked_rule_collections(): list[RulesCollection]
+ every_rule(): list[Rule]
+ generate_output(): str
+ render(format: str, content: Any = '', source: str | None = None, previous: str = ''): dict
+ render_files(format: str, paths: list[str] | str, source: str | None = None): dict
+ guidance_parts(): list[str]
+ templates_in(format: Format): str
+ instructions_in(format: Format): str
---<<reads its stage from>>--> ApproachStage
---<<runs actions through>>--> ActionCatalogue
---<<renders through the formats of>>--> PracticeGuidance
---<<creates>>--> RenderRequest
---<<creates>>--> Format
---<<creates>>--> MarkdownText
---<<creates>>--> Name
---<<annotated with>>--> Identity

## GuidanceCollection : MarkdownCollection, Guidance

A practice's fidelities, read from its markdown, published together, with the one it is at now (`current`).

+ GuidanceCollection(entries: dict[str, Guidance] | None = None, parent: Any = None)
------
+ << association >> current: Guidance | None
----
+ child(name: str, body: str = ''): FidelityGuidance
+ overview(): str
+ guidance(): str
+ rules(): RulesCollection
+ templates(): str
+ instructions(): str
---<<creates>>--> FidelityGuidance
---<<annotated with>>--> ToolSetCollectionAnnotation
---<<joins its children's properties with>>--> Collect

## SketchLens

A practice's section of a sketch: the headings that open it, lower case, such as `stories:`.

+ SketchLens(titles: tuple[str, ...])
------
+ titles: tuple[str, ...]
----
+ opens(title: str): bool

## DeclaredFile

A path a fidelity declares as its output, as a glob over the session's current root, so a session's output makes one for a declared path.

+ DeclaredFile(declared: str)
------
+ glob: str
+ names_one_path: bool
+ pattern: re.Pattern[str]
----

## PracticeFormats

A practice's formats, made once: each format's adapter, the format that reads a file, and the conversion of a render request into output. A practice whose formats convert in a way of their own names its own kind (`formats_type`).

+ PracticeFormats(practice: PracticeGuidance, adapters: dict[str, Any])
------
+ supported: frozenset[Format]
+ adapter_settings: dict[str, Any]
+ suffixes: frozenset[str]
----
+ check(): None
+ adapter_class(format: str): Any
+ adapter(format: str): Any
+ reading(file: Path): Format | None
+ reading_with(file: Path, others: Iterable[PracticeGuidance]): Format | None
+ for_file(file: Path): Any
+ read(paths: list[str] | str, request: RenderRequest): Any
+ render(request: RenderRequest): dict
+ parse(format: Format, content: Any): Any
+ model_for(target: Any, model: Any): Any
---<<renders>>--> RenderRequest
---<<creates>>--> Format

## RenderRequest

One render a practice's formats perform: the target format, the content and its source format, the previous output, the folder, and the fidelity it renders at.

+ RenderRequest(format: Format, content: Any, source: Format, previous: str, folder: str, fidelity: FidelityGuidance | None)
------
+ format: Format
+ content: Any
+ source: Format
+ previous: str
+ folder: str
+ << association >> fidelity: FidelityGuidance | None
+ source_format: Format
+ companion: FidelityGuidance | None
----
+ keeping_sketch_wording(): RenderRequest

## PracticeReading

A practice's part in the knowledge graph: the node types the graph treats as classes, members, or source-ordered, the practices it reads after, how it reads a working copy into its graph, and the graph rules it checks. Each practice names its kind (`reading_type`) in its `model/graph_reading.py`, so the graph never imports a practice.

+ PracticeReading(practice: PracticeGuidance)
------
+ reads_after: tuple[str, ...]
+ node_types: tuple[str, ...]
+ class_types: tuple[str, ...]
+ member_types: tuple[str, ...]
+ class_node_type: str
+ source_ordered_types: frozenset[str]
+ anchor_types: dict[str, str]
+ rule_types: dict[str, tuple[str, ...]]
+ << association >> practice: PracticeGuidance
+ graph: Any
+ in_graph: Any
+ graph_checks: dict[str, Any]
+ package: str
----
+ held_in(graph: Any, nodes: Any): None
+ read(): None
+ read_working_copy(): None
+ own_graph_checks(): dict[str, Any]
+ checks(): dict[str, Any]

## Rule

One rule a practice checks, by its slug, with its body.

+ Rule(slug: str, body: str, fidelity: str | None = None, tag: str = 'base')
------
+ fidelity: str | None
+ tag: str
+ practice: str
+ pattern: str
+ shared: bool
+ slug: str
+ body: str
----
+ validate(): str
+ from_bullet(text: str, fidelity: str | None = None): Rule
---<<creates>>--> Name

## RulesCollection : MarkdownCollection

The rules of one practice or fidelity, and the paths they apply to; a practice's rules are injected into the chat when a file they apply to is edited.

+ RulesCollection(entries: dict[str, Rule | RulesCollection] | None = None, applies_to: AppliesTo | None = None, parent: Any = None)
------
+ applies_to: AppliesTo
+ prose: str
+ injection: RuleInjection
+ practice_key: str
+ fidelity_name: str
+ owner_practice: Any
----
+ inject_rules(payload: HookPayload): dict[str, Any]
+ from_markdown(text: str, fidelity: str | None = None, parent: Any = None): RulesCollection
+ formatted(): str
+ validate(): str
+ scan(paths: Any): Any
---<<reads the annotation>>--> Hook
---<<calls edited_path on>>--> HookPayload
---<<creates>>--> MarkdownText
---<<loads>>--> Rule
---<<only its holder publishes it, annotated>>--> PublishedWhereHeld
---<<annotated with>>--> HostedOnly

## Schema

The types one schema file declares, keyed by their schema key, in the order written.

+ Schema(text: str)
------
+ types: dict[str, SchemaType]
----
+ load(path: Path): Schema
+ guide(): str
+ fidelities(): dict[str, str]
+ node_fidelities(order: list[str]): dict[str, list[str]]
+ fidelity_errors(declared: list[str]): list[str]
+ rules(): dict[str, tuple[str, ...]]

## PracticeCatalogue

Every practice CDD ships, in the order the approach walks them: Stories, DDD, UX, Clean Engineering, BDD. `cdd_guidance/practices` registers their classes when it is imported; the catalogue holds classes only, so every reader makes and holds its own practices.

------
----
+ register(*practice_classes: type[PracticeGuidance]): None
+ keys(): tuple[str, ...]
+ has(key: str): bool
+ create(key: str, **arguments): PracticeGuidance
+ create_all(**arguments): list[PracticeGuidance]
	// each practice of the new set holds the practice it extends and the Clean Engineering practice of the same set
+ practice_class(key: str): type[PracticeGuidance]
---<<creates>>--> PracticeGuidance
---<<raises>>--> UnknownPractice
---<<raises>>--> PracticesNotRegistered

## UnknownPractice : KeyError

A key names no practice the catalogue holds.

+ UnknownPractice(key: str, keys: tuple[str, ...])
------
+ key: str
----

## ActionCatalogue

Every action CDD ships: `cdd_guidance/actions` registers each action folder's toolset when it is imported, and each operation a toolset publishes as a skill is one *Action*. harness/guidance_actions registers how an action runs on a fidelity with `run_actions_with`.

------
----
+ register(*toolset_classes: type): None
+ run_actions_with(runner: ActionRunner): None
+ runner(): ActionRunner
+ fidelity_actions(): tuple[Action, ...]
+ toolsets(): tuple[type, ...]
+ actions(): tuple[Action, ...]
+ names(): tuple[str, ...]
+ has(name: str): bool
+ action(name: str): Action | None
---<<creates>>--> Action
---<<counts as actions the operations annotated>>--> Skill
---<<reads constants of>>--> InstallDestination
---<<raises>>--> ActionsNotRegistered

## Action

One action CDD ships: an operation an action toolset installs as a skill, such as generate, repair, or validate.

+ Action(name: str, toolset_class: type)
------
+ name: str
+ toolset_class: type
+ operation
+ folder: Path
----
+ run_on(fidelity: WorkedFidelity, **arguments): Any
	-> ActionRunner.run

## ApproachStage

One stage of the CDD approach: the name each fidelity's **Stage:** gives it, its title, its scope, and the actions a person runs on a fidelity in it.

+ ApproachStage(name: str, scope: StageScope)
------
+ name: str
+ title: str
+ << composition >> scope: StageScope
+ steps: list[str]
+ actions: list[str]
+ producing_actions: list[str]
+ actions_with_formats: list[str]
----

## StageScope

How much of the solution a stage's work covers, drawn as a shape that narrows and deepens along the board: Discovery takes in the whole solution wide and shallow, Implementation one story narrow and deep.

+ StageScope(shape: str, name: str, reach: str, covers: str)
------
+ shape: str
+ name: str
+ reach: str
+ covers: str
----

# harness/guidance_actions

A *GuidanceAction* is an action, such as generate, run on the guidance a call names, made for the session that call works in; it reads the `guidance` argument (*GuidanceArg*) once into its session's practice and fidelity objects.

- **Purpose:** Give every guidance action the same way to take guidance, open its session, and run once per listed guidance, so each action holds only its own words and steps.
- **Seam (terms):** GuidanceAction, GuidanceArg, GuidanceAgentOperation, UnknownGuidance, ActionWorksInNoSession
- **Dependencies (one-way):** harness/annotations, harness/agent_tools, harness/guidance, harness/hooks

## GuidanceAction

An action, such as generate, on the guidance a call names, such as stories-story-map, made for the session that call works in.

+ GuidanceAction(session: Any = None, call: ToolCall | None = None)
------
+ parameter_notes: dict[str, str]
+ injects_rules: bool
+ << association >> call: ToolCall | None
+ << composition >> work: WorkList
+ session: Any
+ log: Any
+ graph: Any
+ operation_type: type[AgentOperation]
+ practice_slugs: list[str]
+ session_context: str
----
+ for_call(call: ToolCall): GuidanceAction
	-> ToolCall.session_named
	-> made_for
+ made_for(session: Any, call: ToolCall | None = None): GuidanceAction
+ session_for(call: ToolCall): Any
+ wrote(paths: list[str | Path]): None
+ source_label(content: str = '', paths: list[str] | str | None = None): str
+ path_named(named: str | Path): Path
+ document_named(content: str = '', paths: list[str] | str | None = None): str
+ listed(): list
+ practice_of(item: Any): Any
+ fidelity_of(item: Any): Any
+ at_fidelity(item: Any): Any
+ work_on_fidelity(fidelity: FidelityGuidance, format: str = ''): None
+ each(operation: Callable[[Any], Any]): list
+ run(operation: Callable[[Any], Any], action: str = ''): list
+ log_running(action: str): None
+ as_tool(): GuidanceAction
+ rules_to_follow(): str
+ begin(guidance: GuidanceArg | None = None, action: str = ''): str
+ act_quickly(): str
+ inject_rules(payload: HookPayload): dict[str, Any]
---<<raises>>--> ActionWorksInNoSession
---<<raises>>--> UnknownGuidance
---<<instantiates every action with>>--> AgentToolSet
---<<publishes its operations as>>--> GuidanceAgentOperation
---<<calls session_named on>>--> ToolCall
---<<reads the listed practices and fidelities of>>--> PracticeGuidance
---<<asks for instructions, rules, and templates>>--> FidelityGuidance
---<<makes a set of practices with>>--> PracticeCatalogue
---<<registers its fidelity action runner with>>--> ActionCatalogue
---<<reads tool input of>>--> HookPayload
---<<injects rules on the event>>--> Hook
---<<annotated with>>--> Toast

## GuidanceAgentOperation : AgentOperation

An `@agent_tool` on a guidance action: its call is logged as the action, such as `render`, rather than as a `tool …` line.

------
----
+ log_session_invocation(call: ToolCall): None
---<<reads arguments of>>--> ToolCall

## UnknownGuidance : ValueError

A listed word no practice or fidelity has as its slug; its message lists the slugs there are.

+ UnknownGuidance(word: str, slugs: Sequence[str])
------
+ word: str
+ slugs: Sequence[str]
----

## ActionWorksInNoSession : Exception

An action made for no session, such as one listed for install, was asked for the session it works in.

+ ActionWorksInNoSession(action: str)
------
+ action: str
----

# harness/graph

A *Graph* holds the practices it is given and, for each, a *PracticeNodes*: that practice's part of the graph, a tree of *Node* objects read from source, with its edges and the run of its graph rules; *PracticeGraphRule* checks report *Violation* records, and *SavedGraph* is the graph as `.context/graph.json` keeps it. What a practice gives the graph is its *PracticeReading* (harness/guidance), not a class of this module, and the graph's own jobs sit in parts of their own files: `graph_practices.py` (*GraphPractices*), `load_scope.py` (*LoadScope*), `graph_build.py` (*GraphBuild*, the worker build), `explorer.py` (the explorer's answers), `saved_graph.py`, `model_node.py`, `pattern_overlays.py`. The whole model of this module, internals included, is `harness/graph/.context/graph-populate-model.md`; that document is canonical, and this section shows only the classes other modules use.

- **Purpose:** Turn a working copy into a graph of its practices that rules can check and a person can explore.
- **Seam (terms):** Graph, GraphPractices, PracticeNodes, LoadScope, Node, Source, ModelNode, ModelChildren, ModelReferences, GraphOverlay, PatternOverlays, PracticeGraphRule, RuleCheckContext, Violation, SavedGraph, SavedNode, SavedPractice, SavedGraphOutdated; `schema_sync_paused()` (`model_node.py`), `scanned_files(root, suffixes)` and `skips_folder(name)` (`skipped_folders.py`), `GRAPH_APP_PORTS` (`graph_app.py`); the spec support RuleFixture, RulePair, SchemaRuleRun (`rule_fixture.py`), which each practice's `rules/rule_examples.py` imports
- **Dependencies (one-way):** harness/annotations, harness/agent_tools, harness/installation, harness/mcp, harness/guidance

## Graph

One graph. Builders fill nodes, edges, and rules; the explorer reads the tree. Each of its jobs is a part it makes once and keeps.

+ Graph(practices: Iterable[PracticeGuidance] | None = None)
------
+ << composition >> build: GraphBuild
+ << composition >> practices: GraphPractices
+ scope: LoadScope
+ << composition >> applied_patterns: PatternOverlays
+ << composition >> schema_edges: SchemaEdges
+ << composition >> explorer: GraphExplorer
+ folder: str
+ overlays: list[str]
+ saved_file: SavedGraphFile
----
+ for_call(call: ToolCall): Graph
+ open(folder: Path): None
+ open_saved(folder: Path): None
+ report_progress(message: str): None
+ practice(key: str): PracticeGuidance
+ node(node_id: str): Node | None
+ link(kind: str, parent: Node, child: Node, display: Display = 'direct'): None
+ record(edge_type: EdgeType, parent: Node, child: Node): None
+ edges_from(kind: str, parent: Node): list[Edge]
+ direct_parent(child: Node): Node | None
+ restored_from(saved: SavedGraph): None
+ load_working_copy(folder: str, practices: dict[str, str], database: str | None = None, overlays: list[str] | None = None, force: bool = False, call: ToolCall | None = None): GraphLoaded
+ load_files(folder: str, practices: list[str], files: list[str], overlays: list[str] | None = None, call: ToolCall | None = None): GraphLoaded
+ refresh(paths: list[str], call: ToolCall | None = None): GraphLoaded
+ refreshed(paths: list[str], checked: Path, call: ToolCall | None = None): None
+ save_json(): GraphSaved
+ set_overlays(overlays: list[str], call: ToolCall | None = None): AppliedOverlays
+ overlay_of(folder: str): Overlay
+ practice_names(): list[str]
+ inventory(): Inventory
+ filter_choices(practices: list[str], node_types: list[str], practices_before: list[str] | None = None): Filter
+ source(node_id: str): NodeSource | None
+ return_nodes(filter: dict | None = None): list[FilteredNode]
+ explorer_trees(filter: dict | None = None): list[ExplorerEntry]
---<<makes its practices with>>--> PracticeCatalogue
---<<gives each practice its part through>>--> PracticeReading
---<<creates>>--> PracticeNodes
---<<creates>>--> GraphPractices
---<<creates>>--> LoadScope
---<<creates>>--> PatternOverlays
---<<creates>>--> GraphBuild
---<<creates>>--> GraphExplorer
---<<keeps>>--> PracticeGuidance
---<<restores from>>--> SavedGraph
---<<reads the call's session from>>--> ToolCall

## GraphPractices

The practices one graph holds, which the graph makes once and keeps (`graph.practices`): code that knows a practice's class reaches it by that class, and only a call that names a practice by its key looks it up by key.

+ GraphPractices(graph: Graph, held: Iterable[PracticeGuidance])
------
+ held: dict[str, PracticeGuidance]
+ opened: dict[str, PracticeGuidance]
+ chosen: list[PracticeGuidance]
+ roots_by_key: dict[str, Path]
----
+ named(key: str): PracticeGuidance
+ of(kind: type): PracticeGuidance
+ loaded(kind: type): PracticeGuidance | None
+ part_of(practice: PracticeGuidance): PracticeNodes
+ choose(roots: dict[PracticeGuidance, Path]): None
+ open_chosen(): None
+ reopen(saved: SavedGraph, folder: Path): None
+ hold(saved: SavedGraph, folder: Path | None): None
+ take(changes: GraphChanges): None
+ forget(files: list[Path]): None
+ in_reading_order(): list[PracticeGuidance]
+ check(): None
+ rebuild_trees(): None
---<<keeps>>--> PracticeGuidance
---<<reads the part of a practice from>>--> PracticeNodes
---<<restores each practice from>>--> SavedGraph
---<<raises>>--> UnknownPractice

## PracticeNodes

One practice's part of the graph that holds it: the root node its explorer tree starts from, the folder its source is read from, and its nodes by type and by id. The graph makes one for each practice it holds and gives it to the practice, which reads it as `practice.reading.in_graph`.

+ PracticeNodes(graph: Graph, practice: PracticeGuidance)
------
+ << association >> graph: Graph
+ << association >> practice: PracticeGuidance
+ << composition >> edge_index: EdgeIndex
+ << composition >> rule_run: PracticeRuleRun
+ << composition >> restore: PracticeRestore
+ source_root_path: Path | None
+ source_root: str
+ root: Node
+ node_types: list[str]
----
+ changed(): None
+ open(root: Path | None): None
+ close(): None
+ nodes(type: str | None = None): list[Node]
+ nodes_read_now(type: str | None = None): list[Node]
+ files_from_root(files: Iterable[Path]): set[str]
+ node(node_id: str): Node | None
+ holds(node_id: str): bool
+ offer_node_types(types: Iterable[str]): None
+ add(node: Node, node_id: str, file: str, start_line: int, end_line: int): Node
+ add_named(type: str, node_id: str, name: str, source: Source): Node
+ hold(node: Node): None
+ release(node: Node): None
+ unused_node_id(type: str, name: str): str
+ forget_files(files: Iterable[Path]): set[int]
+ forget(dropped: set[int]): set[int]
+ put_in_source_order(): None
+ renew_rules(): None
+ rebuild_tree(): None
+ take_saved(kept: SavedNode): None
+ edges(kind: str | None = None): list[Edge]
+ record(edge_type: EdgeType, parent: Node, child: Node): None
+ drop_edges(dropped: Callable[[Edge], bool]): list[Edge]
---<<keeps>>--> Node
---<<creates>>--> Source
---<<creates>>--> EdgeIndex
---<<creates>>--> PracticeRuleRun
---<<creates>>--> PracticeRestore

## LoadScope

The folder one load or refresh reads, and the files it is limited to; the graph keeps the scope of the read it last made (`graph.scope`), which the practices' readers ask while they read.

+ LoadScope(folder: Path | None, named: Iterable[Path] | None = None)
------
+ folder: Path | None
+ named: list[Path] | None
+ edited_files: list[Path] | None
+ folders: list[Path] | None
----
+ of_paths(folder: Path, paths: Iterable[str], skipped: frozenset[str] = frozenset()): LoadScope
+ refreshing(paths: Iterable[str]): LoadScope
+ source_files(root: Path, suffixes: set[str]): list[Path]
---<<lists files with>>--> scanned_files

## Node

children is the list populate writes on this node. Direct edges are the children; grouped and relationship edges sit under one child named for the kind.

+ Node(practice: PracticeGuidance, type: str, node_id: str, name: str, source: Source)
------
+ << association >> practice: PracticeGuidance
+ type: str
+ node_id: str
+ name: str
+ << composition >> source: Source
+ stage: str
+ data: dict
+ << aggregation >> children: list[Node]
+ parent: Node | None
+ graph_facts: tuple[str, ...]
+ facts: dict
+ graph: Graph
+ schema: PracticeSchema
+ fidelity: FidelityGuidance | None
+ fidelities: list[FidelityGuidance]
+ rules: GraphRulesCollection
+ file_language: str | None
+ failed_rules: list[str]
+ passing_rules: list[str]
----
+ set_fact(key: str, value): None
+ get_fact(key: str, default = None): None
+ merge_fact(key: str, values: list): None
+ has_fact(key: str): bool
+ rule_checks(): dict
+ applying_rule_types(): set[str]
+ forget_rules(): None
+ leave_tree(): None
+ place(file: str, start_line: int, end_line: int): None
+ populate(parent: Node | None = None): None
+ serialize(seen: set[str] | None = None, via: Node | None = None, stack: set[str] | None = None): ExplorerEntry
+ rule_category(): GraphRulesCollection | None
---<<reads its part of the graph from>>--> PracticeReading
---<<calls changed on>>--> PracticeNodes
---<<calls edges_from on>>--> Graph
---<<reads schema from>>--> PracticeRuleRun
---<<creates>>--> GraphRulesCollection

## ModelNode : Node

Base model object for one practice. An object made without a graph is detached: it belongs to no practice and records no edge until a practice adopts it with its whole tree (`join`) or an owner on a graph takes it as a part.

+ ModelNode(name: str, sequential_order: int, graph: Graph | None = None)
------
+ sequential_order: int
+ has_source_file: bool
+ node: ModelNode
+ << association >> graph: Graph
----
+ register_practice(practice_class: type): None
+ practice_kind(): type
+ semantic_type(): str
+ holds_parts(parts: ModelChildren): None
+ holds_references(references: ModelReferences): None
+ attach(child, kind: str): None
+ detach(child, kind: str): None
+ refer(target, kind: str): None
+ join(practice): None
+ subtree(): list[ModelNode]
+ batch_schema_sync(): Iterator[None]
---<<joins a practice through>>--> GraphPractices
---<<calls add on>>--> PracticeNodes
---<<calls record on>>--> Graph
---<<calls held on>>--> SchemaEdges
---<<keeps>>--> ModelChildren
---<<keeps>>--> ModelReferences
---<<creates>>--> Source
---<<raises>>--> ModelDetached

## ModelChildren : list

The list of the parts an owner is made of. Appending a part makes the owner its parent and records the edge.

+ ModelChildren(owner: ModelNode, kind: str)
------
+ << association >> owner: ModelNode
+ kind: str
----
+ append(item): None
+ extend(items: Iterable): None
+ insert(index: int, item): None
+ pop(index: int = -1): None
+ refill(incoming: Iterable): None
+ reconcile(sources: Iterable, load: Callable): None
---<<calls attach on>>--> ModelNode
---<<calls detach on>>--> ModelNode

## ModelReferences : list

The list of model objects an owner refers to without owning them, such as the stories an increment delivers; each one is a relationship edge.

+ ModelReferences(owner: ModelNode, kind: str)
------
+ << association >> owner: ModelNode
+ kind: str
----
+ append(item): None
+ extend(items: Iterable): None
+ insert(index: int, item): None
+ pop(index: int = -1): None
+ refill(incoming: Iterable): None
+ record_all(): None
---<<calls refer on>>--> ModelNode
---<<calls detach on>>--> ModelNode

## Source

Source text Monaco displays: file, start and end line, and text with each call marked.

+ Source(path: str, line_start: int, line_end: int, root: str = '')
------
+ file: str
+ start_line: int
+ end_line: int
+ root: str
+ calls: list[Call]
+ text: str
+ contents: str
----
+ whole_file(relative: str, root: str): Source
+ load_calls(raw: str): None
+ insert_calls(raw: str): str
+ align_to_label(label: str): None
+ widen_to_call_close(): None
+ align_to_example_export(root: str, name: str, files: Iterable[Path]): None
---<<keeps>>--> Call

## GraphOverlay

What one pattern gives the graph on top of the practices: the nodes it reads and the rules it adds to each practice, which live in `<pattern>/practices/<practice>/rules`. A pattern makes its overlay once and keeps it as `graph_overlay`.

+ GraphOverlay(pattern: Any)
------
+ << association >> pattern: PracticeGuidance
+ name: str
+ direct_kinds: frozenset[str]
----
+ display_of(kind: str): str
+ read(graph: Graph): None
+ practice_file(practice_key: str, name: str): Path
+ rules_for(practice: Any): dict[str, PracticeGraphRule]
---<<finds rules with>>--> rules_in
---<<loads>>--> PracticeGraphRule

## PatternOverlays

The pattern overlays one graph applies. The patterns package registers its pattern classes here when it is imported, and each graph makes each pattern once, the first time it applies it or reads its schemas, so the graph never imports a pattern.

+ PatternOverlays(overlays: list[str] | tuple[str, ...] = ())
------
+ paths: list[str]
+ patterns: list[PracticeGuidance]
+ graph_overlays: list[GraphOverlay]
+ every_graph_overlay: list[GraphOverlay]
+ available: list[str]
----
+ register(*pattern_classes): None
+ apply(overlays: list[str] | tuple[str, ...]): None
+ checks_of(practice: Any, overlays: list[str] | None = None): dict[str, PracticeGraphRule]
+ root_of(overlay: str): Path
---<<creates>>--> PracticeGuidance
---<<reads graph_overlay of>>--> GraphOverlay
---<<finds the folder of a pattern with>>--> class_folder

## PracticeGraphRule

One graph rule: the node types it checks and what it reports on a node or on the whole practice.

------
+ slug: str
+ node_types: tuple[str, ...]
----
+ check(node, context: RuleCheckContext): list[str]
+ check_practice(context: RuleCheckContext): list[tuple[str, str]]
+ applies_to(node_type: str): bool
---<<checks a node within>>--> RuleCheckContext

## RuleCheckContext

The practice one load checks, the graph that holds it, and the folder its source was read from.

+ RuleCheckContext(practice, source_root: Path | None)
------
+ << association >> practice: PracticeGuidance
+ << association >> graph: Graph
+ source_root: Path | None
----
+ index(kind: type): None
+ targets(node, kind: str): list
+ nodes(type: str | None = None): list
+ edges(kind: str): list
+ node(node_id: str): None
+ child_count(node, edge_kinds: tuple[str, ...]): int
+ children(node, edge_kind: str): list
+ node_data(node): dict
+ scenario_outline(node): bool
+ scenario_evidence(node): list[str]
---<<calls nodes on>>--> PracticeNodes
---<<calls edges on>>--> PracticeNodes
---<<calls edges_from on>>--> Graph
---<<calls node on>>--> Graph

## Violation

A rule broken at one place: the rule and the practice that checks it, the node it was found on, what that node is (`Operation `checkout``), the file and lines, the message, and how severe it is. A violation found on a graph node is a *NodeViolation*, which holds the node's rule that found it (`NodeViolation.at_node`).

+ Violation(rule: str, message: str, practice: str = '', node_id: str = '', subject: str = '', location: str = '', line: int | None = None, end_line: int | None = None, severity: str = 'error', source: list[SourceLine] | None = None)
------
+ rule: str
+ practice: str
+ node_id: str
+ subject: str
+ location: Annotated[str, SourceFile]
+ line: int | None
+ end_line: int | None
+ message: str
+ severity: str
+ source: list[SourceLine]
+ described: str
----
+ from_data(data: dict): Violation
+ by_rule(violations: list[Violation]): dict[str, list[Violation]]
+ is_under(prefixes: list[str]): bool
+ in_file(location: str, file: Path, lines_before: int, lines_after: int): Violation
---<<annotated with>>--> SourceFile
---<<keeps>>--> SourceLine

## SavedGraph

Every practice a folder's saved graph keeps, with the pattern overlays it was loaded with. A graph kept for the files a validate checks also names the folders of the other files the graph held (`held_beside`).

+ SavedGraph(overlays: list[str], practices: dict[str, SavedPractice], held_beside: list[str] | None = None)
------
+ overlays: list[str]
+ << composition >> practices: dict[str, SavedPractice]
+ held_beside: list[str]
+ document: dict
+ text: str
----
+ from_graph(graph: Graph, files: list[str] | None = None): SavedGraph
+ from_document(document: dict, source: str = ''): SavedGraph
+ from_text(text: str, source: str = ''): SavedGraph
+ from_file(path: Path): SavedGraph
+ from_nodes(nodes: list[dict]): SavedGraph
+ from_violations(violations: list[Violation], overlays: list[str] | None = None): SavedGraph
+ of_practices(keys: list[str]): SavedGraph
+ merged_over(older: SavedGraph | None): SavedGraph
+ holds(practice_roots: dict[str, Path], overlays: list[str]): bool
+ violations(practices: list[str] | None = None): list[Violation]
---<<reads practices of>>--> Graph
---<<creates>>--> SavedPractice
---<<raises>>--> SavedGraphOutdated

## SavedPractice

One practice as the saved graph keeps it: the folder its source was read from, the facts about the practice as a whole, its nodes, its edges, and the violations its rules found.

+ SavedPractice(name: str, source_root: str, root_facts: dict, nodes: list[SavedNode], edges: list[SavedEdge], violations: list[Violation])
------
+ name: str
+ source_root: str
+ root_facts: dict
+ << composition >> nodes: list[SavedNode]
+ << composition >> edges: list[SavedEdge]
+ violations: list[Violation]
+ violations_by_node: dict[str, list[Violation]]
+ record: dict
----
+ from_practice(practice: PracticeGuidance, files: list[str] | None = None): SavedPractice
+ from_record(name: str, record: dict): SavedPractice
+ root_in(folder: Path | None): Path | None
---<<reads nodes and edges of>>--> PracticeNodes
---<<creates>>--> SavedNode
---<<creates>>--> Violation

## SavedNode

One node as the saved graph keeps it: what it is, where it sits in its file, its stage, and its facts.

+ SavedNode(node_id: str, name: str, type: str, practice: str, file: str, line: int, end_line: int, stage: str, facts: dict)
------
+ node_id: str
+ name: str
+ type: str
+ practice: str
+ file: str
+ line: int
+ end_line: int
+ stage: str
+ facts: dict
+ record: dict
----
+ from_record(record: dict): SavedNode

## SavedGraphOutdated : Exception

A saved graph in another shape than this code writes. Load the working copy again to replace it.

+ SavedGraphOutdated(source: str, version: object)
------
----

## RuleFixture

Spec support: fixture files written to a folder of their own and read by one practice, the way a live load reads a working copy, so a rule is checked on the nodes the practice really reads.

+ RuleFixture(practice_class: type, files: dict[str, str])
------
+ context: RuleCheckContext
----
+ read_only(paths: list[str]): None
+ hits(rule): list[str]
---<<creates>>--> Graph
---<<creates>>--> RuleCheckContext

## RulePair

Spec support: a rule's failing fixture and its repaired fixture; the rule must flag the first and pass the second.

+ RulePair(rule, faulty: RuleFixture, repaired: RuleFixture)
------
----
+ check(): None
---<<checks>>--> RuleFixture

## SchemaRuleRun

Spec support: one rule's findings over one practice's nodes, as the graph's own check records them when validate runs it.

+ SchemaRuleRun(rule, context: RuleCheckContext)
------
----
+ hits(): list[str]
+ node_hits(node): list[str]
---<<reads nodes through>>--> RuleCheckContext

# harness/diagnostics

This module reports whether CDD is running and answering: *ServerHealth* says which of its long-running parts are up right now, and the diagnostics toolsets, each a *CallDiagnostics* made for one call, probe what an install published through the MCP host answering that call and write a report section.

- **Purpose:** Show whether CDD is running: which of its servers and apps are up, for the chat's server health band, and whether what an install published answers through the live MCP host, so a broken publication shows up in a report rather than in a failing chat.
- **Seam (terms):** ServerHealth, CallDiagnostics, DiagnosticsNeedACall, AgentToolsDiagnostics, GuidanceDiagnostics, AgentToolsProbe, GuidanceProbe; the MCP operations `server-health.report`, `agent-tools-diagnostics.agent_tools_diagnostics`, `guidance-diagnostics.guidance_diagnostics`
- **Dependencies (one-way):** harness/agent_tools, harness/installation, harness/hooks, harness/mcp, harness/guidance, harness/graph

## ServerHealth

Report the parts of CDD that run outside this MCP host, so a person can see what is up without opening a terminal. Each app a report probes is registered from the ports file its servers read: the graph app's here, the session board's from space/kanban.

+ ServerHealth(repo_root: Path | str, graph_ports: tuple[int, ...] | None = None, kanban_ports: tuple[int, ...] | None = None, hook_daemon: HookDaemon | None = None)
------
+ kanban_app_port: int | None
+ kanban_app_url: str
+ graph_app_port: int | None
+ is_hook_server_running: bool
----
+ reports_graph_app_on(ports: tuple[int, ...]): None
+ reports_kanban_app_on(ports: tuple[int, ...]): None
+ load(project: Path | str): ServerHealth
+ report(): ServerHealth
---<<creates>>--> HookDaemon
---<<reads the graph app's ports from>>--> GRAPH_APP_PORTS
---<<annotated with>>--> LanguageAdapter

## CallDiagnostics

A diagnostics toolset made for one call: it holds the call, so it probes through the MCP host answering it, and the install of the project the call names, made once. The toolset an install publishes is made with no call and answers each call through `for_call`.

+ CallDiagnostics(call: ToolCall | None = None)
------
+ << association >> call: ToolCall
----
+ for_call(call: ToolCall): CallDiagnostics
---<<creates>>--> Installer
---<<raises>>--> DiagnosticsNeedACall

## AgentToolsDiagnostics : CallDiagnostics

Probe the space, harness, and tools MCP operations an install published (ping and invoke), through the MCP host answering the call.

------
----
+ agent_tools_diagnostics(guidance: list[str] | None = None): str
---<<creates>>--> AgentToolsProbe

## GuidanceDiagnostics : CallDiagnostics

Probe installed guidance instructions and guidance-action MCP operations, through the MCP host answering the call.

------
----
+ guidance_diagnostics(guidance: list[str] | None = None): str
---<<creates>>--> GuidanceProbe
---<<calls instructions on>>--> GuidanceProbe
---<<calls actions on>>--> GuidanceProbe

## AgentToolsProbe

A probe of the workspace MCP tools one install deployed (space, harness, and tools): ping each, call the light ones with probe arguments, and call session and graph tools with `cdd-diagnostic` fixtures.

+ AgentToolsProbe(installer: Any, guidance: list[str] | None = None, mcp_host: Any = None, project: Path | None = None)
------
+ host: Any
+ toolset_refs: tuple[str, ...]
+ published: list[str]
----
+ run(): str
+ ping(): str
+ invoke(): str
+ heavy_invoke(): str
---<<loads>>--> McpHost
---<<creates>>--> ProbeArguments
---<<creates>>--> ProbeSection

## GuidanceProbe

A probe of the guidance one install deployed, made for its Installer and the guidance slugs that filter what it calls; it leaves `improvement.repair` and `improvement.verify_fix` alone and reports them skipped.

+ GuidanceProbe(installer: Any, slugs: list[str])
------
+ installer: Installer
+ slugs: list[str]
+ << composition >> arguments: ProbeArguments
+ prefixes: list[str]
----
+ from_filter(installer: Any, guidance: list[str] | None): GuidanceProbe
+ matches(mcp_name: str): bool
+ instructions(): str
+ actions(): str
---<<lists the actions of>>--> ActionCatalogue
---<<names toolsets with>>--> ToolsetReference
---<<creates>>--> ProbeArguments
---<<creates>>--> ProbeSection

# harness/chat

*Chat* is a Claude Code chat reached from outside it, so the session board can see which chats are connected and send one a command; *ChatCommand* is a command a chat takes at its check-in, and *ChatMessage* is a command as the board lists it.

- **Purpose:** Let the board drive any connected chat — send it a command and follow that command until the chat has shown and finished it — without the chats and the board sharing a process.
- **Seam (terms):** Chat, ChatCommand, ChatMessage, ChatNotConnectedError; the MCP operations `chat.list`, `chat.send`, `chat.messages`, `chat.remove`, `chat.resend`, `chat.check_in`, `chat.confirm`, `chat.finish`
- **Dependencies (one-way):** harness/agent_tools, harness/installation, harness/mcp

## Chat

Reach a Claude Code chat from outside it: list the chats that are connected, and send one a command. A chat is a folder every process can read: the chat alone writes its state when it checks in, and a sender adds one file per command to its waiting folder.

+ Chat(folder: Path)
------
+ id: str
+ name: str
+ is_busy: bool
+ folder: str
+ is_connected: bool
----
+ load(chat: str): Chat
+ list(): list[Chat]
+ send(kind: CommandKind, text: str): Chat
+ messages(): list[ChatMessage]
+ check_in(is_busy: bool = False, name: str = '', folder: str = ''): list[ChatCommand]
+ confirm(message: str, is_shown: bool, reason: str = ''): Chat
+ finish(message: str): Chat
+ resend(message: str): Chat
+ remove(message: str): Chat
---<<loads>>--> ChatPointer
---<<reads and writes its state with>>--> JsonFile
---<<creates>>--> ChatCommand
---<<creates>>--> ChatMessage
---<<raises>>--> ChatNotConnectedError
---<<annotated with>>--> LanguageAdapter

## ChatCommand

A command a chat takes at its check-in: the message it came in, and what to do with its text.

+ ChatCommand(message: str, kind: str, text: str)
------
+ message: str
+ kind: str
+ text: str
----

## ChatMessage : ChatCommand

A message sent to a chat, as the board lists it: when it was sent, where it stands, and why it failed.

+ ChatMessage(message: str, kind: str, text: str, sent_at: float, state: MessageState, reason: str)
------
+ sent_at: float
+ state: MessageState
+ reason: str
----

## ChatNotConnectedError : LookupError

Raised when a command is sent to a chat whose mod has not checked in lately.

+ ChatNotConnectedError(chat: str)
------
----

# harness/catalog_generator

The *Catalog* renders CDD's practices, actions, and approach as pages; a *CatalogPractice* is one practice as every page and the session board show it, and a *CatalogFidelity* is one of its fidelities as the catalog shows it, with its board column.

- **Purpose:** Show people what CDD offers, as pages generated from the same guidance the agent follows, for CDD itself or for one project's approach.
- **Seam (terms):** Catalog, CatalogPractice, CatalogFidelity; the MCP operations `catalog.generate_catalog`, `catalog.apply_brand`, `catalog.generate_project_approach`, `catalog.configure_project_approach`; `python -m harness.catalog_generator.generate_cdd_catalog`
- **Dependencies (one-way):** harness/annotations, harness/agent_tools, harness/markdown, harness/guidance, harness/installation, harness/process, harness/mcp

## Catalog

The top-level entry point - the only class `generate_cdd_catalog.py` calls. Holds the project it is generated for, and writes every page with the parts it holds: its project, its brand, its approach copy, and its practices.

+ Catalog(repo_url: str = '', ref: str = '', out_root: str = '', brands_root: str | Path | None = None, approach_md_path: str | Path | None = None, project: str | Path | None = None)
------
+ << composition >> project: CatalogProject
+ << composition >> citation: GitCitation
+ approach_md_path: Path
+ << composition >> brand: Brand
+ repo_url: str
+ out_root: Path
+ << composition >> practices: list[CatalogPractice]
+ utilities: list[Utility]
+ lifecycle_actions: list[LifecycleAction]
+ approach_copy: ApproachCopy
+ board: HubBoard
+ brands: dict[str, Path]
----
+ load(project: Path): Catalog
+ generate_catalog(brand: str | Path = ''): str
+ apply_brand(name: str): str
+ generate_project_approach(examples_json: str = '', project_title: str = ''): str
+ configure_project_approach(example_paths: list[str] | None = None): str
+ write_page(relative_path: str, html_text: str): Path
---<<loads>>--> CatalogPractice
---<<lists actions from>>--> ActionCatalogue
---<<finds the utilities with>>--> RepositoryToolsets
---<<creates>>--> GitCitation
---<<creates>>--> HubBoard

## CatalogPractice

One practice as the catalog shows it: the live `PracticeGuidance`, the catalog card it gives itself, its place in the catalogue, and the fidelities it shows, each placed in the board's stage columns. Its slash command is the folder the Claude Code skill install writes its skill into.

+ CatalogPractice(practice: PracticeGuidance, skills: FileInstallation | None = None, position: int = 0, catalogue: tuple[PracticeGuidance, ...] = ())
------
+ << association >> practice: PracticeGuidance
+ position: int
+ key: str
+ display_name: str
+ label: str
+ product_engineering_label: str
+ gives_stage_examples: bool
+ family: str
+ perspective: str
+ order: int
+ spec_blurb: str
+ href: str
+ skill_name: str
+ fidelities: list[FidelityGuidance]
+ << composition >> shown_fidelities: list[CatalogFidelity]
+ board_fidelities: list[CatalogFidelity]
+ on_board: bool
+ examples_folder: Path
+ shared_markdown: str
----
+ skill_install(): FileInstallation
+ of_practices(practices: Iterable[PracticeGuidance]): list[CatalogPractice]
+ load_all(): list[CatalogPractice]
	-> PracticeCatalogue.create_all
+ giving_stage_examples(practices: list[CatalogPractice]): CatalogPractice | None
+ skill_of(guidance: PracticeGuidance | FidelityGuidance): str
+ fidelity_in(column: StageColumn): CatalogFidelity | None
+ fidelity_at(stage: str): CatalogFidelity | None
+ fidelity_href(fidelity: FidelityGuidance): str
+ language_of(path: Path): str | None
+ copy_examples_into(out_root: Path): None
---<<creates>>--> CatalogFidelity
---<<reads fidelities of>>--> PracticeGuidance
---<<lists practices from>>--> PracticeCatalogue
---<<creates>>--> FileInstallation
---<<creates>>--> IdeLayout
---<<reads constants of>>--> InstallDestination
---<<creates>>--> Name
---<<reads a file's format with>>--> Format
---<<leaves out what is annotated>>--> NoCatalog

## CatalogFidelity

A fidelity as the catalog shows it: its board column, its board label, the opening of its overview, and its example files.

+ CatalogFidelity(fidelity, practice: CatalogPractice)
------
+ << association >> fidelity: FidelityGuidance
+ << association >> practice: CatalogPractice
+ name: str
+ stage: str
+ column: StageColumn | None
+ label: str
+ opening: str
+ example_files: list[Path]
+ panel_example_files: list[Path]
+ examples_html: str
----
---<<reads stage of>>--> FidelityGuidance
---<<finds its column in>>--> StageColumn
---<<creates>>--> ExampleFile

# harness/design_canvas

A *DesignCanvas* is the pages, boards, and artboard files of one Claude Design canvas; a practice lays out its own artboards with `artboard(...)`, `box(...)`, and `thumbnail(...)` and the shared look in `harness.design_canvas.look`, and hands them to the canvas, which decides where every file goes.

- **Purpose:** Let a practice publish its views as a Claude Design canvas without knowing the canvas's file layout, and regenerate it without overwriting what people edited.
- **Seam (terms):** DesignCanvas; `artboard(...)`, `box(...)`, `stem(...)`, `thumbnail(...)` (`canvas.py`); the look `LOOK`, `FONTS`, `BACKGROUND` (`look.py`)
- **Dependencies (one-way):** harness/installation

## DesignCanvas

The pages, boards and artboard files of one Claude Design canvas, and the files its project folder already holds, so a practice never reads the canvas project itself.

+ DesignCanvas(title: str, project: Path | None = None)
------
+ title: str
+ project: Path | None
+ launch_page: str | None
----
+ add_page(page_id: str, name: str): None
+ add_board(name: str, board: dict, text: str | None = None): None
+ artboards_in(folder: str): list[str]
+ holds(name: str): bool
+ size_of(name: str): int | None
+ stylesheets_linked_by(names: list[str]): list[str]
+ files(): dict[str, str]
+ write(root: str | Path): list[str]

# space/work_state

A *WorkState* is what one chat has open — its branch, its worktree, and its session — kept by the cdd server in `~/.cdd/open-sessions.json`, never in the checkout.

- **Purpose:** Keep what is open true for one chat on one machine, so it is never committed and never clashes between worktrees.
- **Seam (terms):** WorkState, SESSIONS_FOLDER, E2E_RESULTS_FOLDER
- **Dependencies (one-way):** harness/installation, harness/mcp

## WorkState

The open branch, worktree, and session of one chat, or of one checkout folder for a call that names no chat. It keeps names only: the repository turns a branch name into its *Branch* and a worktree's folder into its *Worktree*.

+ WorkState(repo_root: Path | str, chat: str = '', home: Path | str | None = None)
------
+ root: Path
+ chat: str
+ sessions_folder: Path
+ path: Path
+ key: str
+ branch_name: str
+ worktree_folder: Path | None
+ session: str
----
+ load(): dict[str, str]
	// every chat's call reaches the one file in the one server process, so its read-change-write runs one at a time
---<<reads and writes>>--> JsonFile
---<<finds its file through>>--> CddHome

# space/repo

A *Repo* is the local clone; a *Branch* is a named branch on it, its *Worktrees* are its checkouts, and a *Worktree* is one of them.

- **Purpose:** Give every caller one object graph for the clone, its branches and worktrees, and its commits, so version control is never reimplemented with raw git output.
- **Seam (terms):** Repo, ServedCheckouts, Branch, Worktrees, Worktree, Commit, WorktreeNotRemovedError
- **Dependencies (one-way):** harness/agent_tools, harness/installation, harness/process, harness/hooks, harness/mcp, space/work_state

## Repo

Local git clone: its branches and its commits. The checkouts beside it are its `worktrees`.

+ Repo(root: str | Path = '.')
------
+ root: Path
+ default_branch: str
+ << composition >> git: Git
+ << composition >> worktrees: Worktrees
+ is_clone: bool
+ checkout_folder: Path
+ branches: list[Branch]
+ current_branch: Branch
+ current_commit: str
+ default_start_point: str
+ << association >> main_clone: Repo
+ own_work_state: WorkState
+ work_state: WorkState
+ open_worktree: Worktree | None
----
+ of_project(project: Path): Repo
	-> ServedCheckouts.at
+ find_root(): Path | None
+ checkout_at(folder: Path | str): Repo
	-> ServedCheckouts.at
+ is_linked_worktree(): bool
+ primary_root(): Path
+ path_from_top(path: Path | str): str
+ branch_named(name: str): Branch
+ has_ref(ref: str): bool
+ is_dirty(path: str | Path | None = None, untracked: bool = True): bool
+ commit(paths: list[str], message: str, untracked: bool = False): str
	-> Git.run
+ push_upstream(): None
+ needs_push(): bool
+ fetch(): None
+ pull(): None
+ merge_from(other: Branch, message: str = ''): str
+ switch_branch(name: str = ''): str
	-> Branch.switch_to
+ close_branch(name: str = '', commit_message: str = 'branch: close'): str
	-> Branch.close
	-> LatestRelease.keep
+ switch_worktree(name: str = ''): str
	-> Branch.move_to_worktree
+ close_worktree(commit_message: str = 'worktree: close'): str
	-> Worktree.close
+ switch_branch_command(): str
+ close_branch_command(): str
+ switch_worktree_command(): str
+ close_worktree_command(): str
+ push_commit(message: str, untracked: bool = True, sync_remote: bool = True): Commit
+ push(hint: str = ''): str
---<<creates>>--> Branch
---<<creates>>--> Commit
---<<creates>>--> Worktrees
---<<creates>>--> LatestRelease
---<<runs>>--> Git
---<<calls succeeds on>>--> Git
---<<raises>>--> RepoConnectError
---<<creates>>--> WorkState
---<<reads the answering call from>>--> ToolCall
---<<annotated with>>--> AgentToolSetAnnotation
---<<annotated with>>--> LanguageAdapter
---<<annotated with>>--> ToolSubject
---<<annotated with>>--> Mcp
---<<annotated with>>--> LongCall
---<<annotated with>>--> Command

## ServedCheckouts

The repository of every checkout this process works in, each made once and held while it runs, so every tool call and every session of one checkout work on the same Repo.

+ ServedCheckouts()
------
----
+ at(root: Path): Repo
---<<creates>>--> Repo

## Commit

One git commit: its sha, subject, full message, and the trailers the message carries, which is what an MCP tool that makes a commit answers with.

+ Commit(sha: str, message: str)
------
+ sha: str
+ subject: str
+ message: str
+ trailers: dict[str, str]
----

## Branch

Named branch on a *Repo* — checkout, commit, merge, and close.

+ Branch(repo: Repo, name: str)
------
+ repo: Repo
+ name: str
+ exists: bool
+ is_checked_out: bool
+ is_default: bool
+ << association >> worktree: Worktree | None
+ start_point: str
----
+ changed_files(): list[str]
+ check_out(): Branch
+ switch_to(): Branch
+ open_in_worktree(): Worktree
	-> Worktrees.open
+ move_to_worktree(): Worktree
+ save(commit_message: str): None
+ land_on_default(): None
+ delete(unmerged: bool = False): None
+ close(commit_message: str = 'branch: close'): None
---<<asks whether a ref exists through>>--> Repo
---<<finds its checkout through>>--> Worktrees

## Worktrees

The checkouts of one repository, as `git worktree` lists them: the main clone and each linked worktree, each with the branch checked out there.

+ Worktrees(repo: Repo)
------
----
+ repository_at(folder: Path): Repo
+ at(folder: Path | str): Worktree | None
+ of(branch: Branch): Worktree | None
+ open(branch: Branch): Worktree
+ sibling_folder(branch: Branch): Path
+ add(path: str | Path, branch: Branch): Worktree
+ remove(worktree: Worktree): None
	// stops the checkout's hook daemon first; a folder still there afterwards raises WorktreeNotRemovedError
---<<lists>>--> Worktree
---<<stops>>--> HookDaemon
---<<raises>>--> WorktreeNotRemovedError

## Worktree

One checkout of the repository, as the *Worktrees* that listed it found it: its folder, its own *Repo*, and the branch checked out there, each made once when it is listed.

+ Worktree(worktrees: Worktrees, path: Path | str, branch_name: str)
------
+ path: Path
+ << association >> repository: Repo
+ << association >> branch: Branch | None
+ sync_failure: str
----
+ fetch_pull(): None
+ close(commit_message: str): Branch
	-> Branch.save
	-> Worktrees.remove
---<<calls branch_named on>>--> Repo

## WorktreeNotRemovedError : RuntimeError

A worktree's folder still there after git, a forced delete, and the Windows fallbacks each tried to remove it; it names the folder left behind.

+ WorktreeNotRemovedError(folder: Path)
------
+ folder: Path
----

# space/session

A *Session* is one named piece of work in `.sessions/{name}/`; *Sessions* are all of a checkout's sessions; its *SessionLog* records each action, a *PracticeSessionOutput* is what one practice has in it, and its *FileManager* lists and reads the files under its roots.

- **Purpose:** Keep the state of one piece of work — where it works, which practices it uses and where they write, the files it works with, the log of what was done, the handoff the next agent resumes from, and the reasons behind hard-to-reverse choices — so any chat or tool can pick the work up from its folder.
- **Seam (terms):** Sessions, Session, BoardPractices, CallSessions, SessionLog, ChatLog, LogEntry, LogTimestamp, HookLog, PracticeSessionOutput, FidelitySessionOutput, FileManager, FileEntry, FileText, PathOutsideRootsError, ThrowawayProject, SessionDiagnostics
- **Dependencies (one-way):** harness/annotations, harness/agent_tools, harness/installation, harness/hooks, harness/mcp, harness/guidance, harness/graph, harness/diagnostics, harness/catalog_generator, space/work_state, space/repo, cdd_guidance/actions (the session diagnostics probe runs Generate and Validate)

## Sessions

The work sessions of one checkout: open ones in `.sessions/{name}/`, closed ones in `.sessions/_complete/`. Which one is open is kept per chat by the cdd server under `~/.cdd` (*WorkState*), never in the checkout; `main` works on the whole repository and is open when no other is.

+ Sessions(project: Path | str)
------
+ << association >> repo: Repo
+ root: Path
+ folder: Path
+ backlog_folder: Path
+ open_name: str
+ << composition >> board_practices: BoardPractices
+ << composition >> file_manager: FileManager
----
+ of_project(project: Path): Sessions
	-> CallSessions.of_project
+ folder_of(name: str): Path
+ all(): list[Session]
+ named(name: str): Session | None
+ with_file(session_file: str): Session
+ load(folder: Path): Session
	// one Session is held for each session folder, so every call in a session, from any chat, works on the same object
+ root_of(session: Session): Path
+ moved(session: Session, moved_from: Path): None
+ open_state(chat: str = ''): WorkState
+ open_name_for(chat: str = ''): str
+ create(name: str, workpath: Path | None = None, title: str = '', scope: str = '', parent: str = ''): Session
+ open(session: Session, chat: str = ''): Session
+ current(call: ToolCall | None = None): Session
+ switch(name: str = '', workpath: Path | None = None, call: ToolCall | None = None): str
	-> SessionLog.instructions
+ close(session: Session): None
---<<creates>>--> Name
---<<calls of_project on>>--> Repo
---<<creates>>--> Session
---<<keeps>>--> Session
---<<creates>>--> WorkState
---<<raises>>--> SessionNotFoundError
---<<reads the answering call from>>--> ToolCall
---<<creates all practices from>>--> PracticeCatalogue
---<<lists practices as>>--> CatalogPractice
---<<annotated with>>--> AgentToolSetAnnotation
---<<annotated with>>--> AgentToolAnnotation
---<<annotated with>>--> Mcp
---<<annotated with>>--> Command

## BoardPractices

The practices a checkout's session board works through, each as the catalog shows it, made once for the checkout and kept by its *Sessions*.

+ BoardPractices(catalogued: list[CatalogPractice])
------
+ << aggregation >> catalogued: list[CatalogPractice]
----
+ of(kind: type): CatalogPractice
+ works_through(kind: type): bool
+ keyed(key: str): CatalogPractice
---<<raises>>--> PracticeNotFoundError

## CallSessions

The sessions of every project this process serves, each made once and held while it runs. Registered with *ToolCall* when `sessions.py` is imported, so the framework opens a call's session without importing space.

+ CallSessions()
------
----
+ of_project(project: Path | str): Sessions
+ saved_in(project: Path): Session
+ open_in(call: ToolCall): Session
+ of_chat(call: ToolCall): Sessions
+ named_in(session_file: str, call: ToolCall): Session
---<<creates>>--> Sessions
---<<calls of_project on>>--> Repo
---<<registers itself as the session opener with>>--> ToolCall

## Session

One named piece of work in a project, kept in `.sessions/{name}/`. It holds where it works, the practices it uses, and its title; its log, files, handoffs, decision records, and chat injections are objects of their own, made with it. It holds no chat: a line a call logs points at that call's chat.

+ Session(sessions: Sessions)
------
+ name: str
+ << association >> sessions: Sessions
+ << association >> repo: Repo
+ repo_path: Path
+ << composition >> context_config: ContextConfig
+ workpath: Path | None
+ session_path: Path | None
+ is_closed: bool
+ session_file: Path
+ session_file_from_project: str
+ work_root: Path
+ << composition >> graph: Graph
+ workpath_from_project: str
+ title: str
+ scope: str
+ parent: str
+ fields: dict
+ reports_folder: Path
+ << composition >> practices: dict[str, PracticeSessionOutput]
+ latest_handoff: str
+ << composition >> log: SessionLog
+ << composition >> session_files: SessionFiles
+ << composition >> handoffs: Handoffs | None
+ << composition >> decision_records: DecisionRecords
+ << composition >> chat_injections: ChatInjections
----
+ from_file(session: str, call: ToolCall): Session
	-> ToolCall.session_named
+ context_folder(module: str = ''): Path
+ path_named(named: str | Path): Path
+ document_named(content: str = '', paths: list[str] | str | None = None): str
+ from_project(path: Path | str): str
	-> Repo.path_from_top
+ save_fields(**values): None
+ save(): None
+ hook_log(filename: str): HookLog
+ keep_file(file: Path): Path
+ move_to_closed(): Session
+ move_to_archive(): Session
+ move_to_backlog(): Session
+ reopen(): Session
	-> Sessions.moved
+ practice(name: str): PracticeSessionOutput
+ close(): None
	-> Sessions.close
+ choose_workpath(path: str = ''): Session
+ folder_files(): list[FileEntry]
	-> SessionFiles.in_folder
+ read_file(path: str = ''): FileText
	-> SessionFiles.read
+ mark_loop(call: ToolCall): str
	-> ChatLog.mark_loop
+ read_loop(number: int | None = None): str
	-> SessionLog.read_loop
+ append_log(call: ToolCall, note: str = '', loop: int | None = None, paths: list[str] | None = None): str
	-> ChatLog.append_note
+ write_handoff(content: str = '', paths: list[str] | str | None = None): str
+ read_handoff_format(): str
+ handoff_session(next_focus: str = ''): str
+ read_cdr_format(): str
+ list_cdrs(): str
+ write_cdr(slug: str, content: str = '', paths: list[str] | str | None = None): str
+ record_decisions_session(): str
---<<creates all practices from>>--> PracticeCatalogue
---<<creates>>--> PracticeSessionOutput
---<<calls work_in on>>--> PracticeGuidance
---<<creates and opens saved>>--> Graph
---<<creates>>--> SessionLog
---<<creates>>--> HookLog
---<<raises>>--> UnknownPracticeError
---<<annotated with>>--> Identity
---<<annotated with>>--> LanguageAdapter
---<<annotated with>>--> AgentToolSetAnnotation
---<<annotated with>>--> ToolSubject
---<<annotated with>>--> Skill
---<<annotated with>>--> Command
---<<annotated with>>--> AgentInstructionsAnnotation
---<<annotated with>>--> NoSessionLog

## SessionLog

The log of one session: `session.log`, one timestamped line per action, tool call, note, and loop marker, each ending with a pointer to the chat that caused it, and `session.err`, the full trace of each failure a log line points at. A chat writes its lines through `by(chat)`.

+ SessionLog(session: Session)
------
+ session: Session
+ path: Path | None
+ error_path: Path | None
+ << composition >> entries: list[LogEntry]
+ << composition >> injected_rules: InjectedRules
+ last_loop_number: int
+ latest_loop_with_entries: int
----
+ latest(*verbs: str, stage: str = ''): LogEntry | None
+ record(line: str): None
	// a session without a folder has a log that writes nothing
+ by(chat: ChatPointer | None): ChatLog
+ append_trace(failure: BaseException, tool: str): int
+ seed_first_loop(): None
+ loop_at(number: int): Loop
+ read_loop(number: int | None = None): str
+ loop_to_note(loop: int | None): int
+ instructions(): str
---<<creates>>--> LogEntry
---<<creates>>--> ChatLog
---<<stamps lines with>>--> LogTimestamp
---<<raises>>--> LoopNotFoundError
---<<reads session path of>>--> Session

## ChatLog

The lines one chat writes in a session's log, each pointing at that chat; `no-chat` when none is known.

+ ChatLog(log: SessionLog, chat: ChatPointer | None)
------
+ << association >> chat: ChatPointer
----
+ line(line: str): None
+ validation(worked: FidelitySessionOutput, violations: list[str]): None
+ action(action: str, paths: list[Path], worked: list[FidelitySessionOutput] | None = None): None
+ guidance_action(action: str, worked: list[FidelitySessionOutput]): None
+ tool(tool_name: str, paths: list[str] | None = None): None
+ note(message: str, paths: list[Path] | None = None): None
+ append_note(note: str, loop: int | None = None, paths: list[str] | None = None): str
+ failure(failure: BaseException, tool: str = ''): None
	-> SessionLog.append_trace
+ next_loop(): Loop
+ mark_loop(): int
---<<records lines in>>--> SessionLog
---<<names practice and fidelity of>>--> FidelitySessionOutput

## LogEntry

One line of a session log: `<time> <verb> <words...>`, the words being the subject the verb acted on.

+ LogEntry(line: str)
------
+ text: str
+ time: str
+ verb: str
+ words: list[str]
+ stage: str
+ loop_number: int | None
----
+ names(fidelity: FidelityGuidance): bool
---<<reads practice guidance of>>--> FidelityGuidance
---<<reads name of>>--> FidelityGuidance

## LogTimestamp

The time a session log line, a hook log entry, or a toast is stamped with: a moment in UTC, to the second, such as `2026-11-07T17:30:05Z`, so every log's lines sort and compare alike.

+ LogTimestamp(moment: datetime)
------
+ moment: datetime
----
+ now(): LogTimestamp
+ read(text: str): LogTimestamp

## HookLog

A log a hook appends to while a session is open, such as `dispatch.debug` or the prompt log, in the `logs` folder of the session's folder.

+ HookLog(path: Path)
------
+ path: Path
----
+ append(text: str): None
+ stamped(line: str): None
---<<stamps lines with>>--> LogTimestamp

## PracticeSessionOutput

What one practice has in one session: the session's one instance of the practice, whether it is on, and the folder it writes under.

+ PracticeSessionOutput(guidance: PracticeGuidance, session: Session)
------
+ name: str
+ << association >> session: Session
+ session_file: str
+ << composition >> guidance: PracticeGuidance
+ fidelities: GuidanceCollection
+ saved: dict
+ enabled: bool
+ chosen_outputs: dict
+ folder: Path
+ output_root: Path
+ root: str
+ is_root_chosen: bool
----
+ load(session: str, practice: str, call: ToolCall): PracticeSessionOutput
	-> ToolCall.session_named
	-> Session.practice
+ of_fidelity(fidelity: FidelityGuidance): FidelitySessionOutput
+ save(**values): None
+ enable(is_enabled: bool): PracticeSessionOutput
+ choose_root(path: str): PracticeSessionOutput
+ keep_root(root: Path): None
+ use_default_root(): PracticeSessionOutput
---<<creates>>--> FidelitySessionOutput
---<<reads the configured folder from>>--> ContextConfig
---<<saves fields>>--> Session
---<<annotated with>>--> Identity
---<<annotated with>>--> LanguageAdapter
---<<annotated with>>--> AgentToolSetAnnotation
---<<annotated with>>--> NoSessionLog

## FidelitySessionOutput

Where one fidelity writes in one session: its output paths by format, the files it declares there, the format it last used, and its reports folder.

+ FidelitySessionOutput(practice: PracticeSessionOutput, fidelity: FidelityGuidance)
------
+ << association >> practice: PracticeSessionOutput
+ << association >> fidelity: FidelityGuidance
+ is_enabled: bool
+ reports_folder: Path
+ root: Path
+ kept_format: str
----
+ reports(): list[Path]
+ new_report_path(): Path
+ keep_format(format: str): None
+ output_paths(): dict[str, list[str]]
+ files(): dict[str, list[FileEntry]]
	-> SessionFiles.find
+ has_output(): bool
---<<matches declared paths with>>--> DeclaredFile
---<<lists the declared files as>>--> FileEntry

## FileManager

List and read the files under a session's roots, the folders its practices work in, named from its workpath. Moved here from tools/file_manager.

+ FileManager(workpath: Path | str, roots: tuple[Path, ...])
------
+ workpath: Path
+ roots: tuple[Path, ...]
----
+ load(call: ToolCall): FileManager
	-> ToolCall.session
+ list(folder: str = ''): Folder
+ read(path: str): FileText
	// never reads a path outside the session's roots; such a path raises PathOutsideRootsError
+ find(pattern: str): list[Path]
---<<creates>>--> Folder
---<<creates>>--> FileText
---<<raises>>--> PathOutsideRootsError
---<<annotated with>>--> LanguageAdapter
---<<annotated with>>--> AgentToolSetAnnotation
---<<annotated with>>--> Mcp
---<<annotated with>>--> NoSessionLog

## FileEntry

One file something declares, such as a fidelity's output, as a path from the project, and whether it is there yet.

+ FileEntry(path: str, exists: bool)
------
+ path: str
+ exists: bool
----

## FileText

The text of one file, with its path from the workpath; no text for a file that is not there.

+ FileText(path: str, text: str)
------
+ path: Annotated[str, SourceFile]
+ text: str
----

## PathOutsideRootsError : ValueError

A path outside every root of the session, which a page may name but never reach.

+ PathOutsideRootsError(path: str)
------
----

## ThrowawayProject

An empty project named by `CDD_PROJECT` while a spec runs, so the actions a spec runs write to their own session log instead of the log of whoever is working in the repository.

+ ThrowawayProject(name: str = '')
------
+ root: Path
+ folder: Path
----
+ close_all(): None
+ close(): None

## SessionDiagnostics : CallDiagnostics

Probe session logging (generate, validate, loops, chat pointers). Made for one call, as every diagnostics toolset is, so it writes the report into the install of the project that call names.

------
----
+ session_diagnostics(): str
+ write_to(diagnostics: InstallDiagnostics): str
	-> SessionProbe.run
---<<writes a section of>>--> InstallDiagnostics
---<<runs>>--> Generate
---<<runs>>--> Validate
---<<annotated with>>--> AgentToolSetAnnotation
---<<annotated with>>--> Mcp
---<<annotated with>>--> Skill
---<<annotated with>>--> Command

# space/kanban

The *Board* shows every session as a *Ticket* in a *Column*: Backlog, a *Stage*, or Complete. A ticket holds three parts made once: its *TicketWork* (its *FidelityProgress* on each fidelity the board requires), its *TicketCheckout* (its branch, worktree, and chat), and its *StageMarks* (the moves and marks a person made). A *BacklogItem* is an idea not yet started, and a *Report* is the rules a validation found broken, read from a *ReportFile*. No Python module imports this one; the Session Board app and the chat bar reach these classes through their MCP tools and TypeScript adapters. The whole model of this module, internals included, is `space/kanban/.context/kanban-model.md`; that document is canonical, and this section shows only the classes those tools publish.

- **Purpose:** See every session's progress through the delivery stages, and move sessions through them, from an agent's tools or from the Session Board app.
- **Seam (terms):** Board, Column, Stage, Card, Ticket, TicketWork, TicketCheckout, StageMarks, FidelityProgress, StageWork, LeaveChoices, OpenChoices, BacklogItem, Report, ReportFile, Help, BoardOverview, FormatChoice
- **Dependencies (one-way):** harness/annotations, harness/agent_tools, harness/installation, harness/mcp, harness/markdown, harness/guidance, harness/graph, harness/diagnostics, harness/chat, harness/catalog_generator, space/repo, space/session

## Board

Show every work session as a ticket on a kanban: Backlog, Discovery, Specification, Implementation, and Complete.

+ Board(repo: Repo, practices: BoardPractices)
------
+ << association >> repo: Repo
+ << association >> sessions: Sessions
+ << association >> catalogued_practices: BoardPractices
+ file: Path
+ project: str
+ worktrees: dict[Branch, Worktree]
+ practices: list[PracticeGuidance]
+ << composition >> columns: list[Column]
+ stages: list[Stage]
+ fidelities: list[BoardFidelity]
+ chats: list[Chat]
+ tickets: list[Ticket]
+ backlog_items: list[BacklogItem]
+ cards: list[Card]
+ open_tickets: list[Ticket]
+ active: Ticket | None
----
+ places_cards(ticket_kind: type[Ticket], backlog_item_kind: type[BacklogItem]): None
	// the kanban package hands the board its card classes when imported, so board.py imports neither ticket.py nor backlog_item.py
+ load(project: Path | str): Board
	-> Sessions.of_project
	-> Sessions.open_state
+ wip_limit(stage: Stage): int
+ set_wip_limit(stage: Stage, limit: int): None
+ stage(name: str): Stage
+ ticket_of(session: Session): Ticket
+ make_ticket(session: Session): Ticket
+ make_backlog_item(path: Path): BacklogItem
+ backlog_item_of(ticket: Ticket): BacklogItem
+ reread(): None
+ column(name: str): Column
+ ticket(name: str): Ticket | None
+ backlog_item(title: str): BacklogItem | None
+ open_ticket(title: str, scope: str, parent: str, path: str): Ticket
	-> Sessions.create
+ show(): Board
+ open_main(leaving: list[str] | None = None): BoardOverview
	-> Ticket.leave_for_another
	-> Branch.check_out
	-> Sessions.switch
+ overview(): BoardOverview
+ folders(path: str = ''): list[str]
+ help(practice: str): Help
	-> BoardPractices.keyed
---<<reads tickets, backlog items, chats, and worktrees once per read through>>--> BoardReads
---<<lists connected chats from>>--> Chat
---<<lists checkouts of>>--> Worktrees
---<<saves the open worktree and branch in>>--> WorkState
---<<calls all on>>--> Sessions
---<<creates>>--> Stage
---<<creates>>--> Ticket
---<<creates>>--> BacklogItem
---<<creates>>--> BoardOverview
---<<creates>>--> Help
---<<reads and writes WIP limits in>>--> JsonFile
---<<registers the board app's port with>>--> ServerHealth
---<<annotated with>>--> LanguageAdapter
---<<annotated with>>--> AgentToolSetAnnotation
---<<annotated with>>--> ToolSubject
---<<annotated with>>--> Mcp
---<<annotated with>>--> LongCall
---<<annotated with>>--> NoSessionLog

## Column

*Column* is one place on the board: Backlog, a stage, or Complete.

+ Column(name: str, kind: str, board: Board)
------
+ name: str
+ kind: str
+ << aggregation >> cards: list[Card]
----
---<<reads cards of>>--> Board
---<<annotated with>>--> Identity

## Stage : Column

Show one stage of the board, the tickets at work in it, and how many it takes before it is over its limit.

+ Stage(approach: ApproachStage, board: Board)
------
+ steps: list[str]
+ << association >> scope: StageScope
+ actions: list[str]
+ producing_actions: list[str]
+ actions_with_formats: list[str]
+ work_required: list[FidelityGuidance]
+ next_stage: Stage | None
+ previous_stage: Stage | None
+ wip_limit: int
+ is_over_limit: bool
+ in_progress: list[Ticket]
+ done: list[Ticket]
----
+ load(stage: str, project: Path | str): Stage
	-> Board.load
+ requires(fidelity: FidelityGuidance): bool
+ set_wip_limit(limit: int): Stage
	-> Board.set_wip_limit
---<<reads title of>>--> ApproachStage
---<<reads steps of>>--> ApproachStage
---<<annotated with>>--> LanguageAdapter
---<<annotated with>>--> AgentToolSetAnnotation
---<<annotated with>>--> Mcp

## Card : ABC

*Card* is anything on the board that a person moves: a ticket or a backlog item.

+ Card(board: Board)
------
+ board: Board
+ title: str
+ column: Column
+ last_activity: str
----
+ move_next(): Card
+ move_previous(): Card

## Ticket : Card

Show one work session as a unit of delivery and move it through the stages. Its tools and data fields stay on it, so their published names do not change; the work behind them is done by its three parts.

+ Ticket(session: Session, board: Board)
------
+ name: str
+ title: str
+ << association >> session: Session
+ << composition >> work: TicketWork
+ << composition >> checkout: TicketCheckout
+ << composition >> marks: StageMarks
+ is_main: bool
+ progress: list[FidelityProgress]
+ column: Column
+ is_closed: bool
+ is_active: bool
+ drop_targets: list[str]
+ is_done: bool
+ next_fidelity: FidelityProgress | None
+ agent_context: str
+ last_activity: str
+ worktree: str
+ << association >> chat: Chat | None
	// published as working_chat: the chat a person assigned, else the one named after the ticket, else the one in its worktree
+ stage_work: list[StageWork]
----
+ load(ticket: str, project: Path | str): Ticket
	-> Board.load
+ create(title: str, scope: str = 'feature', parent: str = '', path: str = '', project: Path | str): Ticket
	-> Board.open_ticket
+ branch(): Branch
+ work_branch(): Branch
+ assign_chat(chat: str = ''): Ticket
	-> TicketCheckout.assign_chat
+ format_choices(fidelities: list[str]): list[FormatChoice]
	-> TicketWork.progress_of
	-> FormatChoice.offered_by
+ close_choices(): LeaveChoices
+ leave_choices(): LeaveChoices
+ open_choices(): OpenChoices
+ activate(leaving: list[str] | None = None, opening: list[str] | None = None): Ticket
	-> leave_for_another
	-> TicketCheckout.open
	-> Sessions.switch
+ leave_for_another(leaving: list[str]): None
	-> TicketCheckout.leave
+ open_worktree(): Ticket
	-> TicketCheckout.open_worktree
+ move_next(): Ticket
	-> StageMarks.mark
	-> StageMarks.enter
+ move_previous(): Ticket | BacklogItem
	-> Session.reopen
	-> StageMarks.place
+ move_to(stage: str, done: bool = False): Ticket | BacklogItem
	-> StageMarks.place
+ close(leaving: list[str] | None = None): Ticket
	-> TicketCheckout.write_handoff
	-> TicketCheckout.free_worktree
	-> Session.move_to_closed
	-> TicketCheckout.save_work
	-> TicketCheckout.return_to_default_branch
+ archive(): Ticket
	-> Session.move_to_archive
+ violations(): Report
	-> FidelityProgress.report
	-> Report.from_reports
---<<moves back to the Backlog as>>--> BacklogItem
---<<closes>>--> Session
---<<raises>>--> MainStaysOpenError
---<<annotated with>>--> Identity
---<<annotated with>>--> LanguageAdapter
---<<annotated with>>--> AgentToolSetAnnotation
---<<annotated with>>--> ToolSubject
---<<annotated with>>--> Mcp
---<<annotated with>>--> LongCall
---<<annotated with>>--> NoSessionLog

## TicketWork

A ticket's progress on each fidelity the board requires whose practice its session holds, in stage order: read from its session's log once per ticket read, and read again after the ticket writes a line.

+ TicketWork(ticket: Ticket)
------
+ << composition >> progress: list[FidelityProgress]
+ enabled: list[FidelityProgress]
----
+ progress_of(slug: str): FidelityProgress
+ in_stage(stage: Stage): StageWork
+ command(action: str, fidelities: list[FidelityGuidance]): str
+ record(line: str): None
	-> SessionLog.record
---<<creates>>--> FidelityProgress
---<<creates>>--> StageWork
---<<reads entries of>>--> SessionLog
---<<asks which fidelities it requires>>--> Stage
---<<raises>>--> FidelityNotFoundError

## TicketCheckout

Where one ticket's work sits in git: its own branch, the worktree that branch is open in, and the chat working there. It answers what opening and leaving the ticket can do now and does it, so a dialog offers only what will be done.

+ TicketCheckout(ticket: Ticket)
------
+ << association >> branch: Branch
+ candidate_branches: list[Branch]
+ work_branch: Branch
+ worktree: str
+ << association >> chat: Chat | None
+ assigned_chat: str
+ leave_choices: LeaveChoices
+ close_choices: LeaveChoices
+ open_choices: OpenChoices
----
+ assign_chat(chat: str): None
	-> Session.save_fields
+ open(opening: list[str]): None
	-> Repo.switch_worktree
	-> Repo.switch_branch
+ open_worktree(): None
	-> Branch.open_in_worktree
+ leave(leaving: list[str]): None
+ write_handoff(leaving: list[str]): None
+ save_work(leaving: list[str]): None
	-> Branch.land_on_default
	-> Branch.delete
+ free_worktree(leaving: list[str]): None
	-> Worktree.close
+ return_to_default_branch(): None
---<<writes>>--> LeavingHandoff
---<<creates>>--> LeaveChoices
---<<creates>>--> OpenChoices
---<<finds its chat among>>--> Chat
---<<reads branch and chat recorded in>>--> Session

## LeaveChoices

What leaving a ticket for another, or closing it, can do with its work now, in the order it is done, with those chosen at first.

+ LeaveChoices(branch: Branch | None, own_branch: Branch | None)
------
+ branch: str
+ own_branch: str
+ choices: list[str]
+ chosen: list[str]
----

## OpenChoices

What opening a ticket can create for it now: its own branch while the repository has none, and its own worktree while it has none.

+ OpenChoices(branch: Branch, worktree: str, candidate_branches: list[str])
------
+ has_branch: bool
+ candidate_branches: list[str]
+ choices: list[str]
+ chosen: list[str]
----

## StageMarks

The moves and marks a person made on one ticket's stages, as its session's log answers them: the stage it was last moved into, and in a stage whether it was last marked done or in progress since entering it.

+ StageMarks(ticket: Ticket)
------
+ moved_into: Stage | None
----
+ latest_in(stage: Stage): str | None
	-> SessionLog.latest
+ enter(stage: Stage): Ticket
+ mark(mark: str, stage: Stage): Ticket
	-> TicketWork.record
+ place(stage: Stage, mark: str): Ticket

## BacklogItem : Card

Hold an idea not yet started. Starting it opens a ticket for it.

+ BacklogItem(path: Path, board: Board)
------
+ path: Path
+ path_from_project: str
+ title: str
+ column: Column
+ ticket: str
+ text: str
+ last_activity: str
----
+ load(backlog_item: str, project: Path | str): BacklogItem
	-> Board.load
+ create(title: str, text: str = '', project: Path | str): BacklogItem
+ from_ticket(ticket: Ticket): BacklogItem
+ write_if_missing(title: str): None
+ start(scope: str = 'feature', path: str = ''): Ticket
	-> Session.keep_file
+ move_next(): Ticket
+ move_previous(): BacklogItem
---<<creates>>--> Name
---<<creates>>--> Ticket
---<<raises>>--> BacklogItemNotFoundError
---<<annotated with>>--> Identity
---<<annotated with>>--> LanguageAdapter
---<<annotated with>>--> AgentToolSetAnnotation
---<<annotated with>>--> Mcp

## FidelityProgress

*FidelityProgress* is how far one fidelity has got through its stage's actions on one ticket.

+ FidelityProgress(fidelity: FidelityGuidance, stage: Stage, done_actions: list[str], has_violations: bool, ticket: Ticket)
------
+ ticket: Ticket
+ << association >> fidelity: FidelityGuidance
+ stage: Stage
+ practice: PracticeGuidance
+ is_enabled: bool
+ done_actions: list[str]
+ remaining_actions: list[str]
+ next_action: str
+ commands: dict[str, str]
+ allowed_actions: list[str]
+ has_violations: bool
+ is_done: bool
+ state: str
+ action_states: ActionStates
+ report_file: str
+ latest_report: ReportFile | None
+ violation_count: int
----
+ from_log(fidelity: FidelityGuidance, stage: Stage, entries: list[LogEntry], ticket: Ticket): FidelityProgress
+ load(ticket: str, fidelity: str, project: Path | str): FidelityProgress
	-> Ticket.load
	-> TicketWork.progress_of
+ command(action: str): str
	-> TicketWork.command
+ finish_review(): FidelityProgress
	-> TicketWork.record
+ report(): Report
	-> ReportFile.report
+ help(): Help
	-> BoardPractices.of
+ files(): dict[str, list[FileEntry]]
	-> FidelityGuidance.files
+ with_violations(): FidelityProgress
---<<reads lines from>>--> LogEntry
---<<finds its latest report through>>--> ReportFile
---<<creates>>--> ActionStates
---<<creates>>--> Help
---<<lists the declared files as>>--> FileEntry
---<<annotated with>>--> Identity
---<<annotated with>>--> LanguageAdapter
---<<annotated with>>--> AgentToolSetAnnotation
---<<annotated with>>--> ToolSubject
---<<annotated with>>--> Mcp

## StageWork

A ticket's work in one stage taken together, for a stage head's action bar.

+ StageWork(ticket: Ticket, stage: Stage, progress: list[FidelityProgress])
------
+ stage: Stage
+ << aggregation >> progress: list[FidelityProgress]
+ action_states: ActionStates
+ has_violations: bool
+ violation_count: int
+ commands: dict[str, str]
+ allowed_actions: list[str]
----
---<<takes action states together with>>--> ActionStates

## Report

The rules a validation found broken. With no report it is empty, and it says when it has no saved graph, or its saved graph is in a shape the graph no longer writes, because the graph's rules are then missing from it.

+ Report(path: str = '', text: str = '', rules: list[ReportRule] | None = None, has_saved_graph: bool = False, is_out_of_date: bool = False)
------
+ path: str
+ text: str
+ << composition >> rules: list[ReportRule]
+ has_saved_graph: bool
+ is_out_of_date: bool
+ violation_count: int
----
+ from_reports(folder: str, reports: list[Report]): Report

## ReportFile

A validation report of one fidelity, saved in a session folder, with the graph the validation checked saved beside it. It knows which of its practice's rules it answers for.

+ ReportFile(file: Path, fidelity: FidelityGuidance)
------
+ file: Path
+ stamp: str
+ text: str
+ has_result: bool
+ is_judged_failing: bool
----
+ from_fidelity(fidelity: FidelityGuidance): ReportFile | None
	-> FidelitySessionOutput.reports
+ report(): Report
---<<reads the saved graph through>>--> SavedGraph
---<<reads the agent's judgment as>>--> Judgment
---<<creates>>--> ReportRule
---<<creates>>--> Report
---<<creates>>--> Violation

# tools

*Tools* are standalone toolsets an agent or an application calls beside the practices: *SubAgent* hands work to a background sub-agent, *Echo* shows an action's instructions inside a do-not-follow fence, *Granola* files meeting notes and writes the ones that matter as `.context` files, *PromptLog* writes what crossed to the model into the open session's logs, and *PromptNotify* shows a toast naming the guidance a tool call used. Each sits in its own package (`tools/sub_agent`, `tools/echo`, `tools/granola`, `tools/prompt_log`, `tools/prompt_notify`) and imports none of the others; they share one card, `tools/.context/module-context.md`. `tools/drawio_viewer` is a small local web server beside them, not a toolset, and imports nothing from the framework. Nothing in the framework imports this module. The whole model of PromptNotify, internals included, is `tools/prompt_notify/.context/prompt-notify-model.md`; that document is canonical for it.

- **Purpose:** Hold the toolsets that are useful on their own, outside any one practice or action: delegating to a sub-agent, reading what an action instructs, filing meeting notes as context, and showing and logging what crosses to the model.
- **Seam (terms):** SubAgent, Echo, Granola, PromptLog, PromptNotify, ToastFile
- **Dependencies (one-way):** harness/annotations, harness/agent_tools, harness/installation, harness/hooks, harness/mcp, harness/guidance, space/session

## SubAgent

Launch a non-blocking sub-agent with custom instructions, and continue the current conversation without waiting for it.

------
----
+ sub_agent(instructions: str, summary: str = ''): str
	// never called from inside the sub-agent it launched
---<<opens its instructions with>>--> SUB_AGENT_CALLER_PREAMBLE
---<<annotated with>>--> AgentToolSetAnnotation
---<<annotated with>>--> Mcp
---<<annotated with>>--> Skill
---<<annotated with>>--> AgentInstructionsAnnotation

## Echo

Echo wrapped action instructions inside a DO-NOT-FOLLOW fence so the user can inspect them.

------
----
+ fence(body: str): str
+ echo_session(): str
---<<annotated with>>--> AgentToolSetAnnotation
---<<annotated with>>--> Mcp
---<<annotated with>>--> Skill
---<<annotated with>>--> NoCatalog

## Granola

Organize Granola notes into folders and capture notes as independent .context files, in the project the call works on.

+ Granola(project: Path | str)
------
+ root: Path
----
+ of_project(project: Path): Granola
+ format_filing_plan(plan: str): str
+ list_note_context(folder: str): str
+ write_note_context(folder: str, note_id: str, title: str, date: str, url: str, content: str): str
+ organize(scope: str = 'unfiled'): str
+ context(notes: str, folder: str): str
---<<creates>>--> Name
---<<writes under>>--> CONTEXT_FOLDER
---<<annotated with>>--> AgentToolSetAnnotation
---<<annotated with>>--> ToolSubject
---<<annotated with>>--> Mcp
---<<annotated with>>--> Skill

## PromptLog

Audit what the IDE sends the model — one `@Hook` per event, each writing that event's entry to the log: the file the toolset was made with, else `prompt-log.txt` in the logs folder of the session the event works in.

+ PromptLog(log: Path | None = None)
------
----
+ log_for(payload: HookPayload): HookLog
	-> HookPayload.session
	-> Session.hook_log
+ before_submit_prompt(payload: HookPayload): dict
+ before_read_file(payload: HookPayload): dict
+ pre_tool_use(payload: HookPayload): dict
+ subagent_start(payload: HookPayload): dict
+ after_agent_response(payload: HookPayload): dict
---<<writes entries as>>--> PromptLogEntry
---<<appends to>>--> HookLog
---<<stamps entries with>>--> LogTimestamp
---<<asks the installed guidance kind of>>--> IdeLayout
---<<reads invoked tool of>>--> HookPayload
---<<annotated with>>--> AgentToolSetAnnotation
---<<annotated with>>--> Hooks
---<<annotated with>>--> Hook
---<<annotated with>>--> NoCatalog

## PromptNotify

Echo detected action, practice, fidelity, and rule names on preToolUse.

------
+ catalog: list[tuple[str, str]]
+ echo_toolsets: list
----
+ on_pre_tool_use(payload: HookPayload): dict
+ handle(payload: HookPayload, toolsets: list | None = None): dict
+ detect_echo(payload: HookPayload, toolsets: list | None = None): tuple[str, str] | None
+ detect(payload: HookPayload): tuple[str, str] | None
+ show_toast(toast: str, workspace_roots: list[Path]): list[Path]
	// registered with HookServer.show_toasts_with when the module is loaded, so the toast a hook gives in its result is shown here
+ show_ide_toast(echo: str, workspace_roots: list[Path | str]): list[Path]
	-> ToastFile.show
+ install_ide_toast_extension(): Path
---<<lists action names from>>--> ActionCatalogue
---<<lists practices from>>--> PracticeCatalogue
---<<loads the running checkout's toolsets from>>--> RepositoryToolsets
---<<loads>>--> AgentToolSet
---<<asks the installed guidance kind of>>--> IdeLayout
---<<reads workspace roots of>>--> HookPayload
---<<reads invoked tool of>>--> HookPayload
---<<registers its toaster with>>--> HookServer
---<<joins rule toasts with>>--> rules_toast
---<<creates>>--> Name
---<<creates>>--> ToastFile
---<<toasts the calls annotated>>--> Toast
---<<annotated with>>--> AgentToolSetAnnotation
---<<annotated with>>--> Hook
---<<annotated with>>--> NoCatalog

## ToastFile

The toast notice of one workspace folder, `.cursor/prompt-notify-toast.json`, which the IDE toast extension shows. A toast written within a moment of the last one joins it, so a burst of tool calls shows as one toast.

+ ToastFile(folder: Path)
------
+ path: Path
----
+ show(message: str, now: datetime): Path
---<<reads and writes>>--> JsonFile
---<<stamps the toast with>>--> LogTimestamp

# cdd_guidance/actions

Each action is a *GuidanceAction*: *Generate*, *Validate*, *Document*, *Render*, *Satisfy*, *Sketch*, *Partition*, *Iterate*, *GrillContext*, *Improvement* (repair), and *Diagnose*. Importing the package registers every action folder's toolset with *ActionCatalogue*, and registers the practices first, since the actions work on them. The saved sketch is read by *SketchOutline* in cdd_guidance/practices/sketch_document, and each practice's section of it is a *SketchLens* in harness/guidance; neither lives here any more.

- **Purpose:** Give every practice the same generate, document, validate, satisfy, render, sketch, partition, grill, iterate, repair, and diagnose steps, so a practice owns only its words, rules, and formats.
- **Seam (terms):** Generate, Validate, Document, Render, Satisfy, Sketch, Partition, Iterate, GrillContext, Improvement, Diagnose
- **Dependencies (one-way):** harness/annotations, harness/agent_tools, harness/markdown, harness/guidance, harness/guidance_actions, harness/installation, harness/mcp, harness/graph, cdd_guidance/practices (the package, which registers the practices)

## Generate : GuidanceAction

Write the artifacts each listed guidance asks for at its current fidelity.

------
----
+ generate(guidance: GuidanceArg): str
	-> GuidanceAction.run
+ generate_fixes_from_validate(): str
---<<creates>>--> Format
---<<reads fidelities of>>--> PracticeGuidance
---<<renders the earlier fidelity with>>--> Render
---<<lists as a tool>>--> Validate

## Validate : GuidanceAction

Check artifacts against each listed guidance's rules, add the graph rules' hits, and save the report.

+ Validate(session = None, call = None)
------
----
+ validate(guidance: GuidanceArg, rule: Rule | None = None, graph: bool | str | list[str] | None = None, paths: list[str] | None = None): str
+ create_rule(guidance: GuidanceArg, failed: str = '', wanted: str = ''): str
---<<validates with>>--> Rule
---<<reads the saved graph with>>--> SavedGraph
---<<annotated with>>--> NoDeploy
---<<annotated with>>--> Skill

## Document : GuidanceAction

Record what already exists for each listed guidance without correcting it.

------
----
+ document(guidance: GuidanceArg, paths: list[str]): str
---<<annotated with>>--> Skill

## Render : GuidanceAction

Convert already-generated content into another format.

------
----
+ render(guidance: GuidanceArg, format: str, paths: list[str] | str, content: str = '', source: str | None = None): list
	-> GuidanceAction.document_named
+ place_rendered(): str

## Satisfy : GuidanceAction

Validate, fix from the report, and validate again.

------
----
+ satisfy(guidance: GuidanceArg): str
---<<lists as a tool>>--> Validate
---<<reads generate fixes from validate of>>--> Generate

## Sketch : GuidanceAction

Sketch a solution interactively before generating the formal artifact.

+ Sketch(agent_dir: str = '', session = None, call = None)
------
+ sketch_template: str
----
+ made_for(session, call = None): Sketch
+ find_template(agent_dir: str = ''): str
+ save_sketch(content: str = '', paths: list[str] | str | None = None, module: str = ''): str
+ list_sketches(module: str = ''): str
+ review_sketch(): str
+ sketch(guidance: GuidanceArg): str
---<<grills with>>--> GrillContext
---<<ends with the recipe of>>--> Generate

## Partition : GuidanceAction

Split a corpus into an index and verbatim segments.

------
----
+ verify_segment_completeness(segment_path: str, expected_names: str = '', min_body_chars: int = MIN_ENTRY_BODY_CHARS, index_path: str = ''): str
+ partition_guidance(): str
+ index(context: str = '', out_root: str | None = None, paths: list[str] | str | None = None): str
+ segment(out_root: str | None = None): str
+ segment_files(out_root: str | None = None): list[str]
+ partition(guidance: GuidanceArg, context: str = '', mode: str = 'one_go', out_root: str | None = None, paths: list[str] | str | None = None): str

## Iterate : GuidanceAction

Grill, then generate and validate one small slice at a time.

------
----
+ mark_iterate_round(): str
+ iterate(guidance: GuidanceArg): str
---<<grills with>>--> GrillContext

## GrillContext : GuidanceAction

Interview a plan relentlessly against the codebase context until reaching shared understanding.

------
----
+ explore_context_files(folder: str = ''): str
+ read_context_file(path: str): str
+ write_grill_answer(heading: str, body: str): str
+ grill(guidance: GuidanceArg): str
+ grill_with_context(plan: str = '', paths: list[str] | str | None = None): str
---<<generates each answer with>>--> Generate

## Improvement : GuidanceAction

Repair a guidance's artifact for one violation, and re-check a repair theme.

------
----
+ repair_loop(): str
+ repair(guidance: GuidanceArg, asset: str = '', violation: str = ''): str
+ verify_fix(guidance: GuidanceArg, theme: str): str
---<<diagnoses with>>--> Diagnose
---<<annotated with>>--> Mcp

## Diagnose : GuidanceAction

Disciplined diagnosis loop for hard bugs and performance regressions.

------
----
+ diagnose(guidance: GuidanceArg | None = None): str
---<<annotated with>>--> SubAgentAnnotation
---<<annotated with>>--> NoCatalog

# cdd_guidance/practices/sketch_document

*SketchOutline* is the saved sketch read as a document: a header, then one section per practice, each opened by a heading that practice's *SketchLens* opens. *DiscoveryDocument* is the document a practice writes at discovery fidelity from a sketch. It sits below both the practices and the actions, so a practice reads a sketch without importing the Sketch action.

- **Purpose:** Give every practice one reader of the saved sketch, below both the practices and the actions, so a practice reads a sketch without importing the Sketch action.
- **Seam (terms):** SketchOutline, DiscoveryDocument
- **Dependencies (one-way):** harness/guidance

## SketchOutline

A sketch whose hierarchy is carried by markdown headings above fenced detail.

+ SketchOutline(text: str, nesting_indent: int = 2)
------
+ title: str
+ sources: str
----
+ holds(lens: SketchLens): bool
+ body_for(lens: SketchLens): str
	// any practice's lens heading ends the section before it, so every practice is asked for its lens
---<<lists every lens with>>--> PracticeCatalogue
---<<calls opens on>>--> SketchLens

## DiscoveryDocument

A discovery document written from a sketch: its artifact, its heading, and the sketch's title and sources.

+ DiscoveryDocument(artifact: str, heading: str, sketch: str)
------
+ artifact: str
+ heading: str
+ title: str
+ sources: str
----
+ lines(body: str): list[str]
---<<reads title and sources of>>--> SketchOutline

# cdd_guidance/practices/clean_engineering

*CleanEngineering* is the practice; its *GraphReading* is its part in the knowledge graph, reading the code and then the model documents. *CleanEngineeringModel* is the one class model every format reads and writes (modules, classes, properties, operations, relationships); *CodeCleanEngineeringModel* is that model written as code; *CodeLanguage*, *CodeBody*, *WrittenBlock*, *BraceCall*, and *BracketStructure* are what every code format shares; *CallGraph* is an indented call graph; *SourceText* is a span of source and what the rules measure in it; *Drawio* draws the model as a class diagram, through *DrawIOCleanEngineeringModel* and its *DrawIOModule* cards. The whole model of this module, internals included, is `cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md` and `cdd_guidance/practices/clean_engineering/model/drawio/.context/drawio-model.md`; those documents are canonical, and this section shows only the classes other modules use.

- **Purpose:** Keep boundaries, types, and code consistent, so a change stays inside one module instead of spreading to every caller.
- **Seam (terms):** CleanEngineering, GraphReading, CleanEngineeringModel, Module, OoadClass, Property, Operation, Relationship, CodeCleanEngineeringModel, PythonCleanEngineeringModel, TypeScriptCleanEngineeringModel, CodeLanguage, CodeBody, WrittenBlock, BraceCall, BracketStructure, CallGraph, CallGraphEntry, SourceText, Drawio, DrawIOCleanEngineeringModel, DrawIOModule
- **Dependencies (one-way):** harness/annotations, harness/agent_tools, harness/markdown, harness/guidance, harness/installation, harness/graph, cdd_guidance/practices/sketch_document

## CleanEngineering : PracticeGuidance

The Clean Engineering practice: modules, model, and code.

+ CleanEngineering(fidelity: str = 'modules', format: str | None = None)
------
+ reading_type: type
	// GraphReading
+ model_document_format: type
	// MarkdownCleanEngineeringModel
+ << composition >> drawio: Drawio
----
+ generate_output(): str
---<<renders>>--> Drawio
---<<creates>>--> Drawio
---<<reads the graph with>>--> GraphReading
---<<registers with>>--> OoadNode

## GraphReading : PracticeReading

How Clean Engineering takes part in the graph: it reads the code, then the model documents; every practice that links to the code asks its code index.

+ GraphReading(practice: PracticeGuidance)
------
+ class_types: tuple[str, ...]
+ code_index: CodeIndex
+ model_documents: ModelDocuments
----
+ read_working_copy(): None
---<<creates>>--> CodeIndex
---<<creates>>--> ModelDocuments

## CleanEngineeringModel : OoadNode

One class model that every format reads and writes: modules holding classes.

+ CleanEngineeringModel(name: str | Graph = '', sequential_order: int = 1, graph: Graph | None = None)
------
+ module_type: type
+ << composition >> modules: list[Module]
+ is_modules_view: bool
----
+ described_member(owner: str, name: str): Operation | Property | None
+ every_class(): list[OoadClass]
+ as_record(): dict
+ update_self(source: OoadNode): None
+ clone(): CleanEngineeringModel
+ save(): str
+ parse(text: str): CleanEngineeringModel
+ load_module(source: Module): Module
+ reconcile_children(source: OoadNode): None
---<<creates>>--> Module
---<<keeps>>--> Module
---<<keeps>>--> OoadClass

## Module : OoadNode

A named module boundary grouping closely related classes.

+ Module(name: str, sequential_order: int, description: str = '', seam: str = '', constraint: str = '', seam_terms: list[str] | None = None, dependencies: list[str] | None = None, graph: Graph | None = None)
------
+ class_type: type
+ description: str
+ seam: str
+ constraint: str
+ seam_terms: list[str]
+ dependencies: list[str]
+ imported_names: list[str]
+ modules: list[Module]
+ << composition >> classes: list[OoadClass]
+ path_parent: str | None
+ documentation: str
----
+ as_record(): dict
+ external_deps(): list[str]
+ public_terms(): list[str]
+ update_self(source: OoadNode): None
+ clone(): Module
+ load_module(source: Module): Module
+ load_class(source: OoadClass): OoadClass
+ take_lines(text: str): None
+ load_source_facts(file: Path, root: Path): None
+ import_targets(file: Path, root: Path): list[str]
+ load_folder_facts(folder: Path): None
+ holds_public_source(file_name: str): bool
+ take_public_sources(sources: list[Module]): None
+ reconcile_children(source: OoadNode): None
---<<creates>>--> OoadClass
---<<keeps>>--> OoadClass

## OoadClass : OoadNode

A class in the model: what it remembers, what it does, and how it relates.

+ OoadClass(name: str, sequential_order: int, intent: str = '', properties: list[Property] | None = None, operations: list[Operation] | None = None, relationships: list[Relationship] | None = None, collaborators: list[str] | None = None, line: int | None = None, graph: Graph | None = None)
------
+ property_type: type
+ operation_type: type
+ intent: str
+ stereotypes: list[str]
+ module_path: list[str]
+ bases: list[str]
+ collaborators: list[str]
+ dependencies: list[Relationship]
+ << composition >> properties: list[Property]
+ << composition >> operations: list[Operation]
+ public_properties: list[Operation | Property]
+ relationships: list[Relationship]
+ composes_peers: bool
+ held_fields: dict[str, str]
----
+ take_lines(lines: list[str]): None
+ doc_comment(marked: bool): DocComment
+ load_source_facts(): None
+ declared_bases(known_names: Iterable[str]): list[str]
+ update_self(source: OoadNode): None
+ clone(): OoadClass
+ as_record(): dict
+ load_relationship(source: Relationship): Relationship
+ load_property(source: Property): Property
+ load_operation(source: Operation): Operation
+ reconcile_children(source: OoadNode): None
+ declares(member: OoadNode): bool
+ place_relationship(relationship: Relationship): None
+ depend_on(target: str, label: str): None
---<<keeps>>--> Operation
---<<keeps>>--> Property
---<<keeps>>--> Relationship

## Property : InvariantHolder, OoadNode

Something a class remembers or derives, with its relationship when its type names a domain class.

+ Property(name: str, sequential_order: int = 0, type_hint: str = '', description: str = '', graph: Graph | None = None)
------
+ type_hint: str
+ description: str
+ value_type: str
+ owner: str
+ relationship: Relationship | None
----
+ from_signature(text: str): Property | None
+ keep_owner(): None
+ clone(): Property
+ take_note(text: str): None
+ take_relationship(relationship: Relationship): None
+ take_drawn_kind(kind: str): None
+ notes(): list[str]
+ derive_relationship(): None
+ save(): str
+ render(): str
+ as_record(): dict
+ update_self(source: OoadNode): None
---<<keeps>>--> Relationship

## Operation : InvariantHolder, OoadNode

Something a class does: its parameters, return, interactions, and invariants.

+ Operation(name: str, sequential_order: int = 0, return_type: str = '', description: str = '', callees: list[str] | None = None, parameters: list[str] | None = None, **fields)
------
+ return_type: str
+ callees: list[str]
+ << composition >> body: CodeBody
+ body_text: str
+ owner: str
+ parameters: list[Parameter]
+ is_constructor: bool
+ is_property: bool
+ value_type: str
+ source_lines: tuple[int, int]
----
+ from_signature(text: str): Operation | None
+ attach(child, kind: str): None
+ keep_owner(): None
+ clone(): Operation
+ take_body(text: str, language): None
+ take_lines(lines: list[str]): None
+ load_span_facts(): None
+ save(): str
+ render(): str
+ as_record(): dict
+ update_self(source: OoadNode): None
+ load_parameter(source: Parameter): Parameter
+ reconcile_children(source: OoadNode): None
---<<creates>>--> CodeBody

## Relationship

One line from a class to another: its target, its kind, and its label.

------
+ target: str
+ kind: str
+ cardinality: str
+ description: str
+ sequential_order: int
+ label: str
+ details: dict[str, str]
+ name: str
----
+ read_line(line: str): Relationship | None
+ split_off(lines: list[str]): tuple[list[str], list[Relationship]]
+ read_lines(lines: list[str]): list[Relationship]
+ line(): str
+ lines(): list[str]
+ as_record(): dict[str, Any]
+ translate_from(source: Relationship): None
+ update_self(source: Relationship): None
+ clone(): Relationship

## CodeCleanEngineeringModel : CleanEngineeringModel

A class model written as code; the Python, TypeScript, JavaScript, and Java formats each spell their own lines.

------
+ << association >> language: CodeLanguage
+ suffixes: tuple
+ class_type: type
+ operation_type: type
+ property_type: type
----
+ file_module(): Module
+ render(canonical: CleanEngineeringModel, previous: str | None = None): str
+ operation_body(class_name: str, operation_name: str): CodeBody
+ render_class(oclass: CodeClass, known_names: list[str], kept: CodeCleanEngineeringModel): list[str]
+ render_operation(oclass: CodeClass, operation: CodeOperation, previous: CodeBody): list[str]
+ render_body(operation: Operation, previous: CodeBody): list[str]
+ file_header(preamble: CodeBody): list[str]
---<<creates>>--> CodeBody

## PythonCleanEngineeringModel : CodeCleanEngineeringModel

The Python format of the class model; DDD names it as its own python format.

------
----
+ parse(text: str): PythonCleanEngineeringModel
+ file_header(preamble: CodeBody): list[str]

## TypeScriptCleanEngineeringModel : BraceCleanEngineeringModel

The TypeScript format of the class model; DDD names it as its own typescript format.

------
----

## CodeLanguage

How one programming language spells what every code format writes the same way. `PYTHON`, `TYPESCRIPT`, and `JAVASCRIPT` are its instances other modules import.

+ CodeLanguage(name: str, line_comment: str, indent: str, unfinished: str, spelling: CodeSpelling, type_names: dict[str, str], suffixes: tuple[str, ...] = ())
------
+ name: str
+ suffixes: tuple[str, ...]
+ line_comment: str
+ indent: str
+ unfinished: str
----
+ comment(text: str): str
+ is_unfinished(text: str): bool
+ identifier(name: str): str
+ type_name(hint: str): str
+ interaction(callee: str): str
+ assignment(name: str): str

## CodeBody

The statements inside one operation, test, or step, kept with the language they were read in.

+ CodeBody(text: str = '', language: CodeLanguage | None = None)
------
+ text: str
+ << association >> language: CodeLanguage | None
+ is_empty: bool
	// a body that is unfinished in its language is empty
----
+ mentions(word: str): bool
+ lines_in(language: CodeLanguage, indent: str, unfinished: str): list[str]
+ in_language_of(other: CodeBody, language: CodeLanguage): CodeBody
---<<calls is_unfinished on>>--> CodeLanguage
---<<calls comment on>>--> CodeLanguage

## WrittenBlock

The source lines around one block of code that no node holds, kept exactly as read, under a `WrittenKey`.

+ WrittenBlock(language: CodeLanguage, key: WrittenKey, lead: list[str], heading: list[str])
------
+ << association >> language: CodeLanguage
+ key: WrittenKey
+ heading: list[str]
+ lead: list[str]
+ closing: list[str]
+ inside: list[str]
+ inline: str
----
+ is_in(language: CodeLanguage, key: WrittenKey): bool
+ split_inside(lines: list[str], inside: tuple[int, int], children: list[tuple[int, int]]): tuple[list[str], list[list[str]], list[str]]
+ inside_for(body: CodeBody): list[str] | None

## BraceCall

One call whose last argument is a callback, such as `describe("a cart", () => { ... })` or `story(...)`, and where its parts sit in the text.

+ BraceCall(text: str, start: int, open_paren: int, name: str)
------
+ text: str
+ start: int
+ name: str
+ close: int
+ brace: int
+ inner_end: int
+ end: int
+ is_whole: bool
+ body: str
----

## BracketStructure

A span of text read for its brackets.

+ BracketStructure(text: str)
------
----
+ closing_bracket(open_at: int, opener: str = '{', closer: str = '}'): int | None
+ opening_bracket(close_at: int, opener: str = '(', closer: str = ')'): int
+ top_level_indexes(mark: str): list[int]
+ top_level_index(mark: str): int
+ braced(open_at: int): str | None

## CallGraph : list

An indented call graph: the operations a step or an observation reaches, one entry per line.

------
----
+ read(text: str): CallGraph
+ add_line(line: str, depth: int): None
+ block(): str
+ callees(): list[str]
---<<keeps>>--> CallGraphEntry

## CallGraphEntry

One line in an indented call graph.

------
+ depth: int
+ kind: str
+ text: str
----

## SourceText

A span of source in any language, such as an operation body, a class, or a markdown card, and what the rules measure in it.

+ SourceText(text: str)
------
+ text: str
----
+ control_flow_depth(): int
+ has_bare_catch(): bool
+ swallows_exceptions(): bool
+ unnamed_numbers(): list[str]
+ reaches_peer_private(own_objects: frozenset[str] = frozenset(), own_members: frozenset[str] = frozenset()): bool
+ built_collaborators(parameter_names: frozenset[str], start_line: int): list[tuple[str, int]]
+ locals_built_of(class_name: str): frozenset[str]
+ mixes_io_and_domain(): bool
+ calls_io_and_domain(): bool
+ raises_on_empty(): bool
+ exception_without_message(): str
+ generic_exception_message(): bool
+ mutates_without_record(): bool
+ has_prose_comment(hash_only: bool = False): bool
+ prototype_swap(start_line: int): dict
+ markdown_bullet_lines(): dict
+ line_of(index: int): int
+ hits(pattern: re.Pattern[str]): list[list]

## Drawio

Draw the class model as a draw.io diagram, then scan its layout and repair the generator.

+ Drawio()
------
+ module_dir: Path
+ domain_slug: str
----
+ contexts(): str
+ examples(): str
+ create_diagram(content: str, path: str): str
+ scan(paths: list[str]): str
+ validate(): str
+ repair(asset: str, violation: str): str
+ render(content: str = '', path: str = ''): str
+ verify_regression(examples_root: str = ''): str

## DrawIOCleanEngineeringModel : DiagramCleanEngineeringModel

The draw.io format of the class model: a modules view of rounded module cards, or a class view of class cards and the arrows between them. DDD's bounded-context map extends it.

+ DrawIOCleanEngineeringModel(name: str = '', sequential_order: int = 1)
------
+ module_cell_types: tuple[type, ...]
+ previous: str | None
+ keep_positioning: bool
----
+ save(): str
+ load_module_cell(source: Module): DrawIOModule
+ imported_class(source: OoadClass, from_module: str = ''): DrawIOImportedClass
+ parse(text: str): DrawIOCleanEngineeringModel
+ render(canonical: CleanEngineeringModel): str
+ kept_previous(): str | None
---<<creates>>--> DrawIOModule

## DrawIOModule : DiagramModule, DrawioVertex

A rounded modules-view cell.

+ DrawIOModule(name: str = '', sequential_order: int = 1, **kwargs)
------
+ dependency_labels: dict[str, str]
----
+ draws(style: str): bool
+ html(): str
+ style(): str
+ from_cell(value: str, sequential_order: int): DrawIOModule | None

# cdd_guidance/practices/stories

*Stories* is the practice; *StoriesReading* is its part in the knowledge graph, and *StoryTree* is the story map as the graph holds it. A *StoryModel* holds *Epic* and *Story* objects (and their scenarios and steps), and the diagram format extends them as *DiagramStoryModel*, *DiagramEpic*, and *DiagramStory*. The whole model of this module, internals included, is `cdd_guidance/practices/stories/model/.context/story-model.md`; that document is canonical, and this section shows only the classes other modules use.

- **Purpose:** Keep one Epic, Story, Scenario hierarchy that discovery, specification, and tests all read, so scope and behaviour stay traceable from the map to the code.
- **Seam (terms):** Stories, StoriesReading, StoryTree, StoryModel, Epic, Story, DiagramStoryModel, DiagramEpic, DiagramStory
- **Dependencies (one-way):** harness/annotations, harness/agent_tools, harness/markdown, harness/guidance, harness/graph, cdd_guidance/practices/sketch_document, cdd_guidance/practices/clean_engineering, cdd_guidance/practices/ddd (StoriesReading reads DDD's reading beside its own; DDD imports nothing of Stories)

## Stories : PracticeGuidance

The Stories practice: story map, scenarios, and acceptance tests.

+ Stories(fidelity: str = 'story_map', format: str | None = None, story_test_folder: str | None = None)
------
+ story_test_folder: str | None
+ formats_type: type
	// StoriesFormats
+ reading_type: type
	// StoriesReading
----
+ read_folder(root: Path, on_file = None): StoryModel
+ read_files(files: list[Path], project: Path, on_file = None): StoryModel
	// a story test's scenarios go on the map's Story of the same name; a test with no map listed reads the map in its own folder or the nearest one above it
---<<creates>>--> StoryModel
---<<reads the graph with>>--> StoriesReading
---<<registers with>>--> StoryNode

## StoriesReading : PracticeReading

How Stories takes part in the graph: it reads the story tests under its root, or the story maps there when there are none, writes the story map onto its graph, and links each step to the Clean Engineering operations it calls; it reads after Clean Engineering.

------
+ reads_after: tuple[str, ...]
+ root: Path
+ << composition >> story_tree: StoryTree
+ object_model: PracticeReading | None
	// Clean Engineering's reading, from the same graph
+ domain_model: PracticeReading | None
	// DDD's reading, from the same graph
----
+ read_working_copy(): None
---<<loads>>--> StoryModel
---<<finds a reading with>>--> CleanEngineering
---<<finds a reading with>>--> Ddd
---<<creates>>--> StoryTree

## StoryTree

The story map as the graph holds it: each epic's sub-epics and stories, each story's scenarios, each scenario's steps.

+ StoryTree(stories: PracticeReading)
------
+ stories: PracticeReading
----
+ epic_of(node): Node | None
+ sub_epics(epic): list
+ stories_under(epic): list
+ scenarios(story): list
+ steps(scenario): list

## StoryModel : StoryNode

One story map: its epics and increments, and the texts of the files it was read from.

+ StoryModel(source: StoryModel | Graph | None = None, graph: Graph | None = None)
------
+ << composition >> epics: list[Epic]
+ increments: list[Increment]
+ source_texts: dict[str, str]
+ links: StoryMapLinks | None
----
+ copy_of(source: StoryModel): StoryModel
+ take_scenarios(stories: list[Story], file: str): None
+ every_epic(): list[Epic]
+ every_story(): list[Story]
+ stories_named(names: list[str]): list[Story]
+ place_in(file: str): None
+ append_epic(epic: Epic): None
+ append_increment(increment: Increment): None
+ record(practice, on_node: Callable[[str], None] | None = None): None
	// an example's facts are looked up only in source_texts, the files the story map was read from
+ clone(): StoryModel
---<<keeps>>--> Epic
---<<records through>>--> StoryRecording

## Epic : StoryNode

An epic; a nested epic is an epic whose parent is an epic.

+ Epic(name: str | Epic, sequential_order: int = 0, story_class: type | None = None)
------
+ epics: list[Epic]
+ << composition >> stories: list[Story]
+ has_epics: bool
+ is_sub_epic: bool
+ top_epic: Epic
+ depth: int
----
+ estimate_label(): str
+ leaf_epics(): list[Epic]
+ record(recording: StoryRecording, parent): None
+ first_story_file(): str
+ evidence_in(recording: StoryRecording, story_file: str): list[str]
+ clone(): Epic
+ load_map_facts(): None
+ every_epic(): list[Epic]
+ every_story(): list[Story]
+ append_epic(epic: Epic): None
+ append_story(story: Story): None
+ place_in(file: str): None
+ span_columns(): int
+ diagram_span_columns(): int
+ tree_depth(): int
---<<keeps>>--> Story

## Story : StoryNode

One story under an epic, with its scenarios.

+ Story(name: str | Story, sequential_order: int = 0, story_type: StoryType = StoryType.USER)
------
+ story_type: StoryType
+ actors: list[str]
+ domain_terms: list[str]
+ backgrounds: list[Background]
+ << composition >> scenarios: list[Scenario]
+ code_key: tuple
+ top_epic: Epic | None
----
+ load_map_facts(): None
+ record(recording: StoryRecording, parent): None
+ clone(): Story

## DiagramStoryModel : StoryModel

Story map whose epics and stories are the diagram types.

------
+ max_sub_epic_depth: int
+ actor_y: int
+ sub_epic_top: int
+ story_floor: int
+ story_y: int
----
+ sub_epic_y(depth: int): int
+ bar_y(top: int, depth: int): int
+ line_y(floor: int, top: int, max_sub_epic_depth: int): int
---<<makes its epics as>>--> DiagramEpic
---<<makes its stories as>>--> DiagramStory

## DiagramEpic : Epic, DiagramStoryNode

An epic as the story map diagram draws it.

------
----

## DiagramStory : Story, DiagramStoryNode

A story as the story map diagram draws it.

------
----

# cdd_guidance/practices/ddd

*Ddd* is the practice: bounded contexts, the aggregate model, and tactics. *DddReading* is its part in the knowledge graph: it reads DDD's nodes after the Clean Engineering classes it extends. The whole model of this module, internals included, is `cdd_guidance/practices/ddd/model/.context/ddd-model.md`; that document is canonical, and this section shows only the classes other modules use.

- **Purpose:** Keep the software in the business's language, with each rule held in the aggregate that owns it, before any technical detail is added.
- **Seam (terms):** Ddd, DddReading
- **Dependencies (one-way):** harness/agent_tools, harness/guidance, harness/graph, cdd_guidance/practices/sketch_document, cdd_guidance/practices/clean_engineering

## Ddd : PracticeGuidance

The DDD practice: bounded context, model, and tactics. Its python and typescript formats are Clean Engineering's class models.

+ Ddd(fidelity: str = 'bounded_context', format: str | None = None)
------
+ formats_type: type
	// DddFormats
+ reading_type: type
	// DddReading
+ extends: str
	// clean_engineering
+ shows_every_fidelity: bool
----
---<<reads the graph with>>--> DddReading
---<<writes code with>>--> PythonCleanEngineeringModel
---<<writes code with>>--> TypeScriptCleanEngineeringModel
---<<registers with>>--> DomainNode

## DddReading : PracticeReading

DDD's nodes, read after Clean Engineering's classes, and its graph checks with Clean Engineering's.

------
+ reads_after: tuple[str, ...]
+ class_types: tuple[str, ...]
+ root: Path
----
+ own_graph_checks(): dict
+ read_working_copy(): None
---<<reads classes of>>--> CleanEngineeringModel

# cdd_guidance/practices/ux

*Ux* is the practice: information architecture, mockups, and front-end code. *UxReading* is its part in the knowledge graph: it names the node types a UX map is made of and checks its screen rules on them. The whole model of this module, internals included, is `cdd_guidance/practices/ux/model/.context/ux-model.md`; that document is canonical, and this section shows only the classes other modules use.

- **Purpose:** Keep screens, navigation, and interactions in one hierarchy that the diagram, the mockup, and the front-end code all follow.
- **Seam (terms):** Ux, UxReading, NoJavascriptPractice, UxOutsideSession
- **Dependencies (one-way):** harness/annotations, harness/agent_tools, harness/guidance, harness/graph, harness/installation, harness/design_canvas, cdd_guidance/practices/stories

## Ux : PracticeGuidance

The UX practice: information architecture, mockup, and front-end code.

+ Ux(fidelity: str = 'ia', format: str | None = None)
------
+ reading_type: type
	// UxReading
----
+ ensure_javascript(practice: str, source_format: str, content: Any): dict
+ javascript_practice(key: str): PracticeGuidance
	// the session's own Stories or Clean Engineering, at the fidelity and format it works at there
---<<raises>>--> UxOutsideSession
---<<raises>>--> NoJavascriptPractice
---<<reads the graph with>>--> UxReading
---<<registers with>>--> UxNode

## UxReading : PracticeReading

The UX practice's node types and its screen rules; a working-copy load reads no UX files yet.

------
+ node_types: tuple[str, ...]
----

## NoJavascriptPractice : ValueError

ensure_javascript was asked for JavaScript from a practice that does not write the JavaScript a mockup imports.

------
----

## UxOutsideSession : ValueError

ensure_javascript was asked of a Ux that works in no session, so it has no Stories or Clean Engineering of its own to render the JavaScript through.

------
----

# cdd_guidance/practices/bdd

*Bdd* is the practice: behavior, realization, and development. *BddGraphReading* is its part in the knowledge graph: it reads each spec file's describe tree after Clean Engineering's code, and links each observation to the Clean Engineering members it drives. The whole model of this module, internals included, is `cdd_guidance/practices/bdd/model/.context/bdd-model.md`; that document is canonical, and this section shows only the classes other modules use.

- **Purpose:** Turn domain vocabulary into passing tests, locking what is observed before how it is built.
- **Seam (terms):** Bdd, BddGraphReading
- **Dependencies (one-way):** harness/annotations, harness/agent_tools, harness/guidance, harness/graph, cdd_guidance/practices/sketch_document, cdd_guidance/practices/clean_engineering

## Bdd : PracticeGuidance

The BDD practice: behavior, realization, and development.

+ Bdd(fidelity: str = 'behavior', format: str | None = None)
------
+ reading_type: type
	// BddGraphReading
----
---<<reads the graph with>>--> BddGraphReading
---<<registers with>>--> BddModel
---<<registers with>>--> BehaviorNode

## BddGraphReading : PracticeReading

BDD's describe trees, read after Clean Engineering's code and linked to the Clean Engineering members each observation drives.

------
+ reads_after: tuple[str, ...]
+ node_types: tuple[str, ...]
+ clean_engineering_reading: PracticeReading | None
----
+ read_working_copy(): None
---<<finds a reading with>>--> CleanEngineering
---<<links with>>--> ObservationLinks

# cdd_guidance/practices/agent_bdd

*AgentBdd* is the practice for specs that drive a real agent and judge what it did. It composes vanilla BDD: its generate output is the session's own *Bdd*'s instructions and generate output.

- **Purpose:** Test agent behaviour end to end against a real agent, so a spec fails when the agent would actually do the wrong thing.
- **Seam (terms):** AgentBdd
- **Dependencies (one-way):** harness/agent_tools, harness/guidance, harness/installation, cdd_guidance/practices/bdd

## AgentBdd : PracticeGuidance

The agent BDD practice: mamba specs that drive a real agent.

+ AgentBdd(format: str = 'python')
------
+ bdd: Bdd
	// the session's own BDD practice, read from the session's graph
----
+ generate_output(): str
---<<reads instructions and generate output of>>--> Bdd

# cdd_guidance/patterns

Each pattern is a *PracticeGuidance* that adds rules for one kind of solution, and its *GraphOverlay*, kept as `graph_overlay`, adds the nodes and facts those rules read; *DomainDrivenStack* is the base for a domain-organized TypeScript stack such as *LernDomainDriven* and *MernDomainDriven*. Importing the package registers the patterns with harness/graph's *PatternOverlays*, after registering the practices they build on.

- **Purpose:** Add the guidance and the graph rules one kind of solution needs on top of the practices, without changing a practice.
- **Seam (terms):** DomainDrivenStack, LernDomainDriven, MernDomainDriven, CddWebDomainAccess, CddClaudeMod, LernOverlay, WebDomainAccessOverlay
- **Dependencies (one-way):** harness/agent_tools, harness/guidance, harness/graph, cdd_guidance/practices (the package, which registers the practices), cdd_guidance/practices/stories, cdd_guidance/practices/ddd, cdd_guidance/practices/bdd, cdd_guidance/practices/clean_engineering (*SourceText*, to read facts)

## DomainDrivenStack : PracticeGuidance

Implementation fidelity for a domain-module-organized TypeScript stack on an already-designed vertical slice: acceptance tests first, with Stories at acceptance_tests in TypeScript, then the production code they drive.

+ DomainDrivenStack()
------
----

## LernDomainDriven : DomainDrivenStack

The LERN stack: lowdb JSON files, Express, React, and Node, in TypeScript, organized by domain module.

------
+ << composition >> graph_overlay: LernOverlay
----
+ test_setup_text(root: Path): str
---<<creates>>--> LernOverlay

## LernOverlay : GraphOverlay

Reads the LERN tiers of a working copy onto the practices the graph holds: behavior files on BDD, tier files on DDD's aggregates, and story files on Stories.

------
+ direct_kinds: frozenset[str]
----
+ read(graph: Graph): None
---<<finds a practice with>>--> Ddd
---<<finds a practice with>>--> Stories
---<<finds a practice with>>--> Bdd
---<<reads facts with>>--> SourceText

## MernDomainDriven : DomainDrivenStack

The MERN stack: MongoDB, Express, React, and Node, in TypeScript, organized by domain module.

------
----

## CddWebDomainAccess : PracticeGuidance

How code outside Python reaches the CDD domain: through MCP tools, by a language adapter the installer deploys.

+ CddWebDomainAccess()
------
+ << composition >> graph_overlay: WebDomainAccessOverlay
----
---<<creates>>--> WebDomainAccessOverlay

## WebDomainAccessOverlay : GraphOverlay

Adds each access tier file of a working copy to DDD's part of the graph, with the facts its access rules read.

------
----
+ read(graph: Graph): None
---<<finds a practice with>>--> Ddd
---<<reads facts with>>--> SourceText

## CddClaudeMod : PracticeGuidance

A Claude Code mod that is a view of the CDD domain: each component runs view, client, MCP tool, domain.

+ CddClaudeMod()
------
+ << composition >> graph_overlay: GraphOverlay
----

# cdd_guidance/builders

A *Builder* is guidance for building a new part of CDD; *CreateAgentToolset* and *CreatePracticeGuidance* are the two builders.

- **Purpose:** Start every new toolset and practice from the same templates, so it installs and runs with the existing actions on its first try.
- **Seam (terms):** Builder, CreateAgentToolset, CreatePracticeGuidance
- **Dependencies (one-way):** harness/agent_tools, harness/guidance

## Builder : PracticeGuidance

Guidance for building a new part of CDD, such as a toolset or a practice; it works from the repository's root rather than a practice folder.

------
+ default_workspace_folder: str
----

## CreateAgentToolset : Builder

Scaffold a new agent toolset: an @agent_toolset class with @agent_tool and @agent_instructions operations.

------
----

## CreatePracticeGuidance : Builder

Scaffold a new practice: its PracticeGuidance class, its markdown, templates, and examples.

------
----

# cdd_guidance/context_setup

*ContextSetup* converts documents or captures a live app, through *LiveAppCapture*, and partitions the result with the practices the user picks; *ContextIndex* embeds the segments and answers questions with citations. The cdd server makes each for the call it answers, so the folders a call names are read from that call's session's project.

- **Purpose:** Turn existing documents or a running application into partitioned, indexed context that later stages can search and cite.
- **Seam (terms):** ContextSetup, ContextIndex, EmbeddingProvider
- **Dependencies (one-way):** harness/agent_tools, harness/installation, harness/markdown, harness/mcp, cdd_guidance/actions (*Partition*)

## ContextSetup

Convert a folder of documents to markdown and partition it through the context tools the user selects.

+ ContextSetup(partition: Partition | None = None, context_index: ContextIndex | None = None)
------
+ << composition >> partition: Partition
+ << composition >> context_index: ContextIndex
+ session: Any
	// the session its Partition was made for
----
+ for_call(call: ToolCall): ContextSetup
+ convert(folder_path: str): ConversionResult
+ smoke_test(repo_path: str, surface: str = 'web', capture_repo: str = '', base_url: str = '', entry_paths: list[str] | None = None): SmokeTestResult
+ scout_app(repo_path: str, surface: str = 'web', capture_repo: str = '', base_url: str = '', entry_paths: list[str] | None = None): ScoutResult
+ complete_capture(repo_path: str, missing_pages: list[str], surface: str = 'web', capture_repo: str = '', base_url: str = ''): CaptureResult
+ capture_from_live_app(repo_path: str, capture_repo: str = '', surface: str = 'web'): str
+ capture_from_documents(folder_path: str, indexers: list[str] | None = None, first: str = ''): str
---<<creates>>--> ContextIndex
---<<creates>>--> Partition
---<<creates>>--> LiveAppCapture
---<<reads session of>>--> ToolCall

## ContextIndex

Embed partitioned segments into a FAISS index and answer questions with source citations.

+ ContextIndex(embedding_provider: EmbeddingProvider | None = None, session: Any = None)
------
----
+ for_call(call: ToolCall): ContextIndex
+ embed(segments_paths: list[str], out_path: str): EmbedResult
+ search(query: str, index_path: str, top_k: int = 5): SearchResult
+ ask(question: str, index_path: str): str
---<<embeds with>>--> EmbeddingProvider
---<<creates>>--> SegmentIndex
---<<reads session of>>--> ToolCall

## EmbeddingProvider : Protocol

What turns text into vectors; OpenAI's embedding service by default.

------
----
+ embed_texts(texts: list[str]): list[list[float]]
+ embed_query(text: str): list[float]
