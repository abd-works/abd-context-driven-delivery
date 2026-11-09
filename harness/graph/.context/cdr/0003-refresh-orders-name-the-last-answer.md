# A refresh order names the worker's last answer, and the worker answers what the refresh changed

Validators refresh one shared session graph one after another. Under CDR 0001 each refresh had the server write its whole graph into the build order (`SavedGraph.from_graph` and `json.dumps`) and read the worker's whole graph back (`json.loads` and `Graph._hold`). For the graph of `cdd_guidance/practices` with every practice loaded (about 11 MB), that was about a second of the server's own Python per refresh, half of it inside single `json` calls that hold the interpreter lock throughout. With six validators on one graph the median `cdd.ping` was 4 s and the slowest 12 s (B10, R8-M1).

## Decision

- **The order names the last answer.** The worker writes its answer to a file the graph keeps (*HeldAnswer*). The graph counts every change to what it holds (`Graph.changed`, called by *PracticeNodes* whenever a node, an edge, or a fact changes, and by every build in this process). While the count is what it was when the graph took the answer, the next order names that file (`BuildOrder.state_file`) and the server writes no graph at all.
- **The worker answers what a refresh changed.** For a refresh whose order names the last answer, the worker also writes *GraphChanges*: per practice, the nodes it dropped, the nodes new or changed, the edges that went or came, each node whose violations changed, and the practice's own facts when they changed. The server takes those (`Graph._take` then; since round 9 `GraphPractices.take`, each practice through its `PracticeRestore`): it changes plain nodes in place, records and drops the edges, restores the changed nodes' violations, and rebuilds the trees of the practices that changed. The whole answer stays on disk as the state for the next order.
- A load, a check, or a refresh of a graph that changed in the server since its last answer works as before: the server writes its graph into the order and holds the whole answer.

## Measured

On `cdd_guidance/practices` with every practice loaded, refreshing one edited file at a time in a worker:

| | server writing the order | server taking the answer |
|---|---|---|
| graph written out and read back whole (before) | 508 ms | 563 ms |
| order names the last answer, worker answers the changes (after) | 1 ms | 72 ms, most of it rebuilding Clean Engineering's tree |

## Considered options

- **Keep the whole graph in one long-lived worker process and forward every graph call to it.** Rejected again, for the reason CDR 0001 gives: every reader of the session graph would cross the process boundary.
- **Hold the worker's answer lazily, reading it back only when a call reads the graph.** Rejected: every reader of the session graph (validate's report, the board, the explorer, actions) would have to remember to read it first, and one that forgot would read a stale graph without failing.
- **Send only the changes and keep no answer file.** Rejected: the worker would still need the whole graph as its starting point, so the server would still write it out every time.

## Consequences

- The graph keeps one answer file per graph in a temporary folder of its own, removed with the graph.
- Anything that changes what a graph holds goes through *PracticeNodes* or `Node.set_fact`, so the count sees it. A parsed object's attributes change only inside a build, and every build counts as a change.
- `harness/graph/graph_build_spec.py` refreshes one graph with each practice's file in turn and checks that every refresh after the first is taken as changes, and that the graph then holds what a fresh build holds. `harness/graph/graph_build_heavy_spec.py` has six chats refresh one shared graph at once while another times `cdd.ping`.
