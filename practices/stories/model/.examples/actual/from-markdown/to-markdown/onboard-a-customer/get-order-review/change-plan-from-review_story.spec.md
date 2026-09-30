## Story: Change Plan From Review

### Scenario: Select a different plan from review

### Background

*Given* the Customer is reviewing their order
*And* the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
*Given* the Customer has opened plan selection from review
*When* My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++
*Then* My Paradise sends the patch cart request to Mavenir with ++plan++ ++Data Freedom++ bundleId
*When* Mavenir returns the updated ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++
*Then* My Paradise stores ++plan++ ++Data Freedom++ as the cart bundle
*And* the Customer is forwarded to Checkout


### Scenario: Keep current plan from review

### Background

*Given* the Customer is reviewing their order
*And* the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
*Given* the Customer has opened plan selection from review
*When* My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++
*Then* My Paradise sends the patch cart request to Mavenir with ++plan++ ++Data Freedom++ bundleId
*When* Mavenir returns the updated ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++
*Then* My Paradise stores ++plan++ ++Data Freedom++ as the cart bundle
*And* the Customer is forwarded to Checkout
*Given* the Customer is reviewing their order
*And* the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
*Given* the Customer has opened plan selection from review
*When* the Customer keeps their current plan
*Then* the Customer is forwarded to Checkout


### Scenario: Select the plan already in the cart from review

### Background

*Given* the Customer is reviewing their order
*And* the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
*Given* the Customer has opened plan selection from review
*When* My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++
*Then* My Paradise sends the patch cart request to Mavenir with ++plan++ ++Data Freedom++ bundleId
*When* Mavenir returns the updated ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++
*Then* My Paradise stores ++plan++ ++Data Freedom++ as the cart bundle
*And* the Customer is forwarded to Checkout
*Given* the Customer is reviewing their order
*And* the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
*Given* the Customer has opened plan selection from review
*When* the Customer keeps their current plan
*Then* the Customer is forwarded to Checkout
*Given* the Customer is reviewing their order
*And* the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
*Given* the Customer has opened plan selection from review
*When* My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++Essentials++
*Then* the cart bundle remains ++plan++ ++Essentials++


### Scenario: Plan update fails from review

### Background

*Given* the Customer is reviewing their order
*And* the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
*Given* the Customer has opened plan selection from review
*When* My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++
*Then* My Paradise sends the patch cart request to Mavenir with ++plan++ ++Data Freedom++ bundleId
*When* Mavenir returns the updated ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++
*Then* My Paradise stores ++plan++ ++Data Freedom++ as the cart bundle
*And* the Customer is forwarded to Checkout
*Given* the Customer is reviewing their order
*And* the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
*Given* the Customer has opened plan selection from review
*When* the Customer keeps their current plan
*Then* the Customer is forwarded to Checkout
*Given* the Customer is reviewing their order
*And* the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
*Given* the Customer has opened plan selection from review
*When* My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++Essentials++
*Then* the cart bundle remains ++plan++ ++Essentials++
*Given* the Customer is reviewing their order
*And* the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
*Given* the Customer has opened plan selection from review
*And* Mavenir returns an error on cart patch
*When* My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++
*Then* My Paradise shows *Failed to update new plan choice.*
*And* the cart bundle remains ++plan++ ++Essentials++
