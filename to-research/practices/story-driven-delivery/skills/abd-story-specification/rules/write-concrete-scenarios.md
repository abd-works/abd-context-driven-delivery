# Rule: Write concrete scenarios with real values

Steps should read as **specific examples**, not abstractions. The approach depends on which template you are using.

**Scenarios (`specification-by-example.md`):** Write all values inline in the step text — real names, amounts, statuses. Use **bold** for domain concept names and *italic* for their values. No tables, no `{placeholder}` tokens.

Given **Account** *Acme Operating* owned by **Enterprise** *Acme Corp* with **Activation Status** *Active* is selected
  And the **Transactional Limit** *daily_wire* is *$500,000.00 USD*
When the **User** *Jane Doe* enters a **Payment Amount** of *$10,000.00 USD*
Then the **Wire Payment** is marked as *successful*


**Outline Scenarios (`specification-by-example-outline.md`):** Use `{column_name}` tokens that match example table headers, with readable domain words beside each placeholder. Every `{token}` must appear in an example table column; every table column must appear in a step. Tables for **Given** go above the scenario; tables for **When** / **Then** go below.


Given an **Account** with account name {account_name} and **Activation Status** {activation_status} is selected
  And the **Transactional Limit** for that Account is {max_amount} {currency}
When the **User** {user_name} enters a **Payment Amount** of {amount} {currency}
Then the **Wire Payment** is marked as {validation_status}
And a **Report** is sent showing {formatted_display}


Account (Given — above scenario):
| enterprise_name | account_name   | activation_status |
| Acme Corp       | Acme Operating | Active            |

TransactionalLimit (Given — above scenario):
| limit_name | max_amount | currency |
| daily_wire | 500000.00  | USD      |

WirePayment (Then — below scenario):
| amount    | currency | formatted_display | validation_status |
| 10000.00  | USD      | $10,000.00        | successful        |
| 500000.01 | USD      | $500,000.01       | rejected          |

## DO

- For plain scenarios: use real values directly in steps — domain concept **bold**, values *italic*.
- For outlines: name `{tokens}` after the domain field and keep the readable concept name beside the brace.
- Trace dependencies: payment needs account, account needs enterprise, user needs entitlements.
- Use collaboration language ("validates against", "owned by", "marked as"), not jammed placeholders.

## DON'T

- Mix approaches: don't use `{column_name}` tokens in a plain scenario or hard-code values in every row of an outline.
- Use generic placeholders (`<the_user>`, `{some_value}`) instead of real names (plain) or domain field names (outline).
- Describe **UI state** as **Given** when domain state suffices ("on Payment Details step" vs **Payment Details** awaits *Account* selection).
