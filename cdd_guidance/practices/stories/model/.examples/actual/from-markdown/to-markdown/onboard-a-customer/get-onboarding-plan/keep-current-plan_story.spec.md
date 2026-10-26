## Story: Keep Current Plan

### Scenario: Keep Current Plan

### Background

*Given* the Prospect is in Account Setup
*And* the Prospect has a ++My Paradise customer++ with a ++Mavenir shopping cart++
*And* ++plan++ ++Essentials++ is in the ++Mavenir shopping cart++

*When* the Prospect clicks Keep current plan
*Then* the Prospect is forwarded to Checkout
