---
scanner: explicit_dependencies_scanner.py
---

### Rule: Use Explicit Dependencies

Pass all dependencies through the constructor. No hidden globals, no constructing collaborators inside __init__.

#### DO

- Accept every dependency as a constructor parameter.
- Store dependencies as private attributes.

```python
class CheckoutService:
    def __init__(self, invoice_repo, inventory, mailer):
        self._invoice_repo = invoice_repo   # injected
        self._inventory = inventory         # injected
        self._mailer = mailer               # injected
```

```javascript
export class CheckoutService {
  constructor(invoiceRepo, inventory, mailer) {
    this._invoiceRepo = invoiceRepo;        // injected
    this._inventory = inventory;            // injected
    this._mailer = mailer;                  // injected
  }
}
```

#### DON'T

- Reach for global state inside the constructor.
- Construct collaborator objects inside __init__ or constructor.

```python
class CheckoutService:
    def __init__(self):
        self.repo = global_invoice_repo     # WRONG: hidden global dependency
        self.inventory = Inventory()        # WRONG: hidden construction, untestable
```

```javascript
export class CheckoutService {
  constructor() {
    this.repo = globalInvoiceRepo;          // WRONG: hidden global dependency
    this.inventory = new Inventory();       // WRONG: hidden construction, untestable
  }
}
```
