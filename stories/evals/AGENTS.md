# Evals — Agent Rules

## Folder structure

```
evals/
  {phase}/
    expected/   ← ground truth — READ ONLY, never modify
    actual/     ← AI output — write here
```

Phases: `03-exploration`, `04-specification`, `05-engineering`.

## When to change expected/

`expected/` is the ground truth the eval scores against. The rule on whether to change it depends on *why* you are changing it:

| Situation | Change expected/? |
|---|---|
| `actual/` output is wrong and you want the eval to pass | **No** — fix `actual/`, not `expected/` |
| A new story or scenario has been added and no expected file exists yet | **Yes** — create the expected file |
| The expected file contains an error (the ground truth itself is wrong) | **Yes** — correct it and document the correction |
| The skill's canonical output has intentionally changed (rule or generator updated) | **Yes** — update expected to match the new canonical form |

The principle: change `expected/` to keep the ground truth accurate. Never change it to make a broken `actual/` pass.

## Scoring

The eval compares `actual/` against `expected/`. A file missing from `actual/` is a gap; a file that differs from its `expected/` counterpart is a violation.

## Repair loop

When scanner violations are found:
1. Fix files in `actual/` only — surgical edits, do not rebuild from scratch
2. Re-run scanners after each fix
3. After 2 consecutive failed fix attempts on the same file — stop and read `behavior/agentic-repair-loop.md` before continuing
