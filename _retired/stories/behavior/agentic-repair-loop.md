# Agentic Repair Loop

Use when a skill's scanners or rules have found violations and you need to
iterate until the output is clean. The loop runs as a background sub-agent;
the main conversation continues uninterrupted.

---

## Execution model — always run as a background sub-agent

```
Task tool — subagent_type: generalPurpose, run_in_background: true
```

The prompt to the sub-agent must include:

- Absolute path to the output file(s) under repair
- Entry point (A or B) and the violation or user complaint verbatim
- Any reference files the agent needs (good/bad examples, target values)
- A clear instruction: apply **surgical fixes only** — do not rebuild from spec
- Which parts of the output to touch and which to leave alone

The parent agent ends its turn immediately after launching. The sub-agent
notifies on completion.

---

## Entry points — choose before starting

### Entry A — scanners/rules already found the problem

The skill's scanner or validator returned violations. The loop is runnable
immediately. Proceed directly to **Step 1**.

### Entry B — the user found the problem (scanners passed)

The output looks clean to the tools but the user sees something wrong.

**You cannot run the repair loop until the tools see the same problem.**

Do this first:

1. **Understand the user's complaint exactly.** Ask for specifics if needed
   (which file, section, element, what is wrong).
2. **Identify the gap.** Read the relevant scanner(s) and rule(s) in
   `scanners/` and `rules/`. Determine why they missed it — wrong threshold,
   missing case, rule not codified, etc.
3. **Fix the scanner or rule** until it flags the same problem the user
   described. This may require:
   - Tightening a threshold in a scanner
   - Adding a new check to the validator
   - Writing a new scanner file
   - Adding a new rule `.md` to `rules/`
4. **Verify the scanner now catches it.** Run the validator — it must report a
   violation on the specific case the user raised.

Only once the scanner/rule reliably detects the problem, proceed to **Step 1**.

> **Key principle:** never attempt to fix the output without a verifiable error
> signal. If you can't reproduce the failure programmatically, you have no way
> to know when you've actually fixed it.

---

## 1. Archive and create the eval folder

The eval folder lives **next to the generated output**:

```
<output-dir>/evals/
```

If `evals/` already exists from a prior session, rename it before starting:

```
evals/     →  evals-1/
evals-1/   →  evals-2/    (if both exist)
…
```

Then create a fresh run folder and **immediately save a copy of the current
(broken) output** there — this is the original failure artifact:

```
evals/run-1/
evals/run-1/<artifact>   ← copy of the output before any fixes
```

Subsequent fix attempts in the same session become `run-2`, `run-3`, etc.

---

## 2. Write violations.md

Create `evals/run-<n>/violations.md`. Include, for every definitive violation:

| Field             | Content |
|-------------------|---------|
| Rule              | filename from `rules/` |
| Location          | which file, page, section, or element |
| Violated element  | the specific thing that failed |
| Scanner / check   | the scanner or rule that detected it |
| Root cause        | why the generator produced it this way |
| Fix applied       | what was changed to resolve it |

Non-blocking warnings (cosmetic / approximate) may be listed separately but do
not block the loop.

---

## 3. Apply the fix

Apply the fix using the skill's scripts or tools. The approach is
skill-specific — write a bespoke fix script, adjust generator parameters, or
edit the output directly. The fix must be **surgical**: touch only what's
needed to clear the violation; do not rebuild from spec.

If the skill has a **`reference/repair-tips.md`**, read it for skill-specific
fix patterns and known-working approaches before writing any fix code.

---

## 4. Run the scanner

After each fix attempt, re-run the skill's scanner or validator against the
fixed output. Save the report in `evals/run-<n>/`.

If violations remain, increment to `run-<n+1>` and repeat from **Step 2**.

---

## 5. Capture fixtures — once everything passes

Only after the scanner reports zero violations on all relevant output:

**Fail fixture** — save the original broken output from `evals/run-1/`:

```
eval/fail/<slug>/<artifact>
```

**Pass fixture** — save the final clean output:

```
eval/pass/<slug>/<artifact>
```

Where `<slug>` describes the violation class (e.g. `inheritance-crosses-class`)
and `<artifact>` is the skill's output format (`.drawio`, `.md`, `.json`, etc.).

Update `eval/cases.json` with both entries:

```json
"fail/<slug>": {
  "date": "<YYYY-MM-DD>",
  "situation": "<one sentence: what was broken and why>",
  "rules": [
    { "rule": "<rule-file>", "scanner": "<scanner-file>", "expect": "violate" }
  ]
},
"pass/<slug>": {
  "date": "<YYYY-MM-DD>",
  "situation": "<one sentence: what the fix achieved>",
  "rules": [
    { "rule": "<rule-file>", "scanner": "<scanner-file>", "expect": "clean" }
  ]
}
```

The interim runs (`run-2`, `run-3`, …) are working notes only — they do not
become fixtures. Only the **original failure** and the **final clean output**
are registered.

---

## 6. Run the full regression suite

After capturing both fixtures, run **every** entry in `eval/cases.json` through
the skill's scanner:

- Every `fail/<slug>` fixture must still produce a **violation** for each
  scanner listed with `"expect": "violate"`. If a scanner no longer catches a
  known-bad fixture, the scanner has regressed — fix it before proceeding.
- Every `pass/<slug>` fixture must still be **clean** for each scanner listed
  with `"expect": "clean"`. If a scanner now flags a known-good fixture, the
  scanner is too aggressive — fix it before proceeding.

The regression suite must be green before the loop is considered done.
Document the results in `evals/SUMMARY.md`.

---

## 7. Propagate generator improvements

If the fix reveals a systematic problem in how the skill's generator works (not
a one-off), improve the generator script so future outputs don't repeat it.
Document the change in `evals/SUMMARY.md`.

---

## File map

| Path | Purpose |
|------|---------|
| `<output-dir>/evals/run-1/<artifact>` | Original broken output (source of fail fixture) |
| `<output-dir>/evals/run-<n>/violations.md` | Per-run violation report |
| `<output-dir>/evals/SUMMARY.md` | Cross-run summary once stable |
| `eval/fail/<slug>/<artifact>` | Fail fixture — original failure |
| `eval/pass/<slug>/<artifact>` | Pass fixture — final clean output |
| `eval/cases.json` | Fixture registry with expected scanner results |
| `<output-dir>/evals/SUMMARY.md` | Regression results + cross-run summary |
