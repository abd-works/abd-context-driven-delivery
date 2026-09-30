## Story: Bring a Number

### Scenario: Bring a number

### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*But* no Transfer Code is on Bring your mobile number
*When* the Prospect clicks Get started on Bring your mobile number
*Then* the Prospect can enter ++portability++
*And* the Prospect can confirm the information is accurate
*And* the Prospect can grant permission to Paradise Mobile to bring the number
*And* the Continue operation is disabled
*And* the Prospect can go Back
*When* the Prospect enters ++portability++ ++valid portability++ and checks both permissions
*Then* the Continue operation is enabled
*When* the Prospect clicks Continue
*Then* My Paradise submits ++portability++ ++valid portability++ to the Midtier
*And* Midtier returns a temporary ++MSISDN++ ++available number++ ++held available number++
*And* the Prospect is forwarded to Select Sim


### Scenario: Number to be ported is incomplete

### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*But* no Transfer Code is on Bring your mobile number
*When* the Prospect clicks Get started on Bring your mobile number
*Then* the Prospect can enter ++portability++
*And* the Prospect can confirm the information is accurate
*And* the Prospect can grant permission to Paradise Mobile to bring the number
*And* the Continue operation is disabled
*And* the Prospect can go Back
*When* the Prospect enters ++portability++ ++valid portability++ and checks both permissions
*Then* the Continue operation is enabled
*When* the Prospect clicks Continue
*Then* My Paradise submits ++portability++ ++valid portability++ to the Midtier
*And* Midtier returns a temporary ++MSISDN++ ++available number++ ++held available number++
*And* the Prospect is forwarded to Select Sim
*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*When* the Prospect leaves Number to be ported as the Bermuda prefix only
*Then* Number to be ported shows *Please enter the full Bermuda number.*
*And* the Continue operation stays disabled


### Scenario: Provider not selected

### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*But* no Transfer Code is on Bring your mobile number
*When* the Prospect clicks Get started on Bring your mobile number
*Then* the Prospect can enter ++portability++
*And* the Prospect can confirm the information is accurate
*And* the Prospect can grant permission to Paradise Mobile to bring the number
*And* the Continue operation is disabled
*And* the Prospect can go Back
*When* the Prospect enters ++portability++ ++valid portability++ and checks both permissions
*Then* the Continue operation is enabled
*When* the Prospect clicks Continue
*Then* My Paradise submits ++portability++ ++valid portability++ to the Midtier
*And* Midtier returns a temporary ++MSISDN++ ++available number++ ++held available number++
*And* the Prospect is forwarded to Select Sim
*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*When* the Prospect leaves Number to be ported as the Bermuda prefix only
*Then* Number to be ported shows *Please enter the full Bermuda number.*
*And* the Continue operation stays disabled
*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*When* the Prospect blurs Your current provider without selecting a provider
*Then* Your current provider shows *Please select a provider.*
*And* the Continue operation stays disabled
