# Story: `Submit same-day transfer`

## Story: Submit same-day transfer

### Scenario 1: `Submit transfer before cutoff settles same day`

*Given* a **`Treasurer`** with a funded **`Account`**
*When* the **`Treasurer`** submits a **`Transfer`** of *`500 USD`* before *`15:00 ET`*
*Then* the **`Transfer`** is marked as *`same-day`*

## Context gaps

- **Recipient KYC status** — the scenario does not specify whether the payee must be KYC-verified before the transfer settles; assumed verified per interview 2026-06-14
