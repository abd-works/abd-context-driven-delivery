# Repair

`Improvement.repair` gives the repair instructions for each listed guidance and logs `repair` in the session's log. It does **not** run a fail-first test, write files, or verify. **Leave the repair open after this call:** diagnose, propose the toolset change, write the fail-first test, then make the change. This file is the recipe `/repair` must follow.

## What you are diagnosing

Not a list of tactical diffs. Not “this annotation is wrong, this type is wrong, this file still says Session.”

The question is: **why did the expected overarching behavior of the toolset fail to occur?**

A mistake in a CDD toolset is almost never “the agent typed the wrong token.” It is: after grill / sketch / generate / validate / satisfy, the **system** was supposed to produce complete, validated artifacts — and it did not. Find the seam that let that happen, then change **that**.

If the answer you are about to write could be a bullet list of file edits that match `wrong:` to `improved:`, stop. You have not found the cause.

## Use diagnose

When the cause is not already a one-line miss of a documented recipe, call the **`diagnose`** tool this repair lists, with the same guidance, and stay in its phases. Follow its instructions only. Do not skip phases unless you can say why in one sentence.

Diagnose phases, applied to **toolset behavior** (not a local crash):

1. **Feedback loop.** An agent-runnable pass/fail for “the expected action outcome happened.” Prefer `/bdd` at the mechanic seam (action refused, path covered, validate failed). Use `/agent-bdd` when the miss is an AI step or markdown recipe. Approximate the mistake’s `original:` as the fixture. If you cannot build a loop, stop and list what you tried.
2. **Reproduce.** Run the same action the session ran (generate, sketch, validate, satisfy) against a fixture that looks like the mistake. Confirm you get the **same class of miss** (partial generate, ungated sketch, silent validate) — not a nearby syntax error.
3. **Hypothesise.** Three to five **falsifiable** claims about *why the toolset allowed that miss*. Show them before testing. Example shape: “If generate only writes under the session's root, then a sketch that names `harness/` will still report generate success and validate will stay green.”
4. **Proposed solution (before any test).** For the leading hypothesis, state the **toolset change** that would make the overarching behavior true: what the action will refuse, which paths it will implement or check, what becomes a hard fail. One paragraph, at the seam — not a file-edit list. Show it to the user. Do not write `/bdd` or `/agent-bdd` specs until this is on the table.
5. **Instrument.** One variable per probe at the seam that distinguishes those claims (what the ask named as source vs what generate treated as source, grill-in-sketch vs sketch-alone, what the session log says ran vs what the agent claims ran).
6. **Fix + regression.** Fail-first test that would fail today’s toolset and pass after the proposed change. Then the smallest tool change. Re-run the Phase 1 loop on the original scenario.
7. **Cleanup.** State the hypothesis that held. Ask what would have prevented the miss (a missing gate, a check that covered too few files, a step the session log never recorded).

Do not proceed from “here is what is still wrong in the tree” to tests or a patch without a held hypothesis **and** a proposed solution.

## Where to look first (toolset seams)

These are the usual places a **toolset** fails its own story. They are starting hypotheses, not a punch list.

- **Generate from the source the ask implies.** Source of truth is **context of the ask**, not a vocabulary lock (“the locked sketch,” “the files on disk,” “the CE diagram”). If this session grilled/sketched and the ask is generate, the source is that sketch. If the ask is transform, the source is the format you already have. If there is no sketch, do not invent one as a rule. Generate must finish the **whole** implied artifact — leftover annotations and half-migrated types mean generate used the wrong source (usually “code already there”) or stopped early. Research: did it invent from scratch instead of **transform** when a model already existed in another format? Did one generate call swallow a job that needed **several calls**? Did “if the module exists, fill gaps” invite a halfway stop? Do not let words like *locked* or *envelope* force a stupid default.
- **Grill in sketch.** `Sketch.sketch` already gives the grill's interview (`GrillContext.grill_with_context`) in its instructions. At diagnose time, **research** whether that path ran — do not re-implement grill-in-sketch unless research shows sketch still completing without it.
- **What the session ran.** The session's `session.log` records each action a call ran (`generate`, `validate`, `repair`, …) and each tool call. Read it before treating a step as skipped: it shows which actions ran, in what order, and which validate passed.
- **`/repair` leaves the repair open.** This call gives the instructions and stops. Diagnose → proposed solution → fail-first happen next, in the same chat. Commit (`repo.push_commit`) only after the fail-first change lands.

## Associate, then theme, then diagnose

1. Pair each mistake with its correction (git notes + `Fixes-Mistake` / `Introducing-Commit`, or the yaml pair if that is all there is).
2. Name a **theme** as an improvement problem (“generate does not cover the sketch,” not a list of rule names).
3. Tag pairs with that theme.
4. For each theme: Diagnose until one seam explains the cluster. **Propose the toolset change.** Then one fail-first test, then that change, then the original scenario.
5. The mistake and its correction stay in separate commits. One ask → change → commit and push with `repo.push_commit`.

## Tests (after the proposed solution)

Do not write these until the proposed toolset change is stated.

- Mechanic of the tool (refuse, path, check, commit): `/bdd`.
- Agent / markdown recipe: `/agent-bdd`.
- Fixture ≈ the mistake `original:` (and the session action that produced it), not a restatement of `wrong`/`improved` as the spec.
- The spec asserts the **proposed behavior** (refuse, wider check, hard fail), not that a particular file now matches `improved:`.

## Verify a theme

`verify_fix` re-runs a theme's fail-first test and the original scenario of each mistake tagged with it. A failing one reopens the theme for diagnose.
