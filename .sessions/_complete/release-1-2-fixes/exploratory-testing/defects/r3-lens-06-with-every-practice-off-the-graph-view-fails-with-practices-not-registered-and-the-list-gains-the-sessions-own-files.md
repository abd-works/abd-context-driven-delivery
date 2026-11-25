# With every practice turned off the graph view fails with a worker traceback (PracticesNotRegistered), and the file list grows to hold the session's own json, log and error files

- **Charter:** Round 3, second pass - explore the Files app's graph view on the combined project in a real browser (checks 5 and 6)
- **Tester:** Lens
- **Story:** Review Generated Work In File Viewer > Explore Graph In Files App. No scenario covers a session with no practice on. The page's own words for a graph with nothing in it are "The graph holds no node of these files."
- **Module and class:** `space/session/session_explorer.py` `SessionExplorer.graph_trees` (`graph.load_files(..., self.practice_outputs.working, ...)` with no practice working) and `harness/graph/graph.py` `Graph.__init__` in the worker (`harness/graph/graph_worker.py`), which takes no practices as "every practice" and finds none registered in its process. The list: `harness/files_app/app/files/files-page.ts` `rootFilesShown` (`withUnclaimed`). Not in the Files app files another chat was editing.
- **Severity:** misleading message (a traceback for an ordinary state; the person is offered "Copy for AI" for something that is no fault)

## Steps

Sandbox `C:\dev\_et\round3\lens\work`, session `main`; script `C:\dev\_et\round3\lens\drv\w11.py`.

1. Open the Files app with every fidelity, press **All session files**, press **Graph**.
2. Press each practice chip off: Stories, DDD, UX, CE, BDD.

## Expected

Either no file and no tree ("The graph holds no node of these files."), or the files no practice claims with whatever the graph reads from them; no failure.

## Actual

- The list grows from 84 to 106 files: the 22 no fidelity declares, among them `.sessions/.gitignore`, `.sessions/main/session.json`, `session.log` and `session.err`.
- `graph-trees` answers 500 and the graph view shows, under **Copy for AI**:

```
The graph did not read: cdd session.graph_trees failed: GraphBuildFailed: the graph build's worker process exited with 1:
Traceback (most recent call last):
  ...
  File "C:\dev\abd-cdd-release-1-2-fixes\harness\graph\graph_worker.py", line 31, in main
    built = Graph().build.carry_out(order)
  File "C:\dev\abd-cdd-release-1-2-fixes\harness\graph\graph.py", line 1490, in __init__
    held = list(PRACTICE_CATALOGUE.create_all(fidelity=None) if practices is None else practices)
  ...
harness.guidance.practice_catalogue.PracticesNotRegistered: no practices are registered with PRACTICE_CATALOGUE in this process; import the package that defines them
```

- Each failure is also written to `.sessions/main/session.err`, which the list then shows.
- Turning the practices on again reads the graph and brings the five trees back.

Screenshot: `C:\dev\_et\round3\lens\shots\33-all-practices-off.png`.

## Tier that should catch it

Heavy (the graph worker is a real process): `space/session/session_graph_spec.py` asks the trees with practices on only; no spec builds a session's graph with none working.

## Also seen by
