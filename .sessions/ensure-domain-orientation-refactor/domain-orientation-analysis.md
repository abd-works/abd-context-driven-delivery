# Domain orientation analysis

Branch `ensure-domain-orientation-refactor`, read from main at `2b8dafd39` on 2026-11-05. The analysis is read only; nothing was changed.

**Trigger.** In the cdd-main thread, Ticket was found copying Session, practice, and board data into dicts, `*_name` fields, and helper classes (`TicketFiles`, `Workspace`, `PracticeRoot`) instead of returning the objects that own that data. Validate passed `do-not-invent-parallel-object-models` because it read one file at a time. This report checks whether the same thing happened across the whole codebase.

**Answer: yes, everywhere.** Five reviewers covered kanban/session/repo, guidance/actions, installation/MCP, the TypeScript clients, and graph/catalog/the remaining modules. Together they found about 120 findings. Most are instances of a few root causes, listed below. The finding ids (K, G, I, T, R) refer to the per-area appendix.

---

## 1. Root causes, in order of how much they cost

### 1.1 No single practice catalogue → the practice list is written out about 15 times
Every module that needs "the practices" keeps its own list, and each one maps a practice key to its class, folder, colour, or stage.
- **Python:**
  - `space/session/session.py:224 _PRACTICE_TYPES`, plus `Board._every_practice`
  - `validate.py:16 _GRAPH_PRACTICES`, `sketch_outline.py:24` and `guidance_actions.py:399 GuidanceCatalog`
  - `harness/graph/graph.py:44`, `schema_rules.py:16`, `schema_edges.py:15`, `practice_rules_registry.py`, `guidance_prose_index.py`
  - `catalog_generator/project_approach.py:27` and `foundry_chrome.py:221/1722/1864`
  - `scripts/kanban_board_e2e.py:11` and `scripts/exercise_hooks.py:114`
- **TypeScript:** `board-brand.ts PRACTICES` and `fidelity-client.ts PRACTICE_COLOURS`. The two parse the slug differently.

The practice key itself is also worked out in several ways: `PracticeGuidance.key`, `context_index_key`, `Session._practice_key_for_instance`, and `slug.replace("-","_")`.

**Fix.** Create one catalogue (on `Installer` or in harness/guidance) that returns `PracticeGuidance` instances. Every caller reads `key`, `module_dir`, `schema`, `rules`, `fidelities`, the sketch title, and the colour from those instances. (R-G8, A-F3, K-F10, T-X1)

### 1.2 FidelityProgress never travels as an object → each client rebuilds it its own way
`Ticket` spreads `FidelityProgress` across six dicts keyed by slug (`reports`, `violation_counts`, `progress`, `actions`, `allowed_actions`, `next_actions`). `Board.Stage` does the same for `FidelityGuidance` (`work_required`, `formats`, `default_formats`).

Both TypeScript clients put the object back together in their own way, and the copies have drifted apart:
- the chat bar invents a `validated` state that Python does not have
- the board enables Validate/Review when files exist on disk, which Python forbids
- "done" is called "reviewed" in one client and "done" in the other
- the activation defaults differ: one client opens a worktree, the other does not
- the default `ActionStates` literal is copied three times

**Fix.** Make `FidelityProgress` a data shape, send `ticket.fidelities: list[FidelityProgress]`, and delete the six dicts. Then wrap the generated `FidelityProgressData` in TypeScript and delete the TypeScript rules. The cdd-main refactor in `abd-cdd-session-board` has started on the Python half. (K-F1, T-PY1, T-CU1, T-KB1, T-KB2, T-X2/X3/X5)

### 1.3 Domain rules re-implemented in TypeScript
These rules are re-implemented in the chat UI and the board app:
- stage order and stage status
- `is_closed` and "Complete takes Implementation's Done"
- the allowed drop targets
- command strings: `/actions-…` and `session=` are built in four places, and only two of them add `session=`
- the handoff prompt, which is copied
- the file tab order, which is coded twice
- the relation between a ticket and its chat
- board events, inferred by diffing two reads

The chat-bar test stub `cdd-stub.ts` re-implements `move_next`, `next_fidelity`, and `next_action`, so those tests keep passing after the Python changes.

**Fix.** Python owns each rule and exposes the answer as a data field or a single method: `Ticket.commands(action, …)`, `is_closed`, allowed moves, `Board.columns` order, `Ticket.chat`. Run the chat-bar story tests against a real cdd server. (T-CU2…CU8, T-KB3…KB9)

### 1.4 The graph keeps a second model beside the parsed practice objects
The practice parsers already build live `BoundNode`s (`OoadClass`, `Operation`, `Scenario`, `Step`, …). `working_copy.py` copies their fields into flat string records and JSON `data` dicts, chosen by name lists (`_CLASS_FACTS`, …), and turns those back into generic `Node(type, data)`. This is the shape left over from the old CodeQL design. Rules then re-parse every file and reload `StoryModel` to find the real object again by name (`rule_context.py`, `story_model_lookup.py`), and step keyword, phase, and owner class are worked out by splitting `node_id`. `GraphStoryModel` repeats the same pattern for stories. `explorer.py` is an `*Entry`/`*Inventory` family that mirrors `Node`, `Source`, `PracticeGraph`, and `Filter`.

**Fix.** Register the parsed `BoundNode`s straight into `Graph`. Keep the flat format only for saving and loading graph.json. Delete the re-parsing and lookup code. Put `@data_field` on `Node`, `Source`, `PracticeGraph`, and `Filter`, and delete the explorer copies. (R-G1…G7, G11, G13, G14)

### 1.5 The MCP server keeps its own model of an operation
`McpOperationDefinition` copies `AgentTool` (its toolset, name, callable, and description) and builds its own `mcp_name`, which repeats `AgentTool.session_log_name`. Free functions then look the method up again by name, look the `AgentTool` up a second time just to log the call, and repeat the description fallback. The language adapter wraps every tool as `McpTool(McpOperationDefinition)` and recovers the names with `mcp_name.split(".")`. That **crashes on a practice's `instructions` operation**, whose MCP name has no dot. `HookHandler` and the hook-handler records are a third copy of the tool.

**Fix.** `AgentTool` owns `mcp_name`, `invoke_line()`, `invoke()`, `hook_event`, `identity`, and one parameter schema. MCP, TypeScript, and hooks all read from it. (I-F1, F2, F3, F8, F12, F13)

### 1.6 Three competing ways to turn an object into data
Objects become data through `data_of` (destination.py), through `McpHost._json_default`, and through `to_mcp_result` (Session, PracticeSessionOutput, Repo, Commit).
- The routes disagree on Windows paths: `as_posix()` in one, `str()` in another.
- `Commit` defines `to_mcp_result` twice, and the second silently overrides the documented one.
- `data_of` lives in `installation/`, so mcp and kanban import the installer just to serialize.

**Fix.** Keep one function, next to `@data_field` in agent_tools, and delete every `to_mcp_result`. (I-F4, K-F6, K-F12)

### 1.7 The catalog builds a second fidelity model from scraped markdown
- `CatalogFidelityGuidance.scrape` re-reads `{practice}.md` and slices `### {fidelity}` itself, although the live `FidelityGuidance` already holds `guidance`, `overview`, `default_format`, and `stage`.
- The practice guide is re-parsed in about eight more functions in `catalog_generator.py` and `foundry_chrome.py`.
- The mapping from stage to board key is written five times.
- The renderers are mutable bags that callers fill with copied fields.

**Fix.** Render from the live `PracticeGuidance` and `FidelityGuidance`. (R-C1…C9)

### 1.8 Session-folder facts are defined in many places
- **The session log** is parsed in about four places in Ticket and Session. Scripts and seed files also write it directly (`session_board_examples.py`, `kanban_board_e2e.py`, `backfill-session-log.py`, `session_probe.py`), and there is no `Session.log_path`.
- **The `validation-reports` folder and the `{slug}-{date}.md` name** are defined in `validate.py`, in `ticket.py`, and in the TypeScript fixtures. The session-board diff adds a third `_REPORT_FOLDER`.
- **The `handoff-*.md` pattern** is defined in both `handoff.py` and `ticket.py`.
- **The session path** (workpath, repo_path or project checkout) is rebuilt four times in `validate.py`/`guidance_actions.py`. `Generate` uses `Session.current()` instead of `acting_session()`, so it can name a different session.

**Fix.** Session owns `log_path`, `log_entries`, `record`, `reports_folder`, `new_report_path(fidelity)`, `handoffs`, and its root. (K-F2, K-F15, A-F5, A-F6, R-H1, R-S1, R-S3)

### 1.9 Git concepts passed around as strings
- `Repo.worktree_for(branch: str)` does work that belongs on `branch.worktree`.
- `Worktree.branch` is a `str`.
- `Branch.open_in_worktree()` returns a `Repo`.
- `Workspace(has_branch, has_worktree, …)` is built from string lookups.
- `WorkState.branch` and `WorkState.worktree` are strings.
- Board data sits on Session as classmethods that take `repo_path`: `all_in`, `backlog_folder`, `board_file`, `default_wip`, `main_session`, `active_name`.

You already agreed in cdd-main that the board data moves to `board.repo`; that move is not yet in the session-board diff.

**Fix.** `Branch.worktree`, `Branch.exists`, `Worktree.branch: Branch`, `Repo.sessions`, and `Repo.current_session`. (K-F5, F7, F8, F14)

### 1.10 Slugs and names built by hand everywhere
- **The `practice-fidelity` slug** is built by hand in `Stage._slug`, `FidelityProgress.slug_of`, and three `.replace('_','-')` calls, although `FidelityGuidance.slug` exists.
- **Camel/kebab/snake conversion regexes** are copied in agent_tools, files.py, hooks.py, guidance_actions, `Guidance.slug`, working_copy, language_adapter, granola, and about eight practice files.
- **`guidance_prefixes`** splits the slug with `rsplit("-",1)`, which turns `stories-story-map` into `stories-story`.
- **The format vocabulary** (extension to format, aliases, code formats) is written out seven times.
- **`FidelityGuidance`** holds both `name` and `fidelity`, which are always equal, and both `parent` and `practice_guidance`. Readers everywhere do `getattr(x,"fidelity") or getattr(x,"name")`.

**Fix.** Each of these belongs to one owner. (K-F9, A-F10, A-F13, A-F16, I-F5, R-G16)

### 1.11 Classes that only read their collaborators
| Class | Members | Public |
|---|---|---|
| Session | 119 | 70 |
| Repo | 102 | 71 |
| Ticket | 73 | 52 |

Session also holds loop logging, chat pointers, practice roots, output paths, board paths, and graph loading. The chat pointer is a `(id, Path, lines)` tuple that is parsed in four places, and it needs a `ChatPointer` value. Repo holds ProjectTicket state in parallel dicts keyed by issue number. (K-F13, F18, F19)

### 1.12 State passed around as parameters (added 2026-11-06)
Operations take, as parameters, state that an object they can reach already holds: `Ticket.generate_commands(fidelities, formats)` and the model's intended `Generate.commands_for(session, fidelities, formats)` are two examples. Every caller then has to gather the session, fidelity, and format and hand them over, and each caller can hand over a different one.

**Fix.** Keep the state on the object it belongs to, and let each operation read it from there:
- A **Session** holds its practices.
- A **practice** holds its fidelities and its current fidelity.
- A **fidelity** holds its actions and the format chosen for it. A format given once is saved there, so the next action on that fidelity uses it.
- An **action** is made for its session.

A command then reads `session.practices.stories.fidelities.story_map.actions.generate(format="drawio")`. The findings are in appendix area P.

---

## 2. Real bugs found along the way
1. `language_adapter.py`: `mcp_name.split(".")[1]` raises IndexError on a practice's `instructions` operation. (I-F3)
2. `Commit.to_mcp_result` is defined twice, so the version that module-context.md documents is dead. (K-F12)
3. `partition` and the shared `on(item)` read `item.contexts`/`scaffold`, which `PracticeGuidance` does not have, so they raise AttributeError. (A-F18)
4. `guidance_prefixes` gives `stories-story` for `stories-story-map`. (A-F16)
5. The board enables Validate/Review when files exist, which contradicts `Ticket._allowed_actions`. (T-KB2)
6. Paths serialize with `/` or `\` depending on which serializer handles them. (I-F4)
7. `Generate._where_outputs_go` uses `Session.current()`, so it can write into a different session than the action is acting for. (A-F6)
8. The edge kind order has drifted between working_copy and the schema/BoundNode (`invokes` is 12 in one and 5 in the other). (R-G10)
9. `FidelityGuidance.instructions` swaps `practice.fidelities.current` and `format` and swaps them back, which is not thread-safe under the MCP threads. (A-F11)
10. A board command carries the ticket's session only in its `session=` word, so an action started inside another (Satisfy, Sketch, Iterate, AgentBdd), the failure record, and the action's log line fall back to `Session.current()` and can save to, or log in, a different session from the ticket's. (P-2, P-15)

## 3. Dead code and legacy aliases (breaks `no-legacy-api-after-refactor`)
- `space/repo/worktree.py` and `space/repo/push.py` have no importers and copy Worktree, Branch, and Commit methods. (K-F11)
- `space/context_config.py` free wrappers: three have no callers, and the other two wrap ContextConfig. (K-F23)
- `cdd_guidance/practices/workspace_bind.py` has no callers. (A-F20)
- `AgentToolSet.agent_tools`, `AgentInstructions.tool_steps`, `ToolsetManifest`, `toolsetCollection`, and `deferred_tools`/`deferred_prompt` are aliases. (I-F14)
- `Graph.load_nodes`/`load_edges` are aliases, `RuleResult` is unused, and `prompt_only` is an alias of `prose_only`. (R-G7, G15)
- `Source.expand` and the Python folds are used only by a spec; TypeScript does this work. (R-G12)
- `tools/echo` and `tools/echo_instructions` are near-identical toolsets, and both are deployed. (R-E1)
- `rule.py format_rules` is an alias of `formatted`. (A-F25)

## 4. Why validate missed all of this
Each finding looks fine inside the one file that holds it. A duplicate only shows up when you read the owner beside the copy, or count how many modules hold the same list. The cdd-main session has already added a backlog item for a checker that reads the whole codebase. These are the checks such a checker needs:
- Find lists of practice keys, stage names, or format names defined in more than one module.
- Find string literals for paths under `.sessions/` (`session.log`, `validation-reports`, `handoff-*`) outside Session.
- Find `split(".")`, `split("-")`, `rsplit`, and camel/kebab regexes applied to names that a domain object already holds.
- For each `@data_field`/`to_mcp_result` dict, check whether its keys repeat another class's members.
- Find TypeScript string unions or literal tables whose values equal a Python enum, constant, or list.
- Count members on each class and how many of them only delegate to a collaborator.

## 5. Suggested order
1. **Finish cdd-main's Ticket/Session work in `abd-cdd-session-board` and merge it.** It covers K-F1/F2/F3/F4/F6/F16 and part of F7/F17. Starting here first would collide with that work.
2. **Practice catalogue (1.1).** It removes about 15 lists and unblocks the catalog, graph, and session fixes.
3. **One serializer plus `AgentTool` as the only operation model (1.5, 1.6).** This fixes bugs 1, 2, and 6.
4. **FidelityProgress as data, then delete the TypeScript shadow models (1.2, 1.3).**
5. **Session-folder facts and Branch/Worktree objects (1.8, 1.9),** including the agreed move of board data to `board.repo`.
6. **Graph registers the parsed BoundNodes (1.4)** and **the catalog renders live guidance (1.7).** These are the largest pieces, and each should be its own ticket.
7. **Delete the dead code (section 3)** in any change that touches those files.

---

## Appendix: findings by area
Ids: **K** kanban/session/repo, **A** guidance/actions, **I** installation/MCP, **T** TypeScript, **R** graph/catalog/the remaining modules. "WIP" means the uncommitted session-board diff already addresses the finding.

### K — harness/kanban, space/session, space/repo, tools/file_manager
| Id | Sev | Where | What |
|---|---|---|---|
| F1 | high | ticket.py:214-251 | Six dicts keyed by slug copy FidelityProgress (WIP) |
| F2 | high | ticket.py log readers, session.py:810-900, 1387-1471 | Session log parsed in about four places; Ticket writes the log itself (WIP) |
| F3 | high | ticket_files.py | TicketFiles helper bag; builds its own FileManager (WIP) |
| F4 | high | ticket.py:266-274, 772-787 | PracticeRoot plus a `practices` dict copy PracticeSessionOutput (WIP) |
| F5 | high | session.py:410-423, 238, 327 | Board and repo data on Session as classmethods taking `repo_path`; not in WIP |
| F6 | high | session.py:216-297 | `to_mcp_result` snapshots on Session and PracticeSessionOutput (WIP) |
| F7 | med | ticket.py:397-407, 790; board.py:120 | Workspace bag built from string lookups (partly WIP, which adds new `ticket: str` parameters) |
| F8 | med | repo.py:1427, 2078-2201 | `worktree_for(str)`, `Worktree.branch: str`, `open_in_worktree` returns a Repo |
| F9 | med | board.py:306-360; ticket.py:500-706 | Slug built by hand; Stage flattens FidelityGuidance |
| F10 | med | session.py:224-1415; board.py:97 | Duplicate practice registry and practice key |
| F11 | med | space/repo/worktree.py, push.py | Dead duplicate modules |
| F12 | med | repo.py:152-187 | `Commit.to_mcp_result` defined twice; `note_payload` repeats `trailers` |
| F13 | med | repo.py:868 and others | ProjectTicket state held on Repo as dicts keyed by issue number |
| F14 | med | space/work_state.py | Copies `Repo.find_root`/`primary_root`; branch and worktree as strings |
| F15 | med | ticket.py:37-39; validate.py:17 | `REPORT_FOLDER`, `LOG_FILE`, and `HANDOFF_FILES` duplicated (the WIP adds a third copy) |
| F16 | med | board.py:203 | `Board.folders` should be FileManager.list (WIP) |
| F17 | med | ticket_files.py:25 | FileEntry beside FolderEntry (partly WIP) |
| F18 | med | — | Class sizes: Session 119, Repo 102, Ticket 73 |
| F19 | low | session.py, chat_context.py, chat_transcript.py | Chat pointer as a tuple; needs a ChatPointer value |
| F20 | low | report.py:82; board.py:393 | `ReportRule.fidelity: str` re-split; `Help` copies names |
| F21 | low | board.py, ticket.py | `*_name` data fields (`active_name`, `column_name`, `next_slug`, …) |
| F22 | low | kanban-model.drawio/.md | Model drift: Branch, Worktree, FileManager, … missing from the drawio; drawio members missing from the code |
| F23 | low | context_config.py:105 | Free wrappers duplicate ContextConfig |

### A — harness/guidance, guidance_actions, markdown, cdd_guidance actions and practices
| Id | Sev | Where | What |
|---|---|---|---|
| F1 | high | validate.py:367; diagnose.py:131; rule.py:196, 411 | "Shared plus active fidelity rules" built in four places |
| F2 | med | validate.py:327 | Re-parses rule bullets that RulesCollection already holds |
| F3 | high | validate.py:16; sketch_outline.py:24; guidance_actions.py:399; ux.py:45 | Practice registry duplicated |
| F4 | high | guidance_actions.py:16-27, 386 | `GuidanceRef` TypedDict turns guidance into dicts and loads it again |
| F5 | high | validate.py:17-120 | Report folder and name in Validate, duplicated in kanban |
| F6 | med | validate.py:122-234; guidance_actions.py:258; generate.py:57 | Session path rebuilt four times; Generate uses the wrong session lookup |
| F7 | med | validate.py:226 | Practice key rebuilt by string replace |
| F8 | med | guidance.py:51-378; improvement.py; partition.py | Practice folder computed seven ways |
| F9 | med | guidance.py:547; schema_map.py | Re-parses `{practice}.md` and the schema instead of `self.fidelities` |
| F10 | med | guidance.py:574-606; markdown.py:450 | `name`/`fidelity` and `parent`/`practice_guidance` duplicate fields |
| F11 | med | guidance.py:675 | Fidelity swaps the practice's current fidelity to find its template |
| F12 | med | sketch.py:47; guidance.py:91 | Sketch template lookup done twice |
| F13 | med | markdown.py:66-1110; guidance.py:390-537; graph_json_reader.py:150 | Format vocabulary written seven times |
| F14 | med | graph_json_reader.py; validation_report*.py | Violation as a 10-key dict beside RuleHit and Violation |
| F15 | med | guidance_actions.py:45-85; render.py | `load_document` free functions; reversed dependency; files read twice |
| F16 | med | guidance_actions.py:347; guidance.py:46, 774 | Slug regex repeated; `rsplit` bug |
| F17 | low | guidance.py:722-1041 | Probe/diagnostics functions in guidance.py |
| F18 | low | document, validate, improvement, partition | Copied `on(item)`; AttributeError on `contexts` |
| F19 | low | generate.py:73; guidance.py:290 | `generate_output` defined twice |
| F20 | low | guidance.py:67-289; workspace_bind.py | Session state held on guidance; dead module |
| F21 | low | guidance.py:225-266 | `supported_formats` copies `formats` |
| F22 | low | ddd.py:91-132 | Free functions that belong on DDD classes |
| F23 | med | ddd class_cards.py:23 | ClassCard re-classifies stereotypes as strings |
| F24 | low | tier_facts.py; access_facts.py | String-keyed fact dicts; copied helpers; another brace parser |
| F25 | low | partition_index.py:64; rule.py:399 | Copied completeness fields; `format_rules` alias |
| F26 | low | sketch_outline.py:63 | Another markdown heading and fence walker |

### I — harness/installation, agent_tools, mcp, hooks, health
| Id | Sev | Where | What |
|---|---|---|---|
| F1 | high | mcp_server.py:110-145 | `McpOperationDefinition` copies AgentTool |
| F2 | high | mcp_server.py:468-572 | Free functions look up the method again; `agent_tool_for_operation` |
| F3 | high | language_adapter.py:184-266, 740 | `mcp_name.split(".")` (IndexError); builds a whole McpHost to get a schema |
| F4 | high | destination.py:123; mcp_server.py:1221; `to_mcp_result` | Three serializers; path separators differ |
| F5 | med | agent_tools.py:88-247, 970; probe; files.py; hooks.py; installer.py | Name, slug, and `module:Class` mangling repeated |
| F6 | med | mcp_server, agent_tools, files.py | `getattr(…, "practice_guidance")` checks instead of polymorphism |
| F7 | med | hooks.py, hook_server.py, agent_tools.py, markdown.py, installer.py | Decorator mark names as scattered strings; two mark lists |
| F8 | med | hook_server.py:221-310; hooks.py:126-199 | HookHandler and handler records copy AgentTool; duplicated special case |
| F9 | med | hooks.py:141; hook_server.py:358; installer.py:73 | Skip lists by class-name string, three copies |
| F10 | med | mcp_server.py:35-43; agent_tools_probe.py:31-63 | Other toolsets' operation names hard-coded |
| F11 | med | installer.py:393-957; files.py:285; hook_server.py:389 | Installer parses files that other installations write; two invoke-line formats |
| F12 | med | mcp_server.py:718 | Throwaway McpInstallation built at runtime |
| F13 | med | agent_tools.py:1097; mcp_server.py:846; language_adapter.py:368-507 | Four readers of Python type hints |
| F14 | low | agent_tools.py:299-2262 | Legacy aliases kept alive |
| F15 | low | installer.py:40-132; mcp_server.py:147-362 | IDE destination facts in several places |
| F16 | low | destination.py:67-120; files.py:12-75 | Mark readers as free functions; identical `__new__` bodies |
| F17 | low | server_health.py:65; installer.py:935 | "Is the hook server running" checked twice; mirrored error classes |

### T — TypeScript clients and Python on their behalf
| Id | Sev | Where | What |
|---|---|---|---|
| PY-1 | high | ticket.py:214; board.py:307 | Python flattens FidelityProgress/FidelityGuidance for the clients; `Board.practices` not a data field |
| CU-1 | high | chat-ui fidelity-client.ts:25-108 | `FidelityJson` view model; invented `validated` state |
| CU-2 | med | chat-bar-client.ts:17-80; stage-client.ts | Stage order and status worked out in TypeScript |
| CU-3 | med | chat-bar-client.ts:19-138 | Open sessions and the active ticket worked out in TypeScript |
| CU-4 | med | fidelity-client.ts:22, 142; chat-bar-client.ts:195 | Commands built in TypeScript without `session=` |
| CU-5 | med | board-chat/board.ts | Hand-written chat route and argument union |
| CU-6 | med | test/cdd-stub.ts | Stub re-implements move_next, next_fidelity, and next_action |
| CU-7 | low | action-button-view.tsx:13 | Advance-or-next rule inside a view |
| CU-8 | low | fidelity-files-client.ts | File tab order and FileText shape copied |
| KB-1 | high | kanban ticket-client.tsx:50-144 | Rebuilds the dicts keyed by slug into progress |
| KB-2 | high | tile-actions-client.ts:58-89 | Validate/Review enabled by files on disk, against Python |
| KB-3 | med | ticket-client, tile-actions-client, board-page, report-client | Command, slug, skill name, and fix prompt built in TypeScript |
| KB-4 | med | ticket-client, board-client, board-columns-view | Rules about Complete and the allowed drops |
| KB-5 | low | board-client.tsx:93 | Board events inferred by diffing reads |
| KB-6 | low | column-client.ts | Column subtype recovered by duck typing |
| KB-7 | low | board-store, activation-client, root-choice-client | Copied titles and domain data held in page state |
| KB-8 | low | ticket-client.tsx:209 | Session-file path built in TypeScript |
| KB-9 | med | chat-client.tsx; board-page.ts | Relation between a ticket and its chat has no Python owner |
| TL-1 | med | tools/prompt_notify/prompt_notify.py | Second catalog built by scraping install folders |
| TL-2 | low | server-health-client.ts:138 | Reads runtime.json directly (intentional) |
| X1-X8 | — | across clients | Practices, states, ActionStates default, commands, activation defaults, handoff prompt, tab order, and column-ticket merging, each duplicated |

### R — harness/graph, catalog_generator, handoff, record_decisions, echo, granola, scripts
| Id | Sev | Where | What |
|---|---|---|---|
| G1 | high | working_copy.py:173-750; graph.py:705-949 | Parsed BoundNodes copied into flat records and turned back into generic Nodes |
| G2 | high | rule_context.py:74-237; story_model_lookup.py | Rules re-parse files to find the model object by name |
| G3 | med | rule_context.py:177; working_copy.py:785; schema_edges.py:281 | Step keyword and phase derived outside Step |
| G4 | med | working_copy, rule_context, graph.py | Member's owner class worked out four ways, by splitting ids |
| G5 | high | explorer.py | `*Entry`/`*Inventory` family mirrors Node, Source, PracticeGraph, and Filter |
| G6 | med | graph.py:1480 | Filter as a dict beside the Filter class |
| G7 | med | graph_rules_collection.py; guidance_prose_index.py | GraphRule copies the guidance Rule body; `prompt_only` alias |
| G8 | high | eight places | Practice registry |
| G9 | med | schema_edges, schema_rules, schema_map | schema.yaml parsed by regex in four places; no Schema class |
| G10 | med | bound_node.py:57; schema_edges.py:84; working_copy | Edge order defined three times, and the copies have drifted |
| G11 | med | working_copy.py; graph.py; schema_edges.py | Regex re-scans of code the class model already holds |
| G12 | low | graph.py:167-528 vs call-expansion.ts | Folding and inlining duplicated; Python side dead |
| G13 | med | working_copy.py:391, 477 | Throwaway DDD objects; bounded contexts read from headings |
| G14 | med | working_copy.py:210 | Model members flattened into dicts |
| G15 | low | graph.py:905-1248 | `load_*` aliases; record writing on Graph; unused RuleResult |
| G16 | low | working_copy.py:858 | Another snake/kebab converter |
| C1 | high | catalog_generator.py:317-423 | CatalogFidelityGuidance scrapes markdown again |
| C2 | high | catalog_generator, foundry_chrome | Practice guide re-parsed in about eight functions |
| C3 | med | catalog_generator, foundry_chrome | Mapping from stage to board key written five times |
| C4 | med | catalog_generator:60; foundry_chrome:184 | Practice cards copied into module globals |
| C5 | low | catalog_generator:112-1711 | Toolset names derived again; fake RegistryEntry |
| C6 | med | catalog_generator:1345-1760 | Renderers are mutable bags of copied fields |
| C7 | med | catalog_generator:680-1060 | Action registry written out three times; AST walk of action sources |
| C8 | med | foundry_chrome; exercise_hooks.py | Three finders for example files |
| C9 | med | project_approach.py | Regex hints repeat FidelityGuidance.outputs; writes to Catalog private fields |
| H1 | low | handoff.py:41; ticket.py:38 | Handoff file pattern in two modules; stale module context |
| R1 | low | record_decisions.py:21 | No CDR object; stale module context |
| E1 | med | tools/echo vs tools/echo_instructions | Duplicate toolsets |
| N1 | low | granola.py:37-53 | Filing plan as dicts; copied slug |
| S1 | med | scripts/backfill-session-log.py | Writes session.log by hand; calls private `_append_log` |
| S2 | low | scripts/instances.py; start.py | Repeats HookDaemon state reading; copied `_first_pong` |
| S3 | low | scripts/kanban_board_e2e.py | Writes session.json and log lines by hand |
| S4 | low | scripts/exercise_hooks.py | Repeats practice discovery and rule flattening |
| A1 | low | graph app overlay-labels.ts | LERN node-type lists repeat the overlay schema |

### P — state passed around as parameters (root cause 1.12)
The search read the working tree on 2026-11-06 and found 37 instances: 10 high, 16 medium, 11 low.

| Id | Sev | Where | What |
|---|---|---|---|
| P-1 | high | agent_tools.py:1191 `log_session_invocation`, :1260 `_expanded_reply`; guidance_actions.py:147 `_bind_guidance`; generate.py:20-34; validate.py:52-91 | One `guidance` argument is handed down five layers and stored again at each; the action should be made for its session, practice, and fidelity once and read them from there |
| P-2 | high | ticket.py:264 `generate_commands`; ticket-client.tsx:243 `actionCommand`; guidance_actions.py:173 `_bind_guidance_string`, :277 `acting_session` | The ticket's session travels as a `session=` word in the command text, is parsed back, and is loaded again on every call, while `run` and `_log_running_action` still use `Session.current()` (overlaps T-CU4, KB-3) |
| P-3 | high | tile-formats.ts:23 → tile-actions-client.ts:106 → ticket.py:259 → guidance_actions.py:180,189 → agent_tools.py:750 → validate.py:173; session.py:1558 `last_generated_format` | The chosen format passes through six layers and is finally read back by parsing session.log; the fidelity should save the format chosen for it (overlaps A-F4) |
| P-4 | high | ticket.py:259 `generate_commands`, :124 `progress_of(slug)`; fidelity-client.ts:352, tile-actions-client.ts:107, ticket-client.tsx:271 | Callers that hold a fidelity's progress pass its slug and the ticket's name so `progress_of` can find it again; this should be `progress.actions.generate(format)` |
| P-5 | high | session.py:713 `practice_root`, :1470 `fidelity_outputs`, :592 `files_declared_by`, :601 `has_declared_output`, :1237 `log_validation`, :1189 `log_guidance_action` | Session is handed a guidance or fidelity it already holds as `session.practices[key].fidelities[name]`; the practice and fidelity should answer their own outputs, root, and log lines |
| P-6 | high | session.py:272-344 `PracticeSessionOutput` → `_guidance_for`, `_default_output_paths`, `choose_practice_root`, `remember_parent_folders` → context_config.py:81 | PracticeSessionOutput passes its own name and guideline back into Session's private methods four layers deep; its root, folders, and graph should be its own state |
| P-7 | high | render.py:35-43 → guidance.py:434 `render` → :450, :514 `_call_render` → ddd.py:78 → format adapter | `format`, `source`, `previous`, `keep_positioning`, and `workspace` pass through four layers, although the practice holds its format and its session's folder |
| P-8 | high | ticket-client.tsx:84,88; ticket.ts:10,17; files-panel-client.ts:79; side-panel-client.ts:44; tile-actions-client.ts:107,133; activation-client.ts:80 | Clients rebuild generated clients with `.named(api, ticketName, slug)` although the TicketClient already holds that data (overlaps KB-8) |
| P-9 | high | board-store `Tile.ticket`, `ReportPanel.ticket`, `FilesPanel.ticket`, `Activation.ticket`, `RootChoice.ticket`; board-page.ts:85-101; tile-client.ts:200 | Page state keeps the ticket's name, and every action searches `board.tickets` for it again; each panel or tile should hold its TicketClient (overlaps KB-7) |
| P-10 | high | chat-ui fidelity-client.ts:347-374; fidelity-files-client.ts:474,487; chat-bar-client.ts:190,201; session-client.ts:401-450 | Free functions take the engine and a client, read the chat bar again, and send `{ticket, fidelity}` strings; they should be methods on the client that holds the ticket |
| P-11 | med | kanban chat-client.tsx:62-134; ticket-client.tsx:177-269 | Every chat call is given `(this.name, this.worktree)`; the ticket should own its chat (overlaps KB-9) |
| P-12 | med | board.py:187 `activate`, :213 `open_worktree`, :222 `workspace`, :200 `leave`, :110 `worktree_of` | Board operations take a ticket's name and do the ticket's work; they belong on Ticket (overlaps K-F7) |
| P-13 | med | ticket.py:75 `Ticket.load`, :360 `FidelityProgress.load`; session.py:252, :514 | Every MCP call carries name strings, and the loader rebuilds the whole board to find the one object the client had |
| P-14 | med | validate.py:115 `_fidelity_in`; ticket.py:490, :528, :391 | A fidelity in hand is looked up again by key and name, because the action's and the board's practices are separate instances; there should be one fidelity object per session |
| P-15 | med | satisfy.py:212-220; sketch.py:130; iterate.py:180; agent_bdd.py:21,28; generate.py:34 | An action builds fresh actions and passes the guidance on; the new action has no session, so its report goes to the current session (bug 10) |
| P-16 | med | sketch.py:27, :67, :89 | The agent passes the session's folder and the slug, which a Sketch made for its session and practice would hold |
| P-17 | med | grill_context.py:17, :43, :77 | The session's workpath is passed as `root` on every call |
| P-18 | med | partition.py:149-172 → :122 `partition_corpus` → :96 `index`, :113 `segment`; :70 `_scaffold_of` | Output folder, slug, and scaffold are pulled off the guidance and passed down three calls; `_scaffold_of` does the fidelity's own work |
| P-19 | med | validate.py:151, :237, :241, :275, :112 | Validate hands the session's folders to free functions and to Graph, which should get them from the session |
| P-20 | med | session.py:1427 `_graph_for`; graph.py:1153 `load_working_copy`, :1187 `load_files` | Session writes a folder and practice roots into Graph's private fields; the session's practice should own its graph |
| P-21 | med | session.py:1202 `log_guidance_action` → `opened.guideline = item` → `_attach_workspace` | Each action replaces the shared session's practice with its own guidance and never restores it; later readers see the last action's fidelity and format (overlaps A-F20) |
| P-22 | med | ticket.py:542 `_report_file` → report.py:165-232 | The report is built from the session's repo and workpath, then progress and superseded reports pass through four private methods; the fidelity should own its reports |
| P-23 | med | repo.py:1896 `_bind`, :1910 `_at`, :1928-2011 switch/close branch and worktree | Repo tools take a path to another clone and forward to it; `_bind` sets `_agent_active` on the shared toolset (overlaps K-F8) |
| P-24 | med | session.py:785 `mark_loop`, :827 `append_log`, :1033; chat_context.py:21,92,102; mcp_server.py:827; agent_tools.py:1031,1189 | Three chat strings are popped from every call, set in context variables, applied to the session, then cleared; the session's turn should hold a chat pointer object (overlaps K-F19) |
| P-25 | med | rule.py:155 → session.py:1228 → :1415 → :931; :1213 | Guidance and its rule groups pass four calls deep and end as a tuple of strings; Session reaches into the rules' private methods |
| P-26 | med | agent_tools_probe.py:83-520; guidance.py:771-860 | About 15 free functions take the Installer first and do its work; they belong on the Installer or a probe object (extends A-F17) |
| P-27 | low | board.py:243 `set_wip_limit`, :272 `wip_limit`; board-client.tsx `submitWipLimit` | A stage's name is passed so Board can look up a limit that Stage owns |
| P-28 | low | board.py:259 `help(practice, fidelity)`; side-panel-client.ts:154; tile-view.tsx:33 | TypeScript splits the slug so Board can find the fidelity the tile already showed (overlaps K-F20) |
| P-29 | low | session.py:451 `repo_from_session(repo_path)`, :746 `switch` → :945 `resolve`; board.py:197 | Four location values are threaded from `switch` to `resolve`, and an instance method takes a repo path it holds (overlaps K-F5) |
| P-30 | low | handoff.py:35; record_decisions.py:23; ticket-client.tsx:256; chat-bar-client.ts:202 | The ticket's name is passed only as prose while the tools write to the current session (overlaps H1, K-F5) |
| P-31 | low | guidance.py:209 `files(stage)`; session.py:567 `files(stage)` | A stage name passes two layers down and is compared to each fidelity's stage string |
| P-32 | low | project_rules.py:19 `load_project_rules(root, practice, fidelities)` | A free function is given the practice's folder, key, and fidelity names; it belongs on PracticeGuidance |
| P-33 | low | practice_catalogue.py:79 `key_of(guidance)`; 7 callers | A classmethod takes a practice and returns its own `key` |
| P-34 | low | guidance.py:672-674 `FidelityGuidance.clean_engineering` | The host practice's format is copied onto the companion's practice instead of the companion reading it from the fidelity |
| P-35 | low | agent_tools.py:1821-1850 | The instruction expander sets and restores loop state on itself instead of passing the loop item |
| P-36 | low | agent_tools.py:1018, 1172 `log_session_invocation(repo_path=)` | No caller passes `repo_path`, and the method uses `Session.current()` |
| P-37 | low | catalog_generator.py:132-164 | Entries set `_current_*` fields on the shared Catalog and never reset them (overlaps C6) |

Groups: actions take guidance, session, format, and paths instead of being made for a session (9); Session does its practices' and fidelities' work (8); clients pass ticket names, session files, and slugs (7); Board does its tickets' and stages' work (2); objects in hand looked up again by name (2); paths and the current session used instead of objects (4); context threaded through calls or left set on shared objects (4); free functions that take their owner first (1).

Other duplicates noted across modules: process liveness is checked in three places (hook_server, hook_daemon, scripts/instances). `GraphStoryModel` copies the parsed story nodes into flat records, the same pattern as G1. About eight slug helpers live in practice files. `space/repo/.context/module-context.md` still describes `space/git`, `GitRepo`, and `WorkSession`.

---

## Progress

Updated 2026-11-06 on `ensure-domain-orientation-refactor`. ✅ done, ◐ partly done, ⬜ not started. Each line names the commit that holds the work.

### Root causes
- ✅ **1.1 Practice catalogue.** `PracticeCatalogue` in `harness/guidance/practice_catalogue.py` replaces every Python practice list (`54fd3c3f3`). The TypeScript lists `PRACTICES` and `PRACTICE_COLOURS` are left for 1.3.
- ◐ **1.2 FidelityProgress as data.** Ticket sends one `FidelityProgress` per fidelity, with its state, its actions, and `allowed_actions`; the six dicts are gone (session-board merge `0b1024083`). Bug 5's TypeScript rule is deleted (`6f6370fcd`). Left: the chat bar's `FidelityJson` and its `validated` state (CU-1), the `ActionStates` default copied in TypeScript, and the reviewed/done naming.
- ⬜ **1.3 Domain rules in TypeScript.** Not started. Commands wait on 1.12, so they are built from the session's practice, fidelity, and action rather than on `Ticket`. The chat bar's findings wait until the cdd-chat-ui work lands, so the two changes do not collide.
- ◐ **1.4 Graph second model.** Mode A is done: each node holds its parsed object as `Node.model`, and the re-parse helpers and `story_model_lookup.py` are deleted. Edge order, the schema reader, and the explorer copies are fixed too (`d351aeed1`). Left: the graph still builds its own `Node`s rather than registering the parsed `BoundNode`s (Mode B), and G3, G4, G13, and G14 are only partly done.
- ◐ **1.5 AgentTool is the only operation model.** `McpOperationDefinition` is gone, and MCP and the language adapter read `AgentTool` (`651c7cb30`). Left: `HookHandler` still copies the tool (I-F8).
- ◐ **1.6 One serializer.** `data_of` is the only serializer, and `McpHost._json_default` is gone (`651c7cb30`). Left: `Commit.to_mcp_result` is still read by a branch in `data_of`; `@data_field` on Commit would remove both.
- ⬜ **1.7 Catalog renders live guidance.** `CatalogFidelity` still scrapes the practice markdown.
- ✅ **1.8 Session-folder facts.** Session owns `log_path`, `error_path`, `reports_folder`, `latest_handoff`, and `new_handoff_path`; Generate reads `acting_session()` (`53d1349e2`).
- ◐ **1.9 Git concepts as objects.** Branch and Worktree are objects, and the board's backlog folder and board file are on Repo (`a0b8dc28c`). Left: `Workspace` is still built from three booleans, and `Session.active_name(repo_path)` is still a classmethod.
- ✅ **1.10 Slugs, formats, and names.** `FidelityGuidance.slug` everywhere, one `Name` converter, one `Format` vocabulary, and `FidelityGuidance` keeps `name` and `practice_guidance` (`df4361395`). Left: K-F21's `*_name` data fields and some prose in `cdd_guidance` that still writes slugs like `ddd-bounded_context`.
- ⬜ **1.11 Classes that only read their collaborators.** Not started; `ChatPointer` does not exist yet.
- ⬜ **1.12 State passed around as parameters.** 37 instances are listed in appendix area P; not started.

### Bugs
- ✅ 1. `language_adapter.py` no longer splits `mcp_name` (`651c7cb30`).
- ✅ 2. `Commit.to_mcp_result` is defined once.
- ✅ 3. Partition and the shared `on(item)` run on a practice, with a spec (`f5c0a030f`).
- ✅ 4. `stories-story-map` resolves to Stories, with a spec (`df4361395`).
- ✅ 5. The board reads `allowed_actions` only, and Python allows Validate and Review once a declared file exists (`6f6370fcd`). The board's own spec for it did not run: its setup times out starting a cdd server.
- ✅ 6. Paths serialize one way, through `data_of` (`651c7cb30`).
- ✅ 7. Generate's output paths come from the session the command names (`53d1349e2`).
- ✅ 8. Edge order is defined once, in `graph.py` (`d351aeed1`).
- ✅ 9. `FidelityGuidance.instructions` reads its own template without swapping the practice's fidelity, with a 20-thread spec (`f5c0a030f`).
- ⬜ 10. Actions started inside another action, the failure record, and the action's log line use `Session.current()` instead of the ticket's session. Fixed by 1.12.

### Dead code and legacy aliases
- ✅ `space/repo/worktree.py` and `space/repo/push.py` are deleted.
- ✅ `space/context_config.py` free wrappers are deleted.
- ✅ `cdd_guidance/practices/workspace_bind.py` is deleted.
- ✅ `AgentToolSet.agent_tools`, `AgentInstructions.tool_steps`, `ToolsetManifest`, `toolsetCollection`, and `deferred_tools`/`deferred_prompt` are deleted.
- ✅ `Graph.load_nodes`/`load_edges`, `RuleResult`, and `prompt_only` are deleted.
- ✅ `Source.expand` and the Python folds are deleted (`d351aeed1`).
- ✅ `tools/echo_instructions` is deleted; `tools/echo` is the one echo toolset.
- ✅ `rule.py format_rules` is deleted (`f5c0a030f`).

### Not yet checked
- **TypeScript runtime tests:** the board's vitest setup hangs starting a cdd server, and the chat bar has no plugin manifest, so the TypeScript changes are type-checked only.
- **Python story tests (`*_story.test.py`):** they fail the same way on the base branch, so they are not counted in the 2645 passing specs.
