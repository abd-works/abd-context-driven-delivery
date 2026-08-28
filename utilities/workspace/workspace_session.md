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

When launching `/cli-agent`, the parent does not call `open` or `start_work_session`. CliAgent opens the session, switches to that path, and binds doer/judge.

Do **not** separately chain `read_context_index` or `record_context_root` from lifecycle bodies — `open` already does that.

## Layout

Two different folders. Do not invent `{path}/.context/{session-name}/` and do not write markdown generate under `{default_workspace_folder}/.context/` or `Scenarios/.context`.

- **path** — durable tool root; code/modules → `{path}/` (or `{path}/{default_workspace_folder}/` for code channels)
- **docs_dir** — `{path}/.context/` — sketches, generated artifacts (`story-map.md`, `scenarios/`, models, module-context), and `grill-answers.md` (survives across sessions). `save_sketch` / `write_grill_answer` destination is `session.path` (or `session.docs_dir`).
- **folder** — `{path}/.context/sessions/{name}/` — `session.md`, handoff, `handoff-latest.md`, `mistakes.log`, `logs/`
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

Write the End section on `{folder}/session.md`. If a turn is still open, finish (commit) that turn first. Push the session branch. Merge with main so the work lands on main — do **not** checkout `main` in a worktree you are about to delete. If the worktree is clean (no dirty files, no stash), `git worktree remove` it. If dirty or stash remains, leave the worktree.

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
