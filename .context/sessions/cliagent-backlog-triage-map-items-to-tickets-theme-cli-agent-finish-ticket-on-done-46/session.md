# Session: cliagent-backlog-triage-map-items-to-tickets-theme-cli-agent-finish-ticket-on-done-46

## Start

- **date:** 2026-08-29
- **path:** C:\dev\abd-cdd-46
- **goal:** CliAgent backlog hygiene: map backlog items to tickets, theme:cli-agent, finish-ticket on defect-fix done (#46).
- **fidelities:** (unset)
- **contexts:** (unset)

## Analysis

### Symptom

When a CliAgent session runs a multi-item backlog, three hygiene failures show up together:

1. **Backlog not triaged up front** — items stay free-text or become duplicate tickets (#42/#43) instead of being resolved to existing `#N` refs and registered on the project board by theme before defect-fix jobs run.
2. **Theme drift** — cli-agent work is supposed to land as project Theme **cli-agent** and label `theme:cli-agent` (not `theme:tools` / `theme:cliagent`); capture/start paths do not reliably force that for backlog-driven work.
3. **`finish-ticket` never runs on item completion** — when an item’s defect-fix jobs finish, the flow advances via `next_backlog_item` without calling `/finish-ticket`, so the board can stay **In Progress** after the issue is closed (cited example: #41).

Live evidence (parent session `cli-agent-fixes` backlog): `#41` done, `#46` in progress, **both `#43` and free-text leftovers**, plus free-text items still `kind: text` — no up-front resolution to tickets / board registration for the whole list.

### Designed behavior (from #46)

| Requirement | Expected |
|-------------|----------|
| Up-front triage | Scan entire `cli-agent-backlog.json` before defect-fix; map each item to existing `#N` or `capture_backlog`; put all tickets on the board under theme so theme filters show the full backlog |
| Theme | `theme:cli-agent` (label + project Theme) on capture/start for cli-agent backlog work |
| Finish before advance | On item defect-fix completion: `/finish-ticket` (merge, Project **Done**, close) **before** `next_backlog_item` |

### Where it lives

| Seam | Path | Role |
|------|------|------|
| Backlog model | `utilities/cli_agent/cli_agent.py` — `CliBacklog` / `CliBacklogItem` | Persist `cli-agent-backlog.json`; `from_ref` only classifies `#?\d+` vs text |
| Backlog API | `set_backlog`, `next_backlog_item` | Assign items; advance status + reload template — **no** GitHub resolve, **no** finish-ticket |
| Parent prompt | `CliAgent.launch_sessions` backlog section | Tells parent to call `next_backlog_item` when jobs done — **omits** finish-ticket |
| Defect-fix template | `utilities/cli_agent/job-templates/defect-fix.json` | Triage → analyze → diagnose → tests → fix — **no** finish-ticket job |
| Workflow | `utilities/workflow/workflow.py` — `capture_backlog`, `start`, `finish` | Ticket create / start / finish exist but are not wired into backlog advance |
| Theme | `utilities/workflow/work_ticket.py` — `THEMES`, `infer_theme` | Includes `cli-agent`; inference is keyword-based, not backlog-policy-based |

No `grill-answers.md` for `cli_agent` or `workflow` on this ticket. Module contexts describe backlog + finish-ticket separately; they do **not** state the “finish then next_backlog_item” or “triage entire backlog up front” contracts.

### What the code actually does

**1. `set_backlog` / `CliBacklogItem.from_ref`**

- Ticket vs text is a regex (`#?\d+`) only.
- No search for an existing GitHub issue by title/body similarity.
- No call to `capture_backlog` / `create_ticket`.
- No project-board registration loop for the full list.
- Free-text stays `kind: text` until some later agent turn (defect-fix job 1 path 2) may create a ticket — by then duplicates like #42/#43 can already exist.

**2. Theme**

- `WorkTicket.infer_theme` can return `cli-agent` when the text mentions that phrase; `THEMES` lists `cli-agent`.
- There is **no** CliAgent backlog policy that forces `theme:cli-agent` for every item in a cli-agent session backlog (items about “logs” / “tools” can infer `tools` instead).
- Wrong labels (`theme:tools`, `theme:cliagent`) are consistent with inference-from-wording + no backlog-level override on capture/start.

**3. `next_backlog_item`**

- Marks current item `done`, starts next `pending`, optionally reloads the defect-fix template onto the job queue.
- **Does not** invoke `Workflow.finish` / `/finish-ticket`.
- Defect-fix’s last job is “fix the defect…” — it does not instruct finish-ticket.
- Parent docs: “Call `next_backlog_item()` when the current item’s jobs are done” with **no** preceding finish-ticket step.

So the kit has the finish-ticket tool, but the backlog spine never calls it. Board/status hygiene depends on a human or ad-hoc agent memory — which failed for #41 as originally reported (issue now Closed/Done after later cleanup; the automation gap remains).

### History (vintage)

| Commit | Meaning |
|--------|---------|
| `2f4ec700` / `b164af24` | Introduce `CliBacklog` / multi-item session processing |
| Workflow finish / theme commits (ongoing) | `/finish-ticket` and theme inference exist as Workflow/WorkTicket capabilities |

Backlog was added as “assign refs or text → run template per item.” Up-front ticket resolution, forced cli-agent theme, and finish-before-advance were **never implemented** in that spine — design/ops gap layered on incomplete automation, not a tip-commit regression of a previously working finish hook.

### Similar / related issues

| Issue | Relation |
|-------|----------|
| [#46](https://github.com/abd-works/abd-context-driven-delivery/issues/46) | This ticket |
| [#41](https://github.com/abd-works/abd-context-driven-delivery/issues/41) (closed) | Cited example — finish-ticket not run; also isolation-before-start-ticket (fixed separately) |
| [#42](https://github.com/abd-works/abd-context-driven-delivery/issues/42) / [#43](https://github.com/abd-works/abd-context-driven-delivery/issues/43) | Duplicate session-log tickets — evidence of missing up-front map-to-existing |
| [#44](https://github.com/abd-works/abd-context-driven-delivery/issues/44) / [#45](https://github.com/abd-works/abd-context-driven-delivery/issues/45) | Sibling cli-agent observability / invoke-path backlog items |
| [#31](https://github.com/abd-works/abd-context-driven-delivery/issues/31) | Better queuing for CLI-agent tasks — adjacent backlog/queue theme |
| [#27](https://github.com/abd-works/abd-context-driven-delivery/issues/27) | Immediate-fix workflow (file/start/fix/finish) — wants autonomous finish; overlaps “finish must run” |
| [#18](https://github.com/abd-works/abd-context-driven-delivery/issues/18) | Theme by impacted package on backlog — related theme hygiene |

### Context read

- Issue #46 body
- `utilities/cli_agent/.context/module-context.md`
- `utilities/workflow/.context/module-context.md` / workflow-bdd-sketch (finish-ticket → Done)
- `CliBacklog`, `set_backlog`, `next_backlog_item`, `launch_sessions` backlog docs
- `job-templates/defect-fix.json`
- `Workflow.capture_backlog` / `start` / `finish`
- `WorkTicket.infer_theme` / `THEMES`
- Live `cli-agent-backlog.json` on `cli-agent-fixes`
- Repo history for backlog introduction; issues #41–#46, #27, #18, #31

### Expected

1. Before any defect-fix job: entire backlog resolved to `#N`, on the project board, with `theme:cli-agent`.
2. Free-text maps to an existing issue when one matches; otherwise one `capture_backlog` — never a second duplicate for the same defect.
3. When an item’s defect-fix queue is exhausted: `/finish-ticket` then `next_backlog_item` (code and/or template/parent prompt so it cannot be skipped).

### Likely fix direction (for later jobs — not applied here)

- **Code:** Up-front triage helper used from `set_backlog` (or a dedicated `triage_backlog`): resolve/create tickets, set theme, ensure project items; `next_backlog_item` (or a `complete_backlog_item`) calls Workflow finish for ticket items before advance.
- **Prompt/template:** defect-fix final step or parent backlog docs require finish-ticket before `next_backlog_item`; force `theme:cli-agent` in capture/start for this backlog.
- Likely category preview: **BOTH** (missing automation seams + missing/weak agent instructions) — confirm in Diagnosis job.

### Branch / session

- Issue: [#46](https://github.com/abd-works/abd-context-driven-delivery/issues/46)
- Branch: `session/cliagent-backlog-triage-map-items-to-tickets-theme-cli-agent-finish-ticket-on-done-46`
- Worktree: `C:\dev\abd-cdd-46`
- Packages: `utilities/cli_agent`, `utilities/workflow` (+ theme helpers in `work_ticket` / `git`)

## Diagnosis

### Hypothesis (concrete)

The defect is **not** a single broken line — it is three missing contracts in the CliAgent backlog spine that were never implemented when `CliBacklog` shipped (`2f4ec700` / `b164af24`). Each maps to a different symptom in #46:

1. **Up-front triage / map-to-ticket**  
   `CliBacklogItem.from_ref` only regex-classifies `#?\d+` vs free-text. `set_backlog` persists that classification and stops. There is **no** resolver that searches existing GitHub issues, calls `capture_backlog` for true new text, or registers the full set on the project board before defect-fix runs. Free-text therefore survives into jobs; agents create tickets ad hoc → duplicates (#42/#43).

2. **Theme `cli-agent`**  
   Theme application is delegated to `WorkTicket.infer_theme` (keyword match against `THEMES`). There is **no** backlog-level policy that forces `theme:cli-agent` for every item in a cli-agent session backlog. Wording that mentions “tools” (or omits “cli-agent”) can land as `theme:tools` / other labels; `theme:cliagent` is a slug drift outside the canonical `cli-agent` theme.

3. **finish-ticket before `next_backlog_item`**  
   Exact underlying issue: `next_backlog_item` only advances backlog status and reloads the job template. It never calls `Workflow.finish` / `/finish-ticket`. The defect-fix template’s last job is “fix the defect…” with **no** finish step. Parent `launch_sessions` backlog docs say to call `next_backlog_item()` when jobs are done and **omit** finish-ticket. So even when `/finish-ticket` exists and works, the backlog automation path never invokes it — board stays In Progress after closed work (#41).

### Why not elsewhere

- Workflow `finish` / `capture_backlog` / theme helpers work when called; the bug is **non-invocation + missing resolve** on the backlog path, not a broken Done column API.
- Session isolation (#41 code fix) is orthogonal; hygiene failures persist after that fix.
- Duplicate #42/#43 are consequences of (1), not a separate root cause.

### Confidence

**High.** Cause is unambiguous from code + template + parent docs; `/diagnose` not required.

### Category

**BOTH**

| Layer | Failure | Fix kind |
|-------|---------|----------|
| **CODE CHANGE** | No up-front resolve/create/board registration in `set_backlog` (or dedicated triage API); `next_backlog_item` does not finish the ticket; no forced `theme:cli-agent` on backlog capture/start | Production edits in `cli_agent.py` (+ Workflow calls / theme override) |
| **PROMPT/AI CHANGE** | `defect-fix.json` has no finish-ticket job; `launch_sessions` backlog instructions tell the parent to advance without finishing; module-context does not state the finish-then-advance or triage-up-front contracts | Prompt / docstring / template / module-context updates |

Agents cannot reliably invent the missing finish/triage steps when the queue API and template never require them; code cannot finish what prompts never schedule without a seam that actually calls finish. Both layers must change.

### Tests implied (for next job)

- **Mechanical BDD:** `set_backlog`/triage resolves text→existing `#N` without duplicate create; backlog items carry/enforce `theme:cli-agent`; completing an item invokes finish (or equivalent) before advance — assert project Done / no advance without finish hook.
- **Agentic BDD:** parent/doer following defect-fix + backlog docs must call finish-ticket before `next_backlog_item` (and must not skip up-front triage when given free-text + existing `#N`).

