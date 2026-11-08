# A checked graph filters violations by the practice key the graph file records

**Status:** decided, round 6 (findings M4 and L5, part); the reader moved in round 7 (L5, space finding 2).

## Decision

`CheckedGraph.violations` keeps only the violations whose `practice` is the key of a practice the call lists (`violation.practice in keys`). Every graph file a validate call checks, and every graph the Session Board's report reads beside a report, is read by one reader in `harness/graph`: `SavedGraph.from_file`. It reads a saved graph document, or the node list `graph.return_nodes` answers with (`SavedGraph.from_nodes`), into one `SavedGraph`, which answers `violations(practices)` and `checks_of(practice)` for both. A node list keeps no pattern overlays, so only each practice's own scanners count for it. Several named graph files are read as one `SavedGraph` of all their violations (`SavedGraph.from_violations`), which is what validate saves beside its report. Hits are grouped by rule with `Violation.by_rule`.

## Why

- A violation read from a graph file is a record in that file. The saved graph and the `graph.return_nodes` answer both name the practice that found a violation by its key, which is that practice's identity in the file, so comparing keys compares identities; nothing is looked up by name, and no practice object is rebuilt to make the comparison.
- Holding a practice object on each `Violation` would make the graph's *Violation* (harness/graph) carry an object that a JSON record cannot hold, so every reader of a saved graph would have to rebuild practices to read one. That is the cost the guardrails forbid ("objects rebuilt per call").
- Deciding "a list is a node list, a dict is a saved graph" belongs with the graph's saved form, beside `SavedGraph.from_document` and `Violation.from_data`. With the reader there, the Validate action and the Session Board each ask the graph's own class instead of the board importing an action's internal module, and the decision is made in one place.

## Consequences

The session's saved graph is read only through the file the session's graph saves in (`Graph.saved_file`), so the path `.context/graph.json` is built in one place. Validate never writes a node list of its own: what it saves beside a report is always a saved graph document.
