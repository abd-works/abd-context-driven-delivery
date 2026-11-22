# Which measures would have flagged the release 1.2 defects (2026-11-22)

The question: starting from the backlog item [Measure Code On The Model](../../../_backlog/measure-code-on-the-model.md), which measures could judge generated code so that the 146 defects exploratory testing found in release 1.2, and that defect rate, are avoided?

The short answer from the numbers: the backlog item's size and complexity measures follow how big a module is, and they say nothing about the defects found at the edges of the tools. What would have flagged most of the defects is a different kind of measure: a count of **behaviour nobody wrote down or tested**, taken per published operation, per format of a fidelity, per story, and per edge of the knowledge graph.

## Summary: the recommended set

Defect counts are the defects in the themes of [defect-themes-by-wave.md](../defect-themes-by-wave.md) that carry the tag; a theme can carry several tags, so the counts overlap.

### Group A — the backlog item's code measures

| Measure | What it counts | Graph node | Verdict from the numbers | Limit |
|---|---|---|---|---|
| Paths through a function (cyclomatic complexity) | 1, plus 1 for each `if`, loop, `and`/`or` and handler | operation | **Keep as a fact, report only.** The count of functions over 10 paths moves with defects (0.51) only because bigger modules have more of both; as a share of the module's functions it does not (0.26), and for the tool-edge defects of waves 1 and 2 it is −0.18. | 10, shown in the report, never failing a validation |
| Readability score (cognitive complexity) | Paths weighted by how deeply they nest | operation | **Drop.** Not measured here (complexipy is in the metrics virtual environment, not run). The practice already keeps nesting depth as a fact with a limit of three levels, which says the same thing in words a person can check. | none |
| Lines in a function | Lines of code in the body | operation | **Keep with the limit the practice already has.** 11 functions of 13,896 are over 50 lines, so a limit of 50 finds almost nothing; the rule `keep-operations-small-focused` already asks for under 20 statements. | 20 statements |
| Parameters of a function | Values a caller supplies | operation | **Keep with the limit the practice already has.** 33 functions are over 5; no relation to defects (0.20). | 3 for a domain operation, as `limit-operation-parameters` says |
| A class's total paths | The paths of all its methods added up | class | **Drop as a limit, keep as a fact.** No relation (0.14); the two modules with fewest defects each hold a class over 100. | none |
| A class's method count | Methods a class declares | class | **Keep as a fact, report only.** Weak relation (0.32); 15 classes today are over 30. Already a typed field, `method_count`. | 30, report only |
| Classes a class depends on | Other classes it calls, builds or holds | class | **Keep.** Not measured here (grimp was not run); the graph already holds these edges, so the count costs nothing. | no more than before the change |
| Methods sharing no data with the rest of their class (cohesion) | Groups of methods that touch separate fields | class | **Keep, unproven.** Not measured here. No defect theme names a class doing two jobs. | report only |

### Group B — measures to add as facts on graph nodes

| Measure | What it counts | Graph node | Limit, and why | Tags it would have caught | Places flagged today |
|---|---|---|---|---|---|
| Name or path argument used without a check | A published operation (`@mcp` or `@agent_tool`) whose name, title, path or id argument reaches a folder, file or stored record through its calls with nothing refusing an empty, taken, too long or outside-the-root value | operation | None allowed. Every such argument is typed by an agent or a person, and 27 defects came from taking it as given. | `unchecked-input` 27, part of `data-loss` 40 | 88 of 249 published operations take such an argument; 62 have no check in their own body, which is too coarse (see the per-tag section) |
| Refusal examples per published operation | Story scenarios and spec examples that hand the operation a value it must refuse | operation, through the `invokes` edge from a story test step | At least one per name or path argument. The defect report's "test that was missing" column asks for a refused input again and again: an empty, taken or too-long title, a blank card, a bad path. | `unchecked-input` 27, `false-success` 32, `raw-error` 19 | not countable yet: needs the `invokes` edges |
| Format with no there-and-back spec | A format a fidelity declares, other than its default, that no spec renders to and back and compares | fidelity (one fact per format) | None allowed. A format nobody has taken there and back holds less than markdown, and the render saves it over the markdown. | `lossy-format-trip` 31, `undeclared-output` 16, part of `data-loss` 40 | 4 of 42 today; **17 of 31 at release 1.2**, among them every format the testers reported |
| Format or file no reader owns | A format a fidelity offers with no adapter or no graph reading; a practice file no fidelity declares | fidelity; practice | None allowed. An offered format with nothing behind it answers `{}` or is refused. | `undeclared-output` 16, `false-success` (part) | 15 of 102 practice files on the Bookshop were undeclared at release |
| Failure answered with a default | A handler that catches a failure and returns a constant, an empty value, or nothing, with no raise | operation | Each one named and justified; none on the call path of a published operation that writes. `JsonFile.read` answering empty for an unreadable file is this, and it cost four defects and lost queue files. | `false-success` 32, `raw-error` 19, `data-loss` (part) | 99 of 230 Python handlers; only 26 catch every exception, so counting `except Exception` alone misses three quarters |
| State file changed without being held | A class that reads a file, changes it and writes it back, where more than one process can run that class, with no lock held from read to write and no atomic replace | class | None allowed for a file two processes write. | `concurrency` 12, part of `data-loss` 40 | 30 files keep state through `JsonFile`; 25 never call `held()` |
| Record that can outlive its subject | A stored record holding a process id, a commit, a path or a claim, with no operation that checks it still describes something live | class (the record) | Every such field has a check; judged, not counted. | `stale-state` 34 | 13 production files keep a process id |
| Edge joined by name alone | A graph edge whose target was found by comparing names, with no class, language or import to tell same-named things apart | relationship (how its target was resolved) | None across practices or languages. | `name-matching` 15 | 35 `.name ==` comparisons in the graph and reading code (242 in the whole codebase, too many to read) |
| Template that fails its own fidelity's rules | A template run through validate at its fidelity | fidelity (one fact per template) | None allowed. | `rule-template-mismatch` 11 | 25 templates; no spec was found that runs each through its rules |
| Story with no failure scenario | Scenarios per story, and how many of them are about a refused, missing, repeated or broken input | story | At least one failure scenario for a story whose operation takes input or writes a file. | every tag found by "missing behaviour at the edges" | 143 of 265 stories have none; 56 have one scenario |
| Practice file with no browser test of its view | For each file kind a fidelity writes, whether a browser story test opens it in the Files app's source view and rendered view | fidelity | Every file kind, both views. | `display` 23 | 13 defects in the report needed a real browser |

### Group C — process measures, per ticket and per release

| Measure | What it counts | Value for release 1.2 | Limit |
|---|---|---|---|
| Defects found per layer | Defects by what found them: unit tier, heavy tier, e2e tier, exploratory testing, review | 6, 2, 1, 135, 2 | trend only |
| Share of unit-tier defects the unit tier caught | Defects the unit tier found, out of those a BDD spec or story test could have failed on | 6 of 103, 6% | above 70% |
| Escaped defect rate | Defects found after every automated tier was green, out of all defects | 132 of 146, 90% | below 30% |
| Defects per thousand lines of production code | Defects over lines, per release | 146 over 78,500 lines, 1.9 | trend only |
| Production change with no test | Commits that change production code with no spec or story test file in the same commit | 334 of 1,309 before the release, 26%; 11 of 155 since, 7% | below 5%, and each one says why |
| Share of scenarios about failure | Failure scenarios out of all scenarios | 99 of 570 at release, 17%; 218 of 977 today, 22% | per story, not per release: see Group B |
| Fixes that broke something | Defects tagged `regression` out of defects fixed | 12 of 146 | trend only |
| First real run recorded | For a new boundary (Flow A), whether a real end-to-end run was recorded before the stubbed tests | missing for the desktop walk | every Flow A ticket |

## Per-module measures, with defects

Measured on the code at the tag `v1.2.0` (commit 18cd597ba, 2026-11-18), which is the code the testers ran. Production code only. `story_tests` (3 defects) holds no production code and `cdd_guidance/desktop_walk` (1 defect) did not exist at the tag, so 17 modules are measured. `harness/files_app` is the Python toolset and its TypeScript app; `space/kanban` includes the board app; `harness/guidance` is measured with `harness/guidance_actions`, as the defects table pairs them.

### Size and complexity

| Module | Defects | Defects per thousand lines | Lines of code | Functions | Functions over 10 paths | Functions over 50 lines | Functions over 5 parameters | Classes over 30 methods | Classes over 100 total paths | Most paths in one function | Median paths |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `stories` | 29 | 3.3 | 8871 | 1430 | 11 | 3 | 5 | 1 | 1 | 37 | 2 |
| `space/session` | 26 | 7.0 | 3737 | 659 | 3 | 0 | 0 | 2 | 0 | 11 | 1 |
| `harness/graph` | 20 | 3.1 | 6424 | 1036 | 11 | 2 | 4 | 1 | 1 | 23 | 2 |
| `space/kanban` | 19 | 2.7 | 7118 | 1551 | 4 | 0 | 0 | 2 | 0 | 14 | 1 |
| `harness/files_app` | 19 | 8.3 | 2298 | 557 | 1 | 1 | 1 | 0 | 0 | 11 | 1 |
| `clean_engineering` | 19 | 2.0 | 9677 | 1206 | 29 | 0 | 0 | 1 | 3 | 17 | 3 |
| `actions` | 17 | 12.8 | 1325 | 163 | 1 | 0 | 0 | 0 | 0 | 11 | 2 |
| `harness/installation` | 16 | 7.8 | 2058 | 321 | 2 | 0 | 0 | 1 | 2 | 12 | 2 |
| `ddd` | 15 | 5.8 | 2585 | 333 | 4 | 0 | 4 | 0 | 1 | 11 | 2 |
| `harness/diagnostics` | 14 | 9.8 | 1432 | 207 | 2 | 0 | 2 | 0 | 0 | 12 | 2 |
| `bdd` | 13 | 12.5 | 1038 | 138 | 1 | 0 | 0 | 0 | 0 | 11 | 2 |
| `scripts` | 12 | 7.1 | 1687 | 130 | 0 | 0 | 0 | 0 | 0 | 9 | 3 |
| `space/repo` | 11 | 8.3 | 1321 | 232 | 1 | 0 | 1 | 0 | 0 | 11 | 1 |
| `tools/prompt_queue` | 10 | 6.6 | 1525 | 309 | 2 | 0 | 5 | 0 | 0 | 13 | 1 |
| `ux` | 10 | 2.1 | 4851 | 698 | 4 | 0 | 0 | 0 | 0 | 20 | 1 |
| `harness/guidance` (with actions) | 3 | 1.3 | 2272 | 405 | 3 | 0 | 0 | 1 | 1 | 15 | 2 |
| `harness/mcp` | 2 | 1.1 | 1876 | 285 | 0 | 0 | 0 | 2 | 1 | 8 | 2 |

The whole production codebase at the tag: 736 files, 78,493 lines, 12,488 functions, 91 over 10 paths (0.7%), 11 over 50 lines, 25 over 5 parameters, 12 classes over 30 methods, median 2 paths, mean 2.45. This is clean code by every limit in the backlog item, and it shipped 146 defects.

### Edge-behaviour signals in the code

| Module | Defects | Published operations | of which take a name or path | of which have no check in their own body | Handlers that catch everything | Handlers that answer a default | TypeScript catch blocks | Functions outside any class | Comparisons on a name | of which `.name ==` | File writes | Files that write with no lock or atomic replace |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `stories` | 29 | 17 | 7 | 6 | 0 | 2 | 10 | 59 | 29 | 17 | 6 | 5 |
| `space/session` | 26 | 49 | 23 | 18 | 1 | 2 | 0 | 6 | 20 | 16 | 25 | 8 |
| `harness/graph` | 20 | 14 | 6 | 6 | 0 | 2 | 16 | 13 | 26 | 15 | 10 | 3 |
| `space/kanban` | 19 | 44 | 9 | 7 | 2 | 0 | 7 | 27 | 63 | 57 | 0 | 0 |
| `harness/files_app` | 19 | 0 | 0 | 0 | 0 | 0 | 39 | 0 | 9 | 3 | 0 | 0 |
| `clean_engineering` | 19 | 3 | 3 | 3 | 0 | 10 | 0 | 80 | 72 | 30 | 1 | 1 |
| `actions` | 17 | 26 | 13 | 7 | 0 | 1 | 0 | 2 | 3 | 3 | 5 | 4 |
| `harness/installation` | 16 | 3 | 0 | 0 | 3 | 9 | 0 | 4 | 7 | 3 | 8 | 4 |
| `ddd` | 15 | 0 | 0 | 0 | 0 | 0 | 0 | 12 | 16 | 7 | 0 | 0 |
| `harness/diagnostics` | 14 | 9 | 0 | 0 | 6 | 8 | 0 | 10 | 11 | 0 | 9 | 3 |
| `bdd` | 13 | 0 | 0 | 0 | 0 | 1 | 0 | 9 | 1 | 1 | 0 | 0 |
| `scripts` | 12 | 0 | 0 | 0 | 0 | 7 | 2 | 40 | 14 | 0 | 8 | 6 |
| `space/repo` | 11 | 8 | 3 | 0 | 0 | 1 | 0 | 0 | 9 | 8 | 11 | 5 |
| `tools/prompt_queue` | 10 | 14 | 1 | 1 | 0 | 1 | 9 | 3 | 4 | 2 | 2 | 1 |
| `ux` | 10 | 1 | 0 | 0 | 0 | 0 | 2 | 16 | 28 | 21 | 4 | 2 |
| `harness/guidance` (with actions) | 3 | 9 | 0 | 0 | 1 | 1 | 0 | 6 | 5 | 2 | 0 | 0 |
| `harness/mcp` | 2 | 0 | 0 | 0 | 4 | 13 | 0 | 11 | 10 | 4 | 12 | 3 |

### Tests beside the code

Spec lines leave out example and fixture folders. A heavy or e2e spec "touches" a module when it sits in the module's folder or names the module's path. Stories are matched to a module when their scenario file names the module's folder, so the practices, whose scenario files name no folder, show none.

| Module | Defects | Lines of spec beside the code | Spec lines per production line | Unit spec files | Heavy specs touching it | E2E specs touching it | Story test code files naming it | Stories whose scenario file names it | of which have one scenario | of which have no failure scenario |
|---|---|---|---|---|---|---|---|---|---|---|
| `stories` | 29 | 6567 | 0.74 | 119 | 2 | 0 | 1 | 0 | 0 | 0 |
| `space/session` | 26 | 3329 | 0.89 | 16 | 15 | 3 | 8 | 56 | 8 | 32 |
| `harness/graph` | 20 | 4732 | 0.74 | 27 | 7 | 1 | 2 | 48 | 7 | 26 |
| `space/kanban` | 19 | 6442 | 0.91 | 36 | 3 | 12 | 40 | 99 | 14 | 57 |
| `harness/files_app` | 19 | 2224 | 0.97 | 13 | 0 | 0 | 4 | 40 | 5 | 23 |
| `clean_engineering` | 19 | 6586 | 0.68 | 35 | 3 | 0 | 0 | 5 | 0 | 2 |
| `actions` | 17 | 2951 | 2.23 | 15 | 13 | 1 | 1 | 6 | 0 | 2 |
| `harness/installation` | 16 | 2145 | 1.04 | 10 | 11 | 0 | 1 | 0 | 0 | 0 |
| `ddd` | 15 | 1389 | 0.54 | 19 | 1 | 0 | 1 | 0 | 0 | 0 |
| `harness/diagnostics` | 14 | 1481 | 1.03 | 8 | 6 | 1 | 0 | 6 | 0 | 4 |
| `bdd` | 13 | 684 | 0.66 | 10 | 3 | 0 | 0 | 0 | 0 | 0 |
| `scripts` | 12 | 0 | 0.00 | 0 | 2 | 0 | 0 | 5 | 0 | 0 |
| `space/repo` | 11 | 1004 | 0.76 | 2 | 12 | 0 | 1 | 0 | 0 | 0 |
| `tools/prompt_queue` | 10 | 1504 | 0.99 | 2 | 1 | 1 | 3 | 30 | 3 | 14 |
| `ux` | 10 | 939 | 0.19 | 10 | 1 | 0 | 1 | 0 | 0 | 0 |
| `harness/guidance` (with actions) | 3 | 1727 | 0.76 | 12 | 2 | 0 | 0 | 12 | 2 | 7 |
| `harness/mcp` | 2 | 1868 | 1.00 | 9 | 17 | 2 | 2 | 0 | 0 | 0 |

Across every scenario file at the tag: 197 stories, 570 scenarios, 47 stories with one scenario, and 121 stories (61%) with no scenario whose title speaks of a refusal, a missing or repeated thing, or a failure.

### Change, from git

The 60 days before today reach back to 2026-09-23. The first four columns count commits up to the tag; the last two count the 231 commits since, which are the fixes.

| Module | Defects | Commits touching it | of which change production code | Share with no spec or story test file anywhere in the commit | Share with no spec file of the same module | Production commits since the release | Share with no test file since the release |
|---|---|---|---|---|---|---|---|
| `stories` | 29 | 198 | 151 | 11% | 39% | 40 | 5% |
| `space/session` | 26 | 272 | 236 | 9% | 34% | 46 | 4% |
| `harness/graph` | 20 | 250 | 191 | 9% | 44% | 20 | 0% |
| `space/kanban` | 19 | 288 | 209 | 19% | 30% | 27 | 4% |
| `harness/files_app` | 19 | 51 | 41 | 5% | 24% | 20 | 5% |
| `clean_engineering` | 19 | 159 | 133 | 11% | 45% | 26 | 4% |
| `actions` | 17 | 150 | 107 | 6% | 30% | 33 | 6% |
| `harness/installation` | 16 | 128 | 84 | 6% | 39% | 13 | 0% |
| `ddd` | 15 | 95 | 77 | 3% | 42% | 22 | 4% |
| `harness/diagnostics` | 14 | 71 | 58 | 3% | 29% | 13 | 0% |
| `bdd` | 13 | 78 | 55 | 4% | 53% | 17 | 6% |
| `scripts` | 12 | 103 | 93 | 16% | 100% | 19 | 10% |
| `space/repo` | 11 | 98 | 86 | 8% | 46% | 11 | 0% |
| `tools/prompt_queue` | 10 | 126 | 119 | 35% | 35% | 6 | 33% |
| `ux` | 10 | 72 | 52 | 6% | 52% | 22 | 9% |
| `harness/guidance` (with actions) | 3 | 178 | 147 | 4% | 50% | 25 | 4% |
| `harness/mcp` | 2 | 160 | 141 | 15% | 45% | 13 | 0% |

Across the whole repository, 334 of the 1,309 commits that changed production code before the tag (26%) held no spec or story test file; since the tag, 11 of 155 (7%).

## What moves with the defect count

Rank correlation (Spearman) across the 17 modules, between each measure and the module's defect count, and between each measure and the module's defects per thousand lines. With 17 modules a value has to pass about 0.49 either way before it is unlikely to be chance, and 53 measures were tried, so two or three would pass that mark by chance alone. Read every value below as a hint.

| Measure | With defect count | With defects per thousand lines |
|---|---|---|
| Unit spec files | **0.77** | −0.32 |
| Lines of spec beside the code | **0.73** | −0.31 |
| Published operations taking a name or path, with no check in their own body | **0.68** | −0.08 |
| Production files | **0.66** | −0.38 |
| Published operations taking a name or path | **0.64** | 0.02 |
| Functions over 50 lines | **0.58** | −0.04 |
| Lines of code | **0.56** | **−0.67** |
| Functions | **0.55** | **−0.62** |
| Functions over 10 paths | **0.51** | **−0.50** |
| Comparisons on a name | 0.48 | **−0.55** |
| Published operations | 0.47 | 0.00 |
| Stories with no failure scenario | 0.40 | −0.08 |
| Commits touching the module | 0.38 | **−0.50** |
| Classes over 30 methods | 0.32 | **−0.61** |
| Most paths in one function | 0.32 | −0.42 |
| Story test code files naming the module | 0.32 | −0.13 |
| Share of functions over 10 paths | 0.26 | −0.10 |
| Functions outside any class | 0.23 | **−0.56** |
| Functions over 5 parameters | 0.20 | 0.11 |
| Files that write with no lock or atomic replace | 0.20 | 0.23 |
| Classes over 100 total paths | 0.14 | **−0.54** |
| Heavy specs touching the module | 0.09 | 0.12 |
| Mean paths per function | 0.09 | 0.14 |
| Share of production commits with no test file | 0.07 | −0.40 |
| Handlers that answer a default | 0.03 | −0.12 |
| Median paths per function | 0.02 | −0.08 |
| Spec lines per production line | 0.02 | 0.28 |
| Handlers that catch everything | −0.14 | −0.17 |
| Share of production commits with no spec of the same module | **−0.51** | −0.31 |

Divided by thousand lines, only one measure still moves with the defect count: published operations taking a name or path with no check in their own body, per thousand lines, at 0.64. Functions over 10 paths per thousand lines falls to 0.19 and comparisons on a name per thousand lines to 0.09.

The two halves of the testing behave differently. Waves 1 and 2 pressed the tools at their edges; waves 3 and 4 ran every fidelity of every practice.

| Measure | With defects of waves 1 and 2 | With defects of waves 3 and 4 |
|---|---|---|
| Lines of code | −0.15 | **0.56** |
| Functions over 10 paths | −0.18 | **0.55** |
| Comparisons of the form `.name ==` | −0.10 | 0.46 |
| Lines of spec beside the code | 0.18 | 0.48 |
| Published operations | 0.42 | 0.08 |
| Files that write with no lock or atomic replace | 0.42 | 0.00 |
| Spec lines per production line | 0.48 | −0.38 |
| Published operations taking a name or path, no check in their own body | 0.27 | 0.41 |
| Heavy specs touching the module | 0.27 | −0.16 |

What the numbers say, plainly:

1. **The expectation holds.** Size explains part of the defect count (0.56), and the complexity measures add nothing beyond size: the count of functions over 10 paths follows size, and the share of such functions, the median and the mean do not move with defects at all (0.26, 0.02, 0.09). For the 66 defects of waves 1 and 2, which are the unchecked inputs, second callers and stale records, size and complexity point slightly the wrong way (−0.15, −0.18).
2. **Smaller modules have more defects per thousand lines** (−0.67). `actions` (12.8), `bdd` (12.5) and `harness/diagnostics` (9.8) are small and were pressed hard; `clean_engineering` (2.0), which has the most complex functions of all (29 over 10 paths, median 3), has the fewest per line after `harness/mcp` and `harness/guidance`. A defect in this release came from an operation or a format that exists, not from a line that is tangled, and a small module has as many operations to get wrong at the edge as a big one.
3. **More specs went with more defects, not fewer** (0.73 to 0.77), and the amount of spec per line of code made no difference (0.02). `actions` has 2.2 lines of spec for each line of code, 13 heavy specs, and the highest defect rate of any module. The specs were there; they checked the path the author thought of. Lines of test, files of test and the share of commits holding a test are all the wrong thing to count: what matters is which behaviours the tests name.
4. **The share of commits with no test did not predict defects** (0.07), and the stricter count, no spec of the same module, points the wrong way (−0.51). A test file in the commit is not evidence the test came first or covers the edge. Git cannot show whether a test failed before the code was written.
5. **The one code signal that survives dividing by size is about published operations** taking a name or path (0.64 per thousand lines). It is still coarse: it is at 0.27 for waves 1 and 2 alone, because `harness/installation`, `scripts`, `harness/diagnostics` and `space/repo` took 50 of those defects through command lines and stored records, not through published operations.
6. **The defect count also follows where the testers were sent.** Round 3 ran every fidelity of every practice, so each practice has 10 to 29 defects whatever its code looks like. No per-module measure can separate that from a real difference between modules, with 17 modules.

The per-module view is therefore the wrong grain. The signals that match the defects are per operation, per format and per story, and the next section checks each one against the defects themselves instead of against a module total.

## Per tag: the signal that would have flagged it, and how many places it flags

"At release" is the code at the tag; "today" is the branch `release-1-2-fixes` at 3c77725bc, after the fixes, over all production code under `harness/`, `space/`, `tools/`, `cdd_guidance/` and `scripts/` (821 files, 86,967 lines).

| Tag | Defects in themes carrying it | Signal tested | Flags at release | Flags today | Usable? |
|---|---|---|---|---|---|
| `unchecked-input` | 27 | A published operation takes a name, title, path or id argument, and its own body neither raises nor calls anything named as a check | 63 of 83 | 62 of 88 | **Too coarse as counted.** The fixes barely moved it, because the checks were added in the objects the operations call (`CardName`, the session's root), not in the operation's body. It becomes usable on the graph: follow the operation's call edges to the first file-system call and ask whether a refusal sits on the way. The test-side form is cheaper: one refusal scenario per such argument. |
| `concurrency` | 12 | A file that writes to disk and never names a lock, a held file, or an atomic replace | 69 of 80 files | 68 of 86 files | **Too noisy.** Most writes are one process writing its own output. Narrowed to state kept through `JsonFile`, 25 of 30 files today never call `held()`: short enough to judge one by one, asking of each "can two processes run this?" |
| `data-loss` | 40 | No single signal. The themes split into a smaller format saved over a fuller file (use the there-and-back spec), an unreadable file read as empty (use the failure-answered-with-a-default count), two writers (use the held-file count), and a save place taken from a name instead of the path given (use the unchecked argument count) | — | — | Covered by the four signals named |
| `lossy-format-trip` | 31 | A format a fidelity declares in its `outputs`, other than its default, that no spec with "trip", "round" or "back" in its file name mentions for that practice | **17 of 31** | 4 of 42 | **Yes, the best signal found.** At release it flagged Java for BDD, `claude_design` for the mockup, TypeScript and JavaScript for front-end code, the thin slice, and every whiteboard: the formats the testers then reported. Today it flags `stories.story_map.thin_slice`, `stories.acceptance_tests.desktop`, `ux.ia.json` and `ux.mockup.claude_design`. It checks only that a spec names the format, not that the spec compares what went in with what came back. |
| `undeclared-output` | 16 | The same count, plus a format offered with no adapter, plus practice files no fidelity declares | 5 of the 17 above had nothing behind them; 15 of 102 Bookshop files undeclared | not recounted | **Yes**, as a graph fact: every format of a fidelity has an adapter and a reading, every practice file is declared |
| `stale-state` | 34 | A production file that keeps a process id | 13 files (today) | 13 files | **Weak.** It finds the record of test runs and the claims, and misses worktrees, the install record and cached line ranges. The real signal is a judgment per stored record: what does each field describe, and what checks it is still there. |
| `false-success` | 32 | A handler that ends by returning a constant, an empty value or nothing, with no raise | 96 of 212 | 99 of 230 | **Usable with a filter.** 99 is too many to fail a validation on, and Clean Engineering's own rule `errors-out-of-existence` asks for a quiet result on ordinary edges, so the rule and this signal pull against each other. Keep only those on the call path of a published operation, and those whose default is "empty" for a file that could not be read. The second cause of this tag, empty input falling through to a quiet answer, has no handler at all and shows only as a missing refusal scenario. |
| `raw-error` | 19 | The same handlers, plus raises of a built-in failure (`ValueError`, `KeyError`, `FileNotFoundError` and the like) | 69 raises | 79 raises | **Partly.** Most raw errors in the report were failures nobody raised at all (`WinError 206`, `TypeError` from a wrongly shaped file), so they show as a missing check on an argument or a file's shape, not as a raise. |
| `name-matching` | 15 | A comparison of the form `.name ==` | 216 | 242 (35 in the graph and reading code) | **Too noisy across the codebase, usable in the reading code.** `space/kanban` alone has 57, nearly all a board finding its own ticket. The measure that fits is on the edge, not the source line: record how each edge's target was found, and count edges found by name alone across a practice or a language. The report's own figure was 15 of 31 BDD links and 51 of 57 story-test links wrong. |
| `rule-template-mismatch` | 11 | A template with no spec that validates it at its fidelity | not counted | 25 templates, no such spec found | **Yes, and cheap:** one shared example run for each template. It covers the two template defects directly; the other themes under this tag (browser tests older than the page, logic decided on the page) need other checks. |
| `display` | 23 | None in the code. The test-side signal is a file kind with no browser story test opening it in each view | — | 29 e2e specs in all today | **Only as test coverage.** No code measure shows that a rendered view drops a stereotype. |
| `regression` | 12 | A production commit with no spec or story test file | 334 of 1,309 | 11 of 155 since the tag | **Weak.** The share fell from 26% to 7% during the fixes and regressions still came, because each was a neighbour's saved answer changing, which only running the unit tier after each pass finds, and it did: all nine defects the automated tiers found were regressions. |
| missing behaviour at the edges (every tag above) | — | A story with one scenario; a story with no scenario about a refusal or failure | 47 and 121 of 197 | 56 and 143 of 265 | **Usable as a prompt, not as a gate.** It is counted from words in scenario titles, so it misreads some. 61% of stories at release had no failure scenario, and 62 of the 146 defects were placed under story tests that were missing. |

## What exists today, after commit 3c77725bc

A class read from code (`CodeClass`, built only by the Python, TypeScript and JavaScript readers) declares these measures as typed fields and saves them with the graph: `method_count`, `operation_shapes` (each operation's name, whether it is a property, whether it is private, and the operations it calls), `property_names`, `constructs`, `prose_comment` and `prototype_swap`. A class read from a markdown model has none of them.

An operation's body answers four measures through `MeasuredBody`: `control_flow_depth` (nesting), `unnamed_numbers`, `catches_everything` and `swallows`. Operations also keep `body_fingerprint` (for duplicated bodies), a statement count, parameters and packed parameters, `raises_on_empty`, `io_and_domain`, `mutates_without_record`, `exception_without_message` and `generic_exception_message`.

So of the backlog item's list, the method count, parameters, a length measure (statements) and nesting depth are already facts. Paths through a function, the readability score, a class's total paths, the classes a class depends on as a count, and cohesion are not. Of Group B, only `catches_everything` and `swallows` exist, and they see 26 of the 99 handlers that answer a default.

## How this was measured, and what could not be

- **Code at two points.** The module tables and correlations use the code at `v1.2.0`, exported with `git archive` to a temporary folder. The "today" counts use the working tree. `harness/diagnostics` shrank after the tag because the record of test runs moved to `harness/release`.
- **Production code** is every `.py`, `.ts`, `.tsx`, `.js`, `.ps1` and `.sh` file in a module's folder that is not a test. A test is a file named `*_spec.py`, `*.spec.ts`, `*.test.*`, `*_examples.py`, `*_tiers.py`, `rule_examples.py` or `*.feature.py`, or any file under `_examples`, `examples`, `fixtures`, `tests`, `test-utils` or `story_tests`. `node_modules`, `dist`, `templates`, `.context` and the pattern `oss_portal_domain_driven` are left out.
- **Tools.** lizard 1.26 gave lines, functions, paths per function and function length for Python and TypeScript. Python's `ast` module gave parameters (not counting `self`), methods per class, functions outside a class, handlers, published operations and a class's total paths (my own count: 1 for each method plus 1 for each `if`, loop, handler, conditional expression, comprehension and extra `and`/`or`). The earlier gate, [.context/model/repo-review/metrics_gate.py](../../../../.context/model/repo-review/metrics_gate.py), and its virtual environment at `~/.cdd/metrics/venv` (radon, complexipy, cohesion, grimp) were found and not run.
- **Not measured:** the readability score (cognitive complexity), cohesion, and the classes each class depends on. Classes over 30 methods and over 100 total paths are Python only. PowerShell and shell scripts have lines only.
- **Comparisons on a name** are lines matching a variable or attribute whose name contains `name` beside `==`, `!=`, `===` or `!==`, a `.get(name)` call, or `by_name`. It counts lines, and it counts innocent comparisons.
- **File writes** are calls to `write_text`, `write_bytes`, `json.dump`, `open` for writing, `writeFileSync`, and file copies, moves, renames and removals. "No lock or atomic replace" means the file's text nowhere holds `lock`, `held(`, `os.replace` or `atomic`.
- **A check in an operation's own body** means a `raise`, or a call to something whose name holds `check`, `valid`, `require`, `refuse`, `ensure`, `within`, `inside`, `resolve`, `safe`, `exists`, `is_file`, `is_dir`, `relative_to` or `parsed`. A check one call further down is not seen.
- **A failure scenario** is a scenario whose title holds a word such as refuse, reject, fail, missing, unknown, empty, cannot, wrong, already, twice, gone, damaged, outside, nothing, without, never or not.
- **Git.** `git log --name-only` over the 60 days to today, split at the tag. A commit "has a test" when any file in it is a test by the rule above or sits under `story_tests`.
- **Defects per tag** were added up from the themes' defect counts; three themes whose names differ between the report's two tables were matched by hand. A theme with three tags gives its defects to all three.
- **Limits of the comparison.** Seventeen modules, 53 measures, defects counted once for each module a theme names, and testing effort that differed by module. No measure here is proven to predict defects. The strongest evidence is not a correlation: it is that the there-and-back count, run on the release's code, names the formats the testers then found broken.
- **Scratch scripts** are in the session's temporary folder, outside the repository, and nothing in the repository was changed apart from this file.
