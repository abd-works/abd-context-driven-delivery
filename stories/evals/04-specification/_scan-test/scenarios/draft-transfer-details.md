## Story: Draft transfer details

**Story type:** user

**Sources / context:** Treasury product brief §"Same-day transfer flow"

### Domain terms

- *Treasurer* — the user composing and submitting transfers
- *Transfer* — a same-day USD payment initiated by the Treasurer
- *Source Account* — the debit account funding the transfer
- *Destination Account* — the recipient account registered in the system
- *Amount* — the USD value to be transferred
- *Draft* — the initial status of a Transfer before it is submitted for approval
- *Daily Transfer Limit* — maximum amount the Treasurer may draft from a Source Account in one day

### Examples

#### Transfer:

| scenario   | source_account | destination_account | amount      | transfer_id | transfer_status |
|------------|----------------|---------------------|-------------|-------------|-----------------|
| Scenario 1 | CHK-001        | ACH-999             | $50,000.00  | T-001       | Draft           |

#### Validation rejection:

| scenario   | source_account | available_balance | daily_transfer_limit | destination_account | destination_status | amount      | error_message                                              |
|------------|----------------|-------------------|----------------------|---------------------|--------------------|-------------|------------------------------------------------------------|
| Scenario 2 | CHK-001        | $500,000.00       | $100,000.00          | ACH-999             | registered         | $150,000.00 | Amount exceeds daily transfer limit of $100,000.00         |
| Scenario 3 | CHK-001        | $500,000.00       | $5,000,000.00        |                     | not provided       | $50,000.00  | Destination account is required                          |
| Scenario 4 | CHK-001        | $500,000.00       | $5,000,000.00        | ACH-999             | registered         | $0.00       | Amount must be greater than zero                         |
| Scenario 5 | CHK-001        | $20,000.00        | $5,000,000.00        | ACH-999             | registered         | $50,000.00  | Insufficient funds in source account CHK-001               |

### Background

*Given* the **Treasurer** *Alice* is composing a same-day USD transfer  
  *And* the transfer date is today  

### Behaviors

#### Scenario Outline 1: Treasurer drafts a valid same-day transfer

#### Steps

*Given* **Source Account** {source_account} is available to debit  
  *And* **Destination Account** {destination_account} is registered in the system  
  *And* an **Amount** of {amount}  
*When* the **Treasurer** *Alice* submits the transfer details form  
*Then* a **Transfer** {transfer_id} is created with status {transfer_status}  
  *And* **Transfer** {transfer_id} references **Destination Account** {destination_account} with **Amount** {amount}  
  *And* **Transfer** {transfer_id} is attributed to **Source Account** {source_account}  

#### Scenario Outline 2: Transfer details submission rejected with validation error

#### Steps

*Given* **Source Account** {source_account} has **Available Balance** {available_balance}  
  *And* **Source Account** {source_account} has **Daily Transfer Limit** {daily_transfer_limit}  
  *And* **Destination Account** {destination_account} is {destination_status} in the system  
  *And* an **Amount** of {amount}  
*When* the **Treasurer** *Alice* submits the transfer details form  
*Then* no **Transfer** is created  
  *But* a validation error {error_message} is shown  

### Evidence

| Scenario   | Source (document / system) | Location                    |
| ---------- | -------------------------- | --------------------------- |
| Scenario 1 | *Treasury product brief*   | §"Same-day transfer flow"   |
| Scenario 2 | *Treasury product brief*   | §"Same-day transfer flow"   |
| Scenario 3 | *Treasury product brief*   | §"Same-day transfer flow"   |
| Scenario 4 | *Treasury product brief*   | §"Same-day transfer flow"   |
| Scenario 5 | *Treasury product brief*   | §"Same-day transfer flow"   |
