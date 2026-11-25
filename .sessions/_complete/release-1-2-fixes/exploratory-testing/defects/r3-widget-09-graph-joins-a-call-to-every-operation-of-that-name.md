# The graph joins a call to every operation of that name in the project: super().__init__ becomes an edge to six other classes' constructors, and order.total() an edge to Cart.total

- **Charter:** Round 3 - Clean Engineering (modules, model, code) in every format, checks 1, 2 and 4
- **Tester:** Widget
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers this.
- **Module and class:** `cdd_guidance/practices/clean_engineering/model/call_graph.py` (callees matched by name), read through `graph_reading.py` `GraphReading`
- **Severity:** wrong result

## Steps
Sandbox `C:\dev\_et\round3\widget\work`, session `main`, throwaway cdd server on the build at 4d47fdf8e (`drv\go.sh g1.json`). The code under `src/` (11 Python files; copy in `drv\seed\code`):

    class Shipment:
        def __init__(self, order: Order, address: str) -> None:
            self.order: Order = order
        def dispatch(self) -> None:
            if not self.order.payment.authorised or self.order.total() <= 0: ...

    class ExpressShipment(Shipment):
        def __init__(self, order: Order, address: str, courier: str) -> None:
            super().__init__(order, address)

1. `graph.load_files {"folder":"C:/dev/_et/round3/widget/work","practices":["clean_engineering"],"files":["src"]}`
2. `graph.save_json {}`, then read the `invokes` edges of `.sessions/main/graph.json`.

## Expected
10 `invokes` edges, one for each call the code makes on another operation: reserve -> is_in_stock, search -> matches, add -> is_in_stock, Cart.total -> subtotal, check_out -> authorise, check_out -> place, place -> reserve, Order.total -> subtotal, dispatch -> Order.total, ExpressShipment.__init__ -> Shipment.__init__.

## Actual
17 `invokes` edges: those 10 and 7 that point at operations the code never calls:

    dispatch:Shipment          -> total:Cart              (self.order is typed Order)
    __init__:ExpressShipment   -> __init__:Book
    __init__:ExpressShipment   -> __init__:Catalogue
    __init__:ExpressShipment   -> __init__:Cart
    __init__:ExpressShipment   -> __init__:CartLine
    __init__:ExpressShipment   -> __init__:Order
    __init__:ExpressShipment   -> __init__:Payment

The wrong edges cross modules (fulfilment to catalogue, which fulfilment does not import), so anything that reads coupling from the graph sees calls that are not there. The model rendered to TypeScript and loaded gives the same `dispatch -> total:Cart`, and `constructor:Order -> Property lines:Cart`. The two objects the code does make, `CartLine(book, quantity)` in `Cart.add` and `Order(self.lines, payment)` in `Cart.check_out`, have no edge, and both classes' `constructs` fact is `[]`.

## Tier that should catch it
Unit, on `call_graph.py`: no example holds two classes with an operation of the same name, or a subclass calling `super().__init__`, and counts the edges.

## Also seen by
- Cog, round 3 second pass: the combined project: 943 Clean Engineering `invokes` edges, 405 of them from Python to TypeScript or back, 793 to another file; `self.status = ...` in `src/ordering/order.py` `Order.__init__` is an edge to nine properties named status, lines or payment in other classes.
- Lens, round 3 second pass: in the Files app graph view `OrderNotPaid.__init__` > invokes lists 26 rows all named `__init__`, and `Order.pack` > invokes lists `status` three times and `Order.confirmation` `total` four times, each a same-named property of another class, with one tooltip.
