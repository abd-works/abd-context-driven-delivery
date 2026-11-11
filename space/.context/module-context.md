# space
*Project being worked on* is the project a call acts on: the folder the calling chat names, carried on the call's *ToolCall* (harness/agent_tools). One cdd server answers every chat, so the project belongs to the call, not to the process: every space object is handed its project, by a `@tool_subject` loader that takes the call's project or by the caller that makes it, and no space code reads a project from anywhere else.

*WorkState* is the branch, worktree, and session saved as open in a checkout's `.sessions/session.json`, by name (the branch's name, the worktree's folder, the session's name), so the repo and session commands agree on what is open after a restart as well as before it; the repository turns the names back into its *Branch* and *Worktree*. Each session's folder, `.sessions/{session}/`, holds that session's files, its design canvas, and its end-to-end results.

The work itself is kept by the child modules, each with its own card: the *Sessions* of a checkout and the *Session* an agent works in, with its log, the handoff the next agent resumes from, and its Context Decision Records (`space/session`), the *Repo* those sessions sit in, with its branches and worktrees (`space/repo`), and the *Board* that shows every session as a *Ticket* and moves it through the delivery stages (`space/kanban`, with the CDD Kanban app in `space/kanban/app`). The board is part of tracking the work, so it sits beside the session and the repo it reads.

- **Purpose:** Keep the open work of each project — its sessions, its branches and worktrees, and its board — so every tool a call runs finds the same `.sessions/` for the project the call names.
- **Seam (terms):** WorkState, `SESSIONS_FOLDER`, `E2E_RESULTS_FOLDER`
- **Dependencies (one-way):** none. `space/repo` and `space/session` save what is open through *WorkState*; it imports neither.

## Constraint

Take the project from the call: a tool's `@tool_subject` loader or class operation takes `project`, which the call fills in, and code it calls is handed that project or an object made for it. Never read it from `Path.cwd()` or a process-wide setting, because a call from another chat names another project. `CDD_PROJECT` names the project only for a call made in process that names none (a spec or a script dispatching to the cdd server); `CDD_REPO` names the CDD checkout that serves the tools, never the project. Read and write `session.json` through *WorkState* and `config.json` through *ContextConfig* (harness/installation), which keep the values other callers store there.
