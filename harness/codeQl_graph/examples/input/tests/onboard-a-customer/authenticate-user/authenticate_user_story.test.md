---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Sub-epic: Authenticate User

## Domain terms

- ++account credentials++ — email, password, confirmPassword; `validate`, `register`, `verify`, `authenticateAccount`, `resendValidationCode`. A signed-in unconfirmed account is on the Verify Account onboarding step.
- ++account credential requirements++ — live rule checklist while creating an account.
- ++validation code++ — emailed code that confirms the unconfirmed account.

## Examples

### account credentials

| account credentials | example | email | password | confirmPassword |
| --- | --- | --- | --- | --- |
| account credentials | valid account credentials | Jeff.anderson@Abdworks.com | Spider-man99p | Spider-man99p |
| account credentials | already-registered account credentials | Jeff.anderson@Agilebydesign.com | Stub@12345 | Stub@12345 |
| account credentials | missing email |  | Spider-man99p | Spider-man99p |
| account credentials | invalid email format | example.prospect | Spider-man99p | Spider-man99p |
| account credentials | missing password | Jeff.anderson@Abdworks.com |  |  |
| account credentials | password missing letters | Jeff.anderson@Abdworks.com | spider-man99p | spider-man99p |
| account credentials | password missing number | Jeff.anderson@Abdworks.com | Spider-manpp | Spider-manpp |
| account credentials | password missing symbol | Jeff.anderson@Abdworks.com | Spiderman99 | Spiderman99 |
| account credentials | password too short | Jeff.anderson@Abdworks.com | Sp1!Man | Sp1!Man |
| account credentials | confirm password missing | Jeff.anderson@Abdworks.com | Spider-man99p |  |
| account credentials | confirm password mismatch | Jeff.anderson@Abdworks.com | Spider-man99p | Spider-man00p |
| account credentials | wrong password | Jeff.anderson@Agilebydesign.com | Wrong#Pass1 | Wrong#Pass1 |
| account credentials | unknown email | unknown.prospect@example.com | Stub@12345 | Stub@12345 |

### validation code

| validation code | example | code | helper message |
| --- | --- | --- | --- |
| validation code | emailed validation code | 123456 |  |
| validation code | resent validation code | 654321 | We sent you a new code. Please check your email. |
| validation code | mismatch validation code | 000000 | Hmm. That code didn't work. |
| validation code | expired validation code | 111111 | Hmm. That code didn't work. |
| validation code | attempts exceeded validation code | 222222 | Attempts limit exceeded. Please try again later. |

---

# Story: Create Account

#### Scenario: Display Create Account

*When* the User proceeds to create an account from the Paradise Mobile website
*Then* the User can enter account credentials
  *And* the email and password rules are unmet
  *And* the customer cannot save the customer account

#### Scenario: Enter Valid account credentials

*When* the User enters valid account credentials
*Then* account credentials are validated continuously
  *And* the customer can save the customer account

#### Scenario: Log out and log back in

*Given* the User has entered valid account credentials
*When* the User logs out of the site
*Then* the account has no browser session
*When* the User enters the username and password
*Then* the account is logged in

#### Scenario Outline: Enter Invalid account credentials

*When* the User registers ${example}
*Then* the account cannot be registered
  *And* the ${unmet} requirement is unmet

##### Examples

| example | unmet | email | password | confirmPassword |
| --- | --- | --- | --- | --- |
| missing email | emailRequired |  | Spider-man99p | Spider-man99p |
| invalid email format | emailFormat | example.prospect | Spider-man99p | Spider-man99p |
| missing password | passwordRequired | Jeff.anderson@Abdworks.com |  |  |
| password missing letters | passwordLetters | Jeff.anderson@Abdworks.com | spider-man99p | spider-man99p |
| password missing number | passwordNumber | Jeff.anderson@Abdworks.com | Spider-manpp | Spider-manpp |
| password missing symbol | passwordSymbol | Jeff.anderson@Abdworks.com | Spiderman99 | Spiderman99 |
| password too short | passwordLength | Jeff.anderson@Abdworks.com | Sp1!Man | Sp1!Man |
| confirm password missing | confirmRequired | Jeff.anderson@Abdworks.com | Spider-man99p |  |
| confirm password mismatch | confirmMismatch | Jeff.anderson@Abdworks.com | Spider-man99p | Spider-man00p |

#### Scenario: Email already registered

*Given* already-registered account credentials are already registered
*When* the User registers already-registered account credentials
*Then* the email is already registered

#### Scenario: Create account

*When* the User creates their account
*Then* the account is unconfirmed and a validation code is emailed

---

# Story: Enter Validation Code

### Background

*Given* the User has submitted valid account credentials
  *And* an unconfirmed account exists
  *And* a validation code has been sent to the User

#### Scenario: Enter validation code

*When* the User verifies the account with the emailed validation code
*Then* the account is verified
  *And* the account has a token for the browser session

#### Scenario Outline: Activate with unusable validation code

*When* the User verifies with ${example}
*Then* the validation code is rejected

##### Examples

| example | code | helper message |
| --- | --- | --- |
| mismatch validation code | 000000 | Hmm. That code didn't work. |
| expired validation code | 111111 | Hmm. That code didn't work. |
| attempts exceeded validation code | 222222 | Attempts limit exceeded. Please try again later. |

#### Scenario: Resend validation code

*When* more than 60 seconds has passed
  *And* the User resends the validation code
*Then* a new validation code is sent
  *And* the Customer is told a new code was sent
*When* less than 60 seconds has passed
  *And* the User resends the validation code
*Then* resend waits 60 seconds before it can be used again
  *And* another validation code is not sent during the wait
*When* more than 60 seconds has passed
  *And* the User resends the validation code
*Then* another validation code is sent

---

# Story: Sign In With Existing Account

#### Scenario: Sign in with already-registered account credentials

*Given* an already-registered account exists
  *And* the Customer is not signed in
  *And* the Customer has already-registered account credentials
*When* the Customer authenticates already-registered account credentials
*Then* the account has a token for the browser session
  *And* the account holds the customer id

#### Scenario: Email format is unmet

*Given* the Customer has invalid email format account credentials
*When* the Customer authenticates invalid email format
*Then* the authentication is rejected
  *And* the account has no token

#### Scenario Outline: Authenticate with incorrect account credentials

*Given* an already-registered account exists
  *And* the Customer is not signed in
  *And* the Customer has ${example}
*When* the Customer authenticates ${example}
*Then* the authentication is rejected
  *And* the account has no token

##### Examples

| example | email | password | confirmPassword |
| --- | --- | --- | --- |
| wrong password | Jeff.anderson@Agilebydesign.com | Wrong#Pass1 | Wrong#Pass1 |
| unknown email | unknown.prospect@example.com | Stub@12345 | Stub@12345 |

#### Scenario: Authenticate with unconfirmed account

*Given* an unconfirmed account exists
  *And* the Customer is not signed in
  *And* the Customer has unconfirmed sign-in account credentials
*When* the Customer authenticates unconfirmed sign-in
*Then* the account has a token for the browser session
  *And* the account has no customer
  *And* the Customer can enter the validation code
  *And* the Customer is on the Verify Account step
