# Code metrics trend, rounds 1–8

How the production code of `ensure-domain-orientation-refactor` changed from the first validation round to now, measured with standard code-measuring tools rather than judged by AI. It sits beside [trend-rounds-1-5.md](trend-rounds-1-5.md), which counts the AI-judged findings, and gives objective numbers to read those findings against.

**How to read the tables.** Each column is the code as it stood when a round began. Next to each number:
- 🟢 means it got **better** since the round before
- 🔴 means it got **worse**
- ⚪ means it stayed **about the same**

No marker means the number is neither good nor bad on its own, such as how many files there are.

## Revisions measured

| Column | Commit | The code as it stood |
|---|---|---|
| Rounds 1–2 | `d6c41b23` | the starting point |
| Round 3 | `42ab935c` | after the round 1–2 fixes |
| Round 4 | `d589b161` | after the round-3 fixes |
| Round 5 | `d71e0b20` | after the round-4 fixes and the single-graph change |
| Round 6 | `b91a73eb` | after the round-5 fixes |
| Round 7 | `c8921451` | after the round-6 fixes |
| Round 8 | `4359b907` | after the round-7 fixes |
| Now | `c5404b75` | after three of the four round-8 fix branches |

The last column is the code after three of the four round-8 fix branches (harness core and actions, space and tools, and the graph fixes). The practices fixes were still being merged.

**What counts as production code.** Python and TypeScript under `harness/`, `cdd_guidance/`, `space/`, `tools/` and `scripts/`. Tests, specs, examples, fixtures, templates, generated installs and retired code are left out. That is about 365–380 Python files and 105 TypeScript files per revision.

## The numbers, round by round

**Size of the Python code**

| What is measured | Rounds 1–2 | Round 3 | Round 4 | Round 5 | Round 6 | Round 7 | Round 8 | Now |
|---|---|---|---|---|---|---|---|---|
| Python files <br>*(no better or worse)* | 363 | 367 | 377 | 364 | 370 | 376 | 379 | 381 |
| Lines of Python code (not counting blanks and comments) <br>*(lower is better)* | 55,479 | 50,390 🟢 | 46,122 🟢 | 44,869 ⚪ | 44,898 ⚪ | 45,480 ⚪ | 45,389 ⚪ | 45,626 ⚪ |
| Classes <br>*(no better or worse)* | 703 | 764 | 867 | 879 | 908 | 936 | 937 | 942 |
| Functions written outside any class, as a share of all functions <br>*(lower is better)* | 17.0% | 16.7% ⚪ | 10.5% 🟢 | 8.9% 🟢 | 8.3% 🟢 | 8.0% 🟢 | 7.8% ⚪ | 7.8% ⚪ |

**How complicated the functions are**

| What is measured | Rounds 1–2 | Round 3 | Round 4 | Round 5 | Round 6 | Round 7 | Round 8 | Now |
|---|---|---|---|---|---|---|---|---|
| Average number of separate paths through a function (each `if`, loop or `and`/`or` adds one) <br>*(lower is better)* | 3.40 | 3.25 🟢 | 3.10 🟢 | 3.02 🟢 | 3.01 ⚪ | 2.99 ⚪ | 2.98 ⚪ | 2.98 ⚪ |
| Functions with more than 10 paths, the usual point where a function needs splitting <br>*(lower is better)* | 189 | 150 🟢 | 117 🟢 | 113 🟢 | 119 🔴 | 120 ⚪ | 121 ⚪ | 124 ⚪ |
| Functions with more than 20 paths <br>*(lower is better)* | 22 | 12 🟢 | 6 🟢 | 3 🟢 | 3 ⚪ | 3 ⚪ | 3 ⚪ | 3 ⚪ |
| Most paths in a single function <br>*(lower is better)* | 50 | 50 ⚪ | 33 🟢 | 26 🟢 | 26 ⚪ | 25 ⚪ | 23 🟢 | 23 ⚪ |
| Functions that are hard to read (a readability score above 15, where deep nesting costs most) <br>*(lower is better)* | 136 | 97 🟢 | 63 🟢 | 59 🟢 | 57 🟢 | 57 ⚪ | 57 ⚪ | 60 🔴 |
| Highest readability score of a single function (lower is easier to read) <br>*(lower is better)* | 105 | 105 ⚪ | 39 🟢 | 37 🟢 | 37 ⚪ | 37 ⚪ | 37 ⚪ | 37 ⚪ |
| Functions longer than 50 lines <br>*(lower is better)* | 26 | 16 🟢 | 5 🟢 | 2 🟢 | 3 ⚪ | 3 ⚪ | 3 ⚪ | 3 ⚪ |
| Functions that take more than 5 parameters <br>*(lower is better)* | 50 | 39 🟢 | 33 🟢 | 35 🔴 | 34 ⚪ | 34 ⚪ | 35 ⚪ | 36 ⚪ |

**How easy the modules are to maintain**

| What is measured | Rounds 1–2 | Round 3 | Round 4 | Round 5 | Round 6 | Round 7 | Round 8 | Now |
|---|---|---|---|---|---|---|---|---|
| Average maintainability score of a module, from 0 to 100 <br>*(higher is better)* | 58.5 | 58.5 ⚪ | 59.5 🟢 | 59.8 ⚪ | 60.7 🟢 | 61.0 ⚪ | 61.4 ⚪ | 61.6 ⚪ |
| Modules with a poor maintainability score (below 20; this mostly means the file is very long) <br>*(lower is better)* | 46 | 40 🟢 | 38 🟢 | 32 🟢 | 31 ⚪ | 31 ⚪ | 31 ⚪ | 31 ⚪ |
| Lines in the longest module <br>*(lower is better)* | 1,917 | 1,875 ⚪ | 1,309 🟢 | 1,226 🟢 | 1,205 ⚪ | 1,229 ⚪ | 1,262 ⚪ | 1,339 🔴 |

**How big and how focused the classes are**

| What is measured | Rounds 1–2 | Round 3 | Round 4 | Round 5 | Round 6 | Round 7 | Round 8 | Now |
|---|---|---|---|---|---|---|---|---|
| Average number of methods in a class <br>*(lower is better)* | 6.55 | 5.94 🟢 | 5.73 🟢 | 5.83 ⚪ | 5.75 ⚪ | 5.74 ⚪ | 5.76 ⚪ | 5.77 ⚪ |
| Most methods in a single class <br>*(lower is better)* | 120 | 73 🟢 | 55 🟢 | 80 🔴 | 71 🟢 | 71 ⚪ | 71 ⚪ | 70 ⚪ |
| Average total complexity of a class (the paths of all its methods added up) <br>*(lower is better)* | 20.9 | 18.2 🟢 | 17.1 🟢 | 17.1 ⚪ | 17.0 ⚪ | 16.8 ⚪ | 16.9 ⚪ | 16.9 ⚪ |
| Total complexity of the most complex class <br>*(lower is better)* | 549 | 323 🟢 | 230 🟢 | 258 🔴 | 227 🟢 | 225 ⚪ | 227 ⚪ | 249 🔴 |
| Classes that do several unrelated jobs (their methods fall into two or more groups that share no data), as a share of classes with methods <br>*(lower is better)* | 60.5% | 53.5% 🟢 | 50.0% 🟢 | 51.2% ⚪ | 51.1% ⚪ | 51.9% ⚪ | 51.8% ⚪ | 52.5% ⚪ |
| Classes that depend on more than 14 other classes <br>*(lower is better)* | 30 | 41 🔴 | 40 ⚪ | 38 🟢 | 43 🔴 | 43 ⚪ | 43 ⚪ | 43 ⚪ |
| Classes where one call can set off more than 50 different methods <br>*(lower is better)* | 78 | 74 🟢 | 78 🔴 | 75 🟢 | 76 ⚪ | 75 ⚪ | 76 ⚪ | 76 ⚪ |
| Deepest chain of classes inheriting from one another <br>*(no better or worse)* | 6 | 6 | 6 | 6 | 6 | 7 | 7 | 7 |

**How the modules depend on one another**

| What is measured | Rounds 1–2 | Round 3 | Round 4 | Round 5 | Round 6 | Round 7 | Round 8 | Now |
|---|---|---|---|---|---|---|---|---|
| Import lines between modules <br>*(no better or worse)* | 948 | 1,091 | 1,136 | 1,104 | 1,170 | 1,208 | 1,219 | 1,237 |
| Most modules that import one single module (the busiest hub) <br>*(lower is better)* | 54 | 57 🔴 | 57 ⚪ | 58 ⚪ | 62 🔴 | 61 ⚪ | 60 ⚪ | 60 ⚪ |
| Folders that many others depend on but that are written as plain concrete code, so every change to them ripples out (a distance above 0.7 from the healthy balance) <br>*(lower is better)* | 18 | 20 🔴 | 22 🔴 | 15 🟢 | 15 ⚪ | 15 ⚪ | 15 ⚪ | 12 🟢 |

**Modules that import each other in a loop (counting only imports that actually run)**

| What is measured | Rounds 1–2 | Round 3 | Round 4 | Round 5 | Round 6 | Round 7 | Round 8 | Now |
|---|---|---|---|---|---|---|---|---|
| Separate loops of modules that import each other <br>*(lower is better)* | 4 | 10 🔴 | 10 ⚪ | 11 ⚪ | 2 🟢 | 0 🟢 | 0 ⚪ | 0 ⚪ |
| Modules caught in one of those loops <br>*(lower is better)* | 86 | 55 🟢 | 46 🟢 | 54 🔴 | 4 🟢 | 0 🟢 | 0 ⚪ | 0 ⚪ |
| Modules in the largest loop <br>*(lower is better)* | 78 | 16 🟢 | 16 ⚪ | 19 🔴 | 2 🟢 | 0 🟢 | 0 ⚪ | 0 ⚪ |
| Separate loops of whole folders that import each other <br>*(lower is better)* | 1 | 3 🔴 | 2 ⚪ | 5 🔴 | 4 ⚪ | 1 🟢 | 1 ⚪ | 1 ⚪ |
| Folders caught in one of those loops <br>*(lower is better)* | 44 | 16 🟢 | 9 🟢 | 22 🔴 | 9 🟢 | 3 🟢 | 3 ⚪ | 3 ⚪ |

**Copied code**

| What is measured | Rounds 1–2 | Round 3 | Round 4 | Round 5 | Round 6 | Round 7 | Round 8 | Now |
|---|---|---|---|---|---|---|---|---|
| Copied lines, as a share of all lines <br>*(lower is better)* | 1.38% | 0.87% 🟢 | 0.48% 🟢 | 0.49% ⚪ | 0.42% 🟢 | 0.42% ⚪ | 0.43% ⚪ | 0.43% ⚪ |
| Copied blocks of code (50 or more tokens, 5 or more lines) <br>*(lower is better)* | 65 | 45 🟢 | 29 🟢 | 29 ⚪ | 24 🟢 | 25 ⚪ | 26 ⚪ | 26 ⚪ |
| Groups of functions that are identical apart from their names <br>*(lower is better)* | 13 | 4 🟢 | 4 ⚪ | 4 ⚪ | 3 ⚪ | 3 ⚪ | 2 ⚪ | 2 ⚪ |
| Helper function names written separately in several modules <br>*(lower is better)* | 31 | 22 🟢 | 14 🟢 | 14 ⚪ | 14 ⚪ | 13 ⚪ | 14 ⚪ | 14 ⚪ |

**Second copies of the same model (shadow models)**

| What is measured | Rounds 1–2 | Round 3 | Round 4 | Round 5 | Round 6 | Round 7 | Round 8 | Now |
|---|---|---|---|---|---|---|---|---|
| Class names defined in more than one module <br>*(lower is better)* | 11 | 6 🟢 | 6 ⚪ | 5 ⚪ | 5 ⚪ | 5 ⚪ | 4 ⚪ | 4 ⚪ |
| Pairs of unrelated classes holding the same fields <br>*(lower is better)* | 4 | 2 🟢 | 3 ⚪ | 2 ⚪ | 1 ⚪ | 1 ⚪ | 3 🔴 | 3 ⚪ |
| Pairs of unrelated classes holding nearly the same fields (80% or more) <br>*(lower is better)* | 5 | 3 🟢 | 3 ⚪ | 2 ⚪ | 1 ⚪ | 1 ⚪ | 3 🔴 | 3 ⚪ |
| TypeScript types named like a Python class, a sign of a copied model <br>*(lower is better)* | 5 | 7 🔴 | 7 ⚪ | 4 🟢 | 4 ⚪ | 4 ⚪ | 4 ⚪ | 4 ⚪ |

**TypeScript (the chat pane, the graph app and the Session Board)**

| What is measured | Rounds 1–2 | Round 3 | Round 4 | Round 5 | Round 6 | Round 7 | Round 8 | Now |
|---|---|---|---|---|---|---|---|---|
| TypeScript files <br>*(no better or worse)* | 107 | 105 | 107 | 105 | 105 | 105 | 105 | 105 |
| Average number of separate paths through a function <br>*(lower is better)* | 2.01 | 2.00 ⚪ | 1.97 ⚪ | 1.97 ⚪ | 1.98 ⚪ | 1.97 ⚪ | 1.97 ⚪ | 1.96 ⚪ |
| Functions with more than 10 paths <br>*(lower is better)* | 15 | 15 ⚪ | 14 ⚪ | 14 ⚪ | 13 ⚪ | 14 ⚪ | 15 ⚪ | 15 ⚪ |
| Separate loops of modules that import each other (this count still includes type-only imports, which never run) <br>*(lower is better)* | 3 | 3 ⚪ | 3 ⚪ | 3 ⚪ | 3 ⚪ | 3 ⚪ | 3 ⚪ | 3 ⚪ |
| Modules in the largest loop <br>*(lower is better)* | 19 | 19 ⚪ | 20 ⚪ | 20 ⚪ | 19 ⚪ | 19 ⚪ | 19 ⚪ | 19 ⚪ |
| Copied blocks of code <br>*(lower is better)* | 3 | 3 ⚪ | 3 ⚪ | 3 ⚪ | 3 ⚪ | 3 ⚪ | 2 ⚪ | 1 ⚪ |


## What the numbers say

- **The functions got much simpler, and stayed that way.**
  - Functions with more than 20 paths fell from 22 to 3.
  - Functions longer than 50 lines fell from 26 to 3.
  - Hard-to-read functions roughly halved.
  - Most of that happened in rounds 1–4. Since then these numbers have stayed low.
- **Copied code is small and still shrinking.** Copied lines went from 1.4% of the code to under half a percent. This catches copies that look alike. Two functions written differently that do the same job are invisible to it, so the AI findings remain the measure for that.
- **Import loops between modules are gone.** At the start, 86 modules sat in loops that imported one another, the largest of them 78 modules. Rounds 3 to 5 still had ten or eleven smaller loops. The round-5 and round-6 fixes removed them all, and since round 7 no module imports another in a loop. One loop of three folders is still left.
- **Classes still do too many unrelated jobs.** About half of the classes with methods fall into two or more groups that share no data. This number has barely moved, and it is the clearest sign of the "bad resource orientation" the AI findings describe. The worst cases are `PracticeGuidance` and the Stories format readers.
- **Dependency on a few hub classes rose and then held.** Classes that depend on more than 14 others grew from 30 to the low forties, as logic moved out of loose functions into classes. The busiest hubs are `Graph` and `PracticeGuidance`. Each has about 70 methods and a total complexity near 200–250.
- **The core framework folders are depended on by everything, yet are written as plain concrete code.** Examples are `harness/agent_tools`, `harness/installation`, `harness/graph` and `harness/mcp`. So any change to them reaches every folder that uses them. This has improved a little, but it is the main structural risk that remains.

## Worst ten, now

**Modules most tangled with others (how many modules import each one, and how many it imports)**

- `harness/graph/graph.py`: imported by 51 imports 18
- `harness/agent_tools/agent_tools.py`: imported by 60 imports 7
- `harness/mcp/mcp_server.py`: imported by 37 imports 17
- `harness/guidance/guidance.py`: imported by 35 imports 16
- `harness/installation/files.py`: imported by 28 imports 6
- `cdd_guidance/practices/clean_engineering/model/base_class_model.py`: imported by 20 imports 11
- `harness/agent_tools/__init__.py`: imported by 29 imports 1
- `cdd_guidance/practices/stories/model/story_model.py`: imported by 21 imports 7
- `harness/annotations/name.py`: imported by 28 imports 0
- `space/session/session.py`: imported by 7 imports 20

**Most complex classes (the paths of all their methods added up; methods; groups of methods that share no data)**

- `harness/graph/graph.py:Graph`: total complexity 249 methods 70 unrelated groups 4
- `harness/guidance/guidance.py:PracticeGuidance`: total complexity 199 methods 70 unrelated groups 12
- `cdd_guidance/practices/stories/model/markdown/nodes.py:MarkdownStoryModel`: total complexity 199 methods 38 unrelated groups 3
- `harness/agent_tools/recipe.py:RecipeExpansion`: total complexity 192 methods 45 unrelated groups 1
- `cdd_guidance/practices/stories/model/markdown/nodes.py:MarkdownScenario`: total complexity 161 methods 32 unrelated groups 3
- `cdd_guidance/practices/stories/model/code_story_model.py:CodeStoryModel`: total complexity 152 methods 56 unrelated groups 5
- `space/kanban/ticket.py:Ticket`: total complexity 143 methods 48 unrelated groups 3
- `harness/graph/graph.py:PracticeNodes`: total complexity 141 methods 47 unrelated groups 1
- `cdd_guidance/practices/clean_engineering/model/graph_reading.py:GraphReading`: total complexity 140 methods 26 unrelated groups 1
- `harness/guidance/guidance.py:FidelityGuidance`: total complexity 138 methods 54 unrelated groups 2

**Classes doing the most unrelated jobs (groups of methods that share no data)**

- `cdd_guidance/practices/stories/model/python/python_story_model.py:PythonStoryModel`: unrelated groups 13 methods 15
- `harness/guidance/guidance.py:PracticeGuidance`: unrelated groups 12 methods 70
- `cdd_guidance/practices/stories/model/brace_story.py:BraceStoryModel`: unrelated groups 9 methods 17
- `harness/agent_tools/agent_tools.py:AgentToolSetOrigin`: unrelated groups 9 methods 11
- `cdd_guidance/practices/ux/model/ux_map.py:UxMap`: unrelated groups 8 methods 17
- `harness/catalog_generator/catalog_generator.py:DetailPage`: unrelated groups 8 methods 8
- `harness/agent_tools/agent_tools.py:AgentToolSet`: unrelated groups 7 methods 32
- `harness/installation/installer.py:Installer`: unrelated groups 7 methods 30
- `harness/guidance/rule.py:RulesCollection`: unrelated groups 7 methods 27
- `cdd_guidance/practices/clean_engineering/model/code_class_model.py:CodeClass`: unrelated groups 7 methods 15

**Classes that depend on the most other classes**

- `harness/graph/practice_rule.py:PracticeGraphRule`: depends on (classes) 70 methods one call can reach 3 total complexity 3
- `harness/graph/graph.py:Graph`: depends on (classes) 64 methods one call can reach 205 total complexity 249
- `harness/graph/graph.py:Node`: depends on (classes) 55 methods one call can reach 65 total complexity 82
- `harness/guidance/guidance.py:PracticeGuidance`: depends on (classes) 44 methods one call can reach 147 total complexity 199
- `harness/graph/rule_context.py:RuleCheckContext`: depends on (classes) 37 methods one call can reach 21 total complexity 20
- `cdd_guidance/practices/clean_engineering/model/base_class_model.py:OoadClass`: depends on (classes) 36 methods one call can reach 70 total complexity 80
- `harness/annotations/name.py:Name`: depends on (classes) 31 methods one call can reach 24 total complexity 22
- `cdd_guidance/practices/clean_engineering/rules/production_code_rule.py:ProductionCodeRule`: depends on (classes) 31 methods one call can reach 3 total complexity 3
- `harness/guidance/guidance.py:FidelityGuidance`: depends on (classes) 28 methods one call can reach 124 total complexity 138
- `cdd_guidance/practices/clean_engineering/model/base_class_model.py:Module`: depends on (classes) 26 methods one call can reach 67 total complexity 46

**Hardest functions to read**

- `cdd_guidance/practices/stories/model/markdown/nodes.py:MarkdownStoryModel.attach_source_locations`: readability score 37
- `cdd_guidance/practices/clean_engineering/model/markdown/markdown_class_model.py:MarkdownOoadClass.read_body`: readability score 33
- `cdd_guidance/practices/clean_engineering/model/markdown/markdown_class_model.py:MarkdownOoadClass._read_operations`: readability score 31
- `cdd_guidance/practices/stories/model/miro/nodes.py:MiroStoryModel.load`: readability score 31
- `cdd_guidance/practices/ux/model/claude_design/story_canvas.py:ClaudeDesignStoryModel._story_entry`: readability score 31
- `cdd_guidance/practices/clean_engineering/model/operation_metrics.py:PythonFunctionBody._raised_or_defaulted`: readability score 29
- `cdd_guidance/practices/clean_engineering/model/markdown/markdown_class_model.py:MarkdownCleanEngineeringModel._apply_module_section`: readability score 28
- `cdd_guidance/practices/clean_engineering/model/markdown/markdown_class_model.py:MarkdownOoadClass._read_properties`: readability score 27
- `cdd_guidance/practices/clean_engineering/model/sketch/sketch_class_model.py:SketchModule._classes_in`: readability score 27
- `cdd_guidance/practices/stories/model/markdown/nodes.py:MarkdownIncrement.parse`: readability score 27

## Tools used

All are free and run offline, from a separate tools folder, not the project's environment:
- **radon:** the maintainability score and each method's paths
- **lizard:** paths, length and parameters, per function, in both Python and TypeScript
- **complexipy:** the readability score, Python only
- **grimp** and **dependency-cruiser:** who imports whom
- **networkx:** finding the import loops
- **jscpd:** copied code
- **cohesion:** a second view of class focus

The measures of classes depending on others and of unrelated jobs are worked out by `measure_revision.py` itself, because no maintained Python tool covers them.

## Measuring a new round

Extract the commit with `git archive <sha>` into an empty folder. Then run:

```
python .context/repo-review/measure_revision.py <folder> --label "round N" --node-tools <folder holding jscpd, dependency-cruiser and typescript> --out roundN.json
```

Run it with a Python that has radon, lizard, complexipy, cohesion, grimp and networkx installed. To rebuild this report from the summaries, run `write_report.py`, beside them.
