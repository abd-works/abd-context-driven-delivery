# Judge And Fix Work From Chat Bar And Board

**Outcome:** generate refreshes the knowledge graph and judges the rules itself, Fix is an action of its own on a rule, a file or every violation, Validate runs on its own only as a slash command, and the chat bar opens the active ticket's card and tiles in a side panel.

**Slicing notes:** what was unique to Fully Integrated App Flow, split on 2026-11-23 at the person's request. The Story UI editor's screen frames and increment tickets went to Author Story Maps, the story explorer's stories to Integrate Stories With The Canvas Explorer, Remove Older Versions When Keeping A Release to Sync Design Canvas With Production, and Test Knowledge Graph Explorer On Session Files and Display Drawio File As Diagram to File Manager Complete. The board and chat bar violation and fix stories were dropped as duplicates of File Manager Complete's Count Fidelity Violations From Live Graph, Count Session Violations From Live Graph, Fix Graph Violations From Files App and Fix Graph Violations From Chat Bar.

## Notes from the backlog

From `board-enhancements.md`:

> better graph integration - eg load up fron on sesison open show all violations as a result of graph no need fo exlici run

From `mod-ideas.md`, "Validate on save":

> When an artifact in a session changes, run the graph rules and update the band.

Built today: Attach Violations To Latest Graph (a graph refresh records each violation on its node).

## Epic: Connect Sessions Across Channels And Apps

### Feature: Check Work In Generate

#### Story: Refresh Graph After Generate

*Generate*. Requested (2026-11-06, "generate --> load refreshed graph based on changes immediately"): when generate writes a fidelity's files, the knowledge graph rebuilds those files at once, without a separate load or Validate run. Built today (checked 2026-11-10): generate tells the agent to call validate afterwards, and validate refreshes the graph (`generate.py:32-33`, `graph.py:1397`). Missing: generate refreshing the graph itself.

#### Story: Judge Rules During Generate

*Generate*. Requested (2026-11-06, "judge validation must be part of generate, merge the two actions"): generate ends with the agent's rule-by-rule judgment of what it wrote, saved with the graph's hits, so a generate counts as generated and validated. Built today (checked 2026-11-10): generate ends by calling validate, which runs the AI judgment and saves it with the graph hits (`generate.py:32-36`, `validate.py:80`). Missing: one action; validate is still a separate call, log line, and board and chat bar action.

#### Story: Fix Graph Violations

*Agent*. Requested (2026-11-06, "/fix is a first class action; fix rule; file; default across all rules / files"): Fix is an action of its own: on one rule, on one file, or by default on every violation of every rule in every file, reading the violations from the latest graph.

#### Story: Validate Fidelity On Demand

*Agent*. Requested (2026-11-06, "validate still exists as independent action"; "validate is a slash command story only now"): Validate runs on its own on any files only as the `/actions-validate` slash command, and its report is saved as today; the board and the chat bar have no Validate, since generate judges the rules. Built today (checked 2026-11-10): `/actions-validate` runs and saves its report. Missing: validate is still on the board tiles (`action-bar-view.tsx:64-70`) and in the chat bar's stage actions.

### Feature: Connect Chat Bar Board And Story UI

#### Story: Open Board Side Panel From Chat Bar

*Person*. Requested (2026-11-06, "chat band -> board side panel"): the chat bar opens the active ticket's board card and tiles in a side panel beside the chat.

Analysis and planning: the stories here are not built yet, or only partly built where a story says so. This is one increment of the thin slice, which sets the order of the increments, [harness/.context/stories/thin-slice.md](../../harness/.context/stories/thin-slice.md); its epics, features and stories are on the story map, [harness/.context/stories/story-map.md](../../harness/.context/stories/story-map.md). Each requirement sits under the story it belongs to.
