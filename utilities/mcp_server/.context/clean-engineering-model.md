---
fidelity: [model]
artifact: [clean_engineering]
format: py
---

**Sources / context:** `utilities/mcp_server/.context/mcp_server_spec.md`; `utilities/mcp_server/.context/clean-engineering-modules.md`; `utilities/mcp_server/.context/module-context.md`

Model fidelity lives in `utilities/mcp_server/mcp_server.py` (Python channel).

## Language

*McpServer* boots a persistent local MCP process, loads annotated toolsets from the repository working tree, registers AI-callable operations and agent guidance, and invokes bound Python callables directly. It remembers loaded toolset instances so repeated MCP calls preserve instance state.

*ToolsetLoader* discovers annotated CDD toolset classes, constructs them, and collects bound members into catalogs. It derives each toolset slug from `TOOLSET_SLUG` or the hosting module name.

*McpToolCatalog* and *McpInstructionCatalog* are in-memory registries keyed by dotted MCP name. *ToolBinding* and *InstructionBinding* are the registration records the catalogs hold.

*McpNameFormatter* always emits `{toolset_slug}.{method_name}` dotted names and never replaces dots with underscores.

- **Invariant:** dotted MCP names are the only exposed identifiers (`bdd.find_examples`, not `bdd_find_examples`)

### mcp_server

- Holds the MCP boundary: discovery, registration, and direct invocation without YAML or CLI dispatch
- Collaborates with `primitives.tools` for `@toolset` / `@agent_tool` discovery and with instruction orchestration via `tool(...)` during `@instruction` invocation

### tool_binding

- Records one AI-callable operation registered for MCP discovery
- Exposes invocable parameter names derived from the bound callable signature

### instruction_binding

- Records one agent-guidance operation registered for MCP discovery
- Holds prompt text, referenced AI tool names discovered from `tool(...)` calls, and the bound callable executed on invocation

### mcp_name_formatter

- Owns dotted-name formatting from toolset slug and method name

## Modules

Build order: `primitives.tools` | `primitives.instructions` → `mcp_server`

---

# utilities/mcp_server
- **Purpose:** MCP-native runtime that discovers CDD `@tool` and `@instruction` members, registers them with MCP, and invokes `@tool` callables directly.
- **Seam (terms):** McpServer, McpToolCatalog, McpInstructionCatalog, ToolsetLoader, ToolBinding, InstructionBinding, McpNameFormatter
- **Dependencies (one-way):** `primitives.tools`, `primitives.instructions`; MCP SDK adapter (internal)

## ToolBinding

ToolBinding records one AI-callable operation exposed under a dotted MCP name.

ToolBinding(mcp_name: str, toolset_slug: str, method_name: str, callable: Callable[..., Any], description: str)
------
mcp_name: str
toolset_slug: str
method_name: str
description: str
----
invocable_parameters(): tuple[str, ...]

## InstructionBinding

InstructionBinding records one agent-guidance operation and its discovery metadata.

InstructionBinding(mcp_name: str, toolset_slug: str, method_name: str, prompt_text: str, referenced_tool_names: tuple[str, ...], callable: Callable[..., Any])
------
mcp_name: str
toolset_slug: str
method_name: str
prompt_text: str
referenced_tool_names: tuple[str, ...]
----

## McpNameFormatter

McpNameFormatter derives stable dotted MCP names from CDD toolset identity.

McpNameFormatter()
------
----
format(toolset_slug: str, method_name: str): str

## McpToolCatalog

McpToolCatalog is the registry of AI tool bindings keyed by dotted MCP name.

McpToolCatalog()
------
bindings: dict[str, ToolBinding]
----
register(binding: ToolBinding): None
binding_for(mcp_name: str): ToolBinding | None
names(): tuple[str, ...]

## McpInstructionCatalog

McpInstructionCatalog is the registry of agent guidance bindings keyed by dotted MCP name.

McpInstructionCatalog()
------
bindings: dict[str, InstructionBinding]
----
register(binding: InstructionBinding): None
binding_for(mcp_name: str): InstructionBinding | None
names(): tuple[str, ...]

## ToolsetLoader

ToolsetLoader discovers toolsets, constructs instances, and collects MCP bindings.

ToolsetLoader(name_formatter: McpNameFormatter, toolset_loader: _ToolsetLoader)
------
name_formatter: McpNameFormatter
----
load_instances(toolset_refs: tuple[str, ...], constructor_context: dict[str, Any] | None): tuple[Any, ...]
	-> _ToolsetLoader.load(ref)
collect_tool_bindings(instance: Any): tuple[ToolBinding, ...]
	-> McpNameFormatter.format(slug, name)
collect_instruction_bindings(instance: Any): tuple[InstructionBinding, ...]
	-> McpNameFormatter.format(slug, name)
toolset_slug(instance: Any): str

## McpServer

McpServer is the persistent local MCP server for CDD tool and instruction discovery.

McpServer(tool_catalog: McpToolCatalog, instruction_catalog: McpInstructionCatalog, loader: ToolsetLoader, name_formatter: McpNameFormatter)
------
tool_catalog: McpToolCatalog
instruction_catalog: McpInstructionCatalog
loader: ToolsetLoader
name_formatter: McpNameFormatter
instances: dict[str, Any]
----
start(toolset_refs: tuple[str, ...], constructor_context: dict[str, Any] | None): None
	-> ToolsetLoader.load_instances(toolset_refs)
	-> ToolsetLoader.collect_tool_bindings(instance)
	-> ToolsetLoader.collect_instruction_bindings(instance)
list_tools(): tuple[str, ...]
	-> McpToolCatalog.names
list_instructions(): tuple[str, ...]
	-> McpInstructionCatalog.names
instruction_for(mcp_name: str): InstructionBinding | None
	-> McpInstructionCatalog.binding_for(mcp_name)
invocable_parameters_for(mcp_name: str): tuple[str, ...]
	-> ToolBinding.invocable_parameters
invoke_tool(mcp_name: str, arguments: dict[str, Any] | None): Any
	-> ToolBinding.callable
invoke_instruction(mcp_name: str, arguments: dict[str, Any] | None): Any
	-> InstructionBinding.callable
