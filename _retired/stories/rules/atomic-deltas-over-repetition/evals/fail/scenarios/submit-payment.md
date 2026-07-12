# Story: `Submit same-day transfer`

## Story: Submit same-day transfer

### Scenario 1: `Submit transfer before cutoff settles same day`

*Given* a **`Treasurer`** with a funded **`Account`** and *`10000 USD`* balance
*And* the **`Treasurer`** is signed in with two-factor
*When* the **`Treasurer`** submits a **`Transfer`** of *`500 USD`* before *`15:00 ET`*
*Then* the **`Transfer`** is marked as *`same-day`*

### Scenario 2: `Submit transfer after cutoff settles next day`

*Given* a **`Treasurer`** with a funded **`Account`** and *`10000 USD`* balance
*And* the **`Treasurer`** is signed in with two-factor
*When* the **`Treasurer`** submits a **`Transfer`** of *`500 USD`* before *`15:00 ET`*
*Then* the **`Transfer`** is marked as *`next-day`*
