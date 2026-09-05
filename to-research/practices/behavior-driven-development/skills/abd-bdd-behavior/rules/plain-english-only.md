---
rule: plain-english-only
scanner: plain_english_only_scanner.py
severity: error
---
# Plain English Only

The behavior scaffold must contain no code syntax. Characters like `()`, `=>`, `{}`, `[]`, `;` and patterns like `async/await` or type annotations signal implementation leaking into the discovery phase.

**DO:** Write behaviors in plain English.

```
Payment
  Voucher redemption
    should apply the discount to the order total
    should reject an expired voucher
```

**DO NOT:** Include code syntax in scaffold lines.

```
Payment
  applyVoucher(voucherId: string): Promise<Discount>
    should call calculateDiscount() and return result
```

- Example (wrong): `applyVoucher(voucherId: string)` — method signature, not a behavior
- Example (correct): `Voucher redemption` — concept name, plain English
