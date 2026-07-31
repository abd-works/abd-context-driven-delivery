# Session

Every BaseContextTool exposes a **`session`** resource (`Session`) and workspace tools from this kit.

## Constructor / run context

- `workspace` — project/sandbox root (default `"."`)
- `path` — tool working area
- `session` — sprint slug (named work period under `.context/sessions/{name}/`)

On `tools run`, pass `context.workspace` / `context.path` / `context.session`.

## Root resolution when `path` is omitted

1. `{workspace}/.context/context-index.md` entry for this tool's `context_index_key`
2. else `{workspace}/{default_workspace_folder}` (Stories `tests`; CleanEngineering / Bdd `src`; Ux `ux`; base = workspace)

Explicit `path` overrides and must be recorded via **`record_context_root`**.

## Hard layout

- **`context-index`** — `{workspace}/.context/context-index.md` tracks `tool = ./root/*` (Current + Log). Read via **`read_context_index`** before generate; update on confirm/override; cite in handoffs.
- **`session.path`** — tool durable working area:
  - Tool docs / diagrams → `{session.path}/.context/`
  - Partitioned chunks + module-local docs → `{session.path}/{module}/.context/`
  - Generated code and module folders → `{session.path}/`
- **`session.folder`** — named sprint under `{session.path}/.context/sessions/{name}/` (`session.md`, grill-answers, engagement sketches, handoff). Create via **`create_session`** after confirming path and slug with the user (also records context-index). Close via **`close_session`**.

## Defaults by kind of work

- Sketch / grill / iterate / handoff for engagement process work → **`session.folder`**
- Partition `out_root` and durable corpus docs → **`session.path`**
- Do not invent a divergent working folder outside the indexed/confirmed root.

# Create Session

Create `{session.path}/.context/sessions/{name}/session.md` (Start section) after confirming path and kebab slug with the user.

Also records this tool's root in `{workspace}/.context/context-index.md` when `context_index_key` is set.

```yaml
tool: create_session
arguments:
  name: <kebab-slug>
  path: <optional; overrides session.path — use when path was not set via context>
  goal: <optional>
  fidelities: <optional>
  contexts: <optional>
```

# Close Session

Write the End section on `{session.folder}/session.md`.

```yaml
tool: close_session
arguments:
  outcome: <optional>
  handoff: handoff.md
```

# Read Context Index

Read `{workspace}/.context/context-index.md` (creates nothing). Prefer an existing entry for this tool over guessing a root.

```yaml
tool: read_context_index
```

# Record Context Root

Upsert this toolset's root into `{workspace}/.context/context-index.md` after the user confirms the working path (including overrides). Handoffs must cite this file.

```yaml
tool: record_context_root
arguments:
  root: <optional; defaults to session.path>
  note: <optional>
```
