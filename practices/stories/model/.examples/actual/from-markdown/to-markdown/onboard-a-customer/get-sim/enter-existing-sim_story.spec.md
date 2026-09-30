## Story: Enter Existing Sim

### Scenario: Enter existing SIM

### Background

*Given* the Customer is choosing a physical SIM
*And* the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++

*Given* Mavenir has ++ICCID++ ++valid ICCID++ available in inventory
*When* the Customer attaches ++ICCID++ ++valid ICCID++
*Then* My Paradise sends the ICCID inventory request to Mavenir with ++ICCID++ ++valid ICCID++
*And* My Paradise sends the patch cart request to Mavenir with ++SIM type++ pSIM and ++ICCID++ ++valid ICCID++
*When* Mavenir returns the updated ++Mavenir shopping cart++ with ++SIM type++ pSIM and ++ICCID++ ++valid ICCID++
*Then* My Paradise stores pSIM and ++ICCID++ ++valid ICCID++ on the line
*And* the Customer is forwarded to Verify ID

### Scenario: ICCID contains spaces

### Background

*Given* the Customer is choosing a physical SIM
*And* the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++

*Given* the Customer has ++ICCID++ ++ICCID with spaces++
*When* the Customer attaches ++ICCID++ ++ICCID with spaces++
*Then* the ICCID format is rejected
*And* My Paradise does not query inventory or patch the cart

### Scenario: Inventory rejects ICCID

### Background

*Given* the Customer is choosing a physical SIM
*And* the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++

*Given* Mavenir does not have ++ICCID++ ++invalid ICCID++ available in inventory
*When* the Customer attaches ++ICCID++ ++invalid ICCID++
*Then* My Paradise sends the ICCID inventory request to Mavenir with ++ICCID++ ++invalid ICCID++
*And* My Paradise does not patch the cart
*And* the ICCID is rejected
