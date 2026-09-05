# Diagnose Mode — When Tests Keep Failing

## When to flip into diagnose mode

If a test that should be passing keeps failing across multiple fix attempts — **stop writing code**. You are spinning. Flip into the diagnose discipline immediately.

**Triggers:**
- Same test fails after 2 or more consecutive fix attempts.
- The failure mode shifts but the test never goes GREEN.
- The error is unexpected (wrong exception type, wrong line, wrong value) and re-reading the code does not explain it.

---

## The six phases

### Phase 1 — Establish a feedback loop

Before any hypothesis: confirm you can reproduce the failure **on demand**.

- Run the single failing test in isolation: `npx jest --testPathPattern character.test.ts -t "should apply damage"`.
- Confirm the failure is deterministic — same error every run.
- If the test is flaky (sometimes passes), that is the root cause; fix the non-determinism first.

### Phase 2 — Read the failure clearly

Read the full failure output without skimming:

- **What was expected?** (`Expected: 3`)
- **What was received?** (`Received: 0`)
- **Where did it fail?** (file, line number)
- **What type of error?** (assertion fail, exception, timeout, type error)

Do not guess. The failure message often names the root cause.

### Phase 3 — Build 3–5 hypotheses

Write them out before testing any. Ranked by likelihood.

```
H1: Character.applyDamage is not accumulating — wounds resets to 0 each call.
H2: beforeEach is not re-creating the character — state bleeding from a sibling test.
H3: The import resolves to a cached/stub version, not the real Character.
H4: Test is asserting on the wrong property (wounds vs woundTotal).
H5: applyDamage method exists but the wounds property is on a nested object.
```

### Phase 4 — Instrument one variable at a time

Add a `[DEBUG-XXXX]` tagged log for the first hypothesis. Run the test. Read the output. Draw a conclusion. Remove the log before testing the next hypothesis.

```typescript
it('should apply damage from attacks', () => {
  character.applyDamage(3);
  console.log('[DEBUG-CHR1] wounds after applyDamage(3):', character.wounds);
  expect(character.wounds).toBe(3);
});
```

**One instrument per run.** Do not add multiple logs at once — you will not be able to read the output cleanly.

### Phase 5 — Fix the root cause

Once a hypothesis is confirmed, fix the root cause — not a symptom. A symptom fix masks the real problem and causes the next test to fail for a different surface reason.

- If the property resets to 0 in every call → fix `applyDamage` to accumulate.
- If state bleeds between tests → fix `beforeEach` to reset properly.
- Do not work around the failure with `// @ts-ignore` or `as any` casts.

### Phase 6 — Watch it go GREEN

Run the test. Watch it go GREEN. Remove all `[DEBUG-*]` instrumentation before proceeding.

Confirm no other tests in the file turned RED as a side effect of the fix.

---

## Rules during diagnose

- **One hypothesis tested at a time.** Testing two simultaneously makes the output unreadable.
- **Read the error before hypothesizing.** The error message often names the cause. Many spinning tests are caused by a typo, wrong import path, or a stale type reference.
- **Do not add a third fix without a confirmed hypothesis.** Two failed fix attempts without a hypothesis means you are guessing. Stop. Diagnose.
- **Do not move on.** Do not start the next test while a spinning test is RED. A spinning test left GREEN-ish through a workaround will cause three more failures later.
