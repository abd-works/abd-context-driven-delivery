## Story: Attach memo to transfer

**Story type:** user

**Sources / context:** Treasury product brief §"Transfer memo and audit trail"

### Domain terms

- *Treasurer* — the user composing and submitting transfers
- *Transfer* — a same-day USD payment in progress
- *Memo* — a free-text note (≤ 500 characters) attached to the Transfer for approver and audit context

### Background

*Given* **Transfer** *T-001* is in status *Draft*  
  *And* the **Treasurer** *Alice* is composing the transfer  

## Behaviors

### Scenario Outline 1: Treasurer attaches or replaces a memo on a draft transfer

#### Steps

*Given* **Transfer** *T-001* has existing **Memo** *{existing_memo}*  
*When* the **Treasurer** *Alice* attaches **Memo** text *{memo_text}* to **Transfer** *T-001*  
*Then* **Transfer** *T-001* has **Memo** *{expected_memo}*  
  *And* **Transfer** *T-001* remains in status *Draft*  

### Examples

| scenario   | existing_memo   | memo_text                                     | expected_memo                                 |
|------------|-----------------|-----------------------------------------------|-----------------------------------------------|
| Scenario 1 |                 | Q3 vendor settlement — invoice #4421          | Q3 vendor settlement — invoice #4421          |
| Scenario 2 | Original note   | Revised: Q3 vendor settlement — invoice #4421 | Revised: Q3 vendor settlement — invoice #4421 |

### Scenario 2: Memo exceeds 500-character limit

*Given* **Transfer** *T-001* is in status *Draft*  
*When* the **Treasurer** *Alice* attaches a **Memo** of *501 characters* to **Transfer** *T-001*  
*Then* no **Memo** is saved on **Transfer** *T-001*  
  *And* a validation error *"Memo must not exceed 500 characters"* is shown  

### Evidence

| Scenario   | Source                   | Location                         |
|------------|--------------------------|----------------------------------|
| Scenario 1 | *Treasury product brief* | §"Transfer memo and audit trail" |
| Scenario 2 | *Treasury product brief* | §"Transfer memo and audit trail" |
| Scenario 2 | *Treasury product brief* | §"Transfer memo and audit trail" |
