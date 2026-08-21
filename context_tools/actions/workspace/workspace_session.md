# Session Guidance

`Session` tracks three things:

| Name | Meaning | Example |
|------|---------|---------|
| **path** | Durable tool root (`active.path`) | `…/sandbox` |
| **folder** | Sprint folder (`active.folder`) | `…/sandbox/.context/sessions/{name}/` |
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

```yaml
tool: open   # via self.open() from BaseContextTool
```

Do **not** separately chain bind + read_context_index + record_context_root from lifecycle bodies — `open` already does that.

## Layout

- **path** — docs → `{path}/.context/`; code/modules → `{path}/`
- **folder** — `session.md`, grill-answers, engagement sketches, handoff, `mistakes.log`
- **context-index** — `{workspace_root}/.context/context-index.md`

## Root when `path` omitted

1. context-index entry for `context_index_key`
2. else `{workspace_root}/{default_workspace_folder}`

## Git branch on every session start

Handoff is only one way a session comes back later. **Every** `open` / `ensure_session` / `create_session` does this check — new sprint or resume of an existing one.

**Reuse `session/{name}`.** Do not mint `session/{name}-2` just because we started again. After a handoff you may be on `main`, or on a later session branch that was created from `main` (so it does not have this session's commits). Restart still checks out `session/{name}` when that branch already exists — same machine or another person who has the session name. You would have to be on that branch to see the work anyway; the start check is how we get there.

1. Compare HEAD to `session/{name}`.
2. Already on that branch → continue (dirty tree is fine; you are already there).
3. Not on it, **and the working tree is dirty** → **do not checkout**. Ask:
   - bring this work onto the existing session branch (merge / pull latest into it), or
   - start a continuation branch `session/{name}-2` (then `-3`, …) — only if they choose that.
4. Not on it, tree clean → checkout `session/{name}` if it exists, otherwise create it.

Eval still only **commits** after a turn. It does not decide the switch.

# Ensure Session

Load `{path}/.context/sessions/{name}/session.md` if present; otherwise create it. `name` defaults to the constructor session.

```yaml
tool: ensure_session
arguments:
  name: <kebab-slug; optional if constructor session set>
  path: <optional; overrides durable root>
  goal: <optional>
  fidelities: <optional>
  contexts: <optional>
```

`create_session` is the same tool (alias) for older call sites.

# Create Session

Same as **Ensure Session** — load or create the sprint under `path`.

```yaml
tool: create_session
arguments:
  name: <kebab-slug>
  path: <optional; overrides durable root>
  goal: <optional>
  fidelities: <optional>
  contexts: <optional>
```

# Close Session

Write the End section on `{folder}/session.md`.

```yaml
tool: close_session
arguments:
  outcome: <optional>
  handoff: handoff.md
```

# Read Context Index

Read `{workspace_root}/.context/context-index.md` (creates nothing). Prefer an existing entry for this tool over guessing a root. Also called from **`open`**.

```yaml
tool: read_context_index
```

# Record Context Root

Upsert this toolset's root into the context index after the durable path is known. Also called from **`open`** when `context_index_key` is set.

```yaml
tool: record_context_root
arguments:
  root: <optional; defaults to path>
  note: <optional>
```

# Open

One tool — ensure sprint + load context index + record root when keyed. Read **Session Guidance** for `path` / `folder` / `context_index` semantics and git branch rules. Do not chain `ensure_session`, `read_context_index`, and `record_context_root` separately when `open` is in the tool list.

```yaml
tool: open
```
