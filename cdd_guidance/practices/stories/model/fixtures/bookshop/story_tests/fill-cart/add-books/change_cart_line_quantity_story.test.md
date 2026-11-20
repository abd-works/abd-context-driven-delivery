---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

## Story: Change Cart Line Quantity

**Story type:** website

A Customer may want more than one copy of a Book.

### Domain terms

- ++[Cart](../../../.context/domain-model.md#cart-aggregate-root-entity)++ — the Books a Customer means to buy
- ++[Cart Line](../../../.context/domain-model.md#cartline-entity)++ — one Book in the Cart with its quantity

### Examples

#### cart

| cart | example | lines | total |
| --- | --- | --- | --- |
| cart | cart with Tiny Tales | 1 x Tiny Tales | 5 |

### Behaviors

#### Scenario Outline: Cart total follows the quantity

*Given* the Customer has ++[Cart](../../../.context/domain-model.md#cart-aggregate-root-entity)++ ++cart with Tiny Tales++  
*When* the Customer changes the ++[Cart Line](../../../.context/domain-model.md#cartline-entity)++ of Tiny Tales to <quantity> copies  
*Then* the Cart total is <total>

#### Examples

| scenario | quantity | total |
| --- | --- | --- |
| one copy | 1 | 5 |
| two copies | 2 | 10 |
| three copies | 3 | 15 |

#### Scenario: Remove the line at quantity zero

*Given* the Customer has ++[Cart](../../../.context/domain-model.md#cart-aggregate-root-entity)++ ++cart with Tiny Tales++  
*When* the Customer changes the ++[Cart Line](../../../.context/domain-model.md#cartline-entity)++ of Tiny Tales to 0 copies  
*Then* the ++[Cart](../../../.context/domain-model.md#cart-aggregate-root-entity)++ holds no ++[Cart Line](../../../.context/domain-model.md#cartline-entity)++  
  *And* the Cart total is *0*
