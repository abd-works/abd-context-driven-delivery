## Story: Draft transfer details

**Story type:** user

### Domain terms

- *Treasurer* — the user composing and submitting transfers
- *Transfer* — a same-day USD payment initiated by the Treasurer
- *Source Account* — the debit account funding the transfer (e.g. a checking account)
- *Destination Account* — the recipient account registered in the system
- *Amount* — the USD value to be transferred
- *Draft* — the initial status of a Transfer before it is submitted for approval

## Behaviors

### Scenario 1: Treasurer drafts a valid same-day transfer

*Given* **Source Account** *CHK-001* is available to debit  
  *And* **Destination Account** *ACH-999* is registered in the system  
  *And* an **Amount** of *$50,000.00*  
*When* the **Treasurer** *Alice* submits the transfer details form  
*Then* a **Transfer** *T-001* is created with status *Draft*  
  *And* **Transfer** *T-001* references **Destination Account** *ACH-999* with **Amount** *$50,000.00*  
  *And* **Transfer** *T-001* is attributed to **Source Account** *CHK-001*  

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Scenario 1 | *Treasury product brief* | §"Same-day transfer flow" |
