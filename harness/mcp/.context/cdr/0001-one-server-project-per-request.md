# One cdd server for every chat, with the project named on each request

Every chat used to start its own stdio cdd server from whichever worktree last ran the install, with its project fixed when the process started; reinstalling rewrote `~/.claude.json` and dropped cdd in every open chat. Now one server, installed from `~/.cdd/`, answers every chat over HTTP, and each request names its chat's project in the `X-CDD-Project` header. Claude Code gets that header from `~/.cdd/connect.py`, its `headersHelper`, which Claude Code runs in the chat's own folder before connecting (checked against Claude Code 2.1.309), and the same script starts the server when none answers.

## Considered options

- **A project-level `.mcp.json` per worktree carrying the header.** Rejected: `.mcp.json` is not checked in, so every new worktree would need an install before cdd knew its project, and a project-level `cdd` entry outranks the user-level one.
- **An explicit `project` argument on every tool.** Rejected: every tool schema grows a parameter agents forget to pass, and the cdd-board mod's calls would all need it too.
- **A `PreToolUse` hook that writes the project into each call's arguments.** Rejected: the mod's `$.mcp.call` does not go through tool hooks, and every call would pay for a hook run.

## Consequences

The first two consequences below are superseded by `0002-the-project-travels-on-the-tool-call.md`: the project and the session now travel on each call's *ToolCall*, and `space.work_state.working_on` is deleted.

- The server keeps one set of toolset objects and one current session per project, because toolsets hold state between calls.
- A call outside the server (a script or a spec) names its project with `space.work_state.working_on`, or falls back to `CDD_PROJECT`, then the current folder.
- Installing from a worktree never changes the serving code. A plain install from the main checkout pins its commit when the server is pinned to an older one; `--pin-runtime` pins without the full install, and `--serve-from-checkout` serves the checkout on disk.
