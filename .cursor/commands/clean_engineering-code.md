# clean_engineering-code

Use clean_engineering guidance at `code` fidelity only.

Use higher-level fidelity guidance only when required information is missing. Reference these commands with `@`; do not inline their content:
@clean_engineering-model
@clean_engineering-modules

# Contexts

## code

**Default format:** Python

**Goal:** Two phases in one fidelity — first lock down the typed contracts (`Class(I{Class})` when an interface was requested at model, otherwise the `Class` stub already in place from model), then wire the full production implementation. When an `I{Class}` exists it stays as the stable seam throughout; when it does not, `Class` itself is the seam.

A vertical is not at **code** fidelity while it still depends on a mockup / Story Demo shell as the only UI, or on in-memory / fake factories as the only "backend." **Code** means real backend **and** real frontend (UX **code** fidelity) — not greybox + demo domain alone.

### Phase 1 — typed contracts

- **When an `I{Class}` interface was requested at model** (interfaces are optional — see `## model` § Interfaces): add `Class(I{Class})` (Java: `implements I{Class}`) in the **same file** as `I{Class}`. Do **not** fill out `I{Class}` or add private members to it.
- **When no interface was requested:** skip that step — the empty `Class` stub already exists from **model** fidelity in its own family file; continue directly onto it.
- On `Class`: implement public properties and operations; add private properties/operations as **empty interfaces** (`...` / `@abstractmethod`); add each relationship with its **kind** (composition / aggregation / association) and **cardinality** (e.g. `1..*`, `0..1`); invariants as **comments** (not methods) — formalizing any named at `## model` § Invariants, or newly introduced here.
- Interactions: `@interaction` abstract methods on `Class` (never on `I{Class}`, whether or not one exists) — formalizing any named at `## model` § Interactions, or newly introduced here.
- Complete `{Type}ExampleFactory` — fill in Fake, Isolated, and Production modes per the **Example factories** pattern in `## model`.
- Refresh `.context/module-context.md` still **public-seam-only**: ensure **Public API**, **Constraint**, and **Dependencies** match the implemented seam; add **Extend** / **Mechanism** only for public variation points. **Do not** add **Participants**, **Internal design**, **Domain separation**, or any other internals section — those stay in source and sketches, never in module-context.
- Edit the same `.context/module-context.md` — do not create parallel context files.
- Edit so remaining language-companion bullets sit on members; class-level docstring keeps only the opening definition.


State which side **navigates** to the other — direction is explicit.

### Phase 2 — production implementation

- Fill all remaining empty bodies on `Class` (no `...`, no `# TODO` on production ops/props).
- Wire **Production** collaborators — real persistence, services, and cross-module dependencies — not Fake-mode stubs as the shipping path.
- Drop `@interaction` methods — not needed once implemented.
- Keep invariants as **comments**.
- If an `I{Class}` exists, leave it in place for the public seam and for hand-written test fakes; if it does not, `Class` itself remains the seam.
- Add exceptions, named constants, private helpers as needed.
- Edit so language-companion prose stays as the class docstring — implementations sit beneath intent, they do not replace it.
- Edit so the implemented public surface matches the seam already designed — a short caller-facing API with real behaviour behind it, still living in the module folder.

### Rules

**Operations**

- **`keep-operations-small-focused`** — Under **20 lines**; extract named helpers.
- **`simplify-control-flow`** — Guard clauses; max nesting depth as enforced by scanners.
- **`maintain-abstraction-levels`** — One level at a time; no raw I/O mixed into orchestration names.

**Naming / context**

- **`provide-meaningful-context`** — Named constants for magic numbers and unexplained literals.

**Errors / comments**

- **`use-exceptions-properly`** — Domain exceptions that name the failure.
- **`never-swallow-exceptions`** — Log and re-raise or convert; never bare swallow.
- **`stop-writing-useless-comments`** — Comments explain **why**, not **what**.

## shopping-cart/examples.py

# @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
# invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
# invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
from __future__ import annotations
from abc import ABC, abstractmethod
from decimal import Decimal


class IShoppingCart(ABC):
    """Running tally of what a customer intends to buy in a single shopping session."""

    @property
    @abstractmethod
    def customer(self) -> Customer: ...

    @property
    @abstractmethod
    def items(self) -> list[CartItem]: ...

    @property
    @abstractmethod
    def discount(self) -> Discount | None: ...

    @property
    @abstractmethod
    def checked_out(self) -> bool: ...

    @abstractmethod
    def __init__(self, customer: Customer) -> None: ...

    @abstractmethod
    def add_item(self, product: str, quantity: int, unit_price: Decimal) -> None: ...

    @abstractmethod
    def remove_item(self, product: str) -> None: ...

    @abstractmethod
    def apply_discount(self, discount: Discount) -> None: ...

    @abstractmethod
    def compute_total(self) -> Decimal: ...

    @abstractmethod
    def checkout(self, inventory: Inventory) -> None: ...


class ShoppingCart(IShoppingCart):
    """Running tally of what a customer intends to buy in a single shopping session."""

    """@association - belongs to exactly one customer whose identity anchors the cart."""
    @property
    def customer(self) -> Customer:
        return self._customer

    """@composition - collects CartItems as the customer browses; keeps the total current."""
    @property
    def items(self) -> list[CartItem]:
        return self._items

    """@association - optional reduction rule applied before the total is computed."""
    @property
    def discount(self) -> Discount | None:
        return self._discount

    """Seals the cart permanently once the customer commits to checkout."""
    # Invariant: once true, never reverts to false.
    @property
    def checked_out(self) -> bool:
        return self._checked_out

    def __init__(self, customer: Customer) -> None:
        self._customer = customer
        self._items: list[CartItem] = []
        self._discount: Discount | None = None
        self._checked_out = False

    # region Public operations

    """Adds a line to the cart; merges quantity if the product is already present."""
    # Invariant: cart may not be modified after checkout.
    # Invariant: quantity must be at least 1.
    def add_item(self, product: str, quantity: int, unit_price: Decimal) -> None:
        ...

    def remove_item(self, product: str) -> None:
        ...

    """Attaches a reduction rule; replaces any previously applied discount."""
    def apply_discount(self, discount: Discount) -> None:
        ...

    """Sums line totals and applies the discount if one is present."""
    def compute_total(self) -> Decimal:
        ...

    """Verifies availability with Inventory, then seals the cart; raises if already checked out."""
    def checkout(self, inventory: Inventory) -> None:
        ...

    # endregion

    # region Private operations (empty until code)

    @abstractmethod
    def _find_item(self, product: str) -> CartItem | None: ...

    # endregion

    # region Interactions (specification only)

    @abstractmethod
    def adding_an_item_merges_if_product_already_present(self) -> None:
        """@interaction"""
        ...

    @abstractmethod
    def checkout_verifies_availability_before_sealing(self) -> None:
        """@interaction"""
        ...

    # endregion


class ICartItem(ABC):
    """A single product choice inside a ShoppingCart."""

    @property
    @abstractmethod
    def product(self) -> str: ...

    @property
    @abstractmethod
    def quantity(self) -> int: ...

    @property
    @abstractmethod
    def unit_price(self) -> Decimal: ...

    @abstractmethod
    def __init__(self, product: str, quantity: int, unit_price: Decimal) -> None: ...

    @abstractmethod
    def line_total(self) -> Decimal: ...

    @abstractmethod
    def update_quantity(self, quantity: int) -> None: ...


class CartItem(ICartItem):
    """A single product choice inside a ShoppingCart."""

    # Invariant: quantity is at least one.
    # Invariant: unit_price is non-negative.

    @property
    def product(self) -> str:
        return self._product

    @property
    def quantity(self) -> int:
        return self._quantity

    @property
    def unit_price(self) -> Decimal:
        return self._unit_price

    def __init__(self, product: str, quantity: int, unit_price: Decimal) -> None:
        self._product = product
        self._quantity = quantity
        self._unit_price = unit_price

    def line_total(self) -> Decimal:
        ...

    def update_quantity(self, quantity: int) -> None:
        ...


class IDiscount(ABC):
    """A reduction rule a customer applies to a ShoppingCart."""

    @property
    @abstractmethod
    def code(self) -> str: ...

    @property
    @abstractmethod
    def reduction(self) -> Decimal: ...

    @abstractmethod
    def __init__(self, code: str, reduction: Decimal) -> None: ...

    @abstractmethod
    def is_valid(self, cart: IShoppingCart) -> bool: ...

    @abstractmethod
    def compute_reduction(self, subtotal: Decimal) -> Decimal: ...


class Discount(IDiscount):
    """A reduction rule a customer applies to a ShoppingCart."""

    # Invariant: discount cannot reduce total below zero.

    @property
    def code(self) -> str:
        return self._code

    @property
    def reduction(self) -> Decimal:
        return self._reduction

    def __init__(self, code: str, reduction: Decimal) -> None:
        self._code = code
        self._reduction = reduction

    def is_valid(self, cart: IShoppingCart) -> bool:
        ...

    def compute_reduction(self, subtotal: Decimal) -> Decimal:
        ...

...                                                             # S / C

        ...                                                             # S / C

    def _{private_helper}(self, {param}: {Type}) -> {ReturnType}:       # C
        ...                                                             # C

    def {delta_operation}(self, {param}: {Type}) -> {ReturnType}:       # S/C
        ...                                                             # S/C

        ...                                                             # S/C