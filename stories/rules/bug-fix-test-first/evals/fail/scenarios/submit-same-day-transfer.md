# Story: `Submit same-day transfer`

## Story: Submit same-day transfer

### Scenario 1: `Zero-amount transfer is rejected`

*Given* a **`Treasurer`** with a funded **`Account`**
*When* the **`Treasurer`** submits a **`Transfer`** of *`0.00 USD`*
*Then* the **`Transfer`** is *`rejected`*
