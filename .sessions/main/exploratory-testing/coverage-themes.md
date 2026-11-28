# Coverage themes — release after v1.2.1, exploratory testing (2026-11-27)

**Status: confirmed by the person on 2026-11-28, all seven as written.**

## Scope

The release is what `main` holds after the tag `v1.2.1` (5af176f4a, 2026-11-24): 60 commits outside `.sessions/`, up to `4c4c82f2e`. Exploratory testing covers what those commits changed and the code that calls it, not the whole product. The regression run that follows covers every story's screens.

Branch `ui-fixes-as-i-use-it` (124 commits not on `main`) had its own hardening round on that branch, and is not in this release.

| Area the release changed | Commits | Tests that came with it |
|---|---|---|
| A project's own patterns, and the guidelines list in `.context/config.json` (`harness/installation/project_guidelines.py`, graph, installer, cdd server, hooks) | d58373b13, 0cd2251fe, 1a6ff6f23 | 4 unit specs and 2 heavy specs on one example project; hook_spec, context_config_spec |
| Chat bar asks the chat to reconnect to cdd; the queue gives each independent card its own robot; app icons for running, not running, failed | 43723eca3, 020e7a512 | board-reconnect.test.ts, register.test.tsx; no mod test runs the bar in a chat |
| Backlog in the chat bar's session list; a parent ticket moves and starts with its children; card drops in any column | eabeeef76, 0a121e232, 8df5c84ec, d61bf328f, 0b41c8ec7, 263b4a154, 020e7a512 | backlog-in-session-list.test.ts, Steer Sessions and Organize Ticket Hierarchy story tests, ticket-client.spec.ts |
| Deleting a session: whatever files stay, paths over 260 characters, a folder an earlier removal set aside | c9bac921a, ea9a407b2 | session_folder_spec |
| Board and ticket answers leave the idea text out, to stay under MCP's size limit | 0a97cec4b, af30e8874 | kanban_tools_spec |
| Story canvas, story explorer, board comments on a canvas, Files app linked-file pane, class cards on whiteboards | 30 commits from 1dba6d13a to f937a969a, with 4acea8442, 92fa602a6, b1322f992 | unit and heavy specs on the bundled LERN fixture project; one Files app e2e spec |
| Switching a practice off changes only what the board and chat show | 8955e44af | guidance_actions_spec, session_protocols_spec, Choose Action And Formats story test |

## Themes

Each theme names the change behind it, the evidence that it is at risk, and what no tier runs for real today.

1. **A project that keeps its own patterns, on a server that answers several projects.**
   *Change:* d58373b13, 0cd2251fe, 1a6ff6f23: patterns read from a project's `guidelines_folder`, used only when the project's `guidelines` list names them, else CDD's list, else all.
   *Evidence:* built in one day and reshaped twice by the person the same day. Every spec uses one example project with a pattern that imports cleanly. Nothing runs two real projects against one running cdd server, a pattern module that fails to import, a config edited while the server runs, an old-style `guidelines` object, or an install into a project after the list changed. The change also stopped CDD's own install publishing `mern_domain_driven` and `oss_portal_domain_driven`.
   *Reach:* in reach: two sandbox projects, the installer, a cdd server and the hook server.

2. **The chat bar when cdd goes down.**
   *Change:* 43723eca3 (the bar asks the chat to reconnect to cdd by itself), 020e7a512 (app icons green, white, red).
   *Evidence:* both are covered only by TypeScript unit tests, because the mod harness does not run from a shell. `install-failures.md` records cdd failing for a chat while the bar still drew. Nothing runs a reconnect against a server that is stopped, restarting, or holding its port, a reconnect asked while the chat is busy, or the icons against those states.
   *Reach:* the health and reconnect calls through a sandbox cdd server; what the bar shows in a live chat needs a person.

3. **Starting work from the chat bar's Backlog and the board at once.**
   *Change:* eabeeef76, 0a121e232, 8df5c84ec, d61bf328f, 0b41c8ec7 (the Backlog in the session list, reshaped five times in two days), 263b4a154 (a parent ticket moves and starts with its children), 020e7a512 (drops in any column).
   *Evidence:* the chat bar and the board can both start one Backlog item, and starting a parent now starts each child, so one start can half-succeed. Two callers on one resource produced the most defects in the last two rounds. Nothing starts an item from both places at once, starts a parent whose child fails to start, or moves a parent while a child is open.
   *Reach:* the board through Playwright and the chat bar's server calls through a sandbox cdd server.

4. **Deleting a session.**
   *Change:* c9bac921a, ea9a407b2.
   *Evidence:* a delete that removes "whatever files stay" can remove more than it should. The round on `ui-fixes-as-i-use-it` found three data-loss defects in folder deletes there (a delete through a junction, a folder holding a root, a delete stopping halfway), and that fix is not on `main`. session_folder_spec runs on plain folders only: no junction, file held open, nested `.git`, or another session's set-aside folder.
   *Reach:* in reach, in a sandbox.

5. **Board answers for a big board.**
   *Change:* 0a97cec4b, af30e8874 (overview and ticket moves leave the idea text out).
   *Evidence:* the change fixed answers that went past MCP's size limit; the spec checks one ticket. Nothing measures the answers for a board of a hundred tickets with long ideas, or checks that the chat bar and robots still get the text they need from another call.
   *Reach:* in reach, through a sandbox cdd server.

6. **The story canvas and explorer on a real project.**
   *Change:* the story canvas and explorer (30 commits), board comments on a canvas answered through the graph (4acea8442), the Files app's linked-file pane (92fa602a6), class cards on whiteboards (b1322f992).
   *Evidence:* every heavy spec renders the bundled LERN fixture project. Several commits are corrections after first shipping (315408a53, 9136b3b46, f937a969a). Nothing renders a project whose stories have no fixture, a scenario with no screen, more than 40 pages, or a re-render over a canvas a person edited.
   *Reach:* rendering and the explorer through Playwright in a sandbox; publishing to Claude Design and board comments in Claude need a person.

7. **Switching a practice off while work on it is under way.**
   *Change:* 8955e44af.
   *Evidence:* the release before fixed the opposite failure (0d29115c8). The new behaviour is covered by unit specs on a faked session; nothing runs generate, validate, or render through the cdd server on a practice that is off, or switches one off with its files open on the board.
   *Reach:* in reach, through a sandbox cdd server.

## Left out

- c582c6935 (the `/version` commit message), 4aa101ca2 and b669300e0 (Stories guidance text), 0c7ff87ab (a demo story map), 0a3178117 and d8ee69b09 (story map records), 12cb0f27a and 4569236f4 (commit messages and a spec): text or records, each with its spec, called by nothing at run time.

## What the session can and cannot reach

Tester robots run Python, git, the installer, a cdd server, and a browser through Playwright, each in its own sandbox with its own `CDD_HOME`. Themes 1, 4, 5 and 7 are fully in reach. Themes 2, 3 and 6 are in reach up to the Claude app: the chat bar in a live chat, publishing to Claude Design, and board comments in Claude need a person, and the final report lists those walks.
