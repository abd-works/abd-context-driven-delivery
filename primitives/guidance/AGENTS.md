# guidance

- Keep behavior on the class that owns the state — private instance methods, not module-level functions or `@staticmethod`.
- Base type is `Guidance` in `primitives/guidance/guidance.py` — not `ContextGuidance`.
- `@markdown` extract for `FidelityGuidance` resolves co-located files through `practice_guidance` (same module folder as the practice host), not through `guidance.py`.
- Read co-located markdown through `@markdown` / `Markdown.from_label`. Do not revive `Instruction`, `@instruction` slots, or `primitives/instructions`.
- Fidelity section parsing (`fidelity_blocks`, subsection reads) lives in `primitives/markdown`; practice hosts call it, they do not reimplement regex parsers.
- Rules inlined into instructions use `RulesCollection.format_rules()` — do not duplicate formatting on the host.
- Instructions assembly is the **`instructions`** property on **`Guidance`** — that is the declared operation (`@skill` / `@command` + `@agent_instructions`). `guidance()` is the markdown section that feeds it, not an installed tool.
- Practice `fidelities` is a `GuidanceCollection` (`ToolSetCollection`). Install walks `toolset.nested_toolsets` then each child’s `tools` — not a merged parent `tools` map.
