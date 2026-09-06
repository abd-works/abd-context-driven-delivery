# log-mistakes-via-nonblocking-subagent

- **tool:** Eval / BaseContextTool (logged as Cdd)
- **error:** log_mistake ran inline on the parent turn and blocked the chat.
- **rule:** (process) log-mistakes-via-nonblocking-subagent
- **what changed:**
  - **Prose — no new rule bullet on a generating tool.** Logging instructions already live on utilities/eval/log_mistake.md.
  - **Code — yes.** @sub_agent on Repair.log_mistake and BaseContextTool.log_mistake so the manifest launches logging as a non-blocking sub-agent.
  - **Scanner — no.**
