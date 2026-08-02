# Diagnose (BDD)

BDD does not own the six-phase loop. When a unit/spec test is still RED after
2 consecutive fix attempts, `satisfy` / `iterate` call
`diagnostic().diagnose()` — the shared Diagnose tool (phases stay on that
tool; they are not inlined into the action markdown).

BDD-specific triggers for that call (also in the action docstrings):

- Same test fails after 2 or more consecutive fix attempts.
- Failure mode shifts but the test never goes GREEN.
- Unexpected error (wrong exception, wrong line, wrong value) and re-reading the code does not explain it.
