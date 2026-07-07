# Story: `Submit same-day transfer`

## Story: Submit same-day transfer

### Scenario 1: `Submit transfer before cutoff time settles same day`

*Given* a **`Treasurer`** who has a funded **`Account`** with balance *`10000 USD`*
*When* the **`Treasurer`** submits a **`Transfer`** of *`500 USD`* to a **`Payee`** before the *`cutoff time`* of *`15:00 ET`*
*And* the **`Settlement`** is expected on *`the same business day`*

### Scenario 2: `Submit transfer after cutoff time settles next day`

*Given* a **`Treasurer`** who has a funded **`Account`** with balance *`10000 USD`*
*When* the **`Treasurer`** submits a **`Transfer`** of *`500 USD`* to a **`Payee`** after the *`cutoff time`* of *`15:00 ET`*
*Then* the **`Transfer`** is marked as *`next-day`*
*And* the **`Settlement`** is expected on *`the next business day`*
