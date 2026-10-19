## Story: Evaluate Porting Two Factor Flag

### Scenario: Porting two factor flag enabled (Intended)

*Given* `porting-2fa` is enabled in GrowthBook
*And* the Prospect is in Account Setup
*When* GrowthBook evaluates the `porting-2fa` flag
*Then* My Paradise mounts the SMS verification step in the porting wizard
*And* My Paradise starts the porting wizard at the SMS verification step when ++portability++ on the ++Mavenir shopping cart++ is unverified

### Scenario: Porting two factor flag disabled (live)

*Given* `porting-2fa` is disabled in GrowthBook
*And* the Prospect is in Account Setup
*When* GrowthBook evaluates the `porting-2fa` flag
*Then* My Paradise omits the SMS verification step from the porting wizard
