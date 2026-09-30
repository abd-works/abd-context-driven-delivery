## Story: Patch Shopping Cart

### Scenario: Patch shopping cart with portability

*Given* a ++Mavenir shopping cart++ with a plan bundle cart item and temporary ++MSISDN++ ++available number++ ++held available number++
*When* Mavenir is asked to patch the ++Mavenir shopping cart++ with ++portability++ ++valid portability++ characteristics
*Then* Mavenir updates the ++Mavenir shopping cart++ cart item with portability characteristics (planName, portinNumber, donorOperator, accountType, userType, accountNumber, device, portin, requestType)
*And* Mavenir returns the updated ++Mavenir shopping cart++ to Midtier

### Scenario: Patch shopping cart with MSISDN

*Given* a ++Mavenir shopping cart++ with a plan bundle cart item
*But* no MSISDN characteristic on the cart item
*When* Mavenir is asked to patch the ++Mavenir shopping cart++ with ++MSISDN++ ++available number++ ++chosen available number++ as a cart item characteristic
*Then* Mavenir updates the ++Mavenir shopping cart++ cart item with ++available number++ ++chosen available number++ as the MSISDN characteristic
*And* Mavenir returns the updated ++Mavenir shopping cart++ to Midtier

### Scenario: Patch Shopping Cart

*Given* a ++Mavenir customer++ with a ++Mavenir shopping cart++ (no bundle) in Mavenir
*When* Mavenir is asked to patch the ++Mavenir shopping cart++ with a bundle cart item for ++plan++ ++Essentials++
*Then* Mavenir updates the ++Mavenir shopping cart++ with the ++plan++ ++Essentials++ bundle product item
*And* returns the patched ++Mavenir shopping cart++ to Patch Cart With Plan
