# Charters — release after v1.2.1, exploratory testing (2026-11-28)

Themes are numbered as in `coverage-themes.md`, confirmed by the person on 2026-11-28. Each robot holds one theme.

**Build under test:** `main` at `0e0f0e9e4`, checked out at `C:\dev\abd-context-driven-delivery-worktrees\nostalgic-mclaren-b1ae7c`. Testers read it and run it, and never change it.

**Sandbox:** each robot works in `C:\dev\_et\after-1-2-1\<robot>\work` with `CDD_HOME=C:\dev\_et\after-1-2-1\<robot>\cdd_home`. It starts its own cdd server and apps on its own ports. Folders from earlier rounds under `C:\dev\_et\` are not used.

**Defects:** each defect is one file in `.sessions/main/exploratory-testing/defects/`, named `<robot>-<nn>-<short-name>.md`. When it is found, a `[defect]` card goes on the prompt queue straight away. Each robot ends with `reports/<robot>.md`.

**Out of scope for every charter:**
- The Claude desktop app itself: the chat bar in a live chat, publishing to Claude Design, and board comments in Claude. The final report lists these walks for the person.
- The real `~/.cdd`, the real board and its tickets, and pml-web.
- Any commit or push to the real repository.

A tester never fixes anything: it reports each defect and keeps testing.

## Testers

| Robot | Theme | Charter | Test data | Ports |
|---|---|---|---|---|
| Sparky | 1 | Explore a project that keeps its own patterns (`harness/installation/project_guidelines.py`, `context_config.py`, the installer, the graph, the cdd server's tool list, the hook server's pattern hooks) as two people whose projects share one cdd server, to discover a pattern used, installed or hooked for a project that does not list it, one project's pattern reaching the other, a pattern module that fails to import taking the server down, a config edited while the server runs being ignored or half-read, and an old-style `guidelines` object or a missing list choosing the wrong patterns. | Two projects in `work/alpha` and `work/beta`, each with its own `guidelines_folder`. Alpha lists `stories`, `ddd` and its own `alpha_domain_driven`. Beta has no list and keeps a pattern named `lern_domain_driven` of its own. A third project, `work/broken`, holds a pattern module with a syntax error. | 8911–8913 |
| Bolt | 2 | Explore what the chat bar's reconnect request and app icons depend on (`harness/chat-ui/` board reconnect, `harness/diagnostics/` server health, the cdd server's ping and restart) as a person whose cdd server goes down mid-chat, to discover health answers that say running for a server that is stopped, restarting, or whose port another process holds, a reconnect that never returns or starts a second server, and icon states that disagree with what the server answers. Test through the server calls and the bar's TypeScript the shell can run, not a live chat. | A cdd server under `CDD_HOME`, then stopped, paused with its port held, restarted on another port, and a dummy listener on its port. | 8921–8923 |
| Widget | 3 | Explore starting work from the chat bar's Backlog and the board at once (`space/kanban/` Start and card drops, `backlog-item.start`, `backlog-item.start_under`, parent tickets that move and start with their children) as a person on the board and a chat acting on one item, to discover items started twice, a parent started while one child fails to start leaving the board half-moved, a parent moved while a child is open, and drops in any column landing a card in a column its stage does not allow. | A repository `work/repo` with a bare `origin.git`, a Backlog of six items (one parent with three children, one of them on a branch name that already exists), and three open tickets in different columns. The board opened through Playwright. | 8931–8933 |
| Gizmo | 4 | Explore deleting a session (`space/session/` session folder delete, the set-aside folder, long paths) as a person cleaning up old work, to discover a delete that removes files outside the session's folder, follows a junction or symbolic link, removes a folder that holds a git repository or another session's set-aside folder, or stops halfway and leaves a session that can neither open nor be deleted again. | Sessions in `work/repo/.sessions/` holding: a junction to a folder outside the sandbox (a canary folder that must survive), a nested `.git`, a file held open by another process, a path longer than 260 characters, and another session's set-aside folder. | none |
| Pixel | 5 | Explore the board's answers for a big board (`space/kanban/` `board.overview`, ticket moves, `harness/mcp/` answer size) as a robot reading a hundred tickets, to discover answers that still go past MCP's size limit, answers that leave out what the chat bar or a robot needs with no other call to get it, and calls that slow down past a few seconds. | A board of 120 tickets in `work/repo`, each with an idea of 2,000 characters, 30 with children, spread over every column. | 8941–8943 |
| Rivet | 6 | Explore rendering the story canvas and opening it in the story explorer (`cdd_guidance/practices/ux/model/claude_design/`, `harness/design_canvas/`, the Files app's linked-file pane, class cards on whiteboards) as a person with a real project rather than the bundled fixture, to discover canvases that fail or draw wrong screens when a story has no example data, a scenario has no screen, there are more than 40 pages, or there is no UX folder, and a re-render that loses a person's edits to the canvas. Open each canvas and the explorer in a browser through Playwright. | A copy of this repository's story map in `work/self`, and a throwaway LERN project in `work/lern` with one story without example data, one scenario without a screen, and a story map of 45 stories. | 8951–8954 |
| Cog | 7 | Explore switching a practice off while work on it is under way (`space/session`, `harness/guidance_actions/`, `session.toggle_guidance`, generate, validate and render through the cdd server) as a person turning UX, DDD and BDD off and on with their files open, to discover calls that still write or check a practice that is off, calls that refuse work on a practice that is on, files of a practice that is off disappearing from the board or Files app, and switching back on losing the fidelity the practice was at. | A session on `work/repo` with Stories, UX and DDD on and the Bookshop story map; UX and DDD files written while on, then switched off and on again. | 8961–8963 |

## Defect-fixing robots

There is one robot for each area of the code base. Each owns only its files, so no two fixers change the same file. For each defect, a fixer:
1. reproduces it from its report alone;
2. triages it as confirmed, not reproduced, or works as intended, with a severity;
3. writes a test, seen failing first, at the tier that owns the behaviour;
4. fixes it, and commits that defect's test and fix alone, naming the defect's file, before taking its next card.

Fixers work in their own worktree off `main`. A defect that shows in files no fixer owns goes to the person, who decides who takes it.

| Robot | Owns | Takes defects from themes |
|---|---|---|
| Patch | `harness/installation/`, `harness/hooks/`, `harness/mcp/`, `harness/graph/` | 1, 5 (answer size) |
| Splice | `harness/chat-ui/`, `harness/diagnostics/` | 2 |
| Mender | `space/kanban/` | 3, 5 (board answers) |
| Tack | `space/session/`, `harness/guidance_actions/`, `cdd_guidance/actions/` | 4, 7 |
| Brush | `cdd_guidance/practices/ux/`, `harness/design_canvas/`, `harness/files_app/`, `harness/whiteboard/` | 6 |
