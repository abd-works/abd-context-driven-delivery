# Clean Code — Concepts

## What is clean code?

Clean code reads like well-written prose. Every name answers "why does this exist?", every function does exactly one thing, and every dependency is visible at the construction site. You can change any one piece without surprising the rest.

Five properties that define clean production code:

- **Functions do one thing** — a calculation function calculates; it does not log, save, or send.
- **Names reveal intent** — `elapsed_time_in_days`, not `e`; `MILLISECONDS_PER_DAY`, not `86400000`.
- **Explicit dependencies** — every collaborator arrives through the constructor; no hidden globals.
- **Domain language** — class and method names come from the business model, not from technical patterns.
- **No hidden state** — internals are private; callers see behavior, not data.

---

## Domain language

Class names are domain entities — the nouns from your story model: `Cart`, `Order`, `Product`, `Invoice`, `Inventory`. Method names are domain responsibilities — the verbs those entities own: `place_order`, `confirm`, `reserve`, `apply_loyalty_discount`. `Service`, `Calculator`, `Manager`, `Handler` are technical suffixes that hide what the code actually does.

**Wrong:** `CheckoutService.process_order(user, cart)` — a service acting on passive data objects.
**Right:** `cart.place_order()` — the Cart places its own order; the Order knows its own total.

---

## Function discipline

Every function has a **single responsibility** and stays under **20 lines**. Prefer **0-2 parameters**; use a dataclass or destructured object when more configuration is needed. Avoid boolean flag parameters. Use **guard clauses** at the top to eliminate deep nesting.

---

## Dependency injection

Pass every collaborator — repositories, mailers, loggers, external clients — through the **constructor**. Store them as private attributes (`_repo`, `_mailer`). Never reach for a global, and never construct a collaborator inside `__init__`.

---

## Class design

Each class has **one reason to change** (Single Responsibility Principle). Keep classes under 200-300 lines. Expose **behavior** through domain methods, not raw data through public attributes. Hide implementation details behind `_private` helpers.

---

## Properties over getters and setters

Prefer properties and property setters over explicit `get_`/`set_` methods. Use the language's property feature (`@property` in Python, `get`/`set` accessors in JS). Properties should never perform side effects — only calculate and return.

---

## Error handling

Define **domain exceptions** that name what went wrong in the domain (`EmptyCartError`, `PaymentDeclinedError`). Never return `None` to signal failure — raise. Never swallow: if you catch an exception you cannot handle, log and re-raise.

---

## The shape of good production code

See [`../templates/clean-code.py`](../templates/clean-code.py) for the canonical module layout with fully worked examples for constants, exceptions, and domain entities.
