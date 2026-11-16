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
- The cdd-board mod is published from the code a server runs (`CddHome.write_board_plugin`). With two lanes, the published mod has to match the lane each chat talks to, or follow the stable lane until a feature changes the mod.
