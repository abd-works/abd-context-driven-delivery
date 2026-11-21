# Judgment: harness lower modules

**Area:** `harness/annotations`, `harness/markdown`, `harness/agent_tools`, `harness/installation`, `harness/process`, `harness/git`, `harness/hooks`, `harness/mcp` (production Python and the TypeScript templates; specs read only to see how a class is used).
**Read:** every production file in the area, the eight module cards and their model documents, the three Clean Engineering rule files, the refactor guardrails, and the graph report `clean-engineering-code-20261121T212842.md`.
**Method:** each finding names the file and line it was read at; every "only used inside" or "unused" claim was checked with a repository-wide grep (specs, `.retired`, `.venv`, and `oss_portal_domain_driven` left out of the production count, specs then checked separately).

Theme tags: **[1]** module boundaries, **[2]** the same work in different shapes, **[3]** resource orientation, **[4]** domain orientation.

## Findings

### harness/annotations/name.py

- name.py:51 `Name.title_words` — deep-module — a public property read only by the four `title_*` properties of the same class (no caller in production or in `name_spec.py`). It is the eighteenth seam method of a module allowed seventeen, so making it private alone brings the module under 35%. [1]

### harness/annotations/annotation.py

- annotation.py:51-71 `AnnotationKinds.of_channel` / `annotated_for` / `publishes` / `name_given_for` — hold-state-on-the-object-not-in-parameters — every one takes a channel name string and looks the kind up again; the callers (`agent_tools.py:360`, `:942`, `:949`, `:1006-1007`, `guidance/action_catalogue.py:160`) pass `InstallDestination.X` constants, so a destination is found by name on every question about a member. [3]
- annotation.py:26 and :47 `AnnotationKinds.register` / `withholds_install` — put-logic-on-the-owning-resource — the registry reads `getattr(kind, "channel", "")` and tests `isinstance(kind, OmissionKind) and kind.omits_install` instead of asking the kind, so two rules that belong to a kind of annotation are kept in the list of kinds. [3]
- annotation.py:146, :175, :281-283 with `hooks/hooks.py:31`, `installation/data_class.py:44-46`, `:112-113` — eliminate-duplication — what an annotation records on its target has five shapes: `True` under its flag; a tuple of names; `True` plus `{flag}_name` and `{flag}_disabled` attributes; the annotation object itself (`@Hooks`, `@on_stage`); a key string plus a second flag (`@data_field`, `@language_adapter`). Each shape needs its own reader on its kind (`annotates`, `names_on`, `name_annotated_on`, `disabled_on`, `recorded_on`, `DataClass.sends_by_identity`). [2]

### harness/markdown/markdown.py

- markdown.py:284 `MarkdownText.named_subsection` — eliminate-duplication — a public method whose whole body is `return self.slice_heading(heading)`; its one caller is `MarkdownFile.read_fidelity_subsection` (:393). [2]
- markdown.py:226, :267, :273 `MarkdownText.child_blocks`, `section_child_blocks`, `fidelity_blocks` — deep-module — public methods of a public class with no caller outside `markdown.py` (`fidelity_block` is the only one of the family another module calls, `guidance.py:775`). [1]
- markdown.py:238-240 `MarkdownText.child_blocks` — hold-state-on-the-object-not-in-parameters — it writes `_parent_headings`, `_parent_index` and `_parent_level` on the document for one call and `_blocks_under` reads them back. A parsed document is shared between threads (`ReadDocuments`, and the comment at :166 says so), so two readers asking for different parents overwrite each other's fields. [3]
- markdown.py:273-282 and :385-398 `fidelity_blocks`, `fidelity_block`, `MarkdownFile.read_fidelity_subsection` — extensions-live-with-the-domain — the markdown module knows that a practice document has a `## Fidelities` heading and a block per fidelity, which is harness/guidance's concept; the module's own card says it "names no type above it". [1]
- markdown.py:495-507 `AssetLocation._skip_fidelity_file` — extensions-live-with-the-domain — the framework's file reader names the Stories practice's files and fidelities (`story-map`, `thin-slice`, `scenario-`, the `examples` label), so a change to how Stories names its examples is an edit to harness/markdown. [1]
- markdown.py:474 `AssetLocation._skip_folder_entry` — single-boundary — `"faultyasset" in name.casefold()` is the Clean Engineering drawio scanners' fixture name (`cdd_guidance/practices/clean_engineering/model/drawio/scanners/_drawio_base.py:20`) spelled a second time in the framework. [1]
- markdown.py:160 `MarkdownText.headings` — use-typed-signatures — the seam answers `list[tuple[int, int, int, str]]`; every reader indexes or unpacks by position (`item[3]` at :193, :210, :216, :232; `_start, _end, level, name` in `catalog_practice.py:237`, `practice_supplement.py:122`, `:149`, `space/session/node_spans.py:44`), so the tuple's order is a public contract. [4]
- markdown.py:402-412 `AssetLocation` — hide-inner-details — a ten-field record whose `kind` string selects the reader in `extract()` (:414-421); its required fields `module_dir` and `domain_slug` are passed in eight constructions and read nowhere. [3]
- markdown.py:428-443 `AssetLocation._extract_fidelity_file`, `_first_stem_text` — eliminate-duplication (no use, delete) — no caller anywhere in the repository. The last four lines of `read_fidelity_subsection` (:395-398) test a condition and return `""` either way. [2]
- markdown.py:46-53 `ExtractedMarkdown.expand` / `__call__` — no-legacy-api-after-refactor — a string subclass kept so that `practice.examples().expand()` still works; only specs call it that way (`clean_engineering_spec.py:130-131`, `:188`, `stories_spec.py:447`, `:452`). Production reads the property. [2]
- markdown.py:731-759 `YamlFields` — shape-classes-around-resources — a class with no state of one text: `mapping(body)` and `yaml_fields(text)` take the text as a parameter, `MarkdownText.yaml_fields` (:136) makes a new one on every read, and the parse cache is class-level (`_parsed`). The fields belong to the *MarkdownText* that holds the text. [3]
- markdown.py:565, :327, :355 `AssetLocator._found`, `SOURCE_STAMPS`, `READ_DOCUMENTS` — eliminate-duplication — three caches that answer "has this file changed since I read it" three ways (a class-level dict keyed by scope and label with folder times; a module object of stat results; a module object of parsed documents by time and size). `installation/json_file.py:157 HeldJsonFile` is a fourth. [2]
- markdown.py:875 `Markdown.location` with `guidance/guidance.py:883`, `:888` — low-coupling — the seam hands out *AssetLocation*, a class the module does not export, and harness/guidance reads `located.location.path`. The caller wants the template's file; *Markdown* should answer that. [1]
- markdown.py:809, :910, :917 `MarkdownCollection.from_section`, `Markdown.built_by`, `Markdown.read_for` — deep-module — public methods called only from `markdown.py` itself. [1]
- markdown.py:823-833 `MarkdownCollection.attach` — hide-inner-details — it walks `vars(instance)` and replaces every attribute that holds the previous collection or one of the same type, so the collection rewrites its owner's fields. [3]
- markdown.py:100 `heading_anchor` — eliminate-duplication — the same function, with the same rule, is written again in `cdd_guidance/practices/stories/model/markdown/links.py:30`, while DDD imports this one (`ddd/model/nodes.py:17`). [2]
- markdown.py:25-35 `__all__` against `.context/module-context.md` — seam-names-current-code — the card's seam lists *MarkdownFile*, *FlatSettings*, *FrontMatter* and `operation_property`; the package exports none of them, callers import them by file path, and *MarkdownFile* has no caller outside `markdown.py`. [1]

### harness/markdown/format.py

- format.py:101 `Format.is_templated` — deep-module — read only by `template_folder` and `template_extension` in the same class. [1]

### harness/agent_tools/agent_tools.py

- agent_tools.py:23-24 `ContextDocument`, `ArgumentDocument` — eliminate-duplication (no use, delete) — two type aliases no file in the repository reads. [2]
- agent_tools.py:124, :129, :137, :671, :678 `session_context`, `pattern`, `schema_guide`, `is_part_of_practice`, `is_served_on_mcp` on *AgentToolSetOrigin* / *AgentToolSet* — extensions-live-with-the-domain — the base every toolset derives from carries members that name modules above it: a session, a pattern's guideline in `.context/config.json`, a practice's schema, a practice's parts, the cdd server. Each is a default that harness/guidance, harness/hooks or harness/mcp overrides or reads. [1]
- agent_tools.py:1015, :1134, :1148, :1195 with `installation/files.py:107`, `:166`, `:225`, `:286` — use-intention-revealing-names — a tool named by the literal `"instructions"` is special-cased in eight places (its MCP name, its listed description, its answer, its file name, its schema). The rule "a practice's own instructions are published under its slug" has no name and no owner. [4]
- agent_tools.py:1096-1101, :1156, :1169 `AgentTool.kind` — shape-classes-around-resources — the tool's class (*AgentOperation*, *AgentInstructions*) is repeated as a string `"tool"` / `"instructions"` / `"none"`, and callers branch on the string (`files.py:136`, `:243`, `:276`, `mcp_server.py:374`) instead of asking the tool. [3]
- agent_tools.py:913-923, :926-953 `InstallDestination`, `AgentToolDestination` — hold-state-on-the-object-not-in-parameters — a channel is a string constant; a tool answers `install_to_mcp`, `install_to_hook`, `install_to_skill`, `install_to(name)`, `destinations` (a list of strings) and the toolset `tools_for(name)`. `install_to` has no caller outside this file. [3]
- agent_tools.py:918-922 with `installation/install_diagnostics.py:24`, `hooks/hook_installation.py:27`, `mcp/mcp_server.py:259`, `installation/files.py:105` — eliminate-duplication — the channel names are spelled again as literals in four other files (`CHANNELS = ("toolset", "skill", "command", "rules", "mcp", "hook", ...)`, `channel = "hook"`, `channel = "mcp"`, `channel = "markdown"`). [2]
- agent_tools.py:585-612 `AgentToolSet.instantiate` / `from_items` with `hooks/hook_server.py:393-401 ref_label`, `mcp/mcp_server.py:421-424 _references` — hold-state-on-the-object-not-in-parameters — a toolset is named five ways (`ToolsetConfiguration`: reference text, a dict with `toolset` and `context`, a dict of constructor arguments, a class, an instance) and three files switch on the type to turn one into another. The guardrails say to hold the reference, never look up by name. [3]
- agent_tools.py:165-166 `ToolSetCollection.attach` — eliminate-duplication — it calls `MarkdownCollection.attach(self, instance, name)` unbound on an object that is not a *MarkdownCollection*. The two collection classes model the same thing (entries by name, a parent, iteration in entry order, attach to an owner) in two modules. [2]
- agent_tools.py:1230-1243 `AgentInstructions.members_of`, `member_of`, `provider_of` — put-logic-on-the-owning-resource — three operations that read nothing of the recipe they are on: each takes the target toolset and answers from it. They exist so `recipe.py` can ask without importing this file. [3]
- agent_tools.py:688-695 `AgentToolSet.session_for` — hold-state-on-the-object-not-in-parameters — the session a board command names travels as a `session` argument whose text is tested for ending in `session.json` and parsed back into a session; the rule names this as state written into a string. [3]
- agent_tools.py:1076-1083 `AgentTool.should_log_session_invocation(arguments)` — hold-state-on-the-object-not-in-parameters — it is handed `call.arguments` by its one caller, which holds the call; its `arguments.get("ping") is True` test is the same rule as `mcp_server.py:873`. [3]
- agent_tools.py:566-582 `_mode` / `ExpansionMode` with `recipe.py:359-370` — use-consistent-naming — the mode is a validated value class on the toolset, a plain string in the expansion that reads it (`str(getattr(target, "mode", "instructions"))`, `== "tool"`), and a string literal where authors set it (`guidance_actions.py:815`). The value class checks nothing the expansion relies on. [2]
- agent_tools.py:956 `names_alike` — prefer-class-operations — a module function that holds the one rule of how a client spells a tool name; its callers are `AgentTool.is_called` and `mcp_server.py:461`. [3]

### harness/agent_tools/tool_call.py

- tool_call.py:29-37, :119-134, :191, :202 `SessionOpener`, `SessionOpening`, `ToolCall.session` — use-typed-signatures — every operation answers `Any`. The framework then calls members of that untyped object in four places: `session.log.by(chat).tool(...)` (`agent_tools.py:1093`), `session.log.by(chat).failure(...)` (`mcp_server.py:888`), `session.chat_injections` (`hook_server.py:494`), `session.folder.hook_log("dispatch.debug").stamped(...)` (`hook_server.py:566`). [4]
- the same four call sites — low-coupling — harness reaches three objects deep into space/session's *Session* with no declared seam, so a rename in space/session breaks the framework at run time only. *ChatRuleInjections* (`hook_server.py:176`) shows the module already declares a protocol where it wants one. [1]
- tool_call.py:22 `_NO_CHAT = "unknown"` with `chat_pointer.py:17`, `:278`, `mcp/scripts/connect.py:29` — eliminate-duplication — "no chat" is spelled `unknown`, `unnamed`, `no-chat` across three files, with two separate lists of which spellings count. [2]
- tool_call.py:45-48 `AnsweringMcpHost.checkout_server -> Any` — use-typed-signatures — the protocol a diagnostics tool reads the server through leaves its main answer untyped. [4]

### harness/agent_tools/chat_pointer.py

- chat_pointer.py:91-96 and :107-112 `from_claude_chat`, `from_claude_session` — eliminate-duplication — two factories with the same lookup; they differ only in whether the pointer counts the transcript's lines when asked. [2]
- chat_pointer.py:37 `_FOUND_TRANSCRIPTS` — use-explicit-dependencies — a module-level dict keeps what `_ClaudeProjects` found, while a new `_ClaudeProjects()` is made on every lookup (:95, :111); the object that owns the folder holds none of its own state. [3]
- chat_pointer.py:136-139 `_checkout_holding` — eliminate-duplication — the same expression as `process/claude_chat_process.py:106-107`; both `working_folder` properties answer "the checkout the chat works in now", one from the transcript and one from the session file, each with its own spare-folder test. [2]
- chat_pointer.py:40 `ChatPointer` — keep-classes-single-responsibility — one class is the pointer a log line ends with (id, transcript, line range, `in_log_line`, `transcript_text`) and the finder of a Claude Code chat (`from_request`, `from_claude_chat`, `working_folder`, reading 256 KB of transcript for the last `cwd`). [3]
- chat_pointer.py:11 with `.context/module-context.md` — seam-names-current-code — the file imports harness/process; the agent_tools card lists only harness/annotations and harness/markdown as dependencies. [1]

### harness/agent_tools/progress.py and worker_process.py

- progress.py:12-29 `report_progress`, `reporting_to` with `tool_call.py:79 CallsBeingAnswered` — eliminate-duplication — "what the running call carries on this thread" is kept twice: an object with a context variable for the call, and a module-level context variable with two functions for its reporter. `mcp_server.py:828` has to enter both together. [2]
- worker_process.py:18, :31-41 — eliminate-duplication — it defines its own `_CREATE_NO_WINDOW` and starts `sys.executable` by hand, while harness/process owns "start a Python with no window" (*BackgroundStart*, *PythonInterpreter*). [2]

### harness/agent_tools/recipe.py

- recipe.py:57-61 `ExpandedRecipe.members_of` / `member_of` / `provider_of` — write-interactions — the protocol asks the recipe to mediate a question the target toolset can answer itself (`target.instruction(member)`); see `agent_tools.py:1230`. [3]

### harness/installation/destination.py

- destination.py:22, :53 with `install_target.py:44` — eliminate-duplication — "is this install in the temporary folder" is a module function, an attribute set on every *Installation*, and a property of *InstallTarget*; the heavy spec sets the attribute by hand (`mcp_host_heavy_spec.py:559`). [2]
- destination.py:46 `Installation(layout, path, repo)` with `install_target.py:22`, `files.py:117-118`, `installer.py:67` — eliminate-duplication — *InstallTarget* is "the IDE folder with its layout", yet *Installation* takes the same two values apart, *FileInstallation* takes a target and unpacks it, and *InstallChannels* unpacks the installer into `layout, path, repo` to make the server channels. [2]
- destination.py:57-62 `track_writes_with` / `track_write` — use-explicit-dependencies — the install record reaches each installation as a callback set after construction; the installation's collaborator is the *InstallRecord*, and it should hold it. [3]
- destination.py:83-87 `Installation.install` / `write` — layer-separation — `install(tool)` only calls `write(tool)`. [1]
- destination.py:165-179 `ServerInstallation.standup -> Any`, `diagnose -> dict[str, Any]`, `ensure_running -> dict[str, str]` — use-typed-signatures — the seam two modules implement answers untyped dicts; the Installer reads `diagnosis.get("notice")` (`installer.py:326`). The same dict (`ok`, `ping`, `exceptions`, `notice`) is built twice (`hook_server.py:527`, `mcp_server.py:988`). [4]

### harness/installation/files.py

- files.py:105, :119 `FileInstallation.channel` — use-consistent-naming — `channel` is a string on *Installation* and *ServerInstallation* (read by `accepts` and `InstallChannels.published`) and a *FileChannel* object here. [4]
- files.py:125-133, :136, :142-145, :243-247, :276 — shape-classes-around-resources — one class writes three kinds of file and tests `self.channel.destination == SKILL / COMMAND / RULE` in five methods; each branch is a different writer. [3]
- files.py:93-99 `FileChannel.served_on_mcp` with `installer.py:74-78`, `:96-97` — hold-state-on-the-object-not-in-parameters — whether a tool is also on MCP is a fact of the tool (`tool.install_to_mcp`), but the install makes six file installations, each channel twice, so the value can be fixed in a constructor and chosen again per tool. [3]
- files.py:107, :177-189, :203-221, :223-227, :254-261, :281-289, :346 — extensions-live-with-the-domain — the file writer knows practices and fidelities: `_GUIDANCE_OWN_OPERATIONS = {"instructions", "rules-markdown"}`, `is_part_of_practice`, `_fidelity_one_liner`, `_fidelity_invoke_parts`, `_schema_guide`, `"Practice rules."`. How a practice's files are named is harness/guidance's rule. [1]

### harness/installation/installer.py and install_diagnostics.py

- installer.py:455-458, :197-202 with `install_diagnostics.py:57-67` — hold-state-on-the-object-not-in-parameters — the diagnosis is built as the text `"{color}\n{body}"` (or `"!\n{color}\n..."` when red), then `record_run` finds the colour by scanning the report's lines for a colour word and `_report_diagnosis` tests `report.startswith("!")`. The colour is written into a string and parsed back twice. [3]
- install_diagnostics.py:32, :48, :69, :87 — use-typed-signatures — what an install deployed is a `dict[str, list[str]]` handed between five methods and the Installer; no class holds "the deployed set" or compares itself with the last one. [4]
- installer.py:130-145 `Deployment` — shape-classes-around-resources — it holds the installer and reads `installer.record`, `.lock`, `.toolsets`, `.last_install`, `.target` for every step; the state of one run (`_channels`, `diagnosis`) is kept on this long-lived object and replaced by the next run, and `channels` (:141) makes a second kind of *InstallChannels* "to read a folder". [3]
- installer.py:414-418 `Installer.install(toolsets: Iterable[Any] | None, ...) -> Any` — use-typed-signatures — the module's main public operation takes and answers `Any`. [4]
- installer.py:370-372 with `install_record.py:137-140 LastInstall.saved` — hide-inner-details — the Installer reads the file's keys (`last.get("ide")`, `last.get("path")`); *LastInstall* answers a dict where it could answer its IDE and folder. `InstallRecord.installed_files` (:45) is a public list the record's own operations also mutate. [3]
- installer.py:470 `__all__ = ["Installer"]` — seam-names-current-code — other modules import *InstallChannels*, `SERVER_CHANNELS`, *ToolsetInstallFailed* and *ServersNotRegistered* from this file. [1]

### harness/installation/json_file.py, install_lock.py

- json_file.py:109-123 with `install_lock.py:115-129` and `hooks/hook_daemon.py:214-247` — eliminate-duplication — the operating system's file lock (`msvcrt.locking` / `fcntl.flock`) is written twice, and "one process at a time, by a file naming its holder" is modelled three times: *InstallLock*, `JsonFile.held`, and `_SpawnLock` (create-exclusive plus a liveness test). `diagnostics/test_runs.py:259` is a fourth. [2]

### harness/installation/repository_toolsets.py

- repository_toolsets.py:128-143 `classes()` / `unloadable` — temporal-independence — `classes()` answers the classes and, as a side effect, replaces `self.unloadable`; all three readers must call it first and then read the attribute (`installer.py:223-225`, `hook_server.py:468-472`, `mcp_server.py:1006-1008`). [3]
- repository_toolsets.py:191, :228 — eliminate-duplication — the literal `"agent_toolset"` is tested beside `annotation_kinds.installing_names`, which exists so no name is spelled here. [2]

### harness/installation/context_config.py, data_class.py, language_adapter.py

- context_config.py:61-81 `guideline`, `practice_folder`, `default_formats(practice, fidelity)` — high-cohesion — a session's and a practice's settings (the folder a practice writes in, a fidelity's default formats) live in the install module because the hook server is its lowest reader (`cdr/0001`). The card names four unrelated jobs for this module: installing, JSON files, project configuration, and the data every MCP answer sends. [1]
- context_config.py:41-59 `load() -> dict[str, Any]`, `update(**sections: Any)` — use-typed-signatures — the public seam is an untyped bag keyed by section name. [4]
- context_config.py:61 `guideline(pattern)` with `agent_tools.py:129 pattern`, `hook_server.py:309-352` — use-consistent-naming — one concept goes by two words, guideline and pattern, in three modules. [4]
- data_class.py:171-177 `DataClass.edited_by(operation)`, `sends_by_identity(field)` — put-logic-on-the-owning-resource — neither reads the class it describes; each answers from its parameter alone. [3]
- data_class.py:220 `data_of` — single-boundary — "the one way an object becomes JSON data, for every MCP answer" is imported by 50 files outside harness/installation and by none of the installer's own steps; it is the published data model, kept in the install module. [1]
- language_adapter.py:36, :889 `_CHAT_CLASS = "Chat"` — low-coupling — the installer finds harness/chat's toolset by its class name, while the file manager's is found by an annotation (`shares_file_views`, :887). Two ways to mark "the adapter a shared file needs", one of them a name string for a class above this module. [1]
- language_adapter.py:46-50, :62-97, :443-471 with `agent_tools/parameter_schema.py:30` — eliminate-duplication — a Python type becomes a TypeScript type by two routes: arguments through the JSON Schema (*PublishedSchema*), answers and data fields through type hints (`hint_type`), each with its own scalar table. [2]
- language_adapter.py:849-870 `LanguageAdapterInstallation` — shape-classes-around-resources — it derives from *Installation* for the layout, path and write tracking, but answers neither `install(tool)` nor `write(tool)`; its operations are `record(toolset)` and `write_all()`. [3]
- language_adapter.py:100 `_SentArguments` with `agent_tools/chat_pointer.py:210` — use-consistent-naming — two private classes of the same name do unrelated jobs. [4]

### harness/process/claude_chat_process.py and process.py

- claude_chat_process.py:95 — eliminate-duplication — `session_file` spells Claude Code's config folder inline; `claude_config_folder()` at :41 is the function for it. [2]
- claude_chat_process.py:156-188 with `process.py:65-113` — eliminate-duplication — Windows' TCP table is declared and read twice in one module (the same six-field structure, the same `_PORT_BITS` constant at :22 and `process.py:60`), once for listeners and once for connections. [2]
- claude_chat_process.py:41, :46 `claude_config_folder`, `is_desktop_spare` — prefer-class-operations — two module functions about one folder, imported by harness/agent_tools and harness/mcp; the folder has no object. [3]
- process.py:231, :237 `BackgroundStart.creationflags`, `startupinfo` — deep-module — public "for a caller that starts the process itself"; no production caller reads either (one spec reads `creationflags`, `hook_spec.py:867`). [1]

### harness/git/git.py

- git.py:22, :45-64 `RepoConnectError`, `Git.succeeds` — use-exceptions-properly — one exception stands for git missing, git running past its limit, and git exiting non-zero, and `succeeds` turns all three into `False`. A caller asking whether a ref exists reads a hung or missing git as "no". The name says "connect" for failures that are not about a connection. [4]

### harness/hooks/hooks.py and hook_installation.py

- hooks.py:131, :144 with `hook_installation.py:35`, `:80` — shape-classes-around-resources — a registered hook is a `dict[str, str]` with `event`, `operation`, `ref`, built in *HookInstallation*, written and read by *HookHandlersFile*, and read by key in both. [3]
- hooks.py:155, :165 — source-parses — `Any` is used in two annotations and never imported (the file imports only `Callable`); it runs because annotations are not evaluated, and fails for any reader that resolves them. [4]
- hook_installation.py:48-57 `standup`, `diagnose`, `ensure_running` — shape-classes-around-resources — three operations of *ServerInstallation* are empty here because the hook channel starts no server; the base says "has a server" for a channel that only needs "registers with the Installer". [3]
- hook_installation.py:119-121 with `hook_server.py:495` — eliminate-duplication — "a `postToolUse` hook also answers `stop` and `subagentStop`" is a rule of the hook server written in the installation; `events_served` (`hooks.py:102`) is where such a rule already has a home. [2]

### harness/hooks/hook_server.py

- hook_server.py:188-220 `HookMessages` / `HookResult` — eliminate-duplication — *HookResult* takes a *HookMessages*, copies its five fields onto itself, and builds a new *HookMessages* from them in its `messages` property. The value class exists only to keep the constructor at three parameters. [2]
- hook_server.py:216, :229, :496, :502 — put-logic-on-the-owning-resource — `followup_only` and `additional_context` are set on a result from outside (`from_handler`, `HookServer.handle_stdin`, `_with_chat_injections`), so what the IDE reads back is decided in three places. [3]
- hook_server.py:285 `HookHandler`, :368 `HandlerCatalog`, with `hooks.py:124 HookHandlersFile.handlers` — use-consistent-naming — "handler" means the class that runs one hook, the dict a file lists, and (in the cards) the hooked operation. [4]
- hook_server.py:440 `HookToasts.shown_by` — eliminate-duplication (no use, delete) — read only by `hook_spec.py:822`. [2]

### harness/hooks/hook_daemon.py

- hook_daemon.py:92-114 `HookDaemonIdentity` / `HookDaemonAddress` — eliminate-duplication — the same pattern as *HookMessages*: the address takes an identity and copies `pid`, `stamp`, `repo` onto itself. [2]
- hook_daemon.py:102-153 `HookDaemonAddress` — keep-classes-single-responsibility — one class is where a daemon answers, who it is, and the client that sends it a ping or an event (`reported`, `answers`, `handle_stdin`, `_call`). [3]
- hook_daemon.py:280-507 `HookDaemon` with `mcp/mcp_daemon.py:55-133 McpDaemon`, `:190 ServingProcess` — eliminate-duplication — two long-running servers are modelled twice: an address, a published address file, a ping that answers who runs, `is_running`, `ensure`, `stop`, `spawn` through *BackgroundStart* into a capped log, a wait-until-it-answers loop with its own error, and an exclusive port claim. The names and shapes differ at every step (see proposal 1). [2]
- hook_daemon.py:359, :423 `replace_stale`, `claim_port` — deep-module — public with no caller outside this file. [1]

### harness/mcp/mcp_server.py

- mcp_server.py:519 `McpHost` — keep-classes-single-responsibility — 52 methods in one class: the MCP protocol handlers, the HTTP app, the server kept for each project, restart, routing between lanes, publishing mods, and working out a request's chat and project. [3]
- mcp_server.py:773, :785, :795 `_folder_the_chat_works_in(headers)`, `_requesting_process(headers)`, `_names_a_project(headers)` — hold-state-on-the-object-not-in-parameters — the request's headers are read again by `_request_headers()` in each entry point and passed down; the request, with its chat, process and project, has no object. [3]
- mcp_server.py:695 `_call_sent` — limit-operation-parameters — five parameters, three of which (`tool`, `chat`, `answers_a_chat`) are the fields of the *ToolRequest* it builds. [3]
- mcp_server.py:332 `McpServer` — use-intention-revealing-names — it serves nothing: it is the toolsets enrolled for one project (its own docstring: "the toolsets one project's calls are answered by"), while *McpHost* is the server. [4]
- mcp_server.py:266-269 `McpInstallation.daemon` / `.served.daemon` — use-intention-revealing-names — two daemons on one object, the stable lane's and the served lane's, told apart only by which attribute path reaches them; *CddEntry* reads `self._installation.served.daemon.home.is_dev_lane` (:153) and `self._installation.daemon.home.write_claude_plugin` (:145). [4]
- mcp_server.py:853-862 `route_between_lanes` and :985-986 `_dev_lane_runs` — temporal-independence — `_lanes` and `_home` are set after construction by `serve`; `_dev_lane_runs` then builds `McpDaemon(dev, McpAddress.of_home(dev.folder))` from parts although `self._lanes.dev.daemon` is that daemon. [3]
- mcp_server.py:727 with `tool_calls.py:63-70` and `installation/templates/typescript/cdd-connection.ts:96`, `:116` — hold-state-on-the-object-not-in-parameters — a call still running is answered as a sentence, and the TypeScript connection recognises it by testing `text.startsWith(tool + " is still running after")`. A change of wording in Python stops every app's retry, and a tool whose answer starts with those words is retried sixty times. [3]
- mcp_server.py:883 — provide-meaningful-context — `"pong"` is written out beside the constant `PONG` (:50); `hook_server.py:531` writes it a third time. [4]

### harness/mcp/server_lanes.py, mcp_address.py

- server_lanes.py:28-48 `LaneCall` — eliminate-duplication — the tool, arguments, project and chat of a call, held a second time beside *ToolCall*, which already holds all four; it exists as the JSON form of a call. [2]
- server_lanes.py:43 `LaneCall.from_data(data)` and mcp_address.py:78 `send_lane_call(lane_call: dict, ...) -> dict` — avoid-vague-parameter-names / use-typed-signatures — the class exists and both ends pass a bare dict, because the address file may import nothing of the framework. [4]
- server_lanes.py:60-66, :124-131 with `cdd_home.py:104-106`, `:171-178`, `mcp_address.py:51-56` — eliminate-duplication — "this home is the dev lane's when its folder is named `dev`" is decided in three classes (*CddHome*, *McpAddress*, *ServerLanes*), each making the other lane's home or address again. [2]

### harness/mcp/cdd_home.py, claude_plugins.py, mcp_daemon.py, scripts/connect.py

- cdd_home.py:81 `CddHome` — keep-classes-single-responsibility — three jobs: the runtime record (which code the server runs, `pin`, `serve_from`, `is_pinned_to`), the Claude Code marketplace (`write_claude_plugin`, `publish_mods_of`, `_publish_mod`, `_copy_mod`, `_content_hash`, `_write_marketplace`, `board_folder`, `install_command`), and the server's files (state file, log, connect script). [3]
- cdd_home.py:142, :201, :238 with `claude_plugins.py:94` — eliminate-duplication (one owner per file) — the path `claude-plugins/{name}/.claude-plugin/plugin.json` is built in four places across two classes, each reading or writing the manifest itself. [2]
- cdd_home.py:28-38 `BOARD_MOD_FOLDER`, `QUEUE_MOD_FOLDER`, `DRAWIO_VIEWER` — one-way-deps / low-coupling — harness/mcp spells the folders of `harness/chat-ui/pane`, `tools/prompt_queue` and `tools/drawio_viewer`. The root card says the framework holds no folder path of the modules built on it; the tools should register what they publish. [1]
- cdd_home.py:376-388 `_branch_of` with `server_lanes.py:148-153`, `mcp_daemon.py:181`, `agent_tools/chat_pointer.py:139`, `process/claude_chat_process.py:107` — eliminate-duplication — five places read a checkout's `.git` by hand (its branch, whether it is a main checkout or a linked worktree, which folder above holds it). `space/repo/git_folder.py GitFolder` already answers the branch and the worktree's own git folder, but sits above the framework, and the git card says git is reached only through harness/git. [2]
- claude_plugins.py:35-79 `install_board`, `install_queue`, `install_cdd` — eliminate-duplication — three operations with the same steps (compare the installed version with the published one, find the `claude` command, install) that answer the bare strings `"installed"`, `"missing"`, `"watched"`. A plugin has no object. [2]
- mcp_daemon.py:151-174 `ServedCheckout.ensure` / `pin` / `update` / `serve_on_disk` — eliminate-duplication — each repeats `self._home.install(self.checkout, CONNECT_SCRIPT)` and ends with `self.daemon.status(self.daemon.restart())`. [2]
- scripts/connect.py:91 with `cdd_home.py:97` — single-boundary (one owner per file) — the connect script reads `runtime.json` itself, with its own key (`source`), while *CddHome* is the file's owner; the script's docstring says only the server reads the files it publishes. [3]
- mcp/spec_support.py, mcp_daemon_doubles.py, cdd_home_checkout_examples.py — deep-module — spec support kept among the production files under names the rule does not skip (it skips `examples/`, `_examples/`, `mock_*`, `fake_*`), so their classes and functions count as production methods of harness/mcp; 20 spec files import them and no production file does. [1]

### Module cards and model documents

- `harness/hooks/.context/module-context.md`, root `.context/module-context.md`, `AGENTS.md` — seam-names-current-code — they name `ToolCall.session_in`, `ToolCall.open_sessions_with` and `HookServer.show_toasts_with`; the code has `SESSION_OPENING.saved_in`, `SESSION_OPENING.open_with` and `HOOK_TOASTS.show_with`. [1]
- `harness/hooks/.context/hooks-runtime-model.md:60`, `:159`, `:321` — one-canonical-model-document — the model still shows `HookInstallation(..., python=...)`, a seven-parameter `HookResult` and a five-parameter `HookDaemonAddress`; the code has three parameters each. The graph report's parameter-count and typed-signature hits on this document come from that. [1]

## Fixes that change no design

Each can be made in one pass without adding or removing a class another module names.

1. **Make `Name.title_words` private** (`name.py:51` → `_title_words`; four readers in the same class). No caller or spec elsewhere. Brings harness/annotations to 17 of 51 seam methods, which passes. Risk: none.
2. **harness/markdown under 35%** (needs three fewer seam methods; these give nine):
   - delete `MarkdownText.named_subsection` (:284); `read_fidelity_subsection` calls `slice_heading`.
   - make private: `MarkdownText.child_blocks`, `section_child_blocks`, `fidelity_blocks`; `Markdown.read_for`, `Markdown.built_by`; `MarkdownCollection.from_section`; `MarkdownScope.beside`; `Format.is_templated`.
   - Callers: all inside `markdown.py` / `format.py`. No spec names any of them. Risk: low; run `markdown_spec.py`, `format_spec.py`, `guidance_spec.py`.
3. **Delete unused code in `markdown.py`:** `AssetLocation._extract_fidelity_file` and `_first_stem_text` (:428-443); the dead tail of `read_fidelity_subsection` (:395-398 → `return named`); the fields `module_dir` and `domain_slug` of *AssetLocation* with their eight constructor arguments. Risk: low (the fields are positional, so each construction changes).
4. **Stop `child_blocks` writing fields on a shared document** (:238-240): pass the parent's index and level to `_blocks_under` and `_end_of_child` as arguments, or compute them in one method. Fixes a real race between threads. Risk: low.
5. **Delete `ContextDocument` and `ArgumentDocument`** (`agent_tools.py:23-24`). Risk: none.
6. **Delete `HookToasts.shown_by`** (`hook_server.py:440`) and change `hook_spec.py:822`, which saves and restores the notifier through it, to save through `show_with`'s argument. Risk: low.
7. **Make private:** `BackgroundStart.creationflags` and `startupinfo` (`process.py:231`, `:237`; change `hook_spec.py:867`); `HookDaemon.replace_stale` and `claim_port` (`hook_daemon.py:359`, `:423`; check `hook_daemon_spec.py` and the heavy spec, which may call `claim_port`); `AgentToolDestination.install_to` (`agent_tools.py:948`; callers are `tools_for` and the three properties in the same file). Risk: low.
8. **Exact duplicates to one place:**
   - `claude_chat_process.py:95` → `claude_config_folder() / "sessions" / ...`.
   - `chat_pointer.py:136-139` and `claude_chat_process.py:106-107` → one function in `claude_chat_process.py` (for example `checkout_holding(folder)`), imported by `chat_pointer.py`, which already imports that file.
   - `claude_chat_process.py:160-162` inner `TcpRow` and `:22 _PORT_BITS` → import `_TcpRowOwnerPid` and `_PORT_BITS` from `process.py` (both files are standard library only, so the connect script's constraint holds).
   - `json_file.py:109-123` and `install_lock.py:115-129` → one private function for the operating system's lock; where it lives is proposal 1's question, but one file importing the other's is enough for now.
   - `mcp_server.py:883` and `hook_server.py:531` → the constant `PONG`.
   - `mcp_server.py:985-986` → `self._lanes.dev.home.is_installed and self._lanes.dev.daemon.is_running()`.
   - `ChatPointer.from_claude_chat` / `from_claude_session` → one factory with a `counted: bool` or have `from_claude_chat` call the other.
   - `mcp_daemon.py:151-174` → one private `_installed_home()` step and one `_restarted_status()`.
   - `repository_toolsets.py:191`, `:228` → keep the literal `"agent_toolset"` in one private constant read by both. (Setting `makes_installable` on *AgentToolSetAnnotation* instead would change which classes count as toolsets, so leave that alone.)
   Risk for the group: low; the heavy specs of harness/process, harness/installation and harness/mcp cover each.
9. **Import `Any` in `hooks.py`** (:155, :165 use it). Risk: none.
10. **Rename vague or misleading parameters:** `LaneCall.from_data(data)` → `from_sent(sent)` (callers: `mcp_server.py:938`); `HookPayload.call` to a `functools.cached_property` instead of `self.__dict__.get("_call")` (`hook_server.py:112-115`). Risk: none.
11. **Type the signatures that are `Any` for no reason:** `Installer.install(toolsets: Iterable[ToolsetConfiguration] | None, replace: bool) -> InstallChannels` (`installer.py:414`); `InstallChannels.toolsets: list[AgentToolSet]` (:83); `HandlerCatalog(toolsets: list[ToolsetConfiguration])` (`hook_server.py:375`). Check the published MCP schema of `installer.install` does not change for callers (it is an `@agent_tool`, not `@mcp`, so it should not). Risk: low.
12. **`installer.py:470`:** list what the module exports (`Installer`, `InstallChannels`, `SERVER_CHANNELS`, `Deployment`, `ToolsetInstallFailed`, `ServersNotRegistered`) or delete `__all__`. Risk: none.
13. **`LastInstall` answers `ide` and `folder`** as two properties, and `Installer.create` (`installer.py:370-372`) reads those instead of `saved.get(...)`. `saved` stays for `hand_over_to`. Risk: none.
14. **Docs to match the code** (no code change): the three stale names in the hooks card, the root card and `AGENTS.md` (`AGENTS.md` is changed only by the person, so report it to them); add harness/process to the agent_tools card's dependencies; take *MarkdownFile* out of the markdown card's seam and say that *FrontMatter*, *FlatSettings* and `operation_property` are imported from their files; bring `hooks-runtime-model.md` up to the three-parameter constructors.
15. **Move the spec support of harness/mcp** (`spec_support.py`, `mcp_daemon_doubles.py`, `cdd_home_checkout_examples.py`) into `harness/mcp/examples/`, where `server_lanes_examples.py` already is, and update the 20 spec imports. This is a path change with no design change, but it touches many spec files; do it in one commit of its own. Risk: low, wide.

## Proposed design changes

### 1. One daemon model and one lock file for the hook server and the cdd server

**Problem.** Two long-running servers are built from different classes that do the same steps (`hook_daemon.py:280-507`; `mcp_daemon.py:55-228`). Each has its own address class, published-address file, ping, "who answers" record, start through *BackgroundStart* into a *CappedLogFile*, wait loop and "did not come up" error. Three lock-by-file classes exist beside them (*InstallLock*, `JsonFile.held`, `_SpawnLock`). A fix to one server's start or stop (for example the stale-port wait) is not made in the other.

**Before**

```
hooks/hook_daemon.py                         mcp/mcp_daemon.py, mcp_address.py
HookDaemonIdentity(pid, stamp, repo)         McpAddress(port): url, ping_answer(), send_lane_call()
HookDaemonAddress(host, port, identity)      RunningServer(answer: dict): pid, source, projects, process
  reported(), answers(), handle_stdin()      McpDaemon(home, address, port)
HookDaemonAddressFile(path, host)              ping(), is_running(), ensure(), restart(), stop(),
_SpawnLock(path): claim(), release()           spawn(), status(), _wait_for_ping()
HookDaemon(repo, port)                       ServingProcess(home, address)
  live_address(), is_running(), ensure(),      claim_port(), publish(), withdraw(),
  replace_stale(), stop(), spawn(), serve(),   end_with_owner(), is_this_process()
  claim_port(), _start_once(),               installation/install_lock.py  InstallLock(folder)
  _wait_until_live()                         installation/json_file.py     JsonFile.held()
```

**After**

```
process/server_daemon.py                                              (+ new file)
+ ServerDaemon(port: ExclusivePort, log: CappedLogFile)               abstract
    + running() -> RunningServer | None       ~ was live_address() / ping()
    + is_running(), ensure(), stop(), restart()
    + spawn()                                  uses _command(), _environment(), _folder()
    - _wait_until_answering()                  one loop, one error
+ RunningServer(process: RunningProcess, serves: Path, code: str)     → moved from mcp, HookDaemonIdentity folded in
+ ServerDidNotStart(daemon, seconds, log_tail)                        ~ replaces HookDaemonNotReady and mcp's ServerDidNotStart
process/lock_file.py                                                  (+ new file)
+ LockFile(path, wait_seconds): held(), claim(), release(), holder    → InstallLock's body moves here

hooks:  HookDaemon(ServerDaemon)   keeps serve(), source_stamp, the older-layout takeover
        HookDaemonAddress          ~ host, port, running(): RunningServer  (− pid, stamp, repo, − identity class)
        − _SpawnLock               → LockFile
mcp:    McpDaemon(ServerDaemon)    keeps home, address, this_process
installation: InstallLock = LockFile for an IDE folder (kept as a thin subclass naming the file)
              JsonFile.held()      uses LockFile
```

**Callers affected.** `space/repo` (closes a worktree's hook daemon), `scripts/instances.py`, `scripts/start.py`, `scripts/exercise_hooks.py` (`live_address`, `spawn`), `harness/diagnostics` (reads `McpDaemon.ping`), `hook_installation.py`, `mcp_server.py`, `server_lanes.py`, `server_hooks.py`, `cdd_home.py` (holds an *InstallLock*), and every heavy spec of both daemons.

**Size.** About 12 production files and 8 spec files; roughly 250 lines removed, 150 added.

**What could go wrong.** These are the two processes every chat depends on; the hook daemon's takeover of a port from older code and the cdd server's "second start exits quietly" differ on purpose and must stay in the subclasses. harness/process's card says "never a helper of another class here"; a base class changes that statement. Only the heavy tier shows a regression, and only on Windows for the job-breakaway path.

### 2. A typed session seam for the framework

**Problem.** `ToolCall.session`, `SessionOpener` and `HookPayload.session` answer `Any` (`tool_call.py:29-37`, `:191`; `hook_server.py:128`), and the framework calls into space/session three objects deep in four places (`agent_tools.py:1093`, `mcp_server.py:888`, `hook_server.py:494`, `:566`). The dependency rule "harness imports nothing from space" holds for imports and is broken in practice by attribute names.

**Before**

```
agent_tools/tool_call.py
SessionOpener(Protocol): saved_in(project) -> Any, open_in(call) -> Any, named_in(file, call) -> Any
ToolCall.session -> Any
callers:  session.log.by(chat).tool(name, paths)          agent_tools.py:1093
          session.log.by(chat).failure(error, tool=...)   mcp_server.py:888
          session.chat_injections                         hook_server.py:494
          session.folder.hook_log("dispatch.debug").stamped(text)   hook_server.py:566
```

**After**

```
agent_tools/tool_call.py
+ CallSession(Protocol)                       the session a call works in, as the framework uses it
    + log_tool(call: ToolCall, tool: str)      ~ replaces session.log.by(chat).tool(...)
    + log_failure(call: ToolCall, failure)     ~ replaces session.log.by(chat).failure(...)
    + chat_injections: ChatRuleInjections      → protocol moves here from hook_server.py
    + log_hook_dispatch(text: str)             ~ replaces session.folder.hook_log(...).stamped(...)
~ SessionOpener: every operation -> CallSession | None
~ ToolCall.session -> CallSession | None
space/session/session.py   Session gains the four members (each one line over what it has)
```

**Callers affected.** `agent_tools.py`, `mcp_server.py`, `hook_server.py`, `guidance_actions.py:532` (its own `log_session_invocation`), `space/session` (*Session* and its opener), the agent BDD harness.

**Size.** 6 files, about 60 lines.

**What could go wrong.** *ChatRuleInjections* takes *HookPayload* and *HookResult*, which live in harness/hooks, above agent_tools; the protocol either stays in hooks (and `CallSession.chat_injections` is typed loosely) or those two move down. Decide which before starting. Low risk otherwise: the calls only move one level.

### 3. A channel is an object, and each file channel has its own installation

**Problem.** A channel is a string everywhere (`InstallDestination`, `annotation_kinds.publishes(channel, op)`, `tools_for("mcp")`, `InstallDiagnostics.CHANNELS`, four `channel = "..."` literals). *FileInstallation* writes three kinds of file behind `if self.channel.destination == ...` in five methods, and the install makes six of them so a per-tool fact (`served_on_mcp`) can sit in a constructor (`installer.py:74-78`). *LanguageAdapterInstallation* inherits an interface it does not answer.

**Before**

```
agent_tools:   InstallDestination.MCP / HOOK / SKILL / COMMAND / RULE   (strings)
               AgentTool.install_to_mcp, install_to_hook, install_to_skill, install_to(name), destinations: list[str]
               AgentToolSet.tools_for(name)
annotations:   annotation_kinds.publishes(channel, op), annotated_for(channel, op), name_given_for(channel, op)
installation:  Installation(layout, path, repo): channel: str, install(tool) -> write(tool), track_writes_with(cb)
               FileChannel(destination: str, served_on_mcp: bool)
               FileInstallation(target, channel: FileChannel)    one class, three writers
               LanguageAdapterInstallation(Installation): record(toolset), write_all()
               ServerInstallation(Installation): accepts, published, standup, diagnose, ensure_running, status
```

**After**

```
annotations:   DestinationKind is the channel:  Skill.publishes(op), Skill.name_given(op)      ~ moved from AnnotationKinds
               − AnnotationKinds.of_channel / annotated_for / publishes / name_given_for
agent_tools:   − InstallDestination (the kinds are imported where a publisher needs one; agent_tools asks
                 annotation_kinds.destinations_of(op) -> tuple[DestinationKind, ...])
               AgentTool.destinations: tuple[DestinationKind, ...]         ~ was list[str]
               AgentTool.is_published_to(kind)                              ~ replaces install_to_* and install_to
               AgentToolSet.tools_published_to(kind)                        ~ was tools_for(name)
installation:  Installation(target: InstallTarget, record: InstallRecord)  ~ holds both; − track_writes_with, − install()
                 + destination: DestinationKind
               SkillInstallation, CommandInstallation, RulesInstallation(FileInstallation)   + three subclasses
                 each: relative_path(tool), front_matter(tool), body(tool)   − every `== SKILL` branch
               − FileChannel            (tool.is_published_to(Mcp) is asked per tool)
               LanguageAdapters(target, record)     − no longer an Installation
               ServerInstallation        unchanged here (see proposal 4)
```

**Callers affected.** Every reader of `install_to_*`, `tools_for`, `InstallDestination` (catalog generator, diagnostics probes, guidance, guidance_actions, hooks, mcp, language adapter), *InstallChannels*, *InstallDiagnostics* (takes the channel names from the kinds), `installer_heavy_spec.py` (builds `FileInstallation(InstallTarget(...), FileChannel(...))` in about ten places).

**Size.** About 18 production files, 10 spec files; 300 to 400 lines changed, net smaller.

**What could go wrong.** agent_tools must still import no publisher: the kinds reach it only through `annotation_kinds`, so a tool's destinations are kinds it was handed, never classes it names; a slip here recreates the cycle the annotations module was made to remove. The heavy installer spec compares installed file paths byte for byte, so it will show any path that moved.

### 4. A registered channel says whether it has a server

**Problem.** *ServerInstallation* means two things: "a channel a module above registers with the Installer" and "a channel whose files point at a server". The hook channel is the first and not the second, so it carries three empty operations (`hook_installation.py:48-57`), and the server's own answers are dicts (`diagnose -> dict[str, Any]`, `ensure_running -> dict[str, str]`, the `notice` key read at `installer.py:326`; the same dict built at `hook_server.py:527` and `mcp_server.py:988`).

**Before**

```
ServerInstallation(Installation)
  accepts(tool), published, toolsets, create()
  standup() -> Any, diagnose() -> dict, ensure_running() -> dict[str, str], status() -> list[str], serves_this_process()
HookInstallation: standup/diagnose/ensure_running do nothing
McpInstallation:  all six
HookServer.diagnose() -> dict     McpHost.diagnose() -> dict
```

**After**

```
RegisteredChannel(Installation)            ~ renamed from ServerInstallation; what SERVER_CHANNELS holds
  accepts(tool), published, toolsets, create(), status() -> list[str]
  + server: ChannelServer | None           none for the hook channel
+ ChannelServer                            the server a channel's files point at
  + stand_up() -> StandUp
  + ensure_running() -> list[str]          the status lines the install prints
  + runs_this_process: bool
+ StandUp(tools: list[str], skipped: SkippedTools)     ~ replaces the two diagnose dicts; notice = skipped.notice
HookInstallation: − three empty operations
McpInstallation:  server = McpChannelServer(served, claude_plugins)
```

**Callers affected.** `installer.py` (`_standup_channels`, `ensure_runtimes`, `_runs_inside_a_server`, `_print_channel_notice`), `hook_installation.py`, `mcp_server.py`, `harness/diagnostics` (reads `diagnose()` of both servers and the `exceptions` key), `SERVER_CHANNELS`, the cards.

**Size.** 6 production files, 5 spec files, about 150 lines.

**What could go wrong.** harness/diagnostics writes the `exceptions` list into `diagnostics.json`, which the health band reads; the data written must stay the same shape even though the object in between gains a type. Renaming `SERVER_CHANNELS` is optional and doubles the edit; keeping the name with the new base is honest enough if the card says so.

### 5. An install run and its diagnosis are objects

**Problem.** What an install deployed is a `dict[str, list[str]]` passed through five methods; its colour is written into the report text and found again by scanning for a colour word (`install_diagnostics.py:65`) and by `startswith("!")` (`installer.py:201`). *Deployment* keeps one run's state on an object that outlives the run, and `Deployment.channels` makes a second, "not installing" *InstallChannels* to read a folder.

**Before**

```
Installer: deployment: Deployment, diagnose_install() -> str ("green\n..." or "!\nred\n...")
Deployment(installer): _channels: InstallChannels | None, diagnosis: list[str]
  run(toolsets, replace), install_self(), write_language_adapters(), ensure_runtimes(), diagnose_after_install()
InstallChannels(installer, servers, installing: bool): deployed: list[str], published: dict[str, list[str]]
InstallDiagnostics: channels_in_folder(toolsets, published) -> dict, deployed(channels) -> dict,
  diagnosed(channels) -> (color, text), compared(actual: dict) -> (color, text),
  record_run(channels, report: str), record_install(actual: dict, report, color)
```

**After**

```
+ InstallRun(installer, toolsets, replace)        one per install; made by Installer.install
    channels: InstallChannels                      − the `installing` flag
    publish(), stand_up(), diagnosis: InstallDiagnosis
+ Deployed                                         what a folder holds on each channel
    of_folder(target, toolsets, published), of_last_install(diagnostics)
    + changes_since(last: Deployed) -> DeployedChanges      added, removed, counts, colour
+ InstallDiagnosis(deployed: Deployed, changes: DeployedChanges, server_status: list[str])
    + colour: str, + is_red: bool, + report: str            report is written from the fields, never read back
InstallDiagnostics: record(diagnosis: InstallDiagnosis), last_deployed() -> Deployed | None,
                    write_section(), installed_items(channel)
                    − channels_in_folder, − deployed, − diagnosed, − compared, − record_run, − record_install
Installer.diagnose_install() -> str               = InstallDiagnosis.report, plus the instructions when red
− Deployment                                       → its steps move to InstallRun; install_self and
                                                     write_language_adapters stay on Installer
```

**Callers affected.** `scripts/install.py` (reads `installer.deployment`), `harness/diagnostics` probes (`installed_items`, `write_section` stay), `mcp/server_lanes` and `cdd_home` callers of `write_language_adapters`, `install_diagnostics_spec.py`, `installer_heavy_spec.py`, `guidance_diagnose_spec.py:43` (`record_install({}, "green", "green")`), the installation card's seam (`deployment: run, install_self, ...`).

**Size.** 4 production files, 5 spec files, about 250 lines.

**What could go wrong.** `diagnostics.json` is read by the health band and by people; its entries must be written exactly as now. The card publishes `installer.deployment` as seam, so this is a seam change with callers in `scripts/`. *Deployment* was introduced in an earlier round to shrink *Installer*; replacing it reverses a decision the product owner may remember.

### 6. McpHost holds a request object and a lane router; McpServer is renamed for what it is

**Problem.** *McpHost* has 52 methods. A third of them work out who is asking (`_requested_project`, `_folder_the_chat_works_in`, `_requesting_process`, `_names_a_project`, `_requesting_chat`, `_request_headers`, `_request_client_port`, `_current_request`, `_folder_of_chat`), passing `headers` down. *McpServer* is not a server; the name misleads every reader of `host.checkout_server` and `_server_for(project)`.

**Before**

```
McpHost(checkout_server: McpServer)
  52 methods: protocol handlers, HTTP app, _servers by project, restart, lanes (_lanes, _home set by serve),
  mods, and nine request-reading methods taking `headers`
  _call_sent(arguments, project, tool, chat, answers_a_chat)
McpServer(repo, project): tools, prompts, enroll, start, for_project, restarted, enrolled, answer, invoke
```

**After**

```
+ ChatRequest(headers: Mapping[str, str], client_port: int | None)     one per request, made by McpHost
    + process: ClaudeChatProcess | None      → from _requesting_process
    + chat: ChatPointer | None               → from _requesting_chat
    + project_for(tool) -> Path | None       → from _requested_project and _folder_the_chat_works_in;
                                               raises ProjectNotNamed, ProjectIsClaudeSettings
    + tool_request(tool, host) -> ToolRequest
~ ProjectToolsets                            renamed from McpServer; same members
~ McpHost(checkout_toolsets: ProjectToolsets, lanes: ServerLanes | None = None, home: CddHome | None = None)
    − nine request methods, − route_between_lanes (lanes and home come through the constructor)
    ~ _call_sent(arguments, project, request: ToolRequest)
    ~ checkout_server → checkout_toolsets (the AnsweringMcpHost protocol in agent_tools changes with it)
```

**Callers affected.** `__main__.py` (builds the host, then `serve`), `harness/diagnostics` (reads `call.request.mcp_host.checkout_server`), `McpInstallation.standup`, `AnsweringMcpHost` in `tool_call.py`, the mcp card and its three decision records, and the four mcp host specs.

**Size.** 3 production files plus diagnostics, 5 spec files; about 200 lines moved, 100 renamed.

**What could go wrong.** `cdd.restart` re-imports every module of the checkout and keeps the host object; *ChatRequest* must be made from the re-imported classes the way `_call_sent` does now (`importlib.import_module`), or a restarted server names chats with stale classes. The rename is wide but mechanical. If only one half is approved, take *ChatRequest*: it is where the bugs have been.

### 7. The Claude Code marketplace is its own object, and mods register what they publish

**Problem.** *CddHome* is the runtime record, the server's files, and a plugin marketplace (`cdd_home.py:133-251`). The manifest path of a plugin is built four times in two classes. harness/mcp names the folders of `harness/chat-ui/pane`, `tools/prompt_queue` and `tools/drawio_viewer` (`cdd_home.py:28-38`), which is the framework holding paths of the modules built on it. *ClaudePlugins* has three near-identical install operations answering strings.

**Before**

```
CddHome(folder)
  runtime: source, mode, served_branch, served_worktree, is_installed, is_pinned_to, pin, serve_from, serve_current, install
  server files: state_file, log_path, connect_script, interpreter, server_environment
  marketplace: claude_plugins, write_claude_plugin, write_mod_plugins, publish_mods_of, publish_mods_for_chats,
               board_folder, install_command, take_language_adapters, _publish_mod, _copy_mod, _content_hash, _write_marketplace
  constants: BOARD_MOD_FOLDER, QUEUE_MOD_FOLDER, DRAWIO_VIEWER, MOD_PARTS
ClaudePlugins(home): install_board(), install_queue(), install_cdd() -> "installed" | "missing" | "watched"
  installed, published_version(name), is_board_watched, claude_cli, run()
```

**After**

```
CddHome(folder)                 runtime and server files only
  + marketplace: ClaudeMarketplace          − every marketplace member above
+ ClaudeMarketplace(folder, home)           → from CddHome
    + plugin(name) -> PublishedPlugin
    + publish_cdd_plugin(server), publish_mods(code: Path), publish_mods_for_chats(...)
+ PublishedPlugin(marketplace, name)        the one owner of {name}/.claude-plugin/plugin.json
    + manifest, version, description, publish_from(source: Path, extras)
+ PublishedMods  (PUBLISHED_MODS)           a ClassRegistry-like list the modules above register with:
    register(name, folder_in_checkout, extras)     chat-ui and tools/prompt_queue register; − the three path constants
ClaudePlugins(marketplace)
  + install(plugin: PublishedPlugin) -> PluginInstall(state)       ~ replaces install_board / install_queue / install_cdd
  the board's "watched" and "installed from a checkout" cases stay as a subclass or a flag on its registration
```

**Callers affected.** `mcp_server.py` (*CddEntry*, `McpInstallation.install_mods`, `McpHost._publish_mods`), `mcp_daemon.py`, `scripts/install.py` and the pin scripts (`take_language_adapters`, `install_command`), `harness/chat-ui` and `tools/prompt_queue` (each gains a registration in its package `__init__`), `cdd_home_spec.py`, `cdd_home_lanes_heavy_spec.py`, `cdd_home_checkout_examples.py`.

**Size.** 5 production files plus two registrations, 4 spec files; about 250 lines moved.

**What could go wrong.** The marketplace is published from the code the server runs, which may be a pinned copy where the registering modules were never imported in this process; the registration has to be read from that code (as `RepositoryToolsets.classes()` makes registrations hold), or a pinned server publishes no mods. This is the risky part and the reason the paths are constants today. The split of *CddHome* alone, without the registration, is safe and already removes the graph hit.

### 8. A checkout on disk is read in harness/git

**Problem.** Five places in the area read `.git` by hand: the branch from `HEAD` (`cdd_home.py:376-388`), "main checkout or linked worktree" (`server_lanes.py:148-153`, `mcp_daemon.py:181`), and "the checkout holding this folder" (`chat_pointer.py:139`, `claude_chat_process.py:107`). `space/repo/git_folder.py GitFolder` already reads the same files for the board, above the framework, so harness cannot use it.

**Before**

```
space/repo/git_folder.py   GitFolder(checkout): head_branch, is_on_branch, head_commit, has_ref, branch_names, has_remote, worktrees
harness/git/git.py         Git(folder): run, listed, succeeds
five hand-written readers in harness/mcp, harness/agent_tools, harness/process
```

**After**

```
harness/git/git_folder.py                       → GitFolder moves down from space/repo, unchanged
harness/git/checkout.py                         (+ new file, standard library only)
+ Checkout(folder)
    + holding(folder) -> Checkout               classmethod factory: the checkout holding a folder, else the folder
    + is_main: bool                             its .git is a directory
    + is_linked_worktree: bool                  its .git is a file
    + branch: str                               = GitFolder(folder).head_branch
cdd_home._branch_of, ServerLanes._is_in_main_checkout, ServedCheckout.keep_pinned_current,
ChatPointer._checkout_holding, ClaudeChatProcess.working_folder     → ask Checkout
```

**Callers affected.** `space/repo` (imports *GitFolder* from its new place: `repo.py`, `worktree.py`, `built_once.py` and their specs), the five readers above, the git and process cards.

**Size.** 9 production files, 3 spec files, about 80 lines removed and 50 added.

**What could go wrong.** harness/process is documented as depending on nothing, and `claude_chat_process.py` is imported by the connect script inside Claude Code's ten-second start window; importing harness/git from it adds a module to that start. If that cost matters, `ClaudeChatProcess` keeps its one-line reader and only the other four move.

### 9. Practice and fidelity knowledge leaves markdown, agent_tools and installation

**Problem.** The three lowest modules that read a toolset know what a practice is: `markdown.py:273-282`, `:385-398`, `:495-507` (fidelity blocks; the Stories practice's file names), `agent_tools.py:671`, `:1015`, `:1134`, `:1148`, `:1195` (`is_part_of_practice`, the member named `instructions`), `files.py:107`, `:177-289` (file names of a practice's and a fidelity's instructions and rules). harness/guidance, which owns those rules, sits above all three.

**Before**

```
markdown:     MarkdownText.fidelity_blocks(), fidelity_block(name); MarkdownFile.read_fidelity_subsection(name)
              MarkdownScope(folder, slug, fidelity, format, in_fidelity_block)
              AssetLocation._skip_fidelity_file(path)      names story-map, thin-slice, scenario-
agent_tools:  AgentToolSet.is_part_of_practice; AgentTool.mcp_name / listed_description / description test name == "instructions"
installation: FileInstallation._GUIDANCE_OWN_OPERATIONS, _guidance_slug, _command_stem, _skill_folder, _rule_path,
              _fidelity_one_liner, _fidelity_invoke_parts, _schema_guide
```

**After**

```
markdown:     MarkdownScope(folder, slug, format, + within: tuple[str, ...], + reads_file: Callable[[Path], bool] | None)
                within = the headings a section is read under (("Fidelities", "story_map") for a fidelity)
                reads_file = the owner's own filter for a folder's files
              − fidelity_blocks, − fidelity_block, − read_fidelity_subsection, − _skip_fidelity_file, − fidelity field
              + MarkdownText.block_under(*headings)
agent_tools:  + AgentToolSet.published_name(tool) -> str         default "{slug}.{tool.name}"
              + AgentToolSet.installed_as(tool) -> InstalledName(folder, stem)   default from the class's folder
              + AgentToolSet.listed_parts() -> list[AgentToolSet]                the parts a skill lists, default none
              − is_part_of_practice, − every name == "instructions" test in AgentTool
guidance:     PracticeGuidance and FidelityGuidance override the three operations and hand their scope the
              `within` headings; Stories hands `reads_file` for its examples folder
installation: FileInstallation asks tool.toolset.installed_as(tool) and listed_parts()
              − _GUIDANCE_OWN_OPERATIONS, − _guidance_slug, − _fidelity_one_liner, − _fidelity_invoke_parts
```

**Callers affected.** harness/guidance (`guidance.py`, `practice_supplement.py`, `rule.py`), the Stories practice, the catalog generator (`catalog_practice.py:59` calls `relative_path`), harness/mcp (`mcp_name` readers are unchanged), the heavy installer spec, which pins every installed path.

**Size.** About 10 production files, 6 spec files, 300 lines moved.

**What could go wrong.** Installed file paths and published MCP names are what every chat and every existing install depend on; a single changed path orphans a skill, and a changed name breaks a tool call. The move must be proved by the installer's heavy spec producing identical paths and by the diagnostics showing no added or deleted items. This is the most valuable boundary fix in the area and also the easiest to get subtly wrong; do it after proposal 3, which gives each file channel its own class to ask.

### 10. One way to name a toolset

**Problem.** `ToolsetConfiguration` is five shapes, and `AgentToolSet.instantiate`, `HandlerCatalog.ref_label` and `McpServer._references` each switch on the type (`agent_tools.py:585-612`, `hook_server.py:393-401`, `mcp_server.py:421-424`). `registration_name` is the reference written as text and carried as text (`installer.py:243`, `hook_installation.py:80`).

**Before**

```
ToolsetConfiguration = str | type | dict | AgentToolSetOrigin | None
AgentToolSet.instantiate(toolset), from_items(items, context=)
AgentToolSetOrigin.registration_name -> str
HandlerCatalog(toolsets: list[Any]), McpServer.start(toolsets: Iterable[Any])
```

**After**

```
ToolsetReference                               the one name; text only where it crosses a process
  + of(cls), + parsed(text)                    ~ parsed replaces the constructor taking text
  + toolset_class
  + made(**context) -> AgentToolSet            → from AgentToolSet.instantiate and ToolSubjectLoader.made
AgentToolSetOrigin.reference -> ToolsetReference       ~ was registration_name: str
HandlerCatalog(references: list[ToolsetReference]), ProjectToolsets.start(references)
− ToolsetConfiguration, − AgentToolSet.instantiate, − from_items, − ref_label, − _references
```

**Callers affected.** The ten production callers of `instantiate` / `from_items` (installer, hook server, mcp server, guidance_actions, agent BDD, `scripts/exercise_hooks.py`, tools/prompt_notify), the shell line an installed skill prints (`files.py:269`, which writes `AgentToolSet.instantiate("...")` into installed files), and many specs that pass a class or an instance.

**Size.** About 10 production files, 20 or more spec files, 200 lines.

**What could go wrong.** Installed skills for tools not on MCP carry the `instantiate` call as text; after the change an old install's skill fails until reinstalled, so the installed text and the function must change in the same release, or the function keeps its name. Specs that hand in ready-made instances (to inject fakes) need a path that still takes an instance.

### 11. A call still running is answered as data

**Problem.** `mcp_server.py:727` answers a `_StillRunning` as a sentence; `cdd-connection.ts:116` recognises it by its opening words. Two languages share a rule through a string.

**Before**

```
_ToolCalls.run() -> SentValue | _StillRunning
McpHost._answer_off_loop: answer.message if _StillRunning else answer        → text content
cdd-connection.ts: if (!text.startsWith(`${tool} is still running after`)) return parsed
```

**After**

```
McpHost._answer_chat: a _StillRunning answers CallToolResult(content=[text for the agent],
                       structuredContent={"still_running": {"tool": ..., "seconds": ...}})   + field
cdd-connection.ts: reads result.structuredContent?.still_running                             − STILL_RUNNING prefix test
```

**Callers affected.** `mcp_server.py`, `tool_calls.py`, the TypeScript template and its generated copies under each install's `language-adapters/`, `cdd-connection.spec.ts`, `tool_calls_spec.py`.

**Size.** 3 files and 2 specs, about 40 lines.

**What could go wrong.** Agents still read the sentence, so the text stays; only the adapter's test changes. An app built against adapters from an older install keeps the prefix test until it is reinstalled, so the sentence's opening words must not change in the same release.

### 12. Smaller merges

- **`HookResult` holds its `HookMessages`** (or loses it): keep `result.messages` as the one place the five texts live and have `merge`, `with_description` and `as_dict` read it; remove the five copied attributes. Same for **`HookDaemonAddress`**: hold `identity` and remove `pid`, `stamp`, `repo` copies (or take proposal 1, which removes the identity class). Callers: hooks in space/session, tools/prompt_notify and harness/guidance that read `result.agent_message` and the like (about 15 sites). Size: 2 files plus those readers. Risk: low, mechanical.
- **`LaneCall` becomes `ToolCall.as_sent` / `ToolCall.from_sent`** in `tool_call.py`, and `McpAddress.send_lane_call` takes and answers typed values. Callers: `server_lanes.py`, `mcp_server.py:938-943`. Size: 3 files, 40 lines. Risk: `mcp_address.py` must stay standard library only, so the typed value it takes has to be defined there or passed as an object with `as_sent`.
- **An annotation records itself** (finding in `annotation.py`): every kind sets the annotation object under its flag and reads its fields back (`recorded_on(target).name`, `.disabled`, `.names`, `.key`). Removes `{flag}_name`, `{flag}_disabled`, `reference_flag`, `file_views_flag` and `companion_flags`. Callers: `annotation_kinds.copy_annotations`, every `annotates` reader (unchanged, since the object is truthy), `DeclaredMembers._annotated_function`. Size: 5 files, 80 lines. Risk: `annotates` on a class must still ignore an inherited `@hosted_only`; wrappers copy one attribute instead of three, which is simpler, but any code that sets `_hook_disabled` by hand (search before starting) breaks.
- **Progress belongs to the call:** `ToolCall.report_progress(message)` with the reporter held on the call, and `report_progress(message)` kept as the one-line function authors call that asks `CALLS_BEING_ANSWERED.current`. Removes `progress._reporter` and `reporting_to`. Callers: `mcp_server.py:823-830`, `worker_process.py`, harness/graph's build. Size: 4 files, 30 lines. Risk: a call made in process with no reporter must stay silent.

## Graph hits judged noise

| File:line | Rule | Why it is noise |
|---|---|---|
| harness/agent_tools/.context/agent-tools-model.md:1 (`ExpansionResult` copies the fields of `ExpansionResult`) | do-not-invent-parallel-object-models | The model document describes the code's class; the scanner read the document and the code as two classes. |
| harness/agent_tools/.context/agent-tools-model.md:1 (`fn`, `value`) | use-intention-revealing-names | `value` is a property setter's parameter; `fn` is in the document only (`Collect(fn: Callable)`, line 396), where the code says `operation`. A stale line in the document, fixed with it. |
| harness/agent_tools/.context/agent-tools-model.md:212 (`AgentInstructions` takes 4 parameters) | limit-operation-parameters | A dataclass's generated constructor: creation is exempt. |
| harness/agent_tools/.context/agent-tools-model.md:1, :212 (`arguments`, `collection`, `context`, `instance`, `member`, `name`, `node`, `operation`, `parent`, `return_type`, `roots`) | use-typed-signatures | The document omits or shortens types the code has (`arguments: dict[str, Any]` is a tool call's JSON arguments, which have no narrower type). |
| harness/hooks/.context/hooks-runtime-model.md:1, :60 (`HookDaemonAddress` 5, `HookResult` 7, `HookInstallation` 5 parameters; untyped `user_message`, `toast`, `item`, `toolset`, `hooks`) | limit-operation-parameters, use-typed-signatures, use-intention-revealing-names | The document is stale: the code's constructors take three typed parameters each. Not a code violation; the document needs bringing up to date (fix 14). The code's way of reaching three parameters is its own finding (*HookMessages*, *HookDaemonIdentity*). |
| harness/markdown/.context/markdown-collection-model.md:19 (`parent`) | use-typed-signatures | `parent: Owner | None` is generic in the owner's class by design; any class can own markdown. |
| harness/mcp/mcp_server.py:945 `_lane_reply` | use-exceptions-properly, never-swallow-exceptions | The failure is not dropped: it is answered to the other lane by its kind and message, and that lane raises *LaneCallFailed* for the chat (`server_lanes.py:97-98`). Catching every exception is right at the edge of a process. |
| harness/mcp/server_lanes.py:32 `LaneCall.__init__`, :55 `ServerLane.__init__` (4 parameters) | limit-operation-parameters | Constructors of a record and of a lane made in one place; creation is exempt. (*LaneCall* duplicating *ToolCall* is reported separately.) |

Graph hits in the area judged **real** and carried into the findings above: `deep-module` for harness/annotations and harness/markdown; `HookDaemonIdentity` and `HookMessages` copying fields; `CddHome` over its public-operation budget; `LaneCall.from_data(data)`; `mcp_address.py:78 lane_call` untyped; `mcp_server.py:695 _call_sent` with five parameters.
