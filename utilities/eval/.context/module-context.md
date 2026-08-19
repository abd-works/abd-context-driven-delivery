# eval — module context

## Purpose
Own the EvalSession domain for context-tool work: turns (tool calls, context,
prompt, result), collections of mistakes and repairs, and Archive. EvalSession
orchestrates turn lifecycle and persistence. Mistake owns recording/tracking
itself; Correction owns applying a fix (status=fixed, fixedIn the closing Turn);
Repair owns the repair loop (including opening a CDD session) and a separate
eval tool. Host `createRule` writes a new rule and matching scanner when scan
does not already match the Mistake. Persist
as one session.yaml plus `{session.folder}/mistakes/{mistake-name}/`
(faultyAsset / repairedAsset, named after the mistake — not a theme). Eval
fixtures stay under `evals/` and are a later, separate step.

## Primary use case
While an agent chat reply is in progress, attach tool calls and mistakes to an
open Turn; when the reply finishes, close that Turn onto the EvalSession (and commit
working-area deltas) if anything changed — otherwise discard the open Turn.

## Rationale
One hierarchical document beats parallel trail files (events / mistakes / spine).
Locations stay in workspace; eval owns the domain story used for RCA and evals.

## Seam
`EvalSession`, `Turn`, `ToolCall`, `Mistake`, `Correction`, `WorkspaceRepo`,
`CDDRepo` (extends WorkspaceRepo), `TurnCommit`, `Repair`, `Archive`. An asset
EvalSession holds `workspaceRepo`, `cddRepo`, and `cddAt` (tool checkout linked
once). Repair opens a WorkspaceSession on the CDD clone. Eval package also holds
explicit vanilla BDD specs and agent-BDD specs (before-fail / after-pass +
agentic validate).

## Constraint
Callers construct `EvalSession` with a workspace area that already has
`path`, `folder`, and `name`. Do not pass a git branch — `EvalSession` ensures
`session/{name}` via `WorkspaceRepo` on construct.

## Public API
- `EvalSession.begin_turn` / `record_tool_call` / `finish_turn` / `save` / `load`
  → `{workspace.folder}/session.yaml`
- `Mistake.record` / repair setter / `correct`
- `Correction.apply`
- `Repair.log_mistake` / `log_correction` / `repair` / `eval` /
  `contribute`. `_begin` and `_kind` are private. No `improve`. If `repair` has no Mistake or Correction, it
  takes them from context and wires them. `eval` is a separate tool — the
  agent (or contribute) runs it after repair; `repair` does not call it.
- `BaseContextTool.createRule(failed, wanted)` — only when scan does not
  already match the Mistake; then run the new rule and detect a failure that
  matches the Mistake.
- BaseContextTool holds `self.eval` (this EvalSession) beside `self.workspace`
- Host wiring: `@log` → `SessionLog.append` → `record_tool_call`; Base
  `log_mistake` / `log_correction` forward to `self.repairer` (session.yaml
  plus `{session.folder}/mistakes/{name}/`; not mistakes.log).
  Base registers `begin_eval_turn` / `finish_eval_turn` on generate, validate,
  document, partition, repair, eval, and createRule so the agent runs them. grill /
  sketch / iterate / satisfy do not register their own — they delegate.

## Dependencies
`workspace` (path/folder/name; package under `context_tools/actions/workspace`).
`scanners.Scan` for regression only. Base composes workspace + eval.

## Git (thin)
`WorkspaceRepo` is the session-tracked git seam (session branch, TurnCommit).
`CDDRepo` **extends** it. `repos_for_workspace` roots `WorkspaceRepo` at
`find_git_root(workspace.path)` and `CDDRepo` at the running tools clone
(`find_cdd_root` — this package's git root). An asset session **links once**
(`cddAt` = `headSha`) — which tools this session used. It does not stamp CDD
on every Turn. Repair **opens a WorkspaceSession** whose path is the CDD clone and **copies**
project Mistakes onto that session (new objects, same entry ids) so the tools
clone holds a consumable `mistakes/` record. Logging on the project does not
mirror in real time — the bring-over happens when repair starts.
`eval` is a separate tool that may open its own session on that clone if repair
has not. When the working area sits inside this clone (e.g. `sandbox/…`), both
share that **same** git root. Isolated paths with no git stay `Null*`. `Null*`
variants remain for isolated unit tests only.
