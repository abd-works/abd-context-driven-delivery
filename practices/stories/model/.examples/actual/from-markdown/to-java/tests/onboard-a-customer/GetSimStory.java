// Epic: Get Sim
// Orders: 0.0.4

/** Story: Choose Esim
 * Actor: Customer
 * SCENARIO: Choose eSIM
 * background: background
 * background-step: Given | eSIM is available
 * background-step: And | the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++
 * background-step: And | the phone supports eSIM
 * GIVEN: no ++SIM type++ is on the line
 * WHEN: the Customer selects eSIM
 * THEN: My Paradise sends the patch cart request to Mavenir with ++SIM type++ eSIM
 * WHEN: Mavenir returns the updated ++Mavenir shopping cart++ with ++SIM type++ eSIM
 * THEN: My Paradise stores eSIM on the line
 * AND: the Customer is forwarded to Verify ID
 * SCENARIO: Choose eSIM — already on the line
 * background: background
 * background-step: Given | eSIM is available
 * background-step: And | the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++
 * background-step: And | the phone supports eSIM
 * GIVEN: the line already has ++SIM type++ eSIM
 * WHEN: the Customer selects eSIM
 * THEN: My Paradise skips the cart patch
 * SCENARIO: Choose eSIM — cart patch fails
 * background: background
 * background-step: Given | eSIM is available
 * background-step: And | the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++
 * background-step: And | the phone supports eSIM
 * GIVEN: Mavenir returns an error on cart patch
 * WHEN: the Customer selects eSIM
 * THEN: the SIM selection fails
 * AND: the line has no ++SIM type++
 */

/** Story: Request a Paradise Sim Card
 * Actor: Customer
 * SCENARIO: Request a Paradise SIM card
 * background: background
 * background-step: Given | the Customer is choosing a physical SIM
 * background-step: And | the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++
 * GIVEN: no ++SIM type++ is on the line
 * AND: no ++ICCID++ is on the line
 * WHEN: the Customer requests a Paradise SIM card
 * THEN: My Paradise sends the patch cart request to Mavenir with ++SIM type++ pSIM
 * WHEN: Mavenir returns the updated ++Mavenir shopping cart++ with ++SIM type++ pSIM
 * THEN: My Paradise stores pSIM on the line
 * BUT: the line has no ++ICCID++
 * AND: the Customer is forwarded to Verify ID
 * SCENARIO: Request a Paradise SIM card — already on the line
 * background: background
 * background-step: Given | the Customer is choosing a physical SIM
 * background-step: And | the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++
 * GIVEN: the line already has ++SIM type++ pSIM
 * WHEN: the Customer requests a Paradise SIM card
 * THEN: My Paradise skips the cart patch
 * SCENARIO: Request a Paradise SIM card — cart patch fails
 * background: background
 * background-step: Given | the Customer is choosing a physical SIM
 * background-step: And | the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++
 * GIVEN: Mavenir returns an error on cart patch
 * WHEN: the Customer requests a Paradise SIM card
 * THEN: the SIM selection fails
 * AND: the line has no ++SIM type++
 */

/** Story: Enter Existing Sim
 * Actor: Customer
 * SCENARIO: Enter existing SIM
 * background: background
 * background-step: Given | the Customer is choosing a physical SIM
 * background-step: And | the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++
 * GIVEN: Mavenir has ++ICCID++ ++valid ICCID++ available in inventory
 * WHEN: the Customer attaches ++ICCID++ ++valid ICCID++
 * THEN: My Paradise sends the ICCID inventory request to Mavenir with ++ICCID++ ++valid ICCID++
 * AND: My Paradise sends the patch cart request to Mavenir with ++SIM type++ pSIM and ++ICCID++ ++valid ICCID++
 * WHEN: Mavenir returns the updated ++Mavenir shopping cart++ with ++SIM type++ pSIM and ++ICCID++ ++valid ICCID++
 * THEN: My Paradise stores pSIM and ++ICCID++ ++valid ICCID++ on the line
 * AND: the Customer is forwarded to Verify ID
 * SCENARIO: ICCID contains spaces
 * background: background
 * background-step: Given | the Customer is choosing a physical SIM
 * background-step: And | the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++
 * GIVEN: the Customer has ++ICCID++ ++ICCID with spaces++
 * WHEN: the Customer attaches ++ICCID++ ++ICCID with spaces++
 * THEN: the ICCID format is rejected
 * AND: My Paradise does not query inventory or patch the cart
 * SCENARIO: Inventory rejects ICCID
 * background: background
 * background-step: Given | the Customer is choosing a physical SIM
 * background-step: And | the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++
 * GIVEN: Mavenir does not have ++ICCID++ ++invalid ICCID++ available in inventory
 * WHEN: the Customer attaches ++ICCID++ ++invalid ICCID++
 * THEN: My Paradise sends the ICCID inventory request to Mavenir with ++ICCID++ ++invalid ICCID++
 * AND: My Paradise does not patch the cart
 * AND: the ICCID is rejected
 */

/** Story: Activate Sim
 * Actor: Customer
 * SCENARIO: Activate Sim
 * background: background
 * background-step: Given | the Customer is waiting for a Paradise SIM
 * background-step: And | the Customer is verified
 * background-step: And | the line has ++SIM type++ pSIM
 * background-step: But | no ++ICCID++ is on the line
 * background-step: And | the ++Mavenir customer++ has ++waiting pSIM++ Active
 * GIVEN: Mavenir has ++ICCID++ ++valid ICCID++ available in inventory
 * WHEN: the Customer activates the SIM with ++ICCID++ ++valid ICCID++
 * THEN: My Paradise sends the ICCID inventory request to Mavenir with ++ICCID++ ++valid ICCID++
 * AND: My Paradise sends the patch cart request to Mavenir with ++SIM type++ pSIM and ++ICCID++ ++valid ICCID++
 * AND: My Paradise sends the pSIM delivered order to Mavenir
 * WHEN: Mavenir creates the product order and clears ++waiting pSIM++
 * THEN: My Paradise stores ++ICCID++ ++valid ICCID++ on the line
 * SCENARIO: waiting pSIM is absent
 * background: background
 * background-step: Given | the Customer is waiting for a Paradise SIM
 * background-step: And | the Customer is verified
 * background-step: And | the line has ++SIM type++ pSIM
 * background-step: But | no ++ICCID++ is on the line
 * background-step: And | the ++Mavenir customer++ has ++waiting pSIM++ Active
 * GIVEN: Mavenir has ++ICCID++ ++valid ICCID++ available in inventory
 * BUT: the ++Mavenir customer++ has no ++waiting pSIM++ characteristic
 * WHEN: the Customer activates the SIM with ++ICCID++ ++valid ICCID++
 * THEN: the pSIM delivered order is rejected
 * SCENARIO: waiting pSIM already completed
 * background: background
 * background-step: Given | the Customer is waiting for a Paradise SIM
 * background-step: And | the Customer is verified
 * background-step: And | the line has ++SIM type++ pSIM
 * background-step: But | no ++ICCID++ is on the line
 * background-step: And | the ++Mavenir customer++ has ++waiting pSIM++ Active
 * GIVEN: Mavenir has ++ICCID++ ++valid ICCID++ available in inventory
 * AND: the ++Mavenir customer++ has ++waiting pSIM++ Cleared
 * WHEN: the Customer activates the SIM with ++ICCID++ ++valid ICCID++
 * THEN: the pSIM delivered order is rejected
 */

/** Story: Complete Draft Sim Order
 * SCENARIO: Complete Draft Sim Order
 * background: background
 * background-step: Given | a Customer completed the My Paradise onboarding flow
 * background-step: And | the Customer's line has ++SIM type++ pSIM
 * background-step: But | the Customer never entered an ++ICCID++
 * background-step: And | the ++Mavenir customer++ has ++waiting pSIM++ Active
 * GIVEN: Care opens the ++Mavenir customer++ record in Mavenir DEP
 * AND: Care sees the draft order in the orders grid (`22-dep-orders-grid.png`)
 * WHEN: Care attaches the ++ICCID++ to the draft order and completes it
 * THEN: the order status in DEP Order History changes from draft to active (`23-dep-order-history.png`)
 * AND: the ++waiting pSIM++ characteristic on the ++Mavenir customer++ is cleared
 */
