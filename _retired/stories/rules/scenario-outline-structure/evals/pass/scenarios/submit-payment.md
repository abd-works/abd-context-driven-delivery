# Story: `Submit same-day transfer`

## Story: Submit same-day transfer

### Scenario Outline 1: `Transfer settlement window depends on submission time`

*Given* a **`Treasurer`** with a funded **`Account`**
*When* the **`Treasurer`** submits a **`Transfer`** of *`<amount>`* at *`<time>`*
*Then* the **`Transfer`** is marked as *`<window>`*

### Examples

| amount    | time     | window   |
| --------- | -------- | -------- |
| 500 USD   | 14:00 ET | same-day |
| 500 USD   | 16:00 ET | next-day |
| 60000 USD | 14:00 ET | rejected |
