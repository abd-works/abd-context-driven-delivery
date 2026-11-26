# widget-8: A `**CartRepository** «Repository»` block under a `### **Cart**` card is drawn nowhere in drawio, and rendered to Python its operations become Cart's own methods (`Cart.load`, `Cart.save`) while its property `carts` is dropped

- **Charter:** C4
- **Tester:** Widget
- **Story:** no scenario. pml-web's domain model writes every aggregate's repository this way ("The root's section ends with its repository, a `**{Root}Repository** «Repository»` block … drawn inside the root's card"), and in pml-web's `#### Class` layout the drawio does draw it inside the root's card; the Clean Engineering template (`templates/class-model.md`) does not name the block. Promise: "The same classes, operations, and relationships must appear in every selected representation".
- **Module and class:** the Clean Engineering markdown model reader (the class section under `### **Cart**` takes the block's members as Cart's); drawio class writer (`model/drawio/drawio_class_model.py`).
- **Severity:** wrong result (or question, if the block is not a notation the template supports: then it should be refused or reported, not folded into the root)

## Steps

1. Copy `cdd_guidance/practices/clean_engineering/model/fixtures/bookshop/ordering-model.md` to `src/ordering/.context/class-model.md` of a throwaway git project.
2. After Cart's last operation (`// an empty cart is refused`) add:
   ```
   **CartRepository** «Repository»

   ------
   + carts: Collection<Cart>
   ----
   + load(customer_id: str): Cart
   + save(cart: Cart): Cart
   ```
3. Render it with `clean-engineering-model` to `drawio`, and to `python` (`Render().for_call(ToolCall({}, ROOT)).render(...)`), then the Python back to markdown.

## Expected

CartRepository as its own class (a card or a section of Cart's card in drawio; a class of its own in Python), with `carts`, `load` and `save` on it.

## Actual

- drawio: "CartRepository" appears only inside the hidden kept source document; no card or section draws it.
- Python: `class Cart` gains `def load(self, customer_id: str) -> Cart` and `def save(self, cart: Cart) -> Cart`; `carts` is nowhere.
- Python back to markdown: `## Cart <<Aggregate Root>>` lists `+ load(customer_id: str): Cart` and `+ save(cart: Cart): Cart` as Cart's operations; the repository is gone for good.

(The class language itself survived md → Python → md with its paragraph break and bullets.)

## Tier that should catch it

Unit: a CE model example with a repository block in the template layout, rendered to drawio and Python.

## Also seen by
