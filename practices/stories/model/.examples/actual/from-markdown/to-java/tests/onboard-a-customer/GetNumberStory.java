// Epic: Get Number

/** Story: Determine Number
 * Actor: Customer
 * SCENARIO: View available numbers
 * SCENARIO: View available numbers — MSISDN in cart
 * SCENARIO: Refresh available numbers
 * SCENARIO: Search for a number
 */

/** Story: Query Msisdn Inventory
 * SCENARIO: Query MSISDN inventory for porting
 * SCENARIO: Query MSISDN inventory
 */

/** Story: List Msisdn Resources
 * SCENARIO: List MSISDN resources for porting
 * SCENARIO: List MSISDN resources
 */

/** Story: Search Msisdn Inventory
 * SCENARIO: Search MSISDN inventory
 */

/** Story: Search Msisdn Resources
 * SCENARIO: Search MSISDN resources by pattern
 */

/** Story: Choose a Number
 * Actor: Customer
 * SCENARIO: Pick new number
 * SCENARIO: Pick new number — replace existing
 * SCENARIO: Keep current number
 */

/** Story: Submit Reserve Number Request to Mid-Tier
 * SCENARIO: Reserve number
 * SCENARIO: Reserve number — replace existing
 * SCENARIO: Reserve number request fails
 */

/** Story: Submit Reserve Msisdn
 * SCENARIO: Reserve temporary MSISDN for porting
 * SCENARIO: Reserve MSISDN
 * SCENARIO: Reserve MSISDN — release previous
 */

/** Story: Reserve Msisdn Resource
 * SCENARIO: Reserve MSISDN resource as temporary port-in number
 * SCENARIO: Reserve MSISDN resource
 * SCENARIO: Reserve MSISDN resource — release previous
 */

/** Story: Submit Patch Cart With Number Request to Mid-Tier
 * SCENARIO: Patch cart with number
 * SCENARIO: Patch cart with number fails
 */

/** Story: Patch Cart With Number
 * SCENARIO: Patch cart with MSISDN
 */

/** Story: Patch Shopping Cart
 * SCENARIO: Patch shopping cart with portability
 * SCENARIO: Patch shopping cart with MSISDN
 * SCENARIO: Patch Shopping Cart
 */

/** Story: Bring a Number
 * SCENARIO: Bring a number
 * SCENARIO: Number to be ported is incomplete
 * SCENARIO: Provider not selected
 */

/** Story: Confirm Number Already With Paradise
 * SCENARIO: Confirm the number is not already with Paradise
 * SCENARIO: Confirm the number is already with Paradise
 */

/** Story: Evaluate Porting Two Factor Flag
 * SCENARIO: Porting two factor flag enabled (Intended)
 * SCENARIO: Porting two factor flag disabled (live)
 */

/** Story: Submit Portability Request to Mid-Tier
 * SCENARIO: Submit portability request — porting-2fa off (live)
 * SCENARIO: Submit portability request — porting-2fa on, SMS sent (Intended)
 * SCENARIO: Submit portability request — rate limited, bypass (Intended)
 * SCENARIO: Submit portability request — invalid number (Intended)
 * SCENARIO: Submit portability request fails
 */

/** Story: Patch Cart With Portability
 * SCENARIO: Patch cart with portability
 */

/** Story: Send Port Verification
 * SCENARIO: Send port verification SMS
 * SCENARIO: Send port verification — rate limited
 * SCENARIO: Send port verification — invalid number
 */

/** Story: Send Verification Sms
 * SCENARIO: Send verification SMS
 * SCENARIO: Send verification SMS — rate limited
 */

/** Story: Enter Porting Sms Code
 * SCENARIO: Enter ++porting SMS code++
 * SCENARIO: Verify with unusable ++porting SMS code++
 * SCENARIO: Resend ++porting SMS code++
 */

/** Story: Check Port Verification
 * SCENARIO: Check port verification — code valid
 * SCENARIO: Check port verification — code mismatch
 */

/** Story: Check Verification
 * SCENARIO: Check verification — code valid
 * SCENARIO: Check verification — code mismatch
 */

/** Story: Sweep Stale Number Reservations
 * Actor: Care
 * SCENARIO: Sweep stale number reservations
 */
