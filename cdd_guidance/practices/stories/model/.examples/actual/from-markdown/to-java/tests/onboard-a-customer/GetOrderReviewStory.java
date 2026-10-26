// Epic: Get Order Review
// Orders: 0.0.6

/** Story: Check The Order
 * Actor: Customer
 * SCENARIO: Check the order
 * background: background
 * background-step: Given | the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
 * background-step: And | ++available number++ ++chosen available number++ is in the ++Mavenir shopping cart++
 * background-step: And | the Customer has chosen eSIM
 * GIVEN: the Customer has completed account setup, number, SIM, and profile
 * WHEN: the Customer proceeds to reviewing their order
 * THEN: the Customer is forwarded to Checkout
 * AND: the Checkout step is the next onboarding step
 * SCENARIO: Check the order with port-in number
 * background: background
 * background-step: Given | the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
 * background-step: And | ++available number++ ++chosen available number++ is in the ++Mavenir shopping cart++
 * background-step: And | the Customer has chosen eSIM
 * GIVEN: the Customer has a port-in number with +1 (441) 123-4567 as port number and +1 (441) 555-0101 as temporary MSISDN
 * WHEN: the Customer proceeds to reviewing their order
 * THEN: the Customer is forwarded to Checkout
 * AND: the Checkout step is the next onboarding step
 */

/** Story: Upgrade To Data Freedom
 * Actor: Customer
 * background-examples: {"upgrade to Data Freedom": {"plan upgrade": "plan upgrade", "example": "upgrade to Data Freedom", "currentPlan": "Essentials", "newPlan": "Data Freedom"}, "upgrade to Ace": {"plan upgrade": "plan upgrade", "example": "upgrade to Ace", "currentPlan": "Data Freedom", "newPlan": "Ace"}, "upgrade to Atlas": {"plan upgrade": "plan upgrade", "example": "upgrade to Atlas", "currentPlan": "Ace", "newPlan": "Atlas"}}
 * BACKGROUND: background
 * SCENARIO: Upgrade plan from review
 * background: background
 * background-step: Given | the Customer is reviewing their order
 * background-step: And | the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++
 * GIVEN: ++plan++ ++{currentPlan}++ is in the ++Mavenir shopping cart++
 * WHEN: My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++{newPlan}++
 * THEN: My Paradise sends the patch cart request to Mavenir with ++plan++ ++{newPlan}++ bundleId
 * WHEN: Mavenir returns the updated ++Mavenir shopping cart++ with ++plan++ ++{newPlan}++
 * THEN: My Paradise stores ++plan++ ++{newPlan}++ as the cart bundle
 * AND: the Customer sees *You have been upgraded!*
 * SCENARIO: No upsell shown on top-tier plan
 * background: background
 * background-step: Given | the Customer is reviewing their order
 * background-step: And | the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++
 * GIVEN: ++plan++ ++Atlas++ is in the ++Mavenir shopping cart++
 * WHEN: the Customer proceeds to reviewing their order
 * THEN: no upgrade option is available
 */

/** Story: Change Plan From Review
 * Actor: Customer
 * SCENARIO: Select a different plan from review
 * background: background
 * background-step: Given | the Customer is reviewing their order
 * background-step: And | the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
 * GIVEN: the Customer has opened plan selection from review
 * WHEN: My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++
 * THEN: My Paradise sends the patch cart request to Mavenir with ++plan++ ++Data Freedom++ bundleId
 * WHEN: Mavenir returns the updated ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++
 * THEN: My Paradise stores ++plan++ ++Data Freedom++ as the cart bundle
 * AND: the Customer is forwarded to Checkout
 * SCENARIO: Keep current plan from review
 * background: background
 * background-step: Given | the Customer is reviewing their order
 * background-step: And | the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
 * GIVEN: the Customer has opened plan selection from review
 * WHEN: the Customer keeps their current plan
 * THEN: the Customer is forwarded to Checkout
 * SCENARIO: Select the plan already in the cart from review
 * background: background
 * background-step: Given | the Customer is reviewing their order
 * background-step: And | the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
 * GIVEN: the Customer has opened plan selection from review
 * WHEN: My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++Essentials++
 * THEN: the cart bundle remains ++plan++ ++Essentials++
 * SCENARIO: Plan update fails from review
 * background: background
 * background-step: Given | the Customer is reviewing their order
 * background-step: And | the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
 * GIVEN: the Customer has opened plan selection from review
 * AND: Mavenir returns an error on cart patch
 * WHEN: My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++
 * THEN: My Paradise shows *Failed to update new plan choice.*
 * AND: the cart bundle remains ++plan++ ++Essentials++
 */
