# Story: `Cancel pending transfer`

## Story: Cancel pending transfer

### Scenario 1: `Cancel pending transfer before route`

*Given* a **`Treasurer`** with a **`Pending Transfer`**
*When* the **`Treasurer`** cancels the **`Transfer`** before the **`System`** routes it
*Then* the **`Transfer`** is marked as *`cancelled`*
