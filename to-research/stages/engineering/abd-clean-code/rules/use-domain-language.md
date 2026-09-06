---
scanner: domain_language_code_scanner.py
---

### Rule: Use Domain Language

Class names are domain entities. Method names are domain responsibilities. Avoid generic names like Manager, Handler, process(), and execute().

#### DO

- Name classes after domain entities from the Domain Language.
- Name methods after domain responsibilities, not technical verbs.

```python
class CheckoutService:
    def __init__(self, invoice_repo, inventory, mailer):
        self._invoice_repo = invoice_repo
        self._inventory = inventory
        self._mailer = mailer

    def process_order(self, user, cart): ...
    def apply_loyalty_discount(self, user, total): ...
```

```javascript
export class CheckoutService {
  constructor(invoiceRepo, inventory, mailer) {
    this._invoiceRepo = invoiceRepo;
    this._inventory = inventory;
    this._mailer = mailer;
  }

  async processOrder(user, cart) { }
  applyLoyaltyDiscount(user, total) { }
}
```

#### DON'T

- Use generic class names: Manager, Handler, Helper, Processor, Util.
- Use generic method names: process(), handle(), execute(), run(), do().

```python
class Manager:                              # WRONG: no domain meaning
    def process(self, data): ...            # WRONG: too generic, hides intent
    def handle(self, event): ...
```

```javascript
export class Handler {                      // WRONG: no domain meaning
  execute(data) { }                         // WRONG: too generic, hides intent
  run(event) { }
}
```
