// Epic: Get New Number
// Orders: 0.0.1.1

/** Story: Determine Number
 * SCENARIO: View available numbers
 * GIVEN: a My Paradise customer with a Mavenir shopping cart and no MSISDN
 * WHEN: the Customer loads available numbers
 * THEN: My Paradise sends the list resources request to Mavenir
 * WHEN: Mavenir locks 20 MSISDN resources and returns the available number values
 * THEN: My Paradise returns the available numbers
 * SCENARIO: View available numbers — MSISDN in cart
 * WHEN: the Customer loads available numbers
 * THEN: My Paradise sends the list resources request to Mavenir
 * WHEN: Mavenir locks 20 MSISDN resources and returns the available number values
 * AND: My Paradise returns the available numbers
 * SCENARIO: Refresh available numbers
 * GIVEN: a My Paradise customer with a Mavenir shopping cart
 * WHEN: the Customer refreshes the number list
 * THEN: My Paradise sends the list resources request to Mavenir
 * WHEN: Mavenir locks 20 MSISDN resources and returns the available numbers
 * THEN: My Paradise returns a fresh set of available numbers
 * SCENARIO: Search for a number
 * GIVEN: a My Paradise customer with a Mavenir shopping cart
 * WHEN: the Customer searches for numbers matching JAMES (52637)
 * THEN: My Paradise sends the search request to Mavenir with pattern 52637
 * WHEN: Mavenir locks MSISDN resources matching 52637 and returns matching values
 * THEN: My Paradise returns Available Numbers matching 52637
 * AND: the matching numbers are stored on the line for selection
 * SCENARIO: Numbers locked by another customer are excluded from results
 * GIVEN: another customer has already locked the standard available numbers in Mavenir
 * WHEN: the Customer loads available numbers
 * THEN: My Paradise sends the list resources request to Mavenir
 * WHEN: Mavenir returns only available numbers, excluding the locked ones
 * THEN: the locked numbers are not in the available numbers list
 * AND: only the currently available numbers are returned
 */

/** Story: Choose a Number
 * SCENARIO: Pick number
 * WHEN: Mavenir confirms the reservation and patches the cart
 * AND: the Customer is forwarded to Select Sim
 * SCENARIO: Pick number — replace existing
 * SCENARIO: Reserve number request fails
 * THEN: My Paradise shows Failed to reserve your number.
 * SCENARIO: Patch cart with number fails
 * THEN: My Paradise shows Failed to update your cart.
 */
