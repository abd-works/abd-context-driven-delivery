# Round 6: actions, patterns, builders, agents, context setup, judged across files

Area: `cdd_guidance/actions`, `cdd_guidance/patterns`, `cdd_guidance/builders`, `cdd_guidance/agents` and `cdd_guidance/context_setup` (not `_examples`). Branch `ensure-domain-orientation-refactor` at b91a73eb, read on 2026-11-08. `cdd_guidance/agents` is new to this area this round, so its findings are **new scope**.

## How each check ran

**Graph rules: failed, not run.** One `validate.validate` call was made: `clean-engineering-modules`, `graph: true`, `paths` set to the five area folders (absolute, forward slashes). The CDD MCP host closed the connection before answering ("MCP server "plugin:cdd:cdd" connection closed before the tool call was answered"). The call had claimed `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\validation-reports\clean-engineering-modules-20261108T081631.md` and left it at 0 bytes; two other agents' calls a minute later (`clean-engineering-code-20261108T081711.md`, `-081743.md`) are also 0 bytes. A `cdd.ping` straight after answered "MCP server "plugin:cdd:cdd" is not connected", Claude Code then reported `ECONNREFUSED`, and nothing listened on `127.0.0.1:8790`. Following `.claude/rules/mcp-fail-loud.md` and the round-6 brief, I stopped there and did not run validate through Python. **The MCP host has to be restarted, and this area's graph check run again, one call at a time.** Three agents' graph builds finished at 08:13-08:15 (100 KB reports), so the host was crashing under load, not refusing this area's paths.

**AI judgment: run, and checked by running the code.** Every `@mcp @agent_instructions` recipe in the area was answered the way the MCP host answers it: `Toolset().instruction(name).answer(ToolCall(arguments, project))`, which is `AgentInstructions.answer` → `_expanded_reply` (`harness/agent_tools/agent_tools.py:1019-1037`), on a throwaway project with an open session. Each was run for `stories-story-map`, `stories-acceptance-tests`, `ddd-model`, `clean-engineering-code`, `ux-mockup` and `bdd-behavior`, with two slugs at once, and in a project with no session. For each reply I measured its length, the tools it lists, its result line, whether the held fidelity's overview, template, Scaffold, sketch template, examples and first rule reach it, what it wrote to `session.log`, and what files it created. Probe scripts: `C:/Users/jeffa/AppData/Local/Temp/claude/C--Users-jeffa--claude-spares-spare-GRHl26/1da33504-c4b4-4a29-9c7f-0741c828af02/scratchpad/r6_ap_expand.py` and `r6_ap_probe2.py` beside it; the replies are dumped there as `r6_dump_*.txt`.

## What reaches the agent (measured, `stories-story-map`)

| Recipe | Reply | Tools listed | Fidelity text that arrives | Side effects of expanding |
|---|---|---|---|---|
| `generate` | 20.4 K | render, validate | overview, template, rules | logs `generate` (by design) |
| `sketch` | 36.8 K | explore_context_files, read_context_file, write_grill_answer, find_template, save_sketch, review_sketch, render, validate | overview, template, Scaffold, sketch template, rules (**twice**), grill interview | logs `generate` (N2) |
| `grill` | 25.1 K | grill tools, render, validate | overview, template, rules, interview | logs `generate` (N2) |
| `iterate` | 25.7 K | grill tools, render, validate, mark_iterate_round | overview, template, rules, interview | logs `iterate`, then `generate` (N2) |
| `satisfy` | 6.8 K | validate | rules, the fixes step | logs `satisfy` only; no report saved |
| `document` | 3.4 K | refresh | template | docstring twice (N5); `{session.path}` left literal |
| `repair` | 12.0 K | refresh, diagnose | template, examples | docstring twice (N5); **raises without `asset`** (N1) |
| `partition` | 4.3 K with `mode` | (refresh) | Scaffold | docstring twice (N5); **raises without `mode`** (N1) |
| `create_rule` | 5.5 K | none | template, examples | docstring twice |
| `capture_from_documents` | 2.1 K | convert, partition, embed | — | docstring twice |
| `capture_from_live_app` | 8.2 K | smoke_test, scout_app, complete_capture, embed | — | its 60-line docstring twice |
| `context_index.ask` | 0.9 K | search | — | docstring twice; `{question}`, `{index_path}` literal |

Every round-5 drop (H1-H5) is gone: Sketch, Grill and Iterate now reach the fidelity's rules, template and the grill interview, Satisfy carries the fixes step, and Context Setup lists `partition` as a tool. The same held for the other five slugs, two slugs at once, and no session.

## Findings, most severe first

| # | file:line | concern | found by | status | fix in one line | severity |
|---|---|---|---|---|---|---|
| N1 | partition.py:114-119 (`mode` in the result line), improvement.py:41-46 (`{{asset}}`), with harness/agent_tools/agent_tools.py:1057 and recipe.py:115-121 | 5, wrong behaviour | AI + measured | new | Placeholders are filled from the call's raw arguments, so a result line naming an optional parameter raises `ValueError: missing argument 'mode'` / `'asset'` whenever the call leaves it out. Every `partition` call without `mode`, and every `repair` without `asset`, fails for all six slugs tried. `capture_from_documents` Step 3 tells the agent to call `partition` with no `mode` (and "with no guidance", which is a required parameter). Fill placeholders with the parameter schema's defaults, and add the minimum MCP arguments to `fidelity_text_spec` | **high** |
| N2 | sketch.py:134, grill_context.py:109, iterate.py:32 (the `_inside(Generate)` recipe runs `self.run(..., action="generate")`, generate.py:28) | 5, wrong behaviour | AI + measured | new | Expanding the sketch, grill or iterate prompt writes a `generate` line naming the fidelity, and `FidelityProgress.from_log` (space/kanban/ticket.py:493) counts any `generate` line as generate done, so the board shows generate done and offers validate before the agent has written anything. Same class as round-5 M1, introduced by the H1-H3 fix. An action started `_inside` another should not log; only the outer action logs | **high** |
| N3 | actions/__init__.py:14 with practices/{stories,ddd,bdd,clean_engineering}/model/sketch/*.py and practices/{stories,ddd}/model/markdown/nodes.py | 7 | AI + measured (`-X importtime`) | new | `cdd_guidance/actions/__init__.py` (added in round-5 fixes) imports `cdd_guidance.practices`, and seven practice files import `cdd_guidance.actions.sketch.sketch_outline` / `discovery_document`. Importing `sketch_outline` loads `cdd_guidance.actions` → `cdd_guidance.practices` → every practice → back into the half-built `cdd_guidance.actions` (1.2 s). Move `SketchOutline` and `DiscoveryDocument` out of the actions package (they are sketch-document readers the practices own), or register actions without importing the practices | **high** |
| N4 | context_setup/context_index.py:167-170 (`embed`), :186 (`search`) | 5, wrong behaviour | AI | new | `ContextIndex` is never made for a call's session, so `Path(out_path)` and each `Path(segment_path)` resolve against the shared MCP host's working folder, not the project; `capture_from_documents` Step 4 passes `folder_path/rag`, relative, so the index lands outside the project. A segment path that is not there is embedded as empty text with no error. Give `ContextIndex` a `for_call` and read paths with `session.path_named`, as `convert` does | **high** |
| N5 | harness/agent_tools/agent_tools.py:1031-1033 `_expanded_reply` | 1 | measured | new | The docstring check compares the dedented docstring with the body's indented copy, so every recipe with a multi-line docstring sends it twice: `partition`, `document`, `repair`, `create_rule`, `capture_from_documents`, `capture_from_live_app` (about 4 K of its 8.2 K is the repeat), `ask`. Compare against the dedented body, or drop the prefix when the recipe walks its own docstring. Owner: harness core | medium |
| N6 | agents/discovery.md:32; actions/sketch/agents/sketcher.md | 3, 11 | AI | new scope | The installed Discoverer defers all sketching to `@sketcher`, but the installer copies only `cdd_guidance/agents/*.md` (harness/installation/installer.py:233-236), so `sketcher.md` is never installed and no such agent exists. Point the Discoverer at the `sketch` skill, as Specification and Implementation do, and delete `sketcher.md` | medium |
| N7 | agents/specification.md:28, agents/implementation.md:26 | 11 | AI | new scope | Both installed agents tell the agent to run `get_fix_violation_instructions`, which nothing defines (removed with the knowledge-graph legacy folder). Name `satisfy` | medium |
| N8 | agents/context.md:21, :25, :29 | 1, 11 | AI | new scope | The Context agent restates `capture_from_documents` and contradicts it: it says partition runs last, after embed, and embeds the converted markdown; the recipe partitions in Step 3 and embeds the `*-segment.md` files partition wrote in Step 4. Point to the recipe instead of restating it | medium |
| N9 | improvement/repair.md:3, :11, :28, :42-44, :52 (reaches the agent through `repair_loop`) | 11 | AI | new | The repair recipe names `finish_turn`, a `Repair` bucket, `Turn` / `WorkSession` / `open_turn` and `Sketcher.sketch_session`; none exists. Rewrite the steps against the session, `diagnose` and `validate` tools that do | medium |
| N10 | validate/checked_graph.py:106; validate/graph_json_reader.py:14-19 | 9, 1 | AI | new | `CheckedGraph` builds the saved-graph path `.context/graph.json` by hand beside `SavedGraphFile.path` (harness/graph/saved_graph.py:227), and `violations_from_graph_json_file` reads a saved graph document (JSON, then `SavedGraph.from_document`) a second way beside `SavedGraphFile.read`. Ask the session's graph for its saved file and read it there | medium |
| N11 | actions/sketch/discovery_document.py:49-58 and sketch_outline.py:73-92 | 1, 9 | AI | new | Two readers of one sketch document with different rules for where the practice sections start: `DiscoveryDocument` stops at the first `## ` line, `SketchOutline` at any heading a practice's lens opens. A sketch whose first `##` is not a practice heading gets a header from one and a section from the other. Give `SketchOutline` the header (title, sources) and build `DiscoveryDocument` from it. (`DiscoveryDocument` was added in round-5 fixes) | medium |
| N12 | partition/partition.py:83-87, :107-108 | 5 | AI | new | The call's `context`, `out_root` and `paths` are handed down `partition` → `on` → `_corpus_steps` → `index` / `segment`, though the Partition is made for that one call. Hold them on the action when the recipe starts | medium |
| N13 | harness/guidance_actions/guidance_actions.py:430-436 (`begin`); tools/prompt_notify/.context/prompt-notify-model.md:9 | 3, 11 | AI | new | Since Sketch and Grill stopped calling `self.begin` (the H1 fix), no recipe calls `begin`, so its `@Toast` never fires and no action toasts "Action →"; the card still says every guidance action starts with it. Put the toast on the action recipes, or delete `begin` and fix the card. Owner: harness upper | medium |
| M4 | validate/checked_graph.py:58-62 | 5 | AI | left | Violations are still filtered by practice key strings (`violation.practice in keys`). Known skip: "Violation.practice stored as a string" | medium |
| M5 | generate/generate.py:54-58 | 2, 5 | AI | left | `Format(...)` is still built from strings at each comparison. Known skip: Format as an object | medium |
| M10 | lern_domain_driven/practices/stories/model/claude_design/fixtures.py:23 | 3 | AI | left | The copy of `story_test_folder` is gone (it reads `LernDomainDriven.story_test_folder`), but nothing calls `LernCanvasFixtures`; only prose (`ux/model/claude_design/story_canvas.md:61`) tells the agent to run it. Publish it as a tool of the LERN pattern or delete it | medium |
| N14 | sketch/sketch.py:56 and :134 | 1 | measured | new | The sketch reply carries the rules block twice: once from `_sketch_text` and again from the nested generate's `rules_to_follow` (`### `vocabulary-traces-to-domain-source`` appears twice). Leave rules out of `_sketch_text` since generate brings them | low |
| N15 | document/document.py:33 | 11 | measured | new | The result line says `{session.path}` in single braces, which nothing fills, so the agent reads it literally. The session block already names the folder; drop it | low |
| L1 | context_setup/context_index.py:196 | 11 | measured | left | `ask` still says `question={question}, index_path={index_path}`, which reaches the agent literally (the two `context_setup.py` cases are fixed) | low |
| L3 | improvement/repair.md:22 | 11 | AI | left | `improvement.py` now lists the `diagnose` tool, but the repair recipe still tells the agent to run `python -m harness manifest cdd_guidance.actions.diagnose.diagnose:Diagnose`, and `harness` has no `manifest` command | low |
| L5 | validate/graph_json_reader.py:14-47 (5 functions), lern_domain_driven/graph_overlay.py:45, :237-259, tier_facts.py:255, cdd_web_domain_access/access_facts.py:79-92 | 8 | AI | left | `_rules_text` and most tier helpers moved onto their owners; these free functions remain. Fold violation reading onto `SavedGraph` / `Violation` (also N10) and the rest onto `TierFile` / `AccessFile` / `LernOverlay` | low |
| L7 | .context/repo-model.md:2737 | 11 | AI | left | The repository model still lists `Partition.partition_corpus` | low |
| N16 | sketch/sketch.py:3-4, sketch/sketch.md:192-196, generate/generate.md:15, sketch/log-action-requests.txt, iterate/log-action-requests.txt | 3, 11 | AI | new | The module docstring and the catalog guide still name `sketch_session`; the generate guide names `finish_turn`; two tracked July runtime logs that no code writes or reads sit in action folders. Update the text and delete the logs | low |
| N17 | agents/context.md:12; agents/dont use yet/*.md | 3, 11 | AI | new scope | The Context agent points at `.cursor/skills/context-setup/`, which is wrong in Claude Code; five agent files under `dont use yet/` are never installed or read. Name the skills by their names; move the parked agents out of the installed folder or delete them | low |
| N18 | generate/generate.py:41 | 7 | AI | new scope | `_render` imports `Render` inside the function though no cycle needs breaking (`render.py` imports only harness). Import it at the top | low |
| L8 | builders/create_agent_toolset, builders/create_practice_guidance, patterns/mern_domain_driven, patterns/cdd_claude_mod | 8 | AI | decided | One-class packages kept because the installer finds one folder per skill; round 5 already accepted this | low |

## Fixed since round 5

- **H1-H3.** Sketch, Grill and Iterate work on their guidance with `_work_on` and walk the nested recipes they name (`instructions(self._generate().generate)`, `instructions(self._grill().grill)`); the fidelity's rules, template, Scaffold, sketch template and the grill interview all reach the reply, with a session and without one.
- **H4.** `generate_fixes_from_validate` has its sentence in the body; Satisfy's reply carries "Apply the fixes the latest validate report names".
- **H5.** Context Setup holds its Partition `as_tool()`; `partition` is listed as a tool and its recipe is no longer pasted in.
- **H6.** `actions/fidelity_text_spec.py` expands each recipe from the call's arguments alone. It does not try the minimum arguments an MCP client sends, which is why N1 got through.
- **M1.** Expanding `satisfy` saves no report and logs no `validate` line (Validate is a tool there).
- **M2.** Sketch and Grill both use `Session.context_folder(module)`.
- **M3.** Context Setup no longer copies GuidanceAction's session handling: `for_call` makes its Partition for the call and the session is read from it.
- **M6.** `save_checked_graph` is gone; `CheckedGraph.save_at` writes the graph it built.
- **M7.** `SketchOutline` reads each lens from `PracticeCatalogue.practice_class(key).sketch_lens`.
- **M8.** The LERN overlay cycle is gone: `test_setup_text` takes the folder, and `tier_facts.py` imports nothing from the pattern.
- **M9.** Render reads files only when `paths` is set and no longer hands the practice back to itself.
- **L2.** Partition fills `partition_guidance.md` with `RecipePlaceholders`.
- **L4.** One `GuidanceAction.rules_to_follow`, used by Generate, Satisfy and Diagnose.
- **L6.** The MERN grill answers and sketch are marked historical.
- **L9.** `actions/render/AGENTS.md` is deleted.

## Counts

- **By concern** (a row counts once per concern; 26 rows): 1: 5 (N5, N8, N10, N11, N14); 2: 1 (M5); 3: 5 (N6, N13, M10, N16, N17); 5: 6 (N1, N2, N4, N12, M4, M5); 7: 2 (N3, N18); 8: 2 (L5, L8); 9: 2 (N10, N11); 11: 11 (N6, N7, N8, N9, N13, N15, N16, N17, L1, L3, L7); 4, 6, 10, 12: 0.
- **By severity:** high 4 (N1-N4), medium 12, low 10 (including L8, decided).
- **By status:** fixed 17; left 7 (M4, M5, M10, L1, L3, L5, L7); new 13; new scope 5 (N6, N7, N8, N17 in `cdd_guidance/agents`, and N18 from checking imports inside functions); regression 0; decided 1 (L8).

## Goal-class counts

| goal class | new | new scope | left | regression | total |
|---|---|---|---|---|---|
| Bad resource orientation (5, 9) | 6 (N1, N2, N4, N12, N10, N11) | 0 | 2 (M4, M5) | 0 | 8 |
| Shadow models (2) | 0 | 0 | 1 (M5) | 0 | 1 |
| Duplicated functions (1, 12) | 4 (N5, N10, N11, N14) | 1 (N8) | 0 | 0 | 5 |
| **Total** | 10 | 1 | 3 | 0 | 14 |

By `concern_counts.py`, round 5 had 20 goal-class counts in this area (concern 5: 13, concern 1: 4, concern 2: 3); round 6 has 14 (concern 5: 6, concern 9: 2, concern 2: 1, concern 1: 5), a 30% cut. Of round 5's 13 concern-5 findings, 11 are fixed; the four new concern-5 findings are three wrong behaviours the round-5 measurements missed (N1, N4) or the round-5 fix introduced (N2), and one parameter hand-down (N12).

## What would make the next round cheaper

1. **Specs that call each recipe the way an MCP client does, with only the required arguments, and that read the session log afterwards.** `fidelity_text_spec` checks what text arrives, but always with every argument filled, and never looks at what expanding wrote. N1 (a missing optional argument raises) and N2 (a nested action logs `generate`) both sit exactly there, and M1 was the same kind of log side effect. A spec per recipe with the minimum arguments, asserting the reply and "no new log line except the action's own", would have caught both.
2. **Check what a new package `__init__` or shared helper drags in.** The fix agents added `cdd_guidance/actions/__init__.py` to register actions, and put `DiscoveryDocument` beside `SketchOutline` in the actions package; practices import both, so the two packages now import each other (N3). Before committing a new import in an `__init__.py` or a new file that another package imports, run `python -X importtime -c "import <that module>"` and look for the importing package in its own chain.

## Scanner false positives

None judged this round: the graph check did not run (see "How each check ran"). Reading the code only, the three round-5 false positives look addressed: `module_naming_rules.py:74` now skips test code through `is_test_code`, and `harness/graph/skipped_folders.py:37` skips `_examples`. The round-5 dismissal of the 32 `one-way-deps` hits relied on "no production file in `cdd_guidance/actions` imports `cdd_guidance/practices`"; that no longer holds (N3), so cycle hits between `actions` and `practices` in the next graph run are likely real.
