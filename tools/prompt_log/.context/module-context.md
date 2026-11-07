# tools/prompt_log
*PromptLog* is a read-only audit of what the IDE sends the model — submitted prompts with their attachments, files read into context, tool calls, sub-agent tasks, and agent responses — appended to `prompt-log.txt` in the log folder of the session open in the project being worked on, so a person can see afterwards exactly what the model was given. It handles the hooks `beforeSubmitPrompt`, `beforeReadFile`, `preToolUse`, `subagentStart`, and `afterAgentResponse`.

- **Purpose:** Record what crossed to the model during a session without changing it.
- **Seam (terms):** PromptLog
- **Dependencies (one-way):** `harness/agent_tools`, `harness/hooks` (*Hook*, *Hooks*), `space/session` (*Sessions*, for the session open in the project the hook fired in)

## Constraint

*PromptLog* ships turned off with `@Hooks(disabled=True)`; remove that mark to turn the audit on. Its hooks only read the payload and never change what is sent. A *PromptLog* made with a log file writes there; otherwise it writes to `prompt-log.txt` in the logs folder of the session open in the event's project. Each event's entry is a *PromptLogEntry*, and each file an event names is a *LoggedFile*, which says what kind of guidance it is.
