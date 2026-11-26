# A class model rendered to Python and back to markdown loses its relationship kinds, notes and the class each call is made on, and gains a private __init__ operation; the same trip through TypeScript keeps them

- **Charter:** Round 3 - Clean Engineering (modules, model, code) in every format, checks 1, 2 and 4
- **Tester:** Widget
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers a class model's trip through the formats.
- **Module and class:** `cdd_guidance/practices/clean_engineering/model/python/python_class_model.py` `PythonCleanEngineeringModel` (reading: it writes `# << composition >>`, the notes and `Book.is_in_stock()` into the Python, and does not read them back)
- **Severity:** wrong result

## Steps
Sandbox `C:\dev\_et\round3\widget\work`, session `main`, a fresh throwaway cdd server on the build at 4d47fdf8e (`drv\go.sh c2.json`, then `c3.json`, `c4.json`). `src/ordering/.context/ordering-model.md` (copy in `drv\seed\ordering`) holds, for Cart:

    + Cart(customer_id: str)
    ------
    + customer_id: str
    	// who is filling the cart
    + << composition >> lines: list[CartLine]
    ----
    + add(book: Book, quantity: int): CartLine
    	-> Book.is_in_stock
    	// a book out of stock is refused

1. `render.render {"guidance":"clean-engineering-model","format":"python","paths":["src/ordering/.context/ordering-model.md"],"source":"markdown"}`; save the content as `src/ordering/ordering.py`.
2. `render.render {"guidance":"clean-engineering-model","format":"markdown","paths":["src/ordering/ordering.py"]}`

## Expected
"The same classes, operations, and relationships must appear in every selected representation" (`clean_engineering.md`, model). The Python of step 1 holds everything as comments and calls (`# << composition >>`, `# who is filling the cart`, `Book.is_in_stock()`), and the same trip through TypeScript brings all of it back.

## Actual
`src/ordering/ordering.md` (kept in `drv\out\trips\alone\python-to-markdown-ordering`):

    ## Cart <<Aggregate Root>>

    + Cart(customer_id: str, lines: list[CartLine])
    ------
    + customer_id: str
    + lines: list[CartLine]
    ----
    - __init__(customer_id: str): None
    + add(book: Book, quantity: int): CartLine
    	-> is_in_stock

Lost, for every class of the three models: each `<< composition | aggregation | association >>` (6), every `//` note (14), and the class of each call (`-> Book.is_in_stock` is `-> is_in_stock`). Changed: the constructor line lists every property instead of the constructor's parameters. Added: `- __init__(...)` as a private operation of each class. Kept: class names, stereotypes, the base of ExpressShipment, properties with types, operations with parameters and return types. Also lost, as through every format: front matter, the Module line, the module's and groups' descriptions (widget-08).

## Tier that should catch it
Unit: `markdown_to_code_spec.py` and `class_dependency_round_trip_spec.py` cover parts of this trip; no example reads back the relationship kind, the note and the call owner the Python render itself wrote.
