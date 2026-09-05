# Diagnose Mode — When Tests Keep Failing

## When to flip into diagnose mode

If a test that should be passing keeps failing across multiple fix attempts — stop writing code. You are spinning. Flip immediately into the **diagnose** discipline.

Triggers:
- Same test fails after 2 or more consecutive fix attempts
- The failure mode shifts but the test never goes GREEN
- The error is unexpected (wrong exception type, wrong line, wrong value) and re-reading the code doesn't explain it
- You are adding defensive workarounds instead of fixing the root cause

Do **not** keep iterating blind. A third fix attempt without a feedback loop is wasted time.

---

## How to diagnose a failing acceptance test

Follow the six-phase loop from the diagnose skill. Applied to acceptance test failures:

### Phase 1 — Build a feedback loop

You already have one: the failing test **is** the feedback loop. But confirm it is a _good_ loop:

- Is the test deterministic? (No random data, no time dependency, no shared mutable state between runs.)
- Does it run in under a few seconds? (A slow loop blunts iteration speed.)
- Does the assertion target the **exact** symptom, not just "didn't crash"?

If the loop is flaky or slow, fix the loop before fixing the bug. A 2-second deterministic failure is a debugging superpower.

### Phase 2 — Reproduce

Run the test in isolation. Confirm:
- [ ] The failure matches what you expect — right test, right assertion, right error message.
- [ ] It fails consistently across multiple runs (or, if flaky, reproducibly enough to debug).

Do not proceed until you can reproduce it on demand.

### Phase 3 — Hypothesise

Before touching any code, write down **3–5 ranked hypotheses**. Each must be falsifiable:

> "If `<X>` is the cause, then `<changing Y>` will make the test pass / `<changing Z>` will make it fail differently."

Common hypotheses for acceptance test failures:
1. Production code does not implement the behavior the test asserts (normal RED state — is this just a new test?)
2. Test helper sets up state incorrectly — the `given_*` step does not match what the domain expects
3. Wrong object or method under test — test calls a stub, mock, or unrelated function
4. Assertion is wrong — `then_*` helper checks the wrong field, wrong type, or wrong equality
5. Import or fixture wiring is broken — test fails at setup, not at assertion

Show the ranked list before testing any of them.

### Phase 4 — Instrument

One probe per hypothesis. Change one variable at a time.

- Add a targeted `print` / log at the boundary that distinguishes hypotheses. Tag it: `[DEBUG-<4-char-id>]`.
- Read the actual value returned; compare it to what the assertion expects.
- Never "log everything and grep."

### Phase 5 — Fix + regression test

Fix **only** the root cause identified in Phase 4. Do not patch around it.

- If the fix touches production code: confirm the test goes GREEN, then re-run all related tests.
- If the fix is in a helper: confirm the helper now correctly models the step it names.
- If the fix is in the assertion: confirm the assertion now captures the real expected outcome.

Remove all `[DEBUG-...]` instrumentation before declaring done.

### Phase 6 — Cleanup

- [ ] Test passes consistently across multiple runs
- [ ] No `[DEBUG-...]` tags remain
- [ ] The root cause is stated in a comment or commit message so the next reader understands the fix

---

## Common acceptance test failure patterns

| Symptom | Likely cause |
|---------|-------------|
| `AttributeError` / `TypeError` on the production object | Method or property does not exist yet — normal RED state |
| `AssertionError` with unexpected actual value | `then_*` helper checks wrong field, or `given_*` wires wrong state |
| Test passes in isolation, fails in suite | Shared mutable fixture or import-side-effect contamination |
| Test passes immediately without production code | Assertion is vacuously true — test proves nothing; tighten it |
| Different error every run | Non-deterministic setup — pin randomness, isolate filesystem |
| Error is in `given_*` / `when_*`, not in production code | Helper is misconfigured; fix the helper, not the production code |

---

## Reference

Full diagnose discipline: `c:\dev\abd-works\.cursor\skills\diagnose\SKILL.md`
