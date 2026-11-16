# scripts/unit_guard
`budget_formatter.py` holds the unit tier to its time budget. `scripts/test.ps1 -Suite unit` puts this folder on `PYTHONPATH` and runs every spec file, and every story test, with `--format budget_formatter.BudgetDocumentation` (`budget_formatter.BudgetProgress` for the quiet re-run of the files flagged in parallel): a custom output format, which Mamba builds from that dotted name, its own extension point for hearing each example's end. *BudgetTiming* is mixed in ahead of Mamba's documentation or progress format; when an example passes or fails it asks *UnitBudget* to write the example to the log `CDD_UNIT_GUARD_LOG` names if it ran longer than `CDD_UNIT_EXAMPLE_BUDGET_MS` (100 ms unless set, its before.each and after.each included), one line each with the spec file, the milliseconds, and the example's describe path. `test.ps1` reads that log and fails each file listed.

- **Purpose:** Keep the unit tier fast enough to run after every change, by failing a spec file whose examples are slow, so a slow example is moved to a heavy spec or made fast with a fake before it slows every run.
- **Seam (terms):** the output formats `budget_formatter.BudgetDocumentation` and `budget_formatter.BudgetProgress` (*BudgetTiming*, *UnitBudget*), the environment variables `CDD_UNIT_GUARD_LOG` and `CDD_UNIT_EXAMPLE_BUDGET_MS`, and the log line `spec file<TAB>milliseconds<TAB>example path`.
- **Dependencies (one-way):** Mamba (`mamba.formatters.DocumentationFormatter` and `ProgressFormatter`, through its `--format` extension point; no Mamba class is changed), and nothing in this repository; when no log is named, it only reports.

## Constraint

Never import anything from the repository here: Mamba loads this module before the spec it times. Change the budget through `test.ps1 -ExampleBudgetMs`, not in this file, so every run reports against the same number.
