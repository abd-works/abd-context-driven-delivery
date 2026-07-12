## Story: Approve single-control transfer

**Story type:** user

**Sources / context:** context/domain-language.md, context/story-map.md

### Domain terms

- *Approver* — Treasurer authorised to approve or reject Transfers in the approval queue
- *Transfer* — a same-day USD payment awaiting approval
- *Pending Approval* — status indicating the Transfer awaits an Approver decision
- *Approved* — status after all required approvals have been recorded on a Transfer
- *Dual-Control Threshold* — transfers at or below the threshold require only one approval

## Behaviors

### Scenario Outline 1: Approver approves a below-threshold transfer

*Given* the **Approver** {approver} is reviewing the approval queue
  *And* **Transfer** {transfer_id} is in status {initial_status} with **Amount** {amount} below the **Dual-Control Threshold** {threshold}
*When* the **Approver** {approver} approves **Transfer** {transfer_id}
*Then* **Transfer** {transfer_id} status is {approved_status}
  *And* **Transfer** {transfer_id} shows approval recorded by **Approver** {approver}

### Examples

| scenario   | approver | transfer_id | initial_status   | amount     | threshold   | approved_status |
|------------|----------|-------------|------------------|------------|-------------|-----------------|
| Scenario 1 | Bob      | T-001       | Pending Approval | $50,000.00 | $250,000.00 | Approved        |

### Evidence

| Scenario   | Source (document / system) | Location                        |
|------------|---------------------------|---------------------------------|
| Scenario 1 | *Treasury product brief*  | §"Submit and approve transfers" |
