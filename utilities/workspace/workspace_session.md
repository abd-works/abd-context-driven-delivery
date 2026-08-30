# Session Guidance

`Session` tracks three things:

| Name | Meaning | Example |
|------|---------|---------|
| **path** | Durable tool root (`active.path`) | `…/sandbox` |
| **docs_dir** | Sketches + generated artifacts (`active.docs_dir`) | `…/sandbox/.context/` |
| **folder** | Session temps (`active.folder`) | `…/sandbox/.context/sessions/{name}/` |
| **context_index** | `{workspace_root}/.context/context-index.md` when present | tool → root map |

## Constructor / run context

- `workspace` — workspace root where `context-index.md` lives (default `"."`)
- `path` — durable tool root
- `session` — sprint slug under `{path}/.context/sessions/{name}/`

## One call to open

**`open`** — single tool before generate / grill / sketch / iterate / validate:

1. Resolve durable root (`path`)
2. Ensure sprint exists (load or create)
3. Load context index if present
4. Record this tool's root when `context_index_key` is set
5. Bind eval turn capture when a host is attached

```yaml
tool: open
arguments:
  name: <optional kebab-slug; defaults to constructor session>
  path: <optional; overrides durable root>
  goal: <optional; first create only>
  fidelities: <optional; first create only>
  contexts: <optional; first create only>
```

Resume leaves `session.md` Start as written. Goal / fidelities / contexts apply on first create only.

**Consumed handoff.** If `handoff-latest.md` (or `handoff.md` / `handoffs/`) is present, `open` reads it once and **deletes** it. That text is only for this open. Do not keep tracking Resume / next-action / increment state from a handoff. After consume, the source of truth is `session.md`, `grill-answers.md`, sketches, and generated artifacts. Do not re-read a deleted or archived handoff as current work.

When launching `/cli-agent`, the parent does not call `open` or `start_work_session`. CliAgent opens the session, switches to that path, and binds doer/judge.

Do **not** separately chain `read_context_index` or `record_context_root` from lifecycle bodies — `open` already does that.

## Layout

Two different folders. Do not invent `{path}/.context/{session-name}/` and do not write markdown generate under `{default_workspace_folder}/.context/` or `Scenarios/.context`.

- **path** — durable tool root; code/modules → `{path}/` (or `{path}/{default_workspace_folder}/` for code channels)
- **docs_dir** — `{path}/.context/` — sketches, generated artifacts (`story-map.md`, `scenarios/`, models, module-context), and `grill-answers.md` (survives across sessions). `save_sketch` / `write_grill_answer` destination is `session.path` (or `session.docs_dir`).
- **folder** — `{path}/.context/sessions/{name}/` — `session.md`, `mistakes.log`, `logs/`. A live `handoff-latest.md` exists only until the next `open`, which consumes and deletes it.
- **context-index** — `{workspace_root}/.context/context-index.md`

## Root when `path` omitted

1. context-index entry for `context_index_key`
2. else `{workspace_root}/{default_workspace_folder}`

## Git worktree on every session start

Handoff is only one way a session comes back later. **Every** `open` / `ensure_started` isolates session git work.

**Reuse `session/{name}`.** Do not mint `session/{name}-2` just because we started again.

1. If the session branch is `main` (or the clone default) → stay in the primary clone. Do not add a worktree for main.
2. If a worktree for `session/{name}` already exists → switch to it (retarget `WorkSession.git`). Do not create a second one.
3. Otherwise create a **sibling** worktree next to the primary clone. Never add a worktree inside the clone. Never checkout the session branch in the primary folder (that steals the checkout from other chats).
4. Fetch/pull so the worktree has the latest from the repository. Do all session work in that tree.

Sibling path: `{abbrev}-{work-session-name}` beside `primary_root()`. `{work-session-name}` is the WorkSession kebab slug (not `session/...`). `{abbrev}` comes from the **primary clone folder name**: keep the first hyphen/underscore token, then the first letter of each later token (`abd-context-driven-delivery` → `abd-cdd`; `story-ui` → `story-u`; `my-app` → `my-a`; `widgets` → `widgets`).

# Close Session

Write the End section on `{folder}/session.md`. If a turn is still open, finish (commit) that turn first. Call `cleanup`: this session removes its own logs. Use `cli_agent` — if that property is set, the agent ran; call `cleanup` on it. Do not import CliAgent or read `cli-agent.json` here. Do not delete durable generate under `{path}/.context/` or product files.

Save chat file path(s) with `save_chat` before CLI bindings are cleared: a note on the close commit (`refs/notes/chats`) and an append on the annotated tag `chat/session/{name}`. Always attach **this** Cursor chat via `CURSOR_CONVERSATION_ID` (per agent process — safe with several chats open; never “newest transcript by mtime”). Also attach CliAgent doer/judge chats when those ids are bound. Look up later with `/worksession-chat` (`worksession_chat` / `chats()`). Close commits `_commit_paths()` (scope + session artifacts), not session.md alone.

```yaml
tool: worksession_chat
arguments:
  name: <optional kebab-slug or session/... branch>
```

**Before close:** run `git status` in the worktree. Delete only temps you can attribute to this session and know are disposable (examples: `Harness.write_deploy` output under `.cursor/commands` / `.cursor/skills`, agent BDD logs under `.context/.agent_bdd_sessions/` from spec runs, `_req*.yaml` scratch). Use judgment from the session — code cannot guess what is real. Never ask the user whether to delete the worktree.

Push the session branch. Merge with main so the work lands on main — do **not** checkout `main` in a worktree you are about to delete. Drop any stash (`clear_stash`) — stash must never keep a session worktree. If the worktree is clean (no dirty files), `git worktree remove` it. If dirty remains after you removed known temps, leave the worktree and report what blocked removal.

```yaml
tool: close_session
arguments:
  outcome: <optional>
  handoff: handoff.md
```

# Open

One tool — ensure sprint + load context index + record root when keyed + bind eval. Read **Session Guidance** for `path` / `folder` / `context_index` semantics and git branch rules.

When no sprint slug exists yet: confirm path and kebab slug with the user, then call **`open`** with `name` (or set run context `session=` first).

```yaml
tool: open
arguments:
  name: <optional kebab-slug>
  path: <optional>
  goal: <optional; first create only>
  fidelities: <optional; first create only>
  contexts: <optional; first create only>
```
