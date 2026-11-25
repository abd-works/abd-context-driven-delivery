# A markdown class model gives the knowledge graph no class, and validate on it says "All scanned graph rules passed" on an empty graph once its module holds Python

- **Charter:** Round 3 - Clean Engineering (modules, model, code) in every format, checks 1, 2 and 4
- **Tester:** Widget
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers this.
- **Module and class:** `cdd_guidance/practices/clean_engineering/model/graph_reading.py` `GraphReading` (what a `.context/*-model.md` adds to the graph); `cdd_guidance/actions/validate` (the report on a checked graph with no node)
- **Severity:** wrong result

## Steps
Sandbox `C:\dev\_et\round3\widget\work`, session `main`, throwaway cdd server on the build at 4d47fdf8e. Models at `src/<module>/.context/<module>-model.md` for catalogue, ordering, fulfilment (8 classes, 18 properties, 15 operations and 8 constructors).

A. Before any code exists (`drv\go.sh c1.json`): `validate.validate {"guidance":"clean-engineering-model","paths":[the three model files]}`
B. After `src/<module>/*.py` exist (`e1.json`): the same call.
C. `graph.load_files {"folder":"C:/dev/_et/round3/widget/work","practices":["clean_engineering"],"files":[the three model files]}`, then `graph.return_nodes` (`g3.json`).
D. With the `.py` files moved away: `graph.load_files {..., "files":["src"]}`, then `graph.inventory` (`g2.json`).

## Expected
Check 4 of the round: a node for each class, property and operation the model file holds, and an edge for each relationship and call. Validate judges the file it is given the same way whether or not code sits beside it, or says that it read nothing.

## Actual
- A: "Total graph violations: 2" (`limit-operation-parameters` on Book's constructor, `limit-comments` on CartLine), on nodes named after the markdown file.
- B: the same three unchanged files: "**No graph rule violations.** All scanned graph rules passed." The checked graph it names, `.sessions\main\.context\checked-graphs\clean-engineering-model-20261120T021000\graph.json`, holds 0 nodes and 0 edges.
- C: 7 nodes, none of them from the model: `Package:src`, `Module:catalogue|ordering|fulfilment`, and three `Package:.context` (each module's `.context` folder shown as a package). No class, property or operation.
- D: `graph.inventory` answers no node at all for clean_engineering.

So the model in markdown, the format the model fidelity names beside drawio and whiteboard, is in the graph only inside validate and only while the module has no code; its stereotypes and its composition, aggregation and association kinds are in no graph afterwards (the Python classes' `stereotypes` fact is `[]`). The `.drawio` and `.whiteboard` models add nothing either.

## Tier that should catch it
Unit, `graph_reading_spec.py`: no example loads a module that holds both a model document and code and looks for the document's stereotypes and relationship kinds; and nothing fails a validate that checked a graph with no node from the paths it was given (compare r3-rivet-02, widget-18).

## Also seen by
- Cog, round 3 second pass: the combined project: the three class models (8 classes) give no node; nothing joins a model class to its code class (r3-cog-05).
