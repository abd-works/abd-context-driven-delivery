---
rule: business-readable-language
scanner: business_readable_language_scanner.py
severity: warning
---
# Business-Readable Language

Every leaf behavior line must start with `should` and use the domain's ubiquitous language. Technical terms that only an engineer would recognise are a signal that the behavior is not yet expressed at the right level.

**DO:** Start leaf lines with `should` using domain language.

```
Voucher
  should apply a percentage discount to eligible items
  should reject a voucher that has already been used
  should show the saving amount on the order summary
```

**DO NOT:** Use technical method names, class names, or system internals in behavior lines.

```
Voucher
  calls DiscountCalculator.apply()
  throws VoucherExpiredException when TTL is exceeded
```

- Example (wrong): `calls DiscountCalculator.apply()` — implementation detail, no `should`
- Example (correct): `should calculate the discounted total for eligible products`
