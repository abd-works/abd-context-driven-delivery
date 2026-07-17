## Code Fidelity — Generate

Produce **fully implemented production code**. Every operation body is written — no `...`, no `# TODO`, no stubs. All specification-fidelity contracts are honoured; this fidelity fills them in using clean code discipline.

The language-fidelity natural language description travels as the class docstring at every fidelity. At engineering, it stays — implementations do not replace prose intent; they sit beneath it.

Apply every rule from the Concepts section (class design, encapsulation, relationships, invariants) plus the following.

---

### Modules

Canonical module layout: module docstring (domain area + responsibilities), named constants, domain exceptions, entities, private helpers. One module per sub-epic area. Apply **`cohesive-file`**: one file per class family (not one class per domain entity). All of that code stays in the module folder (`physical-folder`).

#### Module rules

Apply `deep-module`, `named-seam-and-constraint`, and `physical-folder` from `clean-engineering.md` at this fidelity: verify that the implemented public surface is a short named list and that substantial functionality sits behind it. If the public surface lists everything the module contains, the seam is fictional — push helpers private and tighten the boundary before the implementation ships.

- **`general-purpose-surface`** — Verify the module's public interface is not hardcoded to one caller's current shape. If method names, return shapes, or parameter groupings mirror a specific consumer's UI or workflow, refactor the surface to address the root problem space and let the consumer adapt. A backend surface hardcoded to today's UI creates coupling that will break as the consumer evolves.
- **`errors-out-of-existence`** — For routine edge cases, prefer total functions that return sensible defaults or empty states (`[]`, `None`, an empty result object) over throwing. Reserve exceptions — and the `use-exceptions-properly` rule below — for genuine failures the caller cannot ignore. A caller wrapping every call in `try/except` for ordinary inputs is a signal the surface is under-designed.

---

### Classes

#### Domain language

- **`use-domain-language`** — Class names are domain entities (nouns from the story model: `Cart`, `Order`, `Product`). Operation names are domain responsibilities — verbs those entities own: `place_order`, `confirm`, `add`. Avoid `Service`, `Manager`, `Handler`, `process()`, and `execute()`.

```python
class Cart:                                     # use-domain-language
    def place_order(self) -> Order:             # use-domain-language
        if self.is_empty:
            raise EmptyCartError("Cannot place an order from an empty cart.")
        return Order(owner=self._owner, items=tuple(self._items))
```

#### Operation discipline

`keep-operations-single-responsibility` and `use-clear-operation-parameters` are defined in Concepts (`clean-engineering.md`) and apply here. Engineering adds:

- **`separate-concerns`** — Keep pure calculations separate from side effects; orchestration owns I/O, logging, and mutation.
- **`keep-operations-small-focused`** — Operations stay under **20 lines**; extract named helpers for complex logic.
- **`simplify-control-flow`** — Use **guard clauses** at the top; maximum **2 nesting levels**.
- **`maintain-abstraction-levels`** — Step down one abstraction level at a time — high-level operations call named helpers; never mix raw SQL or HTTP with business logic.

```python
def subtotal(items: list) -> float:             # separate-concerns
    return sum(i.extended_price for i in items) # keep-operations-single-responsibility (Concepts)

def checkout(user, cart, services):             # keep-operations-single-responsibility (Concepts)
    sub = subtotal(cart.items)                  # maintain-abstraction-levels
    services.logger.info("checkout", extra={"user_id": user.id})  # separate-concerns
    return sub

def add_item(cart, product, qty: int) -> None:  # simplify-control-flow
    if qty < 1:
        raise InvalidQuantityError(f"qty for '{product.sku}' must be >= 1")
    cart.add(product=product, qty=qty)          # keep-operations-small-focused

def apply_discount(order, discount_policy) -> float:  # use-clear-operation-parameters (Concepts)
    return discount_policy.rate_for(order)
```

#### Naming

`use-intention-revealing-names` and `use-consistent-naming` are defined in Concepts (`clean-engineering.md`) and apply here. Engineering adds:

- **`provide-meaningful-context`** — Replace magic numbers and unexplained literals with **named constants** that state purpose and unit.

```python
TAX_RATE = 0.13                                 # provide-meaningful-context
LOYALTY_THRESHOLD = 1000                        # provide-meaningful-context

def extended_price(line_item) -> float:         # use-intention-revealing-names (Concepts)
    return round(line_item.unit_price * line_item.qty, 2)

def fetch_order(order_id):                      # use-consistent-naming (Concepts)
    return repository.get(order_id)
```

#### Error handling

- **`use-exceptions-properly`** — Define **domain exceptions** that name what went wrong (`EmptyCartError`, `PaymentDeclinedError`); never return `None` to signal failure.
- **`never-swallow-exceptions`** — If you catch an exception you cannot handle, log and re-raise or convert to a domain exception — never swallow.

```python
class EmptyCartError(Exception):                # use-exceptions-properly
    """Raised when place_order() is called on an empty cart."""

def load_order(order_id, repository):
    try:
        return repository.get(order_id)
    except KeyError as exc:
        logger.exception("order not found", extra={"order_id": order_id})
        raise OrderNotFoundError(order_id) from exc  # never-swallow-exceptions
```

#### Comments

- **`stop-writing-useless-comments`** — Comments explain **why**, not **what**; delete noise comments and commented-out code.

```python
# Loyalty tier resets annually — business rule from pricing policy doc
if customer.annual_spend >= LOYALTY_THRESHOLD:
    apply_loyalty_discount(order)
```
