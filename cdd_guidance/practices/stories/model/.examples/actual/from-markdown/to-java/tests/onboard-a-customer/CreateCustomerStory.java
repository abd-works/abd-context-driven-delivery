// Epic: Create Customer
// Orders: 0.0.1

/** Story: Enter Account Credentials
 * background-examples: {"email required": {"account credential requirements": "account credential requirements", "example": "email required", "field": "email", "requirement": "Email is required", "group": "Account credential requirements"}, "email format": {"account credential requirements": "account credential requirements", "example": "email format", "field": "email", "requirement": "Please use a valid email format: [yourname@domain.com](mailto:yourname@domain.com)", "group": "Account credential requirements"}, "password letters": {"account credential requirements": "account credential requirements", "example": "password letters", "field": "password", "requirement": "Password must contain uppercase and lowercase letters", "group": "Account credential requirements"}, "password number": {"account credential requirements": "account credential requirements", "example": "password number", "field": "password", "requirement": "Password must have at least one number", "group": "Account credential requirements"}, "password symbol": {"account credential requirements": "account credential requirements", "example": "password symbol", "field": "password", "requirement": "Password must have at least one symbol", "group": "Account credential requirements"}, "password length": {"account credential requirements": "account credential requirements", "example": "password length", "field": "password", "requirement": "Length must be greater than 8 characters", "group": "Account credential requirements"}, "confirm required": {"account credential requirements": "account credential requirements", "example": "confirm required", "field": "confirmPassword", "requirement": "Confirm Password is required", "group": "Account credential requirements"}, "confirm mismatch": {"account credential requirements": "account credential requirements", "example": "confirm mismatch", "field": "confirmPassword", "requirement": "Passwords don't match", "group": "Account credential requirements"}, "example": {"account credential requirements": "account credentials", "example": "example", "field": "unmet", "requirement": "Create account", "group": "Account credential requirements"}, "valid account credentials": {"account credential requirements": "account credentials", "example": "valid account credentials", "field": "", "requirement": "enabled", "group": "Account credential requirements"}, "Paradise Mobile account credentials": {"account credential requirements": "account credentials", "example": "Paradise Mobile account credentials", "field": "", "requirement": "enabled", "group": "Account credential requirements"}, "invalid password letters": {"account credential requirements": "account credentials", "example": "invalid password letters", "field": "Password must contain uppercase and lowercase letters", "requirement": "disabled", "group": "Account credential requirements"}, "invalid password number": {"account credential requirements": "account credentials", "example": "invalid password number", "field": "Password must have at least one number", "requirement": "disabled", "group": "Account credential requirements"}, "invalid password symbol": {"account credential requirements": "account credentials", "example": "invalid password symbol", "field": "Password must have at least one symbol", "requirement": "disabled", "group": "Account credential requirements"}, "invalid password length": {"account credential requirements": "account credentials", "example": "invalid password length", "field": "Length must be greater than 8 characters", "requirement": "disabled", "group": "Account credential requirements"}, "invalid confirm required": {"account credential requirements": "account credentials", "example": "invalid confirm required", "field": "Confirm Password is required", "requirement": "disabled", "group": "Account credential requirements"}, "invalid confirm mismatch": {"account credential requirements": "account credentials", "example": "invalid confirm mismatch", "field": "Passwords don't match", "requirement": "disabled", "group": "Account credential requirements"}, "invalid email required": {"account credential requirements": "account credentials", "example": "invalid email required", "field": "Email is required", "requirement": "disabled", "group": "Account credential requirements"}, "invalid email format": {"account credential requirements": "account credentials", "example": "invalid email format", "field": "Please use a valid email format: [yourname@domain.com](mailto:yourname@domain.com)", "requirement": "disabled", "group": "Account credential requirements"}}
 * BACKGROUND: background
 * SCENARIO: Enter new account credentials
 * background: background
 * background-step: Given | the plan catalog contains purchasable plans
 * background-step: And | the User has selected ++plan++ ++Essentials++ on the Paradise Mobile site
 * WHEN: the User proceeds to create an account from the Paradise Mobile website
 * THEN: the User can enter ++account credentials++
 * AND: ++account credential requirements++ are shown in black (Email is required, password rules)
 * AND: the Create account operation is disabled
 * AND: the User can Sign in
 * AND: the User can go Back
 * AND: the User can open Service Agreement, Terms and Conditions, and Privacy Policy
 * WHEN: the User validates ++account credentials++ {example}
 * THEN: ++account credentials++ are validated continuously as the User types
 * AND: unmet ++account credential requirements++ {unmet} are red with ✖
 * AND: the Create account button is {Create account}
 * WHEN: the User clicks on Create account
 * THEN: the system creates an unconfirmed Cognito user routing through Amplify to Cognito
 * AND: the User is forwarded to check their email
 * SCENARIO: Paradise Mobile email
 * background: background
 * background-step: Given | the plan catalog contains purchasable plans
 * background-step: And | the User has selected ++plan++ ++Essentials++ on the Paradise Mobile site
 * WHEN: the User enters ++account credentials++ ++Paradise Mobile account credentials++
 * THEN: the Create Account title is blue
 * SCENARIO: Email already registered
 * background: background
 * background-step: Given | the plan catalog contains purchasable plans
 * background-step: And | the User has selected ++plan++ ++Essentials++ on the Paradise Mobile site
 * GIVEN: ++account credentials++ ++already-registered account credentials++ are already registered
 * WHEN: the User registers ++account credentials++ ++already-registered account credentials++
 * THEN: Email shows the already-registered error
 */

/** Story: Create Unconfirmed Cognito User
 * SCENARIO: Create Unconfirmed Cognito User
 * background: background
 * background-step: Given | no ++Cognito user++ exists for ++account credentials++ ++valid account credentials++
 * WHEN: Cognito is asked to register ++account credentials++ ++valid account credentials++
 * THEN: Cognito creates ++Cognito user++ ++unconfirmed Cognito user++
 * AND: Cognito emails a ++validation code++ for those ++account credentials++
 * BUT: no ++account token++ is issued
 * BUT: no ++Mavenir customer++ exists for those ++account credentials++
 * SCENARIO: Email already registered in Cognito
 * background: background
 * background-step: Given | no ++Cognito user++ exists for ++account credentials++ ++valid account credentials++
 * GIVEN: ++Cognito user++ ++unconfirmed Cognito user++ exists for ++account credentials++ ++already-registered account credentials++
 * WHEN: Cognito is asked to register ++account credentials++ ++already-registered account credentials++
 * THEN: Cognito returns ++UsernameExistsException++
 * AND: Cognito does not create another ++Cognito user++ for those ++account credentials++
 * SCENARIO: Cognito register fails with another error
 * background: background
 * background-step: Given | no ++Cognito user++ exists for ++account credentials++ ++valid account credentials++
 */

/** Story: Enter Validation Code
 * Actor: My Paradise
 * background-examples: {"valid validation code": {"validation code": "validation code", "example": "valid validation code", "code": "123456", "group": "validation code"}, "mismatch validation code": {"validation code": "validation code", "example": "mismatch validation code", "code": "Hmm. That code didn't work.", "group": "validation code"}, "expired validation code": {"validation code": "validation code", "example": "expired validation code", "code": "Hmm. That code didn't work.", "group": "validation code"}, "attempts exceeded validation code": {"validation code": "validation code", "example": "attempts exceeded validation code", "code": "Attempts limit exceeded. Please try again later.", "group": "validation code"}, "example": {"validation code": "validation code", "example": "example", "code": "helper", "group": "validation code"}}
 * BACKGROUND: background
 * SCENARIO: Enter validation code
 * background: background
 * background-step: Given | the User has submitted ++account credentials++ ++valid account credentials++
 * background-step: And | Cognito has an ++Cognito user++ ++unconfirmed Cognito user++
 * WHEN: the User proceeds to check their email
 * THEN: the User sees the code was sent to *[Jeff.anderson@Abdworks.com](mailto:Jeff.anderson@Abdworks.com)*
 * AND: the User can enter a ++validation code++ in Enter Validation Code
 * AND: the User can Resend
 * AND: the User can Close
 * AND: the Activate account operation is disabled
 * WHEN: the User enters a ++validation code++ ++valid validation code++
 * THEN: the Activate account operation is enabled
 * WHEN: the User clicks Activate account
 * THEN: the system confirms the ++Cognito user++ routing through Amplify to Cognito
 * AND: the User is forwarded to onboarding
 * SCENARIO: Activate with unusable validation code
 * background: background
 * background-step: Given | the User has submitted ++account credentials++ ++valid account credentials++
 * background-step: And | Cognito has an ++Cognito user++ ++unconfirmed Cognito user++
 * WHEN: the User clicks Activate account with ++validation code++ {scenario}
 * THEN: Enter Validation Code shows helper text {helper}
 * SCENARIO: Resend validation code
 * background: background
 * background-step: Given | the User has submitted ++account credentials++ ++valid account credentials++
 * background-step: And | Cognito has an ++Cognito user++ ++unconfirmed Cognito user++
 * WHEN: the User clicks Resend
 * THEN: the system emails a new ++validation code++ routing through Amplify to Cognito
 * AND: the User sees *We sent you a new code. Please check your email.*
 * AND: Resend waits 60 seconds before it can be used again
 */

/** Story: Confirm Cognito User
 * background-examples: {"mismatch validation code": {"validation code": "validation code", "example": "mismatch validation code", "error": "CodeMismatchException"}, "expired validation code": {"validation code": "validation code", "example": "expired validation code", "error": "ExpiredCodeException"}, "attempts exceeded validation code": {"validation code": "validation code", "example": "attempts exceeded validation code", "error": "LimitExceededException"}}
 * BACKGROUND: background
 * SCENARIO: Confirm Cognito User
 * background: background
 * background-step: Given | Cognito has an ++Cognito user++ ++unconfirmed Cognito user++
 * WHEN: Cognito is asked to confirm the user with a ++validation code++ ++valid validation code++
 * THEN: Cognito confirms the ++Cognito user++
 * BUT: no ++account token++ is issued
 * BUT: no ++Mavenir customer++ exists for those ++account credentials++
 * SCENARIO: Confirm with unusable validation code
 * background: background
 * background-step: Given | Cognito has an ++Cognito user++ ++unconfirmed Cognito user++
 * WHEN: Cognito is asked to confirm the user with ++validation code++ {scenario}
 * THEN: Cognito returns {error}
 * AND: Cognito does not confirm the ++Cognito user++
 */

/** Story: Issue Account Token To Browser Session
 * SCENARIO: Issue Account Token To Browser Session
 * background: background
 * background-step: Given | Cognito has a ++Cognito user++ ++confirmed Cognito user++
 * WHEN: Cognito is asked to authenticate ++account credentials++ ++valid account credentials++
 * THEN: Cognito issues an ++account token++ for the ++Cognito user++
 * BUT: no ++Mavenir customer++ exists for those ++account credentials++
 */

/** Story: Validate Mavenir Customer in Cognito User Attributes
 * SCENARIO: Cognito User already has a Mavenir Customer id
 * background: background
 * background-step: Given | the User is in Account Setup
 * background-step: And | Cognito has issued an ++account token++ for ++account credentials++ ++valid account credentials++
 * GIVEN: the ++Cognito user++ has a ++Mavenir customer++ id
 * WHEN: the User proceeds to Account Setup
 * THEN: My Paradise reads the ++Cognito user++ attributes routing through Amplify to Cognito
 * AND: My Paradise finds the ++Mavenir customer++ id on the ++Cognito user++
 * AND: My Paradise proceeds to load the ++My Paradise customer++ from Midtier
 * SCENARIO: Cognito User has no Mavenir Customer id
 * background: background
 * background-step: Given | the User is in Account Setup
 * background-step: And | Cognito has issued an ++account token++ for ++account credentials++ ++valid account credentials++
 * BUT: no ++Mavenir customer++ exists for those ++account credentials++
 * WHEN: the User proceeds to Account Setup
 * THEN: My Paradise reads the ++Cognito user++ attributes routing through Amplify to Cognito
 * AND: My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++
 */

/** Story: Submit Create Customer Request to Mid-Tier
 * SCENARIO: Submit Create Customer Request to Mid-Tier
 * background: background
 * background-step: Given | the ++Cognito user++ has no ++Mavenir customer++ id
 * background-step: And | the browser session has an ++account token++
 * WHEN: My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++
 * THEN: My Paradise adds a ++Mavenir customer++ through the Midtier
 * SCENARIO: Email already has a Mavenir Customer
 * background: background
 * background-step: Given | the ++Cognito user++ has no ++Mavenir customer++ id
 * background-step: And | the browser session has an ++account token++
 * GIVEN: a ++Mavenir customer++ already exists for that email
 * WHEN: My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++
 * THEN: My Paradise shows *Could not create customer.*
 * SCENARIO: Invalid Account Token
 * background: background
 * background-step: Given | the ++Cognito user++ has no ++Mavenir customer++ id
 * background-step: And | the browser session has an ++account token++
 * GIVEN: the ++account token++ is invalid
 * WHEN: My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++
 * THEN: My Paradise shows *Could not create customer.*
 * SCENARIO: Mavenir is unreachable
 * background: background
 * background-step: Given | the ++Cognito user++ has no ++Mavenir customer++ id
 * background-step: And | the browser session has an ++account token++
 * GIVEN: Mavenir has no HTTP response
 * WHEN: My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++
 * THEN: My Paradise shows *Could not create customer.*
 */

/** Story: Validate Cognito User
 * SCENARIO: Validate Cognito User
 * background: background
 * background-step: Given | the User has an ++account token++
 * WHEN: Midtier is asked to validate the ++account token++
 * THEN: Midtier verifies the ++account token++
 * AND: Midtier reads the email from the ++account token++
 * WHEN: the ++account token++ is invalid
 * THEN: Midtier returns "Invalid token"
 */

/** Story: Submit Create Mavenir Customer
 * SCENARIO: Submit Create Mavenir Customer
 * background: background
 * background-step: Given | Midtier has verified the ++account token++
 * background-step: And | the ++account token++ has an email
 * WHEN: Midtier receives a Paradise request to create a ++PML customer++ with the email from the ++account token++
 * THEN: Midtier maps that request to a Mavenir createaccounts for a ++Mavenir customer++ (email and ++contact medium++ from that email)
 * AND: Midtier submits createaccounts to Mavenir
 * AND: Midtier receives a Mavenir createaccounts response with the ++Mavenir customer++ id
 * AND: Midtier maps that ++Mavenir customer++ id to a ++PML customer++ id
 * AND: Midtier returns the ++PML customer++ id
 * SCENARIO: Mavenir customer already exists
 * background: background
 * background-step: Given | Midtier has verified the ++account token++
 * background-step: And | the ++account token++ has an email
 * GIVEN: a ++Mavenir customer++ already exists for that email
 * WHEN: Midtier receives a Paradise request to create a ++PML customer++ with the email from the ++account token++
 * THEN: Midtier receives a Mavenir createaccounts conflict
 * AND: Midtier maps that conflict to Paradise 409
 * AND: Midtier returns 409
 * SCENARIO: Mavenir is unreachable
 * background: background
 * background-step: Given | Midtier has verified the ++account token++
 * background-step: And | the ++account token++ has an email
 * GIVEN: Mavenir has no HTTP response
 * WHEN: Midtier receives a Paradise request to create a ++PML customer++ with the email from the ++account token++
 * THEN: Midtier maps that missing response to Paradise 504
 * AND: Midtier returns 504
 */

/** Story: Create Customer
 * Actor: My Paradise
 * SCENARIO: Create Customer
 * background: background
 * background-step: Given | no ++Mavenir customer++ for that email
 * background-step: And | Mavenir has that ++account token++ on the create request
 * WHEN: Mavenir is asked to create a ++Mavenir customer++ for that email
 * THEN: Mavenir creates a ++Mavenir customer++
 * AND: Mavenir returns the ++Mavenir customer++ id
 * SCENARIO: Email already has a Mavenir Customer
 * background: background
 * background-step: Given | no ++Mavenir customer++ for that email
 * background-step: And | Mavenir has that ++account token++ on the create request
 * GIVEN: Mavenir has a ++Mavenir customer++ for that email
 * WHEN: Mavenir is asked to create a ++Mavenir customer++ for that email
 * THEN: Mavenir returns a conflict
 */

/** Story: Store Mavenir Customer Id on Cognito User
 * SCENARIO: Store Mavenir Customer Id on Cognito User
 * background: background
 * background-step: Given | My Paradise has added a ++Mavenir customer++ through the Midtier
 * background-step: And | that add returned a ++Mavenir customer++ id
 * WHEN: My Paradise has a ++Mavenir customer++ id from the Midtier
 * THEN: My Paradise stores the ++Mavenir customer++ id on the ++Cognito user++ routing through Amplify to Cognito
 * AND: My Paradise proceeds to load the ++My Paradise customer++ from Midtier
 */

/** Story: Load My Paradise Customer From Midtier And Store In Session
 * SCENARIO: Load My Paradise Customer From Midtier And Store In Session
 * background: background
 * background-step: Given | the browser session has an ++account token++
 * background-step: And | the ++Cognito user++ has a ++Mavenir customer++ id
 * background-step: And | the ++My Paradise customer++ is not in session
 * WHEN: the User proceeds to Account Setup or My Paradise
 * THEN: My Paradise retrieves the ++Mavenir customer++ through the Midtier
 * AND: My Paradise stores the ++My Paradise customer++ in session
 * SCENARIO: Billing account is terminated
 * background: background
 * background-step: Given | the browser session has an ++account token++
 * background-step: And | the ++Cognito user++ has a ++Mavenir customer++ id
 * background-step: And | the ++My Paradise customer++ is not in session
 * GIVEN: the ++Mavenir customer++ billing state is terminated
 * WHEN: the User proceeds to Account Setup or My Paradise
 * THEN: My Paradise signs the User out
 * AND: My Paradise shows the terminated-account message
 * SCENARIO: Load customer fails
 * background: background
 * background-step: Given | the browser session has an ++account token++
 * background-step: And | the ++Cognito user++ has a ++Mavenir customer++ id
 * background-step: And | the ++My Paradise customer++ is not in session
 * WHEN: the User proceeds to Account Setup or My Paradise
 * THEN: My Paradise signs the User out
 * AND: My Paradise shows *Something went wrong when loading your account*
 */

/** Story: Get Mavenir Customer and Transform To My Paradise Customer And Return
 * SCENARIO: Get Mavenir Customer and Transform To My Paradise Customer And Return
 * background: background
 * background-step: Given | Midtier has verified the ++account token++
 * background-step: And | the ++account token++ has a ++Mavenir customer++ id
 * background-step: And | Mavenir has a new Mavenir customer (`++new Mavenir customer++` row)
 * WHEN: Midtier receives a Paradise request to get a ++PML customer++
 * THEN: Midtier maps that request to a Mavenir customerDetails get for the ++Mavenir customer++ ++new Mavenir customer++
 * AND: Midtier submits customerDetails to Mavenir
 * AND: Midtier receives the ++Mavenir customer++ ++new Mavenir customer++
 * AND: Midtier maps that ++Mavenir customer++ to a new ++PML customer++
 * AND: Midtier returns the new ++PML customer++
 */

/** Story: Get Mavenir Customer
 * SCENARIO: Get Mavenir Customer
 * background: background
 * background-step: Given | Mavenir has a new Mavenir customer (`++new Mavenir customer++` row)
 * WHEN: Mavenir is asked to get the ++Mavenir customer++
 * THEN: Mavenir returns the ++Mavenir customer++ ++new Mavenir customer++
 */

/** Story: Fix Orphan Cognito Account
 * SCENARIO: Fix Orphan Cognito Account
 * background: background
 * background-step: Given | the User has clicked Create account with ++account credentials++ ++valid account credentials++
 * background-step: And | Cognito has an ++Cognito user++ ++unconfirmed Cognito user++
 * background-step: But | the User has not entered a ++validation code++
 * background-step: And | no ++account token++ is issued
 * WHEN: Care is asked to fix the orphan ++Cognito user++
 * THEN: Care changes the email in Mavenir DEP
 * AND: Care does not delete the ++Cognito user++
 */

/** Story: Read False Initial Activation
 * SCENARIO: Read False Initial Activation
 * background: background
 * background-step: Given | Mavenir has a ++Mavenir customer++
 * background-step: And | that ++Mavenir customer++ has a ++Mavenir shopping cart++
 * background-step: But | that ++Mavenir customer++ has no ++billing account++
 * WHEN: Care is asked to read the ++Mavenir customer++ in DEP
 * THEN: Care sees Initial Activation
 */

/** Story: Sign In With Existing Account
 * SCENARIO: Sign in with already-registered account credentials
 * GIVEN: Cognito has ++Cognito user++ ++already-registered Cognito user++
 * AND: the Customer is not signed in
 * AND: the Customer has ++account credentials++ ++already-registered account credentials++
 * WHEN: the Customer authenticates ++account credentials++ ++already-registered account credentials++
 * THEN: My Paradise sends the sign-in request to Cognito
 * WHEN: Cognito authenticates the account and issues an ++account token++
 * THEN: My Paradise stores ++Cognito user++ ++signed-in Cognito user++
 * AND: the Cognito user has the Mavenir customer id
 * SCENARIO: Email format is unmet
 * GIVEN: the Customer has ++account credentials++ ++invalid email format++
 * WHEN: the Customer authenticates ++account credentials++ ++invalid email format++
 * THEN: My Paradise does not send a sign-in request to Cognito
 * AND: the authentication is rejected
 * AND: Cognito does not issue an ++account token++
 * SCENARIO: Authenticate with incorrect account credentials
 * GIVEN: Cognito has ++Cognito user++ ++already-registered Cognito user++
 * AND: the Customer has ++account credentials++ {example}
 * WHEN: the Customer authenticates ++account credentials++ {example}
 * THEN: My Paradise sends the sign-in request to Cognito
 * WHEN: Cognito returns ++NotAuthorizedException++
 * THEN: the authentication is rejected
 * AND: Cognito does not issue an ++account token++
 * SCENARIO: Authenticate with unconfirmed account
 * GIVEN: Cognito has ++Cognito user++ ++unconfirmed Cognito user++
 * WHEN: the Customer authenticates ++account credentials++ ++unconfirmed sign-in++
 * THEN: My Paradise sends the sign-in request to Cognito
 * WHEN: Cognito returns ++CONFIRM_SIGN_UP++
 * THEN: the authentication is rejected as unconfirmed
 * AND: Cognito does not issue an ++account token++
 * SCENARIO: Password reset required
 * GIVEN: Cognito has ++Cognito user++ ++already-registered Cognito user++
 * AND: Cognito requires a password reset for ++already-registered account credentials++
 * AND: the Customer has ++account credentials++ ++already-registered account credentials++
 * WHEN: the Customer authenticates ++account credentials++ ++already-registered account credentials++
 * THEN: My Paradise sends the sign-in request to Cognito
 * WHEN: Cognito returns ++PasswordResetRequiredException++
 * THEN: the authentication requires a password reset
 * AND: Cognito does not issue an ++account token++
 * SCENARIO: New password required
 * GIVEN: Cognito has ++Cognito user++ ++already-registered Cognito user++
 * AND: Cognito requires a new password for ++already-registered account credentials++
 * AND: the Customer has ++account credentials++ ++already-registered account credentials++
 * WHEN: the Customer authenticates ++account credentials++ ++already-registered account credentials++
 * THEN: My Paradise sends the sign-in request to Cognito
 * WHEN: Cognito returns ++CONFIRM_SIGN_IN_WITH_NEW_PASSWORD_REQUIRED++
 * THEN: the authentication requires a new password
 * AND: Cognito does not issue an ++account token++
 */
