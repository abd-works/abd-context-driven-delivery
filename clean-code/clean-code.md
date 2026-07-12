
# Instructions

Write production code that implements behavior using **domain language**, **clean functions**, **explicit dependencies**, and **observable design**.

Run scanners after generation; each scanner reports a **rule name** (e.g. `separate-concerns`). Search this file for that slug in the bullets or inline examples.

**Other languages:** default examples below are Python. For a full module walkthrough see `examples/examples.md`. For scaffold layout see `formats/python/clean-code-template.py`, `formats/javascript/clean-code-template.js`, `formats/typescript/clean-code-template.ts`, `formats/java/clean-code-template.java`, and siblings under `formats/*/`.

---
# Concepts
## What is clean code?

Clean code reads like well-written prose. Every name answers "why does this exist?", every function does exactly one thing, and every dependency is visible at the construction site. You can change any one piece without surprising the rest.

---

## Domain language

Class names are domain entities — nouns from the story model: `Cart`, `Order`, `Product`. Method names are domain responsibilities — verbs those entities own: `place_order`, `confirm`, `add`. Avoid `Service`, `Manager`, `Handler`, `process()`, and `execute()`.

**Wrong:** `CheckoutService.process_order(user, cart)` — a service acting on passive data.
**Right:** `cart.place_order()` — the Cart places its own order.

- **`use-domain-language`** — Name classes after domain entities and methods after domain responsibilities, not technical verbs; one module per sub-epic area, one class per domain entity.

```python
class Cart:                                     # use-domain-language
    def place_order(self) -> Order:             # use-domain-language
        if self.is_empty:
            raise EmptyCartError("Cannot place an order from an empty cart.")
        return Order(owner=self._owner, items=tuple(self._items))
```

---
## Class design

- **`keep-classes-single-responsibility`** — Each class has **one reason to change**; keep classes under 200–300 lines.
- **`enforce-encapsulation`** — Hide implementation details behind `_` or `#` private helpers; expose **behavior** through domain methods, not raw data through public attributes.
- **`eliminate-duplication`** — Repeated logic gets one canonical function — extract copy-pasted calculations and operations.
- **`use-explicit-dependencies`** — Pass every collaborator through the **constructor**, store as private attributes (`_repo`, `_mailer`); never reach for a global or construct a collaborator inside `__init__`.
- Prefer properties over explicit `get_`/`set_` methods (`@property` in Python, `get`/`set` in JS/TS). Properties calculate and return — no side effects. No scanner yet; human review only.

```python
class Cart:                                     # keep-classes-single-responsibility
    def __init__(self, owner) -> None:
        self._owner = owner                     # enforce-encapsulation
        self._items: list[LineItem] = []        # enforce-encapsulation

    @property
    def is_empty(self) -> bool:                 # enforce-encapsulation
        return len(self._items) == 0

    def add(self, product, qty: int) -> None:   # enforce-encapsulation
        self._items.append(LineItem(product=product, qty=qty))

    @property
    def subtotal(self) -> float:
        return round(sum(i.extended_price for i in self._items), 2)

def line_total(item) -> float:                  # eliminate-duplication
    return round(item.unit_price * item.qty, 2)

def cart_subtotal(items) -> float:              # eliminate-duplication
    return round(sum(line_total(i) for i in items), 2)

class OrderService:                             # use-explicit-dependencies
    def __init__(self, repository, mailer, logger) -> None:
        self._repository = repository           # use-explicit-dependencies
        self._mailer = mailer
        self._logger = logger
```

---
## Function discipline

- **`keep-functions-single-responsibility`** — Each function has **one reason to change** — pure calculation or orchestration, not both.
- **`separate-concerns`** — Keep pure calculations separate from side effects; orchestration owns I/O, logging, and mutation.
- **`keep-functions-small-focused`** — Functions stay under **20 lines**; extract named helpers for complex logic.
- **`use-clear-function-parameters`** — Prefer **0–2 parameters**; use a dataclass or options object when more configuration is needed; no boolean flag parameters.
- **`simplify-control-flow`** — Use **guard clauses** at the top; maximum **2 nesting levels**.
- **`maintain-abstraction-levels`** — Step down one abstraction level at a time — high-level functions call named helpers; never mix raw SQL or HTTP with business logic.

```python
def subtotal(items: list) -> float:             # separate-concerns
    return sum(i.extended_price for i in items) # keep-functions-single-responsibility

def checkout(user, cart, services):             # keep-functions-single-responsibility
    sub = subtotal(cart.items)                  # maintain-abstraction-levels
    services.logger.info("checkout", extra={"user_id": user.id})  # separate-concerns
    return sub

def add_item(cart, product, qty: int) -> None:   # simplify-control-flow
    if qty < 1:                                 # simplify-control-flow
        raise InvalidQuantityError(f"qty for '{product.sku}' must be >= 1")
    cart.add(product=product, qty=qty)          # keep-functions-small-focused

def apply_discount(order, discount_policy) -> float:  # use-clear-function-parameters
    return discount_policy.rate_for(order)      # use-clear-function-parameters
```

---
## Naming

- **`use-intention-revealing-names`** — Names reveal intent — no abbreviations or single-letter identifiers outside trivial loop indices.
- **`provide-meaningful-context`** — Replace magic numbers and unexplained literals with **named constants** that state purpose and unit.
- **`use-consistent-naming`** — Use **one word per concept** across the codebase (`get_`, not a mix of `get_`, `fetch_`, and `retrieve_`).

```python
TAX_RATE = 0.13                                 # provide-meaningful-context
LOYALTY_THRESHOLD = 1000                        # provide-meaningful-context

def extended_price(line_item) -> float:         # use-intention-revealing-names
    return round(line_item.unit_price * line_item.qty, 2)

def fetch_order(order_id):                      # use-consistent-naming  (pick one verb; use everywhere)
    return repository.get(order_id)
```

---

## Error handling

- **`use-exceptions-properly`** — Define **domain exceptions** that name what went wrong (`EmptyCartError`, `PaymentDeclinedError`); never return `None` to signal failure.
- **`never-swallow-exceptions`** — If you catch an exception you cannot handle, log and re-raise or convert to a domain exception — never swallow.

```python
class EmptyCartError(Exception):                # use-exceptions-properly
    """Raised when place_order() is called on an empty cart."""

def place_order(self) -> Order:
    if self.is_empty:
        raise EmptyCartError("Cannot place an order from an empty cart.")  # use-exceptions-properly
    return Order(owner=self._owner, items=tuple(self._items))

def load_order(order_id, repository):
    try:
        return repository.get(order_id)
    except KeyError as exc:
        logger.exception("order not found", extra={"order_id": order_id})
        raise OrderNotFoundError(order_id) from exc  # never-swallow-exceptions
```

---

## Comments

- **`stop-writing-useless-comments`** — Comments explain **why**, not **what**; delete noise comments and commented-out code.

```python
# Loyalty tier resets annually — business rule from pricing policy doc
if customer.annual_spend >= LOYALTY_THRESHOLD:  # stop-writing-useless-comments
    apply_loyalty_discount(order)
```

---

# Module shape

Canonical layout: module docstring (domain area + responsibilities), named constants, domain exceptions, entities, private helpers. See `formats/*/{domain-slug}-template.*` and the full Cart/Order module in `examples/examples.md`.
