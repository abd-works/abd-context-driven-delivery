# Modules

*PromptLog* appends a read-only audit of what Cursor sent the model on hook events.
## tools.prompt_log
### Public Seam
#### PromptLog
### Dependencies
 - `harness.hooks` — uses
 - `harness.agent_tools` — uses
---

### Constraint

`@Hooks(disabled=True)` on *PromptLog* skips every audit handler.
