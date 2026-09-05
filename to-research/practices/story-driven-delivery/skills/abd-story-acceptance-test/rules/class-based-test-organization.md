---
scanner: class_based_organization_scanner.py
---

# Rule: Class-Based Test Organization

Organize test files around **behavior clusters** from the source context — stories, flows, or feature areas. The test **file** is named after the grouping that contains the behaviors (flow, sub-epic, feature area), the test **class** is named after the specific behavior, and the test **method** is named after the specific scenario or condition. Getting this wrong requires deleting and recreating files. Before writing any test code, state the file name, class name, and method name explicitly from the source material.

## DO

- **Before writing code**, state the structure explicitly:
  - Source: `[Flow / Area] → [Behavior] → [Scenario]`
  - File: `test_<area_snake_case>.py`
  - Class: `Test<ExactBehaviorName>` (PascalCase of full behavior name from source)
  - Method: `test_<scenario_outcome_snake_case>`
- Name the file after the **grouping** that contains the behaviors — not the behavior itself.
- Name the class using the **exact behavior name** from the source — no abbreviation, no summarisation.
- Add to an existing area file rather than creating a new one when the file already exists.

```python
# Area: 'Manage Orders'  →  File: test_manage_orders.py
# Behavior: 'Place Order'  →  Class: TestPlaceOrder
# Scenario: 'Order confirmed for available items'
#   →  Method: test_order_confirmed_for_available_items

class TestPlaceOrder:
    def test_order_confirmed_for_available_items(self, workspace_root):
        ...

    def test_empty_cart_is_rejected(self, workspace_root):
        ...
```

## DON'T

- Name the file after the individual behavior — use the parent grouping.
- Abbreviate or genericise the class name.

```python
# WRONG: file named after the individual behavior
# File: test_place_order.py

# WRONG: abbreviated or generic class names
class TestOrder:          # abbreviated — exact behavior is 'Place Order'
class TestOrderHandling:  # invented topic, not in source

# CORRECT: exact name from source context
class TestPlaceOrder:
    ...
```
