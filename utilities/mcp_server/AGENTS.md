# MCP server — agent rules

Lessons from correcting `mcp_server_spec.py`. Record each in the same turn as the fix.

1. **Validate with `bdd.md` rules, not scanners alone.** Judge Shared Rules and development Rules; cite rule id and lines.

2. **Labels must match the code (`context-setup-expresses-state`).** Read each `describe`, `that`/`with` label, and everything nested under it as one unit. `before.each` and Arrange must establish exactly what the label says — built, started, discovered, or invoked. Split steps into parent contexts (`that has been built` → `that has called start with an annotated @toolset class reference`) so each label matches its setup.

3. **Nested `that`/`with` must be real preconditions (`nest-by-enabling-events`).** Each branch is an enabling state — not a filing convenience. Sibling operations get sibling branches.

4. **Describe behaviors, not fixture names.** Context labels name what happened — annotated, registered, discovered, invoked, with or without parameters, with or without orchestrated `@agent_tool` references. The example toolset is wiring in the test body; it does not belong in the hierarchy unless the behavior is specifically about that class.

5. **Name decorators and server APIs in labels.** Use `@agent_tool`, `@instruction`, `start`, `list_tools`, `list_prompts`, `invoke_tool`, `invoke_prompt`. Do not hide setup behind opaque helpers.

6. **Direct attribute access on fixtures.** Use normal property access on the example class in the test body — not `getattr` with a default.

7. **Inline literals in tests.** Put MCP names and argument dicts in the test body — no module-level constants used twice.

8. **Walk `utilities/mcp_server/.context/mcp_server_spec.md` § Tests** before declaring coverage complete.

9. **No duplicate discovery contexts.** One parent per discovery kind; nest only the variant (e.g. `with no invocable parameters` → one assertion).

10. **Do not repeat a precondition in a child context.** If the parent `that`/`with` already names the state, nested examples assert outcomes directly — do not nest another label that says the same thing.

11. **Branch on the variant, then assert.** Establish the positive case in a `with` context and run its tests there; branch to the opposite variant (e.g. references vs no references, parameters vs none) as a sibling context — do not assert variant-specific outcomes at the parent level.

12. **Keep discovery-wide outcomes at the discovery parent.** Behaviors true of every discovered operation (`list_tools`, `list_prompts`) belong directly under `that has discovered … operations` on the server. Metadata (`invocable_parameters`, `prompt_text`, `referenced_tool_names`) belongs on `McpTool`, `McpPrompt`, or `McpToolset` — not on `McpServer`.

13. **Nest only when the label completes a readable sentence.** Read parent and child labels as one phrase (`that has discovered … with an @agent_tool that declares no invocable parameters should …`). If a nested `with` adds no setup and only names a second fixture, flatten it to a sibling `it` or a variant label that names the behavior. Do not file examples under `with another … on the same toolset` or repeat an invoke precondition under a child that says the same thing.

14. **`it` labels name what the assertion checks.** Say *instruction result*, *tool(...) call*, *orchestrated side effect* — not vague *output* or *include the tool result in the returned output*, which sounds like a separate channel bundling tool output into something else.

15. **Align discovery and invocation under the same situation.** Name the unique case first (`with @agent_tool operations`, `with an @instruction that references @agent_tool calls`, `with no invocable parameters`), then branch lifecycle children (`that has discovered them` / `that has discovered it`, `that has invoked it through invoke_prompt`). Do not file parallel top-level `that has discovered …` and `that has invoked …` contexts that repeat the same variant label.

16. **Assert the naming rule positively.** An MCP name is `{toolset_slug}.{operation_name}` — e.g. `bdd.find_examples`. State that directly (`should put a dot between the slug and the operation`); do not use roundabout `expect(x == wrong_form).to(equal(False))` when one positive `expect(name).to(equal("bdd.find_examples"))` already pins the convention.

17. **Put `mcp_name` on the binding, not in a separate class.** `ToolBinding` and `InstructionBinding` remember `toolset_name` and `method_name`; `mcp_name` is a property that formats `{toolset_name}.{method}`. Read `toolset_name` from `instance.toolset_name` on the CDD toolset — no static slug helper on the binding.

18. **Name public types publicly once.** If a class is on the module seam (`__all__`, imports from `mcp_server`), define it as `McpServer` — not `_McpServer` with `McpServer = _McpServer` at the bottom. Reserve leading `_` for implementation-only helpers (`_BindingCatalog`, `_McpRuntimeContext`).

19. **Use MCP primitive names on the public seam.** `McpTool` (MCP tool) and `McpPrompt` (MCP prompt from CDD `@instruction`). Do not expose `*Binding` types — binding/register is internal (`from_method`, `register_on`).

20. **Resources respond; the server finds and delegates.** `McpTool.invoke` and `McpPrompt.invoke(server, …)` run the work. `McpServer` loads CDD instances, enrolls `McpToolset` wrappers, finds by `mcp_name`, delegates. No catalog or loader classes.

23. **`McpToolset` is the CDD→MCP bridge, not an MCP primitive.** One loaded `@toolset` instance → one `McpToolset` that discovers `McpTool` / `McpPrompt` per operation and `register_on(server)`. MCP has no toolset type; this is our adapter. Discovery loop lives on `McpToolset`, not `McpServer.start`.

21. **MCP has no tool+prompt superclass.** MCP **primitives** are tools, prompts, and resources separately. Shared identity lives in private `_McpPrimitive` only — do not invent a public domain type for it.

22. **Construct from the bound method on the toolset.** `McpTool(instance.increment)` — one argument already on the instance; constructor reads `toolset_name` from `bound.__self__`. Do not pass instance and unbound `member` separately. Discovery loop lives on `McpToolset`.

24. **No metadata lookup on `McpServer`.** Do not add `prompt_for`, `invocable_parameters_for`, or CDD aliases. Host wire is `list_*` + `invoke_*` by name; read `McpTool` / `McpPrompt` off `McpToolset.tools` / `.prompts`.

25. **Test the host before the domain.** Follow `testing-approach.md`: manual stdio discovery first (`scripts/discover_host.py`, session notes), then `mcp_server_host_spec.py` (real subprocess + MCP Client). Domain behavior stays in `mcp_server_spec.py`.

26. **stdio + `mcp==1.30.0`.** Local Cursor hosts use stdio, not SSE. `McpHost` delegates to `McpServer`; use `get_type_hints()` for JSON Schema — string annotations from `from __future__ import annotations` are not real types.

27. **Dual-register `@instruction` orchestration on `tools/list`.** MCP hosts discover runnable work through `tools/list`; also expose each `McpPrompt` there (still listed in `prompts/list` for docstring discovery). `tools/call` routes prompt names to `invoke_prompt`.

28. **JSON Schema must match the Python parameter type.** After resolving hints, map `list`/`Sequence`/`tuple` to `array`, `dict`/`Mapping` to `object`, `bool` to `boolean`, `int` to `integer`, `float` to `number`, `str` to `string`, and `X | None` / unions to `anyOf`. Anything else advertised as `string` makes the host send a string; Python then walks characters (`"list"` → `'l'`) instead of loading `module:Class` refs.

29. **Write specs with normal Python spacing.** One blank line between sibling `with` blocks and between top-level functions. Do not put a blank line after every statement — that doubles the file and hides the describe/it hierarchy.
