---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

## Story: View Cart Total

**Story type:** website

### Domain terms

- ++[Cart](../../../.context/domain-model.md#cart-aggregate-root-entity)++ — the Books a Customer means to buy

### Examples

#### cart

| cart | example | lines | total |
| --- | --- | --- | --- |
| cart | empty cart | none | 0 |

### Behaviors

#### Scenario: Show the total of a cart with no lines

*Given* the Customer has ++[Cart](../../../.context/domain-model.md#cart-aggregate-root-entity)++ ++empty cart++
*When* the Customer views the total of the ++[Cart](../../../.context/domain-model.md#cart-aggregate-root-entity)++
*Then* the Customer sees the total *0*
