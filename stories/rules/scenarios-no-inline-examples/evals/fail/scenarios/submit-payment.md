## Story: Submit Payment

### Scenario 1: Payment accepted for a valid account

*Given* the **Customer** *Alice* has **Account** *CHK-001* with **Balance** *$100,000.00*
*When* the **Customer** *Alice* submits **Payment** of *$50,000.00* to *ACH-999*
*Then* **Payment** *P-001* is created with status *Accepted*
