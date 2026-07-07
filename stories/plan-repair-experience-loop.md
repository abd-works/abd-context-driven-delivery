# Plan — Consolidated Repair Experience Loop

> **Status:** DRAFT — do not implement until approved
> **Replaces (once implemented):** `behavior/manual-repair-loop.md`, `behavior/agentic-repair-loop.md` (stories-specific section), `evals/README.md §Debugging rule`

---

## Problem

Three separate documents describe overlapping repair processes (`agentic-repair-loop.md`, `manual-repair-loop.md`, `evals/README.md §Debugging`). None of them produce a persistent, navigable, replayable record of what went wrong and how it was fixed. Errors are lost after the chat session ends.

---

## Proposed approach: the Experience Loop

Every error, wherever spotted, creates a **permanent experience entry** that is structured, runnable, and keeps its full iteration history on disk. Experience entries live in `evals/experience/<random_id>/` and mirror the coarse-eval case shape. They are never deleted.

---

## Trigger

Either of:
- **User flags** incorrect output during a session with guidance on what the correct output should have been
- **Agent self-detects** a scanner violation, test failure, or judge mismatch during a run

---

## Step 1 — Create the experience entry

```
evals/experience/<random_id>/
  context/
    prompt.md          ← the original invocation that produced the bad output
    <input artifacts>  ← copies of the inputs the agent had at the time
  description.md       ← one-paragraph: what was wrong, what correct looks like, who found it
  category.txt         ← "ai" or "code" (see Step 2)
  runs/
    run-1/
      violation-report.md   ← first violation analysis
      actual/               ← the bad output (before any fix)
```

`<random_id>` is a short UUID slug, e.g. `a3f8b1`.

---

## Step 2 — Classify the fix

Determine which category applies (write to `category.txt`):

| Category | What it covers | How to verify |
|---|---|---|
| **ai** | Rules (`rules/`), generate-instructions, templates, prompt wording, skill SKILL.md, eval expected/ golden files — anything that requires running the AI through the eval runner to know if the fix worked | Re-run coarse eval; actual must match expected |
| **code** | `src/` Python, scanner `.py` files, `cli/` scripts, `eval.py` — anything that is a deterministic program with a correct/incorrect answer | Write a failing test first (`abd-story-acceptance-test`), then code until green |

A single experience can cross both categories (e.g. a scanner bug + a broken rule description). In that case: fix `code` first (tests green), then `ai`.

---

## Step 3 — Violation report (every run)

Each run gets a `violation-report.md` inside its `runs/run-N/` folder:

```markdown
# Violation Report — run-N

## Error
<exact error message or judge failure reason>

## Location
<file, line, scanner, or judge>

## Root cause
<why did the generator/scanner/rule produce this — not "it was wrong", but the structural reason>

## Fix applied in this run
<what was changed: file path, before/after snippet>

## Verification
<how to confirm the fix worked — eval command or test command>
```

---

## Step 4A — AI fix iteration (category: ai)

1. Apply the fix (rules, generate-instructions, templates, expected/, prompt wording).
2. Re-run: `python src/skill/evals/eval.py --mode coarse --case <case>`
3. Place the new actual output in `runs/run-N/actual/`
4. Write `runs/run-N/violation-report.md`.
5. If judge is still NOT_CLOSE → increment N, repeat.
6. **Do not delete any `runs/run-N/` folder.** All iterations stay; they are the learning record.
7. When judge reaches CLOSE and scanners are clean: re-seed `expected/` from final `actual/`.

---

## Step 4B — Code fix iteration (category: code)

Follow `abd-story-acceptance-test` methodology:

1. **Write a failing test first** that captures the exact broken behavior.
   - For a scanner bug: add a fixture under `rules/<rule>/evals/fail/<slug>/` and confirm the scanner exits 1 on it.
   - For a `src/` bug: add a pytest case that reproduces the failure.
2. Run tests — they must be RED.
3. Edit `src/` or scanner until tests are GREEN.
4. Place the test result in `runs/run-N/`.
5. Write `runs/run-N/violation-report.md`.
6. If tests still fail → increment N, repeat. Never delete runs.
7. When green: run the full scanner regression suite to confirm no regressions.

---

## Step 5 — Scanner/rule fixture variant

If the root cause points to a scanner or rule that lacks a regression fixture:

1. Add `rules/<rule>/evals/fail/<slug>/` with the minimal artifact that triggers the violation.
2. Add `rules/<rule>/evals/pass/<slug>/` with the corrected artifact.
3. Update `rules/<rule>/evals/cases.json` with both entries.
4. Re-run the scanner battery: `python src/skill/evals/eval.py --mode rules` — must be green.
5. Record the cases.json additions in the experience's `runs/run-N/violation-report.md`.

This step is required whenever the scanner didn't catch the original error (false negative) — i.e. Entry B of the agentic-repair-loop.

---

## Folder shape (complete)

```
evals/experience/
  <random_id>/
    context/
      prompt.md
      <input artifacts>
    description.md
    category.txt              ← "ai" | "code" | "ai+code"
    runs/
      run-1/
        violation-report.md
        actual/               ← bad output copy
      run-2/
        violation-report.md
        actual/               ← output after first fix attempt
      run-N/                  ← final passing run
        violation-report.md
        actual/               ← clean output
```

---

## What this replaces

| Old document | Disposition |
|---|---|
| `behavior/manual-repair-loop.md` | Absorbed — manual repair is now just an experience entry with `runs/run-1/` as the pre-fix artifact and `runs/run-2/` as the corrected artifact |
| `behavior/agentic-repair-loop.md` (stories section) | Absorbed — Step 4A is the agentic iteration loop |
| `evals/README.md §Debugging rule` | Keep as a short pointer to this document; remove the inline table |
| `common/reference/agentic-repair-loop.md` | Unchanged — remains the general-purpose reference for non-stories skills |

---

## Open questions before implementation

1. Should `evals/experience/` be git-ignored (working notes) or committed (permanent learning record)? Proposed: committed, since experience entries are the regression fixtures.
2. Should `description.md` be auto-generated by the AI from the user's correction signal, or always written by hand?
3. Does the experience ID need to be human-readable (`fix-verb-noun-format`) or truly random (`a3f8b1`)? Both are valid; random avoids naming conflicts during parallel sessions.
4. Should the eval runner pick up `evals/experience/*/context/prompt.md` as additional coarse cases, or are experience entries run-once only?
