## Language

*Prompt notify* toasts the invoked action, practice, fidelity, or guideline on Cursor `preToolUse`. Authors mark members with `@echo`; PromptNotify writes `.cursor/prompt-notify-toast.json`.

Object model: [prompt-notify-model.md](prompt-notify-model.md).

### Echo

- Put `@echo` on an AgentOperation or AgentInstructions so that invoke toasts.
- One mark on `GuidanceAction.begin` covers every kit because every kit runs `begin`.
- **Invariant:** practice and fidelity `instructions` toast only when those members are marked — never because `begin` is marked.

### PromptNotify

- Cursor fires `preToolUse`. PromptNotify names the invoked member from Echo, or from catalog when no mark hits, then writes the IDE notice.
- **Invariant:** `show_ide_toast` joins same-burst inject lines. A later matching glob must never overwrite an earlier Guidance.

Build order: `harness/hooks` → `tools/prompt_notify`

---

# tools/prompt_notify
- **Purpose:** Mark members with *Echo* and toast the invoked action, practice, fidelity, or guideline on `preToolUse`.
- **Seam (terms):** Echo, PromptNotify
- **Dependencies (one-way):** `installation` (*Destination*), `harness/hooks` (*Hook*), `harness/agent_tools`

## Constraint

Callers mark members with `@echo`. They must not treat inherited begin as the echo for practice or fidelity instructions. They must not overwrite an earlier Guidance when joining same-burst toasts.
