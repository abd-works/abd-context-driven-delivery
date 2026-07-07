# Manual Repair Loop

Use when the **user found and fixed the problem themselves** — no agentic
iteration loop was run. The goal is to capture the original bad output and the
corrected output as fixtures so the skill can be improved and the failure
becomes a permanent regression test.

---

## When to use this

- The user spotted a problem in a skill's output (visual, structural, content, etc.)
- They fixed it manually (edited the file, regenerated with adjusted input, etc.)
- No AI iteration loop was run
- They want the failure and the fix captured for future learning

---

## Step 1 — Locate the original bad artifact

Check these sources in order:

1. **`evals/` folder** next to the generated output — the last `run-n` output
   before the user's fix is the fail artifact.
2. **`skill-errors-log.md`** inside the skill folder — if the user already
   logged the error there, the "Example (wrong)" entry points to what failed.
3. **CDD session journal** (`docs/cdd-sessions/<date>-<topic>/cdd-session-journal.md`)
   — the `## Corrections` section records what the output did wrong and what it
   should have done.
4. **Chat history** — the turn where the user described or showed the problem.

---

## Step 2 — Locate the corrected artifact

The fixed output is one of:

- The file the user edited directly
- A newly regenerated artifact the user approved
- Shown or described in the chat immediately after the fix

---

## Step 3 — Capture the fail fixture

Save the minimal artifact that reproduces the violation:

```
eval/fail/<slug>/<artifact>
```

Where `<slug>` describes the violation and `<artifact>` is the skill's output
format. If the bad artifact spans multiple sections or pages and the failure
is present throughout, copy the whole file unchanged.

Follow the fixture format from
**`behavior/agentic-repair-loop.md` § "3. Capture fail fixtures"** for
the `eval/cases.json` entry, marking affected scanners as `"expect": "violate"`.

---

## Step 4 — Capture the pass fixture

Save the corrected artifact:

```
eval/pass/<slug>/<artifact>
```

Follow the fixture format from
**`behavior/agentic-repair-loop.md` § "6. Capture pass fixtures"** for
the `eval/cases.json` entry, marking all scanners as `"expect": "clean"`.

---

## Step 5 — Check whether the scanner/rule gap needs fixing

Run the skill's scanner or validator against the original bad artifact:

- **If it reports a violation** — the scanner already catches this class of
  problem. No scanner change needed; the fixture alone is enough.
- **If it passes (false negative)** — follow
  **`behavior/agentic-repair-loop.md` Entry B** to fix the scanner or
  rule until it detects the problem, then re-verify against both fixtures.

---

## Step 6 — Run the full regression suite

Follow **`agentic-repair-loop.md` § "6. Run the full regression suite"** exactly.
Every existing `fail/` and `pass/` fixture in `eval/cases.json` must still
match its expected scanner result before this loop is considered done.

---

## Step 7 — Improve the skill / generator

If the fix reveals a systematic problem in how the generator works (not a
one-off), improve the generator script so future outputs don't repeat it.
Document the change in `evals/SUMMARY.md`.

---

## File map

| Path | Purpose |
|------|---------|
| `eval/fail/<slug>/<artifact>` | Bad artifact (pre-fix) |
| `eval/pass/<slug>/<artifact>` | Good artifact (post-fix) |
| `eval/cases.json` | Fixture registry — add entries for both |
| `skill-errors-log.md` | Source of the logged error (read-only here) |
