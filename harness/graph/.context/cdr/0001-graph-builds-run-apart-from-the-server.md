# A chat's graph build runs in a worker process

The cdd server answers every chat from one Python interpreter. A graph build is minutes of CPU-bound Python, and run there it slowed the server's event loop until the operating system's queue of waiting connections filled and every chat's connect was refused (B10, round 6 R6-H2). Limiting the process to one build at a time did not help, since one build alone holds the interpreter. Each node and each rule also sent a progress report through the event loop: about 65,000 for one build of `cdd_guidance/practices`, which on its own doubled the build's time.

So a build that a chat's call asks for runs in a worker process. The graph writes what it holds and what to do as a *BuildOrder* (`harness/graph/graph_build.py`), `python -m harness.graph.graph_worker` carries it out on a graph of its own, and the graph then holds the *SavedGraph* the worker built. The order and the answer are the shape `graph.json` keeps, so a graph the worker built is what the server would have read back from a saved graph: plain nodes with their facts, edges, and violations. A tool's progress reaches its chat at most four times a second (*ThrottledReporter*, harness/mcp), and `cdd.ping` answers on the event loop.

## Considered options

- **Keep the build on a worker thread and throttle only the progress reports.** Rejected: every thread shares the interpreter's lock, so the event loop still waits for the build between its own steps, and a larger build or more callers bring the stall back.
- **Hold every session's graph in one long-lived worker process and forward every graph call to it.** Rejected for now: every operation that reads the session's graph (validate's report, the board, the explorer) would have to cross the process boundary, which is a much larger change for the same effect on the server.

## Consequences

- The graph decides where a build runs from the call it runs in (`is_answering_a_chat`, set by the MCP host for each chat's call). A spec or a script builds in its own process, holding the parsed model objects its rules read.
- `Graph._builds`, the process-wide one-build-at-a-time semaphore, is deleted: builds of several sessions run in separate worker processes at once.
- A refresh sends the graph it holds to the worker and gets the whole graph back, so a small refresh costs the worker's start (a few seconds) on top of the rules it runs again.

## Kept as they are, and why

- *PatternOverlays* keeps its registry of pattern classes on the class. The patterns register themselves when their package is imported, as the practices do with *PracticeCatalogue*, because the framework may not import them. The pattern objects are no longer process-wide: each graph's *PatternOverlays* makes its own.
- *GraphOverlay.rules_for* names its rules package from the module of the pattern it holds, the way a practice reads its own rules (`rules_in(f"{package}.rules")`); nothing is looked up by a name a caller passed.
- *Graph* keeps `loaded(kind)` beside `practice_of(kind)`. `practice_of` opens a practice the graph holds; `loaded` answers whether the last load reads it, which is what a practice linking its nodes to another's needs to know, and opens nothing. `practice(key)` is the one lookup by key, for calls that name a practice by the key they sent.
