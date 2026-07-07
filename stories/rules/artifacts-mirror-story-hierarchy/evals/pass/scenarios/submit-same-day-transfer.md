# Story: `Submit same-day transfer`

## Story: Submit same-day transfer

### Scenario 1: `Submit transfer before cutoff time settles same day`

*Given* a **`Treasurer`** who has a funded **`Account`** with balance *`10000 USD`*
*When* the **`Treasurer`** submits a **`Transfer`** of *`500 USD`* before *`15:00 ET`*
*Then* the **`Transfer`** is marked as *`same-day`*
