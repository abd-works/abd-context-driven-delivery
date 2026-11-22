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

## Story: Record Module Measures As Node Facts

### Evidence

Observed (`cdd_guidance/practices/clean_engineering/measures/code_measures_spec.py`, `cdd_guidance/practices/clean_engineering/measures/code_measures_heavy_spec.py`). The count of defects for each thousand lines of a branch, which the backlog item also lists for a module, is not part of this build.

#### Scenario: Keep a module's measures on its node

*Given* the shop project's config has a `code_measures` section
  *And* radon answers a maintainability score of 62.5 for every file
*When* Claude Code validates clean-engineering-code on `shop/cart.py`
*Then* the node of the module shop holds modules_importing 0 and maintainability_score 62.5

#### Scenario: Read the measures the graph already holds from the graph

*Given* the shop project's config has a `code_measures` section, which names no tool for a module's import loops or the modules it imports
*When* the code measures of `shop/cart.py` are taken
*Then* its import loops are counted from its import_cycles fact and the modules it imports from its dependsOn edges, which every read records, and no tool is asked

#### Scenario: Keep a module's maintainability score from its hardest checked file

Observed (`cdd_guidance/practices/clean_engineering/measures/code_measures_heavy_spec.py`).

*Given* the shop project's config chooses radon for a Python module's maintainability score
*When* the code measures of `catalogue/catalogue.py` are taken with the real tools
*Then* the node of the module catalogue holds a maintainability_score above 0
