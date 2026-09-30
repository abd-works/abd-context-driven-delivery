## Story: Submit Portability Request to Mid-Tier

### Scenario: Submit portability request — porting-2fa off (live)

### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*But* no ++portability++ is in the ++Mavenir shopping cart++
*Given* the Prospect has entered ++portability++ ++valid portability++
*When* My Paradise posts a portability request to Midtier with ++portability++ ++valid portability++
*Then* Midtier returns a temporary ++MSISDN++ ++available number++ ++held available number++
*And* My Paradise stores ++portability++ ++valid portability++ and ++available number++ ++held available number++ in the ++Mavenir shopping cart++
*And* the Prospect is forwarded to Select Sim


### Scenario: Submit portability request — porting-2fa on, SMS sent (Intended)

### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*But* no ++portability++ is in the ++Mavenir shopping cart++
*Given* the Prospect has entered ++portability++ ++valid portability++
*When* My Paradise posts a portability request to Midtier with ++portability++ ++valid portability++
*Then* Midtier returns a temporary ++MSISDN++ ++available number++ ++held available number++
*And* My Paradise stores ++portability++ ++valid portability++ and ++available number++ ++held available number++ in the ++Mavenir shopping cart++
*And* the Prospect is forwarded to Select Sim
*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*But* no ++portability++ is in the ++Mavenir shopping cart++
*Given* the Prospect has entered ++portability++ ++valid portability++
*And* `porting-2fa` is enabled
*When* My Paradise posts a portability request to Midtier with ++portability++ ++valid portability++
*Then* Midtier returns `{ status: sent, temporaryNumber: ++available number++ ++held available number++ }`
*And* My Paradise stores ++portability++ ++valid portability++ and ++available number++ ++held available number++ in the ++Mavenir shopping cart++
*And* My Paradise presents the Confirm your number for porting step


### Scenario: Submit portability request — rate limited, bypass (Intended)

### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*But* no ++portability++ is in the ++Mavenir shopping cart++
*Given* the Prospect has entered ++portability++ ++valid portability++
*When* My Paradise posts a portability request to Midtier with ++portability++ ++valid portability++
*Then* Midtier returns a temporary ++MSISDN++ ++available number++ ++held available number++
*And* My Paradise stores ++portability++ ++valid portability++ and ++available number++ ++held available number++ in the ++Mavenir shopping cart++
*And* the Prospect is forwarded to Select Sim
*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*But* no ++portability++ is in the ++Mavenir shopping cart++
*Given* the Prospect has entered ++portability++ ++valid portability++
*And* `porting-2fa` is enabled
*When* My Paradise posts a portability request to Midtier with ++portability++ ++valid portability++
*Then* Midtier returns `{ status: sent, temporaryNumber: ++available number++ ++held available number++ }`
*And* My Paradise stores ++portability++ ++valid portability++ and ++available number++ ++held available number++ in the ++Mavenir shopping cart++
*And* My Paradise presents the Confirm your number for porting step
*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*But* no ++portability++ is in the ++Mavenir shopping cart++
*Given* `porting-2fa` is enabled
*When* My Paradise posts a ++portability request++
*But* Midtier returns `{ status: rate_limited, canBypass: true, temporaryNumber: ++available number++ ++held available number++ }`
*Then* My Paradise stores ++portability++ ++valid portability++ and ++available number++ ++held available number++ with `verified: true` in the ++Mavenir shopping cart++
*And* the Prospect is forwarded to Select Sim


### Scenario: Submit portability request — invalid number (Intended)

### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*But* no ++portability++ is in the ++Mavenir shopping cart++
*Given* the Prospect has entered ++portability++ ++valid portability++
*When* My Paradise posts a portability request to Midtier with ++portability++ ++valid portability++
*Then* Midtier returns a temporary ++MSISDN++ ++available number++ ++held available number++
*And* My Paradise stores ++portability++ ++valid portability++ and ++available number++ ++held available number++ in the ++Mavenir shopping cart++
*And* the Prospect is forwarded to Select Sim
*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*But* no ++portability++ is in the ++Mavenir shopping cart++
*Given* the Prospect has entered ++portability++ ++valid portability++
*And* `porting-2fa` is enabled
*When* My Paradise posts a portability request to Midtier with ++portability++ ++valid portability++
*Then* Midtier returns `{ status: sent, temporaryNumber: ++available number++ ++held available number++ }`
*And* My Paradise stores ++portability++ ++valid portability++ and ++available number++ ++held available number++ in the ++Mavenir shopping cart++
*And* My Paradise presents the Confirm your number for porting step
*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*But* no ++portability++ is in the ++Mavenir shopping cart++
*Given* `porting-2fa` is enabled
*When* My Paradise posts a ++portability request++
*But* Midtier returns `{ status: rate_limited, canBypass: true, temporaryNumber: ++available number++ ++held available number++ }`
*Then* My Paradise stores ++portability++ ++valid portability++ and ++available number++ ++held available number++ with `verified: true` in the ++Mavenir shopping cart++
*And* the Prospect is forwarded to Select Sim
*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*But* no ++portability++ is in the ++Mavenir shopping cart++
*Given* `porting-2fa` is enabled
*When* My Paradise posts a ++portability request++
*But* Midtier returns `{ status: invalid_number }`
*Then* My Paradise shows *This number is invalid.* on Number to be ported


### Scenario: Submit portability request fails

### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*But* no ++portability++ is in the ++Mavenir shopping cart++
*Given* the Prospect has entered ++portability++ ++valid portability++
*When* My Paradise posts a portability request to Midtier with ++portability++ ++valid portability++
*Then* Midtier returns a temporary ++MSISDN++ ++available number++ ++held available number++
*And* My Paradise stores ++portability++ ++valid portability++ and ++available number++ ++held available number++ in the ++Mavenir shopping cart++
*And* the Prospect is forwarded to Select Sim
*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*But* no ++portability++ is in the ++Mavenir shopping cart++
*Given* the Prospect has entered ++portability++ ++valid portability++
*And* `porting-2fa` is enabled
*When* My Paradise posts a portability request to Midtier with ++portability++ ++valid portability++
*Then* Midtier returns `{ status: sent, temporaryNumber: ++available number++ ++held available number++ }`
*And* My Paradise stores ++portability++ ++valid portability++ and ++available number++ ++held available number++ in the ++Mavenir shopping cart++
*And* My Paradise presents the Confirm your number for porting step
*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*But* no ++portability++ is in the ++Mavenir shopping cart++
*Given* `porting-2fa` is enabled
*When* My Paradise posts a ++portability request++
*But* Midtier returns `{ status: rate_limited, canBypass: true, temporaryNumber: ++available number++ ++held available number++ }`
*Then* My Paradise stores ++portability++ ++valid portability++ and ++available number++ ++held available number++ with `verified: true` in the ++Mavenir shopping cart++
*And* the Prospect is forwarded to Select Sim
*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*But* no ++portability++ is in the ++Mavenir shopping cart++
*Given* `porting-2fa` is enabled
*When* My Paradise posts a ++portability request++
*But* Midtier returns `{ status: invalid_number }`
*Then* My Paradise shows *This number is invalid.* on Number to be ported
*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*But* no ++portability++ is in the ++Mavenir shopping cart++
*When* My Paradise posts a ++portability request++
*But* Midtier returns an error
*Then* My Paradise shows *Failed to save your portability.*
