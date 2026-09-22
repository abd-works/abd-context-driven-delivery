## Language

*Prompt echo* toasts the invoked action, practice, fidelity, or guideline on Cursor `preToolUse`. Authors mark members with `@echo`; PromptEcho writes `.cursor/prompt-echo-toast.json`.

Object model: [prompt-echo-model.md](prompt-echo-model.md).

### Echo

- Put `@echo` on an AgentOperation or AgentInstructions so that invoke toasts.
- One mark on `GuidanceAction.begin` covers every kit because every kit runs `begin`.
- **Invariant:** practice and fidelity `instructions` toast only when those members are marked — never because `begin` is marked.

### PromptEcho

- Cursor fires `preToolUse`. PromptEcho names the invoked member from Echo, or from catalog when no mark hits, then writes the IDE notice.
- **Invariant:** `show_ide_toast` joins same-burst inject lines. A later matching glob must never overwrite an earlier Guidance.

Build order: `harness/hooks` → `tools/prompt_echo`

---

# tools/prompt_echo
- **Purpose:** Mark members with *Echo* and toast the invoked action, practice, fidelity, or guideline on `preToolUse`.
- **Seam (terms):** Echo, PromptEcho
- **Dependencies (one-way):** `installation` (*Destination*), `harness/hooks` (*Hook*), `harness/agent_tools`

## Constraint

Callers mark members with `@echo`. They must not treat inherited begin as the echo for practice or fidelity instructions. They must not overwrite an earlier Guidance when joining same-burst toasts.
