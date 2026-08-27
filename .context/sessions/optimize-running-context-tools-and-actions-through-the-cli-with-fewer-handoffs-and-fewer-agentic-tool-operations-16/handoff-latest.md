# Handoff — issue 16 (2026-08-27)

## Resume

- **Stage:** channel write (next courier experiment)
- **Last work:** `/sub-agent` no-action path names `performTurn`; session finished (`542474e` `finish`)
- **Next action:** Channel write — one `@agent_tool` that calls an existing formatter/channel instead of the agent reading the expand blob and Write-ing the file
- **Next focus:** channel optimization

Start a **new** work session. Session 16 is closed. Stay on this git branch unless you cut `experiment/channel-write`.

## Session

- **goal:** Optimize running context tools and actions through the CLI with fewer handoffs and fewer agentic tool operations
- **branch:** `session/optimize-running-context-tools-and-actions-through-the-cli-with-fewer-handoffs-and-fewer-agentic-tool-operations-16`
- **repo:** `c:\dev\abd-context-driven-delivery`
- **closed:** 2026-08-27
- **outcome:** Turn/WorkSession/Scan kits on the CLI; `/turn` is `performTurn`; `/sub-agent` wraps a no-action run in `performTurn`

## Next experiment — Channel write

Read `options.md` (Channel write) and `experiments.md` (protocol). Do not open another thin-filter row.

**Question:** when a formatter already exists, does one `@agent_tool` that calls the channel (old 6c, plus deterministic header/log as tools — old 3a) beat “read 74k and Write the file”?

Stories markdown / CE markdown already have emitters. Agent still chooses when there is no channel (grill, invent/map). Keep grill interview agentic.

**Risk:** empty or wrong artifact if the channel is thinner than the agent write.

**Fair clocks to beat (stacked, same protocol):**

| Pair | Single-command | Thin-first-expand + CE |
|---|---|---|
| A story_map+generate | **00:51** | **00:41** |
| B model+generate | **00:37** | **00:55** |

Isolated **00:33 / 00:31** (thin-templates alone) are **not** the stacked result. Do not treat them as the bar.

Stories blob **17,767** / CE **45,100**. Pair B leftover is write + Drawio glue, not hop 2.

## How to run (locked)

- Pipe YAML to stdin `python -m tools run -`. Do not write `_req.yaml`. Do not remanifest — the skill is the catalog.
- `tools.ps1` does **not** forward stdin. Set `PYTHONIOENCODING=utf-8` and PYTHONPATH like `tools.ps1`, pipe to `.\.venv\Scripts\python.exe -m tools run -`.
- PowerShell: `;` not `&&`.
- `@agent_instructions` are parsed, not executed. Do not invent `action: guidance`.
- Domain methods return domain objects. `to_dict` is a dump hook only.
- Host extras stay behind `if host:`. Session comes from `workspace` path + `session` name (or `session/` git branch).
- `/sub-agent` is non-blocking. Parent does not inline. Listed **actions** proceed as today. **No actions** → worker runs `performTurn` (open, do the work, `finish_turn`, report branch and commit).
- Harness AskQuestion only when IDE/path are unknown. Saved state: `primitives/harness/.deploy-state.json` (Cursor + `abd-works-repo/.cursor`). Repeat deploys: `generateAgain`.

```yaml
toolset: workspace.workspace:Turn
action: performTurn
```

```yaml
toolset: scan.scan:Scan
# slash /scan needs arguments.tools (hosts). Path-only scan has no rules.
```

## Landed this close (do not re-do)

- Walker + single-command on **main**. Thin filters on `experiment/thin-fidelity-format` (worktree `C:\dev\abd-cdd-experiment-thin-fidelity-format`).
- `Turn`, `WorkSession`, `Workspace` are `@toolset` / Turn is `@agentic_toolset`. CLI: string `workspace` + `session`.
- `performTurn` — open, do work in context, `finish_turn`. `/turn` deployed.
- Scan kit: `context_tools/actions/scan/`, `scan.scan:Scan`. Hosts implement `_scanner_collection()`. `Scan.bound_to(host)`. Bare `Scan().scan(paths)` raises.
- `@agent_instructions` kits are `@agentic_toolset`. No `from tools.tool import tool` / `@tool` alias.
- Harness utilities emit `tool:` + Python method name (not `action:` + `@prompt` slug). `@agent_instructions` deploy as `action:` + method name (not `guidance`).
- `SubAgent.run`: actions listed → unchanged; empty/missing → name `performTurn` around the context-tool work.

## Corrections (do not repeat)

- Follow the command → manifest. Do not reverse-engineer `workspace.py`.
- Every `@agent_tool` class is `@toolset`; every `@agent_instructions` class is `@agentic_toolset`.
- Do not change return types to dicts so YAML can dump them.
- Do not strip host logic — `if host:` around bind/index/attach/trail.
- Scanners are not path-only. Paths are what you walk; `_scanner_collection()` on the host is the rule set.
- `/deploy-harness` answers live in `.deploy-state.json`. Do not re-ask IDE/path.
- A `/sub-agent` fix is only `SubAgent.run`. Do not walk expanders or harness.

## Artifacts to read

- `.context/sessions/optimize-running-context-tools-and-actions-through-the-cli-with-fewer-handoffs-and-fewer-agentic-tool-operations-16/options.md`
- `.context/sessions/optimize-running-context-tools-and-actions-through-the-cli-with-fewer-handoffs-and-fewer-agentic-tool-operations-16/experiments.md`
- `.context/sessions/optimize-running-context-tools-and-actions-through-the-cli-with-fewer-handoffs-and-fewer-agentic-tool-operations-16/backlog.md`
- `utilities/workspace/.context/module-context.md`
- `utilities/sub_agent/.context/module-context.md`
- `context_tools/actions/scan/` (kit)
- `sandbox/courier/courier.md` (corpus)

## Protocol reminder

Name the experiment, cut `experiment/<name>`, apply only that bundle, kick `/sub-agent` with Stories + Clean Engineering + Generate against `sandbox/courier`. Clock prompt → final artifact. No AskQuestion for tool or fidelity.
