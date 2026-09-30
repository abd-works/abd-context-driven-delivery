// Epic: Get Number
// Orders: 0.0.2

/** Story: Determine Number
 * Actor: Customer
 * background-examples: {"held available number": {"available number": "available number", "example": "held available number", "number": "4415550100", "group": "available number"}, "chosen available number": {"available number": "available number", "example": "chosen available number", "number": "4415550101", "group": "available number"}, "James search": {"search term": "search term", "example": "James search", "input": "JAMES", "converted": "52637", "group": "search term"}}
 * BACKGROUND: background
 * SCENARIO: View available numbers
 * background: background
 * background-step: Given | the Prospect is in Account Setup
 * background-step: And | a ++My Paradise customer++ with a ++Mavenir shopping cart++
 * BUT: no ++MSISDN++ is in the ++Mavenir shopping cart++
 * WHEN: the Prospect proceeds to selecting their number
 * THEN: My Paradise loads ++available number++ inventory through the Midtier
 * AND: the Prospect sees ++available number++ ++held available number++ and ++available number++ ++chosen available number++ in the Available Number list
 * AND: the Prospect can Bring your mobile number
 * AND: the Prospect can search for numbers (up to 5 characters: letters or numbers)
 * AND: the Prospect can Refresh
 * AND: the Continue operation is disabled
 * WHEN: the Prospect selects ++available number++ ++chosen available number++
 * THEN: the Continue operation is enabled
 * SCENARIO: View available numbers — MSISDN in cart
 * background: background
 * background-step: Given | the Prospect is in Account Setup
 * background-step: And | a ++My Paradise customer++ with a ++Mavenir shopping cart++
 * GIVEN: ++MSISDN++ ++available number++ ++held available number++ is in the ++Mavenir shopping cart++
 * WHEN: the Prospect proceeds to selecting their number
 * THEN: the Prospect sees their number is ++available number++ ++held available number++
 * AND: the Pick new number operation is disabled
 * AND: the Keep current number operation is enabled
 * WHEN: the Prospect selects ++available number++ ++chosen available number++
 * THEN: the Pick new number operation is enabled
 * SCENARIO: Refresh available numbers
 * background: background
 * background-step: Given | the Prospect is in Account Setup
 * background-step: And | a ++My Paradise customer++ with a ++Mavenir shopping cart++
 * WHEN: the Prospect clicks Refresh
 * THEN: My Paradise loads a fresh set of ++available number++ through the Midtier
 * AND: the Prospect sees a new Available Number list
 * AND: the Continue operation is disabled
 * SCENARIO: Search for a number
 * background: background
 * background-step: Given | the Prospect is in Account Setup
 * background-step: And | a ++My Paradise customer++ with a ++Mavenir shopping cart++
 * WHEN: the Prospect enters ++search term++ ++James search++ in the search field
 * THEN: the search field helper shows *Your number: JAMES (52637)*
 * WHEN: the Prospect triggers the search
 * THEN: My Paradise loads Available Numbers matching ++search term++ ++James search++ through the Midtier
 */

/** Story: Query Msisdn Inventory
 * SCENARIO: Query MSISDN inventory for porting
 * GIVEN: a ++PML customer++ is authenticated in Midtier
 * AND: ++portability++ is in the portability request
 * WHEN: Midtier queries ++MSISDN++ inventory for a temporary port-in number (`count: 1`)
 * THEN: Midtier queries Mavenir for 1 available ++MSISDN++ resource
 * AND: Midtier receives ++available number++ ++held available number++ as the temporary number
 * SCENARIO: Query MSISDN inventory
 * GIVEN: a ++PML customer++ is authenticated in Midtier
 * WHEN: Midtier is asked to query ++MSISDN++ inventory
 * THEN: Midtier queries Mavenir for 5 available ++MSISDN++ resources
 * AND: Midtier returns a list of ++available number++ values to My Paradise
 */

/** Story: List Msisdn Resources
 * SCENARIO: List MSISDN resources for porting
 * GIVEN: ++MSISDN++ resources with available status are in the Mavenir inventory
 * WHEN: Mavenir is asked to list 1 ++MSISDN++ resource (`/updateAndGetAvailableResources`, `size: 1`)
 * THEN: Mavenir transitions 1 ++MSISDN++ resource from available to locked
 * AND: Mavenir returns ++available number++ ++held available number++ as the locked resource to Midtier
 * SCENARIO: List MSISDN resources
 * GIVEN: ++MSISDN++ resources with available status are in the Mavenir inventory
 * WHEN: Mavenir is asked to list ++MSISDN++ resources (`/updateAndGetAvailableResources`, `size: 5`)
 * THEN: Mavenir transitions 5 ++MSISDN++ resources from available to locked
 * AND: Mavenir returns the list of locked ++available number++ values to Midtier
 */

/** Story: Search Msisdn Inventory
 * SCENARIO: Search MSISDN inventory
 * GIVEN: a ++PML customer++ is authenticated in Midtier
 * WHEN: Midtier is asked to search ++MSISDN++ inventory for ++search term++ ++James search++ (`52637`)
 * THEN: Midtier queries Mavenir for available ++MSISDN++ resources matching `52637`
 * AND: Midtier returns matching ++available number++ values to My Paradise
 */

/** Story: Search Msisdn Resources
 * SCENARIO: Search MSISDN resources by pattern
 * GIVEN: ++MSISDN++ resources with available status are in the Mavenir inventory
 * WHEN: Mavenir is asked to search ++MSISDN++ resources with `pattern_search: 52637` (`/updateAndGetAvailableResources`)
 * THEN: Mavenir transitions matching ++MSISDN++ resources from available to locked
 * AND: Mavenir returns the matching ++available number++ values to Midtier
 */

/** Story: Choose a Number
 * Actor: Customer
 * SCENARIO: Pick new number
 * background: background
 * background-step: Given | the Prospect is in Account Setup
 * background-step: And | a ++My Paradise customer++ with a ++Mavenir shopping cart++
 * GIVEN: the Prospect has selected ++available number++ ++chosen available number++
 * BUT: no ++MSISDN++ is in the ++Mavenir shopping cart++
 * WHEN: the Prospect clicks Continue
 * THEN: My Paradise reserves ++available number++ ++chosen available number++ through the Midtier
 * AND: My Paradise patches the ++Mavenir shopping cart++ with ++available number++ ++chosen available number++ through the Midtier
 * AND: the Prospect is forwarded to Select Sim
 * SCENARIO: Pick new number — replace existing
 * background: background
 * background-step: Given | the Prospect is in Account Setup
 * background-step: And | a ++My Paradise customer++ with a ++Mavenir shopping cart++
 * GIVEN: ++MSISDN++ ++available number++ ++held available number++ is in the ++Mavenir shopping cart++
 * AND: the Prospect has selected ++available number++ ++chosen available number++
 * WHEN: the Prospect clicks Pick new number
 * THEN: My Paradise reserves ++available number++ ++chosen available number++ releasing ++available number++ ++held available number++ through the Midtier
 * AND: My Paradise patches the ++Mavenir shopping cart++ with ++available number++ ++chosen available number++ through the Midtier
 * AND: the Prospect is forwarded to Select Sim
 * SCENARIO: Keep current number
 * background: background
 * background-step: Given | the Prospect is in Account Setup
 * background-step: And | a ++My Paradise customer++ with a ++Mavenir shopping cart++
 * GIVEN: ++MSISDN++ ++available number++ ++held available number++ is in the ++Mavenir shopping cart++
 * WHEN: the Prospect clicks Keep current number
 * THEN: the Prospect is forwarded to Select Sim
 */

/** Story: Submit Reserve Number Request to Mid-Tier
 * SCENARIO: Reserve number
 * background: background
 * background-step: Given | the Prospect is in Account Setup
 * background-step: And | a ++My Paradise customer++ with a ++Mavenir shopping cart++
 * GIVEN: ++available number++ ++chosen available number++ is selected
 * BUT: no ++MSISDN++ is in the ++Mavenir shopping cart++
 * WHEN: My Paradise posts a reserve request to Midtier for ++available number++ ++chosen available number++
 * THEN: Midtier returns 204
 * AND: My Paradise submits a patch cart request with ++available number++ ++chosen available number++ through the Midtier
 * SCENARIO: Reserve number — replace existing
 * background: background
 * background-step: Given | the Prospect is in Account Setup
 * background-step: And | a ++My Paradise customer++ with a ++Mavenir shopping cart++
 * GIVEN: ++MSISDN++ ++available number++ ++held available number++ is in the ++Mavenir shopping cart++
 * AND: ++available number++ ++chosen available number++ is selected
 * WHEN: My Paradise posts a reserve request to Midtier for ++available number++ ++chosen available number++ with previous ++available number++ ++held available number++
 * THEN: Midtier returns 204
 * AND: My Paradise submits a patch cart request with ++available number++ ++chosen available number++ through the Midtier
 * SCENARIO: Reserve number request fails
 * background: background
 * background-step: Given | the Prospect is in Account Setup
 * background-step: And | a ++My Paradise customer++ with a ++Mavenir shopping cart++
 * GIVEN: ++available number++ ++chosen available number++ is selected
 * WHEN: My Paradise posts a reserve request to Midtier for ++available number++ ++chosen available number++
 * BUT: Midtier returns an error
 * THEN: My Paradise shows *Failed to reserve your number.*
 */

/** Story: Submit Reserve Msisdn
 * SCENARIO: Reserve temporary MSISDN for porting
 * GIVEN: ++MSISDN++ ++available number++ ++held available number++ is locked
 * WHEN: Midtier reserves ++available number++ ++held available number++ as a port-in temporary number (`portin: true`)
 * THEN: Midtier reserves ++available number++ ++held available number++ in Mavenir with the port-in flag
 * AND: Midtier returns 204
 * SCENARIO: Reserve MSISDN
 * GIVEN: ++MSISDN++ ++available number++ ++chosen available number++ is locked in Mavenir inventory
 * WHEN: Midtier is asked to reserve ++MSISDN++ ++available number++ ++chosen available number++
 * THEN: Midtier reserves ++available number++ ++chosen available number++ in Mavenir
 * AND: Midtier returns 204 to My Paradise
 * SCENARIO: Reserve MSISDN — release previous
 * GIVEN: ++MSISDN++ ++available number++ ++chosen available number++ is locked
 * AND: ++MSISDN++ ++available number++ ++held available number++ is reserved
 * WHEN: Midtier is asked to reserve ++available number++ ++chosen available number++ releasing previous ++available number++ ++held available number++
 * THEN: Midtier reserves ++available number++ ++chosen available number++ and releases ++available number++ ++held available number++ in Mavenir
 * AND: Midtier returns 204 to My Paradise
 */

/** Story: Reserve Msisdn Resource
 * SCENARIO: Reserve MSISDN resource as temporary port-in number
 * GIVEN: ++MSISDN++ ++available number++ ++held available number++ is locked in Mavenir inventory
 * WHEN: Mavenir is asked to reserve ++available number++ ++held available number++ with `kv_tempNumber: true` (`/updateResources`, locked → reserved, relatedParty: Paradise Mobile)
 * THEN: Mavenir transitions ++available number++ ++held available number++ from locked to reserved
 * AND: Mavenir marks ++available number++ ++held available number++ as a temporary port-in number (`kv_tempNumber`)
 * SCENARIO: Reserve MSISDN resource
 * GIVEN: ++MSISDN++ ++available number++ ++chosen available number++ is locked in Mavenir inventory
 * WHEN: Mavenir is asked to reserve ++available number++ ++chosen available number++ (`/updateResources`, locked → reserved, relatedParty: Paradise Mobile)
 * THEN: Mavenir transitions ++available number++ ++chosen available number++ from locked to reserved
 * AND: Mavenir attaches the Paradise Mobile service provider to ++available number++ ++chosen available number++
 * SCENARIO: Reserve MSISDN resource — release previous
 * GIVEN: ++MSISDN++ ++available number++ ++chosen available number++ is locked
 * AND: ++MSISDN++ ++available number++ ++held available number++ is reserved
 * WHEN: Mavenir is asked to reserve ++available number++ ++chosen available number++ and release previous ++available number++ ++held available number++
 * THEN: Mavenir transitions ++available number++ ++chosen available number++ from locked to reserved
 * AND: Mavenir transitions ++available number++ ++held available number++ from reserved to available
 */

/** Story: Submit Patch Cart With Number Request to Mid-Tier
 * SCENARIO: Patch cart with number
 * GIVEN: ++MSISDN++ ++available number++ ++chosen available number++ has been reserved
 * WHEN: My Paradise patches the ++Mavenir shopping cart++ with ++available number++ ++chosen available number++ through the Midtier
 * THEN: Midtier returns the updated ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++
 * AND: the Prospect is forwarded to Select Sim
 * SCENARIO: Patch cart with number fails
 * GIVEN: ++MSISDN++ ++available number++ ++chosen available number++ has been reserved
 * WHEN: My Paradise patches the ++Mavenir shopping cart++ with ++available number++ ++chosen available number++ through the Midtier
 * BUT: Midtier returns an error
 * THEN: My Paradise shows *Failed to update your cart.*
 */

/** Story: Patch Cart With Number
 * SCENARIO: Patch cart with MSISDN
 * GIVEN: a ++PML customer++ with a ++Mavenir shopping cart++
 * AND: ++MSISDN++ ++available number++ ++chosen available number++ has been reserved
 * WHEN: Midtier is asked to patch the ++Mavenir shopping cart++ with ++MSISDN++ ++available number++ ++chosen available number++
 * THEN: Midtier patches the ++Mavenir shopping cart++ in Mavenir with ++available number++ ++chosen available number++ as the MSISDN characteristic
 * AND: Midtier returns the updated ++PML customer++ to My Paradise
 */

/** Story: Patch Shopping Cart
 * SCENARIO: Patch shopping cart with portability
 * GIVEN: a ++Mavenir shopping cart++ with a plan bundle cart item and temporary ++MSISDN++ ++available number++ ++held available number++
 * WHEN: Mavenir is asked to patch the ++Mavenir shopping cart++ with ++portability++ ++valid portability++ characteristics
 * THEN: Mavenir updates the ++Mavenir shopping cart++ cart item with portability characteristics (planName, portinNumber, donorOperator, accountType, userType, accountNumber, device, portin, requestType)
 * AND: Mavenir returns the updated ++Mavenir shopping cart++ to Midtier
 * SCENARIO: Patch shopping cart with MSISDN
 * GIVEN: a ++Mavenir shopping cart++ with a plan bundle cart item
 * BUT: no MSISDN characteristic on the cart item
 * WHEN: Mavenir is asked to patch the ++Mavenir shopping cart++ with ++MSISDN++ ++available number++ ++chosen available number++ as a cart item characteristic
 * THEN: Mavenir updates the ++Mavenir shopping cart++ cart item with ++available number++ ++chosen available number++ as the MSISDN characteristic
 * AND: Mavenir returns the updated ++Mavenir shopping cart++ to Midtier
 * SCENARIO: Patch Shopping Cart
 * GIVEN: a ++Mavenir customer++ with a ++Mavenir shopping cart++ (no bundle) in Mavenir
 * WHEN: Mavenir is asked to patch the ++Mavenir shopping cart++ with a bundle cart item for ++plan++ ++Essentials++
 * THEN: Mavenir updates the ++Mavenir shopping cart++ with the ++plan++ ++Essentials++ bundle product item
 * AND: returns the patched ++Mavenir shopping cart++ to Patch Cart With Plan
 */

/** Story: Bring a Number
 * background-examples: {"valid portability": {"portability": "portability", "example": "valid portability", "donorOperator": "Digicel", "portNumber": "4412345678", "accountNumber": "12345", "userType": "Residential", "accountType": "Postpaid", "device": "Iphone", "group": "portability"}}
 * BACKGROUND: background
 * SCENARIO: Bring a number
 * background: background
 * background-step: Given | the Prospect is in Account Setup
 * background-step: And | a ++My Paradise customer++ with a ++Mavenir shopping cart++
 * BUT: no Transfer Code is on Bring your mobile number
 * WHEN: the Prospect clicks Get started on Bring your mobile number
 * THEN: the Prospect can enter ++portability++
 * AND: the Prospect can confirm the information is accurate
 * AND: the Prospect can grant permission to Paradise Mobile to bring the number
 * AND: the Continue operation is disabled
 * AND: the Prospect can go Back
 * WHEN: the Prospect enters ++portability++ ++valid portability++ and checks both permissions
 * THEN: the Continue operation is enabled
 * WHEN: the Prospect clicks Continue
 * THEN: My Paradise submits ++portability++ ++valid portability++ to the Midtier
 * AND: Midtier returns a temporary ++MSISDN++ ++available number++ ++held available number++
 * AND: the Prospect is forwarded to Select Sim
 * SCENARIO: Number to be ported is incomplete
 * background: background
 * background-step: Given | the Prospect is in Account Setup
 * background-step: And | a ++My Paradise customer++ with a ++Mavenir shopping cart++
 * WHEN: the Prospect leaves Number to be ported as the Bermuda prefix only
 * THEN: Number to be ported shows *Please enter the full Bermuda number.*
 * AND: the Continue operation stays disabled
 * SCENARIO: Provider not selected
 * background: background
 * background-step: Given | the Prospect is in Account Setup
 * background-step: And | a ++My Paradise customer++ with a ++Mavenir shopping cart++
 * WHEN: the Prospect blurs Your current provider without selecting a provider
 * THEN: Your current provider shows *Please select a provider.*
 * AND: the Continue operation stays disabled
 */

/** Story: Confirm Number Already With Paradise
 * SCENARIO: Confirm the number is not already with Paradise
 * background: background
 * background-step: Given | the Prospect is in Account Setup
 * background-step: And | a ++My Paradise customer++ with a ++Mavenir shopping cart++
 * background-step: And | the Prospect has entered ++portability++ ++valid portability++
 * background-step: But | no ++portability++ is in the ++Mavenir shopping cart++
 * WHEN: the Prospect proceeds to confirming whether their number is already with Paradise
 * THEN: the Prospect can confirm whether the ++MSISDN++ is already with Paradise
 * WHEN: the Prospect confirms the ++MSISDN++ is not already with Paradise
 * THEN: My Paradise submits ++portability++ ++valid portability++ to the Midtier
 * AND: the Prospect is forwarded to Select Sim
 * SCENARIO: Confirm the number is already with Paradise
 * background: background
 * background-step: Given | the Prospect is in Account Setup
 * background-step: And | a ++My Paradise customer++ with a ++Mavenir shopping cart++
 * background-step: And | the Prospect has entered ++portability++ ++valid portability++
 * background-step: But | no ++portability++ is in the ++Mavenir shopping cart++
 * WHEN: the Prospect proceeds to confirming whether their number is already with Paradise
 * THEN: the Prospect can confirm whether the ++MSISDN++ is already with Paradise
 * WHEN: the Prospect confirms the ++MSISDN++ is already with Paradise
 * THEN: ++portability++ is not submitted to the Midtier
 * AND: the Prospect is returned to selecting their number
 */

/** Story: Evaluate Porting Two Factor Flag
 * SCENARIO: Porting two factor flag enabled (Intended)
 * GIVEN: `porting-2fa` is enabled in GrowthBook
 * AND: the Prospect is in Account Setup
 * WHEN: GrowthBook evaluates the `porting-2fa` flag
 * THEN: My Paradise mounts the SMS verification step in the porting wizard
 * AND: My Paradise starts the porting wizard at the SMS verification step when ++portability++ on the ++Mavenir shopping cart++ is unverified
 * SCENARIO: Porting two factor flag disabled (live)
 * GIVEN: `porting-2fa` is disabled in GrowthBook
 * AND: the Prospect is in Account Setup
 * WHEN: GrowthBook evaluates the `porting-2fa` flag
 * THEN: My Paradise omits the SMS verification step from the porting wizard
 */

/** Story: Submit Portability Request to Mid-Tier
 * SCENARIO: Submit portability request — porting-2fa off (live)
 * background: background
 * background-step: Given | the Prospect is in Account Setup
 * background-step: And | a ++My Paradise customer++ with a ++Mavenir shopping cart++
 * background-step: But | no ++portability++ is in the ++Mavenir shopping cart++
 * GIVEN: the Prospect has entered ++portability++ ++valid portability++
 * WHEN: My Paradise posts a portability request to Midtier with ++portability++ ++valid portability++
 * THEN: Midtier returns a temporary ++MSISDN++ ++available number++ ++held available number++
 * AND: My Paradise stores ++portability++ ++valid portability++ and ++available number++ ++held available number++ in the ++Mavenir shopping cart++
 * AND: the Prospect is forwarded to Select Sim
 * SCENARIO: Submit portability request — porting-2fa on, SMS sent (Intended)
 * background: background
 * background-step: Given | the Prospect is in Account Setup
 * background-step: And | a ++My Paradise customer++ with a ++Mavenir shopping cart++
 * background-step: But | no ++portability++ is in the ++Mavenir shopping cart++
 * GIVEN: the Prospect has entered ++portability++ ++valid portability++
 * AND: `porting-2fa` is enabled
 * WHEN: My Paradise posts a portability request to Midtier with ++portability++ ++valid portability++
 * THEN: Midtier returns `{ status: sent, temporaryNumber: ++available number++ ++held available number++ }`
 * AND: My Paradise stores ++portability++ ++valid portability++ and ++available number++ ++held available number++ in the ++Mavenir shopping cart++
 * AND: My Paradise presents the Confirm your number for porting step
 * SCENARIO: Submit portability request — rate limited, bypass (Intended)
 * background: background
 * background-step: Given | the Prospect is in Account Setup
 * background-step: And | a ++My Paradise customer++ with a ++Mavenir shopping cart++
 * background-step: But | no ++portability++ is in the ++Mavenir shopping cart++
 * GIVEN: `porting-2fa` is enabled
 * WHEN: My Paradise posts a ++portability request++
 * BUT: Midtier returns `{ status: rate_limited, canBypass: true, temporaryNumber: ++available number++ ++held available number++ }`
 * THEN: My Paradise stores ++portability++ ++valid portability++ and ++available number++ ++held available number++ with `verified: true` in the ++Mavenir shopping cart++
 * AND: the Prospect is forwarded to Select Sim
 * SCENARIO: Submit portability request — invalid number (Intended)
 * background: background
 * background-step: Given | the Prospect is in Account Setup
 * background-step: And | a ++My Paradise customer++ with a ++Mavenir shopping cart++
 * background-step: But | no ++portability++ is in the ++Mavenir shopping cart++
 * GIVEN: `porting-2fa` is enabled
 * WHEN: My Paradise posts a ++portability request++
 * BUT: Midtier returns `{ status: invalid_number }`
 * THEN: My Paradise shows *This number is invalid.* on Number to be ported
 * SCENARIO: Submit portability request fails
 * background: background
 * background-step: Given | the Prospect is in Account Setup
 * background-step: And | a ++My Paradise customer++ with a ++Mavenir shopping cart++
 * background-step: But | no ++portability++ is in the ++Mavenir shopping cart++
 * WHEN: My Paradise posts a ++portability request++
 * BUT: Midtier returns an error
 * THEN: My Paradise shows *Failed to save your portability.*
 */

/** Story: Patch Cart With Portability
 * SCENARIO: Patch cart with portability
 * GIVEN: a ++PML customer++ with a ++Mavenir shopping cart++
 * AND: ++MSISDN++ ++available number++ ++held available number++ has been reserved as the temporary port-in number
 * AND: ++portability++ ++valid portability++ is in the request
 * WHEN: Midtier patches the ++Mavenir shopping cart++ with ++portability++ ++valid portability++ and ++available number++ ++held available number++
 * THEN: Midtier patches the ++Mavenir shopping cart++ in Mavenir with portability characteristics (planName, portinNumber, donorOperator, accountType, userType, accountNumber, device)
 * AND: Midtier returns the updated ++PML customer++ with ++portability++ in the ++Mavenir shopping cart++
 */

/** Story: Send Port Verification
 * SCENARIO: Send port verification SMS
 * GIVEN: `porting-2fa` is enabled
 * AND: ++portability++ ++valid portability++ is in the ++Mavenir shopping cart++
 * WHEN: Midtier sends port verification to ++portability++ ++valid portability++ portNumber
 * THEN: Midtier initiates a Twilio SMS verification to ++portability++ ++valid portability++ portNumber
 * AND: Midtier returns `{ status: sent, temporaryNumber: ++available number++ ++held available number++ }` to My Paradise
 * SCENARIO: Send port verification — rate limited
 * GIVEN: `porting-2fa` is enabled
 * WHEN: Midtier sends port verification
 * BUT: Twilio rate limits the request
 * THEN: Midtier returns `{ status: rate_limited, canBypass: true, temporaryNumber: ++available number++ ++held available number++ }` to My Paradise
 * SCENARIO: Send port verification — invalid number
 * GIVEN: `porting-2fa` is enabled
 * WHEN: Midtier sends port verification
 * BUT: Twilio rejects the number as invalid
 * THEN: Midtier returns `{ status: invalid_number }` to My Paradise
 */

/** Story: Send Verification Sms
 * SCENARIO: Send verification SMS
 * GIVEN: `porting-2fa` is enabled
 * AND: ++portability++ ++valid portability++ portNumber is a valid Bermuda number
 * WHEN: Twilio is asked to send a verification SMS to ++portability++ ++valid portability++ portNumber
 * THEN: Twilio creates a verification for ++portability++ ++valid portability++ portNumber (`channel: sms`)
 * AND: Twilio returns `sent` to Midtier
 * SCENARIO: Send verification SMS — rate limited
 * GIVEN: `porting-2fa` is enabled
 * WHEN: Twilio is asked to send a verification SMS
 * BUT: the rate limit for ++portability++ ++valid portability++ portNumber is exceeded
 * THEN: Twilio returns `rate_limited` to Midtier
 */

/** Story: Enter Porting Sms Code
 * background-examples: {"valid porting SMS code": {"porting SMS code": "porting SMS code", "example": "valid porting SMS code", "code": "123456", "group": "porting SMS code"}, "mismatch porting SMS code": {"porting SMS code": "porting SMS code", "example": "mismatch porting SMS code", "code": "Invalid verification code.", "group": "porting SMS code"}, "example": {"porting SMS code": "porting SMS code", "example": "example", "code": "helper", "group": "porting SMS code"}}
 * BACKGROUND: background
 * SCENARIO: Enter ++porting SMS code++
 * background: background
 * background-step: Given | the Prospect is in Account Setup
 * background-step: And | a ++My Paradise customer++ with a ++Mavenir shopping cart++
 * background-step: And | ++portability++ ++valid portability++ is in the ++Mavenir shopping cart++
 * background-step: And | My Paradise has SMSed a ++porting SMS code++ through the Midtier
 * WHEN: the Prospect proceeds to confirming their number for porting
 * THEN: the Prospect sees the code was sent to the ++portability++ number
 * AND: the Prospect can enter ++porting SMS code++ in Enter SMS code
 * AND: the Prospect can Resend
 * AND: Resend is disabled for 30 seconds
 * AND: the Prospect can Change
 * AND: the Prospect can go Back
 * AND: the Verify code operation is disabled
 * WHEN: the Prospect enters ++porting SMS code++ ++valid porting SMS code++
 * THEN: the Verify code operation is enabled
 * WHEN: the Prospect clicks Verify code
 * THEN: My Paradise checks the ++porting SMS code++ through the Midtier
 * AND: the Prospect is forwarded to Select Sim
 * SCENARIO: Verify with unusable ++porting SMS code++
 * background: background
 * background-step: Given | the Prospect is in Account Setup
 * background-step: And | a ++My Paradise customer++ with a ++Mavenir shopping cart++
 * background-step: And | ++portability++ ++valid portability++ is in the ++Mavenir shopping cart++
 * background-step: And | My Paradise has SMSed a ++porting SMS code++ through the Midtier
 * WHEN: the Prospect clicks Verify code with ++porting SMS code++ ++mismatch porting SMS code++
 * THEN: Enter SMS code shows helper text *Invalid verification code.*
 * SCENARIO: Resend ++porting SMS code++
 * background: background
 * background-step: Given | the Prospect is in Account Setup
 * background-step: And | a ++My Paradise customer++ with a ++Mavenir shopping cart++
 * background-step: And | ++portability++ ++valid portability++ is in the ++Mavenir shopping cart++
 * background-step: And | My Paradise has SMSed a ++porting SMS code++ through the Midtier
 * WHEN: the Prospect clicks Resend
 * THEN: My Paradise SMSes a ++porting SMS code++ through the Midtier
 * AND: the Prospect sees *A new code was sent to* the ++portability++ number
 * AND: Resend is disabled for 30 seconds before it can be used again
 */

/** Story: Check Port Verification
 * SCENARIO: Check port verification — code valid
 * background: background
 * background-step: Given | a ++PML customer++ with a ++Mavenir shopping cart++
 * background-step: And | ++portability++ ++valid portability++ is in the ++Mavenir shopping cart++
 * background-step: And | a ++porting SMS code++ was sent to ++portability++ ++valid portability++ portNumber
 * WHEN: Midtier is asked to check ++porting SMS code++ ++valid porting SMS code++ against ++portability++ ++valid portability++ portNumber
 * THEN: Midtier checks the ++porting SMS code++ with Twilio
 * AND: Twilio returns `approved`
 * AND: Midtier marks the ++PML customer++ phone as verified
 * AND: Midtier returns `{ verified: true }` to My Paradise
 * SCENARIO: Check port verification — code mismatch
 * background: background
 * background-step: Given | a ++PML customer++ with a ++Mavenir shopping cart++
 * background-step: And | ++portability++ ++valid portability++ is in the ++Mavenir shopping cart++
 * background-step: And | a ++porting SMS code++ was sent to ++portability++ ++valid portability++ portNumber
 * WHEN: Midtier is asked to check ++porting SMS code++ ++mismatch porting SMS code++ against ++portability++ ++valid portability++ portNumber
 * THEN: Midtier checks the ++porting SMS code++ with Twilio
 * AND: Twilio returns a non-approved status
 * AND: Midtier returns `{ verified: false }` to My Paradise
 */

/** Story: Check Verification
 * SCENARIO: Check verification — code valid
 * background: background
 * background-step: Given | a verification was sent to ++portability++ ++valid portability++ portNumber
 * WHEN: Twilio is asked to check ++porting SMS code++ ++valid porting SMS code++ against ++portability++ ++valid portability++ portNumber
 * THEN: Twilio creates a verification check (`verificationChecks.create`)
 * AND: Twilio returns `approved` to Midtier
 * SCENARIO: Check verification — code mismatch
 * background: background
 * background-step: Given | a verification was sent to ++portability++ ++valid portability++ portNumber
 * WHEN: Twilio is asked to check ++porting SMS code++ ++mismatch porting SMS code++ against ++portability++ ++valid portability++ portNumber
 * THEN: Twilio creates a verification check
 * AND: Twilio returns a non-approved status to Midtier
 */

/** Story: Sweep Stale Number Reservations
 * Actor: Care
 * SCENARIO: Sweep stale number reservations
 * GIVEN: ++MSISDN++ resources have been reserved but have no active order
 * AND: Care observes mass Reserved ++MSISDN++ resources in the Mavenir DEP Resource Inventory
 * WHEN: Care sweeps stale ++MSISDN++ reservations
 * THEN: Mavenir transitions the stale ++MSISDN++ resources from reserved to available
 * AND: the released ++MSISDN++ resources are visible as available in the Mavenir DEP Resource Inventory
 */
