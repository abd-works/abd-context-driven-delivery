# A checked graph filters violations by the practice key the graph file records

**Status:** decided, round 6 (findings M4 and L5, part).

## Decision

`CheckedGraph.violations` keeps only the violations whose `practice` is the key of a practice the call lists (`violation.practice in keys`), and `graph_json_reader` stays the reader of the graph files a validate call names by path: a saved graph document, read through `SavedGraph.from_document`, or the node list `graph.return_nodes` answers with.

## Why

- A violation read from a graph file is a record in that file. The saved graph and the `graph.return_nodes` answer both name the practice that found a violation by its key, which is that practice's identity in the file, so comparing keys compares identities; nothing is looked up by name, and no practice object is rebuilt to make the comparison. A graph this call built (`graph.refreshed(prefixes, call)`) and the session's saved graph (`graph.saved_file.read()`) are filtered by `SavedGraph.violations(keys)`, the same comparison made by the graph's own saved form.
- Holding a practice object on each `Violation` would make the graph's *Violation* (harness/graph) carry an object that a JSON record cannot hold, so every reader of a saved graph would have to rebuild practices to read one. That is the cost the guardrails forbid ("objects rebuilt per call").
- Reading a `graph.return_nodes` node list belongs with the graph's *Violation* in `harness/graph`, beside `Violation.from_data`, which it already uses for each record. Moving it there changes harness-core's module and the Session Board's report (`space/kanban/report.py`), which also reads node lists; it is left to the harness-core owner, so this module keeps one reader of node lists and does not grow a second.

## Consequences

The session's saved graph is read only through the file the session's graph saves in (`Graph.saved_file`), so the path `.context/graph.json` is built in one place.
