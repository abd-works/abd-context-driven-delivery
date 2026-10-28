## Story: Submit Patch Cart With Number Request to Mid-Tier

### Scenario: Patch cart with number

*Given* ++MSISDN++ ++available number++ ++chosen available number++ has been reserved
*When* My Paradise patches the ++Mavenir shopping cart++ with ++available number++ ++chosen available number++ through the Midtier
*Then* Midtier returns the updated ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++
*And* the Prospect is forwarded to Select Sim

### Scenario: Patch cart with number fails

*Given* ++MSISDN++ ++available number++ ++chosen available number++ has been reserved
*When* My Paradise patches the ++Mavenir shopping cart++ with ++available number++ ++chosen available number++ through the Midtier
*But* Midtier returns an error
*Then* My Paradise shows *Failed to update your cart.*
