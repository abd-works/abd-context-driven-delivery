---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

Shared with every story of Choose Lines: [domain terms and examples](../examples/choose_lines.examples.md).

# Story: Add Line To Cart

#### Scenario: Add the first line

*Given* the **Customer** has an ++empty cart++  

```realization
PlanRepository._seed(Atlas, Ace, Data Freedom, Essentials, Promo)
cart = new Cart(null, cart_empty_cart)
```

*When* the **Customer** adds a ++[line](../../../../src/.context/domain-model.md#line-entity)++ on ++[plan](../../../../src/.context/domain-model.md#plan-aggregate-root-entity)++ ++Atlas++  

```realization
plan = PlanRepository.loadByName(Atlas)
line = cart.addLine(plan)
```

*Then* the stored ++[cart](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++ holds Line 1 · Atlas at $193/mo  
  *And* the **Customer** is told the ++line added++ message  
  *And* every ++[plan](../../../../src/.context/domain-model.md#plan-aggregate-root-entity)++ can now be added as one more line  
  *And* the cart shows $193/mo, 1 line, and the ++one line++ nudge  

#### Scenario: Add one more line

*Given* the **Customer** has a ++[cart](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++ with ++one Atlas line++  

```realization
PlanRepository._seed(Atlas, Ace, Data Freedom, Essentials, Promo)
cart = new Cart(null, cart_one_atlas_line)
plan = PlanRepository.loadByName(Atlas)
cart.addLine(plan)
```

*When* the **Customer** adds one more ++[line](../../../../src/.context/domain-model.md#line-entity)++ on ++[plan](../../../../src/.context/domain-model.md#plan-aggregate-root-entity)++ ++Ace++  

```realization
plan = PlanRepository.loadByName(Ace)
cart.addLine(plan)
```

*Then* the stored ++[cart](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++ holds Line 1 · Atlas at $193/mo and Line 2 · Ace at $153/mo  
  *And* the cart shows $346/mo, 2 lines, and the ++two lines++ nudge  

#### Scenario: Add a line from the order checklist

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

*When* the **Customer** adds a ++[line](../../../../src/.context/domain-model.md#line-entity)++ on ++[plan](../../../../src/.context/domain-model.md#plan-aggregate-root-entity)++ ++Ace++ to the ++[cart](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++  

```realization
plan = PlanRepository.loadByName(Ace)
cart.addLine(plan)
CartRepository.update(cart)
```

*Then* the stored ++[cart](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++ holds Line 1 · Me · Data Freedom and Line 2 · Ace  
  *And* Line 2 · Ace joins the order checklist as to do  

> observed (*Goal 4*): **Add a line** on the checklist's cart opens the catalog with **Back to your order**; the new line joins the checklist as "Line 2 · Ace (to do now)".
