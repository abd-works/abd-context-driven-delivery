# scripts/unit_guard
`sitecustomize.py` holds the unit tier to its time budget. `scripts/test.ps1 -Suite unit` puts this folder first on `PYTHONPATH`, so Python imports it when each spec process starts. It wraps Mamba's end of an example and writes every example that ran longer than `CDD_UNIT_EXAMPLE_BUDGET_MS` (100 ms unless set, its before.each and after.each included) to the log `CDD_UNIT_GUARD_LOG` names, one line each with the spec file, the milliseconds, and the example's describe path. `test.ps1` reads that log and fails each file listed.

- **Purpose:** Keep the unit tier fast enough to run after every change, by failing a spec file whose examples are slow, so a slow example is moved to a heavy spec or made fast with a fake before it slows every run.
- **Seam (terms):** the environment variables `CDD_UNIT_GUARD_LOG` and `CDD_UNIT_EXAMPLE_BUDGET_MS`, and the log line `spec file<TAB>milliseconds<TAB>example path`.
- **Dependencies (one-way):** Mamba (`mamba.example.Example`), and nothing in this repository; when Mamba is not installed or no log is named, it does nothing.

## Constraint

Never import anything from the repository here: this file loads in every Python process started with that path, before the spec it times. Change the budget through `test.ps1 -ExampleBudgetMs`, not in this file, so every run reports against the same number.
