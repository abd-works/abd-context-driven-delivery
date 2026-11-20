# The BDD realization steps say `graph.save_json` writes `.context/graph.json` and to render that path; save_json writes `.sessions/<session>/graph.json`, so the render draws an older graph left in `.context`, and the result is saved as `graph.md`

- **Charter:** Round 3 - BDD (behavior, realization, development) in every format: generate, render, graph
- **Tester:** Rivet
- **Story:** epic "Deliver Work With Context Guidance", sub-epic "Produce Formal Artifacts"; no scenario covers rendering the realization from the graph.
- **Module and class:** `cdd_guidance/practices/bdd/bdd.md` realization Guidance, "Render it from the graph" steps 2 and 3; `harness/graph/graph.py` `Graph.save_json` (docstring: "Write the serialized graph into the loaded folder's `.context`") and `Graph.saved_file`; `cdd_guidance/actions/render/render.py` (where a graph render is saved).
- **Severity:** wrong result (following the steps as written gives a realization of other files, with no word)

## Steps
Sandbox `C:\dev\_et\round3\rivet\work`, session `main` (`drv\run.py`, calls in `drv\b2.json`, `drv\b3.json`, `drv\g1.json`, `drv\g2.json`).

1. Earlier in the session, `validate.validate` with `bdd-behavior` / `bdd-realization` on stage copies of the specs under `_trips/` (signatures only). After these, `.context/graph.json` exists at the project root, holding 16 specs.
2. As generate for `bdd-realization` instructs: `graph.load_files {"folder": "C:/dev/_et/round3/rivet/work", "practices": ["bdd", "clean_engineering"], "files": ["src"]}` -> "Loaded 11 edited files." (3 specs, 12 observations, 18 invokes edges).
3. `graph.save_json {}`
4. `render.render {"guidance": "bdd-realization", "format": "markdown", "source": "graph", "paths": [".context/graph.json"]}`

## Expected
bdd.md: "Save it (`graph.save_json`, written to `.context/graph.json`). Render it: `render` on this guidance with `format=markdown`, `source=graph`, and `paths` naming the saved graph. Write the result to `.context/{scope}-bdd-realization.md`." So step 4 draws the graph loaded in step 2: 3 subjects, 12 observations, with their entry operations.

## Actual
- Step 3 answers `{"path": "C:\\dev\\_et\\round3\\rivet\\work\\.sessions\\main\\graph.json"}`. `.context/graph.json` keeps its older time and content.
- Step 4 answers `isError=False` and saves `.context/graph.md`: 369 lines, the three subjects several times over (once per stage copy validated in step 1), and for the `src` specs every observation reads `// the graph holds no operation this observation calls`.
- With `paths: [".sessions/main/graph.json"]` the render is right for the loaded files (12 observations, entry operations listed), and is saved as `.sessions/main/graph.md`.
- In neither case is the file named `{scope}-bdd-realization.md` or put in `.context`; the name follows the graph file. generate's "Save each format you write at its path" names `.context/{scope}-bdd-realization.md`, and render's own description says a markdown render is saved "under the name the fidelity writes that format to when the path is one of the fidelity's own files".
- In a project where no validate has left `.context/graph.json`, step 4 as written names a file that is not there.

## Tier that should catch it
Heavy: one example that runs the four steps of the realization guidance through the server on a project folder and reads the file it names. `graph_bdd_model_spec.py` renders from a graph in memory, so the path never comes up.

## Also seen by
