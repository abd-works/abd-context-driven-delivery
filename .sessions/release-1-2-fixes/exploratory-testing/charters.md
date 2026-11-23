# Charters — release 1.2 exploratory testing

Build under test: branch `release-1-2-fixes` in `C:\dev\abd-cdd-release-1-2-fixes`, read-only for testers. Each robot works in `C:\dev\_et\<robot>\work` with `CDD_HOME=C:\dev\_et\<robot>\cdd_home`. Defect area: `.sessions/release-1-2-fixes/exploratory-testing/defects/`. Themes are numbered as in `coverage-themes.md`.

Out of scope for every charter: the Claude desktop app itself (theme 7 needs a person), the real `~/.cdd`, the real board and its tickets, and any commit or push on the real repository.

## Round 1

| Robot | Charter | Themes | Test data profile | Ports |
|---|---|---|---|---|
| Sparky | Explore the prompt queue (`tools/prompt_queue/prompt_queue.py`, epic Queue Prompts For Later) as several robots and a person changing one chat's queue at the same time, to discover lost cards, cards worked twice, and refusals that do not say what is wrong. | 1, 4, 5 | A chat's queue of 40 cards the robot builds: some done, some given to robots, some with steps, one very long, one starting with `/`. | none |
| Bolt | Explore installing CDD and making a repository (`harness/installation`, `scripts/install.py`, `repo.make_repository`) as a person on their first day, to discover installs that half-finish, repeat badly, or leave files behind. | 2, 3 | `plain-folder` (no git), `no-commits`, `one-commit`, and `folder with spaces (1)`. | none |
| Gizmo | Explore opening, switching, and closing sessions and tickets (`space/session`, `space/kanban`, `space/repo`) as a person who interrupts flows, to discover leftovers that block the next start: worktree folders, branches, lock files, open-session records. | 1, 5 | A repository `repo` with a bare `origin.git`, on which the robot opens three tickets. | none |
| Widget | Explore generate, validate, render and the fidelity output choices (`cdd_guidance/actions`, `harness/guidance_actions`) as an agent that spells names every way, to discover names accepted but ignored, and files lost or changed by a trip through markdown, drawio, whiteboard and Python. | 4, 6 | A session on `repo` with Stories on and UX off, and the Bookshop story map and `src/order.py`. | none |
| Rivet | Explore the test runner and its cadence (`harness/diagnostics/test_runs.py`, `scripts/test.ps1`) as two chats starting tiers on one checkout, to discover results recorded against the wrong commit, one run recorded twice, and runs that wait for ever. Includes Outstanding 1 and 2 of the main session's handoff of 2026-11-18. | 1, 5, 8 | A repository `repo` with three tiny spec files the robot writes, and a throwaway `test-runs.json` under its `CDD_HOME`. Never start a real tier on the build under test. | none |
| Pixel | Explore the Files app and the board's pages in a real browser (`space/session` file manager, `space/kanban` board, epic Review Generated Work In File Viewer) as a person whose files change under the page, to discover pages that show files that are gone, fail to open what is listed, or break in a folder with no git repository. | 2, 5 | A repository `repo`; the robot starts its own servers. | 8901 to 8909 |

## Round 2

Written after round 1's recap, from what it finds: one robot reproduces every round 1 defect from its report alone, and the others take the areas round 1 shows are still at risk.
