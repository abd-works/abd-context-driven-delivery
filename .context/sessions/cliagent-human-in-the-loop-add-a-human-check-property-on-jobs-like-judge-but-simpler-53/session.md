# Session: cliagent-human-in-the-loop-add-a-human-check-property-on-jobs-like-judge-but-simpler-53

## Start

- **date:** 2026-08-30
- **path:** C:\dev\abd-cdd-53
- **goal:** CliAgent human-in-the-loop: add a human check property on jobs (like judge, but simpler)
- **fidelities:** (unset)
- **contexts:** (unset)

## Analysis

### Intent (what changes)

Add an optional **human check** on CliAgent jobs — analogous to `judge`, but much thinner.

After the doer finishes a job with `human=true` (or an equivalent human-check flag set):

1. **Stop** advancing the queue for that job.
2. **Notify the parent** that human review is required.
3. **Wait** for the human to say either **looks good** or **needs fixing** (with feedback).
4. If **needs fixing**: redo **the same job** with the human feedback included in the next doer attempt.
5. If **looks good**: complete the job and move on.

Hard constraint from the request: do **not** invent a heavy judge-style loop. Keep the human path minimal.

Ticket: [#53](https://github.com/abd-works/abd-context-driven-delivery/issues/53)  
Worktree: `C:/dev/abd-cdd-53` on `session/cliagent-human-in-the-loop-add-a-human-check-property-on-jobs-like-judge-but-simpler-53`

### Context read

- `utilities/cli_agent/.context/module-context.md` — CliAgent owns `JobQueue`, launches doer/judge via `IdeCli`; `run_backlog` is the in-process doer→judge→advance loop; parent launches once and monitors the session log; job templates under `utilities/cli_agent/job-templates/`.
- `utilities/cli_agent/cli_agent.py` — job kit (`judge`, `judge_criteria`, tools, actions), `_job_needs_judge`, `run_backlog` recovery (`max_fail`), `_write_judge_prompt`, `_spawn_judge_for_job`, `_wait_for_verdict`, `_parent_checkin`, `rebind_to_worktree`, `enqueue_jobs` / template apply (jobs are plain dicts — extra keys survive JSON round-trip).
- `utilities/cli_agent/job-templates/small-change.json` (and defect-fix / cli-defect) — existing optional `judge` / `judge_criteria` fields on jobs; no `human` field today.
- `utilities/workflow/.context/module-context.md` + Workflow start/backlog — ticket/session lifecycle used to land this analysis on `#53`.
- No cli_agent grill-answers for this surface; closest human-pause pattern is sketch `#14` (`review_sketch` gate), which is action-level pause/confirm — not CliAgent job-queue orchestration.

### Current behavior (map)

Jobs in the queue are JSON objects. Known fields today:

| Field | Role |
| --- | --- |
| `prompt` | Doer Turn instructions |
| `tools` / `actions` | Tool kit for the Turn |
| `judge` | Bool — whether to run an AI judge after the doer |
| `judge_criteria` | Text scored by the judge |
| `index` | Stable job index for logging |

`run_backlog` loop today (`cli_agent.py`):

1. `launch_next` → doer Turn.
2. Wait until doer Turn ends (`_wait_until_doer_turn_ends`).
3. If **not** `_job_needs_judge(item)` → `complete_job` and advance.
4. If judge needed → write `.context/cli-agent-judge.txt`, spawn/resume judge, wait for transcript `PASS`/`FAIL`.
5. On **PASS** → complete and advance.
6. On **FAIL** → `recovery` (retry same job) up to `max_fail` (default 3), then `orchestrator_stopped` / hard stop for the parent.

Parent role today (`_parent_checkin` / `launch_sessions` docs): monitor session log; do **not** score the judge; only unblock after FAIL×3 or hard stall. Explicit lines say the parent is **not** in the judge loop and the doer must not wait for the operator during normal judged work.

There is **no** job-level human gate: nothing stops after doer success to ask a human before `complete_job`, and nothing feeds human feedback into a redo short of the parent manually rewriting the job prompt after FAIL×3.

### Intended delta

Introduce a job property parallel to `judge`, e.g. `human: true` (name can be `human` or `human_check` — keep one boolean flag; avoid a second AI agent).

Desired post-doer branch (minimal):

```
doer finishes
  ├─ human check set? → notify parent, wait for human
  │     ├─ looks good     → complete_job → next
  │     └─ needs fixing   → re-launch same job with feedback in prompt (no AI judge spawn)
  ├─ judge set? → existing judge PASS/FAIL loop
  └─ else → complete_job → next
```

Contrast with judge (what **not** to copy):

| Judge (heavy) | Human check (minimal) |
| --- | --- |
| Separate CLI identity + spawn | No second agent |
| Criteria file + transcript scrape for PASS/FAIL | Parent/human says looks-good / needs-fixing |
| Auto-retry up to `max_fail` | One explicit human-driven redo with feedback |
| Parent excluded from scoring | Parent **is** the check |

Ordering when both could apply: analysis assumes **human gate is an alternate/simpler path**, not a nested judge. Prefer mutually exclusive use on a job (`human` **or** `judge`), or if both are set, run human **after** doer and **before** any judge — approach job should pick the thinner rule. Default recommendation for the approach job: **human replaces judge for that job** when set (do not also spawn judge).

### Change surface (thorough)

Primary (production code — `utilities/cli_agent`):

1. **Job schema / kit** — accept and preserve `human` (and optional thin feedback field if needed) beside `judge` / `judge_criteria` in `_job_kit`, enqueue, session log `job_started` / `job_finished` if useful for observability.
2. **`run_backlog` (and any legacy doer-driven advance path)** — after doer Turn ends, if human check set: do not call `complete_job`; emit a clear session-log event (e.g. `human_check_needed`); notify parent; block until human resolution; on needs-fixing, append feedback into the same job’s next doer prompt and relaunch; on looks-good, complete.
3. **Parent contract** — `_parent_checkin` / `launch_sessions` guidance: when human check is waiting, parent (or operator) supplies looks-good / needs-fixing; this is intentional involvement, unlike the judge loop.
4. **Session log** — thin events for wait / resolution / redo (mirror `judge_started` / `verdict` / `recovery` lightly — do not invent a full second verdict subsystem).
5. **Job templates** — optional ability to set `"human": true` on selected jobs in `small-change.json` / others; not required to flip all templates in this change unless approach says so. The feature is the property + orchestrator path; template usage can be opt-in.

Secondary / neighbors callers will see:

- Specs: `cli_agent_spec.py` mechanical BDD for the new branch; agent BDD under `cli_agent_*_agent_spec.py` exercising real harness wait/notify (not stubbed pickup-only).
- Module-context: one short public-API note that jobs may set `human` and `run_backlog` pauses for parent resolution.
- IdeCli / WorkSession: likely **untouched** if human wait is orchestrator-side (no new CLI role). Prefer no new `cli_human` identity.

Out of scope / leave alone unless approach forces it:

- Workflow backlog/start/finish.
- Sketch `review_sketch` pause (#14) — similar *product* idea (pause for human confirm) but different seam (action tools, not CliAgent jobs).
- Judge spawn, criteria files, FAIL×3 recovery — leave as-is for `judge: true` jobs.

### History (area)

- `8f3e9ab3` — Add judge property; allow explicit judge without tools.
- `9d42b2b1` — Keep job_queue until judge PASSes; then next job on same doer.
- `4b55a288` — Only judge when launch lists tool/action (later overridden by explicit `judge`).
- `5d6ec895` / `5f15c085` — `#44` `run_backlog` owns doer→judge→advance; thin doer; parent monitors log only.
- `07161e7d` — kick tool; scope judge criteria.
- `5efb1e8e` — small-change template + context tools with generate.
- Session isolation / rebind line (`rebind_to_worktree`, #41) — ticket work on `session/<ticket>` worktree; unchanged by human check but this analysis landed after start-ticket on `abd-cdd-53`.

### Similar / related tickets

- **#44** — resiliency / self-managed doer-judge loop / minimal parent: establishes the loop we must extend lightly, not replace.
- **#42** — session log header / job summaries: observability pattern for any new human-check events.
- **#31** — better queuing for CLI agent tasks: related orchestration, not human gate.
- **#14** — sketch/grill pause for human review: closest *UX* analog (pause → confirm → correct → continue), different module.
- **#27** — immediate-fix autonomous workflow: opposite pressure (less human in the loop); human check is the opt-in opposite for selected jobs.
- Not a duplicate of judge work — this is a **simpler alternate gate**, not more judge criteria.

### Expected after change

- Job JSON may include `"human": true` (or agreed name).
- When set, after doer finishes: orchestrator stops, notifies parent, waits for looks-good / needs-fixing.
- Needs fixing → same job rerun with feedback included; looks good → complete and continue.
- No new AI judge agent, no criteria file, no FAIL×3 AI loop for the human path.
- Jobs without `human` keep today’s judge / no-judge behavior unchanged.

### Non-goals (this item)

- Not a full HITL product framework.
- Not replacing `judge` globally.
- Not changing Workflow ticket lifecycle.
- Not hunting defects in the current judge loop — only mapping the seam for the intended property.
