## Story: Validate destination account

**Story type:** user

### Domain terms

- *Treasurer* — the user composing and submitting transfers
- *Transfer* — a same-day USD payment in progress
- *Destination Account* — the recipient account to be confirmed before submission
- *Validation Status* — the result of the account check: *Valid* or *Invalid*

## Behaviors

### Scenario 1: Treasurer validates a registered destination account

*Given* **Transfer** *T-001* has **Destination Account** *ACH-999*  
  *And* **Destination Account** *ACH-999* is registered and active in the system  
*When* the **Treasurer** *Alice* validates the **Destination Account** on **Transfer** *T-001*  
*Then* **Transfer** *T-001* has **Validation Status** *Valid*  
  *And* **Transfer** *T-001* remains in status *Draft*  

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Scenario 1 | *Treasury product brief* | §"Destination validation" |
