# agent_tools — class model (model fidelity)

Markdown channel for the *AgentToolSet* primitive. Target design: root *AgentToolSet* owns *AgentTool* members — subtypes *AgentOperation* and *AgentInstructions*. **Wire-out** lives in `installation` — not in this module.

**Out of scope:** manifest CLI, `Cls.manifest`, `for_introspection`, `instantiate_refs`, YAML front-matter fences, `run_request`, `ToolsetExtensions`, JSON Schema / MCP shapes on members, **`@resource`**, **`@focus` / `focus_entries`**, **`@instruction` / instruction slots / `_inline`** (markdown lives in string literals inside `@agent_instructions` bodies or in harness deploy — not a third member type), parallel `*Reader` / `*Catalog` / `*Validator` / `*Expander` doer classes, **`listed()` / `_tool_items` / session batch orchestration**, and **guidance action kits** (`harness/guidance_actions`, Generate, Scan, SubAgent, …). Those kits keep their own model; this document does not change them. Persistent server state between MCP calls is the server's job — not a domain member type.

**Only two member marks exist:** `@agent_tool` → *AgentOperation*; `@agent_instructions` → *AgentInstructions*. Nothing else is a toolset member in this module.

**Interfaces:** Clean Engineering treats a separate `I{Class}` contract as optional — add one only when asked.

---

## Language companion                                             <!-- L -->

*AgentToolSet* is the root a practice decorates with `@agent_toolset`. Callable members are *AgentTool* subtypes: *AgentOperation* (`@agent_tool`) runs Python; *AgentInstructions* (`@agent_instructions`) expands its body statically.

Each *AgentTool* exposes introspection fields — `kind`, `description`, `parameters`, `response` — read from the callable. Each member holds a **`toolset`** reference to the parent *AgentToolSet* instance that created it. **`@agent_tool` and `@agent_instructions` both use normal Python `self` (the toolset).** Member **description** is docstring prose for deploy and introspection; do not confuse it with *AgentInstructions* or expansion output. Read `description`, `operations`, `instructions`, or `tools` on a live *AgentToolSet* instance — no aggregate dict in this module.

### agent_toolset                                              <!-- L -->

- One root — do not split a “tool-only” set from an “agent” set. <!-- L -->
- `@agent_toolset` merges *AgentToolSet* behavior onto the decorated class. <!-- L -->
- Class docstring is toolset-level **description**. <!-- L -->
- **Invariant:** A member has exactly one mark — `@agent_tool` or `@agent_instructions`. No `@resource`, `@instruction`, or `@focus` on toolset members. <!-- L -->

### agent_operation                                            <!-- L -->

- `@agent_tool` — body **runs as Python** when called on a toolset instance. <!-- L -->
- Modeled as *AgentOperation* : *AgentTool*. <!-- L -->

### agent_instructions                                         <!-- L -->

- `@agent_instructions` — unwrapped body code **runs during expand** to build instructions; `tools(...)` and `instructions(...)` are handled by the expander without running their targets. **First parameter must be `self`** (the toolset), same as `@agent_tool`. <!-- L -->
- Prose in the expanded runbook comes from string literals in the body and from wrapped member calls — not from `@instruction` slots or focus file injection. <!-- L -->
- **Wrappers (required for defer/expand):** `tools(...)` defers to agent invoke (`@agent_tool` semantics); `instructions(...)` expands inline (`@agent_instructions` semantics) and **walks that nested body recursively**. Unwrapped code runs during expand. <!-- L -->
- Orchestration uses **toolset state on `self`** (for example `self.cars` populated by constructor or `@agent_tool` add/remove) — not a framework-injected peer list. <!-- L -->
- Modeled as *AgentInstructions* : *AgentTool*. <!-- L -->
- **`tools`** (read-only) — walk the `@agent_instructions` body; collect deferred names from `tools(...)`; for each `instructions(...)`, walk that nested *AgentInstructions* and **merge its tools**. Any caller can ask one action what it defers without running `expand`. <!-- L -->
- **`toolset`** is set when the parent builds its `instructions` registry — not passed again on `expand`. <!-- L -->
- **Invariant:** First parameter name is **`self`**. <!-- L -->
- **Invariant:** **Cycles** in nested `instructions(...)` calls rejected at validation or expansion — nesting itself is allowed. <!-- L -->
- Action-body validation runs on the **toolset** at decorate time — not a method on *AgentInstructions*. <!-- L -->

### expansion_mode                                             <!-- L -->

- On the **callee** *AgentToolSet* instance (`mode` field). <!-- L -->
- `instructions` — nested `@agent_instructions` expand inline; `tool` — defer to tools list. <!-- L -->
- Ordinary toolset state — not a separate member. <!-- L -->

### introspection                                              <!-- L -->

- *AgentToolSet* instance (via `instantiate(context)`): `name`, `description`, `operations`, `instructions`, `tools`. <!-- L -->
- Cross-call collections and relationships (for example `cars`, `addCar`, `removeCar`) are ordinary toolset fields and `@agent_tool` members — not framework list injection. <!-- L -->

## Modules                                                        <!-- Mu -->

Build order: `agent_tools` only. One-way consumer: `installation`.

---

# agent_tools                                                     <!-- Mu -->

- **Purpose:** Register, introspect, and validate one decorated *AgentToolSet* and its members. <!-- Mu -->
- **Seam (terms):** AgentToolSet, AgentTool, AgentOperation, AgentInstructions, `@agent_toolset`, `@agent_tool`, `@agent_instructions` <!-- Mu -->

## AgentTool                                                     <!-- Md -->

AgentTool(name: str, callable: Callable, toolset: AgentToolSet)
------
name: str
toolset: AgentToolSet
	Invariant: parent *AgentToolSet* that owns this member; set when the toolset builds operations or instructions on a live instance
kind: str
description: str
	Interaction:
		return member_description(callable)
parameters: dict[str, str]
	Interaction:
		return parameter names and type names from the callable
response: str | None
	Interaction:
		return callable return type name when present

## AgentOperation : AgentTool                                    <!-- Md -->

AgentOperation(name: str, callable: Callable, toolset: AgentToolSet)
------
	Invariant: kind == "tool"
----
invoke(arguments: dict): Any
	Interaction:
		return callable(**arguments)

## AgentInstructions : AgentTool                                 <!-- Md -->

AgentInstructions(name: str, callable: Callable, toolset: AgentToolSet)
------
	Invariant: kind == "instructions"
----
expand(context: dict, arguments: dict): ExpansionResult
	Interaction:
		walked = _scan(callable, instruction=self, context, arguments)
		return ExpansionResult(instructions=walked.instructions, tools=self.tools, result=walked.result)
tools: list[str]
	Invariant: read-only — not set by expand
	Interaction:
		return _collect_deferred_tools(callable, instruction=self)
- _parse_body(callable: Callable): ast.Module
- _scan(callable, instruction, context, arguments, visited): WalkResult
	Interaction:
		for each `tools(...)` in body: collect deferred @agent_tool names
		for each `instructions(...)` in body: _scan on nested member (merge prose); _collect_deferred_tools on nested member (merge tools)
		reject if visit_key already in visited (cycle)
- _collect_deferred_tools(callable, instruction, visited): list[str]
	Interaction:
		for each `tools(...)` in body: collect deferred @agent_tool names
		for each `instructions(...)` in body: extend with _collect_deferred_tools on nested member
		reject if visit_key already in visited (cycle)

## ExpansionMode                                                 <!-- Md -->

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

## AgentToolSet                                                   <!-- Md -->

AgentToolSet()
------
description: str
	Interaction:
		return (self.__class__.__doc__ or "").strip()
name: str
	Interaction:
		return slugify(type(self).__name__)
<< aggregation >> operations: dict[str, AgentOperation]
	Interaction:
		for each @agent_tool on this instance, build AgentOperation(..., toolset=self)
instructions: dict[str, AgentInstructions]
	Interaction:
		for each @agent_instructions on this instance, build AgentInstructions(..., toolset=self)
tools: dict[str, AgentTool]
	Interaction:
		return merge(operations, instructions)
mode: ExpansionMode
----
instantiate(context: dict): AgentToolSet
	Interaction:
		return cls(**context)
validate(): None
	Invariant: Runs at `@agent_toolset` decorate time on the **class** — before any live toolset instance exists
	Interaction:
		allowed: set[str] = operation names | instruction names on cls
		for each @agent_instructions method on cls:
			body = _parse_body(method)
			_InstructionBodyValidator(body, allowed, method.__name__)
- _parse_body(callable: Callable): ast.Module
- _InstructionBodyValidator(body, allowed, action_name): None

---

## Deploy boundary (installation)                           <!-- Mu -->

| Concern | Owner | Reads from domain |
| ------- | ----- | ----------------- |
| Skill/command markdown | `FileInstallation` | live toolset: `description`, `tools`; `toolset.instructions[name].expand(context, arguments)` |
| MCP enrollment | `McpInstallation` | live toolset; reads each member's `kind`, `description`, `parameters`, `response` |
| Runtime call | `McpServer` | `toolset.<operation>(**arguments)` |
| Server state between calls | `McpServer` | toolset instance lifetime — not domain `@resource` entries |

---

## Requirements trace (code → model)                              <!-- Mu -->

| Requirement | Source in code | Model placement |
| ----------- | -------------- | --------------- |
| Root toolset | `AgenticToolset`, `@agentic_toolset` | `AgentToolSet` |
| Member base | `_Tool`, `ToolSetMember` | `AgentTool` |
| Execute vs expand | `@agent_tool` / `@agent_instructions` | `AgentOperation` / `AgentInstructions` : `AgentTool` |
| Toolset name | `toolset_name`, `domain_slug` (slugified class name) | `AgentToolSet.name` |
| Toolset description | `AgenticToolset.instructions` | `AgentToolSet.description` |
| Member description | `_Tool.instructions`, `_SignatureReader.member_instructions` | `AgentTool.description`, `member_description()` |
| Member introspection | `_Tool.signature_entry`, `AgentTool.owner`, `tool_steps` | `AgentTool.toolset`; `.kind`, `.description`, `.parameters`, `.response`; retire `tool_steps` → read-only `AgentInstructions.tools` (body walk) |
| Toolset introspection | `Cls.manifest`, `tools`, `agent_tools` | `instantiate(context)` → `operations`, `instructions`, `tools` |
| Nested `@agent_instructions` walk | `AgentInstructions._scan`, `_expand_member`, `_check_and_advance_visited`; nested `instructions(...)` merges deferred tools into parent | `_scan` / `.tools`: `instructions(...)` walks nested action and merges tools; cycles rejected |
| Deferred tool names | `_AgentToolBody.tool_steps`, `AgentTool.signature_entry["tools"]` from `parse_body` | read-only `AgentInstructions.tools` via body walk (same merge rules as expand) |
| Action-body validation | `AgentToolSet._InstructionBodyValidator`, `_validate_action` | `AgentToolSet.validate()` at decorate time — not on *AgentInstructions* |
| Expansion mode | `@resource` `mode` property (`"action"` in code) | `AgentToolSet.mode` — values `"instructions"` \| `"tool"` (rename `"action"` → `"instructions"`) |
| Retire from agent_tools | `@resource`, `@instruction`, `@focus`, `signature`, `_ManifestBuilder`, `manifest` classproperty, `for_introspection`, `instantiate_refs`, `listed`, `_tool_items`, manifest CLI, `run_request`, runners, extensions | delete from this module; harness uses live toolsets; lifecycle kits keep batch orchestration outside this model |

## Target state vs current code                                    <!-- Mu -->

1. **Rename root** — `AgenticToolset` → `AgentToolSet` (root type; not a member type).
2. **Rename member base** — `_Tool` / `ToolSetMember` → `AgentTool`; subtypes `AgentOperation` | `AgentInstructions` only.
3. **Rename prose** — `.instructions` → `.description` on toolset and members; `member_instructions()` → `member_description()`. **`ExpansionResult.instructions`** stays — expanded runbook output, not description prose.
4. **Drop manifest** — retire `Cls.manifest`, `for_introspection`, `instantiate_refs`, manifest CLI, fenced YAML, `_ManifestBuilder`, `signature_entry`, `add_to_signature`. Introspection is `instantiate(context)` on a real toolset — tests follow prod.
5. **Rename registries** — `tools` → `operations`; `agent_tools` → `instructions`; `toolset_name` / `domain_slug` → `name`.
6. **Drop resources** — retire `@resource`, `_Resource`, `resource_entries`, `resources`. MCP server holds toolset instances; cross-call state is server-managed.
7. **Drop focus** — retire `@focus`, `_focus_entries`, `_inject_focus` from expander.
8. **Drop instruction slots** — retire `instruction_slot_names`, `_inline`, and `@instruction` as allowed action-body steps. Prose in an expanded action = string literals + `tools(...)` + `instructions(...)` + loops over `self.<collection>`.
9. **Drop list injection** — retire `listed()`, `_tool_items`, and `arguments.tools` binding on *AgentToolSet*. Orchestration toolsets own their collections; lifecycle action kits are unchanged and out of scope here.
10. **Validate on toolset** — `AgentToolSet.validate()` at decorate time scans **class** methods via `_InstructionBodyValidator`; scan logic is private to the toolset module.
11. **`self` on actions** — `@agent_instructions` first parameter is **`self`** (the toolset instance), same as `@agent_tool`. The expander binds `self` to the owning toolset during hybrid body execution.
12. **Rename action → instructions** — member `kind` and expansion `mode` value `"action"` → `"instructions"` (default `"instructions"`).
13. **Retire tool_steps** — deferred ops are *AgentInstructions* `.tools` (read-only walk) and *ExpansionResult* `.tools` (same list from `expand`, does not mutate the member).
14. **Retire** — doer classes, invoke bus, `_Tool.manifest`.
15. **Decorator** — `@agentic_toolset` → `@agent_toolset` (when code catches up).
