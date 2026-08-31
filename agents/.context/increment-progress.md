# Increment progress — #55

**Read this first** in every new chat or loop tick. Update before you stop.

| Inc | Name | Status | Last commit / notes |
|-----|------|--------|---------------------|
| 1 | One task, stubbed doer | judge_green | `agents/agent/agent_spec.py`; mamba `agent_spec` |
| 2 | Doer + judge, stubbed | judge_green | same `agent_spec.py` (judge + human trees) |
| 3 | Manifest / turn fence | judge_green | `Turn`/`ToolCall` + stub tools CLI; `agent_spec.py` (28); host-bound CE/Bdd scan |
| 4 | Backlog → current | judge_green | `agents/agent/agent_spec.py`; mamba 39; host-bound Bdd/CE scan clean (`_open_session` separate-concerns fixed) |
| 5 | Queue drain + template | judge_green | `run_task_queue` drain + `load_template` + validation_error skip; mamba 48; host-bound Bdd/CE scan clean (CE rename/encapsulation fixes) |
| 6 | AgentSession open | judge_green | `AgentSession.open` / folder / branch; mamba 80; host-bound Bdd/CE scan clean (`_lookup`, extract, `open_existing` fixed); report `judge-reports/inc-6.md` |
| 7 | SubAgent + two runtime roles | judge_green | mamba 91 + agent BDD; host-bound Bdd/CE scan clean; report `judge-reports/inc-7.md` |
| 8 | Transcript watcher | judge_green | mamba 102; host-bound Bdd/CE scan clean; report `judge-reports/inc-8.md` |
| 9 | CliAgent bind + launch | judge_green | mamba 120; host-bound Bdd/CE scan clean (`planned_file` rename); report `judge-reports/inc-9.md` |
| 10 | CliAgent close (+ optional agent BDD) | judge_green | mamba 125; host-bound Bdd/CE scan clean; close/cleanup/Kick Stalled Doer in `cli_agent_spec.py`; optional CliAgent agent BDD skipped; report `judge-reports/inc-10.md` |
| 11 | WorkTicket + start | judge_green | mamba 143; host-bound Bdd/CE scan clean; `workflow_spec.py`; report `judge-reports/inc-11.md` |
| 12 | Finish + capstone agent BDD | judge_green (vanilla) | mamba **163** consolidated `agent_spec.py`; agent BDD phases 1a–2b in `agent_agent_spec.py` |

**Status values:** `pending` · `in_progress` · `judge_green` · `blocked`

### Real agent BDD (post-12 — required for shippable #55)

| Phase | Scope | Status | Notes |
|-------|--------|--------|-------|
| 1a | ChatAgent `/agent` — one judged job, in_chat | judge_green | phased tools + persistence; `AGENT_BDD_IN_CHAT=1` for agent BDD gate |
| 1b | ChatAgent + backlog tickets | judge_green | `enqueue_judged_from_ticket`, `run_backlog`; vanilla in `agent_spec.py`; two-item queue agent BDD (in_chat gated) |
| 2a | SubAgent — one judged job | judge_green | vanilla + `agent_agent_spec.py` in_process gate (open / doer+judge / turns / PASS / close); session `one-judged-job-55.json` |
| 2b | SubAgent + backlog | judge_green | vanilla two-item queue in `agent_spec.py`; in_process agent BDD; session `sub-two-item-queue-55.json` |
| 3a | CliAgent — one judged job | blocked | **blocked on session unification** — see `session-unification-backlog.md` U1–U6 |
| 3b | CliAgent + backlog | blocked | after U5 + 3a |

### Session unification (WorkSession → AgentSession)

Run as **independent `/sub-agent` tasks** with backlog in `agents/.context/session-unification-backlog.md` (U1–U6). Do not resume 3a until **U4** is judge_green.

| U | Task | Status |
|---|------|--------|
| U1 | AgentSession CDD seam | judge_green |
| U2 | Lifecycle → AgentSession | pending |
| U3 | BaseContextTool → AgentSession | pending |
| U4 | SessionLog + tools run | pending |
| U5 | CliAgent → AgentSession.folder | pending |
| U6 | Retire WorkSession | pending |

**Rule:** set `judge_green` only after Bdd validate + CE validate + pytest/mamba (and agent BDD when inc **7**/12, optional 10) all PASS for that increment.
