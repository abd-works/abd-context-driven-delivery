## Story: Route transfer before cutoff

**Story type:** user

**Sources / context:** context/domain-language.md, context/story-map.md

### Domain terms

- *Treasurer* — corporate employee authorised to initiate and route transfers
- *Transfer* — a same-day USD payment ready for settlement routing
- *Approved* — status indicating required approvals are complete
- *Same-Day Cutoff* — the daily deadline after which same-day settlement is unavailable
- *Same-Day Settlement* — routing outcome marking the Transfer for settlement within the current business day

## Behaviors

### Scenario Outline 1: Treasurer routes an approved transfer before the same-day cutoff

*Given* **Transfer** {transfer_id} is in status {initial_status}
  *And* the current time is before the **Same-Day Cutoff** {cutoff_time}
*When* the **Treasurer** {actor} routes **Transfer** {transfer_id} into the settlement window
*Then* **Transfer** {transfer_id} is marked for **Same-Day Settlement**
  *And* **Transfer** {transfer_id} status is {queue_status} in the settlement queue

### Examples

| scenario   | transfer_id | initial_status | cutoff_time | actor | queue_status |
|------------|-------------|----------------|-------------|-------|--------------|
| Scenario 1 | T-001       | Approved       | 15:00 ET    | Alice | Pending      |

### Evidence

| Scenario   | Source (document / system) | Location                                            |
|------------|---------------------------|-----------------------------------------------------|
| Scenario 1 | *Treasury product brief*  | §"Route transfers into the daily settlement window" |
