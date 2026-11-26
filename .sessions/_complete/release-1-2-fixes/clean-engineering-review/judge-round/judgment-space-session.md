# Judgment — space/session

Judged on 2026-11-21 against the Clean Engineering rules (modules, model, code) and the refactor guardrails, reading every production file of `space/session` (39 Python files, about 7,700 lines; the area holds no TypeScript). Specs were read only to see how a class is used. Nothing was changed.

Themes: **[1]** module boundaries, **[2]** the same work in different shapes, **[3]** resource orientation, **[4]** domain orientation.

How callers were checked: a script listed every public class, method, and module function of the production files and counted whole-word references in every tracked `.py`, `.ts`, `.tsx`, and `.js` file outside the defining file, split into production code outside the module, production code inside it, and specs. "No caller outside" below means no production reference outside `space/session`; where specs still use a name, the finding says so.

## Findings

### .context/module-context.md and space/session/.context/module-context.md

- .context/module-context.md:7 `Dependencies (one-way)` — one-way-deps — [1] The root card says nothing in harness, space, or tools imports cdd_guidance, while line 20 of the same card says space imports some of it, and `AGENTS.md` says harness imports nothing from space while this line says the three "may import each other". The code follows the second reading (space/session imports cdd_guidance in five files), so the card states two opposite rules and nobody can tell which direction is allowed.
- space/session/.context/module-context.md:40 `Dependencies (one-way)` — seam-names-current-code — [1] The card lists `cdd_guidance/actions` only, but the code also imports `cdd_guidance/practices/stories` and `cdd_guidance/practices/clean_engineering` (session_file.py:14-15, practice_session_output.py:11 and 20, proposed_roots.py:9), `tools/prompt_queue` (open_sessions.py:15), `harness/chat`, `harness/design_canvas`, `harness/whiteboard`, `harness/markdown`, `harness/process`, and `harness/files_app`. A reader of the card believes the module is far less coupled than it is.
- space/session/.context/module-context.md:39 `Seam (terms)` — public-seam-only — [1] The seam names about 75 terms, among them classes no other module uses: `HeldSessions`, `SessionListing`, `ServedAnswers`, `NodeSpans`, `RuleReads`, `LineSpan`, `CommentSending`, `FidelityAnswers`, `InjectedRules`, `FileGraphs`, `GuidanceVersion`. Documenting them as seam promises them to callers and hides which few classes other modules really use (Session, Sessions, PracticeSessionOutput, FidelitySessionOutput, FileEntry, FormatGroup, LogEntry, LogTimestamp, HookLog, IdeaFile, Judgment, AcceptedViolations, ViolationHistory, ValidationRun, SaveFailure, BoardPractices, SessionsRead).
- space/session/.context/module-context.md:2 `space/session` — high-cohesion — [1] One card and one flat folder hold at least eight concepts with their own state and their own readers: the session and its record, the open sessions and saves on main, the session log, practice output and roots, the files a viewer shows (file manager, session file, comments, graph views), format alignment, validation records (history, judgment, accepted violations, progress cache), and spec support (ThrowawayProject). Every feature in any of them edits this one module; see proposal 5.

### space/session/__init__.py

- __init__.py:8 `import harness.files_app.files_app` — low-coupling — [1] The package imports a harness application only so that the application registers itself, which makes importing a session start an unrelated app's registration; `scripts/install.py` then imports `space.session` for that side effect alone. Registration belongs where the server's toolsets are discovered.

### space/session/session.py

- session.py:348 `Session.__init__` — temporal-independence — [3] A session is constructed without its name, record folder, work folder, or workpath, with `ProgressCache(None)` and `handoffs = None`, and `HeldSessions.at` (sessions.py:312-315) then assigns three of them from outside. Between the constructor and those assignments the object is not valid (`latest_handoff` at line 635 and open_sessions.py:149 call `self.handoffs.latest` with no guard).
- session.py:352 `Session.repo` / `Session.repo_path` — use-consistent-naming — [4] The session holds two "projects": `repo`, the Repo of the checkout whose Sessions loaded it, and `repo_path`, which `HeldSessions.placed` later points at the ticket's own worktree. Members then disagree about which one "the project" is: `paths.path_named` and `paths.in_project` resolve against `repo_path` (session_paths.py:68, 84) while `paths.from_project` writes from `repo.root` (session_paths.py:79), so a path named from a worktree does not round-trip.
- session.py:355 `Session.context_config` — hold-state-on-the-object-not-in-parameters — [3] `ContextConfig(self.repo_path)` is made once in the constructor from the loading checkout, and is not made again when `placed` moves `repo_path` to the ticket's worktree, so a ticket read through main's sessions takes its practice folders and default formats from main's `.context/config.json`.
- session.py:361 `Session._make_parts` — hide-inner-details — [1] Sixteen parts are public attributes (`paths`, `record`, `folder`, `hierarchy`, `file_graphs`, `guidance_version`, `decision_records`, `handoffs`, `progress_cache`, `log`, `session_files`, `chat_injections`, `practice_outputs`, `context_config`, `repo`, `repo_path`), and callers in other modules chain through them (`session.record.save_fields(...)` in space/kanban/ticket.py:860 and ticket_checkout.py:122, 161; `session.folder.violation_history` in cdd_guidance/actions/validate/report_files.py:62). Every part's whole public interface is therefore part of the module's seam.
- session.py:363-377 `SessionPaths(self)` … `PracticeOutputs(self)` — shape-classes-around-resources — [3] Twelve parts each take the whole `Session` and call back into its other parts (`SessionFiles` → `session.own_practices` → `PracticeOutputs`; `SessionRecord.saved` → `session.sessions.saves`), while five others take only the folder or file they own (`Handoffs`, `DecisionRecords`, `ProgressCache`, `ViolationHistory`, `AcceptedViolations`) and are rebuilt by the session whenever a folder moves (lines 413, 444-445). Two conventions for "a part of a session" means neither can be relied on.
- session.py:80, 134, 180, 280 `SessionFileTools`, `SessionGuidanceTools`, `SessionLogTools`, `SessionDecisionTools` — layer-separation — [1] Four base classes (six with `SessionExplorer` and `SessionAlignmentTools`) exist only to forward a tool to a part (`folder_files` → `session_files.in_folder()`, `read_loop` → `log.read_loop`), each restating in annotations the attributes it needs from `Session`. File comments, the file manager, and practice output publish their own toolsets instead, so two publishing shapes sit side by side.
- session.py:118 `SessionFileTools.file` — limit-operation-parameters — [3] Six parameters (`path, rules, cross_file, folds, paths, node_filter`), three of them booleans that pick what is read, and `node_filter: dict | None` untyped although harness/graph declares `FilterRequest` (use-typed-signatures). The body repacks them into `RuleReads` and `FileViewFilter` on the next line.
- session.py:125 `SessionFileTools.add_to_chat_context` — keep-operations-single-responsibility — [3] To quote a few lines it builds a whole `SessionFile` (which reads the file, counts its lines, and builds a `FileViewFilter`) and then loads a chat by id string and writes to its mailbox; a `Range` of a file's text does not need the viewer's object.
- session.py:157 `SessionGuidanceTools.set_up_roots` — keep-classes-single-responsibility — [4] The instructions for setting a session's roots sit in the class "that reads and changes a session's guidance selection"; they are about practice output and belong with `fidelity-session-output.propose_roots`.
- session.py:233 `SessionLogTools.write_handoff` — errors-out-of-existence — [3] An empty document, which is a missing required argument, is answered with the sentence "Nothing written: draft the handoff…" as if it were a path, so a caller cannot tell a refusal from a written file; `ChatLog.append_note` (session_log.py:440) does the same.
- session.py:297 `SessionDecisionTools.list_cdrs` — use-typed-signatures — [3] A list of paths is joined into one newline-separated string for the caller to split again; the operation holds a `list[Path]`.
- session.py:268 `SessionLogTools.debug_session` — keep-classes-single-responsibility — [4] A six-step debugging and release procedure (lanes, pull requests, a maintainer's email address) is published from the session log's tools; it is neither about the log nor about a session's state.
- session.py:607-629 `practice`, `practices`, `own_practices`, `practice_outputs.every` — use-intention-revealing-names — [4] Four ways to reach a session's practices: `practices` (only those turned on, and it opens the graph), `own_practices` (every practice, which the data field publishes under the key `practices`), `practice(name)` (either), and `practice_outputs.every`. "Own" says nothing about the difference, and the published `practices` is not the Python `practices`.
- session.py:610 `Session.practice(name)` — hold-state-on-the-object-not-in-parameters — [3] A caller that holds the practice's guidance passes its key back to find the practice again (`self._session.practice(practice.key)`, harness/guidance_actions/guidance_actions.py:508), the lookup by name the guardrails rule out.
- session.py:508 `Session.root` — use-consistent-naming — [4] `root` is a string of `work_root` here, a `Path` of the checkout on `Sessions.root`, a path-from-project string on `PracticeSessionOutput.root`, and the first folder (`Path`) on `FidelitySessionOutput.root`; beside them stand `workpath`, `work_root`, `repo_path`, `record_folder`, `work_folder`, `output_root`, and `folder`. The cards define workpath, work folder, and record folder, but `root` has no single meaning.
- session.py:365 `Session.folder` — use-consistent-naming — [4] `session.folder` is a `SessionFolder` object, `sessions.folder` is the `.sessions` `Path`, and `ThrowawayProject.folder` is a temporary `Path`; the same attribute name gives three kinds of thing on neighbouring objects.
- session.py:594, 536, 671 `accepted_violations`, `idea_file`, `file_comments` — use-explicit-dependencies — [3] Each is built again on every access, while `session.folder.violation_history` (session_folder.py:51) also builds a new `Repo.of_project(...)` each time; the guardrail is "build once, keep it", and four different homes (`session`, `session.folder`, a property, a part) hold what are all "files in the session's folders".
- session.py:673 `from space.session.file_comments import FileComments` — one-way-deps — [1] An import inside a function, justified by "a toolset the module holds at run time would be published again as this toolset's tools", yet line 26 imports the `PracticeSessionOutput` toolset at module level. Either the reason no longer holds or line 26 has the problem; as it stands the dependency is only hidden.
- session.py:650 `Session.choose_workpath` — keep-operations-single-responsibility — [3] It collects each practice's chosen root, moves the workpath, saves, and then writes each root back against the new workpath, because roots are saved relative to a folder that can move; the practice should keep its root in a form that survives the move.

### space/session/sessions.py

- sessions.py:293 `HeldSessions.placed` — put-logic-on-the-owning-resource — [3] Another class sets the session's `repo_path`, `work_folder`, and `workpath` from values `SessionRoots` derives, and the comment requires an order ("The work folder is set before the root, so a graph made again for a new root is kept in the new work folder"). The session is treated as a data bag and an undocumented call order protects its graph (temporal-independence).
- sessions.py:42-75, 110-117 `BoardPractices`, `Sessions.board_practices` — single-boundary — [1] The board's view of each practice (space/kanban's concept, built from harness/catalog_generator) is defined and cached in the sessions module "since the board is made for every call", and `PracticeNotFoundError` says "on the board". Sessions therefore imports the catalog generator and changes when the board does (general-purpose-surface).
- sessions.py:119 `Sessions.file_manager` — eliminate-duplication — [2] A third `FileManager`, beside the two `SessionFiles` holds; CDR 0001 records why and the three steps to one. It still stands, so it is listed here as open rather than new.
- sessions.py:177 `Sessions.with_file(session_file)` — avoid-vague-parameter-names — [4] The parameter is a path to a session.json, an absolute path, or a bare session name (`_is_bare_name`, line 192), so one string means three things and `named(name)` is reachable through a parameter called `session_file`.
- sessions.py:201 `Sessions.create(..., parent: str)` — hold-state-on-the-object-not-in-parameters — [3] The parent is passed as its name although the only production caller, `SessionHierarchy.open_child` (session_hierarchy.py:42), holds the parent session and passes `session.name`.
- sessions.py:173, 256, 270 `self.folder / COMPLETE_FOLDER` — eliminate-duplication — [2] The closed sessions' folder is spelled out five times (also open_sessions.py:95 and session_folder.py:64) while the backlog has `backlog_folder`.
- sessions.py:236 `SessionsRead` — hide-inner-details — [3] A result with two public mutable lists that `read_apart` fills from outside (lines 160-162).
- sessions.py:357 `CallSessions.saved_in` — use-intention-revealing-names — [4] "Saved in project" returns the session a project has open (`current()`); the name comes from harness's `SESSION_OPENING` contract and says nothing about opening.
- sessions.py:104 `Sessions.of_project` — prefer-instance-operations — [3] A class method that returns an object from the process-wide `SERVED_SESSIONS`; the rule allows creation factories and names a global accessor as the case to avoid. Five kanban call sites use it (board.py:116, 130 and three tier files).

### space/session/session_roots.py

- session_roots.py:30, 42, 47, 57 `root_of(session)`, `checkout_of(session)`, `own_worktree_of(session)`, `work_folder_of(session)` — put-logic-on-the-owning-resource — [3] Four operations on a collection-level object each take the session they are about and read its record (`session.record.fields.get("workpath")`, `.get("worktree")`). The session should answer `own_worktree`, `checkout`, and `work_folder` itself, asking its sessions only for the worktree listing.
- session_roots.py:52 `fields.get("worktree")` — single-boundary — [1] The session module reads a `worktree` field that only space/kanban writes (ticket_checkout.py:161 writes `branch` and `worktree` through `record.save_fields`); `Session.branch` (session.py:497) reads `branch` the same way. Two modules share a field of session.json by its string key, with no operation naming the act ("the ticket opened a worktree").
- session_roots.py:85 `word = re.compile(...)` — eliminate-duplication — [2] The pattern "the branch holds the ticket's name as a whole word" is written again in open_sessions.py:127, once to find a worktree for a name and once to find a name for a worktree's branch.
- session_roots.py:96 `except (RuntimeError, OSError)` — never-swallow-exceptions — [3] Any runtime or operating-system failure of `git worktree list` becomes "no worktrees", which then places every ticket in the main checkout; only "this folder is in no repository" is the ordinary case.

### space/session/open_sessions.py

- open_sessions.py:71-77 `OpenSessions.state` — hold-state-on-the-object-not-in-parameters — [3] When no chat is passed it falls back to `CALLS_BEING_ANSWERED.current`, a process-wide "call being answered"; `close(session)` (line 109) always uses that fallback because `Session.close` (session.py:641) is not handed its call. The rule names exactly this: a call nobody hands the value to falls back to a global and acts on the wrong object.
- open_sessions.py:130 `OpenSessions.switch` — keep-operations-single-responsibility — [3] One operation finds the worktree's ticket, creates a session, opens it, queues a handoff's steps on the chat's prompt queue, and builds four notes; it returns all of it as one string of prose, so no caller can tell what happened without reading sentences.
- open_sessions.py:146 `_handoff_queued_note` — use-intention-revealing-names — [4] A method named as "the note" queues prompts on another module's queue (`PromptQueue.of_chat(chat).queue_handoff`), a state change hidden behind a getter-like name.
- open_sessions.py:15 `from tools.prompt_queue.prompt_queue import PromptQueue` — low-coupling — [1] The session module depends on one tool package so that switching can queue prompts; the dependency is not on the card, and it means a session cannot be opened without the prompt queue installed.
- open_sessions.py:22-48 `_OUTSIDE_WORKTREE_NOTE` … `_WORKTREE_TICKET_NOTE` — abstraction-focus — [4] Four paragraphs of agent instructions are Python string constants, while the log's instructions are markdown beside the class (`SESSION-LOG.md`); the framework's own convention is that a class's words live in markdown beside it.
- open_sessions.py:114 `ticket_of_worktree` — hide-inner-details — [1] Public, used only inside this class (two calls); no caller outside.

### space/session/session_record.py

- session_record.py:38, 54 `SessionRecord.fields`, `save_fields(**values: object)` — use-typed-signatures — [3] The whole of session.json is an untyped dict read by string key in about 20 places and written with free keyword arguments by six owners: the session (title, scope, tags, overlays, workpath), the hierarchy (parent, pulled_out), practice output (`practices`, `outputs`), guidance selection (`guidance`), and space/kanban (stage, stage mark, assigned chat, branch, worktree). No object owns the record's shape, so a misspelt key is silently a new field.
- session_record.py:73 `save(... repo_path=str(session.repo_path))` — eliminate-duplication — [3] `save` writes the checkout's absolute path into the record that is committed on main, and no production code reads `repo_path` back (the only other mention is a spec fixture that writes it). It is a machine-specific path in a shared file with no reader.
- session_record.py:64 `ANSWER_READS.begin()` — use-explicit-dependencies — [3] The record reaches a module-level global although its session holds `sessions.answers` (the `ServedAnswers` made for this purpose); `ServedAnswers` itself is only a flag in front of the same global (answer_reads.py:36-56).
- session_record.py:75 `SessionRecord.saved(change)` — put-logic-on-the-owning-resource — [3] `keep_text`, `SessionFolder.keep_file`, `remove`, and `_move_to` each have to remember to call `record.saved(...)` after writing; a write to the record folder that forgets it is never committed on main. The queueing belongs behind the one object that writes the record folder.

### space/session/session_folder.py

- session_folder.py:47 `SessionFolder.violation_history` — keep-classes-single-responsibility — [3] The class that moves a record folder among open, closed, archived, and backlog also names a hook's log and builds the violation history (with a new `Repo.of_project` per access); those two are files of the work folder and have nothing to do with moving the record.
- session_folder.py:83, 110 `session.sessions.held.removed(session)` / `.moved(session, moved_from)` — write-interactions — [3] The folder reaches three objects deep to tell the holder of sessions what it did; the move should be asked of the sessions, which own both the folders and the held objects.

### space/session/session_paths.py

- session_paths.py:70 `SessionPaths.document_named` — seam-names-current-code — [1] harness/guidance declares what it asks of a session in `WorkedSession` (harness/guidance/worked_session.py:35) as `session.document_named(...)`, but the session has no such member; harness calls `session.paths.document_named` (harness/guidance/documents.py:17). The declared contract and the code differ, so the contract checks nothing.
- session_paths.py:25 `SessionPaths.resolved` — keep-classes-single-responsibility — [3] One class names paths from the project, finds the `.context` folder, names the sketch, loads documents, and keeps a cache of resolved paths; the path-naming rules it shares with `SessionFiles.existing` / `from_root` / `in_root`, `FileManager._inside` / `_relative`, `SessionRoots.in_checkout`, and `PracticeSessionOutput.root_named` are spread over five classes.

### space/session/session_files.py

- session_files.py:31 `SessionFiles` — keep-classes-single-responsibility — [2] It holds two file managers, lists three folders (`in_folder`, `in_workpath`, `under_root`), reads and writes, finds by pattern, and checks named paths (`existing`, `from_root`, `in_root`); the graph's count of ten public operations stands.
- session_files.py:50-54, 64 `SessionFiles.file_manager` — use-explicit-dependencies — [3] Every `read`, `write`, and `find` works out the roots again from every practice's `folder`, `output_root`, and `output_folders`, and `output_folders` makes a new `FidelitySessionOutput` for every fidelity (practice_session_output.py:171 through `of_fidelity`, line 80), each of which constructs four more objects. The held file manager is only compared against all that work, not spared it.
- session_files.py:155 `_CHANGED` — hold-state-on-the-object-not-in-parameters — [3] A module-level dict keyed by `(repo.root, session.name)` holds what `BranchChanges` knows; that key is the identity of the one `BranchChanges` each session holds, so the state is the object's field kept in a global.
- session_files.py:148 `path == root or root in path.parents` — eliminate-duplication — [2] "Is this path under one of these roots" is written here, in file_manager.py:286, in practice_session_output.py:507 and 585, and in harness/guidance/declared_outputs.py:157.
- session_files.py:151-159 comment and constants — limit-comments — [4] Two comments describe `UNREAD_FOLDERS` (one stranded above `CHANGED_KEPT_SECONDS`), and `UNREAD_FOLDERS` here and `UNWORKED_FOLDERS` / `holds_work` in file_manager.py:25-32 are two lists of "folders that hold no one's work" with different members.

### space/session/file_manager.py

- file_manager.py:160-172, 204 `LANGUAGES`, `FileText.language` — eliminate-duplication — [2] A second table from file suffix to language beside `Format.from_extension`, which `FileEntry.format` uses 70 lines above (line 136); one file gets its `format` from one table and its `language` from the other.
- file_manager.py:305-308 `FileManager.search_again` — hold-state-on-the-object-not-in-parameters — [3] An instance operation clears `_FILES_UNDER`, a process-wide walk cache shared by every file manager of every session; the object neither owns the state nor limits the effect to itself.
- file_manager.py:42, 100, 176 `FolderEntry`, `FileEntry`, `FileText` (and `SessionFile`, `Range`) — class-not-property-instance-or-subtype — [2] Five shapes of "a file of the session": an entry of a folder (path, size), a declared file (path, exists, changed, link, fidelities), a file's text (path, text, exists, language), the viewer's file (path, text, language, plus annotations), and lines of a file (path, lines, content). `SessionFile` wraps a `FileText` and repeats its `path`, `text`, and `language` (session_file.py:262-275).
- file_manager.py:29 `holds_work` — prefer-class-operations — [3] A module function used only by `Folder.folders` and `FileManager._files_under` in this file.

### space/session/session_file.py

- session_file.py:14-15, 38, 320 `MODULE_FUNCTION_HOLDER`, `Stories`, `CLASS_TYPES` — extensions-live-with-the-domain — [1] The viewer's file names Clean Engineering's and DDD's node types in a literal set, imports the Stories practice to find steps, and knows Clean Engineering's placeholder for a module's functions; node_spans.py:13 adds Stories' `Example`. A new practice or node type changes the session module, and the session depends on two practices by import.
- session_file.py:238 `SessionFile` — keep-classes-single-responsibility — [3] One class reads the text, lists comments, diffs what a chat changed, folds classes, finds story steps, opens callouts from links, and gathers violations from three graphs; the constructor does the file read and raises two refusals.
- session_file.py:247-253 `SessionFile.__init__` — limit-operation-parameters — [3] `RuleReads` is passed in and taken apart into three fields on the next lines; `LineSpan` (file_range.py:22-25) and `CommentSending` (file_comments.py:72-77) are taken apart the same way. Each is an object made to pass fewer parameters and never held, which the rule calls packing the same setup.
- session_file.py:440, 433 `_last_validate`, `_whole` — hide-inner-details — [2] The saved graph's file is located here (`work_folder / GRAPH_FILE_NAME`), again in file_graphs.py:108, and set in practice_outputs.py:61 (`graph.kept_in`); the guardrail is one owner per file. `_whole` also scans the session's whole graph into a `SavedGraph` just to compute `is_held`, which it passes to `FileGraphs.file_in_whole` (file_graphs.py:64), an object that holds the same graph.
- session_file.py:47, 87, 133, 161, 187 `Fold`, `FileCallout`, `FileStep`, `FileChange`, `FileViolation` — eliminate-duplication — [2] Five classes that are each "something on lines of the file" with the same read-only property layout; acceptable as the viewer's data, but each new annotation adds a class, a regex or graph walk in `SessionFile`, and a property.

### space/session/file_range.py, file_view_filter.py, node_spans.py, file_graphs.py, session_explorer.py

- file_range.py:10 `LineSpan` — class-not-property-instance-or-subtype — [3] A class with two public integers whose only job is to keep `Range.__init__` at three parameters; `Range` copies both out again.
- file_view_filter.py:78 `fidelity.session_output.written.holds(file)` — write-interactions — [3] To ask whether any practice declares a file it walks `practice_outputs.every` → each output's `fidelities` (the guidance's) → back to `fidelity.session_output` → `written`; the practice in the session cannot be asked "do you hold this file".
- file_graphs.py:26, 30 `_alone`, `_whole_reads` — use-intention-revealing-names — [3] State is kept as positional tuples (`tuple[list[str], Graph, tuple[Path, float] | None] | None`) that every method unpacks; the "graph one file is read into" is a missing object.
- file_graphs.py:38, 83 `opened()`, `listed(paths)` — temporal-independence — [3] Two notifications that `PracticeOutputs.graph` and `SessionExplorer.graph_trees` must remember to send, or `file_in_whole` and `listed_file_as_it_is_now` compare against stale times.
- file_graphs.py:50-56 `file_alone` — eliminate-duplication — [2] It builds a private `Graph` with new instances of the practices, loads one file, and answers `SavedGraph.from_graph`; `ComparisonGraph.reading` (format_alignment.py:314-336) does the same with its own graph and its own practice instances. With `PracticeOutputs`, three places in the module construct practices and a graph, against the card's "the session's one instance of each practice".
- session_explorer.py:44, 57, 68 `node_filter: dict | None`, `_narrowed_to -> dict` — use-typed-signatures — [3] The graph's `FilterRequest` type exists and file_view_filter.py:28 uses it; these three signatures use a bare dict.
- node_spans.py:21 `NodeSpans(graph, request, root)` — hold-state-on-the-object-not-in-parameters — [3] Made per call from the session's graph and work root by `SessionExplorer.graph_node_ranges` (session_explorer.py:78), then asked `file_of`, then `collect(...).spans` in an order the caller must know.

### space/session/file_comments.py

- file_comments.py:239 `f"session={self.session_file}"` — hold-state-on-the-object-not-in-parameters — [3] The session is written into the prompt as `session=<path>` for the agent to pass back as the `session` argument, the "state written into a string and parsed back" the rule names; it is how a chat learns the session today, so it is reported as the cost of every tool taking `session` as a path.
- file_comments.py:65-77, 136-147 `FileComment` — eliminate-duplication — [2] One comment exists as `CommentRecord` (the JSON shape), `FileComment` (with `_chat`, `_message`, `_sent_text` copied out of the sending), and `CommentSending`; `record` then packs the three back. `FileComment` can hold its `CommentSending`.
- file_comments.py:111 `Chat.load(self._chat).mailbox.message(self._message)` — put-logic-on-the-owning-resource — [3] A data property loads a chat by id on every read of `state`, and `clear_processed`, `send_open`, and `SessionFile.changes` each read it for every comment; the comment reaches two objects into harness/chat to learn whether its message is done.
- file_comments.py:169 `session_file` — eliminate-duplication — [2] Rebuilds `session.session_file_from_project` (session.py:460).

### space/session/practice_session_output.py

- practice_session_output.py:41, 290 `PracticeSessionOutput`, `FidelitySessionOutput` — use-intention-revealing-names — [4] The cards speak of "the practice in the session" (`session.practice("stories")`): whether it is on, its colour, its root, its design view. "Output" names one of its jobs, and the class publishes about thirty members (the graph counts ten operations; that hit stands).
- practice_session_output.py:80 `of_fidelity` — use-explicit-dependencies — [3] Makes a new `FidelitySessionOutput` on each call, while each fidelity keeps the one made at `work_in` (`fidelity.session_output`); `output_folders` (line 171) uses the factory, so two objects describe one fidelity in one session.
- practice_session_output.py:228-240, 362, 371, 392 `keep_fidelity_root(fidelity: str, …)`, `keep_fidelity_roots`, `save(formats=…)` — put-logic-on-the-owning-resource — [3] The fidelity's own roots and formats are saved by its practice, which is handed the fidelity's name to find its entry in a dict, although the docstring at line 291 says the fidelity "reads and saves its own part".
- practice_session_output.py:90-98, 135-142 `saved`, `save(**values)`, `chosen_outputs` — use-typed-signatures — [3] A practice's state sits under two top-level keys of session.json (`practices` for on/off and formats, `outputs` for roots), each an untyped nested dict (`ChosenOutputs = dict[str, object]`); in `outputs` the key `root` shares one dict with fidelity names, and in a fidelity's entry `root` / `roots` share one dict with per-format file names.
- practice_session_output.py:239, 438 `"root"` or `"roots"` — eliminate-duplication — [2] One root is saved as `root` and several as `roots`, and every reader handles both; line 354 likewise still reads a format saved as a string by older sessions (no-legacy-api-after-refactor).
- practice_session_output.py:11, 20, 605-634 `is_test_code`, `STORY_TESTS_FOLDER`, `_under_root`, `_below_named`, `_beside_context` — extensions-live-with-the-domain — [1] Where a declared path goes under a root is decided here with special cases for Stories' `story_tests` folder and for `.context`, and what counts as test code is Clean Engineering's function; the docstring of `ProposedRoots` says "no practice is named in it" while its module imports one.
- practice_session_output.py:442 `WrittenFiles` — keep-operations-single-responsibility — [2] `files()`, `every_file()`, and `has_output()` are three listings of the same declared paths, each pairing `_listed` / `_declared` / `_found_by_pattern` slightly differently, and harness's `DeclaredOutputs.output_paths` / `files` / `has_output` (declared_outputs.py:182-198) forward to them, so one question has two entry points (`fidelity.declared.files()` and `fidelity.session_output.written.files()`; both are used by callers).
- practice_session_output.py:457 `WrittenFiles.output_paths` — seam-names-current-code — [1] harness's `FidelityOutput` contract (worked_session.py:54-61) declares `output_paths`, `files`, and `has_output` on the fidelity's output itself; they are on `.written`, which the contract does not declare and harness calls anyway.
- practice_session_output.py:559 `_declared_files(label, path, changed, searched)` — limit-operation-parameters — [3] `changed` and `searched` are the state of one listing, threaded through three private methods; the graph hit stands, and the missing object is the listing.
- practice_session_output.py:250, 31 `_fixed_folder`, `_OUTPUT_PATTERN_MARKS` — eliminate-duplication — [2] "The folder up to the first part a name or pattern fills in" is worked out here (with `{*?`), in proposed_roots.py:131 `_fixed_head` (with `[{*?]`), and in file_manager.py:276 (with `*?`), and the single-file test at line 602 uses a fourth set (`*{`); harness's `DeclaredFile` already owns a declared path.
- practice_session_output.py:637, 649 `latest_version`, `published_link` — prefer-class-operations — [3] Module functions that take a file and know a design canvas's folder layout and a whiteboard's link file; `published_link` is imported by space/kanban/ticket_choices.py. They belong on the file they describe (`FileEntry`) or on the canvas and whiteboard that own those layouts.
- practice_session_output.py:122, 128, 414 `enabled`, `enable(is_enabled)`, `is_enabled` — use-consistent-naming — [4] One concept has five words: `enabled` / `is_enabled` here, `is_selected` in `PracticeSelection`, `working` in `PracticeOutputs`, and "on" in every docstring and the card. Formats have two: `chosen_formats` / `choose_format` / `is_chosen` against `FormatSelection.is_selected` / `select`.
- practice_session_output.py:35 `REPORT_DATE_FORMAT` — eliminate-duplication — [2] The same format string is `REPORT_STAMP` in violation_history.py:25, and handoffs.py:8 imports this module only for the constant. `"%Y-%m-%dT%H:%M:%SZ"` is likewise written three times (session_log.py:28, violation_history.py:27, accepted_violations.py:16) although `LogTimestamp` is documented as "the one time format".

### space/session/practice_outputs.py and proposed_roots.py

- practice_outputs.py:16 `PracticeOutputs` — keep-classes-single-responsibility — [4] The class holds the practices and also makes, keeps, overlays, and forgets the session's knowledge graph; nothing in its name says "graph", and `session.graph` goes through it.
- proposed_roots.py:115-119 `_declared_files` — eliminate-duplication — [2] Flattens `fidelity.outputs` into declared paths again, which `DeclaredOutputs._files` (harness) already holds as `DeclaredFile` objects; lines 76 and 85 then make a new `DeclaredFile(template)` per use.
- proposed_roots.py:20, 142 `_CODE_EXTENSIONS`, `code_extensions` — put-logic-on-the-owning-resource — [3] Which extensions a code format writes is knowledge of `Format` (harness/markdown), kept here as a module function that practice_session_output.py imports.
- proposed_roots.py:131, 137 `_fixed_head`, `_squashed` — prefer-class-operations — [3] Module functions used only by `ProposedRoots`; the graph hits stand.
- proposed_roots.py:36 `_session` — use-typed-signatures — [3] An untyped property.

### space/session/guidance_selection.py and guidance_version.py

- guidance_version.py:57 `GuidanceVersion.select` — shape-classes-around-resources — [3] The class named for a version number changes the selection (practices, stages, format groups) and saves its fields, while `GuidanceSelection` is a read-only snapshot built anew for every answer (session.py:144, 152, 176; format_alignment.py:484). The state is in one class and the behaviour in another.
- guidance_version.py:47-55 `batch` — hold-state-on-the-object-not-in-parameters — [3] `_is_batched` is set on the session's one shared `GuidanceVersion` for the length of a block and put back afterwards, the "field set on a shared object for one call and restored" the rule names; a change from another chat during the block is silently folded into this one.
- guidance_selection.py:76, 122 `FormatGroup`, `FormatSelection` — eliminate-duplication — [2] `FormatSelection` forwards four properties and `select` to the `FormatGroup` it wraps, and space/kanban's `FormatChoice` wraps the same group a third time; the docstring at line 79 names all three.
- guidance_selection.py:208 `stages_chosen` — eliminate-duplication — [1] No reference anywhere, in production or specs.
- guidance_selection.py:205 `output.guidance.fidelities.entries.values()` — hide-inner-details — [3] The selection reads the collection's storage (`entries`) three objects away; practice_session_output.py:171 does the same.

### space/session/session_log.py

- session_log.py:380, 391 `validation`, `action` — use-consistent-naming — [2] A validate line names the practice by its class (`CleanEngineering`) and an action line by its key (`clean_engineering`); `LogEntry.names` (line 126) accepts either to compensate, and the comment at lines 85-86 records the mismatch instead of removing it.
- session_log.py:82, 382-398 `LogEntry`, `ChatLog.action` — hold-state-on-the-object-not-in-parameters — [3] A line is written by joining parts with spaces in four `ChatLog` methods and read back by splitting on spaces in `LogEntry` (verb, words, stage, `names(fidelity)`), with the two sides sharing no definition of the line. The board decides what work was done from that parse (space/kanban/ticket.py imports `LogEntry`), so a path with a space or a new part changes what the board shows.
- session_log.py:369-452 `if self._log.path is None: return` — eliminate-duplication — [2] Six `ChatLog` methods repeat the guard that `SessionLog.record` already makes through `_is_writable`.
- session_log.py:34 `LoopNotFoundError(detail: str)` — domain-exception-carries-context — [3] Carries only a sentence; the loop asked for and the highest loop marked are not on it.
- session_log.py:219, 280, 297, 323, 337 `error_path`, `append_trace`, `last_loop_number`, `latest_loop_with_entries`, `loop_to_note` — hide-inner-details — [1] Public on `SessionLog`, used only by `ChatLog` in the same file; `seed_first_loop` and `ChatLog.append_note` / `next_loop` are used only inside the module.

### space/session/format_alignment.py and callout_alignment.py

- format_alignment.py:35-36 `Render`, `SAVED_GROUPS` — one-way-deps — [1] The session module imports an action of cdd_guidance at import time so that a session tool can run it; session_probe.py:56-57 imports `Generate` and `Validate` inside a function for the same reason. Actions are built on sessions (they take one), so alignment is an action that sits in the layer below actions.
- format_alignment.py:141 `AlignmentFailure`; callout_alignment.py:29 `CalloutGap` — eliminate-duplication — [2] `AlignmentFailure` (kind, file, message) and `CalloutGap` (kind, file, message) are the same three fields as the core of `AlignmentGap`; `_callout_gap(*gap)` (line 523) converts one into the other. The graph hit on `AlignmentFailure` stands.
- format_alignment.py:72, 509 `AlignmentGap(kind, fidelity: str, …)`, `render.render([gap.fidelity], …)` — hold-state-on-the-object-not-in-parameters — [3] The gap keeps the fidelity's slug, and `align` hands the slug to Render, which finds the fidelity again; `FidelityAlignment` held the `FidelityGuidance` when it made the gap.
- format_alignment.py:509-516 `result["path"]`, `result.get("migrate")`, `each.get("kept")` — use-typed-signatures — [3] What a render saved is read out of untyped dicts by six string keys.
- format_alignment.py:414, 426, 443 `_read`, `_compared`, `_lacks` — limit-operation-parameters — [3] `leading`, `placed_at`, the two files, and their formats are the state of one document being compared, passed through three private methods; the graph hits stand and the missing object is the document (its files by format).
- format_alignment.py:420, 510 `except Exception` — use-exceptions-properly — [3] Every exception type is caught and sorted afterwards by `raised_by_a_bug`; session_probe.py:45 does the same. The render declares its failures, and those types are what should be caught.
- format_alignment.py:343 `FidelityAlignment(fidelity, session, comparison)` — hold-state-on-the-object-not-in-parameters — [3] The session is passed beside a fidelity that already works in it (`fidelity.session_output.practice.session`).
- callout_alignment.py:122 `self._session.file(file).callouts` — keep-operations-single-responsibility — [3] A whole viewer file is built for each checked file to get its callouts, and `FileTooLongToShowError`, a viewer limit, becomes "no callouts", so a long document is reported as aligned.

### space/session/violation_history.py and validation_judgment.py

- violation_history.py:139-140, 266 `HitKey`, `HistoryRuns.hits_of` — hold-state-on-the-object-not-in-parameters — [3] `HitKey` reads a node's name out of the backticks in `hit.subject` with a regex, and `hits_of` puts the name back into backticks (`` f"`{event['node']}`" ``) when it rebuilds a `Violation`, so that `HitKey` can parse it again.
- violation_history.py:98-106 `ValidationRun.fidelity`, `ValidationRun.at` — hold-state-on-the-object-not-in-parameters — [2] A report's fidelity and time are written into its file name by `ValidationReports.new_path` (practice_session_output.py:735) and parsed back here with `rsplit("-", 1)`; space/kanban/report.py does the same for `ReportFile.stamp`. Three classes in three modules (`ValidationReports`, `ValidationRun`, `ReportFile`) each know part of what a validation report is.
- violation_history.py:46 `HistoryEvent` — shape-classes-around-resources — [3] One `TypedDict` with every field optional stands for four kinds of line, built as literals in four places (lines 164, 170-171, 178, 295-299) and read with `event.get("event") == RUN`; `previous["run"]` passes a run around as a dict.
- violation_history.py:212 `self._file.parent.name` — hold-state-on-the-object-not-in-parameters — [3] The history takes its session's name from the name of the folder its file is in.
- violation_history.py:128, 266; validation_judgment.py:72, 104 `Violation(FoundBy(...), …)` — eliminate-duplication — [2] A `Violation` is rebuilt by hand in four places from three sources (a report's listed hit, a history line, a judgment's finding, a noise table entry), each choosing its own empty fields.
- violation_history.py:113, 131, 152, 252, 274 `ListedHit`, `HitKey`, `MeasuredRun`, `HistoryRuns`, `JudgedRun` — hide-inner-details — [1] Five public classes with no reference outside this file, in production or specs.
- violation_history.py:301 `_matching(rule, file, place)` — limit-operation-parameters — [3] `place` packs the line and node of the finding the caller holds; the graph hit stands (pass the finding).

### space/session/progress_cache.py, accepted_violations.py, session_saves.py, answer_reads.py

- progress_cache.py:27 `ProgressCache` — general-purpose-surface — [1] A part of every session that exists for one reader: its docstring is about the board, its three questions (`HAS_OUTPUT`, `VIOLATION_COUNT`, `ACCEPTED_COUNT`) and the keys they are kept under are space/kanban's (ticket.py:1031-1032), and `SessionSaves` knows its file name to keep it out of commits (session_saves.py:20).
- progress_cache.py:55 `of(fidelity: str)` — hold-state-on-the-object-not-in-parameters — [3] Asked by slug by a caller that holds the fidelity (`progress_cache.of(self._fidelity.slug)`).
- answer_reads.py:36 `ANSWER_READS` — use-explicit-dependencies — [3] A process-wide counter; with `SERVED_SAVES`, `SERVED_SESSIONS`, `_GUIDANCE_CHANGED`, `RECORDING`, `_CHANGED`, and `_FILES_UNDER` the module keeps seven pieces of state at module level, against the guardrail "no global current objects".

### space/session/chat_injections.py, session_probe.py, session_diagnostics.py, throwaway_project.py

- chat_injections.py:91 `_retire_shared_inject` — no-legacy-api-after-refactor — [1] On every hook result the session deletes `.cursor/rules/practices/chat-inject.mdc`, a file "older installs" wrote; nothing in the repository writes it any more, and the session module should not know an IDE's install path.
- chat_injections.py:51, 61 `payload.chat_id`, `payload.conversation_id` — use-consistent-naming — [4] The two operations of one class read the chat's id from two different fields of the payload, and take their two parameters in opposite orders (`keep(result, payload)`, `replay(payload, result)`).
- session_probe.py:18 `ProbeReport = dict[str, Any]` — use-typed-signatures — [3] The probe's result is an untyped dict built in three places with the same four keys.
- session_probe.py:40, 56-58 function-level imports — one-way-deps — [1] `Generate`, `Validate`, `Sessions`, and `RepositoryToolsets` are imported inside functions; the dependency on cdd_guidance's actions is real and only moved out of sight.
- throwaway_project.py:122 `ThrowawayProject` — high-cohesion — [1] Spec support (five classes and three module-level singletons that change `CDD_HOME` and `CDD_PROJECT`) is a production file of the session module and is on its seam; 142 spec references and no production one.

## Fixes that change no design

Each of these is local: no class is added or removed and no operation another module calls changes.

1. **Delete `GuidanceSelection.stages_chosen`** (guidance_selection.py:207-209). No caller in production or specs. Risk: none.
2. **Stop saving `repo_path`** in `SessionRecord.save` (session_record.py:73). No production reader. Callers to change with it: `space/kanban/session_board_examples.py:355` writes the same field into a fixture; check `session_spec.py` near line 392 for an expectation on the saved fields. Risk: a session.json already on disk keeps the stale field, which nothing reads.
3. **Move `_fixed_head` and `_squashed` onto `ProposedRoots`** as private methods (proposed_roots.py:131-139). Only `ProposedRoots` calls them. Risk: none.
4. **Make the helper classes of violation_history.py private**: `ListedHit`, `HitKey`, `MeasuredRun`, `HistoryRuns`, `JudgedRun` → leading underscore. No reference outside the file, specs included. The same holds for `CalloutGap` and `CrossingEdge` (callout_alignment.py), `FileLink` (session_file.py), `ComparisonGraph` and `FidelityAlignment` (format_alignment.py), `ServedSaves` (session_saves.py), and `FolderSweeper` and `SpecRunHome` (throwaway_project.py; their module-level instances keep their names). Risk: none; it lowers the module's count of public classes and so its seam.
5. **Make `OpenSessions.ticket_of_worktree` private** (open_sessions.py:114). Two callers, both in the class. Risk: none.
6. **Name the closed sessions' folder once**: add `Sessions.closed_folder` beside `backlog_folder` and use it in sessions.py:173, 256, 270, open_sessions.py:95, and session_folder.py:64. Risk: none.
7. **Write the "branch holds the ticket's name" pattern once** (session_roots.py:85 and open_sessions.py:127), as one private operation of `SessionRoots` that both use. Risk: low; `session_roots_examples.py` and the worktree specs cover both directions.
8. **Use one constant for each time format**: `REPORT_STAMP` (violation_history.py:25) becomes `REPORT_DATE_FORMAT`, moved out of practice_session_output.py into the file that names reports so handoffs.py:8 no longer imports practice output; `HISTORY_TIME` and `ACCEPTED_TIME` are written with `LogTimestamp` (`str(LogTimestamp.now())`). Callers: `scripts/backfill_violation_history.py` imports other names from violation_history, not these. Risk: none; the strings are identical today.
9. **Keep `BranchChanges`' answer on the instance** instead of the module-level `_CHANGED` (session_files.py:155, 180-190). Each session holds one `BranchChanges` for its lifetime and the key is that session's identity. Risk: low; a spec that makes two `Sessions` for one checkout would no longer share the answer, which only costs one more git call.
10. **Type the node filter**: `node_filter: FilterRequest | None` in session.py:118 and session_explorer.py:44, 57, 68 (`_narrowed_to -> FilterRequest`). Risk: the TypeScript adapter the installer writes from these signatures may change its declared type; reinstall and compare the generated client before committing.
11. **Use `session.session_file_from_project`** in `FileComments.session_file` (file_comments.py:169). Risk: none.
12. **Let `FileComment` hold its `CommentSending`** instead of copying `chat`, `message`, and `sent_text` into three fields (file_comments.py:71-77, 136-147), and let `Range` hold its `LineSpan`. Private state only; `record`, `sent_in`, `state`, and the data fields keep their answers. Risk: none.
13. **Pass the finding to `JudgedRun._matching`** in place of `(rule, file, (line, node))` (violation_history.py:292, 301). Risk: none.
14. **Give `LoopNotFoundError` the loop asked for and the highest loop marked** as fields (session_log.py:34, 331-345). Callers: `session_log_spec.py` (one reference) reads the message, which stays. Risk: none.
15. **Use the held `FidelitySessionOutput`** in `PracticeSessionOutput.output_folders` (practice_session_output.py:171: `fidelity.session_output` in place of `self.of_fidelity(fidelity)`). Risk: low; `of_fidelity` stays as the factory `PracticeGuidance.work_in` calls, and `output_folders` is only read after `work_in`.
16. **Remove the repeated `if self._log.path is None` guards** in `ChatLog` (session_log.py:371, 385, 411, 428, 448) where `SessionLog.record` already refuses; keep the one in `tool` that also tests the name. Risk: low; `ChatLog.failure` must still not call `append_trace` for a session without a folder, which `_is_writable` already covers.
17. **Delete `ChatInjections._retire_shared_inject`** (chat_injections.py:49, 91-95) once the owner agrees no supported install still has `chat-inject.mdc`. Callers: `harness/hooks/hook_spec.py:362` has an example for it, deleted with it. Risk: an old Cursor install keeps one stale always-on rule file.
18. **Settle the function-level import of `FileComments`** (session.py:673): confirm with the installer whether a toolset imported at module level is really published twice (line 26 imports `PracticeSessionOutput` that way without harm). If not, import at the top and delete the comment at line 44. Risk: if the comment is right, `file-comments.*` tools would be published a second time under `session`; the install diagnostics show it at once.
19. **Read one field for the chat's id** in `ChatInjections` (lines 51 and 61) and give `keep` and `replay` their parameters in the same order. Callers: `harness/hooks/hook_server.py` (the `is_rules_dump` protocol at line 184 and the two call sites). Risk: low, but it touches the hook server's call sites, so run the hook heavy specs.

## Proposed design changes

### Proposal 1 — A session is made whole and places itself

**Problem.** A `Session` is constructed empty and filled from outside: `HeldSessions.at` assigns `record_folder`, `work_folder`, and `name` (sessions.py:312-315), and `HeldSessions.placed` assigns `repo_path`, `work_folder`, and `workpath` in an order a comment has to protect (sessions.py:293-303). `SessionRoots` answers four questions about a session by taking it as a parameter and reading its record (session_roots.py:30-63). The session holds two projects, `repo` (the loading checkout) and `repo_path` (its own checkout), and `SessionPaths` uses one for `path_named` and the other for `from_project`; `context_config` is made from the first and never follows the second (session.py:352-355).

**Before**

```
Sessions
  repo, root, roots: SessionRoots, held: HeldSessions, listing, answers, opened
HeldSessions
  load(folder) -> placed(at(folder))
  at(folder)            sets session.record_folder, .work_folder, .name
  placed(session)       sets session.repo_path, .work_folder, .workpath   (order matters)
  moved(session, from), removed(session)
SessionRoots
  root_of(session), checkout_of(session), own_worktree_of(session), work_folder_of(session)
  in_checkout(checkout, path), worktree_of(name)
Session(sessions)
  repo (loading checkout)   repo_path (settable)   context_config (made once)
  name, record_folder, work_folder, workpath       (all settable from outside)
  handoffs: Handoffs | None, progress_cache = ProgressCache(None)
```

**After**

```
Sessions
  repo, root, worktrees: CheckoutWorktrees (~ SessionRoots, renamed), held, listing, answers, opened
HeldSessions
  load(folder) -> at(folder).placed()
  at(folder)            ~ Session(sessions, record_folder)
  - placed(session)     → moved to Session.placed()
  moved(session, from), removed(session)
CheckoutWorktrees                       (~ was SessionRoots)
  of_branch(name) -> Path | None        (~ worktree_of)
  in_checkout(checkout, path)
  - root_of, - checkout_of, - own_worktree_of, - work_folder_of   → moved to Session
Session(sessions, record_folder)        ~ constructor takes its record folder; name read from it
  + checkout: Repo            (the one project: its own worktree's Repo, else its sessions')
  - repo, - repo_path         (callers use checkout / checkout.root)
  + own_worktree: Path | None
  + placed() -> Session       (derives checkout, work folder, workpath in the one right order)
  record_folder, work_folder, workpath   ~ read-only to callers; changed by placed(), choose_workpath(), folder moves
  context_config              ~ derived from checkout, made again when checkout changes
  handoffs, progress_cache    ~ always present (work folder is known at construction)
```

**Callers affected.** `session.repo_path` has 9 production uses outside the module (cdd_guidance validate, context setup, harness/guidance_actions, space/kanban) and about 19 `session.repo` / `repo_path` uses inside it; all become `session.checkout` / `session.checkout.root`. `sessions.roots.*_of(session)` has one caller outside the module's own files (the worktree specs use `worktree_of`). `HeldSessions.placed` is called from `Sessions.create`.

**Size.** About 12 production files, 150-200 lines changed; `session_spec.py`, `session_roots_examples.py`, and the board's worktree specs follow (roughly 60 spec lines).

**What could go wrong.** A ticket loaded through main's sessions today names paths from main (`repo.path_from_top`), and the board may rely on that for files in a sibling worktree (they show as absolute paths). Making the session's own checkout the one project changes those names to relative ones; the board's file links and `SessionFiles._from_project` must be checked against a ticket with its own worktree in the heavy tier. `context_config` following the worktree changes which `.context/config.json` a ticket reads, which is the intended fix but a behaviour change.

### Proposal 2 — The session record has typed fields and one writer for each

**Problem.** `SessionRecord.fields` is a bare dict and `save_fields(**values)` takes any key (session_record.py:38, 54). Six owners write it by string key, including space/kanban (`stage`, `stage_mark`, assigned chat, `branch`, `worktree`), and the session module reads `branch` and `worktree` that only kanban writes (session.py:497, session_roots.py:52). A practice's state is split over `practices` and `outputs`, with `root` / `roots` and fidelity names sharing dicts (practice_session_output.py:136-142, 238-240). `repo_path` is written and never read.

**Before**

```
SessionRecord
  fields -> dict                       read by key in ~20 places, 7 lines of them in space/kanban
  save_fields(**values: object)        called by Session, SessionHierarchy, PracticeSessionOutput,
                                       GuidanceVersion, Ticket (StageMarks), TicketCheckout
  save()                               writes name, workpath, repo_path
  saved(change)
PracticeSessionOutput
  saved -> dict, save(**values), chosen_outputs -> dict, _save_chosen_outputs(dict)
```

**After**

```
SessionRecord
  ~ fields: SessionFields              typed: name, title, scope, branch, worktree, workpath, tags,
                                       overlays, parent, pulled_out, guidance: SelectionFields,
                                       practices: dict[str, PracticeFields]
  + extra(owner) -> dict               one named section per outside owner, e.g. extra("ticket")
                                       for stage, stage mark, assigned chat
  ~ save_fields(...)                   private to the module; each owner changes its own typed part
  - save() writing repo_path
PracticeFields                         + one entry per practice: enabled, root,
                                         fidelities: dict[str, FidelityFields]
FidelityFields                         + formats: list[str], roots: list[str], file_names: dict[str, str]
Session
  + work_in_worktree(branch, worktree) (kanban's TicketCheckout calls this in place of save_fields)
PracticeSessionOutput / FidelitySessionOutput
  ~ each reads and saves its own PracticeFields / FidelityFields
  - saved, - save(**values), - chosen_outputs (both), - _save_chosen_outputs
  - keep_fidelity_root, - keep_fidelity_roots     → moved to FidelitySessionOutput.keep_roots(roots)
```

**Callers affected.** space/kanban/ticket.py:831-860 and ticket_checkout.py:62-161 (five places); harness/guidance_actions/guidance_actions.py:665 (dumps `record.fields` as JSON); everything in the module that reads `record.fields.get(...)`.

**Size.** About 10 files, 250-300 lines; the heaviest part is reading old session.json files: `outputs` + `practices`, `root` or `roots`, and a format saved as a string must be read once and written in the new shape (a one-time upgrade on read, then the old keys are deleted, so no second shape stays).

**What could go wrong.** Every ticket on every checkout has a session.json in the old shape, and the record is committed on main and read by older servers on the stable lane. The upgrade must be released to both lanes together or an older server will not find roots saved in the new shape. This is the proposal with the highest migration cost.

### Proposal 3 — One validation report object, and typed history events

**Problem.** A validation report is known in pieces by three modules. `ValidationReports.new_path` writes the fidelity's slug and the time into the file name (practice_session_output.py:731-735); `ValidationRun.fidelity` / `.at` parse them back (violation_history.py:98-106) and so does `ReportFile.stamp` in space/kanban/report.py. The graph saved beside a report is located by `ReportFiles` (cdd_guidance validate) and by `ReportFile` (kanban). The judgment is parsed by `Judgment` / `ReportJudgment` here and read by both the history and the board. History lines are untyped dicts (`HistoryEvent`), and a hit's node name travels through backticks and a regex twice (violation_history.py:139-140, 266).

**Before**

```
ValidationReports(output)         space/session   listed() -> list[Path], new_path() -> Path
ValidationRun(report: Path, hits, scope)          name, fidelity (parsed), at (parsed), covers(hit)
ListedHit, HitKey, MeasuredRun, HistoryRuns, JudgedRun   helpers over dict events
HistoryEvent (TypedDict, all optional)
Judgment, ReportJudgment(text)    space/session   parse the agent's judgment
ReportFile(file, fidelity)        space/kanban    stamp (parsed), has_result, text, report()
ReportFiles(session, fidelities)  cdd_guidance    claims paths, saves report + graph beside, records history
```

**After**

```
ValidationReport(file, fidelity)             + one class, in the session module's validation package
  fidelity: FidelityGuidance                 (held, not parsed from the name)
  made_at: LogTimestamp                      (from the name, parsed in this one place)
  text, saved_graph: Path, has_result
  judgment: ReportJudgment                   (~ Judgment / ReportJudgment unchanged, reached from here)
  hits: list[Violation]                      (from the saved graph; from the markdown only for a rebuild)
ValidationReports(output)
  ~ listed() -> list[ValidationReport]
  ~ new() -> ValidationReport                (~ was new_path)
ViolationHistory
  ~ record(report: ValidationReport, hits, scope)
  ~ events -> list[HistoryLine]              + HistoryLine subtypes: RunLine, FoundLine, FixedLine, JudgedLine
  - ValidationRun                            → merged into ValidationReport
  - ListedHit, - HitKey (→ Violation.history_key or a private key), - MeasuredRun, - HistoryRuns, - JudgedRun
    (their work moves onto ValidationReport and the typed lines)
ReportFile (space/kanban)
  ~ holds a ValidationReport; - stamp, - text, - has_result, - its own saved-graph path
ReportFiles (cdd_guidance)
  ~ asks ValidationReports.new(); saves through the report
```

**Callers affected.** cdd_guidance/actions/validate/report_files.py (claim, save, record), space/kanban/report.py (`ReportFile`), space/kanban/ticket.py (report listing), scripts/backfill_violation_history.py, and the two specs `violation_history_spec.py` and `accepted_violations_spec.py`.

**Size.** About 8 files, 300-350 lines changed, with violation_history.py shrinking; the JSON lines on disk keep their keys, so no history file is rewritten.

**What could go wrong.** The history is append-only and tracked in git; the typed lines must write exactly today's keys or `fixed` matching against earlier lines breaks. `ReportFile.version` (the board's cache key) depends on the report file, its graph, and the folder; moving those onto one object must keep the key's parts or the board's progress cache is worked out again for every ticket once.

### Proposal 4 — The practice and fidelity in a session: one object each, held once, each saving its own state

**Problem.** `PracticeSessionOutput.of_fidelity` makes a new `FidelitySessionOutput` per call while each fidelity keeps another (practice_session_output.py:80; harness guidance.py:438, 629). The fidelity's roots and formats are saved by its practice, which is handed the fidelity's name (lines 228-240, 362-392). Callers reach a fidelity's files two ways, `fidelity.declared.files()` (harness, which forwards) and `fidelity.session_output.written.files()`. harness's written contract for these objects (`worked_session.py`) names members that are elsewhere (`output_paths` on the output, `document_named` on the session). "On" has five names. The folder-up-to-the-first-pattern logic exists four times.

**Before**

```
PracticeSessionOutput(guidance, session)
  enabled, enable(is_enabled), folder, output_root, output_folders, root, is_root_chosen, is_root_default
  of_fidelity(fidelity) -> new FidelitySessionOutput each call
  saved, save(**values), chosen_outputs, keep_root, keep_fidelity_root(name, root), keep_fidelity_roots(name, roots), root_named(path)
FidelitySessionOutput(practice, fidelity)
  formats: FidelityFormats, validation_reports, written: WrittenFiles, proposed_roots
  chosen_formats, choose_format, roots, root, choose_root, add_root, chosen_outputs, is_enabled
WrittenFiles(output)      output_paths(), files(), holds(file), every_file(), has_output(), has_named_output(), has_found_output()
DeclaredOutputs (harness) output_paths(), files(), has_output()  → forward to session_output.written
FidelityOutput protocol (harness)  declares output_paths/files/has_output on the output
```

**After**

```
PracticeSessionOutput(guidance, session)
  ~ is_on, turn_on(is_on)                 (~ enabled / enable; one word, as the card says "on or off")
  + fidelities -> list[FidelitySessionOutput]   (held, made once; ~ was the guidance's collection)
  ~ of_fidelity(fidelity)                 answers the held one
  + holds(file) -> bool                   (any of its fidelities holds the file)
  - keep_fidelity_root, - keep_fidelity_roots   → moved to FidelitySessionOutput
  - saved, - save, - chosen_outputs       (state typed, see proposal 2)
FidelitySessionOutput(practice, fidelity)
  + keep_roots(roots)                     (saves its own roots)
  ~ choose_format                         (saves its own formats)
  written: WrittenFiles                   unchanged members
WrittenFiles
  ~ uses DeclaredFile.fixed_folder        (+ on harness's DeclaredFile; replaces _fixed_folder,
                                           proposed_roots._fixed_head, and the test at line 602)
DeclaredOutputs (harness)
  - output_paths(), - files(), - has_output()   (callers ask fidelity.session_output.written)
     or keep these three and make `written` private; one entry point either way
FidelityOutput / WorkedSession protocols (harness)
  ~ declare what is really called: written.output_paths/files/has_output, session.paths.document_named
```

**Callers affected.** `fidelity.declared.files()` / `output_paths()` has about 12 production callers in cdd_guidance (generate, validate, stories) and space/kanban; `.enabled` / `.enable` are read by the TypeScript adapters as data field and tool names (`practice-session-output.enable`), so the rename changes a published tool and every page that reads `enabled`. If that cost is too high, keep `enabled` / `enable` and rename only `is_enabled`, `working`, and `is_selected` to match it.

**Size.** Without the rename: 6 files, about 150 lines. With it: add the installed clients and pages that read `enabled` (harness/chat-ui, files app, story UI) and their specs, about 15 more files.

**What could go wrong.** `PracticeGuidance.work_in` relies on `of_fidelity` during construction; holding the fidelity outputs must not ask a fidelity for its output before `work_in` has given it. Removing `DeclaredOutputs.files()` touches cdd_guidance widely; the lower-cost option (keep it, hide `written`) removes the double entry point with fewer edits.

### Proposal 5 — Split space/session into modules with one-way dependencies

**Problem.** One folder and one card hold eight concepts (finding under the module card). The dependency directions that already exist inside it are clean enough to draw: nothing in the session's core needs the viewer's files, alignment, or validation records, yet `session.py` imports all of them so it can publish their tools, and through them imports cdd_guidance's Render action and two practices.

**Before**

```
space/session   (39 production files, one card)
  everything imports through session.py; session.py imports format_alignment → cdd_guidance.actions.render,
  session_file → cdd_guidance.practices.{stories, clean_engineering}, open_sessions → tools.prompt_queue
```

**After** (each a folder with its own card; arrows are "imports")

```
space/session                    Session, Sessions, OpenSessions, HeldSessions, SessionListing, SessionRecord,
                                 SessionFolder, SessionPaths, SessionSaves, AnswerReads, SessionHierarchy,
                                 IdeaFile, SessionLog (+ ChatLog, Loop, LogEntry, HookLog, LogTimestamp),
                                 Handoffs, DecisionRecords, ChatInjections
space/session/practices   → session      PracticeSessionOutput, FidelitySessionOutput, WrittenFiles,
                                         ProposedRoots, PracticeOutputs, GuidanceSelection (+ version)
space/session/files       → session, practices
                                         FileManager, SessionFiles, BranchChanges, FileEntry, FileText,
                                         SessionFile, Range, FileComments, FileViewFilter, FileGraphs,
                                         NodeSpans, SessionExplorer
space/session/validation  → session      ValidationReport(s), Judgment, ReportJudgment, ViolationHistory,
                                         AcceptedViolations
cdd_guidance/actions/align → session, files, render
                                         SessionAlignment, FidelityAlignment, CalloutAlignment and their results
                                         (→ moved out of space/session: it runs Render, so it is an action)
cdd_guidance (diagnostics) → session     SessionProbe, SessionDiagnostics (→ moved: they run Generate and Validate)
space/session/spec_support               ThrowawayProject, ExampleHome, OPEN_PROJECTS (→ moved; spec files only)
space/kanban              → session      BoardPractices, ProgressCache (→ moved; the board is their only reader)
```

`Session` keeps `session.practice(name)`, `session.graph`, and the file tools by holding the parts it is given, as it does today; what changes is that the parts' files live in packages whose imports run one way, and `session.py` no longer imports an action or a practice.

**Callers affected.** Every `from space.session.<file> import …` in production (37 import lines outside the module, listed by grep) and in specs (several hundred, mostly `ThrowawayProject`: 142 references). Published tool names change only for alignment (`session.diagnose_alignment` / `session.align_formats` would become an action's tools) unless the session keeps two forwarding tools, which the layer-separation rule argues against.

**Size.** No behaviour changes; about 45 production files have import lines edited, plus four new cards and the split of the current card. Best done in four passes (spec support; validation; files; alignment and diagnostics), unit tier after each.

**What could go wrong.** The installer discovers toolsets by package; moving `FileManager`, `FileComments`, and the practice output toolsets changes the folder their skills and commands are generated under (`space-session-*` skill names), so installed skill names would change unless the installer names them by toolset. The deep-module measure is taken per module, so each new module must itself stay under 35%; `files` (many data classes with public properties) is the one at risk. `ProgressCache` moving to kanban needs `SessionSaves` to stop naming its file (the ignore line would be registered by the board).

### Proposal 6 — The guidance selection holds its state and makes its own changes

**Problem.** `GuidanceVersion.select` changes practices, stages, and format groups, and `GuidanceVersion.save` writes the selection's fields, while `GuidanceSelection` is rebuilt for every answer and only reads (guidance_version.py:42-78; session.py:144-176). The once-per-update version raise is done with a flag on the shared object (`_is_batched`). `FormatSelection` only forwards to `FormatGroup`.

**Before**

```
GuidanceVersion(session)        changed(), save(**values), batch(), select(stages, practices, formats), wait_past(version)
                                _is_batched (set and restored around a block)
GuidanceSelection(session)      version, is_stage_chosen, stages, practices, formats, fidelities, covered, stages_chosen
                                (new object per answer)
FormatGroup(label, offering)    label, offering, formats, is_chosen, choose(is_chosen), in_group(fidelity)
FormatSelection(group)          label, formats, offered, is_selected, select(is_selected)   (forwards)
```

**After**

```
GuidanceSelection(session)      held by the session (session.guidance_selection is the object, not a factory)
  version, is_stage_chosen, stages, practices, formats, fidelities, covered
  + select(stages, practices, formats)     → moved from GuidanceVersion; applies all three, then raises the version once
  + changed()                              → moved; raises the version
  + wait_past(version)                     → moved
  - stages_chosen
  - batch() and the _is_batched flag       (select raises once itself; enable/choose_format called on their own still call changed())
GuidanceVersion                 - removed (its three operations are on the selection)
FormatGroup                     + data fields label, formats, offered, is_chosen   (serves the chat bar directly)
FormatSelection                 - removed
```

**Callers affected.** `session.guidance_version.changed()` in practice_session_output.py:131 and 393; the three tools in `SessionGuidanceTools`; format_alignment.py:484; space/kanban/format_choice.py (already uses `FormatGroup`). The TypeScript adapter reads `formats[].is_selected`; keeping that data field name on `FormatGroup` avoids a page change.

**Size.** 5 files, about 120 lines, net smaller.

**What could go wrong.** Without the flag, `select` must stop `enable` and `choose_format` from raising the version once each; the clean way is for `select` to write the practices' and fidelities' fields itself and raise once, which needs proposal 2's typed fields or a private "save without announcing" path. Done carelessly a page gets several version numbers for one update and redraws several times (harmless but visible).

### Proposal 7 — One reader of a single document into a graph, and one owner of the saved graph file

**Problem.** `FileGraphs.file_alone` and `ComparisonGraph.reading` each build a private `Graph` with new practice instances, load one file, and answer a `SavedGraph` (file_graphs.py:42-56; format_alignment.py:304-336). `FileGraphs` keeps its state in positional tuples and depends on two notifications. The saved graph's path is worked out in three places (session_file.py:440, file_graphs.py:108, practice_outputs.py:61), and `PracticeOutputs` owns the session's graph under a name that does not say so.

**Before**

```
PracticeOutputs(session)   every, working, graph, overlay(overlays), forget()
FileGraphs(session)        opened(), file_alone(path), alone_folder, file_in_whole(path, is_held), listed(paths),
                           listed_file_as_it_is_now(path);  _alone: tuple, _whole_reads: tuple
ComparisonGraph()          reading(practice, text, placed_at), close()
SessionFile                _last_validate reads work_folder / graph.json itself; computes is_held for FileGraphs
```

**After**

```
SessionPractices(session)          ~ was PracticeOutputs: every, working, forget()
SessionGraph(session, practices)   + the session's knowledge graph and its file
  graph, overlay(overlays), forget()
  saved_file: Path, last_validated -> SavedGraph | None       (the one place that names graph.json)
  holding(path) -> SavedGraph      (~ FileGraphs.file_in_whole; works out is_held itself)
  listed(paths), as_it_is_now(path)
DocumentGraph(practice keys)       + a private graph that reads one document at a time
  read(folder, path) -> SavedGraph                 (~ FileGraphs.file_alone)
  read_text(practice, text, placed_at) -> SavedGraph   (~ ComparisonGraph.reading)
FileGraphs                         - removed (split into SessionGraph and DocumentGraph)
ComparisonGraph                    - removed (GraphReading is made from DocumentGraph's answer)
SessionFile                        ~ asks session graph for last_validated and holding(path)
```

**Callers affected.** `session.practice_outputs` (file_view_filter.py, session_explorer.py, callout_alignment.py, session.py), `session.file_graphs` (session_file.py, session_explorer.py), format_alignment.py. No caller outside the module uses either part.

**Size.** 7 files, about 200 lines.

**What could go wrong.** `PracticeOutputs` makes practices and graph under one reentrant lock because the graph asks for the practices while it is made; two classes must share that lock or keep the order, or two calls that first ask at once could make two graphs. The times `FileGraphs` compares (`_opened_at`, modification times) are subtle; they should move unchanged.

### Proposal 8 — Practice knowledge leaves the session module

**Problem.** The session module names practices' own facts: Stories' `story_tests` folder and how a declared path is placed under a root inside it or inside `.context` (practice_session_output.py:605-634), Clean Engineering's test-code test (lines 11, 507; proposed_roots.py:9, 128), the class and member node types a file folds on (session_file.py:38-39), Stories' steps and `Example` type (session_file.py:320; node_spans.py:13), and Clean Engineering's module-function placeholder (session_file.py:330). Each is an import of, or a literal copied from, a practice.

**Before**

```
WrittenFiles._under_root(name, root)       special cases: STORY_TESTS_FOLDER, CONTEXT_FOLDER
WrittenFiles._writes_code_to(file)         is_test_code (clean_engineering)
SessionFile.folds                          CLASS_TYPES, MEMBER_TYPES literals
SessionFile.steps                          graph.practices.loaded(Stories)
NodeSpans._used_from_elsewhere(node)       node.type == "Example"
```

**After**

```
PracticeGuidance (harness/guidance, each practice overrides where it differs)
  + placed_under(declared, root) -> str    (Stories answers the story_tests cases; default: root / declared)
  + is_production_code(file) -> bool       (Clean Engineering's; default: true)
PracticeReading (harness/graph, each practice's graph reading)
  + fold_kinds -> {node type: "class" | "block"}     (Clean Engineering and DDD name theirs)
  + steps_in(file) -> nodes                           (Stories names its steps)
  + is_used_from_elsewhere(node) -> bool              (Stories: an example)
WrittenFiles      ~ asks fidelity.practice_guidance.placed_under / is_production_code
SessionFile       ~ asks each loaded practice's reading for fold kinds and steps
NodeSpans         ~ asks the node's practice
space/session     - imports of cdd_guidance.practices.*
```

**Callers affected.** The five practices (two or three gain an override each), harness/guidance and harness/graph (new members with defaults), and the four session files above.

**Size.** About 10 files, 150 lines, across three areas (harness, cdd_guidance practices, space/session), so it needs the owners of all three.

**What could go wrong.** The `.context` placement case is not any one practice's (every practice's documents go in `.context`), so it stays a default in harness rather than moving to Stories; getting that split wrong changes where documents are written for sessions rooted inside a `.context` folder. Fold kinds read per practice must still give DDD's types when only Clean Engineering is on, if today's literal set was relied on for that.

### Proposal 9 — The log line is one object that writes and reads itself

**Problem.** `ChatLog` writes a line by joining parts with spaces in four methods, and `LogEntry` reads one by splitting on spaces; the board decides what work a ticket has done from `LogEntry.names(fidelity)`. Validate lines and action lines name the practice differently, and the reader accepts both (session_log.py:85-86, 126, 380-398).

**Before**

```
ChatLog      line(text), validation(worked, violations), action(action, paths, worked), guidance_action(...),
             tool(name, paths), note(message, paths), failure(...), next_loop()      → each builds a string
LogEntry(line)   text, time, verb, words, stage, loop_number, names(fidelity)       → splits the string
```

**After**

```
LogLine                               + one class for a line of session.log
  verb, time, paths, practices: list[str] (keys), fidelities, formats, rules, chat: ChatPointer, detail
  written -> str                      (the one place the layout is defined)
  LogLine.read(text) -> LogLine       (the one place it is parsed)
  names(fidelity) -> bool, stage, loop_number
ChatLog      ~ each operation makes a LogLine and hands it to SessionLog.record(line)
             ~ validation writes the practice's key, as action does
LogEntry     - removed (→ LogLine)
```

**Callers affected.** space/kanban/ticket.py (`LogEntry` → `LogLine`), session_probe.py (its check for `"Bdd"` on the validate line becomes `"bdd"`), `session_log_spec.py`, and the board specs that seed log lines as text.

**Size.** 4 production files, about 150 lines; the specs that write log text by hand are the larger part.

**What could go wrong.** Existing logs hold validate lines with the class name; `LogLine.read` must still recognise them or tickets validated before the change show no validate on the board. That is reading old data, not keeping an old API, and can be dropped when logs roll.

### Proposal 10 — Opening a session takes its chat, and answers what happened

**Problem.** `OpenSessions.state()` falls back to a process-wide current call when no chat is passed, and `Session.close` relies on it (open_sessions.py:71-77, 107-112; session.py:641-645). `switch` returns one string in which a refusal ("this chat works in X's worktree"), a side effect ("handoff queued"), and the log's instructions are concatenated, and queues prompts on `tools/prompt_queue` from inside a method named as a note.

**Before**

```
OpenSessions   state(chat=""), name_for(chat=""), open(session, chat=""), current(chat=""), close(session),
               switch(name, workpath, call) -> str
Session.close()                 no call; OpenSessions.close reads CALLS_BEING_ANSWERED.current
```

**After**

```
OpenSessions   state(chat), name_for(chat), open(session, chat), current(chat), close(session, chat)
               ~ chat required (the empty chat stays the checkout's own entry, passed explicitly)
               ~ switch(name, workpath, call) -> SwitchedSession
               - the CALLS_BEING_ANSWERED fallback
SwitchedSession                 + session, opened_in_worktree_of (ticket or none), outside_worktree: Path | None,
                                  default_roots: list[PracticeSessionOutput], latest_handoff: Path | None
                                + instructions -> str   (the prose, written from SESSION-SWITCH.md beside the class)
Session.close(call)             ~ takes the call it answers, as mark_loop and append_log do
Sessions.switch (the tool)      ~ returns switched.instructions; queues the handoff's steps through a registered
                                  "on session opened" seam, so tools/prompt_queue registers with the session
                                  instead of being imported by it
```

**Callers affected.** `sessions.switch` callers that read the string (session_probe.py, agent BDD, the `/switch-session` command — unchanged text), `Session.close` (the tool gains the call the framework already hands to tools; it is the only caller of `opened.close`, session.py:645).

**Size.** 4 files, about 120 lines, plus one markdown file.

**What could go wrong.** Calls that reach `state()` without a chat today (work run in process, hook events) get the checkout's own entry only when they pass the empty chat on purpose; any path that silently relied on the global current call will now open the checkout's session instead of the chat's, so each caller of `current()` and `name_for()` needs checking.

## Graph hits judged noise

| File:line | Rule | Why it is noise |
|---|---|---|
| space/session/file_comments.py:55 | do-not-invent-parallel-object-models | `CommentRecord` is the JSON shape of file-comments.json and `CommentSending` three of its fields as held by a comment; a stored shape and the object read from it are not a parallel model. The real problem beside it is that `FileComment` copies the sending's fields out again (fix 12). |
| space/session/format_alignment.py:167 | do-not-invent-parallel-object-models | `AlignedFile` is a file a render saved and `AlignmentGap` a difference found; they share `file`, `format`, `source` because one is made from the other, not because they model one thing. |
| space/session/format_alignment.py:171 | limit-operation-parameters | A four-field result's constructor; packing two of them into another object would add a class that is taken apart on the next line, as `LineSpan` is. |
| space/session/session_file.py:247 | limit-operation-parameters | Two of the four parameters are already objects with defaults (`RuleReads`, `FileViewFilter`); the count is one over only because the session and path are both needed. The finding that stands here is that `RuleReads` is taken apart, not the count. |

The other eleven hits in the area stand and are in the findings above: `AlignmentFailure` copying `AlignmentGap` (format_alignment.py:141); `PracticeSessionOutput` and `SessionFiles` over the public-operation budget (practice_session_output.py:41, session_files.py:31); the parameter counts of `AlignmentGap.__init__`, `_read`, `_compared`, `_lacks` (format_alignment.py:72, 414, 426, 443), `_declared_files` (practice_session_output.py:559), and `_matching` (violation_history.py:301); and the two module functions of proposed_roots.py (lines 131, 137).
