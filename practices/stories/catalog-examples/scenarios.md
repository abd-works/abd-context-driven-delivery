---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Create Unconfirmed User

#### Scenario: Display Create Account

*When* the User proceeds to create an account from the Paradise Mobile website
*Then* the User can enter account credentials
  *And* the email and password rules are unmet
  *And* the customer cannot save the customer account

#### Scenario: Enter Valid account credentials

*When* the User enters valid account credentials
*Then* account credentials are validated continuously
  *And* the customer can save the customer account

#### Scenario: Enter Invalid account credentials: ${example}

*When* the User registers When the requirements have not been met
*Then* the account cannot be registered
  *And* the ${unmet} requirement is unmet

#### Scenario: Email already registered

*Given* already-registered account credentials are already registered
*When* the User registers already-registered account credentials
*Then* the email is already registered

#### Scenario: Create Unconfirmed User

*Given* the amplifyService.signUp spy is set up
*When* the User creates their account
*Then* the system creates an unconfirmed Cognito user and emails a validation code
