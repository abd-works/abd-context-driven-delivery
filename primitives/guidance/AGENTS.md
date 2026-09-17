# guidance

- Keep behavior on the class that owns the state — private instance methods, not module-level functions or `@staticmethod`.
- Base type is `Guidance` in `primitives/guidance/guidance.py` — not `ContextGuidance`.
- `@markdown` extract for `FidelityGuidance` resolves co-located files through `practice_guidance` (same module folder as the practice host), not through `guidance.py`.
- Read co-located markdown through `@markdown` / `Markdown.from_label`. Do not revive `Instruction`, `@instruction` slots, or `primitives/instructions`.
- Fidelity section parsing (`fidelity_blocks`, subsection reads) lives in `primitives/markdown`; practice hosts call it, they do not reimplement regex parsers.
- Rules inlined into instructions use `RulesCollection.format_rules()` — do not duplicate formatting on the host.
- **`instructions`** on **`Guidance`** is the declared install operation (`@skill` / `@command` + `@agent_instructions`). Its docstring is `context`. Install writes that docstring, not the assembled markdown. `guidance()` is the markdown section that feeds the live `instructions` string.
- Practice `fidelities` is a `GuidanceCollection` (`ToolSetCollection`). Install walks `toolset.nested_toolsets` then each child’s `tools` — not a merged parent `tools` map.
- **`Guidance.tools`** lists `@agent_instructions`, `@agent_tool`, and `@rules` members as `AgentTool` entries. A `@rules` `RulesCollection` is one tool per rule slug, with that rule’s text on `tool.docstring`. Install uses that map and `tool.destinations`.
