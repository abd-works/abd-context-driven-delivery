---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Check Clean Engineering Code Through The Graph

Story map: [Check Clean Engineering Code Through The Graph](../../../../.context/story-map.md#e-check-clean-engineering-code-through-the-graph). Session release-1-2-fixes.

**Evidence mode.** Every scenario here is *Observed*: it holds today and names the spec that runs it. `cdd_guidance/practices/clean_engineering/measures/code_measures_spec.py` stands the outside tools in at the one place the practice asks a tool; `cdd_guidance/practices/clean_engineering/measures/code_measures_heavy_spec.py` runs the real tool, lizard. Decided 2026-11-22: radon and the maintainability score it took are dropped. Built on 2026-11-22 from the person's five decisions of that day, written in `.sessions/_backlog/measure-code-on-the-model.md`.

### Domain terms

- ++code measure++ — one number about a function, a class or a module, kept as a fact on its node: the paths through a function (cyclomatic complexity), its readability score (cognitive complexity), its lines of code, its parameters; a class's total complexity, methods, classes depended on, and groups of methods that share no data; a module's importing and imported modules, import loops, copied function bodies, abstractness and instability.
- ++chosen tool++ — the tool a project's `.context/config.json` names, under `code_measures`, to take one measure in one language. `not measured` there is a decision to leave the measure out; a missing entry is a choice nobody made.
- ++checked file++ — a file a validate names in `paths`.

> In steps: the shop project holds `shop/cart.py`, whose class Cart has the function total.

## Story: Check Code Metrics Against Clean Engineering Limits

### Evidence

Observed (`cdd_guidance/practices/clean_engineering/measures/code_measures_spec.py`, `cdd_guidance/practices/clean_engineering/measures/code_measures_heavy_spec.py`). Each rule's failing and repaired example is in `cdd_guidance/practices/clean_engineering/model/python/_examples/<rule>/`.

#### Scenario Outline: Report a node whose measure is past its limit

*Given* the node of <node> holds <measure> <value>
*When* the graph rules run
*Then* <rule> reports it, saying "<words>"

| node | measure | value | rule | words |
| --- | --- | --- | --- | --- |
| the function total | paths_through | 11 | limit-paths-through-a-function | has 11 paths through it (cyclomatic complexity), over the limit of 10. |
| the function total | readability_score | 16 | keep-functions-readable | a readability score of 16 (cognitive complexity; higher is harder to read), over the limit of 15. |
| the function total | line_count | 51 | limit-function-lines | has 51 lines, over the limit of 50. |
| the class Cart | total_complexity | 101 | limit-class-complexity | has a total complexity of 101 (the paths through all its methods, added up), over the limit of 100. |
| the class Cart | method_count | 31 | limit-class-methods | has 31 methods, over the limit of 30. |
| the class Cart | classes_depended_on | 15 | limit-class-coupling | has 15 classes it depends on (coupling between objects), over the limit of 14. |
| the class Cart | methods_set_off | 51 | limit-class-response | has 51 methods one call into it can set off (response for a class), over the limit of 50. |

#### Scenario: Pass a node whose measure is at its limit

*Given* the node of the function total holds paths_through 10
*When* the graph rules run
*Then* limit-paths-through-a-function reports nothing

#### Scenario: Pass a node no read measured

*Given* the node of the function total holds no paths_through
*When* the graph rules run
*Then* limit-paths-through-a-function reports nothing

#### Scenario: Hold a measure to the limit the project sets

*Given* the shop project's config sets the limit of paths_through to 20
  *And* the node of the function total holds paths_through 14
*When* the graph rules run
*Then* limit-paths-through-a-function reports nothing

#### Scenario: Hold an operation's parameters to one limit of 3, in a project that measures its code or not

Decided 2026-11-22: one rule holds parameters, `limit-operation-parameters`, at 3; the rule that held them at 5 is gone. The limit is the shipped limit of `parameters_taken`, which a project's config may change.

*Given* `src/parcels/parcel.py` holds the function send, which takes six parameters, in a project whose config has a `code_measures` section and in one whose config has none
*When* the graph rules run
*Then* limit-operation-parameters reports send in both, saying "takes 6 parameters (maximum 3, excluding self)"
  *And* the metrics group under send shows its parameters with the limit 3, past the limit

#### Scenario Outline: Report a rule's failing example and pass its repaired example

Observed (`cdd_guidance/practices/clean_engineering/measures/code_measures_heavy_spec.py`, with the real tools). The story test runs the five rules on a function or a class whose measure the practice's own reader takes; the three whose measure lizard supplies need the real lizard and run in that heavy spec. The four rules on a module have examples that are small projects of several modules, each module with its card, and run in `code_measures_spec.py` (`limit-modules-importing`, counted by the reader) and in the heavy spec (the three that need lizard or radon).

*Given* the failing example and the repaired example of <rule>
*When* the code measures of each are taken and the graph rules run
*Then* <rule> reports the failing example
  *And* it reports nothing in the repaired example

| rule |
| --- |
| limit-paths-through-a-function |
| keep-functions-readable |
| limit-function-lines |
| limit-class-complexity |
| limit-class-methods |
| keep-class-methods-sharing-data |
| limit-class-coupling |
| limit-class-response |

#### Scenario: Report a function past its limit in the validation report

Observed (`cdd_guidance/practices/clean_engineering/measures/code_measures_heavy_spec.py`).

*Given* the parcels project's config has a `code_measures` section
  *And* `src/parcels/parcel.py` holds the function send, which takes six parameters
*When* Claude Code validates clean-engineering-code on `src/parcels/parcel.py`
*Then* the report holds the limit-operation-parameters violation "takes 6 parameters (maximum 3, excluding self)" in `src/parcels/parcel.py`, beside the other rules
  *And* the node of send is the one reported
