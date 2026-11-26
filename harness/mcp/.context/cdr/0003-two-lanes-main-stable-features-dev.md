# Two lanes: main runs stable, every other session runs the one served feature

Builds on `0001-one-server-project-per-request.md` and `0002-the-project-travels-on-the-tool-call.md`: one cdd server answers every chat, and each call carries its own project, so tickets, sessions and the board already work per worktree. What every chat shares is the code the server runs, which `~/.cdd/runtime.json` names.

Several CDD features are often in progress at once, each in its ticket's worktree on its own branch. Until now, running a feature's change meant merging it to main and pinning main. Main then filled up with unfinished work just so it could be tried, and a plain install from the main checkout moved the server back to main while a feature was being tried. Pinning a feature instead would have put every chat, main's included, on half-finished code.

## Decision

- **Two lanes, each a cdd server with its own home and port.** `CDD_HOME` and `CDD_SERVER_PORT` are already settings.
  - **Stable lane:** `~/.cdd`, pinned to main. It serves only chats in the main checkout, and it moves only when main does.
  - **Dev lane:** a second home, serving the one served feature. It serves every other chat: every ticket worktree and every session that is not main.
- **Every session is in the dev lane by default, except main.** Which lane a call goes to depends on its project, the folder the `X-CDD-Project` header names: the main checkout goes to the stable lane, and anything else goes to the dev lane. Nobody chooses a lane per chat, so nobody can choose the wrong one.
- **Features are developed side by side.** Each ticket keeps its own worktree and branch (`ticket.activate`). Writing code, running unit specs and committing on a feature need no change to either server.
- **The dev lane runs one feature at a time, the served feature.** Serving a feature pins its branch tip directly from its worktree; `CddHome.pin` already fetches the worktree's `HEAD`. While the feature's code is changing quickly, the dev lane serves the worktree as it is on disk instead. Main is not involved either way.
- **The dev lane's runtime record names the served feature.** `runtime.json` records the branch and the worktree beside the commit, so any chat can tell which feature it is running against.
- **Switching the served feature is coordinated between chats.** The chat that wants to switch lists the other dev-lane chats. Each one that is running must give a go before the switch. The switch restarts only the dev lane and tells the other chats which feature now runs. Main's chats are never interrupted.
- **Finishing a feature** merges its branch to main and repins the stable lane to main. Then the dev lane serves the next feature, or main until another feature is served.

## Considered options

- **Merge to main to run anything.** Rejected: main becomes the bottleneck every feature competes for, and unfinished work lands there only so it can be run.
- **One server, repinned to whichever feature runs.** Rejected: main's chats, the ones that keep the board and releases working, would run half-finished feature code too.
- **One server per worktree.** Rejected: several runtimes, several ports, and chats that cannot tell which server they are talking to. That is the setup that became unmanageable before.

## Consequences

- Main's chats always run main. Every other chat runs the served feature's code, including chats working on a different feature. When the served feature breaks the board, those chats can still use main's session, or the dev lane can be pinned back to main.
- Work this decision needs:
  - **Routing by project.** Built: every Claude Code chat reaches cdd at one address, the user-level `cdd` plugin, and Claude Code runs `connect.py` only to set headers, so the stable lane's server hands each tool call whose project belongs to the dev lane to the dev lane's server (`POST /lane-call`, `ServerLane.answer`). It does this per call, not per HTTP request, because a call's project comes from the chat's process as well as the header. It starts the dev lane's server when none answers. Until a feature is served on the dev lane, the stable lane answers those calls itself, on main. Still open: the tool list a chat sees is the stable lane's, so a tool only the served feature has does not show, and progress reports from a dev-lane call do not reach the chat.
  - **The dev home.** Installing it, starting it, and repinning it from a worktree (`install.py --pin-runtime --lane dev` or similar).
  - `CddHome.pin` and `serve_from` record the branch and the worktree in `runtime.json`.
  - `ServedCode.keep_pinned_current` (`harness/mcp/mcp_daemon.py`) keeps the stable lane on main only. Today it pins the main checkout's commit into the single home.
  - A switch operation that checks the other dev-lane chats before it restarts. Today that check is done by hand.
  - `ticket.activate` may offer to serve the ticket's branch on the dev lane. It never switches without asking.
- Both lanes register the same apps, so the dev lane's app servers answer `ServerLanes.DEV_APP_PORT_OFFSET` (1000) above the ports their ports files give them: `AppServer.ports` is the lane's, and `AppServer.command` names the first with `--port`, which every app's server reads before its env variable and its ports file (`harness/graph/app/serve-port.ts`). The lane is the one the server's home is (`ServerLane.from_home`). The chat bar's check-ins stay on the stable board.
- A lane's server outlives the chat that started it: where the chat's Windows job refuses breakaway, `BackgroundStart` creates the process through WMI (`Win32_Process.Create`), outside every job.
- The cdd-board mod is published from the code a server runs (`ClaudeMarketplace.publish_mods`, which publishes every mod that code declares in a `cdd-mod.json`, the prompt queue mod beside it). With two lanes, each lane publishes its mods into its own marketplace only (`~/.cdd/claude-plugins` and `~/.cdd/dev/claude-plugins`), on install and on its server's restart. A feature's mods are never published into the stable lane's marketplace: published there, they gave main's chats a button their server could not serve (issue 105, the prompt queue's Flush calling `prompt-queue.flush`).
- Claude Code loads each cdd plugin from one fixed folder per plugin, `~/.cdd/chat-plugins/{name}`, which its user settings name in `CLAUDE_CODE_PLUGIN_DIRS`, never from its own plugin cache, whose copy keeps the version it was installed at. Every install and every repin points that fixed folder at the published folder of the stable lane, the lane whose server every chat's `cdd` plugin names (a directory junction on Windows, which needs no special rights; a symbolic link elsewhere), for the `cdd` plugin and every mod alike. The settings name the same folder after the first time, so a repin followed by `/reload-plugins` reaches every chat with no cached copy and no restart of the Claude app; only the first install, which names the folder in the settings, needs the app restarted.
- There is one fixed folder per plugin, not one per lane, and a mod calls the server the `cdd` plugin names, so a lane is loaded whole. Loading the dev lane's mods while the `cdd` plugin named the stable server gave every chat a chat bar calling `session.toggle_guidance`, which the stable server did not have (issue 106). A feature's mods therefore reach chats only once the feature is on main; a project's dev-lane choice is carried by its `.mcp.json` and the stable server's routing of its calls.
