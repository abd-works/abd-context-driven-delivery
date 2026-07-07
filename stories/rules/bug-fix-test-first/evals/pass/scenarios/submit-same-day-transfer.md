# Story: `Submit same-day transfer`

## Story: Submit same-day transfer

### Scenario 1: `Zero-amount transfer is rejected`

*Given* a **`Treasurer`** with a funded **`Account`**
*When* the **`Treasurer`** submits a **`Transfer`** of *`0.00 USD`*
*Then* the **`Transfer`** is *`rejected`*
*And* the rejection reason names the minimum **`Amount`**

<!-- Evidence: Bug BUG-1234, Ops team observation 2026-06-30 -->
