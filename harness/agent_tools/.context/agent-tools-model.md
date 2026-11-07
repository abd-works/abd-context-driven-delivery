# agent_tools — class model (model fidelity)

Markdown channel for the *AgentToolSet* primitive. The module's purpose, seam, and dependencies are in [module-context.md](module-context.md); this document holds only its classes. *AgentToolSet* is the toolset the author marks with `@agent_toolset`; its members are *AgentTool* objects — *AgentOperation* for `@agent_tool` and *AgentInstructions* for `@agent_instructions`. Writing members out to MCP, skills, commands, rules, and hooks belongs to `harness/installation`, `harness/mcp`, and `harness/hooks`. *Mark* and *Destination* belong to `harness/annotations`, *Name* to `harness/name`, *Markdown* to `harness/markdown`, *Session* to `space/session`, *SubAgent* (the `sub-agent.sub_agent` operation) to `tools/sub_agent`, and *AgentToolsProbe* and *AgentToolsDiagnostics* to `harness/diagnostics`; they appear here only as names this module uses.

**Out of scope:** guidance actions (`harness/guidance_actions`, Generate, Validate, …) keep their own model; *GuidanceAgentOperation* is listed only because this module defines it.

---

## Language companion                                             <!-- L -->

*AgentToolSet* is the toolset a practice or tool decorates with `@agent_toolset`. Callable members are *AgentTool* subtypes: *AgentOperation* (`@agent_tool`) runs Python; *AgentInstructions* (`@agent_instructions`) expands its body into a recipe the agent follows.

Each *AgentTool* exposes `kind`, `description`, `parameters`, `response`, and `input_schema`, read from the callable, and holds the **`toolset`** that made it. Both annotations use ordinary Python `self` (the toolset).

- `@agent_toolset` merges *AgentToolSet* onto the decorated class; do not subclass *AgentToolSet* directly. The class docstring is the toolset's **description**.
- Inside an `@agent_instructions` body, `tools(...)` names operations the agent calls while following the recipe, and `instructions(...)` includes another recipe inline. A recipe that includes itself is rejected when the class is decorated.
- *ExpansionMode* on the called toolset decides whether a nested recipe expands inline (`instructions`) or is listed as a tool to call (`tool`).
- `@toolset_collection` on a class makes it a *ToolSetCollection*; on a property it annotates one of the toolset's collections, whose children are published as nested toolsets.
- `@tool_subject` annotates the class method that loads the object a tool call acts on; a loader that takes `project` is handed the checkout the call names. `@noSessionLog` keeps a repeated read out of the session log.
- `@subAgent` on a member puts the hand-off to a background sub-agent at the start of its description.
- A toolset's `parameter_notes` are added after the description of every tool that takes that parameter.

---

## AgentToolSet                                                   <!-- Md -->

Merged onto the decorated class by `@agent_toolset`.

AgentToolSet()
------
name: str
	// snake-case class name unless set
slug: str
	Interaction:
		return Name(domain_slug or class name).kebab
description: str
	Interaction:
		return (self.__class__.__doc__ or "").strip()
registration_name: str
	// "{module}:{Class}", the ref installers and the hook server load by
install_folder: Path
<< aggregation >> operations: dict[str, AgentOperation]
	// every @agent_tool on this instance, each made with toolset=self
instructions: Mapping[str, AgentInstructions]
	// every @agent_instructions on this instance, each made with toolset=self
tools: dict[str, AgentTool]
	// instructions, then operations (an @agent_tool wins the same name), then hooks, then collection tools
toolset_collections: list[ToolSetCollection]
mode: ExpansionMode
	Invariant: value is "instructions" or "tool"
HOSTED_ONLY_CLASS_NAMES: frozenset[str]
	// classes whose tools run only through the practice or toolset that holds them; install and the hook server skip them
parameter_notes: dict[str, str]
	// parameter name -> note added after the description of each tool that takes it
----
tools_for(destination: str): list[AgentTool]
	-> AgentTool.install_to
child_toolsets(): Iterator[AgentToolSet]
instantiate(toolset: Any = None): AgentToolSet
	// toolset is None, a "{module}:{Class}" ref, a {toolset, context} dict, a class, or an instance
	-> ToolsetReference.toolset_class
from_items(items: list, context: dict | None = None): list[AgentToolSet]
	// one instance per toolset class
for_call(call: ToolCall): AgentToolSet
	// this toolset as the call works on it; self unless the toolset keeps state of one call (a guidance action)
session_for(call: ToolCall): Session | None
	// the session this toolset's tools log the call in
	-> call.session
validate(): None
	Invariant: a recipe body names callable operations only through tools(...) and nested recipes only through instructions(...)
	Invariant: nested instructions(...) may not form a cycle
	// also runs at @agent_toolset decorate time, on the class
	// raises AgentToolValidationError

## AgentTool                                                      <!-- Md -->

One member of a toolset an agent can see and call.

AgentTool(name: str, callable: Callable, toolset: AgentToolSet)
------
name: str
callable: Callable
toolset: AgentToolSet
	Invariant: the toolset instance that made this member
slug: str
	// the toolset's slug
registration_name: str
	// the toolset's registration_name
deploy_name: str
	// the name a @command or @skill annotation gives, else name
mcp_name: str
	// "{toolset slug}.{name}"; a practice's own instructions publish under the practice slug alone
kind: str
	// "tool", "instructions", or "none"
docstring: str
description: str
	// the docstring expanded once through Markdown
parameters: dict[str, str]
response: str | None
input_schema: dict
	-> ParameterSchema.json_schema
install_to_mcp, install_to_hook, install_to_skill, install_to_command, install_to_rule: bool
hook_event: str
destinations: list[str]
----
install_to(destination: str): bool
invoke_line(): str
	// the "Use MCP tool:" line a skill or command ends with
invoke(arguments: dict | None = None, *, project: Path | None = None): Any
	-> answer(ToolCall(arguments, project))
answer(call: ToolCall): Any
	// runs on the toolset made for the call; a callable annotated as taking the project is handed call.project
	-> on(toolset.for_call(call)).log_session_invocation(call)
	-> ParameterSchema.coerced
	// then call the callable
	// raises CallNamesNoProject when the callable takes the project and the call names none
on(toolset: AgentToolSet): AgentTool
	// this tool on a toolset of the same class made for one call
log_session_invocation(call: ToolCall): None
	// skipped for ping calls and @noSessionLog members, and for a call that works in no session
	-> toolset.session_for(call).log.tool

## AgentOperation : AgentTool                                     <!-- Md -->

AgentOperation(name: str, callable: Callable, toolset: AgentToolSet)
------
	Invariant: kind == "tool"
----

## ToolCall                                                      <!-- Md -->

One call of a tool: the arguments its caller sent, the folder of the project the calling chat works on, and that chat. A tool reads its project, its chat, and the session open there from its own call, because one cdd server answers every chat.

ToolCall(arguments: dict | None = None, project: Path | None = None, chat: ChatPointer | None = None)
------
arguments: dict
project: Path | None
chat: ChatPointer | None
session: Session | None
	// the session saved as open in the project's checkout, read once for this call; none when the call names no project or no opener is registered
	-> SessionOpener.open_in(self)
----
sent(arguments: dict | None, project: Path | None): ToolCall
	// the chat named in the arguments is taken out and kept as the call's chat
	-> ChatPointer.taken_from
open_sessions_with(opener: SessionOpener): None
	// space/session registers its opener when it is imported, so this module never imports space
session_named(session_file: str): Session
	// the session a board command names by its session.json
	-> SessionOpener.named_in(session_file, self)
	// raises SessionsNotLoaded when no opener is registered

## SessionOpener                                                 <!-- Md -->

How a call finds the sessions it works in. A protocol: the module that keeps sessions (`space/session`) implements it.

SessionOpener
------
----
open_in(call: ToolCall): Session
named_in(session_file: str, call: ToolCall): Session

## ChatPointer                                                   <!-- Md -->

The chat a tool call came from: its id, its transcript file, and the transcript lines the call covers. Every session.log line a call writes ends with it, so `read_loop` can put the chat's words back under the line.

ChatPointer(id: str, transcript: Path | None = None, lines: str = "")
------
id: str
transcript: Path | None
lines: str
	// a range such as "1-40"
is_missing: bool
	// true for the no-chat pointer
line_range: tuple[int, int]
----
of(chat_id: str, transcript: str | Path | None, lines: str = ""): ChatPointer | None
taken_from(arguments: dict | None): tuple[ChatPointer | None, dict]
	// the chat named in a call's arguments, and the arguments left for the tool
from_claude_chat(chat_id: str): ChatPointer | None
in_log_line(line: str): ChatPointer | None
in_chat_file(path: Path): tuple[ChatPointer, str]
transcript_text(): list[str]

## GuidanceAgentOperation : AgentOperation                        <!-- Md -->

An `@agent_tool` on a guidance action; the call is logged as the action running in its own session.

GuidanceAgentOperation(name: str, callable: Callable, toolset: AgentToolSet)
------
----
log_session_invocation(call: ToolCall): None
	-> toolset._log_running_action(name)

## AgentInstructions : AgentTool                                  <!-- Md -->

AgentInstructions(name: str, callable: Callable, toolset: AgentToolSet)
------
	Invariant: kind == "instructions" unless the callable is also annotated @agent_tool
prompt: tuple[str, ...]
tools: list[str]
	// deferred operation names from tools(...), merged with those of every nested instructions(...); read-only
result_template: str
----
for_callable(callable: Callable, instance: AgentToolSet | None = None): AgentInstructions
expand(arguments: dict): ExpansionResult
	// raises RecipeLineFailed when a recipe line raises
answer(call: ToolCall): str
	// the instructions an agent follows for this call, expanded by the toolset made for it, with the session context of a guidance action appended
	-> on(toolset.for_call(call)).log_session_invocation(call)
	-> expand
members_of(target: AgentToolSet): ToolsetMembers
member_of(target: AgentToolSet, member: str): AgentInstructions
provider_of(owner: Any, provider_name: str): Any
parent_recipe(after_class: type | None = None): tuple[AgentInstructions, type] | None
	// the same-named recipe on the nearest class above, for a recipe that defers to its parent

## RecipeExpansion                                                <!-- Md -->

One expansion of one recipe for one call's arguments; made per expansion, so two calls never share what it collects.

RecipeExpansion(instructions: AgentInstructions, arguments: dict | None, expanding: frozenset, defining_class: type | None)
------
prompt: tuple[str, ...]
tools: list[str]
----
run(): RecipeExpansion
	// raises RecipeLineFailed for a line that raises, RecipeCallsItself for a recipe that expands back into itself

## RecipeSource                                                   <!-- Md -->

RecipeSource(recipe: Callable)
------
module: ast.Module
function_def: ast.FunctionDef
only_defers_to_parent: bool
result_template: str
----
member_on_self(node): str | None
provider_member(node, roots): tuple[str, str] | None
loop_providers(): set[str]

## RecipePlaceholders                                             <!-- Md -->

RecipePlaceholders(arguments: dict, parameter_names: set[str], toolset: Any = None)
------
----
filled(template: str): str
	// {{name}} from arguments, {{self.attribute}} from the toolset

## ToolsetMembers                                                 <!-- Md -->

The members of one toolset class and which of them its annotations make tools; each class is walked once.

ToolsetMembers(owner: type)
------
every: list[tuple[str, Any]]
annotated: list[tuple[str, Any]]
tool_names: set[str]
instruction_names: frozenset[str]
----
callable_on(instance, name, member): Callable

## ToolsetReference                                               <!-- Md -->

ToolsetReference(reference: str)
------
toolset_class: type
	// raises TypeError for a class that is not an @agent_toolset
----

## ToolsetValidator                                               <!-- Md -->

ToolsetValidator(toolset_class: type)
------
----
validate(): None
	// raises AgentToolValidationError

## ToolSubjectLoader                                              <!-- Md -->

ToolSubjectLoader(toolset_class: type)
------
loader: Callable | None
	// the @tool_subject classmethod, given the called project when it takes one
----
on_subject(load, operation): Callable
given_the_called_project(operation: Callable): Callable

## ExpansionMode                                                  <!-- Md -->

ExpansionMode(value: str)
------
value: str
	Invariant: value in ("instructions", "tool")
----

## ExpansionResult                                                <!-- Md -->

ExpansionResult(instructions: str, tools: list[str], result: str)
------
instructions: str
tools: list[str]
result: str
----

## InstallDestination                                             <!-- Md -->

The channels a member is published to, in the order a tool lists them. Each channel's annotation is a *Destination* its publisher defines, so this module names the channels and never imports the publishers.

InstallDestination
------
MCP = "mcp"
HOOK = "hook"
SKILL = "skill"
COMMAND = "command"
RULE = "rules"
LISTED: tuple[str, ...]
----

## ToolSetCollection                                              <!-- Md -->

Named child toolsets, iterated in entry order. The collection itself may have tools.

ToolSetCollection(entries: dict | None = None, parent: Any = None)
------
entries: dict[str, AgentToolSet]
parent: Any
name: str
slug: str
registration_name: str
tools: dict[str, AgentTool]
	// tools declared on the collection, not on its entries
----
attach(instance: Any, name: str | None = None): None

## Collect                                                        <!-- Md -->

`@collect` on a collection property: the same-named property gathered across the collection's children, joined as text or wrapped in the return type.

Collect(fn: Callable): property
------
----
of(collection: Any, name: str, return_type: Any): Any

## ParameterSchema                                                <!-- Md -->

The parameters a caller passes to one callable, read from its type hints, so the schema MCP publishes and the arguments it hands on agree.

ParameterSchema(callable: Callable)
------
json_schema: dict
----
coerced(arguments: Mapping): dict
	// text sent for a Path parameter becomes a Path

## AgentToolValidationError : Exception                           <!-- Md -->

AgentToolValidationError(message: str, class_name: str = "", action_name: str = "", lineno: int | None = None)
------
class_name: str
action_name: str
lineno: int | None
----

## CallNamesNoProject : Exception                               <!-- Md -->

A tool that acts on a project's objects was called without naming the project.

CallNamesNoProject(tool: str)
------
tool: str
----

## RecipeLineFailed : Exception                                   <!-- Md -->

A line of an `@agent_instructions` recipe raised while the recipe was expanded.

RecipeLineFailed(recipe: Callable, line: ast.AST, cause: BaseException)
------
recipe_name: str
line_source: str
path: str
lineno: int
----

---

## Deploy boundary (installation)                                 <!-- Mu -->

| Concern | Owner | Reads from this module |
| ------- | ----- | ---------------------- |
| Skill, command, and rules markdown | `FileInstallation` | live toolset: `description`, `tools_for(destination)`; `AgentTool.invoke_line`; `AgentInstructions.expand` |
| MCP enrollment | `McpInstallation.write` (records each operation), `McpServer` (enrolls it at start) | each member's `mcp_name`, `kind`, `description`, `parameters` |
| Runtime call | `McpServer` | `AgentTool.invoke(arguments, project=...)`, the project of the runtime the call's project names |
| Hooks | `HookInstallation`, `HookDaemon`, `HookServer` | `tools_for("hook")`, `hook_event`, `HOSTED_ONLY_CLASS_NAMES` |
