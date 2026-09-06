# workspace — module context

## Purpose

Manage a **workspace root** and the **work sessions** under it: where durable artifacts live, where session temps live, how git isolation works, and how turns/commits are tracked.

Two folders matter — never confuse them:

| Folder | Holds |
|--------|--------|
| `{working_path}/.context/` | Durable artifacts local to where you work — sketches, generated markdown, grill-answers, `context-index.md` |
| `{repo_root}/.context/sessions/{name}/` | Session temps at **repository root** — `session.md`, `model`, `logs/` (not under the worktree) |

Closed sessions archive to `{repo_root}/.sessions/closed/{name}/`.

Path helpers: `SessionPaths.docs_dir(working_path)`, `SessionPaths.session_dir(repo_root, name)`, `SessionPaths.repository_root(path)`.

## Public surface

### `Workspace`

Parent of `.context/`. Owns `work_sessions`, `current_work_session`, and `path_overrides`.

| Operation | What it does | Impact |
|-----------|--------------|--------|
| `load()` | Scan `.context/sessions/*` and read path overrides from `context-index.md` | In-memory only — no writes |
| `save()` | Write the path-override table to `.context/context-index.md` | Updates durable index |
| `lookup_path(tool, fidelity)` | Resolve a stored path override | Read only |
| `upsert_path(tool, fidelity, path, default_path)` | Add/update/remove a path override, then `save()` | Rewrites `context-index.md` |
| `open(...)` / `open_work_session(...)` | Start or resume a named work session | Sets `current_work_session`; delegates to `WorkSession.open()` — see below |
| `get_session_model(session)` | Read preferred model id from disk | Read `{session}/model` |
| `set_session_model(model, session)` | Persist preferred model id | Write `{session}/model` |
| `list_session_models()` | List known model ids | Read only |

### `WorkSession`

One named sprint under `.context/sessions/{name}/`. Owns `git`, `open_turn`, `turns`, `repairs`, and the session file kit.

| Operation | What it does | Impact |
|-----------|--------------|--------|
| `open(name, goal, fidelities, contexts, path)` | **Start or resume** a session | See **Open impact** below |
| `close(outcome, handoff)` / `close_session(...)` / `finish_work_session(...)` | **Stop** a session | See **Close impact** below |
| `ensure_started(goal, ...)` | Create session folder + `session.md` if missing | Writes `session.md` **only on first create**; mkdir; may copy `model` from primary repo |
| `load(path, name)` | Load an existing session from disk | Read `session.md`; attach existing git worktree if present |
| `read_context_index()` | Load tool-root map | Read `.context/context-index.md` |
| `record_context_root(root, note)` | Register this tool's durable root in the index | Upsert `context-index.md` |
| `consume_handoff()` | Read then delete handoff files | Deletes `handoff-latest.md`, `handoff.md`, `handoffs/` under session folder or docs_dir |
| `append_trail(call)` | Record a tool invocation | Appends `logs/events.log`; attaches to open turn if any |
| `cleanup()` | Remove session logs | Deletes `logs/` directory |
| `save_chat(path)` | Attach a chat transcript to the close commit | Git note on `refs/notes/chats` + tag `chat/session/{branch}` |
| `chats()` / `worksession_chat(name)` | List saved chat paths for a session | Read git notes/tags |
| `set_session_model(model)` / `session_model` | Read/write `{folder}/model` | Persist model preference for this session |

### `Turn`

Scoped unit of work inside a session. States: Backlog → In Progress → Done.

| Operation | What it does | Impact |
|-----------|--------------|--------|
| `open(action)` / `open_turn` | Start a turn | Binds to current work session; turn state → In Progress |
| `finish_turn(result)` | Close the hanging turn | Commits dirty scope via `git.commit()` when a session is bound; records outcome |
| `record_mistake(...)` | Log a mistake on the open turn | Annotates git notes on the turn commit |
| `record_correction(...)` | Link a fix to a mistake | Adds correction commit + git note link |

### `SessionPaths` / `GitRepo`

| Type | Role |
|------|------|
| `SessionPaths.docs_dir(dest)` | Resolve durable `.context/` dir |
| `SessionPaths.session_dir(dest, name)` | Resolve session temp dir |
| `GitRepo` | Checkout, commit, push, fetch/pull, worktrees, merge, git notes — collaborator on `WorkSession.git` |

## Open impact (`WorkSession.open`)

1. **Folder** — creates `.context/sessions/{name}/` if needed.
2. **`session.md`** — written **only on first create** (goal, fidelities, contexts, start date). Resume does **not** rewrite Start.
3. **Git worktree** — if session branch is not main/default: create or reuse a **sibling worktree** (`{abbrev}-{session-name}` next to the primary clone). Session work happens there; primary checkout is not stolen.
4. **`model`** — copied from primary session or default when missing.
5. **Context index** — read; tool root recorded when `context_index_key` is set.
6. **Handoff** — if `handoff-latest.md` / `handoff.md` / `handoffs/` exists: read once, **delete**, return text to caller. Not durable state.
7. **`cli-agent.json`** — read if present (resume CLI bindings).
8. **Session log** — bound to `logs/events.log`.

## Close impact (`WorkSession.close`)

1. **Open turn** — finished first (commit if dirty).
2. **`logs/`** — deleted (`cleanup`).
3. **`cli-agent.json`** — deleted; CLI processes stopped.
4. **`session.md`** — **always rewritten** with End date, outcome, handoff.
5. **Git** — commit `session.md` + scope paths if dirty; push session branch.
6. **Chats** — transcript paths saved to git notes before bindings cleared.
7. **Archive** — move `{repo_root}/.context/sessions/{name}/` → `{repo_root}/.sessions/closed/{name}/` (creates `.sessions/closed/` when missing). Durable `{working_path}/.context/` artifacts are **not** moved.
8. **Worktree** — merge session branch onto main **without** checking out main in the session tree; remove worktree **only when clean** (no dirty files, no stash). `events.log` does not count as dirty.

## On disk after open vs close

| Artifact | After open | After close |
|----------|------------|-------------|
| `session.md` | Start block (new) or unchanged (resume) | Start + **End** block — archived to `{repo}/.sessions/closed/{name}/` |
| `model` | At `{repo}/.context/sessions/{name}/model` | Moved with session folder to `.sessions/closed/{name}/` |
| `logs/events.log` | Grows during session | **Deleted** (before archive) |
| `cli-agent.json` | Present if CLI was bound | **Deleted** (before archive) |
| `handoff-*.md` | Deleted if consumed on open | — |
| `.context/sessions/{name}/` | Session temps | **Removed** (folder archived) |
| `.context/` durable files | Untouched by open/close | Untouched (only git-committed if in scope) |

## Constraint

- Durable artifacts and session temps are **different folders** — never write sketches or generate output under `sessions/{name}/`.
- Session git isolation: non-default branches get a sibling worktree; never checkout the session branch in the primary clone.
- `events.log` is gitignored and is not a dirty signal for worktree removal.

## Dependencies

stdlib (+ optional yaml); `tools.tool`; consumed by `context_tools.base.base_context_tool`.
