# Code metrics trend, rounds 1–9

How the production code of `ensure-domain-orientation-refactor` changed from the first validation round to now, measured with standard code-measuring tools rather than judged by AI. It sits beside [trend-rounds-1-5.md](trend-rounds-1-5.md), which counts the AI-judged findings, and gives objective numbers to read those findings against.

**How to read the tables.** Each column is the code as it stood when a round began. Next to each number:
- 🟢 means it got **better** since the round before
- 🔴 means it got **worse**, by any amount; a slow creep upward is still worse
- ⚪ means it did **not change**

A count shows what it is out of, such as "31 of 381": 31 modules out of 381.

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
| Round 8 end | `c5404b75` | after the round-8 graph hotfix, before the metrics gate |
| Round 9 | `a4440c7f` | after the round-9 fixes, every one passed the metrics gate |

The last column is the code after three of the four round-8 fix branches (harness core and actions, space and tools, and the graph fixes). The practices fixes were still being merged.

**What counts as production code.** Python and TypeScript under `harness/`, `cdd_guidance/`, `space/`, `tools/` and `scripts/`. Tests, specs, examples, fixtures, templates, generated installs and retired code are left out. That is about 365–380 Python files and 105 TypeScript files per revision.

## The numbers, round by round

**Size of the Python code**

| What is measured | Rounds 1–2 | Round 3 | Round 4 | Round 5 | Round 6 | Round 7 | Round 8 | Round 8 end | Round 9 | Target |
|---|---|---|---|---|---|---|---|---|---|---|
| Python files <br>*(no better or worse)* | 363 | 367 | 377 | 364 | 370 | 376 | 379 | 381 | 396 | – |
| Lines of Python code (not counting blanks and comments) <br>*(lower is better)* | 55,479 | 50,390 🟢 | 46,122 🟢 | 44,869 🟢 | 44,898 🔴 | 45,480 🔴 | 45,389 🟢 | 45,626 🔴 | 45,516 🟢 | – |
| Classes <br>*(no better or worse)* | 703 | 764 | 867 | 879 | 908 | 936 | 937 | 942 | 991 | – |
| Functions written outside any class, as a share of all functions <br>*(lower is better)* | 17.0% | 16.7% 🟢 | 10.5% 🟢 | 8.9% 🟢 | 8.3% 🟢 | 8.0% 🟢 | 7.8% 🟢 | 7.8% ⚪ | 8.2% 🔴 | – |

**How complicated the functions are**

| What is measured | Rounds 1–2 | Round 3 | Round 4 | Round 5 | Round 6 | Round 7 | Round 8 | Round 8 end | Round 9 | Target |
|---|---|---|---|---|---|---|---|---|---|---|
| Average number of separate paths through a function (each `if`, loop or `and`/`or` adds one) <br>*(lower is better)* | 3.40 | 3.25 🟢 | 3.10 🟢 | 3.02 🟢 | 3.01 🟢 | 2.99 🟢 | 2.98 🟢 | 2.98 ⚪ | 2.93 🟢 | – |
| Functions with more than 10 paths, the usual point where a function needs splitting <br>*(lower is better)* | 189 of 5,631 | 150 of 5,515 🟢 | 117 of 5,603 🟢 | 113 of 5,675 🟢 | 119 of 5,747 🔴 | 120 of 5,875 🔴 | 121 of 5,895 🔴 | 124 of 5,935 🔴 | 100 of 6,062 🟢 | 60 |
| Functions with more than 20 paths <br>*(lower is better)* | 22 of 5,631 | 12 of 5,515 🟢 | 6 of 5,603 🟢 | 3 of 5,675 🟢 | 3 of 5,747 ⚪ | 3 of 5,875 ⚪ | 3 of 5,895 ⚪ | 3 of 5,935 ⚪ | 3 of 6,062 ⚪ | 0 |
| Most paths in a single function <br>*(lower is better)* | 50 | 50 ⚪ | 33 🟢 | 26 🟢 | 26 ⚪ | 25 🟢 | 23 🟢 | 23 ⚪ | 21 🟢 | – |
| Functions that are hard to read (a readability score above 15, where deep nesting costs most) <br>*(lower is better)* | 136 of 5,631 | 97 of 5,515 🟢 | 63 of 5,603 🟢 | 59 of 5,675 🟢 | 57 of 5,747 🟢 | 57 of 5,875 ⚪ | 57 of 5,895 ⚪ | 60 of 5,935 🔴 | 43 of 6,062 🟢 | 30 |
| Highest readability score of a single function (lower is easier to read) <br>*(lower is better)* | 105 | 105 ⚪ | 39 🟢 | 37 🟢 | 37 ⚪ | 37 ⚪ | 37 ⚪ | 37 ⚪ | 31 🟢 | – |
| Functions longer than 50 lines <br>*(lower is better)* | 26 of 5,631 | 16 of 5,515 🟢 | 5 of 5,603 🟢 | 2 of 5,675 🟢 | 3 of 5,747 🔴 | 3 of 5,875 ⚪ | 3 of 5,895 ⚪ | 3 of 5,935 ⚪ | 3 of 6,062 ⚪ | 0 |
| Functions that take more than 5 parameters <br>*(lower is better)* | 50 of 5,631 | 39 of 5,515 🟢 | 33 of 5,603 🟢 | 35 of 5,675 🔴 | 34 of 5,747 🟢 | 34 of 5,875 ⚪ | 35 of 5,895 🔴 | 36 of 5,935 🔴 | 35 of 6,062 🟢 | 15 |

**How easy the modules are to maintain**

| What is measured | Rounds 1–2 | Round 3 | Round 4 | Round 5 | Round 6 | Round 7 | Round 8 | Round 8 end | Round 9 | Target |
|---|---|---|---|---|---|---|---|---|---|---|
| Average maintainability score of a module, from 0 to 100 <br>*(higher is better)* | 58.5 | 58.5 🔴 | 59.5 🟢 | 59.8 🟢 | 60.7 🟢 | 61.0 🟢 | 61.4 🟢 | 61.6 🟢 | 62.4 🟢 | – |
| Modules with a poor maintainability score (below 20; this mostly means the file is very long) <br>*(lower is better)* | 46 of 363 | 40 of 367 🟢 | 38 of 377 🟢 | 32 of 364 🟢 | 31 of 370 🟢 | 31 of 376 ⚪ | 31 of 379 ⚪ | 31 of 381 ⚪ | 29 of 396 🟢 | 15 |
| Lines in the longest module <br>*(lower is better)* | 1,917 | 1,875 🟢 | 1,309 🟢 | 1,226 🟢 | 1,205 🟢 | 1,229 🔴 | 1,262 🔴 | 1,339 🔴 | 1,018 🟢 | 800 |

**How big and how focused the classes are**

| What is measured | Rounds 1–2 | Round 3 | Round 4 | Round 5 | Round 6 | Round 7 | Round 8 | Round 8 end | Round 9 | Target |
|---|---|---|---|---|---|---|---|---|---|---|
| Average number of methods in a class <br>*(lower is better)* | 6.55 | 5.94 🟢 | 5.73 🟢 | 5.83 🔴 | 5.75 🟢 | 5.74 🟢 | 5.76 🔴 | 5.77 🔴 | 5.58 🟢 | – |
| Most methods in a single class <br>*(lower is better)* | 120 | 73 🟢 | 55 🟢 | 80 🔴 | 71 🟢 | 71 ⚪ | 71 ⚪ | 70 🟢 | 51 🟢 | 30 |
| Average total complexity of a class (the paths of all its methods added up) <br>*(lower is better)* | 20.9 | 18.2 🟢 | 17.1 🟢 | 17.1 🟢 | 17.0 🟢 | 16.8 🟢 | 16.9 🔴 | 16.9 🔴 | 16.0 🟢 | 15 |
| Total complexity of the most complex class <br>*(lower is better)* | 549 | 323 🟢 | 230 🟢 | 258 🔴 | 227 🟢 | 225 🟢 | 227 🔴 | 249 🔴 | 192 🟢 | 100 |
| Classes that do several unrelated jobs (their methods fall into two or more groups that share no data), as a share of classes with methods <br>*(lower is better)* | 60.5% | 53.5% 🟢 | 50.0% 🟢 | 51.2% 🔴 | 51.1% 🟢 | 51.9% 🔴 | 51.8% 🟢 | 52.5% 🔴 | 44.8% 🟢 | 40.0% |
| Classes that depend on more than 14 other classes <br>*(lower is better)* | 30 of 703 | 41 of 764 🔴 | 40 of 867 🟢 | 38 of 879 🟢 | 43 of 908 🔴 | 43 of 936 ⚪ | 43 of 937 ⚪ | 43 of 942 ⚪ | 42 of 991 🟢 | 25 |
| Classes where one call can set off more than 50 different methods <br>*(lower is better)* | 78 of 703 | 74 of 764 🟢 | 78 of 867 🔴 | 75 of 879 🟢 | 76 of 908 🔴 | 75 of 936 🟢 | 76 of 937 🔴 | 76 of 942 ⚪ | 76 of 991 ⚪ | 50 |
| Deepest chain of classes inheriting from one another <br>*(no better or worse)* | 6 | 6 | 6 | 6 | 6 | 7 | 7 | 7 | 7 | – |

**How the modules depend on one another**

| What is measured | Rounds 1–2 | Round 3 | Round 4 | Round 5 | Round 6 | Round 7 | Round 8 | Round 8 end | Round 9 | Target |
|---|---|---|---|---|---|---|---|---|---|---|
| Import lines between modules <br>*(no better or worse)* | 948 | 1,091 | 1,136 | 1,104 | 1,170 | 1,208 | 1,219 | 1,237 | 1,305 | – |
| Most modules that import one single module (the busiest hub) <br>*(lower is better)* | 54 | 57 🔴 | 57 ⚪ | 58 🔴 | 62 🔴 | 61 🟢 | 60 🟢 | 60 ⚪ | 60 ⚪ | 40 |
| Folders far from the abstractness and instability balance (a distance above 0.7). It counts only abstract classes, so it misses this framework's annotations and registration; for information only <br>*(lower is better)* | 18 of 107 | 20 of 109 🔴 | 22 of 108 🔴 | 15 of 100 🟢 | 15 of 99 ⚪ | 15 of 100 ⚪ | 15 of 100 ⚪ | 12 of 100 🟢 | 12 of 101 ⚪ | – |

**Modules that import each other in a loop (counting only imports that actually run)**

| What is measured | Rounds 1–2 | Round 3 | Round 4 | Round 5 | Round 6 | Round 7 | Round 8 | Round 8 end | Round 9 | Target |
|---|---|---|---|---|---|---|---|---|---|---|
| Separate loops of modules that import each other <br>*(lower is better)* | 4 | 10 🔴 | 10 ⚪ | 11 🔴 | 2 🟢 | 0 🟢 | 0 ⚪ | 0 ⚪ | 0 ⚪ | – |
| Modules caught in one of those loops <br>*(lower is better)* | 86 of 360 | 55 of 364 🟢 | 46 of 374 🟢 | 54 of 361 🔴 | 4 of 367 🟢 | 0 of 373 🟢 | 0 of 376 ⚪ | 0 of 378 ⚪ | 0 of 393 ⚪ | ✅ 0 |
| Modules in the largest loop <br>*(lower is better)* | 78 | 16 🟢 | 16 ⚪ | 19 🔴 | 2 🟢 | 0 🟢 | 0 ⚪ | 0 ⚪ | 0 ⚪ | – |
| Separate loops of whole folders that import each other <br>*(lower is better)* | 1 | 3 🔴 | 2 🟢 | 5 🔴 | 4 🟢 | 1 🟢 | 1 ⚪ | 1 ⚪ | 0 🟢 | – |
| Folders caught in one of those loops <br>*(lower is better)* | 44 of 107 | 16 of 109 🟢 | 9 of 108 🟢 | 22 of 100 🔴 | 9 of 99 🟢 | 3 of 100 🟢 | 3 of 100 ⚪ | 3 of 100 ⚪ | 0 of 101 🟢 | ✅ 0 |

**Copied code**

| What is measured | Rounds 1–2 | Round 3 | Round 4 | Round 5 | Round 6 | Round 7 | Round 8 | Round 8 end | Round 9 | Target |
|---|---|---|---|---|---|---|---|---|---|---|
| Copied lines, as a share of all lines <br>*(lower is better)* | 1.38% | 0.87% 🟢 | 0.48% 🟢 | 0.49% 🔴 | 0.42% 🟢 | 0.42% ⚪ | 0.43% 🔴 | 0.43% ⚪ | 0.26% 🟢 | ✅ 0.30% |
| Copied blocks of code (50 or more tokens, 5 or more lines) <br>*(lower is better)* | 65 | 45 🟢 | 29 🟢 | 29 ⚪ | 24 🟢 | 25 🔴 | 26 🔴 | 26 ⚪ | 18 🟢 | 15 |
| Groups of functions that are identical apart from their names <br>*(lower is better)* | 13 | 4 🟢 | 4 ⚪ | 4 ⚪ | 3 🟢 | 3 ⚪ | 2 🟢 | 2 ⚪ | 1 🟢 | 0 |
| Helper function names written separately in several modules <br>*(lower is better)* | 31 | 22 🟢 | 14 🟢 | 14 ⚪ | 14 ⚪ | 13 🟢 | 14 🔴 | 14 ⚪ | 12 🟢 | 5 |

**Second copies of the same model (shadow models)**

| What is measured | Rounds 1–2 | Round 3 | Round 4 | Round 5 | Round 6 | Round 7 | Round 8 | Round 8 end | Round 9 | Target |
|---|---|---|---|---|---|---|---|---|---|---|
| Class names defined in more than one module <br>*(lower is better)* | 11 | 6 🟢 | 6 ⚪ | 5 🟢 | 5 ⚪ | 5 ⚪ | 4 🟢 | 4 ⚪ | 2 🟢 | 0 |
| Pairs of unrelated classes holding the same fields <br>*(lower is better)* | 4 | 2 🟢 | 3 🔴 | 2 🟢 | 1 🟢 | 1 ⚪ | 3 🔴 | 3 ⚪ | 2 🟢 | 0 |
| Pairs of unrelated classes holding nearly the same fields (80% or more) <br>*(lower is better)* | 5 | 3 🟢 | 3 ⚪ | 2 🟢 | 1 🟢 | 1 ⚪ | 3 🔴 | 3 ⚪ | 2 🟢 | – |
| TypeScript types named like a Python class, a sign of a copied model <br>*(lower is better)* | 5 | 7 🔴 | 7 ⚪ | 4 🟢 | 4 ⚪ | 4 ⚪ | 4 ⚪ | 4 ⚪ | 4 ⚪ | – |

**TypeScript (the chat pane, the graph app and the CDD Kanban)**

| What is measured | Rounds 1–2 | Round 3 | Round 4 | Round 5 | Round 6 | Round 7 | Round 8 | Round 8 end | Round 9 | Target |
|---|---|---|---|---|---|---|---|---|---|---|
| TypeScript files <br>*(no better or worse)* | 107 | 105 | 107 | 105 | 105 | 105 | 105 | 105 | 105 | – |
| Average number of separate paths through a function <br>*(lower is better)* | 2.01 | 2.00 🟢 | 1.97 🟢 | 1.97 ⚪ | 1.98 🔴 | 1.97 🟢 | 1.97 ⚪ | 1.96 🟢 | 1.97 🔴 | – |
| Functions with more than 10 paths <br>*(lower is better)* | 15 | 15 ⚪ | 14 🟢 | 14 ⚪ | 13 🟢 | 14 🔴 | 15 🔴 | 15 ⚪ | 15 ⚪ | – |
| Separate loops of modules that import each other (this count still includes type-only imports, which never run) <br>*(lower is better)* | 3 | 3 ⚪ | 3 ⚪ | 3 ⚪ | 3 ⚪ | 3 ⚪ | 3 ⚪ | 3 ⚪ | 2 🟢 | – |
| Modules in the largest loop <br>*(lower is better)* | 19 | 19 ⚪ | 20 🔴 | 20 ⚪ | 19 🟢 | 19 ⚪ | 19 ⚪ | 19 ⚪ | 19 ⚪ | – |
| Copied blocks of code <br>*(lower is better)* | 3 | 3 ⚪ | 3 ⚪ | 3 ⚪ | 3 ⚪ | 3 ⚪ | 2 🟢 | 1 🟢 | 1 ⚪ | – |


## Targets, and the gate that keeps us moving towards them

The **Target** column is where the refactor is heading, and ✅ marks a target already met. The targets come from common review limits and from where this code already stands:
- no function above 20 paths or 50 lines
- no class above 100 total complexity or 30 methods
- no module above 800 lines
- no import loops
- about half of today's count of complex, hard-to-read and many-parameter functions

They are low enough to remove the worst problems, and reachable in a few rounds.

From round 9, every change must pass the **metrics gate** (`metrics_gate.py`, rule `cdd_guidance/rules/metrics-gate.md`) before it is committed:
- The gate measures the code before and after the change.
- It fails if any metric got worse by any amount.
- It names each function, class or module the change pushed past a limit.

Rounds 5 to 8 slid because nothing measured the code between rounds. Run on the round-8 changes, the gate names every regression, for example:
- `Graph._take`, new with 18 paths
- `PracticeChanges.between`, new with 20 paths
- `GraphReading`, from 133 to 140 total complexity

## What the numbers say

- **Round 9 reversed the creep.** It was the first round in which every fix had to pass the metrics gate, and 16 of the 23 guarded numbers improved while none got worse (measured against the round-9 start, 5f36e6a2; the changes below are from the end of round 8):
  - functions with more than 10 paths: 124 → 100
  - hard-to-read functions: 60 → 43
  - the most complex class: 249 → 192. `Graph` went from 249 to 57 and `PracticeGuidance` from 199 to 80, each split into parts it holds; the most complex class is now `RecipeExpansion`, which is one job.
  - most methods in one class: 70 → 51
  - the longest module: 1,339 → 1,018 lines
  - classes doing several unrelated jobs: 52.5% → 44.8%
  - folders caught in an import loop: 3 → 0
  - copied lines: 0.43% → 0.26%, under the target
- **The functions got much simpler, and stayed that way.**
  - Functions with more than 20 paths fell from 22 to 3.
  - Functions longer than 50 lines fell from 26 to 3.
  - Hard-to-read functions roughly halved.
  - Most of that happened in rounds 1–4. Since then these numbers have stayed low.
- **But since round 5, several numbers have crept back the wrong way, one or two at a time.** Each round's fixes added a few complex functions and grew the biggest classes, and nothing measured them:
  - functions with more than 10 paths: 113 → 124
  - hard-to-read functions: 57 → 60
  - functions taking more than 5 parameters: 33 → 36
  - the longest module: 1,205 → 1,339 lines
  - the most complex class, `Graph`: 227 → 249

  The metrics gate exists to stop this creep.
- **Copied code is small and still shrinking.** Copied lines went from 1.4% of the code to under half a percent. This catches copies that look alike. Two functions written differently that do the same job are invisible to it, so the AI findings remain the measure for that.
- **Import loops between modules are gone.** At the start, 86 modules sat in loops that imported one another, the largest of them 78 modules. Rounds 3 to 5 still had ten or eleven smaller loops. The round-5 and round-6 fixes removed them all, and since round 7 no module imports another in a loop. One loop of three folders is still left.
- **Classes still do too many unrelated jobs.** About half of the classes with methods fall into two or more groups that share no data. This number has barely moved, and it is the clearest sign of the "bad resource orientation" the AI findings describe. The worst cases are `PracticeGuidance` and the Stories format readers.
- **Dependency on a few hub classes rose and then held.** Classes that depend on more than 14 others grew from 30 to the low forties, as logic moved out of loose functions into classes. The busiest hubs are `Graph` and `PracticeGuidance`. Each has about 70 methods and a total complexity near 200–250.
- **The "distance from the healthy balance" number misreads this framework, so it is reported but not used as a goal.** The measure (Robert Martin's abstractness and instability) counts a folder as abstract only by its abstract classes. This framework's extension points are not abstract classes: toolsets, tools and guidance are declared with decorator annotations (`@agent_toolset`, `@agent_tool`, `@agent_instructions`), practices extend the one `PracticeGuidance` base, and code built on the framework registers with it instead of importing it. That is the stable, dependency-inverted shape the measure looks for, but the tool cannot see it, so `harness/annotations`, `harness/agent_tools` and the other framework folders score as plain concrete code. The real risk the measure aims at, a change to a widely used folder reaching its users, is tracked better by the coupling numbers (classes depending on more than 14 others, and the most modules importing one module).

## Worst ten, now

**Modules most tangled with others (how many modules import each one, and how many it imports)**

- `harness/graph/graph.py`: imported by 55 imports 19
- `harness/agent_tools/agent_tools.py`: imported by 60 imports 7
- `harness/mcp/mcp_server.py`: imported by 37 imports 17
- `harness/guidance/guidance.py`: imported by 35 imports 17
- `cdd_guidance/practices/clean_engineering/model/base_class_model.py`: imported by 24 imports 12
- `harness/installation/files.py`: imported by 28 imports 6
- `harness/agent_tools/__init__.py`: imported by 29 imports 1
- `harness/annotations/name.py`: imported by 29 imports 0
- `space/session/session.py`: imported by 7 imports 20
- `cdd_guidance/practices/stories/model/story_model.py`: imported by 20 imports 7

**Most complex classes (the paths of all their methods added up; methods; groups of methods that share no data)**

- `harness/agent_tools/recipe.py:RecipeExpansion`: total complexity 192 methods 45 unrelated groups 1
- `harness/guidance/guidance.py:FidelityGuidance`: total complexity 131 methods 51 unrelated groups 2
- `harness/installation/files.py:FileInstallation`: total complexity 129 methods 30 unrelated groups 1
- `cdd_guidance/practices/ddd/model/markdown/nodes.py:MarkdownAggregate`: total complexity 129 methods 26 unrelated groups 1
- `cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py:ArrowRouter`: total complexity 115 methods 22 unrelated groups 1
- `cdd_guidance/practices/clean_engineering/model/markdown/markdown_class_model.py:MarkdownOoadClass`: total complexity 104 methods 17 unrelated groups 2
- `harness/installation/language_adapter.py:TypeScriptToolset`: total complexity 101 methods 37 unrelated groups 1
- `cdd_guidance/practices/clean_engineering/model/c_family_parse.py:CFamilyParse`: total complexity 98 methods 22 unrelated groups 1
- `cdd_guidance/practices/stories/model/drawio/nodes.py:DrawIOStoryModel`: total complexity 97 methods 18 unrelated groups 4
- `harness/graph/graph.py:Filter`: total complexity 96 methods 28 unrelated groups 1

**Classes doing the most unrelated jobs (groups of methods that share no data)**

- `harness/agent_tools/agent_tools.py:AgentToolSetOrigin`: unrelated groups 9 methods 11
- `cdd_guidance/practices/ux/model/ux_map.py:UxMap`: unrelated groups 8 methods 16
- `harness/catalog_generator/catalog_generator.py:DetailPage`: unrelated groups 8 methods 8
- `harness/guidance/guidance.py:PracticeGuidance`: unrelated groups 7 methods 29
- `harness/agent_tools/agent_tools.py:AgentToolSet`: unrelated groups 7 methods 28
- `harness/installation/installer.py:Installer`: unrelated groups 7 methods 27
- `cdd_guidance/practices/clean_engineering/model/code_class_model.py:CodeClass`: unrelated groups 7 methods 15
- `harness/guidance/rule.py:RulesCollection`: unrelated groups 7 methods 15
- `harness/agent_tools/agent_tools.py:AgentInstructions`: unrelated groups 7 methods 12
- `cdd_guidance/practices/clean_engineering/model/drawio/page/drawio_page.py:DrawioPage`: unrelated groups 7 methods 9

**Classes that depend on the most other classes**

- `harness/graph/practice_rule.py:PracticeGraphRule`: depends on (classes) 70 methods one call can reach 3 total complexity 3
- `harness/graph/graph.py:Graph`: depends on (classes) 60 methods one call can reach 90 total complexity 57
- `harness/graph/graph.py:Node`: depends on (classes) 54 methods one call can reach 64 total complexity 82
- `harness/guidance/guidance.py:PracticeGuidance`: depends on (classes) 44 methods one call can reach 75 total complexity 80
- `harness/graph/rule_context.py:RuleCheckContext`: depends on (classes) 36 methods one call can reach 21 total complexity 20
- `cdd_guidance/practices/clean_engineering/rules/production_code_rule.py:ProductionCodeRule`: depends on (classes) 31 methods one call can reach 3 total complexity 3
- `harness/annotations/name.py:Name`: depends on (classes) 30 methods one call can reach 24 total complexity 22
- `harness/guidance/guidance.py:FidelityGuidance`: depends on (classes) 28 methods one call can reach 114 total complexity 131
- `cdd_guidance/practices/clean_engineering/model/base_class_model.py:OoadClass`: depends on (classes) 27 methods one call can reach 77 total complexity 87
- `cdd_guidance/practices/clean_engineering/model/operation.py:Operation`: depends on (classes) 25 methods one call can reach 76 total complexity 59

**Hardest functions to read**

- `cdd_guidance/practices/clean_engineering/model/markdown/markdown_class_model.py:MarkdownOoadClass.read_body`: readability score 31
- `cdd_guidance/practices/clean_engineering/model/markdown/markdown_class_model.py:MarkdownOoadClass._read_operations`: readability score 31
- `cdd_guidance/practices/stories/model/miro/nodes.py:MiroStoryModel.load`: readability score 31
- `cdd_guidance/practices/ux/model/claude_design/story_canvas.py:ClaudeDesignStoryModel._story_entry`: readability score 31
- `cdd_guidance/practices/clean_engineering/model/markdown/markdown_class_model.py:MarkdownOoadClass._read_properties`: readability score 27
- `cdd_guidance/practices/clean_engineering/model/sketch/sketch_class_model.py:SketchModule._classes_in`: readability score 27
- `scripts/instances.py:RepoProcesses._fetch_ping`: readability score 26
- `cdd_guidance/practices/clean_engineering/model/class_channel.feature.py:check_properties`: readability score 25
- `scripts/instances.py:HttpPing.run`: readability score 25
- `cdd_guidance/practices/stories/model/markdown/nodes.py:MarkdownIncrement.parse`: readability score 23

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

Run it with a Python that has radon, lizard, complexipy, cohesion, grimp and networkx installed. The gate, `metrics_gate.py`, uses the same measurement.
