---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

Shared with every story of Choose Lines: [domain terms and examples](../examples/choose_lines.examples.md).

# Story: Remove Line From Cart

#### Scenario: Remove a line from the cart

*Given* the ++[cart](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++ holds ++Atlas and Ace lines++  

```realization
PlanRepository._seed(Atlas, Ace, Data Freedom, Essentials, Promo)
cart = new Cart(null, cart_atlas_and_ace_lines)
plan = PlanRepository.loadByName(Atlas)
cart.addLine(plan)
plan = PlanRepository.loadByName(Ace)
cart.addLine(plan)
```

*When* the **Customer** removes Line 2 · Ace  

```realization
line = cart.lines.find(position 2)
cart.removeLine(line)
```

*Then* the stored ++[cart](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++ holds Line 1 · Atlas at $193/mo only  
  *And* the cart shows $193/mo, 1 line, and the ++one line++ nudge  

#### Scenario: Remove a set-up line from the order

*Given* the ++[cart](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++ holds ++lines set up for Me and Sam++  

```realization
PlanRepository._seed(Atlas, Ace, Data Freedom, Essentials, Promo)
credentials = CredentialsRepository.new()
customerProfile = new CustomerProfile(credentials, customer_cart_lines_set_up_for_me_and_sam)
CustomerProfileRepository.update(customerProfile)
NumberInventoryRepository.update(new NumberInventory(4415550106, "", available))
NumberInventoryRepository.update(new NumberInventory(4415550107, "", available))
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
plan = PlanRepository.loadByName(Ace)
line = cart.addLine(plan)
line.nameLine(Sam, false)
number = NumberInventoryRepository.load(4415550107)
number.hold()
NumberInventoryRepository.update(number)
line.recordHeldNumbers([number])
number.reserve()
NumberInventoryRepository.update(number)
line.reserveSelectedNumber(number)
line.selectSim(new Sim(eSIM))
CartRepository.update(cart)
```

*When* the **Customer** removes Sam's ++[line](../../../../src/.context/domain-model.md#line-entity)++ and confirms the ++remove line question++  

```realization
line = cart.lines.find(nickname Sam)
number = line.number
cart.removeLine(line)
  -> number.makeAvailable()
NumberInventoryRepository.update(number)
CartRepository.update(cart)
```

*Then* the stored ++[cart](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++ holds Line 1 · Me · Data Freedom only  
  *And* the progress bar's Lines step reads Your line  

> observed (*Goal 4*): **Remove line** on a line's Edit asks the ++remove line question++ with **Keep it** / **Remove line**.

#### Scenario: Removing a line releases its number

*Given* the ++[cart](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++ holds ++lines set up for Me and Sam++  

```realization
PlanRepository._seed(Atlas, Ace, Data Freedom, Essentials, Promo)
credentials = CredentialsRepository.new()
customerProfile = new CustomerProfile(credentials, customer_cart_lines_set_up_for_me_and_sam)
CustomerProfileRepository.update(customerProfile)
NumberInventoryRepository.update(new NumberInventory(4415550106, "", available))
NumberInventoryRepository.update(new NumberInventory(4415550107, "", available))
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
plan = PlanRepository.loadByName(Ace)
line = cart.addLine(plan)
line.nameLine(Sam, false)
number = NumberInventoryRepository.load(4415550107)
number.hold()
NumberInventoryRepository.update(number)
line.recordHeldNumbers([number])
number.reserve()
NumberInventoryRepository.update(number)
line.reserveSelectedNumber(number)
line.selectSim(new Sim(eSIM))
CartRepository.update(cart)
```

*When* the **Customer** removes Sam's ++[line](../../../../src/.context/domain-model.md#line-entity)++ and confirms the ++remove line question++  

```realization
line = cart.lines.find(nickname Sam)
number = line.number
cart.removeLine(line)
  -> number.makeAvailable()
NumberInventoryRepository.update(number)
CartRepository.update(cart)
```

*Then* the ++[number](../../../../src/.context/domain-model.md#numberinventory-aggregate-root-entity)++ Sam's line held is released and can be offered again  

*(intended — not shown in the prototype: releasing the number comes from the bounded-context map, Order → Numbers: "removing the line releases it")*

#### Scenario: Keep the line

*Given* the ++[cart](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++ holds ++lines set up for Me and Sam++  

```realization
PlanRepository._seed(Atlas, Ace, Data Freedom, Essentials, Promo)
credentials = CredentialsRepository.new()
customerProfile = new CustomerProfile(credentials, customer_cart_lines_set_up_for_me_and_sam)
CustomerProfileRepository.update(customerProfile)
NumberInventoryRepository.update(new NumberInventory(4415550106, "", available))
NumberInventoryRepository.update(new NumberInventory(4415550107, "", available))
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
plan = PlanRepository.loadByName(Ace)
line = cart.addLine(plan)
line.nameLine(Sam, false)
number = NumberInventoryRepository.load(4415550107)
number.hold()
NumberInventoryRepository.update(number)
line.recordHeldNumbers([number])
number.reserve()
NumberInventoryRepository.update(number)
line.reserveSelectedNumber(number)
line.selectSim(new Sim(eSIM))
CartRepository.update(cart)
```

*When* the **Customer** starts to remove Sam's ++[line](../../../../src/.context/domain-model.md#line-entity)++  
  *But* does not confirm the ++remove line question++  

```realization
line = cart.lines.find(nickname Sam)
line.removeQuestion
Cart.messages.removeLineWarning
```

*Then* the **Customer** is asked the ++remove line question++  
  *And* the stored ++[cart](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++ still holds Line 1 · Me and Line 2 · Sam with everything set up for them  
