## Story: Search Msisdn Inventory

### Scenario: Search MSISDN inventory

*Given* a ++PML customer++ is authenticated in Midtier
*When* Midtier is asked to search ++MSISDN++ inventory for ++search term++ ++James search++ (`52637`)
*Then* Midtier queries Mavenir for available ++MSISDN++ resources matching `52637`
*And* Midtier returns matching ++available number++ values to My Paradise
