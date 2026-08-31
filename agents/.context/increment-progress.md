# Increment progress — #55

**Read this first** in every new chat or loop tick. Update before you stop.

| Inc | Name | Status | Last commit / notes |
|-----|------|--------|---------------------|
| 1 | One task, stubbed doer | judge_green | `agents/agent/agent_spec.py`; mamba `agent_spec` |
| 2 | Doer + judge, stubbed | judge_green | same `agent_spec.py` (judge + human trees) |
| 3 | Manifest / turn fence | pending | |
| 4 | Backlog → current | pending | |
| 5 | Queue drain + template | pending | |
| 6 | AgentSession open | pending | |
| 7 | SubAgent spawn | pending | |
| 8 | Transcript watcher | pending | |
| 9 | CliAgent bind + launch | pending | |
| 10 | CliAgent close + agent BDD | pending | |
| 11 | WorkTicket + start | pending | |
| 12 | Finish + capstone agent BDD | pending | |

**Status values:** `pending` · `in_progress` · `judge_green` · `blocked`

**Rule:** set `judge_green` only after Bdd validate + CE validate + pytest (and agent BDD when inc 10/12) all PASS for that increment.
