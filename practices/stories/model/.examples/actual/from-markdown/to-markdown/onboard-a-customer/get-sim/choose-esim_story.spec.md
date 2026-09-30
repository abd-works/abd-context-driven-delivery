## Story: Choose Esim

### Scenario: Choose eSIM

### Background

*Given* eSIM is available
*And* the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++
*And* the phone supports eSIM
*Given* no ++SIM type++ is on the line
*When* the Customer selects eSIM
*Then* My Paradise sends the patch cart request to Mavenir with ++SIM type++ eSIM
*When* Mavenir returns the updated ++Mavenir shopping cart++ with ++SIM type++ eSIM
*Then* My Paradise stores eSIM on the line
*And* the Customer is forwarded to Verify ID


### Scenario: Choose eSIM — already on the line

### Background

*Given* eSIM is available
*And* the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++
*And* the phone supports eSIM
*Given* no ++SIM type++ is on the line
*When* the Customer selects eSIM
*Then* My Paradise sends the patch cart request to Mavenir with ++SIM type++ eSIM
*When* Mavenir returns the updated ++Mavenir shopping cart++ with ++SIM type++ eSIM
*Then* My Paradise stores eSIM on the line
*And* the Customer is forwarded to Verify ID
*Given* eSIM is available
*And* the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++
*And* the phone supports eSIM
*Given* the line already has ++SIM type++ eSIM
*When* the Customer selects eSIM
*Then* My Paradise skips the cart patch


### Scenario: Choose eSIM — cart patch fails

### Background

*Given* eSIM is available
*And* the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++
*And* the phone supports eSIM
*Given* no ++SIM type++ is on the line
*When* the Customer selects eSIM
*Then* My Paradise sends the patch cart request to Mavenir with ++SIM type++ eSIM
*When* Mavenir returns the updated ++Mavenir shopping cart++ with ++SIM type++ eSIM
*Then* My Paradise stores eSIM on the line
*And* the Customer is forwarded to Verify ID
*Given* eSIM is available
*And* the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++
*And* the phone supports eSIM
*Given* the line already has ++SIM type++ eSIM
*When* the Customer selects eSIM
*Then* My Paradise skips the cart patch
*Given* eSIM is available
*And* the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++
*And* the phone supports eSIM
*Given* Mavenir returns an error on cart patch
*When* the Customer selects eSIM
*Then* the SIM selection fails
*And* the line has no ++SIM type++
