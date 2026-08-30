## Diagnosis

**Category: CODE CHANGE**

**Root cause:** CliAgent has no in-process control loop. Orchestration is delegated to the doer via `_doer_ask_judge` (contact judge, pop queue, `complete_job`, `launch_next`) and to the parent via kick/monitor prompts. When the doer finishes a Turn without running that side-channel protocol, the queue stalls indefinitely.

**Exact gap:** Missing `run_backlog()` orchestrator that (1) spawns doer only, (2) polls transcript for turn end, (3) spawns judge from code, (4) reads PASS/FAIL, (5) calls `complete_job` + next job internally. Log kinds for `orchestrator_*`, `doer_finished`, `error`, `recovery` exist but the poll/spawn implementations were stubs (`NotImplementedError`).

**Not primarily PROMPT/AI CHANGE:** The doer unreliability is a symptom; the fix is production code owning the loop, not better doer instructions.
