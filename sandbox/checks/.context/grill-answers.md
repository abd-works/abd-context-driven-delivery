# Grill Answers

### First signature deliverable

Thin slice ? check_spec.py covering only a Check (routine, natural 20, modifiers). OpposedCheck and TeamCheck stay in the sketch until Check is green at development. Framework Mamba/Python.

### Natural-20 and dice injection

Check takes optional dice at construction, default 1d20. Tests pass a stub dice that always returns a chosen face (e.g. 20). Same seam supports other dice rules later and stub/mock without patching module RNG.

### Critical near-miss fixture

For the critical-flip leaf, use stubbed dice that always return 20, and choose rank + DC so the total without the crit degree fails, and natural-20 +1 degree makes succeeded true. Document those numbers on the sketch s-lines.

### Test fakes for Trait DC Modifier

Signature/development fixtures use tiny test fakes (SimpleNamespace or equivalent) exposing .rank / .target / .amount ? no full measurement.Rank wiring in this Check slice.

### Deterministic stub dice everywhere

Prefer stubbed dice in every Check context so expects are deterministic. Concrete fixtures filled on sketch ? no-modifiers die=8 rank=5 DC=10 total=13; routine die=10; crit die=20 rank=0 DC=21; modifiers die=10 rank=5 DC=15 mod=+5 total=20.

### Routine context — single leaf

Keep only `it should treat the die as ten` under routine. Total/succeeded stay under no-modifiers; routine proves the die override only.

