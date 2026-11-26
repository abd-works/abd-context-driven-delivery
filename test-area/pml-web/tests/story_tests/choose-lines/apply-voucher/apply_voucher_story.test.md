---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

Shared with every story of Choose Lines: [domain terms and examples](../examples/choose_lines.examples.md).

# Story: Apply Voucher

#### Scenario Outline: Apply a voucher to one line

*Given* the **Customer** has a ++[cart](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++ with ++one Atlas line++  
  *But* the ++[cart](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++ has no ++[applied voucher](../../../../src/.context/domain-model.md#appliedvoucher-aggregate-root-entity)++  

```realization
PlanRepository._seed(Atlas, Ace, Data Freedom, Essentials, Promo)
CatalogVoucherRepository._seedTerms(code, terms) for each code in voucher.json: TRAVEL25, ALL10, CART10, PROMO30, PARTNER20, EXPIRED, USED
cart = new Cart(null, cart_one_atlas_line)
plan = PlanRepository.loadByName(Atlas)
cart.addLine(plan)
```

*When* the **Customer** applies {voucher}  

```realization
voucher = AppliedVoucherRepository.forCode({voucher}, planId => PlanRepository.load(planId))
  -> CatalogVoucherRepository.termsFor({voucher})
cart.applyVoucher(voucher)
  -> voucher.redeem(plans)
AppliedVoucherRepository.update(voucher)
```

*Then* the stored ++[cart](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++ holds {voucher} as its ++[applied voucher](../../../../src/.context/domain-model.md#appliedvoucher-aggregate-root-entity)++  
  *And* the voucher shows its code and rule, and can be removed  
  *And* the cart shows the code with {on one Atlas line}  
  *And* no other code can be entered while {voucher} is applied  

#### Examples

| example | [voucher](../../../../src/.context/domain-model.md#appliedvoucher-aggregate-root-entity) | on one Atlas line |
| --- | --- | --- |
| ALL10 | ++ALL10++ | −$10 first bill |
| CART10 | ++CART10++ | −$19.30 first bill |
| TRAVEL25 | ++TRAVEL25++ | −$25 first bill |

*(intended — not shown in the prototype: CART10's −$19.30 on one Atlas line is 10% of $193; the walk recorded CART10 only on ++family of three++)*

#### Scenario Outline: A voucher stacks with the family discount

*Given* the ++[cart](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++ holds ++family of three++  

```realization
PlanRepository._seed(Atlas, Ace, Data Freedom, Essentials, Promo)
CatalogVoucherRepository._seedTerms(code, terms) for each code in voucher.json: TRAVEL25, ALL10, CART10, PROMO30, PARTNER20, EXPIRED, USED
cart = new Cart(null, cart_family_of_three)
plan = PlanRepository.loadByName(Atlas)
cart.addLine(plan)
plan = PlanRepository.loadByName(Ace)
cart.addLine(plan)
plan = PlanRepository.loadByName(Data Freedom)
cart.addLine(plan)
```

*When* the **Customer** applies {voucher}  

```realization
voucher = AppliedVoucherRepository.forCode({voucher}, planId => PlanRepository.load(planId))
  -> CatalogVoucherRepository.termsFor({voucher})
cart.applyVoucher(voucher)
  -> voucher.redeem(plans)
AppliedVoucherRepository.update(voucher)
```

*Then* the cart shows the ++[applied voucher](../../../../src/.context/domain-model.md#appliedvoucher-aggregate-root-entity)++ with {on family of three}, first bill only  
  *And* the cart still shows "Family discount · $5 × 3 lines −$15/mo"  
  *And* the cart shows {you pay now}  

#### Examples

| example | [voucher](../../../../src/.context/domain-model.md#appliedvoucher-aggregate-root-entity) | on family of three | you pay now |
| --- | --- | --- | --- |
| ALL10 | ++ALL10++ | −$30 first bill | You pay now $404, then $434/mo |
| CART10 | ++CART10++ | −$43.40 first bill | You pay now $390.60, then $434/mo |
| TRAVEL25 | ++TRAVEL25++ | −$50 first bill | You pay now $384, then $434/mo |

> observed: TRAVEL25 takes −$50 on ++family of three++ because only Line 1 · Atlas and Line 2 · Ace qualify; Line 3 · Data Freedom gets nothing. This carries over the legacy *Skip redeem when the cart plan is not in the voucher plan list*. A cart with no Atlas or Ace line was not walked, so what TRAVEL25 shows there is unknown.

*(intended — not shown in the prototype: CART10's "You pay now $390.60" is $434 less 10%; the walk recorded the −$43.40 but not the total)*

#### Scenario: An unknown code is refused

*Given* the **Customer** has a ++[cart](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++ with ++one Atlas line++  
  *But* the ++[cart](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++ has no ++[applied voucher](../../../../src/.context/domain-model.md#appliedvoucher-aggregate-root-entity)++  

```realization
PlanRepository._seed(Atlas, Ace, Data Freedom, Essentials, Promo)
CatalogVoucherRepository._seedTerms(code, terms) for each code in voucher.json: TRAVEL25, ALL10, CART10, PROMO30, PARTNER20, EXPIRED, USED
cart = new Cart(null, cart_one_atlas_line)
plan = PlanRepository.loadByName(Atlas)
cart.addLine(plan)
```

*When* the **Customer** applies the ++unknown code++  

```realization
voucher = AppliedVoucherRepository.forCode(HELLO5, planId => PlanRepository.load(planId))
  -> CatalogVoucherRepository.termsFor(HELLO5)
  <- VoucherException(enter, HELLO5, invalid code)
```

*Then* the ++invalid code++ message is shown  
  *And* the stored ++[cart](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++ has no ++[applied voucher](../../../../src/.context/domain-model.md#appliedvoucher-aggregate-root-entity)++  
  *And* a code can still be entered  

#### Scenario: Remove an applied voucher

*Given* the ++[cart](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++ holds the ++[applied voucher](../../../../src/.context/domain-model.md#appliedvoucher-aggregate-root-entity)++ ++TRAVEL25++  

```realization
PlanRepository._seed(Atlas, Ace, Data Freedom, Essentials, Promo)
CatalogVoucherRepository._seedTerms(code, terms) for each code in voucher.json: TRAVEL25, ALL10, CART10, PROMO30, PARTNER20, EXPIRED, USED
cart = new Cart(null, cart_atlas_with_travel25)
plan = PlanRepository.loadByName(Atlas)
cart.addLine(plan)
voucher = AppliedVoucherRepository.forCode(TRAVEL25, planId => PlanRepository.load(planId))
  -> CatalogVoucherRepository.termsFor(TRAVEL25)
cart.applyVoucher(voucher)
  -> voucher.redeem(plans)
AppliedVoucherRepository.update(voucher)
```

*When* the **Customer** removes the voucher  

```realization
cart.removeVoucher()
```

*Then* the stored ++[cart](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++ has no ++[applied voucher](../../../../src/.context/domain-model.md#appliedvoucher-aggregate-root-entity)++  
  *And* a code can be entered again, the field still holding TRAVEL25  
  *And* the cart shows no voucher amount  
