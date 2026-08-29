# Handoff — abd-context-driven-delivery (2026-08-29)

## Resume

- **Stage:** (unset)
- **Last work:** (see session progress below)
- **Next action:** Fix clean_engineering model + generate manifest confusion
- **Next focus:** Fix clean_engineering model + generate manifest confusion

## Artifacts to read

- `C:\dev\abd-context-driven-delivery\.context\context-index.md`

## Request

**Focus:** Fix clean_engineering model + generate manifest confusion
Agent got completely confused running /.cursor/clean_engineering.model and /.cursor/generate. Tried generate_output instead of following manifest instructions. Defaulted to draw.io diagram even with format=markdown. Confused action names (generate vs generate_output). Should have read the manifest, taken the instructions, and passed them to the action. This used to work before actions and context_tools were separated. Need to identify root cause and fix either the cursor commands, the manifest instructions, or the agent guidance so this works reliably.

## Turn Context

- **Branch:** `main` (primary `C:\dev\abd-context-driven-delivery`); session worktree on `session/abd-context-driven-delivery`
- **Commit (current / Turn Context HEAD):** `8eb9fca26be8` — *Fix path config and workflow repo root handling* (not the causal change)
- **Session HEAD at this Turn:** `2c14ecce2f81` — prior backlog finish for the same focus (#37)
- **Transcript (task path):** `C:\Users\jeffa\.cursor\projects\c-dev-abd-context-driven-delivery\agent-transcripts\a8b46eb2-f131-492e-9be7-a3cfbeaba5a4\a8b46eb2-f131-492e-9be7-a3cfbeaba5a4.jsonl`
- **First notice in named transcript:** **not present.** Three user turns only (2026-08-27 14:26–14:33 UTC-4): (1) run CleanEngineering manifest — succeeded; (2)–(3) empty `python -m tools run -` — failed `request missing toolset`. No `generate_output`, draw.io, or format=markdown confusion is narrated.
- **First notice of this issue (related chat):** [CE model+generate confusion](c7271a70-e55f-454b-986d-72ac73b15750) — user turn **Saturday, Aug 29, 2026, 3:10 PM (UTC-4)** invoking `/.cursor/clean_engineering.model` + `/.cursor/generate`. First wrong agent conclusion shortly after: treat CleanEngineering action as `generate_output` (not follow `action: generate`), then follow draw.io/`create_diagram` guidance despite markdown intent.
- **Causal change vs current commit:** **Earlier than current.** Not introduced by `8eb9fca26be8` or session `2c14ecce2f81`. Request ties failure to post-separation of actions vs context_tools; earlier commits include `dd98f6ee35a4` (*refactor context tools to use separate toolsets*, 2026-07-25) and `2c351a8af4f1` (*Refactor clean engineering and stories toolsets…*, 2026-08-01). Root cause still to confirm (cursor commands vs manifest instructions vs agent guidance).
- **Prior capture:** https://github.com/abd-works/abd-context-driven-delivery/issues/37 (open, same title)

### Recent Commits

```
2c14ecce finish
2d548ab7 Update BDD specs to reflect CliAgent and Workflow refactors
a25ee3a9 finish
1a25a764 finish
9d42b2b1 Keep CliAgent job_queue until the judge PASSes, then run the next job on the same doer.
5c588e44 Add WorkTicket so the workflow package matches its imports.
8eb9fca2 Fix path config and workflow repo root handling
72593a4e Rename _CliSession to _CliAgentLog, event-sourced append-only session log
```
