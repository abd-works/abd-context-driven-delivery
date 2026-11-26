# Record Every Change To The Graph

An idea from the person on 2026-11-22, kept with its reasoning. Nothing here is built, and no stopgap is to be built in its place.

**Outcome:** every command that changes the knowledge graph leaves a record of what changed, the saved graph is brought up to date by that same change, and rules and reports can read how the work has moved over time.

## The idea, in the person's words

"Thinking through whether it makes sense to track every change to the knowledge graph, for example using a simple commit that records the real change, but could also make sure the graph is resaved with deltas, then perhaps the tag of the commit is practice, command, path. Benefits may be: a very quick scan of changes, the impact to quality, execution provenance, better trend analysis."

## Why it is worth having

- **The saved graph falls behind the code today.** It is saved only by a whole load from the working copy or an explicit save. A refresh after files are written changes only the graph in memory, and a later whole load answers from the saved graph when it covers the same roots, without reading the folders again. This repository's saved graph was a day behind its code when this was written.
- **A save is a complete rewrite.** The whole graph is written each time; this repository's file is 56 megabytes. There is no way to save only what changed.
- **Nothing records which command wrote what.** The research into where release 1.2's defective code came from could not tie 20 of 77 commits to any guidance, because no record says which practice, fidelity and action changed a file. The session log keeps a line for each tool call and mostly not its guidance argument.
- **Trends have to be measured again from old code.** Comparing the code measures before and after the judge-led fixes meant checking out two old commits and running the measures on each.

## What to build

- **One record for each command that changes the graph**, tagged with the practice, the fidelity, the action and the paths, with the git commit and the session.
- **The record holds the change, not the graph:** nodes added, removed and changed; facts whose value changed; violations opened and closed.
- **The saved graph is updated by that same change**, so it is never behind the code.
- **The saved graph is split by source file or by module**, so a change writes only the parts it touched and a difference between two saves is small enough to read. One 56 megabyte file committed on every change would bloat the repository and conflict on every merge between tickets.
- **The records are an append-only log beside the session**, keyed by the git commit. `violation-history.jsonl` already records each validate run with its commit, session, fidelity and paths; this widens that from validate runs to every change to the graph.

## What it makes possible

| Benefit | What the record gives |
|---|---|
| A quick scan of a change | "This generate added 4 operations and opened 3 violations", without loading the graph |
| Impact on quality | Violations and metrics before and after each command, for each module |
| Provenance | Which practice, fidelity and action wrote each node |
| Trend analysis | Metrics and violations over commits, with no need to check out and measure old code again |

## A rule that waits on this: a module many depend on that changes often

Decided on 2026-11-22: to be added once the change record exists, not before, and with no separate reader of git history built for it.

How often a module changes is the strongest sign of whether its coupling is a problem. Two modules that are each imported by twenty others carry very different risk when one changed twice in two months and the other sixty times: every change to the second can break twenty callers. The import counts cannot tell them apart, which is why no fixed limit on imports works; published thresholds for coupling disagree, with cutoffs from about 1 to 25 across studies, rising with the size of the system.

The rule: a module that many others import and that also changes often is reported, with both counts. The count of changes is not in the code the graph reads; it comes from the history of changes, which this record holds. With the record in place the rule is a count over it.

Until then the module's metrics group shows the modules it imports and that import it with no limit, and the rule that a module depends in the direction of stability, which needs only those two counts, lists its candidates.

## Cost to weigh

Every command that writes files has to refresh the graph and save the change, which adds time to each generate and render. The split saved graph is what keeps that small.

## Open questions

- Is the record kept in the repository and committed with the work, or beside the session and left out of commits?
- Does a change made by hand, with no command, get a record at the next validate or load that notices it?
- How long are records kept, and are they folded into a summary when a ticket closes?
