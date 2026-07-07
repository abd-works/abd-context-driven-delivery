## Story: Validate destination account

**Story type:** user

**Sources / context:** Treasury product brief §"Destination validation"

### Domain terms

- *Treasurer* — the user composing and submitting transfers
- *Transfer* — a same-day USD payment in progress
- *Destination Account* — the recipient account to be confirmed before submission
- *Validation Status* — the result of the account check: *Valid* or *Invalid*

### Background

*Given* **Transfer** *T-001* is in status *Draft*  
  *And* the **Treasurer** *Alice* is composing the transfer  

## Behaviors

### Scenario Outline 1: Destination account validation outcome

*Given* **Transfer** *T-001* has **Destination Account** {destination_account}  
  *And* **Destination Account** {destination_account} is {account_registration_status} in the system  
*When* the **Treasurer** *Alice* validates the **Destination Account** on **Transfer** *T-001*  
*Then* the **Treasurer** *Alice* sees **Validation Status** {validation_status} on the compose screen  
  *And* **Transfer** *T-001* has **Validation Status** {validation_status} while remaining in status *Draft*  
  *But* the **Treasurer** *Alice* sees error {error_message} when **Validation Status** is *Invalid*  

### Examples

| scenario   | destination_account | account_registration_status | validation_status | error_message                                      |
|------------|---------------------|-----------------------------|-------------------|----------------------------------------------------|
| Scenario 1 | ACH-999             | registered and active       | Valid             |                                                    |
| Scenario 2 | ACH-000             | not registered              | Invalid           | Destination account ACH-000 is not registered      |
| Scenario 3 | ACH-888             | registered but inactive     | Invalid           | Destination account ACH-888 is inactive            |

### Evidence

| Scenario   | Source (document / system) | Location                 |
| ---------- | -------------------------- | ------------------------ |
| Scenario 1 | *Treasury product brief* | §"Destination validation" |
| Scenario 2 | *Treasury product brief* | §"Destination validation" |
| Scenario 3 | *Treasury product brief* | §"Destination validation" |
