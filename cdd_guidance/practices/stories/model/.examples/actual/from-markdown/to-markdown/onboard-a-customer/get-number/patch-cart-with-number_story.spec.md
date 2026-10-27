## Story: Patch Cart With Number

### Scenario: Patch cart with MSISDN

*Given* a ++PML customer++ with a ++Mavenir shopping cart++
*And* ++MSISDN++ ++available number++ ++chosen available number++ has been reserved
*When* Midtier is asked to patch the ++Mavenir shopping cart++ with ++MSISDN++ ++available number++ ++chosen available number++
*Then* Midtier patches the ++Mavenir shopping cart++ in Mavenir with ++available number++ ++chosen available number++ as the MSISDN characteristic
*And* Midtier returns the updated ++PML customer++ to My Paradise
