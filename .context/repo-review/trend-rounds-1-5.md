# Validation trend, rounds 1–5

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

## Wrong behaviour (the bugs) by round

| Round | Wrong-behaviour findings | What kind |
|---|---|---|
| 1 | 19 (B1–B18, B34) | MCP host crashes and pile-ups, data erased (`config.json`), hooks logging into the wrong session, recipe failures hidden |
| 2 | 15 (B19–B33) | Imports of deleted code, format round trips losing data, rules that could never fire |
| 3 | 17 (11 high) | Round trips still losing data, paths resolved against the server's folder, malformed files read as empty |
| 4 | not graded | — |
| 5 | about 10 high | Actions sending prompts with text missing; the server stalling on a graph validate; the graph going empty after a ticket switch; hooks reading the wrong install; draw.io rules never firing |

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
- **The graph scanners have not yet added a finding the AI judges missed.** In round 5 every graph cycle came from spec or `_examples` imports. Fixing the scanners is now a task of its own.

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
| Bad resource orientation | 5, 9 | 68 (62 + 6) |
| Shadow models | 2 | 33 |
| Duplicated functions | 1, 12 | 62 (50 + 12) |
| **Goal total** | | **163** |

**Done when** the goal total is below 30 (under a fifth of round 5's 163) and no high finding remains in the three classes. The user set this target on 2026-11-08; it replaced the first target of 81.

**What counts as cycling, and what to change when it happens.** After each round, compare it with the round before:
- **Each round should cut the goal total by at least 20%.** If it doesn't, change the fix brief, not just the code. Find which findings were reported again:
  - **The same finding reported again** means the fix was skipped or reverted. Make it a named task with a spec that fails first.
  - **A new finding of an old kind** means the guardrails missed it. Add the pattern to `refactor-guardrails.md`.
- **Watch the share of regressions.** These are findings marked fixed in an earlier round that are back. If more than 10% of a round's findings are regressions, each fix agent's brief adds a grep-based check for the earlier patterns before it commits.
- **A finding the fix agents skip twice** goes into a decision record, with the reason, and leaves the count. That way a deliberate decision does not keep the loop running.
- **New scope is counted separately from progress.** A round that checks more code (for example, a scanner that now sees cycles between files) reports its findings in the newly checked code in their own column, so a wider check does not hide progress.

| Round | Bad resource orientation | Shadow models | Duplicated functions | Goal total | Change from last round | Regressions | Notes |
|---|---|---|---|---|---|---|---|
| 5 | 68 | 33 | 62 | 163 | baseline | — | First cross-file round. Nine fix agents ran on it |
