# workspace — module context

## Purpose

**Workspace** aggregate (`workspace.py`): parent of `.context/`, owns many **WorkSession**s,
**currentWorkSession**, and **pathOverrides**. **GitRepo** is the git collaborator on
`WorkSession.git`. Session git work for a non-default branch lives in a **sibling
worktree** so the primary clone checkout stays put. **SessionLog** records
expand|run trails explicitly (not via `@log`).

## Primary use case

`BaseContextTool.workspace` is a **Workspace**. Opening a sprint calls
`Workspace.open_work_session(...)` → sets `currentWorkSession`. Turn/git go through
`currentWorkSession` (`openTurn`, `git`).

## Layout

```
{workspace.path}/                       # Workspace.path — parent of .context/
  .context/                             # WorkSession.docs_dir — sketches, generated, grill-answers
    story-map.md
    scenarios/
    grill-answers.md                    # durable across sessions
    context-index.md                    # PathOverride persistence
    sessions/{name}/                    # WorkSession.folder — session temps only
      session.md
      handoff-latest.md                 # deleted on the next open (consume_handoff)
      logs/events.log                   # gitignored + .cursorignore; not a dirty signal
```

## Public API

- `Workspace` — `@agentic_toolset` (`workspace.workspace:Workspace`); `path`, `work_sessions`, `current_work_session`, `path_overrides`;
  `load` / `save` / `lookup_path` / `upsert_path` / `open_work_session`. CLI context is `workspace` path. `open` starts or resumes a named work session.
- `WorkSession` — `@agentic_toolset` (`workspace.workspace:WorkSession`); back-ref `workspace`; owns `git`, `open_turn`, `turns`, `repairs`, trail;
  session.md kit (`ensure_started`, `close`, `close_session`, context index helpers);
  `start_work_session` / `finish_work_session` `@agent_tool` with `@prompt` names
  `start-work-session` / `finish-work-session`. CLI context is `workspace` path + `session` name (session may come from the current `session/` git branch).
  A `/cli-agent` parent does not call `start_work_session`; CliAgent opens the
  session, switches to that path, and binds doer/judge. Resume does not rewrite Start.
  **Open** (`ensure_started`): stay in the primary clone when the session branch is
  main/default; otherwise create or reuse a sibling worktree, fetch/pull, and do
  session work there — do not checkout the session branch in the primary folder.
  Sibling path is `{abbrev}-{work-session-name}` next to `primary_root()`:
  abbreviate the clone folder (first token, then first letter of each later
  hyphen/underscore token; e.g. this repo `abd-context-driven-delivery` →
  `abd-cdd-<slug>`). Never hardcode a repo prefix.
  **Close** (`close` / `finish_work_session`): finish an open/forgotten turn,
  write End, commit `session.md` if dirty, push, merge onto main without
  checking main out in the session tree, then `git worktree remove` only when the
  tree is clean (no dirty files, no stash). `events.log` is ignored (Cursor + git)
  and does not count as dirty.
- `SessionPaths` / `docs_dir` / `session_dir` — durable `{path}/.context/` vs temps `{path}/.context/sessions/{name}/`
- `GitRepo` / `NullGitRepo` — `checkout_or_create`, `commit`, `push`, worktrees
  (`list_worktrees` / `worktree_for` / `add_worktree` / `remove_worktree`),
  `fetch` / `pull` / `fetch_pull`, `merge_from` / `push_to`, notes (`note` /
  `read_notes` / `find_mistakes`). Session branch naming and sibling-path policy
  are WorkSession's.
- `Turn` — `@toolset` (`workspace.workspace:Turn`); CLI context is `workspace` path + `session` name (session may come from the current `session/` git branch). Owns `mistakes` and optional `correction`; `record_mistake` / `record_correction` attach to the open turn before `finish`. `finish_turn` closes the hanging turn when a work session is bound; if none is, it commits (and pushes when it can) on the current checkout so the work is still tracked.
- `Turn` / `Mistake` / `Correction` / `PathOverride` / `ToolCall` / `TurnCommit`
  (`TurnCommit.name` = git commit subject from `Turn.name`, not a uuid slug)
- `SessionLog` — `append` → events.log + openTurn.toolCalls; **delete `@log` as host primary**
- `ContextToolHost` — OO host used by `workspace_spec` (production host is `BaseContextTool`)

## Dependencies

stdlib (+ optional yaml); `tools.tool`;
consumed by `context_tools.base.base_context_tool`
