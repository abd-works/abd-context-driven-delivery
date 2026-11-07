# The project and the chat travel on the tool call

Supersedes the consequences of `0001-one-server-project-per-request.md` that relied on a module-level current project; the one server and the `X-CDD-Project` header stay.

The server used to set a module-level current project (`space.work_state.working_on`) and a current chat (`ChatPointer.serving`) around each request, and space code read them back. A call started from inside another, or a thread the server did not wrap, read whichever project or chat was set last, so it could log into the wrong session or act on the wrong checkout. Now the MCP server builds one `ToolCall` per request (`ToolCall.sent(arguments, project)`), holding the request's arguments, the project its header names, and the chat. Every tool, tool subject and guidance action reads the project and its session from that call. space/session registers how a call opens its sessions (`ToolCall.open_sessions_with`), so the framework reaches sessions through `call.session` without importing space.

## Considered options

- **Keep the module-level current project, made thread-local.** Rejected: it still hides which project an operation acts on, and a call that starts work on another thread loses it.
- **Pass `project` as an argument through every operation.** Rejected: the same value would be handed down through every layer, which is the state-in-parameters the Clean Engineering rules forbid; the call already holds it.

## Consequences

- `working_on`, `project_folder`, `project_checkout` and `ChatPointer.serving` are deleted; `Sessions(project)` and `Session(repo_root)` require their project.
- The server keys its toolsets by the folder the chat names; space code works out the git checkout itself.
- A call made in process with no project (a script or a spec) falls back to `CDD_PROJECT`, then the current folder.
- A session's log line reads the chat from `Session.chat`, then the environment, then writes `no-chat`.
