# Repair

Iterate until **validate** passes on `{{asset}}`. The violation signal is:

```
{{violation}}
```

That text may be a scanner report, a user complaint, or both together. The loop
fixes **why the context tool produced the violation** — not the artifact in
isolation. Never proceed without a verifiable error signal from **scan** or
**validate**.

**Fail first.** Before any tool-file change, write a test that fails on the
current conditions. Mechanical rules: `expect_scan_fails` / `expect_scan_passes`
on the fail file and the pass file (`context_tools.bdd.spec_helpers`).
Judgment rules: `generate_and_judge` on the pass file (`agent_bdd.spec_helpers`).
Do not create an eval-package spec harness. If you cannot make a test fail under
current conditions, **do not repair** — append the mistake to
`{session.folder}/deferred.md` (not the mistake log) and move on.

**Evals always.** After a fix lands, run the same helpers on the pair under
`{session.folder}/repairs/{theme}/`: `expect_scan_fails` on `faultyAsset`,
`expect_scan_passes` on `repairedAsset`, and `generate_and_judge` on
`repairedAsset`. Do not add an eval-package spec. Do not wait for eval approval.

When the user has instructed auto-approve for this session, skip the approval
ask and apply after the failing test exists.

## Several open mistakes

When more than one open mistake is in play, **do not walk them one by one
asking for approval**. Do not re-triage from a nested Repair's `{{asset}}`.

1. Read `{session.folder}/mistakes/` (skip `status: fixed`). Repairs already
   done live under `{session.folder}/repairs/{theme}/`.
2. For **the whole set**, inspect the **existing tool** — prose, templates,
   examples, generators, seeds, DSLs — not just the rule list. Same class of
   mistake is one row.
3. Write **`{session.folder}/batch-improvements.md`** — one table and one
   summary — then stop for a single batch decision (skip the ask when this
   session is auto-approved). Do not leave the table only in chat. Columns:

   | Theme | Already in the tool | Why it failed | Improvement |
   |-------|---------------------|---------------|-------------|

   Improvement means change what is already there (sharpen, contradict-fix,
   show it in the template/example/seed). **Do not default to a new named
   rule or scanner.** A scanner is allowed only when the failure is
   mechanical (a deterministic shape someone else's content could also hit)
   **and** the existing surface cannot carry it — e.g. story files must stay
   tier-neutral while `*_test_helper.{tier}` owns `describe("tier: …")`.
4. After that one decision, apply. Same root cause → one `{theme}` Repair;
   attach further mistakes of that class to it. Keep `batch-improvements.md`
   in the session folder as the batch record.

A single-mistake Repair still uses `{{asset}}` / `{{violation}}`. If that
violation is already logged, read that folder first (`mistake.md`,
`faultyAsset`). Do not start a parallel trail.

Read the **`active`** resource first. `{{asset}}` and repaired outputs live under
that root (docs → `{session.path}/.context/`; code → `{session.path}/{module}/`). Do not
repair into a divergent folder.

Run this loop in the current session when invoked directly. When launched
as a non-blocking background sub-agent, this text is the sub-agent's own
instructions — run the loop there instead, and report back once **validate**
passes.

**Log first.** If this violation has not already been recorded via
`log_mistake`, call `log_mistake` now (Repair takes the Mistake from context
when the session has none). Pass the **file** at `artifact` as `original` —
the `.drawio` XML or source, not a diagnosis of what was wrong (`wrong` is
the diagnosis). That writes `{session.folder}/mistakes/{name}/`
(`faultyAsset`, `mistake.md`). Call `log_correction` once this loop's fix lands
(Repair takes the Correction from context when none exists) and pass the
repaired file contents as `improved` — not a description of the redraw.
That creates `{session.folder}/repairs/{theme}/` (sibling of `mistakes/`) with
`improvement.md` and moves the Mistake folder(s) into it. `{theme}` is a
concise kebab-case name of the **root-cause improvement** (what you changed
in the tool), named after Step 3 — not the mistake rule or nested mistake
folder. The YAML index is `session.yaml`.

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

## When scan is clean but the user still reported a failure

The first question is **why the existing tool did not steer this** —
template, example, seed, generator, or a bullet that is vague or in
conflict — not whether a new scanner would catch it. Fix that surface.

Call **`createRule`** only when all of these are true: the failure is
mechanical; `ScanReport.matches(mistake)` is false; and the existing prose /
template / example / generator cannot carry the check. Then it writes a
named rule and scanner and runs that rule until scan fails on `{{asset}}`
in a way that matches the Mistake. Do **not** call `createRule` when scan
already matches, or to ban a one-off invented notation.

Do not proceed to root-cause analysis until **scan** fails on `{{asset}}`
for a mechanical rule — unless this is a prose/judgment rule per the
section above, in which case **validate** is the signal instead.

---

## 1. Open the mistake folder — mechanical rules only

Skip this step entirely for a prose/judgment rule (see above) — there is no
scanner to prove a fixture against. Otherwise work in the session mistake
folder (`{session.folder}/mistakes/{name}/`). `log_mistake` already created it
with `faultyAsset`. Add working notes there:

```
{session.folder}/mistakes/{name}/
  faultyAsset          ← the artifact file (already written — not a diagnosis)
  faultyAssets/        ← when more than one file (same layout as {{asset}})
  runs/1/run.md
```

Do not invent a parallel `{domain}/examples/` tree from this action. Do not
copy into `evals/` from this action — that is contribute, later.

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

Once you know the root cause, name `{theme}`: a concise kebab-case description
of **that** problem and the improvement (what the tool was missing or did
wrong). Create `{session.folder}/repairs/{theme}/` under that name. Do not
copy the mistake rule or the `mistakes/{name}/` folder name. Same root cause
→ same `{theme}` folder; a different root cause → a new folder.

Repair implements the tool fix as turns on a WorkspaceSession opened on the
CDD clone (`cddRepo.openSession`). Further Mistakes collected during this
loop attach to the same Repair.

If eval cannot connect the project clone and the CDD tools clone, **stop**.
Surface the error. Do not edit CDD files, do not log a correction, do not
pretend a session opened. Continue only if the user explicitly says to.

---

## 4. Fix the root cause

Draft a **surgical** change wherever root cause actually lives:

- Usually the context tool itself — its contexts, examples, template, action
  prose, or scanners.
- Occasionally a shared utility or primitive it depends on, when root cause
  traces down into one of those instead.

Touch only what root cause implicates; do not rebuild from spec.

**Fail-first test (required).** Write the test that fails on current conditions
before changing the context tool. Mechanical: `expect_scan_fails` /
`expect_scan_passes` from `context_tools.bdd.spec_helpers` (fail file fails
scan; pass file passes). Judgment: `generate_and_judge` from
`agent_bdd.spec_helpers` on the pass file. Do not add an eval-package spec
harness. If that test cannot fail, stop this mistake — append
it to `{session.folder}/deferred.md` and take the next open mistake.

When the user has auto-approved this repair session, apply after the failing
test exists. Otherwise: a **batch** uses the table in **Several open
mistakes** as the one ask — not a four-part ask per row. A **single**
mistake uses the four-part ask below.

### Approval ask — single mistake only

Every single-mistake approval ask — the repair sub-agent's return, and any
parent summary of it — MUST include all four, in plain English. Slug
labels, "Draft A/B", or "approve?" alone are a defect.

1. **What went wrong** — the concrete mistake in the artifact (one or two
   sentences a reader who was not in the session can follow).
2. **Why** — what was missing or wrong in the context tool (or utility /
   primitive) that let it happen — the root cause, not a restatement of (1).
   Start from the existing tool surface, not a missing scanner.
3. **What we will change** — the surgical fix: which files, what existing
   prose / template / example / seed / generator (or, only if mechanical
   and the surface cannot carry it, rule / scanner) lands, and what that
   stops next time. Name paths.
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

When validate passes, call `log_correction` (or Repair takes the Correction
from context). That sets `status=fixed`, `fixedIn` the Turn that did the fix,
and writes `repairedAsset` beside `faultyAsset` in the mistake folder under
`{session.folder}/repairs/{theme}/`.

Then eval that pair in place: `expect_scan_fails` on `faultyAsset`,
`expect_scan_passes` on `repairedAsset`, `generate_and_judge` on
`repairedAsset`. Do not wait for eval approval. Do not invent an eval-package
spec.

---

## 6. Capture the pass fixture — once validate passes

Skip this step for a prose/judgment rule — closing on **validate** in Step 5
is the end of that loop. Otherwise the mistake folder already holds the pair:

```
{session.folder}/repairs/{theme}/{name}/
  faultyAsset          ← or faultyAssets/ when more than one file
  repairedAsset        ← or repairedAssets/ when more than one file
```

Only the **original failure** and **final clean output after the fix** are
kept as fixtures. Delete `runs/` when the repair is done — working notes only
during the loop. Do **not** promote this pair into `evals/` from this action.

---

## 7. Eval is a separate tool

Do **not** run eval from this action. After repair, the agent (or
`contribute`) runs **`eval`**: `expect_scan_fails` on the before file,
`expect_scan_passes` on the after file, `generate_and_judge` on the pass
file, and hold that last generate for human review. Those helpers live on
Bdd and AgentBdd — not a new eval spec package.

---

# Validate

Take the persona of a **critical judge** — do not edit the artifact.

1. Follow **`session_guidance`**. Scope judgment to artifacts under `session.path` / the session layout.
2. Use **contexts** as the rubric — report pass/fail per named context and named rule with brief evidence.
3. Call **`scan`** on the session-rooted paths under review.
4. Do not fix. Report failures for fixing, then **validate** again when ready.

---
