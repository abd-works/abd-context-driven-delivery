# Second judge round (2026-11-24)

The person asked on 2026-11-23 for a second judge round once section 7's work had landed, on the production files changed since 2026-11-21, with the count set beside the first round's 1,106. Seven judges read the 613 production files changed between `66f410de3` (the last commit before 2026-11-21) and `5d16245ff`, each file in full, in the same seven areas and the same format as the first round ([judge-round](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\clean-engineering-review\judge-round)). Specs, story tests, fixtures, examples and `oss_portal_domain_driven` were left out. Each judgment opens with its counts and ends with its design proposals.

Not yet in at `5d16245ff`: section 7 item 9 ("one thing is one node in the graph") and the other robots' work still uncommitted in the worktree at the time.

| Area | Files read | Findings | Still open from round 1 | Design proposals |
|---|---|---|---|---|
| [guidance and graph](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\clean-engineering-review\judge-round-2\judgment-guidance-graph.md) | 69 | 167 | 85 | 24 |
| [harness apps and tools](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\clean-engineering-review\judge-round-2\judgment-harness-apps-tools.md) | 100 | 189 | 50 | 18 |
| [harness lower modules](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\clean-engineering-review\judge-round-2\judgment-harness-lower.md) | 52 | 115 | 50 | 7 |
| [kanban and repo](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\clean-engineering-review\judge-round-2\judgment-kanban-repo.md) | 59 | 68 | 38 | 7 |
| [Clean Engineering, DDD and BDD practices](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\clean-engineering-review\judge-round-2\judgment-practices-ce-ddd-bdd.md) | 153 | 274 | 89 | 30 |
| [space and session](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\clean-engineering-review\judge-round-2\judgment-space-session.md) | 41 | 104 | 68 | 7 |
| [Stories, UX, actions and patterns](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\clean-engineering-review\judge-round-2\judgment-stories-ux-actions-patterns.md) | 139 | 420 | 206 | 44 |
| **All** | **613** | **1,337** | **586** | **137** |

## How 1,337 compares with 1,106

The two counts are not like for like:

- The first round read every production file; this one read only the 613 changed since 2026-11-21, so findings in unchanged files are not counted here at all.
- Most judges this round split their area among sub-judges and merged the reports, which writes more, finer findings per file than one judge did; the Stories area alone went from 393 to 420 on fewer files.
- 586 of the 1,337 are the first round's findings, still open in these files. The rest (751) are new: some in code written since, some in code the first round read and did not report.

The judges name about 280 of the first round's findings as ended by the fixes in these files (83 in guidance and graph, 61 in harness apps and tools, about 40 in space and session, and the rest in the judgments' own lists).

## Defects found while judging

Each needs a failing test before it is fixed. The ones the judges rank highest:

- `harness/graph`: a filter chosen by a rule's label opens a node with no failing rules (`graph_rules_collection.py:192` against `node_filter.py:209`).
- `space/repo/repo.py:367` `WorkingTree.is_merging` looks for `MERGE_HEAD` in a `.git` folder, which a linked worktree does not have, so a commit during a merge in a ticket's worktree names paths instead of finishing the merge.
- `space/session/session_saves.py:139`: a queued save is skipped without a word while the main folder is not on the default branch.
- `space/session/files/session_files.py:200` `BranchChanges` looks the branch up by the session's name, not `SessionCheckout.branch`.
- `harness/installation/published_links.py:143-166`: an unreadable `whiteboards.json` or `versions.json` reads as empty and the next record writes over every other board's link; the same unreadable-as-empty pattern in the plugin manifest, the hook daemon's address file, hook stdin and the kept-document readers.
- `cdd_guidance/practices/agent_bdd/agent_bdd_common.py:182` writes to a frozen dataclass, so a judge verdict wrapped in prose crashes the spec.
- `harness/e2e_review/report/run.ts` `summary` counts verdicts made against an earlier run.
- `scripts/install.py:295-323` can report a version change it never made.
- Fourteen in the Stories, UX, actions and patterns judgment's own section, four of them in the Story UI.
