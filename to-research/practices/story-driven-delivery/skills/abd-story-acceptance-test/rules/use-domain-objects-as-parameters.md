---
---

# Rule: Use Domain Objects as Parameters

Pass **constructed domain objects** to test and helper functions — never raw IDs or bare primitives. Parameters must be named after their business role so each Given/When/Then step reads as a natural scenario in the domain language.

## DO

- Pass real domain objects (`Cart`, `Order`, `User`) — not IDs or plain data.
- Name parameters after their business role (`cart`, `product`) — not their technical representation (`cart_id`, `product_id`).

```python
def test_adds_product_to_cart(self, workspace_root):
    # Given
    cart = given_cart_exists(workspace_root)
    product = given_product_is_available(workspace_root, 'item-a')
    # When
    when_product_is_added(cart, product)
    # Then
    then_cart_contains(cart, product)
```

## DON'T

- Pass IDs or primitives where domain objects belong — steps become unreadable as business scenarios.

```python
def test_adds_product_to_cart(self, cart_id, product_id):
    given_cart_exists(cart_id)            # ID — not a business entity
    when_product_is_added(cart_id, product_id)
    then_cart_contains(cart_id, product_id)
```
