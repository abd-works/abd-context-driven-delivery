# Clean Engineering metrics backlog

The always-on metrics gate rule (`cdd_guidance/rules/metrics-gate.md`) was removed on 2026-11-09, because a gate run before every commit got in the way of small fixes. The measuring itself stays useful, so it moves into the Clean Engineering practice, where it applies when someone works at that practice's fidelities rather than on every commit.

## 1. Add formal code metrics to the Clean Engineering practice

**Goal.** Clean Engineering's code fidelity (`cdd_guidance/practices/clean_engineering/clean_engineering.md`) states its size and complexity limits as named rules, and Validate measures them, so a person sees which function, class or module is past a limit in the same validation report as the other rules.

**Starting points.**
- The limits the removed rule used: a function over 10 paths, a readability score over 15, over 50 lines, or over 5 parameters; a class over 100 total complexity or 30 methods; a class that depends on more classes than before; a group of methods sharing no data with the rest of their class.
- `.context/repo-review/metrics_gate.py` and `.context/repo-review/code-metrics-trend.md` already measure these with radon, lizard, complexipy, cohesion and grimp. They need a metrics venv and Node tools, which a practice rule would have to install or check for.
- The rules should report a metric in plain English, never by its abbreviation, and colour a trend as getting better or worse.

**Open questions.** Does a rule fail on any regression against the base commit, as the gate did, or only past a fixed limit? Do the metrics run inside Validate's graph rules, or as a separate step that Validate reads?
