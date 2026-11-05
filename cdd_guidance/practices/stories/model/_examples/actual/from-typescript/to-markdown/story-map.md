# (E) Onboard A Customer
## (E) Create Customer
### (S) --> Create Customer

#### Story Background: each

*Given* the User has a verified account with an account token

#### Examples

| example |
| --- |
| enteredValidAccountCredentials |

#### Scenario: Create customer

*When* the User creates their Paradise account
*Then* My Paradise sends the correct create request to Mavenir
*When* Mavenir creates the customer
*Then* the customer has a Mavenir customer id
*And* My Paradise stores the customer id on the Cognito user

#### Examples

| example |
| --- |
| enteredValidAccountCredentials |

#### Scenario: Mavenir customer already exists

*Given* Mavenir already has a customer for that email
*When* the User creates their Paradise account
*Then* My Paradise shows Could not create customer

#### Examples

| example |
| --- |
| enteredValidAccountCredentials |
### (E) Create Empty Cart
#### (S) --> Ensure Cart on Customer

##### Scenario: Load Cart — no cart

*Given* the Customer enters the onboarding journey with a valid account token and no cart
*When* My Paradise loads the cart for the customer
*Then* My Paradise finds no cart on the customer

##### Examples

| example |
| --- |
| storedAccountCredentialsWithToken |

##### Scenario: Create Cart

*Given* the Customer enters the onboarding journey with a valid account token and no cart
*When* My Paradise creates a cart for the customer
*Then* My Paradise sends the create request to Midtier with the customer id
*When* Mavenir creates the shopping cart
*Then* My Paradise stores the cart on the customer
*And* the Customer proceeds to Get Number

##### Examples

| example |
| --- |
| storedAccountCredentialsWithToken |

##### Scenario: customer already has a Mavenir shopping cart

*Given* the Customer enters the onboarding journey with a valid account token
*And* the customer has a Mavenir shopping cart
*When* My Paradise loads the cart for the customer
*Then* My Paradise finds the cart on the customer
*And* the Customer proceeds to Get Number

##### Examples

| example |
| --- |
| storedAccountCredentialsWithToken |
| newMavenirShoppingCart |

##### Scenario: cart already exists

*Given* the Customer enters the onboarding journey and already has a cart loaded
*When* My Paradise creates a cart for the customer
*Then* My Paradise reports a cart creation error

##### Examples

| example |
| --- |
| storedAccountCredentialsWithToken |
| newMavenirShoppingCart |
### (E) Create Unconfirmed User
#### (S) --> Create Unconfirmed Cognito User

##### Scenario: Display Create Account

*When* the User proceeds to create an account from the Paradise Mobile website
*Then* the User can enter account credentials
*And* the email and password rules are unmet
*And* the customer cannot save the customer account

##### Scenario: Enter Valid account credentials

*When* the User enters valid account credentials
*Then* account credentials are validated continuously
*And* the customer can save the customer account

##### Examples

| example |
| --- |
| enteredValidAccountCredentials |

##### Scenario: Enter Invalid account credentials: ${example}

*When* the User validates ${example}
*Then* the ${unmet} requirement is unmet
*And* the customer cannot save the customer account

##### Scenario: Email already registered

*Given* already-registered account credentials are already registered
*When* the User registers already-registered account credentials
*Then* Email shows the already-registered error

##### Examples

| example |
| --- |
| enteredAlreadyRegisteredAccountCredentials |
| storedAlreadyRegisteredUnconfirmedCognitoUser |

##### Scenario: Create Unconfirmed User

*Given* the amplifyService.signUp spy is set up
*When* the User creates their account
*Then* the system creates an unconfirmed Cognito user and emails a validation code

##### Examples

| example |
| --- |
| enteredValidAccountCredentials |
| expectedValidAccountCredentials |

##### Scenario: Email already registered in Cognito

*Given* an unconfirmed Cognito user exists for already-registered account credentials
*When* Cognito is asked to register already-registered account credentials
*Then* Cognito returns UsernameExistsException
*And* Cognito does not create another Cognito user

##### Examples

| example |
| --- |
| enteredAlreadyRegisteredAccountCredentials |
| storedAlreadyRegisteredUnconfirmedCognitoUser |
### (E) Load Customer
#### (S) --> Load My Paradise Customer From Midtier And Store In Session

##### Story Background: each

*Given* Mavenir has a customer and the Cognito user holds its id

##### Examples

| example |
| --- |
| enteredValidAccountCredentials |
| storedAccountCredentialsWithToken |

##### Scenario: Load My Paradise Customer From Midtier And Store In Session

*When* My Paradise loads the customer through Midtier
*Then* My Paradise calls Midtier with the correct customer id
*And* Midtier maps the Mavenir contact medium to Paradise identity and address

##### Examples

| example |
| --- |
| enteredValidAccountCredentials |

##### Scenario: Load customer fails

*Given* Mavenir no longer has that customer
*When* My Paradise loads the customer
*Then* My Paradise signs the User out
*And* My Paradise shows Something went wrong when loading your account

##### Scenario: Terminated account

*Given* the Customer has an account token
*And* the Mavenir customer billing state is terminated
*When* My Paradise loads the customer
*Then* My Paradise signs the Customer out
*And* the Customer account is terminated

##### Examples

| example |
| --- |
| storedAccountCredentialsWithToken |
### (E) Verify Account
#### (S) --> Enter Validation Code

##### Story Background: each

*Given* the User has submitted valid account credentials
*And* Cognito has an unconfirmed Cognito user
*And* Cognito has sent a validation code to the User
*And* the User has account credentials with valid email and password

##### Examples

| example |
| --- |
| storedUnconfirmedCognitoUser |
| enteredValidAccountCredentials |
| unusableValidationCodeExamples |
| enteredValidValidationCode |

##### Scenario: Enter validation code

*When* the User activates the account with the emailed validation code
*Then* My Paradise sends the correct confirmation request to Cognito
*And* the account is verified
*And* Cognito issues an account token for the browser session
*But* no Mavenir customer exists for those account credentials

##### Examples

| example |
| --- |
| enteredValidAccountCredentials |

##### Scenario: Activate with unusable validation code: ${example}

*When* the User activates with ${example}
*Then* Enter Validation Code shows ${helper}

##### Scenario: Resend validation code

*When* more than 60 seconds has passed
*And* the User resends the validation code
*Then* Cognito sends a new validation code
*And* My Paradise shows the resend confirmation
*When* less than 60 seconds has passed
*And* the User resends the validation code
*Then* Resend waits 60 seconds before it can be used again
*And* Cognito does not send another validation code during the wait
*When* more than 60 seconds has passed
*And* the User resends the validation code
*Then* Cognito sends another validation code
## (E) Get Number
### (E) Enter Porting Number
#### (S) --> Submit Portability Request

##### Scenario: Port the number

*Given* a My Paradise customer with a Mavenir shopping cart
*And* ${storedHeldAvailableNumber} is available as a temporary port-in MSISDN
*When* the Customer enters valid portability and ports their number
*Then* My Paradise submits the portability request to Mavenir with the customer's portability details
*And* Mavenir reserves the temporary MSISDN and Twilio sends an SMS verification to the port number
*When* Mavenir assigns ${storedHeldAvailableNumber} as a temporary port-in MSISDN and patches the shopping cart, and Twilio sends the SMS verification
*Then* the Customer is forwarded to Verify Ported Number

##### Examples

| example |
| --- |
| storedHeldAvailableNumber |
| enteredValidPortability |
| customerWithCart |
| stubBundle |
| reloadCart |

##### Scenario: Port the number — SMS verification skipped

*Given* a My Paradise customer with a Mavenir shopping cart
*And* Mavenir returns the temporary MSISDN and Twilio rate-limits the SMS send
*When* the Customer enters valid portability and ports their number
*When* Mavenir processes the portability request and Twilio rate-limits the SMS send
*Then* portability is stored on the line with verification skipped
*And* the Customer is forwarded to Select Sim — no verification step required

##### Examples

| example |
| --- |
| storedHeldAvailableNumber |
| enteredValidPortability |
| customerWithCart |
| stubBundle |

##### Scenario: Port the number: ${example}

*Given* a My Paradise customer with a Mavenir shopping cart
*When* the Customer submits portability and ports their number
*Then* submit returns error: ${expectedMessage}

##### Examples

| example |
| --- |
| customerWithCart |
| stubBundle |
### (E) Get New Number
#### (S) --> Determine Number

##### Scenario: View available numbers

*Given* a My Paradise customer with a Mavenir shopping cart and no MSISDN
*When* the Customer loads available numbers
*Then* My Paradise sends the list resources request to Mavenir
*When* Mavenir locks 20 MSISDN resources and returns the available number values
*Then* My Paradise returns the available numbers
*And* ${storedHeldAvailableNumber} and ${enteredChosenAvailableNumber} are in the Available Number list

##### Examples

| example |
| --- |
| storedHeldAvailableNumber |
| enteredChosenAvailableNumber |
| storedAvailableNumbers |
| customerWithCart |

##### Scenario: View available numbers — MSISDN in cart

*Given* MSISDN ${storedHeldAvailableNumber} is in the Mavenir shopping cart
*When* the Customer loads available numbers
*Then* My Paradise sends the list resources request to Mavenir
*When* Mavenir locks 20 MSISDN resources and returns the available number values
*Then* the Customer sees their number is ${storedHeldAvailableNumber}
*And* My Paradise returns the available numbers

##### Examples

| example |
| --- |
| storedHeldAvailableNumber |
| storedAvailableNumbers |
| customerWithCart |
| stubBundle |

##### Scenario: Refresh available numbers

*Given* a My Paradise customer with a Mavenir shopping cart
*When* the Customer refreshes the number list
*Then* My Paradise sends the list resources request to Mavenir
*When* Mavenir locks 20 MSISDN resources and returns the available numbers
*Then* My Paradise returns a fresh set of available numbers

##### Examples

| example |
| --- |
| storedAvailableNumbers |
| customerWithCart |

##### Scenario: Search for a number

*Given* a My Paradise customer with a Mavenir shopping cart
*When* the Customer searches for numbers matching JAMES (52637)
*Then* My Paradise sends the search request to Mavenir with pattern 52637
*When* Mavenir locks MSISDN resources matching 52637 and returns matching values
*Then* My Paradise returns Available Numbers matching 52637
*And* the matching numbers are stored on the line for selection

##### Examples

| example |
| --- |
| customerWithCart |

##### Scenario: Numbers locked by another customer are excluded from results

*Given* another customer has already locked the standard available numbers in Mavenir
*When* the Customer loads available numbers
*Then* My Paradise sends the list resources request to Mavenir
*When* Mavenir returns only available numbers, excluding the locked ones
*Then* the locked numbers are not in the available numbers list
*And* only the currently available numbers are returned

##### Examples

| example |
| --- |
| storedHeldAvailableNumber |
| enteredChosenAvailableNumber |
| customerWithCart |
#### (S) --> Choose a Number

##### Scenario: Pick number

*Given* Mavenir has locked ${enteredChosenAvailableNumber} in the available numbers list and no MSISDN is in the cart
*When* My Paradise reserves ${enteredChosenAvailableNumber} in Mavenir and patches the shopping cart
*Then* My Paradise sends the reserve request to Mavenir with ${enteredChosenAvailableNumber}
*And* My Paradise patches the Mavenir shopping cart with ${enteredChosenAvailableNumber}
*When* Mavenir confirms the reservation and patches the cart
*Then* My Paradise stores ${expectedChosenAvailableNumber} on the line
*And* the Customer is forwarded to Select Sim

##### Examples

| example |
| --- |
| enteredChosenAvailableNumber |
| expectedChosenAvailableNumber |
| storedAvailableNumbers |
| customerWithCart |
| reloadCart |
| stubBundle |

##### Scenario: Pick number — replace existing

*Given* MSISDN ${storedHeldAvailableNumber} is in the cart and Mavenir has locked ${enteredChosenAvailableNumber} in the available numbers list
*When* My Paradise reserves ${enteredChosenAvailableNumber} releasing ${storedHeldAvailableNumber}
*Then* My Paradise sends the reserve request to Mavenir with ${enteredChosenAvailableNumber} releasing ${storedHeldAvailableNumber}
*When* Mavenir releases ${storedHeldAvailableNumber} and reserves ${enteredChosenAvailableNumber}
*Then* My Paradise stores ${expectedChosenAvailableNumber} on the line

##### Examples

| example |
| --- |
| storedHeldAvailableNumber |
| enteredChosenAvailableNumber |
| expectedChosenAvailableNumber |
| storedAvailableNumbers |
| customerWithCart |
| reloadCart |
| stubBundle |

##### Scenario: Reserve number request fails

*Given* Mavenir has locked ${enteredChosenAvailableNumber} in the available numbers list but reserve returns an error
*When* My Paradise attempts to reserve ${enteredChosenAvailableNumber} but Mavenir returns an error
*Then* My Paradise shows Failed to reserve your number.

##### Examples

| example |
| --- |
| enteredChosenAvailableNumber |
| storedAvailableNumbers |
| customerWithCart |

##### Scenario: Patch cart with number fails

*Given* Mavenir has reserved ${enteredChosenAvailableNumber} but patching the cart returns an error
*When* My Paradise patches the Mavenir shopping cart with ${enteredChosenAvailableNumber} but Mavenir returns an error
*Then* My Paradise shows Failed to update your cart.

##### Examples

| example |
| --- |
| enteredChosenAvailableNumber |
| storedAvailableNumbers |
| customerWithCart |
### (E) Verify Ported Number
#### (S) --> Check Port Verification

##### Scenario: Enter porting SMS code

*Given* the Customer submitted portability and Twilio sent an SMS to the port number
*And* Twilio is ready to confirm the SMS code as valid
*When* the Customer enters verification code ${validPortingSmscode}
*Then* My Paradise sends the verification check to Twilio with the port number and code
*When* Twilio creates a verification check (verificationChecks.create)
*Then* Twilio returns approved and the Customer is forwarded to Select Sim

##### Examples

| example |
| --- |
| enteredValidPortability |
| validPortingSmscode |
| customerWithCartAndPortability |

##### Scenario: Verify with unusable porting SMS code

*Given* the Customer submitted portability and has an incorrect verification code
*When* the Customer enters verification code ${mismatchPortingSmscode}
*Then* My Paradise sends the verification check to Twilio
*When* Twilio creates a verification check and returns a non-approved status
*Then* the verification is rejected

##### Examples

| example |
| --- |
| enteredValidPortability |
| mismatchPortingSmscode |
| customerWithCartAndPortability |

##### Scenario: Resend porting SMS code

*Given* the Customer submitted portability and Twilio sent an SMS to the port number
*When* the Customer requests a new verification code
*Then* My Paradise SMSes a porting verification code via Twilio
*When* Twilio sends the SMS verification
*Then* the resend is confirmed

##### Examples

| example |
| --- |
| enteredValidPortability |
| customerWithCartAndPortability |
## (E) Get Onboarding Plan
### (S) --> Load Plan Catalog

#### Scenario: Load plan catalog

*Given* the plan catalog is available
*When* My Paradise loads the plan catalog
*Then* the catalog includes Essentials, Data Freedom, Ace, and Atlas
*And* Internal Test Plan PROMO is excluded from the catalog

#### Examples

| example |
| --- |
| internalTestPlan |
| purchasablePlansExamples |
### (S) --> Choose Onboarding Plan

#### Scenario: Select a plan

*Given* no plan is in the Mavenir shopping cart
*When* the Customer selects Essentials
*Then* My Paradise patches the Mavenir cart with the Essentials planId
*And* the Customer is forwarded to Pick Number
*When* Mavenir confirms the cart is patched with Essentials
*Then* the cart bundle is a snapshot of Essentials loaded from the gateway

#### Examples

| example |
| --- |
| essentials |
| customerWithCart |
| reloadCart |

#### Scenario: Change an existing plan

*Given* Essentials is in the Mavenir shopping cart
*When* the Customer selects Data Freedom
*Then* My Paradise patches the Mavenir cart with the Data Freedom planId
*When* Mavenir confirms the cart is patched with Data Freedom
*Then* the cart bundle is updated to a snapshot of Data Freedom loaded from the gateway

#### Examples

| example |
| --- |
| essentials |
| customerWithCart |
| reloadCart |

#### Scenario: Failed to update plan

*Given* the Mavenir cart patch returns an error
*When* the Customer selects Essentials
*Then* the plan selection fails
*When* My Paradise reloads the shopping cart
*Then* the cart bundle remains empty

#### Examples

| example |
| --- |
| essentials |
| customerWithCart |
| reloadCart |
## (E) Get Order Review
### (S) --> Check The Order

#### Scenario: Check the order: ${example}

*Given* the Customer has completed account setup, number, SIM, and profile
*When* My Paradise loads the order state from the Mavenir shopping cart
*Then* the Customer is forwarded to Checkout
*And* the order summary shows the plan
*And* the order summary shows the number and SIM
*And* the order summary shows the profile

#### Examples

| example |
| --- |
| seedCustomerCart |
| loadCart |
| stubBundle |
### (S) --> Upgrade To Data Freedom

#### Scenario: Upgrade plan from review: ${example}

*Given* ${currentPlan.name} is in the Mavenir shopping cart
*When* My Paradise patches the Mavenir shopping cart with ${newPlan.name}
*Then* My Paradise sends the patch cart request to Mavenir with ${newPlan.name} bundleId
*When* Mavenir returns the updated Mavenir shopping cart with ${newPlan.name}
*Then* My Paradise stores ${newPlan.name} as the cart bundle

#### Examples

| example |
| --- |
| customerWithCart |
| reloadCart |
### (S) --> Change Plan From Review

#### Scenario: Select a different plan from review

*Given* the Customer has opened plan selection from review with Essentials in the cart
*When* My Paradise patches the Mavenir shopping cart with Data Freedom
*Then* My Paradise sends the patch cart request to Mavenir with Data Freedom bundleId
*When* Mavenir returns the updated Mavenir shopping cart with Data Freedom
*Then* My Paradise stores Data Freedom as the cart bundle loaded from the gateway
*And* the Customer is forwarded to Checkout

#### Examples

| example |
| --- |
| customerWithCart |
| reloadCart |
| enteredChosenAvailableNumber |
| essentials |
| dataFreedom |

#### Scenario: Keep current plan from review

*Given* the Customer has opened plan selection from review with Essentials in the cart
*When* the Customer keeps their current plan
*Then* the cart bundle remains Essentials
*And* the Customer is forwarded to Checkout

#### Examples

| example |
| --- |
| customerWithCart |
| enteredChosenAvailableNumber |
| essentials |

#### Scenario: Plan update fails from review

*Given* the Customer has opened plan selection from review with Essentials in the cart
*When* My Paradise patches the Mavenir shopping cart with Data Freedom but Mavenir returns an error
*Then* My Paradise shows Failed to update new plan choice.
*When* My Paradise reloads the shopping cart
*Then* the cart bundle remains Essentials

#### Examples

| example |
| --- |
| customerWithCart |
| reloadCart |
| essentials |
| dataFreedom |
## (E) Get Payment
### (S) --> Enter Payment

#### Scenario: Enter Payment

*Given* the Customer is at Checkout with Essentials
*And* Mavenir CCS authorizes stub auth
*When* the Customer proceeds to adding their payment
*Then* My Paradise sends the card authorization request to Mavenir with TotalAmount $1 and salesChannel ON-BOARDING
*When* Mavenir authorizes the card and returns the hosted payment page
*Then* the payment has stub auth transaction id, amount $1, and sales channel ON-BOARDING

#### Examples

| example |
| --- |
| customerReadyForPayment |
| maxPaymentAttempts |
| stubAuth |

#### Scenario: Payment authorization fails to load

*Given* the Customer is at Checkout with Essentials
*But* Mavenir CCS does not return a payment authorization
*When* the Customer proceeds to adding their payment
*Then* My Paradise sends the card authorization request to Mavenir
*When* Mavenir does not return a payment authorization
*Then* the payment authorization cannot be loaded

#### Examples

| example |
| --- |
| customerReadyForPayment |
| maxPaymentAttempts |

#### Scenario: FAC authorization timeout

*Given* the Customer is at Checkout with Essentials
*But* Mavenir does not return a transaction id
*When* the Customer proceeds to adding their payment
*Then* My Paradise sends the card authorization request to Mavenir
*When* Mavenir does not return a transaction id
*Then* the payment authorization cannot be loaded

#### Examples

| example |
| --- |
| customerReadyForPayment |
| maxPaymentAttempts |
### (S) --> Authorize Card

#### Scenario: Payment completed

*Given* the Customer has stub auth
*And* Mavenir CCS has completed auth
*When* the Customer authorizes their card
*Then* My Paradise sends the tokenized card request to Mavenir for stub auth
*When* Mavenir returns completed auth
*Then* the payment is authorized
*And* the payment step does not place the order

#### Examples

| example |
| --- |
| reloadCart |
| customerReadyForPayment |
| paymentWithAuthorization |
| stubAuth |
| completedAuth |

#### Scenario: Card not verified

*Given* the Customer has stub auth
*And* Mavenir CCS has failed auth
*And* payment attempts are under the maximum
*When* the Customer authorizes their card
*Then* My Paradise sends the tokenized card request to Mavenir
*When* Mavenir returns failed auth
*Then* the card is not verified
*And* My Paradise requests a fresh payment authorization from Mavenir

#### Examples

| example |
| --- |
| customerReadyForPayment |
| maxPaymentAttempts |
| paymentWithAuthorization |
| stubAuth |
| failedAuth |

#### Scenario: Maximum payment attempts

*Given* the Customer has stub auth
*And* Mavenir CCS has failed auth
*And* payment attempts equal the maximum
*When* the Customer authorizes their card
*Then* My Paradise sends the tokenized card request to Mavenir for stub auth
*When* Mavenir returns failed auth
*Then* My Paradise records the failed card addition with Zendesk
*And* the payment step does not place the order

#### Examples

| example |
| --- |
| reloadCart |
| customerReadyForPayment |
| maxPaymentAttempts |
| paymentWithAuthorization |
| stubAuth |
| failedAuth |
### (S) --> Provide Apple Pay Certificate

#### Scenario: Provide Apple Pay certificate

*Given* the Apple Pay merchant certificate is available
*When* My Paradise provides the Apple Pay certificate
*Then* My Paradise sends the certificate request to Apple
*When* Apple returns Bermuda Apple Pay cert
*Then* My Paradise returns Bermuda Apple Pay cert

#### Examples

| example |
| --- |
| bermudaApplePayCert |
| bermudaApplePayCertificate |
## (E) Get Sign Up Plan
### (S) --> Open Plan Deep Link

#### Scenario: Open plan deep link: ${plan.name}

*Given* the plan catalog contains purchasable plans and the Customer arrived at sign-up from the Paradise Mobile website
*When* the Customer opens a plan deep link for ${plan.name}
*Then* ${plan.name} is selected
*And* the Customer continues to Enter Account Credentials

#### Examples

| example |
| --- |
| seedPurchasableCatalog |

#### Scenario: Unknown plan deep link

*Given* the plan catalog contains purchasable plans
*But* the deep-link plan id is not in the catalog
*When* the Customer opens a plan deep link
*Then* the plan is not found

#### Examples

| example |
| --- |
| seedPurchasableCatalog |
| unknownPlanDeepLinkId |
### (S) --> Apply Catalog Voucher

#### Scenario: Apply Catalog Voucher via deep link

*Given* the plan catalog contains purchasable plans
*And* Vouchera has valid catalog voucher
*When* the Customer applies valid catalog voucher from a promotional voucher link
*Then* My Paradise sends the voucher code to Vouchera
*When* Vouchera returns the voucher view
*Then* the catalog voucher is applied
*And* the voucher discounts Essentials, Data Freedom, Ace, and Atlas by 10 percent

#### Examples

| example |
| --- |
| seedPurchasableCatalog |
| purchasablePlanIds |
| seedValidCatalogVoucher |
| enteredValidCatalogVoucherCode |
| expectedValidCatalogVoucherCode |

#### Scenario: Apply Catalog Voucher manually

*Given* the Customer is selecting a plan
*And* Vouchera has valid catalog voucher
*When* the Customer applies valid catalog voucher
*Then* My Paradise sends the voucher code to Vouchera
*When* Vouchera returns the voucher view
*Then* the catalog voucher is applied
*And* the voucher discounts Essentials, Data Freedom, Ace, and Atlas by 10 percent

#### Examples

| example |
| --- |
| seedPurchasableCatalog |
| purchasablePlanIds |
| seedValidCatalogVoucher |
| enteredValidCatalogVoucherCode |

#### Scenario: Short catalog voucher code is rejected

*Given* the Customer is selecting a plan
*When* the Customer applies a catalog voucher shorter than ${VoucherCodeRule.MinLength} characters
*Then* the catalog voucher is rejected
*And* Vouchera is not asked for the voucher

#### Examples

| example |
| --- |
| seedPurchasableCatalog |
| shortCatalogVoucherCode |
| VoucherCodeRule |

#### Scenario: Remove Catalog Voucher

*Given* the Customer is selecting a plan with valid catalog voucher applied
*When* the Customer removes valid catalog voucher
*Then* the catalog has no catalog voucher

#### Examples

| example |
| --- |
| seedPurchasableCatalog |
| seedAppliedValidCatalogVoucher |

#### Scenario: Apply unusable catalog voucher: ${example}

*Given* the Customer is selecting a plan
*And* Vouchera has ${example}
*When* the Customer applies ${example}
*Then* My Paradise sends the voucher code to Vouchera
*Then* the catalog voucher is rejected

#### Examples

| example |
| --- |
| seedPurchasableCatalog |
| seedUnusableCatalogVoucher |
## (E) Get Sim
### (S) --> Choose Esim

#### Scenario: Choose eSIM

*Given* no SIM type is on the line
*When* the Customer selects eSIM
*Then* My Paradise sends the patch cart request to Mavenir with SIM type eSIM
*When* Mavenir returns the updated Mavenir shopping cart with SIM type eSIM
*Then* My Paradise stores eSIM on the line
*But* the line has no ICCID
*And* the Customer is forwarded to Verify ID

#### Examples

| example |
| --- |
| reloadCart |
| customerReadyToChooseSim |

#### Scenario: Choose eSIM — already on the line

*Given* the line already has SIM type eSIM
*When* the Customer selects eSIM
*Then* My Paradise skips the cart patch

#### Examples

| example |
| --- |
| customerReadyToChooseSim |

#### Scenario: Choose eSIM — cart patch fails

*Given* Mavenir returns an error on cart patch
*When* the Customer selects eSIM
*Then* the SIM selection fails
*When* My Paradise reloads the shopping cart
*Then* the line has no SIM type
*And* the line has no ICCID

#### Examples

| example |
| --- |
| reloadCart |
| customerReadyToChooseSim |
### (S) --> Request a Paradise Sim Card

#### Scenario: Request a Paradise SIM card

*Given* no SIM type is on the line and no ICCID is on the line
*When* the Customer requests a Paradise SIM card
*Then* My Paradise sends the patch cart request to Mavenir with SIM type pSIM
*When* Mavenir returns the updated Mavenir shopping cart with SIM type pSIM
*Then* My Paradise stores pSIM on the line
*But* the line has no ICCID
*And* the Customer is forwarded to Verify ID

#### Examples

| example |
| --- |
| reloadCart |
| customerReadyToChooseSim |

#### Scenario: Request a Paradise SIM card — already on the line

*Given* the line already has SIM type pSIM
*When* the Customer requests a Paradise SIM card
*Then* My Paradise skips the cart patch

#### Examples

| example |
| --- |
| customerReadyToChooseSim |

#### Scenario: Request a Paradise SIM card — cart patch fails

*Given* Mavenir returns an error on cart patch
*When* the Customer requests a Paradise SIM card
*Then* the SIM selection fails
*When* My Paradise reloads the shopping cart
*Then* the line has no SIM type
*And* the line has no ICCID

#### Examples

| example |
| --- |
| reloadCart |
| customerReadyToChooseSim |
### (S) --> Enter Existing Sim

#### Scenario: Enter existing SIM

*Given* Mavenir has valid ICCID available in inventory
*When* the Customer attaches valid ICCID
*Then* My Paradise sends the ICCID inventory request to Mavenir with valid ICCID
*And* My Paradise sends the patch cart request to Mavenir with SIM type pSIM and valid ICCID
*When* Mavenir returns the updated Mavenir shopping cart with SIM type pSIM and valid ICCID
*Then* My Paradise stores pSIM and valid ICCID on the line
*And* the line has valid ICCID
*And* the Customer is forwarded to Verify ID

#### Examples

| example |
| --- |
| reloadCart |
| enteredValidIccid |
| expectedValidIccid |
| customerReadyToChooseSim |

#### Scenario: ICCID contains spaces

*Given* the Customer has ICCID with spaces
*When* the Customer attaches ICCID with spaces
*Then* the ICCID format is rejected
*And* My Paradise does not query inventory or patch the cart

#### Examples

| example |
| --- |
| enteredIccidWithSpaces |
| customerReadyToChooseSim |

#### Scenario: Inventory rejects ICCID

*Given* Mavenir does not have invalid ICCID available in inventory
*When* the Customer attaches invalid ICCID
*Then* My Paradise sends the ICCID inventory request to Mavenir with invalid ICCID
*And* My Paradise does not patch the cart
*And* the ICCID is rejected

#### Examples

| example |
| --- |
| enteredInvalidIccid |
| customerReadyToChooseSim |
### (S) --> Activate Sim

#### Scenario: Activate Sim

*Given* Mavenir has valid ICCID available in inventory
*When* the Customer activates the SIM with valid ICCID
*Then* My Paradise sends the ICCID inventory request to Mavenir with valid ICCID
*And* My Paradise sends the patch cart request to Mavenir with SIM type pSIM and valid ICCID
*And* My Paradise sends the pSIM delivered order to Mavenir
*When* Mavenir creates the product order and clears waiting pSIM
*Then* My Paradise stores valid ICCID on the line

#### Examples

| example |
| --- |
| reloadCart |
| enteredValidIccid |
| expectedValidIccid |
| customerWaitingForPsim |

#### Scenario: waiting pSIM is absent

*Given* Mavenir has valid ICCID available in inventory but the Mavenir customer has no waiting pSIM characteristic
*When* the Customer activates the SIM with valid ICCID
*Then* the pSIM delivered order is rejected

#### Examples

| example |
| --- |
| enteredValidIccid |
| customerWaitingForPsim |

#### Scenario: waiting pSIM already completed

*Given* Mavenir has valid ICCID available in inventory and the Mavenir customer has waiting pSIM false
*When* the Customer activates the SIM with valid ICCID
*Then* the pSIM delivered order is rejected

#### Examples

| example |
| --- |
| enteredValidIccid |
| customerWaitingForPsim |
## (E) Get Verified Profile
### (S) --> Customer Complete Persona Kyc

#### Scenario: Persona verification required

*Given* the Customer has a cart with a plan, number, and SIM and no idNumber
*When* the Customer validates whether a Persona inquiry is required
*Then* a Persona inquiry is required
*And* the Customer is on the Profile KYC step

#### Examples

| example |
| --- |
| customerWithProfile |

#### Scenario: Persona verification already complete

*Given* the Customer has identity with an idNumber
*When* the Customer validates whether a Persona inquiry is required
*Then* the Persona inquiry is already complete
*And* the Customer is forwarded to Checkout

#### Examples

| example |
| --- |
| customerWithProfile |
| expectedValidIdentity |

#### Scenario: Create a completed Persona inquiry

*Given* the Customer has no idNumber on identity
*When* the Customer creates a Persona inquiry
*Then* My Paradise sends the inquiry request to Persona with the Customer email
*And* My Paradise retrieves the Persona document
*When* Persona returns the completed inquiry
*Then* the Customer has a verified Persona inquiry
*And* My Paradise maps the inquiry onto identity and address
*And* Customer verified stays false until the Customer confirms their identity
*When* Persona returns the valid Persona document
*Then* identity expiry date is the Persona document expiration date

#### Examples

| example |
| --- |
| completedInquiryId |
| completedPersonaInquiryResult |
| validDocumentId |
| validPersonaDocument |
| customerWithProfile |
| expectedValidAddress |
| expectedValidIdentity |

#### Scenario: Persona inquiry not completed

*Given* the Customer has no idNumber on identity
*When* the Customer creates a Persona inquiry
*Then* My Paradise sends the inquiry request to Persona with the Customer email
*When* Persona returns the failed Persona inquiry
*Then* the Customer has an unverified Persona inquiry
*And* identity and address stay empty

#### Examples

| example |
| --- |
| failedPersonaInquiryResult |
| customerWithProfile |

#### Scenario: No government ID document on inquiry

*Given* the completed Persona inquiry has no government ID document
*When* the Customer creates a Persona inquiry
*Then* My Paradise sends the inquiry request to Persona
*And* My Paradise does not retrieve a Persona document
*When* Persona returns the completed inquiry without a government ID
*Then* identity expiry date is empty

#### Examples

| example |
| --- |
| completedInquiryWithoutDocument |
| customerWithProfile |

#### Scenario: Persona errors on inquiry load

*Given* the Customer has no idNumber on identity
*When* the Customer creates a Persona inquiry
*Then* My Paradise sends the inquiry request to Persona
*When* Persona returns an error
*Then* the Customer has an unverified Persona inquiry
*And* identity stays empty

#### Examples

| example |
| --- |
| customerWithProfile |

#### Scenario: Document not found

*Given* Persona has no Persona document for that document ID
*When* the Customer creates a Persona inquiry
*Then* My Paradise retrieves the Persona document
*When* Persona returns that the document is not found
*Then* identity expiry date is empty

#### Examples

| example |
| --- |
| completedPersonaInquiryResult |
| validDocumentId |
| customerWithProfile |

#### Scenario: Document email mismatch

*Given* the Persona document email does not match the Customer email
*When* the Customer creates a Persona inquiry
*Then* My Paradise retrieves the Persona document
*When* Persona returns unauthorized
*Then* identity expiry date is empty

#### Examples

| example |
| --- |
| completedPersonaInquiryResult |
| validDocumentId |
| customerWithProfile |

#### Scenario: Verify later

*Given* the Customer has no idNumber on identity
*When* the Customer proceeds without a Persona inquiry
*Then* My Paradise does not send an inquiry request to Persona
*And* no Persona inquiry is stored
*And* the Customer is still on the Profile KYC step

#### Examples

| example |
| --- |
| customerWithProfile |

#### Scenario: Enter valid identity and address

*Given* the Customer has a My Paradise customer in session
*When* the Customer enters valid identity and address
*Then* all profile requirements are met
*And* the Customer can confirm their identity

#### Examples

| example |
| --- |
| customerWithProfile |
| enteredValidAddress |
| enteredValidIdentity |
| expectedValidAddress |
| expectedValidIdentity |

#### Scenario: Enter identity after a verified Persona inquiry

*Given* the Customer has a verified Persona inquiry mapped onto valid identity
*When* the Customer enters the mapped identity and address
*Then* all profile requirements are met
*And* the ID fields are present on identity

#### Examples

| example |
| --- |
| completedInquiryId |
| customerWithProfile |
| enteredValidAddress |
| enteredValidIdentity |
| expectedValidIdentity |
| validProfileSeed |

#### Scenario: Re-enter a verified identity

*Given* the Customer has valid identity already verified
*When* the Customer re-enters valid identity
*Then* the identity is no longer verified
*And* the Customer can confirm their identity again

#### Examples

| example |
| --- |
| completedInquiryId |
| customerWithProfile |
| enteredValidAddress |
| enteredValidIdentity |
| expectedValidIdentity |
| validProfileSeed |

#### Scenario: Enter incomplete identity or address: ${example}

*Given* the Customer has a My Paradise customer in session
*When* the Customer enters identity and address with ${field} empty
*Then* ${field} is missing
*And* the Customer cannot confirm their identity

#### Examples

| example |
| --- |
| customerWithProfile |

#### Scenario: Confirm identity with a verified Persona inquiry

*Given* the Customer has entered valid identity and address and has a verified Persona inquiry
*When* the Customer confirms their identity
*Then* My Paradise maps identity and address onto the Mavenir engaged party and contact medium
*And* My Paradise sends the profile patch to Mavenir
*When* Mavenir patches the customer
*Then* the Customer identity is persisted
*And* the Customer is verified

#### Examples

| example |
| --- |
| reloadCart |
| completedInquiryId |
| customerWithProfile |
| expectedValidAddress |
| expectedValidIdentity |
| validProfileSeed |

#### Scenario: Customer already exists

*Given* another Mavenir customer already has identity idNumber I1234562
*When* the Customer confirms their identity
*Then* My Paradise sends the profile patch to Mavenir
*And* the identity cannot be confirmed because a customer with that information already exists

#### Examples

| example |
| --- |
| completedInquiryId |
| customerWithProfile |
| expectedValidIdentity |
| validProfileSeed |

#### Scenario: Profile requirements unmet

*Given* the Customer has not entered identity or address
*When* the Customer confirms their identity
*Then* the identity cannot be confirmed
*And* My Paradise does not send a profile patch to Mavenir

#### Examples

| example |
| --- |
| customerWithProfile |

#### Scenario: Mavenir profile patch error

*Given* Mavenir returns a profile patch error
*When* the Customer confirms their identity
*Then* My Paradise sends the profile patch to Mavenir
*And* the identity cannot be confirmed

#### Examples

| example |
| --- |
| completedInquiryId |
| customerWithProfile |
| validProfileSeed |
### (S) --> Collect Identity With Brand Amassador
## (E) Get Voucher Credit
### (S) --> Redeem Voucher and Apply Credit

#### Scenario: Redeem a plan-restricted voucher that matches the cart bundle: ${example}

*Given* the Customer is in Order Creation with ${example} applied
*When* the Customer redeems the voucher
*Then* My Paradise sends the redeem request to Vouchera with ${example} orderAmount ${orderAmount}
*When* Vouchera records the voucher redemption
*Then* My Paradise stores the ${example} redemption
*When* the Customer applies the voucher credit
*Then* My Paradise sends the ${creditExample} to Mavenir
*When* Mavenir records the credit adjustment on the billing account
*Then* My Paradise stores the credit on the Customer billing account

#### Examples

| example |
| --- |
| reloadCart |
| billingAccountId |
| cartWithBilling |
| essentials |

#### Scenario: Redeem an any-plan voucher

*Given* the Customer is in Order Creation with any-plan voucher applied
*When* the Customer redeems the voucher
*Then* My Paradise sends the redeem request to Vouchera with zero redemption orderAmount 0.00
*When* Vouchera records the voucher redemption
*Then* My Paradise stores the zero redemption
*And* My Paradise skips the apply credit request to Mavenir

#### Examples

| example |
| --- |
| anyPlanVoucher |
| anyPlanVoucherCode |
| anyPlanVoucheraSeed |
| zeroRedemption |
| cartWithBilling |
| essentials |

#### Scenario: Skip redeem when the cart bundle is not in the voucher plan list

*Given* the Customer is in Order Creation with amount-off voucher applied and Ace in the cart
*When* the Customer redeems the voucher
*Then* My Paradise skips the redeem request to Vouchera
*And* My Paradise skips the apply credit request to Mavenir

#### Examples

| example |
| --- |
| ace |
| amountOffVoucher |
| cartWithBilling |

#### Scenario: Failed voucher redemption

*Given* the Customer is in Order Creation with amount-off voucher applied
*When* the Customer redeems the voucher
*Then* My Paradise sends the redeem request to Vouchera
*When* Vouchera returns an error
*Then* the voucher redemption is unsuccessful
*When* the Customer applies the voucher credit
*Then* My Paradise skips the apply credit request to Mavenir

#### Examples

| example |
| --- |
| amountOffVoucher |
| amountOffVoucherCode |
| amountOffVoucheraSeed |
| redeemMatchOutlines |
| cartWithBilling |
| essentials |
## (E) Place Order
### (S) --> Create Billing Account

#### Scenario: Create billing account

*Given* the Customer has a configured cart and no billing account
*When* the Customer creates a billing account
*Then* My Paradise sends the billing account request to Mavenir
*When* Mavenir creates the billing account
*Then* the Customer has a billing account
*And* the Customer is on the Done step

#### Examples

| example |
| --- |
| reloadCart |
| customerReadyToPlaceOrder |
| expectedBillingAccountRequest |

#### Scenario: Billing account already exists

*Given* the Customer already has a billing account
*When* the Customer creates a billing account
*Then* the billing account is rejected
*And* Mavenir does not receive a billing account request

#### Examples

| example |
| --- |
| customerReadyToPlaceOrder |

#### Scenario: Billing account creation fails

*Given* Mavenir returns an error for the billing account request
*When* the Customer creates a billing account
*Then* the billing account cannot be created
*When* My Paradise reloads the customer
*Then* the Customer has no billing account

#### Examples

| example |
| --- |
| reloadCart |
| customerReadyToPlaceOrder |
### (S) --> Create Product Order

#### Scenario: Create product order

*Given* the Customer is verified and has a billing account, plan, number, and eSIM
*When* the Customer places the product order
*Then* My Paradise sends the product order request to Mavenir
*When* Mavenir creates the product order
*Then* the order succeeded with pay-up-front
*And* the Customer onboarding is done

#### Examples

| example |
| --- |
| reloadCart |
| customerReadyToPlaceOrder |
| expectedProductOrderRequest |

#### Scenario: Pay-up-front charge fails

*Given* the pay-up-front charge fails
*When* the Customer places the product order
*Then* My Paradise does not send a product order to Mavenir
*When* My Paradise reloads the cart
*Then* the order succeeded without pay-up-front

#### Examples

| example |
| --- |
| reloadCart |
| customerReadyToPlaceOrder |

#### Scenario: Product order fails

*Given* Mavenir returns an error for the product order
*When* the Customer places the product order
*Then* My Paradise sends the product order request to Mavenir
*When* My Paradise reloads the cart
*Then* the order did not succeed

#### Examples

| example |
| --- |
| reloadCart |
| customerReadyToPlaceOrder |

#### Scenario: Onboarding is already done

*Given* the Customer onboarding is already done
*When* the Customer places the product order
*Then* the product order is rejected
*And* Mavenir does not receive a product order request

#### Examples

| example |
| --- |
| customerReadyToPlaceOrder |

#### Scenario: Unverified with no bypass and no portability

*Given* the Customer is not verified and the plan does not bypass verification
*When* the Customer places the product order
*Then* My Paradise does not send a product order to Mavenir
*And* the cart is marked to submit the order later
*When* My Paradise reloads the cart
*Then* the Customer onboarding is done

#### Examples

| example |
| --- |
| reloadCart |
| customerReadyToPlaceOrder |
### (S) --> View Order Result

#### Scenario: View order result: ${example}

*Given* the order result is ${example}
*When* the Customer views their order result

#### Examples

| example |
| --- |
| reloadCart |
| customerReadyToPlaceOrder |
### (S) --> Create Order Ticket

#### Scenario: Create order ticket: ${example}

*Given* the Customer ${example}
*When* the Customer creates the order ticket
*Then* My Paradise sends the ${subject} ticket to Zendesk
*When* Zendesk creates the ticket
*Then* the ticket is created for the Customer

#### Examples

| example |
| --- |
| customerReadyToPlaceOrder |
| expectedTicketRequest |
| requesterName |
## (E) Sign In With Existing Account
### (S) --> Sign In With Existing Account

#### Scenario: Sign in with already-registered account credentials

*Given* Cognito has an already-registered Cognito user
*And* the Customer is not signed in
*And* the Customer has already-registered account credentials
*When* the Customer authenticates already-registered account credentials
*Then* My Paradise sends the sign-in request to Cognito
*When* Cognito authenticates the account and issues an account token
*Then* My Paradise stores the signed-in Cognito user
*And* the Cognito user has the Mavenir customer id

#### Examples

| example |
| --- |
| enteredAlreadyRegisteredAccountCredentials |
| storedAlreadyRegisteredCognitoUser |

#### Scenario: Email format is unmet

*Given* the Customer has invalid email format account credentials
*When* the Customer authenticates invalid email format
*Then* My Paradise does not send a sign-in request to Cognito
*And* the authentication is rejected
*And* Cognito does not issue an account token

#### Examples

| example |
| --- |
| enteredInvalidEmailFormat |

#### Scenario: Authenticate with incorrect account credentials: ${example}

*Given* Cognito has an already-registered Cognito user
*And* the Customer is not signed in
*And* the Customer has ${example}
*When* the Customer authenticates ${example}
*Then* My Paradise sends the sign-in request to Cognito
*When* Cognito returns NotAuthorizedException
*Then* the authentication is rejected
*And* Cognito does not issue an account token

#### Examples

| example |
| --- |
| enteredAlreadyRegisteredAccountCredentials |
| storedAlreadyRegisteredCognitoUser |

#### Scenario: Authenticate with unconfirmed account

*Given* Cognito has an unconfirmed Cognito user
*And* the Customer is not signed in
*And* the Customer has unconfirmed sign-in account credentials
*When* the Customer authenticates unconfirmed sign-in
*Then* My Paradise sends the sign-in request to Cognito
*When* Cognito returns CONFIRM_SIGN_UP
*Then* the authentication is rejected as unconfirmed
*And* Cognito does not issue an account token

#### Examples

| example |
| --- |
| enteredValidAccountCredentials |
| storedUnconfirmedCognitoUser |

#### Scenario: Password reset required

*Given* Cognito has an already-registered Cognito user
*And* Cognito requires a password reset for already-registered account credentials
*And* the Customer is not signed in
*And* the Customer has already-registered account credentials
*When* the Customer authenticates already-registered account credentials
*Then* My Paradise sends the sign-in request to Cognito
*When* Cognito returns PasswordResetRequiredException
*Then* the authentication requires a password reset
*And* Cognito does not issue an account token

#### Examples

| example |
| --- |
| enteredAlreadyRegisteredAccountCredentials |
| storedAlreadyRegisteredCognitoUser |

#### Scenario: New password required

*Given* Cognito has an already-registered Cognito user
*And* Cognito requires a new password for already-registered account credentials
*And* the Customer is not signed in
*And* the Customer has already-registered account credentials
*When* the Customer authenticates already-registered account credentials
*Then* My Paradise sends the sign-in request to Cognito
*When* Cognito returns CONFIRM_SIGN_IN_WITH_NEW_PASSWORD_REQUIRED
*Then* the authentication requires a new password
*And* Cognito does not issue an account token

#### Examples

| example |
| --- |
| enteredAlreadyRegisteredAccountCredentials |
| storedAlreadyRegisteredCognitoUser |