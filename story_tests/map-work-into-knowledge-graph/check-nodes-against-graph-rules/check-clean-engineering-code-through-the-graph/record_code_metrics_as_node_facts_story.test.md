---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Check Clean Engineering Code Through The Graph

Story map: [Check Clean Engineering Code Through The Graph](../../../../.context/story-map.md#e-check-clean-engineering-code-through-the-graph). Session release-1-2-fixes.

**Evidence mode.** Every scenario here is *Observed*: it holds today and names the spec that runs it. `cdd_guidance/practices/clean_engineering/measures/code_measures_spec.py` stands the outside tools in at the one place the practice asks a tool; `cdd_guidance/practices/clean_engineering/measures/code_measures_heavy_spec.py` runs the real tools, lizard and radon. Built on 2026-11-22 from the person's five decisions of that day, written in `.sessions/_backlog/measure-code-on-the-model.md`.

### Domain terms

- ++code measure++ — one number about a function, a class or a module, kept as a fact on its node: the paths through a function (cyclomatic complexity), its readability score (cognitive complexity), its lines of code, its parameters; a class's total complexity, methods, classes depended on, and groups of methods that share no data; a module's importing and imported modules, import loops, maintainability score, copied function bodies, abstractness and instability.
- ++chosen tool++ — the tool a project's `.context/config.json` names, under `code_measures`, to take one measure in one language. `not measured` there is a decision to leave the measure out; a missing entry is a choice nobody made.
- ++checked file++ — a file a validate names in `paths`.

> In steps: the shop project holds `shop/cart.py`, whose class Cart has the function total.

## Story: Record Code Metrics As Node Facts

### Evidence

Observed (`cdd_guidance/practices/clean_engineering/measures/code_measures_spec.py`, `cdd_guidance/practices/clean_engineering/measures/code_measures_heavy_spec.py`).

#### Scenario: Keep a function's measures on its node

*Given* the shop project's config has a `code_measures` section
  *And* lizard answers 14 paths and a readability score of 3 for every function
*When* Claude Code validates clean-engineering-code on `shop/cart.py`
*Then* the node of the function total holds paths_through 14 and readability_score 3, and its lines and its parameters are read from line_count and its parameter nodes, which every read keeps

#### Scenario: Keep a class's measures on its node

*Given* the shop project's config has a `code_measures` section
  *And* lizard answers a total complexity of 40 for every class
*When* Claude Code validates clean-engineering-code on `shop/cart.py`
*Then* the node of the class Cart holds total_complexity 40, method_count 4, classes_depended_on 0 and unshared_method_groups 2

#### Scenario: Take a measure with the tool chosen for its language

Observed (`cdd_guidance/practices/clean_engineering/measures/code_measures_heavy_spec.py`).

*Given* the shop project's config has a `code_measures` section
  *And* the Catalogue class's priceOf, in `catalogue/catalogue.<extension>`, has eleven branches
*When* the code measures of that file are taken
*Then* the node of the function holds paths_through 12, as lizard counts them

| language | extension |
| --- | --- |
| Python | py |
| TypeScript | ts |

#### Scenario: Report code in a language nobody chose a tool for

*Given* the shop project's config has a `code_measures` section, which chooses no tool for JavaScript
*When* Claude Code validates clean-engineering-code on `catalogue/catalogue.js`
*Then* limit-paths-through-a-function reports the file once, naming the measure paths_through, the language javascript, and the config file to choose a tool in

#### Scenario: Report a chosen tool that is not installed

*Given* the shop project's config chooses lizard for a Python function's paths
  *And* lizard is not installed
*When* the code measures of `shop/cart.py` are taken
*Then* limit-paths-through-a-function reports the file once, naming the tool lizard, the measure, and the command that installs it

#### Scenario: Leave out a measure the project says is not measured

*Given* the shop project's config writes `not measured` for copied code blocks in Python
*When* the code measures of `shop/cart.py` are taken
*Then* the node of the module shop holds no copied_code_blocks

#### Scenario: Measure only the files a read names

*Given* the shop project's config has a `code_measures` section
*When* the whole working copy of the shop project is loaded into the graph
*Then* no node holds a code measure

#### Scenario: Take no measure in a project that chose no tools

*Given* the shop project's config has no `code_measures` section
*When* Claude Code validates clean-engineering-code on `shop/cart.py`
*Then* no node holds a code measure
  *And* the validate reports the other rules as before
