# (E) Onboard A Customer
## (E) Get Sign Up Plan
### (S) Website --> Hand Off Sign Up To Onboarding
### (S) Customer --> Open Plan Deep Link

#### Scenario Outline: Open Plan Deep Link

#### Background

*Given* the plan catalog contains purchasable plans
*And* the Customer arrived at sign-up from the Paradise Mobile website

*When* the Customer opens a plan deep link for ++plan++ ++{scenario}++
*Then* ++{scenario}++ is selected
*And* the Customer continues to Enter Account Credentials

#### Scenario: Unknown plan deep link

#### Background

*Given* the plan catalog contains purchasable plans
*And* the Customer arrived at sign-up from the Paradise Mobile website

*Given* the plan catalog contains purchasable plans
*But* the deep-link plan id is not in the catalog
*When* the Customer opens a plan deep link
*Then* the plan is not found
### (S) My Paradise --> Load Plan Catalog
### (S) Customer --> Apply Catalog Voucher

#### Scenario: Apply Catalog Voucher via deep link

#### Background

*Given* the plan catalog contains purchasable plans

*Given* Vouchera has ++catalog voucher++ ++valid catalog voucher++
*When* the Customer applies ++catalog voucher++ ++valid catalog voucher++ from a promotional voucher link
*Then* My Paradise sends the voucher code to Vouchera
*When* Vouchera returns the voucher view
*Then* the catalog voucher is applied
*And* the voucher discounts ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, and ++plan++ ++Atlas++ by 10 percent

#### Scenario: Apply Catalog Voucher manually

#### Background

*Given* the plan catalog contains purchasable plans

*Given* the Customer is selecting a plan
*And* Vouchera has ++catalog voucher++ ++valid catalog voucher++
*When* the Customer applies ++catalog voucher++ ++valid catalog voucher++
*Then* My Paradise sends the voucher code to Vouchera
*When* Vouchera returns the voucher view
*Then* the catalog voucher is applied
*And* the voucher discounts ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, and ++plan++ ++Atlas++ by 10 percent

#### Scenario: Short catalog voucher code is rejected

#### Background

*Given* the plan catalog contains purchasable plans

*Given* the Customer is selecting a plan
*When* the Customer applies a catalog voucher shorter than 4 characters
*Then* the catalog voucher is rejected
*And* Vouchera is not asked for the voucher

#### Scenario: Remove Catalog Voucher

#### Background

*Given* the plan catalog contains purchasable plans

*Given* the Customer is selecting a plan with ++catalog voucher++ ++valid catalog voucher++ applied
*When* the Customer removes ++catalog voucher++ ++valid catalog voucher++
*Then* the catalog has no catalog voucher

#### Scenario Outline: Apply unusable catalog voucher

#### Background

*Given* the plan catalog contains purchasable plans

*Given* the Customer is selecting a plan
*And* Vouchera has ++catalog voucher++ ++{scenario}++
*When* the Customer applies ++{scenario}++
*Then* My Paradise sends the voucher code to Vouchera
*When* Vouchera returns
*Then* the catalog voucher is rejected
## (E) Create Customer
### (S) --> Enter Account Credentials

#### Examples

#### Account credential requirements

| account credential requirements | example | field | requirement | group |
| --- | --- | --- | --- | --- |
| account credential requirements | email required | email | Email is required | Account credential requirements |
| account credential requirements | email format | email | Please use a valid email format: yourname@domain.com | Account credential requirements |
| account credential requirements | password letters | password | Password must contain uppercase and lowercase letters | Account credential requirements |
| account credential requirements | password number | password | Password must have at least one number | Account credential requirements |
| account credential requirements | password symbol | password | Password must have at least one symbol | Account credential requirements |
| account credential requirements | password length | password | Length must be greater than 8 characters | Account credential requirements |
| account credential requirements | confirm required | confirmPassword | Confirm Password is required | Account credential requirements |
| account credential requirements | confirm mismatch | confirmPassword | Passwords don't match | Account credential requirements |
| account credentials | example | unmet | Create account | Account credential requirements |
| account credentials | valid account credentials |  | enabled | Account credential requirements |
| account credentials | Paradise Mobile account credentials |  | enabled | Account credential requirements |
| account credentials | invalid password letters | Password must contain uppercase and lowercase letters | disabled | Account credential requirements |
| account credentials | invalid password number | Password must have at least one number | disabled | Account credential requirements |
| account credentials | invalid password symbol | Password must have at least one symbol | disabled | Account credential requirements |
| account credentials | invalid password length | Length must be greater than 8 characters | disabled | Account credential requirements |
| account credentials | invalid confirm required | Confirm Password is required | disabled | Account credential requirements |
| account credentials | invalid confirm mismatch | Passwords don't match | disabled | Account credential requirements |
| account credentials | invalid email required | Email is required | disabled | Account credential requirements |
| account credentials | invalid email format | Please use a valid email format: yourname@domain.com | disabled | Account credential requirements |

#### Scenario Outline: Enter new account credentials

#### Background

*Given* the plan catalog contains purchasable plans
*And* the User has selected ++plan++ ++Essentials++ on the Paradise Mobile site

*When* the User proceeds to create an account from the Paradise Mobile website
*Then* the User can enter ++account credentials++
*And* ++account credential requirements++ are shown in black (Email is required, password rules)
*And* the Create account operation is disabled
*And* the User can Sign in
*And* the User can go Back
*And* the User can open Service Agreement, Terms and Conditions, and Privacy Policy
*When* the User validates ++account credentials++ {example}
*Then* ++account credentials++ are validated continuously as the User types
*And* unmet ++account credential requirements++ {unmet} are red with ✖
*And* the Create account button is {Create account}
*When* the User clicks on Create account
*Then* the system creates an unconfirmed Cognito user routing through Amplify to Cognito
*And* the User is forwarded to check their email

#### Scenario: Paradise Mobile email

#### Background

*Given* the plan catalog contains purchasable plans
*And* the User has selected ++plan++ ++Essentials++ on the Paradise Mobile site

*When* the User enters ++account credentials++ ++Paradise Mobile account credentials++
*Then* the Create Account title is blue

#### Scenario: Email already registered

#### Background

*Given* the plan catalog contains purchasable plans
*And* the User has selected ++plan++ ++Essentials++ on the Paradise Mobile site

*Given* ++account credentials++ ++already-registered account credentials++ are already registered
*When* the User registers ++account credentials++ ++already-registered account credentials++
*Then* Email shows the already-registered error
### (S) --> Create Unconfirmed Cognito User

#### Scenario: Create Unconfirmed Cognito User

#### Background

*Given* no ++Cognito user++ exists for ++account credentials++ ++valid account credentials++

*When* Cognito is asked to register ++account credentials++ ++valid account credentials++
*Then* Cognito creates ++Cognito user++ ++unconfirmed Cognito user++
*And* Cognito emails a ++validation code++ for those ++account credentials++
*But* no ++account token++ is issued
*But* no ++Mavenir customer++ exists for those ++account credentials++

#### Scenario: Email already registered in Cognito

#### Background

*Given* no ++Cognito user++ exists for ++account credentials++ ++valid account credentials++

*Given* ++Cognito user++ ++unconfirmed Cognito user++ exists for ++account credentials++ ++already-registered account credentials++
*When* Cognito is asked to register ++account credentials++ ++already-registered account credentials++
*Then* Cognito returns ++UsernameExistsException++
*And* Cognito does not create another ++Cognito user++ for those ++account credentials++

#### Scenario: Cognito register fails with another error

#### Background

*Given* no ++Cognito user++ exists for ++account credentials++ ++valid account credentials++
### (S) My Paradise --> Enter Validation Code

#### Examples

#### validation code

| validation code | example | code | group |
| --- | --- | --- | --- |
| validation code | valid validation code | 123456 | validation code |
| validation code | mismatch validation code | Hmm. That code didn't work. | validation code |
| validation code | expired validation code | Hmm. That code didn't work. | validation code |
| validation code | attempts exceeded validation code | Attempts limit exceeded. Please try again later. | validation code |
| validation code | example | helper | validation code |

#### Scenario: Enter validation code

#### Background

*Given* the User has submitted ++account credentials++ ++valid account credentials++
*And* Cognito has an ++Cognito user++ ++unconfirmed Cognito user++

*When* the User proceeds to check their email
*Then* the User sees the code was sent to *Jeff.anderson@Abdworks.com*
*And* the User can enter a ++validation code++ in Enter Validation Code
*And* the User can Resend
*And* the User can Close
*And* the Activate account operation is disabled
*When* the User enters a ++validation code++ ++valid validation code++
*Then* the Activate account operation is enabled
*When* the User clicks Activate account
*Then* the system confirms the ++Cognito user++ routing through Amplify to Cognito
*And* the User is forwarded to onboarding

#### Scenario Outline: Activate with unusable validation code

#### Background

*Given* the User has submitted ++account credentials++ ++valid account credentials++
*And* Cognito has an ++Cognito user++ ++unconfirmed Cognito user++

*When* the User clicks Activate account with ++validation code++ {scenario}
*Then* Enter Validation Code shows helper text {helper}

#### Scenario: Resend validation code

#### Background

*Given* the User has submitted ++account credentials++ ++valid account credentials++
*And* Cognito has an ++Cognito user++ ++unconfirmed Cognito user++

*When* the User clicks Resend
*Then* the system emails a new ++validation code++ routing through Amplify to Cognito
*And* the User sees *We sent you a new code. Please check your email.*
*And* Resend waits 60 seconds before it can be used again
### (S) --> Confirm Cognito User

#### Examples

| validation code | example | error |
| --- | --- | --- |
| validation code | mismatch validation code | CodeMismatchException |
| validation code | expired validation code | ExpiredCodeException |
| validation code | attempts exceeded validation code | LimitExceededException |

#### Scenario: Confirm Cognito User

#### Background

*Given* Cognito has an ++Cognito user++ ++unconfirmed Cognito user++

*When* Cognito is asked to confirm the user with a ++validation code++ ++valid validation code++
*Then* Cognito confirms the ++Cognito user++
*But* no ++account token++ is issued
*But* no ++Mavenir customer++ exists for those ++account credentials++

#### Scenario Outline: Confirm with unusable validation code

#### Background

*Given* Cognito has an ++Cognito user++ ++unconfirmed Cognito user++

*When* Cognito is asked to confirm the user with ++validation code++ {scenario}
*Then* Cognito returns {error}
*And* Cognito does not confirm the ++Cognito user++
### (S) --> Issue Account Token To Browser Session

#### Scenario: Issue Account Token To Browser Session

#### Background

*Given* Cognito has a ++Cognito user++ ++confirmed Cognito user++

*When* Cognito is asked to authenticate ++account credentials++ ++valid account credentials++
*Then* Cognito issues an ++account token++ for the ++Cognito user++
*But* no ++Mavenir customer++ exists for those ++account credentials++
### (S) --> Validate Mavenir Customer in Cognito User Attributes

#### Scenario: Cognito User already has a Mavenir Customer id

#### Background

*Given* the User is in Account Setup
*And* Cognito has issued an ++account token++ for ++account credentials++ ++valid account credentials++

*Given* the ++Cognito user++ has a ++Mavenir customer++ id
*When* the User proceeds to Account Setup
*Then* My Paradise reads the ++Cognito user++ attributes routing through Amplify to Cognito
*And* My Paradise finds the ++Mavenir customer++ id on the ++Cognito user++
*And* My Paradise proceeds to load the ++My Paradise customer++ from Midtier

#### Scenario: Cognito User has no Mavenir Customer id

#### Background

*Given* the User is in Account Setup
*And* Cognito has issued an ++account token++ for ++account credentials++ ++valid account credentials++

*But* no ++Mavenir customer++ exists for those ++account credentials++
*When* the User proceeds to Account Setup
*Then* My Paradise reads the ++Cognito user++ attributes routing through Amplify to Cognito
*And* My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++
### (S) --> Submit Create Customer Request to Mid-Tier

#### Scenario: Submit Create Customer Request to Mid-Tier

#### Background

*Given* the ++Cognito user++ has no ++Mavenir customer++ id
*And* the browser session has an ++account token++

*When* My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++
*Then* My Paradise adds a ++Mavenir customer++ through the Midtier

#### Scenario: Email already has a Mavenir Customer

#### Background

*Given* the ++Cognito user++ has no ++Mavenir customer++ id
*And* the browser session has an ++account token++

*Given* a ++Mavenir customer++ already exists for that email
*When* My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++
*Then* My Paradise shows *Could not create customer.*

#### Scenario: Invalid Account Token

#### Background

*Given* the ++Cognito user++ has no ++Mavenir customer++ id
*And* the browser session has an ++account token++

*Given* the ++account token++ is invalid
*When* My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++
*Then* My Paradise shows *Could not create customer.*

#### Scenario: Mavenir is unreachable

#### Background

*Given* the ++Cognito user++ has no ++Mavenir customer++ id
*And* the browser session has an ++account token++

*Given* Mavenir has no HTTP response
*When* My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++
*Then* My Paradise shows *Could not create customer.*
### (S) --> Validate Cognito User

#### Scenario: Validate Cognito User

#### Background

*Given* the User has an ++account token++

*When* Midtier is asked to validate the ++account token++
*Then* Midtier verifies the ++account token++
*And* Midtier reads the email from the ++account token++
*When* the ++account token++ is invalid
*Then* Midtier returns "Invalid token"
### (S) --> Submit Create Mavenir Customer

#### Scenario: Submit Create Mavenir Customer

#### Background

*Given* Midtier has verified the ++account token++
*And* the ++account token++ has an email

*When* Midtier receives a Paradise request to create a ++PML customer++ with the email from the ++account token++
*Then* Midtier maps that request to a Mavenir createaccounts for a ++Mavenir customer++ (email and ++contact medium++ from that email)
*And* Midtier submits createaccounts to Mavenir
*And* Midtier receives a Mavenir createaccounts response with the ++Mavenir customer++ id
*And* Midtier maps that ++Mavenir customer++ id to a ++PML customer++ id
*And* Midtier returns the ++PML customer++ id

#### Scenario: Mavenir customer already exists

#### Background

*Given* Midtier has verified the ++account token++
*And* the ++account token++ has an email

*Given* a ++Mavenir customer++ already exists for that email
*When* Midtier receives a Paradise request to create a ++PML customer++ with the email from the ++account token++
*Then* Midtier receives a Mavenir createaccounts conflict
*And* Midtier maps that conflict to Paradise 409
*And* Midtier returns 409

#### Scenario: Mavenir is unreachable

#### Background

*Given* Midtier has verified the ++account token++
*And* the ++account token++ has an email

*Given* Mavenir has no HTTP response
*When* Midtier receives a Paradise request to create a ++PML customer++ with the email from the ++account token++
*Then* Midtier maps that missing response to Paradise 504
*And* Midtier returns 504
### (S) My Paradise --> Create Customer

#### Scenario: Create Customer

#### Background

*Given* no ++Mavenir customer++ for that email
*And* Mavenir has that ++account token++ on the create request

*When* Mavenir is asked to create a ++Mavenir customer++ for that email
*Then* Mavenir creates a ++Mavenir customer++
*And* Mavenir returns the ++Mavenir customer++ id

#### Scenario: Email already has a Mavenir Customer

#### Background

*Given* no ++Mavenir customer++ for that email
*And* Mavenir has that ++account token++ on the create request

*Given* Mavenir has a ++Mavenir customer++ for that email
*When* Mavenir is asked to create a ++Mavenir customer++ for that email
*Then* Mavenir returns a conflict
### (S) --> Store Mavenir Customer Id on Cognito User

#### Scenario: Store Mavenir Customer Id on Cognito User

#### Background

*Given* My Paradise has added a ++Mavenir customer++ through the Midtier
*And* that add returned a ++Mavenir customer++ id

*When* My Paradise has a ++Mavenir customer++ id from the Midtier
*Then* My Paradise stores the ++Mavenir customer++ id on the ++Cognito user++ routing through Amplify to Cognito
*And* My Paradise proceeds to load the ++My Paradise customer++ from Midtier
### (S) --> Load My Paradise Customer From Midtier And Store In Session

#### Scenario: Load My Paradise Customer From Midtier And Store In Session

#### Background

*Given* the browser session has an ++account token++
*And* the ++Cognito user++ has a ++Mavenir customer++ id
*And* the ++My Paradise customer++ is not in session

*When* the User proceeds to Account Setup or My Paradise
*Then* My Paradise retrieves the ++Mavenir customer++ through the Midtier
*And* My Paradise stores the ++My Paradise customer++ in session

#### Scenario: Billing account is terminated

#### Background

*Given* the browser session has an ++account token++
*And* the ++Cognito user++ has a ++Mavenir customer++ id
*And* the ++My Paradise customer++ is not in session

*Given* the ++Mavenir customer++ billing state is terminated
*When* the User proceeds to Account Setup or My Paradise
*Then* My Paradise signs the User out
*And* My Paradise shows the terminated-account message

#### Scenario: Load customer fails

#### Background

*Given* the browser session has an ++account token++
*And* the ++Cognito user++ has a ++Mavenir customer++ id
*And* the ++My Paradise customer++ is not in session

*When* the User proceeds to Account Setup or My Paradise
*Then* My Paradise signs the User out
*And* My Paradise shows *Something went wrong when loading your account*
### (S) --> Get Mavenir Customer and Transform To My Paradise Customer And Return

#### Scenario: Get Mavenir Customer and Transform To My Paradise Customer And Return

#### Background

*Given* Midtier has verified the ++account token++
*And* the ++account token++ has a ++Mavenir customer++ id
*And* Mavenir has a new Mavenir customer (`++new Mavenir customer++` row)

*When* Midtier receives a Paradise request to get a ++PML customer++
*Then* Midtier maps that request to a Mavenir customerDetails get for the ++Mavenir customer++ ++new Mavenir customer++
*And* Midtier submits customerDetails to Mavenir
*And* Midtier receives the ++Mavenir customer++ ++new Mavenir customer++
*And* Midtier maps that ++Mavenir customer++ to a new ++PML customer++
*And* Midtier returns the new ++PML customer++
### (S) --> Get Mavenir Customer

#### Scenario: Get Mavenir Customer

#### Background

*Given* Mavenir has a new Mavenir customer (`++new Mavenir customer++` row)

*When* Mavenir is asked to get the ++Mavenir customer++
*Then* Mavenir returns the ++Mavenir customer++ ++new Mavenir customer++
### (S) --> Ensure Cart on Customer
### (S) --> Fix Orphan Cognito Account

#### Scenario: Fix Orphan Cognito Account

#### Background

*Given* the User has clicked Create account with ++account credentials++ ++valid account credentials++
*And* Cognito has an ++Cognito user++ ++unconfirmed Cognito user++
*But* the User has not entered a ++validation code++
*And* no ++account token++ is issued

*When* Care is asked to fix the orphan ++Cognito user++
*Then* Care changes the email in Mavenir DEP
*And* Care does not delete the ++Cognito user++
### (S) --> Read False Initial Activation

#### Scenario: Read False Initial Activation

#### Background

*Given* Mavenir has a ++Mavenir customer++
*And* that ++Mavenir customer++ has a ++Mavenir shopping cart++
*But* that ++Mavenir customer++ has no ++billing account++

*When* Care is asked to read the ++Mavenir customer++ in DEP
*Then* Care sees Initial Activation
### (S) --> Sign In With Existing Account

#### Scenario: Sign in with already-registered account credentials

*Given* Cognito has ++Cognito user++ ++already-registered Cognito user++
*And* the Customer is not signed in
*And* the Customer has ++account credentials++ ++already-registered account credentials++
*When* the Customer authenticates ++account credentials++ ++already-registered account credentials++
*Then* My Paradise sends the sign-in request to Cognito
*When* Cognito authenticates the account and issues an ++account token++
*Then* My Paradise stores ++Cognito user++ ++signed-in Cognito user++
*And* the Cognito user has the Mavenir customer id

#### Scenario: Email format is unmet

*Given* the Customer has ++account credentials++ ++invalid email format++
*When* the Customer authenticates ++account credentials++ ++invalid email format++
*Then* My Paradise does not send a sign-in request to Cognito
*And* the authentication is rejected
*And* Cognito does not issue an ++account token++

#### Scenario Outline: Authenticate with incorrect account credentials

*Given* Cognito has ++Cognito user++ ++already-registered Cognito user++
*And* the Customer has ++account credentials++ {example}
*When* the Customer authenticates ++account credentials++ {example}
*Then* My Paradise sends the sign-in request to Cognito
*When* Cognito returns ++NotAuthorizedException++
*Then* the authentication is rejected
*And* Cognito does not issue an ++account token++

#### Scenario: Authenticate with unconfirmed account

*Given* Cognito has ++Cognito user++ ++unconfirmed Cognito user++
*When* the Customer authenticates ++account credentials++ ++unconfirmed sign-in++
*Then* My Paradise sends the sign-in request to Cognito
*When* Cognito returns ++CONFIRM_SIGN_UP++
*Then* the authentication is rejected as unconfirmed
*And* Cognito does not issue an ++account token++

#### Scenario: Password reset required

*Given* Cognito has ++Cognito user++ ++already-registered Cognito user++
*And* Cognito requires a password reset for ++already-registered account credentials++
*And* the Customer has ++account credentials++ ++already-registered account credentials++
*When* the Customer authenticates ++account credentials++ ++already-registered account credentials++
*Then* My Paradise sends the sign-in request to Cognito
*When* Cognito returns ++PasswordResetRequiredException++
*Then* the authentication requires a password reset
*And* Cognito does not issue an ++account token++

#### Scenario: New password required

*Given* Cognito has ++Cognito user++ ++already-registered Cognito user++
*And* Cognito requires a new password for ++already-registered account credentials++
*And* the Customer has ++account credentials++ ++already-registered account credentials++
*When* the Customer authenticates ++account credentials++ ++already-registered account credentials++
*Then* My Paradise sends the sign-in request to Cognito
*When* Cognito returns ++CONFIRM_SIGN_IN_WITH_NEW_PASSWORD_REQUIRED++
*Then* the authentication requires a new password
*And* Cognito does not issue an ++account token++
## (E) Get Number
### (S) Customer --> Determine Number

#### Examples

#### available number

| available number | example | number | group |
| --- | --- | --- | --- |
| available number | held available number | 4415550100 | available number |
| available number | chosen available number | 4415550101 | available number |

#### search term

| search term | example | input | converted | group |
| --- | --- | --- | --- | --- |
| search term | James search | JAMES | 52637 | search term |

#### Scenario: View available numbers

#### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++

*But* no ++MSISDN++ is in the ++Mavenir shopping cart++
*When* the Prospect proceeds to selecting their number
*Then* My Paradise loads ++available number++ inventory through the Midtier
*And* the Prospect sees ++available number++ ++held available number++ and ++available number++ ++chosen available number++ in the Available Number list
*And* the Prospect can Bring your mobile number
*And* the Prospect can search for numbers (up to 5 characters: letters or numbers)
*And* the Prospect can Refresh
*And* the Continue operation is disabled
*When* the Prospect selects ++available number++ ++chosen available number++
*Then* the Continue operation is enabled

#### Scenario: View available numbers — MSISDN in cart

#### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++

*Given* ++MSISDN++ ++available number++ ++held available number++ is in the ++Mavenir shopping cart++
*When* the Prospect proceeds to selecting their number
*Then* the Prospect sees their number is ++available number++ ++held available number++
*And* the Pick new number operation is disabled
*And* the Keep current number operation is enabled
*When* the Prospect selects ++available number++ ++chosen available number++
*Then* the Pick new number operation is enabled

#### Scenario: Refresh available numbers

#### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++

*When* the Prospect clicks Refresh
*Then* My Paradise loads a fresh set of ++available number++ through the Midtier
*And* the Prospect sees a new Available Number list
*And* the Continue operation is disabled

#### Scenario: Search for a number

#### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++

*When* the Prospect enters ++search term++ ++James search++ in the search field
*Then* the search field helper shows *Your number: JAMES (52637)*
*When* the Prospect triggers the search
*Then* My Paradise loads Available Numbers matching ++search term++ ++James search++ through the Midtier
### (S) --> Query Msisdn Inventory

#### Scenario: Query MSISDN inventory for porting

*Given* a ++PML customer++ is authenticated in Midtier
*And* ++portability++ is in the portability request
*When* Midtier queries ++MSISDN++ inventory for a temporary port-in number (`count: 1`)
*Then* Midtier queries Mavenir for 1 available ++MSISDN++ resource
*And* Midtier receives ++available number++ ++held available number++ as the temporary number

#### Scenario: Query MSISDN inventory

*Given* a ++PML customer++ is authenticated in Midtier
*When* Midtier is asked to query ++MSISDN++ inventory
*Then* Midtier queries Mavenir for 5 available ++MSISDN++ resources
*And* Midtier returns a list of ++available number++ values to My Paradise
### (S) --> List Msisdn Resources

#### Scenario: List MSISDN resources for porting

*Given* ++MSISDN++ resources with available status are in the Mavenir inventory
*When* Mavenir is asked to list 1 ++MSISDN++ resource (`/updateAndGetAvailableResources`, `size: 1`)
*Then* Mavenir transitions 1 ++MSISDN++ resource from available to locked
*And* Mavenir returns ++available number++ ++held available number++ as the locked resource to Midtier

#### Scenario: List MSISDN resources

*Given* ++MSISDN++ resources with available status are in the Mavenir inventory
*When* Mavenir is asked to list ++MSISDN++ resources (`/updateAndGetAvailableResources`, `size: 5`)
*Then* Mavenir transitions 5 ++MSISDN++ resources from available to locked
*And* Mavenir returns the list of locked ++available number++ values to Midtier
### (S) --> Search Msisdn Inventory

#### Scenario: Search MSISDN inventory

*Given* a ++PML customer++ is authenticated in Midtier
*When* Midtier is asked to search ++MSISDN++ inventory for ++search term++ ++James search++ (`52637`)
*Then* Midtier queries Mavenir for available ++MSISDN++ resources matching `52637`
*And* Midtier returns matching ++available number++ values to My Paradise
### (S) --> Search Msisdn Resources

#### Scenario: Search MSISDN resources by pattern

*Given* ++MSISDN++ resources with available status are in the Mavenir inventory
*When* Mavenir is asked to search ++MSISDN++ resources with `pattern_search: 52637` (`/updateAndGetAvailableResources`)
*Then* Mavenir transitions matching ++MSISDN++ resources from available to locked
*And* Mavenir returns the matching ++available number++ values to Midtier
### (S) Customer --> Choose a Number

#### Scenario: Pick new number

#### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++

*Given* the Prospect has selected ++available number++ ++chosen available number++
*But* no ++MSISDN++ is in the ++Mavenir shopping cart++
*When* the Prospect clicks Continue
*Then* My Paradise reserves ++available number++ ++chosen available number++ through the Midtier
*And* My Paradise patches the ++Mavenir shopping cart++ with ++available number++ ++chosen available number++ through the Midtier
*And* the Prospect is forwarded to Select Sim

#### Scenario: Pick new number — replace existing

#### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++

*Given* ++MSISDN++ ++available number++ ++held available number++ is in the ++Mavenir shopping cart++
*And* the Prospect has selected ++available number++ ++chosen available number++
*When* the Prospect clicks Pick new number
*Then* My Paradise reserves ++available number++ ++chosen available number++ releasing ++available number++ ++held available number++ through the Midtier
*And* My Paradise patches the ++Mavenir shopping cart++ with ++available number++ ++chosen available number++ through the Midtier
*And* the Prospect is forwarded to Select Sim

#### Scenario: Keep current number

#### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++

*Given* ++MSISDN++ ++available number++ ++held available number++ is in the ++Mavenir shopping cart++
*When* the Prospect clicks Keep current number
*Then* the Prospect is forwarded to Select Sim
### (S) --> Submit Reserve Number Request to Mid-Tier

#### Scenario: Reserve number

#### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++

*Given* ++available number++ ++chosen available number++ is selected
*But* no ++MSISDN++ is in the ++Mavenir shopping cart++
*When* My Paradise posts a reserve request to Midtier for ++available number++ ++chosen available number++
*Then* Midtier returns 204
*And* My Paradise submits a patch cart request with ++available number++ ++chosen available number++ through the Midtier

#### Scenario: Reserve number — replace existing

#### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++

*Given* ++MSISDN++ ++available number++ ++held available number++ is in the ++Mavenir shopping cart++
*And* ++available number++ ++chosen available number++ is selected
*When* My Paradise posts a reserve request to Midtier for ++available number++ ++chosen available number++ with previous ++available number++ ++held available number++
*Then* Midtier returns 204
*And* My Paradise submits a patch cart request with ++available number++ ++chosen available number++ through the Midtier

#### Scenario: Reserve number request fails

#### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++

*Given* ++available number++ ++chosen available number++ is selected
*When* My Paradise posts a reserve request to Midtier for ++available number++ ++chosen available number++
*But* Midtier returns an error
*Then* My Paradise shows *Failed to reserve your number.*
### (S) --> Submit Reserve Msisdn

#### Scenario: Reserve temporary MSISDN for porting

*Given* ++MSISDN++ ++available number++ ++held available number++ is locked
*When* Midtier reserves ++available number++ ++held available number++ as a port-in temporary number (`portin: true`)
*Then* Midtier reserves ++available number++ ++held available number++ in Mavenir with the port-in flag
*And* Midtier returns 204

#### Scenario: Reserve MSISDN

*Given* ++MSISDN++ ++available number++ ++chosen available number++ is locked in Mavenir inventory
*When* Midtier is asked to reserve ++MSISDN++ ++available number++ ++chosen available number++
*Then* Midtier reserves ++available number++ ++chosen available number++ in Mavenir
*And* Midtier returns 204 to My Paradise

#### Scenario: Reserve MSISDN — release previous

*Given* ++MSISDN++ ++available number++ ++chosen available number++ is locked
*And* ++MSISDN++ ++available number++ ++held available number++ is reserved
*When* Midtier is asked to reserve ++available number++ ++chosen available number++ releasing previous ++available number++ ++held available number++
*Then* Midtier reserves ++available number++ ++chosen available number++ and releases ++available number++ ++held available number++ in Mavenir
*And* Midtier returns 204 to My Paradise
### (S) --> Reserve Msisdn Resource

#### Scenario: Reserve MSISDN resource as temporary port-in number

*Given* ++MSISDN++ ++available number++ ++held available number++ is locked in Mavenir inventory
*When* Mavenir is asked to reserve ++available number++ ++held available number++ with `kv_tempNumber: true` (`/updateResources`, locked → reserved, relatedParty: Paradise Mobile)
*Then* Mavenir transitions ++available number++ ++held available number++ from locked to reserved
*And* Mavenir marks ++available number++ ++held available number++ as a temporary port-in number (`kv_tempNumber`)

#### Scenario: Reserve MSISDN resource

*Given* ++MSISDN++ ++available number++ ++chosen available number++ is locked in Mavenir inventory
*When* Mavenir is asked to reserve ++available number++ ++chosen available number++ (`/updateResources`, locked → reserved, relatedParty: Paradise Mobile)
*Then* Mavenir transitions ++available number++ ++chosen available number++ from locked to reserved
*And* Mavenir attaches the Paradise Mobile service provider to ++available number++ ++chosen available number++

#### Scenario: Reserve MSISDN resource — release previous

*Given* ++MSISDN++ ++available number++ ++chosen available number++ is locked
*And* ++MSISDN++ ++available number++ ++held available number++ is reserved
*When* Mavenir is asked to reserve ++available number++ ++chosen available number++ and release previous ++available number++ ++held available number++
*Then* Mavenir transitions ++available number++ ++chosen available number++ from locked to reserved
*And* Mavenir transitions ++available number++ ++held available number++ from reserved to available
### (S) --> Submit Patch Cart With Number Request to Mid-Tier

#### Scenario: Patch cart with number

*Given* ++MSISDN++ ++available number++ ++chosen available number++ has been reserved
*When* My Paradise patches the ++Mavenir shopping cart++ with ++available number++ ++chosen available number++ through the Midtier
*Then* Midtier returns the updated ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++
*And* the Prospect is forwarded to Select Sim

#### Scenario: Patch cart with number fails

*Given* ++MSISDN++ ++available number++ ++chosen available number++ has been reserved
*When* My Paradise patches the ++Mavenir shopping cart++ with ++available number++ ++chosen available number++ through the Midtier
*But* Midtier returns an error
*Then* My Paradise shows *Failed to update your cart.*
### (S) --> Patch Cart With Number

#### Scenario: Patch cart with MSISDN

*Given* a ++PML customer++ with a ++Mavenir shopping cart++
*And* ++MSISDN++ ++available number++ ++chosen available number++ has been reserved
*When* Midtier is asked to patch the ++Mavenir shopping cart++ with ++MSISDN++ ++available number++ ++chosen available number++
*Then* Midtier patches the ++Mavenir shopping cart++ in Mavenir with ++available number++ ++chosen available number++ as the MSISDN characteristic
*And* Midtier returns the updated ++PML customer++ to My Paradise
### (S) --> Patch Shopping Cart

#### Scenario: Patch shopping cart with portability

*Given* a ++Mavenir shopping cart++ with a plan bundle cart item and temporary ++MSISDN++ ++available number++ ++held available number++
*When* Mavenir is asked to patch the ++Mavenir shopping cart++ with ++portability++ ++valid portability++ characteristics
*Then* Mavenir updates the ++Mavenir shopping cart++ cart item with portability characteristics (planName, portinNumber, donorOperator, accountType, userType, accountNumber, device, portin, requestType)
*And* Mavenir returns the updated ++Mavenir shopping cart++ to Midtier

#### Scenario: Patch shopping cart with MSISDN

*Given* a ++Mavenir shopping cart++ with a plan bundle cart item
*But* no MSISDN characteristic on the cart item
*When* Mavenir is asked to patch the ++Mavenir shopping cart++ with ++MSISDN++ ++available number++ ++chosen available number++ as a cart item characteristic
*Then* Mavenir updates the ++Mavenir shopping cart++ cart item with ++available number++ ++chosen available number++ as the MSISDN characteristic
*And* Mavenir returns the updated ++Mavenir shopping cart++ to Midtier

#### Scenario: Patch Shopping Cart

*Given* a ++Mavenir customer++ with a ++Mavenir shopping cart++ (no bundle) in Mavenir
*When* Mavenir is asked to patch the ++Mavenir shopping cart++ with a bundle cart item for ++plan++ ++Essentials++
*Then* Mavenir updates the ++Mavenir shopping cart++ with the ++plan++ ++Essentials++ bundle product item
*And* returns the patched ++Mavenir shopping cart++ to Patch Cart With Plan
### (S) --> Bring a Number

#### Examples

#### portability

| portability | example | donorOperator | portNumber | accountNumber | userType | accountType | device | group |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| portability | valid portability | Digicel | 4412345678 | 12345 | Residential | Postpaid | Iphone | portability |

#### Scenario: Bring a number

#### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++

*But* no Transfer Code is on Bring your mobile number
*When* the Prospect clicks Get started on Bring your mobile number
*Then* the Prospect can enter ++portability++
*And* the Prospect can confirm the information is accurate
*And* the Prospect can grant permission to Paradise Mobile to bring the number
*And* the Continue operation is disabled
*And* the Prospect can go Back
*When* the Prospect enters ++portability++ ++valid portability++ and checks both permissions
*Then* the Continue operation is enabled
*When* the Prospect clicks Continue
*Then* My Paradise submits ++portability++ ++valid portability++ to the Midtier
*And* Midtier returns a temporary ++MSISDN++ ++available number++ ++held available number++
*And* the Prospect is forwarded to Select Sim

#### Scenario: Number to be ported is incomplete

#### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++

*When* the Prospect leaves Number to be ported as the Bermuda prefix only
*Then* Number to be ported shows *Please enter the full Bermuda number.*
*And* the Continue operation stays disabled

#### Scenario: Provider not selected

#### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++

*When* the Prospect blurs Your current provider without selecting a provider
*Then* Your current provider shows *Please select a provider.*
*And* the Continue operation stays disabled
### (S) --> Confirm Number Already With Paradise

#### Scenario: Confirm the number is not already with Paradise

#### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*And* the Prospect has entered ++portability++ ++valid portability++
*But* no ++portability++ is in the ++Mavenir shopping cart++

*When* the Prospect proceeds to confirming whether their number is already with Paradise
*Then* the Prospect can confirm whether the ++MSISDN++ is already with Paradise
*When* the Prospect confirms the ++MSISDN++ is not already with Paradise
*Then* My Paradise submits ++portability++ ++valid portability++ to the Midtier
*And* the Prospect is forwarded to Select Sim

#### Scenario: Confirm the number is already with Paradise

#### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*And* the Prospect has entered ++portability++ ++valid portability++
*But* no ++portability++ is in the ++Mavenir shopping cart++

*When* the Prospect proceeds to confirming whether their number is already with Paradise
*Then* the Prospect can confirm whether the ++MSISDN++ is already with Paradise
*When* the Prospect confirms the ++MSISDN++ is already with Paradise
*Then* ++portability++ is not submitted to the Midtier
*And* the Prospect is returned to selecting their number
### (S) --> Evaluate Porting Two Factor Flag

#### Scenario: Porting two factor flag enabled (Intended)

*Given* `porting-2fa` is enabled in GrowthBook
*And* the Prospect is in Account Setup
*When* GrowthBook evaluates the `porting-2fa` flag
*Then* My Paradise mounts the SMS verification step in the porting wizard
*And* My Paradise starts the porting wizard at the SMS verification step when ++portability++ on the ++Mavenir shopping cart++ is unverified

#### Scenario: Porting two factor flag disabled (live)

*Given* `porting-2fa` is disabled in GrowthBook
*And* the Prospect is in Account Setup
*When* GrowthBook evaluates the `porting-2fa` flag
*Then* My Paradise omits the SMS verification step from the porting wizard
### (S) --> Submit Portability Request to Mid-Tier

#### Scenario: Submit portability request — porting-2fa off (live)

#### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*But* no ++portability++ is in the ++Mavenir shopping cart++

*Given* the Prospect has entered ++portability++ ++valid portability++
*When* My Paradise posts a portability request to Midtier with ++portability++ ++valid portability++
*Then* Midtier returns a temporary ++MSISDN++ ++available number++ ++held available number++
*And* My Paradise stores ++portability++ ++valid portability++ and ++available number++ ++held available number++ in the ++Mavenir shopping cart++
*And* the Prospect is forwarded to Select Sim

#### Scenario: Submit portability request — porting-2fa on, SMS sent (Intended)

#### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*But* no ++portability++ is in the ++Mavenir shopping cart++

*Given* the Prospect has entered ++portability++ ++valid portability++
*And* `porting-2fa` is enabled
*When* My Paradise posts a portability request to Midtier with ++portability++ ++valid portability++
*Then* Midtier returns `{ status: sent, temporaryNumber: ++available number++ ++held available number++ }`
*And* My Paradise stores ++portability++ ++valid portability++ and ++available number++ ++held available number++ in the ++Mavenir shopping cart++
*And* My Paradise presents the Confirm your number for porting step

#### Scenario: Submit portability request — rate limited, bypass (Intended)

#### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*But* no ++portability++ is in the ++Mavenir shopping cart++

*Given* `porting-2fa` is enabled
*When* My Paradise posts a ++portability request++
*But* Midtier returns `{ status: rate_limited, canBypass: true, temporaryNumber: ++available number++ ++held available number++ }`
*Then* My Paradise stores ++portability++ ++valid portability++ and ++available number++ ++held available number++ with `verified: true` in the ++Mavenir shopping cart++
*And* the Prospect is forwarded to Select Sim

#### Scenario: Submit portability request — invalid number (Intended)

#### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*But* no ++portability++ is in the ++Mavenir shopping cart++

*Given* `porting-2fa` is enabled
*When* My Paradise posts a ++portability request++
*But* Midtier returns `{ status: invalid_number }`
*Then* My Paradise shows *This number is invalid.* on Number to be ported

#### Scenario: Submit portability request fails

#### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*But* no ++portability++ is in the ++Mavenir shopping cart++

*When* My Paradise posts a ++portability request++
*But* Midtier returns an error
*Then* My Paradise shows *Failed to save your portability.*
### (S) --> Patch Cart With Portability

#### Scenario: Patch cart with portability

*Given* a ++PML customer++ with a ++Mavenir shopping cart++
*And* ++MSISDN++ ++available number++ ++held available number++ has been reserved as the temporary port-in number
*And* ++portability++ ++valid portability++ is in the request
*When* Midtier patches the ++Mavenir shopping cart++ with ++portability++ ++valid portability++ and ++available number++ ++held available number++
*Then* Midtier patches the ++Mavenir shopping cart++ in Mavenir with portability characteristics (planName, portinNumber, donorOperator, accountType, userType, accountNumber, device)
*And* Midtier returns the updated ++PML customer++ with ++portability++ in the ++Mavenir shopping cart++
### (S) --> Send Port Verification

#### Scenario: Send port verification SMS

*Given* `porting-2fa` is enabled
*And* ++portability++ ++valid portability++ is in the ++Mavenir shopping cart++
*When* Midtier sends port verification to ++portability++ ++valid portability++ portNumber
*Then* Midtier initiates a Twilio SMS verification to ++portability++ ++valid portability++ portNumber
*And* Midtier returns `{ status: sent, temporaryNumber: ++available number++ ++held available number++ }` to My Paradise

#### Scenario: Send port verification — rate limited

*Given* `porting-2fa` is enabled
*When* Midtier sends port verification
*But* Twilio rate limits the request
*Then* Midtier returns `{ status: rate_limited, canBypass: true, temporaryNumber: ++available number++ ++held available number++ }` to My Paradise

#### Scenario: Send port verification — invalid number

*Given* `porting-2fa` is enabled
*When* Midtier sends port verification
*But* Twilio rejects the number as invalid
*Then* Midtier returns `{ status: invalid_number }` to My Paradise
### (S) --> Send Verification Sms

#### Scenario: Send verification SMS

*Given* `porting-2fa` is enabled
*And* ++portability++ ++valid portability++ portNumber is a valid Bermuda number
*When* Twilio is asked to send a verification SMS to ++portability++ ++valid portability++ portNumber
*Then* Twilio creates a verification for ++portability++ ++valid portability++ portNumber (`channel: sms`)
*And* Twilio returns `sent` to Midtier

#### Scenario: Send verification SMS — rate limited

*Given* `porting-2fa` is enabled
*When* Twilio is asked to send a verification SMS
*But* the rate limit for ++portability++ ++valid portability++ portNumber is exceeded
*Then* Twilio returns `rate_limited` to Midtier
### (S) --> Enter Porting Sms Code

#### Examples

#### porting SMS code

| porting SMS code | example | code | group |
| --- | --- | --- | --- |
| porting SMS code | valid porting SMS code | 123456 | porting SMS code |
| porting SMS code | mismatch porting SMS code | Invalid verification code. | porting SMS code |
| porting SMS code | example | helper | porting SMS code |

#### Scenario: Enter ++porting SMS code++

#### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*And* ++portability++ ++valid portability++ is in the ++Mavenir shopping cart++
*And* My Paradise has SMSed a ++porting SMS code++ through the Midtier

*When* the Prospect proceeds to confirming their number for porting
*Then* the Prospect sees the code was sent to the ++portability++ number
*And* the Prospect can enter ++porting SMS code++ in Enter SMS code
*And* the Prospect can Resend
*And* Resend is disabled for 30 seconds
*And* the Prospect can Change
*And* the Prospect can go Back
*And* the Verify code operation is disabled
*When* the Prospect enters ++porting SMS code++ ++valid porting SMS code++
*Then* the Verify code operation is enabled
*When* the Prospect clicks Verify code
*Then* My Paradise checks the ++porting SMS code++ through the Midtier
*And* the Prospect is forwarded to Select Sim

#### Scenario: Verify with unusable ++porting SMS code++

#### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*And* ++portability++ ++valid portability++ is in the ++Mavenir shopping cart++
*And* My Paradise has SMSed a ++porting SMS code++ through the Midtier

*When* the Prospect clicks Verify code with ++porting SMS code++ ++mismatch porting SMS code++
*Then* Enter SMS code shows helper text *Invalid verification code.*

#### Scenario: Resend ++porting SMS code++

#### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*And* ++portability++ ++valid portability++ is in the ++Mavenir shopping cart++
*And* My Paradise has SMSed a ++porting SMS code++ through the Midtier

*When* the Prospect clicks Resend
*Then* My Paradise SMSes a ++porting SMS code++ through the Midtier
*And* the Prospect sees *A new code was sent to* the ++portability++ number
*And* Resend is disabled for 30 seconds before it can be used again
### (S) --> Check Port Verification

#### Scenario: Check port verification — code valid

#### Background

*Given* a ++PML customer++ with a ++Mavenir shopping cart++
*And* ++portability++ ++valid portability++ is in the ++Mavenir shopping cart++
*And* a ++porting SMS code++ was sent to ++portability++ ++valid portability++ portNumber

*When* Midtier is asked to check ++porting SMS code++ ++valid porting SMS code++ against ++portability++ ++valid portability++ portNumber
*Then* Midtier checks the ++porting SMS code++ with Twilio
*And* Twilio returns `approved`
*And* Midtier marks the ++PML customer++ phone as verified
*And* Midtier returns `{ verified: true }` to My Paradise

#### Scenario: Check port verification — code mismatch

#### Background

*Given* a ++PML customer++ with a ++Mavenir shopping cart++
*And* ++portability++ ++valid portability++ is in the ++Mavenir shopping cart++
*And* a ++porting SMS code++ was sent to ++portability++ ++valid portability++ portNumber

*When* Midtier is asked to check ++porting SMS code++ ++mismatch porting SMS code++ against ++portability++ ++valid portability++ portNumber
*Then* Midtier checks the ++porting SMS code++ with Twilio
*And* Twilio returns a non-approved status
*And* Midtier returns `{ verified: false }` to My Paradise
### (S) --> Check Verification

#### Scenario: Check verification — code valid

#### Background

*Given* a verification was sent to ++portability++ ++valid portability++ portNumber

*When* Twilio is asked to check ++porting SMS code++ ++valid porting SMS code++ against ++portability++ ++valid portability++ portNumber
*Then* Twilio creates a verification check (`verificationChecks.create`)
*And* Twilio returns `approved` to Midtier

#### Scenario: Check verification — code mismatch

#### Background

*Given* a verification was sent to ++portability++ ++valid portability++ portNumber

*When* Twilio is asked to check ++porting SMS code++ ++mismatch porting SMS code++ against ++portability++ ++valid portability++ portNumber
*Then* Twilio creates a verification check
*And* Twilio returns a non-approved status to Midtier
### (S) Customer --> Keep Current Number
### (S) Care --> Sweep Stale Number Reservations

#### Scenario: Sweep stale number reservations

*Given* ++MSISDN++ resources have been reserved but have no active order
*And* Care observes mass Reserved ++MSISDN++ resources in the Mavenir DEP Resource Inventory
*When* Care sweeps stale ++MSISDN++ reservations
*Then* Mavenir transitions the stale ++MSISDN++ resources from reserved to available
*And* the released ++MSISDN++ resources are visible as available in the Mavenir DEP Resource Inventory
## (E) Get Onboarding Plan
### (S) --> Query Product Offerings And Map To Catalog

#### Scenario: Query Product Offerings And Map To Catalog

*Given* Mavenir has returned product offerings for service provider 100000000
*When* Midtier is asked to query product offerings and map to catalog
*Then* Midtier filters offerings to valid bundle IDs — ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, ++plan++ ++Atlas++, and ++plan++ ++Internal Test Plan PROMO++
*And* strips "PROMO" from ++plan++ ++Internal Test Plan PROMO++ name
*And* marks ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, and ++plan++ ++Atlas++ as isSellable
*And* marks ++plan++ ++Internal Test Plan PROMO++ as not isSellable
*And* tags ++plan++ ++Ace++ as "Best value"
*And* returns the ++plan++ catalog sorted by price descending to Choose Onboarding Plan
### (S) --> List Product Offerings

#### Scenario: List Product Offerings

*Given* Mavenir catalog for service provider 100000000 is reachable
*When* Mavenir is asked to list product offerings with channelName CRM
*Then* Mavenir returns product bundles including ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, ++plan++ ++Atlas++, and ++plan++ ++Internal Test Plan PROMO++ with their productOfferingPrice and bundledProductOffering
### (S) My Paradise --> Load Plan Catalog
### (S) Customer --> Choose Onboarding Plan

#### Scenario Outline: Choose Onboarding Plan

#### Background

*Given* the Prospect is in Account Setup
*And* the Prospect has a ++My Paradise customer++ with a ++Mavenir shopping cart++

*But* no ++plan++ is in the ++Mavenir shopping cart++
*And* Keep current plan is not shown
*When* the Prospect is forwarded to Plan Selection
*Then* the system retrieves the ++plan++ catalog from the Midtier
*And* the Prospect sees ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, and ++plan++ ++Atlas++
*And* each ++plan++ has a Select operation
*When* the Prospect clicks Select on ++plan++ ++{scenario}++
*Then* the system patches the ++Mavenir shopping cart++ with ++{scenario}++ through the Midtier
*And* the ++My Paradise customer++ cart is updated in session with ++{scenario}++
*And* the Prospect is forwarded to Time to pick your number

#### Scenario: Choose a different ++plan++

#### Background

*Given* the Prospect is in Account Setup
*And* the Prospect has a ++My Paradise customer++ with a ++Mavenir shopping cart++

*Given* ++plan++ ++Essentials++ is in the ++Mavenir shopping cart++
*When* the Prospect arrives at Plan Selection from Checkout
*Then* the Prospect sees "Your current plan Essentials"
*And* Keep current plan is enabled
*And* the ++plan++ catalog is displayed
*And* each ++plan++ has a Select operation
*When* the Prospect clicks Select on ++plan++ ++Data Freedom++
*Then* the system patches the ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++ through the Midtier
*And* the ++My Paradise customer++ cart is updated in session with ++plan++ ++Data Freedom++
*And* the Prospect is forwarded to Checkout

#### Scenario: Select the ++plan++ already in the cart

#### Background

*Given* the Prospect is in Account Setup
*And* the Prospect has a ++My Paradise customer++ with a ++Mavenir shopping cart++

*Given* ++plan++ ++Essentials++ is in the ++Mavenir shopping cart++
*When* the Prospect clicks Select on ++plan++ ++Essentials++
*Then* the Prospect stays on Plan Selection to choose a different ++plan++ or Keep current plan

#### Scenario: Failed to update plan

#### Background

*Given* the Prospect is in Account Setup
*And* the Prospect has a ++My Paradise customer++ with a ++Mavenir shopping cart++

*Given* Midtier PATCH to ++Mavenir shopping cart++ returns a server error
*When* the Prospect clicks Select on ++plan++ ++Data Freedom++
*Then* My Paradise shows "Failed to update new plan choice."
*And* the Prospect stays on Plan Selection
### (S) --> Patch Cart With Plan

#### Scenario: Patch Cart With Plan

*Given* a ++Mavenir customer++ with a ++Mavenir shopping cart++ (no bundle) in Mavenir
*When* Midtier is asked to patch cart with bundleId for ++plan++ ++Essentials++
*Then* Midtier fetches the catalog bundle for ++plan++ ++Essentials++ from Mavenir
*And* builds the cart item payload with the bundle product offering
*And* patches the ++Mavenir shopping cart++ through Mavenir Patch Shopping Cart
*And* returns the ++PML customer++ cart with ++plan++ ++Essentials++ bundle to Choose Onboarding Plan

#### Scenario: Patch Cart With Plan — portability plan name updated

*Given* a ++Mavenir customer++ with a ++Mavenir shopping cart++ that has a ++portability++ record in Mavenir
*When* Midtier is asked to patch cart with bundleId for ++plan++ ++Data Freedom++ and portability planSelected "Data Freedom"
*Then* Midtier builds the cart item for ++plan++ ++Data Freedom++ with the portability planName characteristic set to "Data Freedom"
*And* patches the ++Mavenir shopping cart++ through Mavenir Patch Shopping Cart
*And* returns the ++PML customer++ cart with ++plan++ ++Data Freedom++ bundle and updated ++portability++ planName
### (S) --> Patch Shopping Cart

#### Scenario: Patch shopping cart with portability

*Given* a ++Mavenir shopping cart++ with a plan bundle cart item and temporary ++MSISDN++ ++available number++ ++held available number++
*When* Mavenir is asked to patch the ++Mavenir shopping cart++ with ++portability++ ++valid portability++ characteristics
*Then* Mavenir updates the ++Mavenir shopping cart++ cart item with portability characteristics (planName, portinNumber, donorOperator, accountType, userType, accountNumber, device, portin, requestType)
*And* Mavenir returns the updated ++Mavenir shopping cart++ to Midtier

#### Scenario: Patch shopping cart with MSISDN

*Given* a ++Mavenir shopping cart++ with a plan bundle cart item
*But* no MSISDN characteristic on the cart item
*When* Mavenir is asked to patch the ++Mavenir shopping cart++ with ++MSISDN++ ++available number++ ++chosen available number++ as a cart item characteristic
*Then* Mavenir updates the ++Mavenir shopping cart++ cart item with ++available number++ ++chosen available number++ as the MSISDN characteristic
*And* Mavenir returns the updated ++Mavenir shopping cart++ to Midtier

#### Scenario: Patch Shopping Cart

*Given* a ++Mavenir customer++ with a ++Mavenir shopping cart++ (no bundle) in Mavenir
*When* Mavenir is asked to patch the ++Mavenir shopping cart++ with a bundle cart item for ++plan++ ++Essentials++
*Then* Mavenir updates the ++Mavenir shopping cart++ with the ++plan++ ++Essentials++ bundle product item
*And* returns the patched ++Mavenir shopping cart++ to Patch Cart With Plan
### (S) --> Keep Current Plan

#### Scenario: Keep Current Plan

#### Background

*Given* the Prospect is in Account Setup
*And* the Prospect has a ++My Paradise customer++ with a ++Mavenir shopping cart++
*And* ++plan++ ++Essentials++ is in the ++Mavenir shopping cart++

*When* the Prospect clicks Keep current plan
*Then* the Prospect is forwarded to Checkout
## (E) Get Sim
### (S) Customer --> Choose Esim

#### Scenario: Choose eSIM

#### Background

*Given* eSIM is available
*And* the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++
*And* the phone supports eSIM

*Given* no ++SIM type++ is on the line
*When* the Customer selects eSIM
*Then* My Paradise sends the patch cart request to Mavenir with ++SIM type++ eSIM
*When* Mavenir returns the updated ++Mavenir shopping cart++ with ++SIM type++ eSIM
*Then* My Paradise stores eSIM on the line
*And* the Customer is forwarded to Verify ID

#### Scenario: Choose eSIM — already on the line

#### Background

*Given* eSIM is available
*And* the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++
*And* the phone supports eSIM

*Given* the line already has ++SIM type++ eSIM
*When* the Customer selects eSIM
*Then* My Paradise skips the cart patch

#### Scenario: Choose eSIM — cart patch fails

#### Background

*Given* eSIM is available
*And* the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++
*And* the phone supports eSIM

*Given* Mavenir returns an error on cart patch
*When* the Customer selects eSIM
*Then* the SIM selection fails
*And* the line has no ++SIM type++
### (S) Customer --> Request a Paradise Sim Card

#### Scenario: Request a Paradise SIM card

#### Background

*Given* the Customer is choosing a physical SIM
*And* the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++

*Given* no ++SIM type++ is on the line
*And* no ++ICCID++ is on the line
*When* the Customer requests a Paradise SIM card
*Then* My Paradise sends the patch cart request to Mavenir with ++SIM type++ pSIM
*When* Mavenir returns the updated ++Mavenir shopping cart++ with ++SIM type++ pSIM
*Then* My Paradise stores pSIM on the line
*But* the line has no ++ICCID++
*And* the Customer is forwarded to Verify ID

#### Scenario: Request a Paradise SIM card — already on the line

#### Background

*Given* the Customer is choosing a physical SIM
*And* the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++

*Given* the line already has ++SIM type++ pSIM
*When* the Customer requests a Paradise SIM card
*Then* My Paradise skips the cart patch

#### Scenario: Request a Paradise SIM card — cart patch fails

#### Background

*Given* the Customer is choosing a physical SIM
*And* the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++

*Given* Mavenir returns an error on cart patch
*When* the Customer requests a Paradise SIM card
*Then* the SIM selection fails
*And* the line has no ++SIM type++
### (S) Customer --> Enter Existing Sim

#### Scenario: Enter existing SIM

#### Background

*Given* the Customer is choosing a physical SIM
*And* the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++

*Given* Mavenir has ++ICCID++ ++valid ICCID++ available in inventory
*When* the Customer attaches ++ICCID++ ++valid ICCID++
*Then* My Paradise sends the ICCID inventory request to Mavenir with ++ICCID++ ++valid ICCID++
*And* My Paradise sends the patch cart request to Mavenir with ++SIM type++ pSIM and ++ICCID++ ++valid ICCID++
*When* Mavenir returns the updated ++Mavenir shopping cart++ with ++SIM type++ pSIM and ++ICCID++ ++valid ICCID++
*Then* My Paradise stores pSIM and ++ICCID++ ++valid ICCID++ on the line
*And* the Customer is forwarded to Verify ID

#### Scenario: ICCID contains spaces

#### Background

*Given* the Customer is choosing a physical SIM
*And* the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++

*Given* the Customer has ++ICCID++ ++ICCID with spaces++
*When* the Customer attaches ++ICCID++ ++ICCID with spaces++
*Then* the ICCID format is rejected
*And* My Paradise does not query inventory or patch the cart

#### Scenario: Inventory rejects ICCID

#### Background

*Given* the Customer is choosing a physical SIM
*And* the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++

*Given* Mavenir does not have ++ICCID++ ++invalid ICCID++ available in inventory
*When* the Customer attaches ++ICCID++ ++invalid ICCID++
*Then* My Paradise sends the ICCID inventory request to Mavenir with ++ICCID++ ++invalid ICCID++
*And* My Paradise does not patch the cart
*And* the ICCID is rejected
### (S) Customer --> Activate Sim

#### Scenario: Activate Sim

#### Background

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

#### Scenario: waiting pSIM is absent

#### Background

*Given* the Customer is waiting for a Paradise SIM
*And* the Customer is verified
*And* the line has ++SIM type++ pSIM
*But* no ++ICCID++ is on the line
*And* the ++Mavenir customer++ has ++waiting pSIM++ Active

*Given* Mavenir has ++ICCID++ ++valid ICCID++ available in inventory
*But* the ++Mavenir customer++ has no ++waiting pSIM++ characteristic
*When* the Customer activates the SIM with ++ICCID++ ++valid ICCID++
*Then* the pSIM delivered order is rejected

#### Scenario: waiting pSIM already completed

#### Background

*Given* the Customer is waiting for a Paradise SIM
*And* the Customer is verified
*And* the line has ++SIM type++ pSIM
*But* no ++ICCID++ is on the line
*And* the ++Mavenir customer++ has ++waiting pSIM++ Active

*Given* Mavenir has ++ICCID++ ++valid ICCID++ available in inventory
*And* the ++Mavenir customer++ has ++waiting pSIM++ Cleared
*When* the Customer activates the SIM with ++ICCID++ ++valid ICCID++
*Then* the pSIM delivered order is rejected
### (S) --> Complete Draft Sim Order

#### Scenario: Complete Draft Sim Order

#### Background

*Given* a Customer completed the My Paradise onboarding flow
*And* the Customer's line has ++SIM type++ pSIM
*But* the Customer never entered an ++ICCID++
*And* the ++Mavenir customer++ has ++waiting pSIM++ Active

*Given* Care opens the ++Mavenir customer++ record in Mavenir DEP
*And* Care sees the draft order in the orders grid (`22-dep-orders-grid.png`)
*When* Care attaches the ++ICCID++ to the draft order and completes it
*Then* the order status in DEP Order History changes from draft to active (`23-dep-order-history.png`)
*And* the ++waiting pSIM++ characteristic on the ++Mavenir customer++ is cleared
## (E) Get Verified Profile
### (S) Customer --> Customer Complete Persona Kyc

#### Scenario: Persona verification required

#### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*But* no idNumber on ++identity++
*When* the Customer validates whether a Persona inquiry is required
*Then* a Persona inquiry is required
*And* the Customer is on the Profile KYC step

#### Scenario: Persona verification already complete

#### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*Given* the Customer has ++identity++ with an idNumber
*When* the Customer validates whether a Persona inquiry is required
*Then* the Persona inquiry is already complete
*And* the Customer is forwarded to Checkout

#### Scenario: Create a completed Persona inquiry

#### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*Given* the Customer has no idNumber on ++identity++
*When* the Customer creates a Persona inquiry
*Then* My Paradise sends the inquiry request to Persona with the Customer email
*And* My Paradise retrieves the Persona document
*When* Persona returns ++Persona inquiry++ ++completed Persona inquiry++
*Then* the Customer has a verified ++Persona inquiry++
*And* My Paradise maps the inquiry onto ++identity++ ++valid identity++ and ++address++ ++valid address++
*And* Customer verified stays false until the Customer confirms their identity
*When* Persona returns ++Persona document++ ++valid Persona document++
*Then* ++identity++ expiry date is the ++Persona document++ expiration date

#### Scenario: Persona inquiry not completed

#### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*When* the Customer creates a Persona inquiry
*Then* My Paradise sends the inquiry request to Persona with the Customer email
*When* Persona returns ++Persona inquiry++ ++failed Persona inquiry++
*Then* the Customer has an unverified ++Persona inquiry++
*And* ++identity++ and ++address++ stay empty

#### Scenario: No government ID document on inquiry

#### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*Given* the completed ++Persona inquiry++ has no government ID document
*When* the Customer creates a Persona inquiry
*Then* My Paradise sends the inquiry request to Persona
*And* My Paradise does not retrieve a Persona document
*When* Persona returns the completed inquiry without a government ID
*Then* ++identity++ expiry date is empty

#### Scenario: Persona errors on inquiry load

#### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*When* the Customer creates a Persona inquiry
*Then* My Paradise sends the inquiry request to Persona
*When* Persona returns an error
*Then* the Customer has an unverified ++Persona inquiry++
*And* ++identity++ stays empty

#### Scenario: Document not found

#### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*Given* Persona has no ++Persona document++ for that document ID
*When* the Customer creates a Persona inquiry
*Then* My Paradise retrieves the Persona document
*When* Persona returns that the document is not found
*Then* ++identity++ expiry date is empty

#### Scenario: Document email mismatch

#### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*Given* the ++Persona document++ email does not match the Customer email
*When* the Customer creates a Persona inquiry
*Then* My Paradise retrieves the Persona document
*When* Persona returns unauthorized
*Then* ++identity++ expiry date is empty

#### Scenario: Verify later

#### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*Given* the Customer has a ++My Paradise customer++ with no idNumber on ++identity++
*When* the Customer proceeds without a Persona inquiry
*Then* My Paradise does not send an inquiry request to Persona
*And* no ++Persona inquiry++ is stored
*And* the Customer is still on the Profile KYC step

#### Scenario: Enter valid identity and address

#### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*Given* the Customer has a ++My Paradise customer++ in session
*When* the Customer enters ++identity++ ++valid identity++ and ++address++ ++valid address++
*Then* all profile requirements are met
*And* the Customer can confirm their identity

#### Scenario: Enter identity after a verified Persona inquiry

#### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*Given* the Customer has a verified ++Persona inquiry++ mapped onto ++identity++ ++valid identity++
*When* the Customer enters the mapped ++identity++ and ++address++
*Then* all profile requirements are met
*And* the ID fields are present on ++identity++

#### Scenario: Re-enter a verified identity

#### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*Given* the Customer has ++identity++ ++valid identity++ already verified
*When* the Customer re-enters ++identity++ ++valid identity++
*Then* the identity is no longer verified
*And* the Customer can confirm their identity again

#### Scenario Outline: Enter incomplete identity or address

#### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*When* the Customer enters ++identity++ and ++address++ with {field} empty
*Then* {field} is missing
*And* the Customer cannot confirm their identity

#### Scenario: Confirm identity with a verified Persona inquiry

#### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*Given* the Customer has entered ++identity++ ++valid identity++ and ++address++ ++valid address++
*And* the Customer has a verified ++Persona inquiry++
*When* the Customer confirms their identity
*Then* My Paradise maps ++identity++ and ++address++ onto the Mavenir engaged party and contact medium
*And* My Paradise sends the profile patch to Mavenir
*When* Mavenir patches the customer
*Then* the Customer identity is persisted
*And* the Customer is verified
*And* the ++Persona inquiry++ is cleared

#### Scenario: Profile requirements unmet

#### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*Given* the Customer has not entered ++identity++ or ++address++
*When* the Customer confirms their identity
*Then* the identity cannot be confirmed
*And* My Paradise does not send a profile patch to Mavenir

#### Scenario: Customer already exists

#### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*Given* another Mavenir customer already has ++identity++ idNumber I1234562
*When* the Customer confirms their identity
*Then* My Paradise sends the profile patch to Mavenir
*And* the identity cannot be confirmed because a customer with that information already exists

#### Scenario: Mavenir profile patch error

#### Background

*Given* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++ that already has a plan, number, and SIM

*Given* Mavenir returns a profile patch error
*When* the Customer confirms their identity
*Then* My Paradise sends the profile patch to Mavenir
*And* the identity cannot be confirmed
### (S) Ambassador --> Collect Identity With Brand Amassador

#### Scenario: Collect identity with Brand Ambassador

*Given* the Customer is choosing how to verify their ID
*When* the Customer asks a Brand Ambassador to verify their ID
*Then* the Ambassador will be in touch to proceed with verification
*And* the Ambassador collects the Customer's ++identity++ documents over WhatsApp
*And* the Customer proceeds to enter identity in My Paradise
## (E) Get Order Review
### (S) Customer --> Check The Order

#### Scenario: Check the order

#### Background

*Given* the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
*And* ++available number++ ++chosen available number++ is in the ++Mavenir shopping cart++
*And* the Customer has chosen eSIM

*Given* the Customer has completed account setup, number, SIM, and profile
*When* the Customer proceeds to reviewing their order
*Then* the Customer is forwarded to Checkout
*And* the Checkout step is the next onboarding step

#### Scenario: Check the order with port-in number

#### Background

*Given* the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
*And* ++available number++ ++chosen available number++ is in the ++Mavenir shopping cart++
*And* the Customer has chosen eSIM

*Given* the Customer has a port-in number with +1 (441) 123-4567 as port number and +1 (441) 555-0101 as temporary MSISDN
*When* the Customer proceeds to reviewing their order
*Then* the Customer is forwarded to Checkout
*And* the Checkout step is the next onboarding step
### (S) Customer --> Upgrade To Data Freedom

#### Examples

| plan upgrade | example | currentPlan | newPlan |
| --- | --- | --- | --- |
| plan upgrade | upgrade to Data Freedom | Essentials | Data Freedom |
| plan upgrade | upgrade to Ace | Data Freedom | Ace |
| plan upgrade | upgrade to Atlas | Ace | Atlas |

#### Scenario Outline: Upgrade plan from review

#### Background

*Given* the Customer is reviewing their order
*And* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++

*Given* ++plan++ ++{currentPlan}++ is in the ++Mavenir shopping cart++
*When* My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++{newPlan}++
*Then* My Paradise sends the patch cart request to Mavenir with ++plan++ ++{newPlan}++ bundleId
*When* Mavenir returns the updated ++Mavenir shopping cart++ with ++plan++ ++{newPlan}++
*Then* My Paradise stores ++plan++ ++{newPlan}++ as the cart bundle
*And* the Customer sees *You have been upgraded!*

#### Scenario: No upsell shown on top-tier plan

#### Background

*Given* the Customer is reviewing their order
*And* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++

*Given* ++plan++ ++Atlas++ is in the ++Mavenir shopping cart++
*When* the Customer proceeds to reviewing their order
*Then* no upgrade option is available
### (S) Customer --> Change Plan From Review

#### Scenario: Select a different plan from review

#### Background

*Given* the Customer is reviewing their order
*And* the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++

*Given* the Customer has opened plan selection from review
*When* My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++
*Then* My Paradise sends the patch cart request to Mavenir with ++plan++ ++Data Freedom++ bundleId
*When* Mavenir returns the updated ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++
*Then* My Paradise stores ++plan++ ++Data Freedom++ as the cart bundle
*And* the Customer is forwarded to Checkout

#### Scenario: Keep current plan from review

#### Background

*Given* the Customer is reviewing their order
*And* the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++

*Given* the Customer has opened plan selection from review
*When* the Customer keeps their current plan
*Then* the Customer is forwarded to Checkout

#### Scenario: Select the plan already in the cart from review

#### Background

*Given* the Customer is reviewing their order
*And* the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++

*Given* the Customer has opened plan selection from review
*When* My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++Essentials++
*Then* the cart bundle remains ++plan++ ++Essentials++

#### Scenario: Plan update fails from review

#### Background

*Given* the Customer is reviewing their order
*And* the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++

*Given* the Customer has opened plan selection from review
*And* Mavenir returns an error on cart patch
*When* My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++
*Then* My Paradise shows *Failed to update new plan choice.*
*And* the cart bundle remains ++plan++ ++Essentials++
## (E) Get Payment
### (S) Customer --> Enter Payment

#### Examples

#### payment authorization

| payment authorization | example | transactionId | totalAmount | salesChannel | group |
| --- | --- | --- | --- | --- | --- |
| payment authorization | stub auth | d4a1b2c3-9f3a-4e1b-8c7d-a2b5e8f1d0c3 | 1 | ON-BOARDING | payment authorization |

#### Scenario: Enter Payment

#### Background

*Given* the Customer has completed order review and is on Checkout
*And* the Customer has a loaded ++My Paradise customer++ with a ++Mavenir shopping cart++

*Given* `payUpFront` is off
*And* Mavenir CCS authorizes ++payment authorization++ ++stub auth++
*When* the Customer proceeds to adding their payment
*Then* My Paradise sends the card authorization request to Mavenir with TotalAmount $1 and salesChannel ON-BOARDING
*When* Mavenir authorizes the card and returns the hosted payment page
*Then* My Paradise stores ++payment authorization++ ++stub auth++

#### Scenario: Pay upfront

#### Background

*Given* the Customer has completed order review and is on Checkout
*And* the Customer has a loaded ++My Paradise customer++ with a ++Mavenir shopping cart++

*Given* `payUpFront` is on
*And* the cart has ++plan++ ++Essentials++
*And* Mavenir CCS authorizes ++payment authorization++ ++stub auth++
*When* the Customer proceeds to adding their payment
*Then* My Paradise sends the card authorization request to Mavenir with TotalAmount $1 and salesChannel ON-BOARDING
*When* Mavenir authorizes the card and returns the hosted payment page
*Then* My Paradise stores ++payment authorization++ ++stub auth++

#### Scenario: Payment authorization fails to load

#### Background

*Given* the Customer has completed order review and is on Checkout
*And* the Customer has a loaded ++My Paradise customer++ with a ++Mavenir shopping cart++

*Given* `payUpFront` is off
*But* Mavenir CCS does not return a payment authorization
*When* the Customer proceeds to adding their payment
*Then* My Paradise sends the card authorization request to Mavenir
*When* Mavenir does not return a payment authorization
*Then* the payment authorization cannot be loaded

#### Scenario: FAC authorization timeout

#### Background

*Given* the Customer has completed order review and is on Checkout
*And* the Customer has a loaded ++My Paradise customer++ with a ++Mavenir shopping cart++

*Given* `payUpFront` is off
*But* Mavenir does not return a transaction id
*When* the Customer proceeds to adding their payment
*Then* My Paradise sends the card authorization request to Mavenir
*When* Mavenir does not return a transaction id
*Then* the payment authorization cannot be loaded
### (S) --> Evaluate Payment Flags
### (S) My Paradise --> Authorize Card

#### Examples

#### payment status

| payment status | example | transactionId | status | reason | group |
| --- | --- | --- | --- | --- | --- |
| payment status | completed auth | d4a1b2c3-9f3a-4e1b-8c7d-a2b5e8f1d0c3 | completed | APPROVED | payment status |
| payment status | failed auth | d4a1b2c3-9f3a-4e1b-8c7d-a2b5e8f1d0c3 | failed | DECLINED | payment status |

#### Scenario: Payment completed

*Given* the Customer has ++payment authorization++ ++stub auth++
*And* Mavenir CCS has ++payment status++ ++completed auth++
*When* the Customer authorizes their card
*Then* My Paradise sends the tokenized card request to Mavenir for ++payment authorization++ ++stub auth++
*When* Mavenir returns ++payment status++ ++completed auth++
*Then* the payment is authorized
*And* the payment step does not place the order

#### Scenario: Card not verified

*Given* the Customer has ++payment authorization++ ++stub auth++
*And* Mavenir CCS has ++payment status++ ++failed auth++
*And* payment attempts are under the maximum
*When* the Customer authorizes their card
*Then* My Paradise sends the tokenized card request to Mavenir
*When* Mavenir returns ++payment status++ ++failed auth++
*Then* the card is not verified
*And* My Paradise requests a fresh payment authorization from Mavenir

#### Scenario: Maximum payment attempts

*Given* the Customer has ++payment authorization++ ++stub auth++
*And* Mavenir CCS has ++payment status++ ++failed auth++
*And* payment attempts equal the maximum
*When* the Customer authorizes their card
*Then* My Paradise sends the tokenized card request to Mavenir for ++payment authorization++ ++stub auth++
*When* Mavenir returns ++payment status++ ++failed auth++
*Then* My Paradise records the failed card addition with Zendesk
*And* the payment step does not place the order
### (S) My Paradise --> Provide Apple Pay Certificate

#### Examples

#### Apple Pay certificate

| Apple Pay certificate | example | keyIdentifier | group |
| --- | --- | --- | --- |
| Apple Pay certificate | Bermuda Apple Pay cert | CertificateSerialNumber=08b3a3b7b23c2c56a625e95211699f0b | Apple Pay certificate |

#### Scenario: Provide Apple Pay certificate

*Given* the Apple Pay merchant certificate is available
*When* My Paradise provides the Apple Pay certificate
*Then* My Paradise sends the certificate request to Apple
*When* Apple returns ++Apple Pay certificate++ ++Bermuda Apple Pay cert++
*Then* My Paradise returns ++Apple Pay certificate++ ++Bermuda Apple Pay cert++
### (S) Care --> Adjust Credit Manually

#### Scenario: Adjust credit for pay-upfront or voucher

*Given* the Care agent is in Mavenir DEP for the loaded ++My Paradise customer++
*And* the ++Mavenir customer++ has completed onboarding in My Paradise
*But* the credit adjustment was not applied after checkout
*When* the Care agent manually adjusts the credit amount in Mavenir DEP
*Then* the ++Mavenir customer++ billing account is credited the adjustment amount
## (E) Place Order
### (S) My Paradise --> Create Billing Account

#### Scenario: Create billing account

#### Background

*Given* the Customer has a configured cart
*But* the Customer has no billing account

*When* the Customer creates a billing account
*Then* My Paradise sends the billing account request to Mavenir
*When* Mavenir creates the billing account
*Then* the Customer has a billing account
*And* the Customer is on the Done step

#### Scenario: Billing account already exists

#### Background

*Given* the Customer has a configured cart
*But* the Customer has no billing account

*Given* the Customer already has a billing account
*When* the Customer creates a billing account
*Then* the billing account is rejected
*And* Mavenir does not receive a billing account request

#### Scenario: Billing account creation fails

#### Background

*Given* the Customer has a configured cart
*But* the Customer has no billing account

*Given* Mavenir returns an error for the billing account request
*When* the Customer creates a billing account
*Then* the billing account cannot be created
*And* the Customer has no billing account
### (S) My Paradise --> Create Product Order

#### Scenario: Create product order

#### Background

*Given* the Customer has a billing account
*And* the cart has plan, number, and SIM

*Given* the Customer is verified
*When* the Customer places the product order
*Then* My Paradise sends the product order request to Mavenir
*When* Mavenir creates the product order
*Then* the order succeeded with pay-up-front
*And* the Customer onboarding is done

#### Scenario: Pay-up-front charge fails

#### Background

*Given* the Customer has a billing account
*And* the cart has plan, number, and SIM

*Given* the pay-up-front charge fails
*When* the Customer places the product order
*Then* My Paradise does not send a product order to Mavenir
*And* the order succeeded without pay-up-front

#### Scenario: Product order fails

#### Background

*Given* the Customer has a billing account
*And* the cart has plan, number, and SIM

*Given* Mavenir returns an error for the product order
*When* the Customer places the product order
*Then* the order did not succeed

#### Scenario: Onboarding is already done

#### Background

*Given* the Customer has a billing account
*And* the cart has plan, number, and SIM

*Given* the Customer onboarding is already done
*When* the Customer places the product order
*Then* the product order is rejected
*And* Mavenir does not receive a product order request

#### Scenario: Unverified with no bypass and no portability

#### Background

*Given* the Customer has a billing account
*And* the cart has plan, number, and SIM

*Given* the Customer is not verified
*And* the plan does not bypass verification
*And* the cart has no portability
*When* the Customer places the product order
*Then* My Paradise does not send a product order to Mavenir
*And* the cart is marked to submit the order later
*And* the Customer onboarding is done
### (S) Customer --> View Order Result

#### Scenario Outline: View order result

*Given* the order result is {example}
*When* the Customer views their order result
*Then* the order is {outcome}
### (S) My Paradise --> Create Order Ticket

#### Scenario Outline: Create order ticket

*Given* the Customer {example}
*When* the Customer creates the order ticket
*Then* My Paradise sends the {subject} ticket to Zendesk
*When* Zendesk creates the ticket
*Then* the ticket is created for the Customer
### (S) Care --> View Order History

#### Scenario: View Order History

#### Background

*Given* the Customer has a product order in Mavenir
*And* Care is in Customer Management → Order History

*When* Care views Order History for the Customer
*Then* Care sees the product order with status badges
## (E) Get Voucher Credit
### (S) My Paradise --> Redeem Voucher and Apply Credit

#### Scenario Outline: Redeem a plan-restricted voucher that matches the cart bundle

*Given* the Customer is in Order Creation with ++voucher++ ++{voucher}++ applied
*And* the ++Mavenir shopping cart++ carries ++plan++ ++Essentials++ (id `100000000014`, totalPrice `70.00`)
*And* Vouchera has ++voucher++ ++{voucher}++
*And* the Customer has a billing account
*When* the Customer redeems the voucher
*Then* My Paradise sends the redeem request to Vouchera with ++voucher redemption++ ++{redemption}++ (voucherCode, redeemerIdentifier, orderAmount `70.00`)
*When* Vouchera records the ++voucher redemption++
*Then* My Paradise stores ++voucher redemption++ ++{redemption}++
*When* the Customer applies the voucher credit
*Then* My Paradise sends the ++credit adjustment++ ++{credit}++ to Mavenir (`transactionType` creditAdjustment, glCode `100004`, unit BMD, channel `@type`)
*When* Mavenir records the ++credit adjustment++ on the billing account
*Then* My Paradise stores the credit on the Customer billing account
*And* continues to Create Product Order

#### Scenario: Redeem an any-plan voucher

*Given* the Customer is in Order Creation with ++voucher++ ++any-plan voucher++ applied
*And* the ++Mavenir shopping cart++ carries ++plan++ ++Essentials++ (id `100000000014`, totalPrice `70.00`)
*And* Vouchera has ++voucher++ ++any-plan voucher++
*When* the Customer redeems the voucher
*Then* My Paradise sends the redeem request to Vouchera with ++voucher redemption++ ++zero redemption++ (orderAmount `0.00`)
*When* Vouchera records the ++voucher redemption++
*Then* My Paradise stores ++voucher redemption++ ++zero redemption++
*And* My Paradise skips the apply credit request to Mavenir
*And* continues to Create Product Order

#### Scenario: Skip redeem when the cart bundle is not in the voucher plan list

*Given* the Customer is in Order Creation with ++voucher++ ++amount-off voucher++ applied
*But* the ++Mavenir shopping cart++ carries ++plan++ ++Ace++ (id `100000000042`) which is not in ++voucher++ ++amount-off voucher++ planIds
*When* the Customer redeems the voucher
*Then* My Paradise skips the redeem request to Vouchera
*And* My Paradise skips the apply credit request to Mavenir
*And* continues to Create Product Order

#### Scenario: Failed voucher redemption

*Given* the Customer is in Order Creation with ++voucher++ ++amount-off voucher++ applied
*And* the ++Mavenir shopping cart++ carries ++plan++ ++Essentials++
*And* Vouchera returns an error for the redeem request
*When* the Customer redeems the voucher
*Then* My Paradise sends the redeem request to Vouchera
*When* Vouchera returns an error
*Then* the voucher redemption is unsuccessful
*When* the Customer applies the voucher credit
*Then* My Paradise skips the apply credit request to Mavenir
*And* continues to Create Product Order
# (E) Self-Serve Subscription
## (E) Access Selfcare
### (S) Customer --> Enter Sign In Credentials
### (S) Customer --> Reset Password
### (S) Customer --> Edit Profile
### (S) Customer --> Sign Out
## (E) Manage Billing
### (S) Customer --> View Billing
### (S) Customer --> Pay Now
### (S) Customer --> Enter New Payment Method
## (E) Manage Services
### (S) Customer --> View Dashboard
### (S) Customer --> Change Plan
### (S) Customer --> Request Line Portability
### (S) --> Purchase Device
### (S) Customer --> Send Support Request