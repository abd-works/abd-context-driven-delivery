# Story: `Submit same-day transfer`

## Story: Submit same-day transfer

### Scenario 1: `Submit transfer via HTTP endpoint`

*Given* a **`Treasurer`** with a funded **`Account`**
*When* the **`Treasurer`** POSTs to */v2/transfers* with a valid **`TransferRequest`**
*Then* the response is *201 Created* with a **`TransferResponse`** containing a **`Confirmation Number`**
*And* an event *TransferAccepted* is emitted with the **`Confirmation Number`**
