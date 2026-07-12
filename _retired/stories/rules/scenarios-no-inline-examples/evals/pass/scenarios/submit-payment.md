## Story: Submit Payment

### Scenario Outline 1: Payment accepted for a valid account

*Given* the **Customer** {actor} has **Account** {account_id} with **Balance** {balance}
*When* the **Customer** {actor} submits **Payment** of {amount} to {destination}
*Then* **Payment** {payment_id} is created with status {status}

### Examples

| scenario   | actor | account_id | balance     | amount     | destination | payment_id | status   |
|------------|-------|------------|-------------|------------|-------------|------------|----------|
| Scenario 1 | Alice | CHK-001    | $100,000.00 | $50,000.00 | ACH-999     | P-001      | Accepted |
