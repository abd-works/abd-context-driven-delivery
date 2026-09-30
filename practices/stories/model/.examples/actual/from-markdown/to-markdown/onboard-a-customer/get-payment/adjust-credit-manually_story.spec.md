## Story: Adjust Credit Manually

### Scenario: Adjust credit for pay-upfront or voucher

*Given* the Care agent is in Mavenir DEP for the loaded ++My Paradise customer++
*And* the ++Mavenir customer++ has completed onboarding in My Paradise
*But* the credit adjustment was not applied after checkout
*When* the Care agent manually adjusts the credit amount in Mavenir DEP
*Then* the ++Mavenir customer++ billing account is credited the adjustment amount
