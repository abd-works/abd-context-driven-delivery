# Repair

`Improvement.repair` opens a work session, a turn, and a domain `Repair` bucket. It does **not** close the turn. It does **not** run fail-first scan, nest files, or verify. **Leave the turn open.** Diagnose, propose the kit change, fail-first, then `finish_turn`. This file is the recipe `/repair` must follow.

## What you are diagnosing

Not a list of tactical diffs. Not “this annotation is wrong, this type is wrong, this file still says Session.”

The question is: **why did the expected overarching behavior of the toolset fail to occur?**

A mistake on this kit is almost never “the agent typed the wrong token.” It is: after grill / sketch / generate / validate / satisfy / finish_turn, the **system** was supposed to produce a complete, gated, scannable, one-commit turn — and it did not. Find the seam that let that happen, then change **that**.

If the answer you are about to write could be a bullet list of file edits that match `wrong:` to `improved:`, stop. You have not found the cause.

## Use `/diagnose`

When the cause is not already a one-line miss of a documented recipe, run **Diagnose** and stay in its phases:

```
python -m tools manifest diagnose.diagnose:Diagnose
```

On Windows use `.\tools.ps1` (sets venv + UTF-8). Invoke `diagnose` (`kind: sub_agent`). Follow `response.instructions` only. Do not skip phases unless you can say why in one sentence.

Diagnose phases, applied to **toolset behavior** (not a local crash):

1. **Feedback loop.** An agent-runnable pass/fail for “the expected action outcome happened.” Prefer `/bdd` at the mechanic seam (action refused, path covered, scan failed). Use `/agent-bdd` when the miss is an AI step or markdown recipe. Approximate the mistake’s `original:` as the fixture. If you cannot build a loop, stop and list what you tried.
2. **Reproduce.** Run the same action the session ran (generate, sketch, validate, finish_turn) against a fixture that looks like the mistake. Confirm you get the **same class of miss** (partial generate, ungated sketch, silent scan, dropped turn) — not a nearby syntax error.
3. **Hypothesise.** Three to five **falsifiable** claims about *why the toolset allowed that miss*. Show them before testing. Example shape: “If generate only writes under `session.path`, then a sketch that names `primitives/` will still report generate success and validate will stay green.”
4. **Proposed solution (before any test).** For the leading hypothesis, state the **kit change** that would make the overarching behavior true: what the action will refuse, which paths it will implement or scan, what becomes a hard fail. One paragraph, at the seam — not a file-edit list. Show it to the user. Do not write `/bdd` or `/agent-bdd` specs until this is on the table.
5. **Instrument.** One variable per probe at the seam that distinguishes those claims (what the ask named as source vs what generate treated as source, grill-in-sketch vs sketch-alone, process boundary vs `open_turn` memory).
6. **Fix + regression.** Fail-first test that would fail today’s kit and pass after the proposed change. Then the smallest tool change. Re-run the Phase 1 loop on the original scenario.
7. **Cleanup.** State the hypothesis that held. Ask what would have prevented the miss (missing gate, scan bound too small, turn not a process property).

Do not proceed from “here is what is still wrong in the tree” to tests or a patch without a held hypothesis **and** a proposed solution.

## Where to look first (toolset seams)

These are the usual places the **kit** fails its own story. They are starting hypotheses, not a punch list.

- **Generate from the source the ask implies.** Source of truth is **context of the ask**, not a vocabulary lock (“the locked sketch,” “the files on disk,” “the CE diagram”). If this session grilled/sketched and the ask is generate, the source is that sketch. If the ask is transform, the source is the format you already have. If there is no sketch, do not invent one as a rule. Generate must finish the **whole** implied artifact — leftover annotations and half-migrated types mean generate used the wrong source (usually “code already there”) or stopped early. Research: did it invent from scratch instead of **transform** when a model already existed in another format? Did one `finish_turn` swallow a job that needed **several turns**? Did “if the module exists, fill gaps” invite a halfway stop? Do not let words like *locked* or *envelope* force a stupid default.
- **Grill in sketch.** `Sketcher.sketch_session` already calls `grill_with_context` at step 0. At diagnose time, **research** whether that path ran — do not re-implement grill-in-sketch unless research shows sketch still completing without it.
- **Turn envelope.** Check the **current** `Turn` / `WorkSession` code before treating process-local `open_turn` as a live bug. Notes + same-process `open`/`finish_turn` may already be enough. Do not persist `open_turn` blindly.
- **`/repair` leaves the turn open.** `Improvement.repair` opens the bucket and stops. Diagnose → proposed solution → fail-first happen on that open turn. Close with `finish_turn` only after the fail-first change lands.

## Associate, then theme, then diagnose

1. Pair each mistake with its correction (git notes + `Fixes-Mistake` / `Introducing-Commit`, or the yaml pair if that is all there is).
2. Name a **theme** as an improvement problem (“generate does not cover the sketch,” not a scanner slug dump).
3. Tag pairs with that theme.
4. For each theme: Diagnose until one seam explains the cluster. **Propose the kit change.** Then one fail-first test, then that change, then the original scenario.
5. Mistake turn and correction turn stay separate. One ask → change → `finish_turn` (commit + push on `session/{name}`).

## Tests (after the proposed solution)

Do not write these until the proposed kit change is stated.

- Mechanic of the tool (refuse, path, scan, commit): `/bdd`.
- Agent / markdown recipe: `/agent-bdd`.
- Fixture ≈ the mistake `original:` (and the session action that produced it), not a restatement of `wrong`/`improved` as the spec.
- The spec asserts the **proposed behavior** (refuse, expanded envelope, hard fail), not that a particular file now matches `improved:`.

## Domain bucket

`WorkSession.repairs[theme]` is the nest. Status: `backlog` → work → `finished`. `/repair` owns the recipe; domain `Repair` is not agentic.
