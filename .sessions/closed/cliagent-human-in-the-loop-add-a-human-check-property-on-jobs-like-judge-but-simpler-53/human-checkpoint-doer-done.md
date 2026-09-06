# Human checkpoint doer done (#53)

## Summary

Implemented CliAgent **human check** — optional job flag `human: true` (alias `human_check`), parallel to `judge` but thinner: after doer finishes, `run_backlog` stops, notifies via session log, waits for parent/human **looks_good** vs **needs_fixing**, then completes or redoes the same job with feedback. No second AI agent.

## Files changed

| File | Change |
| --- | --- |
| `utilities/cli_agent/cli_agent.py` | `_job_kit` preserves `human`; log events `human_check_needed` / `human_check_resolved`; `run_backlog` human branch + `wait_human` hook; `resolve_human_check` tool; file wait `human-check-{index}.json`; feedback rewrite on redo; `human` replaces `judge`; parent checkin + launch_sessions docs |
| `utilities/cli_agent/.context/module-context.md` | Public API note for human / resolve_human_check |
| `utilities/cli_agent/cli_agent_spec.py` | Mechanical BDD: kit, gate, looks_good, needs_fixing redo, resolve tool, parent text |
| `utilities/cli_agent/cli_agent_human_check_agent_spec.py` | Agentic CLI harness: real `run_backlog` + background file resolve |
| `utilities/cli_agent/cli_agent_human_check_docs_agent_spec.py` | Agentic in_chat: docs/parent contract |
| `utilities/cli_agent/.context/.agent_bdd_sessions/human-check-53.json` | Agent BDD session |
| `utilities/cli_agent/.context/.agent_bdd_sessions/human-check-53-docs.json` | Docs agent BDD session |
| GitHub `#53` | `## Approach` + `## Model` on issue body |

## How the human gate works

1. Enqueue a job with `"human": true` (and usually `"judge": false`).
2. `run_backlog` launches the doer; when the Turn ends it logs `human_check_needed`.
3. **Notify:** fires IDE/OS notification via `show_os_notification` (same bridge as manifest gate) and logs `human_notified` with title/body/channel. Tests spy with `notify_human=` hook — assert notify happens **before** wait.
4. Parent/operator resolves one of:
   - **Tool:** `resolve_human_check(result="looks_good")` or `resolve_human_check(result="needs_fixing", feedback="…")`
   - **File:** write `{session}/human-check-{index}.json`  
     `{"result":"looks_good"}` or `{"result":"needs_fixing","feedback":"…"}`
5. **looks_good** → `complete_job` → next job.
6. **needs_fixing** → append `HUMAN FEEDBACK` to the same job prompt → relaunch doer → notify+wait again.

When both `human` and `judge` are set, **human wins** (no AI judge for that job).

## Test status

- Mechanical (`cli_agent_spec.py` human-check): gate + **notify-before-wait spy** + **default OS notifier patched** + looks_good / needs_fixing.
- Agentic docs: require `human_notified` / IDE-OS notification wording.
- Agentic CLI: real wait/resolve path (file).

Did **not** call finish-ticket / close the workspace session.
