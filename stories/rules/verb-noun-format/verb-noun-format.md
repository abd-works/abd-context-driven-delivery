---
fidelity: [shaping, discovery, exploration, specification, engineering]
artifact: [story-map, ac, scenario, test]
scanner: verb-noun-format
kind: quality

---

# Rule: Verb–Noun Format

Use verb-noun format at every level. Actor is separate metadata — never in the name. Use base verb forms (imperative/infinitive: `Place Order`, not `Placing Order` or `Places Order`).

## DO

- Verb + noun [optional qualifiers]
- Base verb form: `Select Items`, `Process Payment`, `Validate Submission`
- Specific objects: `Load Order Data`, not `Load Data`

## DON'T

- Actor in name: not `Customer Places Order` → `Place Order` (actor: Customer)
- Noun-only: not `Payment Processing` → `Process Payment`
- Gerund-led: not `Submitting Order` → `Submit Order`
- Generic capability: not `Order Management` → `Manage Customer Orders`

## At each fidelity

**Shaping / Discovery — epic and story names:**
| Wrong | Correct |
|---|---|
| `Customer Places Order` | `Place Order` (actor: Customer) |
| `Payment Processing` | `Process Payment` |
| `Order Management` | `Manage Customer Orders` |

**Exploration — AC phrasing and scenario names:**
| Wrong | Correct |
|---|---|
| `When the submitting of the order happens` | `When the Customer submits the Order` |
| `Acceptance criteria: ordering` | `Acceptance criteria: Submit Order` |

**Specification — scenario name and table column names:**
| Wrong | Correct |
|---|---|
| `Scenario: ordering flow works` | `Scenario: Submit Order with valid Payment` |
| column: `orderingAmount` | column: `payment_amount` |

**Engineering — test method names:**
| Wrong | Correct |
|---|---|
| `test_ordering_works` | `test_customer_submits_order_when_cart_is_valid` |
| `test_payment` | `test_validate_payment_rejects_over_limit` |
