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
