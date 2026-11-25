# validate on a BDD sketch (`*-sketch.md`) or on the describe tree as markdown reads no node from it and reports "No graph rule violations. All scanned graph rules passed."

- **Charter:** Round 3 - BDD (behavior, realization, development) in every format: generate, render, graph
- **Tester:** Rivet
- **Story:** epic "Deliver Work With Context Guidance", sub-epic "Check Artifacts Against Rules"; no scenario covers a file the graph reads nothing from.
- **Module and class:** `cdd_guidance/actions/validate/validate.py` (the graph-rule report), `cdd_guidance/practices/bdd/model/graph_reading.py` `BddGraphReading` (reads spec code only). bdd.md's rule globs for all three fidelities name `**/*-sketch.md`, and realization's also `**/*-bdd-realization.md`.
- **Severity:** misleading message

## Steps
Sandbox `C:\dev\_et\round3\rivet\work`, session `main` (`drv\run.py`, calls in `drv\b2.json`; `drv\cg.py` prints what the checked graph holds).

1. Write `_trips/behavior/sketch/bookshop-sketch.md` in the notation of `templates/bdd-sketch.md` (`Fidelity: behavior`, `## behavior driven development:`, `### a cart`, `#### that is new`, fenced `it should ...`): 3 subjects, 8 states, 12 observations.
2. `validate.validate {"guidance": "bdd-behavior", "paths": ["_trips/behavior/sketch/bookshop-sketch.md"]}`
3. The same on `_trips/behavior/markdown/bookshop-tree.md` (the indented tree `render` writes for `format: markdown`), and on `_trips/realization/sketch/bookshop-sketch.md` with `bdd-realization`.
4. Read `.sessions/main/.context/checked-graphs/<run>/graph.json` after each call.
5. Probe (`drv\b3.json`): rename the state `that is new` to `when the cart is new` in a copy of the Python spec, the sketch and the tree markdown (`_trips/probe/when_spec.py`, `when-sketch.md`, `when-tree.md`) and validate each.

## Expected
The file named in `paths` is checked by the graph rules its globs put it under (`state-not-when`, `shared-describe-subject`, ...), or the report says that no graph rule read the file, so the agent knows only the AI rules apply. render reads the same file into a full describe tree (`render` sketch -> python gives 12 `it` blocks), so the tree can be read.

## Actual
Each call: `isError=False`, report "## Summary **No graph rule violations.** All scanned graph rules passed. **AI rules in scope:** 13" (17 for realization). The checked graph holds no node in any practice (`"bdd": {"nodes": [], "edges": []}`). The same wording is given for the Python specs, where 26 nodes were checked, so the two cases cannot be told apart from the report.

Step 5: the Python copy is reported, "Context `when the cart is new`: Nested context 'when the cart is new' must not start with 'when'; use 'that' or 'with'." The sketch and the tree markdown with the same state: "No graph rule violations. All scanned graph rules passed.", no node checked.

## Tier that should catch it
Unit, on validate's report: a path that adds no node to the checked graph is named as not read. Same family as widget-18 (a Python file that does not parse validates clean), with a different cause: here the file is well formed and in the rule's globs.

## Also seen by
