# Story: `Chargeback disputed transfer`

## Story: Chargeback disputed transfer

### Scenario 1: `Chargeback settles when merchant does not respond in 7 days`

*Given* a **`Cardholder`** files a *`chargeback`* on a settled **`Transfer`**
*When* the **`Merchant`** does not respond within *`7 days`*
*Then* the **`Chargeback`** is *`settled`* in favour of the **`Cardholder`**
