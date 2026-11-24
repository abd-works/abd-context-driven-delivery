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
+ << composition >> files: ActionFiles
+ works_in: Any
+ session: Any
+ log: Any
+ graph: Any
+ operation_type: type[AgentOperation]
+ practice_slugs: list[str]
+ session_context: str
----
+ for_call(call: ToolCall): GuidanceAction
	-> ToolCall.session_named
+ session_for(call: ToolCall): Any
+ listed(): list
+ run(operation: Callable[[Any], Any], action: str = ''): list
	-> WorkList.each
+ log_running(action: str): None
+ begin(guidance: GuidanceArg | None = None, action: str = ''): str
+ act_quickly(): str
+ inject_rules(payload: HookPayload): dict[str, Any]
---<<raises>>--> ActionWorksInNoSession
---<<raises>>--> UnknownGuidance
---<<makes the guidance a call names by its reference with>>--> ToolsetReference
---<<publishes its operations as>>--> GuidanceAgentOperation
---<<calls session_named on>>--> ToolCall
---<<reads the listed practices and fidelities of>>--> PracticeGuidance
---<<asks for instructions, rules, and templates>>--> FidelityGuidance
---<<makes a set of practices with>>--> PracticeCatalogue
---<<registers its fidelity action runner with>>--> ActionCatalogue
---<<reads tool input of>>--> HookPayload
---<<injects rules on the event>>--> Hook
---<<annotated with>>--> Toast

## ActionFiles

The files one guidance action names and writes in the session it works in.

+ ActionFiles(action: GuidanceAction)
------
----
+ path_named(named: str | Path): Path
+ paths_to_read(named: list[str] | str | None): list[Path]
	// each path a call names must be there under one of the session's roots; one that is not is refused by name
+ read(content: str = '', paths: list[str] | str | None = None): str
+ wrote(paths: list[str | Path]): None
---<<refreshes the graph of>>--> GuidanceAction

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

## GuidanceMappingNamesNoToolset : ValueError

A guidance mapping with no `toolset`, which is where a mapping names its practice; its message lists the slugs there are.

+ GuidanceMappingNamesNoToolset(mapping: Mapping[str, Any], slugs: Sequence[str])
------
+ mapping: dict
+ slugs: tuple
----

## ActionWorksInNoSession : Exception

An action made for no session, such as one listed for install, was asked for the session it works in.

+ ActionWorksInNoSession(action: str)
------
+ action: str
----
