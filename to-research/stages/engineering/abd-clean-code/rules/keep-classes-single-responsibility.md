---
scanner: single_responsibility_scanner.py
---

### Rule: Keep Classes Single Responsibility

Each class has one reason to change. Split classes that calculate, persist, and notify into dedicated collaborators.

#### DO

- One class per domain responsibility.
- Separate repository, calculator, and notifier roles.

```python
class InvoiceRepository:                    # focused on persistence
    def save(self, invoice): ...
    def find_by_id(self, invoice_id): ...

class InvoiceCalculator:                    # focused on calculation
    def calculate_total(self, items): ...
    def apply_discount(self, total, discount): ...
```

```javascript
export class InvoiceRepository {            // focused on persistence
  async save(invoice) { }
  async findById(invoiceId) { }
}

export class InvoiceCalculator {            // focused on calculation
  calculateTotal(items) { }
  applyDiscount(total, discount) { }
}
```

#### DON'T

- Build classes that calculate, persist, notify, and format.

```python
class Invoice:                              # WRONG: multiple responsibilities
    def calculate_total(self): ...          # calculation
    def save_to_db(self): ...               # persistence
    def send_email(self): ...               # notification
    def format_pdf(self): ...              # formatting
```

```javascript
export class Invoice {                      // WRONG: multiple responsibilities
  calculateTotal() { }                      // calculation
  saveToDB() { }                            // persistence
  sendEmail() { }                           // notification
  formatPDF() { }                           // formatting
}
```
