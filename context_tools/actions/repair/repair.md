# Repair

Iterate until **validate** passes on `{{asset}}`. The violation signal is:

```
{{violation}}
```

That text may be a scanner report, a user complaint, or both together. The loop
fixes **why the context tool produced the violation** — not the artifact in
isolation. Never proceed without a verifiable error signal from **scan** or
**validate**.

Read the **`active`** resource first. `{{asset}}` and repaired outputs live under
that root (docs → `{session.path}/.context/`; code → `{session.path}/{module}/`). Do not
repair into a divergent folder.

Run this loop in the current session when invoked directly. When launched
from `improve` as a non-blocking background sub-agent, this text is the
sub-agent's own instructions — run the loop there instead, and report back
once **validate** passes.

**Log first.** If this violation has not already been recorded via
`log_mistake` (directly, or via `improve` before this loop started), call
`log_mistake` now, and call `log_correction` once this loop's fix lands.
This loop assumes the mistake is already logged — it does not log it for you.

---

## Not every rule is a scanner rule

A scanner only makes sense when the violation is **mechanical** - a specific
text pattern, a missing structural element, something a deterministic check
can find. Plenty of rules are not that: they are judgment calls (is this
story actually a repeatable behaviour? is this the right level of
abstraction?) that a reader has to weigh, not a regex has to match. Forcing
a scanner onto a judgment-call rule produces a brittle check that is
technically green while proving nothing.

Before building or editing a scanner, ask: can this violation be stated as a
deterministic pattern someone else's content might also hit? If yes,
continue below. If no - it is a prose/judgment rule - skip straight to
**Step 3 (Root cause)** and **Step 4 (Fix)** with a **prose-only** change
(a rule bullet, a clarifying example, sharper guidance in the context
tool's `.md`). Close that loop with **validate** (critical-judge review)
instead of **scan**, and skip Steps 1 and 6 below entirely - there is no
fixture pair to capture when there is nothing mechanical to check.

## When scan is clean but a mechanical violation is a user complaint

The tools do not see the problem yet. Edit the relevant scanner under
`scanners/` or `formats/{format}/scanners/` until **scan** reports a failure on
`{{asset}}` that matches the complaint. Re-run **scan** after each scanner edit.

Do not proceed to root-cause analysis until **scan** fails on `{{asset}}` -
unless this is a prose/judgment rule per the section above, in which case
**validate** is the signal instead.

---

## 1. Open an example folder — mechanical rules only

Skip this step entirely for a prose/judgment rule (see above) — there is no
scanner to prove a fixture against. Otherwise, create a descriptive folder
under the domain examples tree and copy the broken output before any fixes:

```
<domain>/examples/<descriptive-folder>/
  faultyAsset          ← copy of {{asset}} when there is one file
  faultyAssets/        ← when more than one file (same layout as {{asset}})
  runs/1/run.md
```

Use a folder name that describes the violation class (e.g.
`inheritance-crosses-class`). If that folder already exists from a prior session,
pick a new descriptive name or suffix (`-2`, `-3`, …).

When `{{asset}}` is multiple files, use `faultyAssets/` instead of a single
`faultyAsset` file. Mirror the same paths inside that folder.

---

## 2. Write run.md

Create `runs/<n>/run.md` for each attempt. Include, for every definitive
violation:

| Field | Content |
|-------|---------|
| Rule | context slug |
| Location | file, section, or element |
| Violated element | the specific thing that failed |
| Scanner / check | the scanner that detected it |
| Root cause | why the context tool produced it |
| Fix applied | what changed to resolve it |

Non-blocking warnings may be listed separately but do not block the loop.

---

## 3. Root cause

Use **contexts**, **examples**, and **template** to determine why the context
tool produced the violation. Review context bullets, worked samples, and file
shape. If those three do not explain it, the root cause may sit one layer
down, in a shared utility or primitive the context tool depends on
(`utilities/`, `primitives/`) — trace the call into there before concluding.

---

## 4. Fix the root cause

Draft a **surgical** change wherever root cause actually lives:

- Usually the context tool itself — its contexts, examples, template, action
  prose, or scanners.
- Occasionally a shared utility or primitive it depends on, when root cause
  traces down into one of those instead.

Touch only what root cause implicates; do not rebuild from spec.

**Present the drafted change to the user and wait for approval before
applying it.** Never apply a root-cause-level fix silently, even when the
cause is obvious.

### Approval ask (required shape — no mind-reading)

Every approval ask — the repair sub-agent's return, and any parent summary of
it — MUST include all four, in plain English. Slug labels, "Draft A/B", or
"approve?" alone are a defect.

1. **What went wrong** — the concrete mistake in the artifact (one or two
   sentences a reader who was not in the session can follow).
2. **Why** — what was missing or wrong in the context tool (or utility /
   primitive) that let it happen — the root cause, not a restatement of (1).
3. **What we will change** — the surgical fix: which files, what rule /
   scanner / template / prose lands, and what that stops next time. Name
   paths; do not hide the solution behind a process-slug.
4. **Your decision** — exactly what the user should answer, e.g. "Approve
   applying these changes?", "Approve with X dropped?", or "Reshape Y?".
   Offer reshape / reject, not only yes.

Do not proceed to apply until the user answers that decision.

Once approved, re-run **generate** (or the steps that produced `{{asset}}`) and
write the output back to `{{asset}}`. Do not hand-edit `{{asset}}` to
greenwash the scanners while leaving the underlying context tool (or utility/
primitive) broken.

If the domain has `reference/repair-tips.md`, read it before writing fix code.
Save every fix in `runs/<n>/run.md`.

---

## 5. Validate and repeat

Run **validate** on `{{asset}}` after regenerating from the fixed context tool
(or utility/primitive). The report names the failing scanner when scan finds
violations.

If violations remain, increment to `runs/<n+1>/run.md` and repeat from **Step 2**.

---

## 6. Capture the pass fixture — mechanical rules only, once validate passes

Skip this step for a prose/judgment rule — closing on **validate** in Step 5
is the end of that loop. Otherwise, save the final clean output beside the
original failure:

```
<domain>/examples/<descriptive-folder>/
  faultyAsset          ← or faultyAssets/ when more than one file
  repairedAsset        ← or repairedAssets/ when more than one file
```

Only the **original failure** and **final clean output after the fix** are
kept as fixtures. Delete `runs/` when the repair is done — working notes only
during the loop.

---

## 7. Run regression across repair history

Offer **`verify_regression`** as a non-blocking background sub-agent scoped
to this tool's own `<domain>/examples/` folder (never repo-wide) whenever
there is a growing fixture history to re-check. It re-scans every captured
pair directly under `examples/`:

- Every `faultyAsset` or file under `faultyAssets/` must still **violate**
- Every `repairedAsset` or file under `repairedAssets/` must still be **clean**

The folder structure is the registry — no separate cases file. Once this
sprint's fixes are settled, offer **`archive_mistakes`** — also a
non-blocking background sub-agent — to move the closed mistakes.log out of
the session folder.

---

# Validate

Take the persona of a **critical judge** — do not edit the artifact.

1. Follow **`session_guidance`**. Scope judgment to artifacts under `session.path` / the session layout.
2. Use **contexts** as the rubric — report pass/fail per named context and named rule with brief evidence.
3. Call **`scan`** on the session-rooted paths under review.
4. Do not fix. Report failures for fixing, then **validate** again when ready.

---
