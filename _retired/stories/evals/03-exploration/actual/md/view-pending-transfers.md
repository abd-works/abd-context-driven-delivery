## Story: View pending transfers

**Story type:** user

**Sources / context:** context/domain-language.md, context/story-map.md

### Domain terms

- *Treasurer* — corporate employee monitoring transfer status
- *Transfer* — a same-day USD payment in the settlement pipeline
- *Pending Transfers* — list of Transfers not yet settled or rejected
- *Pending* — status indicating the Transfer has entered the settlement queue

## Behaviors

### Scenario Outline 1: Treasurer views a transfer pending settlement

*Given* **Transfer** {transfer_id} is in status {transfer_status} in the settlement queue
  *And* **Transfer** {transfer_id} has **Amount** {amount} and **Destination Account** {destination_account}
*When* the **Treasurer** {actor} opens **Pending Transfers**
*Then* **Transfer** {transfer_id} is listed with status {transfer_status}
  *And* the list entry shows **Amount** {amount} and **Destination Account** {destination_account}

### Examples

| scenario   | transfer_id | transfer_status | amount     | destination_account | actor |
|------------|-------------|-----------------|------------|---------------------|-------|
| Scenario 1 | T-001       | Pending         | $50,000.00 | ACH-999             | Alice |

### Evidence

| Scenario   | Source (document / system) | Location                                                   |
|------------|---------------------------|------------------------------------------------------------|
| Scenario 1 | *Treasury product brief*  | §"View pending, approved, settled, and rejected transfers" |
