# Exploratory testing of release 1.2 — final report (2026-11-19)

Build tested: branch `release-1-2-fixes`, from commit 302efe378. Fixes are on the same branch, up to 301b6094c. Nothing here is live in a chat until the dev lane is repinned, and nothing is merged to main.

## What was done

- **Themes.** Eight kinds of behaviour that keep producing defects and that the test tiers reach only through fakes: [coverage-themes.md](coverage-themes.md).
- **Two rounds, six tester robots**, each on its own charter, sandbox and throwaway cdd home: [charters.md](charters.md). Round 1 explored; in round 2 a robot that had not reported a defect reproduced it from the report alone, and the others took the areas round 1 had not reached.
- **88 files in the defect area** ([defects/](defects/)): 66 defects and 22 questions for the person.
- **Seven closing robots** wrote, for each confirmed defect, a scenario, a test seen failing first at the tier that owns the behaviour, and the fix. A last robot brought the story map, module cards and class model up to date.

## Defects by epic, sub-epic and story

| Epic | Sub-epic | Story | Defects | Fixed |
|---|---|---|---|---|
| Move Work Forward On Session Board | Steer Ticket Sessions | Open Ticket Session | gizmo-04, 05, 06 | all |
| | | Activate Ticket | gizmo-01, 03, 07, 08 | all |
| | | Close Active Session | gizmo-14, 15, 17 | all, one case left (see decisions) |
| | Maintain Tickets | Add Backlog Item | gizmo-13 | yes |
| | | Archive Ticket, Delete Ticket | gizmo-09, 16 | all |
| | See Work On Session Board | Display Board | pixel-07 | yes |
| | Guide Work Through Practices On Board | Choose Session And Practice Roots | widget-12 | in part |
| Register And Install Toolsets | Install Markdown Files | Store Install State | bolt-01, 03, 06, 13 | all |
| | | Choose Where To Install (new) | bolt-02, 04, 11 | all (bolt-11: the empty name) |
| | | Refresh The Installer's Own Commands (new) | bolt-14 | yes |
| | | Install The Latest Release (new) | bolt-16 | yes |
| | | Publish Mods For Every Chat (new) | bolt-12 | yes |
| Move Work Forward From Chat Bar | Check CDD Server Health In Chat Bar | Create Git Repository First | bolt-05 | yes |
| Deliver Work With Context Guidance | Produce Formal Artifacts | Generate Fidelity Artifact | widget-01, 02 | all |
| | | Render Artifact Into Another Format | widget-06, 07, 09 | all |
| | | Take Artifact To Another Format And Back (new) | widget-04, 05, 08, 19, 20 | 04, 05 yes; 08, 20 in part; 19 no |
| | Check Artifacts Against Rules | Validate Artifact Against Rules | widget-03, 10 | all |
| | Turn Source Material Into Context | Describe Existing Artifacts | widget-11 | yes |
| Map Work Into Knowledge Graph | Build Practice Trees From Source | Read Modules Classes And Operations; Read Story Maps And Story Tests | widget-18, 21 | all |
| Queue Prompts For Later | Build Prompt Queue | Queue Draft Prompt; Edit Queued Prompt | sparky-01, 02, 07 | all |
| | | Refuse Queue File That Holds No Queue (new) | sparky-03, 04 | all |
| | | Name Queue By Chat Id (new) | sparky-09 | the path part; an unknown id is a decision |
| | Nest Prompt Steps In Queue | Set Steps Of Queued Prompt; Add Interruption To Working Prompt | sparky-07, 08 | all |
| | Share Queue Among Robots | Group Queue Into Robots | sparky-05 | yes |
| Review Generated Work In File Viewer | Review Files In Files App | List Files The Link Names; View File In Source View | pixel-01, 02, 03, 04 | all |
| | Switch Files App Between Files And Graph | Open Several Files From Graph Nodes | pixel-08 | yes |
| no story on the map | the test runner and its cadence | | rivet-01 to 10 | all |

Of the 66 defects, 59 are fixed, 4 are fixed in part (widget-08, widget-12, widget-20, sparky-09), and 3 are not fixed: widget-19, and pixel-09 and pixel-10, two browser tests the e2e tier showed failing from before this session (see Test results).

## Defects by module and class

| Module | Class or operation at fault | Defects |
|---|---|---|
| `space/kanban` | `Ticket.close` order of steps; `TicketCheckout.save_work` | gizmo-14, 17 |
| | `Ticket.create` / `CardPlacement.open_ticket`, `BacklogItem.create` (a name made from a title, unchecked) | gizmo-04, 05, 06, 13 |
| | `Ticket.delete`, `Ticket.archive` | gizmo-09, 16 |
| | `Board.show` | pixel-07 |
| `space/repo` | `Worktrees.of / open / add / remove / sibling_folder` | gizmo-01, 03, 07, 08, 15 |
| | `NewRepository.write_ignores` | bolt-05 |
| | `Branch.changed_files` (git's quoted names) | pixel-02 |
| `space/session` | `SessionFiles._tracked_under`, `FileManager.read`, `NodeSpans.collect` | pixel-01, 02, 08 |
| | `PracticeSessionOutput.choose_root`, `FidelitySessionOutput.choose_root` | widget-12 |
| `harness/installation` | `Installer.create`, `InstallRecord`, `IdeLayout`, `InstallTarget`, `Deployment` | bolt-01, 02, 03, 04, 06, 13, 14 |
| | `JsonFile.read` (an unreadable file read as empty) | sparky-01, 03 |
| | `cdd-connection.ts` template | pixel-04 |
| `harness/mcp` | `CddHome._copy_mod` | bolt-12 |
| `scripts` | `install.py` (`_chat_folder_refusal`, `_match_release_version`), `test.ps1` (`Start-SpecBatch`) | bolt-11, 16; rivet-08 |
| `harness/diagnostics` | `TestRun.is_live`, `TestCadence`, `TestRunner.run`, `TestRunRecord` | rivet-01 to 07, 09, 10 |
| `harness/files_app` | the Files page's editor; the Files server | pixel-03, 04 |
| `harness/guidance_actions`, `harness/guidance` | matching a guidance argument to a practice or fidelity | widget-01, 02 |
| `cdd_guidance/actions` | `Render._render_files`, `RenderedFile.save`, `Validate.validate`, `Document` | widget-03, 04, 06, 07, 09, 10, 11 |
| `cdd_guidance/practices` | Stories, Clean Engineering and DDD format adapters; each practice's graph reading | widget-04, 05, 08, 18, 19, 20, 21 |
| `tools/prompt_queue` | `PromptQueue._held / _keep / load / edit / set_steps`; the mod's `robotPromptsOf` | sparky-01 to 05, 07, 08, 09 |

## Themes the defects confirm

1. **Two callers on one shared resource** — the largest group: the prompt queue lost changes (with one cdd server, 86 of 90 adds kept; with both lanes' servers on one chat, 43 of 90), two installs failed each other, three chats activating one ticket, and the record of test runs read as empty during a write. No tier ran two real processes on one file before today.
2. **A name or path taken as given** — a ticket name made from a title, a chat id used as a folder, an install path, an output root, a render path outside the session's root, a misspelled slug run as prose.
3. **An unreadable file read as empty and written over** — the prompt queue file and the record of test runs; the board did the opposite and dropped every ticket for one bad file.
4. **State that outlives what it describes** — worktree folders after a branch or a close, a run's process id reused by another program, graph nodes and listed files of files that are gone, a run blamed on a commit it did not test.
5. **A trip between formats writes over what a person wrote** — story map, class model, bounded-context map, domain model, scenarios.
6. **A call that answers success while doing less than asked** — `validate` with `graph: true`, `document`'s paths, a spec batch that ran nothing counted as passed.

## Coverage added

| Tier | New spec files | What they run for the first time |
|---|---|---|
| Unit | `worktree_spec.py`, `new_repository_spec.py`, `install_lock_spec.py`, `install_target_spec.py`, `ide_layout_spec.py`, `document_spec.py`, `practice_session_output_spec.py`, Stories `graph_reading_spec.py`, and examples added to about 25 existing specs | the refusals by name: card names, install arguments, guidance names, roots, queue files, step states |
| Heavy | `install_record_heavy_spec.py`, `scripts/install_heavy_spec.py`, `cdd_home_heavy_spec.py`, `prompt_queue_processes_heavy_spec.py`, `test_runs_heavy_spec.py`, `test_ps1_heavy_spec.py`, `starter_bound_job_heavy_spec.py`, `named_arguments_heavy_spec.py`, and examples added to the worktree, ticket, repo, render and session-files heavy specs | two real processes on one file (queue, install, mods, record of runs); real git refusing a merge, a held worktree folder, a branch without its folder; a tier in a detached worktree; a trip through drawio and back on a real file |
| Browser | examples added to `open-files-in-files-app.story.ui_e2e_spec.py` and `see-work-on-session-board.story.ui.spec.ts` | a file gone, renamed or too long under the Files page; a missing project folder; the board with one unreadable session file |
| Story tests | 9 new scenario files and about 70 new scenarios; seven stories added to the map and 56 linked to their scenario files | the epics Deliver Work With Context Guidance and Register And Install Toolsets had almost no scenario files before |

A new Stories rule, `scenarios-name-a-story-on-the-map`, reports a scenario file whose story the map lacks.

## Test results

- **Each robot's own specs**: every final run passed; the counts are in each robot's confirmation and in the commits.
- **Unit tier** (`scripts/test.ps1 -Suite unit`): four runs on the finished code, 365 or 366 of 367 files passing each time, no example failing on an assertion. Two causes, both fixed after the fourth run:
  - `story_map_edits_spec.py` copies a story test into a throwaway project at its real path, which went past Windows' 260 character path limit under the tier's temporary folder. The tier's folder and the throwaway project's folder now have short names; the spec passed in the fourth run.
  - `harness/mcp/cdd_home_spec.py` had three examples that serve two checkouts and publish their mods as real files, at 100 to 146 ms against the 100 ms unit budget. They are now in `cdd_home_lanes_heavy_spec.py`.
  - `space/session/session_spec.py` and `session_log_spec.py` each had one example at 102 or 103 ms in one run and inside the budget in the others, while robots were loading the machine.
  The fifth run, after these two fixes, passed 366 of 367: one example of `session_spec.py` at 107 ms. A different example of that spec is at the budget's edge in each run, so the tier has not passed whole in one run, and no example has failed on an assertion in any of the five.
- **Heavy tier as a whole**, through the changed runner in a detached worktree (`python -m harness.diagnostics.test_runs heavy`, throwaway cdd home): the first run passed 58 of 62 files. One failure was a stale list of repo tools in `mcp_host_heavy_spec.py` (fixed). Two were the worktree itself: it had no installed language adapters, so the Graph app and the Story UI did not start; a tier's worktree now gets a copy of them (8762cff7a). The fourth was a path over Windows' limit in the OSS pattern's rules spec, an effect of the long temporary folder used for that run. **The second run passed 62 of 62 on 8762cff7a.**
- **E2E tier without the agent specs** (`scripts/test.ps1 -Suite e2e -SkipAgents`, on 8762cff7a): 7 of 10 files passed, and 274 of 275 Playwright tests. The three failures:
  - `review-files-in-files-app.story.ui_e2e_spec.py`, one example: the file bar of another project lists its whiteboard beside its drawing. The page does what the story Open Whiteboard In Files App asks; the test and its scenario are older. Not caused by this session (pixel-09), and which of the two is right is a decision for the person.
  - `review-files-in-viewer.story.ui.spec.ts`, one test: a changed line's row holds the removed line and the new one, and the test's locator finds both once the change is drawn. A fault in the test since 2026-11-12, passing or failing by timing (pixel-10). Not fixed.
  - `tools/prompt_queue/prompt_queue_plugin_e2e_spec.py`, all six examples: `'NoneType' object has no attribute 'stdin'` when it starts a headless Claude Code chat. `claude` is not on PATH on this machine; read as a fault of the machine's set-up, not confirmed.
  The new browser examples of this session passed in that run, the board's unreadable-session-file band among them.

## Not tested, and why

- **The Claude desktop app** (theme 7): the chat bar and queue mods in a live chat, robots started by the queue, Auto mode, Remote Control. It needs a person.
- **`--from-latest`, `--restart-everything`, `install-latest.py` run for real**: they stop servers on fixed ports that a sandbox cannot confine.
- **Drag and drop on the board, its roots dialog and health panel**: the tester's automated drags fired no call.
- **The e2e tier in a detached worktree**, and a real heavy tier on the CDD repository through the changed runner. The person's own check of a real tier run, which the main session's handoff asks for, is still owed.
- **The locks on Linux and macOS**: only the Windows branch of the install lock and the queue's file lock has run.
- **Decision records, `handoff_session`, the DDD, BDD and UX fidelities beyond one render each, the story explorer, graph filters.**

## Decisions for the person

The 22 question files in [defects/](defects/) (those with `question` in their name), and these choices the closing robots made where no source said what should happen:

1. A ticket's name is at most 64 characters.
2. Delete and archive of a ticket with a worktree save and push its work and keep its branch, unmerged.
3. A close of a ticket whose worktree is already gone still offers to commit and push main, and would commit the main clone's edits: the one case where a close can still publish uncommitted edits. An existing heavy spec expects the offer.
4. A close from a chat inside its own worktree, on Windows, now raises `WorktreeNotRemovedError`; the work is saved and merged by then.
5. A folder in the way of a worktree is refused, not reused.
6. A guidance word in another spelling of a real slug is refused, not matched; an empty guidance still answers with no rules.
7. `validate` with no paths now builds the graph of every folder under the practice's root.
8. A file over 30,000 lines is refused by the Files viewer.
9. A root may still be a folder outside the project or one that is not there yet; five existing specs rely on it.
10. Where prose is kept when a drawing cannot hold it (descriptions, notes, calls, invariants, an integration's details). Until then a trip through a drawing still loses them, and widget-19 needs the story model to hold an outline's examples.
11. An unknown but well-formed chat id still gets a new queue on `add`.
12. Whether the test runner gets a story on the map.
13. Splitting the stories that now hold more than seven scenarios (Activate Ticket, Close Active Session, Open Ticket Session, Display Board, Add Backlog Item), and moving the two new queue stories to a sub-epic of their own.
14. One shared class in `harness/process` for the four places that claim a file between processes (`InstallLock`, `JsonFile.held`, the hook daemon's `_SpawnLock`, the test runner's claim file).

## Known loose ends

- Every `validate` and `render` today ran on the pinned dev-lane runtime, which is the code from before these fixes. `validate` for `stories-scenarios` and `stories-acceptance-tests` often did not answer within its wait; where it did, it reported "Then has no observes relationship to Example" on every Then of every scenario file it was given, old and new.
- The class model's whiteboard was not written; the story map's whiteboard is saved and its board in Claude is not published.
- Delete Ticket and Add Child Ticket have scenarios without a story test file.
- `TestRunRecord.save` has no lock across processes; `JsonFile.held` could give it one.
- `partition_documents_flow_spec.py` fails 10 of 16 with `No module named 'faiss'`; not looked into.
- The supervisor's own queue showed every step of its goal as done when a turn ended mid-work, and some `[defect]` cards may be missing from it, since robots queued them at the same moment (sparky-02). The files in the defect area are the full record.
- Sandboxes are left in `C:\dev\_et`.
