## Story: Draft transfer details

**Story type:** user

**Sources / context:** context/domain-language.md, context/story-map.md

### Domain terms

- *Treasurer* — corporate employee authorised to initiate transfers
- *Transfer* — a same-day USD payment initiated by the Treasurer
- *Source Account* — the demand-deposit account debited to fund the Transfer
- *Destination Account* — the registered recipient account credited by the Transfer
- *Amount* — the USD value of a Transfer
- *Draft* — initial status of a Transfer before it is submitted for approval

## Behaviors

### Scenario Outline 1: Treasurer drafts a valid same-day transfer

*Given* the **Treasurer** {actor} is composing a new **Transfer**
  *And* **Source Account** {source_account} is available to debit
  *And* **Destination Account** {destination_account} is registered in the system
*When* the **Treasurer** {actor} submits **Amount** {amount} on the transfer details form
*Then* a **Transfer** {transfer_id} is created with status {transfer_status}
  *And* **Transfer** {transfer_id} references **Source Account** {source_account}, **Destination Account** {destination_account}, and **Amount** {amount}

### Examples

| scenario   | actor | source_account | destination_account | amount     | transfer_id | transfer_status |
|------------|-------|----------------|---------------------|------------|-------------|-----------------|
| Scenario 1 | Alice | CHK-001        | ACH-999             | $50,000.00 | T-001       | Draft           |

### Evidence

| Scenario   | Source (document / system) | Location                  |
|------------|---------------------------|---------------------------|
| Scenario 1 | *Treasury product brief*  | §"Same-day transfer flow" |
