## Story: Get Mavenir Customer and Transform To My Paradise Customer And Return

### Scenario: Get Mavenir Customer and Transform To My Paradise Customer And Return

### Background

*Given* Midtier has verified the ++account token++
*And* the ++account token++ has a ++Mavenir customer++ id
*And* Mavenir has a new Mavenir customer (`++new Mavenir customer++` row)

*When* Midtier receives a Paradise request to get a ++PML customer++
*Then* Midtier maps that request to a Mavenir customerDetails get for the ++Mavenir customer++ ++new Mavenir customer++
*And* Midtier submits customerDetails to Mavenir
*And* Midtier receives the ++Mavenir customer++ ++new Mavenir customer++
*And* Midtier maps that ++Mavenir customer++ to a new ++PML customer++
*And* Midtier returns the new ++PML customer++
