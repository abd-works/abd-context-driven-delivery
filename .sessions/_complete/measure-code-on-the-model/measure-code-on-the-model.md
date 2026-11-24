# Measure Code On The Model

Analysis and planning: the stories here are not built yet. This is one increment of the thin slice, which sets the order of the increments, [harness/.context/stories/thin-slice.md](../../harness/.context/stories/thin-slice.md); its epic, feature and stories are on the story map, [harness/.context/stories/story-map.md](../../harness/.context/stories/story-map.md). Each requirement sits under the story it belongs to.

**Outcome:** validating at the Clean Engineering model or code fidelity measures each function, class and module, keeps each measure as a fact on its node, and reports what is past a limit in the same validation report.

Requested on 2026-11-10: "when we run validation at clean model or clean code we make sure that we integrate the metrics that we did internally before using the metrics tools, and figure out a way to add those findings onto the model itself, eg it's just another fact on the model: what is its cyclomatic complexity".

## Notes from the backlog

From the Clean Engineering metrics backlog:

> The always-on metrics gate rule (`cdd_guidance/rules/metrics-gate.md`) was removed on 2026-11-09, because a gate run before every commit got in the way of small fixes. The measuring itself stays useful, so it moves into the Clean Engineering practice, where it applies when someone works at that practice's fidelities rather than on every commit.
>
> ## 1. Add formal code metrics to the Clean Engineering practice
>
> **Goal.** Clean Engineering's code fidelity (`cdd_guidance/practices/clean_engineering/clean_engineering.md`) states its size and complexity limits as named rules, and Validate measures them, so a person sees which function, class or module is past a limit in the same validation report as the other rules.
>
> **Starting points.**
> - The limits the removed rule used: a function over 10 paths, a readability score over 15, over 50 lines, or over 5 parameters; a class over 100 total complexity or 30 methods; a class that depends on more classes than before; a group of methods sharing no data with the rest of their class.
> - `.context/repo-review/metrics_gate.py` and `.context/repo-review/code-metrics-trend.md` already measure these with radon, lizard, complexipy, cohesion and grimp. They need a metrics venv and Node tools, which a practice rule would have to install or check for.
> - The rules should report a metric in plain English, never by its abbreviation, and colour a trend as getting better or worse.
>
> **Open questions.** Does a rule fail on any regression against the base commit, as the gate did, or only past a fixed limit? Do the metrics run inside Validate's graph rules, or as a separate step that Validate reads?

## Epic: Map Work Into Knowledge Graph

### Feature: Check Nodes Against Graph Rules → Check Clean Engineering Code Through The Graph

Validate at Clean Engineering's modules, model and code fidelities checks what one file at a time cannot see. The other half of this feature is [Check Clean Engineering Across Files](check-clean-engineering-across-files.md).

#### Story: Record Code Metrics As Node Facts

- Each function, class and module node in the knowledge graph carries its measures as facts, so a measure is read like any other fact on the model.
- The measures the removed gate used: paths through a function (cyclomatic complexity), readability score (cognitive complexity), lines, parameters; a class's total complexity, method count and the classes it depends on; a group of methods sharing no data with the rest of their class (cohesion).
- Measured with what `.context/repo-review/metrics_gate.py` and `code-metrics-trend.md` already use: radon, lizard, complexipy, cohesion and grimp. They need a metrics venv and Node tools, which the practice would have to install or check for.

#### Story: Check Code Metrics Against Clean Engineering Limits

- Clean Engineering's code fidelity (`cdd_guidance/practices/clean_engineering/clean_engineering.md`) states its size and complexity limits as named rules, and Validate checks them at the model and code fidelities.
- The limits: a function over 10 paths, a readability score over 15, over 50 lines, or over 5 parameters; a class over 100 total complexity or 30 methods; a class that depends on more classes than before; a group of methods sharing no data with the rest of their class.
- Each function, class or module past a limit shows in the same validation report as the other rules.
- A metric is named in plain English, never by its abbreviation, and its trend is coloured as getting better or worse.
- Open questions: does a rule fail on any regression against the base commit, as the gate did, or only past a fixed limit? Do the metrics run inside Validate's graph rules, or as a separate step that Validate reads?
