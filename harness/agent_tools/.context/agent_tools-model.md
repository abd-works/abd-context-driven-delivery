# harness/agent_tools

An *AgentToolSet* is an ordinary class an agent can list and run: each `@agent_tool` member is an *AgentOperation* and each `@agent_instructions` member is *AgentInstructions*. A *ToolCall* is one call as a chat made it, with its project and chat. The whole model of this module, internals included, is `harness/agent_tools/.context/agent-tools-model.md`; that document is canonical, and this section shows only the classes other modules use.

- **Purpose:** Let an author publish an ordinary class as operations and instructions an agent can list and use, and let every publisher read those members from one place.
- **Seam (terms):** AgentToolSet, ToolSetCollection, ToolsetMembers, ToolsetReference, AgentTool, InvokeLine, ToolRequest, CallsBeingAnswered (`CALLS_BEING_ANSWERED`), `names_alike`, `is_built_in`, AgentOperation, AgentInstructions, InstallDestination, AgentToolAnnotation, AgentInstructionsAnnotation, AgentToolSetAnnotation, ToolSetCollectionAnnotation, Collect, ToolSubject, OnSubject, TakesFromCall, NoSessionLog, PublishedWhereHeld, SubAgentAnnotation, ToolSubjectLoader, RecipePlaceholders, ToolCall, SessionOpening (`SESSION_OPENING`), ChatPointer; `tools(...)`, `instructions(...)`, `report_progress`, `reporting_to`, `NO_CHAT`, `SUB_AGENT_CALLER_PREAMBLE`
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
+ << composition >> invoke_line: InvokeLine
----
+ is_called(called: str): bool
+ install_to(destination: str): bool
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

## InvokeLine

Text that holds the `Use MCP tool:` line a skill or command ends with; a tool writes it and the installer reads the tool names back through it.

+ InvokeLine(text: str)
------
+ text: str
+ names: list[str]
+ is_invoke_line: bool
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
	// builds its property with operation_property (harness/markdown)

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

One call of a tool as its caller made it: the arguments it sent, the folder of the project the calling chat works on, and the request it answers.

+ ToolCall(arguments: dict[str, Any] | None = None, project: Path | str | None = None, request: ToolRequest = ToolRequest())
------
+ arguments: dict[str, Any]
+ project: Path
+ << association >> request: ToolRequest
+ chat_id: str
+ identity: str
+ named_paths: list[str]
+ session: Any
	// the session open in this call's own project, never the one the process worked on last; a call that names no project works in no session
----
+ sent(arguments: dict[str, Any] | None, project: Path | str | None, request: ToolRequest = ToolRequest()): ToolCall
+ session_named(session_file: str): Any
---<<takes the chat out of the arguments with>>--> ChatPointer
---<<opens sessions through>>--> SessionOpening

## SessionOpening

How the process's calls open their sessions: the one *SessionOpener* space/session registers when it is imported. The process keeps one, `SESSION_OPENING`.

+ SessionOpening()
------
----
+ open_with(opener: SessionOpener): None
+ saved_in(project: Path | str): Any
+ open_in(call: ToolCall): Any
+ named_in(session_file: str, call: ToolCall): Any
---<<opens sessions through>>--> SessionOpener
---<<raises>>--> SessionsNotLoaded

## ToolRequest

The request a call answers: the chat that sent it and, for a call the cdd server answers, the tool it names, the MCP host answering it, and whether that host answers it for a chat.

+ ToolRequest(chat: ChatPointer | None = None, tool: str = '', mcp_host: AnsweringMcpHost | None = None, answers_a_chat: bool = False)
------
+ << association >> chat: ChatPointer | None
+ tool: str
+ << association >> mcp_host: AnsweringMcpHost | None
+ answers_a_chat: bool
----
+ sent_by(chat: ChatPointer | None): ToolRequest

## CallsBeingAnswered

The call a tool is answering on each thread; the process keeps one, `CALLS_BEING_ANSWERED`.

+ CallsBeingAnswered()
------
+ current: ToolCall | None
----
+ answering(call: ToolCall): Iterator[ToolCall]

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
