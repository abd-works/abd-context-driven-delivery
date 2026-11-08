# A tool is handed the call it serves; `session_in` serves work with no call

The round-6 review (harness core, row 23) flagged `ToolCall.session_in(project)`, a class-level lookup of the session saved as open in a project, which a tool's loader had started to call (`FileManager.load`). The space review (H1) found the same shape in `Session.from_file` and `PracticeSessionOutput.load`, which built a stand-in `ToolCall(project=...)` only to open a session, so every session tool lost the chat that called it.

## Decision

- **A loader or a class tool that takes `call` is handed the call it serves**, as one that takes `project` is handed the call's project (`TakesFromCall`, `FROM_THE_CALL`). `Session.from_file`, `PracticeSessionOutput.load` and `FileManager.load` take `call` and open their session through it (`call.session_named(...)`, `call.session`), so the session they open names the calling chat, and its log lines carry it.
- **`ToolCall.session_in` stays for work that serves no call**: the agent BDD harness, which runs a request read from a spec's YAML, and the diagnostics probe, which opens the main session of a temporary project. Both read the session through the opener space/session registers (`ToolCall.open_sessions_with`), so neither imports space; neither has a chat to lose.

## Why `session_in` is not deleted

Its two remaining callers have no `ToolCall` to ask, and making one for them is the stand-in the space review rejected: a call with no chat, no arguments and no tool, built only to reach the opener. The opener is the registration seam this module declares (`SessionOpener.saved_in`), and `session_in` is the one place outside a call that reaches it.

## Consequences

- A tool that acts on a session takes `call`, never `project` plus a lookup.
- A spec that loads a session tool's subject in process makes the call it would serve, such as `FileManager.load(call=ToolCall({}, project))`.
