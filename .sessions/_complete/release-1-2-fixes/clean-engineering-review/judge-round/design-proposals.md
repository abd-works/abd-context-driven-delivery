# Design proposals for review

Seven judges read the code in this worktree and made 86 proposals for design changes. Many of them describe the same concept from the side of the module each judge was reading, so they are merged here into **25 proposals**, plus a closing table of **13 smaller changes** that stand alone. One of the 86 was dropped because the code had already been fixed another way. No code was changed in writing this document.

**How this was checked.** For every merged proposal the main classes it names were opened and the "before" picture was compared with the code today: class names, key members, file paths, and line numbers. Where a judge's picture was wrong it is corrected here and the correction is said in the proposal. Line numbers in links were read from the files on 2026-11-21; a link without a line number points to a file whose lines were not checked one by one.

**The code was moving while this was written.** Other agents were applying the judges' "fixes that change no design" in this same worktree. The pictures and line numbers here match the working tree at commit `fca361c79` plus the uncommitted fixes then in progress in space/kanban and space/repo. Three things the judges proposed were already done by those fixes and are said so where they come up: Clean Engineering's `card_lines` left its markdown package (proposal 1), the UX reading no longer imports format packages (listed under "Dropped"), and a story map saved as a whiteboard file now opens (proposal 11). Line numbers in space/kanban and space/repo may drift again before you read this; the class and member names are what to go by.

**How to read the class boxes.** Each proposal has one `diff` block. A line that starts with `@@` names the file or module the classes below it live in. A line that starts with a space is there today and stays. A line that starts with `-` is removed. A line that starts with `+` is added. A move or a rename is shown as a `-` line and a `+` line, with a note such as `(moved from TicketCheckout)`. `...` stands for members the change does not touch.

**How to decide.** Each proposal ends with one decision line. Several proposals have parts marked (a), (b), (c) that can be approved separately; write the parts you want after `change:`.

**The four goals** each proposal is judged against, by the names used through this document: **Sharper module boundaries** (smaller seams, one-way dependencies, deeper private surface); **One object model** (the same work in one shape); **Resource orientation** (things with behaviour and properties, fewer doers and managers); **Domain orientation** (objects, interactions and state whose names form the API's language).

**The waves.** Proposals are ordered by what they give against the four goals, divided by their cost and risk. Each wave leaves the unit tier green; the heavy tier runs once at the end of each wave.

| Wave | What it does | Proposals |
|---|---|---|
| 1 | Cheap boundary fixes: no saved file changes, no published name changes | 1, 2, 3 (a-e), 4 (a) |
| 2 | One owner for each fact: git, the session record, declared outputs, rules, the graph toolset | 5, 6, 7, 8, 9, 10 |
| 3 | One object model for render, reports, and what the pages show | 4 (b-f), 11, 12, 13, 14, 15 |
| 4 | Framework internals and large moves, each needing the heavy tier | 16, 17, 18, 19, 20, 21, 22, 3 (f) |
| 5 | Wide renames and changes a person must verify on screen | 23, 24, 25 |

## Summary

| # | Proposal | Goals served | Modules touched | Size (files, rough lines) | Risk | Wave | Sources |
|---|---|---|---|---|---|---|---|
| 1 | The graph reading leaves the model packages, and *PracticeReading* moves to harness/graph | Sharper module boundaries | harness/guidance, harness/graph, clean_engineering, ddd | 26 files, 240 lines, mostly moves | Low | 1 | practices 1; guidance-graph P2 |
| 2 | The framework has one typed description of a session | Sharper module boundaries, Domain orientation | harness/agent_tools, hooks, mcp, guidance, guidance_actions, graph; space/session | 12 files, 180 lines | Low | 1 | harness-lower 2; guidance-graph P9 |
| 3 | Practices reach each other through named seams: a source-code module, a class-model seam, and *StoryTree* | Sharper module boundaries, One object model | new `practices/source_code`; clean_engineering, ddd, bdd, stories, ux, patterns, desktop_walk, space/session | 60 files, 900 lines (most are import lines) | Low for (a-e), high for (f) | 1, 4 | practices 7, 3; stories S7, S4, U2, R5 |
| 4 | One board element id, one whiteboard reader, one draw.io document, one record of where a file is published | Sharper module boundaries, One object model, Resource orientation | harness/whiteboard, new harness/drawio, harness/design_canvas, four practices, files_app, space/session | 55 files, 1,500 lines | Low for (a), medium for the rest | 1, 3 | stories A2, U7; practices 5; apps D5, D3, D4 |
| 5 | Git facts have one reader, a checkout is one class, and a branch answers where it is checked out | Sharper module boundaries, One object model, Resource orientation | harness/git, space/repo, harness/mcp, agent_tools, process, space/kanban | 22 files, 700 lines | High | 2 | kanban 2, 3, 4; harness-lower 8 |
| 6 | The session record has typed fields with one writer each, and a session knows its one checkout | Sharper module boundaries, One object model, Resource orientation, Domain orientation | space/session, space/kanban, harness/guidance_actions | 22 files, 650 lines; session.json upgraded on read | High | 2 | space-session 1, 2; kanban 1 |
| 7 | Declared outputs are declarations; the session answers what is on disk | Sharper module boundaries, One object model | harness/guidance, space/session, cdd_guidance actions, space/kanban | 18 files, 350 lines | Medium | 2 | guidance-graph P8; space-session 4; stories R2 (placement) |
| 8 | Practice knowledge leaves the framework and the session module | Sharper module boundaries, Domain orientation | harness/markdown, agent_tools, installation, graph, guidance; space/session; five practices; validate | 35 files, 900 lines | High | 2 | harness-lower 9; space-session 8; guidance-graph P6; stories R3 (scope) |
| 9 | A rule is one object: its text, its check, and its findings | One object model, Resource orientation | harness/guidance, harness/graph, every practice's and pattern's rules, validate | 40 files, 250 lines in harness/graph plus one-line returns | Medium | 2 | guidance-graph P1 |
| 10 | The *Graph* toolset comes within its budget | Sharper module boundaries, Resource orientation | harness/graph, space/session, graph app, files_app, validate | 14 files, 500 lines | Medium | 2 | guidance-graph P3, P4, P5, P11, P12 |
| 11 | One format contract, and a render request that renders itself and answers a typed result | Sharper module boundaries, One object model, Resource orientation | harness/guidance, render action, every practice's format adapters, space/session, files_app | 45 files, 900 lines; 80 spec call sites | High | 3 | stories A1, R2 (result), U6; guidance-graph P7 |
| 12 | One way to write a render onto a file that is already there | One object model | harness/guidance, render action, stories, ux, bdd, clean_engineering, ddd | 20 files, 500 lines | Medium (first pass only) | 3 | stories R1; practices 6 |
| 13 | One validation report object and one checked-fidelity object | One object model, Resource orientation | space/session, space/kanban, validate action | 14 files, 550 lines | Medium | 3 | space-session 3; stories R3 |
| 14 | The pages ask Python for rules, listings, prompts, and commands | Sharper module boundaries, One object model, Domain orientation | space/session, space/kanban and its page, harness/chat-ui, files_app, harness/guidance | 40 files, 950 lines; 400 TypeScript lines removed | Medium | 3 | kanban 8, 5; apps D6; space-session 6; guidance-graph P10 |
| 15 | The chat that asked is passed, a new chat is one object, and a queued prompt does its own work | Sharper module boundaries, Resource orientation, Domain orientation | harness/chat, space/session, space/repo, space/kanban, tools/prompt_queue, desktop_walk | 22 files, 750 lines | Medium | 3 | apps D9, D1, D2; space-session 10 |
| 16 | One daemon model and one lock file | One object model | harness/process, hooks, mcp, installation, space/repo, scripts | 20 files, 400 lines | High | 4 | harness-lower 1 |
| 17 | Install channels, the install run, and a toolset's name are objects | One object model, Resource orientation, Domain orientation | harness/annotations, agent_tools, installation, hooks, mcp, diagnostics, catalog_generator | 40 files, 1,000 lines | High | 4 | harness-lower 3, 4, 5, 10 |
| 18 | *McpHost* holds a request object, the marketplace is its own object, and a running call answers data | Sharper module boundaries, Resource orientation | harness/mcp, agent_tools, diagnostics, chat-ui, tools/prompt_queue, the TypeScript adapter template | 16 files, 600 lines | Medium | 4 | harness-lower 6, 7, 11 |
| 19 | Apps and releases leave harness/diagnostics, and an end-to-end run has one model | Sharper module boundaries, One object model | harness/diagnostics, new harness/apps and harness/release, e2e_review, files_app, kanban, chat-ui | 37 files, 550 lines of real change | Medium | 4 | apps D7, D8 |
| 20 | space/session splits into modules with one-way dependencies | Sharper module boundaries | space/session, space/kanban, cdd_guidance actions, every importer | 45 files of import lines, four new cards | Medium | 4 | space-session 5 |
| 21 | A story file in code is read once, by a thin *Stories* | One object model, Resource orientation | cdd_guidance/practices/stories | 30 files, 800 lines | Medium | 4 | stories S1, S2, S3, A5 |
| 22 | One class-card notation, and a class in code that answers for itself | One object model, Resource orientation | clean_engineering, ddd, bdd | 20 files, 700 lines | Medium | 4 | practices 2, 4 |
| 23 | The TypeScript pages keep their state in objects | Resource orientation | stories app, graph app, files_app, UX story demo, chat-ui, prompt queue mod | 25 files, 1,300 lines | Medium, verified on screen | 5 | stories A4, U5; guidance-graph P13; apps D10 |
| 24 | The board opens the Files app for files, and its own file panel goes | One object model | space/kanban page | 1,200 lines removed | Product decision | 5 | kanban 9 |
| 25 | The Stories root class is named *StoryMap*, and each node has one copy path | Domain orientation | stories, ux, space/kanban, space/session, diagnostics, every install | 80 files, mechanical | High (published tool names change) | 5 | stories S5, S6 |
| X1-X13 | Smaller changes (table at the end) | mixed | mixed | 13 changes, 20 to 450 lines each | Low to medium | any | space-session 7, 9; kanban 6, 7, 10; harness-lower 12 (four); stories A3, U3, U4, R4 |

---

## 1. The graph reading leaves the model packages, and *PracticeReading* moves to harness/graph

- **Problem today:** The code that reads the working copy into the graph sits inside each practice's model package, although it is a client of the model and of its formats. In DDD that still makes an import cycle: the reading imports the model's markdown format ([ddd/model/graph_reading.py:31](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ddd\model\graph_reading.py#L31)), which imports the model back. In Clean Engineering the cycle itself was removed while this was written (`card_lines.py` moved out of `model/markdown/`, so the reading now imports [model/card_lines](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\graph_reading.py#L28)), but fourteen files and about 2,300 lines that exist only for the reading and the rules are still mixed into the class model that every format adapter and three other practices import. In the framework, *PracticeReading* lives in harness/guidance ([practice_reading.py:57](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\practice_reading.py#L57)) although only harness/graph uses it, so it needs three protocols that describe the graph loosely ([practice_reading.py:15](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\practice_reading.py#L15)) and it names the practices it reads after by string key.
- **Class model, with the change marked:**

```diff
@@ harness/guidance/practice_reading.py  ->  harness/graph/practice_reading.py @@
-class HoldingGraph(Protocol)
-class HeldRuleRun(Protocol)
-class HeldNodes(Protocol)
-def rules_in(module_path) -> dict[str, Any]
 class PracticeReading(practice)                      (moved from harness/guidance)
-  graph: HoldingGraph | None
-  in_graph: HeldNodes | None
-  reads_after: tuple[str, ...]
-  graph_checks / own_graph_checks / checks -> dict[str, Any]
+  graph: Graph | None
+  in_graph: PracticeNodes | None
+  reads_after: tuple[type[PracticeGuidance], ...]
+  graph_checks / own_graph_checks / checks -> dict[str, PracticeGraphRule]
+  _rules_in(package)                                 (was the module function rules_in)
   ...
@@ harness/guidance/guidance.py @@
 class PracticeGuidance
-  reading_type: type[PracticeReading] = PracticeReading
+  reading_type: type | None = None                   (harness/graph sets the default when it is imported)
   ...
@@ cdd_guidance/practices/clean_engineering/model/ @@
-  graph_reading, code_read, call_links, compared_facts, class_facts, class_graph, folder_facts,
-  operation_facts, module_exposure, public_routes, import_cycles, near_copies, operation_counts,
-  imported_classes, card_lines
@@ cdd_guidance/practices/clean_engineering/reading/      (new package with its own module card) @@
+  the fifteen files above, unchanged                 (moved from model/)
+  imports model/ and model/markdown/; nothing in model/ imports reading/
@@ cdd_guidance/practices/ddd/ @@
-  model/graph_reading.py
+  reading/graph_reading.py                           (moved from model/)
```

- **What callers write, before and after:**

```python
# before
from harness.guidance.practice_reading import PracticeReading
from cdd_guidance.practices.clean_engineering.model.graph_reading import GraphReading
reads_after = ("clean_engineering", "ddd")
# after
from harness.graph.practice_reading import PracticeReading
from cdd_guidance.practices.clean_engineering.reading.graph_reading import GraphReading
reads_after = (CleanEngineering, Ddd)
```

- **What it buys:** Sharper module boundaries. DDD's import cycle goes, and the dependencies run one way in both practices: reading, then formats, then model. harness/guidance loses one class and three protocols; harness/graph types what it reads instead of taking `Any` in four signatures. In Clean Engineering the class model is separated from about 2,300 lines that exist only for the reading and the rules.
- **Cost and risk:** About 26 files; 150 lines moved and 40 changed in the framework, 16 files moved and about 50 import lines in the practices. Two new module cards. Unit tier, then the heavy graph specs (the worker graph build). No saved file and no published name changes. Checked: every practice names its reading on its own class (`reading_type = GraphReading` at [clean_engineering.py:28](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\clean_engineering.py#L28)), so moving the files does not break how the framework finds it. Risks: a spec that makes a bare practice without importing harness/graph gets no reading; the new file must sit below `graph.py` to avoid a new cycle; the new `reading` module is measured for `deep-module` on its own and may show a wide seam until proposal 22.
- **Depends on / conflicts with:** Do before 8 (which adds members to *PracticeReading*) and 22. Do the framework move and the practice move in one pass, so the five `graph_reading.py` files change their import once.
- **Decision:** `[ ] approve  [ ] reject  [ ] change:`

---

## 2. The framework has one typed description of a session

- **Problem today:** harness may not import space/session, so it describes the session it is handed, and it does so in three places and loosely. `ToolCall.session` and every operation of *SessionOpener* answer `Any` ([tool_call.py:25](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\tool_call.py#L25), [tool_call.py:191](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\tool_call.py#L191)). *ActionSession* types most members as `Any` ([guidance_actions.py:53](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance_actions\guidance_actions.py#L53)). *WorkedSession* ([worked_session.py:45](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\worked_session.py#L45)) is a second, separate description of the same object. It was out of step with the code when the judges read it and was corrected while this was written (it now names `paths`, `log`, and the output's `written` files), which shows how such a copy drifts. The framework also calls three objects deep into the session ([agent_tools.py:1091](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\agent_tools.py#L1091), [mcp_server.py:888](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L888), [hook_server.py:564](C:\dev\abd-cdd-release-1-2-fixes\harness\hooks\hook_server.py#L564)) and reads the graph with `getattr` ([graph.py:1537](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\graph.py#L1537)). A rename in space/session breaks the framework with no type to say so.
- **The two judges disagreed.** One proposed a narrow protocol with four operations in harness/agent_tools (*CallSession*). The other proposed one wide protocol in the same file, covering everything three framework modules read. **Recommended:** a protocol at each layer, each extending the one below, so every module declares only what it reads and agent_tools learns nothing about practices. The wide single protocol would copy most of *Session*'s interface into the lowest module.
- **Class model, with the change marked:**

```diff
@@ harness/agent_tools/tool_call.py @@
+class CallSession(Protocol)                    the session a call works in, as agent_tools and mcp use it
+  log_tool(call: ToolCall, tool: str)          (replaces session.log.by(chat).tool(...))
+  log_failure(call: ToolCall, failure)         (replaces session.log.by(chat).failure(...))
 class SessionOpener(Protocol)
-  saved_in(project) -> Any
-  open_in(call) -> Any
-  named_in(session_file, call) -> Any
+  saved_in(project) -> CallSession | None
+  open_in(call) -> CallSession | None
+  named_in(session_file, call) -> CallSession | None
 class ToolCall
-  session -> Any
+  session -> CallSession | None
@@ harness/hooks/hook_server.py @@
+class HookSession(CallSession, Protocol)
+  chat_injections: ChatRuleInjections          (ChatRuleInjections stays here, beside HookPayload and HookResult)
+  log_hook_dispatch(text: str)                 (replaces session.folder.hook_log("dispatch.debug").stamped(text))
@@ harness/guidance/worked_session.py @@
-class WorkedSession(Protocol)
+class WorkedSession(CallSession, Protocol)
   work_root
   session_files: _SessionFiles                 find(pattern)
   paths: _SessionPaths                         document_named(content, paths)
+    path_named(path)
   log: _SessionLog                             injected_rules
+    by(chat)
+  name, repo_path, session_file, record_folder, overlays, stories
+  record: _SessionRecord                       fields
+  practices: Mapping[str, PracticeOutput]
+  graph: object                                (typed as Graph only inside harness/graph)
+  choose_overlays(overlays), practice(key)     (these members moved from ActionSession, typed)
 class FidelityOutput(Protocol)
   chosen_formats, choose_format(format, is_chosen), roots
   written: _WrittenFiles                       output_paths(), files(), has_output()
@@ harness/guidance_actions/guidance_actions.py @@
-class ActionSession(Protocol)                  name, practices: Mapping[str, Any], overlays, stories, record,
-                                               log: Any, graph: Any, work_root, repo_path, paths: Any,
-                                               session_files: Any, record_folder, session_file; choose_overlays,
-                                               practice(key) -> Any, path_named(path)
-class _SessionRecord(Protocol)                 (moves to worked_session.py)
@@ harness/graph/graph.py @@
 class Graph
-  for_call(call): getattr(session, "graph", None)
+  for_call(call): call.session.graph
@@ space/session/session.py @@
 class Session
+  log_tool(call, tool), log_failure(call, failure), log_hook_dispatch(text)     one line each over what it has
+  (a unit spec in space/session asserts that Session answers all three protocols)
```

- **What callers write, before and after:**

```python
# before (harness/agent_tools/agent_tools.py:1091)
session.log.by(call.request.chat).tool(self.mcp_name, call.named_paths)
# after
session.log_tool(call, self.mcp_name)
```

- **What it buys:** Sharper module boundaries and Domain orientation. Four call chains into space/session's internals become three named operations. One protocol family replaces three separate descriptions, one of which had already drifted from the code. `Any` leaves `ToolCall.session`, *SessionOpener*, and twelve members of *ActionSession*.
- **Cost and risk:** About 12 files and 180 lines, almost all type declarations; cdd_guidance's Partition and Sketch actions change the name they import. Unit tier; the hook and MCP heavy specs once. No saved file or published name changes. Risk: a protocol can itself fall out of step, which is why the spec in space/session is part of the change.
- **Depends on / conflicts with:** Proposal 6 replaces `repo_path` with `checkout`; whichever is done second edits one line of *WorkedSession*. Proposal 7 changes *FidelityOutput* further.
- **Decision:** `[ ] approve  [ ] reject  [ ] change:`

---

## 3. Practices reach each other through named seams: a source-code module, a class-model seam, and *StoryTree*

- **Problem today:** Code that several practices need is an internal file of one practice. Stories (13 production files), BDD (6), DDD, two pattern packages, and space/session ([practice_session_output.py:11](C:\dev\abd-cdd-release-1-2-fixes\space\session\practice_session_output.py#L11), [session_file.py:14](C:\dev\abd-cdd-release-1-2-fixes\space\session\session_file.py#L14)) import `code_body`, `bracket_structure`, `call_graph`, `script_imports`, `production_code`, and `operation_metrics` from inside `clean_engineering/model/`, whose `__init__.py` exports nothing. UX keeps its own copy of Stories' rules for its nodes: which node types are steps and scenarios ([story_link.py:20](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ux\model\story_link.py#L20)), how a scenario is keyed, and which node a heading names (*StoryTargets*, [story_link.py:94](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ux\model\story_link.py#L94)); the Validate action copies ten of them again ([checked_graph.py:19](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\actions\validate\checked_graph.py#L19)). Inside Stories the type sets are now defined once ([graph_reading.py:33](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\graph_reading.py#L33); a second copy was removed while this was written, and every link writer is now handed the tree), but each link writer still walks the graph itself, and *StoryTree*, the class made to answer these questions, answers five ([graph_reading.py:257](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\graph_reading.py#L257)).
- **The judges disagreed on the shared module.** One proposed `practices/code_text` holding two files, with *CallGraph* left in Clean Engineering. Another proposed `practices/source_code` holding six, and a third suggested harness/graph. **Recommended:** `practices/source_code` with the six files, because BDD, the patterns, and space/session import `script_imports`, `production_code`, and *SourceText* too, and none of it is framework knowledge. It has the same standing as `sketch_document`: shared by practices, not a practice.
- **Class model, with the change marked:**

```diff
@@ (a) cdd_guidance/practices/source_code/       (new module, own card; depends on nothing in practices) @@
+  code_body.py          CodeLanguage, CodeSpelling, CodeBody, BraceCall, WrittenBlock, WrittenKey, InsideLines,
+                        PYTHON, TYPESCRIPT, JAVASCRIPT            (moved from clean_engineering/model/)
+  bracket_structure.py  BracketStructure                         (moved)
+  call_graph.py         CallGraph                                (moved)
+  script_imports.py     ScriptImports, ClassReference            (moved)
+  source_text.py        SourceText, SpanFailures, SpanCollaborators   (split out of operation_metrics.py)
+  test_files.py         TestFileName, is_spec_file, is_test_code, is_example_code   (was production_code.py)
@@ (b) cdd_guidance/practices/clean_engineering/model/__init__.py @@
-  (one empty line)
+  exports CleanEngineeringModel, Module, OoadClass, Operation, Parameter, Property, Invariant, Relationship,
+          CONSTRUCTOR_NAMES, MODULE_FUNCTION_HOLDER, marks_in, without_marks, module_path_in
+  (ddd and bdd import from here, never from base_class_model, operation, property, field_types)
@@ (c) cdd_guidance/practices/ddd/model/nodes.py @@
 class BoundedContext
+  notes, module_name, module_notes, group_notes                  (moved from MarkdownBoundedContext)
 class Aggregate
+  description, group, consumed_events, integrations              (moved from MarkdownAggregate)
@@ (c) cdd_guidance/practices/ddd/model/sketch/ @@
+  take_sketch_line, load_sketch, sketch_lines, read_sketch_lines, SKETCH_* constants   (moved from markdown/nodes.py)
@@ (c) cdd_guidance/practices/ddd/model/drawn/drawn_map.py @@
-  imports MarkdownBoundedContext, MarkdownIntegration
+  bounded_context_type = BoundedContext
@@ (d) cdd_guidance/practices/stories/model/story_tree.py     (StoryTree moves to its own file) @@
 class StoryTree(stories: PracticeReading)
   epic_of(node), sub_epics(epic), stories_under(epic), scenarios(story), steps(scenario)
+  STEP_TYPES, EPIC_TYPES, KEY_SEPARATOR          the one definition (UX's and Validate's copies removed)
+  every_step(), examples(), examples_of_file(file)
+  scenario_of(step), story_of(node), background_steps(story), area_of(node)
+  step_body(step), step_text(step), step_phase(step), steps_saying(text)
+  key_of(node)                                   (moved from ux story_link.key_of)
+  node_written_at(kind, file, heading, key)      (moved from ux StoryTargets)
@@ (d) cdd_guidance/practices/stories/model/graph_reading.py, modelled_areas.py, term_links.py @@
-class StoryLinks(stories, clean, tree)           examples, _step_body, ...
+class StoryLinks(tree, clean)
-class ExampleObservations(stories, tree)         examples, _step_body, _givens_of, _backgrounds_of
+class ExampleObservations(tree)
-class ModelledAreas(stories, tree)               _area_of
+class ModelledAreas(tree)
-class TermLinks(stories, model, tree)            _examples_by_file
+class TermLinks(tree, model)
@@ (d) cdd_guidance/practices/stories/rules/scenarios.py @@
+class StepRule(PracticeGraphRule)                keyword(), text(), phase(), is_a(phase)
-  _keyword, _text, _phase, _parent_story, _background_steps      (module functions)
@@ (d) cdd_guidance/practices/ux/model/story_link.py @@
-  STEP_TYPES, _NODE_TYPES, key_of, _story_name, _ancestor, _parent
-class StoryTargets(graph)
 class StoryLink(kind, key, node)
-  resolved_on(graph, written_in), _candidates(graph)
+  resolved_in(story_tree, written_in)
@@ (d) cdd_guidance/practices/ux/model/graph_reading.py, explorer_tree.py @@
 class LinksAcrossPractices
+  story_tree: StoryTree | None                   found once, handed to the three link builders
-class ExplorerTree(screens)                      story_tree read through node.practice.reading
+class ExplorerTree(screens, story_tree)
@@ (e) cdd_guidance/practices/stories/stories.py @@
 class Stories
+  desktop_story_tests(project) -> list[DesktopStoryTest]    story, file, scenarios with each step's lines below it
@@ (e) cdd_guidance/desktop_walk/desktop_walk.py @@
-  imports stories.model.markdown.nodes, .markdown.scenario_file, .story_file, .story_map_files
+  imports cdd_guidance.practices.stories.stories
 class DesktopScenario
-  read_steps(steps, lines)
+  (steps made in the constructor from the Stories scenario; published fields unchanged)
@@ (f) cdd_guidance/practices/clean_engineering/reading/ (after proposal 1) @@
 class CodeIndex
+  file(relative) -> CodeFile                     the one seam other practices ask
+class CodeFile                                   class_named(name), function_named(name),
+                                                 members_called_in(span: CodeSpan), constructors_of(class_name)
+class CodeSpan                                   text, owner class or none, known locals
-class ClassesInReach, ImportedClasses            (-> CodeFile)
-class CallerBody                                 (-> CodeFile.members_called_in)
@@ (f) cdd_guidance/practices/bdd/model/graph_reading.py, nodes.py @@
-class ImportedCode, ReachedMembers; reach_of(text) -> Reach     (ObservationLinks asks CodeFile)
```

- **What callers write, before and after:**

```python
# before (in Stories, BDD, a pattern, and space/session)
from cdd_guidance.practices.clean_engineering.model.code_body import CodeBody
from cdd_guidance.practices.clean_engineering.model.production_code import is_test_code
# after
from cdd_guidance.practices.source_code import CodeBody, is_test_code

# before (ux/model/story_link.py)
StoryTargets(graph).node_at(link, written_in)
# after
story_tree.node_written_at(link.kind, file, heading, link.key)
```

- **What it buys:** Sharper module boundaries and One object model. Stories' code formats no longer load the Clean Engineering model to parse a brace. Clean Engineering's class model gets a seam of 13 names where DDD imports 13 internal files and BDD 10 today. DDD's drawn and sketch formats stop importing its markdown format. UX loses about 190 lines that restate Stories' rules, Validate loses its copy of ten node types, and Stories loses three copies of the walk from a step to its story. Desktop walk stops importing four files from inside Stories' model. Part (f) removes about 400 lines across Clean Engineering and BDD and makes an `invokes` edge mean the same member whichever practice draws it.
- **Cost and risk:** (a) 6 files moved, one split, about 75 import lines, one card. (b) one `__init__.py` and about 40 import lines; check import time and that it adds no cycle with `clean_engineering.py`. (c) 4 files, 250 lines moved; `markdown/nodes.py` is 778 lines and was read by the judge only in outline, so read it fully first. (d) 12 files, 300 lines moved and 200 removed; *StoryTree* grows from 5 to about 17 public operations, so measure Stories' `deep-module` share afterwards and split the tree into parts it holds if it fails; the moved code must keep reading facts and edges, because rules run on graphs read back from `graph.json`. (e) 3 files, 80 lines. (f) 7 to 9 files; **the riskiest part of the whole document**: three sets of resolution rules were tuned separately, so one resolver changes some edges, and each changed edge needs a decision. Do (f) as Flow A: compare the `invokes` edges of this repository's whole graph before and after, and review every difference. Unit tier after each part; heavy graph specs for (d) and (f).
- **Depends on / conflicts with:** (f) needs proposal 1. Proposal 8 uses (a) to remove space/session's imports. Proposal 21 reshapes *ScenarioFileReading*, which (e) wraps, so do (e) after 21 or accept one more edit. The ignored pattern `oss_portal_domain_driven` imports some moved files and gets the import lines only.
- **Decision:** `[ ] approve  [ ] reject  [ ] change:`

---

## 4. One board element id, one whiteboard reader, one draw.io document, one record of where a file is published

- **Problem today:** Three practices each compute a board element's id as a cut SHA-1, with two lengths ([stories whiteboard/nodes.py:44](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\whiteboard\nodes.py#L44), [ux whiteboard/nodes.py:76](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ux\model\whiteboard\nodes.py#L76), [whiteboard_class_model.py:78](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\whiteboard\whiteboard_class_model.py#L78)), and each splits ids apart again by hand ([stories whiteboard/nodes.py:227](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\whiteboard\nodes.py#L227)). The Files app reads the `.whiteboard` file's stored fields again in TypeScript ([whiteboard-canvas.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\whiteboard-canvas.ts)). Reading and writing a draw.io file, and keeping the places a person gave its cells, is written three to five times ([clean_engineering drawio_page.py:20](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\drawio\page\drawio_page.py#L20), [stories drawio/nodes.py:240](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\drawio\nodes.py#L240), [ux drawio/nodes.py:90](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ux\model\drawio\nodes.py#L90), and two more in the catalog generator and the Render action), with three failure classes and two rectangle types (*Geometry* and *Box*). *BoardLinks* ([whiteboard.py:459](C:\dev\abd-cdd-release-1-2-fixes\harness\whiteboard\whiteboard.py#L459)) and *PublishedLinks* ([versions.py:29](C:\dev\abd-cdd-release-1-2-fixes\harness\design_canvas\versions.py#L29)) keep the same record, and *CanvasVersions* passes a version's number into five operations ([versions.py:79](C:\dev\abd-cdd-release-1-2-fixes\harness\design_canvas\versions.py#L79)).
- **Corrected from the judge's report:** the element kinds *Shape*, *Section*, *Label*, and *Arrow* are not private classes. They are ordinary classes in `whiteboard.py` that the package's `__init__.py` leaves out; there is also a *Block* base under *Shape* and *Section*.
- **The judges disagreed on three shapes.** (1) The element id: a `board_path()` / `board_key` pair on *WhiteboardNode*, a `Whiteboard.key(*names)` function, or an *ElementId* value. **Recommended:** *ElementId*, because it removes the hashing and also the four places that split an id back into role and parts. Each practice keeps its key length as a class attribute (Clean Engineering 12, the others 10), so no published board is redrawn. (2) The draw.io names: *Drawing* / *Page* / *Cell*, or *DrawioFile* / *DrawioPage* / *DrawioCell*. **Recommended:** the second set; `Page` and `Cell` say nothing outside their module. (3) How much of Clean Engineering's page moves: all of it, or only geometry. **Recommended:** geometry and style first, with Clean Engineering's edge routing kept in a class of its own over the framework page until its eleven scanners have been moved.
- **Class model, with the change marked:**

```diff
@@ (a) harness/whiteboard/whiteboard.py @@
+class ElementId(role, *parts)                    str(), role, parts
+  ElementId.of(role, *names, length)             the one hash of a node's names
 class BoardElement
-  id: str
+  id: ElementId
 class WhiteboardNode
   board_box(), board_elements(), board_shape(id, ...)
+  KEY_LENGTH                                     set by each practice: 10, or 12 for Clean Engineering
@@ (a) stories, ux, clean_engineering whiteboard adapters @@
-  board_key bodies, _key(*names), inline hashlib.sha1 calls (five), element.id.split(".") (four)
@@ (b) harness/whiteboard/whiteboard.py @@
 class BoardElement
-  shape(id, box, ...), section(id, box, ...), words(id, corner, ...), arrow(id, ...)     (factories)
+  Shape, Section, Label, Arrow                   exported and built directly
 class Whiteboard
-  sections, shapes, labels, arrows -> List[BoardElement]
+  sections -> List[Section], shapes -> List[Shape], labels -> List[Label], arrows -> List[Arrow]
+  drawn_over(previous_text) -> str               keep_places and save in one call (three practices repeat the lines)
+  published through @language_adapter            its elements as data fields
@@ (b) harness/files_app/app/files/whiteboard-canvas.ts @@
-  WhiteboardCanvas.from(text) reads elements[*].type, x, y, w, h, from, to, dash, kind itself
+  WhiteboardCanvas reads the generated WhiteboardData; keeps only the frame and the side an arrow leaves from
@@ (c) harness/drawio/                           (new framework module beside harness/whiteboard) @@
+class DrawioFile                                 from_text(text) raises UnreadableDrawio; pages; page(name);
+                                                 add_page(name, page_id); keep_places(previous); save()
+class DrawioPage                                 cells, cell(id), add(cell), positions()
+class DrawioCell                                 id, label, style: CellStyle, box: Box | None, source, target, link
+class CellStyle                                  value(key), number(key), role    (moved from ux/model/drawio/nodes.py)
+class UnreadableDrawio(ValueError)               (replaces DrawIOParseError, ux UnreadableDrawio, UnreadableSource here)
@@ (c) stories/model/drawio/nodes.py @@
-class DrawIOParseError
-class _DrawIOPage, _KeptPlaces; _drawn_geometries()
@@ (c) ux/model/drawio/nodes.py @@
-class CellStyle, UnreadableDrawio; _diagram_of, _page_named
@@ (c) clean_engineering/model/drawio/page/drawio_page.py @@
 class DrawioPage
-  pages_in(mxfile), whole(text), cell(id), positions()
+class ClassDiagramPage(page: DrawioPage)         edges_by_ends, kind_of, segments  (the routing that is its own)
-  cell_box(cell), style_value(style, key), style_number(style, key)       (module functions)
@@ (d) harness/whiteboard/whiteboard.py  and  clean_engineering/model/diagram/geometry.py @@
 class Box(x, y, w, h)
   holds(other)
+  overlaps(other), shifted(right, down), moved_to(left, top), clear_gap_to(other), center
-class Geometry(NamedTuple)                       (-> Box)
@@ (e) harness/installation/                     (beside JsonFile) @@
+class PublishedLinks(record: JsonFile)           of(name), named_at(url), record(name, url), rename(name, new)
@@ (e) harness/whiteboard/whiteboard.py @@
-class BoardLinks(folder)                         beside(file), of(file), file_published_to(url), record(file, url)
 class Whiteboard
+  links_beside(file) -> PublishedLinks
@@ (e) harness/design_canvas/versions.py @@
-class PublishedLinks                             (moved to harness/installation)
+class CanvasVersion                              number, folder, link, title(name), publish_at(url), release(name)
 class CanvasVersions(root)
-  numbers, latest -> int, folder(n), start_next() -> int, release(n, name), working() -> int,
-  unpublished() -> int, title(n, name), link(n), record_link(n, url)
+  latest -> CanvasVersion | None; working(), unpublished(), start_next() -> CanvasVersion
@@ (e) space/session   FileEntry @@
+  link, published_kind: "whiteboard" | "design canvas" | ""     (the Files app stops working it out from the path)
@@ (f) harness/design_canvas/canvas.py @@
 class DesignCanvas(title, project?)
   add_page, placed, files, write
-  add_board(name, board: CanvasBoard, text)
+  add(artboard: Artboard, at: CanvasBoard)
-  artboards_in(folder), holds(name), size_of(name), stylesheets_linked_by(names)
+class CanvasProject(folder)                      artboards_in, size_of (None when not held), stylesheets_linked_by
 class Artboard
+  name, stem                                     (stem() was a module function)
@@ (f) harness/design_canvas/fixture_bar.py, look.py  ->  cdd_guidance/practices/ux/model/claude_design/ @@
-  FixtureScreen, ScenarioSource, bar(), methods(); LOOK, FONTS, BACKGROUND
+  fixture_screen.py: FixtureScreen, ScenarioSource (bar and methods become private); look.py   (moved; CardLook stays)
```

- **What callers write, before and after:**

```python
# before (three whiteboard adapters)
key = hashlib.sha1("/".join(reversed(names)).encode("utf-8")).hexdigest()[:KEY_LENGTH]
board.keep_places(Whiteboard.from_text(previous)); text = board.save()
canvas.folder(canvas.working())
# after
key = ElementId.of("story", *names, length=self.KEY_LENGTH)
text = board.drawn_over(previous)
canvas.working().folder
```

- **What it buys:** Sharper module boundaries, One object model and Resource orientation. One hash and one id type where there are five hash calls and four splits. One reader of a `.whiteboard` file where Python and TypeScript each have one. About 450 lines of draw.io handling in the practices become about 300 in one framework module, as harness/whiteboard already does for boards. One rectangle. One record of published addresses, and a canvas version that is an object. Practice-specific canvas code (a screen that plays a story's scenario fixtures) leaves the framework. harness/whiteboard's seam falls from 36 of 54 methods to about 15 of 50, under the 35% limit.
- **Cost and risk:** (a) 4 files, 60 lines. (b) 14 files, 450 lines. (c) one new module of about 300 lines, 25 files touched, 450 lines removed, one new card. (d) the layout code (`class_layout.py`, 927 lines) uses *Geometry* positionally in places, so the rename is a mechanical pass with the layout specs and the heavy render spec. (e) 12 files, 300 lines. (f) 9 files, 250 lines, mostly moved. Unit tier after each part; heavy render specs for (b) to (d). **Saved files:** element ids are how a board already published in Claude is updated in place; if *ElementId* produces a different hash for an existing node, the next render redraws every element and loses where people moved them. (a) and (b) are Flow A at the store: render onto a real published board and compare before the unit specs are trusted. `versions.json` and `whiteboards.json` keep their shape. The UX recipe `story_canvas.md` is an API agents follow from markdown, so the recipe and the classes in (e) and (f) change in one commit. Agents' saved build scripts in closed sessions import `harness.design_canvas.fixture_bar` and stop running. harness/design_canvas will still fail `deep-module` after (f) (about 17 of 26), because a small module whose purpose is a file-layout API has little to hide; see the open questions.
- **Depends on / conflicts with:** (a) first. Proposal 12's second pass (not recommended) would rely on (c). Stories' cells sit inside a `UserObject` when linked; *DrawioCell* must cover both forms.
- **Decision:** `[ ] approve  [ ] reject  [ ] change:`

---

## 5. Git facts have one reader, a checkout is one class, and a branch answers where it is checked out

- **Problem today:** Eight questions about a repository each choose, at the place they are asked, between reading the `.git` files and running git ([repo.py:159](C:\dev\abd-cdd-release-1-2-fixes\space\repo\repo.py#L159) to [repo.py:233](C:\dev\abd-cdd-release-1-2-fixes\space\repo\repo.py#L233), [repo.py:330](C:\dev\abd-cdd-release-1-2-fixes\space\repo\repo.py#L330), [worktree.py:129](C:\dev\abd-cdd-release-1-2-fixes\space\repo\worktree.py#L129)). The framework cannot use *GitFolder* because it lives in space/repo ([git_folder.py:15](C:\dev\abd-cdd-release-1-2-fixes\space\repo\git_folder.py#L15)), so four places in harness read `.git` by hand ([cdd_home.py:376](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\cdd_home.py#L376), [server_lanes.py:149](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\server_lanes.py#L149), [mcp_daemon.py:182](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_daemon.py#L182), and the function `checkout_holding` at [claude_chat_process.py:57](C:\dev\abd-cdd-release-1-2-fixes\harness\process\claude_chat_process.py#L57), which *ChatPointer* now shares; the judges counted five, and two were joined while this was written). space/repo's *GitFolder* answers the same two questions (`from_inside`, `main_checkout`), so they are written once on each side of the boundary. *Repo* and *Worktree* both stand for one checkout ([repo.py:78](C:\dev\abd-cdd-release-1-2-fixes\space\repo\repo.py#L78), [worktree.py:54](C:\dev\abd-cdd-release-1-2-fixes\space\repo\worktree.py#L54)). `Branch.is_checked_out` means "in the checkout this object was made from" ([repo.py:474](C:\dev\abd-cdd-release-1-2-fixes\space\repo\repo.py#L474)), `default_branch` is a string ([repo.py:186](C:\dev\abd-cdd-release-1-2-fixes\space\repo\repo.py#L186)), and four places commit and push with different conditions, so *TicketCheckout* works the answers out again ([ticket_checkout.py:227](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\ticket_checkout.py#L227), [ticket_checkout.py:259](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\ticket_checkout.py#L259)).
- **The judges proposed overlapping shapes.** One moved *GitFolder* down and added a small `Checkout(folder)` in harness/git. One added a *GitFacts* interface in space/repo. One said *Repo* is the checkout and removed *Worktree*. **Recommended:** harness/git owns reading (*GitFacts*, *GitFolder*, *AskedOfGit*, and *Checkout*, which answers which checkout holds a folder and whether it is the main one); space/repo's *Repo* holds its *Checkout* and adds everything that changes a repository. That gives one reader for both layers and no second class meaning "a checkout that can be changed".
- **Class model, with the change marked:**

```diff
@@ (a) harness/git/git_facts.py                 (new; standard library and Git only) @@
+class GitFacts (interface)                     head_branch, is_on_branch, head_commit, has_ref(ref), branch_names,
+                                               has_remote(name), worktrees, common_folder
+class GitFolder(checkout) implements GitFacts  (moved from space/repo/git_folder.py, unchanged)
+class AskedOfGit(git) implements GitFacts      the git commands written inline in Repo, Refs, Worktrees today
@@ (a) harness/git/checkout.py                  (new) @@
+class Checkout(folder)
+  Checkout.holding(folder) -> Checkout         the checkout holding a folder, else the folder
+                                               (over GitFolder.from_inside, which space/repo has today)
+  is_main, is_linked_worktree                  its .git is a directory, or a file
+  branch: str
+  facts: GitFacts                              GitFolder when readable, else AskedOfGit; chosen again when a
+                                               plain folder becomes a repository
@@ (a) harness/mcp, harness/agent_tools, harness/process @@
-  CddHome._branch_of, ServerLanes._is_in_main_checkout, ServedCheckout.keep_pinned_current's .git read,
-  checkout_holding(folder) in claude_chat_process.py (used by ChatPointer too)     (-> Checkout)
@@ (a) space/repo/repo.py @@
 class Repo(root)
+  checkout: Checkout
-  readable_folder -> GitFolder | None
   branches, current_branch, is_on_branch, current_commit, has_origin     (each one line: self.checkout.facts.X)
 class Refs
   has(ref)                                     (one line over facts.has_ref)
@@ (a) space/repo/mock_repo.py @@
 class MockRepo(Repo)
+  supplies a GitFacts answered from MockGit    (replaces eight overridden properties)
@@ (b) space/repo/repo.py @@
 class Repo
-  default_branch: str
+  default_branch: Branch
 class Branch(repo, name)
-  is_checked_out                               true only in the checkout it was made from
+  is_checked_out                               true when any checkout has it
+  is_checked_out_here                          the old meaning, for the two callers that need it
+  linked_worktree -> Repo | None               (moved from kanban's own_worktree_of)
   checkout -> Repo | None
-  save(commit_message)
+  save(commit_message, push=True)              the one "commit everything here and push"
 class Publishing
   push_work()                                  (calls current_branch.save)
@@ (b) space/kanban/ticket_checkout.py @@
-def own_worktree_of(branch)
 class TicketCheckout
-  _commit_and_push(branch, leaving)            (-> Branch.save)
-  _work_from_main_clone()                      (Branch operations already run in the main clone)
-  _checked_out_work_branch()                   (-> branch.checkout is not None)
@@ (c) space/repo/worktree.py, repos.py, new_repository.py @@
-class Worktree(worktrees, path, branch_name)   path, branch, close(commit_message); _fetch_pull, _pull_fetched, _catch_up
 class Repo
+  is_main_clone                                (= checkout.is_main)
+  catch_up_with_origin()                       (moved from Worktree._fetch_pull / _pull_fetched)
+  close(commit_message)                        (moved from Worktree.close)
 class Worktrees(repo)
-  __iter__ -> Worktree, of(branch) -> Worktree | None, open(branch) -> Worktree, listing() -> [(Path, str)]
+  __iter__ -> Repo, of(branch) -> Repo | None, open(branch) -> Repo          (listing becomes private)
 class SiblingRepo(folder)
-  runs its own Git
+  holds a Repo
 class NewRepository(root)
-  runs its own Git; answers sentences
+  takes a Repo; answers a record (created or already there, branch, ignored lines) that the tool words
```

- **What callers write, before and after:**

```python
# before (ticket_checkout.py)
default = self._repo.branch_named(self._repo.default_branch)
tree = own_worktree_of(branch)
# after
default = self._repo.default_branch
tree = branch.linked_worktree
```

- **What it buys:** Sharper module boundaries, One object model and Resource orientation. One reader of git's facts for the framework and for space/repo; four hand-written readers and eight per-question choices go. One class for a checkout where there are four partial ones (*Repo*, *Worktree*, *SiblingRepo*, *NewRepository*). `ticket_checkout.py` loses about 60 lines because *Branch* answers what it re-derives three times.
- **Cost and risk:** (a) 13 files, about 200 lines. (b) 6 production files, 150 lines changed. (c) 8 to 10 files, 300 to 400 lines. Unit tier after each part; **the heavy tier is required**: this is real git, and the area decision record 0005 already flagged. Risks: (b) changes what `is_checked_out` means, and `ticket.branch` is a published data field the chat bar and the Close dialog read, so check both readers. The four save operations differ on purpose (the default branch is committed and not pushed); each difference must stay as a named argument, or a close could push main. (c) a *Worktree* today also covers a checkout whose branch is detached (`branch is None`); every such test needs a deliberate replacement, and *ServedCheckouts* must not start git for every listed worktree. (a) harness/process is documented as depending on nothing, and `claude_chat_process.py` is imported inside Claude Code's ten-second start window; if the extra import matters, it keeps its one-line reader.
- **Depends on / conflicts with:** Do before 6, which holds a *Repo* and a *Branch* on the session. (c) only after (b). The root card and AGENTS.md disagree on whether harness may import space; see the open questions.
- **Decision:** `[ ] approve  [ ] reject  [ ] change:`

---

## 6. The session record has typed fields with one writer each, and a session knows its one checkout

- **Problem today:** `SessionRecord.fields` is a bare dict and `save_fields(**values)` takes any key ([session_record.py:38](C:\dev\abd-cdd-release-1-2-fixes\space\session\session_record.py#L38), [session_record.py:54](C:\dev\abd-cdd-release-1-2-fixes\space\session\session_record.py#L54)). Six owners write it by string key, among them the board ([ticket.py:864](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\ticket.py#L864), [ticket_checkout.py:122](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\ticket_checkout.py#L122), [ticket_checkout.py:161](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\ticket_checkout.py#L161)), and space/session reads back `branch` and `worktree` that only the board writes ([session.py:511](C:\dev\abd-cdd-release-1-2-fixes\space\session\session.py#L511), [session_roots.py:52](C:\dev\abd-cdd-release-1-2-fixes\space\session\session_roots.py#L52)). A practice's state is split over two keys, `practices` and `outputs` ([practice_session_output.py:92](C:\dev\abd-cdd-release-1-2-fixes\space\session\practice_session_output.py#L92), [practice_session_output.py:137](C:\dev\abd-cdd-release-1-2-fixes\space\session\practice_session_output.py#L137)). `repo_path` is written ([session_record.py:73](C:\dev\abd-cdd-release-1-2-fixes\space\session\session_record.py#L73)) and no production code reads it (checked). A *Session* is also constructed empty and filled from outside in an order a comment protects ([sessions.py:298](C:\dev\abd-cdd-release-1-2-fixes\space\session\sessions.py#L298), [sessions.py:310](C:\dev\abd-cdd-release-1-2-fixes\space\session\sessions.py#L310)), and *SessionRoots* answers four questions about a session by taking it as a parameter ([session_roots.py:30](C:\dev\abd-cdd-release-1-2-fixes\space\session\session_roots.py#L30)).
- **The two judges disagreed on who owns the board's facts.** The kanban judge moved stage, stage mark, branch, worktree, and assigned chat into two new parts of the session. The session judge kept the board as their owner, in a named section of the record. **Recommended:** a fact lives with the module that reads it. Branch, worktree, and assigned chat become the session's (*SessionCheckout*), because space/session already reads two of them. Stage and stage mark stay the board's, written through `record.extra("ticket")`, because nothing in space/session reads them. The two judges also both used the name `session.checkout`, one for a *Repo* and one for the new part; here it is the part, which holds the *Repo*.
- **Class model, with the change marked:**

```diff
@@ (a) space/session/session_record.py @@
 class SessionRecord
-  fields -> dict
+  fields: SessionFields
-  save_fields(**values: object)                (public; called by six owners)
+  _save_fields(...)                            (private to the module; each owner changes its own typed part)
+  extra(owner) -> OwnedFields                  one named part per outside owner; extra("ticket") is the board's
   save()
-    writes repo_path
+class SessionFields                            name, title, scope, workpath, tags, overlays, parent, pulled_out,
+                                               branch, worktree, chat, guidance: SelectionFields,
+                                               practices: dict[str, PracticeFields]
+class PracticeFields                           enabled, root, fidelities: dict[str, FidelityFields]
+class FidelityFields                           formats: list[str], roots: list[str], file_names: dict[str, str]
@@ (a) space/session/session_checkout.py       (new part, session.checkout) @@
+class SessionCheckout(session)                 the one reader and writer of "branch", "worktree", "chat"
+  repo: Repo, root: Path                       the session's one project: its own worktree, else its sessions'
+  branch: Branch                               (moved from TicketCheckout._found_branch; one name pattern, not two)
+  candidate_branches                           (moved from TicketCheckout)
+  own_worktree: Repo | None                    (replaces own_worktree_of in kanban and in SessionRoots)
+  assigned_chat, assign_chat(chat)             (moved from TicketCheckout)
+  record_opened()                              (replaces save_fields(branch=, worktree=))
@@ (a) space/session/practice_session_output.py @@
 class PracticeSessionOutput
-  saved -> dict, save(**values), chosen_outputs -> dict, _save_chosen_outputs(dict)
-  keep_fidelity_root(name, root), keep_fidelity_roots(name, roots)
+  (reads and saves its own PracticeFields)
 class FidelitySessionOutput
+  keep_roots(roots)                            (saves its own FidelityFields)
@@ (a) space/session/session_hierarchy.py @@
 class SessionHierarchy
+  ancestors, can_take_parent(other)            (moved from TicketTree)
@@ (a) space/kanban/ticket.py, ticket_checkout.py, ticket_tree.py @@
 class StageMarks(ticket)
-  reads and writes ticket.session.record.fields["stage" | "stage_mark"]
+  reads and writes ticket.session.record.extra("ticket")
+class StageMark (enum)                         DONE, IN_PROGRESS  (replaces the bare strings)
-def own_worktree_of(branch)
 class TicketCheckout
-  _recorded, _found_branch, candidate_branches, assigned_chat, assign_chat(chat)
   work_branch, chat, close_choices, open, save_work, leave_branch     (read session.checkout)
 class TicketTree
-  ancestors, can_be_child_of(parent)
   is_stacked, parent_choices, furthest_back_child_stage
@@ (b) space/session/session.py @@
-class Session(sessions)                        name, record_folder, work_folder, workpath all set from outside
+class Session(sessions, record_folder)         name read from the folder
-  repo, repo_path
+  checkout: SessionCheckout
+  placed() -> Session                          derives checkout, work folder, workpath in the one right order
   branch                                       (answers checkout.branch.name)
   context_config                               (derived from checkout; made again when the checkout changes)
   handoffs, progress_cache                     (always present)
@@ (b) space/session/sessions.py @@
 class HeldSessions
   load(folder)                                 (= at(folder).placed())
-  placed(session)
@@ (b) space/session/session_roots.py @@
-class SessionRoots                             root_of(session), checkout_of(session), own_worktree_of(session),
-                                               work_folder_of(session), in_checkout(checkout, path), worktree_of(name)
+class CheckoutWorktrees                        of_branch(name) -> Path | None, in_checkout(checkout, path)
```

- **What callers write, before and after:**

```python
# before (space/kanban/ticket_checkout.py:161 and space/kanban/ticket.py:864)
self._ticket.session.record.save_fields(branch=self.branch.name, worktree=self.worktree)
self._ticket.session.record.save_fields(**{_STAGE_FIELD: stage.name, _STAGE_MARK_FIELD: mark})
session.repo_path
# after
self._ticket.session.checkout.record_opened()
self._marks.enter(stage, StageMark.IN_PROGRESS)        # StageMarks writes record.extra("ticket")
session.checkout.root
```

- **What it buys:** Sharper module boundaries, One object model, Resource orientation, Domain orientation. Seven lines in space/kanban that read or write the session's dict by key become calls on two named objects. The branch name pattern and "the ticket's own worktree" are each decided once, not twice. A practice's saved state has one typed entry, not two dicts. A session is valid from the moment it is constructed, so the comment that protects an assignment order goes with the order.
- **Cost and risk:** About 22 production files and 650 lines; `session_spec.py`, the root and worktree specs, `kanban_spec.py`, and two kanban heavy specs follow. Unit tier, then the session and kanban heavy specs with a ticket that has its own worktree. **Saved files:** every ticket on every checkout has a `session.json` in today's shape, the record is committed on main, and the stable lane's older server reads it. Recommended: the keys `stage`, `stage_mark`, `chat`, `branch`, and `worktree` stay where they are on disk, so only `outputs` merged into `practices` is upgraded, once, on read. Even so the upgrade must be released to both lanes together, or an older server will not find roots saved in the new shape. **This is the proposal with the highest migration cost.** Other risks: a ticket moved before `stage` was recorded is read from its log ([ticket.py:835](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\ticket.py#L835)); that fallback stays in *StageMarks*. *SessionRoots* caches the worktree listing for two seconds; one owner needs one caching rule. Making the session's own checkout its one project changes the paths a ticket in a sibling worktree names, and which `.context/config.json` it reads; that is the intended fix and also a behaviour change.
- **Depends on / conflicts with:** After 5 (*Repo* and *Branch* shapes). Before 7, 13, 14, and 20. `harness/guidance_actions/guidance_actions.py:668` dumps `record.fields` as JSON and needs the typed fields to write themselves as a dict.
- **Decision:** `[ ] approve  [ ] reject  [ ] change:`

---

## 7. Declared outputs are declarations; the session answers what is on disk

- **Problem today:** *DeclaredOutputs* ([declared_outputs.py:98](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\declared_outputs.py#L98)) is both a fidelity's declared path patterns and a view of the session's files: `output_paths`, `files`, and `has_output` ([declared_outputs.py:183](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\declared_outputs.py#L183)) only forward to space/session's *WrittenFiles*, which reads the declarations back. Thirteen production callers use the first door and others the second. `PracticeSessionOutput.of_fidelity` makes a new *FidelitySessionOutput* on each call while each fidelity keeps another ([guidance.py:439](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\guidance.py#L439)). The Render action then decides where a render is saved in about 230 lines that redo parts of *DeclaredOutputs* and *DeclaredFile*, and "the folder up to the first pattern" is written four times.
- **The judges pulled in two directions.** One made *DeclaredOutputs* declarations only and moved `saved_beside` to the session. Another moved Render's placement logic into *DeclaredOutputs*. The session judge offered either. **Recommended:** split by what the answer needs. What can be answered from the patterns alone (the name a render gets, the declared place for a source) belongs to the declarations, in a part they hold. What needs the session's roots or the disk (`output_paths`, `files`, `has_output`, `saved_beside`, `files_to_review`) belongs to *WrittenFiles*.
- **Class model, with the change marked:**

```diff
@@ harness/guidance/declared_outputs.py @@
 class DeclaredOutputs
-  __init__(fidelity, outputs)
+  __init__(outputs)                             no fidelity: declarations only
   includes(path, format), code_folders, file_name_beside(source, format), file_beside(source, format)
+  declared_files(format) -> list[DeclaredFile]  (WrittenFiles stops rebuilding them from raw outputs)
+  paths_in(format) -> list[str]                 the one normalisation of a str or list declaration
+  placement: RenderPlacement                    a part it holds, so DeclaredOutputs does not grow
-  output_paths(), files(), has_output()         (-> fidelity.session_output.written)
-  saved_beside(source, format)                  (-> WrittenFiles.saved_beside)
-  files_to_review()                             (-> WrittenFiles.files_to_review)
+class RenderPlacement(declared)
+  place_of(sources, source_format, format) -> RenderPlace | None
+                                                (moved from RenderedFile.from_sources, beside_itself and
+                                                 RenderedCode._counterpart_of, _named_for_source, _beside_source)
+  place_for_scope(scope, format) -> str         (moved from RenderedFile.from_graph)
+class RenderPlace                               the declared path or paths, and whether each is the fidelity's own file
 class DeclaredFile
   pattern, parts_of(path), named_with(parts), names_one_path, start_of(path)
+  fixed_folder                                  (replaces WrittenFiles._fixed_folder, ProposedRoots._fixed_head, and two more)
+  own_name_of(source) -> str | None             (moved from rendered_code.own_name, _says_where_name_ends)
+  filled_with(names) -> str                     (moved from RenderedCode._section_file)
@@ harness/guidance/worked_session.py @@
 class FidelityOutput(Protocol)
+  written: WrittenOutput                        output_paths, files, has_output, saved_beside, files_to_review
+class NoSessionOutput                           answers empty for a fidelity that works in no session
@@ harness/graph/saved_graph.py @@
 class SavedGraph
+  scope_name(practice_key) -> str               (moved from RenderedFile._scope_of)
@@ space/session/practice_session_output.py @@
 class PracticeSessionOutput(guidance, session)
+  fidelities -> list[FidelitySessionOutput]     held, made once
   of_fidelity(fidelity)                         (answers the held one; today it makes a new one per call)
+  holds(file) -> bool
 class WrittenFiles(output)
   output_paths(), files(), holds(file), every_file(), has_output(), ...
+  saved_beside(source, format), files_to_review()
@@ cdd_guidance/actions/render/rendered_file.py, rendered_code.py @@
 class RenderedFile
-  from_sources(...), beside_itself(...), from_graph(...), _scope_of(...)
 class RenderedCode
-  _named_for_source, _counterpart_of, _beside_source, _section_file
-def own_name(), _says_where_name_ends()
```

- **What callers write, before and after:**

```python
# before
fidelity.declared.output_paths()
fidelity.declared.saved_beside(source, "drawio")
# after
fidelity.session_output.written.output_paths()
fidelity.session_output.written.saved_beside(source, "drawio")
```

- **What it buys:** Sharper module boundaries and One object model. One way to ask what a fidelity has written. harness/guidance stops forwarding into space/session through an object that claims to be a declaration. About 150 lines of placement leave the Render action for the class that owns the patterns. One *FidelitySessionOutput* per fidelity, held once.
- **Cost and risk:** About 18 production files and 350 lines, plus about 40 spec lines; `declared_outputs_spec.py`, `render_spec.py`, `rendered_code_spec.py`. Unit tier, then the heavy render spec that saves beside a source. No saved file or published name changes: the session judge also proposed renaming `enabled` / `enable` to `is_on` / `turn_on`, which would rename a published tool; recommended here is the cheaper option, keeping the published names and renaming only the three private spellings to match them. Risks: `PracticeGuidance.work_in` relies on `of_fidelity` during construction, so the held outputs must not ask a fidelity for its output before `work_in` has given it. The five placement cases listed in `rendered_code.py`'s docstring were each added for a reported defect; every one needs its spec case kept green through the move. The framework must not learn about Clean Engineering's banner lines; cutting text into sections stays in the action.
- **Depends on / conflicts with:** After 6 (typed *PracticeFields*). Proposal 11 builds its typed render result on the *RenderPlace* made here. Proposal 2 edits the same protocols.
- **Decision:** `[ ] approve  [ ] reject  [ ] change:`

---

## 8. Practice knowledge leaves the framework and the session module

- **Problem today:** The three lowest framework modules that read a toolset know what a practice is: harness/markdown reads fidelity blocks and names Stories' files, harness/agent_tools has `is_part_of_practice` ([agent_tools.py:669](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\agent_tools.py#L669)) and tests for a member named `instructions`, and harness/installation holds the file names of a practice's and a fidelity's skills and rules ([files.py:102](C:\dev\abd-cdd-release-1-2-fixes\harness\installation\files.py#L102)). harness/graph lists practices' node types and edge kinds, and decides three times which fields of a schema type are relationships. space/session imports two practices and copies their literals ([practice_session_output.py:11](C:\dev\abd-cdd-release-1-2-fixes\space\session\practice_session_output.py#L11), [practice_session_output.py:20](C:\dev\abd-cdd-release-1-2-fixes\space\session\practice_session_output.py#L20), [proposed_roots.py:9](C:\dev\abd-cdd-release-1-2-fixes\space\session\proposed_roots.py#L9), [session_file.py:14](C:\dev\abd-cdd-release-1-2-fixes\space\session\session_file.py#L14)). The Validate action names Stories and copies its ten node types. The root card's own constraint says: keep practice-specific parsing and rules in the practice that owns them.
- **Note on size.** Three judges each add members to *PracticeReading* (nine in all). **Recommended:** hold the type tables in one part, *PracticeNodeTypes*, so *PracticeReading*'s own interface grows by one member and two questions.
- **Class model, with the change marked:**

```diff
@@ (a) harness/markdown/markdown.py @@
 class MarkdownScope(folder, slug, format, ...)
-  fidelity, in_fidelity_block
+  within: tuple[str, ...]                       the headings a section is read under, e.g. ("Fidelities", "story_map")
+  reads_file: Callable[[Path], bool] | None     the owner's own filter for a folder's files
 class MarkdownText
-  fidelity_block(name), _fidelity_blocks()
+  block_under(*headings)
-class MarkdownFile.read_fidelity_subsection(name); AssetLocation._skip_fidelity_file(path)
@@ (a) harness/agent_tools/agent_tools.py @@
 class AgentToolSet
-  is_part_of_practice
+  published_name(tool) -> str                   default "{slug}.{tool.name}"
+  installed_as(tool) -> InstalledName(folder, stem)
+  listed_parts() -> list[AgentToolSet]          the parts a skill lists; default none
 class AgentTool
-  every test of name == "instructions"
@@ (a) harness/guidance/guidance.py @@
 class PracticeGuidance, FidelityGuidance
+  override published_name, installed_as, listed_parts; hand their scope the `within` headings
@@ (a) harness/installation/files.py @@
 class FileInstallation
-  _GUIDANCE_OWN_OPERATIONS, _guidance_slug, _fidelity_one_liner, _fidelity_invoke_parts
+  asks tool.toolset.installed_as(tool) and listed_parts()
@@ (b) harness/guidance/guidance.py @@
 class PracticeGuidance
+  placed_under(declared, root) -> str           Stories answers its story_tests cases; default root / declared
+  is_production_code(file) -> bool              Clean Engineering answers; default true
@@ (b), (c), (d) harness/graph/practice_reading.py  (after proposal 1) @@
 class PracticeReading
+  types: PracticeNodeTypes
+  steps_in(file) -> list[Node]                  Stories names its steps; default none
+  is_used_from_elsewhere(node) -> bool          Stories: an example; default false
+class PracticeNodeTypes
+  node_type_of: dict[str, str]                  (moved from schema_edges._NODE_TYPES)
+  child_lists, edge_order                       (moved from CHILD_LISTS, EDGE_ORDER)
+  links(owner, kind, target) -> bool            (moved from SchemaEdges._matches)
+  fold_kinds: dict[str, "class" | "block"]      (replaces CLASS_TYPES, MEMBER_TYPES literals in session_file.py)
+  scope_types: frozenset[str]                   the types a practice scopes by the session's stories; Stories names ten
@@ (c) harness/guidance/schema.py, harness/graph/schema_edges.py, schema_rules.py @@
 class SchemaType
   fields: list[(name, written)]
+  relationships: list[SchemaRelationship(name, targets, optional)]     read once in Schema._read
   required_relationships                        (derives from relationships)
-  SchemaFields._fields_of, _TYPE_FIELDS, _DESCRIBING outside schema.py, NodeEvidence
 class SchemaEdges                               (asks owner.practice.reading.types.links(...))
@@ (b) space/session @@
 class WrittenFiles
-  _under_root special cases for STORY_TESTS_FOLDER; _writes_code_to uses is_test_code
+  asks fidelity.practice_guidance.placed_under / is_production_code
 class SessionFile
-  CLASS_TYPES, MEMBER_TYPES; graph.practices.loaded(Stories); MODULE_FUNCTION_HOLDER
+  asks each loaded practice's reading for fold kinds and steps
 class NodeSpans
-  node.type == "Example"
-  imports of cdd_guidance.practices.*           (five import lines go)
@@ (d) cdd_guidance/actions/validate/checked_graph.py @@
 class CheckedGraph
-  _STORIES, _STORY_MAP_TYPES
+  for each practice of the saved graph: outside(session.stories, practice.reading.types.scope_types)
```

- **What callers write, before and after:**

```python
# before (space/session/practice_session_output.py)
from cdd_guidance.practices.stories.model.story_map_files import STORY_TESTS_FOLDER
if STORY_TESTS_FOLDER in root.parts: ...
# after
fidelity.practice_guidance.placed_under(declared, root)
```

- **What it buys:** Sharper module boundaries and Domain orientation. harness/markdown, agent_tools, and installation stop naming practices and fidelities; harness/graph stops listing practices' types; space/session's core stops importing cdd_guidance practices; Validate stops naming Stories. One relationship model on the schema where there are three definitions and two exclusion lists. A new practice then needs no edit to the framework or the session.
- **Cost and risk:** (a) about 16 files, 300 lines moved. (b) about 10 files, 150 lines, across harness, the practices, and space/session. (c) about 14 files, 350 lines. (d) 4 files, 60 lines. Unit tier after each part; then the installer's heavy spec, which compares every installed path, and the graph heavy specs. **Installed names:** (a) is the most valuable boundary fix in the framework and the easiest to get subtly wrong. Installed file paths and published MCP names are what every chat and every existing install depend on: one changed path orphans a skill and one changed name breaks a tool call. (a) is proved only by the heavy installer spec producing identical paths and the diagnostics showing no added or deleted items. **Saved files:** in (c), edge order and inverse edges must stay byte-identical in `graph.json` (shape 4), or every saved graph is rebuilt; pattern schemas add edge kinds no practice lists, so the tables need a place for a pattern's. In (b) the `.context` placement case belongs to no single practice and stays a default in the framework.
- **Depends on / conflicts with:** After 1. (a) after proposal 17 (a), which gives each file channel its own class to ask. (b) is simpler after 3 (a), which gives `is_test_code` a home outside Clean Engineering. Proposal 13 reshapes the same *CheckedGraph*.
- **Decision:** `[ ] approve  [ ] reject  [ ] change:`

---

## 9. A rule is one object: its text, its check, and its findings

- **Problem today:** A rule is three objects joined by its slug as a string. *Rule* is the text ([rule.py:81](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\rule.py#L81)). *PracticeGraphRule* is the check ([practice_rule.py:15](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\practice_rule.py#L15)). `GraphRule(Rule)` is the rule on one node ([graph_rules_collection.py:19](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\graph_rules_collection.py#L19)), built by looking the text and the check up by slug again; two more places repeat the join. Checks return plain strings, a `Finding` that is a `str` subclass, or `(node_id, message)` pairs that the graph turns back into nodes. *Rule* carries `practice`, `pattern`, and `shared` fields that only the graph fills.
- **Class model, with the change marked:**

```diff
@@ harness/guidance/rule.py @@
 class Rule(slug, body, fidelity)
-  practice, pattern, shared                     (set from outside; -> GraphRule.source)
@@ harness/graph/practice_rule.py @@
 class PracticeGraphRule(slug, node_types)
+  rule: Rule                                    set once by PracticeRuleRun from the practice's rules
-  check(node, context) -> list[str | Finding]
+  check(node, context) -> list[Finding]
-  check_practice(context) -> list[(node_id, message)]
+  check_practice(context) -> list[Finding]
-class Finding(str)
+class Finding(node, message, lines=None)        no longer a str subclass
@@ harness/graph/graph_rules_collection.py @@
-class GraphRule(Rule)                           (node, slug, check?) record(message)
+class GraphRule                                 holds node, check, and where the rule came from; not a Rule
+  record(finding)                               prose is check.rule.body, or the prose handed in for a rule with no check
-class GraphRulesCollection(RulesCollection)     record_violation(slug, message), graph_rules, from_node (joins by slug)
+class GraphRulesCollection                      a plain holder of dict[str, GraphRule]
```

- **What callers write, before and after:**

```python
# before (the shape of a practice's rule; illustrative)
return [f"{node.name} takes {count} parameters"]
# after
return [Finding(node, f"{node.name} takes {count} parameters")]
```

- **What it buys:** One object model and Resource orientation. One object per rule where three are joined by a string in three places. A finding names its node, so the graph stops looking nodes up by id. *Rule* loses three fields it does not own, and *GraphRulesCollection* loses a base class it uses for two members.
- **Cost and risk:** About 40 files: every rule under `cdd_guidance/practices/*/rules` and the patterns' rules changes a return line (ten `check_practice`), and about 250 lines change in harness/graph. Unit tier, then the graph heavy specs. Risks: a rule judged only by an agent has no check, so *GraphRule* must still take prose without one. The data `graph.return_nodes` and `graph.json` send for a rule must not change (the graph JSON spec, the app tests, saved-graph shape 4). A rule that still returns a plain string and is missed fails only when it fires, so the change needs a type check or a spec that runs every rule on a failing example; each practice's `rules/rule_examples.py` already does that.
- **Depends on / conflicts with:** Independent. Easier after 1, which types `checks` as `dict[str, PracticeGraphRule]`. The ignored pattern's rules get the return-line change only.
- **Decision:** `[ ] approve  [ ] reject  [ ] change:`

---

## 10. The *Graph* toolset comes within its budget

- **Problem today:** *Graph* ([graph.py:1499](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\graph.py#L1499)) has 18 public operations, 14 of which forward one line to `self.reads` or `self.explorer`. *Filter* ([graph.py:328](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\graph.py#L328)) is both the choices the explorer offers and the match test for one request; the graph keeps one that production never selects on (`select_violations` and `select_relationships` are called only by specs, checked), and the tools take `filter: dict` although *FilterRequest* models it ([graph.py:311](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\graph.py#L311)). `_HeldNodes`, *PracticeNodes*, and *PracticeLoading* share one collection through 12 forwarding methods ([graph.py:973](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\graph.py#L973), [graph.py:1073](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\graph.py#L1073), [graph.py:1192](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\graph.py#L1192)). The `call` passes through four layers to answer one boolean. harness/graph also records which patterns content was generated with, which no graph build uses.
- **Class model, with the change marked:**

```diff
@@ (a) harness/graph/graph.py   Filter @@
+class FilterChoices(graph, practices, node_types, practices_before)
+  node_types, offered_node_types, relationships, rules        (moved from Filter)
-class Filter(graph)                             ten public operations
+class Filter(graph, request: FilterRequest)     made for one request
   matches(node), lists(file), collect(roots)
-  clear(), select_violations(), select_relationships(), select_practices(), select_node_types(),
-  change_practices(), narrowed_by(request)
 class GraphExplorer
-  filter: Filter
-  filter_choices(...) -> Filter
+  filter_choices(...) -> FilterChoices
@@ (b) harness/graph/graph.py   Graph @@
 class Graph [@agent_toolset]
   for_call, node
-  practice(key)                                 (-> practices.named)
-  restored_from(saved)                          (-> GraphPractices.restore(saved))
   load_working_copy, load_practice_roots, load_files, refresh, save_json, set_overlays
-  inventory, filter_choices, source, return_nodes, explorer_trees, explorer_branch, practice_names, overlay_of
+  (those eight are published by GraphExplorer under the toolset name "graph"; no tool is renamed)
-  return_nodes / explorer_trees / explorer_branch (filter: dict | None)
+  ... (filter: FilterRequest | None)
@@ (c) harness/graph/graph.py   PracticeNodes @@
 class PracticeNodes(graph, practice)
   nodes, node, holds, add, add_file, unused_node_id, node_types, offer_node_types
+  nodes_read_now                                (moved from PracticeLoading)
+  (holds its nodes by id, by type, and by group itself)
-class _HeldNodes
 class PracticeLoading(part)
   open, close, forget_files, put_in_source_order
-  release, forget
@@ (d) harness/graph/graph_build.py, graph_reads.py @@
 class BuildTask(step, saves, checked)
+  apart: bool
-class WorkingCopyRead, FilesRead                (argument carriers with one builder and one reader each)
 class GraphBuild
-  load(force, call), refresh(paths, call, checked), run(task, call, state)
+  run(task, state)                              (reads task.apart)
@@ (e) harness/graph/pattern_overlays.py, patterns_file.py  ->  harness/guidance_actions @@
 class PatternOverlays
-  record_content, recorded_for, _recorded_in, _recording_instructions
 class GraphOverlay
-  record_in
+class GeneratedPatterns(overlays: PatternOverlays)     record_content, recorded_for, instructions    (in guidance_actions)
+class PatternsFile                              (moved to guidance_actions)
```

- **What callers write, before and after:**

```python
# before (space/session/file_view_filter.py:59)
self._session.graph.explorer.filter.narrowed_by(request)
# after
Filter(self._session.graph, request)
```

- **What it buys:** Sharper module boundaries and Resource orientation. *Graph* ends at 8 public operations and *GraphExplorer* at 8, with every MCP tool name unchanged. *Filter* goes from 10 public operations to 3, and no filter stays chosen on the server between calls. `graph.py` loses about 100 lines of forwarding. The `call` stops at the toolset. harness/graph loses a job that is the Generate action's.
- **Cost and risk:** (a) 5 production Python files, 4 spec files, the regenerated TypeScript adapter and its users in the graph app and the Files app; 190 lines. (b) `graph.py`, 120 lines moved, one installer change. (c) `graph.py` only. (d) 3 files, 60 lines. (e) 5 files, 120 lines moved. Unit tier after each part; graph heavy specs and the two apps' tests at the end. Risks: in (b) it is not confirmed that a part can publish its operations under the toolset that holds it with `for_call` resolved through the graph. The framework has `@hosted_only`, used by *FidelityGuidance* and *Rule*, which is the likely route; confirm before starting. If it cannot, do only the two removals, accept 16 operations, and record the exception on the card, because a second toolset name would rename eight tools. In (a) the MCP schema and the generated adapter must accept a `TypedDict` parameter; regenerate and compare before committing. (e) makes guidance_actions' dependency on harness/graph an explicit import; the card's dependency line changes with it. Renaming `in_graph` itself (115 production and about 170 spec sites) is deliberately left out.
- **Depends on / conflicts with:** After 1. Independent of the others.
- **Decision:** `[ ] approve  [ ] reject  [ ] change:`

---

## 11. One format contract, and a render request that renders itself and answers a typed result

- **Problem today:** *FormatAdapter* is declared as `parse(content)` and `render(model, **options)` ([practice_formats.py:31](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\practice_formats.py#L31)), and `_call_render` inspects each adapter's `render` signature to find out which options it takes ([practice_formats.py:272](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\practice_formats.py#L272)). So every Stories format has its own shape, and `stories.py` chooses between them with `isinstance` tests. The whiteboard and Miro story maps have no `from_workspace`; opening a `.whiteboard` story map raised `AttributeError` until commit `d67efe74a` added `Stories._read_by`, which asks `hasattr(adapter, "from_workspace")` and falls back to `parse` ([stories.py:258](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\stories.py#L258)). The defect is fixed; the cause, formats that each read a file their own way, is still there, now behind a second probe of the adapter's shape. One render has five public entries on two classes ([guidance.py:514](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\guidance.py#L514), [guidance.py:828](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\guidance.py#L828) to [guidance.py:848](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\guidance.py#L848)), because the request is built in the server and rendered in a worker. Every result is a bare `dict` whose keys callers test for.
- **The judges proposed three result and request shapes.** `Rendered(format, content)` for what a fidelity answers; `RenderResult(format, saved, migrate, content, board, batches)` for what the Render action answers; and `Written(previous, folder)` handed to an adapter. **Recommended:** all three, as two levels. A format adapter and a fidelity answer a *Rendered* (content in a format). The Render action, which also saves, answers a *RenderResult* that holds the *Rendered* and what was saved. *Written* is the part of a *RenderRequest* an adapter is allowed to see, so no adapter is handed the fidelity.
- **Class model, with the change marked:**

```diff
@@ harness/guidance/practice_formats.py @@
 class FormatAdapter (Protocol)
-  parse(content) -> ObjectModel
-  render(model, **options) -> Any
+  parse(text, file="") -> Self                   always fills and returns itself
+  render(model, written: Written) -> str         one signature
+  read_file(path, project, on_file=None) -> Self default: parse the file's text, then place it
+  reshape(rendered, existing) -> Reshaped | None declared and optional (Render reads it with getattr today)
+class Written                                    previous: str, folder: Path | None
 class RenderRequest (frozen)
   format, content, source, previous, folder, fidelity; source_format, companion
+  written -> Written
+  RenderRequest.from_files(fidelity, format, paths, source, previous)     (moved from FidelityGuidance.files_to_render)
+  render() -> Rendered                           (moved from FidelityGuidance.render_request)
+  _folder_holding(paths)                         (moved from FidelityGuidance)
+class Rendered(format: Format, content)          replaces the bare dict; writes itself as today's two fields
 class PracticeFormats
-  read(paths, request), render(request) -> dict
+  read(paths), render(request) -> Rendered
-  _call_render: inspect.signature(target.render)
+  _call_render: target.render(parsed, request.written)
@@ harness/guidance/guidance.py @@
 class FidelityGuidance
-  render(format, content, source) -> dict
-  render_files(format, paths, source, previous) -> dict
+  render(format, content, source) -> Rendered            (one line: RenderRequest(...).render())
+  render_files(format, paths, source, previous) -> Rendered
-  files_to_render(format, paths, source, previous) -> RenderRequest
-  render_request(request) -> dict
@@ cdd_guidance/actions/render/ @@
+class RenderResult                               rendered: Rendered; saved: list[Path]; migrate: list[Migration];
+                                                 board, batches; writes itself as today's dictionary keys
+class Migration                                  file; kept | signature_differs; may_have_replaced_it | model_has
 class Render
-  render(...) -> list[dict]; _saved_by(result: dict), _format_named_by(sources), _saved_code(... seven values)
+  render(...) -> list[RenderResult]
 class RenderedFile, RenderedCode
-  save(rendered: dict) -> dict
+  save(rendered: Rendered) -> RenderResult
@@ cdd_guidance/practices/stories/model/ @@
 class StoryModel
+  render(canonical, written) -> str; parse(text, file="") -> Self; read_file(path, project, on_file=None) -> Self
 class MarkdownStoryModel
-  render(canonical, previous, workspace); parse(text, file) -> new model; from_workspace(root, on_file, project)
+  render(canonical, written); parse fills self; read_file (a file), read_folder (a folder merge); opened_from kept
 class JsonStoryModel
-  render(canonical, previous); from_workspace(root); parse_file(file, text)
+  render(canonical, written); read_file
 class DrawIOStoryModel
-  render(canonical=None, previous, workspace); from_workspace(path, on_file, project)
+  render(canonical, written); inherited read_file
 class WhiteboardStoryModel, MiroStoryModel
-  render(canonical=None, previous); parse(text)              (no from_workspace)
+  render(canonical, written); inherited read_file
@@ cdd_guidance/practices/stories/stories.py @@
 class Stories
-  open_file: isinstance(adapter, MarkdownStoryModel)
-  _read_by(adapter, path, project, on_file): hasattr(adapter, "from_workspace"), else adapter.parse(text)
+  open_file / _story_map_file: adapter.read_file(path, project, on_file)
@@ ux, clean_engineering, ddd, bdd format adapters (about 20 classes) @@
-  render(canonical), render(canonical, previous), render(canonical, previous, workspace)
+  render(canonical, written)
```

- **What callers write, before and after:**

```python
# before (cdd_guidance/actions/render)
request = fidelity.files_to_render(format, paths, source, previous)    # in the server
result = fidelity.render_request(request)                              # in the worker
text = result["content"]
# after
request = RenderRequest.from_files(fidelity, format, paths, source, previous)
rendered = request.render()
text = rendered.content
```

- **What it buys:** Sharper module boundaries, One object model and Resource orientation. One contract every format adapter of every practice meets, so `inspect.signature`, the `isinstance` and `hasattr` probes in `stories.py`, and the differing `from_workspace` signatures go; a format that cannot be opened becomes impossible to write, where today each one has to be remembered. *FidelityGuidance* goes from 10 public operations to 8. A render result is a type the Files app, the session's format alignment, and the instruction texts can rely on.
- **Cost and risk:** About 45 files: 12 production files in Stories, 2 in the framework, 15 to 20 adapter classes in the other practices, 8 to 10 in the Render action, and 60 to 80 spec call sites; `render_spec.py` (825 lines) mostly asserts dictionary keys. The no-legacy rule forbids a pass in which the framework accepts both shapes, so the framework and every adapter change in one commit. Unit tier, then the whole heavy tier. **Published names:** `PracticeGuidance.render` and `render.render` are published tools; *Rendered* and *RenderResult* must write themselves as the same JSON keys, so no installed skill text changes. Risks: `parse` filling `self` changes behaviour where a caller parses twice on one adapter instance. A *RenderRequest* crosses to the render worker; whatever serialises it must still carry or rebuild the fidelity. **A smaller first step, if the whole contract is too much at once:** Stories only (`read_file` on *StoryModel*, `parse` fills `self`), about 100 lines, which removes `_read_by` and the `isinstance` branch while leaving `render`'s signature alone.
- **Not included (recorded for a later decision):** separating the format adapter from the domain root in UX and Stories (*UxMapFormat* beside *UxMap*). Its judge did not recommend it on its own; see the open questions.
- **Depends on / conflicts with:** After 7 (*RenderPlace*). Together with 12, which uses the declared `reshape`. Proposal 21 changes Stories' code formats and should follow this one.
- **Decision:** `[ ] approve  [ ] reject  [ ] change:`

---

## 12. One way to write a render onto a file that is already there

- **Problem today:** When a model is rendered onto a file that exists, what only the file held must stay. Five classes do this for code and documents with five outlines and five copies of the marker text `"no longer in the model"` ([reshaped_code.py:37](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\actions\render\reshaped_code.py#L37), [kept_document.py:33](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\actions\render\kept_document.py#L33), [reshaped_story_file.py:34](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\reshaped_story_file.py#L34), [reshaped_view.py:29](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ux\model\view\reshaped_view.py#L29), [spec_reshape.py:29](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\bdd\model\spec_reshape.py#L29)). Three more classes give a rendered model back the words the earlier file held, from the outside of the objects that own the words: *UnwrittenProse* ([markdown_class_model.py:757](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\markdown\markdown_class_model.py#L757)) and *ReplacedDocument* with two helpers ([replaced_document.py:23](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ddd\model\markdown\replaced_document.py#L23)).
- **Class model, with the change marked:**

```diff
@@ (a) harness/guidance/practice_formats.py @@
 class Reshaped
   text, kept, added, changed
+  set_apart: int                                lines kept below the text (a sentence inside `kept` today)
+class ExistingText                              the file as it was
+  holds_every_line_of(other) -> list[str]       the lost-line check, written once (three copies today)
+  set_apart_below(rendered, comment) -> Reshaped
+class KeptMark                                  NO_LONGER_IN_MODEL: the one definition
+  marks(lines_above_a_member) -> bool           (four copies today)
+  line_for(member, where, comment) -> str       (four copies today)
+class OutlinedMember                            name, lead, start, end, indent
+  lead_of(lines, start, indent)                 (moved from CodeOutline, SpecOutline, Component)
@@ (a) cdd_guidance/actions/render/ @@
 class Render
-  _saved_code: getattr(adapter, "reshape", None)
+  _saved_code: formats.adapter(format).reshape
 class CodeOutline
-  Member
+  OutlinedMember; the comment sign comes from the language
 class KeptDocument                              _markdown, _drawio, _whiteboard    (all three stay; see the risk)
@@ (a) stories ReshapedStoryFile, ux ReshapedView, bdd SpecReshape @@
-  NO_LONGER_IN_MODEL (each), _lead_of (each), own "already marked" test and marking line
+  use KeptMark, ExistingText; ComponentMember and SpecBlock extend OutlinedMember
@@ (b) cdd_guidance/practices/clean_engineering/model/ @@
 class OoadNode
+  take_words_from(earlier: OoadNode)            each node keeps what it has and takes what it lacks
 class OoadClass
+  take_words_from                               intent, then each member by name
 class Operation, Property
+  take_words_from                               description, callees, invariants
 class Module
+  take_words_from                               language, constraint, a description cut short by a drawing
-class UnwrittenProse(model)                     give_back()
@@ (b) cdd_guidance/practices/ddd/model/ @@
 class BoundedContext, Aggregate
+  take_words_from                               notes, group, consumed events, integrations
-class _ReplacedCard                             give_its_words, _give_operation
 class ReplacedDocument, _ReplacedAggregate      (shrink to the integration matching: same_target, draws_no_arrow)
```

- **What callers write, before and after:**

```python
# before (MarkdownCleanEngineeringModel.render)
UnwrittenProse(model).give_back()
# after
model.take_words_from(earlier_model)
```

- **What it buys:** One object model, and Resource orientation for part (b). One marker, one lost-line check, and one member record where each is written three to five times (150 to 200 of about 1,100 lines). The words a file held are given back by the node that owns them, so a new field on *Operation* is kept by adding it in one place.
- **Cost and risk:** (a) about 12 production files, 300 lines changed, no behaviour change. (b) 8 production files, 110 lines removed and 70 added. Unit tier; the reshape specs of the Render action and the three practices, and the round-trip specs of Clean Engineering and DDD. Risks: the practice reshapers differ in real ways (nested `with` blocks, React components), so what is shared must stay the record and the marker, never a shared algorithm. In (b), *UnwrittenProse* clones the model before translation because translation overwrites objects in place; the clone stays and moves into `render`. DDD's rules for integrations and events are subtler than "keep what is missing", which is why they stay in *ReplacedDocument*.
- **Deliberately left out:** the stories judge's second pass, which would remove `KeptDocument._drawio` and `_whiteboard` and trust each practice's adapter to keep what a person drew. *KeptDocument* is the safety net that keeps a person's cell whatever the adapter does; this branch fixed a defect there in commit 134df3e88 ("a drawing that holds only a person's note keeps it"). See "Dropped".
- **Depends on / conflicts with:** (a) with 11 (the declared `reshape`). (b) needs 3 (c), which puts DDD's word fields on its base classes.
- **Decision:** `[ ] approve  [ ] reject  [ ] change:`

---

## 13. One validation report object and one checked-fidelity object

- **Problem today:** A validation report is known in pieces by three modules. `ValidationReports.new_path` writes the fidelity's slug and the time into the file name ([practice_session_output.py:718](C:\dev\abd-cdd-release-1-2-fixes\space\session\practice_session_output.py#L718)); *ValidationRun* parses them back ([violation_history.py:69](C:\dev\abd-cdd-release-1-2-fixes\space\session\violation_history.py#L69)) and so does the board's *ReportFile* ([report.py:176](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\report.py#L176)). The graph saved beside a report is located by Validate's *ReportFiles* ([report_files.py:25](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\actions\validate\report_files.py#L25)) and by the board. History lines are untyped dicts ([violation_history.py:45](C:\dev\abd-cdd-release-1-2-fixes\space\session\violation_history.py#L45)) worked on by five helper classes. In the Validate action, *CheckedGraph* keeps fidelities and formats as two parallel lists, exposes six mutable fields, and is passed to *ReportFiles* while *ReportFiles* is passed to it.
- **Corrected from the judge's report:** the five history helpers are private classes (`_ListedHit`, `_HitKey`, `_MeasuredRun`, `_HistoryRuns`, `_JudgedRun`), so removing them changes no seam.
- **Class model, with the change marked:**

```diff
@@ space/session/  (the validation files) @@
+class ValidationReport(file, fidelity)
+  fidelity: FidelityGuidance                    held, not parsed from the name
+  made_at: LogTimestamp                         from the name, parsed in this one place
+  text, saved_graph: Path, has_result
+  judgment: ReportJudgment
+  hits: list[Violation]                         from the saved graph; from the markdown only for a rebuild
 class ValidationReports(output)
-  listed() -> list[Path]
-  new_path() -> Path
+  listed() -> list[ValidationReport]
+  new() -> ValidationReport
 class ViolationHistory
-  record(report: Path, hits, scope)
+  record(report: ValidationReport, hits, scope)
-  events -> list[HistoryEvent]                  (TypedDict, every key optional)
+  events -> list[HistoryLine]                   RunLine, FoundLine, FixedLine, JudgedLine; same keys on disk
-class ValidationRun(report: Path, hits, scope)  (-> ValidationReport)
-class _ListedHit, _HitKey, _MeasuredRun, _HistoryRuns, _JudgedRun
@@ space/kanban/report.py @@
 class ReportFile(file, fidelity)
-  stamp (parsed again), text, has_result, its own saved-graph path
+  holds a ValidationReport
@@ cdd_guidance/actions/validate/ @@
+class CheckedFidelity                           fidelity, format (read once)
+  checked_files, other_format_files, written_folders       (moved from CheckedGraph)
+  report: ValidationReport                      (was ReportFiles._claimed_for[(fidelity, path)])
 class CheckedGraph
-  (session, fidelities, named); _fidelities[], _formats[] in parallel
-  session, edited, prefixes, files, checked_files, unchecked_files     (public and mutable)
-  check_beside(reports)
+  (session, checked: list[CheckedFidelity], named: NamedToCheck)
+  holds its ReportFiles; fields read through properties; files_built_from (was prefixes)
 class ReportFiles
-  save(report, graph)
+  save(report)                                  asks ValidationReports.new(); saves through the report
```

- **What callers write, before and after:**

```python
# before: the name is parsed twice
self._file.stem.rsplit("-", 1)[-1]                                   # space/kanban/report.py:204
self.report.stem.rsplit("-", 1)[-1][:REPORT_STAMP_LENGTH]            # space/session/violation_history.py:104
# after
report.made_at
```

- **What it buys:** One object model and Resource orientation. One object for a report where three modules each know a piece: the file name is written and parsed in one class, and the saved graph has one path. `violation_history.py` shrinks by five helper classes. Validate holds one object per checked fidelity instead of two lists joined four times.
- **Cost and risk:** About 14 files and 550 lines; `scripts/backfill_violation_history.py`, `violation_history_spec.py`, `accepted_violations_spec.py`, `checked_graph_spec.py`, and `validate_spec.py` (which patches `CheckedGraph.check_beside` to order two calls and needs another way in). Unit tier, then the Validate heavy specs. **Saved files:** the history is append-only and tracked in git; the typed lines must write exactly today's keys, or matching a fix against earlier lines breaks. `ReportFile.version` is the board's cache key; its parts must stay, or the board's progress cache is worked out again for every ticket once. Risk: report files are claimed before the graph is built so that a path that does not exist is refused before any file is created; building on first read must keep that order.
- **Depends on / conflicts with:** After 6 and 7. Proposal 8 (d) edits the same *CheckedGraph*; do them together. Proposal 20 then moves these files into `space/session/validation`.
- **Decision:** `[ ] approve  [ ] reject  [ ] change:`

---

## 14. The pages ask Python for rules, listings, prompts, and commands

- **Problem today:** The chat bar ([guidance-client.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\chat-ui\pane\hooks\chat-bar\guidance-client.ts)) and the Files app ([guidance-selector.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\guidance-selector.ts)) each implement the same press, because `Session.update_guidance_selection` takes whole lists ([session.py:149](C:\dev\abd-cdd-release-1-2-fixes\space\session\session.py#L149)); only the chat bar applies "select the ticket's stage first". In Python the change itself is made by *GuidanceVersion* ([guidance_version.py:57](C:\dev\abd-cdd-release-1-2-fixes\space\session\guidance_version.py#L57)) while *GuidanceSelection* is rebuilt for every answer and only reads. The board's page holds rules Python also holds, and one already disagrees (the stage count against `is_over_limit`, [board.py:688](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\board.py#L688)); it writes agent prompts with tool names in them ([report-client.ts](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\app\src\kanban\ticket\report-client.ts), [ticket-chat-prompts.ts](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\app\src\kanban\ticket\ticket-chat-prompts.ts)), and the chat bar writes some again. A command is built from parameters its caller already holds ([ticket.py:799](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\ticket.py#L799)) and the pages add `format=` to it themselves. Every stage answers the same four action lists, computed three times ([stages.py:144](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\stages.py#L144); checked: `_placed` never uses the stage).
- **Where the judges overlapped.** Two proposed a place for the command text: `Work.command(action)` on the board, and `GuidanceSelection.command(action)` in the session. **Recommended:** the text is written once, by the session's selection (space/kanban may import space/session and not the reverse); the board's `Work.command` asks it with its own fidelities. Corrected from the judge's report: `ticket.py` uses the three action-name constants 13 times, not 18.
- **Class model, with the change marked:**

```diff
@@ (a) space/session/guidance_selection.py, guidance_version.py @@
 class GuidanceSelection(session)                held by the session (a new object per answer today)
   version, is_stage_chosen, stages, practices, formats, fidelities, covered
+  select(stages, practices, formats)            (moved from GuidanceVersion; raises the version once)
+  toggle(part: "stage" | "practice" | "format", name) -> GuidanceSelection     MCP: session.toggle_guidance
+  changed(), wait_past(version)                 (moved from GuidanceVersion)
+  fidelities_for_actions -> list[slug]          none selected means all
+  command(action, formats=None) -> str          the one place a command and its `format=` are written
+  (applies "the ticket's stage first" itself when nothing was chosen)
-class GuidanceVersion                           changed, save, batch, select, wait_past; the _is_batched flag
 class FormatGroup(label, offering)
+  data fields label, formats, offered, is_selected       (the chat bar reads it directly)
-class FormatSelection(group)                    (only forwarded)
@@ (a) space/session   FileEntry @@
+  is_listed, is_session_work                    answered for the selection the call names
@@ (b) space/kanban/ticket.py @@
+class Work (base)                               stage, action_states, has_violations, violation_count, commands,
+                                                allowed_actions, fidelities; command(action) -> str
 class FidelityProgress(Work)                    fidelities = [its own]
 class StageWork(Work)                           fidelities = each of its progress, sent by reference
 class TicketWork
-  command(action, fidelities)
@@ (c) space/kanban/ticket.py, board.py, report.py @@
 class Ticket
+  prompts: TicketPrompts                        split, handoff, set_up_roots, close_session, new_chat (the text to send)
+  can_edit: bool                                false for main; edit_text and tag refuse main with MainStaysOpenError
 class Stage
+  ticket_count: int                             the number the head shows, by the same rule as is_over_limit
 class ReportRule, ListedViolation
+  fix_prompt, false_prompt
 class Report
+  fix_prompt
 class BacklogItem
+  parent_choices                                (as Ticket.parent_choices is sent today)
@@ (d) harness/guidance/stages.py, action_catalogue.py @@
 class ApproachStage(name, scope, catalogue)
-  catalogue; steps, actions, producing_actions, actions_with_formats
 class ActionCatalogue
+  steps, on_fidelities, producing, taking_formats: tuple[Action, ...]     made once
 class Action
+  place: OnStage | None
-GENERATE, VALIDATE, RENDER                      (the board asks the catalogue for the step actions)
@@ TypeScript pages @@
-  chat bar: flipped(), startStage(), commandOn(), the shownStages / isPracticeOn / fidelities rules
-  Files app: GuidanceSelector.toggleStage / togglePractice / toggleFormat; listedBy, filesShown, rootFilesShown, isSessionWork
-  board: TicketChatPrompts' texts, ReportClient's four prompt builders, ChatOpening.newChatPrompt,
-         ColumnClient.count's own rule, the isMain tests for editing, BacklogItemClient.canTakeAsChild,
-         TicketWork.progressIn, the `${command} format=${formats}` joins
+  each press calls one tool and draws the answer
```

- **What callers write, before and after:**

```ts
// before (chat bar)
await session.updateGuidanceSelection(flipped(selection, 'stage', name))
const text = `${command} format=${formats}`
// after
await session.toggleGuidance('stage', name)
const text = work.commands[action]
```

- **What it buys:** Sharper module boundaries, One object model and Domain orientation. A rule is written in one language: about 400 lines of TypeScript that restate Python go, among them the one rule that already disagrees. The selection is one object that changes itself; *GuidanceVersion*, *FormatSelection*, and the batching flag go. Prompts that name MCP tools are worded beside the tools they name, and their specs move with them. *ApproachStage* loses four operations that answer the same lists on every stage.
- **Cost and risk:** (a) about 20 files, 600 lines, 200 TypeScript lines removed. (b) 2 Python files and 5 TypeScript files, 140 lines. (c) 3 Python files (120 lines added), 8 TypeScript files (150 removed). (d) about 9 files, 100 lines. One reinstall regenerates the adapters. Unit tier, the pages' own tests, the chat bar and Files app story tests; then e2e for the board. **Published names:** one new tool (`session.toggle_guidance`); the published key `actions` and the data field `formats[].is_selected` keep their names. A selection file written by the old chat bar must still read. Risks: both pages draw a press at once and correct it from the answer; with the flip in Python the press shows after one round trip unless the page keeps drawing the flip, which is display and may stay. Prompts on every ticket and violation make `board.show` and a report larger; the report's prompts could instead be answered by a tool at the cost of one call per click. Without the batching flag, `select` must write the practices' and fidelities' fields itself and raise the version once, which needs proposal 6's typed fields. In (d) render has no trait of its own today, so one is added, and the board's data shape changes with the pages in the same pass. Whether main's text may be edited is a product decision the page made alone; see the open questions.
- **Depends on / conflicts with:** After 6. Independent of the framework proposals. Proposal 24 removes some of the same page files.
- **Decision:** `[ ] approve  [ ] reject  [ ] change:`

---

## 15. The chat that asked is passed, a new chat is one object, and a queued prompt does its own work

- **Problem today:** `OpenSessions.state()` falls back to a process-wide "call being answered" when no chat is passed, and `Session.close` relies on it ([open_sessions.py:69](C:\dev\abd-cdd-release-1-2-fixes\space\session\open_sessions.py#L69), [session.py:655](C:\dev\abd-cdd-release-1-2-fixes\space\session\session.py#L655)). `switch` answers one string in which a refusal, a side effect, and the log's instructions are joined ([open_sessions.py:128](C:\dev\abd-cdd-release-1-2-fixes\space\session\open_sessions.py#L128)), and space/session imports tools/prompt_queue to queue a handoff's steps ([open_sessions.py:13](C:\dev\abd-cdd-release-1-2-fixes\space\session\open_sessions.py#L13)), although the handoff's format is the session's and the queue parses it ([prompt_queue.py:374](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\prompt_queue.py#L374)). Four places describe "open a new chat on this folder with this first prompt" and three call `links_of_run()` themselves ([chat.py:210](C:\dev\abd-cdd-release-1-2-fixes\harness\chat\chat.py#L210), [repos.py:79](C:\dev\abd-cdd-release-1-2-fixes\space\repo\repos.py#L79), [ticket.py:579](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\ticket.py#L579), [desktop_walk.py:219](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\desktop_walk\desktop_walk.py#L219)). A queued prompt and its steps are dicts ([prompt_queue.py:50](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\prompt_queue.py#L50)), ten operations of *PromptQueue* look one up by id, and the rule for which prompt is next lives only in the mod's TypeScript.
- **The judges disagreed on the handoff.** One kept space/session calling the queue (`queue.queue_once(...)`). The other made tools/prompt_queue register with the session, so the session imports no tool. **Recommended:** the registration, with the first judge's `Handoff.next_steps` and `queue_once`. It removes an import from the session's core into a tool, which is the direction `ToolCall.open_sessions_with` already sets.
- **Class model, with the change marked:**

```diff
@@ (a) space/session/open_sessions.py, session.py, handoffs.py @@
 class OpenSessions
-  state(chat=""), name_for(chat=""), open(session, chat=""), current(chat=""), close(session)
+  state(chat), name_for(chat), open(session, chat), current(chat), close(session, chat)
-  the CALLS_BEING_ANSWERED fallback
-  switch(name, workpath, call) -> str
+  switch(name, workpath, call) -> SwitchedSession
+  on_session_opened(listener)                   a seam; tools/prompt_queue registers with it
-  import of tools.prompt_queue
+class SwitchedSession                           session, opened_in_worktree_of, outside_worktree, default_roots,
+                                                latest_handoff; instructions -> str (from SESSION-SWITCH.md)
 class Session
-  close()
+  close(call)
+class Handoff.next_steps -> list[str]           (moved from prompt_queue.handoff_steps)
@@ (b) harness/chat/chat.py @@
+class NewChat(folder, prompt, opened_from: Chat | None)      link; open() -> str
-class ChatLinks                                 open_new(folder, prompt), link_to_new(folder, prompt), hand_over(link)
+class ChatOpener                                open(link)                    (renamed from ChatLinks)
-def links_of_run()                              (public; Chats.load() builds the opener)
 class Chats(folder, opener)
+  new_chat(folder, prompt) -> NewChat
   open(folder, prompt)                          (= new_chat(folder, prompt).open())
@@ (b) space/repo/repos.py, space/kanban/ticket.py, cdd_guidance/desktop_walk @@
-class NewChat(root, title, session)             first_prompt, link, instructions, open()
+class RepositoryChat(root, title, session)      keeps title, first_prompt, instructions; holds a harness NewChat
 class Ticket
   new_chat_link                                 (= Chats.load().new_chat(worktree, prompt).link)
@@ (c) tools/prompt_queue/prompt_queue.py @@
-class QueuedPrompt(TypedDict), PromptStep(TypedDict)
+class QueuedPrompt                              id, text, steps: PromptSteps, attachments, is_done, robot
+  edit(text), mark_done(), reopen(), assign(robot), plan(steps), interrupt(text), attach(file); record -> dict
+class PromptSteps                               done(number), move(step, place), remove(step), back(), on(); pointer
 class PromptQueue (toolset)
-  prompts: list[dict]
+  prompts: list[QueuedPrompt]
+  next: QueuedPrompt | None                     the pointer rule (in prompt-queue.ts today)
+  prompt(id) -> QueuedPrompt                    refuses with PromptNotQueued
   show, add, add_all, move, remove, clear
   done, reopen, assign, set_steps, add_interruption, step_done, attach, edit     (each: self.prompt(id).<verb>(); names unchanged)
+  move_step(prompt, step, place), remove_step(prompt, step), step_back(prompt), step_on(prompt)
-  queue_handoff(handoff: Path) -> int
+  queue_once(source: str, texts: list[str]) -> int
-def handoff_steps(text)
@@ (c) tools/prompt_queue/hooks/queue/prompt-queue.ts @@
-  pointerOf, movePointerUp/Down, stepPointerOf, moveStepPointerUp/Down, removeStep, moveStep -> set_steps(whole list)
+  each press calls one tool
```

- **What callers write, before and after:**

```python
# before
links_of_run().link_to_new(self.worktree, prompt)          # space/kanban/ticket.py:579
queue.queue_handoff(handoff_path)                          # space/session/open_sessions.py
# after
Chats.load().new_chat(self.worktree, prompt).link
queue.queue_once(handoff.name, handoff.next_steps)         # in the listener the queue registered
```

- **What it buys:** Sharper module boundaries, Resource orientation and Domain orientation. No operation finds its chat through a process-wide value. space/session's core stops importing a tool, and the handoff format has one reader. One object for a new chat where four places describe one. A prompt and its steps have behaviour; the mod and the agent follow one pointer rule instead of two, and 120 lines of TypeScript go.
- **Cost and risk:** (a) 4 files, 120 lines, one markdown file. (b) 8 files, 180 lines; harness/chat's seam goes from 27 to about 22 of 66. (c) 6 files, 350 lines changed; four new MCP operations, so *PromptQueue* rises to 21 public operations unless the prompt's tools are republished as `queued-prompt.*`, a rename that is not part of this proposal. Unit tier; the queue heavy spec that changes one queue from two processes; the chat heavy specs. **Saved files:** the queue file is shared by the stable and dev lanes, so `QueuedPrompt.record` must write exactly today's keys, and the list of queued handoffs keeps its key `handoffs`. Risks: every caller of `current()` and `name_for()` that silently relied on the process-wide value needs checking, or it opens the checkout's session instead of the chat's. The "join the opener's sidebar section" text is added only when a chat asked; `Chats.load` must be given the call, as `PromptQueue.load` already is, or the text is lost for links the board builds.
- **Depends on / conflicts with:** Independent. Proposal 23 (d) keeps the queue mod's remaining state in atoms.
- **Decision:** `[ ] approve  [ ] reject  [ ] change:`

---

## 16. One daemon model and one lock file for the hook server and the cdd server

- **Problem today:** Two long-running servers are built from different classes that do the same steps: *HookDaemon* ([hook_daemon.py:280](C:\dev\abd-cdd-release-1-2-fixes\harness\hooks\hook_daemon.py#L280)) and *McpDaemon* ([mcp_daemon.py:55](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_daemon.py#L55)). Each has its own address class, published-address file, ping, record of who answers, start into a capped log file, wait loop, and "did not come up" error ([hook_daemon.py:74](C:\dev\abd-cdd-release-1-2-fixes\harness\hooks\hook_daemon.py#L74), [mcp_daemon.py:32](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_daemon.py#L32)). Three lock-by-file classes exist beside them: *InstallLock* ([install_lock.py:36](C:\dev\abd-cdd-release-1-2-fixes\harness\installation\install_lock.py#L36)), `JsonFile.held` ([json_file.py:109](C:\dev\abd-cdd-release-1-2-fixes\harness\installation\json_file.py#L109)), and `_SpawnLock` ([hook_daemon.py:214](C:\dev\abd-cdd-release-1-2-fixes\harness\hooks\hook_daemon.py#L214)). A fix to one server's start or stop, such as the wait for a stale port, is not made in the other.
- **Class model, with the change marked:**

```diff
@@ harness/process/server_daemon.py             (new file) @@
+class ServerDaemon(port: ExclusivePort, log: CappedLogFile)       abstract
+  running() -> RunningServer | None            (was HookDaemon.live_address() and McpDaemon.ping())
+  is_running(), ensure(), stop(), restart()
+  spawn()                                      uses _command(), _environment(), _folder()
+  _wait_until_answering()                      one loop, one error
+class RunningServer(process: RunningProcess, serves: Path, code: str)     (moved from harness/mcp; HookDaemonIdentity folded in)
+class ServerDidNotStart(daemon, seconds, log_tail)                        (replaces HookDaemonNotReady and mcp's ServerDidNotStart)
@@ harness/process/lock_file.py                 (new file) @@
+class LockFile(path, wait_seconds)             held(), claim(), release(), holder     (InstallLock's body moves here)
@@ harness/hooks/hook_daemon.py @@
-class HookDaemon(repo, port)                   live_address, is_running, ensure, stop, spawn, serve, claim_port
+class HookDaemon(ServerDaemon)                 keeps serve(), source_stamp, the takeover of a port from older code
-class HookDaemonIdentity(pid, stamp, repo)
 class HookDaemonAddress
-  host, port, identity; pid, stamp, repo copies
+  host, port, running() -> RunningServer
-class _SpawnLock                               (-> LockFile)
-class HookDaemonNotReady
@@ harness/mcp/mcp_daemon.py @@
-class McpDaemon(home, address, port)           ping, is_running, ensure, restart, stop, spawn, status, _wait_for_ping
+class McpDaemon(ServerDaemon)                  keeps home, address, status, "a second start exits quietly"
-class RunningServer(answer: dict)
-class ServerDidNotStart
@@ harness/installation/install_lock.py, json_file.py @@
 class InstallLock                              (a thin LockFile that names the file in an IDE folder)
 class JsonFile
   held()                                       (uses LockFile)
```

- **What callers write, before and after:**

```python
# before
HookDaemon(repo).live_address()        McpDaemon(home).ping()
# after
HookDaemon(repo).running()             McpDaemon(home).running()
```

- **What it buys:** One object model. One model of a long-running server and one lock, so a fix to starting, stopping, or waiting is made once. About 250 lines removed and 150 added.
- **Cost and risk:** About 12 production files and 8 spec files: space/repo (closes a worktree's hook daemon), `scripts/instances.py`, `scripts/start.py`, `scripts/exercise_hooks.py`, harness/diagnostics, `hook_installation.py`, `mcp_server.py`, `server_lanes.py`, `cdd_home.py`. Unit tier, then **every heavy spec of both daemons**; only the heavy tier shows a regression, and the job-breakaway path only on Windows. These are the two processes every chat depends on. The hook daemon's takeover of a port from older code and the cdd server's quiet second start differ on purpose and stay in the subclasses. harness/process's card says "never a helper of another class here"; a base class changes that sentence, so the card changes with the code.
- **Depends on / conflicts with:** Independent. Do it alone in its pass, so a heavy-tier failure has one cause.
- **Decision:** `[ ] approve  [ ] reject  [ ] change:`

---

## 17. Install channels, the install run, and a toolset's name are objects

- **Problem today:** A channel is a string everywhere: `InstallDestination.MCP` and its siblings ([agent_tools.py:911](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\agent_tools.py#L911)), `tools_for("mcp")` ([agent_tools.py:665](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\agent_tools.py#L665)), `annotation_kinds.publishes(channel, op)` ([annotation.py:60](C:\dev\abd-cdd-release-1-2-fixes\harness\annotations\annotation.py#L60)). *FileInstallation* writes three kinds of file behind `if` tests on the destination ([files.py:102](C:\dev\abd-cdd-release-1-2-fixes\harness\installation\files.py#L102)). *ServerInstallation* ([destination.py:139](C:\dev\abd-cdd-release-1-2-fixes\harness\installation\destination.py#L139)) means both "a channel a module registers" and "a channel with a server", so the hook channel carries three operations that do nothing ([hook_installation.py:48](C:\dev\abd-cdd-release-1-2-fixes\harness\hooks\hook_installation.py#L48)). What an install deployed is a `dict[str, list[str]]` passed through five methods, and its colour is written into the report text and found again by scanning for a colour word ([install_diagnostics.py:57](C:\dev\abd-cdd-release-1-2-fixes\harness\installation\install_diagnostics.py#L57)). A toolset is named in five shapes ([agent_tools.py:28](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\agent_tools.py#L28)) and three places switch on the type.
- **Class model, with the change marked:**

```diff
@@ (a) harness/annotations, harness/agent_tools @@
 class AnnotationKinds
-  of_channel(channel), annotated_for(channel, op), publishes(channel, op), name_given_for(channel, op)
+  destinations_of(op) -> tuple[DestinationKind, ...]
 class DestinationKind                          (Skill, Command, Rules, Mcp, Hook: the kind is the channel)
+  publishes(op), name_given(op)
-class InstallDestination                       MCP, HOOK, SKILL, COMMAND, RULE as strings
 class AgentTool
-  install_to_mcp, install_to_hook, install_to_skill, install_to(name), destinations: list[str]
+  destinations: tuple[DestinationKind, ...]; is_published_to(kind)
 class AgentToolSet
-  tools_for(name)
+  tools_published_to(kind)
@@ (a) harness/installation/destination.py, files.py, language_adapter.py @@
 class Installation
-  (layout, path, repo); channel: str; install(tool) -> write(tool); track_writes_with(callback)
+  (target: InstallTarget, record: InstallRecord); destination: DestinationKind
-class FileChannel(destination: str, served_on_mcp: bool)
-class FileInstallation(target, channel: FileChannel)       one class, three writers
+class FileInstallation                         base
+class SkillInstallation, CommandInstallation, RulesInstallation(FileInstallation)
+  relative_path(tool), front_matter(tool), body(tool)       (every `== SKILL` branch goes)
-class LanguageAdapterInstallation(Installation)            record(toolset), write_all()
+class LanguageAdapters(target, record)         no longer an Installation
@@ (b) harness/installation/destination.py, harness/hooks, harness/mcp @@
-class ServerInstallation(Installation)         accepts, published, toolsets, create, standup, diagnose -> dict,
-                                               ensure_running -> dict[str, str], status, serves_this_process
+class RegisteredChannel(Installation)          accepts(tool), published, toolsets, create(), status() -> list[str]
+  server: ChannelServer | None                 none for the hook channel
+class ChannelServer                            stand_up() -> StandUp; ensure_running() -> list[str]; runs_this_process
+class StandUp(tools: list[str], skipped: SkippedTools)     (replaces the two diagnose dicts)
 class HookInstallation
-  standup(), diagnose(), ensure_running()      (do nothing)
 class McpInstallation
+  server = McpChannelServer(served, claude_plugins)
@@ (c) harness/installation/installer.py, install_diagnostics.py @@
-class Deployment(installer)                    run, install_self, write_language_adapters, ensure_runtimes, diagnose_after_install
+class InstallRun(installer, toolsets, replace) one per install: channels, publish(), stand_up(), diagnosis
+class Deployed                                 what a folder holds on each channel
+  of_folder(target, toolsets, published), of_last_install(diagnostics), changes_since(last) -> DeployedChanges
+class InstallDiagnosis(deployed, changes, server_status)    colour, is_red, report (written from the fields, never read back)
 class InstallDiagnostics
-  channels_in_folder, deployed, diagnosed, compared, record_run, record_install
+  record(diagnosis), last_deployed() -> Deployed | None
   write_section(section, results), installed_items(channel)
 class Installer
+  install_self(), write_language_adapters()    (moved from Deployment)
 class InstallChannels
-  the `installing` flag
@@ (d) harness/agent_tools/agent_tools.py @@
-type ToolsetConfiguration = str | type | dict | AgentToolSetOrigin | None
 class ToolsetReference                         the one name; text only where it crosses a process
+  of(cls), parsed(text), toolset_class, made(**context) -> AgentToolSet
 class AgentToolSet
-  instantiate(toolset), from_items(items, context=)
 class AgentToolSetOrigin
-  registration_name -> str
+  reference -> ToolsetReference
```

- **What callers write, before and after:**

```python
# before
if tool.install_to_mcp: ...
toolset.tools_for("skill")
AgentToolSet.instantiate("cdd_guidance.practices.stories.stories:Stories")
# after
if tool.is_published_to(Mcp): ...
toolset.tools_published_to(Skill)
ToolsetReference.parsed("cdd_guidance.practices.stories.stories:Stories").made()
```

- **What it buys:** One object model, Resource orientation and Domain orientation. A channel is one object; a string compared in five modules goes. Each file channel has its own class, so five branching methods become three small classes. The hook channel stops carrying server operations it does not have. An install run and its diagnosis are objects, so a colour is a field and not a word found in text. One way to name a toolset replaces five shapes and three type switches.
- **Cost and risk:** (a) about 18 production files and 10 spec files, 300 to 400 lines, net smaller. (b) 6 production files, 5 spec files, 150 lines. (c) 4 production files, 5 spec files, 250 lines. (d) about 10 production files, 20 or more spec files, 200 lines. Unit tier after each part; then the heavy installer spec, which compares installed file paths byte for byte and shows any path that moved. **Saved files and installed text:** `diagnostics.json` is read by the health band and by people, so its entries and the `exceptions` list keep their shape. In (d), installed skills for tools not on MCP carry the `instantiate` call as text ([files.py](C:\dev\abd-cdd-release-1-2-fixes\harness\installation\files.py)); an old install's skill fails until reinstalled, so the installed text and the function change in the same release. Risks: in (a) agent_tools must still import no publisher; kinds reach it only through `annotation_kinds`, and a slip recreates the cycle the annotations module was made to remove. In (c) the installation card publishes `installer.deployment` as seam with callers in `scripts/`, and *Deployment* was introduced in an earlier round to shrink *Installer*, so this reverses a decision you may remember. In (d) specs that hand in ready-made instances to inject fakes need a path that still takes an instance.
- **Depends on / conflicts with:** (a) before proposal 8 (a). (b), (c), and (d) are independent of each other. Proposal 18 renames *McpServer*, which (d) also touches.
- **Decision:** `[ ] approve  [ ] reject  [ ] change:`

---

## 18. *McpHost* holds a request object, the marketplace is its own object, and a running call answers data

- **Problem today:** *McpHost* ([mcp_server.py:519](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L519)) has 52 methods; nine of them work out who is asking and pass `headers` down ([mcp_server.py:754](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L754) to [mcp_server.py:815](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L815)). *McpServer* ([mcp_server.py:332](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L332)) is not a server but one project's enrolled toolsets, which misleads every reader of `host.checkout_server`. *CddHome* is the runtime record, the server's files, and a Claude Code plugin marketplace at once ([cdd_home.py:133](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\cdd_home.py#L133)), and harness/mcp names the folders of `harness/chat-ui/pane`, `tools/prompt_queue`, and `tools/drawio_viewer` ([cdd_home.py:30](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\cdd_home.py#L30)), so the framework holds paths of modules built on it. *ClaudePlugins* has three near-identical install operations that answer strings ([claude_plugins.py:35](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\claude_plugins.py#L35)). A call still running is answered as a sentence ([mcp_server.py:727](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L727)) that the TypeScript adapter recognises by its opening words ([cdd-connection.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\installation\templates\typescript\cdd-connection.ts)).
- **Class model, with the change marked:**

```diff
@@ (a) harness/mcp/mcp_server.py @@
+class ChatRequest(headers, client_port)        one per request, made by McpHost
+  process: ClaudeChatProcess | None            (was _requesting_process)
+  chat: ChatPointer | None                     (was _requesting_chat)
+  project_for(tool) -> Path | None             (was _requested_project, _folder_the_chat_works_in);
+                                               raises ProjectNotNamed, ProjectIsClaudeSettings
+  tool_request(tool, host) -> ToolRequest
-class McpServer(repo, project)
+class ProjectToolsets(repo, project)           same members: tools, prompts, enroll, start, for_project, restarted, ...
-class McpHost(checkout_server: McpServer)
+class McpHost(checkout_toolsets: ProjectToolsets, lanes: ServerLanes | None = None, home: CddHome | None = None)
-  _requested_project, _folder_the_chat_works_in, _requesting_process, _names_a_project, _requesting_chat,
-  _request_headers, _request_client_port, _current_request, _folder_of_chat
-  route_between_lanes(lanes, home)             (both come through the constructor)
-  _call_sent(arguments, project, tool, chat, answers_a_chat)
+  _call_sent(arguments, project, request: ToolRequest)
@@ (a) harness/agent_tools/tool_call.py @@
 class AnsweringMcpHost (Protocol)
-  checkout_server
+  checkout_toolsets
@@ (b) harness/mcp/cdd_home.py, claude_plugins.py @@
 class CddHome(folder)                          runtime and server files only
+  marketplace: ClaudeMarketplace
-  write_claude_plugin, write_mod_plugins, publish_mods_of, publish_mods_for_chats, board_folder,
-  install_command, take_language_adapters, _publish_mod, _copy_mod, _content_hash, _write_marketplace
-  BOARD_MOD_FOLDER, QUEUE_MOD_FOLDER, DRAWIO_VIEWER, MOD_PARTS
+class ClaudeMarketplace(folder, home)          plugin(name) -> PublishedPlugin; publish_cdd_plugin(server);
+                                               publish_mods(code), publish_mods_for_chats(...)
+class PublishedPlugin(marketplace, name)       the one owner of {name}/.claude-plugin/plugin.json:
+                                               manifest, version, description, publish_from(source, extras)
+class PublishedMods (PUBLISHED_MODS)           register(name, folder_in_checkout, extras); chat-ui and prompt_queue register
 class ClaudePlugins
-  install_board(), install_queue(), install_cdd() -> "installed" | "missing" | "watched"
+  install(plugin: PublishedPlugin) -> PluginInstall(state)
@@ (c) harness/mcp/mcp_server.py, harness/installation/templates/typescript/cdd-connection.ts @@
 class McpHost
-  a _StillRunning answers its message as text only
+  a _StillRunning answers the same text plus structuredContent {"still_running": {"tool", "seconds"}}
-  cdd-connection.ts: text.startsWith(`${tool} is still running after`)
+  cdd-connection.ts: result.structuredContent?.still_running
```

- **What callers write, before and after:**

```python
# before
project = self._requested_project(tool)                 # reads headers found through a context variable
home.write_mod_plugins()
# after
project = request.project_for(tool)
home.marketplace.publish_mods(code)
```

- **What it buys:** Sharper module boundaries and Resource orientation. *McpHost* loses a third of its methods to an object made once per request. *CddHome* does one job, and the manifest path of a plugin is built in one class where two classes build it four times. With the registration, harness/mcp holds no folder path of chat-ui or the tools. Python and TypeScript share the "still running" rule through a data field, not through a sentence's opening words.
- **Cost and risk:** (a) 3 production files plus diagnostics and `__main__.py`, 5 spec files, 200 lines moved and 100 renamed; the mcp card and its three decision records. (b) 5 production files, two registrations, 4 spec files, 250 lines moved. (c) 3 files and 2 specs, 40 lines. Unit tier, then the mcp heavy specs and the lanes heavy spec. Risks: `cdd.restart` re-imports every module of the checkout and keeps the host object, so *ChatRequest* must be made from the re-imported classes as `_call_sent` does now, or a restarted server names chats with stale classes. **The registration in (b) is the risky part:** the marketplace is published from the code the server runs, which may be a pinned copy where the registering modules were never imported in this process; the registration has to be read from that code, or a pinned server publishes no mods. The split of *CddHome* without the registration is safe on its own. In (c) agents still read the sentence, so the text stays; an app built against adapters from an older install keeps the old test until it is reinstalled, so the sentence's opening words must not change in the same release. If only one half of (a) is approved, take *ChatRequest*: it is where the defects have been.
- **Depends on / conflicts with:** Independent. Shares `mcp_server.py` with 17 (d).
- **Decision:** `[ ] approve  [ ] reject  [ ] change:`

---

## 19. Apps and releases leave harness/diagnostics, and an end-to-end run has one model

- **Problem today:** harness/diagnostics holds four jobs: server health and the install probes, the apps ([app.py](C:\dev\abd-cdd-release-1-2-fixes\harness\diagnostics\app.py)), versions and releases, and the test cadence. A module that only wants to register an app imports diagnostics ([files_app.py:7](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\files_app.py#L7), [board.py:14](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\board.py#L14)), and diagnostics registers the Graph app on behalf of harness/graph ([app.py:495](C:\dev\abd-cdd-release-1-2-fixes\harness\diagnostics\app.py#L495)). Separately, an end-to-end run's files are read in three places with rules that already differ: `review.ts` and `report.ts` pass a run's folder into every function and read the same files twice, and Python's *E2eRun* reads them again as untyped dicts ([e2e_review.py:124](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\e2e_review.py#L124)).
- **Class model, with the change marked:**

```diff
@@ (a) harness/diagnostics  ->  harness/apps      (new module: after harness/mcp, before harness/graph) @@
+  App(label, package: AppPackage, page: AppPage), Apps / APPS, AppServer, NodeScript, Npm, AppSources, PortProbe   (moved)
 class AppPackage
+  install(), is_installed, is_current          (moved from App: stamps, npm, build)
-GRAPH_APP                                      (harness/graph registers its own app)
@@ (a) harness/diagnostics  ->  harness/release   (new module) @@
+  CddVersion, CddRelease, ReleaseNotes, GitHubCli                          (moved)
+  Version                                      (renamed from Release)
+class ProjectVersion(pyproject)                read(), write(version): the one reader and writer of the version line
+  TestCadence, TestRun, TestRunner, RunWorktree, DesktopWalkQuestion       (moved)
+  TestRunRecord                                (moved; kept on JsonFile)
@@ (a) harness/diagnostics                        (what stays) @@
   ServerHealth, AgentToolsProbe, GuidanceProbe, ProbeArguments, ProbeOutcome, CallDiagnostics
@@ (b) harness/e2e_review/report/run.ts           (new; imports nothing from report.ts or review.ts) @@
+class SubEpicRuns(dir)                         baseline: Run | undefined; runs: Run[]; accept(run, by)
+class Run(dir)                                 steps: StepRow[]; review; previous; pairsAgainst(other);
+                                               changedAgainst(other); judge(key, verdict, reason);
+                                               recordVerdict(against, key, review); addWalkedStep(step);
+                                               summary -> RunSummary (JSON)
@@ (b) harness/e2e_review/report/review.ts, report.ts @@
-  baselineOf(dir), runsOf(dir), changedPairs(run, against), reviewOf(run), recordVerdict(run, against, key, review),
-  judgeStep(run, key, verdict, reason), openPairs, isReviewed, acceptRun; previousRunOf, checkedRows, readRows, stepPairs
+  review.ts: only the command line (pairs, verdict, judge, walk-step, accept, summary)
+  report.ts: only rendering; reads Run
@@ (b) harness/e2e_review/e2e_review.py @@
 class E2eRun(folder)
-  rows -> list[dict], verdicts -> dict, add_walked_step(key, step, screenshot, verdict, reason) writing the files
+  reads `summary` once through ReportTool (cached in changed.json as today)
 class E2eReview
-  record_verdict(run, step, verdict, reason, cites, step_text, ...)     eight parameters, three branches
+  record_verdict(run, step, verdict, reason, cites, against)            review verdicts only
+  judge_step(run, step, verdict, reason)
+  record_walked_step(run, step, ...)
```

- **What callers write, before and after:**

```python
# before (harness/files_app/files_app.py:7, space/kanban/board_app.py:9)
from harness.diagnostics.app import App, AppPackage, AppPage, AppServer, NodeScript
# after
from harness.apps import App, AppPackage, AppPage, AppServer, NodeScript
```

- **What it buys:** Sharper module boundaries and One object model. harness/diagnostics does one job. A module that registers an app no longer imports the module that diagnoses installs, and harness/graph registers its own app. One model of an end-to-end run, in the language that already renders it, and Python asks it once instead of reading the files a third time.
- **Cost and risk:** (a) about 30 files, mostly moved code and import lines; 150 lines of real change. (b) 7 files, 400 lines. Unit tier; the cadence heavy spec; the e2e report's own specs; one e2e run at the end. **Published and installed names:** MCP names (`app.open`, `cdd-version.check`, `server-health.report`) come from the toolset names and do not change, but the language adapter paths (`@cdd/harness/diagnostics/app`) do, so every app and the mod are rebuilt and reinstalled together. `python -m harness.diagnostics.test_runs` is written in `/release`'s instructions and in `TestRunner.start`; a background test run started by the old server calls the old module path, so the first run after the move may be recorded as abandoned. In (b), splitting `record_verdict` changes a published tool a scheduled background agent calls by name; its prompt changes in the same commit. `server-health.report` reads the latest review after every cdd call and must not start Node, so the summary stays cached in a file. (a) is the largest and least urgent change in its judge's report; it can be done as the move alone first.
- **Depends on / conflicts with:** Independent. Do (a) when no other proposal that edits diagnostics imports is in flight.
- **Decision:** `[ ] approve  [ ] reject  [ ] change:`

---

## 20. space/session splits into modules with one-way dependencies

- **Problem today:** One folder and one card hold eight concepts in 39 production files. Nothing in the session's core needs the viewer's files, format alignment, or validation records, yet `session.py` imports all of them so it can publish their tools, and through them it imports the Render action ([format_alignment.py:35](C:\dev\abd-cdd-release-1-2-fixes\space\session\format_alignment.py#L35)), two practices ([session_file.py:15](C:\dev\abd-cdd-release-1-2-fixes\space\session\session_file.py#L15)), the Generate and Validate actions ([session_probe.py:56](C:\dev\abd-cdd-release-1-2-fixes\space\session\session_probe.py#L56)), and a tool ([open_sessions.py:13](C:\dev\abd-cdd-release-1-2-fixes\space\session\open_sessions.py#L13)).
- **Class model, with the change marked:** no class changes; each line is a folder with its own card, and `->` reads "imports".

```diff
@@ space/session                                (the core that stays) @@
   Session, Sessions, OpenSessions, HeldSessions, SessionListing, SessionRecord, SessionFolder, SessionPaths,
   SessionSaves, AnswerReads, SessionHierarchy, IdeaFile, SessionLog, Handoffs, DecisionRecords, ChatInjections
@@ space/session/practices  -> session          (new module) @@
+  PracticeSessionOutput, FidelitySessionOutput, WrittenFiles, ProposedRoots, PracticeOutputs, GuidanceSelection
@@ space/session/files  -> session, practices   (new module) @@
+  FileManager, SessionFiles, BranchChanges, FileEntry, FileText, SessionFile, Range, FileComments,
+  FileViewFilter, FileGraphs, NodeSpans, SessionExplorer
@@ space/session/validation  -> session         (new module) @@
+  ValidationReports, Judgment, ReportJudgment, ViolationHistory, AcceptedViolations
@@ cdd_guidance/actions/align  -> session, files, render    (new action) @@
+  SessionAlignment, FidelityAlignment, CalloutAlignment and their results     (moved: it runs Render, so it is an action)
@@ cdd_guidance  (diagnostics)  -> session @@
+  SessionProbe, SessionDiagnostics             (moved: they run Generate and Validate)
@@ space/session/spec_support                   (spec files only) @@
+  ThrowawayProject, ExampleHome, OPEN_PROJECTS (moved)
@@ space/kanban  -> session @@
+  BoardPractices, ProgressCache                (moved: the board is their only reader)
@@ space/session/session.py @@
-  imports of format_alignment (-> cdd_guidance.actions.render), session_file (-> two practices), session_probe
```

- **What callers write, before and after:**

```python
# before
from space.session.practice_session_output import PracticeSessionOutput
from space.session.format_alignment import SessionAlignment
# after
from space.session.practices import PracticeSessionOutput
from cdd_guidance.actions.align import SessionAlignment
```

- **What it buys:** Sharper module boundaries. `session.py` stops importing an action or a practice, so the session's core can change and be tested without them. Four concepts each get a card that says what they are for, and each new module is measured for `deep-module` on its own.
- **Cost and risk:** About 45 production files have import lines edited (37 import lines outside the module), several hundred spec references follow (142 name *ThrowawayProject*), four new cards and the split of the current one. No behaviour changes. Best done in four passes (spec support; validation; files; alignment and diagnostics), unit tier after each, heavy tier at the end. **Installed and published names:** the installer finds toolsets by package, so moving *FileManager*, *FileComments*, and the practice output toolsets changes the folder their skills and commands are generated under (the `space-session-*` skill names), unless the installer names them by toolset. Alignment's tools (`session.diagnose_alignment`, `session.align_formats`) become an action's tools unless the session keeps two forwarding tools, which the layer-separation rule argues against. Risks: the new `files` module holds many data classes with public properties and is the one most likely to fail the 35% limit. *ProgressCache* moving to the board needs *SessionSaves* to stop naming its file.
- **Depends on / conflicts with:** After 2, 6, 7, 8 (b), and 13, so the files move once in their final shape. The two smaller changes X1 and X2 (the session's graph, and the log line) fit inside the new modules.
- **Decision:** `[ ] approve  [ ] reject  [ ] change:`

---

## 21. A story file in code is read once, by a thin *Stories*

- **Problem today:** A story test is parsed twice and the two results are joined by position. *StorySyntax* reads the text by regular expression to build stories, scenarios, and steps ([code_story_model.py:86](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\code_story_model.py#L86)); *StoryFile* reads the same text into blocks to attach each node's code ([story_file.py:40](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\story_file.py#L40)); the block type is `Any` ([story_file.py:23](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\story_file.py#L23)). *Stories* itself is about 190 lines of file reading with `project` passed through eleven operations ([stories.py:90](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\stories.py#L90) to [stories.py:278](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\stories.py#L278)), and *StoriesReading* repeats parts of it with its own root. *StoryNode* ([story_model.py:81](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\story_model.py#L81)) is the hierarchy, the kept code, eleven rule facts, and the edit tools, and *EpicColumns*, a drawing concern, sits in the core file ([story_model.py:1513](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\story_model.py#L1513)). The markdown scenarios file keeps its read lines as `object` parts and positional tuples.
- **Class model, with the change marked:**

```diff
@@ (a) cdd_guidance/practices/stories/model/story_file.py, code_story_model.py @@
-CodeBlock = Any
+class StoryBlock (abstract)                    name, line_span, opening_line, is_chained, body, text, keyword,
+                                               description_lines; scenarios(), backgrounds(scenarios), steps(skip), written(lead)
+  BraceBlock(StoryBlock), PythonBlock(StoryBlock)
-class StoryFile(language, content)             story_blocks() -> list | None; stories(story_type, path, project) -> tuple | None
+class StoryFile(model, path, content)          stories -> list[CodeStory]; own_code -> WrittenBlock | None
+  BlockStoryFile: BraceStoryFile, PythonStoryFile
+  ScreenSpecFile(StoryFile), SharedStoryFile(StoryFile)      (readers of their own today)
 class CodeStoryModel
-  story_file(content) -> StoryFile | None; stories_of(content, source_file, project) -> tuple
+  story_file(path, content) -> StoryFile       always answers; picks the kind once
 class CodeStory
-  load_all, load_file, load(content, scenario_blocks), from_block(block, lead, text), read_code(block, lead, scenarios), fill
+  from_block(block: StoryBlock)                builds name, description, backgrounds, scenarios, steps, and code
 class CodeScenario
-  read(body, example_names), read_code(block, lead)
+  from_block(block: StoryBlock)
 class StorySyntax                              (shrinks to example_names, example_imports, story_name, description marks)
-  steps_in, scenario_blocks, backgrounds_in, story_texts, _balanced, _outside_scenarios; the brace and Python call patterns
@@ (b) cdd_guidance/practices/stories/stories.py, model/project_story_files.py @@
 class Stories(PracticeGuidance)
-  read_folder, read_files, open_file, story_tests, story_test_sources, and fourteen private helpers taking project
+  story_files(project, on_file=None) -> ProjectStoryFiles
+class ProjectStoryFiles(formats, project, on_file)
+  code_readers, reader_of(path), story_map_in(folder), story_map_of(files), opened(path),
+  story_tests(written_files) -> dict[Path, list[Story]], sources_of(test), take_code_scenarios(model, edited)
 class StoriesReading
-  _code_readers, _take_code_scenarios          (-> ProjectStoryFiles)
@@ (c) cdd_guidance/practices/stories/model/story_model.py, name_facts.py, diagram_story_model.py @@
 class StoryNode
   name, sequential_order, estimate, description_text, evidence; rename, edit_description, move_before, remove
+  facts: NameFacts
-  opening_token, opening_class, child_count, child_label, child_band, child_target, near_duplicate,
-  generic_handler, shared_verb, artifact_name, camel_case_path; _load_opening, _load_path_case, _load_child_band
-  written, file_written, setup, take_code_from(source)
+class NameFacts(node)                          the eleven facts and load(children)     (in name_facts.py)
+class CodeHeld                                 written, file_written, setup, take_code_from(source)
+                                               (on Epic, Story, Background, Scenario, Step; not on Example, Increment)
 class Epic
-  columns: EpicColumns
+class DiagramEpic.columns; EpicColumns and the _ESTIMATE_* constants move to diagram_story_model.py
@@ (d) cdd_guidance/practices/stories/model/markdown/ @@
+class ReadLine (abstract)                      written() -> str
+  KeptLine(text), HeadingLine(node, said, text), StepLines(owner), ExampleLine(example)
+class ReadScenarioDocument                     lines, holder, tree, examples; text()
 class ScenarioFileReading
-  read() -> sections; eighteen public working fields
+  read() -> ReadScenarioDocument
 class MarkdownScenario, MarkdownStory
-  markdown_heading (tuples of two shapes), markdown_parts: list
+  read_lines: list[ReadLine] | None
-class _SectionLines, _ScenarioDocument; DocumentPart = object; HEADING_LINE, STEP_LINE
```

- **What callers write, before and after:**

```python
# before
stories, written = reader.stories_of(text, file, project)
model = stories_practice.read_files(files, project, on_file=on_file)
# after
story_file = reader.story_file(path, text); story_file.stories; story_file.own_code
model = stories_practice.story_files(project, on_file).story_map_of(files)
```

- **What it buys:** One object model and Resource orientation. One reader of a story test where two are joined by position; about 250 lines removed in (a). The block is a type. *Stories* becomes a thin practice class over one object that owns a project's story files, and the duplicate reader list in *StoriesReading* goes. *StoryNode* holds the story map; rule facts, kept code, and drawing widths move to the parts that use them. A read scenarios file is a list of typed lines.
- **Cost and risk:** (a) about 12 production files, 250 lines removed and 120 added, 10 spec call sites. (b) 5 production files, one new, 200 lines moved. (c) about 8 production files, 150 lines moved, in three separable steps. (d) 4 files, 200 lines rewritten. Unit tier after each part; the Stories round-trip specs; graph heavy specs for (b). No saved file or published name changes. Risks: in (a) the regular-expression path is today the fallback for a file the block reader cannot parse (a Python story test with a syntax error, a file with no `story(...)` block, brace code where a call is not whole). Those three behaviours must be pinned by specs before the path is deleted; if blocks cannot meet them, keep *StorySyntax* as the named fallback and still do the *StoryBlock* base and the *StoryFile* kinds. In (b) *StoriesReading* passes its reading root as "project" while the formats pass the session's repository; where the two differ they must be two named values, or node file paths change and saved graphs stop matching. In (c) if the graph reads facts with `getattr(node, name)`, the eleven names stay readable on the node as delegating properties. In (d) this code guarantees a hand-written scenarios file survives an edit byte for byte; the round-trip specs must pass unchanged, and the rule that an owner's last step line writes every step still pending is easy to lose.
- **Depends on / conflicts with:** After 3 (d) and 11. Before 25, which renames the classes touched here. Proposal 3 (e) wraps *ScenarioFileReading*.
- **Decision:** `[ ] approve  [ ] reject  [ ] change:`

---

## 22. One class-card notation, and a class in code that answers for itself

- **Problem today:** The notation for a class's members (`+ name(args): Type`, `-> callee`, `// note`, `<< kind >>`) is read and written by two practices in two shapes: Clean Engineering's *MarkdownOoadClass* ([markdown_class_model.py:116](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\markdown\markdown_class_model.py#L116)) and DDD's *ClassCard*, `_CardBody`, and `_SketchFence` ([class_cards.py:65](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ddd\model\markdown\class_cards.py#L65)). They already differ, so a card written by one practice and read by the other loses what the reader does not know. Inside Clean Engineering a class in code exists in three shapes: the parsed model object with measures set by `setattr`, the graph node read through 86 string-keyed facts, and `operation_shapes` dicts. *ClassGraph* ([class_graph.py:72](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\class_graph.py#L72)) then offers `fields(node)`, `bases_of(node)`, `operations(node)`, and four more questions that each take the node, and eleven recorder classes loop over nodes.
- **Class model, with the change marked:**

```diff
@@ (a) cdd_guidance/practices/clean_engineering/model/markdown/class_card.py     (new) @@
+class ClassCard(heading: ClassHeading, body_lines)
+  read_into(oclass: OoadClass)                 properties, operations, callees, notes, invariants, arrows
+  lines_of(oclass: OoadClass) -> list[str]
+class SketchFence                              read_into(oclass: OoadClass)
 class MarkdownOoadClass(OoadClass)
-  _read_properties, _read_operations, _member_lines, _property_line, _note_on_property, _note_on_operation
+  read_body / render ask ClassCard
@@ (a) cdd_guidance/practices/ddd/model/markdown/class_cards.py @@
-class ClassCard(MarkdownDomainNode), _CardBody, _SketchFence
 class MarkdownEntity(Entity), MarkdownValueObject, MarkdownRepository, ...     (plain subclasses of the domain classes)
+  DDD keeps what is its own as options of ClassCard: stereotype order, the repository drawn in its root, **Invariants**
@@ (b) cdd_guidance/practices/clean_engineering/reading/  (model/ before proposal 1) @@
-class ClassGraph(reading)                      classes: list[Node]; fields(node), bases_of(node), operations(node),
-                                               has_behavior(node), is_production(node), is_mixin(node); kinds: ClassKinds
+class ProductionClasses(reading)               __iter__ -> ProductionClass; named(type_name); defining(operation_name)
+class ProductionClass                          one per class node: node, fields, bases, operations, has_behavior,
+                                               is_mixin, is_value, is_failure, operation_count, folder
-class ClassKinds
+class ComparedFact(classes) (base)             record()
-class ResourceShapes, ParallelModels, Forwarding, ImportCycleFacts
+class ServicesTakingDataBags, CopiedModels, PassThroughClasses, FolderImportCycles     (renamed for what they find)
+class MeasuredBody (Protocol)                  control_flow_depth(), unnamed_numbers(), catches_everything(), swallows(), ...
 class SourceText, PythonFunctionBody           (both declare MeasuredBody)
 class OoadClass
+  declares method_count, property_names, constructs, prose_comment, prototype_swap     (created by setattr today)
 class ClassSourceFacts, OperationSourceFacts
-  load(): setattr(target, name, fact)
+  load(): assigns declared fields
```

- **What callers write, before and after:**

```python
# before (the shape of a Clean Engineering rule; illustrative)
if class_graph.has_behavior(node) and len(class_graph.operations(node)) > limit: ...
# after
if production_class.has_behavior and len(production_class.operations) > limit: ...
```

- **What it buys:** One object model and Resource orientation. One reader and writer of the card notation; about 150 fewer lines, and a card means the same in both practices. A class in code is an object that answers for itself; the base-name parsing written in three places is written once; hidden attributes become declared fields. It does not remove the string-keyed facts between recorder and rule: the framework saves facts on nodes so a graph read back from JSON can run rules without the source.
- **Cost and risk:** (a) 6 production files, 300 lines removed and 150 added. (b) 12 to 14 production files, 350 lines, in three passes (*ProductionClass*; the recorder base and names; declared fields and *MeasuredBody*). Unit tier; the round-trip specs of both practices; the Clean Engineering rule specs; graph heavy specs for (b). Risks: in (a) the two readers accept slightly different text today, so unifying them changes what some existing domain models parse to; expect a handful of round-trip specs to need a decision (the private-name prefix, where a `//` note is kept). In (b) `operation_shapes` cannot simply go: it lists getters, which the graph holds as property nodes, so *ProductionClass* must read both kinds of member, or the fact keeps its place with a typed shape. *ProductionClass* must stay a view of one node and not collect the recorders' logic; run the metrics gate on each pass.
- **Depends on / conflicts with:** After 1 (the `reading` package) and 3 (b). Proposal 12 (b) puts `take_words_from` on the same model classes.
- **Decision:** `[ ] approve  [ ] reject  [ ] change:`

---

## 23. The TypeScript pages keep their state in objects

- **Problem today:** Four pages pass state between free functions or keep it where a reload loses it. The Story UI keeps three parallel descriptions of a node (the generated data, a view model with no behaviour, and `StoryMapNode(address, kind)` that is told its kind by the caller) joined by thirty-six callbacks and four functions that turn ids back into nodes ([story-map folder](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\app)). The graph explorer page passes its tree, its failures, and its callout scan through free functions ([graph-failures.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\app\graph\graph-failures.ts), [graph-selection.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\app\graph\graph-selection.ts), [source-pane.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\app\explorer\source-pane.ts)). The UX Story Demo runner contains one product's nouns (`paintCharacterTree`, `paintAbilities`, a fixed list of shop session keys) in a 750-line file. The chat mod keeps working state in module variables ([chat-turns.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\chat-ui\pane\hooks\board-chat\chat-turns.ts), [chat-name.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\chat-ui\pane\hooks\board-chat\chat-name.ts), [check-in-client.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\chat-ui\pane\hooks\chat-bar\check-in-client.ts), [prompt-queue.ts](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\prompt-queue.ts)), which the mod pattern forbids because a reload empties them; Python works round it with `ChatMailbox.finish_worked_on` ([chat.py:459](C:\dev\abd-cdd-release-1-2-fixes\harness\chat\chat.py#L459)).
- **Class model, with the change marked:**

```diff
@@ (a) cdd_guidance/practices/stories/app/story-map/ @@
 class StoryMapClient
-  nodeAt(address, kind), exampleAt(address), incrementAt(address), reorder(before, after, kind)
+  epics: EpicOnPage[]; increments: IncrementOnPage[]      built once from each answer
+class StoryNodeOnPage (abstract: map, data)    name, description, rename(name), describe(text), remove(), moveBefore(other)
+  EpicOnPage      subEpics, stories; newSubEpic(name, after?), newStory(name, after?)
+  StoryOnPage     scenarios, acceptanceTests, increment; newScenario(name)
+  ScenarioOnPage  steps, examples; newStep(keyword, text)
+  StepOnPage      keyword, text; editText(text)
+  ExampleOnPage   fields; editField(field, text), remove()
+  IncrementOnPage stories; deliver(story), stopDelivering(story)
-class StoryMapNode, StoryMapExample, StoryMapIncrement; NodeKind, SemanticType, StoryMapViewModel.kinds
-class MapEditing; epicEditsOf, storyEditsOf, scenarioEditsOf, incrementEditsOf; HierarchyEdits (36 callbacks)
 StoryHierarchyView(props)
-  36 callbacks
+  storyMap, view state, edit(change)           each card calls its own node
@@ (b) harness/graph/app/ @@
-class GraphFailures                            api, chat (public); toldChat, toasts, listeners; tellChat
+class GraphFailures extends ChatToldFailures   correct(correction) -> CorrectionOutcome   (was the free function correctInChat)
+class ExplorerTrees(entries)                   withBranch(branch), rulesOf(nodeId), isViolating(entry), entries
-  graph-selection: withBranch, opening, childrenOf, childrenLeftOut, isRule; source-pane: findNode, rulesUnder
+class SourceSpan {file, startLine, text, language}
 class CallCatalog
-  calloutsIn(text, origin, language, stack, file)
+  calloutsIn(span, stack)
+class CalloutScan(catalog, span, stack)        calloutsOn(line, number)
+class OpenCallouts(open, toggle, within, goTo) block, section, and one line of a callout
-  FoldMember (a copy of NodeSourceData)
@@ (c) cdd_guidance/practices/ux/story-demo/mount-generated-mockup.js, paint-reflect.js @@
-  SESSION_KEYS (fixed shop nouns); paintCharacterTree, paintAbilities
+  carried keys come from the page's data-session-keys attribute
+class ProductScreens(root)                     showScreensForStory, showScreen, selectWithinRegion as methods
+class Snapshot(exposed)                        at(path)
+class ControlWiring(mockup)                    the wiring GeneratedMockup holds today
-class PaintReflect                             (forwarded one call; the frame was given every snapshot twice)
@@ (d) harness/chat-ui/pane/types/index.d.ts, hooks/board-chat/, tools/prompt_queue/hooks/queue/ @@
-  let isBusy, turnsStarted, idleTicks; const unfinished: Map          (module variables)
+  'cdd-board'.chatTurns: { isBusy, turnsStarted, idleCheckIns, unfinished }
+  'cdd-board'.chatName: string; 'cdd-board'.failedCheckIns: number
+  every function takes $ and reads or updates the atom
```

- **What callers write, before and after:**

```ts
// before (Story UI)
storyMap.nodeAt(address, 'story').rename(name)
// after
story.rename(name)
```

- **What it buys:** Resource orientation. In the Story UI a node knows its kind and its own operations, so a call such as `newStory` on a step cannot be written; `kinds`, `kindOf`, and thirty-six callbacks go. The explorer page's tree, failures, and callout scan are objects instead of five-parameter chains. The Story Demo runner knows no product. The chat mod's state survives a reload, after which Python's work-round can go.
- **Cost and risk:** (a) the largest view change in the document: 600 to 800 changed lines and most of the app's specs. (b) about 15 files, 300 lines, including `harness/files_app` users of `childrenOf`. (c) 5 JavaScript files, 60 lines deleted and 250 moved. (d) 6 files, 120 lines. Each page's own tests, then e2e. **These are Flow A changes for the screen:** run each page and have a person walk it before the unit specs are trusted; drag and drop in the Story UI has the least unit coverage. Risks: (a) view models are rebuilt on every two-second read, so node objects must not be used as React keys; a filtered epic must still edit the real epic. A smaller first step replaces `nodeAt(address, kind)` with `epicAt`, `storyAt`, `scenarioAt`, `stepAt` returning four small typed classes (about 80 lines). (b) objects rebuilt each render break identity-based memoisation. (c) a mockup outside this repository that relies on `[data-character-tree]` stops painting it. (d) reading an atom is asynchronous, so the once-a-second check-in callback can overlap itself; `isBusy` must be reset on `session.start`, or a mod reloaded mid-turn comes back still busy. `finish_worked_on` stays until a heavy spec shows a reload no longer loses a message.
- **Depends on / conflicts with:** (a) is simpler after 25 and 14. (b) shares the adapter type renamed by 10 (a). Each part is independent of the others.
- **Decision:** `[ ] approve  [ ] reject  [ ] change:`

---

## 24. The board opens the Files app for files, and its own file panel goes

- **Problem today:** The board's page carries a second file viewer of 620 lines (counted: [files-panel-client.ts](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\app\src\kanban\ticket\files-panel-client.ts), [file-viewer-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\app\src\kanban\ticket\file-viewer-view.tsx), [files-panel-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\app\src\kanban\ticket\files-panel-view.tsx), [open-file-comments.ts](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\app\src\kanban\ticket\open-file-comments.ts), [file-views-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\app\src\kanban\ticket\file-views-view.tsx)) beside harness/files_app, and the page's own entry file already says files never open here ([main.tsx:8](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\app\packages\session-board\main.tsx#L8)).
- **Class model, with the change marked:**

```diff
@@ space/kanban/app/src/kanban/ @@
 class EditorAppClient
+  files: AppClientGenerated                    (as graph and kanban are today)
+  openFilesOn(ticket, { fidelities | folder, file, line })     opens the Files app's page on the ticket's session
-class FilesPanelClient                         openFiles, openFolder, openTab, openFileAtLine, togglePractice, toggleRead,
-                                               filterChanged, save, reload, refreshShown
-class OpenFileComments                         add, remove, send, sendOpen, clearProcessed
-  file-viewer-view, files-panel-view, file-views-view
-  BoardStore: FilesPanel, FilesSource, FileReads
-  PageLinks.openFiles, openSessionFolder       (the chat bar links to the Files app)
```

- **What callers write, before and after:**

```ts
// before
page.files.openFileAtLine(file, line)
// after
page.editorApps.openFilesOn(ticket, { file, line })
```

- **What it buys:** One object model. One file viewer. About 620 production lines and 600 spec lines removed, 40 added.
- **Cost and risk:** `board-page.ts`, `page-links.ts`, `side-panels-view.tsx`, `details-view.tsx`, `card-upkeep-view.tsx`, `report-rule-view.tsx`, `board-store.ts`; `linked-files.spec.ts`, most of `side-panel-client.spec.ts`, the files-and-reports tests and story tests. The page's tests, then e2e. **This changes what a person sees:** a file opens in another window, not beside the board, and "open the file at this violation's line" must work in the Files app first (confirm its link takes a line). The other honest option is the reverse: the board embeds the Files app's views. Keeping both viewers is the cost today.
- **Depends on / conflicts with:** Needs your decision on which viewer stays (open questions). Do before 14 (c) to avoid moving prompts in files that are then deleted.
- **Decision:** `[ ] approve  [ ] reject  [ ] change:`

---

## 25. The Stories root class is named *StoryMap*, and each node has one copy path

- **Problem today:** The practice's language is "story map" wherever a person reads it: the fidelity `story_map`, the file `story-map.md`, *OpenedStoryMap*, *StoryMapFiles*, the app's *StoryMapClient*. The root class is *StoryModel* ([story_model.py:1288](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\story_model.py#L1288)), so the published toolset is `story-model.*` beside `epic.*`, `story.*`, and `increment.*`, and nine adapters are named `...StoryModel`. Each node also has a copy-constructor and a `clone()` that list the same fields (about 60 duplicated lines), and the class attributes that say which class to build are named `step_type`, `story_type`, `scenario_type` ([story_model.py:778](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\story_model.py#L778), [story_model.py:1296](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\story_model.py#L1296)) beside the domain values `Step.step_type: StepType` and `Story.story_type: StoryType`.
- **Class model, with the change marked:**

```diff
@@ (a) cdd_guidance/practices/stories/model/story_model.py and every format package @@
 class Scenario
-  __init__(name: str | Scenario, sequential_order)       (a name or a source to copy)
+  __init__(name: str, sequential_order)
+  Scenario.copy_of(source) -> Scenario                   the one field list
   clone()                                                (= type(self).copy_of(self))
   (the same for Story, Epic, Background, Step, Increment, StoryModel)
 class Epic
-  __init__(..., story_class=)                            (the story class comes from the map)
-  step_type = Step; background_type = Background; scenario_type = Scenario
-  epic_type = Epic; story_type = Story (on StoryModel); increment_type = Increment; writing_type
+  step_class, background_class, scenario_class, epic_class, story_class, increment_class, writing_class
   Step.step_type: StepType, Story.story_type: StoryType  (unchanged)
@@ (b) the rename @@
-class StoryModel                               model/story_model.py
+class StoryMap                                 model/story_map.py
-class CodeStoryModel, BraceStoryModel, ScriptStoryModel, PythonStoryModel, TypeScriptStoryModel, JavaScriptStoryModel
+class CodeStoryMap, ...
-class DiagramStoryModel, DrawIOStoryModel, MiroStoryModel, WhiteboardStoryModel
+class DiagramStoryMap, ...
-class MarkdownStoryModel, JsonStoryModel, SketchStoryModel
+class MarkdownStoryMap, ...
-MCP toolset story-model.*                      (story-model.show, story-model.new_epic, story-model.open_in_session, ...)
+MCP toolset story-map.*
```

- **What callers write, before and after:**

```python
# before
copy = Scenario(source_scenario, order)        # a constructor that takes a name or a source
story_model = StoryModel.load(file, call=call) # MCP: story-model.show
# after
copy = Scenario.copy_of(source_scenario)
story_map = StoryMap.load(file, call=call)     # MCP: story-map.show
```

- **What it buys:** Domain orientation. The class and the published tools use the word the practice uses everywhere else. A constructor's `name` is a name; one field list per node where there are two; the class attributes stop sharing names with two domain values.
- **Cost and risk:** (a) about 20 production files, mostly one-line renames, 60 lines removed. (b) 60 or more files: every file in `stories/model`, the Stories app, the UX story canvas, space/kanban, space/session, harness/diagnostics, and every Stories spec. Unit tier, heavy tier, e2e, and a reinstall for every IDE. **Published names change:** saved chats, handoffs, and board comments that name `story-model.*` tools stop resolving, and by the no-legacy rule no alias may be kept. **Saved files:** the semantic type string `"StoryModel"` is saved in graphs, so saved `graph.json` files need a rebuild, or the string is left as it is and becomes a second name. Risks in (a): `Epic(source)` builds each story with the map's story class (converting formats) while `Epic.clone()` keeps each child's own class; they are not the same operation today, and a wrong `copy_of` turns a *MarkdownStory* into a base *Story* on clone, which loses format behaviour silently. This is the costliest proposal for a naming gain; do it at a version boundary, when nothing else is in flight.
- **Depends on / conflicts with:** Last. After 11 and 21, which change the same classes.
- **Decision:** `[ ] approve  [ ] reject  [ ] change:`

---

## Smaller changes

Each stands alone and fits no merged proposal. In the "Class model" column, `-` is removed and `+` is added. Write the numbers you approve after the decision line below.

| # | Change | Class model | Goals served | Size | Risk | Source |
|---|---|---|---|---|---|---|
| X1 | One reader of a single document into a graph, and one owner of the saved graph file (space/session) | `+ SessionGraph(session, practices)`: graph, overlay, forget, saved_file, last_validated, holding(path), listed(paths), as_it_is_now(path). `+ DocumentGraph`: read(folder, path), read_text(practice, text, placed_at). `- FileGraphs`, `- _ComparisonGraph` (a private class; corrected from the report). *PracticeOutputs* renamed *SessionPractices* (every, working, forget) | One object model, Resource orientation | 7 files, 200 lines | Medium: the two classes must share the reentrant lock that makes practices and graph today | space-session 7 |
| X2 | A log line is one object that writes and reads itself | `+ LogLine`: verb, time, paths, practices, fidelities, formats, rules, chat, detail; written; LogLine.read(text); names(fidelity). `- LogEntry`. *ChatLog*'s operations make a *LogLine* | One object model, Resource orientation | 4 files, 150 lines; specs that write log text by hand | Low: old logs hold validate lines with the class name, and the reader must still recognise them | space-session 9 |
| X3 | What a person chose when closing a ticket is an object | `+ Leaving`: writes_handoff, commits, pushes, merges, deletes_branch, deletes_worktree, saves_work, changes_branch, done. `- leaving: list[str]` passed through nine methods of *TicketCheckout*. `Ticket.close(leaving)` keeps its published argument | Resource orientation, Domain orientation | 2 files, 90 lines | Low: an unknown name is refused where it is ignored today; the documented order of the close's steps must stay | kanban 6 |
| X4 | The Backlog owns its folder | `+ BacklogFolder(folder)`: idea_files(). `+ IdeaPlace(file, backlog_folder)`: parent_file, holds_ticket, ticket_folder, is_in_own_folder, move_under(parent), move_out(). `- BoardReads.backlog_items` scan and eight private members of *BacklogItem* | Resource orientation | 3 files, 190 lines | Low: "never delete or write over an idea's file" is kept by the moved code, so move it whole | kanban 7 |
| X5 | `board.py` makes its cards without a registry | `+ column.py`: Column, Backlog, Complete, Stage, Card, RequiredFidelity, BoardFile. `- CardKinds / CARD_KINDS`. `board.py` imports `ticket.py` and `backlog_item.py` directly | Sharper module boundaries | 4 files, 30 import lines | **Recommended: defer.** `Ticket.load`, `Stage.load`, and `BacklogItem.load` still call `Board.load`, so one import inside a function remains, which the rule also counts | kanban 10 |
| X6 | *HookResult* holds its *HookMessages* | `- five copied text attributes on HookResult`; merge, with_description, as_dict read `result.messages` | One object model | 2 files and about 15 readers | Low | harness-lower 12 |
| X7 | A call sent between lanes is typed | `+ ToolCall.as_sent()`, `+ ToolCall.from_sent(sent)`. `- LaneCall dict`; `McpAddress.send_lane_call` takes and answers typed values | One object model | 3 files, 40 lines | Low: `mcp_address.py` must stay standard library only | harness-lower 12 |
| X8 | An annotation records itself | every kind sets the annotation object under its flag and reads `recorded_on(target).name`, `.disabled`, `.names`, `.key`. `- {flag}_name`, `- {flag}_disabled`, `- reference_flag`, `- file_views_flag`, `- companion_flags` | One object model, Resource orientation | 5 files, 80 lines | Low: `annotates` on a class must still ignore an inherited `@hosted_only`; search for code that sets `_hook_disabled` by hand first | harness-lower 12 |
| X9 | Progress belongs to the call | `+ ToolCall.report_progress(message)`. `- progress._reporter`, `- reporting_to`. The one-line function `report_progress(message)` stays for authors | Resource orientation | 4 files, 30 lines | Low: a call made in process with no reporter must stay silent | harness-lower 12 |
| X10 | The thin slice is one layout; Miro reads by position like the other drawn formats | `+ ThinSliceLayout`: columns, lanes, epic_headers(), sub_epic_headers(), draw_on(surface). `- thin_slice_columns / thin_slice_lanes / thin_slice_widths` (tuples), `- _ThinSliceDrawing`, `- _ThinSliceBoard`, `- _MiroReading` | One object model, Resource orientation | 4 files, 160 lines removed, 105 added | Medium: Miro's ids have a different shape, so reading by position may change what existing Miro boards read as; the two pictures must not change | stories A3 |
| X11 | A front-end view hands out its components | *Component* and *ComponentMember* move from `reshaped_view.py` to `front_end_view.py`. `FrontEndView.components -> list[Component]`. `- scanned`, `- declared_components()`, `- taken_apart(opening)`. `+ ViewText.statement_end, top_level_line_starts, function_body_after`. `- ReshapedView.kept / added` as public lists | Resource orientation | 3 files, 120 lines moved, 35 removed | Medium: the two `_statement_end` versions differ on purpose in one detail; pin both with the reshape specs first | stories U3 |
| X12 | One notation for what a screen serves, and navigation kinds as a value | `+ Served`: stories, scenarios, steps, serve(kind, shown), as_lines(link_text), read_lines(lines). `+ NavType`: ACTION, TAB, is_tab, from_drawn(kept, dashed). `- DrawnServed.serve_listed`, `- ServedOnCard`, `- two _SERVED_HEADINGS tables and four separator constants`. `Transition.nav_type: NavType` | One object model, Domain orientation | 6 files, 80 lines removed, 60 added | Low: `nav_type` is saved as a graph fact and in JSON, so *NavType* must write the strings it reads | stories U4 |
| X13 | A *Pattern* class, and fact files that say what they are | `+ Pattern(PracticeGuidance)`: pattern (read from the folder's name), graph_overlay (default), `__init__(format="typescript")`. `- three repeated constructors`. `+ FactFile(relative, text)`: node_type, facts; `+ NodeRootFile, RouteFile, BehaviorFile, StoryTestFile`; `- TierFile`. One module of fact-name constants per pattern | One object model, Resource orientation | 12 files, 350 to 450 lines; the *Pattern* base alone is 5 files and under 60 lines | Low for the base, medium for the split. The ignored pattern imports *TierFile* and gets the rename only | stories R4 |

- **Decision:** `[ ] approve all  [ ] reject all  [ ] approve only:`

---

## New modules and abstractions that do not exist today

The number after each is the proposal that adds it. A name marked "renamed" or "moved" replaces one that exists.

**New modules and packages**

- `cdd_guidance/practices/clean_engineering/reading/` and `cdd_guidance/practices/ddd/reading/` (1)
- `cdd_guidance/practices/source_code/` with `source_text.py` and `test_files.py` (3)
- `cdd_guidance/practices/stories/model/story_tree.py`, a file for the existing *StoryTree* (3)
- `harness/drawio/` (4)
- `cdd_guidance/practices/ux/model/claude_design/fixture_screen.py` and `look.py`, moved from harness/design_canvas (4)
- `harness/git/git_facts.py` and `harness/git/checkout.py` (5)
- `space/session/session_checkout.py` (6)
- `harness/process/server_daemon.py` and `harness/process/lock_file.py` (16)
- `harness/apps/` and `harness/release/` (19)
- `harness/e2e_review/report/run.ts` (19)
- `space/session/practices/`, `space/session/files/`, `space/session/validation/`, `space/session/spec_support/`, and the action `cdd_guidance/actions/align/` (20)
- `cdd_guidance/practices/stories/model/project_story_files.py` (21)
- `cdd_guidance/practices/clean_engineering/model/markdown/class_card.py` (22)
- `space/kanban/column.py` (X5)

**New classes and protocols**

- *CallSession*, *HookSession*, *SessionPaths*, *SessionFiles*, *SessionLog*, *WrittenOutput* (protocols) (2)
- *StepRule*, *DesktopStoryTest*, *CodeFile*, *CodeSpan* (3)
- *ElementId*, *DrawioFile*, *DrawioPage*, *DrawioCell*, *UnreadableDrawio* (one, in harness/drawio), *ClassDiagramPage*, *CanvasVersion*, *CanvasProject*; *PublishedLinks* and *CellStyle* moved (4)
- *GitFacts*, *AskedOfGit*, *Checkout*; *GitFolder* moved (5)
- *SessionFields*, *PracticeFields*, *FidelityFields*, *SelectionFields*, *OwnedFields*, *SessionCheckout*, *StageMark*; *CheckoutWorktrees* renamed from *SessionRoots* (6)
- *RenderPlacement*, *RenderPlace*, *NoSessionOutput* (7)
- *PracticeNodeTypes*, *SchemaRelationship*, *InstalledName* (8)
- *Finding* reshaped from a `str` subclass into a class with a node (9)
- *FilterChoices*, *GeneratedPatterns* (10)
- *Written*, *Rendered*, *RenderResult*, *Migration* (11)
- *ExistingText*, *KeptMark*, *OutlinedMember* (12)
- *ValidationReport*, *HistoryLine* with *RunLine*, *FoundLine*, *FixedLine*, *JudgedLine*, *CheckedFidelity* (13)
- *Work*, *TicketPrompts*, *MainStaysOpenError*; the MCP tool `session.toggle_guidance` (14)
- *SwitchedSession*, harness/chat's *NewChat*, *QueuedPrompt* as a class, *PromptSteps*; *ChatOpener* renamed from *ChatLinks*; *RepositoryChat* renamed from space/repo's *NewChat*; four MCP tools `prompt-queue.move_step`, `remove_step`, `step_back`, `step_on` (15)
- *ServerDaemon*, *LockFile*; *RunningServer* and *ServerDidNotStart* moved to harness/process (16)
- *SkillInstallation*, *CommandInstallation*, *RulesInstallation*, *ChannelServer*, *McpChannelServer*, *StandUp*, *InstallRun*, *Deployed*, *DeployedChanges*, *InstallDiagnosis*; *RegisteredChannel* renamed from *ServerInstallation*; *LanguageAdapters* renamed from *LanguageAdapterInstallation* (17)
- *ChatRequest*, *ClaudeMarketplace*, *PublishedPlugin*, *PublishedMods*, *PluginInstall*; *ProjectToolsets* renamed from *McpServer* (18)
- *ProjectVersion*; *Version* renamed from *Release*; TypeScript *SubEpicRuns*, *Run*, *RunSummary* (19)
- *StoryBlock*, *BlockStoryFile*, *ProjectStoryFiles*, *NameFacts*, *CodeHeld*, *ReadLine* with *KeptLine*, *HeadingLine*, *StepLines*, *ExampleLine*, *ReadScenarioDocument* (21)
- *ClassCard* and *SketchFence* in Clean Engineering, *ClassHeading*, *ProductionClass*, *ComparedFact*, *MeasuredBody*; *ProductionClasses* renamed from *ClassGraph* (22)
- TypeScript *StoryNodeOnPage* with *EpicOnPage*, *StoryOnPage*, *ScenarioOnPage*, *StepOnPage*, *ExampleOnPage*, *IncrementOnPage*; *ExplorerTrees*, *SourceSpan*, *CalloutScan*, *OpenCallouts*; JavaScript *ProductScreens*, *Snapshot*, *ControlWiring*; three atoms of the `cdd-board` mod (23)
- *StoryMap* and its format classes, renamed from *StoryModel* (25)
- *SessionGraph*, *DocumentGraph*; *SessionPractices* renamed from *PracticeOutputs* (X1); *LogLine* (X2); *Leaving* (X3); *BacklogFolder*, *IdeaPlace* (X4); *ThinSliceLayout*, *ThinSliceColumn*, *ThinSliceLane* (X10); *Served*, *NavType* (X12); *Pattern*, *FactFile*, *NodeRootFile*, *RouteFile*, *BehaviorFile*, *StoryTestFile* (X13)

---

## Dropped

One whole proposal was dropped because its premise no longer holds; the other 85 name classes that are there today. The parts below it were dropped, or replaced where two judges disagreed:

| What | From | Why |
|---|---|---|
| One named failure, *UxMapUnreadable*, so the UX reading imports no format package | stories U1 (whole proposal) | Already solved another way while this was written (commit `d67efe74a`): each UX format class now names its own `not_a_map_failures`, and `ux/model/graph_reading.py` imports neither `drawio.nodes` nor `html.nodes`. The cycle the proposal removed is gone. |
| Moving only `card_lines.py` out of Clean Engineering's `model/markdown/` | practices 1, "smallest first step" | Already done by the fixes (commit `c7450f033`). The full move of the reading out of `model/` is kept as proposal 1. |
| Removing `KeptDocument._drawio` and `_whiteboard`, so each practice's adapter alone keeps what a person drew | stories R1, second pass | The premise that the keeping is done twice holds only for adapters that exist today. *KeptDocument* is what keeps a person's cell for an adapter written later, and this branch fixed a defect there in commit 134df3e88. The judge also advised doing only the first pass. |
| A *SessionStage* part in space/session that owns `stage` and `stage_mark` | kanban 1 | Nothing in space/session reads the stage. It stays the board's, written through `record.extra("ticket")` (proposal 6). |
| One wide *WorkedSession* protocol in `harness/agent_tools/tool_call.py` | guidance-graph P9 | It would copy most of *Session*'s interface into the lowest framework module. Replaced by a protocol per layer (proposal 2). |
| A two-file `practices/code_text` module, with *CallGraph* left in Clean Engineering | stories S7 | BDD, the patterns, and space/session also import `script_imports`, `production_code`, and *SourceText*. Replaced by the six-file `practices/source_code` (proposal 3). |
| `board_path()` / `board_key` on *WhiteboardNode*, and `Whiteboard.key(*names)` | stories U7, A2 | Replaced by the *ElementId* value, which also removes the four places that split an id apart (proposal 4). |
| *Drawing* / *Page* / *Cell* as the draw.io class names, and one key length for every practice | practices 5; apps D5 | The names say nothing outside their module; replaced by *DrawioFile* / *DrawioPage* / *DrawioCell*. A single key length would redraw every published Clean Engineering board once. |
| Renaming `enabled` / `enable` to `is_on` / `turn_on` | space-session 4 | It renames a published tool (`practice-session-output.enable`) and a data field every page reads. The cheaper option is taken: keep the published names and rename the three private spellings to match. |
| `queue.queue_once(...)` called from space/session | apps D2 | Replaced by tools/prompt_queue registering with the session (proposal 15), so the session imports no tool. The rest of D2 is kept. |
| `Work.command_in(action, formats)` as a second writer of command text | kanban 5 | One writer, on the session's selection; the board's `Work.command` asks it (proposal 14). |
| Moving every `GitFolder` reader into space/repo's own *GitFacts* | kanban 4 | The interface is kept but lives in harness/git, so the framework's four hand-written readers can use it too (proposal 5). |

Other first slices the fixes already made, with the proposals kept for what remains: Stories' second copy of its step and epic type sets is gone and every link writer is handed the tree (3 d); *WorkedSession* was corrected to match the code (2); the `load` aliases on the drawn story map formats are gone and a whiteboard story map opens (11); `checkout_holding` is one function shared by two framework classes (5); `GuidanceSelection.stages_chosen` is gone (14).

Three statements in the judges' reports were corrected and the proposals kept: the whiteboard element kinds are unexported, not private (4); the five history helpers and `_ComparisonGraph` are private classes (13, X1); `ticket.py` uses the three action-name constants 13 times, not 18 (14).

---

## Open questions for the owner

1. **May harness import space?** AGENTS.md says `harness/` imports nothing from `space/`, `tools/`, or `cdd_guidance/`. The root card `.context/module-context.md` says harness, space, and tools "are the lower layer together and may import each other". The code today follows AGENTS.md (checked: no production file in harness imports space, tools, or cdd_guidance). Proposals 2, 5, and 15 assume AGENTS.md; if it is the rule, the root card's sentence should change.
2. **Which file viewer stays** (24): the Files app, with the board's panel removed, or the Files app's views embedded in the board?
3. **May main's text and tags be edited** (14 c)? The page decided alone that they may not; Python would then enforce it.
4. **Can the session record upgrade be released to both lanes together** (6)? An older server on the stable lane will not find roots saved in the new shape.
5. **The *StoryMap* rename** (25): is a version boundary coming at which `story-model.*` tools may stop resolving? And is the saved type string `"StoryModel"` rebuilt in every `graph.json`, or left as it is?
6. **harness/design_canvas will still fail `deep-module`** after proposal 4 (about 17 of 26 methods are seam), because the module's purpose is a file-layout API. Accept it by a decision record, or go further?
7. **A format adapter that is also an empty domain root** (stories U6, recorded and not proposed): UX and Stories both make the adapter and the map one class. Separate them in both practices, or keep the shape an earlier review accepted?
8. **Clean Engineering's board key length** (4): keep 12 beside the others' 10, or accept one re-layout of published Clean Engineering boards to have one length?
9. **The Graph toolset** (10 b): if a part cannot publish its tools under the name `graph`, accept 16 public operations with the exception recorded on the card?
10. **The prompt queue's budget** (15 c): four new tools take *PromptQueue* to 21 public operations. Accept that, or rename the prompt's tools to `queued-prompt.*`, which every chat and space/session name?
11. **Reversing *Deployment*** (17 c): it was introduced in an earlier round to shrink *Installer*. Is replacing it with *InstallRun* acceptable?
12. **Refusing an unknown close step** (X3): `ticket.close` ignores a misspelt name today. Refusing it is the point of the change and needs announcing.
13. **Prompts on every ticket and violation** (14 c): send them with `board.show` and the report, or answer each from a tool when a button is pressed?
14. **Miro** (X10): may a Miro board read differently after it reads by position, and may its thin-slice column headings change to the shared ones?
15. **MERN** (X13): should it receive LERN's graph rules? Its files are named differently, so sharing the rules is at least the size of X13 again and was not costed.
16. **One resolver from a call to a member** (3 f): three practices' edges will differ in places after it. Who reviews each changed `invokes` edge, and is Stories included or left until Clean Engineering and BDD have held?
