---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

Shared with every story of Choose Lines: [domain terms and examples](../examples/choose_lines.examples.md).

# Story: Unlock Promo Plan

#### Scenario: PROMO30 unlocks the Promo plan

*Given* the ++[plan catalog](../../../../src/.context/domain-model.md#plan-aggregate-root-entity)++ hides ++[plan](../../../../src/.context/domain-model.md#plan-aggregate-root-entity)++ ++Promo++  
  *And* the **Customer** has an ++empty cart++  

```realization
PlanRepository._seed(Atlas, Ace, Data Freedom, Essentials, Promo)
CatalogVoucherRepository._seedTerms(code, terms) for each code in voucher.json: TRAVEL25, ALL10, CART10, PROMO30, PARTNER20, EXPIRED, USED
cart = new Cart(null, cart_empty_cart)
```

*When* the **Customer** applies ++[voucher](../../../../src/.context/domain-model.md#appliedvoucher-aggregate-root-entity)++ ++PROMO30++  

```realization
voucher = AppliedVoucherRepository.forCode(PROMO30, planId => PlanRepository.load(planId))
  -> CatalogVoucherRepository.termsFor(PROMO30)
cart.applyVoucher(voucher)
  -> cart.addLine(plan) for the unsellable Promo plan in voucher.plans
  -> voucher.redeem(plans)
AppliedVoucherRepository.update(voucher)
```

*Then* the **Customer** is shown ++promo plan ready++ with ++[plan](../../../../src/.context/domain-model.md#plan-aggregate-root-entity)++ ++Promo++ tagged *Unlocked*, free for 30 days, with its ++[plan feature](../../../../src/.context/domain-model.md#planfeature-value-object)++s and $0/mo  
  *And* the stored ++[cart](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++ holds Line 1 · Promo at $0/mo  
  *And* the cart shows $0/mo, 1 line, and "PROMO30 free for 30 days"  

> observed (*Goal 3*): PROMO30 was applied from the catalog with no line in the cart. Applying it to a cart that already has lines, or applying another voucher on top of it, was not walked.
