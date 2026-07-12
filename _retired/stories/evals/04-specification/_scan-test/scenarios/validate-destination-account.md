## Story: Validate destination account

**Story type:** user

**Sources / context:** Treasury product brief §"Destination validation"

### Domain terms

- *Treasurer* — the user composing and submitting transfers
- *Transfer* — a same-day USD payment in progress
- *Destination Account* — the recipient account to be confirmed before submission
- *Validation Status* — the result of the account check: *Valid* or *Invalid*

### Examples

#### Destination validation:

| scenario   | destination_account | account_registration_status | validation_status | error_message                                      |
|------------|---------------------|-----------------------------|-------------------|----------------------------------------------------|
| Scenario 1 | ACH-999             | registered and active       | Valid             |                                                    |
| Scenario 2 | ACH-000             | not registered              | Invalid           | Destination account ACH-000 is not registered      |
| Scenario 3 | ACH-888             | registered but inactive     | Invalid           | Destination account ACH-888 is inactive            |

### Background

*Given* **Transfer** *T-001* is in status *Draft*  
  *And* the **Treasurer** *Alice* is composing the transfer  

### Behaviors

#### Scenario Outline 1: Destination account validation outcome

#### Steps

*Given* **Transfer** *T-001* has **Destination Account** {destination_account}  
  *And* **Destination Account** {destination_account} is {account_registration_status} in the system  
*When* the **Treasurer** *Alice* validates the **Destination Account** on **Transfer** *T-001*  
*Then* **Transfer** *T-001* has **Validation Status** {validation_status}  
  *And* **Transfer** *T-001* remains in status *Draft*  
  *But* an error {error_message} is shown when **Validation Status** is *Invalid*  

### Evidence

| Scenario   | Source (document / system) | Location                 |
| ---------- | -------------------------- | ------------------------ |
| Scenario 1 | *Treasury product brief* | §"Destination validation" |
| Scenario 2 | *Treasury product brief* | §"Destination validation" |
| Scenario 3 | *Treasury product brief* | §"Destination validation" |
