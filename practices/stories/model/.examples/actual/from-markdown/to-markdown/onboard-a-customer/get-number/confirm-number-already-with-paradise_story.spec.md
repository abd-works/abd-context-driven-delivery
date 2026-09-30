## Story: Confirm Number Already With Paradise

### Scenario: Confirm the number is not already with Paradise

### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*And* the Prospect has entered ++portability++ ++valid portability++
*But* no ++portability++ is in the ++Mavenir shopping cart++
*When* the Prospect proceeds to confirming whether their number is already with Paradise
*Then* the Prospect can confirm whether the ++MSISDN++ is already with Paradise
*When* the Prospect confirms the ++MSISDN++ is not already with Paradise
*Then* My Paradise submits ++portability++ ++valid portability++ to the Midtier
*And* the Prospect is forwarded to Select Sim


### Scenario: Confirm the number is already with Paradise

### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*And* the Prospect has entered ++portability++ ++valid portability++
*But* no ++portability++ is in the ++Mavenir shopping cart++
*When* the Prospect proceeds to confirming whether their number is already with Paradise
*Then* the Prospect can confirm whether the ++MSISDN++ is already with Paradise
*When* the Prospect confirms the ++MSISDN++ is not already with Paradise
*Then* My Paradise submits ++portability++ ++valid portability++ to the Midtier
*And* the Prospect is forwarded to Select Sim
*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*And* the Prospect has entered ++portability++ ++valid portability++
*But* no ++portability++ is in the ++Mavenir shopping cart++
*When* the Prospect proceeds to confirming whether their number is already with Paradise
*Then* the Prospect can confirm whether the ++MSISDN++ is already with Paradise
*When* the Prospect confirms the ++MSISDN++ is already with Paradise
*Then* ++portability++ is not submitted to the Midtier
*And* the Prospect is returned to selecting their number
