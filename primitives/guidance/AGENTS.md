# guidance

- Keep behavior on the class that owns the state — private instance methods, not module-level functions or `@staticmethod`.
- Base type is `Guidance` in `primitives/guidance/guidance.py` — not `ContextGuidance`.
- `@markdown` extract for `FidelityGuidance` resolves co-located files through `practice_guidance` (same module folder as the practice host), not through `guidance.py`.
- Fidelity section parsing (`fidelity_blocks`, subsection reads) lives in `primitives/markdown`; practice hosts call it, they do not reimplement regex parsers.
- Rules inlined into instructions use `RulesCollection.format_rules()` — do not duplicate formatting on the host.
- Instructions assembly is the **`instructions`** property on **`Guidance`** — join `@markdown` properties with `"\n\n".join(...)`. No assembler class or build request.
- Deploy marks (`@skill`, `@command`, `@rules`, `@agent_instructions`) stack on the same `@markdown` members as read — no import-time property patching.
