# Validation trend, rounds 1–9

**Where it stands (2026-11-08, after round 9):**
- In the scope round 8 checked, the goal total is **27**, under the target of 30. Round 5 had 150, so 82% are gone.
- The full total rose from 31 to **56**. 29 of the 56 are new scope: the graph check ran in all six areas for the first time, and the validators used the code metrics as evidence for the first time.
- Only 3 of round 8's findings are left. The fixes work; the rise comes from looking harder.
- **One high finding in the goal classes keeps the loop open:** the UX explorer crash on a reopened graph, the same fault as round 8's Stories crash in a sibling reader.
- **Round 9's fixes:** that high, the 4 regressions, and splitting the oversized classes (`Graph`, `PracticeGuidance`, `GraphReading`, `PracticeNodes`, `CodeStoryModel`, `Ticket`). Every fix must pass the metrics gate against 5f36e6a2.

How many findings each validation round on `ensure-domain-orientation-refactor` produced, and how severe they were. Severity follows the same scale in every round:
- **high:** wrong behaviour, or a second object model
- **medium:** a rule plainly broken
- **low:** naming or documentation

Rounds 1 and 2 wrote several findings to a bullet, so their counts are ranges. The low end counts one finding per tagged bullet; the high end counts one per sub-item.

## By round

| Round | Commit | How it checked | Findings | High | Medium | Low | New / carried |
|---|---|---|---|---|---|---|---|
| 1 | `d6c41b23` | AI judge on every rule at the modules, model and code fidelities, plus a cross-file pass (63 reports) | 64–114 | 21–41 | 36–58 | 7–15 | all new |
| 2 | `d6c41b23` | Same method on the six practice folders and the module cards (53 reports) | 23–44 | 13–21 | 5–11 | 1–5 | not marked; a few repeat round 1 |
| 3 | `42ab935c` | Same method again, plus a whole-repository cross-file pass (130 reports) | 38–48 | 16 | 20–30 | 2 | 23 new, 5 left, 3 both, 7 unmarked |
| 4 | `d589b161` | Relationship review: five agents read the code behind all 921 runtime relationships and 832 classes. Graded right, wrong shape or no use, not by severity | 363 wrong-shape relationships, 19 classes with no use | — | — | — | 84 earlier verdicts overturned |
| 5 | `d71e0b20` | Six AI agents for twelve concerns that span files; recipes expanded and measured; graph rules in five of six areas; an end-to-end test | 170 | 21 | 99 | 50 | ~70% new, ~15% left from round 4, ~12% known skips |
| 6 | `b91a73eb` | Same twelve concerns; graph check mostly lost to B10 (the server stalled on graph builds) | 133 | 12 | 66 | 55 | 58 new, 67 left, 2 regressions, 12 new scope |
| 7 | `c8921451` | Same twelve concerns; graph check blocked by a DDD crash in the graph worker, so mostly the AI check | 54 | 4 | 17 | 33 | left and new about evenly; no regressions |

## Wrong behaviour (the bugs) by round

| Round | Wrong-behaviour findings | What kind |
|---|---|---|
| 1 | 19 (B1–B18, B34) | MCP host crashes and pile-ups, data erased (`config.json`), hooks logging into the wrong session, recipe failures hidden |
| 2 | 15 (B19–B33) | Imports of deleted code, format round trips losing data, rules that could never fire |
| 3 | 17 (11 high) | Round trips still losing data, paths resolved against the server's folder, malformed files read as empty |
| 4 | not graded | — |
| 5 | about 10 high | Actions sending prompts with text missing; the server stalling on a graph validate; the graph going empty after a ticket switch; hooks reading the wrong install; draw.io rules never firing |
| 6 | 12 high | Round-5 fixes that broke things (a premature "generate done", `partition`/`repair` failing on optional arguments, a new import cycle); B10 still stalling the server; a stale hook daemon keeping hooks dead after an update; session tools losing the calling chat |
| 7 | 4 high | The DDD crash in the graph worker (from the round-6 merge); 12 rules that never run because the schema lists them on the wrong node types; a validate that reported clean code as clean |

## What the trend shows

- **Bugs are falling, and changing kind.**
  - Rounds 1–3 found the system losing or corrupting data and the server falling over.
  - Round 5's bugs are narrower: missing prompt text, one stall under load, and one regression from the single-graph change.
- **The high count has levelled off, not fallen to zero:** 21–41, then 13–21, then 16, then 21.
  - Each round looked somewhere new. Round 2 covered the practices, round 3 the whole repository, round 4 every relationship, and round 5 problems that show only across files.
  - In round 5, 12 of the 21 high findings are structural: import cycles, second object models and duplicate registries. Only about 10 are behaviour.
- **Medium and low findings rose in round 5 (99 and 50),** because it was the first round to grade every cross-file duplication and every TypeScript rule that belongs in Python. Rounds 1–3 mostly left those as untagged lists.
- **Problems come back.**
  - Round 3 found four mistakes the corrections logs had recorded back in the code, among them B6 (a malformed file overwritten) and B31/B34 (relative paths).
  - Round 5 carries about 30% from earlier rounds: 23–29 left from the round 4 review, plus 18–23 known skips.
  - The skips cluster in three places: DDD's second object model, the Clean Engineering companion per fidelity, and the chat bar's format.
- **Each round's fixes held where they had specs.**
  - Round 3 confirmed 10 round-1 bugs and about 14 structural fixes as fixed.
  - The repeats were all in code no spec covered: hooks, relative paths, and round trips with no round-trip spec.
  - This is why the round-5 fix agents write the failing spec before each fix.
- **The graph scanners missed real cycles in round 5.** Every cycle they reported came from spec or `_examples` imports. But the metrics run ([code-metrics-trend.md](code-metrics-trend.md)) found 11 real import cycles at `d71e0b20`, closed by imports written inside functions, which the folder-level scanner could not see. The round-5 fixes removed 9 of them and fixed the scanner.

## Round 5 by area

| Area | Findings | High | Medium | Low |
|---|---|---|---|---|
| harness core | 35 | 2 | 21 | 12 |
| harness upper | 28 | 4 | 19 | 5 |
| space and tools | 29 | 2 | 18 | 9 |
| actions, patterns, context setup | 25 | 6 | 10 | 9 |
| Clean Engineering, BDD | 29 | 4 | 17 | 8 |
| Stories, UX, DDD | 22 | 2 | 13 | 7 |
| end-to-end test (B10, B11) | 2 | 1 | 1 | 0 |

Sources:
- `.sessions/ensure-domain-orientation-refactor/clean-engineering-validation.md` (rounds 1–2)
- `clean-engineering-validation-round3.md` (round 3)
- `README.md` and its area files (round 4)
- `round5-report.md` (round 5)

## Fix-and-revalidate loop: goal, measure, and stopping rule

From round 5 on, each round runs validate, writes a report, has agents fix it, and is then measured here. The loop's goal is to remove most findings in three classes:
- **bad resource orientation:** concern 5, wrong-shape relationships, and concern 9, one file with several owners
- **shadow models:** concern 2, duplicated shapes and second object models
- **duplicated functions:** concern 1, plus concern 12, rules decided in both TypeScript and Python

**How it is measured.** The script counts every finding row in a round's area files by the concerns it carries, using the same script every round so the numbers compare (`concern_counts.py` beside this file; a row naming several concerns counts once for each). Rounds 6 on use round 5's twelve concerns, area split and status words (new / left / known skip / regression), so the counts mean the same thing.

**Round 5 baseline:**

| Goal class | Concerns | Round 5 |
|---|---|---|
| Bad resource orientation | 5, 9 | 63 |
| Shadow models | 2 | 30 |
| Duplicated functions | 1, 12 | 57 |
| **Goal total** | | **150** |

The first count gave 163, because it also counted round 5's summary tables of concerns. The counter now counts only finding rows: rows with a concern and a severity, read from a severity column or from the row's id (H1, R6-M4). That gives 150, the baseline.

**Done when** the goal total is below 30 (under a fifth of round 5's 150) and no high finding remains in the three classes. The user set this target on 2026-11-08; it replaced the first target of 81.

**What counts as cycling, and what to change when it happens.** After each round, compare it with the round before:
- **Each round should cut the goal total by at least 20%.** If it doesn't, change the fix brief, not just the code. Find which findings were reported again:
  - **The same finding reported again** means the fix was skipped or reverted. Make it a named task with a spec that fails first.
  - **A new finding of an old kind** means the guardrails missed it. Add the pattern to `refactor-guardrails.md`.
- **Watch the share of regressions.** These are findings marked fixed in an earlier round that are back. If more than 10% of a round's findings are regressions, each fix agent's brief adds a grep-based check for the earlier patterns before it commits.
- **A finding the fix agents skip twice** goes into a decision record, with the reason, and leaves the count. That way a deliberate decision does not keep the loop running.
- **New scope is counted separately from progress.** A round that checks more code (for example, a scanner that now sees cycles between files) reports its findings in the newly checked code in their own column, so a wider check does not hide progress.

| Round | Bad resource orientation | Shadow models | Duplicated functions | Goal total | Change from last round | Regressions | Notes |
|---|---|---|---|---|---|---|---|
| 5 | 63 | 30 | 57 | 150 | baseline | — | First cross-file round. Nine fix agents ran on it |
| 6 | 56 | 18 | 36 | 110 | −27% | 1 (0.9%) | 133 findings, 12 high. Shadow models −40%, duplicated functions −37%, resource orientation only −11%. See [round6-report.md](round6-report.md) |
| 7 | 16 | 3 | 20 | 39 | −65% | 0 | 54 findings, 4 high. Mostly the AI check only, since a DDD crash in the graph worker blocked graph checks. See [round7-report.md](round7-report.md) |
| 8 | 12 | 4 | 15 | 31 (21 old scope) | −21% (old scope −46%) | 1 | 43 findings, 4 high. The graph check ran in three areas; 10 findings are new scope. A Stories crash on a restored graph blocked the rest. See [round8-report.md](round8-report.md) |
| 9 | 30 (9 old scope) | 3 (1) | 23 (17) | 56 (27 old scope) | +81% (old scope +29%) | 4 (6.5%) | 62 findings, 3 high. The graph check ran in all six areas; 29 goal findings are new scope. Only 3 round-8 findings are left; 20 are new findings in code that existed at round 8. All 4 regressions come from the round-8 graph hotfix, merged before the metrics gate existed. See the round9-*.md files |

**Code metrics beside the findings.** [code-metrics-trend.md](code-metrics-trend.md) measures the code at each round with standard tools, and marks every number better, worse or about the same. The numbers that track bad resource orientation are:
- classes that depend on more than 14 other classes (43 now)
- the share of classes doing several unrelated jobs (about half)
- modules that import each other in a loop (none since round 7)
- the most modules importing one single module (60)
- the total complexity of the biggest classes, `Graph` and `PracticeGuidance`
- the share of copied lines (0.43%)

Second copies of a model, and functions that do the same job but are written differently, are mostly invisible to these numbers, so the AI findings remain the measure for those two goal classes.

## Round 6 analysis: on track, with one class lagging

- **The loop is making progress, not going in circles.** The goal total fell from 150 to 110, a 27% cut, above the 20% bar. Regressions were 1 of 110, well under the 10% limit. About 120 of round 5's 166 findings are fixed.
- **Shadow models and duplicated functions are falling fast:** −40% and −37%. At this rate they reach single figures in about three more rounds.
- **Bad resource orientation is lagging, at −11%.** Fixes removed 33 of its round-5 findings, but the validators found 25 new ones in code that round 5 read and missed. Three patterns explain most of it, and the round-6 fix brief changes for each:
  - **Stand-in swapped for stand-in:** one lookup replaced by another with the same effect. A concern-5 fix must now come with a spec on the effect it protects.
  - **Named copy removed, twin left:** fix agents must grep for the job and list every place doing it, not just the named function.
  - **Skipped items held open:** each becomes a named task with a failing spec, or a decision record that takes it out of the count.
- **The round-5 fixes introduced three high bugs:** a premature "generate done", `partition` and `repair` failing on optional arguments, and a new actions↔practices cycle. New checks before each commit target exactly these: recipes called with required arguments only, `-X importtime` on changed package `__init__` files, and a grep for caches and registries that were moved rather than removed.
- **The graph check is still unreliable because of B10.** Every validator lost the server during graph builds, so this round rests mainly on the AI check. B10 gets a structural fix this round: graph builds run outside the server's request loop. Until it lands, graph calls run one area at a time.

**What would mean the loop is cycling:** a round-7 total above 88, which is less than a 20% cut, or resource orientation not falling. Either would mean changing the approach. For resource orientation, the next step would be one agent per pattern across the whole repository, instead of one agent per area.

**To reach the goal of under 30:** at a 27% cut per round, 110 needs about four more rounds (80, 59, 43, 31, then below 30). At the 40% rate of the two faster classes, it needs about three.

## Round 7 analysis: close to the goal; the next risk is what the graph check has not yet seen

- **The goal total fell from 110 to 39, a 65% cut.** That is far above the 20% bar, with no regressions.
  - Shadow models are almost gone: 30, then 18, then 3.
  - Resource orientation fell from 56 to 16. The round-6 rule "a spec on the effect first" worked: the validators found effect specs for the concern-5 fixes.
  - Duplicated functions are now the largest class, at 20. Most are twins the fix agents missed.
- **The count rests mostly on the AI check.** A DDD crash in the graph worker, introduced by the round-6 merge fix-up, blocked graph checks in most areas. So the ten Clean Engineering rules switched on in round 6 have not yet judged most code. When they do, expect a jump in **new scope**, which is counted apart from progress. The loop's stop test (under 30, no highs) is applied to findings in old scope.
- **New failure pattern: specs that skip the live path.**
  - Rule examples call `rule.check` directly, so rules the schema never applies still pass. There are 12 such rules across Stories, DDD and BDD.
  - Graph specs build in-process, so they missed the worker-only crash.
  - The round-7 fix brief makes both specs mandatory.
- **To reach under 30:** one more fix round at even half of round 7's rate (−30%) brings 39 to about 27. Round 8 then confirms it, with a working graph check.

## Round 7 fixes: what has landed so far

| Fix | Status | What changed |
|---|---|---|
| Graph and MCP | Merged and pushed (77741148) | The DDD worker crash is fixed. DDD builds from the classes the current load read, and the result is the same in process, in a worker, and from a restored graph. A failed build no longer wipes a session's violations, so validate can no longer report clean code that isn't. Refresh and save are one locked step. With five concurrent builds, the slowest ping fell from 3.9 s to 1.05 s. The call decides where a build runs. |
| Harness core | Merged locally (8db65b9a); quick suite running | No shared practice instances: the catalogue holds classes only. A call's fidelity lives on the call, not the shared practice. One owner each for the class folder (it was written six times), operation discovery, the names annotation, JSON file writing, and the nested-generate rule. Decision records for `ContextConfig`, `Name`, and the guidance and markdown seams. |
| Space, tools, actions | In progress | Two owners of graph-file reading; a second Session for a subfolder; a `Session.graph` race; the capture → partition → embed chain building an empty index; board labels from Python. |
| Harness upper | In progress | The graph app's type check; filter choices in Python; the catalog's twin tables. |
| Practices | In progress | The 12 rules that never run, plus one schema-alignment spec for all five practices; the UX readers; the DDD integration target. |

**Is the loop still converging?** Yes.
- Each round has cut the goal total by more than the 20% bar: −27%, then −65%.
- Regressions have stayed at or below 1%.
- The patterns that held rounds back were stand-in swaps, twins left behind, open skips, and specs that skip the live path. Each one has been turned into a rule in the fix brief, and each validator report since has checked those rules.

**Risk for round 8:** the graph check will run in every area for the first time with the ten Clean Engineering rules switched on in round 6. Their findings count as new scope, so they do not hide the comparison. But they may add real work.

## Round 8 analysis: the old-scope goal is met; two highs hold the loop open

- **In old scope the total is 21, under 30.**
  - The full total is 31, because the graph check finally ran in three areas and judged code it never had before: 10 findings are new scope.
  - Resource orientation is at 12 and shadow models at 4, both near their floor. Duplicated functions are at 15, 6 of them new scope.
- **Two high findings in the goal classes keep the loop open:**
  - the Stories reader crash on a restored graph
  - the Grill fidelity regression
  
  Both are misses of rules already in the brief: fix every sibling, and specs take the live path. Neither is a new kind of problem, so the loop is not cycling. But it does show that the rules need checking, not just stating.
- **The next fix round is narrow:**
  - those two highs
  - B10 under concurrent refreshes
  - the scanner false positives, which shrink the next graph check's noise
  - the remaining low findings
- **Round 9 is expected to be the confirming round.** It needs graph checks that run in every area, and those depend on the hotfix landing.

## Round 9 analysis: the fixes hold, the checks got deeper, and the loop must stop widening

- **What was reported again is small.** 3 findings are left from round 8. The fix agents fix what they are given.
- **What grew is what the check could see:**
  - 29 goal findings are **new scope**. The graph check ran in every area for the first time, and the validators read the code metrics' offender lists for the first time. Most are concern 5: an oversized class holding jobs that should be parts it holds.
  - 20 are **new**: code that existed at round 8, not reported then. Many are duplicates the deeper reading found, such as three classes refusing a path outside the project, or 13 `load_module` definitions.
- **4 regressions (6.5%), all from one change:** the round-8 graph hotfix. It took `Graph` from 227 to 249 total complexity and added `Graph._take`, `PracticeChanges.between` and `GraphReading._link_types`, each a complex function. It was merged before the metrics gate existed, and the gate's later runs started from a commit that already held it, so nothing measured it.
- **One high in the goal classes:** the UX explorer reads Stories facts that a reopened graph doesn't keep. The sibling-reader rule was in the brief and was missed again.
- **Is the loop cycling?** By the rule above, the full total rose, so the brief must change, not just the code. The cause isn't fixes being skipped or reverted. Each round looks somewhere new, so it finds new things. Left as it is, that never ends. Two changes:
  1. **Round 9's fixes go after the cause, not the symptoms.** Most new findings sit in six oversized classes. Splitting each into the parts it holds removes a group of findings at once and moves the code metrics toward their targets.
  2. **Round 10 freezes the check.** It uses round 9's checks, graph rules and metrics evidence, and nothing wider. Its findings in round 9's scope decide the stop. Anything a new kind of check would find goes into a list for later, not into the loop's count.
- **The stop for round 10:** in round 9's scope, a goal total below 30, no high finding in the goal classes, and a metrics gate that passed for every fix.

## The loop ends after round 9

The user ended the loop after the round-9 fixes (2026-11-09, a4440c7f), so no round-10 validation ran.
- **Findings:** the goal total went from 150 in round 5 to 27 in round 9, counting only the scope round 8 checked: 82% fewer. Round 9's fixes addressed every round-9 finding but one: a partial part of R9-M1, the regex reading of Java story files. That includes the one high finding, the UX explorer crash on a reopened graph, which now has a reopen spec for every reader of another practice's facts.
- **Code metrics:** round 9 was the first round where every fix passed the metrics gate. 16 of the 23 guarded numbers improved and none got worse. For example:
  - functions with more than 10 paths: 124 → 100
  - the most complex class: 249 → 192
  - most methods in one class: 70 → 51
  - copied lines: 0.43% → 0.26%
- **Remaining work and remediation strategy:** see [remaining-work-plan.md](remaining-work-plan.md).
