## Story: Enter Account Credentials

### Examples

#### Account credential requirements

| example | account credential requirements | field | requirement | group |
| --- | --- | --- | --- | --- |
| email required | account credential requirements | email | Email is required | Account credential requirements |
| email format | account credential requirements | email | Please use a valid email format: yourname@domain.com | Account credential requirements |
| password letters | account credential requirements | password | Password must contain uppercase and lowercase letters | Account credential requirements |
| password number | account credential requirements | password | Password must have at least one number | Account credential requirements |
| password symbol | account credential requirements | password | Password must have at least one symbol | Account credential requirements |
| password length | account credential requirements | password | Length must be greater than 8 characters | Account credential requirements |
| confirm required | account credential requirements | confirmPassword | Confirm Password is required | Account credential requirements |
| confirm mismatch | account credential requirements | confirmPassword | Passwords don't match | Account credential requirements |
| example | account credentials | unmet | Create account | Account credential requirements |
| valid account credentials | account credentials |  | enabled | Account credential requirements |
| Paradise Mobile account credentials | account credentials |  | enabled | Account credential requirements |
| invalid password letters | account credentials | Password must contain uppercase and lowercase letters | disabled | Account credential requirements |
| invalid password number | account credentials | Password must have at least one number | disabled | Account credential requirements |
| invalid password symbol | account credentials | Password must have at least one symbol | disabled | Account credential requirements |
| invalid password length | account credentials | Length must be greater than 8 characters | disabled | Account credential requirements |
| invalid confirm required | account credentials | Confirm Password is required | disabled | Account credential requirements |
| invalid confirm mismatch | account credentials | Passwords don't match | disabled | Account credential requirements |
| invalid email required | account credentials | Email is required | disabled | Account credential requirements |
| invalid email format | account credentials | Please use a valid email format: yourname@domain.com | disabled | Account credential requirements |

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

*When* the User enters ++account credentials++ ++Paradise Mobile account credentials++
*Then* the Create Account title is blue

### Scenario: Email already registered

### Background

*Given* the plan catalog contains purchasable plans
*And* the User has selected ++plan++ ++Essentials++ on the Paradise Mobile site

*Given* ++account credentials++ ++already-registered account credentials++ are already registered
*When* the User registers ++account credentials++ ++already-registered account credentials++
*Then* Email shows the already-registered error
