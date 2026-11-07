# agent_tools — class model (model fidelity)

Markdown channel for the *AgentToolSet* primitive. The module's purpose, seam, and dependencies are in [module-context.md](module-context.md); this document holds only its classes. *AgentToolSet* is the toolset the author marks with `@agent_toolset`; its members are *AgentTool* objects — *AgentOperation* for `@agent_tool` and *AgentInstructions* for `@agent_instructions`. Writing members out to MCP, skills, commands, rules, and hooks belongs to `harness/installation`, `harness/mcp`, and `harness/hooks`; *Mark* and *Destination* belong to `harness/installation`, *Session* to `space/session`, and *Markdown* to `harness/markdown`, and they appear here only as names this module uses.

**Out of scope:** guidance actions (`harness/guidance_actions`, Generate, Validate, …) keep their own model; *GuidanceAgentOperation* is listed only because this module defines it.

---

## Language companion                                             <!-- L -->

*AgentToolSet* is the toolset a practice or tool decorates with `@agent_toolset`. Callable members are *AgentTool* subtypes: *AgentOperation* (`@agent_tool`) runs Python; *AgentInstructions* (`@agent_instructions`) expands its body into a recipe the agent follows.

Each *AgentTool* exposes `kind`, `description`, `parameters`, `response`, and `input_schema`, read from the callable, and holds the **`toolset`** that made it. Both marks use ordinary Python `self` (the toolset).

- `@agent_toolset` merges *AgentToolSet* onto the decorated class; do not subclass *AgentToolSet* directly. The class docstring is the toolset's **description**.
- Inside an `@agent_instructions` body, `tools(...)` names operations the agent calls while following the recipe, and `instructions(...)` includes another recipe inline. A recipe that includes itself is rejected when the class is decorated.
- *ExpansionMode* on the called toolset decides whether a nested recipe expands inline (`instructions`) or is listed as a tool to call (`tool`).
- `@toolset_collection` on a class makes it a *ToolSetCollection*; on a property it marks one of the toolset's collections, whose children are published as nested toolsets.
- `@tool_subject` marks the class method that loads the object a tool call acts on; `@noSessionLog` keeps a repeated read out of the session log.

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
----
tools_for(destination: str): list[AgentTool]
	-> AgentTool.install_to
child_toolsets(): Iterator[AgentToolSet]
instantiate(item: Any = None): AgentToolSet
	// item is None, a "{module}:{Class}" ref, a {toolset, context} dict, a class, or an instance
from_items(items: list, context: dict | None = None, skip_errors: bool = False): list[AgentToolSet]
	// one instance per toolset class
tool_subject_of(toolset: type): Callable | None
	// the @tool_subject loader, given the called project when it takes one
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
	// the name a @command or @skill mark gives, else name
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
invoke(arguments: dict | None = None): Any
	-> log_session_invocation(arguments)
	-> ParameterSchema.coerced
	// then call the callable
log_session_invocation(arguments: dict | None): None
	// skipped for ping calls and @noSessionLog members
	-> Session.log_agent_tool

## AgentOperation : AgentTool                                     <!-- Md -->

AgentOperation(name: str, callable: Callable, toolset: AgentToolSet)
------
	Invariant: kind == "tool"
----

## GuidanceAgentOperation : AgentOperation                        <!-- Md -->

An `@agent_tool` on a guidance action; the call is logged as the action running in its own session.

GuidanceAgentOperation(name: str, callable: Callable, toolset: AgentToolSet)
------
----
invoke(arguments: dict | None = None): Any
	-> toolset.start_call
log_session_invocation(arguments: dict | None): None
	-> toolset.call_session

## AgentInstructions : AgentTool                                  <!-- Md -->

AgentInstructions(name: str, callable: Callable, toolset: AgentToolSet)
------
	Invariant: kind == "instructions" unless the callable is also marked @agent_tool
prompt: tuple[str, ...]
tools: list[str]
	// deferred operation names from tools(...), merged with those of every nested instructions(...); read-only
result_template: str
----
for_callable(callable: Callable, instance: AgentToolSet | None = None): AgentInstructions
expand(context: dict, arguments: dict): ExpansionResult
	// raises RecipeLineFailed when a recipe line raises
invoke(arguments: dict | None = None): str
	// the instructions an agent follows for this call, with the session context of a guidance action appended
	-> expand
substitute_template(template: str, arguments: dict, parameter_names: set[str], instance: Any = None): str

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

## Name                                                           <!-- Md -->

One name written in several cases, so a class name, a toolset slug, and a published tool name always agree.

Name(text: str)
------
words: list[str]
snake: str
kebab: str
camel: str
spellings: list[str]
title_words: list[str]
title_slug: str
title_snake: str
title_pascal: str
title_camel: str
----

## ParameterSchema                                                <!-- Md -->

The parameters a caller passes to one callable, read from its type hints, so the schema MCP publishes and the arguments it hands on agree.

ParameterSchema(callable: Callable)
------
json_schema: dict
----
coerced(arguments: Mapping): dict
	// text sent for a Path parameter becomes a Path

## SubAgent                                                       <!-- Md -->

The `sub-agent.sub_agent` operation; `@subAgent` on a member prepends the hand-off instructions to its description.

SubAgent()
------
----
sub_agent(instructions: str, summary: str = ""): str

## AgentToolsProbe                                                <!-- Md -->

Checks the space, harness, and tools operations one install published, through the running MCP server.

AgentToolsProbe(installer: Installer, guidance: list[str] | None = None)
------
toolset_refs: tuple[str, ...]
published: list[str]
host: Any
	// the running CDD MCP server; raises ProbeRequiresServingHost when none is serving
----
run(): str
	// ping, invoke, and heavy invoke; on a one-off server when none is serving
run_standalone(): str
ping(): str
invoke(host: Any | None = None): str

## AgentToolsDiagnostics                                          <!-- Md -->

AgentToolsDiagnostics()
------
----
agent_tools_diagnostics(guidance: list[str] | None = None): str
	// appends results under agent_tools in diagnostics.json
	-> AgentToolsProbe.run

## AgentToolValidationError : Exception                           <!-- Md -->

AgentToolValidationError(message: str, class_name: str = "", action_name: str = "", lineno: int | None = None)
------
class_name: str
action_name: str
lineno: int | None
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
| MCP enrollment | `McpInstallation.enroll_operations` | each member's `mcp_name`, `kind`, `description`, `parameters` |
| Runtime call | `McpServer` | `AgentTool.invoke(arguments)` |
| Hooks | `HookInstallation`, `HookServer` | `tools_for("hook")`, `hook_event`, `HOSTED_ONLY_CLASS_NAMES` |
