# Coarse eval cases

Each folder here is one end-to-end coarse-eval case that exercises the `stories` skill at a specific fidelity. Every case has the same shape:

```
<case>/
  eval.json                  descriptor: fidelity, artifacts, timeouts
  context/                   everything the agent may read
    prompt.md                the instructions (always here, no exceptions)
    <upstream artifacts>     e.g. story-map.md, brief.md, scenarios/
  expected/                  golden output tree the agent should produce
  actual/                    populated by the runner (wiped every run)
```

The runner (`stories/src/skill/evals/eval.py --mode coarse`) discovers every folder with an `eval.json`, wipes `actual/`, invokes `cursor-agent` with `context/prompt.md` + `context/`, then:

- **harvests** only what the agent produced (via the stories skill / CLI) into `actual/`
- streams the agent run to **`.last-run/<case>/agent/run.txt`** (prompt + response, echoed live unless `--quiet`)
- **reuses** one cursor-agent chat (`.last-run/agent-session.json`) across runs — use `--fresh-session` to reset
- logs **skill workflow** into the same `run.txt`: `SKILL GRILL/GENERATE/VALIDATE — assemble` (full manifest file list), `SKILL CLI — stories render`, and agent tool commands
- checks the **manifest**: every path listed under `expected/` must appear in `actual/` (no byte-for-byte diff)
- runs every scanner under `stories/rules/*` against the merged workspace and expects zero violations
- runs a **coarse AI judge** (cursor-agent) that compares `expected/` vs `actual/` semantically — pass requires verdict **CLOSE** (disable with `--no-coarse-judge`)

`expected/` is the golden reference for humans and for the AI judge. Mechanical scanners cannot catch "valid but wrong" output.

## Debugging rule — fix the root cause, never work around it

When an eval fails, **always fix the root cause**. Never paper over a failure with fallback logic.

| Wrong | Right |
| ----- | ----- |
| Scanner reports no actor → add markdown fallback to scanner | Scanner reports no actor → fix the formatter so it writes `"users"` |
| Judge returns empty string → widen verdict search to raw bytes | Judge returns empty string → find out why the stream event type isn't recognised and handle it correctly |
| Expected file passes but actual fails → adjust scanner heuristic | Expected and actual differ → fix the agent output or the expected golden file |

If you find yourself adding `if something_is_missing: try_another_way`, stop. The root cause is that `something_is_missing`. Fix that.

## Cases

| Folder | Fidelity | Input → Output |
| ------ | -------- | -------------- |
| `01-shaping/` | shaping | brief → `story-map.md` |
| `02-discovery/` | discovery | story-map → `thin-slicing.md`, `story-graph.json` |
| `03-exploration/` | exploration (md + ts) | story-map → `story-context/*.md`, `scenarios/*.md`, `{epic}/{sub-epic}/{story}/*-stories.ts` |
| `04-specification/` | specification (md + ts) | main-flow scenarios → outline + examples `.md`, `{epic}/{sub-epic}/{story}/*-stories.ts` |
| `05-engineering/` | engineering (ts) | outline scenarios → `{epic}/{sub-epic}/{story}/*-stories.ts`, `*.test.ts` |

All five cases thread the same domain (corporate treasury same-day USD transfers) so a reviewer can watch fidelity progress from a business brief through to executable tests.

## Running

```bash
python stories/src/evals/eval.py --mode coarse                     # every case
python stories/src/evals/eval.py --mode coarse --model gpt-5.5-medium
python stories/src/evals/eval.py --mode all                        # rules + ai-judge + coarse
```

Reports land in `stories/evals/_runs/<utc-timestamp>/`.

## `_runs/`

Timestamped run artifacts. Safe to delete. Never checked in.
