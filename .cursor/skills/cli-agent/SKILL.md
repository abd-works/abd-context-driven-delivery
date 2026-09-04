---
name: cli-agent
description: "Run listed tools/actions via the IDE CLI, or prefer ``run_backlog`` for queue work."
disable-model-invocation: true
---

Run listed tools/actions via the IDE CLI, or prefer ``run_backlog`` for queue work.

CliAgent owns session/workspace setup and (via ``run_backlog``) the doer→human/judge→advance
loop. Parent contract is minimal for judged jobs: launch once, read the session log, unblock only after
CliAgent recovery stops. For jobs with ``human: true``, the parent IS the check — resolve
``human_check_needed`` via ``resolve_human_check``. Model, mode, and agent_mode are fixed on this ide instance.

## Preferred Steps (orchestrated)

1. **Enqueue** jobs / backlog (`enqueue_jobs`, `set_backlog`, templates).
2. **Launch ``run_backlog`` once.** CliAgent code spawns the doer, waits for Turn end,
   then either pauses for human check, or writes the judge prompt / reads PASS/FAIL, then calls
   ``complete_job`` / ``launch_next`` internally. Do not ask the doer to contact the
   judge or advance the queue.
3. **Monitor the session log** (exact paths in the launch report — read, do not recurse).
   Key files: session jsonl, job queue, doer/judge transcripts. CliAgent also fires an
   IDE/OS notification on ``human_check_needed`` (logged as ``human_notified``).
   Notify / act on ``orchestrator_stopped``, ``error``, ``human_check_needed``, or hard stall.
4. **On ``human_check_needed`` / ``human_notified``:** call ``resolve_human_check(result='looks_good')`` or
   ``resolve_human_check(result='needs_fixing', feedback='...')`` (session file
   ``human-check-{index}.json`` is also accepted). Needs-fixing redoes the same job with feedback.
5. **Unblock only on hard failure** (e.g. FAIL×3 after orchestrator stops). Revise the
   job prompt, then one continue resume — do not stack prompts or drive with -p.

## Legacy Steps (single launch_sessions without run_backlog)

1. **Launch.** Pass workspace (and session when known). If NOT TAKEN UP, stop immediately.
2. **Monitor** doer/judge logs and job queue; report back to the user.
3. **Unblock on three judge FAILs** if the doer stopped waiting.

## Job templates

Before building the job queue from scratch, check for a matching template:
- Call `list_templates()` and compare names against the user's request.
- If one matches, offer it via AskQuestion. If the user confirms, call `use_template(name)` to enqueue its jobs automatically.
- Skip this if the user described something clearly not matching any template.
- Call `use_template(name, overrides)` to merge fields (e.g. swap the prompt or toggle judge) into the template jobs before enqueueing.

## Backlog

A backlog is an ordered list of items (ticket refs like ``#12`` / ``27``, or free-text) assigned to this session.
One work session covers the whole backlog — never open a new session per item.
- **Up-front triage:** After `set_backlog`, call `triage_backlog` to scan the **entire backlog** before defect-fix jobs. Map each free-text item to an existing `#N` when one covers it, or `capture_backlog` for true new text — never duplicate tickets. Register all tickets on the project board with **theme:cli-agent**.
- Call `set_backlog(items, template)` to assign items and optionally bind a job template (e.g. ``defect-fix``).
- When the current item's defect-fix jobs are done: call **finish-ticket** (`Workflow.finish`) for that ticket, **then** `next_backlog_item()` to advance. Do not advance without finish-ticket. (`next_backlog_item` also invokes finish-ticket for ticket items when leaving them.)
- Free-text items that do not match an existing ticket may create one during triage with theme:cli-agent.
- Order is the order given unless you reorder via the ``order`` argument and record that choice.

## Doer prompt (thin when using run_backlog)

Tell the doer the task and toolset only. Do **not** instruct it to contact the judge,
call ``complete_job`` / ``launch_next``, or edit the job queue — ``run_backlog`` owns that.

For a one-off ``launch_sessions`` without orchestrator, you may still include queue tool
hints (`enqueue_jobs`, `launch_next`, `complete_job`) for doer-driven advance.

## Judge

Under ``run_backlog``, CliAgent code spawns/resumes the judge and records the verdict —
the parent never launches, prompts, or scores the judge; the doer never contacts it.
A judge runs when the job lists tools/actions, or when ``judge=`` is set on the launch/job.
Jobs with ``human: true`` (or ``human_check``) skip the AI judge: parent resolves looks_good /
needs_fixing instead.

through the tools cli

Pipe the fence to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```yaml
toolset: cli_agent.cli_agent:CliAgent
tool: launch_sessions
```
.\tools.ps1 run -
