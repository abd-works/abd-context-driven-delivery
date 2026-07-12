## Story: View settled transfers

**Story type:** user

**Sources / context:** context/domain-language.md, context/story-map.md

### Domain terms

- *Treasurer* — corporate employee monitoring transfer outcomes
- *Transfer* — a same-day USD payment that has completed settlement
- *Settled Transfers* — list of Transfers that have completed same-day settlement
- *Settled* — status indicating same-day funds movement has completed for the Transfer

## Behaviors

### Scenario Outline 1: Treasurer views a same-day settled transfer

*Given* **Transfer** {transfer_id} has completed **Same-Day Settlement**
  *And* **Transfer** {transfer_id} status is {transfer_status}
*When* the **Treasurer** {actor} opens **Settled Transfers**
*Then* **Transfer** {transfer_id} is listed with status {transfer_status}
  *And* the list entry shows settlement date as {settlement_date} and **Amount** {amount}

### Examples

| scenario   | transfer_id | transfer_status | actor | settlement_date | amount     |
|------------|-------------|-----------------|-------|-----------------|------------|
| Scenario 1 | T-001       | Settled         | Alice | today           | $50,000.00 |

### Evidence

| Scenario   | Source (document / system) | Location                                                   |
|------------|---------------------------|------------------------------------------------------------|
| Scenario 1 | *Treasury product brief*  | §"View pending, approved, settled, and rejected transfers" |
