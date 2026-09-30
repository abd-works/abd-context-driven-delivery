## Story: Enter Account Credentials

### Scenario Outline: Enter new account credentials

### Background

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


### Scenario: Paradise Mobile email

### Background

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
*Given* the plan catalog contains purchasable plans
*And* the User has selected ++plan++ ++Essentials++ on the Paradise Mobile site
*When* the User enters ++account credentials++ ++Paradise Mobile account credentials++
*Then* the Create Account title is blue


### Scenario: Email already registered

### Background

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
*Given* the plan catalog contains purchasable plans
*And* the User has selected ++plan++ ++Essentials++ on the Paradise Mobile site
*When* the User enters ++account credentials++ ++Paradise Mobile account credentials++
*Then* the Create Account title is blue
*Given* the plan catalog contains purchasable plans
*And* the User has selected ++plan++ ++Essentials++ on the Paradise Mobile site
*Given* ++account credentials++ ++already-registered account credentials++ are already registered
*When* the User registers ++account credentials++ ++already-registered account credentials++
*Then* Email shows the already-registered error
