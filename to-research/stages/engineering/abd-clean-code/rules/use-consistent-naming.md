---
scanner: consistent_naming_scanner.py
---

### Rule: Use Consistent Naming

One word per concept across the codebase. Pick a verb and use it everywhere for the same operation.

#### DO

- All retrieval functions share the same prefix across the codebase.

```python
def get_user(user_id): ...
def get_order(order_id): ...
def get_product(sku): ...
```

```javascript
function getUser(userId) { }
function getOrder(orderId) { }
function getProduct(sku) { }
```

#### DON'T

- Mix `get_`, `fetch_`, and `retrieve_` for the same concept in the same codebase.

```python
def get_user(user_id): ...      # WRONG: inconsistent verb usage
def fetch_order(order_id): ...
def retrieve_product(sku): ...
```

```javascript
function getUser(userId) { }        // WRONG: mixed terms for retrieval
function fetchOrder(orderId) { }
function retrieveProduct(sku) { }
```
