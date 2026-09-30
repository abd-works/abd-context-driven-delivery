## Story: Patch Cart With Portability

### Scenario: Patch cart with portability

*Given* a ++PML customer++ with a ++Mavenir shopping cart++
*And* ++MSISDN++ ++available number++ ++held available number++ has been reserved as the temporary port-in number
*And* ++portability++ ++valid portability++ is in the request
*When* Midtier patches the ++Mavenir shopping cart++ with ++portability++ ++valid portability++ and ++available number++ ++held available number++
*Then* Midtier patches the ++Mavenir shopping cart++ in Mavenir with portability characteristics (planName, portinNumber, donorOperator, accountType, userType, accountNumber, device)
*And* Midtier returns the updated ++PML customer++ with ++portability++ in the ++Mavenir shopping cart++
