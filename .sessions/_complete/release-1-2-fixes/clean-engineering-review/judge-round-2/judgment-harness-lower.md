# Judgment: harness lower modules (round 2)

**Area:** `harness/annotations`, `harness/agent_tools`, `harness/drawio`, `harness/git`, `harness/hooks`, `harness/installation` (with the TypeScript template `cdd-connection.ts`), `harness/markdown`, `harness/mcp`, `harness/process`, `harness/whiteboard`: the 52 production files changed since 2026-11-21 (base `66f410de3`), read at `5d16245ff` on release-1-2-fixes.
**Read:** every file in `harness-lower.txt` in full at its current content; the round-1 judgment `judge-round/judgment-harness-lower.md`; the module cards of all ten modules; the Clean Engineering code and model rules, `.claude/rules/coding.md`, and the refactor guardrails.
**Method:** the whole file is judged, not only the lines changed. Each finding names the file and line it was read at. Every "unused", "only specs call it" or "only used inside" claim was checked with a repository-wide grep (`.venv`, `.retired`, installed copies under `.claude/`, generated `language-adapters/` and `oss_portal_domain_driven` left out; specs then checked separately). A finding the first round made on the same file, rule and problem ends with *(still open from round 1)*.

Theme tags: **[1]** module boundaries, **[2]** the same work in different shapes, **[3]** resource orientation, **[4]** domain orientation.

## Counts

- **Files read:** 52 (51 Python, 1 TypeScript).
- **Findings:** 115.
- **Still open from round 1:** 50.
- **Design proposals:** 7.

| Rule | Findings |
|---|---|
| eliminate-duplication | 28 |
| hold-state-on-the-object-not-in-parameters | 10 |
| hide-inner-details | 7 |
| refuse-unreadable-input | 6 |
| extensions-live-with-the-domain | 6 |
| put-logic-on-the-owning-resource | 5 |
| prefer-class-operations | 5 |
| use-typed-signatures | 4 |
| use-consistent-naming | 4 |
| shape-classes-around-resources | 4 |
| make-module-only-operations-private | 3 |
| low-coupling | 3 |
| delete-unused-operations | 3 |
| use-property-not-accessor | 2 |
| use-explicit-dependencies | 2 |
| use-exceptions-properly | 2 |
| temporal-independence | 2 |
| single-boundary | 2 |
| limit-comments | 2 |
| limit-class-methods | 2 |
| keep-operations-single-responsibility | 2 |
| errors-out-of-existence | 2 |
| use-intention-revealing-names | 1 |
| seam-names-current-code | 1 |
| provide-meaningful-context | 1 |
| no-legacy-api-after-refactor | 1 |
| never-swallow-exceptions | 1 |
| limit-operation-parameters | 1 |
| keep-classes-single-responsibility | 1 |
| high-cohesion | 1 |
| deep-module | 1 |

### What the fixes since round 1 ended

Of the round-1 findings on these files, these are gone: `Name.title_words` private; `AnnotationKinds.of_channel` and the five shapes of recorded annotations (an annotation now records itself); `ContextDocument`/`ArgumentDocument`; `InstallDestination` and the channel strings in agent_tools (tools ask `DestinationKind`s); `ToolsetConfiguration` and `instantiate`/`from_items` (one *ToolsetReference*); `ToolCall.session -> Any` (*CallSession*); the two `progress` context variables; `from_claude_chat`/`from_claude_session` duplicated lookup; `_checkout_holding` and the five hand-written `.git` readers (*Checkout*); *HookMessages* copied onto *HookResult* and *HookDaemonIdentity* onto the address; `HookToasts.shown_by`; the two daemon models and the three file locks (*ServerDaemon*, *LockFile*); the empty operations of the hook channel (*RegisteredChannel* with `server`); *Deployment* and the colour parsed back from report text (*InstallRun*, *InstallDiagnosis*); `Installer.install -> Any`; `LastInstall` dict reads; `installer.__all__`; *FileInstallation*'s five `== SKILL` branches (three subclasses); `served_on_mcp`; the `"agent_toolset"` literal twice; *LanguageAdapterInstallation*; the fidelity knowledge in `MarkdownText` and `_skip_fidelity_file`; `named_subsection`; `_extract_fidelity_file`; the race in `child_blocks`; *McpServer* renamed *ProjectToolsets*; the request headers passed down (*ChatRequest*); `_call_sent` with five parameters; *LaneCall*; the still-running sentence parsed in TypeScript (`structuredContent`); *CddHome* as marketplace (*ClaudeMarketplace*, *PublishedPlugin*); the mod folder constants (*PublishedMods*); three near-identical plugin installs (*PluginInstall*); *ServedCheckout*'s repeated steps.

## Findings

### harness/annotations/annotation.py

- annotation.py:27, :44-49 `AnnotationKinds.register` / `withholds_install` — put-logic-on-the-owning-resource — the registry reads `getattr(kind, "channel", "")` and tests `isinstance(kind, OmissionKind) and kind.omits_install` instead of asking the kind (`kind.is_destination`, `kind.withholds_install(target)`), so two rules of a kind of annotation are kept in the list of kinds. [3] (still open from round 1)

### harness/agent_tools/agent_tools.py

- agent_tools.py:130, :135, :687 `AgentToolSetOrigin.session_context`, `pattern`, `AgentToolSet.is_served_on_mcp` — extensions-live-with-the-domain — the base every toolset derives from names a session, a pattern's guideline in `.context/config.json`, and the cdd server; each is a default that harness/guidance, harness/hooks or harness/mcp overrides or reads. (`is_part_of_practice` is gone; `installed_as`, `listed_parts`, `published_name` are neutral hooks and are fine.) [1] (still open from round 1)
- agent_tools.py:1066-1072, :1123-1125, :1136-1140 `AgentTool.kind` — shape-classes-around-resources — the tool's class is repeated as the strings `"tool"` / `"instructions"` / `"none"`, and callers branch on the string: `files.py:121`, `:210`, `mcp_server.py:407`, `diagnostics/guidance_probe.py:119`. [3] (still open from round 1)
- agent_tools.py:166-167 `ToolSetCollection.attach` — eliminate-duplication — it calls `MarkdownCollection.attach(self, instance, name)` unbound on an object that is not a *MarkdownCollection*; the two collection classes still model entries by name, a parent, iteration and attach-to-owner in two modules. [2] (still open from round 1)
- agent_tools.py:1196-1209 `AgentInstructions.members_of`, `member_of`, `provider_of` — put-logic-on-the-owning-resource — none reads the recipe it is on; each answers from its parameter (`ToolsetMembers.of(type(target))`, `target.instruction(member)`). They exist so `recipe.py:372-378` can ask the recipe instead of the target toolset. [3] (still open from round 1)
- agent_tools.py:697-704 `AgentToolSet.session_for` — hold-state-on-the-object-not-in-parameters — the session a board command names travels as a `session` argument whose text is tested for ending in `session.json` and parsed back into a session. [3] (still open from round 1)
- agent_tools.py:1047-1049 `AgentTool.should_log_session_invocation(arguments)` — hold-state-on-the-object-not-in-parameters — its one caller (`log_session_invocation`, :1059) holds the call and hands it `call.arguments`; the `arguments.get("ping") is True` test is the same rule as `mcp_server.py:904`. [3] (still open from round 1)
- agent_tools.py:937 `names_alike` — prefer-class-operations — a module function that holds the one rule of how a client spells a tool name; callers are `AgentTool.is_called` (:996) and `mcp_server.py:486`. [3] (still open from round 1)
- agent_tools.py:692, :697 `AgentToolSet.for_call -> Any`, `session_for -> Any` — use-typed-signatures — *CallSession* now exists (`tool_call.py:25`), and `session_for` answers one, yet both seams still say `Any`; `log_session_invocation` (:1064) then calls `log_tool` on an untyped value. [4]
- agent_tools.py:271-277 `DeclaredMembers._annotated_function` — keep-operations-single-responsibility — walking a class's members writes copied annotation flags onto the function a static or class method wraps, so reading a toolset's members changes a function object other classes share, as a side effect of a read. [3]

### harness/agent_tools/tool_call.py

- tool_call.py:22 `_NO_CHAT = "unknown"` with `chat_pointer.py:18`, `:89-90`, `mcp/scripts/connect.py:29` — eliminate-duplication — "no chat" is spelled `unknown`, `unnamed` and `no-chat`, with a separate list of which spellings count in `chat_pointer.py`, and the literal `"unknown"` written twice more inside `ChatPointer.taken_from`. [2] (still open from round 1)
- tool_call.py:57-58 `AnsweringMcpHost.checkout_toolsets -> Any` — use-typed-signatures — the protocol a diagnostics tool reads the server through leaves its main answer untyped; `diagnostics/agent_tools_probe.py:93`, `:153`, `:171` read `.skipped.as_data` and `.enrolled(...)` on it. [4] (still open from round 1)
- tool_call.py:91-119 `CallsBeingAnswered` / `CALLS_BEING_ANSWERED.current` — hold-state-on-the-object-not-in-parameters — a process-global "the call being answered now" that `progress.report_progress` reads (`progress.py:14`); the guardrails forbid global current objects. Its `answering` also sets `call.reporter = outer.reporter` on a call from outside (:110-111). Round 1's two context variables became one, but the global stays. [3]

### harness/agent_tools/chat_pointer.py

- chat_pointer.py:38, :112, :221-238 `_FOUND_TRANSCRIPTS` — use-explicit-dependencies — a module-level dict keeps what *_ClaudeProjects* found, while a new `_ClaudeProjects()` is made on every lookup; the object that owns the folder holds none of its own state. [3] (still open from round 1)
- chat_pointer.py:41 `ChatPointer` — keep-classes-single-responsibility — one class is the pointer a log line ends with (`in_log_line`, `line_range`, `transcript_text`) and the finder of a Claude Code chat (`taken_from`, `from_request`, `from_claude_chat`, `working_folder`, reading 256 KB of transcript for the last `cwd`). [3] (still open from round 1)

### harness/agent_tools/parameter_schema.py

- parameter_schema.py:21 `is_built_in` — prefer-class-operations — a module function over a class's flags, imported by `agent_tools.py` and `installation/data_class.py`; it reads only its argument. [3]

### harness/drawio/drawio.py

- drawio.py:16 `from harness.whiteboard import Box` — low-coupling — the draw.io module depends on the Claude Whiteboard module for a plain rectangle; *Box* is the geometry both draw in and belongs to neither, so a change to how boards publish data (its `@data_fields`) reaches every draw.io reader. [1]
- drawio.py:73, :132-135 `DrawioCell.element`, `DrawioPage.element` — hide-inner-details — the card says a `.drawio` file is read only through *DrawioFile*, its pages and cells, yet both hand out the raw XML, and practices walk it: `ux/model/drawio/nodes.py:366`, `:371`, `clean_engineering/model/drawio/page/drawio_page.py:33`. [3]
- drawio.py:108-121, :137-158 `DrawioCell.geometry` / `box`, `DrawioPage.cells` / `boxes` — eliminate-duplication — `geometry` and `box` each find `mxGeometry` again; `boxes()` reads `cell.box` twice per cell; `cells` rebuilds every cell on each read, and `cell(id)` scans that rebuilt list, so every lookup reparses the page. [2]
- drawio.py:156, :160 `DrawioPage.boxes()`, `positions()` — use-property-not-accessor — parameterless reads of derived state written as operations beside the property `cells`. [4]
- drawio.py:272-293 with `whiteboard/whiteboard.py:573-594` `KeepsDocumentInDrawing` / `KeepsDocumentOnBoard` — eliminate-duplication — the same two operations with the same steps (parse the text, catch the format's own unreadable error, read or set the kept document, save), written once per format. [2]
- drawio.py:277-282, :288-291 and `whiteboard.py:578-592` `document_kept_in`, `keeping` — errors-out-of-existence — a drawing that cannot be parsed is answered as "keeps no document" (`None`) or passed through unchanged, so a render of a corrupt drawing back into markdown silently drops the prose the drawing should have kept instead of naming the file. [3]

### harness/git/checkout.py and git_facts.py

- git_facts.py:93-95 and :152-154 `GitFolder.head_branch` / `_branch_in` — eliminate-duplication — the same reading of a `HEAD` file (`removeprefix(_SYMBOLIC).removeprefix(_HEADS)` after the same test) written twice, differing only in what a detached head answers. [2]
- checkout.py:44-58, :63 with git_facts.py:76-82, :160-168 — eliminate-duplication — whether `.git` is a file or a folder is read by *Checkout* (`is_clone`, `is_main`, `is_linked_worktree`) and again by *GitFolder* (`main_checkout`, `_own_folder`); `Checkout.main_folder` builds a new *GitFolder* rather than asking its own `facts`, so a reftable checkout takes the files route there and the git route everywhere else. [2]
- git_facts.py:107 `GitFolder.commit_of` — make-module-only-operations-private — public on a seam class; only `head_commit` and `has_ref` in the same class call it. [1]
- git_facts.py:24-55, :76 `GitFacts.head_branch()`, `is_on_branch()`, `head_commit()`, `branch_names()`, `worktrees()`, `common_folder()`, `GitFolder.main_checkout()` — use-property-not-accessor — parameterless facts written as operations, while `checkout` and `is_readable` beside them are properties; callers cannot tell which kind they are asking. [4]
- git_facts.py:236-243 `NoGitFacts.head_branch`, `head_commit` — use-exceptions-properly — a folder that is no clone raises *RepoConnectError* "Cannot connect git", the error for a git that failed to run; the failure "this folder is no checkout" has no name a caller can catch apart. [4]

### harness/hooks/hooks.py and hook_installation.py

- hooks.py:127-141 with hook_installation.py:73-78 — shape-classes-around-resources — a registered hook is a `dict[str, str]` with `event`, `operation`, `ref`, built in *HookInstallation*, written by *HookHandlersFile*, and read back by key in both. [3] (still open from round 1)
- hook_installation.py:112-114 with hook_server.py:493 — eliminate-duplication — "a `postToolUse` hook also answers `stop` and `subagentStop`" is written in the installation and again in the server; `events_served` (hooks.py:98) is where such a rule already lives. [2] (still open from round 1)

### harness/hooks/hook_server.py

- hook_server.py:297, :380 `HookHandler`, `HandlerCatalog`, with hooks.py:127 `HookHandlersFile.handlers` — use-consistent-naming — "handler" means the class that runs one hook, the dicts a file lists, and the hooked operation. [4] (still open from round 1)
- hook_server.py:232, :240-241, :493-494 `HookResult.followup_only` — put-logic-on-the-owning-resource — set from outside in `from_handler` and again by `HookServer.handle_stdin` for stop events, so what the IDE reads back is decided in two places. [3] (still open from round 1)
- hook_server.py:529 `"pong"` — provide-meaningful-context — written out while `mcp_server.py:53` defines `PONG`. [4] (still open from round 1)
- hook_server.py:525-533 `HookServer.diagnose` — delete-unused-operations — no production caller (only `hook_spec.py:613-1000`); the MCP side now reports through *StandUp*, so this dict, built in the same shape as `McpHost.diagnose`, is kept alive by its spec alone. [2]
- hook_server.py:485-488 `HookServer.handle_stdin` — refuse-unreadable-input — an event whose stdin is not JSON or not UTF-8 is answered with an empty *HookResult* (permission `allow`), logged nowhere, so a broken hook command looks like a hook that had nothing to say. [3]
- hook_server.py:25-26 — limit-comments — a comment describing "what loading a toolset by its `module:Class` reference raises" stands above the next class with no constant under it; the constant moved to `AgentToolSet.LOAD_FAILURES`. [4]
- hook_server.py:316-330, :363-364 `HookHandler._pattern_name`, `_guideline_value` — use-consistent-naming — one concept is a `pattern` on the toolset and a `guideline` in *ContextConfig*. [4] (still open from round 1)
- hook_server.py:301-306, :387-392, :420 `HookHandler.repo_root`, `HandlerCatalog.repo_root` — hold-state-on-the-object-not-in-parameters — the checkout is handed to the catalog, which hands it to every handler (`self.repo_root or Path()`), while *HookServer* holds it as `_repo_root` too; three objects hold one fact, and the catalog's default of the current folder is a guess. [3]

### harness/hooks/hook_daemon.py

- hook_daemon.py:71-81 `_server_named_by`, `_fields_of` — prefer-class-operations — module functions that turn the daemon's published fields into a *RunningServer* and back; they belong to *HookDaemonAddress* (or the address file), which every caller already holds. [3]
- hook_daemon.py:140-147 `HookDaemonAddressFile._fields` — refuse-unreadable-input — an address file that is not JSON is read as `{}`. The comment gives the reason (a daemon writing it), but the next start then treats the checkout as having no daemon; a retry on the race, as `JsonFile._text` does for a refused read, would keep the rule. [3]
- hook_daemon.py:208-210 `_Serving.handle` — errors-out-of-existence — the result of `self._loaded.wait(_CALL_TIMEOUT_SECONDS)` is ignored; when the hook server has not loaded in ten minutes, `self._server` is `None` and the `AttributeError` reaches the hook command as a dropped connection, not as a failure that says the server never loaded. [3]
- hook_daemon.py:351 `HookDaemon.claim_port` — make-module-only-operations-private — public, called only by `serve` (:335) and by `hook_daemon_spec.py` / `hook_daemon_heavy_spec.py`. [1] (still open from round 1)

### harness/process

- claude_chat_process.py:25, :173-183 — eliminate-duplication — `_PORT_BITS` and the inner `TcpRow` structure repeat `process.py:60` and `process.py:65 _TcpRowOwnerPid`; Windows' TCP table is declared and read twice in one module. [2] (still open from round 1)
- claude_chat_process.py:43, :48 `claude_config_folder`, `is_desktop_spare` — prefer-class-operations — two module functions about one folder, imported by `agent_tools/chat_pointer.py`, `mcp/mcp_server.py` and `scripts/install.py`; the folder has no object. [3] (still open from round 1)
- answer_reads.py:12-78 `AnswerReads`, `ServedAnswers`, `HeldForAnswer` — extensions-live-with-the-domain — a cache of what sessions read, whose docstrings speak of sessions, `session.json` and *CallSessions*; its only users are space/session (`sessions.py:52`, `practices/guidance_selection.py:170`, `practices/practice_session_output.py:45`). The framework's process toolkit holds a concept of the module above it. [1]
- answer_reads.py:36, :50, :56 `ANSWER_READS` — use-explicit-dependencies — *ServedAnswers* reaches the process-global counter instead of being handed it, and `AnswerReads.current` is a global "current" the guardrails forbid. [3]
- answer_reads.py:67 `HeldForAnswer.get(answer, read)` — hold-state-on-the-object-not-in-parameters — every read hands the holder the answer number and the reading function; the holder could hold its *ServedAnswers* and its reader, so a caller cannot pass another session's answer. [3]
- server_daemon.py:24-28 `RunningServer.projects` — delete-unused-operations — filled by `McpDaemon.running` and read only by `mcp_server_host_heavy_spec.py:265`; the docstring says it is "the cdd server's only", a field of one subclass kept on the shared record. [2]
- lock_file.py:17 `_takes_operating_system_lock` — prefer-class-operations — a module function only *LockFile._claimed* calls. [3]
- log_timestamp.py:58 `REPORT_DATE_FORMAT` — extensions-live-with-the-domain — the file-name stamp of a validation report and a handoff (validate and space/session's concepts) kept in the process toolkit. [1]

### harness/installation/destination.py and install_target.py

- destination.py:87-91 `Installation.install` / `write` — eliminate-duplication — `install(tool)` only calls `write(tool)`; callers use `install`, subclasses override `write`. [2] (still open from round 1)
- install_target.py:13, :69 with destination.py:33, installer.py:180, scripts/install.py:136 — eliminate-duplication — "is this install in the temporary folder" is a module function, a property of *InstallTarget*, and an attribute set on every *InstallPlace*; *InstallRun* calls the function on `installer.path` though it holds the target. [2] (still open from round 1)
- installer.py:66-72 with destination.py:24-34 — eliminate-duplication — *InstallChannels* hands the same `(target, record, repository)` to five constructors, and each installation *is* an *InstallPlace* by inheritance; the docstring says "every channel of one install writes through one place", but there are five copies of it. [2] (still open from round 1)

### harness/installation/installer.py

- installer.py:127-281 `InstallRun` — shape-classes-around-resources — the run holds the installer and reads `installer.lock`, `.record`, `.last_install`, `.toolsets`, `.diagnostics`, `.path`, `.target`, `.clean()`, `.diagnosis_of`, `.red_report` in every step; round 1's *Deployment* moved to a per-run object but kept reaching into the installer for each part. [3] (still open from round 1)
- installer.py:221-223 `InstallRun._install_toolset` — hide-inner-details — appends to `channels.deployed`, a public list of *InstallChannels*, from outside. [3]
- installer.py:229-244 `InstallRun._install_agents` — eliminate-duplication — agents are written by the run itself (`write_text`, `record.track`), while standing rules go through `RulesInstallation.write_standing_rule` and skills through *SkillInstallation*; a fourth file writer outside the installations. [2]
- installer.py:388-400 `Installer.write_language_adapters` — eliminate-duplication — repeats `InstallRun.publish`'s walk (the repository's toolsets, the registered channels' toolsets, each child toolset) to feed *LanguageAdapters*. [2]
- installer.py:410, :190, :453 `Installer.diagnosis_of(channels, published)` — hold-state-on-the-object-not-in-parameters — two of its three callers pass `channels.published` beside `channels`. [3]

### harness/installation/files.py

- files.py:114, :265, :343 `front_matter(tool, relative, parts, text)` — limit-operation-parameters — four parameters, two of them (`relative`, `parts`) values `write` worked out from `tool`. [4]
- files.py:244-252 `FileInstallation._claude_rules_front_matter` — put-logic-on-the-owning-resource — on the base, called only by *RulesInstallation* (:358, :377). [3]
- files.py:103, :372 `_RULE_FILE_NAME`, `"Practice rules."` — extensions-live-with-the-domain — the file writer still knows that rule files live under `practices/` and that a rules file belongs to a practice. [1] (still open from round 1)

### harness/installation/install_diagnostics.py and install_record.py

- install_diagnostics.py:24, :45-46 `Deployed.CHANNELS`, `published.get("mcp")`, `published.get("hook")` — eliminate-duplication — the channel names are spelled again as literals, while the registered channels publish under `destination.channel`. [2] (still open from round 1)
- install_diagnostics.py:35-50 with install_record.py:199, :296 — eliminate-duplication — the folders `skills`, `commands`, `prompts`, `rules`, `agents`, `language-adapters` are spelled in two files beside *IdeLayout*, which already says where commands and rules go (`commands_folder`, `rule_suffix`). [2]
- install_diagnostics.py:13, :80, :144, :170 — use-consistent-naming — `colour` in the code, `color` in the JSON keys and `_COLORS`/`colors` locals in the same file. [4]
- install_record.py:229, :232 `InstallRecord.installed_files`, `saved` — hide-inner-details — a public list the record's own operations mutate, and the raw file dict *LastInstall* reads keys from. [3] (still open from round 1)

### harness/installation/published_links.py

- published_links.py:143-150, :160-166 `PublishedLinks.all`, `record`, `rename` — refuse-unreadable-input — an unreadable `whiteboards.json` or `versions.json` is read as `{}`, and the next `record` writes `{name: url}` over it, losing every other board's address: exactly the loss the rule exists to prevent. [3]
- published_links.py:12 `PublishedLinks` — high-cohesion — the addresses of Claude artifacts a whiteboard or a design canvas was published to are kept in the install module; neither publishing nor its users (harness/whiteboard, harness/design_canvas, the Render action, space/session) are installation. [1]

### harness/installation/repository_toolsets.py

- repository_toolsets.py:130-145 `classes()` / `unloadable` — temporal-independence — `classes()` answers the classes and replaces `self.unloadable` as a side effect; every reader must call it first (`installer.py:405-406`, `hook_server.py:466-469`, `mcp_server.py:1035-1036`). [3] (still open from round 1)
- repository_toolsets.py:65-75 `GUIDANCE_FOLDER`, `IMPORT_FOLDERS` — extensions-live-with-the-domain — the framework spells `cdd_guidance`, `tools` and the four guidance packages, the folders of modules built on it, which the root card says it holds none of. [1]

### harness/installation/data_class.py

- data_class.py:209-216 `DataClass.edited_by(operation)`, `sends_by_identity(field)` — put-logic-on-the-owning-resource — neither reads the class it describes; each answers from its parameter alone. [3] (still open from round 1)
- data_class.py:259 `data_of` — single-boundary — the one way an object becomes JSON for every MCP answer lives in the install module and is imported by about 50 files outside it. [1] (still open from round 1)

### harness/installation/language_adapter.py

- language_adapter.py:39, :894-895 `_CHAT_CLASS = "Chat"` — low-coupling — the installer finds harness/chat's toolset by its class name, while the file manager's is found by an annotation (`shares_file_views`, :892). [1] (still open from round 1)
- language_adapter.py:49-53, :65-100 with :446-477, :845-852 — eliminate-duplication — a type becomes TypeScript by two routes with their own tables: `_SCHEMA_TYPES` / `_SCALAR_TYPES`, `_SCHEMA_INPUTS` / `_HINT_INPUTS`, `PublishedSchema.input_kind` / `TypeScriptViews._hint_input`. [2] (still open from round 1)
- language_adapter.py:103 `_SentArguments` with `agent_tools/chat_pointer.py:206` — use-consistent-naming — two private classes of one name do unrelated jobs. [4] (still open from round 1)
- language_adapter.py:121-131 `_PythonName.label` — eliminate-duplication — turns `is_enabled` into "Is enabled" by `replace("_", " ")`, a case conversion outside *Name*, which the annotations card makes the only one. [2]
- language_adapter.py:343-346, :386-399, :498-506 `TypeScriptToolset._imports`, `_shapes` — temporal-independence — `hint_type` fills the imports and nested shapes as a side effect, so `render` must write the operations before the header and data (its own comment at :387 says so); calling them in another order writes a file with missing imports. [3]
- language_adapter.py:335-660 `TypeScriptToolset` — limit-class-methods — 39 methods: file paths, type mapping, imports, the data shapes, three class texts, routes, identities. [3]

### harness/installation/templates/typescript/cdd-connection.ts

- cdd-connection.ts:271-277 `CddConnection.parsed` — refuse-unreadable-input — an answer whose JSON does not parse is returned as its raw text cast to `Result`; a truncated object answer reaches the page typed as data it is not. A string answer can be told apart by the tool's declared result type, which the adapter knows. [3]
- cdd-connection.ts:98 `cddHome` — eliminate-duplication — `CDD_HOME` else `~/.cdd` is the rule *CddHome* (`cdd_home.py:64`) owns, written again in TypeScript. [2]

### harness/markdown/markdown.py

- markdown.py:451 `AssetLocation._skip_folder_entry` — single-boundary — `"faultyasset"` is the Clean Engineering drawio scanners' fixture name, spelled in the framework. [1] (still open from round 1)
- markdown.py:173 `MarkdownText.headings` — use-typed-signatures — answers `list[tuple[int, int, int, str]]`; readers index by position (`item[3]` at :206, :223, :241, :282) and unpack elsewhere, so the tuple's order is a public contract. [4] (still open from round 1)
- markdown.py:397-415 `AssetLocation` — hide-inner-details — a nine-field record whose `kind` string selects the reader in `extract()`; each kind uses a different subset of the fields. [3] (still open from round 1)
- markdown.py:49-56 `ExtractedMarkdown.expand` / `__call__` — no-legacy-api-after-refactor — a string subclass kept so `examples().expand()` works; only specs call it (`clean_engineering_spec.py:130-131`, `:188`, `stories_spec.py:469`, `:474`). [2] (still open from round 1)
- markdown.py:692-720 `YamlFields` — shape-classes-around-resources — no state of one text; `MarkdownText.yaml_fields` makes a new one per read and the parse cache is class-level. [3] (still open from round 1)
- markdown.py:286-353, :541, :698 with installation/json_file.py:150 `HeldJsonFile` and process/answer_reads.py — eliminate-duplication — "has this file changed since I read it" is answered by `SOURCE_STAMPS`, `READ_DOCUMENTS`, `AssetLocator._found`, `YamlFields._parsed`, *HeldJsonFile* and *HeldForAnswer*, six caches with six invalidation rules. [2] (still open from round 1)
- markdown.py:837-841 `Markdown.location` — low-coupling — the seam hands out *AssetLocation*, a class the module does not export, and `cdd_guidance/practices/template_checks.py:102` reads `located.location.path`. [1] (still open from round 1)
- markdown.py:267, :772, :873, :880 `MarkdownText.section_child_blocks`, `MarkdownCollection.from_section`, `Markdown.built_by`, `Markdown.read_for` — make-module-only-operations-private — public, called only inside `markdown.py`. [1] (still open from round 1)
- markdown.py:786-795 `MarkdownCollection.attach` — hide-inner-details — it walks `vars(instance)` and replaces every attribute that holds the previous collection or one of the same type; the collection rewrites its owner's fields. [3] (still open from round 1)
- markdown.py:113 `heading_anchor` — eliminate-duplication — the same rule is written again in `cdd_guidance/practices/stories/model/markdown/links.py:50`, while DDD imports this one (`ddd/model/nodes.py:18`). [2] (still open from round 1)
- markdown.py:25-36 `__all__` against `.context/module-context.md` — seam-names-current-code — the package exports `FileFilter`, which the card's seam does not name. (The card was brought up to date otherwise.) [1] (still open from round 1)
- markdown.py:543-548, :625-630 `AssetLocator._module_dir`, `_search_root_path` — eliminate-duplication — both hold `scope.folder`; `_canonical_domain_md` loops over the same folder twice and `_located_beside` reads the second name for the first. [2]
- markdown.py:585-592 with :639-651 `_locate_template_or_missing` / `_locate_templates` — eliminate-duplication — the `.no-template` fallback is built in both; the outer test can never pick the inner result over its own fallback. [2]
- markdown.py:122-125 `_section_heading` — eliminate-duplication — makes a heading from a label by `replace("_", " ").replace("-", " ").title()` and maps `context`/`contexts`/`overview` to `Overview`: a case conversion outside *Name* and a label rule no reader can find. [2]
- markdown.py:737-741, :755-756 `MarkdownCollection._adopt`, `__getitem__` — eliminate-duplication — `entries` is a dict or a list; `__getitem__(name)` on a list collection fails, and every reader of `entries` must test which shape it holds (as `agent_tools.py:206-208` does). [2]
- markdown.py:880-888 with :772-784 `Markdown.read_for` — hold-state-on-the-object-not-in-parameters — hands `build(self, return_type, self._instance)` the owner the Markdown already holds, so `from_section` can pass it back to `markdown.built_by(..., parent)`. [3]

### harness/markdown/format.py

- format.py:25-42, :72-99, :116-126 `Format.GROUPS`, `WRITTEN_TOGETHER`, `FILE_ORDER`, `_FILE_NAME_ENDINGS`, `group_order`, `file_order`, `is_offered` — extensions-live-with-the-domain — the order an action bar offers format groups, the order a fidelity's files are shown in, that a diagram is written as draw.io and whiteboard together, and that a sketch's file ends `-sketch` are rules of harness/guidance and the apps, kept in the module the card says "names no type above it"; readers are `render.py`, `template_checks.py`, `declared_outputs.py`, `format_trip.py`, `catalog_examples.py`. [1]

### harness/mcp/mcp_server.py

- mcp_server.py:622-1058 `McpHost` — limit-class-methods — 41 methods (down from 52): the protocol handlers, the HTTP app, the toolsets kept for each project, the restart gate, lane routing, publishing mods, ping and diagnose. *ChatRequest* took the request reading out; the protocol and HTTP side is the next part that changes for its own reasons. [3] (still open from round 1)
- mcp_server.py:332-333, :148, :166-168, :176, :221 `McpInstallation.daemon` / `.served.daemon` / `.lanes` — use-intention-revealing-names — the stable lane's daemon, the served lane's daemon and both lanes hang off one object, and *CddEntry* reaches three and four objects deep to tell them apart (`_installation.daemon.home.marketplace.publish_cdd_plugin`, `_installation.served.home.is_dev_lane`, `_installation.lanes.dev.daemon.url`). [4] (still open from round 1)
- mcp_server.py:1016-1025, :292 `McpHost.diagnose` — use-typed-signatures — answers a dict whose `"tools"` key `McpChannelServer.stand_up` reads by name, built in the same `ok`/`ping`/`exceptions`/`notice` shape as `HookServer.diagnose`; *StandUp* exists for exactly this answer. [4] (still open from round 1)
- mcp_server.py:805, :810, :819, :970 — eliminate-duplication — `importlib.import_module("...").ToolCall` / `ToolRequest` / `ChatRequest` written four times so a restarted host makes objects from the re-imported classes; one "classes as they are now" part would hold the rule. [2]
- mcp_server.py:344-345 `McpInstallation.create` — hold-state-on-the-object-not-in-parameters — `ServerLanes().for_project(checkout).served_checkout(checkout)` hands the checkout twice: the lane chosen for it is then told it again. [3]
- mcp_server.py:47-48 imports `_RestartGate`, `_StillRunning`, `_ToolCalls` — hide-inner-details — names their modules mark private are imported across modules (and `_ListeningLoop` at :930), so the leading underscore says nothing about who may use them. [4]
- mcp_server.py:637 with claude_marketplace.py:32, claude_plugins.py:53 `IdeLayout("Claude")` — eliminate-duplication — Claude Code's layout is made from the literal name in three files; *IdeLayout* has no named Claude Code instance. [2]
- mcp_server.py:60-61 — limit-comments — the comment "what loading a toolset's module ... raises" sits above `_LEGAL_MCP_NAME`, which it does not describe; the constant it described moved to `AgentToolSet.LOAD_FAILURES`. [4]

### harness/mcp/cdd_home.py, server_lanes.py, mcp_address.py

- cdd_home.py:74-101 with mcp_address.py:93-98, server_lanes.py:180-186, :242-260 — eliminate-duplication — "this home is the dev lane's when its folder is named `dev`, on the port after the stable lane's" is decided in four places: `CddHome.is_dev_lane` / `stable_lane` / `dev_lane`, `McpAddress.of_home`, `ServerLanes.__init__` / `from_serving`, `ServerLane.from_home`. The shared constants are new; the decision still has four owners. [2] (still open from round 1)
- cdd_home.py:70 with mcp_daemon.py:397-415 `CddHome.state_file`, `ServingProcess.publish` / `is_this_process` — hide-inner-details — *CddHome* exposes the `server.json` *JsonFile* and *ServingProcess* writes and reads its keys (`url`, `port`, `pid`, `source`) itself; the guardrails give each file one owner. [3]
- server_lanes.py:267-279 `ServerLanes.other_lane_answering` — keep-operations-single-responsibility — a question asked on every tool call (`mcp_server.py:879`) also withdraws the dev lane's runtime record (`CddHome.return_to_main_when_feature_gone` unlinks `runtime.json`) and logs it. [3]
- server_lanes.py:267 with mcp_server.py:890-893 `other_lane_answering(serving, project)` — hold-state-on-the-object-not-in-parameters — the host hands its own home on every call; the lanes it was made with already know which lane serves. [3]

### harness/mcp/mcp_daemon.py

- mcp_daemon.py:393-395 `ServingProcess.claim_port` — eliminate-duplication — makes a second *ExclusivePort* for the port *McpDaemon* already holds as `_port` (:278), so "the one port this server may hold" has two objects. [2]

### harness/mcp/claude_plugins.py and claude_marketplace.py

- claude_plugins.py:52 `ClaudePlugins._home` — delete-unused-operations — assigned (defaulting to a new `CddHome()`) and read nowhere; the import of *CddHome* exists only for it. [2]
- claude_marketplace.py:94-99, :129-133 `PublishedPlugin.manifest`, `publish_from` — refuse-unreadable-input — an unreadable `plugin.json` is read as `{}`, and `publish_from` then writes `{"version": "0.0.0-<hash>"}` over it, dropping the plugin's name and description. [3]
- claude_plugins.py:326-330, :336-339 `ClaudePlugins.installed`, `is_watched` — refuse-unreadable-input — Claude Code's `installed_plugins.json` and `settings.json` are read as empty when unreadable; the comment covers the race, but a settings file a person broke is read as "nothing watched" and the plugin is installed a second time. [3]
- claude_plugins.py:340 `plugin.marketplace.mod_folder(plugin)` — hold-state-on-the-object-not-in-parameters — the plugin is handed back to its own marketplace; the plugin can answer the folder it is loaded from. [3]
- claude_plugins.py:353-361 `ClaudePlugins.run` — never-swallow-exceptions — a `claude` command that cannot run answers its failure's text as if it were the command's output; `_install` then tests `named in output` and reports `missing`, losing why. [3]

### harness/mcp spec support

- spec_support.py, cdd_home_checkout_examples.py — deep-module — spec support kept among production files under names the rule does not skip (it skips `examples/`, which `server_lanes_examples.py` already uses), so their classes count as production members of harness/mcp; only specs import them. [1] (still open from round 1)

### harness/whiteboard/whiteboard.py

- whiteboard.py:144-145, :260-261, :470-471 — use-exceptions-properly — an illegal element id, a block taller than a board draws, and a second element with one id each raise a bare `ValueError` with a message; a caller cannot catch one apart from a bug, and the module already declares *UnreadableBoard* for its own failures. [4]

## Design proposals

1. **A tool says what it is, and the deployed channels come from the kinds.** Replace `AgentTool.kind` strings with the class (`isinstance(tool, AgentOperation)`) or one boolean `runs_python`; `Deployed` takes its channel names from `annotation_kinds` destinations plus the four file kinds it counts, and reads `published[kind.channel]`. Files: `agent_tools.py`, `files.py`, `mcp_server.py`, `install_diagnostics.py`, `diagnostics/guidance_probe.py`. Ends: `AgentTool.kind`; `Deployed.CHANNELS` literals; the folder names spelled beside *IdeLayout* (with `install_record.py` reading `IdeLayout` folders). Three findings.

2. **An unreadable file is refused, and the "being written" race is a retry, not an empty read.** Give *JsonFile* one `read_settled()` that retries a decode failure for `_SWAP_SECONDS` (as `_text` already retries a refused read) and then raises; every caller that now catches *JsonFileUnreadable* to answer empty uses it and lets the failure name the file. Apply the same to `KeepsDocumentInDrawing`/`OnBoard` (raise the format's unreadable error), `HookServer.handle_stdin` (log and answer the IDE with a message), and `CddConnection.parsed` (parse only when the tool's result type is not a string). Files: `json_file.py`, `published_links.py`, `claude_marketplace.py`, `claude_plugins.py`, `hook_daemon.py`, `hook_server.py`, `drawio.py`, `whiteboard.py`, `cdd-connection.ts`. Ends the six refuse-unreadable-input findings and the errors-out-of-existence finding on `document_kept_in`. Risk: a page that today shows nothing on a corrupt `whiteboards.json` will show the failure, which is the point.

3. **One base keeps a source document in a drawing, and the rectangle moves down.** Put `KeepsSourceDocument` in `harness/markdown/format.py` beside *SourceDocument*, parameterised by the reader (`from_text`, its unreadable error, where it keeps the document), and move *Box* to a small geometry module both drawio and whiteboard import. Files: `format.py`, `drawio.py`, `whiteboard.py`, each practice's draw.io and whiteboard formats (imports only). Ends: the duplicated mixins; drawio's dependency on whiteboard; with proposal 2, the swallowed parse in both. Three findings.

4. **Every case conversion goes through *Name*.** Add `Name.label` ("Is enabled") and `Name.heading` (the title-case heading a label is read under), and move `heading_anchor` onto a markdown heading reader that both harness/markdown and the Stories practice import. Files: `name.py`, `markdown.py`, `language_adapter.py`, `stories/model/markdown/links.py`. Ends: `_PythonName.label`, `_section_heading`, the duplicated `heading_anchor`. Three findings.

5. **The answer cache moves to space/session, and the held value holds its answers.** Move `AnswerReads`, `ServedAnswers` and `HeldForAnswer` into space/session; `ServedAnswers` is handed its counter, and `HeldForAnswer(answers, read)` holds both, so `get()` takes nothing. Files: `answer_reads.py` (deleted), `space/session/sessions.py`, `guidance_selection.py`, `practice_session_output.py`, the process card. Ends three findings. Risk: none outside space/session imports it.

6. **One owner for the two lanes.** *ServerLanes* alone decides which home and port is the dev lane's: `CddHome.stable_lane`/`dev_lane` and `McpAddress.of_home` go (the connect script asks a standard-library helper in `mcp_address.py` that *ServerLanes* also uses), `ServerLanes` is made with the home it serves from, and `other_lane_answering(project)` only answers; the withdrawal of a gone feature runs once per restart and per install (where `McpChannelServer.ensure_running` already does it). Files: `cdd_home.py`, `mcp_address.py`, `server_lanes.py`, `mcp_server.py`, `scripts/connect.py`, the lane heavy specs. Ends three findings. Risk: the connect script must stay standard library only.

7. **An install holds one place, and every file goes through an installation.** `InstallChannels` makes one *InstallPlace* and each installation holds it (composition, not inheritance); `Installation.install` goes; `is_temporary` is asked only of *InstallTarget*; agents get an `AgentsInstallation` beside *RulesInstallation*; *InstallRun* holds the place, the lock and the diagnostics it uses instead of the installer; `diagnosis_of(channels)` reads `channels.published` itself; `write_language_adapters` reuses the run's walk of toolsets. Files: `destination.py`, `installer.py`, `files.py`, `language_adapter.py`, `install_target.py`, `mcp_server.py` (*McpInstallation*), `hook_installation.py`, `scripts/install.py`, `installer_heavy_spec.py`. Ends: `Installation.install`; the three temporary-folder tests; the five copies of the place; *InstallRun* reaching into the installer; `channels.deployed.append`; the agents writer; the duplicated toolset walk; `diagnosis_of`'s second parameter. Eight findings. Risk: the heavy installer spec pins every installed path, which is the proof the move changed nothing.
