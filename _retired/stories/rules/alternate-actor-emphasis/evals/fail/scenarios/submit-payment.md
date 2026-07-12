# Story: `Submit same-day transfer`

## Story: Submit same-day transfer

### Scenario 1: `Submit transfer before cutoff settles same day`

*Given* a **`Treasurer`** with a funded **`Account`**
*When* the **`Treasurer`** opens the transfer form
*And* the **`Treasurer`** enters an **`Amount`** of *`500 USD`*
*And* the **`Treasurer`** confirms the **`Transfer`**
*Then* the **`System`** returns a **`Confirmation Number`**
