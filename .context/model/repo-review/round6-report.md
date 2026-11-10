# Round 6: re-validation after the round-5 fixes

**When:** 2026-11-08, on branch and main at b91a73eb. The CDD MCP server ran 8a91c49f, which has the same code.

**What was checked:** the same twelve cross-file concerns as round 5, area by area. Six AI validators read each file beside the files it imports and the files that import them. The actions validator also built every action's prompt the way the server does. Each round-5 finding was checked against the code and marked fixed, left, regression, new or new scope.

Per-area detail is in the six `round6-*.md` files beside this one. Counts come from `concern_counts.py` (rerun with `python concern_counts.py "round6-*.md"`).

## Counts

| Area | Round 5 | Round 6 | High (round 6) |
|---|---|---|---|
| harness core | 35 | 27 | 0 |
| harness upper | 28 | 26 | 6 |
| space and tools | 29 | 19 | 1 |
| actions, patterns, context setup | 24 | 26 | 4 |
| Clean Engineering, BDD | 29 | 20 | 1 |
| Stories, UX, DDD | 21 | 15 | 0 |
| **Total** | **166** | **133** | **12** |

The harness-core and harness-upper areas were split differently in round 6: hooks and mcp moved to harness upper, and guidance and guidance_actions to harness core. Only the overall total compares between rounds, not those two rows.

**Round-5 findings fixed: about 120 of 166.** Most of the rest are left. Two are regressions.

## The loop's goal classes

| Goal class | Concerns | Round 5 | Round 6 | Change | Left | New | Regression |
|---|---|---|---|---|---|---|---|
| Bad resource orientation | 5, 9 | 63 | 56 | −11% | 30 | 25 | 1 |
| Shadow models | 2 | 30 | 18 | −40% | 16 | 2 | 0 |
| Duplicated functions | 1, 12 | 57 | 36 | −37% | 15 | 20 (+1 new scope) | 0 |
| **Total** | | **150** | **110** | **−27%** | 61 | 47 | 1 |

## High findings

**Bugs the round-5 fixes introduced:**
1. **The board shows generate as done before anything is generated.** Building the Sketch, Grill or Iterate prompt writes a `generate` line to the session log, and `FidelityProgress.from_log` counts it (actions N2).
2. **`partition` and `repair` fail when an optional argument is left out.** A recipe line names an optional parameter, and its placeholder is filled with no default (`agent_tools.py:1057`, `recipe.py:115`) (actions N1).
3. **actions and practices import each other.** `cdd_guidance/actions/__init__.py:14` imports the practices, and seven practice files import `actions/sketch` (actions N3).

**Problems already there before round 5:**
4. **B10 still happens.** A graph build stops the server answering anyone, for up to 9 minutes this round. All six validators lost the server, and only some graph checks finished. The likely cause is progress reported per node and per rule through the event loop, while the Session Board holds about 257 open connections waiting (upper H2).
5. **A hook daemon started by the old code keeps hooks dead after an update.** The new daemon cannot claim the port and never finds the old one. Closing a worktree never stops its daemon: 71 old-layout daemons are running (upper H1).
6. **Session tools called with `session=` lose the calling chat.** The `@tool_subject` loaders build a stand-in `ToolCall` (`session.py:98`, `practice_session_output.py:56`) (space H1).
7. **The context index reads paths against the server's folder,** and embeds a missing segment as empty text (actions N4).
8. **A getter's property node takes its type from its own name,** so `hasType`/`dependsOn` edges are wrong and the coupling rules undercount (`clean_engineering/model/graph_reading.py:212`) (CE N1).
9. **Two runtime file cycles remain:** `saved_graph` ↔ `graph` and `catalog_generator` ↔ `project_approach` (upper H3).
10. **harness imports `scripts`** (`server_health.py:12`) (upper H4).
11. **A detached model object still makes a private `Graph()`,** now lazily (`model_node.py:199`) (upper H5).
12. **`SavedGraph.restored_graph` builds a new Graph with new practices,** and the board does this on every report read (upper H6).

## Scanner defects still open
- **`one-way-deps` counts imports under `if TYPE_CHECKING:`** (`python_class_model.py:184`). This explains most of its false cycles.
- **`production_code.py` misses `*.feature.py`, `test-utils/` and test-support modules,** and `skipped_folders.py` misses `catalog-examples/` and `templates/`.
- **Several rules still judge spec files.** They derive from `PracticeGraphRule`, not `ProductionCodeRule` (`class_rules.py:36`, `operation_checks.py:112/200/284`, `operation_semantics.py:33`).

## Why the loop is not cycling, and what changes for the round-6 fixes

**The good news:**
- Shadow models and duplicated functions fell by about 40% each.
- No area got worse overall.
- Only one finding is a regression.

**What needs attention:** bad resource orientation fell only 11%. The validators named three patterns behind that:
1. **A fix replaced one stand-in with another.** A `Sessions(project)` lookup became a stand-in `ToolCall`, so the chat is still lost. A fix for concern 5 must come with a spec on the effect it protects, such as the chat named in the log line.
2. **A fix removed the named copy but left its twin.** `_behavior_node` stays beside `add_child`, the `parameters` fact stays beside the `Parameter` nodes, the type translator stays beside its copy, and the story-map search stays in `StoryMapLinks`. Every fix brief now requires a grep for the job, not the function name, and a list of every other place doing it.
3. **Skipped items stay open.** These are 7 of harness core's 16 goal findings, plus DDD's state carried as text. Each one now gets either a named task with a failing spec, or a decision record that takes it out of the count.

**New checks before each fix agent commits:**
- Call each changed recipe with only the required arguments, and check what it wrote to the session log.
- Run `python -X importtime` on any changed package `__init__`.
- Grep for `ClassVar`, `lru_cache`, `vars(` and `Graph()` outside specs.
- Type-check the graph app.

**B10 gets a structural fix:** graph builds run outside the server's request loop, and progress is reported in batches.
