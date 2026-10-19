## Story: Query Msisdn Inventory

### Scenario: Query MSISDN inventory for porting

*Given* a ++PML customer++ is authenticated in Midtier
*And* ++portability++ is in the portability request
*When* Midtier queries ++MSISDN++ inventory for a temporary port-in number (`count: 1`)
*Then* Midtier queries Mavenir for 1 available ++MSISDN++ resource
*And* Midtier receives ++available number++ ++held available number++ as the temporary number

### Scenario: Query MSISDN inventory

*Given* a ++PML customer++ is authenticated in Midtier
*When* Midtier is asked to query ++MSISDN++ inventory
*Then* Midtier queries Mavenir for 5 available ++MSISDN++ resources
*And* Midtier returns a list of ++available number++ values to My Paradise
