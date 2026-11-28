# Charters — release after v1.2.1 exploratory testing

Build under test: `main` at `febcb4595` in `C:\dev\abd-context-driven-delivery`, read-only for testers. Each robot works in `C:\dev\_et\v1-2-2\<robot>\work` with `CDD_HOME=C:\dev\_et\v1-2-2\<robot>\cdd_home`, and starts its own cdd server and apps on its own ports. Defect area: `.sessions/main/exploratory-testing/defects/`, one file per defect, with a `[defect]` card queued as soon as it is found. Themes are numbered as in `coverage-themes.md`; each robot holds one theme.

Out of scope for every charter: the Claude desktop app itself (publishing to Claude Design, opening a board in Claude, the chat bar in a live chat; the final report lists these walks for the person), the real `~/.cdd`, the real board and its tickets, and any commit or push on the real repository. A tester never fixes: it reports and keeps testing.

## Testers

| Robot | Theme | Charter | Test data | Ports |
|---|---|---|---|---|
| Sparky | 1 | Explore rendering the UX story canvas (`render_story_canvas`, `ProjectStoryCanvas`, `StoryScreen`, mounted views; `cdd_guidance/practices/ux/model/claude_design/`) as a person with a real project, to discover canvases that fail or draw wrong screens when stories have no example data, a scenario has no screen, there are more stories than 40 pages, or there is no UX folder. Open each canvas in a browser through Playwright. | A copy of this repository's story map in `work/self`, and a throwaway LERN project in `work/lern`, with one story given no example data and one story map of 45 stories. | 8911–8914 |
| Bolt | 2 | Explore rendering the story canvas again over one already there (`harness/design_canvas/` `versions.json` `keep_one`, ported screens) as a person who keeps re-rendering while editing, to discover canvases that keep removed screens, lose updates, duplicate versions, or break on a hand-edited `versions.json` or a moved screen source. | The LERN project from Sparky's profile, rebuilt in `work/lern`; renders twice, with a screen removed between, and two renders started at once. | none |
| Gizmo | 3 | Explore switching a practice off while work on it is under way (`space/session`, `harness/guidance_actions/`) as a person turning UX, DDD and BDD on and off, to discover generate, validate or render calls through the cdd server that do nothing, check nothing, or write in the wrong place, and board or Files app views that keep showing a practice that is off. | A session on `work/repo` with Stories on, UX off, and the Bookshop story map; UX and DDD files written while on, then switched off. | 8921–8923 |
| Widget | 4 | Explore starting and moving work from two places at once (`space/kanban/` card drops and Start; the chat bar's session list starting a Backlog item) as a person and a chat acting on the same item, to discover items started twice, cards dropped onto a ticket that moved or closed meanwhile, and the Close dialog cancelled after a drop leaving a card half-moved. | A repository `work/repo` with a bare `origin.git`, a Backlog of five items (two nested), and three open tickets in different columns. | 8931–8933 |
| Pixel | 5 | Explore opening a whiteboard from the Files app (`harness/files_app/`, `harness/whiteboard/`) as a person whose whiteboard is not ready, to discover pages that crash, hang, or open the wrong board when its board was never made, was deleted, or belongs to another project. | A repository `work/repo` with three whiteboard files: one with no board, one whose board was deleted, one copied from another project. | 8941–8943 |
| Rivet | 6 | Explore what the chat bar's app icons say (`harness/chat-ui/pane/hooks/health/`, server health) as a person whose apps go down, to discover icons that say running for a server that is stopped, deadlocked, or holding its port, or say failed for one that is running. Test the health calls and wording through the cdd server. | A cdd server and one app started under `CDD_HOME`, then stopped, paused so its port stays open, and restarted on another port. | 8951–8953 |

## Defect-fixing robots

One for each area of the code base; each owns only its files, so no two fixers change the same file. Each reproduces a defect from its report alone, triages it (confirmed, not reproduced, works as intended, with severity), writes a scenario and a test seen failing first at the tier that owns the behaviour, fixes it, and commits that defect's test and fix alone, naming the defect's file, before it takes its next card. Fixers work in their own worktree off `main`.

| Robot | Owns | Takes defects from themes |
|---|---|---|
| Patch | `cdd_guidance/practices/ux/`, `harness/design_canvas/`, `cdd_guidance/patterns/lern_domain_driven/` | 1, 2 |
| Mender | `space/session/`, `harness/guidance_actions/`, `cdd_guidance/actions/` | 3 |
| Splice | `space/kanban/`, `harness/chat-ui/` | 4, 6 |
| Tack | `harness/files_app/`, `harness/whiteboard/` | 5 |

A defect whose failure shows in files no fixer owns goes to the person, who decides who takes it.
