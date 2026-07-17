# Diagnose Mode — When Acceptance Tests Keep Failing

## When to flip into diagnose mode

If an acceptance / story test that should be passing keeps failing across multiple fix attempts — **stop writing tier or production code**. You are spinning. Flip into the diagnose discipline immediately.

**Triggers:**
- Same scenario stays RED after 2 or more consecutive fix attempts.
- The failure mode shifts (tier wiring → assertion → import) but the test never goes GREEN.
- RED looks like a wiring or vocabulary problem (wrong tier import, missing Story constant, domain term drift) and re-reading the tier file does not explain it.
- Transform / regenerate “fixed” the map but the leaf scenario still fails for a different surface reason.

---

## The six phases

### Phase 1 — Establish a feedback loop

Before any hypothesis: confirm you can reproduce the failure **on demand**.

- Run the single failing acceptance test in isolation (one story / one scenario / one tier).
- Confirm the failure is deterministic — same error every run.
- If the test is flaky (sometimes passes), that is the root cause; fix the non-determinism first (shared fixtures, background state, clock, IO).

### Phase 2 — Read the failure clearly

Read the full failure output without skimming:

- **What was expected?** (Then observation, example row, domain outcome)
- **What was received?** (actual UI/API/state, exception message)
- **Where did it fail?** (tier file, runner, story-spec constant, production boundary)
- **What type of error?** (assertion fail, import/wiring, missing scenario key, timeout, vocabulary mismatch)

Do not guess. Many RED story tests are wrong tier wiring or a story name that no longer matches the map — not production logic.

### Phase 3 — Build 3–5 hypotheses

Write them out before testing any. Ranked by likelihood.

```
H1: Tier file imports the wrong Story constant / scenario key — runner never hits the intended path.
H2: Story or scenario was renamed on the map; regeneratable leaf updated but write-once tier still uses the old name.
H3: Given/background leaves the system in a different state than the scenario assumes.
H4: Then asserts an internal/mechanic term; production speaks domain vocabulary the step no longer matches.
H5: Example row placeholders do not bind to the steps (outline vs concrete values drift).
```

### Phase 4 — Instrument one variable at a time

Add a `[DEBUG-XXXX]` tagged log for the first hypothesis — at the tier boundary or runner entry, not deep inside production. Run the single test. Read the output. Draw a conclusion. Remove the log before testing the next hypothesis.

```python
def test_submit_order_happy_path(self):
    story = SUBMIT_ORDER
    print("[DEBUG-ST1] scenario keys:", list(story.keys()))
    run_scenario(self, story, "happy_path")
```

**One instrument per run.** Do not add multiple logs at once — you will not be able to read the output cleanly.

### Phase 5 — Fix the root cause

Once a hypothesis is confirmed, fix the root cause — not a symptom. A symptom fix masks the real problem and causes the next scenario to fail for a different surface reason.

- If the tier points at a stale scenario key → re-wire to the regeneratable Story constant; do not duplicate step text in the tier.
- If vocabulary drifted → align Then steps and domain terms with the domain source; do not loosen the assertion to “whatever the UI returns.”
- If background/state is wrong → fix Given / shared helper setup, not the Then.
- Do not work around RED with skipped tests, broad `except`, or inventing a parallel story name.

### Phase 6 — Watch it go GREEN

Run the test. Watch it go GREEN. Remove all `[DEBUG-*]` instrumentation before proceeding.

Confirm no sibling scenarios or tiers in the same leaf turned RED as a side effect of the fix.

---

## Rules during diagnose

- **One hypothesis tested at a time.** Testing two simultaneously makes the output unreadable.
- **Read the error before hypothesizing.** Import errors, missing keys, and name mismatches usually name the cause. Many spinning acceptance tests are tier wiring or map/tier drift — not deep production bugs.
- **Do not add a third fix without a confirmed hypothesis.** Two failed fix attempts without a hypothesis means you are guessing. Stop. Diagnose.
- **Do not move on.** Do not start the next story while a spinning scenario is RED. A scenario left GREEN-ish through a workaround will poison the thin slice and the next fidelity.
- **Respect regeneratable vs write-once.** Prefer fixing the regeneratable story-spec via transform/generate when the map is wrong; edit tier files only for production calls and assertions that must stay hand-authored.
