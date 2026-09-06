# Rule: Ground scenarios in domain model content when available

When domain specification, domain model, or domain language content exists in the workspace or has been provided as context, scenario language must use the exact concept names and relationships that content defines.

Look in this order — use the first type you find:
1. **Domain specification** — typed classes with attributes and typed relationships between classes (most precise source)
2. **Domain model** — each concept with its responsibilities and the other concepts it works with
3. **Domain language or key abstractions** — glossaries, defined terms, or grouped concept names with definitions

These types of content are the outputs of domain-driven design practices. If such content is present in the workspace or supplied as context, it is the authoritative source for concept names and relationships.

## DO

- Read any available domain model content before naming any concept in a step — domain specification first, then domain model, then domain language.
- Use the exact term the model defines.

```gherkin
Given a **Payment Product Agreement** {agreement_id} agreed to by **Customer** {customer_id}
    using **Account** {account_id}
    naming **Owner** {owner_id}
      with **Contact Details** {owner_email}
```

## DON'T

- Use a synonym or informal shorthand for a concept the domain model has formally named.
- Rename or paraphrase concept names even when the formal name feels long or unfamiliar.

```gherkin
Given a **Contract** {agreement_id} for **Customer** {customer_id}
    using **Bank Account** {account_id}
    naming **Holder** {owner_id}
      with **Info** {owner_email}
```

---

## DO

- In Scenario Outlines, structure example tables using the same language and cardinality as the domain model — a one-to-many relationship in the model means a separate table with a linking key, not repeated columns; a joining concept in the model means its own table with references to what it joins.

domain model the scenario is grounded in:

```markdown
#### **User**
user id                             | (identifier)
user name                           | (string)
payment role                        | Payment Role
contact details                     | Contact Details
direct deposit account              | DDA Account

#### **Payment Role**
role type                           | (Customer, Owner)

#### **DDA Account**
account id                          | (identifier)
user                                | User

#### **Payment Product**
product id                          | (identifier)
product name                        | (string)
payment channel                     | Payment Channel

#### **Contact Details**
user                                | User
email                               | (string)

#### **Payment Product Agreement**
agreement id                        | (identifier)
customer                            | User
account                             | DDA Account
payment product                     | Payment Product
owner                               | User
application status                  | (Submitted, Approved, Rejected)
apply                               | User, DDA Account, Payment Product
```

Scenario Outline steps that trace the relational chain, with a normalized table per concept:

```gherkin
Given a **User** {customer_id} {customer_name} with **Payment Role** *Customer*
  And a **DDA Account** {account_id} for **User** {customer_id}
  And **Payment Product** {product_id} {product_name} is available
When the **User** {customer_id} applies for a **Payment Product Agreement** {agreement_id}
    with **DDA Account** {account_id} and **Payment Product** {product_id}
    naming **User** {owner_id} as **Owner**
Then **Payment Product Agreement** {agreement_id} has application status *Submitted*
  And **User** {owner_id} is notified at {owner_email}
```

```text
### User:
| user_id | user_name | payment_role |
| USR-001 | Jane Doe  | Customer     |
| USR-002 | John Doe  | Owner        |
| USR-003 | Bob Smith | Customer     |
| USR-004 | Alice Lee | Owner        |

### DDA Account: with User
| account_id | user_id |
| DDA-001    | USR-001 |
| DDA-002    | USR-003 |

### Payment Product:
| product_id | product_name     |
| PROD-001   | Savings Plus     |
| PROD-002   | Premium Checking |

### Contact Details: with User
| user_id | owner_email    |
| USR-002 | john@acme.com  |
| USR-004 | alice@corp.com |

### Payment Product Agreement: with User (Customer), DDA Account, Payment Product, and User (Owner)
| agreement_id | customer_id | account_id | product_id | owner_id | application_status |
| AGR-001      | USR-001     | DDA-001    | PROD-001   | USR-002  | Submitted          |
| AGR-002      | USR-003     | DDA-002    | PROD-002   | USR-004  | Submitted          |
```

## DON'T

- Denormalize by repeating names across tables instead of linking through IDs — this hides ownership and breaks when a Customer has more than one Account or an Agreement covers more than one Product.

```gherkin
Given a **Customer** {customer_name} applies for a **Payment Product Agreement**
    with **Payment Product** {product_name}
Then the agreement is submitted
```

```text
| customer_name | account_number | product_name     | owner_name | owner_email   |
| Jane Doe      | DDA-001        | Savings Plus     | John Doe   | john@acme.com |
```
