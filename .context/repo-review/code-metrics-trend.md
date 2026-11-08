# Code metrics trend, rounds 1–5

How the production code of `ensure-domain-orientation-refactor` changed across the five validation rounds, measured with standard code metrics and real measurement tools. It sits beside `trend-rounds-1-5.md`, which counts the AI-judged findings; this file gives the objective numbers to read those findings against.

## Revisions measured

| Revision | Input to | What happened before it |
|---|---|---|
| `d6c41b23` | rounds 1 and 2 | the starting point |
| `42ab935c` | round 3 | fixes from rounds 1–2 |
| `d589b161` | round 4 (relationship review) | fixes from round 3 |
| `d71e0b20` | round 5 (170 findings) | fixes from round 4, and the single-graph change |
| `9821ec3f` | round 6, not yet run | the round-5 fixes; the tip of `ensure-domain-orientation-refactor` on 2026-11-08 |

Each revision was extracted with `git archive <sha>` into its own temporary folder; no checkout was switched.

**What counts as production code.** Python and TypeScript under `harness/`, `cdd_guidance/`, `space/`, `tools/` and `scripts/`. Left out, as the brief asked: `*_spec.py`, `*_heavy_spec.py`, `_examples/`, `fixtures/`, `node_modules/`, `.claude/`, `.cursor/`, `catalog/`, `.sessions/`, `retired/`. Also left out, because they are tests or scaffolds rather than shipped code: `.retired/`, `.context/`, `templates/` (scaffolds with `{epicSlug}` placeholders), `test/`, `tests/`, `test-utils/`, `conftest.py`, `*.test.*`, `*.spec.*`, `*.story.*.py` and `*.d.ts`. That leaves 363–377 Python files (45–55 thousand source lines) and 105–107 TypeScript files (8.5 thousand lines) per revision.

## The metrics, and why each one

| Metric | What it measures | Why it is here | Source |
|---|---|---|---|
| **Afferent coupling (Ca)** and **efferent coupling (Ce)** | For a package (here, a folder of modules): how many other packages depend on it (Ca), and how many it depends on (Ce) | Ca says how much breaks when the package changes; Ce says how many reasons it has to change | Martin, *Agile Software Development: Principles, Patterns, and Practices* (2002), ch. 20 |
| **Instability** I = Ce / (Ca + Ce) | 0 = everything depends on it and it depends on nothing; 1 = the reverse | Dependencies should point toward stable packages (the Stable Dependencies Principle) | Martin, ibid. |
| **Abstractness** A and **distance from the main sequence** D = \|A + I − 1\| | A is the share of abstract classes (ABC, Protocol, abstract methods). D measures how far a package is from the balance "stable packages are abstract, unstable ones are concrete" | D near 1 with I near 0 is the **zone of pain**: a concrete package that everything depends on, so every change to it reaches all its dependants | Martin, ibid. |
| **Cyclomatic complexity** (CCN) | The number of independent paths through a function (decisions + 1) | The minimum number of tests to cover a function; above 10 is the usual review threshold | McCabe, "A Complexity Measure", *IEEE TSE* SE-2(4), 1976 |
| **Cognitive complexity** | How hard a function is to read: nesting and breaks in linear flow cost more than flat branches | Tracks what a reader finds hard better than CCN does; above 15 is SonarSource's default threshold | Campbell, *Cognitive Complexity: A new way of measuring understandability*, SonarSource white paper, 2018 |
| **Maintainability index** (MI) | A formula over Halstead volume, cyclomatic complexity, lines of code and comment ratio, normalised to 0–100 | A single per-module score; below 20 is the usual warning band. It is dominated by module size | Oman & Hagemeister (1992); Coleman et al., *IEEE Computer* 27(8), 1994; SEI *C4 Software Technology Reference Guide*, 1997 |
| **Class size**, **methods per class** (NOM) and **weighted methods per class** (WMC = sum of the methods' CCN) | How big and how complex a class is | Large WMC marks a class that has taken on too many responsibilities (a *god class*) | Chidamber & Kemerer, "A Metrics Suite for Object Oriented Design", *IEEE TSE* 20(6), 1994 |
| **Depth of inheritance** (DIT) and **number of children** (NOC) | How deep a class sits in its inheritance tree, and how many classes extend it | Deep trees spread one behaviour over many files; many children make the base class hard to change | Chidamber & Kemerer, ibid. |
| **Coupling between objects** (CBO) | The number of other classes in the repository this class uses or is used by | High CBO means a change reaches many classes; above 14 is a commonly quoted review threshold | Chidamber & Kemerer, ibid. |
| **Response for a class** (RFC) | Methods of the class plus the distinct methods and functions they call | How much code can run in answer to one message; above 50 is a commonly quoted review threshold | Chidamber & Kemerer, ibid. |
| **Lack of cohesion** (LCOM4) | The number of separate groups of methods, where two methods are in one group if they share an attribute or one calls the other | LCOM4 = 1 is one responsibility; 2 or more means the class could be split into that many classes | Hitz & Montazeri, "Measuring Coupling and Cohesion in Object-Oriented Systems", 1995 (refining Chidamber & Kemerer's LCOM) |
| **Function length** (NLOC) and **parameter count** | Non-comment lines in a function, and its parameters (without `self`/`cls`) | Long functions and long parameter lists are the commonest readability smells | Fowler, *Refactoring* (1999), "Long Method", "Long Parameter List" |
| **Duplication** | Duplicated lines as a share of all lines, and the number of clones (token sequences of 50+ tokens and 5+ lines found twice). Also exact function clones (Type-2: same body once identifiers are renamed) | Copied code has to be fixed in every copy | Roy & Cordy, *A Survey on Software Clone Detection Research*, Queen's University TR 2007-541 |
| **Import cycles** | Strongly connected components (SCCs) of the module import graph: their count and their size | Every module in an SCC depends on every other, so none can be understood, tested or changed alone (the Acyclic Dependencies Principle) | Martin, ibid.; Tarjan (1972) for SCCs |

Import cycles are counted three ways, because Python lets an import be deferred:
- **all imports**, including those under `if TYPE_CHECKING:`
- **runtime imports**, without the `TYPE_CHECKING` ones but with imports written inside functions. This is the design-level dependency: the module still needs the other at run time.
- **import-time imports**, only the imports a module runs when it is itself imported. A cycle here fails or leaves a module half-initialised.

### Which metrics speak to the loop's three goal classes

`trend-rounds-1-5.md` sets the loop's goal: cut the findings for bad resource orientation, shadow models and duplicated functions from 163 to below 30. The metrics that bear on each class:

| Goal class | Metrics that measure it | What they can and cannot see |
|---|---|---|
| **Bad resource orientation** (concern 5, wrong-shape relationships; concern 9, one file with several owners) | share of module-level functions against methods; LCOM4 > 1; CBO > 14 and RFC > 50; fan-in of the hub modules; packages with D > 0.7; classes per module; import cycles | They see behaviour living outside classes, classes with several responsibilities, and dependencies pointing the wrong way. They cannot judge whether a relationship has the right *meaning* |
| **Shadow models** (concern 2, second object models) | class names defined in several modules; classes in different files, with no common ancestor, that hold the same (or 80% the same) fields; TypeScript types named like Python classes | They catch a mechanical copy of a model. A second model of the same concept under different names is invisible to them |
| **Duplicated functions** (concern 1; concern 12, rules decided in both TypeScript and Python) | jscpd duplicated lines and clones; exact function clones; module-level function names defined in several modules | They catch copied text and drifted copies of a helper. A rule written once in Python and again in TypeScript is invisible to them |

## Tool choice

All tools are free and run offline. They were installed into a separate venv and a separate `node_modules` in the scratch folder, not into the project's `.venv`.

| Need | Candidates compared | Chosen | Why |
|---|---|---|---|
| Python CCN, MI, raw size | radon, lizard, wily | **radon 6.0** for MI and per-method CCN (WMC); **lizard 1.25** for per-function CCN, NLOC and parameters | radon implements the SEI MI formula. lizard gives the same per-function numbers for Python and TypeScript, so the two languages compare. wily only tracks radon's metrics through git history and works on a live checkout, which the brief rules out |
| Cognitive complexity | complexipy, flake8-cognitive-complexity | **complexipy 8.3** (Python only) | Implements the SonarSource definition and has a Python API. TypeScript would need `eslint-plugin-sonarjs` and an ESLint config per app, so it is left out |
| Python import graph | grimp, import-linter, pydeps | **grimp 3.19** | Static, has an API, separates `TYPE_CHECKING` imports and reports each import's line. import-linter is built on grimp and only adds contracts; pydeps draws graphs rather than returning them |
| TypeScript import graph | dependency-cruiser, madge | **dependency-cruiser 16** | Resolves TypeScript, including type-only imports, and writes JSON |
| Duplication | jscpd, pylint `duplicate-code` | **jscpd 4.3** | One tool for both languages, with a JSON report. pylint covers Python only and is much slower |
| Cohesion | cohesion, own LCOM4 | **cohesion 1.2** for its per-class percentage, and LCOM4 computed in the script | cohesion's percentage is not LCOM4, and it goes above 100 for a few classes, so only its median is reported |
| Chidamber & Kemerer suite (CBO, RFC, DIT, NOC) | ckjm (Java only), no maintained Python tool | **computed in the script with the standard-library `ast` module** | Class references are resolved through each module's imports, so a class is matched by its real module, not by name |
| Cycles | networkx | **networkx 3.7** | Tarjan's strongly connected components over the grimp and dependency-cruiser graphs |

The script is `measure_revision.py`, beside this file. It copies a checkout's production files into a short temporary folder, so that every tool sees the same files (and Windows path lengths stay short), runs every tool, and writes one JSON summary. A revision takes about 15 seconds.

**Known limits.**
- CBO counts inheritance in both directions, as Chidamber & Kemerer do. So `PracticeGraphRule`, the base of about a hundred graph rules, has CBO ≈ 100 and RFC 3; it is not a hub of behaviour.
- Imports made through `importlib` strings are invisible to grimp, so the harness's reach into the practices (round-5 finding 14) is not in the coupling numbers.
- MI is 0 for any module above roughly 500 lines whatever its quality, so MI here mostly ranks module size.
- grimp skips the two `*.feature.py` modules, whose file names contain a dot; they are still in every other metric. `space/kanban/story_test.py`, a story-test helper, is counted as production.

## Headline numbers per revision

Python, production code only.

| Metric | `d6c41b23` (R1–2) | `42ab935c` (R3) | `d589b161` (R4) | `d71e0b20` (R5) | `9821ec3f` (after R5) |
|---|---|---|---|---|---|
| **Size** | | | | | |
| files / source lines | 363 / 55,479 | 367 / 50,390 | 377 / 46,122 | 364 / 44,869 | 369 / 44,733 |
| classes / methods | 703 / 4,603 | 764 / 4,536 | 867 / 4,967 | 879 / 5,123 | 905 / 5,189 |
| module-level functions (share of all functions) | 945 (17.0%) | 907 (16.7%) | 583 (10.5%) | 503 (8.9%) | 474 (8.4%) |
| **Complexity** | | | | | |
| CCN total / mean / p90 / max | 19,146 / 3.40 / 7 / 50 | 17,938 / 3.25 / 7 / 50 | 17,358 / 3.10 / 6 / 33 | 17,143 / 3.02 / 6 / 26 | 17,227 / 3.02 / 6 / 26 |
| functions with CCN > 10 / > 20 | 189 / 22 | 150 / 12 | 117 / 6 | 113 / 3 | 118 / 3 |
| cognitive total / mean / p90 / max | 16,471 / 2.96 / 8 / 105 | 14,664 / 2.68 / 7 / 105 | 13,326 / 2.39 / 7 / 39 | 12,838 / 2.27 / 6 / 37 | 12,882 / 2.27 / 6 / 37 |
| functions with cognitive > 15 | 136 | 97 | 63 | 59 | 57 |
| function NLOC mean / p90 / max | 8.2 / 17 / 343 | 7.4 / 15 / 343 | 6.5 / 14 / 89 | 6.2 / 13 / 77 | 6.1 / 13 / 77 |
| functions over 50 NLOC | 26 | 16 | 5 | 2 | 2 |
| parameters mean / max; functions with > 5 | 1.19 / 16; 50 | 1.17 / 16; 39 | 1.11 / 11; 33 | 1.04 / 11; 35 | 1.04 / 11; 34 |
| MI mean / p10; modules with MI < 20 | 58.5 / 10.0; 46 | 58.5 / 17.3; 40 | 59.5 / 19.9; 38 | 59.8 / 22.8; 32 | 60.7 / 22.7; 31 |
| module source lines p90 / max | 363 / 1,917 | 343 / 1,875 | 298 / 1,309 | 293 / 1,226 | 301 / 1,205 |
| **Classes (Chidamber & Kemerer)** | | | | | |
| class lines mean / p90 / max | 68 / 160 / 1,575 | 58 / 141 / 1,029 | 52 / 132 / 592 | 52 / 132 / 757 | 52 / 134 / 608 |
| NOM mean / p90 / max | 6.6 / 17 / 120 | 5.9 / 15 / 73 | 5.7 / 15 / 55 | 5.8 / 15 / 80 | 5.7 / 15 / 71 |
| WMC mean / p90 / max | 20.9 / 52 / 549 | 18.2 / 51 / 323 | 17.1 / 46 / 230 | 17.1 / 45 / 258 | 17.0 / 45 / 227 |
| CBO mean / p90; classes with CBO > 14 | 4.14 / 9; 30 | 4.76 / 10; 41 | 4.67 / 10; 40 | 4.58 / 10; 38 | 4.69 / 10; 43 |
| RFC mean / p90 / max; classes with RFC > 50 | 20.5 / 55 / 330; 78 | 19.0 / 50 / 232; 74 | 18.1 / 47 / 165; 78 | 18.0 / 46 / 228; 75 | 17.7 / 46 / 178; 75 |
| LCOM4 mean / max; classes with LCOM4 > 1 (share) | 2.32 / 15; 230 (60%) | 2.12 / 13; 223 (54%) | 2.00 / 13; 244 (50%) | 2.05 / 13; 251 (51%) | 2.05 / 13; 252 (51%) |
| cohesion (tool %) median | 14.3 | 16.7 | 20.0 | 20.0 | 21.2 |
| DIT mean / max | 1.30 / 6 | 1.18 / 6 | 1.07 / 6 | 1.24 / 6 | 1.28 / 6 |
| abstract classes | 21 | 19 | 21 | 26 | 23 |
| **Coupling between modules (Martin)** | | | | | |
| import edges between modules | 948 | 1,091 | 1,136 | 1,104 | 1,161 |
| module fan-in p90 / max | 6 / 54 | 7 / 57 | 7 / 57 | 7 / 58 | 8 / 62 |
| module fan-out mean / p90 / max | 2.63 / 6 / 26 | 3.00 / 7 / 18 | 3.04 / 7 / 23 | 3.06 / 7 / 20 | 3.17 / 7 / 20 |
| packages; Ce mean / max; Ca max | 107; 3.3 / 19; 58 | 109; 3.4 / 12; 47 | 108; 3.4 / 14; 46 | 100; 3.3 / 13; 43 | 99; 3.5 / 13; 43 |
| package I mean / A mean / D mean | 0.69 / 0.02 / 0.31 | 0.68 / 0.01 / 0.31 | 0.67 / 0.01 / 0.33 | 0.69 / 0.01 / 0.30 | 0.69 / 0.01 / 0.30 |
| packages with D > 0.7 | 18 | 20 | 22 | 15 | 15 |
| **Import cycles** | | | | | |
| runtime: SCCs / modules in them / largest | 4 / 86 / 78 | 10 / 55 / 16 | 10 / 46 / 16 | 11 / 54 / 19 | **2 / 4 / 2** |
| all imports: SCCs / modules / largest | 5 / 97 / 86 | 12 / 67 / 16 | 12 / 55 / 16 | 15 / 70 / 19 | 11 / 35 / 7 |
| import-time: SCCs | 0 | 0 | 0 | 0 | 0 |
| package cycles, runtime: SCCs / packages | 1 / 44 | 3 / 16 | 2 / 9 | 5 / 22 | 4 / 9 |
| **Duplication** | | | | | |
| jscpd duplicated lines (%) / clones / across files | 670 (1.38%) / 65 / 47 | 468 (0.87%) / 45 / 32 | 264 (0.48%) / 29 / 21 | 264 (0.49%) / 29 / 20 | 226 (0.42%) / 24 / 18 |
| exact function-clone groups (functions) | 13 (26) | 4 (8) | 4 (8) | 4 (8) | 3 (6) |
| module-level function names in several modules | 31 | 22 | 14 | 14 | 14 |
| **Shadow-model signals** | | | | | |
| class names defined in several modules | 11 | 6 | 6 | 5 | 5 |
| unrelated classes with identical / 80%-similar fields | 4 / 5 | 2 / 3 | 3 / 3 | 2 / 2 | 1 / 1 |
| TypeScript types named like a Python class | 5 | 7 | 7 | 4 | 4 |

TypeScript barely changed over the five revisions; the refactor has not reached it yet.

| TypeScript | `d6c41b23` | `42ab935c` | `d589b161` | `d71e0b20` | `9821ec3f` |
|---|---|---|---|---|---|
| files / NLOC / functions | 107 / 8,434 / 1,469 | 105 / 8,425 / 1,471 | 107 / 8,456 / 1,486 | 105 / 8,501 / 1,512 | 105 / 8,452 / 1,500 |
| CCN mean / p90 / max; functions > 10 | 2.01 / 4 / 49; 15 | 2.00 / 4 / 49; 15 | 1.97 / 4 / 49; 14 | 1.97 / 4 / 49; 14 | 1.96 / 4 / 48; 13 |
| function NLOC p90 / max | 11 / 254 | 11 / 254 | 11 / 254 | 11 / 254 | 11 / 247 |
| import edges; fan-in max / fan-out max | 264; 22 / 16 | 259; 22 / 16 | 277; 23 / 16 | 276; 23 / 16 | 277; 23 / 16 |
| cycles: SCCs / modules / largest | 3 / 25 / 19 | 3 / 25 / 19 | 3 / 26 / 20 | 3 / 26 / 20 | 3 / 26 / 20 |
| jscpd clones / duplicated % | 3 / 0.19% | 3 / 0.19% | 3 / 0.19% | 3 / 0.19% | 3 / 0.19% |

## Worst ten per revision

### By coupling: modules with the highest fan-in + fan-out

| # | `d6c41b23` | `42ab935c` | `d589b161` | `d71e0b20` | `9821ec3f` |
|---|---|---|---|---|---|
| 1 | agent_tools/agent_tools.py 54+10 | graph/graph.py 47+16 | graph/graph.py 49+16 | agent_tools/agent_tools.py 58+7 | agent_tools/agent_tools.py 62+6 |
| 2 | mcp/mcp_server.py 42+10 | agent_tools/agent_tools.py 57+6 | agent_tools/agent_tools.py 57+7 | graph/graph.py 46+17 | graph/graph.py 48+17 |
| 3 | stories/model/story_model.py 30+12 | mcp/mcp_server.py 40+11 | mcp/mcp_server.py 39+12 | mcp/mcp_server.py 37+15 | mcp/mcp_server.py 37+15 |
| 4 | ce/model/base_class_model.py 25+16 | ce/model/base_class_model.py 25+15 | guidance/guidance.py 23+14 | guidance/guidance.py 31+18 | guidance/guidance.py 29+18 |
| 5 | guidance/guidance.py 23+13 | guidance/guidance.py 24+13 | stories/model/story_model.py 25+12 | installation/destination.py 33+2 | installation/destination.py 34+2 |
| 6 | agent_tools/\_\_init\_\_.py 31+2 | stories/model/story_model.py 25+12 | installation/files.py 27+7 | installation/files.py 27+6 | installation/files.py 27+6 |
| 7 | installation/files.py 28+4 | installation/files.py 27+5 | ce/model/base_class_model.py 23+10 | ce/model/base_class_model.py 21+11 | ce/model/base_class_model.py 21+11 |
| 8 | graph/practice_rule.py 30+1 | agent_tools/\_\_init\_\_.py 30+2 | installation/destination.py 32+1 | agent_tools/\_\_init\_\_.py 29+2 | agent_tools/\_\_init\_\_.py 29+1 |
| 9 | graph/graph.py 16+14 | installation/destination.py 31+1 | agent_tools/\_\_init\_\_.py 30+2 | stories/model/story_model.py 22+8 | stories/model/story_model.py 22+7 |
| 10 | installation/installer.py 20+10 | graph/practice_rule.py 29+1 | name/name.py 30+0 | graph/practice_rule.py 27+1 | graph/practice_rule.py 27+1 |

`ce` is `cdd_guidance/practices/clean_engineering`; the others are under `harness/` or `cdd_guidance/practices/`.

### By coupling: classes with the highest CBO (leaving out `PracticeGraphRule`, CBO ≈ 100 from its subclasses, at every revision)

| # | `d6c41b23` | `42ab935c` | `d589b161` | `d71e0b20` | `9821ec3f` |
|---|---|---|---|---|---|
| 1 | OoadClass 35 | Node 53 | Node 56 | Graph 56 | Node 57 |
| 2 | Name 30 | Graph 48 | Graph 54 | Node 56 | Graph 55 |
| 3 | PracticeGuidance 29 | OoadClass 36 | Name 42 | PracticeGuidance 37 | PracticeGuidance 37 |
| 4 | Story 29 | RuleCheckContext 35 | OoadClass 36 | Name 36 | RuleCheckContext 37 |
| 5 | Graph 27 | Name 31 | RuleCheckContext 36 | RuleCheckContext 36 | OoadClass 36 |
| 6 | AgentToolSet 27 | Story 30 | PracticeGuidance 31 | OoadClass 34 | Name 30 |
| 7 | Module (ce) 27 | PracticeGuidance 29 | Story 30 | FidelityGuidance 28 | FidelityGuidance 27 |
| 8 | Repo 24 | AgentToolSet 28 | Epic 28 | UxMap 27 | UxMap 27 |
| 9 | Installer 23 | Epic 27 | StoryModel 25 | Epic 25 | Module (ce) 26 |
| 10 | Epic 23 | StoryModel 26 | Module (ce) 24 | Story 24 | Epic 25 |

### By complexity: classes with the highest WMC (WMC / NOM / LCOM4)

| # | `d6c41b23` | `42ab935c` | `d589b161` | `d71e0b20` | `9821ec3f` |
|---|---|---|---|---|---|
| 1 | DrawioScanner 549/120/9 | AgentInstructions 323/73/2 | MarkdownStoryModel 230/42/2 | **Graph 258/80/3** | MarkdownStoryModel 227/40/3 |
| 2 | Repo 371/111/12 | Installer 266/72/1 | MarkdownScenario 197/38/3 | MarkdownStoryModel 234/41/3 | Graph 205/61/5 |
| 3 | DrawIOCleanEngineeringModel 342/80/2 | MarkdownStoryModel 225/43/4 | RecipeExpansion 194/45/1 | RecipeExpansion 194/45/1 | PracticeGuidance 199/71/13 |
| 4 | Installer 320/82/1 | PromptNotify 197/49/4 | MarkdownCleanEngineeringModel 189/26/6 | PracticeGuidance 192/68/11 | RecipeExpansion 194/45/1 |
| 5 | AgentInstructions 314/71/2 | MarkdownScenario 196/37/3 | PracticeGuidance 179/53/7 | CodeStoryModel 152/56/5 | MarkdownScenario 154/30/3 |
| 6 | Session 283/97/1 | MarkdownCleanEngineeringModel 193/29/7 | CodeStoryModel 149/55/4 | MarkdownScenario 141/29/2 | CodeStoryModel 152/56/5 |
| 7 | MarkdownStoryModel 254/51/4 | AgentToolSet 186/50/7 | FileInstallation 138/29/1 | FileInstallation 136/29/1 | FidelityGuidance 136/50/2 |
| 8 | PromptNotify 230/52/4 | Graph 164/47/4 | CFamilyParse 125/24/2 | MarkdownAggregate 136/27/1 | MarkdownAggregate 136/27/1 |
| 9 | MarkdownCleanEngineeringModel 201/31/7 | PracticeGuidance 163/47/10 | SessionLog 112/32/1 | FidelityGuidance 134/49/2 | FileInstallation 135/29/1 |
| 10 | MarkdownScenario 196/37/3 | Validate 158/33/1 | RulesCollection 111/30/6 | MarkdownCleanEngineeringModel 120/20/2 | Ticket 123/43/6 |

### By complexity: functions with the highest cognitive complexity (top five)

| # | `d6c41b23` | `42ab935c` | `d589b161` | `d71e0b20` | `9821ec3f` |
|---|---|---|---|---|---|
| 1 | `markdown_to_html` 105 | `markdown_to_html` 105 | `_parse_operations_and_relationships` 39 | `attach_source_locations` 37 | `attach_source_locations` 37 |
| 2 | `SketchDddModel.parse` 77 | `MarkdownOoadClass.render` 43 | `_render_control` (UX html) 39 | `MarkdownOoadClass.read_body` 36 | `MarkdownOoadClass.read_body` 36 |
| 3 | `_record_lern` (working_copy) 54 | `_parse_operations_and_relationships` 39 | `attach_source_locations` 37 | `MiroStoryModel.load` 31 | `MarkdownOoadClass._read_operations` 31 |
| 4 | `_class_fact` (working_copy) 47 | `_render_control` 39 | `_parse_class` 34 | `ClaudeDesignStoryModel._story_entry` 31 | `MiroStoryModel.load` 31 |
| 5 | `_record_story_edges` 47 | `_render_classes` (Miro CE) 37 | `_render_scenario_lines` 33 | `_read_operations` 28 | `_story_entry` 31 |

### Packages furthest from the main sequence at the tip

All in the zone of pain (stable and concrete): `harness/annotations` D = 1.0 (Ca 20, Ce 0), `harness/process` 1.0, `harness/agent_tools` 0.93 (Ca 43, I 0.04, A 0.02), `harness/markdown` 0.92, `harness/installation` 0.86 (Ca 30), `harness/mcp` 0.84 (Ca 26), `harness/graph` 0.80 (Ca 23), `harness/guidance` 0.78 (Ca 28). The list has been the same harness packages since round 3. For leaf utilities such as `annotations` and `process` that is expected; for `agent_tools`, `graph` and `guidance`, which hold behaviour and change often, it means every change to them reaches 23–43 other packages, with no abstraction between.

## Assessment of each revision

**`d6c41b23`, input to rounds 1 and 2: the weakest code.** It is the largest (55.5 thousand lines) and the most procedural: 945 module-level functions, 17% of all functions. It holds several god classes: `DrawioScanner` (WMC 549, 120 methods), `Repo` (WMC 371, 111 methods, LCOM4 12), `Installer` and `AgentInstructions` (WMC above 300). It also has 22 functions above CCN 20, one 343-line function, and `markdown_to_html` at cognitive complexity 105. Its import graph has one knot of 78 modules: the Clean Engineering, Stories, DDD and BDD models and the LERN pattern all reach each other. 44 packages sit in one package cycle. Duplication is the highest measured, though still low in absolute terms (1.38%, 65 clones, 13 groups of identical functions, `Change` and `ChildCollectionPair` copied between Clean Engineering and UX).

**`42ab935c`, input to round 3: the knot cut, the god classes split.** Source lines fell 9%. The 78-module cycle shrank to a 16-module ring inside the Stories model, and package cycles went from 44 packages to 16. The biggest classes were split: WMC max fell from 549 to 323, class lines max from 1,575 to 1,029. Duplication fell to 0.87% and the identical-function groups from 13 to 4. Not yet touched: `markdown_to_html` (cognitive 105) and the 343-line function. Coupling rose as classes multiplied: classes with CBO above 14 went from 30 to 41, and the new `Graph`/`Node` pair became the most coupled classes (CBO 48–53).

**`d589b161`, input to round 4: the best complexity profile.** The long and tangled functions are gone (max cognitive 39, max NLOC 89, only 5 functions above 50 lines). Module-level functions fell to 10.5% of all functions, the largest drop of any round. Package cycles are at their minimum (9 packages). Graph is at its smallest (WMC 105). The relationship review's 363 wrong-shape relationships fit these numbers: the classes are smaller and simpler, but the edges between modules are at a high (1,136) and so is CBO > 14 (40). The remaining problem is the direction and meaning of dependencies, not the size of the units.

**`d71e0b20`, input to round 5: complexity held, structure slipped.** Complexity and duplication held or improved slightly (3 functions above CCN 20, 59 above cognitive 15, 0.49% duplicated). The structure got worse:
- `Graph` grew back from WMC 105 to 258, with 80 methods and RFC 228. The single-graph change put its behaviour in one class.
- Runtime import cycles grew to 11 SCCs holding 54 modules, the largest a 19-module ring through the whole Clean Engineering model (`operation`/`property` ↔ `base_class_model` and every language's class model). The others: the DDD and Stories models with their practices, the hooks trio, `repo` ↔ `worktree`, the session family, `board` ↔ `ticket`, and the LERN pattern.
- Package cycles rose to 22 packages, the most since round 1.

This is the same list as round 5's high structural findings 15 and 16 (model nodes importing their practice, cycles hidden by imports inside functions).

**`9821ec3f`, after the round-5 fixes: the cycles are gone, the hubs remain.** The round-5 fixes removed nine of the eleven runtime cycles. What is left is `graph` ↔ `saved_graph` and `catalog_generator` ↔ `project_approach`, 4 modules in all. Package cycles are back to 9 packages. `Graph` shrank to WMC 205 and RFC 178, and only one shadow-model signal is left (`Edge` and `SavedEdge` hold the same fields). Complexity and duplication are flat at their best values (0.42% duplicated, 24 clones). Coupling is at its highest of the five revisions:
- 43 classes with CBO above 14
- `harness/agent_tools/agent_tools.py` with a fan-in of 62
- 1,161 import edges

`PracticeGuidance` keeps growing: 71 methods, CBO 37, and LCOM4 13, the least cohesive class in the repository. Half of all classes with two or more methods (252) still have LCOM4 above 1.

## Trend, and how it compares with the findings trend

**Complexity, size and duplication improved steeply over rounds 1–3, then levelled off from round 4.** Between the first and last revision:
- functions above CCN 20 fell from 22 to 3, and functions above cognitive 15 from 136 to 57
- functions over 50 lines fell from 26 to 2
- the largest class fell from WMC 549 to 227
- jscpd duplication fell from 1.38% to 0.42%
- modules below MI 20 fell from 46 to 31
- the code shrank by 19% while the number of classes grew by 29%

Almost all of this happened before round 4. From `d589b161` to the tip, every complexity and duplication number moves by less than 10%.

**Object orientation improved; the objects are not yet well shaped.** The share of behaviour in module-level functions halved (17% → 8.4%) and the share of non-cohesive classes fell from 60% to 51%. That is the code moving into classes, which is the direction the resource-orientation goal asks for. But coupling rose at every round:
- import edges up 22% (948 → 1,161)
- classes with CBO above 14 up from 30 to 43
- the top module fan-in up from 54 to 62

The behaviour moved into a few hub classes: `Graph`, `Node`, `PracticeGuidance`, `FidelityGuidance`, `AgentToolSet` and `OoadClass`, and the hub packages sit in the zone of pain (abstractness about 0.01 across the repository). The metrics show what the findings call "wrong-shape relationships" as rising CBO and as packages far from the main sequence.

**Import cycles fell, rose in round 5, and were then fixed.** The runtime cycles went 86 → 55 → 46 → 54 → 4 modules. No revision has a cycle at import time: every module cycle is closed by an import written inside a function, which hides the cycle from Python and from a folder-level scanner but not from the design.

**Agreement with `trend-rounds-1-5.md`.**
- **It agrees on the direction of rounds 1–3.** Round 1, the worst code by every complexity and duplication metric, drew the most findings (64–114); the measured code improved sharply into rounds 2 and 3, as the falling and narrowing bug findings say.
- **It explains why the finding counts rose in rounds 4 and 5 without the code getting worse.** Complexity and duplication did not rise. The higher counts come from the wider scope of those rounds, as the trend file says. The one real slip between rounds 4 and 5 is structural: the cycles (46 → 54 modules), the package cycles (9 → 22) and the regrown `Graph`. These match round 5's 12 structural high findings.
- **It disagrees on one point.** The trend file says every graph-scanner cycle in round 5 came from spec or `_examples` imports. The production code at `d71e0b20` did have 11 module cycles; the project's scanner missed them because it measures folders and skips imports inside functions (round-5 report, "Scanner defects"). The AI agents' finding 16 was right.
- **On the goal classes, the metrics can confirm only part of the remaining 163.**
  - *Duplicated functions:* textual duplication is already far below the usual 3–5% alarm level (0.42%, 24 clones, 3 identical-function groups, 14 helper names defined twice). The 62 findings in this class are mostly the same responsibility written twice in different words, or once in Python and once in TypeScript. Clone detectors cannot see those.
  - *Shadow models:* only `Edge`/`SavedEdge`, `Scenario`/`Step` (in `story_model.py` and `space/kanban/story_test.py`), `TypeScriptOperation` (in two modules) and four TypeScript types sharing a Python class's name are mechanical copies. The 33 findings are mostly second models under other names.
  - *Bad resource orientation* is where the metrics give a usable progress measure. Watch these numbers round by round alongside the 68 findings: classes with CBO above 14 (43), classes with LCOM4 above 1 (252), packages with D above 0.7 (15), and the fan-in of `agent_tools.py` (62).
- **TypeScript has not moved.** Its 20-module cycle between the board and ticket clients of the kanban app, and `KindMark` at CCN 48 in the graph app, are the same at every revision. Concern 12, rules decided in both TypeScript and Python, has not yet reached that code.

## Rerunning on a new round's commit

`git archive -o rev.tar <sha>`, extract it into an empty folder, then run `python .context/repo-review/measure_revision.py <folder> --label "round N input" --node-tools <dir with jscpd@4, dependency-cruiser@16, typescript@5> --out roundN.json` with a venv that has radon, lizard, complexipy, cohesion, grimp and networkx.
