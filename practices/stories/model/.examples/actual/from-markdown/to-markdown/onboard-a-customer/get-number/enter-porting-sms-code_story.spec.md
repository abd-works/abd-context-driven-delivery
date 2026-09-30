## Story: Enter Porting Sms Code

### Scenario: Enter ++porting SMS code++

### Background

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


### Scenario: Verify with unusable ++porting SMS code++

### Background

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
*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*And* ++portability++ ++valid portability++ is in the ++Mavenir shopping cart++
*And* My Paradise has SMSed a ++porting SMS code++ through the Midtier
*When* the Prospect clicks Verify code with ++porting SMS code++ ++mismatch porting SMS code++
*Then* Enter SMS code shows helper text *Invalid verification code.*


### Scenario: Resend ++porting SMS code++

### Background

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
*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*And* ++portability++ ++valid portability++ is in the ++Mavenir shopping cart++
*And* My Paradise has SMSed a ++porting SMS code++ through the Midtier
*When* the Prospect clicks Verify code with ++porting SMS code++ ++mismatch porting SMS code++
*Then* Enter SMS code shows helper text *Invalid verification code.*
*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*And* ++portability++ ++valid portability++ is in the ++Mavenir shopping cart++
*And* My Paradise has SMSed a ++porting SMS code++ through the Midtier
*When* the Prospect clicks Resend
*Then* My Paradise SMSes a ++porting SMS code++ through the Midtier
*And* the Prospect sees *A new code was sent to* the ++portability++ number
*And* Resend is disabled for 30 seconds before it can be used again
