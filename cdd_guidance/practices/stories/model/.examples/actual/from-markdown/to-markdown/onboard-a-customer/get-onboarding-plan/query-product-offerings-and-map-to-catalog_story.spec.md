## Story: Query Product Offerings And Map To Catalog

### Scenario: Query Product Offerings And Map To Catalog

*Given* Mavenir has returned product offerings for service provider 100000000
*When* Midtier is asked to query product offerings and map to catalog
*Then* Midtier filters offerings to valid bundle IDs — ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, ++plan++ ++Atlas++, and ++plan++ ++Internal Test Plan PROMO++
*And* strips "PROMO" from ++plan++ ++Internal Test Plan PROMO++ name
*And* marks ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, and ++plan++ ++Atlas++ as isSellable
*And* marks ++plan++ ++Internal Test Plan PROMO++ as not isSellable
*And* tags ++plan++ ++Ace++ as "Best value"
*And* returns the ++plan++ catalog sorted by price descending to Choose Onboarding Plan
