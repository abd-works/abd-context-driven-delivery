# Round 5: cross-file validation of the refactored repository

**When:** 2026-11-08, on branch and main at d71e0b20.
**What was checked:** every area, for the twelve concerns that span more than one code file, using two checks:
- **The AI check:** six agents read each file beside the files it imports and the files that import it.
- **The graph check:** the CDD validate graph rules.

**Status:** nothing has been fixed yet; this is the list to fix from. Per-area detail is in the six `round5-*.md` files beside this one. Each finding there gives file:line, its concern, which check found it, whether it is new, left from the review, or a known skip, the fix, and its severity.

## How the checks ran

- **The AI check ran in every area.** The actions agent also expanded every recipe the way the MCP host does, and measured what text actually reaches the agent.
- **The graph check ran fully** for harness upper, space and tools, actions and patterns, Clean Engineering and BDD, and the modules level of harness core.
  - It did not finish for Stories, UX and DDD: the MCP host crashed during that call with `WinError 64` in `harness.mcp.listening_loop`, and it is still down.
- **The graph check found no cross-file problem the AI check missed.** The coupling, deep-module, duplication and module-context scanners returned 0 hits in every area. Every cycle hit came from spec or `_examples` imports (see Scanner defects).
- **Running six graph validates at once overloaded the shared server.** Calls dropped, other sessions' board calls hung for 1–3 minutes, and the host finally crashed (see B10 below).

## Counts

| Area | Findings | High | Medium | Low |
|---|---|---|---|---|
| harness core | 35 | 2 | 21 | 12 |
| harness upper (incl. chat-ui TypeScript) | 28 | 4 | 19 | 5 |
| space and tools (incl. board TypeScript) | 29 | 2 | 18 | 9 |
| actions, patterns, context setup, builders | 25 | 6 | 10 | 9 |
| Clean Engineering, BDD, agent BDD | 29 | 4 | 17 | 8 |
| Stories, UX, DDD | 22 | 2 | 13 | 7 |
| Found by the end-to-end test (B10, B11) | 2 | 1 | 1 | 0 |
| **Total** | **170** | **21** | **99** | **50** |

**Which concerns the findings fall under:** most are wrong-shape relationships (5) or duplicated functionality (1), then duplicated shapes (2) and dependency direction (7). Concern 12, a rule decided in TypeScript that belongs in Python, accounts for about 12 findings across chat-ui and the board.

**Status:** about two thirds are new since the review.

## High findings

**Actions send the agent prompts with text missing.** These are wrong behaviour, and no spec catches them. All are new.
1. **Sketch and Grill lose their text.** They expand a nested `begin` with no arguments, so `listed()` is empty. Sketch's prompt carries no rules and no sketch template, and the begin log line is never written (`sketch.py:115`, `grill_context.py:111`).
2. **Grill drops Generate's text.** It runs Generate as ordinary Python, so its prompt has none of Generate's instructions, rules or template (`grill_context.py:116-124`).
3. **Iterate's prompt is nearly empty: 461 characters,** just its docstring and return line. Expanding it with no session raises (`iterate.py:34-38`).
4. **Satisfy's "apply the fixes" step expands to nothing** (`generate.py:101-109`, `satisfy.py:33`).
5. **Context setup pastes Partition in with no arguments,** and never lists `partition` as a tool even though its steps tell the agent to call it (`context_setup.py:287`).
6. **No spec catches 1–5.** The sketch spec calls `begin` in Python before expanding, which hides finding 1.

**Behaviour regressions found by the end-to-end test.**
7. **B11: the graph goes empty after a ticket is activated.** Each session now has its own in-memory graph that reads nothing until loaded, and activating a ticket switches the open session. The graph app should reload on a switch, or a session's graph should load its working copy when first opened. (Medium, counted above.)
8. **B10: one graph-heavy validate stalls the whole shared server.** Every other call hangs for 1–3 minutes, and enough of them at once crash the host. Graph builds need to run off the request path, or be limited.

**Two object models for one thing.**
9. **DDD still keeps a second object model at the class level.** Each render copies its cards into Clean Engineering classes and back, and its draw.io class view copies twice per render. `ValueObject.clone` returns an empty class, so a module holding a value object loses that object's members when the module is cloned (new; no production path reaches it yet). Known skip, plus one new bug.
10. **An operation exists three times.** It is the object, a fact on its code node, and an entry in the `model_members` dict that BDD follows (`operation.py:323`, `property.py:185`, `graph_bdd_model.py:105`). Left from the review.
11. **Each fidelity builds its own Clean Engineering companion** outside the session's practices, so it keeps no format or outputs there (`guidance.py:1054`). Known skip.
12. **`graph or Graph()` gives every model object made without a graph a private graph** holding five new practices (`model_node.py:160`). Left from the review.
13. **Three lists of import folders that already disagree,** so the installer and the toolset loader find different modules (`cdd_home.py:27`, `repository_toolsets.py:51`, `agent_tools.py:257`). New.

**Dependency direction.**
14. **harness reaches the practices, actions and patterns through `importlib` strings and hard-coded paths.** So the card's claim that harness imports none of them is false, and the cycle scanner cannot see these imports (`practice_catalogue.py:33`, `action_catalogue.py`, `pattern_overlays.py`, `schema_rules.py`, `schema_edges.py`). New.
15. **Model nodes import their practice** (`practice_kind()`) while each practice imports its model, in Clean Engineering, BDD, Stories and DDD. Confirmed by both checks.
16. **Import cycles between files, hidden by imports inside functions:**
    - seven in space (repo↔worktree, session↔sessions, board↔ticket and others)
    - `operation`/`property`↔`base_class_model` in Clean Engineering
    - two inside `harness/hooks`
17. **space and cdd_guidance import each other** (`session_probe.py`, `kanban/report.py`, `agent_bdd_common.py:543`).

**Other high findings.**
18. **The hook server ignores which hooks a VS Code or Kilo install left out.** It always reads `.cursor/hook-handlers.json`, then falls back to every toolset, including hooks marked not to deploy (`hook_server.py:446`, `hook_daemon.py:162`). New.
19. **The draw.io layout graph rules never fire in a real validate run.** The graph never reads `.drawio` files, so only their spec reaches them (`drawio/rules/__init__.py:33-40`). New.
20. **The chat bar adds `format=` and `session=` in TypeScript,** so every button press resets the format a fidelity kept (`fidelity-progress-client.ts:121`). Known skip P-2/P-3.

## Medium themes

**One job written several times:**
- brace matching six times, with BDD's matcher word for word the same as Stories'
- "this checkout" worked out in nine places
- `module:Class` spelled by hand in seven places
- three ways of turning Python types into text
- two key-value readers, two property builders, and two `_sketch_metadata` writers
- five lists of file suffixes that disagree; `CODE_SUFFIXES` leaves out `.java`, so the graph never reads Java code
- four places that search for the story map file
- `python_type` defined twice in `python_class_model.py`: two merges each kept a copy

**Wrong-shape relationships:**
- **Graph:** 16 `Graph` operations take a practice the graph already holds.
- **Per-session state:** the `PracticeSchema` cache can serve another session's practice. A second `Session` object gives each practice two outputs.
- **Board and session:** the board and the session hold separate practice instances, so tickets look fidelities up by name. Two `WorkState` objects write one `session.json`. ReportFile parses its graph twice per read.
- **Rebuilt per call:** a new `Markdown` on every `@markdown` read, and `InstallChannels.toolsets` and `ContextConfig` built per event.

**Rules decided in TypeScript that belong in Python:**
- format groups and default picks
- tile standing
- `canMoveNext`
- the leave and open choices
- matching a chat to its ticket by folder
- matching a backlog item to a ticket by title
- a next-fidelity rule that differs slightly from `Ticket.next_fidelity`
- the board server running `git pull` and the pin itself
- the chat bar reading `~/.cdd/server.json`, which `CddHome` owns
- the graph explorer filtering the tree again after Python's `Filter`

**Other medium findings:**
- **Leaking seams:** `GuidanceAction.session_context` reads `session.json` from disk, though space/session owns that file.
- **Deep module:** other modules use 62% of `harness/guidance`'s production classes, against the 40% limit. The scanner measured 33%.
- **Satisfy side effect:** expanding Satisfy's prompt runs a real validate, writing a report and a "validate" log line, so the board shows the work as checked when it wasn't.

## Scanner defects (graph check)

- **Cycle scanner (`one-way-deps`):** it reports spec and `_examples` imports as module cycles, which is every cycle hit in every area (`practice_wide_rules.py:29-31`, `clean_engineering/model/graph_reading.py:52`). It measures folders only, so it misses the real cycles between files and the importlib-string imports.
- **Folders scanned as production:** `skipped_folders.py:11-34` skips neither `_examples` nor `fixtures`.
- **Code rules judging specs:** `never-swallow-exceptions`, `use-exceptions-properly` and `errors-out-of-existence` never call `is_test_code`, so they flag spec files.
- **`deep-module` undercounts:** it counts fixture classes and sees importers only inside the validated paths (`practice_wide_rules.py:90`, `:117`).
- **`eliminate-duplication` matches identical bodies only,** so it misses near copies (`operation_checks.py:298-310`).
- **False hits from three rules:**
  - `use-explicit-dependencies` flags building a `Path` or another value object (`operation_checks.py:97-104`).
  - `prefer-instance-operations` flags factories (`load_*`, `for_project`, `whole_file`).
  - `use-intention-revealing-names` flags `value` in Python property setters (`operation_checks.py:84-86`).
- **Module naming counts `*_spec.py` classes as public** (`module_naming_rules.py:52`, `:63-64`).
- **`public-seam-only` matches its own string literal** (`base_class_model.py:41-48`).
- **The repaired `_examples` fail rules they should pass.**
- **The TypeScript reader reads `cdd-connection.ts` twice** and reports a class that does not exist.

## Still to do to complete this round

- **Restart the CDD MCP host,** then run the Stories/UX/DDD graph call (one call) and, optionally, harness core's code-level call.
- **Expect little from it:** the graph check has added nothing new in the other areas.
- **2026-11-08: tried again on a freshly restarted server, and it fails the same way every time.**
  - The validate of `stories`, `ux` and `ddd` with `graph: true` stopped the server answering within seconds. The process spent over 1,000 CPU seconds without finishing, and it had to be killed and restarted.
  - So B10 reproduces on demand with this one call. It is the test for the B10 fix.
  - The check runs after that fix is merged and the runtime is repinned.
