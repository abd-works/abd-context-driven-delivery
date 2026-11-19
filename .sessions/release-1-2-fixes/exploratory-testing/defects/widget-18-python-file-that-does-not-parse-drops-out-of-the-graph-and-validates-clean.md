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

## Confirmation (Cog)
- Result: confirmed
- What I ran and saw: The Clean Engineering reading on a real folder of my own through the rule fixture, which reads files the way a live load does (`C:\dev\_et\cog\w18.py`, CDD_HOME in `C:\dev\_et\cog`): `src/order.py` holding the report's broken text beside a valid `src/other.py`, and `shop/b1.py` starting with a byte-order mark beside a CRLF file, with no module card in either folder. Before the fix the graph held `CrlfOnly` and `Other` only, the `source-parses` rule reported nothing, and both files sat in the fact `unreadable_sources` on the practice's root. The cdd server and the validate report were not run.
- Cause: `cdd_guidance/practices/clean_engineering/model/code_read.py`. `keep_unreadable` kept a file that did not parse on the nearest module card and, where a folder has none, on the practice's root, "which no rule checks"; `SourceParses` (`rules/practice_wide_rules.py`) checked Module nodes only. The byte-order mark is a second cause: `_text_of` read the file as `utf-8`, so the mark reached Python's parser as a character and the file was called unparseable.
- Fix: a file that does not parse is kept on the folder that holds it when no module does, and `source-parses` checks packages too; source files are read as `utf-8-sig`. Not changed: a file that does not parse at the project's root, in no folder, is still kept on the practice's root, which no rule checks.
