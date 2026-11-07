# What changed: Clean Engineering pass on `ensure-domain-orientation-refactor`

48 commits from `d6c41b23`, 1,259 files outside the catalog and session folders; Python is 5,700 lines smaller. Every finding in `clean-engineering-validation.md` (rounds 1–2) and `clean-engineering-validation-round3.md` (the re-validation) was fixed or deliberately decided. The full suite passes: 3,201 examples, 0 failed, plus every heavy spec (servers, browsers, installer, real git).

## Bugs fixed (34 in rounds 1–2, ~20 more in round 3)

- **MCP host:** a timed-out call keeps running and identical calls join it instead of piling up; the listener survives WinError 64; errors come back flagged as errors.
- **Data that was being erased or lost:** a malformed `config.json`, `hooks.json` or `.mcp.json` is refused, not overwritten; an unreadable spec no longer re-renders over hand-written tests; every practice format now round-trips (Stories, DDD, UX, Clean Engineering — bases, stereotypes, story types, scenarios, actors), each with a round-trip spec.
- **Wrong place, wrong session:** paths resolve against the call's session, not the server's folder; the catalog, prompt log, Granola and diagnostics act for the project the call names; hooks follow a session switch.
- **Failures hidden:** recipe lines, parse errors, git errors, worktree removal and install records now raise named errors instead of returning a fallback.
- **Imports of deleted code** (agent specs, scan helpers, sketch renders) fixed.

## Design changes

- **One call, one session.** Every MCP call is a `ToolCall` that carries its own project, chat and session; each action is made for that session. All global "current" objects are gone (Session, Board, Graph, FileManager, the serving host, `working_on`).
- **One owner per concept.** One registry of practices and one of actions; stages defined once; one `Violation`; the parsed practice object is the graph node; one saved-graph shape; one mark spelling (`@mcp`, `@skill`, `@hook`); `Name` for every case conversion; `Git` for every git call.
- **No second object models.** The board sends objects and references, not string and slug copies; the chat bar and board app use the generated adapter types; ProjectTicket, Workspace, ToolRequest, GuidanceCatalog and the scraped catalogues are deleted.
- **No dependency cycles.** The framework imports nothing above it; practices and space register with it (`GraphPractice`, `ToolCall.open_sessions_with`, `HookServer.show_toasts_with`). `harness` gained `name`, `marks`, `process`, `installer`, `diagnostics`, `sub_agent`.
- **Smaller classes.** Session and Repo split into objects with one job each (Sessions, SessionLog, SessionFiles, Handoffs, DecisionRecords; Repo, Branch, Commit, Worktrees); the Installer split into four; Validate split into three.
- **Moves.** The Session Board is `space/kanban`; handoff and decision records live in `space/session`; the Claude Design story canvas lives in UX.
- **Validation itself.** Scanners now catch what they missed (copies across files, cycles, the 40% public measure, swallowed exceptions, packed parameters, `current` as a global); each validate call writes its own graph and report; the judge is told to judge the graph at model and code.
- **Documents.** Every module card, model document and diagram matches the code; the catalog is regenerated from this branch.

## Decisions

All 37 are logged with their reasons at the end of `clean-engineering-validation.md`. The ones that change how you work:

- Buttons build the command they put in the chat box; server-side rules stay in Python (generate renders the earlier fidelity itself).
- ProjectTicket deleted; `iterate.mark_iterate_round`; `create_rule`; rule slugs `story-scenarios-at-most-seven` and `outline-entries-loop-over-examples`.
- Handoff and decision records are `session.*` operations; `sessions.current` / `sessions.switch`.
- The Clean Engineering Miro adapter is removed (not a listed format, unreachable).
- Saved graphs (`.context/graph.json`) are no longer tracked; they are a cache.

## What you need to do

- **Rotate the `CURSOR_API_KEY`.** It was committed in `agent_bdd/conf/.secrets`; the file is now untracked and ignored, but the key is still in git history.
- **AGENTS.md** (which agents may not edit) needs: harness imports nothing above it and offers hook-in points; stages live in `harness/guidance/stages.py`; practices keep rule-example spec support in `rules/rule_examples.py`; `harness/installation/AGENTS.md` should name `ContextConfig` and `RepositoryToolsets`; `tools/prompt_notify/AGENTS.md` line 2 describes a deleted lookup.
- **The CDD MCP host still serves the pinned main runtime.** Once this branch merges, update the runtime so chats get the new operations and the new validate scanners.
- **`board.show`** now sends each practice's guidance text (~200 KB more per read). If that is too slow, send practices by reference and read the text separately.

## Left on purpose

`get_fact`/`set_fact` (~150 callers) and `data_of` stay as they are; `FileInstallation` still has 30 methods; `tools/file_manager` and the Clean Engineering class model are above 40% public (their cards say why); the session opener registers when `space/session` is imported, because the framework may not import space.
