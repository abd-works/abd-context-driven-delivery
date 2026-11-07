# space/session
*Session* is one named piece of work in a project — a board ticket's work, or `main`, which works on the whole repository — so every action, log line, handoff, and validation report lands in the folder of the work it belongs to. A session lives in `.sessions/{name}/`: its `session.json` (title, scope, parent, workpath, and practice roots), its `session.log`, its handoffs, and its validation reports. A closed session moves to `.sessions/_complete/{name}/`. `Session.current()` is the open session of the project the running call names.

The *workpath* is the folder a session works in; its practices write under it and its graph loads from it. An empty workpath is the whole repository.

*PracticeSessionOutput* is what one practice has in one session: whether it is on, the guideline it works with at its current fidelity and format, the folder it writes under, the files each fidelity declares there, and its graph. `session.practice("stories")` returns it.

A *Loop* is one context–generate–evaluate cycle marked in the session log, so the lines of one cycle can be read back together with the chat that produced them. *ChatPointer* names the chat a log line came from — its id, its transcript, and the transcript lines the line covers — so `session.read_loop` can put that chat's words back under the line.

*ThrowawayProject* is an empty project a spec works in, so the actions a spec runs write to their own session log instead of the log of whoever is working in the repository.

The MCP tools are `session.current`, `session.switch`, `session.close`, `session.choose_workpath`, `session.files`, `session.folder_files`, `session.read_file`, `session.mark_loop`, `session.read_loop`, and `session.append_log`; per practice, `practice-session-output.enable`, `practice-session-output.choose_root`, and `practice-session-output.use_default_root`; and `session-diagnostics.session_diagnostics` probes the session log through the live MCP host. The commands `/current-session`, `/switch-session`, `/close-session`, `/mark-loop`, `/read-loop`, and `/append-log` call them.

- **Purpose:** Keep the state of one piece of work — where it works, which practices it uses and where they write, and the log of what was done — so any chat or tool can pick the work up from its folder.
- **Seam (terms):** Session, PracticeSessionOutput, Loop, ChatPointer, ThrowawayProject, `session.current`, `session.switch`, `session.close`, `session.choose_workpath`, `session.files`, `session.folder_files`, `session.read_file`, `session.mark_loop`, `session.read_loop`, `session.append_log`, `practice-session-output.enable`, `practice-session-output.choose_root`, `practice-session-output.use_default_root`, `session-diagnostics.session_diagnostics`
- **Dependencies (one-way):** `space` (*WorkState*, *ContextConfig*, `working_on`), `space/repo`, `tools/file_manager`, `harness/agent_tools`, `harness/installation`, `harness/mcp`, `harness/guidance`, `harness/graph`, `harness/hooks`, `cdd_guidance/actions` (*Generate* and *Validate*, in the session diagnostics probe). `space/repo`, `tools/file_manager`, `harness/agent_tools`, `harness/guidance`, `harness/hooks`, and `harness/mcp` import `space/session` back; these cycles, and the upward import of `cdd_guidance/actions`, are tracked in `.sessions/_backlog/break-module-dependency-cycles.md`.

## Constraint

Name the session work is for. Work asked for a named session — a board ticket's handoff, decision record, or validation — goes to that session through `Repo.session_named(name)`, never to whichever session the chat has open; a name the project has no session for raises `SessionNotFoundError`. Read another session with `Session.load` or `Repo.session_named`, which do not make it current; only `session.switch` changes the open session. Write large or temporary outputs (graph JSON, probes, reports) under the session's folder, not beside the work. Specs that run actions open a *ThrowawayProject* and close it after each example.
