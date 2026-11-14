# Quick suite speed analysis — 2026-11-13

Measured on main at 2a07cde6b (before this branch's commits), Snapdragon X 12-core, Windows 11.
Other agents were editing the main checkout during the runs, so absolute numbers carry some noise.

## Baseline

- `scripts/test.ps1` (vanilla): **703 s wall**, 307/313 files passed.
- Sum of batch times 3,865 s; the slowest batch alone took 523 s, so wall time is set by one batch, not total work.
- Each file in its own process, 10 at once: 838 s wall, 7,384 s total, of which **4,116 s (56%) was imports**
  (median 13.6 s import per process).

## Slowest files (10 running at once)

| File | s | Examples | Cause |
|---|---|---|---|
| cdd_guidance/actions/validate/validate_spec.py | 814 | 58 | practice catalogue rebuilt per call: 22× `create_all`, 132× `guidance.__init__`, 488 markdown reads/YAML parses of unchanged files |
| harness/graph/graph_build_spec.py | 424 (165 alone) | 27 | 18 worker subprocesses ~6 s each (2–4 s of it import); serial refresh loop in before_all at line 265 (54 s); `_bodiless_members` regex 21.6 s |
| space/repo/worktree_spec.py | 158 | 16 | git origin + clone rebuilt in `before.each` |
| space/repo/repos_spec.py | 119 | 18 | |
| space/kanban/validate-fidelity-outputs.story.domain.spec.py | 117 | 19 | |
| space/repo/git_folder_spec.py | 104 | 13 | git repos per example |
| space/kanban/kanban_tools_spec.py | 101 | 118 | |
| harness/graph/graph_spec.py | 95 | 201 | |
| harness/diagnostics/agent_tools_diagnostics_spec.py | 87 | 14 | |
| space/session/session_saves_spec.py | 87 | 8 | git repos per example |

By area: practices 1,772 s, kanban 1,587 s, actions 1,168 s, graph 882 s, repo 433 s, session 355 s.

## Findings and status on this branch

| # | Finding | Status |
|---|---|---|
| 1 | `_BODILESS_RE` starts `^\s*`; `\s` spans newlines over `_top_level`'s blanked bodies → quadratic backtracking. Line-anchored `[ \t]` version: same matches, 0.147 s → 0.005 s on a 17k-char file. Production code (every TS/Java graph load). | **Done** ff8c91a18 |
| 2 | `@mcp` lives in `harness/mcp/mcp_server.py`, which imports the MCP SDK (`mcp.types`, `mcp.server`, pydantic, httpx) at the top; 55 modules import it → ~10 s of the ~15 s per-process import. Also slows prod: graph workers, hooks. | **Done** 8a0061e2f (`harness.mcp.mcp_annotations`) |
| 3 | Practice markdown re-read and YAML re-parsed per call | **Done** 64ab6abc5. Re-checked after the merge: `create_all` 57 calls take 0.84 s in all; validate_spec runs in 38.5 s (was 814 s), its time spread over graph-rule regexes with no single hotspot. |
| 4 | Git specs build origin + clone per example | **Done** cfa7633dc (`space/repo/built_once.py`) |
| 5 | Server/worker specs in quick suite; graph_build_spec serial refreshes | **Done** 801b6d07f, 756ced6d1 |
| 6 | `PYTHONDONTWRITEBYTECODE=1` inherited from a Claude Code chat's environment → no bytecode for spec processes; every one recompiles mcp, pydantic, httpx, coverage, clint. With a cache: 21 s → 15 s import. The cdd server and hook daemon are not affected: their `.pycache` folders hold site-packages bytecode. | **Done** — `Set-TestEnvironment` clears it and sets `PYTHONPYCACHEPREFIX` to the checkout's `.pycache`, as the servers do (graph workers inherit it). |
| 7 | `test.ps1` excludes `retired`/`.retired` but not `_retired` → 3 files always fail. | **Done** on main (came in with the merge). |
| 8 | Batches start largest-by-file-count first, not slowest-first; slow files share batches (523 s batch). | **Done** — each run saves every file's seconds to `.pycache/spec-seconds.json`; the next run gives a file of 20 s or more its own batch and starts the batches expected to take longest first. Batch headers now print their seconds. |
| 11 | The quick suite started agent runs (`agent_bdd` judge prompts in its log). | **Done** on main: `CDD_AGENT_RUNS_OFF` outside the agent suite. |
| 9 | Defender real-time scan: first read ~22 ms/file vs 0.3 ms cached; ~600 modules per process. | **User's call** — exclusion for repo/.venv, or move repo to a Dev Drive. Not a code change. |
| 10 | `.venv` is uv's **x86_64** CPython running emulated on ARM64; native arm64 Python is 1.5× faster on a CPU loop (2.91 s vs 1.91 s). Blocked: `cryptography` (via `mcp` → `pyjwt[crypto]`) had no win-arm64 wheel and failed to build. | **Open / blocked** — revisit when a win_arm64 cryptography wheel is available. |

## Failures seen in the baseline (not caused by speed work)

- `cdd_guidance/actions/partition/partition_documents_flow_spec.py` — 9 examples
- `cdd_guidance/context_setup/context_setup_spec.py` — 6 examples
- `harness/hooks/hook_daemon_spec.py` — 1 example
- `space/kanban/review-files-in-viewer.story.server.spec.py` — failed alone, passed in its batch (possibly flaky / order-dependent)
- `agent_bdd` LLM judge prompts appeared in the vanilla suite's log — check nothing in the quick pass calls a model.

## Result after the merge of main and #6–#8 (2026-11-13)

- Quick suite: **703 s → 174 s** wall (second run 204 s while another session reinstalled the cdd server), 312/314 files.
- Importing every module the merge touched: 1.7 s, and the MCP SDK is not loaded (was ~15 s, SDK ~10 s of it).
- The two failures also fail on main at 6e86e6a10, so they are not from this work:
  - `cdd_guidance/practices/stories/model/story_map_edits_spec.py` — 9 examples: it edits this repository's real
    story map, which no longer holds the story it renames (`StoryNodeNotFound`).
  - `harness/guidance_actions/guidance_actions_spec.py` — 1 example: expects `drawio` as the first kept format, gets
    `markdown`.

## Still open

- #9 Defender exclusion or Dev Drive — the person's call.
- #10 native ARM64 Python — blocked on a win_arm64 `cryptography` wheel.
