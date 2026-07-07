## Story: Review composed transfer

**Story type:** user

**Sources / context:** context/domain-language.md, context/story-map.md

### Domain terms

- *Treasurer* — corporate employee authorised to initiate transfers
- *Transfer* — a same-day USD payment in progress
- *Composed Transfer* — a Transfer whose details and destination validation are complete
- *Submit for Approval* — the action that advances the Transfer to the approval queue
- *Validation Status* — the result of the destination account check

## Behaviors

### Scenario Outline 1: Treasurer reviews a fully composed transfer ready for submission

*Given* the **Treasurer** {actor} has a **Composed Transfer** {transfer_id} in status {transfer_status} with **Validation Status** {validation_status}
  *And* **Transfer** {transfer_id} shows **Source Account** {source_account}, **Destination Account** {destination_account}, **Amount** {amount}
*When* the **Treasurer** {actor} opens the review screen for **Transfer** {transfer_id}
*Then* the summary shows **Source Account** {source_account}, **Destination Account** {destination_account}, **Amount** {amount}
  *And* the **Submit for Approval** action is available

### Examples

| scenario   | actor | transfer_id | transfer_status | validation_status | source_account | destination_account | amount     |
|------------|-------|-------------|-----------------|-------------------|----------------|---------------------|------------|
| Scenario 1 | Alice | T-001       | Draft           | Valid             | CHK-001        | ACH-999             | $50,000.00 |

### Evidence

| Scenario   | Source (document / system) | Location                      |
|------------|---------------------------|-------------------------------|
| Scenario 1 | *Treasury product brief*  | §"Transfer review and submit" |
