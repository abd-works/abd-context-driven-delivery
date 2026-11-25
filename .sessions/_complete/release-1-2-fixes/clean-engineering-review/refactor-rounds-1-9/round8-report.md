# Round 8: re-validation after the round-7 fixes

**When:** 2026-11-08, at 4359b907. The CDD MCP server ran the same code (2c30c2f7).

**Checks:**
- The same twelve concerns and areas as before. Per-area detail is in the six `round8-*.md` files. The counts come from `concern_counts.py`.
- **The graph check ran in three of six areas:** space and tools, Stories/UX/DDD, and harness core at code level. Most of these areas had never had a graph check with the ten Clean Engineering rules switched on in round 6. Their findings on code no rule had judged before count as **new scope**.
- **In the other areas, graph builds crashed** once the shared session graph held Stories (high finding 1).

## Counts

| Area | Round 7 | Round 8 | High |
|---|---|---|---|
| harness core | 15 | 4 | 0 |
| harness upper | 10 | 6 | 1 |
| space and tools | 7 | 8 | 1 |
| actions, patterns, context setup | 7 | 6 | 1 |
| Clean Engineering, BDD | 2 | 3 | 0 |
| Stories, UX, DDD | 13 | 16 | 1 |
| **Total** | **54** | **43** | **4** (2 of them are the same crash) |

## The loop's goal classes

| Goal class | Round 5 | Round 6 | Round 7 | Round 8 | Round 8, old scope only |
|---|---|---|---|---|---|
| Bad resource orientation (5, 9) | 63 | 56 | 16 | 12 | 9 |
| Shadow models (2) | 30 | 18 | 3 | 4 | 3 |
| Duplicated functions (1, 12) | 57 | 36 | 20 | 15 | 9 |
| **Total** | **150** | **110** | **39** | **31** | **21** |

The old-scope total of 21 is under the target of 30. The stop rule also requires no high finding in the three classes, and two remain, so the loop runs one more fix round.

## High findings

1. **Graph builds crash once the shared session graph holds Stories.**
   - **What happens:** `StoryLinks.link` reads `step.body` on steps restored from the saved graph, which are plain `Node`s.
   - **Where it came from:** this is round 7's DDD crash in a sibling reader. The round-7 fix reached DDD only, and its spec restored only Clean Engineering with DDD.
   - **Who reported it:** harness upper and Stories each reported it, so it is one finding counted twice.
   - **Status:** a hotfix agent is fixing every reader with one design.
2. **Grill hands the agent the wrong fidelity** (regression). `GuidanceAction._inside` copies `_worked_at` before `listed()` fills it, so Grill's inner Generate works at the practice's first fidelity. At `stories-acceptance-tests` the agent gets the story-map template. The specs only ever test a first fidelity.
3. **The board page's TypeScript packages import each other at run time** (new scope, concern 7). `board/` is both the page's composition root and the shared kit.

**B10 got worse under load.** With six validators refreshing one shared session graph, the median ping was 4.1 s and the slowest 12.3 s. Each build order still carries the whole shared graph. The heavy spec missed it because it builds into empty graphs. The hotfix agent owns this too.

## What the fix agents still miss

1. **"Fix every sibling" is the most-missed rule.** This round's misses:
   - the reader crash: DDD was fixed, but not Stories
   - the outside-filled reader: UX was fixed, but not Stories
   - `JsonFile`: installation was fixed, but not the 13 other places in harness
   - the TypeScript reader still counts `import type`, while the Python reader stopped counting `TYPE_CHECKING` imports
   - deleted names still in `.md` cards and AGENTS.md
2. **"Specs take the live path" is missed in two forms:**
   - specs that test only a first fidelity, which missed the Grill regression
   - specs that count on objects they build themselves, while the live path makes a new `Board` per call

**Scanner false positives**, for the scanner owner:
- **TypeScript `import type`** counts as a dependency.
- **`hide-inner-details`** flags a class reading its own class's private members, and its own children.
- **DDD guesses aggregates from class-name endings** in folders with no DDD model (110 false hits in harness).
- **BDD applies behavior-fidelity rules to finished specs** (816 false hits).
- **`use-typed-signatures`** judges plain JavaScript (190 hits).
- **`extensions-live-with-the-domain`** flags nested format packages.
- **`state-change-returns-record`** flags constructors.
- **The near-copy check** has no line floor.

## Changes for the round-8 fixes

- **Each fix brief names the pattern, and the agent greps every practice and module for it,** including `.md` cards. The agent reports every place it found the pattern, not just the place the finding named.
- **Action specs run at a non-first fidelity,** and every option word a recipe offers goes through the tool it names.
- **A process-held part is specced with two served calls** that count one construction.
- **Smoke checks before round 9:**
  - a graph validate on `cdd_guidance/patterns` and on a Stories folder, after a refresh
  - a ping measurement while three refreshes run at once
