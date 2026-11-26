# A render to TypeScript keeps Python types and call names, and from Python code it declares no property, imports nothing and calls no super constructor, so the file does not compile

- **Charter:** Round 3 - Clean Engineering (modules, model, code) in every format, checks 1, 2 and 4
- **Tester:** Widget
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers this.
- **Module and class:** `cdd_guidance/practices/clean_engineering/model/typescript/typescript_class_model.py` `TypeScriptCleanEngineeringModel` (writing)
- **Severity:** wrong result

## Steps
Sandbox `C:\dev\_et\round3\widget\work`, session `main`, throwaway cdd server on the build at 4d47fdf8e (`drv\go.sh c2.json` for the model, `e1.json` for the code).

1. Model: `render.render {"guidance":"clean-engineering-model","format":"typescript","paths":["src/ordering/.context/ordering-model.md"],"source":"markdown"}` (result kept as `drv\out\ts-from-md\ordering\ordering.ts`)
2. Code: `render.render {"guidance":"clean-engineering-code","format":"typescript","paths":["src/ordering/cart.py"]}` and the same for `src/fulfilment/shipment.py` (results in `drv\out\code-ts`)

## Expected
TypeScript that holds what the source holds: types in TypeScript's spelling, calls that name operations as the file itself spells them, the properties of each class, the classes it uses from other files, and a subclass constructor that calls its base.

## Actual
1, from the markdown model:

    lines: list[CartLine];                     // Python's list[...]; number, string, boolean are translated beside it
    add(book: Book, quantity: int): CartLine { // int here, number for the same word in CartLine's constructor
      Book.is_in_stock();                      // the operation itself is written isInStock; checkOut, customerId are renamed

2, from the Python code:

    class EmptyCart extends ValueError {
    }
    class Cart {
      constructor(customerId: string) {
        // python body to translate: ...
        this.customerId = customerId;          // no property is declared: customerId, lines
      }
      add(book: Book, quantity: int): CartLine {

    class ExpressShipment extends Shipment {
      constructor(order: Order, address: string, courier: string) {
        // super().__init__(order, address)
        this.order = order;                    // no super(...) call

No class of `cart.ts` declares a property, so `lines` (set to `[]` in `__init__`) and `dispatched` are nowhere but in a comment; no file imports Book, CartLine, Order, Payment or Shipment's Order. Bodies left as "python body to translate" comments are as round 2 noted and are not counted here.

## Tier that should catch it
Unit: `sketch_typescript_render_spec.py` and `code_render_spec.py` check parts of the TypeScript writer; none renders a class with a `list[...]` property, an `int` parameter, a call note, or a subclass, and none checks that the properties set in a Python `__init__` are declared.

## Status: fixed (2026-11-23)
- From the markdown model (already fixed before this pass by `ed5bc974e` and the one type translation, `CodeLanguage.type_name`): `lines: CartLine[];`, `quantity: number` wherever the model says `int`, and a call note named as the operation is spelled in TypeScript (`Book.isInStock();`).
- From Python code, fixed now (`cdd_guidance/practices/clean_engineering/model/code_class_model.py`, `source_facts.py`, `cdd_guidance/practices/source_code/code_body.py`):
  - each field a constructor assigns and the class does not declare becomes a declared property, typed as its assignment writes it or as the parameter it is assigned from (`declare_assigned_fields`, `ClassSourceFacts.assigned_fields`): `customerId: string;`, `lines: CartLine[];`;
  - the imports the Python file states are written as TypeScript imports (`CodeLanguage.imports_in`, `import_line`): `import { Book, OutOfStock } from "src/catalogue/book";`;
  - a subclass's constructor calls its base class's constructor with what the Python passed (`super(order, address);`) and assigns only the rest (`base_constructor_arguments`, `base_constructor_call`);
  - a class extending one of Python's own failures extends `Error` (`ValueError` and the others are TypeScript's and JavaScript's `Error` in `type_names`).
- Covered by `cdd_guidance/practices/clean_engineering/model/code_render_spec.py`: "Python code rendered to TypeScript" (on the Bookshop's `cart.py` and `shipment.py`) and "a markdown class model rendered to TypeScript" (on `ordering-model.md`).
- Bodies translated (2026-11-24): a body written in code is now translated into the other language statement by statement, by one translation every code render uses (`BodyTranslation`, `cdd_guidance/practices/source_code/statement_translation.py`, called from `CodeCleanEngineeringModel.render_body` and the constructor, which DDD's render writes through). Python is read with `ast`; a TypeScript or JavaScript body is read by `ScriptReading` into the same syntax tree. It covers assignments to locals and fields, returns, calls with their arguments (Python keyword arguments in the order the model's operation declares its parameters, else as one object), if / elif / else, a loop over a collection or a range, while, raise / throw, comparisons and `and` / `or` / `not`, `None`, `True` and `False`, strings and f-strings / template literals, list and dict literals, `len(x)` / `x.length`, list comprehensions / `filter` and `map`, a few list and string methods, and the base class's constructor. A statement outside that subset stays in its own language under a "python statement to translate:" note, the body then ends with the line that fails until it is written, and comments are kept above the statement they were written over. Covered by `cdd_guidance/practices/clean_engineering/model/code_render_spec.py`, "a body written in code, rendered into the other language" (Python to TypeScript, and back, and TypeScript to Python), and `class_model_render_heavy_spec.py` (a Python module rendered to TypeScript through a cdd server, its body saved as TypeScript).
- Still not translated: generator expressions and calls such as `sum`, `any`, `all`, `sorted`, `enumerate`, `zip`, `dict`, `list`, `int`, `float`; slices; `with`, `try`, `del`, `assert`, `lambda` with a block, tuple unpacking, `for ... else`; script `?.`, `??`, `switch`, `try`, arrow functions with a block body, destructuring, and typed arrow parameters. TypeScript and JavaScript are not translated into each other (a body between them stays under its note), and `===` comes back to Python as `==`, not `is`. A note above a statement inside a nested block is written before that statement, and a comment on the same line as code is written on its own line above it. A call made inside real code is still read for the graph and the markdown model by name only (`-> load`): the graph's rules join calls by those names, so giving them arguments would change every rule that reads them; in code the translated body keeps each call with its arguments.
