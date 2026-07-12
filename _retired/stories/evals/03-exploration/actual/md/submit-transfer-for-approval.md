## Story: Submit transfer for approval

**Story type:** user

**Sources / context:** context/domain-language.md, context/story-map.md

### Domain terms

- *Treasurer* — corporate employee authorised to initiate and submit transfers
- *Transfer* — a same-day USD payment in progress
- *Pending Approval* — status after submission, awaiting an Approver action
- *Dual-Control Threshold* — the amount boundary above which two Approver decisions are required

## Behaviors

### Scenario Outline 1: Treasurer submits a below-threshold transfer for approval

*Given* the **Treasurer** {actor} is reviewing **Transfer** {transfer_id} ready for submission
  *And* **Transfer** {transfer_id} is a **Composed Transfer** with **Amount** {amount} and **Validation Status** {validation_status} below the **Dual-Control Threshold** {threshold}
*When* the **Treasurer** {actor} selects **Submit for Approval** on **Transfer** {transfer_id}
*Then* **Transfer** {transfer_id} status is {submitted_status}
  *And* **Transfer** {transfer_id} is visible in the approval queue requiring {approval_count} approval

### Examples

| scenario   | actor | transfer_id | amount     | validation_status | threshold   | submitted_status | approval_count |
|------------|-------|-------------|------------|-------------------|-------------|------------------|----------------|
| Scenario 1 | Alice | T-001       | $50,000.00 | Valid             | $250,000.00 | Pending Approval | single         |

### Evidence

| Scenario   | Source (document / system) | Location                        |
|------------|---------------------------|---------------------------------|
| Scenario 1 | *Treasury product brief*  | §"Submit and approve transfers" |
