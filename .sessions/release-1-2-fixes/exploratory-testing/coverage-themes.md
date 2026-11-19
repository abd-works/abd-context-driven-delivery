# Coverage themes — release 1.2 exploratory testing (2026-11-19)

What the scenarios and the three test tiers cover, set beside the defects fixed since 2026-11-10, to find the kinds of behaviour that keep failing and that no tier runs for real.

## What the tiers hold today

282 unit spec files, 54 heavy, 29 e2e or agent, and 191 TypeScript test files. Story tests by epic (`story_tests/`):

| Epic | Scenario files | Story tests in Python | Browser story tests |
|---|---|---|---|
| Move Work Forward On Session Board | 9 | 68 | 8 |
| Review Generated Work In File Viewer | 6 | 18 | 1 |
| Move Work Forward From Chat Bar | 8 | 10 | 0 |
| Register And Install Toolsets (lanes only) | 0 | 8 | 0 |
| Queue Prompts For Later | 4 | 3 | 0 |
| Deliver Work With Context Guidance (overlays only) | 1 | 1 | 0 |
| Explore Stories In Story UI | 4 | 0 | 0 |
| Author Story Maps | 3 | 0 | 0 |
| Connect Sessions Across Channels And Apps | 2 | 0 | 0 |
| Build Design Canvas Screens | 1 | 0 | 0 |
| Draw Practice Models On Claude Whiteboard | 1 | 0 | 0 |
| Map Work Into Knowledge Graph | 1 | 0 | 0 |

The board is the only epic covered at every tier. In Deliver Work With Context Guidance, 25 of 30 stories (slash commands, partition, sketch, grill, generate, render, validate, satisfy, repair, the chat lifecycle hooks) link to no scenario file at all, and in Register And Install Toolsets only the lanes sub-epic has story tests.

## Themes

Each theme is a kind of behaviour that produced several defects and that the tiers reach only through fakes, or not at all.

1. **Two callers on one shared resource.** Robots piled up on the same cards (683fabe2f), robots' sweep commits pushed each other's work, two tier runs collided on port 8779 (4dc157cfc), a spec-timings file held by another run cut a tier short (8b10729fb), a stale `.git/index.lock` blocked `ticket.activate`, and one long render stalled every chat's calls (c9de800df). Unit specs use one caller and `MockGit`; nothing runs two real callers against one queue file, one git index, or one server.
2. **First run in a folder that is not a prepared repository.** Install into home, temp and spare folders; the Files app in a folder with no git repository (26212981c); a new repository with no first commit; the cdd server's tools in a plain folder. Fixtures start from a repository that already has commits and a session.
3. **Lanes, install and what a running chat actually serves.** A dev lane kept serving an older branch after v1.2 was installed (f36b82c98); mods lost after a server restart (7b7ee0df9); `.mcp.json` pointing at the wrong lane (6c3f3a169, 99332cfdc, e49e56c16); leftover language adapters (b79a90519). The lane story tests run on fakes of the machine; only the installer heavy spec touches real files, and it did not run after yesterday's fixes (its skill list was stale until today).
4. **Names given in a form the code did not expect.** A fidelity given by slug and not by name gave a `KeyError` (06d0845d9); a slug of a practice turned off ran as plain text so validate checked nothing (0d29115c8); `PromptNotQueued` with another chat's id (a2e8edc0d); text starting with `/` refused by the host (chat bar Fix). Unit specs pass the one spelling the author used.
5. **State that outlives the thing it describes.** Graph nodes of files moved away gave 207 hits on files that no longer exist (2f8254e88); a session log re-created a removed worktree's folder (42d8bf7d5, 73aa116b7); the roots dialog kept the old root; a tier run recorded under one commit while the checkout moved to another (main handoff, Outstanding 1); the launcher and the runner recorded as two runs (Outstanding 2).
6. **Turning one format into another.** Markdown to Python stopped working (e0c069873); a call gained a second argument list (d36b8b8cc); a saved whiteboard broke the graph build (6af44bc98); render not saving beside its source or losing the layout. Each adapter has unit specs for its own direction; no test takes one file through markdown, drawio, whiteboard and back.
7. **The Claude app as a boundary.** Auto mode refusing the Browser pane, Remote Control refusing a session start, `prompt.submit` refusing a slash command, the status line gone after a reinstall, and every prompt queue card layout fix. The chat bar and queue mods have plugin tests against a fake of the app and no browser tier, and nobody has tried yesterday's fixes in a live chat.
8. **The test runner itself.** Heavy has not run since the merge of fix-e2e-42d8bf7d5; the full tiers never ran through `scripts/test.ps1` on this branch because Windows blocks `mamba.exe`; tier runs waiting on each other and the cadence are covered by unit specs with a faked process list.

## What the session can and cannot reach

Tester robots run Python, git, the installer, a cdd server and a browser through Playwright, each in its own sandbox. Themes 1 to 6 and 8 are in reach. Theme 7 needs a person in the Claude desktop app: the robots test the mods' plugin code and the server calls behind them, and the report lists the live-app walks still owed.
