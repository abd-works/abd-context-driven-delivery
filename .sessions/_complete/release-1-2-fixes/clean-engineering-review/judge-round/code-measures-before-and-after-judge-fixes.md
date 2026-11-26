# Code measures before and after the judge-led fixes

**Measured again 2026-11-22, every figure in one run.** An earlier version of this report counted every folder of code as a module, packages included, scored modules with radon's maintainability index, counted a method that uses no field of its class as a group of its own, held parameters to 5 under the retired `limit-function-parameters`, and left JavaScript unmeasured. Every figure below replaces it, taken in one run on both commits with this branch's measuring code: `measure_checkout.py`, in [../scripts](../scripts/measure_checkout.py), with lizard 1.26.1 installed into a folder outside the repository and put on PYTHONPATH, on each commit extracted with `git archive` into a folder of its own. lizard measures Python, TypeScript and JavaScript alike. radon and the maintainability score are dropped, so the report has no maintainability rows.

What Clean Engineering's limit rules report on the production Python, TypeScript and JavaScript under `harness/`, `space/`, `tools/`, `cdd_guidance/` and `scripts/`, before and after the judge-led reshape. Each count is of the rule's violations in the validation of that checkout: the script runs the Validate action at the code fidelity on those five folders and counts what the graph rules found, with the shipped limits. The paths through a function, its readability score and a class's total complexity are supplied by lizard; a function's lines and parameters, a class's methods, and a module's imports are facts the reader keeps on every read, with no tool. Specs, fixtures, examples, templates and the `oss_portal_domain_driven` pattern are left out.

A module is a folder that owns `.context/module-context.md`. A folder without one is a package, a part of the nearest module above it: a module is measured over its own files and its packages' files, and its imports are those of all of them to other modules, a child module with a module card of its own among them. An import between a module's own files and packages is not counted.

- **Before:** commit `33b3839e3` (2026-11-21 16:54), which holds the seven judges' findings and changes no code. It is the commit just before the first judge-led fix, `631e9b19d` (17:03).
- **After:** commit `3c77725bc` (2026-11-22 00:31), the last commit of the judge-led reshape: the local fixes, the 25 merged proposals, and rounds three and four. The two removals that follow it on 2026-11-22 (the chat bar's browser test page and the desktop walk) are deletions the person ordered, not judge fixes, so they are left out.

| | Before | After |
| --- | --- | --- |
| Production files with a measured function or class | 648 | 676 |
| Functions measured | 10498 | 10893 |
| Classes measured | 1671 | 1776 |
| Modules measured (folders that own a module card) | 43 | 56 |

## Past its limit, for each measure

A lower count is better. The share is of the functions or classes that hold the measure, since the code grew between the two commits.

| Measure | Graph rule | Read from | Limit | Past the limit before | Past the limit after | Change | Share before | Share after |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Paths through a function (cyclomatic complexity) | `limit-paths-through-a-function` | lizard | 10 | 115 | 117 | <span style="color:#cf222e">**worse**</span> (+2) | 1.1% | 1.1% |
| Readability score of a function (cognitive complexity; higher is harder to read) | `keep-functions-readable` | lizard | 15 | 9 | 14 | <span style="color:#cf222e">**worse**</span> (+5) | 0.1% | 0.1% |
| Lines in a function | `limit-function-lines` | the `line_count` fact every read keeps | 50 | 5 | 6 | <span style="color:#cf222e">**worse**</span> (+1) | 0.0% | 0.1% |
| Parameters a function takes | `limit-operation-parameters` | the function's parameter nodes | 3 | 72 | 95 | <span style="color:#cf222e">**worse**</span> (+23) | 0.7% | 0.9% |
| Total complexity of a class (the paths through all its methods, added up) | `limit-class-complexity` | lizard | 100 | 18 | 17 | <span style="color:#1a7f37">**better**</span> (-1) | 1.2% | 1.1% |
| Methods in a class | `limit-class-methods` | the `method_count` fact every read keeps | 30 | 18 | 16 | <span style="color:#1a7f37">**better**</span> (-2) | 1.1% | 0.9% |
| Groups of methods in a class that share no data with one another (lack of cohesion) | `keep-class-methods-sharing-data` | the practice's own reader, Python only | 1 | 201 | 211 | <span style="color:#cf222e">**worse**</span> (+10) | 22.9% | 22.6% |

## Measures kept for information, with no limit of their own

| Measure | Before | After | Change |
| --- | --- | --- | --- |
| Loops of modules importing one another, added up over every module | 2 | 4 | <span style="color:#cf222e">**worse**</span> (+2) |
| Classes a class depends on (coupling between objects), on average | 0.9 | 1.0 | <span style="color:#cf222e">**worse**</span> (+0.1) |
| Modules a module imports (outgoing coupling), on average | 5.0 | 5.3 | <span style="color:#cf222e">**worse**</span> (+0.3) |
| Modules that import a module (incoming coupling), on average | 5.0 | 5.3 | <span style="color:#cf222e">**worse**</span> (+0.3) |

## The ten worst functions after

By the paths through each (cyclomatic complexity).

| Function | File | Paths through it | Readability score (cognitive complexity) | Lines | Parameters |
| --- | --- | --- | --- | --- | --- |
| `_walk` | `cdd_guidance/practices/clean_engineering/reading/code_file.py:606` | 30 | 30 | 36 | 2 |
| `_class_lines` | `cdd_guidance/actions/render/reshaped_code.py:255` | 28 | 5 | 26 | 2 |
| `_whiteboard` | `cdd_guidance/actions/render/kept_document.py:106` | 20 | 7 | 18 | 2 |
| `record` | `cdd_guidance/practices/clean_engineering/reading/module_exposure.py:48` | 18 | 5 | 18 | 0 |
| `SourceEditor` | `harness/graph/app/source/SourceView.tsx:87` | 18 | 11 | 50 | 0 |
| `onto` | `cdd_guidance/practices/bdd/model/spec_reshape.py:123` | 17 | 5 | 15 | 2 |
| `_layers` | `cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py:168` | 17 | 10 | 18 | 0 |
| `_typed_head` | `cdd_guidance/practices/clean_engineering/reading/code_file.py:656` | 17 | 27 | 26 | 2 |
| `_under_heading` | `cdd_guidance/practices/stories/model/story_tree.py:214` | 17 | 5 | 11 | 4 |
| `_drawio` | `cdd_guidance/actions/render/kept_document.py:69` | 16 | 4 | 14 | 2 |

## The ten worst classes after

By total complexity (the paths through all a class's methods, added up).

| Class | File | Total complexity | Methods | Classes it depends on | Groups of methods sharing no data |
| --- | --- | --- | --- | --- | --- |
| `RecipeExpansion` | `harness/agent_tools/recipe.py:256` | 194 | 48 | 0 | 1 |
| `_SpanCalls` | `cdd_guidance/practices/clean_engineering/reading/code_file.py:452` | 176 | 23 | 0 | 1 |
| `TypeAnnotations` | `cdd_guidance/practices/ux/model/view/front_end_view.py:295` | 152 | 34 | 0 | 1 |
| `FilesPage` | `harness/files_app/app/files/files-page.ts:33` | 142 | 29 | 1 | not measured |
| `FidelityGuidance` | `harness/guidance/guidance.py:597` | 142 | 54 | 10 | 1 |
| `CFamilyParse` | `cdd_guidance/practices/clean_engineering/model/c_family_parse.py:83` | 135 | 40 | 2 | 1 |
| `Aggregate` | `cdd_guidance/practices/ddd/model/nodes.py:172` | 130 | 29 | 5 | 1 |
| `ArrowRouter` | `cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py:624` | 129 | 28 | 1 | 1 |
| `CodeStoryMap` | `cdd_guidance/practices/stories/model/code_story_map.py:385` | 128 | 32 | 4 | 1 |
| `PracticeSchema` | `harness/graph/schema_rules.py:27` | 111 | 32 | 2 | 1 |

## The ten worst modules after

By the modules each imports (outgoing coupling), then by the modules that import it. A module's imports are those of its own files and of the packages inside it.

| Module | Modules it imports | Modules that import it | Import loops it is part of |
| --- | --- | --- | --- |
| `space/kanban` | 17 | 1 | 0 |
| `scripts` | 16 | 0 | 0 |
| `space/session` | 15 | 6 | 0 |
| `cdd_guidance/practices/stories` | 14 | 6 | 0 |
| `cdd_guidance/actions` | 12 | 3 | 0 |
| `cdd_guidance/practices/ux` | 12 | 1 | 0 |
| `cdd_guidance/practices/clean_engineering` | 11 | 8 | 1 |
| `space/session/practices` | 10 | 2 | 0 |
| `cdd_guidance/practices/ddd` | 9 | 5 | 1 |
| `cdd_guidance/align` | 9 | 0 | 0 |

## How to read this

- The counts are of nodes past a limit, not of how far past. A function split in two, each still over the limit, counts twice.
- The code grew by 28 measured production files between the two commits, so the share columns say more than the counts.
- The parameter count is the rule's, with its exemptions: creation and mapping factories, operations published as tools, and an external system's verified contract are not reported.
- A method that uses no field of its class is not counted as a group of methods sharing no data: it holds no data, so it is no second job the class does. Only Python classes are read for this measure, so a TypeScript or JavaScript class shows "not measured".
- Blocks of code copied across files are not measured: no tool is chosen for it yet.
- The numbers come from one validation of each commit on one machine; the tools are deterministic, so a second run gives the same numbers.
