# The domain model rendered to Python or TypeScript comes back as one text holding every aggregate, with nothing saved: not the file per aggregate generate names, and not the `.context/bounded-context.md` the practice says the code build writes

- **Charter:** Round 3 - DDD (bounded_context, model, tactics), checks 1, 2 and 4
- **Tester:** Bolt
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers the code formats of the DDD model.
- **Module and class:** `cdd_guidance/actions/render/render.py` / `rendered_file.py` (a code render is returned, never saved), `cdd_guidance/practices/ddd/ddd_formats.py` `DddFormats.model_for` and `ddd/model/markdown/nodes.py` `MarkdownAggregate.write_classes_into`.
- **Severity:** wrong result

## Steps
Sandbox `C:\dev\_et\round3\bolt\work`, session `main`, throwaway cdd server (`C:\dev\_et\round3\bolt\drv\run.py`, calls in `drv\m1.json` and `drv\c2.json`; answers kept in `drv\out\model-py.json`, `model-ts.json`).

1. `fidelity-session-output.choose_format` python and typescript for `ddd` `model`; `generate.generate {"guidance": "ddd-model"}`. It says: "Save each format you write at its path, filling any {name} from the work: python: C:/dev/_et/round3/bolt/work/{bounded_context}/{aggregate}/{aggregate}.py; typescript: .../{bounded_context}/{aggregate}/{aggregate}.ts".
2. `render.render {"guidance": "ddd-model", "format": "python", "paths": [".context/domain-model.md"]}` on a model of three contexts and four aggregates, and the same for `typescript`.
3. The other way: `render.render {"guidance": "ddd-model", "format": "markdown", "paths": ["ordering/cart/cart.py", "ordering/order/order.py", "catalogue/book/book.py", "fulfilment/shipment/shipment.py"]}`, and `format` `drawio` and `whiteboard`.

## Expected
A file for each aggregate at the path generate names, as the drawio and whiteboard renders are saved at theirs. `ddd.md`, Default folder: "A bounded context folder contains `.context/bounded-context.md`. The code-format build writes that file when it creates the context folder and the aggregate folders under it" (also rule `bounded-context-file-marks-the-folder`). Back from code, the document at `.context/domain-model.md`.

## Actual
Step 2 answers `[{"format": "python", "content": "..."}]`: one text of 7,406 characters with all twelve classes, the aggregates parted only by comment lines such as `# === Ordering | custom · Cart ===`. No file and no folder is written, and no `bounded-context.md`. The agent has to cut the text at those comments, make up the folder names from `Ordering | custom`, and write the marker files by hand, with no template for them; without them the graph has no bounded context (r3-bolt-01).

The Python declares `-> void` on six operations, uses `@aggregate_root`, `@entity`, `@repository`, `@value_object` and `Collection[...]` with no import, and gives every class a constructor, which the model rule `aggregate-view-only` leaves out. Each integration's `sync:` line is not in the code.

Step 3 saves `ordering/cart/domain-model.md`, `ordering/cart/domain-model.drawio` and `ordering/cart/domain-model.whiteboard`: the whole model, three contexts, inside the first aggregate's folder (the same placing as r3-widget-01), where the graph does not read it as a domain model because it is not in a `.context` folder.

## Tier that should catch it
Heavy (a render through the cdd server): no spec renders a DDD model to a code format and checks what is on disk afterwards.
