# BDD behavior and development offer Java as a format, and generate tells the agent to save it, but render refuses Java, the graph reads a Java spec as Clean Engineering classes, and validate on it reports "No graph rule violations"

- **Charter:** Round 3 - BDD (behavior, realization, development) in every format: generate, render, graph
- **Tester:** Rivet
- **Story:** epic "Deliver Work With Context Guidance", sub-epic "Produce Formal Artifacts" (generate and render) and "Check Artifacts Against Rules" (validate); no scenario covers a Java spec.
- **Module and class:** `cdd_guidance/practices/bdd/bdd.md` (behavior and development `outputs: java: "**/*Spec.java"`), `cdd_guidance/practices/bdd/bdd.py` `Bdd.format_adapters` (sketch, markdown, python, typescript, graph; no java), `cdd_guidance/practices/bdd/templates/` (bdd.py, bdd.ts, no Java template, while bdd.md names `templates/bdd-templates.{ext}` (`.py` / `.java` / `.ts`), files that do not exist under that name).
- **Severity:** wrong result

## Steps
Sandbox `C:\dev\_et\round3\rivet\work`, session `main`, throwaway cdd server (`C:\dev\_et\round3\rivet\drv\run.py`; calls in `drv\a2.json`, `drv\b2.json`, `drv\c1.json`).

1. `generate.generate {"guidance": "bdd-behavior"}` (the same for `bdd-development`).
2. Write the JUnit 5 behavior specs it asks for: `_trips/behavior/java/src/ordering/CartSpec.java`, `OrderSpec.java`, `src/fulfilment/ShipmentSpec.java` (`@Nested` classes with `@DisplayName`, `@Test` methods holding `// BDD: SIGNATURE`; 3 describes, 8 states, 12 observations).
3. `validate.validate {"guidance": "bdd-behavior", "paths": [the three .java files]}`, then read `.sessions/main/.context/checked-graphs/<run>/graph.json`.
4. `render.render {"guidance": "bdd-behavior", "format": "java", "paths": ["_trips/behavior/python/src/ordering/order_spec.py"], "source": "python"}`
5. `render.render {"guidance": "bdd-behavior", "format": "python", "paths": ["_trips/behavior/java/src/ordering/OrderSpec.java"], "source": "java"}`, and the same with `source` left out.

## Expected
A format the fidelity offers is one the practice can write, read, render and check (bdd.md, behavior: "Default: Mamba/Python; Jest/TypeScript or JUnit 5/Java when the project uses those"; generate's answer: "Save each format you write at its path ... java: .../**/*Spec.java"). Or Java is not offered.

## Actual
- Step 1: the answer names the Java path, and holds the Python and TypeScript templates only; no Java template or example.
- Step 3: `isError=False`; the report says "**No graph rule violations.** All scanned graph rules passed." The checked graph holds no BDD node: `bdd` nodes 0. The three test classes and their nested classes are in `clean_engineering` as 11 `OoadClass` and 28 `Operation` nodes, so the specs are read as production classes. The same call on the Python or TypeScript files reads 3 Spec, 3 Description, 8 Context, 12 Observation.
- Step 4 and both calls of step 5: `ValueError: Unsupported format 'java'. Choose from: ['graph', 'markdown', 'python', 'sketch', 'typescript']`. With `source` left out, the message still blames the format asked for (`python` was asked), not the file.

## Tier that should catch it
Unit: a spec over each practice that every format a fidelity's `outputs` offers has a format adapter (or is refused by `choose_format`). `bdd_spec.py` and `code_spec_render_spec.py` cover Python and TypeScript only.

## Also seen by
