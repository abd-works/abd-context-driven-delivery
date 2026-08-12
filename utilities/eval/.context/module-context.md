# eval — module context

## Purpose
Own the Session domain for context-tool work: turns (tool calls, context,
prompt, result), mistakes nested on turns, corrections linking to later turns,
repair/improve loop, and archive promote. Persist as one Session YAML.

## Primary use case
While an agent chat reply is in progress, attach tool calls and mistakes to an
open Turn; when the reply finishes, close that Turn onto the Session (and commit
working-area deltas) if anything changed — otherwise discard the open Turn.

## Rationale
One hierarchical document beats parallel trail files (events / mistakes / spine).
Locations stay in workspace; eval owns the domain story used for RCA and evals.

## Seam
`Session`, `Turn`, `ToolCall`, `Mistake`, `Correction`, `WorkspaceRepo`,
`CDDRepo` (and later `Repair`, `ArchivePromoter`).

## Constraint
Callers construct `eval.Session` with a workspace area that already has
`path`, `folder`, and `name`. Do not pass a git branch — `Session` ensures
`session/{name}` via `WorkspaceRepo` on construct.

## Public API
- `Session.begin_turn` / `record_tool_call` / `record_mistake` / `record_correction` / `finish_turn`
- `Session.save` / `load` → `{workspace.folder}/session.yaml`
- BaseContextTool holds `self.eval` (this Session) beside `self.workspace`
- Host wiring: `@log` → `SessionLog.append` → `record_tool_call`; `log_mistake` /
  `log_correction` dual-write to eval; `finish_eval_turn` closes the Turn at the
  chat-reply boundary (no second boundary)

## Dependencies
`workspace` (path/folder/name; package under `context_tools/actions/workspace`).
`scanners.Scan` for regression only. Base composes workspace + eval.

## Git (thin)
`WorkspaceRepo` / `CDDRepo` shell out to `git`. When the working area sits inside
this clone (e.g. `sandbox/…`), both repos use the **same** git root — tool and
workspace identity are one repository while we develop here. `Null*` variants
remain for isolated unit tests only.
