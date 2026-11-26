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

## Triage

- **Status:** confirmed
- **Severity:** wrong result
- **Triaged by:** Quill
- **Why:** the `**XRepository** «Repository»` block inside its root's card is a notation the class-card family promises: the DDD model reads it (`ddd/model/markdown/class_cards.py`, "a repository drawn inside its root's card"), pml-web's model (written after the DDD model template, which extends the Clean Engineering template) writes every repository that way, and the Clean Engineering model guidance says "The same classes, operations, and relationships must appear in every selected representation". The Clean Engineering card reader took the block's lines as the root's own members, so the repository was drawn nowhere and its operations became the root's methods in code. The Clean Engineering template did not name the block; it now does.


## Fix

- **Test (unit):** `cdd_guidance/practices/clean_engineering/model/markdown/domain_model_layout_spec.py` with fixture `model/markdown/fixtures/ddd-layout-domain-model.md` (a trimmed copy of pml-web's model in the DDD template layout: front matter, `## Layout` and `## Coverage` sections, plain `####` cards, a `**CredentialsRepository** «Repository»` block, a heading repository, language, invariants, `//` notes and `->` calls), plus the bookshop template layout with a `**CartRepository** «Repository»` block. 14 of its 16 examples seen failing at HEAD (run in a detached worktree); all 16 pass after the fix. Every unit spec under `practices/clean_engineering` and `practices/ddd` passes.
- **Fix:** `model/markdown/markdown_class_model.py`: a card heading is a bold class name or a plain name followed by its `<<Stereotypes>>`, so the DDD template's `## context / ### aggregate / #### Class` reads as modules and class cards; a card keeps its heading as written (`ClassHeading.bold`) and writes a constructor line only when it was read with one; a `**Name** «Repository»` block inside a card (`REPOSITORY_IN_ROOT`, now in `class_card.py` beside the card notation) is read as a class of its own, kept in place, and written back as a block when changed. `model/base_class_model.py`: a class written from a drawing takes back the **Invariants** list the drawing does not hold. Guidance (`clean_engineering.md`, model Guidance, "Write each class card under its heading") and template (`templates/class-model.md`, the repository block) name both layouts.
- **End to end** on a copy of pml-web's `src/.context/domain-model.md` through `Render().for_call(...)`: clean-engineering-model to drawio draws 55 cards and 51 arrows (was 6 and 0); whiteboard 55 shapes, 51 arrows; drawio back to markdown leaves the file byte for byte unchanged (was +1328/-574); python writes each repository (CartRepository, SubscriptionRepository...) as its own class.
- **Commit:** dfe41aa2a (one commit for widget-5, widget-1 and widget-8: one shared fix)
