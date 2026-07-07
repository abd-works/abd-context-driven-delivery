## Story: Review composed transfer

**Story type:** user

**Sources / context:** Treasury product brief §"Transfer review and submit"

### Domain terms

- *Treasurer* — the user composing and submitting transfers
- *Transfer* — a same-day USD payment in progress
- *Composed Transfer* — a Transfer whose details and destination validation are complete
- *Validation Status* — the result of destination account validation
- *Submit for Approval* — the action that advances the Transfer to the approval queue

### Examples

#### Review screen:

| scenario   | validation_status | submit_for_approval_available | warning_or_error_message                                      |
|------------|-------------------|-------------------------------|---------------------------------------------------------------|
| Scenario 1 | Valid             | true                          |                                                               |
| Scenario 2 | Pending           | false                         | Validate destination account before submitting                |
| Scenario 3 | Invalid           | false                         | Destination account is invalid — correct before submitting    |

#### Transfer summary:

| scenario   | source_account | destination_account | amount      |
|------------|----------------|---------------------|-------------|
| Scenario 1 | CHK-001        | ACH-999             | $50,000.00  |
| Scenario 2 | CHK-001        | ACH-999             | $50,000.00  |
| Scenario 3 | CHK-001        | ACH-999             | $50,000.00  |

### Background

*Given* **Transfer** *T-001* is in status *Draft*  
  *And* **Transfer** *T-001* has **Source Account** *CHK-001*, **Destination Account** *ACH-999*, **Amount** *$50,000.00*  
  *And* the **Treasurer** *Alice* is composing the transfer  

### Behaviors

#### Scenario Outline 1: Treasurer reviews a composed transfer before submission

#### Steps

*Given* **Transfer** *T-001* has **Validation Status** {validation_status}  
*When* the **Treasurer** *Alice* opens the review screen for **Transfer** *T-001*  
*Then* the summary shows **Source Account** {source_account}, **Destination Account** {destination_account}, **Amount** {amount}  
  *And* the **Submit for Approval** action is available when {submit_for_approval_available} is *true*  
  *But* the **Submit for Approval** action is disabled when {submit_for_approval_available} is *false*  
  *And* a message {warning_or_error_message} is shown when {submit_for_approval_available} is *false*  

### Evidence

| Scenario   | Source (document / system) | Location                      |
| ---------- | -------------------------- | ----------------------------- |
| Scenario 1 | *Treasury product brief*   | §"Transfer review and submit" |
| Scenario 2 | *Treasury product brief*   | §"Transfer review and submit" |
| Scenario 3 | *Treasury product brief*   | §"Transfer review and submit" |
