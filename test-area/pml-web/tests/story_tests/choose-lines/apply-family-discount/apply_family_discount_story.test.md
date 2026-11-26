---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

Shared with every story of Choose Lines: [domain terms and examples](../examples/choose_lines.examples.md).

# Story: Apply Family Discount

#### Scenario: A third line earns the family discount

*Given* the ++[cart](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++ holds ++family of three++  

```realization
PlanRepository._seed(Atlas, Ace, Data Freedom, Essentials, Promo)
cart = new Cart(null, cart_family_of_three)
plan = PlanRepository.loadByName(Atlas)
cart.addLine(plan)
plan = PlanRepository.loadByName(Ace)
cart.addLine(plan)
plan = PlanRepository.loadByName(Data Freedom)
cart.addLine(plan)
```

*When* **My Paradise** prices the ++[cart](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++  

```realization
summary = cart.orderSummary()
```

*Then* each ++[line](../../../../src/.context/domain-model.md#line-entity)++'s price is struck through and shows $5 less, as in ++three lines++  
  *And* the cart shows "Family discount · $5 × 3 lines −$15/mo" and the ++family discount saving++  
  *And* the cart shows $449 struck through and $434/mo  
  *And* the cart shows the ++three lines++ nudge  

#### Scenario Outline: Fewer than three lines get a nudge, not a discount

*Given* the ++[cart](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++ holds {lines}  

```realization
PlanRepository._seed(Atlas, Ace, Data Freedom, Essentials, Promo)
cart = new Cart(null, cart_empty_cart | cart_one_atlas_line | cart_atlas_and_ace_lines)
for each plan name of {lines}: Atlas, then Ace
  plan = PlanRepository.loadByName(name)
  cart.addLine(plan)
```

*When* **My Paradise** prices the ++[cart](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++  

```realization
summary = cart.orderSummary()
```

*Then* no ++[family discount](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++ is taken  
  *And* the cart shows the {lines} nudge  

#### Examples

| example | lines |
| --- | --- |
| no lines | ++no lines++ |
| one line | ++one line++ |
| two lines | ++two lines++ |

> The discount was observed with three lines only; the walk did not add a fourth line or remove one from three, so the $5 × 4 price and the drop back below three are not shown.
