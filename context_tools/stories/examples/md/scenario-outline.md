---
fidelity: [specification]
artifact: [story-scenarios]
format: md
example-of: scenario-outline
---

<!-- Worked example — Scenario Outline with normalized Examples tables. -->
<!-- Shows the shape templates/md/scenario-outline.md produces once filled in. -->

## Story: Submit Payment and Validate Against Account Limit

**Story type:** user

### Domain terms

- *Account* — enterprise sub-account with an activation status
- *Transactional Limit* — maximum amount rule attached to an **Account**
- *Wire Payment* — payment request submitted by the user
- *Payment Amount* — value entered for the **Wire Payment**
- *Validation Status* — outcome after limit check (*successful* or *rejected*)

### Examples

#### Account:

| scenario      | enterprise_name | account_name       | activation_status |
|---------------|-----------------|--------------------|-------------------|
| Scenario 1    | Acme Corp       | Acme Operating     | Active            |
| Scenario 2    | Acme Corp       | Acme Payroll       | Active            |

#### Transactional Limit:

| scenario      | account_name       | limit_name  | max_amount   | currency |
|---------------|--------------------|-------------|--------------|----------|
| Scenario 1    | Acme Operating     | daily_wire  | 500000.00    | USD      |
| Scenario 2    | Acme Payroll       | weekly_wire | 2000000.00   | USD      |

#### Wire Payment:

| scenario      | amount      | currency | formatted_display | validation_status |
|---------------|-------------|----------|-------------------|-------------------|
| Scenario 1    | 10000.00    | USD      | $10,000.00        | successful        |
| Scenario 2    | 500000.01   | USD      | $500,000.01       | rejected          |

### Background

*Given* a **User** {user_name} is logged into ChannelOne 2.0  
  *And* that **User** {user_name} is representing **Enterprise** {enterprise_name}  

### Behaviors

#### Scenario Outline 1: Submit Payment and Validate Against Account Limit

#### Steps

*Given* an **Account** {account_name} with **Activation Status** {activation_status}  
  *And* the **Transactional Limit** for that **Account** is {max_amount} {currency}  
*When* the **User** enters a **Payment Amount** of {amount} {currency}  
*Then* the **Wire Payment** is marked as {validation_status}  
  *And* a **Report** is sent with formatted display {formatted_display}  

### Evidence

| Scenario | Source (document / system) | Location |
| --- | --- | --- |
| Scenario 1 | *Order Management Workshop* | Whiteboard "submit flow", 2026-03-15 |
| Scenario 2 | *API Spec* v2 | p. 8, §"Limit exceeded" |
