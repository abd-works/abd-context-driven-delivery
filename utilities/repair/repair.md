# Repair

Iterate until **validate** passes on `{{asset}}`. The violation signal is:

```
{{violation}}
```

That text may be a scanner report, a user complaint, or both together. The loop
fixes **why the generator produced the violation** — not the artifact in isolation.
Never proceed without a verifiable error signal from **scan** or **validate**.

Read the **`active`** resource first. `{{asset}}` and repaired outputs live under
that root (docs → `{session.path}/.context/`; code → `{session.path}/{module}/`). Do not
repair into a divergent folder.

Run this loop inline in the current session.

---

## When scan is clean but the violation is a user complaint

The tools do not see the problem yet. Edit the relevant scanner under
`scanners/` or `formats/{format}/scanners/` until **scan** reports a failure on
`{{asset}}` that matches the complaint. Re-run **scan** after each scanner edit.

Do not proceed to root-cause analysis until **scan** fails on `{{asset}}`.

---

## 1. Open an example folder

Create a descriptive folder under the domain examples tree and copy the broken
output before any fixes:

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
| Root cause | why the generator produced it |
| Fix applied | what changed to resolve it |

Non-blocking warnings may be listed separately but do not block the loop.

---

## 3. Root cause

Use **contexts**, **examples**, and **template** to determine why the generator
produced the violation. Review context bullets, worked samples, and file shape.

---

## 4. Fix the generator

Apply a **surgical** change to the generator — contexts, examples, template,
action prose, or scanners — so the violation does not recur. Touch only what
root cause implicates; do not rebuild from spec.

Re-run **generate** (or the steps that produced `{{asset}}`) and write the output
back to `{{asset}}`. Do not hand-edit `{{asset}}` to greenwash the scanners while
leaving the generator broken.

If the domain has `reference/repair-tips.md`, read it before writing fix code.
Save every generator change in `runs/<n>/run.md`.

---

## 5. Validate and repeat

Run **validate** on `{{asset}}` after regenerating from the fixed generator. The
report names the failing scanner when scan finds violations.

If violations remain, increment to `runs/<n+1>/run.md` and repeat from **Step 2**.

---

## 6. Capture the pass fixture — once validate passes

Save the final clean output beside the original failure:

```
<domain>/examples/<descriptive-folder>/
  faultyAsset          ← or faultyAssets/ when more than one file
  repairedAsset        ← or repairedAssets/ when more than one file
```

Only the **original failure** and **final clean output after generator fix** are
kept as fixtures. Delete `runs/` when the repair is done — working notes only
during the loop.

---

## 7. Run regression across repair history

Re-run **scan** on every captured example pair under
`<domain>/examples/*/`:

- Every `faultyAsset` or file under `faultyAssets/` must still **violate**
- Every `repairedAsset` or file under `repairedAssets/` must still be **clean**

The folder structure is the registry — no separate cases file.

---

# Validate

Take the persona of a **critical judge** — do not edit the artifact.

1. Follow **`session_guidance`**. Scope judgment to artifacts under `session.path` / the session layout.
2. Use **contexts** as the rubric — report pass/fail per named context and named rule with brief evidence.
3. Call **`scan`** on the session-rooted paths under review.
4. Do not fix. Report failures for fixing, then **validate** again when ready.

---
