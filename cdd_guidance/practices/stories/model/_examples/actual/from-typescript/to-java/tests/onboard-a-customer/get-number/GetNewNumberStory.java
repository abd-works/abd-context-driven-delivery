// Epic: Get New Number
// Orders: 0.0.1.1

/** Story: Determine Number
 * SCENARIO: View available numbers
 * EXAMPLES: storedHeldAvailableNumber, enteredChosenAvailableNumber, storedAvailableNumbers, customerWithCart
 * GIVEN: a My Paradise customer with a Mavenir shopping cart and no MSISDN
 * WHEN: the Customer loads available numbers
 * THEN: My Paradise sends the list resources request to Mavenir
 * WHEN: Mavenir locks 20 MSISDN resources and returns the available number values
 * THEN: My Paradise returns the available numbers
 * AND: ${storedHeldAvailableNumber} and ${enteredChosenAvailableNumber} are in the Available Number list
 * SCENARIO: View available numbers — MSISDN in cart
 * EXAMPLES: storedHeldAvailableNumber, storedAvailableNumbers, customerWithCart, stubBundle
 * GIVEN: MSISDN ${storedHeldAvailableNumber} is in the Mavenir shopping cart
 * WHEN: the Customer loads available numbers
 * THEN: My Paradise sends the list resources request to Mavenir
 * WHEN: Mavenir locks 20 MSISDN resources and returns the available number values
 * THEN: the Customer sees their number is ${storedHeldAvailableNumber}
 * AND: My Paradise returns the available numbers
 * SCENARIO: Refresh available numbers
 * EXAMPLES: storedAvailableNumbers, customerWithCart
 * GIVEN: a My Paradise customer with a Mavenir shopping cart
 * WHEN: the Customer refreshes the number list
 * THEN: My Paradise sends the list resources request to Mavenir
 * WHEN: Mavenir locks 20 MSISDN resources and returns the available numbers
 * THEN: My Paradise returns a fresh set of available numbers
 * SCENARIO: Search for a number
 * EXAMPLES: customerWithCart
 * GIVEN: a My Paradise customer with a Mavenir shopping cart
 * WHEN: the Customer searches for numbers matching JAMES (52637)
 * THEN: My Paradise sends the search request to Mavenir with pattern 52637
 * WHEN: Mavenir locks MSISDN resources matching 52637 and returns matching values
 * THEN: My Paradise returns Available Numbers matching 52637
 * AND: the matching numbers are stored on the line for selection
 * SCENARIO: Numbers locked by another customer are excluded from results
 * EXAMPLES: storedHeldAvailableNumber, enteredChosenAvailableNumber, customerWithCart
 * GIVEN: another customer has already locked the standard available numbers in Mavenir
 * WHEN: the Customer loads available numbers
 * THEN: My Paradise sends the list resources request to Mavenir
 * WHEN: Mavenir returns only available numbers, excluding the locked ones
 * THEN: the locked numbers are not in the available numbers list
 * AND: only the currently available numbers are returned
 */

/** Story: Choose a Number
 * SCENARIO: Pick number
 * EXAMPLES: enteredChosenAvailableNumber, expectedChosenAvailableNumber, storedAvailableNumbers, customerWithCart, reloadCart, stubBundle
 * GIVEN: Mavenir has locked ${enteredChosenAvailableNumber} in the available numbers list and no MSISDN is in the cart
 * WHEN: My Paradise reserves ${enteredChosenAvailableNumber} in Mavenir and patches the shopping cart
 * THEN: My Paradise sends the reserve request to Mavenir with ${enteredChosenAvailableNumber}
 * AND: My Paradise patches the Mavenir shopping cart with ${enteredChosenAvailableNumber}
 * WHEN: Mavenir confirms the reservation and patches the cart
 * THEN: My Paradise stores ${expectedChosenAvailableNumber} on the line
 * AND: the Customer is forwarded to Select Sim
 * SCENARIO: Pick number — replace existing
 * EXAMPLES: storedHeldAvailableNumber, enteredChosenAvailableNumber, expectedChosenAvailableNumber, storedAvailableNumbers, customerWithCart, reloadCart, stubBundle
 * GIVEN: MSISDN ${storedHeldAvailableNumber} is in the cart and Mavenir has locked ${enteredChosenAvailableNumber} in the available numbers list
 * WHEN: My Paradise reserves ${enteredChosenAvailableNumber} releasing ${storedHeldAvailableNumber}
 * THEN: My Paradise sends the reserve request to Mavenir with ${enteredChosenAvailableNumber} releasing ${storedHeldAvailableNumber}
 * WHEN: Mavenir releases ${storedHeldAvailableNumber} and reserves ${enteredChosenAvailableNumber}
 * THEN: My Paradise stores ${expectedChosenAvailableNumber} on the line
 * SCENARIO: Reserve number request fails
 * EXAMPLES: enteredChosenAvailableNumber, storedAvailableNumbers, customerWithCart
 * GIVEN: Mavenir has locked ${enteredChosenAvailableNumber} in the available numbers list but reserve returns an error
 * WHEN: My Paradise attempts to reserve ${enteredChosenAvailableNumber} but Mavenir returns an error
 * THEN: My Paradise shows Failed to reserve your number.
 * SCENARIO: Patch cart with number fails
 * EXAMPLES: enteredChosenAvailableNumber, storedAvailableNumbers, customerWithCart
 * GIVEN: Mavenir has reserved ${enteredChosenAvailableNumber} but patching the cart returns an error
 * WHEN: My Paradise patches the Mavenir shopping cart with ${enteredChosenAvailableNumber} but Mavenir returns an error
 * THEN: My Paradise shows Failed to update your cart.
 */
