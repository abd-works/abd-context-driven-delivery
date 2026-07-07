## Story: Review composed transfer

**Story type:** user

### Domain terms

- *Treasurer* — the user composing and submitting transfers
- *Transfer* — a same-day USD payment in progress
- *Composed Transfer* — a Transfer whose details and destination validation are complete
- *Submit for Approval* — the action that advances the Transfer to the approval queue

## Behaviors

### Scenario 1: Treasurer reviews a fully composed transfer ready for submission

*Given* **Transfer** *T-001* is in status *Draft*  
  *And* **Transfer** *T-001* has **Source Account** *CHK-001*, **Destination Account** *ACH-999*, **Amount** *$50,000.00*  
  *And* **Transfer** *T-001* has **Validation Status** *Valid*  
*When* the **Treasurer** *Alice* opens the review screen for **Transfer** *T-001*  
*Then* the summary shows **Source Account** *CHK-001*, **Destination Account** *ACH-999*, **Amount** *$50,000.00*  
  *And* the **Submit for Approval** action is available  

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Scenario 1 | *Treasury product brief* | §"Transfer review and submit" |
