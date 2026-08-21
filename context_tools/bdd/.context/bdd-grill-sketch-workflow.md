# Bdd grill ΓåÆ sketch ΓÇö two-agent workflow

**Purpose:** Bdd behavior prep for iterate must **grill before sketch**. Two agents split responsibility; **eval owns every turn** as its own commit.

## Agents

| Agent | Skill | Owns |
|---|---|---|
| **Runner** | `bdd-grill-runner` | One grill question per turn; sketch after 2ΓÇô3 grounded answers unlock a slice; never self-answers from memory |
| **Judge** | `bdd-grill-judge` | Prove-read repo; answer grill questions with citations; validate sketches **independently** and **against runner output**; record mistakes + corrections on the turn |

Read this file from both skills before acting.

## Turn kinds (each = `begin_eval_turn` ΓÇª work ΓÇª `finish_eval_turn` ΓåÆ commit)

| Kind | Agent | `prompt` (example) | `result` (example) |
|---|---|---|---|
| **grill** | Runner | `bdd grill tick N ΓÇö slice boundary` | One question + options + paths prove-read |
| **answer** | Judge | `bdd judge answer ΓÇö grill tick N` | Grounded answer with cited paths; PASS/FAIL on question quality |
| **sketch** | Runner | `bdd sketch tick ΓÇö <slice name>` | Path to persisted `{slug}-bdd-sketch.md` delta |
| **validate** | Judge | `bdd judge validate ΓÇö <slice name>` | Independent rubric + scan report; mistakes logged if FAIL |

**Never** combine grill + sketch in one turn. **Never** skip `begin_eval_turn` / `finish_eval_turn`.

## Eval toolset (default)

```yaml
toolset: context_tools.bdd.bdd:Bdd
context:
  fidelity: behavior
  path: <module under test, e.g. context_tools/actions/workspace>
  session: <eval session slug, e.g. eval-consolidate-workspace>
```

Use `.\tools.ps1` from repo root. Write `_req.yaml`, run, delete.

## Session artifacts

Under `{active.folder}` (sprint):

- `grill-answers.md` ΓÇö append-only: question, judge answer, paths cited, slice notes
- `workspace-bdd-sketch.md` (or `{slug}-bdd-sketch.md`) ΓÇö behavior hierarchy; runner writes, judge validates
- `session.yaml` ΓÇö turn index; mistakes attach to the **validate** turn (or **answer** turn if the question itself was defective)

Under `{active.path}` when behavior signatures exist:

- `{module}_spec.py` ΓÇö **after** sketch is judge-clean and iterate unlocks generate (not during grill/sketch turns)

## Source-of-truth read order (judge prove-read)

1. User-cited OO / CE sketch (e.g. `workspace-eval-oo-sketch.md`)
2. `{module}/.context/module-context.md`
3. Existing `*-bdd-sketch.md` and `grill-answers.md` in session folder
4. `context_tools/bdd/bdd.md`, `templates/bdd-sketch.md`
5. Production source only when documenting **current** behavior (`document`); target-model Bdd follows sketch, not today's code

## Judge mistakes

When judge FAILs:

1. `log_mistake` ΓÇö artifact path, rule name, wrong, original excerpt
2. Fix artifact (sketch or grill-answers)
3. `log_correction` ΓÇö entry_id, improved, how, status=fixed
4. Same turn's `finish_eval_turn` includes mistake ids in session.yaml

Runner **does not** argue with judge; runner applies correction or re-grills.

## Orchestration (parent chat)

1. Task **runner** with `bdd-grill-runner` ΓåÆ one grill turn ΓåÆ stop
2. Task **judge** with `bdd-grill-judge` ΓåÆ answer turn ΓåÆ stop
3. Repeat until 2ΓÇô3 answers name one slice boundary
4. Task **runner** ΓåÆ sketch turn ΓåÆ stop
5. Task **judge** ΓåÆ validate turn ΓåÆ stop
6. If validate FAIL ΓåÆ correction on turn ΓåÆ runner may re-sketch in a **new** sketch turn

Do not chain ticks in one agent message.
