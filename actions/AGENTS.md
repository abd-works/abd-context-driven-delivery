# Action kits

Action kits declare one public **`@agent_instructions`** recipe per action — the method the user invokes — and any **`@agent_tool`** the runtime should call. Mark each of those **`@Mcp`** and **`@Skill`**. Helpers (`generate_output`, `begin`, `grill_with_context`, `partition_corpus`, …) stay unmarked so install does not publish them.

Lifecycle actions live here: `validate`, `scan`, `generate`, `satisfy`, `render`, `iterate`, and the rest of this tree. `Rule` / `RulesCollection` belong on the scan kit (`actions/scan/rule.py`) because scan and validate honor those same objects. Do not invent a `practices/agent_toolset` package for them — that name collides with the `@agent_toolset` decorator in `harness/agent_tools` and splits the action from its kit.

## Listed toolsets in a recipe

When an action takes a ``guidance: str | list`` argument, call ``self.run(guidance, operation, action=...)``. Lifecycle begins the turn, runs ``operation`` once on a string or once per Guidance host, then ends. Do not copy the string-vs-list walk into each recipe.

```python
def generate(self, guidance: GuidanceArg) -> str:
    self.run(guidance, self._generate_item, action="generate")
    return "When done, run validate."
```

That expands each host to MCP tool steps and prompt content — do not load toolsets in the actions layer.

**``Toolset.listed()``** lives in `harness/agent_tools/tool.py`. **``instantiate_refs(refs)``** is for callers that already hold explicit refs (CLI bring-in), not for recipe bodies.

Do not add practice/context-tool loading to **`AgenticToolset`** in `harness/agent_tools/action.py`.
