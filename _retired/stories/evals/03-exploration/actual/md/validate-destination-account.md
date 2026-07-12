## Story: Validate destination account

**Story type:** user

**Sources / context:** context/domain-language.md, context/story-map.md

### Domain terms

- *Treasurer* — corporate employee authorised to initiate transfers
- *Transfer* — a same-day USD payment in progress
- *Destination Account* — the registered recipient account to be confirmed before submission
- *Validation Status* — the result of checking a Destination Account: Valid or Invalid
- *Draft* — status indicating the Transfer is composed but not yet submitted

## Behaviors

### Scenario Outline 1: Treasurer validates a registered destination account

*Given* **Transfer** {transfer_id} has **Destination Account** {destination_account}
  *And* **Destination Account** {destination_account} is {account_status} in the system
*When* the **Treasurer** {actor} validates the **Destination Account** on **Transfer** {transfer_id}
*Then* **Transfer** {transfer_id} has **Validation Status** {validation_status}
  *And* **Transfer** {transfer_id} remains in status {transfer_status}

### Examples

| scenario   | transfer_id | destination_account | account_status        | actor | validation_status | transfer_status |
|------------|-------------|---------------------|-----------------------|-------|-------------------|-----------------|
| Scenario 1 | T-001       | ACH-999             | registered and active | Alice | Valid             | Draft           |

### Evidence

| Scenario   | Source (document / system) | Location                  |
|------------|---------------------------|---------------------------|
| Scenario 1 | *Treasury product brief*  | §"Destination validation" |
