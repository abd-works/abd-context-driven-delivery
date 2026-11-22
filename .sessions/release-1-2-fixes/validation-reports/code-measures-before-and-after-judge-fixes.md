# Code measures before and after the judge-led fixes

What Clean Engineering's seven limit rules report on the production Python and TypeScript under `harness/`, `space/`, `tools/`, `cdd_guidance/` and `scripts/`, before and after the judge-led reshape. Each number is a count of the rule's violations in the validation of that checkout: `measure_checkout.py`, beside this file, runs the Validate action at the code fidelity on those five folders and counts what the graph rules found, with the shipped limits. The paths through a function, its readability score and a class's total complexity are supplied by lizard 1.26.1 and a module's maintainability score by radon 6.0.1; a function's lines and parameters and a class's methods are facts the reader keeps on every read, with no tool. Specs, fixtures, examples, templates and the `oss_portal_domain_driven` pattern are left out. Written on 2026-11-22.

- **Before:** commit `33b3839e3` (2026-11-21 16:54), which holds the seven judges' findings and changes no code. It is the commit just before the first judge-led fix, `631e9b19d` (17:03).
- **After:** commit `3c77725bc` (2026-11-22 00:31), the last commit of the judge-led reshape: the local fixes, the 25 merged proposals, and rounds three and four. The two removals that follow it on 2026-11-22 (the chat bar's browser test page and the desktop walk) are deletions the person ordered, not judge fixes, so they are left out.

| | Before | After |
| --- | --- | --- |
| Production files with a measured function or class | 648 | 676 |
| Functions measured | 10498 | 10893 |
| Classes measured | 1671 | 1776 |
| Modules measured (folders of code) | 159 | 172 |

## Past its limit, for each measure

A lower count is better. The share is of the functions or classes that hold the measure, since the code grew between the two commits.

| Measure | Graph rule | Read from | Limit | Past the limit before | Past the limit after | Change | Share before | Share after |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Paths through a function (cyclomatic complexity) | `limit-paths-through-a-function` | lizard | 10 | 113 | 115 | <span style="color:#cf222e">**worse**</span> (+2) | 1.1% | 1.1% |
| Readability score of a function (cognitive complexity; higher is harder to read) | `keep-functions-readable` | lizard | 15 | 9 | 14 | <span style="color:#cf222e">**worse**</span> (+5) | 0.1% | 0.1% |
| Lines in a function | `limit-function-lines` | the `line_count` fact every read keeps | 50 | 5 | 6 | <span style="color:#cf222e">**worse**</span> (+1) | 0.0% | 0.1% |
| Parameters a function takes | `limit-function-parameters` | the function's parameter nodes | 5 | 11 | 15 | <span style="color:#cf222e">**worse**</span> (+4) | 0.1% | 0.1% |
| Total complexity of a class (the paths through all its methods, added up) | `limit-class-complexity` | lizard | 100 | 18 | 17 | <span style="color:#1a7f37">**better**</span> (-1) | 1.2% | 1.1% |
| Methods in a class | `limit-class-methods` | the `method_count` fact every read keeps | 30 | 18 | 16 | <span style="color:#1a7f37">**better**</span> (-2) | 1.1% | 0.9% |
| Groups of methods in a class that share no data with one another (lack of cohesion) | `keep-class-methods-sharing-data` | the practice's own reader, Python only | 1 | 382 | 432 | <span style="color:#cf222e">**worse**</span> (+50) | 40.9% | 43.0% |

## Measures kept for information, with no limit of their own

| Measure | Before | After | Change |
| --- | --- | --- | --- |
| Loops of modules importing one another, added up over every module (reported by `one-way-deps`) | 10 | 4 | <span style="color:#1a7f37">**better**</span> (-6) |
| Classes a class depends on (coupling between objects), on average | 1 | 1 | no change |
| Maintainability score of a module's hardest file (maintainability index, 0 to 100; higher is easier to maintain), on average | 47.9 | 47.2 | <span style="color:#cf222e">**worse**</span> (-0.7) |
| Modules whose hardest file scores under 20 on maintainability | 28 | 27 | <span style="color:#1a7f37">**better**</span> (-1) |
| Modules a module imports (outgoing coupling), on average | 3.1 | 3.5 | <span style="color:#cf222e">**worse**</span> (+0.4) |
| Modules that import a module (incoming coupling), on average | 3.5 | 3.9 | <span style="color:#cf222e">**worse**</span> (+0.4) |

## The ten worst functions after

By the paths through each (cyclomatic complexity).

| Function | File | Paths through it | Readability score (cognitive complexity) | Lines | Parameters |
| --- | --- | --- | --- | --- | --- |
| `_walk` | `cdd_guidance/practices/clean_engineering/reading/code_file.py:606` | 30 | 30 | 36 | 2 |
| `_class_lines` | `cdd_guidance/actions/render/reshaped_code.py:255` | 28 | 5 | 26 | 2 |
| `_whiteboard` | `cdd_guidance/actions/render/kept_document.py:106` | 20 | 7 | 18 | 2 |
| `SourceEditor` | `harness/graph/app/source/SourceView.tsx:87` | 18 | 11 | 50 | 0 |
| `record` | `cdd_guidance/practices/clean_engineering/reading/module_exposure.py:48` | 18 | 5 | 18 | 0 |
| `_under_heading` | `cdd_guidance/practices/stories/model/story_tree.py:214` | 17 | 5 | 11 | 4 |
| `_typed_head` | `cdd_guidance/practices/clean_engineering/reading/code_file.py:656` | 17 | 27 | 26 | 2 |
| `_layers` | `cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py:168` | 17 | 10 | 18 | 0 |
| `onto` | `cdd_guidance/practices/bdd/model/spec_reshape.py:123` | 17 | 5 | 15 | 2 |
| `proseAt` | `harness/graph/app/source/call-expansion.ts:239` | 16 | 15 | 9 | 3 |

## The ten worst classes after

By total complexity (the paths through all a class's methods, added up).

| Class | File | Total complexity | Methods | Classes it depends on | Groups of methods sharing no data |
| --- | --- | --- | --- | --- | --- |
| `RecipeExpansion` | `harness/agent_tools/recipe.py:256` | 194 | 48 | 0 | 1 |
| `_SpanCalls` | `cdd_guidance/practices/clean_engineering/reading/code_file.py:452` | 176 | 23 | 0 | 1 |
| `TypeAnnotations` | `cdd_guidance/practices/ux/model/view/front_end_view.py:295` | 152 | 34 | 0 | 1 |
| `FidelityGuidance` | `harness/guidance/guidance.py:597` | 142 | 54 | 10 | 5 |
| `FilesPage` | `harness/files_app/app/files/files-page.ts:33` | 142 | 29 | 1 | not measured |
| `CFamilyParse` | `cdd_guidance/practices/clean_engineering/model/c_family_parse.py:83` | 135 | 40 | 2 | 1 |
| `Aggregate` | `cdd_guidance/practices/ddd/model/nodes.py:172` | 130 | 29 | 5 | 1 |
| `ArrowRouter` | `cdd_guidance/practices/clean_engineering/model/diagram/class_layout.py:624` | 129 | 28 | 1 | 1 |
| `CodeStoryMap` | `cdd_guidance/practices/stories/model/code_story_map.py:385` | 128 | 32 | 4 | 2 |
| `PracticeSchema` | `harness/graph/schema_rules.py:27` | 111 | 32 | 2 | 1 |

## The ten worst modules after

By the maintainability score of each module's hardest file (maintainability index, 0 to 100; lower is harder to maintain), then by the modules it imports. Only Python is scored.

| Module | Maintainability score of its hardest file | Modules that import it | Modules it imports | Import loops it is part of |
| --- | --- | --- | --- | --- |
| `space/kanban` | 0 | 1 | 17 | 0 |
| `cdd_guidance/practices/stories/model` | 0 | 14 | 13 | 1 |
| `harness/graph` | 0 | 37 | 7 | 0 |
| `cdd_guidance/practices/clean_engineering/reading` | 0 | 5 | 6 | 0 |
| `harness/agent_tools` | 0 | 61 | 4 | 0 |
| `harness/installation` | 0 | 49 | 4 | 0 |
| `cdd_guidance/practices/clean_engineering/model/diagram` | 0 | 3 | 4 | 0 |
| `cdd_guidance/practices/ddd/model` | 0 | 8 | 4 | 0 |
| `harness/markdown` | 0 | 21 | 1 | 0 |
| `cdd_guidance/practices/ux/model/view` | 0 | 0 | 1 | 0 |

## How to read this

- The counts are of nodes past a limit, not of how far past. A function split in two, each still over the limit, counts twice.
- The code grew by 28 measured production files between the two commits, so the share columns say more than the counts.
- A group of methods sharing no data counts a method that uses no field of its object as a group of its own, so a class with one such helper is reported. That is why this count is far above the others.
- JavaScript files have no tool chosen for the measures a tool supplies. The rules report each such file by name, once for each measure, and those reports are left out of the counts above: 16 files before and 15 after.
- Blocks of code copied across files are not measured: no tool is chosen for it yet.
- The numbers come from one validation of each commit on one machine; the tools are deterministic, so a second run gives the same numbers.
