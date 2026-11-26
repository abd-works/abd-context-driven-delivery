---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

Shared with every story of Choose Lines: [domain terms and examples](../examples/choose_lines.examples.md).

# Story: Display Plans

#### Scenario: See the plan catalog

*Given* the **Customer** has no account  
  *And* the **Customer** has an ++empty cart++  
  *And* the ++[plan](../../../../src/.context/domain-model.md#plan-aggregate-root-entity)++ repository holds ++[plan](../../../../src/.context/domain-model.md#plan-aggregate-root-entity)++ ++Atlas++, ++[plan](../../../../src/.context/domain-model.md#plan-aggregate-root-entity)++ ++Ace++, ++[plan](../../../../src/.context/domain-model.md#plan-aggregate-root-entity)++ ++Data Freedom++, ++[plan](../../../../src/.context/domain-model.md#plan-aggregate-root-entity)++ ++Essentials++, and ++[plan](../../../../src/.context/domain-model.md#plan-aggregate-root-entity)++ ++Promo++  

```realization
cart = new Cart(null, cart_empty_cart)
PlanRepository._seed(Atlas, Ace, Data Freedom, Essentials, Promo)
```

*When* the **Customer** opens My Paradise  

```realization
plans = PlanRepository.list()
```

*Then* the catalog shows ++[plan](../../../../src/.context/domain-model.md#plan-aggregate-root-entity)++ ++Atlas++, ++[plan](../../../../src/.context/domain-model.md#plan-aggregate-root-entity)++ ++Ace++, ++[plan](../../../../src/.context/domain-model.md#plan-aggregate-root-entity)++ ++Data Freedom++, and ++[plan](../../../../src/.context/domain-model.md#plan-aggregate-root-entity)++ ++Essentials++, each with its tagline, its ++[plan feature](../../../../src/.context/domain-model.md#planfeature-value-object)++s in Bermuda and when you travel, and its monthly price with ++all fees included++  
  *And* ++[plan](../../../../src/.context/domain-model.md#plan-aggregate-root-entity)++ ++Ace++ is tagged *Best value*  
  *And* each ++[plan](../../../../src/.context/domain-model.md#plan-aggregate-root-entity)++ can be added  
  *And* the cart shows the ++no lines++ nudge  
  *But* ++[plan](../../../../src/.context/domain-model.md#plan-aggregate-root-entity)++ ++Promo++ is not in the catalog  

#### Scenario: Continue with no line in the cart

*Given* the **Customer** has an ++empty cart++  

```realization
cart = new Cart(null, cart_empty_cart)
```

*When* the **Customer** continues from the plan catalog  

```realization
cart.continueFromCatalog()
  <- CartException(continueFromCatalog, Add at least one line to continue.)
```

*Then* the catalog says *Add at least one line to continue.*  
  *And* the cart still holds ++no lines++  

> observed: the prototype keeps Continue enabled on an empty cart and answers it with this message under the page's title.

> observed: the country-list links behind each plan (190+, 70+, 30+, 5+, 10+ countries) open lists the walk did not capture; the map puts them out of scope.
