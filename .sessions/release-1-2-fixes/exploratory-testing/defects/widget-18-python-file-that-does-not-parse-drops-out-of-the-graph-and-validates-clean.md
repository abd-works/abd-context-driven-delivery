# A Python file that stops parsing, or that starts with a byte-order mark, drops out of the graph without a word, and validate on it reports "No graph rule violations"

- **Charter:** Round 2 - the knowledge graph and the formats of the other practices, as an agent whose files move, rename and stop parsing between two calls
- **Tester:** Widget
- **Story:** epic "Map Work Into Knowledge Graph"; no scenario covers a file that does not parse (only review-violations-in-graph-app has a folder).
- **Module and class:** `harness/graph/graph.py` `Graph.refresh` / `load_files` (`graph_reads.py`), the Clean Engineering Python reader under `cdd_guidance/practices/clean_engineering/model/python`, and `cdd_guidance/actions/validate/validate.py`. The inventory lists a rule named `source-parses`; it reported nothing here.
- **Severity:** wrong result (the worst file in the change is the one reported clean)

## Steps
Sandbox `repo` (`C:\dev\_et\widget\work\repo`), session `main`, throwaway cdd server (`C:\dev\_et\widget\work\drv\run.py`, calls in `drv\d4.json`, `drv\d8.json`, `drv\d9.json`).

1. `src/order.py` holds class Order with an untyped parameter. `graph.load_files` on it: node `src/order.py:Order`, violations `missing-module-context` and `use-typed-signatures`.
2. Overwrite it with text that is not Python:

        class Order(:
            def total(self
                return ((

3. Write `shop/b1.py` as valid Python that starts with a UTF-8 byte-order mark (`class BomOnly: ...`); `shop/b2.py` the same class with CRLF line ends, `shop/b3.py` with tabs.
4. `graph.refresh {"paths": ["src", "shop"]}`, then `graph.return_nodes {"filter": {"types": ["OoadClass"]}}` and `{"filter": {"violations": true}}`.
5. `validate.validate {"guidance": "clean-engineering-code", "paths": ["shop/b1.py", "src/order.py"]}`

## Expected
A file named in `paths` that cannot be read is reported: a violation on the file (the `source-parses` rule), or a refusal naming it. A byte-order mark is not a reason to skip a file.

## Actual
Step 4: the refresh answers "Refreshed N files"; `src/order.py:Order` and its two violations are gone, and no node or violation names `src/order.py`. `CrlfOnly` and `TabsOnly` are in the graph, `BomOnly` is not, and nothing names `shop/b1.py`.

Step 5: `isError=False`. The saved report (`repo\.sessions\main\validation-reports\clean-engineering-code-20261119T182828.md`) says "**No graph rule violations.** All scanned graph rules passed." and names neither file.

A TypeScript file cut off mid-class (`web2/cart.ts`) also lost its class node; its package got one `conforms-to-schema` hit, so it is at least visible.

## Tier that should catch it
Heavy (`graph_build_heavy_spec.py` / `validate_heavy_spec.py`): no example refreshes or validates a file that does not parse or that carries a byte-order mark.
