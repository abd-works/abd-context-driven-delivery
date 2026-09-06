---

---

# Rule: Map table columns to scenario parameters (outline template)

This rule applies to stories that use *Scenario Outlines* eg: that use `{column_name}` tokens and example tables. It does not apply to plain *Scenarios*, which use inline values instead.

Every `{column_name}` in steps must resolve to a column header on the matching concept table. Every column on a table must appear in at least one step. Work both directions — no orphan columns, no unused tables.

**Document order:** Tables whose columns appear in **Given** go immediately above that Background or scenario block. Tables whose columns first appear in **When** or **Then** go immediately below that scenario.

## DO

- Match `{token}` spelling exactly to the table column header.
- Keep tables minimal — only the columns the scenario actually references.

```gherkin
Given a User {user_name} has Entitlement {entitlement_name} with status {entitlement_status}
```

```text
User:
| user_name | user_role |
| Jane Doe | Wire Operator |

Entitlement:
| entitlement_name | entitlement_status |
| WirePayment.Create | Granted |
```

## DON'T

- Leave orphan tables (columns never referenced in steps) or `{tokens}` with no matching table.
- Use `<angle_bracket>` placeholders in step prose — use `{column_name}` for outline steps.

```gherkin
# WRONG
Given User <user_name> is logged in

# CORRECT (outline)
Given a User {user_name} is logged in
```
