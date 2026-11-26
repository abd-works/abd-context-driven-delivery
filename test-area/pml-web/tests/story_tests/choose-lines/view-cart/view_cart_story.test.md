---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

Shared with every story of Choose Lines: [domain terms and examples](../examples/choose_lines.examples.md).

# Story: View Cart

#### Scenario: View the cart with a voucher

*Given* the ++[cart](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++ holds one Atlas line with TRAVEL25 (++Atlas with TRAVEL25++)  

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

*When* the **Customer** views the cart  

```realization
summary = cart.orderSummary()
```

*Then* the cart shows Line 1 · Atlas at $193/mo, which can be removed  
  *And* the cart shows "Voucher TRAVEL25, first bill only, −$25"  
  *And* the cart shows "You pay now $168, then $193/mo"  

#### Scenario: View the cart with several lines

*Given* the ++[cart](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++ holds ++Atlas and Ace lines++  

```realization
PlanRepository._seed(Atlas, Ace, Data Freedom, Essentials, Promo)
cart = new Cart(null, cart_atlas_and_ace_lines)
plan = PlanRepository.loadByName(Atlas)
cart.addLine(plan)
plan = PlanRepository.loadByName(Ace)
cart.addLine(plan)
```

*When* the **Customer** views the cart  

```realization
summary = cart.orderSummary()
```

*Then* the cart shows Line 1 · Atlas at $193/mo and Line 2 · Ace at $153/mo, each of which can be removed  
  *And* the cart shows $346/mo, 2 lines, and the ++two lines++ nudge  
  *And* a voucher can be added  

#### Scenario: View the cart from the order checklist

*Given* the ++[cart](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++ holds ++one line set up for Me++  

```realization
PlanRepository._seed(Atlas, Ace, Data Freedom, Essentials, Promo)
credentials = CredentialsRepository.new()
customerProfile = new CustomerProfile(credentials, customer_cart_one_line_set_up_for_me)
CustomerProfileRepository.update(customerProfile)
NumberInventoryRepository.update(new NumberInventory(4415550106, "", available))
cart = CartRepository.create(customerProfile)
plan = PlanRepository.loadByName(Data Freedom)
line = cart.addLine(plan)
line.nameLine(Me, false)
number = NumberInventoryRepository.load(4415550106)
number.hold()
NumberInventoryRepository.update(number)
line.recordHeldNumbers([number])
number.reserve()
NumberInventoryRepository.update(number)
line.reserveSelectedNumber(number)
line.selectSim(new Sim(eSIM))
CartRepository.update(cart)
```

*When* the **Customer** views the cart from the order checklist  

```realization
cart = CartRepository.load(customerProfile)
summary = cart.orderSummary()
```

*Then* the cart shows "Line 1 · Me — Data Freedom $103/mo", which can be removed  
  *And* a line can be added and a voucher can be added  
  *And* the cart shows the ++one line++ nudge  

> observed (*Goal 4*): "Your cart — Line 1 · Me — Data Freedom $103/mo", **Remove Line 1**, **Add a line**, **Add a voucher**, family-discount nudge.
