# Round 7: re-validation after the round-6 fixes

**When:** 2026-11-08. The checkout and the CDD MCP server were both at c8921451.

**Checks:** the same twelve cross-file concerns and areas as round 6. Each round-6 finding was checked against the code and marked one of:
- **fixed**
- **left**
- **decided:** a decision record covers it
- **regression**
- **new**
- **new scope:** found only because round 7 looked somewhere new

Per-area detail is in the six `round7-*.md` files. The counts come from `concern_counts.py`.

**Graph check: only one area got a full run.** Every graph build that holds DDD crashed in the worker process (H1 below), so most validators had the AI check only. Harness core got one full run before the crash, which gave 431 hits. The ten Clean Engineering rules switched on in round 6 have still not judged most areas. When they do, their findings count as new scope.

## Counts

| Area | Round 6 | Round 7 | High |
|---|---|---|---|
| harness core | 27 | 15 | 0 |
| harness upper | 26 | 10 | 1 |
| space and tools | 19 | 7 | 0 |
| actions, patterns, context setup | 26 | 7 | 0 |
| Clean Engineering, BDD | 20 | 2 | 0 |
| Stories, UX, DDD | 15 | 13 | 3 |
| **Total** | **133** | **54** | **4** |

## The loop's goal classes

| Goal class | Concerns | Round 5 | Round 6 | Round 7 | Left / new / new scope |
|---|---|---|---|---|---|
| Bad resource orientation | 5, 9 | 63 | 56 | 16 | 8 / 8 / 0 |
| Shadow models | 2 | 30 | 18 | 3 | 0 / 3 / 0 |
| Duplicated functions | 1, 12 | 57 | 36 | 20 | 11 / 7 / 2 |
| **Total** | | **150** | **110** | **39** | 19 / 18 / 2 |

The round-6 to round-7 cut is −65%. No finding is a regression.

## High findings

1. **Graph builds that hold DDD crash in the worker process.**
   - The round-6 worker build restores the session's graph as plain `Node` objects. A scoped read then leaves Clean Engineering's other classes plain, and DDD's reading calls `.stereotypes` on them (`ddd/model/graph_reading.py:203`).
   - Worse, a chat-built graph and a script-built graph hold different objects.
   - No spec covered one practice reading another's nodes in a worker build.
   - A hotfix agent is on it.
2. **Rules that never run on the live graph (rule-versus-schema gaps).**
   - Stories: 5 rules. `kebab-case-paths`, `domain-operation-in-the-step` and `originating-sub-epic-examples` are listed on no node type, `scenario-names-continuation` is on the wrong type, and `branch-on-mechanical-uniqueness` never runs on a Story.
   - DDD: 2 rules.
   - BDD: 5 rules, including `layer-isolation` and `describe-is-plain-english`.
   - Their specs pass because `rule_examples.py` calls `rule.check` directly, on node types set by hand.
3. **`every-class-carries-ddd-stereotype` can never report in a live graph.** Six specs pass `node_type="Entity"` for classes the graph never makes building blocks.
4. **A graph validate can report clean code as clean when it isn't.** One `clean-engineering-modules` run reported 0 violations, while the same paths a few minutes later saved 1,264. The suspected cause is several calls refreshing one shared session graph at once.

**Medium findings to note:**
- **B10 is much better but not done.** During a build there were no failed pings, but the slowest took 8.8 s and the median 1.2 s. The server still serialises the whole graph into each build order.
- **The graph app's new type check fails with 3 errors,** so its tests never run.

## Why the loop is converging, and what changes for the round-7 fixes

- **The goal total is at 39, near the target of under 30.** Shadow models are almost gone, at 3.
- **Duplicated functions (20) are now the largest class.** Most are twins the round-6 fixes missed:
  - the class-folder computation, written four times
  - two owners for "a nested generate does not count"
  - the catalog's own file-order and language tables
  - `GuidanceAction._discover_operations`, which copies `AgentToolSet`'s
- **Two new patterns came from the validators:**
  1. **Specs skip the path the live system takes.** Rule examples bypass the schema, and graph-reading specs build in-process, never on a restored worker graph. That is behind high findings 1–3.
  2. **A fix lands on the format the finding named, but not on its siblings.** For example, the UX JSON reader was folded into its nodes, but the draw.io and markdown readers were not.
- **One finding fixed twice by two areas** produced a duplicate, the nested-generate rule.

**New rules for the round-7 fixes:**
- **One spec checks every practice's rules against its schema,** and rule examples go through the schema.
- **Graph-reading specs also run on a worker build of a restored graph** that holds several practices.
- **A fix to one format is applied to every sibling format.**
- **A finding that spans two areas has exactly one owner** among the fix agents.
- **The class-folder job and the other named twins** are fixed by grepping for their body, not their name.
- **Skips without a decision record:** `ContextConfig` and `Name`, skipped in rounds 5–7, and the TypeScript-side rows. Each gets a decision record, or a fix.
- **After the last merge, before the validators start,** the lead runs one graph validate over all areas as a smoke check.
