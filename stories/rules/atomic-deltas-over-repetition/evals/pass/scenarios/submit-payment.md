# Story: `Submit same-day transfer`

## Story: Submit same-day transfer

### Scenario 1: `Submit transfer before cutoff settles same day`

*Given* a **`Treasurer`** with a funded **`Account`** and *`10000 USD`* balance
*When* the **`Treasurer`** submits a **`Transfer`** of *`500 USD`* before *`15:00 ET`*
*Then* the **`Transfer`** is marked as *`same-day`*

### Scenario 2: `Reject transfer above limit`

*When* the **`Treasurer`** submits a **`Transfer`** of *`60000 USD`*
*Then* the **`Transfer`** is rejected for exceeding the daily **`Limit`**
