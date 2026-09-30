## Story: Activate Sim

### Scenario: Activate Sim

### Background

*Given* the Customer is waiting for a Paradise SIM
*And* the Customer is verified
*And* the line has ++SIM type++ pSIM
*But* no ++ICCID++ is on the line
*And* the ++Mavenir customer++ has ++waiting pSIM++ Active

*Given* Mavenir has ++ICCID++ ++valid ICCID++ available in inventory
*When* the Customer activates the SIM with ++ICCID++ ++valid ICCID++
*Then* My Paradise sends the ICCID inventory request to Mavenir with ++ICCID++ ++valid ICCID++
*And* My Paradise sends the patch cart request to Mavenir with ++SIM type++ pSIM and ++ICCID++ ++valid ICCID++
*And* My Paradise sends the pSIM delivered order to Mavenir
*When* Mavenir creates the product order and clears ++waiting pSIM++
*Then* My Paradise stores ++ICCID++ ++valid ICCID++ on the line

### Scenario: waiting pSIM is absent

### Background

*Given* the Customer is waiting for a Paradise SIM
*And* the Customer is verified
*And* the line has ++SIM type++ pSIM
*But* no ++ICCID++ is on the line
*And* the ++Mavenir customer++ has ++waiting pSIM++ Active

*Given* Mavenir has ++ICCID++ ++valid ICCID++ available in inventory
*But* the ++Mavenir customer++ has no ++waiting pSIM++ characteristic
*When* the Customer activates the SIM with ++ICCID++ ++valid ICCID++
*Then* the pSIM delivered order is rejected

### Scenario: waiting pSIM already completed

### Background

*Given* the Customer is waiting for a Paradise SIM
*And* the Customer is verified
*And* the line has ++SIM type++ pSIM
*But* no ++ICCID++ is on the line
*And* the ++Mavenir customer++ has ++waiting pSIM++ Active

*Given* Mavenir has ++ICCID++ ++valid ICCID++ available in inventory
*And* the ++Mavenir customer++ has ++waiting pSIM++ Cleared
*When* the Customer activates the SIM with ++ICCID++ ++valid ICCID++
*Then* the pSIM delivered order is rejected
