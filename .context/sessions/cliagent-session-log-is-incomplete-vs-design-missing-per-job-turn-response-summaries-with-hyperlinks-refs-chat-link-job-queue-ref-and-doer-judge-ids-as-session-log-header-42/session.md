# Session: cliagent-session-log-is-incomplete-vs-design-missing-per-job-turn-response-summaries-with-hyperlinks-refs-chat-link-job-queue-ref-and-doer-judge-ids-as-session-log-header-42

## Start

- **date:** 2026-08-29
- **path:** C:\dev\abd-cdd-42
- **goal:** CliAgent session log incomplete vs design: response summaries, chat/job-queue links, fold cli-agent.json IDs into session log header.
- **fidelities:** (unset)
- **contexts:** (unset)

## Analysis

### Symptom

`cli-agent-session.jsonl` (via `_CliAgentLog`) records orchestration lifecycle events only. Relative to the stated design it is missing:

1. **Per-job / per-turn response summaries** with hyperlinks or refs to content the doer read, wrote, or changed.
2. A durable **link to the chat** (doer / judge transcript) as part of the log itself.
3. A durable **reference to the job queue** file for the session.
4. **Doer / judge IDs from `cli-agent.json` folded into a session-log header** so operators are not forced to keep two parallel identity files (`cli-agent.json` may be legacy).

Operators therefore cannot reconstruct “what happened and where” from the session log alone; they bounce between `cli-agent.json`, the launch report text, transcript paths, and the job-queue JSON.

### Design vs implementation

| Designed field | Intended location | Actual today |
|---|---|---|
| Response summary + content refs | per `job_finished` / turn close | **Absent** — `job_finished` is `{kind, index, prompt, ts}` only |
| Chat link | session log (header or first-class event) | Transcript paths appear on `session_start` events and in `_session_report` stdout; **not** a stable header / first-class chat link in the log contract |
| Job-queue ref | session log | Path printed only in `_session_report` monitor section; **never written to jsonl** |
| Doer/judge IDs as header | first record / header of session log | IDs live in parallel `cli-agent.json` (`WorkSession.save_cli_sessions`) and are **re-emitted on every `session_start`**, not as a one-time header that replaces the sidecar |

Module context (`utilities/cli_agent/.context/module-context.md`) documents `_CliAgentLog` as: `session_start`, `spawn`, `jobs_defined`, `job_started`, `job_finished`, `verdict` — i.e. the thin event set matches the code and does **not** yet encode the richer observability design in the backlog item. No `grill-answers.md` exists for this package on this ticket.

### Where it lives

| Artifact | Path | Role today |
|----------|------|------------|
| Session JSONL | `.context/sessions/<name>/cli-agent-session.jsonl` | Event stream via `_CliAgentLog` |
| CLI IDs | `.context/sessions/<name>/cli-agent.json` | `{doer, judge, doer_pid, judge_pid}` only |
| Job queue | `.context/sessions/<name>/cli-agent-job-queue.json` | FIFO jobs; path printed in launch report, not linked from JSONL |
| Module context | `utilities/cli_agent/.context/module-context.md` | Thin event kinds only — no summary/header contract |

### Observed shape (live `cli-agent-fixes` log)

Kinds present in `.context/sessions/cli-agent-fixes/cli-agent-session.jsonl`:

- `jobs_defined` — full job list payloads
- `job_started` / `job_finished` — index + prompt only
- `session_start` — doer/judge ids, pids, transcript paths (repeated per spawn)
- `spawn` — role, resume, prompt, argv

No `summary`, `refs`, `chat`, `job_queue`, or `header` fields appear on any kind. In a sampled live log, `job_finished` (6) is rare relative to `job_started` (15) — jobs often restart without a finished event — which further weakens the log as a completion narrative.

### Call chain / seam

- Writer: `utilities/cli_agent/cli_agent.py` → `_CliAgentLog` (`filename = cli-agent-session.jsonl`)
- Emit sites: session launch (`session_start` + `spawn`), enqueue / `jobs_defined`, launch next → `job_started`, `complete_job` → `job_finished`, `record_verdict` → `verdict`
- Identity sidecar: `WorkSession.cli_agent_file` → `cli-agent.json` via `save_cli_sessions` / `load_cli_sessions`
- Launch UX already knows the missing links: `_session_report` prints session-log path, job-queue path, and transcript paths — but only as ephemeral report text, not as structured log records

There is **no writer** today for response summaries or content refs. Completing a job does not inspect the hanging Turn, workspace session logs, or the doer transcript for artifacts touched. `job_finished(work, index, prompt)` has no API seam for summary or content refs.

### Contrast: richer workspace logging

Workspace session/Turn logging already keeps prompt, result, context, and tool-call trails under session `logs/`. CliAgent’s jsonl sits beside that stack but does not project Turn/SessionLog outcomes into per-job summaries. Issue **#9** (extra workspace info for correlation) and **#40** (attach chat transcripts on session close) are adjacent: they also want chat/work product preserved with the session, but do not replace this defect’s need for **in-log** summaries and identity header.

### History (vintage)

| Commit | Meaning |
|--------|---------|
| `25233963` | Introduce structured `cli-agent-session.jsonl` + `record_verdict` |
| `72593a4e` | Rename `_CliSession` → `_CliAgentLog`; event-sourced append-only API |
| `28dc95a2` | Move spawn logs into session folder; expand session report monitor paths |

The log was introduced as a **lifecycle event stream**, then renamed for clarity. The backlog design (summaries, chat/queue links, fold IDs into header) was **never implemented** in those commits — this is an incomplete instrumentation / design gap, not a recent tip-commit regression. Triage Turn Context (`main` @ `afd51dd8`) matches that reading.

### Similar / related issues

| Issue | Relation |
|-------|----------|
| [#42](https://github.com/abd-works/abd-context-driven-delivery/issues/42) | This ticket (canonical open wording) |
| [#43](https://github.com/abd-works/abd-context-driven-delivery/issues/43) | Same defect (shorter title); closed as duplicate / superseded by #42 |
| [#44](https://github.com/abd-works/abd-context-driven-delivery/issues/44) | Finding CliAgent logs/tools painful vs manifest path — discoverability; complementary to #42’s **content** incompleteness |
| [#40](https://github.com/abd-works/abd-context-driven-delivery/issues/40) | Attach chat transcripts on work-session close — transcript **preservation**; overlaps “link to chat” but different seam (`WorkSession.close`) |
| [#9](https://github.com/abd-works/abd-context-driven-delivery/issues/9) | Track extra workspace info for correlation — broader Turn prompt/result theme |
| [#41](https://github.com/abd-works/abd-context-driven-delivery/issues/41) (closed) | Session isolation before start-ticket — adjacent hygiene, not logging shape |

Not duplicates of #42: #44/#40/#9 share the observability theme but different seams.

### Context read for this analysis

- Issue #42 body + Turn Context
- `utilities/cli_agent/.context/module-context.md` (no grill-answers for this package on this ticket)
- `_CliAgentLog`, `_session_report`, `complete_job` / launch path, `WorkSession.save_cli_sessions`
- Live `cli-agent-fixes` session jsonl + `cli-agent.json`
- Repo history for `utilities/cli_agent/cli_agent.py` (commits above)
- Related issues #43, #44, #40, #9, #41

### Expected

1. Session log opens with a **header** carrying doer/judge (and pids) so `cli-agent.json` is not a second source of truth.
2. Each finished job/turn appends a **response summary** plus refs/links to content read, written, or changed (and ideally chat + job-queue hrefs when not already in the header).
3. Chat link and job-queue path are **first-class log fields** (header and/or per-job), not only monitor lines in the launch report.
4. Module-context / specs describe that richer contract so BDD can lock it.

### Likely fix direction (for later jobs — not applied here)

Extend `_CliAgentLog` (and emit sites) rather than invent a third file: header write on session bind/start; enrich `job_finished` (or a new `job_summary` kind) from Turn/SessionLog/transcript; add `chat` + `job_queue` fields; decide whether `cli-agent.json` becomes a derived cache or is retired. Pair with mechanical BDD on log shape; agentic coverage only if prompt/report text also drifts.

### Branch / session

- Issue: [#42](https://github.com/abd-works/abd-context-driven-delivery/issues/42)
- Branch: `session/cliagent-session-log-is-incomplete-vs-design-missing-per-job-turn-response-summaries-with-hyperlinks-refs-chat-link-job-queue-ref-and-doer-judge-ids-as-session-log-header-42`
- Worktree: `C:\dev\abd-cdd-42`
- Package: `utilities/cli_agent` (`_CliAgentLog`, launch report, `cli-agent.json` persistence)

## Diagnosis

### Hypothesis (concrete)

The defect is **not** a tip-commit regression or a mis-behaving agent prompt. It is **missing production instrumentation** in `_CliAgentLog` and its emit sites, left out when the lifecycle log shipped:

1. **No response-summary / content-ref writer** — `job_finished(work, index, prompt)` only records `{kind, index, prompt, ts}`. There is no API argument and no call path that gathers a turn/job summary or refs to content read/written/changed from Turn, SessionLog, or the doer transcript.

2. **No first-class chat or job-queue fields in jsonl** — transcript paths are re-emitted on `session_start` and printed in `_session_report`; the job-queue path is printed only in the launch report. Neither is written as a durable structured field that replaces those ephemeral surfaces.

3. **No session-log header that owns doer/judge IDs** — identity lives in parallel `cli-agent.json` via `WorkSession.save_cli_sessions`. `session_start` repeats IDs on every spawn instead of a one-time header that makes the sidecar unnecessary.

Module-context documents the thin event set (`session_start`, `spawn`, `jobs_defined`, `job_started`, `job_finished`, `verdict`) and matches the code — docs describe today’s incomplete contract; they are not an independent prompt bug that causes agents to omit fields the code never writes.

### Why not elsewhere

- `_session_report` already *knows* the missing paths (session log, job queue, transcripts) but only as stdout — proves the gap is “not persisted into jsonl,” not “unknown to the kit.”
- Workspace Turn/SessionLog already hold richer trails; CliAgent never projects them into `_CliAgentLog`.
- Adjacent issues (#40 attach transcripts on close, #44 discoverability) are different seams.

### Confidence

**High.** Cause is unambiguous from code + module-context + live log shape; `/diagnose` not required.

### Category

**CODE CHANGE**

| Layer | Finding | Fix kind |
|-------|---------|----------|
| **CODE CHANGE** | `_CliAgentLog` / emit sites lack header, summary+refs, and durable `chat` / `job_queue` fields; `job_finished` has no summary seam | Production edits in `utilities/cli_agent/cli_agent.py` (+ possibly WorkSession identity fold-in) |
| Prompt / module-context | May be updated *after* the code contract exists so BDD/docs match; not the root cause of missing fields | Follow-on doc sync, not the primary fix |

Agents cannot invent structured log fields the writer never emits. Tests implied next: **mechanical BDD** on log shape (header, enriched `job_finished` / summary kind, chat + job-queue fields). Agentic BDD only if launch-report / prompt text is also part of the required contract drift.

## Resolution

**Status:** done on `main`. GitHub #42 closed.

### Phase 1 — Log completeness (`919cc997`, merge `54f0b674`)

- `header` kind: one-time doer/judge IDs, `chat`, `job_queue`
- `session_start`: `chat`, `job_queue`
- `job_finished`: optional `summary`, `refs`
- `_record_cli_binding`: writes header on first bind
- BDD: `"CliAgent session log completeness (#42)"` in `cli_agent_spec.py`

### Phase 2 — Observability (`046dfabf`)

- All records: `ts_ms`, `since_last_s`
- `job_started` / `job_finished`: `tools`, `actions`, `judge`; `duration_s` on finish
- `spawn`: structured `tools`, `actions`, `tool_calls`, `job_index`
- New `judge_started`; `verdict` gets `job_index`, `duration_s`
- Logs utilities + context_tools at toolset level (not primitives)
- BDD: `"CliAgent session log observability"` in `cli_agent_spec.py`

### Remaining (out of #42 scope)

- Auto-populate `summary`/`refs` in `complete_job()` from doer transcript
- `cli-defect` template regression job (`cda830c4`) — separate backlog/process item

