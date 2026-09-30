## Story: List Product Offerings

### Scenario: List Product Offerings

*Given* Mavenir catalog for service provider 100000000 is reachable
*When* Mavenir is asked to list product offerings with channelName CRM
*Then* Mavenir returns product bundles including ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, ++plan++ ++Atlas++, and ++plan++ ++Internal Test Plan PROMO++ with their productOfferingPrice and bundledProductOffering
