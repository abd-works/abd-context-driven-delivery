# What caused the defects of release 1.2 — guidance, tools and measures (2026-11-22)

CDD is built with its own guidance, so each defect of [defect-themes-by-wave.md](defect-themes-by-wave.md) was written by an agent following a practice, an action or no guidance at all. This page answers three questions and rests on three research files, each with its evidence and its limits:

- [analysis/provenance.md](analysis/provenance.md): which guidance and tools were in use when the defective code was written
- [analysis/guidance-gaps.md](analysis/guidance-gaps.md): what the guidance says, and does not say, about each kind of defect and each evaluation finding
- [analysis/code-metrics.md](analysis/code-metrics.md): which measures of the code move with the defects

Counts by tag overlap, because a theme carries up to three tags.

## 1. What produced the defective code

133 of the 156 defect files were traced with `git blame` to 77 commits, and 57 of those commits to the chat that made them.

| How the code was produced | Commits (of 77) | Defects (of 133) |
|---|---|---|
| A chat that called `validate` at Clean Engineering model or code | 44 | 77 |
| The same, with `generate` never called: refactoring to clear rule findings | 28 | 57 |
| `generate` at Stories scenarios or acceptance tests | 14 | 24 |
| No `generate` and no `validate`: plain chat coding | 11 | 20 |
| BDD development named in a call (BDD behavior never) | 2 | 6 |
| No chat could be matched (most are older than 2026-10-26) | 20 | 28 |

- **The largest single source is refactoring to satisfy Clean Engineering.** The refactoring rounds account for 21 commits and 40 defects. Sub-agents cleared findings and called only `validate`; rounds 3 to 9 had 330 sub-agent launches and 6,596 sub-agent edits against 205 by the lead chat. Behaviour was reshaped with no scenario stating what it had to keep doing.
- **Plain chat coding holds most `concurrency` and `raw-error` defects.** The record of test runs and the opening of a ticket were written with no guidance call.
- **Tests were present and did not help.** 54 of the 77 commits changed a spec in the same module and 22 changed a heavy spec. The tests covered the path the author had in mind.
- **The TDD supplement came too late for most of it.** 47 of the 77 commits are older than the supplement (2026-11-15), and no call ever named it. The prompt queue and the Files app were written after it and still had 29 defects between them.
- **`render` wrote none of the defective functions.** The defects in formats are in the adapters agents wrote, not in code an adapter produced.

### By kind of defect

| Tag | Where the code came from | Guidance at fault |
|---|---|---|
| `unchecked-input` | Half from refactoring rounds with `validate` only | Nothing asks for a bad, empty or oddly spelled input to be specified or refused |
| `concurrency` | Plain chat coding by the lead chat | Nothing asks what happens with a second caller |
| `stale-state` | Refactoring rounds and plain chat coding | Nothing asks that a kept record be checked against the thing it describes |
| `false-success` | Refactoring rounds, 9 commits by sub-agents | Clean Engineering's `errors-out-of-existence` tells authors to answer a quiet empty result |
| `raw-error` | Plain chat coding | No rule asks that a failure name the file or argument at fault |
| `data-loss` | Render's saved file, written by a sub-agent the day before testing; the ticket's close | No scenario for a render that meets a file already there; generate's step 6 says the scaffold wins |
| `lossy-format-trip`, `undeclared-output` | Format adapters, and formats offered in practice markdown with no adapter | No practice owns its formats: nothing asks for an adapter, or a there-and-back test, for each format a fidelity declares |
| `name-matching` | The practices' graph readings, last written in refactoring rounds | No guidance on joining graph nodes by identity |
| `rule-template-mismatch` | A rule, its template and its reader each changed in a different commit by a different chat | Nothing runs a template through its own fidelity's validate |
| `display` | Session `file-manager`, after `generate` at Stories fidelities, with UX turned off | TDD does not supplement UX front-end code; nothing says which stories need a browser test |
| `regression` | Fixes in this session, each with tests for its own change only | Nothing asks a fix to run the neighbours it touches |

## 2. The shortcomings in the guidance

Most important first. The first seven let the defects through; the last three produced the evaluation findings that had to be fixed besides defects.

1. **The guidance forbids behaviour the source does not describe, and nothing asks about the edges.** `do-not-invent-requirements` and generate's step 2b hold scenarios to what the source says. The list of edges to try (odd names, two callers, a damaged file) exists only in the exploratory tester's brief. This let through `unchecked-input`, `concurrency`, `stale-state` and `raw-error`.
2. **`errors-out-of-existence` asks for a quiet empty answer and no rule separates "nothing there" from "unreadable" or "did less than asked".** This let through `false-success` and the files read as empty and then written over.
3. **No practice owns its formats.** This let through `lossy-format-trip`, `undeclared-output` and most of `data-loss`.
4. **Every coverage rule is prose only.** `explore-full-interaction-surface`, `full-surface-coverage` and the TDD supplement's proving-test rules have no check; the supplement has 1 mechanical check for 35 rules. The unit tier should have caught 103 of the 146 defects and caught 6.
5. **Refactoring runs under `validate` alone.** A round that clears Clean Engineering findings has no step that states the behaviour to keep, so the rules it satisfies are the only thing it is checked against.
6. **Nothing says which tier a story needs.** The server tier and the browser tier are file-name patterns only, and the implementation agent's brief asks only for red-green-refactor.
7. **The TDD supplement is not in any call.** It is installed as an always-on rule, and no `generate` or `validate` call hands it over.
8. **A rule, its template, its check and its numbers sit apart.** One schema rule that the scenarios template itself fails made 662 of the 1,193 distinct graph findings. The child-count band is written in five places, which is how "7 children (target 2-6)" was reported against a band of 3-9.
9. **Word-matching scanners stand in for judgment.** The finding on a story name ending in "once" and 85 graph hits judged as noise came from these, many from code rules run on model documents.
10. **The Clean Engineering rules the judges found broken most have no check.** There were 1,092 judged findings against 373 distinct graph findings for Clean Engineering code; `hold-state-on-the-object-not-in-parameters`, `put-logic-on-the-owning-resource` and `single-boundary` are prose only.

What could not be established: which rule each defective line was written under, the exact number of defects for each tag, and the original report of the render that removed code.

## 3. Measures of the code

- **Size and complexity do not explain the defects.** Across 17 modules, lines of code move loosely with the defect count (rank correlation 0.56) and the share of functions over 10 paths does not (0.26). The release had 91 of 12,488 functions over 10 paths and shipped 146 defects.
- **The amount of testing did not protect.** Spec lines for each production line show no relation to defects (0.02). `actions` has 2.2 spec lines for each code line, 13 heavy specs, and the highest defect rate, 12.8 for each thousand lines.
- **The best signal found is on a fidelity, not a function.** A count of formats a fidelity declares with no there-and-back test flags 17 of 31 on the release code and 4 of 42 after the fixes.
- With 17 modules and 53 measures tried, each correlation is a hint, not proof.

The person's decisions on 2026-11-22, recorded in the backlog item [measure-code-on-the-model.md](../../_backlog/measure-code-on-the-model.md):

- The function and class measures of the backlog item, and the module measures of the older script, are taken on validate. Each node read from code collects each measure through a tool chosen for that measure and language. The mapping is kept in the CDD config file, filled in for Python and TypeScript, and a language with no tool chosen fails. Graph rules raise errors past the limits.
- From the defect analysis, one module measure is kept: defects for each thousand lines, measured for a branch when its defects are captured and wiped on the next merge to main. The other proposed measures are left out.
