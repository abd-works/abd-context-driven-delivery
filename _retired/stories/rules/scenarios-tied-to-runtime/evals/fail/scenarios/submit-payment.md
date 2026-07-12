# Story: `Submit same-day transfer`

## Story: Submit same-day transfer

### Scenario 1: `Submit transfer via HTTP endpoint`

*Given* a **`Treasurer`** with a funded **`Account`**
*When* the **`Treasurer`** submits a **`Transfer`** and the service accepts it
*Then* the **`Transfer`** is marked as *`same-day`*
