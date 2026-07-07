# Story: `Submit same-day transfer`

## Story: Submit same-day transfer

### Scenario 1: `Submit transfer before cutoff settles same day`

*Given* a **`Treasurer`** *`foo`* with a funded **`Account`** *`DDA-001`*
*When* the **`Treasurer`** submits a **`Transfer`** of *`10000.00 USD`* before *`15:00 ET`*
*Then* the **`Transfer`** is marked as *`same-day`*
