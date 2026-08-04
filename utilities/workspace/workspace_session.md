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

**`open`** — single action before generate / grill / sketch / iterate / validate:

1. Resolve durable root (`path`)
2. Ensure sprint exists (load or create)
3. Load context index if present
4. Record this tool's root when `context_index_key` is set

```yaml
action: open   # via self.workspace.open() from BaseContextTool
```

Do **not** separately chain bind + read_context_index + record_context_root from lifecycle bodies — `open` already does that.

## Layout

- **path** — docs → `{path}/.context/`; code/modules → `{path}/`
- **folder** — `session.md`, grill-answers, engagement sketches, handoff, `mistakes.log`
- **context-index** — `{workspace_root}/.context/context-index.md`

## Root when `path` omitted

1. context-index entry for `context_index_key`
2. else `{workspace_root}/{default_workspace_folder}`

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
