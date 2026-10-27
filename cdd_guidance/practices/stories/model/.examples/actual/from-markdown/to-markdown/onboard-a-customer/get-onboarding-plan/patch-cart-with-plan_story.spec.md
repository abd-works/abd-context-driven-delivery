## Story: Patch Cart With Plan

### Scenario: Patch Cart With Plan

*Given* a ++Mavenir customer++ with a ++Mavenir shopping cart++ (no bundle) in Mavenir
*When* Midtier is asked to patch cart with bundleId for ++plan++ ++Essentials++
*Then* Midtier fetches the catalog bundle for ++plan++ ++Essentials++ from Mavenir
*And* builds the cart item payload with the bundle product offering
*And* patches the ++Mavenir shopping cart++ through Mavenir Patch Shopping Cart
*And* returns the ++PML customer++ cart with ++plan++ ++Essentials++ bundle to Choose Onboarding Plan

### Scenario: Patch Cart With Plan — portability plan name updated

*Given* a ++Mavenir customer++ with a ++Mavenir shopping cart++ that has a ++portability++ record in Mavenir
*When* Midtier is asked to patch cart with bundleId for ++plan++ ++Data Freedom++ and portability planSelected "Data Freedom"
*Then* Midtier builds the cart item for ++plan++ ++Data Freedom++ with the portability planName characteristic set to "Data Freedom"
*And* patches the ++Mavenir shopping cart++ through Mavenir Patch Shopping Cart
*And* returns the ++PML customer++ cart with ++plan++ ++Data Freedom++ bundle and updated ++portability++ planName
