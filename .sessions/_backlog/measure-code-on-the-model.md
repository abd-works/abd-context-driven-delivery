# Measure Code On The Model

Built on 2026-11-22: the three stories here are built, with the person's decisions of that day written under "Decided and built" below. One measure is left for later, defects for each thousand lines of a branch. This is one increment of the thin slice, which sets the order of the increments, [harness/.context/stories/thin-slice.md](../../harness/.context/stories/thin-slice.md); its epic, feature and stories are on the story map, [harness/.context/stories/story-map.md](../../harness/.context/stories/story-map.md). Each requirement sits under the story it belongs to.

**Outcome:** validating at the Clean Engineering model or code fidelity measures each function, class and module, keeps each measure as a fact on its node, and reports what is past a limit in the same validation report.

Requested on 2026-11-10: "when we run validation at clean model or clean code we make sure that we integrate the metrics that we did internally before using the metrics tools, and figure out a way to add those findings onto the model itself, eg it's just another fact on the model: what is its cyclomatic complexity".

## Decided and built (2026-11-22)

The person's decisions, and what was built from each:

1. **The measures are taken on validate, at Clean Engineering's model and code fidelities.** The limits are ordinary graph rules of Clean Engineering, listed on its node types at the model and code fidelities, so they report there. The measures they read are facts the practice's reader keeps while it reads the files a validate names (`GraphReading.read_working_copy`, through `keep_code_measures`); a load of the whole working copy keeps none, because a measuring tool run over every file would slow every load of the graph. Nothing in validate or in `harness/graph` was changed for them (the person's direction of 2026-11-22: "please make sure we are simply adding new mechanical graph rules").
2. **Each function, class or module read from Python or TypeScript collects each measure through a tool chosen for that measure and that language.** *CheckedCodeMeasures* asks, for each node, the tool *ChosenTools* names for the measure in the node's language.
3. **The table of measure by language is stored in the CDD config file**, `.context/config.json`, under `code_measures`, with the limits beside it. Only Python and TypeScript are filled in. Code in any other language is reported by name (*NoToolChosen*), once for each file, by the limit rule of each measure nobody chose a tool for, until someone chooses a tool or writes `not measured`. A project takes the measures once its config has the section; a project with no section measures nothing.
4. **Graph rules read the measures off the nodes, compare them with the limits, and report in the same validation report as the other rules.** Seven rules: `limit-paths-through-a-function`, `keep-functions-readable`, `limit-function-lines`, `limit-function-parameters`, `limit-class-complexity`, `limit-class-methods`, `keep-class-methods-sharing-data`.
5. **The module measures of the older script stay in; defects for each thousand lines of a branch are not part of this build.**

What was settled while building:

- **No tool for a fact the graph already records** (the person, 2026-11-22: "If we are already reporting a fact we don't need a tool to do it again"). A function's lines are its `line_count`, its parameters are counted from its parameter nodes as `limit-operation-parameters` counts them, a class's methods are its `method_count`, a module's import loops its `import_cycles` and the modules it imports its `dependsOn` edges; copied function bodies are the `duplicate_of` and `near_copy_of` facts `eliminate-duplication` already reports. None of these is in the tool table.
- **Tools, only for what no fact gives.** Lizard supplies the paths through a function, its readability score (lizard's cognitive complexity extension) and a class's total complexity, in both languages. Radon supplies a Python file's maintainability score and nothing else. The practice's own reader counts the classes a class depends on, the modules that import a module, abstractness and instability from the graph's edges, and the groups of a Python class's methods that share no data from the class's syntax tree. Complexipy, cohesion, grimp, networkx and dependency-cruiser are not needed.
- **A metrics group in the graph tree** (the person, 2026-11-22). Under a function, a class or a module the explorer tree shows one child named `metrics`, holding each fact a limit rule reads there with its plain-English name, its value and its limit, marked when past the limit. The filter offers `metrics` beside the relationship kinds. The limit rules and the group read one list (`GraphReading.metrics_of`, from the measures in `measures/code_measures.py`).
- **Not measured, written so in the table:** groups of methods sharing no data in TypeScript, a maintainability score in TypeScript, and blocks of code copied across files in either language (jscpd takes it, and is not installed).
- **Limits.** A function over 10 paths, a readability score over 15, over 50 lines, over 5 parameters; a class over 100 total complexity, over 30 methods, or with more than one group of methods sharing no data. An import loop is already reported by `one-way-deps`, so no second rule reports it. A class that depends on more classes than before is kept as a fact with no rule, since it needs a base commit to compare with. The module measures are kept for information, with no limit.
- **Installing the tools.** `pip install -e ".[measures]"` installs lizard and radon, the optional `measures` group of `pyproject.toml`. A chosen tool that is missing is reported by the measure's rule, by name, with that command.
- **The open questions above are answered:** a rule fails past a fixed limit, not on a regression against a base commit; the measures are facts the reader keeps when a validate's refresh reads the files it names, and ordinary graph rules read them.

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

#### Story: Record Module Measures As Node Facts

Requested on 2026-11-22: the item names functions, classes and modules, and listed no measure for a module. The exploratory testing of release 1.2 found that defects gather by module (see [code-metrics.md](../release-1-2-fixes/exploratory-testing/analysis/code-metrics.md)), so a module carries its own measures.

- Each module node in the knowledge graph carries its measures as facts, beside the facts of its classes and functions.
- Measures the older script `.context/model/repo-review/measure_revision.py` already took, which were not carried into this item:
  - the modules that import this one, and the modules it imports (grimp for Python, dependency-cruiser for TypeScript; the graph already holds the import edges, so the two counts can be read from it)
  - import loops, where modules import each other in a circle (networkx, from the import data)
  - a maintainability score for each file (radon)
  - copied code, as blocks repeated across files (jscpd) and as function bodies of the same shape under different names (the script's own count; an operation already keeps a fingerprint of its body)
  - abstractness and instability, the share of abstract classes against the share of outgoing imports: reported for information only, because this framework extends through annotations and registration and the measure misreads it
- One measure from the defect analysis of release 1.2: defects found for each thousand lines of the module's production code.
  - It is measured for a branch at the time its defects are captured, such as an exploratory testing session on that branch, from that session's defect reports and the branch's code as it stands then.
  - It belongs to that branch only: the next merge to main wipes it, so main never carries a defect rate measured on code that has since been fixed.
- Decided on 2026-11-22: the other measures the defect analysis proposed for a module are left out (lines of production code as a measure of its own, stories with no failure scenario, published operations with no test of a refused argument, formats with no there-and-back test, production changes with no test in the same commit).
- Open question: which of the older script's measures fail validate past a limit, and which are only reported?

#### Story: Check Code Metrics Against Clean Engineering Limits

- Clean Engineering's code fidelity (`cdd_guidance/practices/clean_engineering/clean_engineering.md`) states its size and complexity limits as named rules, and Validate checks them at the model and code fidelities.
- The limits: a function over 10 paths, a readability score over 15, over 50 lines, or over 5 parameters; a class over 100 total complexity or 30 methods; a class that depends on more classes than before; a group of methods sharing no data with the rest of their class.
- Each function, class or module past a limit shows in the same validation report as the other rules.
- A metric is named in plain English, never by its abbreviation, and its trend is coloured as getting better or worse.
- Open questions: does a rule fail on any regression against the base commit, as the gate did, or only past a fixed limit? Do the metrics run inside Validate's graph rules, or as a separate step that Validate reads?
