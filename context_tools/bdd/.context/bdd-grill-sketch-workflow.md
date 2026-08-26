# Bdd grill → sketch — two-agent workflow

**Purpose:** Bdd behavior prep for iterate must **grill before sketch**. Two agents split responsibility; **workspace WorkSession owns every turn** as its own commit on the session branch.

## Agents

| Agent | Skill | Owns |
|---|---|---|
| **Runner** | `bdd-grill-runner` | One grill question per turn; sketch after 2–3 grounded answers unlock a slice; never self-answers from memory |
| **Judge** | `bdd-grill-judge` | Prove-read repo; answer grill questions with citations; validate sketches **independently** and **against runner output**; record mistakes + corrections on the turn |

Read this file from both skills before acting.

## Turn kinds (each = open turn … work … finish → commit)

| Kind | Agent | `prompt` (example) | `result` (example) |
|---|---|---|---|
| **grill** | Runner | `bdd grill tick N — slice boundary` | One question + options + paths prove-read |
| **answer** | Judge | `bdd judge answer — grill tick N` | Grounded answer with cited paths; PASS/FAIL on question quality |
| **sketch** | Runner | `bdd sketch tick — <slice name>` | Path to persisted `{slug}-bdd-sketch.md` delta |
| **validate** | Judge | `bdd judge validate — <slice name>` | Independent rubric + scan report; mistakes logged if FAIL |

**Never** combine grill + sketch in one turn. **Never** skip opening and finishing the workspace turn.

Turn commit messages use **`Turn.name`** (e.g. `bdd-grill-behavior-python`, `bdd-mistake-behavior-python`) — not generic `turn {id}`.

## Bdd toolset (default)

```yaml
toolset: context_tools.bdd.bdd:Bdd
context:
  fidelity: behavior
  path: <module under test, e.g. context_tools/actions/workspace>
  session: <work session slug, e.g. workflow-package>
```

Use `.\tools.ps1` from repo root. Write `_req.yaml`, run, delete.

## Workspace turn — one process per turn (required)

Turns live on **`WorkSession.open_turn`** via **`Turn.open` / `Turn.finish`**. Do **not** use `EvalSession`, `Repair.log_mistake`, or `begin_eval_turn` / `finish_eval_turn` — those are legacy; commits from eval turns ignore `Turn.name`.

**Mistake and correction are different turns** — each gets its own open turn → … → finish → commit. Never `record_mistake` and `record_correction` on the same turn.

**Within one turn**, never run open turn, `record_mistake` or `record_correction`, and finish as **separate** `tools.ps1 run` calls. Each invocation is a new Python process; the open turn is lost, so finish commits without the mistake/correction linkage.

**Mistake turn** — one process, then commit:

```python
import uuid

bdd = Bdd(fidelity="behavior", path=..., session=...)
bdd.workspace.open(bdd)
turn = bdd.turn.open(bdd, action="mistake")
entry_id = uuid.uuid4().hex[:8]
turn.record_mistake(
    entry_id=entry_id,
    artifact=...,
    rule=...,
    wrong=...,
    original=...,
    tool="bdd",
    fidelity="behavior",
    introducing_commit=<SHA that introduced the fault>,
)
turn.finish(prompt="log mistake — …", result=f"entry_id={entry_id}", context=...)
```

Mistakes are **git-primary**: `record_mistake` annotates the **introducing commit** via git notes — not `session.yaml` or `mistakes/` folders.

**Fix the artifact** on disk (separate work between turns).

**Correction turn** — new process, new turn, then commit:

```python
bdd = Bdd(fidelity="behavior", path=..., session=...)
bdd.workspace.open(bdd)
turn = bdd.turn.open(bdd, action="correction")
turn.record_correction(
    entry_ids=[entry_id],
    improved=<full repaired file contents>,
    how=...,
    status="fixed",
)
turn.finish(prompt="log correction — …", result=f"entry_id={entry_id} fixed", context=...)
```

`record_correction` finds mistakes by **git notes** (`GitRepo.find_mistakes`) on introducing SHAs — not by scanning `mistakes/` on disk or eval `session.yaml`.

## Session artifacts

Under `{active.folder}` (work session sprint):

- `grill-answers.md` — append-only: question, judge answer, paths cited, slice notes
- `{slug}-bdd-sketch.md` — behavior hierarchy; runner writes, judge validates
- `session.yaml` — bootstrap only (name, branch, path) — **not** a mistake/turn index
- `logs/events.log` — expand|run trail (appended each turn finish)

Under `{active.path}` when behavior signatures exist:

- `{module}_spec.py` — **after** sketch is judge-clean and iterate unlocks generate (not during grill/sketch turns)

## Source-of-truth read order (judge prove-read)

1. User-cited OO / CE sketch (e.g. `workspace-eval-oo-sketch.md`)
2. `{module}/.context/module-context.md`
3. Existing `*-bdd-sketch.md` and `grill-answers.md` in session folder
4. `context_tools/bdd/bdd.md`, `templates/bdd-sketch.md`
5. Production source only when documenting **current** behavior (`document`); target-model Bdd follows sketch, not today's code

## Judge mistakes

When judge FAILs:

1. **Mistake turn:** open turn → `record_mistake` → finish → commit (one process for all three)
2. Fix artifact (sketch or grill-answers)
3. **Correction turn:** open turn → `record_correction` → finish → commit (one process; separate turn from step 1)

Runner **does not** argue with judge; runner applies correction or re-grills.

## Orchestration (parent chat)

1. Task **runner** with `bdd-grill-runner` → one grill turn → stop
2. Task **judge** with `bdd-grill-judge` → answer turn → stop
3. Repeat until 2–3 answers name one slice boundary
4. Task **runner** → sketch turn → stop
5. Task **judge** → validate turn → stop
6. If validate FAIL → correction on turn → runner may re-sketch in a **new** sketch turn

Do not chain ticks in one agent message.
