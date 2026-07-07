---
fidelity: [exploration, specification]
artifact: [story-scenarios]
scanner: actor-alternation
kind: quality

---

# Rule: Alternate Actor Emphasis

Interleave **user-visible** and **system-visible** outcomes within an
interaction. Long runs of the same actor (three or more consecutive steps
where only the user acts, or only the system reacts, without a switch)
usually indicate a missing beat or a story that should split.

## DO

- Alternate between what the user does and what the system does back
- After a user action, name the system's observable reaction before the next
  user action
- After a system reaction, name the user's next action or the state the user
  can now see

## DON'T

- Chain multiple user actions in a row without naming the system response in
  between
- Chain multiple internal system outcomes without naming what the user can
  observe
- Hide a missing story behind a long unilateral run

## At each fidelity

**Exploration — AC:**
```
# Wrong — three user actions with no system reaction
When the Customer selects a Product
And the Customer adds it to the Cart
And the Customer proceeds to Checkout
Then the Order is created

# Correct — actors alternate
When the Customer adds the Product to the Cart
Then the Cart shows the Product with its price
When the Customer proceeds to Checkout
Then the Order Summary is displayed
```

**Specification — scenarios:** same shape; each `When` is followed by a
`Then` before the next `When`.
