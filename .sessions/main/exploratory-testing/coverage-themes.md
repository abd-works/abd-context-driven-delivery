# Coverage themes — release after v1.2.1 exploratory testing (2026-11-26)

**Status: all six themes confirmed by the person on 2026-11-26, as written, before any robot started.**

## Scope

The release is what main holds after the tag `v1.2.1` (5af176f4a, 2026-11-24): 25 commits, outside `.sessions/`. Exploratory testing covers what they changed and what calls that code, not the whole product. The regression run that follows exploratory testing covers every story's screens.

| Area the release changed | Commits | Tests added with it |
|---|---|---|
| UX story canvas on Claude Design (`cdd_guidance/practices/ux/model/claude_design/`, `harness/design_canvas/`, LERN pattern story runtime) | 315408a53, 394700602, 3ae1c18f5, f9a14895c, cac07a66b, 63e52cb4d, 3de215a2e, f0bfba060, cd3ecd720, 1602daec7, f8309f3df, 27428bb57, 44a5d6f1d, f1103e7d9, 9136b3b46 | 10 unit specs, 6 heavy specs (mounted view, screen walk, canvas rules, project story canvas); no browser test |
| Files app opens a whiteboard in Claude (`harness/files_app/`, `harness/whiteboard/`) | 1dba6d13a, 6da63b712 | files-page and whiteboard-canvas TypeScript specs, whiteboard_spec |
| Board: drop a card above a card in any column; a second press on Start is ignored (`space/kanban/`) | 020e7a512 | ticket-client and root-choice-client TypeScript specs, Maintain Tickets story test |
| Chat bar: session list shows the Backlog and starts an item; app icons show running, not running, failed (`harness/chat-ui/pane/`) | eabeeef76, 020e7a512 | backlog-in-session-list.test.ts, kanban_tools_spec, Steer Sessions story test |
| A practice switched off changes only what the board and chat show (`space/session/`, `harness/guidance_actions/`) | 8955e44af | guidance_actions_spec, session_protocols_spec, Choose Action And Formats story test |
| Stories guidance: main-flow-first replaces scenario-names-continuation; `/version` commit message | 4aa101ca2, c582c6935 | cdd_version_spec; guidance text only otherwise |

## Themes

Each theme names the change behind it, the evidence that it is at risk, and what no tier runs for real today.

1. **The story canvas on a real project, not the fixture project.**
   *Change:* the whole story canvas (`render_story_canvas`, `StoryScreen`, mounted production views, the 40-page limit, the publish gate), built in 15 commits over one day.
   *Evidence:* every heavy spec renders the bundled LERN fixture project. Nothing renders the canvas for a project whose stories have no fixture, a scenario with no screen, more stories than Claude Design's 40 pages, or a project with no UX root. 315408a53 (a mounted view must wait for its fixture and mount afresh on each load) and 9136b3b46 (the explorer must load the scripts its screens load) were both corrections made after the feature first shipped, and both are about the canvas meeting the fixture's data and the browser, which no browser test runs.
   *Reach:* a robot renders the canvas for this repository's own story map and for a throwaway LERN project, then opens the result in a browser through Playwright. Publishing to Claude Design itself needs a person.

2. **Re-rendering the canvas over one already there.**
   *Change:* f9a14895c (`keep_one` in `versions.json` updates one canvas in place), 3ae1c18f5 (copies a ported screen's files, reads prototype positions).
   *Evidence:* `versions_spec` covers the setting on a fresh folder. Nothing renders twice with a screen removed between the renders, two renders at once, a hand-edited `versions.json`, or a copied screen whose source moved. The last release's theme 5, state that outlives the thing it describes, produced five defects.
   *Reach:* in reach, in a sandbox.

3. **Switching a practice off while work on it is under way.**
   *Change:* 8955e44af (switching a practice off changes only what the board and chat show; actions sent to the agent still work on it).
   *Evidence:* the last release fixed the opposite failure (0d29115c8: a slug of a practice turned off ran as plain text, so validate checked nothing). The new behaviour is covered by unit specs on a faked session. Nothing runs generate, validate, or render through the cdd server on a practice that is off, nor switches a practice off with its files open on the board or in the Files app. This session has UX, DDD, and BDD switched off, so this is the normal case here, not an edge case.
   *Reach:* in reach, through the cdd server in a sandbox.

4. **Starting and moving work from two places at once.**
   *Change:* 020e7a512 (a card dropped above a card in another column moves there; above a closed ticket it goes through the Close dialog; a second press on Start is ignored), eabeeef76 (the chat bar's session list starts a Backlog item as the board does).
   *Evidence:* the board and the chat bar can now both start one Backlog item, and the double-press guard is in the board's browser code only. The last release's theme 1 (two callers on one shared resource) produced the most defects. Nothing covers the Close dialog being cancelled after a drop, a drop onto a card that moved or closed meanwhile, or a start from the chat bar while the board starts the same item.
   *Reach:* the board through Playwright in a sandbox; the chat bar's server calls through the cdd server. The chat bar in a live chat needs a person.

5. **Opening a whiteboard that is not ready.**
   *Change:* 1dba6d13a, 6da63b712 (the Files app opens a whiteboard's board in Claude and never draws one).
   *Evidence:* the whiteboard render was the first defect in Increment 9, Defect Fixing (098ab71e2), and a saved whiteboard broke the graph build in the last release (6af44bc98). The specs open a whiteboard whose board exists. Nothing opens one whose board was never made, was deleted, or belongs to another project.
   *Reach:* the Files app through Playwright; the board opening in Claude needs a person.

6. **What the chat bar's app icons say when an app is down.**
   *Change:* 020e7a512 (app icons green running, white not running, red failed; no Graph icon).
   *Evidence:* the icons read the server-health wording, and the session's `install-failures.md` records the cdd server failing for a chat (401 to OAuth) while the bar still drew. This session started with `plugin:cdd:cdd` refused. Nothing checks the icons against a server that is stopped, deadlocked, or held on its port.
   *Reach:* the health calls and wording through the cdd server in a sandbox; the colours in a live chat need a person.

## Left out

- The Stories guidance change (4aa101ca2) and the `/version` commit message (c582c6935): text and one message, each with its spec, and nothing calls them at run time.

## What the session can and cannot reach

Tester robots run Python, git, the installer, a cdd server, and a browser through Playwright, each in its own sandbox with its own `CDD_HOME`. Themes 2 and 3 are fully in reach. Themes 1, 4, 5, and 6 are in reach up to the Claude app: publishing to Claude Design, opening a board in Claude, and the chat bar in a live chat need a person, and the final report lists those walks.
