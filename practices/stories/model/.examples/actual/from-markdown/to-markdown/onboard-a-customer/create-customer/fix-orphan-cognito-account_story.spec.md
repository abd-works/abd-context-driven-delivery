## Story: Fix Orphan Cognito Account

### Scenario: Fix Orphan Cognito Account

### Background

*Given* the User has clicked Create account with ++account credentials++ ++valid account credentials++
*And* Cognito has an ++Cognito user++ ++unconfirmed Cognito user++
*But* the User has not entered a ++validation code++
*And* no ++account token++ is issued
*When* Care is asked to fix the orphan ++Cognito user++
*Then* Care changes the email in Mavenir DEP
*And* Care does not delete the ++Cognito user++
