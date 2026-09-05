---

---

# Rule: Mention the domain concept beside the placeholder (outline template)

This rule applies to **`specification-by-example-outline.md`** — scenarios that use `{column_name}` tokens. In plain scenarios, the concept name is written in **bold** and the value in *italics* directly in the step; no token is needed.

In outline steps, put the readable domain concept name next to each `{token}` so readers can follow the step without decoding braces alone.

## DO

- Use a short English cue before or after the brace: e.g. `a User {user_name}`, `activation status {activation_status}`, `Payment Amount of {amount} {currency}`.
- Apply the same pattern in Background (Given/And) and in scenario steps.

``Background:
  Given a User {user_name} is logged into ChannelOne 2.0
  And that User {user_name} is representing an Enterprise {enterprise_name} with the Role {user_role}
  And that Enterprise {enterprise_name} has {payment_service} Payment Service enabled
  And that User has an Entitlement {entitlement_name} with an Entitlement Status of {entitlement_status}

Scenario: Wire capture
  Given an Account with account name {account_name} and activation status {activation_status} is selected
  When the User {user_name} enters a Payment Amount with amount {amount} and currency {currency}
  Then Wire Payment outcome has status {status}
``
## DON'T

- Use a bare `{token}` with no surrounding domain words — prefer `the User {user_name}`.
- Repeat the brace twice (`{user_name} User …`) — one natural phrase is enough.
